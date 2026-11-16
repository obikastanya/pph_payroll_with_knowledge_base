"""Monthly payslip accuracy of the real-company chains (reviewer condition, with and without the completeness gate,
and the code-based update), for the timeline figure of the paper. No model calls.

    env\\Scripts\\python -m v2.harness.monthly
"""
import json
from collections import defaultdict

from . import WORK, chain
from .analysis import OUT, code_rows, panels_of, real_chains
from .measure import MEASURED


def by_month(acc):
    out = defaultdict(lambda: [0, 0])
    for rows in acc.values():
        for r in rows:
            k = f"{r['year']}-{r['month']:02d}"
            out[k][0] += bool(r["at_payroll"])
            out[k][1] += 1
    return dict(out)


def main():
    res = {}
    for c in real_chains():
        panels = panels_of(c)
        rec = {"code": by_month(code_rows(c, panels))}
        for label, d in (("reviewer", MEASURED / "chains"), ("reviewer_g7", WORK / "posthoc_g7" / "chains")):
            log = chain.load(d, c)
            rec[label] = by_month(chain.accuracy(c, chain.replay(c, log, "base"), panels))
        res[c.id] = rec
        print(c.id, "done", flush=True)
    (OUT / "monthly.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
