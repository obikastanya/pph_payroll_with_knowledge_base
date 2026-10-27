"""Records of the knowledge base (representasi.md sections 2 and 3).

A record is immutable. Updates append records; a record never changes after it is created. The effective record of an
element id at knowledge date omega is the one with the latest (recorded_on, seq) not later than omega.
"""
from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction

from ..expr import Expression

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
        """Lex superior rank (representasi.md 8): mandatory regulation 4, company 3, adopted optional 2, default 1.
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
    from ..expr.numbers import decimal_value
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
