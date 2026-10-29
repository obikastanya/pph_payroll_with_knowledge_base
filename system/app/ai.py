"""The real AI of the application, through the research pipeline and its budget ledger.

- upload(): an uploaded PDF/TXT becomes a document of the inbox (Docling extraction, segments, registry), as in the
  research corpus (dataset/13_teks/UPLOAD-*, not committed).
- read(): the acquisition pipeline of the research (relevance, m candidate Deltas, gates G1-G5, one repair round,
  behavioural agreement or abstain) with Claude, on the knowledge base in use.
- repair(): one more repair round of a proposal with the reviewer's note added to the gate messages
  (prompts.repair_user, the research's own repair prompt), then gates G1-G5 again. Not part of the research results.
- chat(): the assistant on an OpenAI model. It answers and picks at most one action of the app; the app carries the
  action out with its own code (drafts go to Review). It never approves anything.

Every call is logged by the research ledger in experiments/app-*/calls.jsonl (not committed), so the provider limits of
config.BUDGET_USD hold for the app as well, and each kind of work has its own cumulative limit (LIMITS).
"""
import json
import re
import time
from datetime import date

import store  # noqa: F401  (puts system/ and system/tools on the path)
from pph21kbs import config
from pph21kbs.corpus import Event
from pph21kbs.pipeline import llm

ASSISTANT_MODEL = "gpt-5.4-mini"
# USD per million tokens (developers.openai.com, model page of gpt-5.4-mini). Cached input is counted at the full
# input price, so the ledger never counts less than was spent.
llm.PRICES.setdefault(ASSISTANT_MODEL, {"input": 0.75, "output": 4.50, "cache_read": 0.75, "cache_write": 0.75})
LIMITS = {"akuisisi": 4.0, "perbaikan": 1.5, "asisten": 1.0}          # USD, cumulative per kind of work
PROVIDER = {"akuisisi": "anthropic", "perbaikan": "anthropic", "asisten": "openai"}


# ---------------------------------------------------------------- budget
def ledger(kind):
    return llm.Ledger(f"app-{kind}", run_limit_usd=LIMITS[kind])


def spent(kind):
    return ledger(kind).spent_run()


def provider_left(provider):
    return round(config.BUDGET_USD[provider] - llm.spent_total(llm.EXPERIMENTS, provider), 4)


def ready(kind):
    """(usable, reason): a key for the provider, and money left both for this kind of work and for the provider."""
    provider = PROVIDER[kind]
    key = config.anthropic_key() if provider == "anthropic" else config.openai_key()
    if not key:
        return False, f"kunci API {provider} tidak ada di .env"
    if spent(kind) >= LIMITS[kind]:
        return False, f"batas aplikasi untuk {kind} (USD {LIMITS[kind]}) sudah terpakai"
    if provider_left(provider) <= 0.05:
        return False, f"anggaran {provider} penelitian hampir habis"
    return True, ""


def budget_text(kind):
    return (f"Terpakai USD {spent(kind):.3f} dari batas aplikasi USD {LIMITS[kind]:g} untuk {kind}; sisa anggaran "
            f"{PROVIDER[kind]} USD {provider_left(PROVIDER[kind]):.2f}.").replace(".", ",").rstrip(",") + "."


# ---------------------------------------------------------------- documents
def _doc_row(item):
    return {"id": item["doc"], "event": item["id"], "role": "upload", "issued": item["issued"], "title": item["title"],
            "files": ""}


def register(items):
    """Put the uploaded documents of the inbox in the document registry (needed by gates G1 and G2); the registry is
    read once per process, so this is done at every start."""
    from pph21kbs.text import registry
    reg = registry()
    for x in items:
        if x.get("upload") and x["doc"] not in reg:
            reg[x["doc"]] = _doc_row(x)


def upload(file, title, issued, kind, force_ocr=False):
    """The uploaded file as a document of the inbox, in the locked-text format of the corpus. Returns the inbox item."""
    import shutil

    import build_texts
    from pph21kbs import pdf_extract, text
    doc_id = "UPLOAD-" + re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-").upper()[:40]
    folder = text.TEXT_DIR / doc_id
    shutil.rmtree(folder, ignore_errors=True)                       # a new upload under the same title
    folder.mkdir(parents=True)
    if file.name.lower().endswith(".pdf"):
        source = folder / "sumber.pdf"
        source.write_bytes(file.getvalue())
        ext = pdf_extract.extract(source, force_ocr=force_ocr)
        pdf_extract.write(ext, folder)
        raw = ext.text()
    else:
        raw = file.getvalue().decode("utf-8", errors="replace")
        if "=== PDF hlm." not in raw:
            raw = "=== PDF hlm. 1 ===\n" + raw
        (folder / "teks.txt").write_text(raw, encoding="utf-8")
    company = kind == "kebijakan"
    (folder / "segmen.json").write_text(json.dumps(build_texts.segment(raw, company), ensure_ascii=False),
                                        encoding="utf-8")
    item = {"id": doc_id, "doc": doc_id, "kind": kind, "title": title, "issued": issued.isoformat(), "run": None,
            "upload": True, "research": None, "why": ""}
    for cached in (text.pages, text.normalized, text.segments):
        cached.cache_clear()
    text.registry().pop(doc_id, None)
    register([item])
    return item


def event_of(item):
    issued = date.fromisoformat(item["issued"])
    return Event(item["id"], "unggahan", True, (item["doc"],), issued, None, None, "",
                 "company" if item["kind"] == "kebijakan" else "regulation", item["title"])


def text_stats(item):
    from pph21kbs import text
    pages = text.pages(item["doc"])
    tables = sorted((text.TEXT_DIR / item["doc"] / "tabel").glob("*.csv"))
    return pages, tables


# ---------------------------------------------------------------- acquisition and repair (Claude)
def read(item, m=3, client=None):
    """Run the research's acquisition pipeline on an inbox document against the knowledge base in use. Writes the run
    to the workspace and records it in the inbox. client: a test client (llm.MockClient) instead of Claude."""
    from pph21kbs.pipeline.run import Config, run_document
    ev = event_of(item)
    led = client.ledger if client is not None else ledger("akuisisi")
    client = client or llm.AnthropicClient(led)
    run_id = f"app-{int(time.time())}"
    policies = (item["doc"],) if ev.layer == "company" else ()
    res = run_document(ev, store.kb(), client, led, Config(m=m), run_id=run_id, out_dir=store.RUNS, policies=policies)
    rel = f"runs/{ev.id}.json"
    store.set_run(item["id"], rel, res.get("cost_usd") or 0.0)
    return res


def _previous_llm(pid, delta):
    """The proposal in the form the model writes (delta_llm), for the repair prompt: the selected candidate's own
    output, or the output of an earlier repair."""
    s = store.load()
    if pid in s["fixed"] and s["fixed"][pid].get("llm"):
        return s["fixed"][pid]["llm"]
    r = store.run(pid)
    if r:
        sel = r.get("selected")
        for c in r.get("candidates", []):
            if c.get("n") == sel and c.get("llm"):
                return c["llm"]
    return None


def can_repair(pid, delta):
    return _previous_llm(pid, delta) is not None and store.pending_by_id().get(pid) is not None


def repair(pid, delta, note, client=None):
    """One repair round of the proposal pid with the reviewer's note, on the knowledge base in use, then gates G1-G5.
    Returns (new delta or None, passed, gate log, cost)."""
    from pph21kbs import corpus
    from pph21kbs.pipeline import context, prompts, select
    from pph21kbs.pipeline.convert import ConversionError, to_delta
    from pph21kbs.pipeline.run import Config, _schema, check, documents_of
    item = store.pending_by_id()[pid]
    try:
        ev = corpus.event(pid)                      # a research document (demo)
    except KeyError:
        ev = event_of(item)
    cfg = Config(m=1)
    base = store.kb()
    docs = documents_of(ev)
    view = base.view(ev.issued)
    selections = [select.select(x["id"], view, cfg.budget_tokens) for x in docs]
    doc_text = "\n\n".join(select.render(x) for x in selections)
    ctx = context.context_text(view, doc_text, records=cfg.with_context)
    led = client.ledger if client is not None else ledger("perbaikan")
    client = client or llm.AnthropicClient(led)
    call_id = f"app-{int(time.time())}-{pid}-reviewer"
    messages = [f"Reviewer's note (Indonesian, from the person who reviews this proposal): {note}"]
    rel = ((store.run(pid) or {}).get("relevance") or {}).get("output")
    _, out, entry = client.complete(system=prompts.SYSTEM_DRAFT, prefix=[doc_text, ctx],
                                    user=prompts.repair_user(ev, docs, _previous_llm(pid, delta), messages),
                                    schema=_schema(), schema_name="delta", effort=cfg.draft_effort,
                                    step="repair-reviewer", document=ev.document, event=ev.id, call_id=call_id,
                                    max_tokens=cfg.max_tokens)
    cost = entry.get("cost_usd") or 0.0
    if out is None:
        return None, False, {"G1": f"fail: {entry.get('error') or 'no parsable output'}"}, cost
    try:
        new = to_delta(out, f"{call_id}", ev.id, docs[0])
    except ConversionError as e:
        return None, False, {"G1": f"fail: {e}"}, cost
    policies = (item["doc"],) if ev.layer == "company" else ()
    ok, log, _, _ = check(base, new, ev, ev.issued, rel, cfg, policies)
    store.set_fixed(pid, new, note, f"AI ({client.model})", llm=out)
    return new, ok, {k: str(v) for k, v in log.items() if k.startswith("G") and k != "G3_warnings"}, cost


# ---------------------------------------------------------------- assistant (OpenAI)
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
is a finance or payroll admin. Answer in plain Indonesian, short, everyday words, no research jargon.

You get CONTEXT: the page the user is on, the knowledge base facts relevant to the question (numbers with their source
articles, recent updates), the proposal under review if any, and the last calculator result if any. Use only the
context for facts about tax rules and numbers; if the context does not say, say you do not know and where to look.

You may pick ONE action that the application then carries out with its own code:
- explain_proposal, check_proposal: the proposal under review (check = are the quotes in the document).
- fix_proposal: the user wants the AI to fix the proposal under review; put the user's instruction in args.note. The
  app fills it in on the Review page; the user starts it (it costs credit).
- why_unsure: why the system abstained on a document.
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
    led = client.ledger if client is not None else ledger("asisten")
    client = client or llm.OpenAIClient(led, model=model)
    convo = "\n".join(f"{m['role']}: {m['content'][:600]}" for m in history[-6:])
    user = f"CONVERSATION SO FAR:\n{convo or '-'}\n\nQUESTION:\n{question}"
    _, out, entry = client.complete(system=SYSTEM_CHAT, prefix=[f"CONTEXT:\n{context}"], user=user,
                                    schema=CHAT_SCHEMA, schema_name="asisten", effort="low", step="assistant",
                                    call_id=f"app-{int(time.time())}-chat", max_tokens=1500)
    cost = entry.get("cost_usd") or 0.0
    if not out:
        return f"Asisten tidak bisa menjawab sekarang ({(entry.get('error') or 'tanpa jawaban')[:120]}).", "none", {}, cost
    return out.get("answer") or "", out.get("action") or "none", out.get("args") or {}, cost
