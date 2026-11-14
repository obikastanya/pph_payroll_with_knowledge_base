"""Inter-coder agreement: Krippendorff's alpha (nominal, any number of coders, missing values allowed) and Cohen's
kappa (two coders). Used for the second reader of the gold (Tahap 7) and for RQ4 labels (Tahap 10)."""
from collections import Counter, defaultdict


def krippendorff_alpha_nominal(units):
    """units: list of lists of values (one list per unit, one value per coder; None = missing).
    Units with fewer than two values are not pairable and are ignored. Returns None when undefined."""
    o = defaultdict(float)
    for values in units:
        vals = [v for v in values if v is not None]
        m = len(vals)
        if m < 2:
            continue
        for i, a in enumerate(vals):
            for j, b in enumerate(vals):
                if i != j:
                    o[(a, b)] += 1.0 / (m - 1)
    n_c = Counter()
    for (a, _), w in o.items():
        n_c[a] += w
    n = sum(n_c.values())
    if n <= 1:
        return None
    d_o = sum(w for (a, b), w in o.items() if a != b) / n
    d_e = sum(n_c[a] * n_c[b] for a in n_c for b in n_c if a != b) / (n * (n - 1))
    if d_e == 0:
        return 1.0 if d_o == 0 else None
    return 1 - d_o / d_e


def cohen_kappa(pairs):
    """pairs: list of (coder A value, coder B value)."""
    n = len(pairs)
    if not n:
        return None
    p_o = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    p_e = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if p_e == 1 else (p_o - p_e) / (1 - p_e)


def percent_agreement(pairs):
    return sum(a == b for a, b in pairs) / len(pairs) if pairs else None
