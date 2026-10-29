"""How a result was computed, read from the knowledge base and the engine trace, for the calculator's result cards.

Nothing here names a step of the tax calculation. The program only knows the value it is asked about (the PPh 21 of
a month); the steps under it are the facts that the winning rules' formulas read, in the order the formulas name them,
and the results to show are the facts the knowledge base marks as output. A new component, deduction, or way of
computing the tax in the knowledge base therefore shows up in the cards without changing this module.
"""
import streamlit as st

import data as d
import demo

ROOT = "pph21_due"          # the value the calculator is for: the PPh 21 withheld in a month


@st.cache_resource
def _view(signature, omega):
    return d.kb().view(omega)


def view(omega):
    return _view(demo.signature(), omega)


def rule(r, key, omega):
    t = (r.trace or {}).get(key)
    return view(omega).rules.get(t["rule"]) if t else None


def children(r, key, omega):
    """(fact, month) read directly by the formula of the rule that gave this value, in the order the formula names
    them. Year facts are read at month 0. Only values the engine computed for this case."""
    rl = rule(r, key, omega)
    if rl is None or rl.expression is None:
        return []
    text = rl.expression.text
    out = []
    for f in sorted(rl.expression.dependencies(), key=lambda f: (text.find(f) if f in text else len(text), f)):
        fd = view(omega).facts.get(f)
        k = (f, 0 if fd is not None and fd.fact_scope == "year" else key[1])
        if k in r.trace and k != key:
            out.append(k)
    return out


def value(r, key):
    t = (r.trace or {}).get(key)
    return t["value"] if t else None


def working(r, key, omega):
    """Skip rules that only pass one value on unchanged (the PPh 21 of the month = the PPh 21 of the final month):
    the rule that does the work."""
    seen = {key}
    while True:
        kids = [k for k in children(r, key, omega) if value(r, k) not in (None, 0, False, "")]
        if len(kids) == 1 and value(r, kids[0]) == value(r, key) and kids[0] not in seen:
            key = kids[0]
            seen.add(key)
            continue
        return key


def is_sum(r, key, omega):
    """True when the value is the sum of the non-zero values its formula reads (a subtotal such as gross income)."""
    kids = [k for k in children(r, key, omega) if _number(value(r, k))]
    return len(kids) > 1 and sum(value(r, k) for k in kids) == value(r, key)


def _number(v):
    return v not in (None, 0) and not isinstance(v, (bool, str))


def is_input(r, key):
    t = (r.trace or {}).get(key)
    return bool(t) and any(s.get("document") == "INPUT-CONVENTION" for s in t.get("source") or [])


def ladder(r, key, omega, scope_month=0, depth=8):
    """Post-order list of (key, depth) of the year values under key: the steps of the year calculation from the first
    one to the result. Stops at values of a single month (they are sums of months, shown as one line)."""
    out, seen = [], set()

    def go(k, level):
        if k in seen or level > depth:
            return
        seen.add(k)
        for c in children(r, k, omega):
            if c[1] == scope_month and value(r, c) not in (None, 0, ""):
                go(c, level + 1)
        out.append((k, level))
    go(key, 0)
    return out


def downstream(r, month, omega, source=ROOT):
    """Facts of the month that the KB marks as output and whose rules read the source value, directly or through
    other values of the month (e.g. PPh 21 borne by the government, take-home pay)."""
    facts = view(omega).facts
    readers = {}
    for (f, m), t in r.trace.items():
        if m == month:
            for c in children(r, (f, m), omega):
                readers.setdefault(c[0], set()).add(f)
    found, todo = set(), [source]
    while todo:
        for f in readers.get(todo.pop(), ()):
            if f not in found:
                found.add(f)
                todo.append(f)
    return [f for f in sorted(found, key=lambda f: facts[f].seq if f in facts else 0)
            if f in facts and facts[f].output and (f, month) in r.trace]


def outputs(r, months, omega):
    """Output facts of a month (as the KB marks them) that are non-zero in some of the months, in KB order."""
    facts = view(omega).facts
    names = {f for m in months for f, v in (r.periods.get(m) or {}).items() if _number(v)}
    return [f for f in sorted(names, key=lambda f: facts[f].seq if f in facts else 0)
            if f in facts and facts[f].output]


def source_of(r, key):
    t = (r.trace or {}).get(key)
    s = (t or {}).get("source") or []
    return s[0] if s else None
