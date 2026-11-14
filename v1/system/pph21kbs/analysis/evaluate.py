"""Scoring of an acquired update against S^E (akuisisi.md Definition 6 and 8; skeleton RQ2/RQ3 metrics).

A document outcome is "benar" (correctly applied) when K' = K_base (+) Delta-hat reproduces the gold expected value of
every S^E tuple of the event (A2 for t >= t_berlaku, A3t for earlier periods, both at omega = issue date; A3omega at
omega = issue date - 1 day; A4 conflict reports), "salah" (wrongly applied, a silent error) when some tuple differs
or the update cannot be applied, and "abstain" when the pipeline abstained. An empty Delta applied to a relevant
document is scored like any other update: if the gold changes the results, it is a silent error (a missed update).
"""
import gzip
import json
from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction
from pathlib import Path

from ..config import REPO
from ..engine import evaluate_case
from ..kb import apply_delta
from ..kb.delta import UpdateError

SE_DIR = REPO / "dataset" / "14_ruang_uji"


def load_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def se_cases(dev=False):
    root = SE_DIR / "pengembangan" if dev else SE_DIR
    out = {c["case_id"]: c for c in load_gz(root / "kasus.jsonl.gz")}
    for extra in ("kasus_kebijakan", "kasus_terarah"):    # test policy cases; targeted cases from mutation analysis
        if (root / f"{extra}.jsonl.gz").exists():
            out.update({c["case_id"]: c for c in load_gz(root / f"{extra}.jsonl.gz")})
    return out


def se_expected(event_id, dev=False):
    root = SE_DIR / "pengembangan" if dev else SE_DIR
    path = root / "harapan" / f"{event_id}.jsonl.gz"
    return load_gz(path) if path.exists() else []


@dataclass
class Score:
    outcome: str                     # benar | salah | abstain
    tuples: int = 0
    wrong_tuples: int = 0
    a2: int = 0                      # wrong observations in periods >= effective start, omega = issue date
    a3t: int = 0                     # wrong observations before the effective start, omega = issue date
    a3w: int = 0                     # wrong observations at omega = issue date - 1 day
    a4: int = 0                      # tuples whose conflict report differs
    errors: int = 0                  # tuples with an engine error not in the gold
    wrong_ids: list = field(default_factory=list)
    note: str = ""


def _obs(kb, case, omega):
    r = evaluate_case(kb, case, omega)
    obs = {f"{m}:{f}": (str(v) if isinstance(v, Fraction) else v) for m, row in r.periods.items()
           for f, v in row.items()}
    obs.update({f"0:{f}": (str(v) if isinstance(v, Fraction) else v) for f, v in r.year.items()})
    return obs, sorted(map(str, r.conflict_keys())), r.errors


def score_kb(kb, event, tuples, cases, keep_ids=50, gold_produces=None):
    """Compare a knowledge base with the gold expected tuples of an event. gold_produces (company rule id -> fact of
    the gold policy) aligns conflict keys of differently named company rules (representasi.md 8; policy events)."""
    s = Score("benar")
    produces_at = {}
    start = event.effective_from or event.issued
    for t in tuples:
        case = cases[t["case_id"]]
        omega = date.fromisoformat(t["omega"])
        obs, conflicts, errors = _obs(kb, case, omega)
        s.tuples += 1
        wrong = False
        if errors and not t.get("errors"):
            s.errors += 1
            wrong = True
        for key, want in t["obs"].items():
            if obs.get(key) != want:
                wrong = True
                m, _ = key.split(":", 1)
                month = int(m) or max(p["month"] for p in case["periods"])
                if omega < event.issued:
                    s.a3w += 1
                elif date(int(case["tax_year"]), month, 1) >= date(start.year, start.month, 1):
                    s.a2 += 1
                else:
                    s.a3t += 1
        want_conflicts = t["conflicts"]
        if gold_produces is not None:
            from .conflicts import aligned, produces_map
            if omega not in produces_at:
                produces_at[omega] = produces_map(kb, omega)
            conflicts = aligned(conflicts, produces_at[omega])
            want_conflicts = aligned(want_conflicts, gold_produces)
        if conflicts != want_conflicts:
            s.a4 += 1
            wrong = True
        if wrong:
            s.wrong_tuples += 1
            if len(s.wrong_ids) < keep_ids:
                s.wrong_ids.append(f"{t['case_id']}@{t['omega']}")
    if s.wrong_tuples:
        s.outcome = "salah"
    return s


def score_update(base, delta, event, tuples, cases, gold_produces=None):
    """Score Delta-hat applied to base (strict application)."""
    if delta is None:
        return Score("abstain", note="no update selected")
    try:
        kb = apply_delta(base, delta)
    except (UpdateError, ValueError, KeyError) as e:
        return Score("salah", note=f"not applicable: {e}"[:200])
    return score_kb(kb, event, tuples, cases, gold_produces=gold_produces)


def score_result(base, result, event, tuples, cases):
    """Score a pipeline result record (format_data.md 7)."""
    if result.get("status") in ("abstain", "budget", None):
        return Score("abstain", note=result.get("status") or "")
    return score_update(base, result.get("delta"), event, tuples, cases)
