"""Units of the isolated mode: real regulations, distractors, and company documents, each with its base, gold
update, and test cases. A perfect drafter (the gold update as model output) is provided for dry runs."""
import gzip
import json
from functools import lru_cache

from pph21kbs import documents, draft  # noqa: E402

from . import DATA, corpus, domains, gold, instances
from . import testspace as ts
from .isolated import Unit

SPACE = DATA / "14_ruang_uji"


def _load(name):
    with gzip.open(SPACE / name, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


@lru_cache(maxsize=1)
def general_cases():
    """The v1 test space: 2,398 employee-years 2023-2026 and the 21 cases added by the mutation analysis."""
    return _load("kasus.jsonl.gz") + _load("kasus_terarah.jsonl.gz")


def regulation_unit(event):
    years = ts.event_years(event)
    return Unit(event, gold.base_before(event), gold.expected_delta(event),
                [c for c in general_cases() if c["tax_year"] in years])


def regulation_units(part=("test", "distractor")):
    return [regulation_unit(e) for e in corpus.test_stream() if e.part in part]


def company_event(inst, doc):
    return corpus.Event(doc.id, "company", True, (doc.id,), doc.known_on, doc.policy_from, None, layer="company",
                        title=documents.registry().get(doc.id, {}).get("title", doc.id), gold=doc.gold,
                        extra={"instance": inst.id})


def company_units(insts, panels=None):
    """One unit per company document with a gold update: the base is the gold regulation chain as known on the day
    the company uploads it plus the company's earlier gold updates; the cases are the company's panel."""
    out = []
    for inst in insts:
        fields = fields_of(inst)
        cases = (panels or {}).get(inst.id) or instances.panel(inst, fields=fields)
        base = None
        for doc in sorted(inst.documents, key=lambda d: d.known_on):
            if doc.gold is None or not gold.exists(doc.gold):
                continue
            reg = gold.chain().known_on(doc.known_on)
            base = reg if base is None else _with_company(reg, base)
            ev = company_event(inst, doc)
            first = (doc.policy_from or doc.known_on).year
            out.append(Unit(ev, base, gold.recorded(gold.delta(doc.gold), doc.known_on),
                            [c for c in cases if c["tax_year"] >= first],
                            policies=(doc.id,), extra={"instance": inst.id, "fields": fields}))
            base = gold.apply(base, gold.delta(doc.gold))
    return out


def gold_updates_of(inst):
    return [gold.delta(d.gold) for d in sorted(inst.documents, key=lambda d: d.known_on)
            if d.gold and gold.exists(d.gold)]


def fields_of(inst):
    """The company's payroll fields and their values, from its gold policy updates."""
    updates = gold_updates_of(inst)
    kb = gold.chain()
    for u in updates:
        kb = gold.apply(kb, u)
    return domains.company_fields(updates, kb) if updates else {}


def _with_company(reg, previous):
    """The regulation knowledge base `reg` with the company updates already in `previous`."""
    kb = reg
    for u in previous.updates:
        if u.update_id.startswith("GOLD-") and u.update_id not in {x.update_id for x in kb.updates} \
                and not u.update_id.startswith(("GOLD-E", "GOLD-D", "BG-")):
            kb = gold.apply(kb, gold.delta(u.update_id))
    return kb


# ------------------------------------------------------------------------------------------------- perfect drafter
def _quote_in(doc_id):
    for seg in documents.segments(doc_id):
        for line in seg["text"].splitlines():
            line = line.strip()
            if len(line) > 40 and documents.find_quote(doc_id, line):
                return line[:120]
    return ""


def relevance_output(unit):
    ev, d = unit.event, unit.expected
    relevant = bool(d.get("add") or d.get("change") or d.get("remove"))
    quote = next((s["quote"] for op in ("add", "change") for r in d.get(op, []) for s in r.get("source", [])
                  if s.get("quote")), None) or _quote_in(ev.document)
    return {"relevant": relevant, "layer": ev.layer, "reason": "perfect drafter",
            "quotes": [{"provision": "-", "quote": quote}], "effective_from": None, "effective_from_quote": None,
            "effective_until": None, "effective_until_quote": None, "subjects": []}


def perfect_client(ledger, unit, m=3):
    """A mock client that answers like a drafter who knows the gold update: m identical drafts."""
    return draft.MockClient(ledger, [relevance_output(unit)] + [draft.to_llm(unit.expected)] * m)
