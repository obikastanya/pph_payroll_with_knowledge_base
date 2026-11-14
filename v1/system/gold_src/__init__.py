"""Authoring of the gold chain (background updates and gold Deltas, akuisisi.md section 1).

Each module in this package defines UPDATES: a list of Update objects. Quotes are verified against the locked texts
in dataset/13_teks when the module is built, and the page is filled in automatically. system/tools/build_gold.py
writes dataset/12_emas/delta/<id>.json and dataset/12_emas/rantai.csv in chain order.
"""
from dataclasses import dataclass, field
from datetime import date

from pph21kbs.text import find_quote, registry


class QuoteNotFound(ValueError):
    pass


class Doc:
    """A source document bound to its id and issue date (t_terbit = recorded_on of gold records)."""

    def __init__(self, doc_id, issued=None):
        reg = registry().get(doc_id)
        if reg is None:
            raise KeyError(f"document {doc_id} not in dataset/13_teks/dokumen.csv")
        self.id = doc_id
        self.issued = issued or reg["issued"]
        self.title = reg["title"]

    def q(self, provision, quote):
        """Verified source entry: the quote must occur in the locked text."""
        page = find_quote(self.id, quote)
        if page is None:
            raise QuoteNotFound(f"{self.id} {provision}: quote not found: {quote[:90]!r}")
        return {"document": self.id, "provision": provision, "page": page, "quote": quote}


def _clean(d):
    return {k: v for k, v in d.items() if v not in (None, "", [], ())}


def fact(name, ftype, scope, src, *, output=False, label="", label_id="", unit=""):
    return _clean({"kind": "fact", "id": name, "fact_type": ftype, "fact_scope": scope, "output": output,
                   "label": label, "label_id": label_id, "unit": unit, "source": src if isinstance(src, list) else [src]})


def rule(rid, produces, expression, src, vf, *, scope="period", cond=None, vu=None, layer="regulation",
         modality="mandatory", overrides=(), fixed_point=None, label="", policy=None, code=None):
    return _clean({"kind": "rule", "id": rid, "layer": layer, "modality": modality, "scope": scope,
                   "produces": produces, "condition": cond, "expression": expression, "valid_from": vf,
                   "valid_until": vu, "overrides": list(overrides),
                   "fixed_point": ({"lower": fixed_point[0], "upper": fixed_point[1]} if fixed_point else None),
                   "label": label, "policy": policy, "conflict_code": code,
                   "source": src if isinstance(src, list) else [src]})


def param(pid, name, value, vtype, src, vf, *, vu=None, label="", label_id=""):
    return _clean({"kind": "parameter", "id": pid, "name": name, "value": value, "value_type": vtype,
                   "valid_from": vf, "valid_until": vu, "label": label, "label_id": label_id,
                   "source": src if isinstance(src, list) else [src]}) | {"value": value}


def table(tid, name, kind, src, vf, *, rows=None, rows_ref=None, vu=None, label="", label_id=""):
    out = _clean({"kind": "table", "id": tid, "name": name, "table_kind": kind, "valid_from": vf, "valid_until": vu,
                  "label": label, "label_id": label_id, "source": src if isinstance(src, list) else [src]})
    if rows_ref:
        out["rows_ref"] = rows_ref
    else:
        out["rows"] = rows
    return out


def constraint(cid, assertion, code, src, vf, *, scope="period", cond=None, vu=None, label=""):
    return _clean({"kind": "constraint", "id": cid, "scope": scope, "condition": cond, "assertion": assertion,
                   "conflict_code": code, "valid_from": vf, "valid_until": vu, "label": label,
                   "source": src if isinstance(src, list) else [src]})


@dataclass
class Update:
    """One update of the gold chain. kind: background (not acquired), event (gold Delta of a corpus event), or
    policy (gold Delta of a company policy)."""
    delta_id: str
    doc: Doc
    kind: str
    event_id: str | None = None
    add: list = field(default_factory=list)
    change: list = field(default_factory=list)
    remove: list = field(default_factory=list)
    adopts: list = field(default_factory=list)
    recorded_on: str | None = None
    note: str = ""
    relevant: bool = True

    def to_json(self):
        rec = self.recorded_on or self.doc.issued
        for e in self.add + self.change:
            e.setdefault("recorded_on", rec)
        for e in self.remove:
            e.setdefault("recorded_on", rec)
        out = {"delta_id": self.delta_id, "event_id": self.event_id,
               "document": {"id": self.doc.id, "title": self.doc.title, "issued": self.doc.issued},
               "relevant": self.relevant, "add": self.add, "change": self.change, "remove": self.remove,
               "note": self.note}
        if self.adopts:
            out["adopts"] = self.adopts
        return out
