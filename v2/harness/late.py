"""Late upload: the company learns of a retroactive regulation 1, 2, or 3 months after it was issued. The update is
recorded on the upload day; the months already paid are recalculated, and the system's recalculation report
(pph21kbs.recalc) must equal the report of the gold update recorded on the same day. No model calls: the update is
the one the system selected in the isolated mode."""
from datetime import date, timedelta

from pph21kbs import recalc  # noqa: E402

from . import gold
from .chain import lenient, shifted

RETROACTIVE = ("E06", "E07", "E09", "E10", "E13")
LAGS = (1, 2, 3)


def add_months(day, n):
    m = day.month - 1 + n
    return date(day.year + m // 12, m % 12 + 1, min(day.day, 28))


def scenario(event, delta, cases, lag):
    """{"event", "lag", "upload", "cases", "wrong_cases", "outcome"} for one upload delay."""
    upload = add_months(event.issued, lag)
    days = (upload - event.issued).days
    base = gold.base_before(event)
    system = lenient(base, shifted(delta, days), "LATE-SYSTEM")
    expected = gold.apply(base, shifted(gold.delta(event.gold), days), update_id="LATE-GOLD")
    before = upload - timedelta(days=1)
    paid = upload.month - 1 if upload.year == event.issued.year else 12
    wrong = []
    year_cases = [c for c in cases if c["tax_year"] in (event.issued.year, upload.year)]
    for c in year_cases:
        a = recalc.report(system, [c], before, upload, paid_through=paid)
        b = recalc.report(expected, [c], before, upload, paid_through=paid)
        if a != b:
            wrong.append(c["case_id"])
    return {"event": event.id, "lag": lag, "upload": upload.isoformat(), "cases": len(year_cases),
            "wrong_cases": wrong[:20], "outcome": "correct" if not wrong else "wrong"}
