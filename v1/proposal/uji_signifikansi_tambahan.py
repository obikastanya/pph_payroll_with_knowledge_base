"""Exploratory significance tests for 'proposal reserach.docx' (section 10.2-10.3).

Reads only existing logs (experiments/*/scores.csv, chain.csv); makes no model calls.
Run from the repository root:  env/Scripts/python.exe proposal/uji_signifikansi_tambahan.py
"""
import collections
import csv
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments"

RUNS = {
    "main": ["e2-regulasi", "e2-pkb"],
    "rerun": ["e2-regulasi-ulang"],
    "ab2": ["e2-ab2-regulasi", "e2-ab2-pkb"],
    "model2": ["e2-model2-regulasi", "e2-model2-pkb"],
    "m5": ["e2-regulasi-m5", "e2-pkb-m5"],
}
# Documents whose prompt lost segments under the 14,000-token selector (research_summary.md 6.4).
TRUNCATED = ["E02", "E04", "E13", "PKB-AVCO-2024", "PKB-CENTEX-2024",
             "PKB-SANSAN-2021", "PKB-TAEKWANG-2024", "PKB-WIKA-2025"]


def load_outcomes():
    table = collections.defaultdict(dict)
    for key, dirs in RUNS.items():
        for d in dirs:
            for row in csv.DictReader(open(EXP / d / "scores.csv", encoding="utf8")):
                if row["part"] == "uji":
                    table[(key, row["condition"])][row["event"]] = row["outcome"]
    return table


def mcnemar(a, b, positive):
    docs = [d for d in a if d in b]
    a_only = sum(a[d] == positive and b[d] != positive for d in docs)
    b_only = sum(a[d] != positive and b[d] == positive for d in docs)
    n = a_only + b_only
    p = stats.binomtest(a_only, n, 0.5).pvalue if n else 1.0
    return a_only, b_only, p


def kappa(a, b):
    docs = [d for d in a if d in b]
    cats = ["benar", "salah", "abstain"]
    po = np.mean([a[d] == b[d] for d in docs])
    pe = sum(np.mean([a[d] == c for d in docs]) * np.mean([b[d] == c for d in docs]) for c in cats)
    return po, (po - pe) / (1 - pe)


def holm(pvals):
    order = sorted(pvals, key=pvals.get)
    out, running, m = {}, 0.0, len(order)
    for i, k in enumerate(order):
        running = max(running, min(1.0, (m - i) * pvals[k]))
        out[k] = running
    return out


def cp_upper(k, n, conf=0.95):
    return 1.0 if k == n else stats.beta.ppf(conf, k + 1, n - k)


def main():
    T = load_outcomes()
    main_ = T[("main", "proposed")]
    tests = {
        "T1 SER vs AB4_first": mcnemar(main_, T[("main", "AB4_first")], "salah"),
        "T2 SER vs B3": mcnemar(main_, T[("main", "B3")], "salah"),
        "T3 CAR vs AB2": mcnemar(main_, T[("ab2", "proposed")], "benar"),
        "T4 SER vs AB2": mcnemar(main_, T[("ab2", "proposed")], "salah"),
        "T5 SER m3 vs m5": mcnemar(main_, T[("m5", "proposed")], "salah"),
        "T6 CAR Claude vs model2": mcnemar(main_, T[("model2", "proposed")], "benar"),
        "T7 SER Claude vs model2": mcnemar(main_, T[("model2", "proposed")], "salah"),
        "T8 SER model2 proposed vs B3": mcnemar(T[("model2", "proposed")], T[("model2", "B3")], "salah"),
        "T9 SER run1 vs run2": mcnemar(main_, T[("rerun", "proposed")], "salah"),
    }
    pvals = {k: v[2] for k, v in tests.items()}

    # T10: update size (<=7 elements vs >=11 elements) against correctness, from the paper (Fig. acq b).
    pvals["T10 size vs correct"] = stats.fisher_exact([[8, 1], [0, 9]]).pvalue
    # T11: truncation against correctness.
    tc = sum(main_[d] == "benar" for d in TRUNCATED)
    rest = [d for d in main_ if d not in TRUNCATED]
    rc = sum(main_[d] == "benar" for d in rest)
    pvals["T11 truncated vs correct"] = stats.fisher_exact(
        [[tc, len(TRUNCATED) - tc], [rc, len(rest) - rc]]).pvalue
    # T12: events adding new errors, transplanted vs regenerated chain.
    def new_err(f):
        return {r["event"]: int(r["new_errors"]) > 0 for r in csv.DictReader(open(f, encoding="utf8"))}
    t = new_err(EXP / "e3-tetap" / "chain.csv")
    g = new_err(EXP / "e3-bangkit-ulang" / "chain.csv")
    a = sum(t[e] and not g[e] for e in t)
    b = sum(g[e] and not t[e] for e in t)
    pvals["T12 chain transplanted vs regenerated"] = stats.binomtest(a, a + b, 0.5).pvalue

    adj = holm(pvals)
    for k in pvals:
        extra = tests.get(k, "")
        print(f"{k:40s} {str(extra[:2]) if extra else '':10s} p={pvals[k]:.4f} holm={adj[k]:.4f}")
    print("truncated correct", tc, "/", len(TRUNCATED), "; untruncated correct", rc, "/", len(rest))
    print("chain discordant", a, b)
    print("size-vs-truncation overlap p=", round(stats.fisher_exact([[7, 2], [1, 8]]).pvalue, 4))
    print("kappa run1-run2", kappa(main_, T[("rerun", "proposed")]))
    print("kappa claude-model2", kappa(main_, T[("model2", "proposed")]))

    # Power of H2a: P(one-sided 95% CP upper bound <= 0.25) under true SER p.
    for p in (1 / 6, 0.10, 0.05):
        for n in (18, 30, 40, 50, 100, 150, 200):
            ks = np.arange(n + 1)
            ok = np.array([cp_upper(k, n) <= 0.25 for k in ks])
            print(f"H2a power SER={p:.3f} n={n}: {stats.binom.pmf(ks[ok], n, p).sum():.2f}")

    # Power of one-sided exact McNemar when pipeline is better on 20% and worse on 5% of documents.
    rng = np.random.default_rng(1)
    for n in (18, 36, 54, 100):
        draws = rng.multinomial(n, [0.20, 0.05, 0.75], size=4000)
        hits = sum(
            1 for x in draws
            if x[0] + x[1] and stats.binomtest(x[0], x[0] + x[1], 0.5, alternative="greater").pvalue < 0.05)
        print(f"McNemar power n={n}: {hits / 4000:.2f}")


if __name__ == "__main__":
    main()
