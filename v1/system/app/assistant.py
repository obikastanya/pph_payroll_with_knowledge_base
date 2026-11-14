"""AI assistant as a pop-up: a floating button on every page opens a separate chat window. The conversation is kept
when the window is closed (workspace/chat.json, also after a reload) and can be cleared.

The model (gpt-5.4-mini by default, through ai.chat) answers from the knowledge base context and picks at most one
action; the app carries it out with its own code: explain or check the proposal under review, prepare a fix note for
the reviewer, explain why the system was unsure, draft a new number, a revocation or a company policy (drafts go to
Review), explain the calculator result, look up a number. It never approves. Without a key or budget, or when chosen,
the keyword matching below answers instead (no API).
"""
import re
from datetime import date

import streamlit as st

import ai
import data as d
import drafts
import store

OFFLINE = "tanpa-ai"                           # logic value of the model choice; shown as "No AI"
MODEL_NAME = {OFFLINE: "No AI"}
MODELS = {"gpt-5.4-mini": "OpenAI · cheap, default (USD 0.75 / 4.50 per million tokens)",
          "gpt-6.1-sol": "OpenAI · the research's second model (USD 2 / 10)",
          OFFLINE: "keyword matching, free"}
# The suggested questions work through the model and through the keyword matching below (Indonesian works too).
SUGGEST = {
    "kelola": ["Explain the proposal under review", "Check this proposal against its source quotes",
               "Why is the system unsure about the WIKA collective labor agreement (PKB)?",
               "Create a meal allowance rule of Rp50,000 per day present",
               "Revoke the gift rule", "Change the JP wage cap for 2027 to Rp11,600,000"],
    "kalkulator": ["Why is this month's PPh this amount?", "How much is the JP wage cap now?", "What is TER?"],
    "kb": ["How much is the JP wage cap now?", "How much is the position cost (biaya jabatan)?",
           "What changed most recently?"],
}
STOP = {"the", "and", "for", "per", "with", "from", "than", "other", "rule", "dan", "yang", "atau", "untuk", "dari"}
UNITS = {"juta": 10**6, "jt": 10**6, "million": 10**6, "m": 10**6,
         "ribu": 10**3, "rb": 10**3, "thousand": 10**3, "k": 10**3}
AMOUNT = re.compile(r"(rp\.?\s*)?(\d[\d.,]*\d|\d)(?:\s*(juta|jt|million|ribu|rb|thousand)(?![a-z])|(k|m)(?![a-z]))?")
ORIGIN = "AI assistant"                         # origin shown for the drafts the assistant makes
REQUEST = "request through the assistant"      # source document of a number or revocation asked of the assistant


def _n(n, one, many=None):
    """'1 change', '2 changes'."""
    return f"{n} {one if n == 1 else many or one + 's'}"


def _has(ql, *words):
    return any(w in ql for w in words)


def _number(text):
    """'11,600,000', '11.600.000', '1.5', '1,5' -> float (separators are thousands when every group has 3 digits)."""
    parts = re.split(r"[.,]", text)
    if len(parts) == 1:
        return float(text)
    if all(len(x) == 3 for x in parts[1:]) and 1 <= len(parts[0]) <= 3:
        return float("".join(parts))
    return float("".join(parts[:-1]) + "." + parts[-1])


def amounts(text):
    """[(rupiah, looks like money)] in a sentence: 'Rp50 ribu', '50.000', '50,000', '50k', 'Rp11,600,000', '1.5 juta',
    '11.6 million'. A bare number that is a year (20xx) is skipped."""
    out = []
    for m in AMOUNT.finditer(text.lower()):
        rp, num, unit1, unit2 = m.groups()
        unit = unit1 or unit2
        plain = not (rp or unit) and re.fullmatch(r"\d+", num)
        if plain and re.fullmatch(r"20\d\d", num):
            continue
        value = _number(num) * (UNITS[unit] if unit else 1)
        out.append((int(round(value)), bool(rp or unit or not plain or len(num) >= 5)))
    return out


def _amount(text, strict=True):
    """First amount of the sentence; strict: only one that looks like money (Rp, unit, separators or 5+ digits)."""
    for value, moneylike in amounts(text):
        if moneylike or not strict:
            return value
    return None


# ---------------------------------------------------------------- answers
def _current_item():
    pid = st.session_state.get("mg_open")
    if not pid:
        return None, None
    return pid, store.proposal(pid)


def _explain(pid, delta):
    els = [e for e in delta.get("add", []) + delta.get("change", []) if e.get("kind") in ("rule", "parameter", "table")]
    touched = sorted({d.fact_label(e.get("produces") or e.get("name") or e["id"]) for e in els})
    starts = sorted({e.get("valid_from") for e in els if e.get("valid_from")})
    title = (delta.get("document") or {}).get("title", pid)
    return (f"**{title}** proposes {_n(len(delta.get('add', [])), 'addition')} and "
            f"{_n(len(delta.get('change', [])), 'change')}, effective from {', '.join(starts[:3]) or '-'}. "
            f"Numbers affected: {', '.join(touched[:8])}.\n\n"
            "Open the *Review* tab to see before-and-after examples on common scenarios.")


def quote_status(delta):
    """Per element: (what, provision, quote found in the document text or None when the text is not available,
    every number of a money parameter appears in its quote). The quote gate (G2), run here and now."""
    from pph21kbs.text import normalize, normalized
    out = []
    for e in delta.get("add", []) + delta.get("change", []):
        for s in (e.get("source") or [])[:1]:
            try:
                found = normalize(s.get("quote", "")) in normalized(s.get("document"))
            except Exception:  # noqa: BLE001 - document text not available
                found = None
            num_ok = True
            if e.get("kind") == "parameter" and e.get("value_type") == "money":
                num_ok = str(int(float(e["value"]))) in re.sub(r"\D", "", s.get("quote", ""))
            out.append((d.fact_label(e.get("produces") or e.get("name") or e["id"]), s.get("provision", ""), found, num_ok))
    return out


def _check(pid, delta):
    """Real check: is every quote in the document text, and does every number of a parameter appear in its quote?"""
    lines, problems = [], 0
    for what, provision, found, num_ok in quote_status(delta):
        mark = "✓" if found and num_ok else ("?" if found is None else "⚠")
        problems += mark == "⚠"
        note = "" if found else " · quote not found in the document" if found is False else " · document text not available"
        note += "" if num_ok else " · number not in the quote"
        lines.append(f"{mark} {what} ({provision}){note}")
    head = ("All quotes are in the document and the numbers match." if not problems else
            f"{_n(problems, 'part')} need{'s' if problems == 1 else ''} a human check.")
    return (f"{head}\n\n" + "\n".join(f"- {x}" for x in lines[:14]) +
            "\n\nThis is a second opinion, not a decision. A matching quote does not prove the rule is right: also "
            "check the conditions and the formula.")


def _why_unsure(pid):
    r = store.run(pid)
    if not r:
        return "There is no saved AI result for that document."
    groups = r.get("groups") or []
    passed = sum(1 for c in r.get("candidates", []) if c.get("passed"))
    return (f"The AI wrote {_n(len(r.get('candidates', [])), 'proposed version')}; {passed} passed the automatic "
            f"checks. The versions that passed were run on example cases and grouped by result: "
            f"{_n(len(groups), 'group')} ({', '.join(_n(len(g), 'version') for g in groups)}). No group was clearly "
            "larger, so the system is unsure and does not guess. You can write the policy in the *Company policy* "
            "tab, or ask me to redo it with your note.")


def _words(name, minlen):
    """Words that name a fact or parameter: its English label, its Indonesian label and its identifier."""
    recs = (d.facts().get(name), d.params().get(name))
    text = " ".join([d.fact_label(name), name.replace("_", " ")] + [getattr(r, "label_id", "") or "" for r in recs if r])
    return {w for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= minlen and w not in STOP}


def _score(words, ql):
    """How many of the words occur in the question (short words as whole words, long ones also inside a word)."""
    tokens = set(re.findall(r"[a-z]+", ql))
    return sum(w in tokens or (len(w) >= 4 and w in ql) for w in words)


def _param(q):
    ql = q.lower()
    best = None
    for name in d.params():
        score = _score(_words(name, 2), ql)
        if score and (best is None or score > best[0]):
            best = (score, name)
    return best[1] if best else None


def _find_rule(q):
    """The rule a request names, by its English or Indonesian label (drafts.find_rule reads the English label only)."""
    ql = q.lower()
    best = None
    for r in d.kb().view(store.TODAY).rules.values():
        if d.is_input_convention(r):
            continue
        score = _score(_words(r.produces, 4), ql)
        if score and (best is None or score > best[0]):
            best = (score, r)
    return best[1] if best else drafts.find_rule(q)


def _lookup(name):
    vs = sorted((r for r in d.kb().records if r.kind == "parameter" and r.name == name), key=lambda r: r.valid_from)
    cur = [r for r in vs if r.valid_from <= store.TODAY and (r.valid_until is None or store.TODAY <= r.valid_until)]
    r = cur[-1] if cur else vs[-1]
    fmt = lambda v: d.money(v.value) if v.value_type == "money" else d.pct(v.value) if v.value_type == "rate" else v.value  # noqa: E731
    src = r.source[0]
    return (f"**{d.fact_label(name)}** according to the knowledge base now: **{fmt(r)}**, effective since "
            f"{d.tgl(r.valid_from)}.\n\nSource: {d.short_doc(src.document)} {src.provision}, “{src.quote}”.\n\nHistory: "
            + ", ".join(f"{v.valid_from.year}: {fmt(v)}" for v in vs[-4:]) +
            f"\n\nThe knowledge base is current up to {d.tgl(store.known_until())}.")


def _calc_why():
    last = st.session_state.get("k_last")
    if not last:
        return "Open the calculator and calculate first; I explain from the last result there."
    m = last["month"]
    due, work = last["due"], last["work"]

    def said(x):
        rid, expr, reads = work[x]
        parts = ", ".join(f"{d.fact_label(k[0]).lower()} {d.fmt(k[0], v)}" for k, v in reads if v not in (None, 0))
        return rid, expr, parts
    rid, expr, parts = said(m)
    text = (f"PPh {d.MONTHS[m - 1]}: **{d.money(due[m])}**, calculated by rule `{rid}`: "
            f"{d.readable(expr) if expr else '-'} (with {parts or '-'}).")
    prev = max((x for x in due if x < m), default=None)
    if prev:
        prid, _, _ = said(prev)
        before = {k[0]: v for k, v in work[prev][2]}
        moved = [f"{d.fact_label(k[0]).lower()} {d.fmt(k[0], before.get(k[0]))} → {d.fmt(k[0], v)}"
                 for k, v in work[m][2] if k[0] in before and before[k[0]] != v]
        text += f" The previous month was {d.money(due[prev])}."
        if prid != rid:
            text += f" This month uses a different rule (`{prid}` → `{rid}`)."
        elif moved:
            text += " What changed: " + "; ".join(moved) + "."
    if last.get("final"):
        text += " This is the closing month: the full-year tax is recalculated and what was already withheld is subtracted."
    return text + "\n\nThe details and the articles are in the *Why this number?* section below the result."


def _meal_draft(n):
    delta = drafts.meal_policy(n)
    store.add_draft(delta["delta_id"], delta["document"]["title"], delta, ORIGIN, inputs=[
        {"key": "hr.days_present", "label": "Days present", "help": "Number of days present in the month.",
         "type": "int", "group": "bulanan", "order": 65, "source": delta["document"]["title"]}])


def reply(q):
    """(answer, action label or None). Actions are already carried out (drafts saved) when they are returned.
    Indonesian and English keywords both work."""
    ql = q.lower()
    pid, delta = _current_item()
    pick = "Select a proposal in the *Review* tab first."
    if ("jelaskan usulan" in ql or ("usulan" in ql and "jelaskan" in ql)
            or ("explain" in ql and _has(ql, "proposal", "proposed update", "update under review"))):
        return (_explain(pid, delta) if delta else pick), None
    if ("periksa" in ql and "usulan" in ql) or (_has(ql, "check", "verify") and _has(ql, "proposal", "proposed update")):
        return (_check(pid, delta) if delta else pick), None
    if "perbaiki" in ql or re.search(r"\bfix\b", ql):
        if not pid:
            return "Select a proposal in the *Review* tab first, then write your note.", None
        return act("fix_proposal", {"note": q}, q), "fix"
    if _has(ql, "ragu", "pkb", "unsure", "not sure", "uncertain", "abstain", "doubt"):
        return _why_unsure("PKB-WIKA-2025" if "wika" in ql or not pid else pid), None
    if (_has(ql, "buat", "tambah", "create", "add ", "make", "set up")
            and _has(ql, "per hari", "uang makan", "per day", "meal")):
        n = _amount(ql, strict=False) or 50_000
        _meal_draft(n)
        return (f"I made a draft company policy: **meal allowance {d.money(n)} × days present**, regular income, "
                "effective 1 January next year. This rule reads a new data item, *days present*, so once it is "
                "approved the column appears in the calculator by itself. Check it in the *Review* tab."), "draft"
    if _has(ql, "cabut", "hentikan", "revoke", "withdraw", "remove", "cancel", "end the rule", "stop the rule"):
        rule = _find_rule(q)
        if not rule:
            return "Which rule do you want to revoke? Name it, e.g. \"revoke the gift rule\".", None
        delta = drafts.revoke(rule, date(store.TODAY.year, 12, 31), REQUEST, "-")
        store.add_draft(delta["delta_id"], delta["document"]["title"], delta, ORIGIN)
        return (f"The draft revocation of **{d.fact_label(rule.produces)}** ({d.short_doc(rule.source[0].document)} "
                f"{rule.source[0].provision}) is in the *Review* tab, effective until 31 December {store.TODAY.year}. "
                "The rule is not deleted, only given an end date, so old calculations stay the same. Add the legal "
                "basis before approving."), "draft"
    if "menjadi" in ql or (re.search(r"\b(change|set|raise|lower|increase|update|make)\b", ql)
                           and re.search(r"\bto\b|\bbecomes?\b|=", ql)):
        name = _param(q)
        value = _amount(ql)
        year = re.search(r"\b(20\d\d)\b", ql)
        if name and value:
            start = date(int(year.group(1)) if year else store.TODAY.year + 1, 1, 1)
            delta = drafts.new_value(name, value, start, REQUEST, "-", "")
            store.add_draft(delta["delta_id"], delta["document"]["title"], delta, ORIGIN)
            return (f"Draft of a new number: **{d.fact_label(name)} = {d.money(value)}** from {d.tgl(start)}; the old "
                    "value ends the day before. It is in the *Review* tab. Add the source document and article "
                    "before approving."), "draft"
    if "pph" in ql and _has(ql, "kenapa", "segini", "naik", "why", "how come", "this amount", "this much", "went up"):
        return _calc_why(), None
    if "terakhir" in ql or (_has(ql, "last", "latest", "recent") and _has(ql, "chang", "update")):
        u = d.kb().updates[-1]
        return f"Latest update: **{d.doc_title(u.document)}**, recorded {d.tgl(u.recorded_on)}.", None
    asked = re.search(r"(?:apa itu|what is|what's|what are|define|meaning of)\s+(?:the |an? )?(.+)", ql)
    if asked:
        import glossary
        word = asked.group(1).strip(" ?.!")
        exact = [k for k, (lab, _) in glossary.TERMS.items() if word in (k.lower(), lab.lower())]
        near = [k for k, (lab, _) in glossary.TERMS.items() if word and (word in k.lower() or word in lab.lower())]
        for k in exact + near:
            return glossary.tip(k), None
    name = _param(q)
    if name and _has(ql, "berapa", "nilai", "how much", "what is", "what's", "current", "value", "now", "amount"):
        return _lookup(name), None
    return ("I can help with:\n- explaining or checking the proposal under review;\n- fixing a proposal following your "
            "note;\n- explaining why the system is unsure;\n- drafting a new number, a new rule, a revocation or a "
            "company policy;\n- explaining the calculator result and the numbers in the knowledge base.\n\nEvery change "
            "goes to *Review*; I never approve anything. You can write in Indonesian or English."), None


# ---------------------------------------------------------------- the model (OpenAI) and its actions
def _context(q):
    """What the model may use: the page, the numbers of the knowledge base with their source, the latest updates, the
    proposal under review, and the last calculator result. No employee name is sent."""
    s = st.session_state
    lines = [f"Page: {s.get('page_ctx', 'kelola')}. Today: {store.TODAY}. Knowledge base known until "
             f"{store.known_until()}."]
    lines.append("NUMBERS OF THE KNOWLEDGE BASE IN FORCE TODAY (parameter name | label | value | source):")
    for name in sorted(d.params()):
        r = d.param_at(name, store.TODAY)
        if r is not None:
            src = r.source[0] if r.source else None
            value = (d.money(r.value) if r.value_type == "money" else d.pct(r.value) if r.value_type == "rate"
                     else str(r.value))
            lines.append(f"- {name} | {d.fact_label(name)} | {value}"
                         f" | {d.short_doc(src.document) + ' ' + src.provision if src else '-'}")
    lines.append("LATEST UPDATES: " + "; ".join(f"{d.doc_title(u.document)} ({u.recorded_on})" for u in d.kb().updates[-5:]))
    pid, delta = _current_item()
    if delta:
        lines.append(f"PROPOSAL UNDER REVIEW ({pid}): " + _explain(pid, delta))
        for e in (delta.get("change", []) + delta.get("add", []))[:12]:
            src = (e.get("source") or [{}])[0]
            lines.append(f"- {e.get('kind')} {e.get('id')} {e.get('produces') or e.get('name') or ''}: "
                         f"{e.get('expression') or e.get('value') or ''} from {e.get('valid_from')} until "
                         f"{e.get('valid_until') or '-'}; source {src.get('provision', '')}: \"{src.get('quote', '')[:160]}\"")
    if s.get("k_last"):
        lines.append("LAST CALCULATOR RESULT: " + _calc_why().split("\n\n")[0])
    return "\n".join(lines)


def act(action, args, q):
    """Carry out the action the model picked, with the app's own code. Returns the text to add, or None."""
    pid, delta = _current_item()
    args = args or {}
    if action in ("explain_proposal", "check_proposal", "fix_proposal") and not delta:
        return "Select a proposal in the *Review* tab first."
    if action == "explain_proposal":
        return _explain(pid, delta)
    if action == "check_proposal":
        return _check(pid, delta)
    if action == "fix_proposal":
        st.session_state.mg_open, st.session_state.mg_fix = pid, pid
        st.session_state.setdefault("mg_prefill", {})[pid] = args.get("note") or q
        return ("I filled in your note under *Review* → **Ask AI to fix**. Check the note, then press *Send to AI*: "
                "the fix uses Claude credit and the result goes through checks G1–G5 again.")
    if action == "why_unsure":
        return _why_unsure(pid or "PKB-WIKA-2025")
    if action == "calc_why":
        return _calc_why()
    if action == "lookup":
        name = args.get("param") if args.get("param") in d.params() else _param(q)
        return _lookup(name) if name else None
    if action == "new_value":
        name = args.get("param") if args.get("param") in d.params() else _param(q)
        if not name or args.get("value") is None:
            return None
        try:
            start = date.fromisoformat(args.get("start")) if args.get("start") else date(store.TODAY.year + 1, 1, 1)
        except ValueError:
            start = date(store.TODAY.year + 1, 1, 1)
        value = args["value"]
        value = int(value) if float(value).is_integer() else value
        delta = drafts.new_value(name, value, start, REQUEST, "-", "")
        store.add_draft(delta["delta_id"], delta["document"]["title"], delta, ORIGIN)
        return (f"Draft of a new number: **{d.fact_label(name)} = {d.fmt(name, value)}** from {d.tgl(start)}; the old "
                "value ends the day before. It is in the *Review* tab. Add the source document and article before "
                "approving.")
    if action == "revoke":
        rule = _find_rule(args.get("rule") or q)
        if not rule:
            return "I could not find that rule. Name it, e.g. \"revoke the gift rule\"."
        delta = drafts.revoke(rule, date(store.TODAY.year, 12, 31), REQUEST, "-")
        store.add_draft(delta["delta_id"], delta["document"]["title"], delta, ORIGIN)
        return (f"The draft revocation of **{d.fact_label(rule.produces)}** ({d.short_doc(rule.source[0].document)} "
                f"{rule.source[0].provision}) is in the *Review* tab, effective until 31 December {store.TODAY.year}.")
    if action == "meal_policy":
        n = int(args.get("amount") or 50_000)
        _meal_draft(n)
        return (f"The draft company policy **meal allowance {d.money(n)} × days present** is in the *Review* tab. Once "
                "approved, the *days present* column appears in the calculator by itself.")
    return None


def answer(q, msgs):
    """The reply to a question: the model when one is chosen and usable, else the keyword matching."""
    model = st.session_state.get("as_model") or default_model()
    if model == OFFLINE:
        return reply(q)[0]
    ok, why = ai.ready("asisten")
    if not ok:
        return reply(q)[0] + f"\n\n*No AI: {why}.*"
    try:
        text, action, args, cost = ai.chat(q, msgs, _context(q), model=model)
    except Exception as e:  # noqa: BLE001 - the keyword matching still answers
        return reply(q)[0] + f"\n\n*The model could not be used ({type(e).__name__}); answered without AI.*"
    extra = act(action, args, q) if action != "none" else None
    if extra and action not in ("new_value", "revoke", "meal_policy", "fix_proposal"):
        text = ""             # facts come from the knowledge base through the app's own text, not the model's wording
    return (text + (f"\n\n{extra}" if extra else "")).strip() + f"\n\n<sub>{model} · USD {cost:.4f}</sub>"


def default_model():
    return ai.ASSISTANT_MODEL if ai.ready("asisten")[0] else OFFLINE


# ---------------------------------------------------------------- pop-up
def _close():
    st.session_state.as_open = False


@st.dialog("AI assistant", width="large", on_dismiss=_close)
def window():
    s = st.session_state
    msgs = store.chat_load()
    c1, c2 = st.columns([3, 1])
    if "as_model" not in s:
        s.as_model = default_model()
    c1.selectbox("Model", list(MODELS), key="as_model", format_func=lambda m: f"{MODEL_NAME.get(m, m)} · {MODELS[m]}",
                 label_visibility="collapsed")
    if c2.button("Clear conversation", icon=":material/delete:", width="stretch"):
        store.chat_clear()
        st.rerun(scope="fragment")
    st.caption(("No AI: answers come from keyword matching." if s.as_model == OFFLINE else
                f"The model receives the knowledge base numbers, the proposal under review and the last calculator "
                f"result, without employee names. {ai.budget_text('asisten')}") + " The assistant approves nothing.")
    box = st.container(height=300)
    with box:
        if not msgs:
            st.caption("No conversation yet.")
        for m in msgs:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
    page = s.get("page_ctx", "kelola")
    pick = st.pills("Examples", SUGGEST.get(page, SUGGEST["kelola"]), key=f"as_pick_{len(msgs)}",
                    label_visibility="collapsed")
    q = st.chat_input("Ask a question or ask me to do something ...", key="as_in") or pick
    if q:
        with st.spinner("The assistant is answering ..."):
            text = answer(q, msgs)
        msgs += [{"role": "user", "content": q}, {"role": "assistant", "content": text}]
        store.chat_save(msgs)
        st.rerun(scope="fragment")


def button():
    """Floating button, bottom right, on every page."""
    with st.container(key="fab"):
        if st.button("AI assistant", icon=":material/forum:", type="primary"):
            st.session_state.as_open = True
    if st.session_state.get("as_open"):
        window()


def open_with(question):
    """Open the pop-up and ask a question (used by buttons on the pages)."""
    msgs = store.chat_load()
    text = answer(question, msgs)
    msgs = msgs + [{"role": "user", "content": question}, {"role": "assistant", "content": text}]
    store.chat_save(msgs)
    st.session_state.as_open = True
