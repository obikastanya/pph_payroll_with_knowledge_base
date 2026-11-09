"""Knowledge base: immutable records, versions, knowledge-date views, and updates (Deltas).

A record (rule, parameter, table, constraint, fact) is never changed. An update adds new records: a new id, a new
version of an existing id, or a tombstone that removes it. Every record carries its legal validity
(valid_from/valid_until) and the date it became known (recorded_on), so the knowledge base answers two questions:
what applies to period t, and what was known on date omega.
"""
import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from functools import lru_cache

import jsonschema

from . import config
from .expr import Expression, ExpressionError, PrecisionError, decimal_value


# ====================================================================================================================
# Records
# ====================================================================================================================
LAYERS = ("regulation", "company")
MODALITIES = ("mandatory", "default", "optional")
SCOPES = ("period", "year")
FACT_TYPES = ("money", "exact", "rate", "int", "bool", "category", "date")
TABLE_KINDS = ("lookup", "bracket", "progressive", "set")


@dataclass(frozen=True)
class Source:
    document: str
    provision: str
    quote: str
    page: int | None = None

    def to_json(self):
        out = {"document": self.document, "provision": self.provision, "quote": self.quote}
        if self.page is not None:
            out["page"] = self.page
        return out


@dataclass(frozen=True)
class Record:
    kind: str
    id: str
    recorded_on: date
    source: tuple
    seq: int                      # global application order; ties on recorded_on are broken by seq
    update_id: str
    valid_from: date | None = None
    valid_until: date | None = None
    label: str = ""
    label_id: str = ""

    def valid_on(self, d):
        return (self.valid_from is None or self.valid_from <= d) and (self.valid_until is None or d <= self.valid_until)

    @property
    def key(self):
        return (self.recorded_on, self.seq)


@dataclass(frozen=True)
class Rule(Record):
    layer: str = "regulation"
    modality: str = "mandatory"
    scope: str = "period"
    produces: str = ""
    condition: Expression | None = None
    expression: Expression | None = None
    fixed_point: tuple | None = None          # (lower Expression, upper Expression)
    overrides: tuple = ()
    conflict_code: str | None = None
    policy: str | None = None

    @property
    def rank(self):
        """Lex superior rank: mandatory regulation 4, company 3, adopted optional 2, default 1.
        Optional rules get rank 2 only when adopted; the engine checks adoption separately."""
        if self.layer == "company":
            return 3
        return {"mandatory": 4, "optional": 2, "default": 1}[self.modality]


@dataclass(frozen=True)
class Parameter(Record):
    name: str = ""
    value: object = None
    value_type: str = "money"


@dataclass(frozen=True)
class TableVersion(Record):
    name: str = ""
    table_kind: str = "lookup"
    rows: tuple = ()               # tuple of dicts with normalised values
    rows_ref: dict | None = None   # how rows were obtained from an extracted table, if they were


@dataclass(frozen=True)
class Constraint(Record):
    scope: str = "period"
    condition: Expression | None = None
    assertion: Expression | None = None
    conflict_code: str = "C?"


@dataclass(frozen=True)
class FactDef(Record):
    fact_type: str = "money"
    fact_scope: str = "period"
    output: bool = False
    unit: str = ""


@dataclass(frozen=True)
class Tombstone(Record):
    pass


@dataclass(frozen=True)
class Document:
    id: str
    title: str = ""
    issued: date | None = None


def value_of(value, value_type):
    """Normalise a parameter value from JSON to its exact Python value."""
    from .expr import decimal_value
    if value_type in ("money", "int"):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{value_type} value must be an integer, got {value!r}")
        return value
    if value_type in ("exact", "rate"):
        return decimal_value(value if isinstance(value, str) else str(value))
    if value_type == "bool":
        if not isinstance(value, bool):
            raise ValueError(f"bool value expected, got {value!r}")
        return value
    if not isinstance(value, str):
        raise ValueError(f"category value must be text, got {value!r}")
    return value


def json_value(value):
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else value.numerator
    return value


# ====================================================================================================================
# Serialisation of records
# ====================================================================================================================
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


# ====================================================================================================================
# Knowledge base and views
# ====================================================================================================================
class UpdateError(ValueError):
    """A Delta cannot be applied to the knowledge base (wrong operation for an id, kind mismatch, ...)."""


@dataclass(frozen=True)
class UpdateInfo:
    update_id: str
    delta_id: str
    event_id: str | None
    document: str
    recorded_on: date | None
    first_seq: int
    last_seq: int
    note: str = ""


class KnowledgeBase:
    def __init__(self, records=(), updates=(), documents=None, name="K", adoptions=None):
        self.records = tuple(records)
        self.updates = tuple(updates)
        self.documents = dict(documents or {})
        self.adoptions = dict(adoptions or {})     # policy document id -> ids of optional rules it adopts
        self.name = name
        self._views = {}
        self._by_id = None

    # ------------------------------------------------------------------ basics
    @property
    def next_seq(self):
        return self.records[-1].seq + 1 if self.records else 1

    def history(self, element_id):
        """All records of one element id in application order."""
        if self._by_id is None:
            by_id = defaultdict(list)
            for r in self.records:
                by_id[r.id].append(r)
            self._by_id = by_id
        return self._by_id.get(element_id, [])

    def effective(self, element_id, omega):
        """The effective record of an id at knowledge date omega, or None (absent or removed)."""
        best = None
        for r in self.history(element_id):
            if r.recorded_on <= omega and (best is None or r.key > best.key):
                best = r
        if best is None or isinstance(best, Tombstone):
            return None
        return best

    def extended(self, new_records, update, documents=None, adoptions=None):
        docs = dict(self.documents)
        docs.update(documents or {})
        adopt = dict(self.adoptions)
        adopt.update(adoptions or {})
        return KnowledgeBase(self.records + tuple(new_records), self.updates + (update,), docs, self.name, adopt)

    def first_recorded(self, element_id):
        """Recording date of the first record of an element (stable under later revisions)."""
        h = self.history(element_id)
        return h[0].recorded_on if h else None

    def until(self, update_id):
        """Prefix of the knowledge base up to and including the named update."""
        for i, u in enumerate(self.updates):
            if u.update_id == update_id:
                keep = {x.update_id for x in self.updates[: i + 1]}
                recs = [r for r in self.records if r.update_id in keep]
                return KnowledgeBase(recs, self.updates[: i + 1], self.documents, self.name, self.adoptions)
        raise KeyError(update_id)

    def view(self, omega):
        v = self._views.get(omega)
        if v is None:
            v = View(self, omega)
            self._views[omega] = v
        return v

    def fingerprint(self):
        """SHA-256 over the canonical serialisation of all records (stable across runs)."""
        import hashlib
        import json
        h = hashlib.sha256()
        for r in self.records:
            h.update(json.dumps(record_to_json(r), sort_keys=True, ensure_ascii=False).encode("utf-8"))
        return h.hexdigest()


class View:
    """Effective records at knowledge date omega, indexed by what the engine asks for.

    omega filters the regulation layer only. Company-layer records belong to a policy that the case states, so the
    latest record of each company element is used whatever omega is."""

    def __init__(self, kb, omega):
        self.kb = kb
        self.omega = omega
        # every record of a policy update (one that contains company rules) belongs to the company layer, including
        # the facts and parameters the policy defines for its own rules
        policy_updates = {r.update_id for r in kb.records if getattr(r, "layer", None) == "company"}
        latest = {}
        for r in kb.records:
            company = (getattr(r, "layer", None) == "company" or r.id.startswith("PRS.")
                       or r.update_id in policy_updates)
            if company or r.recorded_on <= omega:
                prev = latest.get(r.id)
                if prev is None or r.key > prev.key:
                    latest[r.id] = r
        self.records = [r for r in latest.values() if not isinstance(r, Tombstone)]
        self.records.sort(key=lambda r: r.seq)
        self.rules_by_fact = defaultdict(list)
        self.params = defaultdict(list)
        self.tables = defaultdict(list)
        self.constraints = []
        self.facts = {}
        self.rules = {}
        self.first_recorded = {}
        for r in self.records:
            self.first_recorded[r.id] = kb.first_recorded(r.id)
            if isinstance(r, Rule):
                self.rules_by_fact[r.produces].append(r)
                self.rules[r.id] = r
            elif isinstance(r, Parameter):
                self.params[r.name].append(r)
            elif isinstance(r, TableVersion):
                self.tables[r.name].append(r)
            elif isinstance(r, Constraint):
                self.constraints.append(r)
            elif isinstance(r, FactDef):
                self.facts[r.id] = r
        self._override_closure = {}

    def overrides_closure(self, rule_id):
        """Transitive closure of the overrides relation from one rule (lex specialis)."""
        out = self._override_closure.get(rule_id)
        if out is None:
            out, stack = set(), [rule_id]
            while stack:
                r = self.rules.get(stack.pop())
                if r is None:
                    continue
                for t in r.overrides:
                    if t not in out:
                        out.add(t)
                        stack.append(t)
            self._override_closure[rule_id] = out
        return out

    def output_facts(self, scope):
        return [f for f in self.facts.values() if f.output and f.fact_scope == scope]


# ====================================================================================================================
# Updates (Delta) and their application
# ====================================================================================================================
@lru_cache(maxsize=None)
def schema(name):
    return json.loads((config.SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))


def validate_delta_json(delta):
    """Raise jsonschema.ValidationError if the Delta does not follow spec/schemas/delta.schema.json."""
    jsonschema.validate(delta, schema("delta"))


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
    """Rows of an extracted table: workspace/documents/<DOC>/tables/<TABLE>.csv, mapped through rows_ref["columns"]."""
    doc, _, table = rows_ref["extracted_table"].partition("/")
    path = config.DOCUMENTS / doc / "tables" / f"{table}.csv"
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
        from .expr import normalize
        value = normalize(Fraction(value) / 100)
    return value


_DECIMAL_TEXT = re.compile(r"^-?[0-9]+(\.[0-9]+)?(/[0-9]+)?$")
_RUPIAH_TEXT = re.compile(r"^[0-9]{1,3}(\.[0-9]{3})+(,[0-9]+)?$")


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


def apply_delta(kb, delta, update_id=None, resolver=default_table_resolver, validate=True):
    """K' = K + Delta: a new knowledge base with the records of the update added. Raises UpdateError when an
    operation does not fit the knowledge base (add of an existing id, change or remove of an absent one)."""
    if validate:
        validate_delta_json(delta)
    update_id = update_id or delta["delta_id"]
    if any(u.update_id == update_id for u in kb.updates):
        raise UpdateError(f"update id already used: {update_id}")
    seq = kb.next_seq
    first = seq
    new, seen = [], set()
    for op in ("add", "change"):
        for e in delta[op]:
            if e["id"] in seen:
                raise UpdateError(f"{e['id']}: appears twice in the same Delta")
            seen.add(e["id"])
            rec = build_record(e, seq, update_id, resolver)
            prior = [r for r in kb.history(e["id"])]
            live = kb.effective(e["id"], rec.recorded_on)
            if op == "add" and live is not None:
                raise UpdateError(f"{e['id']}: add for an id that already exists; use change")
            if op == "change":
                if not prior:
                    raise UpdateError(f"{e['id']}: change for an id that does not exist; use add")
                if prior[-1].kind != rec.kind and not isinstance(prior[-1], Tombstone):
                    raise UpdateError(f"{e['id']}: change from {prior[-1].kind} to {rec.kind}")
            new.append(rec)
            seq += 1
    for e in delta["remove"]:
        if e["id"] in seen:
            raise UpdateError(f"{e['id']}: removed and changed in the same Delta")
        if not kb.history(e["id"]):
            raise UpdateError(f"{e['id']}: remove for an id that does not exist")
        new.append(Tombstone(kind="tombstone", id=e["id"], recorded_on=_date(e["recorded_on"]),
                             source=_sources(e["source"]), seq=seq, update_id=update_id))
        seq += 1
    doc = delta["document"]
    documents = {doc["id"]: Document(doc["id"], doc.get("title", ""), _date(doc.get("issued")))}
    recorded = max((r.recorded_on for r in new), default=_date(doc.get("issued")))
    note = delta.get("note", "")
    info = UpdateInfo(update_id, delta["delta_id"], delta.get("event_id"), doc["id"], recorded, first, seq - 1,
                      note)
    adoptions = {doc["id"]: tuple(delta.get("adopts") or ())} if delta.get("adopts") else None
    return kb.extended(new, info, documents, adoptions)


def empty_kb(name="K"):
    return KnowledgeBase(name=name)
