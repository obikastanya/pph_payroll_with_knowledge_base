"""Records back to Delta-element JSON (format_data.md 2): fingerprints, LLM context, diffs, and Delta export."""
from fractions import Fraction

from .model import Constraint, FactDef, Parameter, Rule, TableVersion, Tombstone, json_value


def fraction_text(v):
    """Exact decimal text of a Fraction whose denominator has only factors 2 and 5, else "p/q"."""
    d, k2, k5 = v.denominator, 0, 0
    while d % 2 == 0:
        d //= 2
        k2 += 1
    while d % 5 == 0:
        d //= 5
        k5 += 1
    if d != 1:
        return f"{v.numerator}/{v.denominator}"
    places = max(k2, k5)
    scaled = v.numerator * (10 ** places) // v.denominator
    sign = "-" if scaled < 0 else ""
    digits = str(abs(scaled)).rjust(places + 1, "0")
    return f"{sign}{digits[:-places]}.{digits[-places:]}" if places else f"{sign}{digits}"


def _row_json(row):
    return {k: (json_value(v) if isinstance(v, Fraction) else v) for k, v in row.items()}


def record_to_json(r, with_source=True):
    out = {"kind": r.kind, "id": r.id, "recorded_on": r.recorded_on.isoformat()}
    if r.valid_from is not None:
        out["valid_from"] = r.valid_from.isoformat()
    if r.valid_until is not None:
        out["valid_until"] = r.valid_until.isoformat()
    if r.label:
        out["label"] = r.label
    if getattr(r, "label_id", ""):
        out["label_id"] = r.label_id
    if isinstance(r, Rule):
        out.update(layer=r.layer, modality=r.modality, scope=r.scope, produces=r.produces,
                   expression=r.expression.text)
        if r.condition is not None:
            out["condition"] = r.condition.text
        if r.fixed_point:
            out["fixed_point"] = {"lower": r.fixed_point[0].text, "upper": r.fixed_point[1].text}
        if r.overrides:
            out["overrides"] = list(r.overrides)
        if r.policy:
            out["policy"] = r.policy
        if r.conflict_code:
            out["conflict_code"] = r.conflict_code
    elif isinstance(r, Parameter):
        v = r.value
        if isinstance(v, Fraction):
            v = fraction_text(v)
        out.update(name=r.name, value=v, value_type=r.value_type)
    elif isinstance(r, TableVersion):
        out.update(name=r.name, table_kind=r.table_kind)
        if r.rows_ref:
            out["rows_ref"] = r.rows_ref
        else:
            out["rows"] = [_row_json(x) for x in r.rows]
    elif isinstance(r, Constraint):
        out.update(scope=r.scope, assertion=r.assertion.text, conflict_code=r.conflict_code)
        if r.condition is not None:
            out["condition"] = r.condition.text
    elif isinstance(r, FactDef):
        out.update(fact_type=r.fact_type, fact_scope=r.fact_scope, output=r.output)
        if r.unit:
            out["unit"] = r.unit
    elif isinstance(r, Tombstone):
        out["kind"] = "tombstone"
    if with_source:
        out["source"] = [s.to_json() for s in r.source]
    return out
