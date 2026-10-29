"""Real updates (Delta JSON) built from the forms and from the assistant: a new value for a number, a new rule, a
change of a rule from a date, a revocation, and company policies from examples. They are validated and applied by the
research system's own code when reviewed.
"""
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from fractions import Fraction

import data as d
import store


def _id(prefix):
    return f"{prefix}-{datetime.now():%m%d%H%M%S}"


def _src(doc, provision, quote):
    return [{"document": doc or "CATATAN-ADMIN", "provision": provision or "-", "quote": quote or "(belum diisi)"}]


def _num(v, value_type):
    if isinstance(v, Fraction):
        v = Decimal(v.numerator) / Decimal(v.denominator)
    if value_type == "money":
        return int(v)
    return str(v) if isinstance(v, Decimal) else v


def record_json(r):
    """A KB record as a Delta element (for change and revoke)."""
    e = {"kind": r.kind, "id": r.id, "recorded_on": store.TODAY.isoformat(),
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
                  "expression": d.expr_text(r.expression)})
        if r.condition:
            e["condition"] = d.expr_text(r.condition)
        if r.overrides:
            e["overrides"] = list(r.overrides)
        if r.conflict_code:
            e["conflict_code"] = r.conflict_code
        if r.fixed_point:
            e["fixed_point"] = r.fixed_point if isinstance(r.fixed_point, (str, dict)) else str(r.fixed_point)
        if r.policy:
            e["policy"] = r.policy
    elif r.kind == "parameter":
        e.update({"name": r.name, "value": _num(r.value, r.value_type), "value_type": r.value_type})
    return e


def _delta(prefix, title, issued, add=(), change=()):
    did = _id(prefix)
    return {"delta_id": did, "event_id": None, "document": {"id": did, "title": title, "issued": issued.isoformat()},
            "relevant": True, "add": list(add), "change": list(change), "remove": [], "note": "dibuat di aplikasi"}


def current_param(name, at=None):
    at = at or store.TODAY
    vs = sorted((r for r in d.kb().records if r.kind == "parameter" and r.name == name), key=lambda r: r.valid_from)
    live = [r for r in vs if r.valid_from <= at and (r.valid_until is None or at <= r.valid_until)]
    return (live or vs)[-1]


def new_value(name, value, start, doc, provision, quote):
    """A new value of a number from a date; the value in force then ends the day before."""
    old = current_param(name, start)
    src = _src(doc, provision, quote)
    add = {"kind": "parameter", "id": f"PAR.{name.upper()}.{start:%Y%m}", "name": name, "value": value,
           "value_type": old.value_type, "valid_from": start.isoformat(), "recorded_on": store.TODAY.isoformat(),
           "source": src, "label_id": old.label_id}
    change = []
    if old.valid_from < start and (old.valid_until is None or old.valid_until >= start):
        ch = record_json(old)
        ch["valid_until"] = (start - timedelta(days=1)).isoformat()
        ch["source"] = src
        change.append(ch)
    return _delta("ANGKA", f"{d.fact_label(name)} menjadi {d.money(value) if old.value_type == 'money' else value} "
                           f"mulai {d.tgl(start)}", store.TODAY, [add], change)


def new_rule(produces, expression, condition, start, end, company, policy, doc, provision, quote):
    e = {"kind": "rule", "id": f"{'PRS.' + policy if company else 'REG.ADMIN'}.{produces.upper()}.{start:%Y%m}",
         "layer": "company" if company else "regulation", "modality": "default" if company else "mandatory",
         "scope": "period" if d.facts().get(produces) is None or d.facts()[produces].fact_scope == "period" else "year",
         "produces": produces, "expression": expression, "valid_from": start.isoformat(),
         "recorded_on": store.TODAY.isoformat(), "source": _src(doc, provision, quote)}
    if condition:
        e["condition"] = condition
    if end:
        e["valid_until"] = end.isoformat()
    if company:
        e["policy"] = policy
    return _delta("ATURAN", f"Aturan baru: {d.fact_label(produces)}", store.TODAY, [e])


def change_rule(rule, expression, start, doc, provision, quote):
    """The rule ends the day before start; a new version with the new formula starts then."""
    old = record_json(rule)
    old["valid_until"] = (start - timedelta(days=1)).isoformat()
    old["source"] = _src(doc, provision, quote)
    new = record_json(rule)
    new.update({"id": f"{rule.id}.V{start:%Y%m}", "expression": expression, "valid_from": start.isoformat(),
                "source": _src(doc, provision, quote)})
    new.pop("valid_until", None)
    return _delta("UBAH", f"Ubah: {d.fact_label(rule.produces)} mulai {d.tgl(start)}", store.TODAY, [new], [old])


def revoke(rule, end, doc, provision, quote=""):
    e = record_json(rule)
    e["valid_until"] = end.isoformat()
    e["source"] = _src(doc, provision, quote or "dicabut")
    return _delta("CABUT", f"Cabut: {d.fact_label(rule.produces)} sesudah {d.tgl(end)}", store.TODAY, [], [e])


def find_rule(text):
    ql = text.lower()
    best = None
    for r in d.kb().view(store.TODAY).rules.values():
        if d.is_input_convention(r):
            continue
        words = [w for w in re.findall(r"[a-z]{5,}", d.fact_label(r.produces).lower())]
        score = sum(w in ql for w in words)
        if score and (best is None or score > best[0]):
            best = (score, r)
    return best[1] if best else None


# ---------------------------------------------------------------- company policies from examples
def _policy(pid, title, start, rules):
    did = _id("KEBIJAKAN")
    for r in rules:
        r.update({"kind": "rule", "layer": "company", "modality": "default", "scope": "period", "policy": pid,
                  "valid_from": start.isoformat(), "recorded_on": store.TODAY.isoformat()})
        r.setdefault("source", _src(pid, "-", title))
    return {"delta_id": did, "event_id": None, "document": {"id": pid, "title": title, "issued": store.TODAY.isoformat()},
            "relevant": True, "add": rules, "change": [], "remove": [], "note": "kebijakan dari contoh"}


def meal_policy(amount, pid="PRS-DEMO", start=None):
    start = start or date(store.TODAY.year + 1, 1, 1)
    return _policy(pid, f"Kebijakan {pid}: uang makan Rp{amount:,} per hari hadir".replace(",", "."), start, [
        {"id": f"PRS.{pid}.MEAL", "produces": "other_regular_income",
         "expression": f"{amount} * hr('days_present') + income('other_regular')"}])


def thr_policy(times, pid="PRS-DEMO", start=None):
    start = start or date(store.TODAY.year + 1, 1, 1)
    return _policy(pid, f"Kebijakan {pid}: THR {times:g} × upah pada bulan hari raya", start, [
        {"id": f"PRS.{pid}.THR", "produces": "thr",
         "expression": f"round(dec('{times}') * (base_salary + fixed_allowance), 1, 'down') if hr('thr_holiday') == 1 "
                       f"else income('thr')"}])


def bonus_policy(percent, month, pid="PRS-DEMO", start=None):
    start = start or date(store.TODAY.year + 1, 1, 1)
    return _policy(pid, f"Kebijakan {pid}: bonus {percent:g}% gaji pokok setiap bulan {d.MONTHS[month - 1]}", start, [
        {"id": f"PRS.{pid}.BONUS", "produces": "bonus",
         "expression": f"round(dec('{percent / 100}') * base_salary, 1, 'down') if month == {month} else income('bonus')"}])
