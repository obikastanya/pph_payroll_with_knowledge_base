"""Statistical estimators and tests of the analysis plan (skeleton "Rencana analisis statistik").

All intervals are two-sided at level 1 - alpha unless stated. Inputs are counts or paired observations; nothing here
reads experiment files.
"""
import math
import random

from scipy import stats as _st


def clopper_pearson(k, n, alpha=0.05):
    """Exact CI for a proportion k/n."""
    if n == 0:
        return (None, None)
    lo = 0.0 if k == 0 else _st.beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else _st.beta.ppf(1 - alpha / 2, k + 1, n - k)
    return (float(lo), float(hi))


def upper_bound(k, n, alpha=0.05):
    """One-sided exact upper bound for an error rate with k failures in n (skeleton: Beta(1-alpha; k+1, n-k));
    for k = 0 it is 1 - alpha^(1/n)."""
    if n == 0:
        return None
    if k >= n:
        return 1.0
    return float(_st.beta.ppf(1 - alpha, k + 1, n - k))


def lower_bound_all_detected(n, alpha=0.05):
    """One-sided exact lower bound of recall when all n positives are detected: alpha^(1/n)."""
    return alpha ** (1 / n) if n else None


def _wilson(k, n, z):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    centre = (2 * n * p + z * z) / (2 * (n + z * z))
    half = z * math.sqrt(z * z + 4 * n * p * (1 - p)) / (2 * (n + z * z))
    return centre - half, centre + half


def newcombe_unpaired(k1, n1, k2, n2, alpha=0.05):
    """Difference p1 - p2 of independent proportions, Newcombe's hybrid score interval (method 10 with phi = 0)."""
    z = _st.norm.ppf(1 - alpha / 2)
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = _wilson(k1, n1, z)
    l2, u2 = _wilson(k2, n2, z)
    diff = p1 - p2
    return (diff, diff - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), diff + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2))


def newcombe_paired(a, b, c, d, alpha=0.05):
    """Difference of paired proportions p1 - p2 with Newcombe's method 10 (1998).
    Table: a = both success, b = condition 1 only, c = condition 2 only, d = neither. Returns (diff, lo, hi)."""
    n = a + b + c + d
    if n == 0:
        return (None, None, None)
    z = _st.norm.ppf(1 - alpha / 2)
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = _wilson(a + b, n, z)
    l2, u2 = _wilson(a + c, n, z)
    diff = p1 - p2
    denom = (a + b) * (c + d) * (a + c) * (b + d)
    if denom == 0:
        phi = 0.0
    else:
        num = a * d - b * c
        if num > 0:
            num = max(num - n / 2, 0)
        phi = num / math.sqrt(denom)
    dl = math.sqrt((p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2)
    du = math.sqrt((u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2)
    return (diff, max(-1.0, diff - dl), min(1.0, diff + du))


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value from the discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    return float(min(1.0, 2 * _st.binom.cdf(min(b, c), n, 0.5)))


def noninferior(upper_ci_of_difference, margin):
    """Non-inferiority holds when the upper CI bound of (SER new - SER comparator) is below the margin."""
    return upper_ci_of_difference is not None and upper_ci_of_difference < margin


def wilcoxon(x, y):
    """Wilcoxon signed-rank test of paired samples; (statistic, p, rank-biserial r)."""
    diffs = [a - b for a, b in zip(x, y) if a != b]
    if not diffs:
        return (0.0, 1.0, 0.0)
    res = _st.wilcoxon(diffs)
    ranks = _st.rankdata([abs(d) for d in diffs])
    pos = sum(r for r, d in zip(ranks, diffs) if d > 0)
    neg = sum(r for r, d in zip(ranks, diffs) if d < 0)
    r_rb = (pos - neg) / (pos + neg)
    return (float(res.statistic), float(res.pvalue), float(r_rb))


def cluster_bootstrap(clusters, statistic, b=2000, alpha=0.05, seed=20261027):
    """Percentile CI of statistic(list of items) resampling whole clusters (dict cluster -> list of items)."""
    keys = list(clusters)
    rng = random.Random(seed)
    values = []
    for _ in range(b):
        sample = []
        for _ in keys:
            sample += clusters[rng.choice(keys)]
        v = statistic(sample)
        if v is not None:
            values.append(v)
    if not values:
        return (None, None)
    values.sort()
    lo = values[int(math.floor(alpha / 2 * len(values)))]
    hi = values[min(len(values) - 1, int(math.ceil((1 - alpha / 2) * len(values))) - 1)]
    return (lo, hi)


def holm(pvalues):
    """Holm-Bonferroni adjusted p-values, same order as given."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[i]))
        adj[i] = running
    return adj


def pass_at(m, c, j):
    """Unbiased pass@j from m i.i.d. candidates of which c pass: 1 - C(m-c, j) / C(m, j)."""
    if j > m:
        return None
    if m - c < j:
        return 1.0
    return 1 - math.comb(m - c, j) / math.comb(m, j)


def selection_efficiency(one_at_m, pass1, pass_m):
    """eta = (1@m - pass@1) / (pass@m - pass@1); None when the denominator is zero."""
    den = pass_m - pass1
    return None if den == 0 else (one_at_m - pass1) / den


def f_beta(precision, recall, beta=2.0):
    if precision is None or recall is None or precision + recall == 0:
        return 0.0 if precision is not None and recall is not None else None
    b2 = beta * beta
    return (1 + b2) * precision * recall / (b2 * precision + recall)


def f2_flag_all(prevalence):
    """F2 of the baseline that flags every pair: 5 pi / (4 pi + 1)."""
    return 5 * prevalence / (4 * prevalence + 1)
