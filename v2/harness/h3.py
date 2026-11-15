"""Impact labels (H3): a company is affected by a regulation event when a fact produced by its policy's rules takes
another value on its employees after the gold update than before. The label comes from the policy's clauses
(their results), not from the regulation facts that change."""
from datetime import date

from pph21kbs import engine  # noqa: E402

from . import corpus, gold, testspace as ts


def company_facts(kb, policies, omega):
    return sorted({r.produces for r in kb.view(omega).rules.values()
                   if getattr(r, "layer", "") == "company" and getattr(r, "policy", None) in policies})


def _with_policies(kb, inst, until):
    for doc in sorted(inst.documents, key=lambda d: d.known_on):
        if doc.gold and gold.exists(doc.gold) and doc.known_on <= until:
            kb = gold.apply(kb, gold.delta(doc.gold))
    return kb


def affected(inst, event, cases):
    """(label, policies in force): whether the regulation event changes a company-produced fact of `inst`."""
    years = set(ts.event_years(event))
    cs = [c for c in cases if c["tax_year"] in years and c["employer"].get("policy")]
    if not cs:
        return None, ()
    policies = tuple(sorted({c["employer"]["policy"] for c in cs}))
    before = _with_policies(gold.base_before(event), inst, event.issued)
    after = gold.apply(before, gold.delta(event.gold), update_id="H3-GOLD")
    facts = company_facts(after, policies, event.issued)
    if not facts:
        return None, policies
    w = max(event.issued, date(max(years), 12, 31))
    for c in cs:
        a = engine.evaluate_case(before, c, omega=w, outputs=facts)
        b = engine.evaluate_case(after, c, omega=w, outputs=facts)
        pick = lambda r: ({m: {f: v for f, v in row.items() if f in facts} for m, row in r.periods.items()},
                          {f: v for f, v in r.year.items() if f in facts})
        if pick(a) != pick(b):
            return True, policies
    return False, policies


def labels(insts, panels):
    """[(instance, event, label, policies)] for every relevant test event in each company's window."""
    out = []
    events = [e for e in corpus.test_stream() if e.relevant]
    for inst in insts:
        for e in events:
            if e.issued < inst.installed:
                continue
            label, policies = affected(inst, e, panels[inst.id])
            if label is not None:
                out.append((inst.id, e.id, label, policies))
    return out
