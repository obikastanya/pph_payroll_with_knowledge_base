"""Load, validate, and apply updates Delta = <add, change, remove> (akuisisi.md Definition 5, format_data.md 2)."""
import csv
import json
from datetime import date
from functools import lru_cache
from pathlib import Path

import jsonschema

from ..config import REPO
from ..expr import Expression, ExpressionError, PrecisionError, decimal_value
from .model import (Constraint, Document, FactDef, Parameter, Rule, Source, TableVersion, Tombstone, value_of)
from .store import KnowledgeBase, UpdateError, UpdateInfo

SCHEMA_DIR = REPO / "system" / "schemas"
TEXT_DIR = REPO / "dataset" / "13_teks"


@lru_cache(maxsize=None)
def schema(name):
    return json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))


def validate_delta_json(delta):
    """Raise jsonschema.ValidationError if the Delta does not follow system/schemas/delta.schema.json."""
    jsonschema.validate(delta, schema("delta"))


def load_delta(path):
    delta = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_delta_json(delta)
    return delta


def _date(text):
    return None if text in (None, "") else date.fromisoformat(text)


def _sources(items):
    return tuple(Source(s["document"], s["provision"], s["quote"], s.get("page")) for s in items)


def _expr(text, what, element_id):
    if text in (None, ""):
        return None
    try:
        return Expression(text)
    except (ExpressionError, PrecisionError) as e:
        raise UpdateError(f"{element_id}: {what}: {e}") from None


# ---------------------------------------------------------------------- extracted tables
def default_table_resolver(rows_ref):
    """Rows of an extracted table: dataset/13_teks/<DOC>/tabel/<TABLE>.csv, mapped through rows_ref["columns"]."""
    doc, _, table = rows_ref["extracted_table"].partition("/")
    path = TEXT_DIR / doc / "tabel" / f"{table}.csv"
    if not path.exists():
        raise UpdateError(f"extracted table not found: {rows_ref['extracted_table']} ({path})")
    with open(path, encoding="utf-8", newline="") as f:
        raw = list(csv.DictReader(f))
    filt = rows_ref.get("filter") or {}
    cols = rows_ref["columns"]
    out = []
    for r in raw:
        if any(str(r.get(k, "")) != str(v) for k, v in filt.items()):
            continue
        row = {}
        for target, column in cols.items():
            if column not in r:
                raise UpdateError(f"column {column!r} not in extracted table {rows_ref['extracted_table']}")
            row[target] = r[column]
        out.append(row)
    if not out:
        raise UpdateError(f"extracted table {rows_ref['extracted_table']} gives no rows for filter {filt}")
    return out


def _int_or_none(v):
    if v in (None, "", "null"):
        return None
    if isinstance(v, int) and not isinstance(v, bool):
        return v
    s = str(v).strip().replace("Rp", "").replace(" ", "")
    if _RUPIAH_TEXT.match(s):
        s = s.split(",")[0].replace(".", "")
    try:
        return int(s)
    except ValueError:
        raise UpdateError(f"bound must be a whole number of rupiah, got {v!r}") from None


def _number_text(v, scale):
    if isinstance(v, bool):
        raise UpdateError(f"numeric table value expected, got {v!r}")
    text = str(v).strip().replace(",", ".") if isinstance(v, str) else str(v)
    value = decimal_value(text)
    if scale == "percent":
        from fractions import Fraction
        from ..expr.numbers import normalize
        value = normalize(Fraction(value) / 100)
    return value


_DECIMAL_TEXT = __import__("re").compile(r"^-?[0-9]+(\.[0-9]+)?(/[0-9]+)?$")
_RUPIAH_TEXT = __import__("re").compile(r"^[0-9]{1,3}(\.[0-9]{3})+(,[0-9]+)?$")


def normalize_rows(kind, rows, scale="unit"):
    out = []
    for r in rows:
        if kind == "lookup":
            v = r.get("value")
            if isinstance(v, str) and _DECIMAL_TEXT.match(v.strip()):
                v = decimal_value(v.strip())
                if scale == "percent":
                    v = _number_text(r.get("value"), "percent")
            out.append({"key": str(r["key"]), "value": v})
        elif kind == "bracket":
            out.append({"key": None if r.get("key") in (None, "") else str(r["key"]),
                        "lower": _int_or_none(r.get("lower")) or 0, "upper": _int_or_none(r.get("upper")),
                        "value": _number_text(r["value"], scale)})
        elif kind == "progressive":
            out.append({"lower": _int_or_none(r.get("lower")) or 0, "upper": _int_or_none(r.get("upper")),
                        "rate": _number_text(r.get("rate", r.get("value")), scale)})
        else:
            row = {k: (str(v) if k == "key" else v) for k, v in r.items()}
            out.append(row)
    if kind in ("bracket", "progressive"):
        for r in out:
            if r["upper"] is not None and r["upper"] <= r["lower"]:
                raise UpdateError(f"table row with upper <= lower: {r}")
    return tuple(out)


# ---------------------------------------------------------------------- records
def build_record(e, seq, update_id, resolver=default_table_resolver):
    common = dict(kind=e["kind"], id=e["id"], recorded_on=_date(e["recorded_on"]), source=_sources(e["source"]),
                  seq=seq, update_id=update_id, valid_from=_date(e.get("valid_from")),
                  valid_until=_date(e.get("valid_until")), label=e.get("label", ""),
                  label_id=e.get("label_id") or "")
    if common["valid_from"] and common["valid_until"] and common["valid_until"] < common["valid_from"]:
        raise UpdateError(f"{e['id']}: valid_until before valid_from")
    kind = e["kind"]
    if kind == "rule":
        fp = e.get("fixed_point")
        fixed = None
        if fp:
            fixed = (_expr(fp["lower"], "fixed_point.lower", e["id"]), _expr(fp["upper"], "fixed_point.upper", e["id"]))
        if e["layer"] == "company" and not e.get("policy"):
            raise UpdateError(f"{e['id']}: company rule without policy")
        return Rule(**common, layer=e["layer"], modality=e["modality"], scope=e["scope"], produces=e["produces"],
                    condition=_expr(e.get("condition"), "condition", e["id"]),
                    expression=_expr(e["expression"], "expression", e["id"]),
                    fixed_point=fixed, overrides=tuple(e.get("overrides", [])),
                    conflict_code=e.get("conflict_code"), policy=e.get("policy"))
    if kind == "parameter":
        try:
            value = value_of(e["value"], e["value_type"])
        except (ValueError, PrecisionError) as err:
            raise UpdateError(f"{e['id']}: {err}") from None
        return Parameter(**common, name=e["name"], value=value, value_type=e["value_type"])
    if kind == "table":
        if "rows_ref" in e:
            rows = normalize_rows(e["table_kind"], resolver(e["rows_ref"]), e["rows_ref"].get("value_scale", "unit"))
        else:
            rows = normalize_rows(e["table_kind"], e["rows"])
        return TableVersion(**common, name=e["name"], table_kind=e["table_kind"], rows=rows,
                            rows_ref=e.get("rows_ref"))
    if kind == "constraint":
        return Constraint(**common, scope=e["scope"], condition=_expr(e.get("condition"), "condition", e["id"]),
                          assertion=_expr(e["assertion"], "assertion", e["id"]), conflict_code=e["conflict_code"])
    if kind == "fact":
        return FactDef(**common, fact_type=e["fact_type"], fact_scope=e["fact_scope"], output=bool(e.get("output")),
                       unit=e.get("unit", ""))
    raise UpdateError(f"unknown element kind {kind!r}")


def apply_delta(kb, delta, update_id=None, resolver=default_table_resolver, validate=True, lenient=False):
    """K' = K (+) Delta. Raises UpdateError when an operation does not fit the knowledge base.

    lenient=True is the transplant mode (akuisisi.md Definition 5): change of an absent id becomes add, add of a
    present id becomes change, remove of an absent id is skipped. Adjustments are listed in the update note."""
    if validate:
        validate_delta_json(delta)
    update_id = update_id or delta["delta_id"]
    if any(u.update_id == update_id for u in kb.updates):
        raise UpdateError(f"update id already used: {update_id}")
    seq = kb.next_seq
    first = seq
    new, seen, adjustments = [], set(), []
    for op in ("add", "change"):
        for e in delta[op]:
            if e["id"] in seen:
                raise UpdateError(f"{e['id']}: appears twice in the same Delta")
            seen.add(e["id"])
            rec = build_record(e, seq, update_id, resolver)
            prior = [r for r in kb.history(e["id"])]
            live = kb.effective(e["id"], rec.recorded_on)
            if op == "add" and live is not None:
                if not lenient:
                    raise UpdateError(f"{e['id']}: add for an id that already exists; use change")
                adjustments.append(f"add->change {e['id']}")
            if op == "change":
                if not prior:
                    if not lenient:
                        raise UpdateError(f"{e['id']}: change for an id that does not exist; use add")
                    adjustments.append(f"change->add {e['id']}")
                    prior = [rec]
                if prior[-1].kind != rec.kind and not isinstance(prior[-1], Tombstone):
                    raise UpdateError(f"{e['id']}: change from {prior[-1].kind} to {rec.kind}")
            new.append(rec)
            seq += 1
    for e in delta["remove"]:
        if e["id"] in seen:
            raise UpdateError(f"{e['id']}: removed and changed in the same Delta")
        if not kb.history(e["id"]):
            if not lenient:
                raise UpdateError(f"{e['id']}: remove for an id that does not exist")
            adjustments.append(f"remove skipped {e['id']}")
            continue
        new.append(Tombstone(kind="tombstone", id=e["id"], recorded_on=_date(e["recorded_on"]),
                             source=_sources(e["source"]), seq=seq, update_id=update_id))
        seq += 1
    doc = delta["document"]
    documents = {doc["id"]: Document(doc["id"], doc.get("title", ""), _date(doc.get("issued")))}
    recorded = max((r.recorded_on for r in new), default=_date(doc.get("issued")))
    note = delta.get("note", "") + (f" [lenient: {'; '.join(adjustments)}]" if adjustments else "")
    info = UpdateInfo(update_id, delta["delta_id"], delta.get("event_id"), doc["id"], recorded, first, seq - 1,
                      note)
    adoptions = {doc["id"]: tuple(delta.get("adopts") or ())} if delta.get("adopts") else None
    return kb.extended(new, info, documents, adoptions)


def empty_kb(name="K"):
    return KnowledgeBase(name=name)
