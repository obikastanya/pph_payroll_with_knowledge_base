"""The work on proposed updates: the AI that reads documents and repairs proposals, the drafts built from forms, and
the assistant.

- upload(): an uploaded PDF or text file becomes a document of the inbox (text, segments, tables, registry entry).
- read(): the acquisition pipeline (relevance, m independent drafts, the automatic checks, one repair round, the
  drafts' agreement or "the AI is not sure") with Claude, against the knowledge base in use.
- repair(): one more repair round of a proposal with the reviewer's note added to the check messages, then the
  checks again.
- Drafts: a new value for a number, a new rule, a change of a rule from a date, a revocation, and company policies
  from examples. They are validated and applied by the library when a person approves them.
- The assistant: a pop-up chat on every page. An OpenAI model answers from the knowledge-base context and picks at
  most one action, which the app carries out with its own code (drafts go to Review). Without a key or budget, or
  when chosen, keyword matching answers instead. It never approves anything.

Every model call is logged in workspace/calls/app-<kind>/calls.jsonl, so the provider limits of config.BUDGET_USD
hold for the app as well, and each kind of work has its own cumulative limit (LIMITS).
"""
import re
import tempfile
import time
from datetime import date, datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import streamlit as st

import common
import state
from pph21kbs import config, documents, draft, pipeline
from pph21kbs.kb import schema


# ====================================================================================================================
# Budget
# ====================================================================================================================
MAIN_MODEL = config.MAIN_MODEL
ASSISTANT_MODEL = "gpt-5.4-mini"
SECOND_MODEL = "gpt-6.1-sol"
LIMITS = {"acquisition": 4.0, "repair": 1.5, "assistant": 1.0, "digest": 2.0}   # USD, cumulative per kind of work
PROVIDER = {"acquisition": "anthropic", "repair": "anthropic", "assistant": "openai", "digest": "openai"}
PROVIDER_NAMES = {"anthropic": "Anthropic", "openai": "OpenAI"}
KIND_LABELS = {"acquisition": "reading documents", "repair": "fixing proposals", "assistant": "the assistant",
               "digest": "mapping documents"}


def ledger(kind):
    return draft.Ledger(f"app-{kind}", limit_usd=LIMITS[kind])


def spent(kind):
    return ledger(kind).spent()


def provider_left(provider):
    """USD left of the provider's total limit, or None when there is no limit."""
    limit = config.BUDGET_USD.get(provider)
    if limit is None:
        return None
    return round(limit - draft.spent_total(provider=provider), 4)


def ready(kind):
    """(usable, reason): a key for the provider, and money left both for this kind of work and for the provider."""
    provider = PROVIDER[kind]
    key = config.anthropic_key() if provider == "anthropic" else config.openai_key()
    if not key:
        return False, f"the {PROVIDER_NAMES[provider]} API key is missing from .env"
    if spent(kind) >= LIMITS[kind]:
        return False, f"the app limit for {KIND_LABELS[kind]} (USD {LIMITS[kind]:g}) is used up"
    left = provider_left(provider)
    if left is not None and left <= 0.05:
        return False, f"the {PROVIDER_NAMES[provider]} budget is almost used up"
    return True, ""


def budget_text(kind):
    provider = PROVIDER[kind]
    left = provider_left(provider)
    rest = (f"{PROVIDER_NAMES[provider]} budget left: USD {left:.2f}." if left is not None
            else f"no overall {PROVIDER_NAMES[provider]} limit is set.")
    return f"Used USD {spent(kind):.3f} of the app limit of USD {LIMITS[kind]:g} for {KIND_LABELS[kind]}; {rest}"


# ====================================================================================================================
# Documents
# ====================================================================================================================
def upload(file, title, issued, kind, force_ocr=False):
    """The uploaded file (PDF or text) as a stored document. kind: "regulation" or "policy". Returns the inbox
    item."""
    doc_id = "UPLOAD-" + re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-").upper()[:40]
    company = kind == "policy"
    if file.name.lower().endswith(".pdf"):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.pdf"
            path.write_bytes(file.getvalue())
            documents.add_document(doc_id, title, issued, pdf=path, company=company, force_ocr=force_ocr)
    else:
        documents.add_document(doc_id, title, issued, text=file.getvalue().decode("utf-8", errors="replace"),
                               company=company)
    return {"id": doc_id, "doc": doc_id, "kind": kind, "title": title, "issued": issued.isoformat(), "run": None,
            "upload": True}


def event_of(item):
    issued = date.fromisoformat(item["issued"])
    return pipeline.Event(item["id"], (item["doc"],), issued, "company" if item["kind"] == "policy" else "regulation",
                          item["title"])


def text_stats(item):
    """(pages as [(number, text)], extracted table files) of an inbox document."""
    return documents.pages(item["doc"]), documents.tables_of(item["doc"])


# ====================================================================================================================
# Acquisition and repair (Claude)
# ====================================================================================================================
def digest_on():
    """Documents are mapped before Claude reads them: switched on, with an OpenAI key and budget left."""
    return config.DIGEST and ready("digest")[0]


def read(item, m=3, client=None, digester=None):
    """Run the acquisition pipeline on an inbox document against the knowledge base in use. Writes the run to the
    workspace and records it in the inbox. client, digester: test clients instead of Claude and OpenAI."""
    ev = event_of(item)
    led = client.ledger if client is not None else ledger("acquisition")
    client = client or draft.AnthropicClient(led)
    if digester is None and client.provider != "mock" and digest_on():
        digester = draft.OpenAIClient(ledger("digest"), model=config.DIGEST_MODEL)
    run_id = f"app-{int(time.time())}"
    policies = (item["doc"],) if ev.layer == "company" else ()
    res = pipeline.run_document(ev, state.kb(), client, led, pipeline.Config(m=m, use_stored_map=True), run_id=run_id,
                                out_dir=state.RUNS, policies=policies, digester=digester)
    state.set_run(item["id"], f"runs/{ev.id}.json", res.get("cost_usd") or 0.0)
    return res


def _previous_llm(pid, delta):
    """The proposal in the form the model writes (delta_llm), for the repair prompt: the output of an earlier repair,
    the hand-edited version converted to that form, or the selected draft's own output."""
    s = state.load()
    if pid in s["fixed"]:
        fixed = s["fixed"][pid]
        if fixed.get("llm"):
            return fixed["llm"]
        try:                                    # edited by hand: the edited version is what the AI repairs
            return draft.to_llm(fixed["delta"])
        except Exception:  # noqa: BLE001 - an edit the model form cannot hold
            return None
    r = state.run(pid)
    if r:
        sel = r.get("selected")
        for c in r.get("drafts", []):
            if c.get("n") == sel and c.get("llm"):
                return c["llm"]
    return None


def can_repair(pid, delta):
    return _previous_llm(pid, delta) is not None and state.pending_by_id().get(pid) is not None


def repair(pid, delta, note, client=None):
    """One repair round of the proposal pid with the reviewer's note, on the knowledge base in use, then the checks.
    Returns (new delta or None, passed, check log, cost)."""
    item = state.pending_by_id()[pid]
    ev = event_of(item)
    cfg = pipeline.Config(m=1, use_stored_map=True)
    base = state.kb()
    docs = pipeline.documents_of(ev)
    view = base.view(ev.issued)
    doc_text, _ = pipeline.document_text(docs, view, cfg)
    ctx = draft.context_text(view, doc_text)
    led = client.ledger if client is not None else ledger("repair")
    client = client or draft.AnthropicClient(led)
    call_id = f"app-{int(time.time())}-{pid}-reviewer"
    messages = [f"Reviewer's note (from the person who reviews this proposal): {note}"]
    rel = ((state.run(pid) or {}).get("relevance") or {}).get("output")
    _, out, entry = client.complete(system=draft.SYSTEM_DRAFT, prefix=[doc_text, ctx],
                                    user=draft.repair_user(ev, docs, _previous_llm(pid, delta), messages),
                                    schema=schema("delta_llm"), schema_name="delta", effort=cfg.draft_effort,
                                    step="repair-reviewer", document=ev.document, event=ev.id, call_id=call_id,
                                    max_tokens=cfg.max_tokens)
    cost = entry.get("cost_usd") or 0.0
    if out is None:
        return None, False, {"G1": f"fail: {entry.get('error') or 'no parsable output'}"}, cost
    try:
        new = draft.to_delta(out, call_id, ev.id, docs[0])
    except draft.ConversionError as e:
        return None, False, {"G1": f"fail: {e}"}, cost
    policies = (item["doc"],) if ev.layer == "company" else ()
    ok, log, _, _ = pipeline.check(base, new, ev, ev.issued, rel, cfg, policies)
    state.set_fixed(pid, new, note, f"AI ({client.model})", llm=out)
    return new, ok, {k: str(v) for k, v in log.items() if k.startswith("G") and not k.endswith("_warnings")}, cost


# ====================================================================================================================
# Drafts built in the app
# ====================================================================================================================
def _id(prefix):
    return f"{prefix}-{datetime.now():%m%d%H%M%S}"


def shown_value(value_type, v):
    """A parameter value as text, by its value type."""
    if v is None:
        return "-"
    if value_type == "rate":
        return state.pct(v)
    if value_type == "money":
        return state.money(v)
    return str(v)


def param_text(name, v):
    """A value of the parameter name as text, by the value type the knowledge base gives the parameter."""
    p = state.params().get(name)
    return shown_value(p.value_type if p else None, v)


def _src(doc, provision, quote):
    return [{"document": doc or "ADMIN-NOTE", "provision": provision or "-", "quote": quote or "(not filled in)"}]


def _num(v, value_type):
    if isinstance(v, Fraction):
        v = Decimal(v.numerator) / Decimal(v.denominator)
    if value_type == "money":
        return int(v)
    return str(v) if isinstance(v, Decimal) else v


def record_json(r):
    """A knowledge-base record as an update element (for change and revoke)."""
    e = {"kind": r.kind, "id": r.id, "recorded_on": state.TODAY.isoformat(),
         "source": [s.to_json() for s in r.source]}
    if r.valid_from:
        e["valid_from"] = r.valid_from.isoformat()
    if r.valid_until:
        e["valid_until"] = r.valid_until.isoformat()
    for f in ("label", "label_id"):
        if getattr(r, f, ""):
            e[f] = getattr(r, f)
    if r.kind == "rule":
        e.update({"layer": r.layer, "modality": r.modality, "scope": r.scope, "produces": r.produces,
                  "expression": state.expr_text(r.expression)})
        if r.condition:
            e["condition"] = state.expr_text(r.condition)
        if r.overrides:
            e["overrides"] = list(r.overrides)
        if r.conflict_code:
            e["conflict_code"] = r.conflict_code
        if r.fixed_point:
            lower, upper = r.fixed_point
            e["fixed_point"] = {"lower": state.expr_text(lower), "upper": state.expr_text(upper)}
        if r.policy:
            e["policy"] = r.policy
    elif r.kind == "parameter":
        e.update({"name": r.name, "value": _num(r.value, r.value_type), "value_type": r.value_type})
    return e


def _delta(prefix, title, issued, add=(), change=()):
    did = _id(prefix)
    return {"delta_id": did, "event_id": None, "document": {"id": did, "title": title, "issued": issued.isoformat()},
            "relevant": True, "add": list(add), "change": list(change), "remove": [], "note": "made in the app"}


def current_param(name, at=None):
    at = at or state.TODAY
    vs = sorted((r for r in state.kb().records if r.kind == "parameter" and r.name == name),
                key=lambda r: r.valid_from)
    live = [r for r in vs if r.valid_from <= at and (r.valid_until is None or at <= r.valid_until)]
    return (live or vs)[-1]


def new_value(name, value, start, doc, provision, quote):
    """A new value of a number from a date; the value in force then ends the day before."""
    old = current_param(name, start)
    src = _src(doc, provision, quote)
    add = {"kind": "parameter", "id": f"PAR.{name.upper()}.{start:%Y%m}", "name": name, "value": value,
           "value_type": old.value_type, "valid_from": start.isoformat(), "recorded_on": state.TODAY.isoformat(),
           "source": src, "label_id": old.label_id}
    if old.label:
        add["label"] = old.label
    change = []
    if old.valid_from < start and (old.valid_until is None or old.valid_until >= start):
        ch = record_json(old)
        ch["valid_until"] = (start - timedelta(days=1)).isoformat()
        ch["source"] = src
        change.append(ch)
    shown = shown_value(old.value_type, value)
    return _delta("VALUE", f"{state.fact_label(name)} becomes {shown} from {state.fmt_date(start)}", state.TODAY,
                  [add], change)


def new_rule(produces, expression, condition, start, end, company, policy, doc, provision, quote):
    e = {"kind": "rule", "id": f"{'PRS.' + policy if company else 'REG.ADMIN'}.{produces.upper()}.{start:%Y%m}",
         "layer": "company" if company else "regulation", "modality": "default" if company else "mandatory",
         "scope": ("period" if state.facts().get(produces) is None or state.facts()[produces].fact_scope == "period"
                   else "year"),
         "produces": produces, "expression": expression, "valid_from": start.isoformat(),
         "recorded_on": state.TODAY.isoformat(), "source": _src(doc, provision, quote)}
    if condition:
        e["condition"] = condition
    if end:
        e["valid_until"] = end.isoformat()
    if company:
        e["policy"] = policy
    return _delta("RULE", f"New rule: {state.fact_label(produces)}", state.TODAY, [e])


def change_rule(rule, expression, start, doc, provision, quote):
    """The rule ends the day before start; a new version with the new formula starts then."""
    old = record_json(rule)
    old["valid_until"] = (start - timedelta(days=1)).isoformat()
    old["source"] = _src(doc, provision, quote)
    new = record_json(rule)
    new.update({"id": f"{rule.id}.V{start:%Y%m}", "expression": expression, "valid_from": start.isoformat(),
                "source": _src(doc, provision, quote)})
    new.pop("valid_until", None)
    return _delta("CHANGE", f"Change: {state.fact_label(rule.produces)} from {state.fmt_date(start)}", state.TODAY,
                  [new], [old])


def revoke(rule, end, doc, provision, quote=""):
    e = record_json(rule)
    e["valid_until"] = end.isoformat()
    e["source"] = _src(doc, provision, quote or "revoked")
    return _delta("REVOKE", f"Revoke: {state.fact_label(rule.produces)} after {state.fmt_date(end)}", state.TODAY,
                  [], [e])


def find_rule(text):
    ql = text.lower()
    best = None
    for r in state.kb().view(state.TODAY).rules.values():
        if state.is_input_convention(r):
            continue
        words = re.findall(r"[a-z]{5,}", state.fact_label(r.produces).lower())
        score = sum(w in ql for w in words)
        if score and (best is None or score > best[0]):
            best = (score, r)
    return best[1] if best else None


def _policy(pid, title, start, rules):
    did = _id("POLICY")
    for r in rules:
        r.update({"kind": "rule", "layer": "company", "modality": "default", "scope": "period", "policy": pid,
                  "valid_from": start.isoformat(), "recorded_on": state.TODAY.isoformat()})
        r.setdefault("source", _src(pid, "-", title))
    return {"delta_id": did, "event_id": None,
            "document": {"id": pid, "title": title, "issued": state.TODAY.isoformat()}, "relevant": True,
            "add": rules, "change": [], "remove": [], "note": "policy from an example"}


def meal_policy(amount, pid="PRS-COMPANY", start=None):
    start = start or date(state.TODAY.year + 1, 1, 1)
    return _policy(pid, f"Policy {pid}: meal allowance Rp{amount:,} per day present", start, [
        {"id": f"PRS.{pid}.MEAL", "produces": "other_regular_income",
         "expression": f"{amount} * hr('days_present') + income('other_regular')"}])


def thr_policy(times, pid="PRS-COMPANY", start=None):
    start = start or date(state.TODAY.year + 1, 1, 1)
    return _policy(pid, f"Policy {pid}: THR {times:g} × wages in the month of the religious holiday", start, [
        {"id": f"PRS.{pid}.THR", "produces": "thr",
         "expression": f"round(dec('{times}') * (base_salary + fixed_allowance), 1, 'down') if hr('thr_holiday') == 1 "
                       f"else income('thr')"}])


def bonus_policy(percent, month, pid="PRS-COMPANY", start=None):
    start = start or date(state.TODAY.year + 1, 1, 1)
    return _policy(pid, f"Policy {pid}: bonus {percent:g}% of base salary every {state.MONTHS[month - 1]}", start, [
        {"id": f"PRS.{pid}.BONUS", "produces": "bonus",
         "expression": f"round(dec('{percent / 100}') * base_salary, 1, 'down') if month == {month} "
                       f"else income('bonus')"}])


# ====================================================================================================================
# Assistant model (OpenAI)
# ====================================================================================================================
ACTIONS = ("none", "explain_proposal", "check_proposal", "fix_proposal", "why_unsure", "new_value", "revoke",
           "meal_policy", "calc_why", "lookup")
CHAT_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["answer", "action", "args"],
    "properties": {
        "answer": {"type": "string"},
        "action": {"type": "string", "enum": list(ACTIONS)},
        "args": {"type": "object", "additionalProperties": False,
                 "required": ["param", "value", "start", "rule", "note", "amount"],
                 "properties": {"param": {"type": ["string", "null"]}, "value": {"type": ["number", "null"]},
                                "start": {"type": ["string", "null"]}, "rule": {"type": ["string", "null"]},
                                "note": {"type": ["string", "null"]}, "amount": {"type": ["number", "null"]}}}}}
SYSTEM_CHAT = """You are the assistant of a knowledge-based system for Indonesian PPh 21 (employee income tax). The user
is a finance or payroll admin. Answer in plain English, short, everyday words, no technical jargon. Keep Indonesian
terms that have no English equivalent (PPh 21, PTKP, TER, BPJS, THR, NPWP) and quotes from documents as they are.

You get CONTEXT: the page the user is on, the knowledge base facts relevant to the question (numbers with their source
articles, recent updates), the proposal under review if any, and the last calculator result if any. Use only the
context for facts about tax rules and numbers; if the context does not say, say you do not know and where to look.

You may pick ONE action that the application then carries out with its own code:
- explain_proposal, check_proposal: the proposal under review (check = are the quotes in the document).
- fix_proposal: the user wants the AI to fix the proposal under review; put the user's instruction in args.note. The
  app fills it in on the Review page; the user starts it (it costs credit).
- why_unsure: why the AI was not sure about a document.
- new_value: a new value of a number from a date; args.param = the parameter name from the context, args.value,
  args.start (YYYY-MM-DD).
- revoke: end a rule; args.rule = words naming the rule.
- meal_policy: a company meal allowance per day present; args.amount in rupiah.
- calc_why: explain the last calculator result.
- lookup: the current value of a number; args.param = the parameter name from the context.
- none: just answer.
Never approve, apply or reject anything: drafts always go to Review for a person. Fill unused args with null.
When you pick an action, keep answer to one sentence: the app adds the details."""


def chat(question, history, context, model=ASSISTANT_MODEL, client=None):
    """(answer, action, args, cost). history: earlier messages [{role, content}], the last few are sent."""
    led = client.ledger if client is not None else ledger("assistant")
    client = client or draft.OpenAIClient(led, model=model)
    convo = "\n".join(f"{m['role']}: {m['content'][:600]}" for m in history[-6:])
    user = f"CONVERSATION SO FAR:\n{convo or '-'}\n\nQUESTION:\n{question}"
    _, out, entry = client.complete(system=SYSTEM_CHAT, prefix=[f"CONTEXT:\n{context}"], user=user,
                                    schema=CHAT_SCHEMA, schema_name="assistant", effort="low", step="assistant",
                                    call_id=f"app-{int(time.time())}-chat", max_tokens=1500)
    cost = entry.get("cost_usd") or 0.0
    if not out:
        reason = (entry.get("error") or "no answer")[:120]
        return f"The assistant cannot answer right now ({reason}).", "none", {}, cost
    return out.get("answer") or "", out.get("action") or "none", out.get("args") or {}, cost


# ====================================================================================================================
# Assistant answers
# ====================================================================================================================
OFFLINE = "no-ai"
MODELS = {ASSISTANT_MODEL: "OpenAI · low cost, default (USD 0.75 / 4.50 per million tokens)",
          SECOND_MODEL: "OpenAI · stronger (USD 2 / 10 per million tokens)",
          OFFLINE: "No AI · keyword matching, free"}
# Example questions per page (st.session_state.page_ctx)
SUGGEST = {
    "manage": ["Explain the proposal under review", "Check this proposal against its quotes",
               "Why is the AI not sure about this document?", "Create a meal allowance of Rp50,000 per day present",
               "Revoke the rule on non-holiday gifts", "JP wage cap from 2027 becomes Rp11,600,000"],
    "calculator": ["Why is this month's PPh 21 this amount?", "What is the JP wage cap now?", "What is TER?"],
    "kb": ["What is the JP wage cap now?", "How much is the job expense?", "What changed most recently?"],
}
FROM_ASSISTANT = "request through the assistant"
DAYS_PRESENT_INPUT = {"key": "hr.days_present", "label": "Days present", "help": "Number of days present that month.",
                      "type": "int", "group": "monthly", "order": 65}


def _current_item():
    pid = st.session_state.get("mg_open")
    if not pid:
        return None, None
    return pid, state.proposal(pid)


def _latest_uncertain():
    """The most recent inbox document the AI was not sure about, or None."""
    return next((p["id"] for p in reversed(state.pending()) if state.status(p["id"]) == "uncertain"), None)


def _explain(pid, delta):
    els = [e for e in delta.get("add", []) + delta.get("change", []) if e.get("kind") in ("rule", "parameter", "table")]
    touched = sorted({state.fact_label(e.get("produces") or e.get("name") or e["id"]) for e in els})
    starts = sorted({e.get("valid_from") for e in els if e.get("valid_from")})
    title = (delta.get("document") or {}).get("title", pid)
    return (f"**{title}** proposes {len(delta.get('add', []))} additions and {len(delta.get('change', []))} changes, "
            f"in force from {', '.join(starts[:3]) or '-'}. Values affected: {', '.join(touched[:8])}.\n\n"
            "Open the *Review* tab to see before-and-after examples on common scenarios.")


def quote_status(delta):
    """Per element: (what, provision, quote found in the document text or None when the text is not available,
    every number of a money parameter appears in its quote). The quote check, run here and now."""
    out = []
    for e in delta.get("add", []) + delta.get("change", []):
        for s in (e.get("source") or [])[:1]:
            try:
                found = documents.normalize(s.get("quote", "")) in documents.normalized(s.get("document"))[0]
            except Exception:  # noqa: BLE001 - document text not available
                found = None
            num_ok = True
            if e.get("kind") == "parameter" and e.get("value_type") == "money":
                num_ok = str(int(float(e["value"]))) in re.sub(r"\D", "", s.get("quote", ""))
            out.append((state.fact_label(e.get("produces") or e.get("name") or e["id"]), s.get("provision", ""),
                        found, num_ok))
    return out


def _check(pid, delta):
    """Is every quote in the document text, and does every number of a parameter appear in its quote?"""
    lines, problems = [], 0
    for what, provision, found, num_ok in quote_status(delta):
        mark = "✓" if found and num_ok else ("?" if found is None else "⚠")
        problems += mark == "⚠"
        note = "" if found else " · quote not found in the document" if found is False else " · no document text"
        note += "" if num_ok else " · number not in the quote"
        lines.append(f"{mark} {what} ({provision}){note}")
    head = ("All quotes are in the document and their numbers match." if not problems else
            f"{problems} part(s) need a person to check them.")
    return (f"{head}\n\n" + "\n".join(f"- {x}" for x in lines[:14]) +
            "\n\nThis is a second opinion, not a decision. A matching quote does not prove the rule is right: check "
            "its conditions and formula too.")


def stop_reason(r):
    """Why the AI proposed nothing for a document: "budget" (the spending limit stopped it), "unconfirmed" (it found
    the document not relevant but its reason is not in the text), "none_passed" (no draft passed the checks),
    "disagree" (the drafts that passed give different results), or None (it proposed an update or found the document
    not relevant)."""
    status = (r or {}).get("status")
    if status == "budget":
        return "budget"
    if status != "abstain":
        return None
    drafts = r.get("drafts") or []
    if not drafts:
        return "unconfirmed"
    if not any(c.get("passed") for c in drafts):
        return "none_passed"
    return "disagree"


def _why_unsure(pid):
    if not pid:
        return "No document is waiting because the AI was not sure. Open a document in the *Review* tab first."
    r = state.run(pid)
    if not r:
        return "There is no saved AI result for that document."
    why = stop_reason(r)
    drafts = r.get("drafts") or []
    passed = sum(1 for c in drafts if c.get("passed"))
    after = (" You can write the update by hand (the *Company policies* or *Add, change, revoke* tab), or run the AI "
             "again.")
    if why == "budget":
        return ("The AI did not finish this document: it stopped because the spending limit was reached, so it wrote "
                "no proposal." + after)
    if why == "unconfirmed":
        return ("The AI thought the document does not change the PPh 21 calculation, but the reason it gave could not "
                "be found in the document text, so it does not decide." + after)
    if why == "none_passed":
        return (f"The AI wrote {len(drafts)} drafts and none of them passed the automatic checks, so it proposes "
                "nothing." + after)
    if why == "disagree":
        groups = r.get("groups") or []
        return (f"The AI wrote {len(drafts)} drafts; {passed} passed the automatic checks. Those were calculated on "
                f"example cases and grouped by their results: {len(groups)} groups "
                f"({' and '.join(str(len(g)) for g in groups)} drafts). No group is larger than the others, so "
                "the AI is not sure and does not guess." + after)
    if r.get("status") == "empty":
        return "The AI found that this document does not change the PPh 21 calculation."
    return (f"The AI was sure about this document: {passed} of {len(drafts)} drafts passed the checks and the largest "
            "group of drafts that give the same results was chosen.")


def _param(q):
    ql = q.lower()
    best = None
    for name in state.params():
        words = [w for w in re.findall(r"[a-z]+", state.fact_label(name).lower()) if len(w) > 2]
        score = sum(w in ql for w in words)
        if score and (best is None or score > best[0]):
            best = (score, name)
    return best[1] if best else None


def _lookup(name):
    vs = sorted((r for r in state.kb().records if r.kind == "parameter" and r.name == name),
                key=lambda r: r.valid_from)
    cur = [r for r in vs if r.valid_from <= state.TODAY and (r.valid_until is None or state.TODAY <= r.valid_until)]
    r = cur[-1] if cur else vs[-1]

    def shown(v):
        return shown_value(v.value_type, v.value)
    src = r.source[0]
    return (f"**{state.fact_label(name)}** in the knowledge base now: **{shown(r)}**, in force since "
            f"{state.fmt_date(r.valid_from)}.\n\nSource: {state.short_doc(src.document)} {src.provision}, "
            f"“{src.quote}”.\n\nHistory: " + ", ".join(f"{v.valid_from.year}: {shown(v)}" for v in vs[-4:]) +
            f"\n\nThe knowledge base is known up to {state.fmt_date(state.known_until())}.")


def _calc_why():
    last = st.session_state.get("k_last")
    if not last:
        return "Open the Calculator and calculate first; I explain the latest result there."
    m = last["month"]
    due, work = last["due"], last["work"]

    def said(x):
        rid, expr, reads = work[x]
        parts = ", ".join(f"{state.fact_label(k[0]).lower()} {state.fmt(k[0], v)}" for k, v in reads
                          if v not in (None, 0))
        return rid, expr, parts
    rid, expr, parts = said(m)
    text = (f"PPh 21 for {state.MONTHS[m - 1]}: **{state.money(due[m])}**, calculated by rule `{rid}`: "
            f"{state.readable(expr) if expr else '-'} (with {parts or '-'}).")
    prev = max((x for x in due if x < m), default=None)
    if prev:
        prid, _, _ = said(prev)
        before = {k[0]: v for k, v in work[prev][2]}
        moved = [f"{state.fact_label(k[0]).lower()} {state.fmt(k[0], before.get(k[0]))} → {state.fmt(k[0], v)}"
                 for k, v in work[m][2] if k[0] in before and before[k[0]] != v]
        text += f" The month before: {state.money(due[prev])}."
        if prid != rid:
            text += f" This month uses a different rule (`{prid}` → `{rid}`)."
        elif moved:
            text += " What changed: " + "; ".join(moved) + "."
    if last.get("final"):
        text += (" This is the final tax period: the tax for the whole year is recalculated and what was already "
                 "withheld is subtracted.")
    return text + "\n\nThe details and their articles are in the explanation below the result."


def _meal_draft(n):
    """A company meal-allowance policy as a draft for Review, with the new input it reads."""
    delta = meal_policy(n)
    title = delta["document"]["title"]
    state.add_draft(delta["delta_id"], title, delta, "assistant", inputs=[{**DAYS_PRESENT_INPUT, "source": title}])


def _value_draft(name, value, start):
    delta = new_value(name, value, start, FROM_ASSISTANT, "-", "")
    state.add_draft(delta["delta_id"], delta["document"]["title"], delta, "assistant")


def _revoke_draft(rule):
    delta = revoke(rule, date(state.TODAY.year, 12, 31), FROM_ASSISTANT, "-")
    state.add_draft(delta["delta_id"], delta["document"]["title"], delta, "assistant")


def reply(q):
    """(answer, action label or None) by keyword matching. Actions are already carried out (drafts saved) when they
    are returned."""
    ql = q.lower()
    pid, delta = _current_item()
    if "explain" in ql and "proposal" in ql:
        return (_explain(pid, delta) if delta else "Pick a proposal in the *Review* tab first."), None
    if "check" in ql and "proposal" in ql:
        return (_check(pid, delta) if delta else "Pick a proposal in the *Review* tab first."), None
    if re.search(r"\bfix\b", ql):
        if not pid:
            return "Pick a proposal in the *Review* tab first, then write your note.", None
        return act("fix_proposal", {"note": q}, q), "repair"
    if "not sure" in ql or "unsure" in ql:
        return _why_unsure(pid or _latest_uncertain()), None
    if "meal allowance" in ql and re.search(r"\b(add|create)\b", ql):
        amt = re.search(r"(\d[\d,.]*)\s*(thousand|k\b)?", ql)
        n = int(re.sub(r"\D", "", amt.group(1))) * (1000 if amt.group(2) else 1) if amt else 50_000
        _meal_draft(n)
        return (f"I have drafted a company policy: **meal allowance {state.money(n)} × days present**, regular "
                "income, in force from 1 January next year. This rule reads a new input, *days present*, so after "
                "approval the field appears in the calculator by itself. Check it in the *Review* tab."), "draft"
    if re.search(r"\brevoke\b", ql):
        rule = find_rule(q)
        if not rule:
            return "Which rule should be revoked? Name it, for example \"revoke the rule on non-holiday gifts\".", None
        _revoke_draft(rule)
        return (f"A draft revocation of **{state.fact_label(rule.produces)}** "
                f"({state.short_doc(rule.source[0].document)} "
                f"{rule.source[0].provision}) is in the *Review* tab, in force until 31 Dec {state.TODAY.year}. The "
                "rule is not deleted, only given an end date, so earlier calculations stay the same. Add its legal "
                "basis before approving."), "draft"
    if "becomes" in ql:
        name = _param(q)
        num = re.search(r"rp\s*([\d.,]+)", ql) or re.search(r"([\d.,]{6,})", ql)
        year = re.search(r"\b(20\d\d)\b", ql)
        digits = re.sub(r"\D", "", num.group(1)) if num else ""
        if name and digits:
            value = int(digits)
            start = date(int(year.group(1)) if year else state.TODAY.year + 1, 1, 1)
            _value_draft(name, value, start)
            return (f"Draft new value: **{state.fact_label(name)} = {param_text(name, value)}** from "
                    f"{state.fmt_date(start)}; the old value ends the day before. It is in the *Review* tab. Add the "
                    "document and article it is based on before approving."), "draft"
    if "pph" in ql and any(w in ql for w in ("why", "this amount", "this much", "higher", "went up")):
        return _calc_why(), None
    if any(w in ql for w in ("recent", "latest", "last change", "changed last")):
        u = state.kb().updates[-1]
        return (f"Latest update: **{state.doc_title(u.document)}**, recorded {state.fmt_date(u.recorded_on)}."), None
    if "what is" in ql:
        word = ql.split("what is", 1)[1].strip(" ?")
        for k, (lab, _) in common.TERMS.items():
            if word and (word in k.lower() or word in lab.lower()):
                return common.tip(k), None
    name = _param(q)
    if name and any(w in ql for w in ("how much", "what is", "value")):
        return _lookup(name), None
    return ("I can help you:\n- explain or check the proposal under review;\n- fix a proposal following your note;\n"
            "- explain why the AI was not sure;\n- draft a new value, a new rule, a revocation, or a company policy;\n"
            "- explain the calculator result and the numbers in the knowledge base.\n\nEvery change goes to "
            "*Review*; I never approve anything."), None


# ====================================================================================================================
# The model's actions
# ====================================================================================================================
def _context(q):
    """What the model may use: the page, the numbers of the knowledge base with their source, the latest updates, the
    proposal under review, and the last calculator result. No employee name is sent."""
    s = st.session_state
    lines = [f"Page: {s.get('page_ctx', 'manage')}. Today: {state.TODAY}. Knowledge base known until "
             f"{state.known_until()}."]
    lines.append("NUMBERS OF THE KNOWLEDGE BASE IN FORCE TODAY (parameter name | label | value | source):")
    for name in sorted(state.params()):
        r = state.param_at(name, state.TODAY)
        if r is not None:
            src = r.source[0] if r.source else None
            lines.append(f"- {name} | {state.fact_label(name)} | {shown_value(r.value_type, r.value)}"
                         f" | {state.short_doc(src.document) + ' ' + src.provision if src else '-'}")
    lines.append("LATEST UPDATES: " + "; ".join(f"{state.doc_title(u.document)} ({u.recorded_on})"
                                                for u in state.kb().updates[-5:]))
    pid, delta = _current_item()
    if delta:
        lines.append(f"PROPOSAL UNDER REVIEW ({pid}): " + _explain(pid, delta))
        for e in (delta.get("change", []) + delta.get("add", []))[:12]:
            src = (e.get("source") or [{}])[0]
            lines.append(f"- {e.get('kind')} {e.get('id')} {e.get('produces') or e.get('name') or ''}: "
                         f"{e.get('expression') or e.get('value') or ''} from {e.get('valid_from')} until "
                         f"{e.get('valid_until') or '-'}; source {src.get('provision', '')}: "
                         f"\"{src.get('quote', '')[:160]}\"")
    if s.get("k_last"):
        lines.append("LAST CALCULATOR RESULT: " + _calc_why().split("\n\n")[0])
    return "\n".join(lines)


def act(action, args, q):
    """Carry out the action the model picked, with the app's own code. Returns the text to add, or None."""
    pid, delta = _current_item()
    args = args or {}
    if action in ("explain_proposal", "check_proposal", "fix_proposal") and not delta:
        return "Pick a proposal in the *Review* tab first."
    if action == "explain_proposal":
        return _explain(pid, delta)
    if action == "check_proposal":
        return _check(pid, delta)
    if action == "fix_proposal":
        st.session_state.mg_open, st.session_state.mg_fix = pid, pid
        st.session_state.setdefault("mg_prefill", {})[pid] = args.get("note") or q
        return ("I have put your note into the AI fix of this proposal in *Review*. Check the note, then send it to "
                "the AI: a fix uses Claude credit and the result goes through the automatic checks again.")
    if action == "why_unsure":
        return _why_unsure(pid or _latest_uncertain())
    if action == "calc_why":
        return _calc_why()
    if action == "lookup":
        name = args.get("param") if args.get("param") in state.params() else _param(q)
        return _lookup(name) if name else None
    if action == "new_value":
        name = args.get("param") if args.get("param") in state.params() else _param(q)
        if not name or args.get("value") is None:
            return None
        try:
            start = date.fromisoformat(args.get("start")) if args.get("start") else date(state.TODAY.year + 1, 1, 1)
        except ValueError:
            start = date(state.TODAY.year + 1, 1, 1)
        value = args["value"]
        value = int(value) if float(value).is_integer() else value
        _value_draft(name, value, start)
        return (f"Draft new value: **{state.fact_label(name)} = {param_text(name, value)}** from "
                f"{state.fmt_date(start)}; the old value ends the day before. It is in the *Review* tab. Add the "
                "document and article it is based on before approving.")
    if action == "revoke":
        rule = find_rule(args.get("rule") or q)
        if not rule:
            return "I could not find that rule. Name it, for example \"revoke the rule on non-holiday gifts\"."
        _revoke_draft(rule)
        return (f"A draft revocation of **{state.fact_label(rule.produces)}** "
                f"({state.short_doc(rule.source[0].document)} "
                f"{rule.source[0].provision}) is in the *Review* tab, in force until 31 Dec {state.TODAY.year}.")
    if action == "meal_policy":
        n = int(args.get("amount") or 50_000)
        _meal_draft(n)
        return (f"A draft company policy **meal allowance {state.money(n)} × days present** is in the *Review* tab. "
                "After approval, the *days present* field appears in the calculator by itself.")
    return None


def answer(q, msgs):
    """The reply to a question: the model when one is chosen and usable, else the keyword matching."""
    model = st.session_state.get("as_model") or default_model()
    if model == OFFLINE:
        return reply(q)[0]
    ok, why = ready("assistant")
    if not ok:
        return reply(q)[0] + f"\n\n*Answered without AI: {why}.*"
    try:
        text, action, args, cost = chat(q, msgs, _context(q), model=model)
    except Exception as e:  # noqa: BLE001 - the keyword matching still answers
        return reply(q)[0] + f"\n\n*The model could not be used ({type(e).__name__}); answered without AI.*"
    extra = act(action, args, q) if action != "none" else None
    if extra and action not in ("new_value", "revoke", "meal_policy", "fix_proposal"):
        text = ""             # facts come from the knowledge base through the app's own text, not the model's wording
    return (text + (f"\n\n{extra}" if extra else "")).strip() + f"\n\n<sub>{model} · USD {cost:.4f}</sub>"


def default_model():
    return ASSISTANT_MODEL if ready("assistant")[0] else OFFLINE


# ====================================================================================================================
# Assistant pop-up
# ====================================================================================================================
def _close():
    st.session_state.as_open = False


@st.dialog("AI assistant", width="large", on_dismiss=_close)
def window():
    s = st.session_state
    msgs = state.chat_load()
    c1, c2 = st.columns([3, 1])
    if "as_model" not in s:
        s.as_model = default_model()
    c1.selectbox("Model", list(MODELS), key="as_model", format_func=lambda m: f"{m} · {MODELS[m]}",
                 label_visibility="collapsed")
    if c2.button("Clear conversation", icon=":material/delete:", width="stretch"):
        state.chat_clear()
        st.rerun(scope="fragment")
    st.caption(("No AI: answers come from keyword matching." if s.as_model == OFFLINE else
                "The model receives the knowledge-base numbers, the proposal under review, and the last calculator "
                f"result, without employee names. {budget_text('assistant')}")
               + " The assistant never approves anything.")
    box = st.container(height=300)
    with box:
        if not msgs:
            st.caption("No conversation yet.")
        for m in msgs:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
    page = s.get("page_ctx", "manage")
    pick = st.pills("Examples", SUGGEST.get(page, SUGGEST["manage"]), key=f"as_pick_{len(msgs)}",
                    label_visibility="collapsed")
    q = st.chat_input("Ask a question or ask for something to be done ...", key="as_in") or pick
    if q:
        with st.spinner("The assistant is answering ..."):
            text = answer(q, msgs)
        msgs += [{"role": "user", "content": q}, {"role": "assistant", "content": text}]
        state.chat_save(msgs)
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
    msgs = state.chat_load()
    text = answer(question, msgs)
    msgs = msgs + [{"role": "user", "content": question}, {"role": "assistant", "content": text}]
    state.chat_save(msgs)
    st.session_state.as_open = True
