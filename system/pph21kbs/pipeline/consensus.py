"""Behavioural consensus (akuisisi.md 3.6): candidates that passed the gates are grouped by their behaviour on the
union of their S^G, at both knowledge dates. Two candidates share a group when every F_nilai observation and the
conflict report (stable keys) are equal on every tuple. The largest group wins (no quorum); its representative is
the first member in the random candidate order. A tie between the largest groups, or no passing candidate, gives
abstain.
"""
from .gates import observe


def signature(kb2, cases, omegas, extra=()):
    out = []
    for i, case in enumerate(cases):
        for w in omegas:
            obs, conflicts, errors, _ = observe(kb2, case, w, extra)
            out.append((i, w.isoformat(), tuple(sorted((k, str(v)) for k, v in obs.items())),
                        tuple(sorted(map(str, conflicts))), bool(errors)))
    return tuple(out)


def choose(passing, order, extra=()):
    """passing: {candidate number: (K', cases, omegas)}; order: candidate numbers in random order.
    Returns (selected candidate or None, groups as lists of candidate numbers, status)."""
    if not passing:
        return None, [], "abstain"
    union, seen, omegas = [], set(), None
    for n in order:
        if n not in passing:
            continue
        _, cases, ws = passing[n]
        omegas = omegas or ws
        for c in cases:
            key = repr(sorted(c.items(), key=lambda t: t[0]))
            if key not in seen:
                seen.add(key)
                union.append(c)
    sigs = {n: signature(passing[n][0], union, omegas, extra) for n in passing}
    groups = []
    for n in [x for x in order if x in passing]:
        for g in groups:
            if sigs[g[0]] == sigs[n]:
                g.append(n)
                break
        else:
            groups.append([n])
    groups.sort(key=lambda g: -len(g))
    if len(groups) > 1 and len(groups[0]) == len(groups[1]):
        return None, groups, "abstain"
    return groups[0][0], groups, "applied"
