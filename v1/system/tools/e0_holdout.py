r"""E0: the GT1 holdout, used once (PANDUAN Tahap 13; prareg section 5).

    env\Scripts\python system\tools\e0_holdout.py

Compares the frozen gold chain (tag emas-v1) with the 14 holdout cases of GT1, which were never opened during
development, and writes docs/hasil/acuan_gt1_holdout.csv. Refuses to run when that file exists: the holdout is
used once, and a difference is adjudicated (gold error -> gold correction protocol; erratum of the official example;
outside the case model), never tuned away.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import check_refs  # noqa: E402
from pph21kbs.refs import load_gt1  # noqa: E402

OUT = ROOT / "docs" / "hasil" / "acuan_gt1_holdout.csv"


def main():
    """--after-correction: the same comparison after the gold correction protocol, written beside the first result
    (both are reported; the first one is never overwritten)."""
    after = "--after-correction" in sys.argv
    if OUT.exists() and not after:
        sys.exit(f"{OUT.relative_to(ROOT)} exists: the GT1 holdout has already been used")
    rows = []
    check_refs.gt1(verbose=True, rows=rows, cases=load_gt1("holdout"),
                   label="GT1 holdout" + (" (after gold correction)" if after else ""))
    check_refs._write("gt1_holdout_koreksi" if after else "gt1_holdout", rows)


if __name__ == "__main__":
    main()
