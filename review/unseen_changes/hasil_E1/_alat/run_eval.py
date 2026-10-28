"""Evaluate converted examples on a knowledge base and compare with the stated values."""
from pph21kbs.engine import evaluate_case


def observe(r, key):
    if key[0] == "period":
        return (r.periods.get(key[1]) or {}).get(key[2])
    if key[0] == "year":
        return r.year.get(key[1])
    return "UNMAPPED"


def evaluate(kb, omega, case, exp):
    view = kb.view(omega)
    names = {f.id for f in view.facts.values() if f.output}
    names |= {k[-1] for k in exp if k[0] in ("period", "year")}
    r = evaluate_case(view, case, outputs=sorted(n for n in names if n in view.facts))
    diffs = [(k, observe(r, k), v) for k, v in exp.items() if observe(r, k) != v]
    return r, diffs
