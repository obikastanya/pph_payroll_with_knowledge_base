"""Conflict keys aligned across differently named company rules (representasi.md 8).

The stable key of a conflict holds the ids of the company rules involved. In policy experiments the candidate's company
rules carry names the LLM chose, so the key is aligned before two reports are compared: each company rule id is
replaced by the fact the rule produces in its own knowledge base. Override: (kind, fact, month); constraint: (kind,
sorted facts produced by the company rules the constraint reads, month, code). Regulation experiments do not need this
(the company rules come from the gold policy and keep their ids).
"""
import ast


def produces_map(kb, omega):
    """Rule id -> produced fact for the rules effective at omega."""
    return {rid: r.produces for rid, r in kb.view(omega).rules.items()}


def align(key, produces):
    """key: a conflict key tuple or its str(); produces: rule id -> fact."""
    if isinstance(key, str):
        key = ast.literal_eval(key)
    if key[0] == "override":
        _, _source, fact, month = key
        return ("override", fact, month)
    _, rules, month, code = key
    rules = rules if isinstance(rules, (list, tuple)) else (rules,)
    return ("constraint", tuple(sorted({produces.get(r, r) for r in rules})), month, code)


def aligned(keys, produces):
    return sorted(map(str, {align(k, produces) for k in keys}))
