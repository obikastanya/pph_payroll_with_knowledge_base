"""Compare the gold chain with reference cases (E0 development check; holdout cases are not used here).

    env\\Scripts\\python system\\tools\\check_refs.py gt3 [year] [omega]
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_gold  # noqa: E402
from pph21kbs.refs import compare, gt3_case, load_gt3  # noqa: E402


def gt3(year=None, omega=date(2026, 10, 27), verbose=True):
    kb = build_gold.build(check_only=True)
    ok = total = obs = bad = 0
    for d in load_gt3():
        if year and d["tahun_pajak"] != year:
            continue
        case, exp = gt3_case(d)
        r, diffs = compare(kb, case, exp, omega)
        total += 1
        obs += len(exp)
        bad += len(diffs)
        if not diffs and not r.errors:
            ok += 1
        elif verbose:
            print(d["id"], d["tahun_pajak"], d["uraian"][:80])
            if r.errors:
                print("   errors", r.errors[:3])
            for k, got, want in diffs[:8]:
                print(f"   {k}: engine {got} reference {want}")
    print(f"GT3: {ok}/{total} cases equal; {obs - bad}/{obs} observations equal")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "gt3"
    year = int(sys.argv[2]) if len(sys.argv) > 2 else None
    omega = date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3 else date(2026, 10, 27)
    if which == "gt3":
        gt3(year, omega)
