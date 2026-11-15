"""The prospective set: plausible changes that have not happened, written from a specification in the format of real
documents, sealed before any run. Each unit lives in v2/dataset/15_set_prospektif/units/<ID>/:

    spec.json   id, layer (regulation|company), instance (company units), change_type, size, traps, title,
                issued, effective_from, effective_until, retroactive, gold (a delta), triggers (employee-years)
    teks.md     the document text (Indonesian, in the layout of its kind)
    teks.txt    the text extracted from the rendered PDF (written by render.py), what the system reads

A trigger is a compact employee-year: {"id", "year", "salary", optional "ptkp", "klu", "jkk_risk", "relief",
"method", "start_month", "end_month", "income": {key: amount}, "benefits": {...}, "hr": {...}, "employee": {...},
"employer": {...}, "income_months": [months the extra income is paid]}.
"""
import json
from datetime import date

from pph21kbs import documents, draft, engine, gates  # noqa: E402

from . import DATA, gold, instances
from . import testspace as ts
from .isolated import Unit

DIR = DATA / "15_set_prospektif"
UNITS = DIR / "units"
REGULATION_BASE_DAY = date(2026, 12, 31)


def specs():
    return [json.loads((d / "spec.json").read_text(encoding="utf-8"))
            for d in sorted(UNITS.iterdir()) if (d / "spec.json").exists()]


def event_of(spec):
    from .corpus import Event
    return Event(spec["id"], "prospective", True, (spec["id"],), date.fromisoformat(spec["issued"]),
                 date.fromisoformat(spec["effective_from"]),
                 date.fromisoformat(spec["effective_until"]) if spec.get("effective_until") else None,
                 layer=spec["layer"], title=spec["title"], gold=None,
                 extra={"instance": spec.get("instance"), "size": spec["size"], "type": spec["change_type"]})


def base_of(spec):
    """Regulation units: the full gold chain. Company units: the chain as known on the issue day plus the company's
    gold policy updates."""
    issued = date.fromisoformat(spec["issued"])
    if spec["layer"] == "regulation":
        return gold.chain()
    kb = gold.chain().known_on(issued)
    inst = next(i for i in instances.fictional(instances.FICTIONAL_TEST) if i.id == spec["instance"])
    for doc in sorted(inst.documents, key=lambda d: d.known_on):
        if doc.gold and doc.id != spec["id"] and doc.known_on <= issued and gold.exists(doc.gold):
            kb = gold.apply(kb, gold.delta(doc.gold))
    return kb


def case_of(spec, t):
    c = ts.make_case(f"{spec['id']}-{t['id']}", t["year"], t["salary"], t.get("ptkp", "TK/0"), t.get("method", "gross"),
                     "full", "regular")
    start, end = t.get("start_month", 1), t.get("end_month", 12)
    c["employment"] = {"start_month": start, "end_month": end}
    c["periods"] = [p for p in c["periods"] if start <= p["month"] <= end]
    c["employer"].update(klu=t.get("klu", "62019"), jkk_risk_group=t.get("jkk_risk", "very_low"),
                         jkk_relief_eligible=t.get("relief", False),
                         policy=spec.get("policy") if spec["layer"] == "company" else None, **t.get("employer", {}))
    c["employee"].update(t.get("employee", {}))
    months = set(t.get("income_months") or [p["month"] for p in c["periods"]])
    for p in c["periods"]:
        if p["month"] in months:
            p["income"].update(t.get("income", {}))
            p["benefits"].update(t.get("benefits", {}))
        p.setdefault("hr", {}).update(t.get("hr", {}))
    c["criterion"] = "trigger"
    return c


def triggers(spec):
    return [case_of(spec, t) for t in spec.get("triggers", [])]


def unit_of(spec, general=()):
    ev = event_of(spec)
    years = {t["year"] for t in spec.get("triggers", [])}
    cases = triggers(spec) + [c for c in general if c["tax_year"] in years]
    policy = (spec["policy"],) if spec["layer"] == "company" else ()
    return Unit(ev, base_of(spec), spec["gold"], cases, policies=policy,
                extra={"instance": spec.get("instance"), "size": spec["size"], "type": spec["change_type"]})


# ---------------------------------------------------------------------------------------------------- validation
def gate_problems(spec, base, fields=None):
    """The system's gates G1-G6 run on the gold as if it were a draft (through the model format and back, as a
    draft is): a correct answer key must pass them, or the system could never be scored correct on the unit (every
    number and date of an element quoted, and so on)."""
    from dataclasses import replace

    from pph21kbs import pipeline

    from .isolated import as_pipeline_event, set_dictionary
    from .units import relevance_output
    ev = event_of(spec)
    unit = unit_of(spec)
    set_dictionary(fields)
    try:
        doc = {"id": spec["id"], "title": spec["title"], "issued": spec["issued"]}
        try:
            as_draft = draft.to_delta(draft.to_llm(spec["gold"]), f"CHECK-{spec['id']}", spec["id"], doc)
        except draft.ConversionError as e:
            return [f"model format: {e}"]
        cfg = replace(pipeline.Config(), policy_omega=ev.issued)
        ok, log, _, _ = pipeline.check(base, as_draft, as_pipeline_event(ev), ev.issued, relevance_output(unit),
                                       cfg, unit.policies)
    finally:
        set_dictionary(None)
    return [] if ok else [f"{g}: {str(v)[:300]}" for g, v in log.items() if str(v).startswith("fail")]



def validate(spec, fields=None):
    """Problems of one unit (empty when it is usable): the gold applies (G1), every quote is in the extracted text,
    no input outside the payroll data (schema, standard dictionary, the company's fields), no engine error on a
    trigger, and the gold changes the payslip of at least one trigger."""
    problems = []
    ev, base, d = event_of(spec), base_of(spec), spec["gold"]
    r1, kb2 = gates.g1(base, d)
    if not r1.passed:
        return [f"G1: {r1.summary()}"]
    if (documents.folder(spec["id"]) / "text.txt").exists():
        for op in ("add", "change"):
            for el in d.get(op, []):
                for s in el.get("source", []):
                    if documents.find_quote(spec["id"], s["quote"]) is None:
                        problems.append(f"quote not found in {el['id']}: {s['quote'][:70]}")
    else:
        problems.append("not imported yet (no extracted text in the workspace)")
    extra = {(a, k) for a, k in (fields or {})}
    new = [n for n in draft.new_inputs(base.view(ev.issued), d)
           if (n.split("(")[0], n.split("'")[1]) not in extra]
    if new:
        problems.append("inputs outside the payroll data: " + ", ".join(new))
    problems += gate_problems(spec, base, fields)
    changed = 0
    for c in triggers(spec):
        w = max(ev.issued, date(c["tax_year"], 12, 31))
        before, after = engine.evaluate_case(base, c, omega=w), engine.evaluate_case(kb2, c, omega=w)
        if after.errors:
            problems.append(f"engine error on {c['case_id']}: {after.errors[0][:100]}")
        if (before.periods, before.year) != (after.periods, after.year):
            changed += 1
    if not changed:
        problems.append("no trigger's payslip changes")
    return problems
