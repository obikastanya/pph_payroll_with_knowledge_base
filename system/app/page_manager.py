"""Knowledge base management: new documents with the AI's real work from the research runs, review (approve, edit,
ask the AI to fix with your notes, reject), add / change / revoke by hand or by asking the AI, company policies,
knowledge base check, and version history. Everything is kept in the demo workspace and undone by Reset.
"""
import json
from datetime import date, timedelta

import pandas as pd
import streamlit as st

import ai
import assistant
import data as d
import drafts
import employee as emp
import glossary as g
import inputs
import store
import ui
from pph21kbs import static
from pph21kbs.kb import apply_delta
from pph21kbs.kb.delta import validate_delta_json

STATUS = {"review": ("Ready for review", "blue"), "ragu": ("System unsure", "yellow"), "tidak relevan": ("Not relevant", "grey"),
          "disetujui": ("Approved", "green"), "ditolak": ("Rejected", "red"), "menunggu AI": ("Waiting for AI", "grey"),
          "anggaran habis": ("Budget used up", "red")}
GATES = {"G1": "Correct format and structure", "G2": "Quotes, numbers, and dates are in the document",
         "G3": "No conflict with other rules", "G4": "Past calculations do not change",
         "G5": "Every part of the proposal has an effect"}
# Display names of the stored origin / "by" values of drafts and repaired proposals (the stored values stay as they are).
ORIGIN_EN = {"unggah JSON": "JSON upload", "manual": "manual", "contoh": "example", "asisten": "assistant",
             "jawaban acuan penelitian (simulasi)": "research reference answer (simulation)",
             "disunting manual": "edited by hand"}
RESEARCH_EN = {"benar": "correct", "salah": "wrong", "ragu": "system unsure", "tidak relevan": "not relevant",
               "tidak bisa dinilai": "could not be judged"}


def _shown(value):
    return ORIGIN_EN.get(value, value)


def _pl(n, word):
    """'1 rule', '3 rules'."""
    return f"{n} {word}" + ("" if n == 1 else "s")


def _title(pid):
    p = store.pending_by_id().get(pid)
    return d.doc_title(p["doc"]) if p else pid


# ---------------------------------------------------------------- new documents
def _ai_steps(pid, stat):
    r = store.run(pid)
    n = len(r.get("candidates", [])) if r else 0
    passed = sum(1 for c in (r or {}).get("candidates", []) if c.get("passed"))
    groups = (r or {}).get("groups") or []
    steps = [("Read text", "done")]
    if stat == "tidak relevan":
        return steps + [("Relevance check: not relevant", "skip")]
    steps += [("Relevance check", "done"), (f"Draft {_pl(n, 'proposed version')}", "done"),
              (f"Checks: {passed}/{n} passed", "done")]
    if stat == "ragu":
        return steps + [(f"Agreement check: {_pl(len(groups), 'different group')}", "skip")]
    steps.append((f"Agreement check: {max(map(len, groups)) if groups else 0}/{passed} agree", "done"))
    label = {"disetujui": ("Approved", "done"), "ditolak": ("Rejected", "fail")}.get(stat, ("Your review", "now"))
    return steps + [label]


def _ai_detail(pid):
    r = store.run(pid)
    rel = (r.get("relevance") or {}).get("output") or {}
    st.markdown(f"**The AI's reason for relevance**: _{rel.get('reason', '-')}_")
    sel = r.get("selection") or {}
    st.caption("Parts of the document read: " + ", ".join(f"{k} ({v.get('tokens', 0):,} tokens)"
                                                          for k, v in sel.items()))
    rows = []
    for c in r.get("candidates", []):
        log = c.get("gate_log") or {}
        rows.append({"Version": c.get("n"), "Passed": "yes" if c.get("passed") else "no",
                     "Repaired automatically": "yes" if c.get("repaired") else "-",
                     **{GATES[k]: ("✓" if log.get(k) == "pass" else "✗" if log.get(k) else "-") for k in GATES},
                     "Note": (c.get("error") or "")[:80]})
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    groups = r.get("groups") or []
    if groups:
        st.caption("Versions with the same calculation result: " + " · ".join("version " + ", ".join(map(str, g_)) for g_ in groups)
                   + f". Chosen: version {r.get('selected') or '-'}. AI cost: USD {r.get('cost_usd', 0):.2f}.")


def _sample_picker():
    """Examples of the research corpus, so a first try needs no file: the browser's file dialog cannot be pointed at a
    folder by the page, so the examples are chosen here and enter the list as if uploaded."""
    found = ai.samples()
    if not found:
        return
    with st.expander("No file yet? Use an example document", icon=":material/folder_open:"):
        by_id = {doc_id: (row, chars) for doc_id, row, chars in found}
        pick = st.selectbox("Example", list(by_id), key="mg_sample", label_visibility="collapsed",
                            format_func=lambda i: f"{by_id[i][0]['title'][:70]} · ~{by_id[i][1] // 1000}k characters")
        row, chars = by_id[pick]
        st.caption(f"Issued {d.tgl(date.fromisoformat(row['issued']))} · "
                   f"{'company policy' if row['role'].startswith('policy') else 'government regulation'}. "
                   "The text comes from the research corpus; the original files are in `dataset/01_regulasi/` (regulations) "
                   "and `dataset/10_kebijakan_perusahaan/` (company policies). The longer the text, the more it "
                   "costs the AI to read it.")
        if st.button("Use this example", key="mg_sample_go", icon=":material/add:"):
            store.add_inbox(ai.upload_sample(pick))
            st.toast("Example added to the document list. Check the text, then run the AI.")
            st.rerun()


def _upload_form(s):
    with st.container(border=True):
        st.markdown("**Upload a document**")
        _sample_picker()
        with st.form("mg_upload", clear_on_submit=True, border=False):
            up = st.file_uploader("PDF, TXT, or JSON", type=["pdf", "txt", "json"], key="mg_up",
                                  help="The AI reads PDF/TXT and proposes an update. Scanned PDFs are read with "
                                       "OCR. JSON is a ready-made update: it goes straight to Review.")
            c1, c2, c3 = st.columns([2.2, 1, 1.3])
            title = c1.text_input("Document title", placeholder="e.g. PMK 12/2027 on ...")
            issued = c2.date_input("Issue date", store.TODAY, help=g.tip("dicatat"))
            kind = c3.radio("Type of document", ("regulasi", "kebijakan"), horizontal=True,
                            format_func={"regulasi": "Government regulation", "kebijakan": "Company policy"}.get,
                            help=g.tip("regulasi") + "\n\n" + g.tip("kebijakan perusahaan"))
            ocr = st.checkbox("Re-read all pages with OCR", help="For PDFs whose text came out garbled.")
            sent = st.form_submit_button("Add to document list", type="primary", icon=":material/upload:")
        if not (sent and up):
            return
        if up.name.lower().endswith(".json"):
            try:
                delta = json.loads(up.getvalue())
                validate_delta_json(delta)
                store.add_draft(delta["delta_id"], (delta.get("document") or {}).get("title", up.name), delta,
                                "unggah JSON")
                st.success("Valid JSON update, added to Review.")
            except Exception as e:  # noqa: BLE001
                st.error(f"The JSON cannot be used: {str(e)[:250]}")
            return
        if not title.strip():
            st.error("Enter the document title first.")
            return
        with st.spinner("Reading the document text (PDF: layout, tables, and OCR; about 5 seconds per page) ..."):
            item = ai.upload(up, title.strip(), issued, kind, force_ocr=ocr)
        store.add_inbox(item)
        st.success("Document added to the list. Check the text, then run the AI.")


def _waiting(p):
    """An uploaded document the AI has not read yet: its text, and the button that runs the AI."""
    pages, tables = ai.text_stats(p)
    chars = sum(len(t.strip()) for _, t in pages)
    st.caption(f"{_pl(len(pages), 'page')} · {chars:,} characters · {_pl(len(tables), 'table')} · issued "
               f"{d.tgl(date.fromisoformat(p['issued']))}")
    if chars < 40 * max(1, len(pages)):
        st.warning("Very little text was extracted. Check the scan, or upload again with OCR.",
                   icon=":material/document_scanner:")
    with st.expander("Show the text the AI will read"):
        st.text("\n".join(t for _, t in pages)[:4000])
    ok, why = ai.ready("akuisisi")
    c1, c2 = st.columns([1, 2])
    m = c1.radio("Number of proposed versions", (3, 1), horizontal=True, key=f"mg_m_{p['id']}",
                 help=g.tip("versi usulan") + " One version is cheaper, but has no agreement check.")
    c2.caption(f"Claude ({ai.llm.MAIN_MODEL}) reads the document with the research workflow: relevance, proposed "
               f"versions, G1–G5 checks, one repair round, agreement check. Estimated USD 0.1–0.9 per document "
               f"(3 versions). {ai.budget_text('akuisisi')}")
    if not ok:
        st.warning(f"The AI cannot run: {why}.", icon=":material/payments:")
        return
    sure = st.checkbox("I understand this uses API credit", key=f"mg_ok_{p['id']}")
    if st.button("Run AI", type="primary", icon=":material/smart_toy:", key=f"mg_run_{p['id']}", disabled=not sure):
        with st.spinner("The AI is reading the document and drafting a proposal (a few minutes) ..."):
            try:
                res = ai.read(p, m=m)
                st.toast(f"Done. Cost USD {res.get('cost_usd', 0):.3f}.")
            except Exception as e:  # noqa: BLE001 - shown to the user
                st.error(f"AI failed: {type(e).__name__}: {str(e)[:300]}")
                return
        st.rerun()


def tab_documents():
    s = store.load()
    _upload_form(s)
    items = store.pending(s)
    if not items:
        st.caption("No documents yet. Upload a regulation or company policy above.")
        return
    presenter = store.DEMO and st.toggle(
        "Show presenter notes", key="mg_presenter",
        help="Shows the research result for each document. Turn it off during a demo so the audience can judge for themselves.")
    for p in reversed(items):
        stat = store.status(p["id"], s)
        label, colour = STATUS.get(stat, (stat, "grey"))
        reg = p["kind"] == "regulasi"
        with st.container(border=True):
            ui.html(f"{ui.badge(label, colour)}"
                    f"{ui.badge('government regulation' if reg else 'company policy', 'blue' if reg else 'orange')}"
                    f"<b>{_title(p['id'])}</b>" + (" <span class='muted'>· uploaded</span>" if p.get("upload") else ""))
            if stat == "menunggu AI":
                _waiting(p)
                continue
            ui.flow(_ai_steps(p["id"], stat))
            if presenter and p.get("research"):
                st.caption(f"Presenter note · result in the research: **{RESEARCH_EN.get(p['research'], p['research'])}**. {p['why']}")
            if p.get("cost_usd"):
                st.caption(f"AI cost for this document: USD {p['cost_usd']:.3f}")
            c1, c2, c3 = st.columns(3)
            if stat == "review" and c1.button("Review", key=f"rv_{p['id']}", icon=":material/rate_review:",
                                              width="stretch"):
                st.session_state.mg_open = p["id"]
                st.toast("Open the Review tab.")
            if stat in ("ragu", "anggaran habis"):
                g.md(f"The AI's proposed versions disagree, so the system is {g.term('ragu', 'unsure')} and does not guess."
                     if stat == "ragu" else "The AI stopped because the budget limit was reached.")
                if p.get("upload"):
                    if c1.button("Run AI again", key=f"redo_{p['id']}", icon=":material/smart_toy:",
                                 width="stretch", disabled=not ai.ready("akuisisi")[0], help=ai.budget_text("akuisisi")):
                        with st.spinner("The AI is re-reading the document ..."):
                            ai.read(p)
                        st.rerun()
                elif c1.button("Ask AI to redo it (simulation)", key=f"redo_{p['id']}",
                               icon=":material/smart_toy:", width="stretch",
                               help="Demo: the result is the research reference answer, no API call."):
                    ref = store.gold_delta(p["id"])
                    store.add_draft(p["id"], _title(p["id"]), ref, "jawaban acuan penelitian (simulasi)")
                    st.session_state.mg_open = p["id"]
                    st.rerun()
                if c2.button("Do it manually", key=f"man_{p['id']}", icon=":material/edit:", width="stretch"):
                    st.toast("Write the rule in the Company policy tab or the Add, change, revoke tab.")
            if stat == "tidak relevan":
                g.md(f"The AI judged this document not {g.term('relevan', 'relevant')} to PPh 21 for permanent employees. Nothing changes.")
            if store.run(p["id"]):
                with st.expander("Show the AI's work"):
                    _ai_detail(p["id"])


# ---------------------------------------------------------------- review
def _prev(rec_id, kb):
    found = [r for r in kb.records if r.id == rec_id]
    return max(found, key=lambda r: r.seq) if found else None


def _iso(x):
    return d.tgl(date.fromisoformat(str(x))) if x else "-"


def _up(text):
    return text[:1].upper() + text[1:]


def card(el, kb):
    kind = el.get("kind")
    src = (el.get("source") or [{}])[0]
    quote = f"<div class='quote'>“{src.get('quote', '')}” · {src.get('provision', '')}</div>"
    period = f"effective {_iso(el.get('valid_from'))}" + (f" until {_iso(el['valid_until'])}" if el.get("valid_until") else "")
    old = _prev(el["id"], kb)
    if kind == "parameter":
        title = d.label_of(el) or _up(d.fact_label(el.get("name", "")))
        same = [r for r in kb.records if r.kind == "parameter" and r.name == el.get("name") and r.id != el["id"]]
        ref = old or (max(same, key=lambda r: r.valid_from) if same else None)
        fmt = lambda v, t: d.money(int(float(v))) if t == "money" else (d.pct(float(v)) if t == "rate" else str(v))  # noqa: E731
        new = fmt(el.get("value"), el.get("value_type"))
        oldv = fmt(ref.value, ref.value_type) if ref else None
        body = (f"<span class='diff-old'>{oldv}</span> → " if oldv and oldv != new else "") + f"<span class='diff-new'>{new}</span>"
        what = "Number changed" if old else ("New number" if not oldv else "New number (old value ends)")
    elif kind == "rule":
        title = d.fact_label(el["produces"])
        body = f"<b>Formula:</b> {d.readable(el['expression'])}"
        if el.get("condition"):
            body = f"<b>If:</b> {d.readable(el['condition'])}<br>" + body
        if old and d.expr_text(old.expression) == el["expression"]:
            what = "Validity period changed"
            body += (f"<br><span class='diff-old'>until {d.tgl(old.valid_until) if old.valid_until else 'no end'}</span>"
                     f" → <span class='diff-new'>until {_iso(el.get('valid_until')) if el.get('valid_until') else 'no end'}</span>")
        elif old:
            what = "Rule changed"
            body = f"<span class='diff-old'>{d.readable(old.expression)}</span><br>" + body
        else:
            what = "New rule" + (" (company)" if el.get("layer") == "company" else "")
            # the rule already in the knowledge base for the same value, so the reviewer can compare
            same = [r for r in kb.view(store.TODAY).rules.values() if r.produces == el["produces"]
                    and r.layer == el.get("layer", "regulation") and not d.is_input_convention(r)]
            if same:
                prev = max(same, key=lambda r: r.valid_from or date.min)
                body += (f"<br><span class='muted'>Existing rule for this value "
                         f"({d.tgl(prev.valid_from)}{' until ' + d.tgl(prev.valid_until) if prev.valid_until else ''}): "
                         f"</span><span class='diff-old' style='text-decoration:none'>{d.readable(prev.expression)}</span>")
                if prev.condition:
                    body += f" <span class='muted'>if {d.readable(prev.condition)}</span>"
    elif kind == "table":
        title, what = d.label_of(el) or _up(el.get("name", "")), "Table changed" if old else "New table"
        body = (f"Taken from the annex table of the document ({el['rows_ref'].split('/')[-1]})" if el.get("rows_ref")
                else _pl(len(el.get("rows") or []), "row"))
    elif kind == "fact":
        title, what, body = d.label_of(el) or _up(el["id"]), "New term", ""
        period = ""
    else:
        title, what, body = el.get("id", ""), kind, ""
    cls = "rule company" if el.get("layer") == "company" else "rule"
    ui.html(f"<div class='{cls}'>{ui.badge(what, 'green' if what.startswith('New') else 'blue')}<b>{title}</b> "
            f"<span class='muted'>· {period}</span><br>{body}{quote}</div>")


def check(delta, kb):
    """Schema, application, static check: the gates that run without the AI, here and now."""
    try:
        validate_delta_json(delta)
    except Exception as e:  # noqa: BLE001
        return None, [("error", f"Format: {str(e)[:250]}")]
    try:
        kb2 = apply_delta(kb, delta)
    except Exception as e:  # noqa: BLE001
        return None, [("error", f"Cannot be applied to the current knowledge base: {str(e)[:250]}")]
    pols = tuple({e.get("policy") for e in delta.get("add", []) + delta.get("change", []) if e.get("policy")})
    issued = (delta.get("document") or {}).get("issued")
    at = max(date.fromisoformat(issued) if issued else store.TODAY, date(2013, 1, 1))
    rep = static.check(kb2, at, policies=pols)
    return kb2, [(f.severity, f"{f.kind}: {f.detail}") for f in rep.findings]


@st.cache_data(show_spinner="Validating SHACL ...")
def shacl_new(signature, delta_json):
    """SHACL violations that the update would add to the current knowledge base of the demo."""
    from pph21kbs.kb import shacl
    kb = store.kb()
    kb2 = apply_delta(kb, json.loads(delta_json))
    docs = sorted(set(shacl.corpus_documents()) | set(kb2.documents))
    before = set(shacl.validate(kb, docs))
    return [v for v in shacl.validate(kb2, docs) if v not in before]


def research_gates(signature, pid, delta_json):
    """Gates G1-G5 of the research (pipeline.run.check, the same code and S^G generator as the experiments), run on
    the current knowledge base of the demo. Returns (passed, {gate: summary})."""
    from types import SimpleNamespace
    from pph21kbs import corpus
    from pph21kbs.pipeline.run import Config, check as gate_check
    delta = json.loads(delta_json)
    els = delta.get("add", []) + delta.get("change", [])
    company = any(e.get("layer") == "company" for e in els)
    try:
        ev = corpus.event(pid)
    except KeyError:              # a draft made in the demo: its own document and date
        doc = delta.get("document") or {}
        ev = SimpleNamespace(id=pid, layer="company" if company else "regulation",
                             issued=date.fromisoformat(doc["issued"]) if doc.get("issued") else store.TODAY,
                             documents=tuple(sorted({s["document"] for e in els for s in e.get("source") or []
                                                     if s.get("document")})))
    pols = tuple(sorted({e["policy"] for e in els if e.get("policy")}))
    ok, log, _, _ = gate_check(store.kb(), delta, ev, ev.issued, None, Config(), policies=pols)
    return ok, {k: str(v) for k, v in log.items() if k in ("G1", "G2", "G3", "G4", "G5")}


def research_gates_panel(pid, delta_json):
    st.markdown("**Research gates G1–G5**",
                help="The same check code as the research, including the automatically generated S^G example cases, "
                     "run on the current knowledge base. Passing the gates does not mean correct: the research "
                     "found proposals that passed all five gates but were wrong, so you still need to check the "
                     "content.")
    done = st.session_state.setdefault("mg_gates", {})
    key = (store.signature(), pid, delta_json)
    if key not in done:
        if st.button("Run the gates (~15 seconds)", icon=":material/fact_check:", key=f"mg_gate_{pid}",
                     width="stretch"):
            with st.spinner("Running G1–G5 ..."):
                try:
                    done[key] = research_gates(*key)
                except Exception as e:  # noqa: BLE001 - shown to the user
                    done[key] = (False, {"G1": f"could not run: {type(e).__name__}: {e}"[:200]})
        else:
            return
    ok, log = done[key]
    for gate, summary in log.items():
        good = summary.startswith("pass")
        if "known document" in summary:
            summary = ("the source document is not registered yet. In the research every document is registered first "
                       "(title, issue date, text) before it is read; this draft uses a document that is not registered.")
        st.markdown(f"{':material/check_circle:' if good else ':material/cancel:'} {gate} · {GATES.get(gate, gate)}"
                    + ("" if good else f": {summary[:160]}"))
    if ok:
        st.caption("Passed all five gates. Still check the content of the changes.")


def regression(kb, kb2, policies):
    """Every scenario before and after: PPh of the scenario's month and of the year."""
    outputs = {n for n, f in kb2.view(store.TODAY).facts.items() if f.output}     # the results the KB declares
    rows = []
    for sc in emp.scenarios().values():
        case = emp.scenario_case(sc)
        m = sc["month"]
        res = [d.compute(case, store.TODAY, k)[0] for k in (kb, kb2)]
        vals = [{(f, mm): v for mm, p in (r.periods.items() if r else ()) for f, v in p.items() if f in outputs}
                | {(f, 0): v for f, v in ((r.year or {}).items() if r else ()) if f in outputs} for r in res]
        moved = sorted({f for key in set(vals[0]) | set(vals[1]) if vals[0].get(key) != vals[1].get(key)
                        for f in [key[0]]}, key=d.fact_label)
        a, b = (r.periods[m].get("pph21_due") if r else None for r in res)
        ya, yb = ((r.year or {}).get("annual_pph21") if r else None for r in res)
        rows.append({"Scenario": sc["title"], "Month": f"{d.MON[m - 1]} {case['tax_year']}",
                     "PPh before": d.money(a), "PPh after": d.money(b),
                     "Full year before → after": f"{d.money(ya)} → {d.money(yb)}" if ya != yb else d.money(ya),
                     "Result": "changed" if moved else "same",
                     "Values that changed": ", ".join(d.fact_label(f) for f in moved[:4])
                                           + (f" +{len(moved) - 4}" if len(moved) > 4 else "")})
    return pd.DataFrame(rows)


def affected_policies(delta, kb):
    """Installed company policies whose rules read or produce a value this update touches (static, like RQ4)."""
    touched = set()
    for e in delta.get("add", []) + delta.get("change", []):
        if e.get("kind") == "rule":
            touched.add(e["produces"])
        elif e.get("kind") in ("parameter", "table"):
            for r in kb.view(store.TODAY).rules.values():
                if f"'{e.get('name')}'" in d.expr_text(r.expression) + d.expr_text(r.condition or ""):
                    touched.add(r.produces)
    out = []
    for r in kb.view(store.TODAY).rules.values():
        if r.layer != "company":
            continue
        text = d.expr_text(r.expression) + " " + d.expr_text(r.condition or "")
        hit = [f for f in touched if f == r.produces or f in text]
        if hit:
            out.append((r.policy, r.id, hit))
    return out


def tab_review():
    s = store.load()
    items = [p["id"] for p in store.pending(s) if store.status(p["id"], s) == "review"]
    items += [x["id"] for x in s["drafts"] if x["id"] not in items]
    if not items:
        st.success("Nothing is waiting for review.")
        return
    names = {i: _title(i) for i in items}
    names.update({x["id"]: f"{x['title']} ({_shown(x['origin'])})" for x in s["drafts"]})
    cur = st.session_state.get("mg_open")
    pid = st.selectbox("Reviewing", items, index=items.index(cur) if cur in items else 0, format_func=names.get)
    st.session_state.mg_open = pid
    delta = store.proposal(pid, s)
    kb = store.kb()
    if pid in s["fixed"]:
        st.info(f"This is the repaired version ({_shown(s['fixed'][pid]['by'])}). Note: “{_shown(s['fixed'][pid]['note'])}”",
                icon=":material/auto_fix_high:")
        last = st.session_state.get(f"mg_fixlog_{pid}")
        if last:
            passed, log, cost = last
            st.caption(f"AI repair result: {'passed' if passed else 'did not pass'} G1–G5 "
                       f"({', '.join(f'{k} {v[:30]}' for k, v in log.items())}) · cost USD {cost:.3f}")
    elif pid in store.pending_by_id(s):
        r0 = store.run(pid) or {}
        st.caption("Original AI proposal from the research (claude-opus-5-5)." if not store.pending_by_id(s)[pid].get("upload")
                   else f"AI proposal ({r0.get('run', 'app')}).")
    kb2, msgs = check(delta, kb)
    left, right = st.columns([1.6, 1], gap="large")
    with left:
        st.markdown(f"**Proposed changes** · {_pl(len(delta.get('add', [])), 'addition')}, "
                    f"{_pl(len(delta.get('change', [])), 'change')}")
        for el in delta.get("change", []) + delta.get("add", []):
            card(el, kb)
    with right:
        st.markdown("**Checks against the current knowledge base**", help=g.tip("pemeriksaan"))
        errors = [m for sev, m in msgs if sev == "error"]
        if kb2 is None:
            st.error(errors[0] if errors else msgs[0][1])
        else:
            dj = json.dumps(delta, sort_keys=True, default=str)
            st.markdown(":material/check_circle: Format is valid and can be applied")
            new_v = shacl_new(store.signature(), dj)
            st.markdown(f"{':material/cancel:' if new_v else ':material/check_circle:'} Graph shape matches SHACL"
                        + (f": {_pl(len(new_v), 'new violation')}" if new_v else ""), help=g.tip("SHACL"))
            for e, m in new_v[:3]:
                st.caption(f"⚠ {e}: {m}")
            qs = assistant.quote_status(delta)
            bad = [q for q in qs if q[2] is False or not q[3]]
            unknown = [q for q in qs if q[2] is None]
            st.markdown(f"{':material/cancel:' if bad else ':material/check_circle:'} Quotes are in the document"
                        + (f": {len(bad)} need checking" if bad else "")
                        + (f" · {len(unknown)} without document text" if unknown else ""), help=g.tip("kutipan"))
            st.markdown(f"{':material/warning:' if msgs else ':material/check_circle:'} Static checker"
                        + (f": {_pl(len(msgs), 'note')}" if msgs else ""), help=g.tip("pemeriksa statis"))
            for sev, m in msgs[:4]:
                st.caption(f"⚠ {m}")
            research_gates_panel(pid, dj)
        run = store.run(pid) if pid in store.pending_by_id(s) and pid not in s["fixed"] else None
        if run:
            sel = next((c for c in run["candidates"] if c.get("n") == run.get("selected")), run["candidates"][0])
            with st.expander("Check results when the AI drafted the proposal"):
                st.caption("Recorded when the AI drafted the proposal, against the knowledge base at that time, not the "
                           "current knowledge base.")
                for k, v in GATES.items():
                    ok = (sel.get("gate_log") or {}).get(k) == "pass"
                    st.markdown(f"{':material/check_circle:' if ok else ':material/cancel:'} {v}")
        if st.button("Ask the assistant about this proposal", icon=":material/forum:", width="stretch"):
            assistant.open_with("Check this proposal against its source quotes")
            st.rerun()
    if kb2 is not None:
        st.markdown("**Examples before and after** · all common scenarios, calculated with the current knowledge base "
                    "and after this proposal. Results for years before the effective date must be the same.")
        with st.spinner("Calculating scenarios ..."):
            df = regression(kb, kb2, tuple(store.installed_policies()))
        st.dataframe(df.style.apply(lambda r: ["background-color: #fff4d6" if r["Result"] == "changed" else ""] * len(r),
                                    axis=1), hide_index=True, width="stretch")
        affected = affected_policies(delta, kb2)
        st.markdown("**Company policies affected**", help=g.tip("dampak"))
        if affected:
            for pol, rid, facts in affected:
                ui.html(f"<div class='rule company'><b>{pol}</b> · rule <code>{rid}</code> reads or produces a "
                        f"value that changes: {', '.join(d.fact_label(f) for f in facts)}. Check whether this policy "
                        "still fits.</div>")
        else:
            st.caption("No installed company policy reads a value that changes.")
    st.divider()
    c1, c2 = st.columns([1, 2])
    reviewer = c1.text_input("Reviewer name", "Admin", key="mg_reviewer")
    note = c2.text_input("Note", key=f"mg_note_{pid}", placeholder="optional")
    b = st.columns(4)
    if b[0].button("Approve", type="primary", icon=":material/check:", width="stretch", disabled=kb2 is None):
        store.approve(pid, names[pid].split(" (")[0], delta, reviewer, note)
        st.session_state.mg_open = None
        st.toast("Approved. Knowledge base updated.")
        st.rerun()
    if b[1].button("Edit", icon=":material/edit:", width="stretch"):
        st.session_state.mg_edit = pid
    if b[2].button("Ask AI to fix", icon=":material/auto_fix_high:", width="stretch"):
        st.session_state.mg_fix = pid
    if b[3].button("Reject", icon=":material/close:", width="stretch"):
        store.reject(pid, names[pid], note or "-")
        st.session_state.mg_open = None
        st.rerun()
    if st.session_state.get("mg_fix") == pid:
        fix_panel(pid, delta)
    if st.session_state.get("mg_edit") == pid:
        with st.container(border=True):
            text = st.text_area("Proposal (JSON)", json.dumps(delta, ensure_ascii=False, indent=1), height=300,
                                key=f"mg_json_{pid}")
            if st.button("Save edits", icon=":material/save:"):
                try:
                    new = json.loads(text)
                    store.set_fixed(pid, new, "disunting manual", "Admin")
                    st.session_state.mg_edit = None
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {e}")


def fix_panel(pid, delta):
    """The reviewer's note goes to the AI with the old proposal and the document text (the research's repair round),
    and the new version is checked with gates G1-G5 again. In the demo, a research document can also take the
    research's reference answer instead (free, labelled as a simulation)."""
    with st.container(border=True):
        prefill = (st.session_state.get("mg_prefill") or {}).pop(pid, None)    # a note written through the assistant
        if prefill:
            st.session_state[f"mg_fixnote_{pid}"] = prefill
        note = st.text_area("Note for the AI", key=f"mg_fixnote_{pid}",
                            placeholder="e.g. The DTP income limit of Rp10 million is calculated from salary and fixed "
                                        "allowances only; leave out the company car (natura).")
        real = ai.can_repair(pid, delta)
        ok, why = ai.ready("perbaikan")
        reference = store.DEMO and not store.pending_by_id().get(pid, {}).get("upload") and store.gold_delta(pid)
        options = (["Real AI"] if real else []) + (["Research reference answer (simulation, free)"] if reference else [])
        if not options:
            st.caption("This proposal did not come from the AI (a draft or an edit), so the AI cannot repair it. Edit it "
                       "directly, or ask the assistant to make a new draft.")
            return
        how = st.radio("How to fix it", options, horizontal=True, key=f"mg_fixhow_{pid}")
        if how == "Real AI":
            st.caption(f"One repair round with {ai.llm.MAIN_MODEL}, then G1–G5 run again. Estimated "
                       f"USD 0.1–0.4. {ai.budget_text('perbaikan')}")
            if not ok:
                st.warning(f"The AI cannot run: {why}.", icon=":material/payments:")
                return
        if st.button("Send to AI", icon=":material/send:", disabled=not note.strip()):
            if how == "Real AI":
                with st.spinner("The AI is repairing the proposal and checking it again ..."):
                    try:
                        new, passed, log, cost = ai.repair(pid, delta, note.strip())
                    except Exception as e:  # noqa: BLE001 - shown to the user
                        st.error(f"AI failed: {type(e).__name__}: {str(e)[:300]}")
                        return
                st.session_state[f"mg_fixlog_{pid}"] = (passed, log, cost)
                if new is None:
                    st.error("The AI did not produce a usable proposal: " + "; ".join(log.values())[:300])
                    return
            else:
                store.set_fixed(pid, reference, note.strip(), "jawaban acuan penelitian (simulasi)")
            st.session_state.mg_fix = None
            st.rerun()


# ---------------------------------------------------------------- add, change, revoke
def _source(key):
    c1, c2 = st.columns(2)
    doc = c1.text_input("Source document", key=f"{key}_doc", placeholder="e.g. PMK 168/2023")
    prov = c2.text_input("Article (pasal)", key=f"{key}_prov", placeholder="e.g. Pasal 2 ayat (1)")
    quote = st.text_input("Quoted sentence", key=f"{key}_quote", help=g.tip("kutipan"))
    return doc, prov, quote


def tab_edit():
    with st.container(border=True):
        g.md(f"**Ask the AI to do it**: describe the change in plain words; the {g.term('asisten', 'AI assistant')} "
             "drafts it and sends it to Review.")
        c1, c2 = st.columns([4, 1])
        ask = c1.text_input("Permintaan", key="mg_ask", label_visibility="collapsed",
                            placeholder="e.g. JP wage cap 2027 becomes Rp11,600,000 · Revoke the gift rule")
        if c2.button("Ask AI", icon=":material/smart_toy:", width="stretch") and ask:
            assistant.open_with(ask)
            st.rerun()
    st.markdown("**Or do it manually**")
    what = st.segmented_control("Type", ["New number", "New rule", "Change a rule", "Revoke a rule"],
                                default="New number", key="mg_what", label_visibility="collapsed")
    if what == "New number":
        names = sorted({r.name for r in d.kb().records if r.kind == "parameter" and r.value_type in ("money", "rate")},
                       key=d.fact_label)
        name = st.selectbox("Number", names, format_func=d.fact_label, key="mg_p")
        cur = drafts.current_param(name)
        cv = d.money(cur.value) if cur.value_type == "money" else d.pct(cur.value)
        st.caption(f"Currently **{cv}**, effective since {d.tgl(cur.valid_from)} ({d.short_doc(cur.source[0].document)}).")
        c1, c2 = st.columns(2)
        value = c1.number_input("New value" + (" (Rp)" if cur.value_type == "money" else " (decimal, e.g. 0.01)"),
                                0.0, 1e11, None, key="mg_pv")
        start = c2.date_input("Effective from", date(store.TODAY.year + 1, 1, 1), key="mg_ps")
        doc, prov, quote = _source("mg_pp")
        if value is not None and st.button("Send to Review", type="primary", icon=":material/send:"):
            v = int(value) if cur.value_type == "money" else value
            delta = drafts.new_value(name, v, start, doc, prov, quote)
            store.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
            st.success("Sent to Review.")
    elif what == "New rule":
        facts = sorted(d.facts(), key=d.fact_label)
        c1, c2 = st.columns(2)
        produces = c1.selectbox("Value to calculate", facts, format_func=d.fact_label, key="mg_rf")
        company = c2.radio("Applies to", ("Government regulation", "Company policy"), key="mg_rl") != "Government regulation"
        policy = st.text_input("Policy code", "PRS-DEMO", key="mg_rpol") if company else None
        cond = st.text_input("Applies if (optional)", key="mg_rc", placeholder="e.g. gross_income > 10000000")
        expr = st.text_input("Formula", key="mg_re", placeholder="e.g. 50000 * hr('days_present') + income('other_regular')")
        with st.expander("Names of the values and data you can use"):
            st.dataframe(pd.DataFrame([{"Name": f, "Meaning": d.fact_label(f)} for f in facts]), hide_index=True,
                         height=200, width="stretch")
            st.caption("Case data is read with income('…'), benefit('…'), hr('…'), employee('…'), employer('…'). "
                       "New data read through hr('…') automatically becomes a column in the calculator.")
        c1, c2 = st.columns(2)
        start = c1.date_input("Effective from", date(store.TODAY.year + 1, 1, 1), key="mg_rs")
        end = c2.date_input("Effective until (leave empty for no end)", None, key="mg_ru")
        doc, prov, quote = _source("mg_rp")
        if expr:
            ui.html(f"<div class='rule{' company' if company else ''}'><b>{d.fact_label(produces)}</b> = {d.readable(expr)}"
                    + (f" <i>if {d.readable(cond)}</i>" if cond else "") + "</div>")
            if st.button("Send to Review", type="primary", icon=":material/send:", key="mg_rsend"):
                delta = drafts.new_rule(produces, expr, cond, start, end, company, policy, doc, prov, quote)
                store.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
                st.success("Sent to Review.")
    else:
        rules = {r.id: r for r in d.kb().view(store.TODAY).rules.values()
                 if not d.is_input_convention(r) and (r.valid_until is None or r.valid_until >= store.TODAY)}
        ids = sorted(rules, key=lambda i: d.fact_label(rules[i].produces))
        rid = st.selectbox("Rule", ids, key="mg_cr", format_func=lambda i: f"{d.fact_label(rules[i].produces)} · "
                           f"{d.short_doc(rules[i].source[0].document) if rules[i].source else ''}")
        r = rules[rid]
        ui.html(f"<div class='rule'><b>{d.fact_label(r.produces)}</b><br><b>Formula:</b> {d.readable(r.expression)}<br>"
                f"<span class='muted'>Effective {d.tgl(r.valid_from)}{' until ' + d.tgl(r.valid_until) if r.valid_until else ''}"
                f"</span></div>")
        if what == "Revoke a rule":
            g.md(f"{g.term('pencabutan', 'Revoking')} = giving an end date. The rule is not deleted, so past "
                 "calculations stay the same.")
            end = st.date_input("No longer effective after", date(store.TODAY.year, 12, 31), key="mg_ce")
            others = [x for x in d.kb().view(store.TODAY).rules.values() if x.produces == r.produces and x.id != r.id
                      and (x.valid_until is None or x.valid_until > end)]
            readers = [x.id for x in d.kb().view(store.TODAY).rules.values()
                       if r.produces in d.expr_text(x.expression) + d.expr_text(x.condition or "")]
            if not others:
                st.warning(f"After {d.tgl(end)} no other rule calculates *{d.fact_label(r.produces)}*, "
                           f"yet {_pl(len(readers), 'rule')} {'uses' if len(readers) == 1 else 'use'} it. Add a "
                           "replacement, or make sure the regulation really removes it.", icon=":material/warning:")
            doc, prov, quote = _source("mg_cp")
            if st.button("Send to Review", type="primary", icon=":material/send:", key="mg_csend"):
                delta = drafts.revoke(r, end, doc, prov, quote)
                store.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
                st.success("Sent to Review.")
        else:
            expr = st.text_input("New formula", d.expr_text(r.expression), key="mg_ue")
            start = st.date_input("Effective from", date(store.TODAY.year + 1, 1, 1), key="mg_us",
                                  help="The old version is still used for earlier months.")
            doc, prov, quote = _source("mg_up_")
            if expr != d.expr_text(r.expression) and st.button("Send to Review", type="primary", icon=":material/send:",
                                                               key="mg_usend"):
                delta = drafts.change_rule(r, expr, start, doc, prov, quote)
                store.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
                st.success("Sent to Review.")


# ---------------------------------------------------------------- company policies
def tab_policy():
    pols = store.installed_policies()
    g.md(f"Installed {g.term('kebijakan perusahaan', 'company policies')} are used by the calculator when selected. "
         "Company rules must not conflict with regulations; the system checks this.")
    if pols:
        for pid, title in pols.items():
            with st.expander(f"{pid} · {title}"):
                for r in d.kb().view(store.TODAY).rules.values():
                    if r.layer == "company" and r.policy == pid:
                        ui.html(f"<div class='rule company'><b>{d.fact_label(r.produces)}</b>: {d.readable(r.expression)}"
                                f"<br><span class='muted'>effective {d.tgl(r.valid_from)}"
                                f"{' until ' + d.tgl(r.valid_until) if r.valid_until else ''}</span></div>")
                found = inputs.discover(store.TODAY.year, pid)
                new_cols = [inputs.label(k) for k, e in found.items() if e["layer"] == "company"]
                if new_cols:
                    st.caption("Data the calculator asks for because of this policy: " + ", ".join(new_cols))
    else:
        st.caption("No company policy is installed yet. Approve SP14 in New documents, or create one from an example "
                   "below.")
    st.markdown("**Create from an example**")
    c1, c2 = st.columns(2)
    pid = c1.text_input("Policy code", "PRS-DEMO", key="mg_pol_id")
    tpl = c2.selectbox("Example", ["Meal allowance per day present", "THR as a multiple of wages", "Annual bonus"],
                       key="mg_pol_tpl")
    start = st.date_input("Effective from", date(store.TODAY.year + 1, 1, 1), key="mg_pol_start")
    if tpl == "Meal allowance per day present":
        n = st.number_input("Rupiah per day present", 0, 1_000_000, 50_000, 5_000, key="mg_pol_n")
        delta = drafts.meal_policy(int(n), pid, start)
    elif tpl == "THR as a multiple of wages":
        n = st.number_input("Wage multiple", 0.5, 5.0, 1.5, 0.5, key="mg_pol_t")
        delta = drafts.thr_policy(n, pid, start)
    else:
        c1, c2 = st.columns(2)
        n = c1.number_input("Percent of base salary", 1, 500, 100, key="mg_pol_b")
        m = c2.selectbox("Month paid", range(1, 13), 11, format_func=lambda x: d.MONTHS[x - 1], key="mg_pol_m")
        delta = drafts.bonus_policy(n, m, pid, start)
    for el in delta["add"]:
        card(el, d.kb())
    if st.button("Send to Review", type="primary", icon=":material/send:", key="mg_pol_send"):
        store.add_draft(delta["delta_id"], delta["document"]["title"], delta, "contoh")
        st.success("Sent to Review.")


# ---------------------------------------------------------------- check and history
@st.cache_data
def _health(signature, today):
    kb = store.kb()
    out = []
    by_name = {}
    for r in kb.records:
        if r.kind == "parameter":
            by_name.setdefault(r.name, []).append(r)
    for name, vs in by_name.items():
        years = sorted({v.valid_from.year for v in vs})
        if len(years) >= 3 and years[-1] - years[-2] == 1 and years[-1] < today.year + 1:
            out.append(("warn", f"{d.fact_label(name)} changes every year; the {years[-1] + 1} value is missing.",
                        f"Latest: {d.short_doc(vs[-1].source[0].document)} ({years[-1]})."))
    ending = {}
    for r in kb.view(today).rules.values():
        if r.valid_until and r.valid_until >= today - timedelta(days=400) and r.valid_until.year <= today.year:
            ending.setdefault((r.valid_until, d.topic_of(r)), []).append(r)
    for (until, topic), rs in sorted(ending.items())[-4:]:
        out.append(("info", f"{topic}: {_pl(len(rs), 'rule')} {'ends' if len(rs) == 1 else 'end'} {d.tgl(until)}.",
                    "If extended, upload the new regulation in New documents."))
    found = inputs.discover(today.year, None)
    undefined = [k for k in found if not inputs.has_def(k)]
    if undefined:
        out.append(("warn", f"Data read by rules without a definition (label and explanation): {len(undefined)}.",
                    ", ".join(undefined[:6])))
    for f in static.check(kb, today).findings[:8]:
        out.append(("error" if f.severity == "error" else "warn", f"{f.kind}: {f.detail}", ", ".join(f.ids)))
    return out


def tab_health():
    g.md("Routine checks of the knowledge base content, so problems are found before a calculation goes wrong.")
    items = _health(store.signature(), store.TODAY)
    for level, title, detail in items:
        icon = {"warn": ":material/schedule:", "info": ":material/event:", "error": ":material/error:"}[level]
        (st.warning if level == "warn" else st.error if level == "error" else st.info)(f"**{title}**  \n{detail}", icon=icon)
    if not items:
        st.success("No findings.")


def tab_history():
    s = store.load()
    base = store.base()
    ui.html(f"<div class='rule'><b>{'Initial state of the demo' if store.DEMO else 'Research reference knowledge base'}</b> · "
            f"{_pl(len(base.updates), 'update')}, known up to {store.base_label()}.</div>")
    for i, a in enumerate(s["approved"]):
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"**v{i + 1}** · {a['title']} · approved {a['when']} by {a['reviewer']}"
                    + (f"  \n_{a['note']}_" if a.get("note") else ""))
        if c2.button("Roll back to before this", key=f"rb_{i}", icon=":material/history:", width="stretch",
                     help="This update and the ones after it are undone; the document goes back to waiting for review."):
            store.rollback(i)
            st.rerun()
    if s["log"]:
        st.markdown("**Activity log**")
        for e in s["log"][:20]:
            st.caption(f"{e['when']} · {e['what']}")


def show():
    st.session_state.page_ctx = "kelola"
    st.title("Knowledge base management")
    g.md(f"Add, change, revoke, and {g.term('review')} the system's knowledge. You can do it by hand, or ask the "
         f"{g.term('asisten', 'AI assistant')} (button at the bottom right) to help check and do it. Nothing "
         "changes until you approve.")
    s = store.load()
    n_review = len({p["id"] for p in store.pending(s) if store.status(p["id"], s) == "review"}
                   | {x["id"] for x in s["drafts"]})
    tabs = st.tabs(["New documents", f"Review ({n_review})", "Add, change, revoke", "Company policy", "KB check",
                    "Version history"])
    with tabs[0]:
        tab_documents()
    with tabs[1]:
        tab_review()
    with tabs[2]:
        tab_edit()
    with tabs[3]:
        tab_policy()
    with tabs[4]:
        tab_health()
    with tabs[5]:
        tab_history()
