"""Scoring.

One document: the update the system selected, applied to the base, is correct when every output value, the aligned
conflict report, and the engine errors equal those of the gold update applied to the same base, for every test case
at both knowledge dates (the day before the document was issued and its issue day). One value off makes it a silent
error; an abstention is an abstention. An empty update for a relevant document is scored like any other update.

Payslip accuracy (the chain): every payslip of every employee-month is compared with the gold payslip as known on
the payroll date of that month, and again as known at the end of the window, after every retroactive rule.
"""
import ast
from dataclasses import dataclass, field
from datetime import date

from pph21kbs import gates, pipeline  # noqa: E402
from pph21kbs.kb import UpdateError  # noqa: E402

from . import gold

APPLIED = ("proposed", "empty")


@dataclass
class Score:
    outcome: str                     # correct | silent_error | abstain
    tuples: int = 0
    wrong_tuples: int = 0
    wrong_cases: list = field(default_factory=list)
    note: str = ""


class Behaviour:
    """Observations of one knowledge base, computed once per (case, knowledge date)."""

    def __init__(self, kb):
        self.kb, self._obs, self._produces = kb, {}, {}

    def __call__(self, case, omega):
        k = (case["case_id"], omega)
        if k not in self._obs:
            obs, conflicts, errors, _ = gates.observe(self.kb, case, omega)
            if omega not in self._produces:
                self._produces[omega] = pipeline.produces_map(self.kb, omega)
            self._obs[k] = (obs, tuple(pipeline.aligned(conflicts, self._produces[omega])), bool(errors))
        return self._obs[k]


def compare(observed, expected, cases, omegas, keep=20):
    s = Score("correct")
    for case in cases:
        for w in omegas:
            s.tuples += 1
            if observed(case, w) != expected(case, w):
                s.wrong_tuples += 1
                if len(s.wrong_cases) < keep:
                    s.wrong_cases.append(f"{case['case_id']}@{w.isoformat()}")
    if s.wrong_tuples:
        s.outcome = "silent_error"
    return s


def delta_of(result, event):
    """The update a pipeline result applies, or None when it abstained."""
    if result.get("status") not in APPLIED:
        return None
    if result["status"] == "empty":
        return gold.empty(event.id, event.document, event.issued)
    return result["delta"]


def score_delta(base, delta, expected, cases, omegas):
    """Score an update (None = abstain) against the gold behaviour `expected` on `base`."""
    if delta is None:
        return Score("abstain", note="no update selected")
    try:
        kb = gold.apply(base, delta, update_id="SYSTEM")
    except (UpdateError, ValueError, KeyError) as e:
        return Score("silent_error", note=f"not applicable: {e}"[:200])
    return compare(Behaviour(kb), expected, cases, omegas)


# ---------------------------------------------------------------------------------------------- payslip accuracy
def payroll_date(year, month):
    return date(year, month, 25)


def _conflict_month(c):
    return ast.literal_eval(c)[2]


def _slip(behaviour, case, omega, month, final):
    """The payslip of one month: its values (with the year's values in the final month), conflicts, and errors."""
    obs, conflicts, errors = behaviour(case, omega)
    months = {month, 0} if month == final else {month}
    return ({k: v for k, v in obs.items() if k[0] in months},
            tuple(c for c in conflicts if _conflict_month(c) in months), errors)


def payslips(system_kb, gold_kb, cases, window_end):
    """Payslip accuracy of one company: per employee-month, whether the system's payslip equals the gold payslip
    as known on that month's payroll date ("at_payroll") and as known at the window's end ("at_end")."""
    sys_b, gold_b = Behaviour(system_kb), Behaviour(gold_kb)
    rows = []
    for case in cases:
        y, final = int(case["tax_year"]), max(p["month"] for p in case["periods"])
        for p in case["periods"]:
            m = p["month"]
            row = {"case_id": case["case_id"], "year": y, "month": m}
            for label, w in (("at_payroll", payroll_date(y, m)), ("at_end", window_end)):
                row[label] = _slip(sys_b, case, w, m, final) == _slip(gold_b, case, w, m, final)
            rows.append(row)
    return rows
