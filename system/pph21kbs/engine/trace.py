"""Trace completeness (Tahap 5): every output value must lead back to legal sources (representasi.md 11.5).

An output is traced completely when the rule that produced it and every rule of every fact it read (transitively)
are in the trace with at least one source whose quote is not empty and whose document is known. Facts read inside a
fixed-point iteration are in the trace like any other fact.
"""
from dataclasses import dataclass, field

from .evaluator import ERROR_VALUE, YEAR


@dataclass
class TraceReport:
    outputs: int = 0
    complete: int = 0
    nodes: int = 0
    problems: list = field(default_factory=list)     # (output key, problem key, message)

    @property
    def ok(self):
        return not self.problems


def check_trace(result, documents):
    """Check a Result evaluated with trace=True. documents: ids of known source documents."""
    if result.trace is None:
        raise ValueError("evaluate the case with trace=True")
    rep = TraceReport()
    seen = set()
    outputs = [((name, m), v) for m, row in result.periods.items() for name, v in row.items()]
    outputs += [((name, YEAR), v) for name, v in result.year.items()]
    for key, value in outputs:
        if value is None or value == ERROR_VALUE:
            continue
        rep.outputs += 1
        before = len(rep.problems)
        stack, visited = [key], set()
        while stack:
            k = stack.pop()
            if k in visited:
                continue
            visited.add(k)
            entry = result.trace.get(k)
            if entry is None:
                rep.problems.append((key, k, "fact value has no trace entry"))
                continue
            sources = entry.get("source") or []
            if not sources:
                rep.problems.append((key, k, f"rule {entry['rule']} has no source"))
            for s in sources:
                if not (s.get("quote") or "").strip():
                    rep.problems.append((key, k, f"rule {entry['rule']} has an empty quote"))
                if s.get("document") not in documents:
                    rep.problems.append((key, k, f"rule {entry['rule']} cites unknown document {s.get('document')}"))
            stack.extend(entry.get("reads", ()))
        seen |= visited
        if len(rep.problems) == before:
            rep.complete += 1
    rep.nodes = len(seen)
    return rep
