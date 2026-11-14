"""Self-check round with execution feedback (pipeline v2, development).

After a candidate passes the gates, the model sees what its Delta does when executed on the generated cases S^G
(which facts change, in how many cases and months, with an example), the case-data attributes it reads that do not
exist yet, and the gate warnings, and returns a final Delta. The gates then run again; a reviewed Delta that fails
them is discarded and the candidate keeps its version before the review.
"""
import json
from collections import defaultdict

REVIEW_INSTRUCTION = """SELF-CHECK: your Delta for this document passed the automatic checks. Below is what it does when
the engine executes it on generated test cases ("before" = the knowledge base without your Delta, "after" = with it).
Check it against the document text and return the complete final Delta:
1. Every changed fact must follow from the document. Remove or correct elements that cause changes the document does
   not require (for example a rewritten total, an extra rounding, or a rule that also fires for cases the document
   excludes).
2. Every provision of the document that changes the computation must be covered: values, rates, thresholds,
   exemptions or ceilings, eligibility conditions, periods, calculation steps, and how the tax is borne or paid. Add
   the elements that are missing. Name the provisions you covered in note.
3. Case-data inputs your Delta reads that do not exist yet are listed below. Use an existing attribute from CASE DATA
   if one has the same meaning; keep a new input only if the document introduces a genuinely new item.
4. Keep everything that is right. If nothing needs to change, return the same Delta."""


def _fmt(v):
    return str(v) if v is not None else "none"


def effect_summary(base, kb2, sgs, evals, limit_facts=14):
    """Text: per observed fact, the cases and months in which K' differs from K, with one example."""
    late = sgs.omegas[1]
    per_fact = defaultdict(lambda: {"cases": set(), "months": set(), "example": None})
    n = len(sgs.cases)
    for i in range(n):
        o1, c1, e1, final = evals.get("K'", kb2, i, late)
        o0, c0, e0, _ = evals.get("K", base, i, late)
        for k in set(o1) | set(o0):
            if o1.get(k) != o0.get(k):
                m, f = k
                d = per_fact[f]
                d["cases"].add(i)
                d["months"].add(m or final)
                if d["example"] is None:
                    case = sgs.cases[i]
                    d["example"] = (f"{case['case_id']} (year {case['tax_year']}, method {case.get('method')}, "
                                    f"PTKP {case['employee'].get('ptkp_status')}, policy "
                                    f"{case['employer'].get('policy')}), month {m or final}: "
                                    f"{_fmt(o0.get(k))} -> {_fmt(o1.get(k))}")
    lines = [f"EXECUTION ON {n} GENERATED CASES (facts whose values change):"]
    if not per_fact:
        lines.append("- no observed fact changes in any generated case")
    for f, d in sorted(per_fact.items(), key=lambda x: -len(x[1]["cases"]))[:limit_facts]:
        months = sorted(d["months"])
        lines.append(f"- {f}: changes in {len(d['cases'])} of {n} cases, months {months[:12]}; e.g. {d['example']}")
    if len(per_fact) > limit_facts:
        lines.append(f"- ... {len(per_fact) - limit_facts} more facts change")
    return "\n".join(lines)


def review_user(metadata, llm_delta, summary, new_inputs, warnings):
    parts = [metadata, REVIEW_INSTRUCTION, "YOUR DELTA:\n" + json.dumps(llm_delta, ensure_ascii=False), summary]
    parts.append("NEW CASE-DATA INPUTS READ BY YOUR DELTA: " + (", ".join(new_inputs) if new_inputs else "none"))
    parts.append("GATE WARNINGS: " + ("; ".join(warnings) if warnings else "none"))
    parts.append("Return the complete final Delta.")
    return "\n\n".join(parts)
