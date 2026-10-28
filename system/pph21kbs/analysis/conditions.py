"""Comparison conditions computed from the candidates and gate logs of the proposed pipeline (akuisisi.md 7):

  proposed   consensus over candidates that passed G1-G5 (with one repair round)
  B3         first candidate in the random order that passes G1-G2, before repair
  B4         behavioural majority over the m initial candidates, without gates (tie -> abstain)
  AB3_noG5, AB3_noG4, AB3_norepair   consensus with one gate or the repair round removed
  proposed_aligned   sensitivity (policy events): the consensus of the proposed pipeline with conflict keys aligned
             across differently named company rules (representasi.md 8), which the frozen consensus did not do
  AB4_first, AB4_consensus, AB4_perfect   first passing candidate; consensus; a passing candidate that is correct on
             S^E when there is one (selection by an oracle: an upper bound, never a usable condition)

Gates that did not run for a candidate (the gates stop at the first failure) are run here, without stopping, so that
every condition sees the same candidates. Behaviour for B4 and the consensus variants is computed on S^G generated
from the candidates, never on S^E.
"""
from datetime import date

from ..pipeline import consensus, gates, sg
from ..kb import apply_delta
from ..kb.delta import UpdateError

ORDER = ("G1", "G2", "G3", "G4", "G5")


def all_gates(base, delta, event, issued, relevance=None, policies=(), policy_omega=date(2026, 10, 27)):
    """Status of every gate for one candidate Delta (True/False; None when G1 fails and nothing else can run)."""
    out = {g: None for g in ORDER}
    if delta is None:
        out["G1"] = False
        return out, None
    r1, kb2 = gates.g1(base, delta)
    out["G1"] = r1.passed
    if kb2 is None:
        return out, None
    company = event.layer == "company"
    out["G2"] = gates.g2(base, delta, list(event.documents), issued).passed
    out["G3"] = gates.g3(kb2, policy_omega if company else issued, policies).passed
    starts, s_d = gates.effect_start(base, delta)
    sgs = sg.generate(base, kb2, delta, s_d, issued, relevance, starts=starts,
                      omega=policy_omega if company else None)
    extra = [e["id"] for e in delta["add"] if e["kind"] == "fact"] if company else []
    ev = gates.Evaluations(sgs.cases, extra)
    out["G4"] = gates.g4(base, kb2, sgs, ev, s_d, company=company).passed
    out["G5"] = gates.g5(base, kb2, delta, sgs, ev, starts, relevance).passed
    return out, (kb2, sgs.cases, sgs.omegas)


def _aligned_choose(pool, order):
    """consensus.choose with conflict keys aligned through the facts the company rules produce."""
    from .conflicts import aligned, produces_map
    if not pool:
        return None, "abstain"
    union, seen, omegas = [], set(), None
    for n in order:
        if n in pool:
            omegas = omegas or pool[n][2]
            for c in pool[n][1]:
                key = repr(sorted(c.items(), key=lambda t: t[0]))
                if key not in seen:
                    seen.add(key)
                    union.append(c)
    sigs = {}
    for n, (kb2, _, _) in pool.items():
        sig = []
        for i, case in enumerate(union):
            for w in omegas:
                obs, conflicts, errors, _ = gates.observe(kb2, case, w)
                sig.append((i, w.isoformat(), tuple(sorted((k, str(v)) for k, v in obs.items())),
                            tuple(aligned(conflicts, produces_map(kb2, w))), bool(errors)))
        sigs[n] = tuple(sig)
    groups = []
    for n in [x for x in order if x in pool]:
        for g in groups:
            if sigs[g[0]] == sigs[n]:
                g.append(n)
                break
        else:
            groups.append([n])
    groups.sort(key=lambda g: -len(g))
    if len(groups) > 1 and len(groups[0]) == len(groups[1]):
        return None, "abstain"
    return groups[0][0], "applied"


def _choose(pool, order):
    if not pool:
        return None, "abstain"
    sel, groups, status = consensus.choose(pool, [n for n in order if n in pool])
    return sel, status


def conditions(result, base, event, oracle=None, policies=()):
    """{condition: Delta or None}. oracle(delta) -> bool marks a candidate correct on S^E (AB4_perfect only);
    policies: the policy document of a company-layer event, as in the pipeline's G3."""
    rel = (result.get("relevance") or {}).get("output") or None
    issued = event.issued
    cands = result.get("candidates") or []
    order = [c["n"] for c in sorted(cands, key=lambda c: c["order"])]
    initial, final = {}, {}
    for c in cands:
        init_delta = c.get("initial_delta") or (c["delta"] if not c.get("repaired") else None)
        if init_delta is not None:
            initial[c["n"]] = (init_delta,) + all_gates(base, init_delta, event, issued, rel, policies)
        if c.get("delta") is not None:
            final[c["n"]] = (c["delta"],) + all_gates(base, c["delta"], event, issued, rel, policies)
    out = {"proposed": result.get("delta") if result.get("status") in ("applied", "empty") else None}
    if result.get("status") == "empty":
        for k in ("B3", "B4", "AB3_noG5", "AB3_noG4", "AB3_norepair", "AB4_first", "AB4_consensus", "AB4_perfect",
                  "proposed_aligned"):
            out[k] = result["delta"]
        return out

    def ok(gs, need):
        return all(gs.get(g) for g in need)

    # B3
    out["B3"] = next((initial[n][0] for n in order if n in initial and ok(initial[n][1], ("G1", "G2"))), None)
    # B4: behaviour of every initial candidate that can be applied, on the union of their S^G
    pool = {}
    for n in order:
        if n in initial:
            d = initial[n][0]
            try:
                kb2 = apply_delta(base, d)
            except (UpdateError, ValueError, KeyError):
                continue
            k2sg = initial[n][2]
            if k2sg is None:
                continue
            pool[n] = (kb2, k2sg[1], k2sg[2])
    sel, _ = _choose(pool, order)
    out["B4"] = initial[sel][0] if sel is not None else None
    # AB3
    for name, need in (("AB3_noG5", ("G1", "G2", "G3", "G4")), ("AB3_noG4", ("G1", "G2", "G3", "G5"))):
        pool = {n: final[n][2] for n in order if n in final and final[n][2] and ok(final[n][1], need)}
        sel, _ = _choose(pool, order)
        out[name] = final[sel][0] if sel is not None else None
    pool = {n: initial[n][2] for n in order if n in initial and initial[n][2] and ok(initial[n][1], ORDER)}
    sel, _ = _choose(pool, order)
    out["AB3_norepair"] = initial[sel][0] if sel is not None else None
    # proposed with aligned conflict keys (policy events only; identical for regulation events)
    if event.layer == "company":
        pool = {n: final[n][2] for n in order if n in final and final[n][2] and ok(final[n][1], ORDER)}
        sel, _ = _aligned_choose(pool, order)
        out["proposed_aligned"] = final[sel][0] if sel is not None else None
    else:
        out["proposed_aligned"] = out["proposed"]
    # AB4
    passing = [n for n in order if n in final and ok(final[n][1], ORDER)]
    out["AB4_first"] = final[passing[0]][0] if passing else None
    out["AB4_consensus"] = out["proposed"]
    perfect = None
    if oracle is not None:
        perfect = next((final[n][0] for n in passing if oracle(final[n][0])), None)
    out["AB4_perfect"] = perfect if perfect is not None else (out["AB4_first"] if oracle is None else None)
    return out
