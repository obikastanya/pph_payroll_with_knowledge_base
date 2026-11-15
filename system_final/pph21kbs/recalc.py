"""Recalculation report: what changes for months already paid when a rule recorded later applies to them, as with a
regulation that takes effect retroactively. The results as known on the earlier date stay reproducible; this report
lists the difference to the results as known on the later date."""
from . import engine


def differences(kb, case, before, after):
    """Output values of one case that differ between the knowledge dates `before` and `after`:
    [{"month" (0 = the year), "fact", "before", "after"}], in month order."""
    old = engine.evaluate_case(kb, case, omega=before)
    new = engine.evaluate_case(kb, case, omega=after)
    rows = []
    for month in sorted(set(old.periods) | set(new.periods)):
        a, b = old.periods.get(month, {}), new.periods.get(month, {})
        rows += [{"month": month, "fact": f, "before": a.get(f), "after": b.get(f)}
                 for f in sorted(set(a) | set(b)) if a.get(f) != b.get(f)]
    rows += [{"month": 0, "fact": f, "before": old.year.get(f), "after": new.year.get(f)}
             for f in sorted(set(old.year) | set(new.year)) if old.year.get(f) != new.year.get(f)]
    return rows


def report(kb, cases, before, after, paid_through=12):
    """Per case, the differences in months up to `paid_through` (the months already paid) and in the year values."""
    out = []
    for case in cases:
        rows = [r for r in differences(kb, case, before, after) if r["month"] <= paid_through]
        if rows:
            out.append({"case_id": case["case_id"], "differences": rows})
    return out
