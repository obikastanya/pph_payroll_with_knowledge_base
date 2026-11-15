"""Knowledge base management page: new documents read by the AI, review of proposed changes (approve, edit, ask the
AI to fix them with your notes, reject), add / change / revoke by hand or through the assistant, company policies,
a check of the knowledge base, and the version history. Nothing changes the knowledge base before it is approved.
"""
import json
import re
from datetime import date, timedelta

import pandas as pd
import streamlit as st

import calculator
import common
import state
import workflow
from pph21kbs import config, consistency, digest, documents, graph, pipeline
from pph21kbs.kb import apply_delta, validate_delta_json

# The checks a proposal goes through, in the order they run
GATES = {"G1": "Correct format and structure", "G6": "The payroll data it reads exists",
         "G2": "Quotes, numbers, and dates are in the document", "G3": "No conflict with other rules",
         "G4": "Past calculations do not change", "G5": "Every part of the proposal has an effect"}
ORIGINS = {"manual": "written by hand", "upload": "uploaded file", "template": "from a template",
           "assistant": "from the assistant", "sample": "sample policy", "model": "from the AI"}
# How an update can touch a company policy (the kinds returned by pipeline.detect)
IMPACT_KINDS = {
    "a": "One of its rules uses a value that this update changes.",
    "b": "One of its rules calculates a value that a rule of this update also calculates.",
    "c": "A rule of this update that must be followed calculates the same value as one of its rules, or a check in "
         "this update uses a value that one of its rules calculates.",
    "d": "One of its rules takes the place of a regulation rule whose result this update changes, through a number, "
         "a table, or a rule it depends on.",
}


LEVEL_NAMES = {"core": "about PPh 21: sent word for word", "general": "general: sent as its summary",
               "none": "not about PPh 21: left out"}
FALLBACK = "the parts with the most PPh 21 terms are sent instead"


def _title(pid):
    p = state.pending_by_id().get(pid)
    return state.doc_title(p["doc"]) if p else pid


def _at(delta):
    """The date a proposal is checked at: its issue date (today when it has none)."""
    issued = (delta.get("document") or {}).get("issued")
    return max(date.fromisoformat(issued) if issued else state.TODAY, date(2013, 1, 1))


# ====================================================================================================================
# New documents
# ====================================================================================================================
def _ai_steps(pid, stat):
    """The steps the AI went through for a document, as shown in the document list."""
    r = state.run(pid) or {}
    drafts = r.get("drafts") or []
    n, passed = len(drafts), sum(1 for c in drafts if c.get("passed"))
    groups = r.get("groups") or []
    why = workflow.stop_reason(r)
    steps = [("Read the text", "done")]
    if why == "budget":
        if r.get("relevance"):
            steps.append(("Relevant?", "done"))
        return steps + [("Stopped: the spending limit was reached", "fail")]
    if stat == "not_relevant":
        return steps + [("Relevant? No", "skip")]
    if why == "unconfirmed":
        return steps + [("Relevant? The AI's reason is not in the text", "skip")]
    steps += [("Relevant?", "done"), (f"Write {n} drafts", "done"),
              (f"Checks: {passed}/{n} passed", "done" if passed else "fail")]
    if why == "none_passed":
        return steps + [("No draft passed the checks", "skip")]
    if why == "disagree":
        return steps + [(f"Do the drafts agree? No: {len(groups)} different results", "skip")]
    steps.append((f"Do the drafts agree? {max(map(len, groups)) if groups else 0}/{passed} the same", "done"))
    label = {"approved": ("Approved", "done"), "rejected": ("Rejected", "fail")}.get(stat, ("Your review", "now"))
    return steps + [label]


STOP_TEXT = {
    "budget": "The AI stopped because the spending limit was reached, so it wrote no proposal.",
    "unconfirmed": "The AI thought this document does not change the calculation, but the reason it gave is not in "
                   "the document text, so it does not decide.",
    "none_passed": "None of the AI's drafts passed the automatic checks, so the AI proposes nothing and does not "
                   "guess.",
    "disagree": "The AI's drafts give different results, so {term} and does not guess.",
}


def _ai_detail(pid):
    r = state.run(pid)
    rel = (r.get("relevance") or {}).get("output") or {}
    st.markdown(f"**Why the AI thinks it matters (or not):** _{rel.get('reason', '-')}_")
    sel = r.get("selection") or {}
    st.caption("Parts of the document read: " + ", ".join(f"{k} ({v.get('tokens', 0):,} tokens)"
                                                          for k, v in sel.items()))
    for dg in (v["digest"] for v in sel.values() if v.get("digest")):
        c = dg["parts"]
        note = (f"Mapped by {dg['model']}: {c['core']} parts about PPh 21, {c['general']} general, {c['none']} not "
                "about PPh 21.")
        if dg.get("failed_calls"):
            note += f" {dg['failed_calls']} mapping call(s) failed; their parts were sent word for word."
        if not dg.get("used"):
            note += f" The map marks no part as about PPh 21, so {FALLBACK}."
        st.caption(note)
    rows = []
    for c in r.get("drafts", []):
        log = c.get("gate_log") or {}
        rows.append({"Draft": c.get("n"), "Passed": "yes" if c.get("passed") else "no",
                     "Fixed automatically": "yes" if c.get("repaired") else "-",
                     **{GATES[k]: ("✓" if log.get(k) == "pass" else "✗" if log.get(k) else "-") for k in GATES},
                     "Note": (c.get("error") or "")[:80]})
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    groups = r.get("groups") or []
    if groups:
        st.caption("Drafts that give the same results: "
                   + " · ".join("drafts " + ", ".join(map(str, g)) for g in groups)
                   + f". Chosen: draft {r.get('selected') or '-'}. AI cost: USD {r.get('cost_usd', 0):.2f}.")


def _upload_form(s):
    """The upload form. Enter in a field does not send it, and the fields are kept when it is sent with a mistake; the
    form starts empty again (new widget keys) only after a document was added."""
    n = st.session_state.get("mg_up_n", 0)
    with st.container(border=True):
        st.markdown("**Upload a document**")
        with st.form(f"mg_upload_{n}", clear_on_submit=False, enter_to_submit=False, border=False):
            up = st.file_uploader("PDF, TXT, or JSON", type=["pdf", "txt", "json"], key=f"mg_up_{n}",
                                  help="The AI reads a PDF or TXT file and proposes an update. Scanned PDFs are read "
                                       "with OCR. A JSON file is a finished update: it goes straight to Review.")
            c1, c2, c3 = st.columns([2.2, 1, 1.3])
            title = c1.text_input("Document title", placeholder="e.g. PMK 12/2027 on ...")
            issued = c2.date_input("Issue date", state.TODAY, help="The date the document was signed or published.")
            kind = c3.radio("The document is a", ("regulation", "policy"), horizontal=True,
                            format_func={"regulation": "Government regulation", "policy": "Company policy"}.get,
                            help=common.tip("regulation") + "\n\n" + common.tip("company policy"))
            ocr = st.checkbox("Read every page again with OCR", help="For a PDF whose text comes out garbled.")
            sent = st.form_submit_button("Add to the document list", type="primary", icon=":material/upload:")
        _sample_picker()
        if not sent:
            return
        if not up:
            st.error("Choose a file first.")
            return
        if up.name.lower().endswith(".json"):
            try:
                delta = json.loads(up.getvalue())
                validate_delta_json(delta)
                state.add_draft(delta["delta_id"], (delta.get("document") or {}).get("title", up.name), delta,
                                "upload")
            except Exception as e:  # noqa: BLE001 - shown to the user
                st.error(f"The JSON file cannot be used: {str(e)[:250]}")
                return
            st.session_state.mg_up_n = n + 1
            _sent_to_review(delta["delta_id"])
        if not title.strip():
            st.error("Enter the document title first.")
            return
        with st.spinner("Reading the document text (PDF: layout, tables, and OCR; about 5 seconds per page) ..."):
            item = workflow.upload(up, title.strip(), issued, kind, force_ocr=ocr)
        state.add_inbox(item)
        st.session_state.mg_added = item["title"]      # shown above the list it is now in
        st.session_state.mg_up_n = n + 1                # a fresh, empty form
        st.rerun()


SAMPLES = config.ROOT / "examples" / "documents" / "samples.json"
KIND_NAMES = {"regulation": "government regulation", "policy": "company policy"}


class _SampleFile:
    """A sample document in the shape of an uploaded file, so it goes through the same upload path."""

    def __init__(self, name, data):
        self.name, self._data = name, data

    def getvalue(self):
        return self._data


def sample_documents():
    """({id: entry}, [entries left out]) of the sample documents in examples/documents/samples.json. A document that is
    not shipped with this folder (its text is copyrighted) is offered only when its file exists on this computer. Both
    are in issue-date order, oldest first."""
    entries = json.loads(SAMPLES.read_text(encoding="utf-8"))["documents"] if SAMPLES.exists() else []
    entries = sorted(entries, key=lambda e: e["issued"])
    found, missing = {}, []
    for e in entries:
        path = (config.ROOT / e["file"]).resolve()
        if path.exists():
            found[e["id"]] = {**e, "path": path}
        else:
            missing.append(e)
    return found, missing


def sample_text(doc_id):
    """The text of a sample document or sample policy, with page marks in the form the app reads, or None."""
    shipped = config.ROOT / "examples" / "documents" / f"{doc_id}.txt"
    entry = sample_documents()[0].get(doc_id)
    path = shipped if shipped.exists() else entry["path"] if entry else None
    if path is None:
        return None
    return re.sub(r"^=== PDF hlm\. (\d+) ===$", r"=== page \1 ===", path.read_text(encoding="utf-8"), flags=re.M)


def _sample_picker():
    """Sample documents that can be added without a file: regulations issued after the starting knowledge base, and
    the company's labour agreement when its text is on this computer, listed by issue date (oldest first)."""
    with st.expander("No file at hand? Use a sample document", icon=":material/folder_open:"):
        found, missing = sample_documents()
        if found:
            pick = st.selectbox("Sample document", list(found), key="mg_sample_pick",
                                format_func=lambda k: f"{found[k]['title']} · issued "
                                                      f"{state.fmt_date(date.fromisoformat(found[k]['issued']))} · "
                                                      f"{KIND_NAMES[found[k]['kind']]}")
            e = found[pick]
            st.caption(f"{KIND_NAMES[e['kind']].capitalize()}, issued "
                       f"{state.fmt_date(date.fromisoformat(e['issued']))}. It is added to the document list like an "
                       "uploaded file; the AI reads it only when you run it.")
            if st.button("Use this sample", key="mg_sample_use", icon=":material/note_add:"):
                text = sample_text(pick)
                item = workflow.upload(_SampleFile(f"{pick}.txt", text.encode("utf-8")), e["title"],
                                       date.fromisoformat(e["issued"]), e["kind"])
                state.add_inbox(item)
                st.session_state.mg_added = item["title"]
                st.rerun()
        for e in missing:
            st.caption(f"{e['title']} is not included: its text is copyrighted. It is offered here when the research "
                       "data set is next to this folder.")


def _waiting(p):
    """An uploaded document the AI has not read yet: its text, and the button that runs the AI."""
    pages, tables = workflow.text_stats(p)
    chars = sum(len(t.strip()) for _, t in pages)
    st.caption(f"{len(pages)} pages · {chars:,} characters · {len(tables)} tables · issued "
               f"{state.fmt_date(date.fromisoformat(p['issued']))}")
    if chars < 40 * max(1, len(pages)):
        st.warning("Very little text came out. Check the scan, or upload it again with OCR.",
                   icon=":material/document_scanner:")
    with st.expander("See the document text"):
        _document_text(p, pages)
    _run_ai(p)


def _document_text(p, pages):
    record = digest.load(p["doc"])
    sent, mapped, full = st.tabs(["Sent to the AI", "AI map of the document", "Full text"])
    with sent:
        _sent_text(p, record)
    with mapped:
        _map_table(record)
    with full:
        st.caption(f"{len(pages)} pages, as extracted from the file.")
        with st.container(height=480):
            st.code("\n\n".join(f"--- page {n} ---\n{t}" for n, t in pages), language=None, wrap_lines=True)


def _sent_text(p, record):
    if record is None and workflow.digest_on():
        st.caption(f"Chosen when the AI runs: first {config.DIGEST_MODEL} maps every part of the document. Parts "
                   "about PPh 21 are sent word for word, general parts as one-line summaries, and the rest is left "
                   "out.")
        return
    try:
        view = state.kb().view(date.fromisoformat(p["issued"]))
        cfg = pipeline.Config(use_stored_map=True)
        text, info = pipeline.document_text([{"id": p["doc"], "title": p["title"]}], view, cfg)
    except Exception as e:  # noqa: BLE001 - shown to the user
        st.caption(f"The selection cannot be shown: {type(e).__name__}: {e}")
        return
    sel = info[p["doc"]]
    used = (sel.get("digest") or {}).get("used")
    notes = [f"About {sel['tokens']:,} tokens"
             + (" (over the usual size; nothing about PPh 21 is cut)." if sel.get("over_budget") else
                f" of the {cfg.digest_budget if used else cfg.budget_tokens:,} allowed.")]
    if used:
        notes.append("Chosen from the AI map.")
    elif record is not None:
        notes.append(f"The AI map marks no part as about PPh 21, so {FALLBACK}.")
    if sel["dropped"]:
        notes.append(f"Not sent: {len(sel['dropped'])} parts; the AI is told they exist.")
    if documents.tables_of(p["doc"]):
        notes.append("Annex tables are sent as descriptions; the rules refer to the extracted tables.")
    st.caption(" ".join(notes))
    with st.container(height=480):
        st.code(text, language=None, wrap_lines=True)


def _map_table(record):
    if record is None:
        st.caption("Not mapped yet." + (" The map is made when the AI runs." if workflow.digest_on()
                                        else f" Mapping is off or has no OpenAI key: {FALLBACK}."))
        return
    c = digest.counts(record)
    st.caption(f"Made by {record['model']} in {record['calls']} call(s), USD {record['cost_usd']:.3f}: {c['core']} "
               f"parts about PPh 21, {c['general']} general, {c['none']} not about PPh 21. A short opening and closing "
               "are always sent.")
    rows = [{"Part": u["label"], "Characters": u["chars"],
             "Level": "always sent" if digest.always(u) else LEVEL_NAMES[digest.level(record, u["key"])],
             "Summary": (record["entries"].get(u["key"]) or {}).get("summary", "")}
            for u in record["units"]]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=480)


def _run_ai(p, again=False):
    """The choice of the number of drafts, the cost, the confirmation, and the button that runs the AI."""
    ok, why = workflow.ready("acquisition")
    c1, c2 = st.columns([1, 2])
    m = c1.radio("Number of drafts", (3, 1), horizontal=True, key=f"mg_m_{p['id']}",
                 help=common.tip("draft") + " One draft costs less, but there is nothing to compare it with.")
    mapping = (f"First {config.DIGEST_MODEL} maps the document (about USD 0.01–0.6, depending on length; "
               f"{workflow.budget_text('digest')}). " if workflow.digest_on() and digest.load(p["doc"]) is None
               else "")
    c2.caption(f"{mapping}Claude ({config.MAIN_MODEL}) reads the document: it decides whether it matters for PPh 21, "
               "writes the drafts, checks them, fixes a failed draft once, and compares the drafts. About USD "
               f"0.1–0.5 per document (3 drafts). {workflow.budget_text('acquisition')}")
    if not ok:
        st.warning(f"The AI cannot run: {why}.", icon=":material/payments:")
        return
    sure = st.checkbox("I understand this uses API credit", key=f"mg_ok_{p['id']}")
    if st.button("Run the AI again" if again else "Run the AI", type="primary", icon=":material/smart_toy:",
                 key=f"mg_run_{p['id']}", disabled=not sure):
        with st.spinner("The AI is reading the document and writing a proposal (a few minutes) ..."):
            try:
                res = workflow.read(p, m=m)
                st.toast(f"Done. Cost USD {res.get('cost_usd', 0):.3f}.")
            except Exception as e:  # noqa: BLE001 - shown to the user
                st.error(f"The AI failed: {type(e).__name__}: {str(e)[:300]}")
                return
        st.rerun()


ACTION_NEEDED = ("awaiting_ai", "uncertain", "budget_exhausted")     # document statuses that wait for the user


def tab_documents():
    """The ways to add a document (upload or a sample) first, then the documents added in the app (newest on top)
    under a heading of their own."""
    s = state.load()
    items = state.pending(s)
    st.markdown("#### Add a document")
    _upload_form(s)
    st.divider()
    st.markdown(f"#### Your documents ({len(items)})")
    added = st.session_state.pop("mg_added", None)
    if added:
        st.success(f"**{added}** is added below, waiting for the AI. Check its text, then run the AI on its card.",
                   icon=":material/check_circle:")
    if not items:
        st.caption("No documents yet. Upload a regulation or a company policy above, or use a sample document.")
        return
    st.caption("Newest first. The AI reads a document only when you run it on the document's card; after that it goes "
               "to Review.")
    for p in reversed(items):
        _document_card(p, s)


def _document_card(p, s):
    stat = state.status(p["id"], s)
    reg = p["kind"] == "regulation"
    with st.container(border=True):
        layer = (common.badge("government regulation", "blue") if reg
                 else common.badge("company policy", "orange"))
        head, act = st.columns([6, 1])
        with head:
            common.html(f"{common.status_badge(stat)}{layer}<b>{_title(p['id'])}</b>")
        if stat != "approved":
            with act.popover("Remove", icon=":material/delete:", width="stretch"):
                st.markdown(f"Remove **{p['title']}** from the list?")
                st.caption("Its text and the AI's work on it are deleted. The AI cost already spent stays counted. "
                           "The knowledge base does not change.")
                if st.button("Yes, remove", type="primary", key=f"mg_rm_{p['id']}"):
                    state.remove_document(p["id"])
                    st.toast(f"Removed: {p['title']}", icon=":material/delete:")
                    st.rerun()
        if stat == "awaiting_ai":
            _waiting(p)
            return
        common.flow(_ai_steps(p["id"], stat))
        if p.get("cost_usd"):
            st.caption(f"AI cost of this document: USD {p['cost_usd']:.3f}")
        if stat == "review":
            c1, _, _ = st.columns(3)
            if c1.button("Review", key=f"rv_{p['id']}", icon=":material/rate_review:", width="stretch"):
                st.session_state.mg_open = p["id"]
                st.toast("Open the Review tab.")
        if stat in ("uncertain", "budget_exhausted"):
            why = workflow.stop_reason(state.run(p["id"])) or ("budget" if stat == "budget_exhausted"
                                                               else "disagree")
            common.md(STOP_TEXT[why].format(term=common.term("AI not sure", "the AI is not sure")))
            st.caption("You can run the AI again, or write the update by hand in the Company policies tab or the "
                       "Add, change, revoke tab.")
            _run_ai(p, again=True)
        if stat == "not_relevant":
            common.md(f"The AI found this document not {common.term('relevant')} to PPh 21 for permanent "
                      "employees. Nothing changes.")
        if state.run(p["id"]):
            with st.expander("See what the AI did"):
                _ai_detail(p["id"])
        if st.toggle("Show the document text", key=f"mg_text_{p['id']}"):
            _document_text(p, workflow.text_stats(p)[0])


# ====================================================================================================================
# Review
# ====================================================================================================================
def _prev(rec_id, kb):
    found = [r for r in kb.records if r.id == rec_id]
    return max(found, key=lambda r: r.seq) if found else None


def _iso(x):
    return state.fmt_date(date.fromisoformat(str(x))) if x else "-"


def card(el, kb):
    kind = el.get("kind")
    src = (el.get("source") or [{}])[0]
    quote = f"<div class='quote'>“{src.get('quote', '')}” · {src.get('provision', '')}</div>"
    period = f"valid from {_iso(el.get('valid_from'))}" + (f" to {_iso(el['valid_until'])}" if el.get("valid_until")
                                                           else "")
    old = _prev(el["id"], kb)
    if kind == "parameter":
        title = state.fact_label(el.get("name", ""))
        same = [r for r in kb.records if r.kind == "parameter" and r.name == el.get("name") and r.id != el["id"]]
        ref = old or (max(same, key=lambda r: r.valid_from) if same else None)
        fmt = lambda v, t: (state.money(int(float(v))) if t == "money"  # noqa: E731
                            else (state.pct(float(v)) if t == "rate" else str(v)))
        new = fmt(el.get("value"), el.get("value_type"))
        oldv = fmt(ref.value, ref.value_type) if ref else None
        body = ((f"<span class='diff-old'>{oldv}</span> → " if oldv and oldv != new else "")
                + f"<span class='diff-new'>{new}</span>")
        what = "Number changed" if old else ("New number" if not oldv else "New number (the old value ends)")
    elif kind == "rule":
        title = state.fact_label(el["produces"])
        body = f"<b>Formula:</b> {state.readable(el['expression'])}"
        if el.get("condition"):
            body = f"<b>If:</b> {state.readable(el['condition'])}<br>" + body
        if old and state.expr_text(old.expression) == el["expression"]:
            what = "Validity changed"
            body += (f"<br><span class='diff-old'>to {state.fmt_date(old.valid_until) if old.valid_until else 'no end'}"
                     f"</span> → <span class='diff-new'>to "
                     f"{_iso(el.get('valid_until')) if el.get('valid_until') else 'no end'}</span>")
        elif old:
            what = "Rule changed"
            body = f"<span class='diff-old'>{state.readable(old.expression)}</span><br>" + body
        else:
            what = "New rule" + (" (company)" if el.get("layer") == "company" else "")
            # the rule already in the knowledge base for the same value, so the reviewer can compare
            same = [r for r in kb.view(state.TODAY).rules.values() if r.produces == el["produces"]
                    and r.layer == el.get("layer", "regulation") and not state.is_input_convention(r)]
            if same:
                prev = max(same, key=lambda r: r.valid_from or date.min)
                until = " to " + state.fmt_date(prev.valid_until) if prev.valid_until else ""
                body += (f"<br><span class='muted'>The rule already in place for this value "
                         f"({state.fmt_date(prev.valid_from)}{until}): </span>"
                         f"<span class='diff-old' style='text-decoration:none'>"
                         f"{state.readable(prev.expression)}</span>")
                if prev.condition:
                    body += f" <span class='muted'>if {state.readable(prev.condition)}</span>"
    elif kind == "table":
        title, what = el.get("label") or el.get("name", ""), "Table " + ("changed" if old else "added")
        title = title[:1].upper() + title[1:]
        ref = el.get("rows_ref")
        ref = (ref.get("extracted_table") or "") if isinstance(ref, dict) else str(ref or "")
        body = (f"Taken from the table in the document's appendix ({ref.split('/')[-1]})"
                if el.get("rows_ref") else f"{len(el.get('rows') or [])} rows")
    elif kind == "fact":
        title, what, body = state.fact_label(el["id"]), "New term", el.get("label", "")
        period = ""
    else:
        title, what, body = el.get("id", ""), kind, ""
    cls = "rule company" if el.get("layer") == "company" else "rule"
    common.html(f"<div class='{cls}'>{common.badge(what, 'green' if 'New' in what or 'added' in what else 'blue')}"
                f"<b>{title}</b> <span class='muted'>· {period}</span><br>{body}{quote}</div>")


def check(delta, kb):
    """Format, application, and the consistency checker: the checks that run without the AI, here and now."""
    try:
        validate_delta_json(delta)
    except Exception as e:  # noqa: BLE001
        return None, [("error", f"Format: {str(e)[:250]}")]
    try:
        kb2 = apply_delta(kb, delta)
    except Exception as e:  # noqa: BLE001
        return None, [("error", f"Cannot be applied to the current knowledge base: {str(e)[:250]}")]
    pols = tuple({e.get("policy") for e in delta.get("add", []) + delta.get("change", []) if e.get("policy")})
    rep = consistency.check(kb2, _at(delta), policies=pols)
    return kb2, [(f.severity, f"{f.kind}: {f.detail}") for f in rep.findings]


@st.cache_data(show_spinner="Checking the graph shape (SHACL) ...")
def shacl_new(signature, delta_json):
    """SHACL violations that the update would add to the knowledge base in use."""
    kb = state.kb()
    kb2 = apply_delta(kb, json.loads(delta_json))
    docs = sorted(set(graph.registered_documents()) | set(kb2.documents))
    before = set(graph.validate(kb, docs))
    return [v for v in graph.validate(kb2, docs) if v not in before]


def full_checks(signature, pid, delta_json):
    """All checks of the reading pipeline (pipeline.check, with automatically generated example cases), run on the
    knowledge base in use. Returns (passed, {gate: summary})."""
    delta = json.loads(delta_json)
    els = delta.get("add", []) + delta.get("change", [])
    company = any(e.get("layer") == "company" for e in els)
    item = state.pending_by_id().get(pid)
    if item:
        ev = workflow.event_of(item)
    else:                         # a draft: its own document and date
        doc = delta.get("document") or {}
        ev = pipeline.Event(pid, tuple(sorted({s["document"] for e in els for s in e.get("source") or []
                                               if s.get("document")})),
                            date.fromisoformat(doc["issued"]) if doc.get("issued") else state.TODAY,
                            "company" if company else "regulation", doc.get("title", ""))
    pols = tuple(sorted({e["policy"] for e in els if e.get("policy")}))
    try:
        ok, log, _, _ = pipeline.check(state.kb(), delta, ev, ev.issued, None, pipeline.Config(), policies=pols)
    except FileNotFoundError:                   # a source document without stored text: the quotes cannot be read
        return False, {"G2": "fail: the document text is not stored"}
    return ok, {k: str(v) for k, v in log.items() if k in GATES}


def full_checks_panel(pid, delta_json):
    st.markdown("**All checks**",
                help="The same checks the AI's drafts go through, including example cases made automatically, run "
                     "on the current knowledge base. Passing every check does not prove the proposal is right, so "
                     "still read what it changes.")
    done = st.session_state.setdefault("mg_gates", {})
    key = (state.signature(), pid, delta_json)
    if key not in done:
        if st.button("Run all checks (about 15 seconds)", icon=":material/fact_check:", key=f"mg_gate_{pid}",
                     width="stretch"):
            with st.spinner("Running the checks ..."):
                try:
                    done[key] = full_checks(*key)
                except Exception as e:  # noqa: BLE001 - shown to the user
                    done[key] = (False, {"G1": f"could not run: {type(e).__name__}: {e}"[:200]})
        else:
            return
    ok, log = done[key]
    for gate, summary in log.items():
        good = summary.startswith("pass")
        if "known document" in summary:
            summary = ("its source document is not registered yet. A document must be registered (title, issue date, "
                       "text) before it is read; this draft cites a document that is not registered.")
        st.markdown(f"{':material/check_circle:' if good else ':material/cancel:'} {GATES.get(gate, gate)}"
                    + ("" if good else f": {summary[:160]}"))
    if ok:
        st.caption("Passed every check. Still read what it changes.")


def regression(kb, kb2, policies):
    """Every scenario before and after: PPh 21 of the scenario's month and of the year. A company policy that the
    proposal adds is applied to the scenarios without a policy of their own (the scenarios are the sample company's
    employees)."""
    outputs = {n for n, f in kb2.view(state.TODAY).facts.items() if f.output}     # the results the KB declares
    new_policies = sorted({r.policy for r in kb2.records if getattr(r, "policy", None)}
                          - {r.policy for r in kb.records if getattr(r, "policy", None)})
    rows = []
    for sc in calculator.scenarios().values():
        case = calculator.scenario_case(sc)
        if new_policies and not case["employer"].get("policy"):
            case["employer"]["policy"] = new_policies[0]
        m = sc["month"]
        res = [state.compute(case, state.TODAY, k)[0] for k in (kb, kb2)]
        vals = [{(f, mm): v for mm, p in (r.periods.items() if r else ()) for f, v in p.items() if f in outputs}
                | {(f, 0): v for f, v in ((r.year or {}).items() if r else ()) if f in outputs} for r in res]
        moved = sorted({f for key in set(vals[0]) | set(vals[1]) if vals[0].get(key) != vals[1].get(key)
                        for f in [key[0]]}, key=state.fact_label)
        a, b = (r.periods[m].get("pph21_due") if r else None for r in res)
        ya, yb = ((r.year or {}).get("annual_pph21") if r else None for r in res)
        rows.append({"Scenario": sc["title"], "Month": f"{state.MON[m - 1]} {case['tax_year']}",
                     "PPh 21 before": state.money(a), "PPh 21 after": state.money(b),
                     "Year before → after": (f"{state.money(ya)} → {state.money(yb)}" if ya != yb
                                             else state.money(ya)),
                     "Result": "changed" if moved else "same",
                     "Values that changed": ", ".join(state.fact_label(f) for f in moved[:4])
                                            + (f" +{len(moved) - 4}" if len(moved) > 4 else "")})
    return pd.DataFrame(rows)


@st.cache_data(show_spinner="Looking for company policies this update affects ...")
def impact(signature, delta_json, policies, omega):
    """Installed company policies the update affects (pipeline.detect on the knowledge base with the update applied).
    Returns {policy: {"kinds": ..., "hits": [(kind, company rule id, update element id, fact)]}} for affected ones."""
    delta = json.loads(delta_json)
    kb2 = apply_delta(state.kb(), delta)
    found = pipeline.detect(kb2, delta["delta_id"], list(policies), omega)
    return {p: r for p, r in found.items() if r["kinds"]}


def impact_panel(delta, dj):
    """The company policies the proposal affects, each with a plain explanation of how."""
    own = {e.get("policy") for e in delta.get("add", []) + delta.get("change", []) if e.get("policy")}
    installed = state.installed_policies()
    pols = tuple(sorted(p for p in installed if p not in own))
    st.markdown("**Company policies affected**", help=common.tip("impact"))
    if not pols:
        st.caption("No other company policy is installed, so none can be affected.")
        return
    try:
        affected = impact(state.signature(), dj, pols, _at(delta))
    except Exception as e:  # noqa: BLE001 - shown to the user
        st.error(f"The search could not run: {type(e).__name__}: {str(e)[:200]}")
        return
    if not affected:
        st.caption("No installed company policy is affected by this change.")
        return
    for pol, found in affected.items():
        lines = []
        for kind in sorted(found["kinds"]):
            hits = [h for h in found["hits"] if h[0] == kind]
            values = sorted({h[3] for h in hits}, key=state.fact_label)
            rules = sorted({h[1] for h in hits})
            lines.append(f"<li>{IMPACT_KINDS.get(kind, kind)} Values: "
                         f"{', '.join(state.fact_label(f) for f in values)} · rules "
                         f"{', '.join(f'<code>{r}</code>' for r in rules)}</li>")
        common.html(f"<div class='rule company'><b>{installed.get(pol, pol)}</b> <span class='muted'>· {pol}</span>"
                    f"<ul style='margin:.3rem 0'>{''.join(lines)}</ul>Check whether this policy still fits.</div>")


def _sent_to_review(pid):
    """Open a draft just sent to Review. The Review tab is drawn before the tabs that send drafts, so the page is run
    again; otherwise it would still say that nothing is waiting."""
    st.session_state.mg_open = pid
    st.session_state.mg_sent = True
    st.rerun()


def tab_review():
    s = state.load()
    items = [p["id"] for p in state.pending(s) if state.status(p["id"], s) == "review"]
    items += [x["id"] for x in s["drafts"] if x["id"] not in items]
    if not items:
        st.success("Nothing is waiting for review.")
        return
    titles = {i: _title(i) for i in items}
    titles.update({x["id"]: x["title"] for x in s["drafts"]})
    names = dict(titles)
    names.update({x["id"]: f"{x['title']} ({ORIGINS.get(x['origin'], x['origin'])})" for x in s["drafts"]})
    cur = st.session_state.get("mg_open")
    pid = st.selectbox("Under review", items, index=items.index(cur) if cur in items else 0, format_func=names.get)
    st.session_state.mg_open = pid
    delta = state.proposal(pid, s)
    kb = state.kb()
    if pid in s["fixed"]:
        st.info(f"This is a revised version ({s['fixed'][pid]['by']}). Note: “{s['fixed'][pid]['note']}”",
                icon=":material/auto_fix_high:")
        last = st.session_state.get(f"mg_fixlog_{pid}")
        if last:
            passed, log, cost = last
            st.caption(f"Result of the AI fix: {'passed' if passed else 'did not pass'} the checks "
                       f"({', '.join(f'{GATES.get(k, k)}: {v[:30]}' for k, v in log.items())}) · cost USD {cost:.3f}")
    elif pid in state.pending_by_id(s):
        r0 = state.run(pid) or {}
        st.caption(f"Proposed by the AI ({r0.get('run', 'app')}).")
    kb2, msgs = check(delta, kb)
    left, right = st.columns([1.6, 1], gap="large")
    with left:
        st.markdown(f"**Proposed changes** · {len(delta.get('add', []))} added, "
                    f"{len(delta.get('change', []))} changed")
        for el in delta.get("change", []) + delta.get("add", []):
            card(el, kb)
    dj = json.dumps(delta, sort_keys=True, default=str)
    with right:
        st.markdown("**Checks on the current knowledge base**", help=common.tip("checks"))
        errors = [m for sev, m in msgs if sev == "error"]
        if kb2 is None:
            st.error(errors[0] if errors else msgs[0][1])
        else:
            st.markdown(":material/check_circle: Correct format, and it can be applied")
            new_v = shacl_new(state.signature(), dj)
            st.markdown(f"{':material/cancel:' if new_v else ':material/check_circle:'} Graph shape matches SHACL"
                        + (f": {len(new_v)} new violations" if new_v else ""), help=common.tip("SHACL"))
            for e, m in new_v[:3]:
                st.caption(f"⚠ {e}: {m}")
            qs = workflow.quote_status(delta)
            bad = [q for q in qs if q[2] is False or not q[3]]
            unknown = [q for q in qs if q[2] is None]
            st.markdown(f"{':material/cancel:' if bad else ':material/check_circle:'} Quotes are in the document"
                        + (f": {len(bad)} to check" if bad else "")
                        + (f" · {len(unknown)} without document text" if unknown else ""), help=common.tip("quote"))
            st.markdown(f"{':material/warning:' if msgs else ':material/check_circle:'} Consistency checker"
                        + (f": {len(msgs)} notes" if msgs else ""), help=common.tip("consistency checker"))
            for sev, m in msgs[:4]:
                st.caption(f"⚠ {m}")
            full_checks_panel(pid, dj)
        run = state.run(pid) if pid in state.pending_by_id(s) and pid not in s["fixed"] else None
        if run and run.get("drafts"):
            sel = next((c for c in run["drafts"] if c.get("n") == run.get("selected")), run["drafts"][0])
            with st.expander("Check results when the AI wrote the proposal"):
                st.caption("Recorded when the AI wrote the proposal, against the knowledge base at that time, not the "
                           "current one.")
                for k, v in GATES.items():
                    ok = (sel.get("gate_log") or {}).get(k) == "pass"
                    st.markdown(f"{':material/check_circle:' if ok else ':material/cancel:'} {v}")
        if st.button("Ask the assistant about this proposal", icon=":material/forum:", width="stretch"):
            workflow.open_with("Check this proposal against the quoted provisions")
            st.rerun()
    if kb2 is not None:
        st.markdown("**Before and after** · every standard scenario is calculated with the current knowledge base and "
                    "with this proposal. Results for the years before the start date must stay the same. A new "
                    "company policy is applied to the scenarios that have no policy of their own.")
        with st.spinner("Calculating the scenarios ..."):
            df = regression(kb, kb2, tuple(state.installed_policies()))
        st.dataframe(df.style.apply(lambda r: ["background-color: #fff4d6" if r["Result"] == "changed" else ""]
                                    * len(r), axis=1), hide_index=True, width="stretch")
        impact_panel(delta, dj)
    st.divider()
    c1, c2 = st.columns([1, 2])
    reviewer = c1.text_input("Reviewer name", "Admin", key="mg_reviewer")
    note = c2.text_input("Note", key=f"mg_note_{pid}", placeholder="optional")
    b = st.columns(4)
    if b[0].button("Approve", type="primary", icon=":material/check:", width="stretch", disabled=kb2 is None):
        state.approve(pid, titles[pid], delta, reviewer, note)
        st.session_state.mg_open = None
        st.toast("Approved. The knowledge base is updated.")
        st.rerun()
    if b[1].button("Edit", icon=":material/edit:", width="stretch"):
        st.session_state.mg_edit = pid
    if b[2].button("Ask the AI to fix it", icon=":material/auto_fix_high:", width="stretch"):
        st.session_state.mg_fix = pid
    if b[3].button("Reject", icon=":material/close:", width="stretch"):
        state.reject(pid, titles[pid], note or "-")
        st.session_state.mg_open = None
        st.rerun()
    if st.session_state.get("mg_fix") == pid:
        fix_panel(pid, delta)
    if st.session_state.get("mg_edit") == pid:
        with st.container(border=True):
            text = st.text_area("Proposal (JSON)", json.dumps(delta, ensure_ascii=False, indent=1), height=300,
                                key=f"mg_json_{pid}")
            if st.button("Save the edit", icon=":material/save:"):
                try:
                    new = json.loads(text)
                    state.set_fixed(pid, new, "edited by hand", "Admin")
                    st.session_state.mg_edit = None
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {e}")


def fix_panel(pid, delta):
    """The reviewer's note goes to the AI with the current proposal and the document text, and the new version goes
    through the checks again."""
    with st.container(border=True):
        prefill = (st.session_state.get("mg_prefill") or {}).pop(pid, None)    # a note written through the assistant
        if prefill:
            st.session_state[f"mg_fixnote_{pid}"] = prefill
        note = st.text_area("Note for the AI", key=f"mg_fixnote_{pid}",
                            placeholder="e.g. The Rp10 million DTP income limit counts only salary and fixed "
                                        "allowances; leave out the company car.")
        if not workflow.can_repair(pid, delta):
            st.caption("The AI fixes a proposal by reading its uploaded document again, and this draft has no "
                       "uploaded document. Edit it directly, or ask the assistant for a new draft.")
            return
        ok, why = workflow.ready("repair")
        st.caption(f"One round of fixing with {config.MAIN_MODEL}, then all checks run again. About USD 0.1–0.4. "
                   f"{workflow.budget_text('repair')}")
        if not ok:
            st.warning(f"The AI cannot run: {why}.", icon=":material/payments:")
            return
        if st.button("Send to the AI", icon=":material/send:", disabled=not note.strip()):
            with st.spinner("The AI is fixing the proposal and checking it again ..."):
                try:
                    new, passed, log, cost = workflow.repair(pid, delta, note.strip())
                except Exception as e:  # noqa: BLE001 - shown to the user
                    st.error(f"The AI failed: {type(e).__name__}: {str(e)[:300]}")
                    return
            st.session_state[f"mg_fixlog_{pid}"] = (passed, log, cost)
            if new is None:
                st.error("The AI did not produce a usable proposal: " + "; ".join(log.values())[:300])
                return
            st.session_state.mg_fix = None
            st.rerun()


# ====================================================================================================================
# Add, change, revoke
# ====================================================================================================================
def _source(key):
    c1, c2 = st.columns(2)
    doc = c1.text_input("Source document", key=f"{key}_doc", placeholder="e.g. PMK 168/2023")
    prov = c2.text_input("Provision", key=f"{key}_prov", placeholder="e.g. Pasal 2 ayat (1)")
    quote = st.text_input("Quoted sentence", key=f"{key}_quote", help=common.tip("quote"))
    return doc, prov, quote


def tab_edit():
    with st.container(border=True):
        common.md(f"**Ask the AI to do it**: describe the change in plain words; the {common.term('assistant')} "
                  "writes a draft and sends it to Review.")
        c1, c2 = st.columns([4, 1])
        ask = c1.text_input("Request", key="mg_ask", label_visibility="collapsed",
                            placeholder="e.g. The 2027 JP wage cap becomes Rp11,600,000 · Revoke the gift parcel rule")
        if c2.button("Ask the AI", icon=":material/smart_toy:", width="stretch") and ask:
            workflow.open_with(ask)
            st.rerun()
    st.markdown("**Or do it by hand**")
    what = st.segmented_control("Kind", ["New number", "New rule", "Change a rule", "Revoke a rule"],
                                default="New number", key="mg_what", label_visibility="collapsed")
    if what == "New number":
        names = sorted({r.name for r in state.kb().records
                        if r.kind == "parameter" and r.value_type in ("money", "rate")}, key=state.fact_label)
        name = st.selectbox("Number", names, format_func=state.fact_label, key="mg_p")
        cur = workflow.current_param(name)
        cv = state.money(cur.value) if cur.value_type == "money" else state.pct(cur.value)
        st.caption(f"Now **{cv}**, valid since {state.fmt_date(cur.valid_from)} "
                   f"({state.short_doc(cur.source[0].document)}).")
        c1, c2 = st.columns(2)
        value = c1.number_input("New value" + (" (Rp)" if cur.value_type == "money" else " (decimal, e.g. 0.01)"),
                                0.0, 1e11, None, key="mg_pv")
        start = c2.date_input("Valid from", date(state.TODAY.year + 1, 1, 1), key="mg_ps")
        doc, prov, quote = _source("mg_pp")
        if value is not None and st.button("Send to Review", type="primary", icon=":material/send:"):
            v = int(value) if cur.value_type == "money" else value
            delta = workflow.new_value(name, v, start, doc, prov, quote)
            state.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
            _sent_to_review(delta["delta_id"])
    elif what == "New rule":
        facts = sorted(state.facts(), key=state.fact_label)
        c1, c2 = st.columns(2)
        produces = c1.selectbox("Value it calculates", facts, format_func=state.fact_label, key="mg_rf")
        company = c2.radio("Applies as", ("Government regulation", "Company policy"),
                           key="mg_rl") != "Government regulation"
        policy = st.text_input("Policy code", "PRS-01", key="mg_rpol") if company else None
        cond = st.text_input("Applies if (optional)", key="mg_rc", placeholder="e.g. gross_income > 10000000")
        expr = st.text_input("Formula", key="mg_re",
                             placeholder="e.g. 50000 * hr('days_present') + income('other_regular')")
        with st.expander("Names of values and data you can use"):
            st.dataframe(pd.DataFrame([{"Name": f, "Meaning": state.fact_label(f)} for f in facts]), hide_index=True,
                         height=200, width="stretch")
            st.caption("Case data is read with income('…'), benefit('…'), hr('…'), employee('…'), "
                       "employer('…'). "
                       "New data read through hr('…') becomes a column in the calculator automatically.")
        c1, c2 = st.columns(2)
        start = c1.date_input("Valid from", date(state.TODAY.year + 1, 1, 1), key="mg_rs")
        end = c2.date_input("Valid until (leave empty for no end)", None, key="mg_ru")
        doc, prov, quote = _source("mg_rp")
        if expr:
            common.html(f"<div class='rule{' company' if company else ''}'><b>{state.fact_label(produces)}</b> = "
                        f"{state.readable(expr)}" + (f" <i>if {state.readable(cond)}</i>" if cond else "") + "</div>")
            if st.button("Send to Review", type="primary", icon=":material/send:", key="mg_rsend"):
                delta = workflow.new_rule(produces, expr, cond, start, end, company, policy, doc, prov, quote)
                state.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
                _sent_to_review(delta["delta_id"])
    else:
        view = state.kb().view(state.TODAY)
        rules = {r.id: r for r in view.rules.values()
                 if not state.is_input_convention(r) and (r.valid_until is None or r.valid_until >= state.TODAY)}
        ids = sorted(rules, key=lambda i: state.fact_label(rules[i].produces))
        rid = st.selectbox("Rule", ids, key="mg_cr", format_func=lambda i: f"{state.fact_label(rules[i].produces)} · "
                           f"{state.short_doc(rules[i].source[0].document) if rules[i].source else ''}")
        r = rules[rid]
        until = " to " + state.fmt_date(r.valid_until) if r.valid_until else ""
        common.html(f"<div class='rule'><b>{state.fact_label(r.produces)}</b><br><b>Formula:</b> "
                    f"{state.readable(r.expression)}<br><span class='muted'>Valid {state.fmt_date(r.valid_from)}"
                    f"{until}</span></div>")
        if what == "Revoke a rule":
            common.md(f"{common.term('revocation', 'Revoking')} means giving the rule an end date. The rule is not "
                      "deleted, so past calculations stay the same.")
            end = st.date_input("No longer valid after", date(state.TODAY.year, 12, 31), key="mg_ce")
            others = [x for x in view.rules.values() if x.produces == r.produces and x.id != r.id
                      and (x.valid_until is None or x.valid_until > end)]
            readers = [x.id for x in view.rules.values()
                       if r.produces in state.expr_text(x.expression) + state.expr_text(x.condition or "")]
            if not others:
                st.warning(f"After {state.fmt_date(end)} no other rule calculates *{state.fact_label(r.produces)}*, "
                           f"yet {len(readers)} rules use it. Add a replacement, or make sure the regulation really "
                           "removes it.", icon=":material/warning:")
            doc, prov, quote = _source("mg_cp")
            if st.button("Send to Review", type="primary", icon=":material/send:", key="mg_csend"):
                delta = workflow.revoke(r, end, doc, prov, quote)
                state.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
                _sent_to_review(delta["delta_id"])
        else:
            expr = st.text_input("New formula", state.expr_text(r.expression), key="mg_ue")
            start = st.date_input("Valid from", date(state.TODAY.year + 1, 1, 1), key="mg_us",
                                  help="The old version is still used for the months before.")
            doc, prov, quote = _source("mg_up_")
            if expr != state.expr_text(r.expression) and st.button("Send to Review", type="primary",
                                                                   icon=":material/send:", key="mg_usend"):
                delta = workflow.change_rule(r, expr, start, doc, prov, quote)
                state.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
                _sent_to_review(delta["delta_id"])


# ====================================================================================================================
# Company policies
# ====================================================================================================================
def _sample_policy(installed):
    """Send one of the sample company policies to Review, with its document text when it is shipped, so the review
    can be tried without the AI."""
    samples = state.sample_policies()
    if not samples:
        return
    st.markdown("**Add a sample company policy to review**")
    c1, c2 = st.columns([3, 1])
    pick = c1.selectbox("Sample policy", list(samples), key="mg_pol_sample", label_visibility="collapsed",
                        format_func=lambda k: f"{k} · {samples[k][0]}")
    title, delta = samples[pick]
    rules = [e for e in delta.get("add", []) if e.get("kind") == "rule"]
    issued = (delta.get("document") or {}).get("issued")
    st.caption(f"{len(rules)} company rules, issued {_iso(issued)}."
               + (" This policy is already installed." if pick in installed else ""))
    if c2.button("Send to Review", icon=":material/send:", key="mg_pol_sample_send", width="stretch",
                 disabled=pick in installed):
        text = sample_text(pick)
        if text:                                # the policy text, so the quote check can read it
            documents.add_document(pick, title, date.fromisoformat(issued) if issued else state.TODAY,
                                   text=text, company=True)
        state.add_draft(pick, title, delta, "sample")
        _sent_to_review(pick)


def tab_policy():
    pols = state.installed_policies()
    common.md(f"Installed {common.term('company policy', 'company policies')} are used by the calculator when "
              "selected. A company rule must not contradict the regulations; the system checks this.")
    if pols:
        for pid, title in pols.items():
            with st.expander(f"{pid} · {title}"):
                for r in state.kb().view(state.TODAY).rules.values():
                    if r.layer == "company" and r.policy == pid:
                        until = " to " + state.fmt_date(r.valid_until) if r.valid_until else ""
                        common.html(f"<div class='rule company'><b>{state.fact_label(r.produces)}</b>: "
                                    f"{state.readable(r.expression)}<br><span class='muted'>valid "
                                    f"{state.fmt_date(r.valid_from)}{until}</span></div>")
                found = calculator.discover(state.TODAY.year, pid)
                new_cols = [calculator.label(k) for k, e in found.items() if e["layer"] == "company"]
                if new_cols:
                    st.caption("Data the calculator asks for because of this policy: " + ", ".join(new_cols))
    else:
        st.caption("No company policy is installed yet. Approve one in Review, or create one from a sample below.")
    _sample_policy(pols)
    st.markdown("**Create from a template**")
    c1, c2 = st.columns(2)
    pid = c1.text_input("Policy code", "PRS-01", key="mg_pol_id")
    tpl = c2.selectbox("Template", ["Meal allowance per day present", "THR as a multiple of wages", "Annual bonus"],
                       key="mg_pol_tpl")
    start = st.date_input("Valid from", date(state.TODAY.year + 1, 1, 1), key="mg_pol_start")
    inputs = []
    if tpl == "Meal allowance per day present":
        n = st.number_input("Rupiah per day present", 0, 1_000_000, 50_000, 5_000, key="mg_pol_n")
        delta = workflow.meal_policy(int(n), pid, start)
        inputs = [{**workflow.DAYS_PRESENT_INPUT, "source": delta["document"]["title"]}]
    elif tpl == "THR as a multiple of wages":
        n = st.number_input("Multiple of wages", 0.5, 5.0, 1.5, 0.5, key="mg_pol_t")
        delta = workflow.thr_policy(n, pid, start)
    else:
        c1, c2 = st.columns(2)
        n = c1.number_input("Percent of base salary", 1, 500, 100, key="mg_pol_b")
        m = c2.selectbox("Month paid", range(1, 13), 11, format_func=lambda x: state.MONTHS[x - 1], key="mg_pol_m")
        delta = workflow.bonus_policy(n, m, pid, start)
    for el in delta["add"]:
        card(el, state.kb())
    if st.button("Send to Review", type="primary", icon=":material/send:", key="mg_pol_send"):
        state.add_draft(delta["delta_id"], delta["document"]["title"], delta, "template", inputs=inputs)
        _sent_to_review(delta["delta_id"])


# ====================================================================================================================
# Knowledge base check and version history
# ====================================================================================================================
@st.cache_data
def _health(signature, today):
    kb = state.kb()
    out = []
    by_name = {}
    for r in kb.records:
        if r.kind == "parameter":
            by_name.setdefault(r.name, []).append(r)
    for name, vs in by_name.items():
        years = sorted({v.valid_from.year for v in vs})
        if len(years) >= 3 and years[-1] - years[-2] == 1 and years[-1] < today.year + 1:
            out.append(("warn", f"{state.fact_label(name)} changes every year; the {years[-1] + 1} value is missing.",
                        f"Latest: {state.short_doc(vs[-1].source[0].document)} ({years[-1]})."))
    ending = {}
    for r in kb.view(today).rules.values():
        if r.valid_until and r.valid_until >= today - timedelta(days=400) and r.valid_until.year <= today.year:
            ending.setdefault((r.valid_until, state.topic_of(r)), []).append(r)
    for (until, topic), rs in sorted(ending.items())[-4:]:
        out.append(("info", f"{topic}: {len(rs)} rules end on {state.fmt_date(until)}.",
                    "If they are extended, upload the new regulation under New documents."))
    found = calculator.discover(today.year, None)
    undefined = [k for k in found if not calculator.has_def(k)]
    if undefined:
        out.append(("warn", f"{len(undefined)} data items read by rules have no definition (label and explanation).",
                    ", ".join(undefined[:6])))
    for f in consistency.check(kb, today).findings[:8]:
        out.append(("error" if f.severity == "error" else "warn", f"{f.kind}: {f.detail}", ", ".join(f.ids)))
    return out


def tab_health():
    common.md("A routine check of the knowledge base, so problems show up before a calculation goes wrong.")
    items = _health(state.signature(), state.TODAY)
    for level, title, detail in items:
        icon = {"warn": ":material/schedule:", "info": ":material/event:", "error": ":material/error:"}[level]
        show_as = st.warning if level == "warn" else st.error if level == "error" else st.info
        show_as(f"**{title}**  \n{detail}", icon=icon)
    if not items:
        st.success("Nothing found.")


def tab_history():
    s = state.load()
    base = state.base()
    common.html(f"<div class='rule'><b>Starting knowledge base</b> · {len(base.updates)} updates, known until "
                f"{state.base_label()}.</div>")
    for i, a in enumerate(s["approved"]):
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"**v{i + 1}** · {a['title']} · approved {a['when']} by {a['reviewer']}"
                    + (f"  \n_{a['note']}_" if a.get("note") else ""))
        if c2.button("Go back to before this", key=f"rb_{i}", icon=":material/history:", width="stretch",
                     help="This update and the ones after it are removed from the knowledge base. To use one again, "
                          "send it to review again from where it came from."):
            state.rollback(i)
            st.rerun()
    if s["log"]:
        st.markdown("**Activity log**")
        for e in s["log"][:20]:
            st.caption(f"{e['when']} · {e['what']}")
    _start_over()


def _start_over():
    """Clear everything done in the app and go back to the starting knowledge base."""
    with st.container(border=True):
        st.markdown("**Start over**", help=common.tip("starting knowledge base"))
        st.caption("Removes every approved update, draft, uploaded document, saved employee, added pay component, and "
                   "the assistant chat, and goes back to the starting knowledge base. The record of AI spending is "
                   "kept.")
        sure = st.checkbox("I understand everything done in the app is removed", key="mg_reset_ok")
        if st.button("Start over", icon=":material/restart_alt:", key="mg_reset", disabled=not sure):
            state.reset()
            st.rerun()


# ====================================================================================================================
# Page
# ====================================================================================================================
def show():
    st.session_state.page_ctx = "manage"
    st.title("Knowledge base management")
    common.md(f"Add, change, revoke, and {common.term('review')} what the system knows. Do it by hand, or ask the "
              f"{common.term('assistant', 'AI assistant')} (button at the bottom right) to help check and do the work. "
              "Nothing changes before you approve it.")
    if st.session_state.pop("mg_sent", False):
        st.toast("Sent to Review. Open the Review tab.", icon=":material/send:")
    s = state.load()
    n_review = len({p["id"] for p in state.pending(s) if state.status(p["id"], s) == "review"}
                   | {x["id"] for x in s["drafts"]})
    n_new = sum(state.status(p["id"], s) in ACTION_NEEDED for p in state.pending(s))
    tabs = st.tabs([f"New documents ({n_new})" if n_new else "New documents", f"Review ({n_review})",
                    "Add, change, revoke", "Company policies",
                    "Knowledge base check", "Version history"])
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
