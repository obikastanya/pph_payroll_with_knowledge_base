"""Static consistency of a knowledge base: gate G3 and the anomaly checker (akuisisi.md G3, representasi.md 11.1).

Errors (fail G3):
  cycle            dependency cycle not broken by a fixed-point rule
  override_cycle   cycle in the overrides relation
  dangling         a fact, parameter, or table read by a rule has no valid producer in some month the rule is valid
  unknown_name     a rule reads a fact, parameter, or table that no record of the knowledge base defines
Warnings (reported, do not fail):
  potential_conflict  same-rank rules for the same fact, overlapping validity, same valid_from, no overrides, and
                      conditions not recognisably exclusive (the engine raises UnresolvedConflict if values differ)
  dead                rule that can never contribute: it produces a fact no output depends on, or its whole validity
                      is covered by an unconditional rule that beats it
  redundant           two rules with the same fact, condition, and expression and overlapping validity
  subsumed            rule whose validity lies inside that of a rule with the same fact and expression, at least
                      the same rank, and a weaker condition

Dependency edges follow what is read in the same period or year: names in the expression and condition, and the
fact arguments of sum_periods, sum_to_date, cumulative, and year_value. Reads of earlier periods (sum_before,
cumulative_before, sum_periods_before_final), of a stated month (value_in), and optional reads (defined, value_or) are
not edges: they cannot close a cycle in one evaluation, and optional reads may be absent by design.
"""
import ast
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

from .expr.functions import CONTEXT_FACTS
from .kb.model import Rule

SAME_TIME = {"sum_periods", "sum_to_date", "cumulative", "year_value"}
OPTIONAL = {"defined", "value_or"}
RANGE = (date(2012, 1, 1), date(2027, 12, 31))


@dataclass(frozen=True)
class Finding:
    kind: str
    severity: str                 # "error" or "warning"
    ids: tuple                    # element ids involved
    fact: str = ""
    detail: str = ""


@dataclass
class Report:
    findings: list = field(default_factory=list)

    @property
    def errors(self):
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self):
        return [f for f in self.findings if f.severity == "warning"]

    @property
    def ok(self):
        return not self.errors

    def counts(self):
        out = defaultdict(int)
        for f in self.findings:
            out[f.kind] += 1
        return dict(out)


# ---------------------------------------------------------------------- reads of an expression
def _calls(expr):
    """(function name, first string argument) of every call in the expression."""
    out = []
    for n in ast.walk(expr.tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.args:
            a = n.args[0]
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                out.append((n.func.id, a.value))
    return out


def reads(rule):
    """(edges, required, optional): facts read in the same evaluation, facts that must have a producer, and facts
    read optionally."""
    edges, required, optional = set(), set(), set()
    for e in (rule.expression, rule.condition):
        if e is None:
            continue
        edges |= e.facts
        required |= e.facts
        for fn, arg in _calls(e):
            if fn in OPTIONAL:
                optional.add(arg)
            elif fn in SAME_TIME:
                edges.add(arg)
                required.add(arg)
            elif fn in ("sum_before", "cumulative_before", "sum_periods_before_final", "value_in"):
                required.add(arg)
    return edges, required, optional


def _params_tables(rule):
    p, t = set(), set()
    for e in (rule.expression, rule.condition):
        if e is not None:
            p |= e.params
            t |= e.tables
    return p, t


# ---------------------------------------------------------------------- time helpers
def _months(start, end):
    d = date(start.year, start.month, 1)
    while d <= end:
        yield d
        d = date(d.year + (d.month == 12), d.month % 12 + 1, 1)


def _span(r):
    lo = max(r.valid_from or RANGE[0], RANGE[0])
    hi = min(r.valid_until or RANGE[1], RANGE[1])
    return lo, hi


def _overlap(a, b):
    (a0, a1), (b0, b1) = _span(a), _span(b)
    return a0 <= b1 and b0 <= a1


def _covers(outer, inner):
    (o0, o1), (i0, i1) = _span(outer), _span(inner)
    return o0 <= i0 and i1 <= o1


def _valid_in_month(r, m, scope):
    if scope == "year":
        y0, y1 = date(m.year, 1, 1), date(m.year, 12, 31)
        return (r.valid_from is None or r.valid_from <= y1) and (r.valid_until is None or y0 <= r.valid_until)
    return r.valid_on(m)


# ---------------------------------------------------------------------- conditions
def _atoms(expr):
    if expr is None:
        return set()
    t = expr.tree
    parts = t.values if isinstance(t, ast.BoolOp) and isinstance(t.op, ast.And) else [t]
    return {ast.dump(p) for p in parts}


def _exclusive(c1, c2):
    """Recognisably exclusive conditions: X and not X, complementary comparisons (a > b, a <= b), or the same name
    compared for equality with different constants, among the conjuncts."""
    if c1 is None or c2 is None:
        return False
    a1 = _conjuncts(c1.tree)
    a2 = _conjuncts(c2.tree)
    for x in a1:
        for y in a2:
            if _negates(x, y) or _negates(y, x) or _different_value(x, y) or _complementary(x, y):
                return True
    return False


_COMPLEMENT = {ast.Gt: ast.LtE, ast.LtE: ast.Gt, ast.Lt: ast.GtE, ast.GtE: ast.Lt, ast.Eq: ast.NotEq,
               ast.NotEq: ast.Eq}


def _complementary(x, y):
    """a > b and a <= b (and the other complementary pairs) on the same operands."""
    if not (isinstance(x, ast.Compare) and isinstance(y, ast.Compare) and len(x.ops) == len(y.ops) == 1):
        return False
    same = ast.dump(x.left) == ast.dump(y.left) and ast.dump(x.comparators[0]) == ast.dump(y.comparators[0])
    return same and _COMPLEMENT.get(type(x.ops[0])) is type(y.ops[0])


def _conjuncts(t):
    return list(t.values) if isinstance(t, ast.BoolOp) and isinstance(t.op, ast.And) else [t]


def _negates(x, y):
    return isinstance(x, ast.UnaryOp) and isinstance(x.op, ast.Not) and ast.dump(x.operand) == ast.dump(y)


def _eq_parts(x):
    if isinstance(x, ast.Compare) and len(x.ops) == 1 and isinstance(x.ops[0], (ast.Eq, ast.NotEq)):
        if isinstance(x.comparators[0], ast.Constant):
            return ast.dump(x.left), x.comparators[0].value, isinstance(x.ops[0], ast.Eq)
    return None


def _different_value(x, y):
    px, py = _eq_parts(x), _eq_parts(y)
    if not px or not py or px[0] != py[0]:
        return False
    (_, vx, ex), (_, vy, ey) = px, py
    if ex and ey:
        return vx != vy
    return (ex != ey) and vx == vy


def _weaker_or_equal(general, specific):
    """Condition `general` holds whenever `specific` holds, judged by conjuncts."""
    return _atoms(general) <= _atoms(specific)


# ---------------------------------------------------------------------- the check
def check(kb, omega, policies=(), adopted=()):
    """Static check of the view of kb at omega. policies: company policies installed (their rules count);
    adopted: ids of optional rules adopted by those policies."""
    view = kb.view(omega)
    rules = [r for r in view.rules.values()
             if (r.layer != "company" or r.policy in policies) and (r.modality != "optional" or r.id in adopted)]
    by_fact = defaultdict(list)
    for r in rules:
        by_fact[r.produces].append(r)
    report = Report()
    add = report.findings.append

    facts = set(view.facts)
    params = {name for name in view.params}
    tables = {name for name in view.tables}

    # unknown names
    for r in rules:
        _, req, opt = reads(r)
        p, t = _params_tables(r)
        for f in sorted((req | opt | {r.produces}) - facts - set(CONTEXT_FACTS)):
            add(Finding("unknown_name", "error", (r.id,), f, "fact not in the vocabulary"))
        for n in sorted(p - params):
            add(Finding("unknown_name", "error", (r.id,), n, "parameter not defined"))
        for n in sorted(t - tables):
            add(Finding("unknown_name", "error", (r.id,), n, "table not defined"))

    # dependency cycles not broken by fixed-point rules
    graph = defaultdict(set)
    for r in rules:
        if r.fixed_point:
            continue
        edges, _, _ = reads(r)
        for f in edges:
            if f in facts:
                graph[r.produces].add(f)
    for cyc in _cycles(graph):
        involved = sorted({r.id for f in cyc for r in by_fact[f] if not r.fixed_point})
        add(Finding("cycle", "error", tuple(involved), cyc[0], " -> ".join(cyc + [cyc[0]])))

    # overrides cycles
    ograph = {r.id: set(r.overrides) for r in rules}
    for cyc in _cycles(ograph):
        add(Finding("override_cycle", "error", tuple(cyc), "", " -> ".join(cyc + [cyc[0]])))

    # dangling references
    for r in rules:
        lo, hi = _span(r)
        if lo > hi:
            continue
        _, req, _ = reads(r)
        p, t = _params_tables(r)
        missing = defaultdict(list)
        for m in _months(lo, hi):
            for f in req:
                if f in CONTEXT_FACTS or f not in facts:
                    continue
                scope = view.facts[f].fact_scope
                if not any(_valid_in_month(x, m, scope) for x in by_fact.get(f, ())):
                    missing[("fact", f)].append(m)
            for n in p:
                if n in params and not any(x.valid_on(m) for x in view.params[n]):
                    missing[("parameter", n)].append(m)
            for n in t:
                if n in tables and not any(x.valid_on(m) for x in view.tables[n]):
                    missing[("table", n)].append(m)
        for (what, name), months in sorted(missing.items()):
            add(Finding("dangling", "error", (r.id,), name,
                        f"{what} has no valid producer in {_month_ranges(months)}"))

    # warnings: potential conflicts, redundancy, subsumption
    for f, rs in by_fact.items():
        for i, a in enumerate(rs):
            for b in rs[i + 1:]:
                if not _overlap(a, b):
                    continue
                same_text = (a.expression.canonical() == b.expression.canonical())
                same_cond = _atoms(a.condition) == _atoms(b.condition)
                if same_text and same_cond:
                    add(Finding("redundant", "warning", (a.id, b.id), f, "same condition and expression"))
                    continue
                if same_text and a.rank <= b.rank and _covers(b, a) and _weaker_or_equal(b.condition, a.condition):
                    add(Finding("subsumed", "warning", (a.id, b.id), f, f"{a.id} adds nothing to {b.id}"))
                    continue
                if same_text and b.rank <= a.rank and _covers(a, b) and _weaker_or_equal(a.condition, b.condition):
                    add(Finding("subsumed", "warning", (b.id, a.id), f, f"{b.id} adds nothing to {a.id}"))
                    continue
                if (a.rank == b.rank and a.valid_from == b.valid_from
                        and b.id not in view.overrides_closure(a.id) and a.id not in view.overrides_closure(b.id)
                        and not _exclusive(a.condition, b.condition)):
                    add(Finding("potential_conflict", "warning", (a.id, b.id), f,
                                "same rank and valid_from, no overrides, conditions not exclusive"))

    # warnings: dead rules
    needed = _needed(view, by_fact)
    for r in rules:
        if r.produces not in needed:
            add(Finding("dead", "warning", (r.id,), r.produces, "no output depends on the fact it produces"))
            continue
        for b in by_fact[r.produces]:
            if b is r or b.condition is not None or not _covers(b, r):
                continue
            beats = b.rank > r.rank or r.id in view.overrides_closure(b.id) or (
                b.rank == r.rank and (b.valid_from or RANGE[0]) > (r.valid_from or RANGE[0])
                and r.id not in view.overrides_closure(b.id) and b.id not in view.overrides_closure(r.id)
                and _covers(b, r) and (b.valid_from or RANGE[0]) <= _span(r)[0])
            if beats:
                add(Finding("dead", "warning", (r.id, b.id), r.produces, f"always beaten by {b.id}"))
                break
    report.findings.sort(key=lambda x: (x.severity, x.kind, x.ids, x.fact))
    return report


def _needed(view, by_fact):
    """Facts some output fact depends on, through any read (including earlier periods and optional reads)."""
    out = {f.id for f in view.facts.values() if f.output}
    stack = list(out)
    while stack:
        f = stack.pop()
        for r in by_fact.get(f, ()):
            e, req, opt = reads(r)
            for g in e | req | opt:
                if g not in out:
                    out.add(g)
                    stack.append(g)
    return out


def _cycles(graph):
    """Strongly connected components with more than one node, or with a self-loop, as lists of nodes."""
    index, low, on, stack, out = {}, {}, set(), [], []
    counter = [0]

    def visit(v):
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in sorted(graph.get(v, ())):
            if w not in index:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1 or v in graph.get(v, ()):
                out.append(sorted(comp))

    import sys
    sys.setrecursionlimit(max(10000, sys.getrecursionlimit()))
    for v in sorted(graph):
        if v not in index:
            visit(v)
    return out


def _month_ranges(months):
    months = sorted(months)
    parts, start, prev = [], months[0], months[0]
    for m in months[1:]:
        nxt = date(prev.year + (prev.month == 12), prev.month % 12 + 1, 1)
        if m != nxt:
            parts.append((start, prev))
            start = m
        prev = m
    parts.append((start, prev))
    return ", ".join(f"{a:%Y-%m}" if a == b else f"{a:%Y-%m}..{b:%Y-%m}" for a, b in parts)
