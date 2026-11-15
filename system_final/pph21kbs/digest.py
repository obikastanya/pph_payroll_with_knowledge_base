"""Map of a document by a low-cost model before the drafting model reads it.

Each part gets a level: core parts are sent word for word, general parts as a summary, none parts are left out. A
short opening and closing are always sent; a long one is mapped like any other part. A part the map does not mention
counts as core. Core parts are never cut: a selection over the budget is sent whole and reported as over budget.
"""
import concurrent.futures as cf
import hashlib
import json
import re

from . import documents

UNIT_CHARS = 12_000
BATCH_CHARS = 90_000
BUDGET_TOKENS = 40_000
WORKERS = 6
LEVELS = ("core", "general", "none")
ALWAYS = ("opening", "closing")
SUMMARY_NOTE = ("[Summaries of the other parts, written by another model to show what they cover. They are not the "
                "document's words: never quote them; quote only the text above.]")

SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["entries"],
    "properties": {"entries": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["unit", "level", "summary"],
        "properties": {"unit": {"type": "string"}, "level": {"type": "string", "enum": list(LEVELS)},
                       "summary": {"type": "string"}}}}}}

SYSTEM = """You read parts of an Indonesian legal document (a regulation or a company's labour agreement) for a system
that computes PPh 21: the income tax withheld from the wages of permanent employees (pegawai tetap). Each part starts
with <<Uk>> and its reference. Return exactly one entry for EVERY part; "unit" is the key alone, for example "U3".

- level "core": it states or changes something the computation reads: wages, allowances, overtime, THR, bonuses,
  severance or other payments with an amount, benefits in kind, social security contributions or premiums (BPJS, JKK,
  JKM, JHT, JP, JKN) and their wage caps or relief, PTKP, tax rates, brackets or TER, job expense, deductions, the
  withholding method, rounding, tax borne by the government (DTP) and who qualifies (sectors, KLU code lists, income
  limits), the employees or periods covered, the dates of validity, or a definition such provisions use.
  Social security counts even when the document never mentions tax: the premiums an employer pays (JKK, JKM, JKN)
  are part of an employee's gross income for PPh 21, and the employee's own contributions (JHT, JP) are deducted
  from it. So any part about the rate, relief or discount, wage base or cap, period, or which employers or workers
  these contributions apply to is core.
- level "general": tax administration or legal context that applies to PPh 21 withholding but does not change the
  amount (payment or reporting deadlines, documents in general, sanctions), or the legal basis.
- level "none": unrelated to PPh 21 of permanent employees: other taxes (PPN, PPnBM, PBB, bea meterai, PPh 22, 23,
  25, 26, final income tax), customs, other taxpayers or workers (civil servants, pensioners, non-employees) unless
  the document is about their PPh 21, filling instructions and layouts of forms, leave, discipline, safety, and
  procedures without an amount of pay.
When unsure whether a part is core, choose core.

summary: one sentence in the language of the document with the substance; keep numbers, rates, and dates exactly as
written. Do not invent content."""

UNIT_KEY = re.compile(r"\bU(\d+)\b")


def units(doc_id):
    """Parts of a stored document in order; long articles and annexes are split into windows."""
    out = []
    for s in documents.segments(doc_id):
        always = s["kind"] in ALWAYS and documents.tokens(s["text"]) <= documents.ALWAYS_CAP
        pieces = [s["text"]] if always else _windows(s["text"])
        for i, piece in enumerate(pieces, 1):
            label = s["id"] if len(pieces) == 1 else f"{s['id']} (part {i} of {len(pieces)})"
            out.append({"key": f"U{len(out) + 1}", "label": label, "kind": s["kind"], "always": always,
                        "text": piece, "page_start": s.get("page_start"), "page_end": s.get("page_end")})
    return out


def always(u):
    """Sent without a map: a short opening or closing."""
    return u.get("always", u["kind"] in ALWAYS)


def _windows(text):
    out, start = [], 0
    while start < len(text):
        end = min(len(text), start + UNIT_CHARS)
        if end < len(text):
            cut = text.rfind("\n", start + UNIT_CHARS // 2, end)
            end = cut if cut > 0 else end
        out.append(text[start:end])
        start = end
    return out


def _outline(parts):
    return [{"key": u["key"], "label": u["label"], "kind": u["kind"], "always": u["always"], "chars": len(u["text"])}
            for u in parts]


def _text_hash(doc_id):
    return hashlib.sha256((documents.folder(doc_id) / "text.txt").read_bytes()).hexdigest()


def _path(doc_id):
    return documents.folder(doc_id) / "digest.json"


def load(doc_id, model=None):
    """The stored map, or None if missing, unreadable, made from another text or split, or by another model."""
    try:
        record = json.loads(_path(doc_id).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if (record.get("text_sha256") != _text_hash(doc_id) or record.get("units") != _outline(units(doc_id))
            or (model and record.get("model") != model)):
        return None
    return record


def _batches(parts):
    out, cur, size = [], [], 0
    for u in parts:
        if cur and size + len(u["text"]) > BATCH_CHARS:
            out.append(cur)
            cur, size = [], 0
        cur.append(u)
        size += len(u["text"])
    return out + [cur] if cur else out


def _request(doc_id, title, batch, call_id):
    user = f"DOCUMENT: {title or doc_id}\n\n" + "\n\n".join(
        f"<<{u['key']}>> {u['label']}\n{u['text'].strip()}" for u in batch)
    return dict(system=SYSTEM, prefix=[], user=user, schema=SCHEMA, schema_name="digest", effort="low",
                step="digest", document=doc_id, call_id=call_id, max_tokens=32000)


def build(doc_id, client, title="", call_prefix=""):
    """Map a document, or return its stored map. The map is stored only when every call answered."""
    stored = load(doc_id, client.model)
    if stored:
        return stored
    all_units = units(doc_id)
    parts = [u for u in all_units if not always(u)]

    def one(i, batch):
        _, out, entry = client.complete(**_request(doc_id, title, batch, f"{call_prefix}digest{i + 1}"))
        return out, entry.get("cost_usd") or 0.0

    batches = _batches(parts)
    results = []
    if batches and getattr(client, "batched", False):     # a batch client takes all requests of the document at once
        outs = client.complete_many([_request(doc_id, title, b, f"{call_prefix}digest{i + 1}")
                                     for i, b in enumerate(batches)])
        results = [(out, entry.get("cost_usd") or 0.0) for _, out, entry in outs]
    elif batches:
        with cf.ThreadPoolExecutor(max_workers=min(WORKERS, len(batches))) as ex:
            results = list(ex.map(lambda a: one(*a), enumerate(batches)))
    keys = {u["key"] for u in parts}
    entries = {}
    for out, _ in results:
        for e in (out or {}).get("entries") or []:
            m = UNIT_KEY.search(str(e.get("unit", "")))
            key = f"U{m.group(1)}" if m else None
            if key in keys and e.get("level") in LEVELS:
                entries[key] = {"level": e["level"], "summary": (e.get("summary") or "").strip()}
    record = {"document": doc_id, "model": client.model, "text_sha256": _text_hash(doc_id),
              "units": _outline(all_units), "entries": entries, "calls": len(batches),
              "failed_calls": sum(out is None for out, _ in results),
              "cost_usd": round(sum(c for _, c in results), 6)}
    if not record["failed_calls"]:
        _path(doc_id).write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    return record


def level(record, key):
    entry = record["entries"].get(key)
    return entry["level"] if entry else "core"


def counts(record):
    out = dict.fromkeys(LEVELS, 0)
    for u in record["units"]:
        if not always(u):
            out[level(record, u["key"])] += 1
    return out


def usable(record):
    """A complete map of a document with parts, at least one of them core."""
    c = counts(record)
    return bool(record["units"]) and not record["failed_calls"] and (c["core"] > 0 or c["general"] + c["none"] == 0)


def select(doc_id, record):
    """The text for the drafting model as a documents.Selection: short opening and closing, every core part word for
    word (an annex window that repeats an extracted table as the table's description), general parts as summaries. Nothing core is cut;
    the caller reports a selection above BUDGET_TOKENS as over budget."""
    tables = documents.extracted_tables(doc_id)
    chosen, kept, summaries, dropped = [], set(), [], []
    for u in units(doc_id):
        seg = {"id": u["label"], "kind": u["kind"], "page_start": u["page_start"], "page_end": u["page_end"]}
        lv = None if always(u) else level(record, u["key"])
        if lv is None:
            kept.add(len(chosen))
            chosen.append(dict(seg, text=u["text"]))
        elif lv == "core" and u["kind"] == "annex" and tables and documents.table_like(u["text"], doc_id):
            if not any(s["kind"] == "annex" and i in kept for i, s in enumerate(chosen)):
                kept.add(len(chosen))
                chosen.append(dict(seg, text="\n".join(documents.table_text(t) for t in tables)))
        elif lv == "core":
            chosen.append(dict(seg, text=u["text"]))
        elif lv == "general":
            summaries.append(f"- {u['label']}: {record['entries'][u['key']]['summary']}")
        else:
            dropped.append(u["label"])
    block = SUMMARY_NOTE + "\n" + "\n".join(summaries) if summaries else ""
    used = sum(documents.tokens(s["text"]) for s in chosen) + (documents.tokens(block) if block else 0)
    if block:
        chosen.append({"id": "summaries", "kind": "summary", "text": block})
    return documents.Selection(doc_id, chosen, tables, dropped, used)
