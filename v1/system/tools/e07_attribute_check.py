r"""Counterfactual check of the silent error on E07 (exploratory, 8 November 2026; no LLM call).

    env\Scripts\python system\tools\e07_attribute_check.py

Scores the update that the pipeline selected for E07 (experiments/e2-regulasi/results/E07.json) twice on the test
space: as selected, and with its case attribute employer('jkk_relief_padat_karya_2025') renamed to the attribute that
the test cases carry, employer('jkk_relief_eligible'). Writes docs/hasil/e07_atribut.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from kb_context import base_for  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.analysis.evaluate import score_update, se_cases, se_expected  # noqa: E402

DRAFT_ATTR, CASE_ATTR = "jkk_relief_padat_karya_2025", "jkk_relief_eligible"


def main():
    res = json.loads((ROOT / "experiments/e2-regulasi/results/E07.json").read_text(encoding="utf-8"))
    delta = res["delta"]
    ev = corpus.event("E07")
    base, _ = base_for(ev, build_gold.load_graph())
    cases, tuples = se_cases(), se_expected(ev.id)
    as_selected = score_update(base, delta, ev, tuples, cases, None)
    renamed = json.loads(json.dumps(delta).replace(DRAFT_ATTR, CASE_ATTR))
    after_rename = score_update(base, renamed, ev, tuples, cases, None)
    eligible = sum(1 for c in cases.values() if (c.get("employer") or {}).get(CASE_ATTR))
    out = {"event": "E07", "draft_attribute": DRAFT_ATTR, "case_attribute": CASE_ATTR,
           "test_cases_with_case_attribute_true": eligible,
           "as_selected": {"outcome": as_selected.outcome, "wrong_tuples": as_selected.wrong_tuples,
                           "tuples": as_selected.tuples},
           "attribute_renamed": {"outcome": after_rename.outcome, "wrong_tuples": after_rename.wrong_tuples,
                                 "tuples": after_rename.tuples}}
    (ROOT / "docs/hasil/e07_atribut.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
