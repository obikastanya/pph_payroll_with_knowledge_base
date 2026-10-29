"""One employee as the admin enters it, and the engine case built from it.

A record holds the admin's words: profile and company fields (by data key), company pay components by name, and one
grid of values per month (columns: component names, and "data:<key>" for non-money data such as HR data). The pay
components are mapped to knowledge base data through the company catalog, so the same record stays valid when the
knowledge base changes; what the rules read decides what is used.
"""
import copy
import json
from pathlib import Path

import demo
import inputs

DATA = Path(__file__).resolve().parent / "demo_data"


def catalog():
    """{component name: data key}: the company's pay components (initial ones plus those added during the demo)."""
    out = {c["name"]: c["key"] for c in json.loads((DATA / "catalog.json").read_text(encoding="utf-8"))["components"]}
    out.update({c["name"]: c["key"] for c in demo.load()["catalog"]})
    return out


def scenarios():
    return {s["title"]: s for s in json.loads((DATA / "scenarios.json").read_text(encoding="utf-8"))["scenarios"]}


def _fill(spec, months):
    """{month: value} from a scenario value spec: from (carried forward), once, inc (counts up by 1 each month)."""
    out = {}
    carry = {int(k): v for k, v in (spec.get("from") or {}).items()}
    months = list(months)
    before = [k for k in carry if months and k <= months[0]]
    cur = carry[max(before)] if before else None
    for m in months:
        if m in carry:
            cur = carry[m]
        if cur is not None:
            out[m] = cur
    for k, v in (spec.get("once") or {}).items():
        if int(k) in months:
            out[int(k)] = v
    for k, v in (spec.get("inc") or {}).items():
        for i, m in enumerate(x for x in months if x >= int(k)):
            out[m] = v + i
    return out


def from_scenario(sc):
    months = range(sc["start"], sc["end"] + 1)
    grid = {m: {} for m in months}
    for name, spec in sc["values"].items():
        for m, v in _fill(spec, months).items():
            grid[m][name] = v
    for key, spec in sc["data"].items():
        for m, v in _fill(spec, months).items():
            grid[m][f"data:{key}"] = v
    return {"name": sc["name"], "year": sc["year"], "month": sc["month"], "start": sc["start"], "end": sc["end"],
            "policy": sc["policy"], "fields": dict(sc["fields"]), "components": list(sc["components"]),
            "grid": {str(m): r for m, r in grid.items()}, "withheld": dict(sc["withheld"]), "scenario": sc["title"],
            "component_keys": {c["name"]: c["key"] for c in sc.get("extra_components", [])}}


def ensure_components(sc):
    """Scenario components missing from the catalog are added (company data, kept until reset)."""
    cat = catalog()
    for c in sc.get("extra_components", []):
        if c["name"] not in cat:
            demo.add_component(c["name"], c["key"])


def cell(rec, m, col):
    return (rec["grid"].get(str(m)) or {}).get(col)


def to_case(rec, policy_installed=True):
    """The engine case. Months after the month asked for are filled with the recurring values of that month, so that
    the final month stays December or the month the employee leaves (engine limitation, see README)."""
    cat = {**rec.get("component_keys", {}), **catalog()}
    year, start, end = rec["year"], rec["start"], max(rec["end"], rec["start"])
    asked = min(max(rec["month"], start), end)
    periods = []
    last = rec["grid"].get(str(asked)) or {}
    for i, m in enumerate(range(start, end + 1)):
        if m <= asked:
            row = rec["grid"].get(str(m)) or {}
        else:      # recurring values only; counters go on counting
            row = {}
            for col, v in last.items():
                key = col[5:] if col.startswith("data:") else cat.get(col)
                df = inputs.definition(key) if key else None
                if df and df.get("repeat") and v not in (None, "", 0, False):
                    row[col] = v + (df.get("increment") or 0) * (m - asked)
        p = {"month": m, "income": {}, "benefits": {}, "hr": {}, "zakat": 0}
        for col, v in row.items():
            if v in (None, "", 0, False):
                continue
            key = col[5:] if col.startswith("data:") else cat.get(col)
            if not key:
                continue
            b, k = key.split(".", 1)
            if b == "zakat":
                p["zakat"] += int(v)
            elif b in ("income", "benefit"):
                bucket = p["income" if b == "income" else "benefits"]
                bucket[k] = bucket.get(k, 0) + int(v)
            elif b == "hr":
                p["hr"][k] = int(v) if isinstance(v, (bool, int, float)) else str(v)
        periods.append(p)
    emp, er, method = {}, {"policy": rec.get("policy") if policy_installed else None}, "gross"
    for key, v in rec["fields"].items():
        if v is None or v == "":
            continue
        b, k = key.split(".", 1)
        if b == "employee":
            emp[k] = v
        elif b == "employer":
            er[k] = v
        elif key == "case.method":
            method = v
    return {"case_id": rec["name"] or "pegawai", "tax_year": year, "method": method, "employee": emp, "employer": er,
            "employment": {"start_month": start, "end_month": end}, "periods": periods}


def scenario_case(sc):
    rec = from_scenario(sc)
    return to_case(rec, policy_installed=bool(sc.get("policy")) and sc["policy"] in demo.installed_policies())


def copy_record(rec):
    return copy.deepcopy(rec)
