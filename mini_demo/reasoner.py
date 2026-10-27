"""Mini inference engine that reads its rules from the knowledge graph (skeleton Section IV, Algorithm 1).

Reused from the existing calculator: the safe expression evaluator (engine/ekspresi.py), exact arithmetic
(engine/angka.py), and rounding (engine/pembulatan.py). The existing code keeps its Indonesian names; this module
wraps it with an English interface.
"""
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

from rdflib import RDF

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine.angka import persen as _percent  # noqa: E402
from engine.ekspresi import Ekspresi as _Expression  # noqa: E402
from engine.ekspresi import jumlah_konjungsi as _conjunct_count  # noqa: E402
from engine.pembulatan import bulatkan as _round  # noqa: E402

from kg import TAX  # noqa: E402


def _arity(lo, hi):
    return SimpleNamespace(arg_min=lo, arg_maks=hi)


# Expression language: the only functions a rule may call, including rules written by the LLM.
FUNCTIONS = {"min": _arity(2, None), "max": _arity(2, None), "percent": _arity(1, 1), "round_down": _arity(1, 1),
             "floor_thousand": _arity(1, 1), "table_value": _arity(2, 2), "table_rate": _arity(2, 2),
             "progressive_tax": _arity(2, 2)}
# Output facts that are scored (definition of the calculation result).
OUTPUTS = ("gross_income", "pph21", "pph21_dtp", "pph21_withheld", "take_home_pay")
NOW = date(9999, 12, 31)
EMPLOYEE = "employee"


class ReasoningError(ValueError):
    pass


def parse(text):
    return _Expression(text, FUNCTIONS)


def dependencies(condition, expression):
    deps = set()
    for text in (condition, expression):
        if text:
            deps |= parse(text).dependensi()
    return deps - {EMPLOYEE}


@dataclass(frozen=True)
class Rule:
    id: str
    layer: str
    modality: str
    valid_from: date
    valid_until: object
    recorded_on: date
    produces: str
    condition: object
    expression: object
    source: str
    supersedes: tuple

    @property
    def rank(self):
        """Lex superior: mandatory regulation > company policy > default or optional regulation."""
        if self.layer == "regulation" and self.modality == "mandatory":
            return 3
        return 2 if self.layer == "company" else 1

    def active(self, t, knowledge_date):
        return (self.valid_from <= t and (self.valid_until is None or t <= self.valid_until)
                and self.recorded_on <= knowledge_date)


def _read_rules(g):
    rules = []
    for n in g.subjects(RDF.type, TAX.Rule):
        v = lambda p: g.value(n, p)  # noqa: E731
        article = v(TAX.hasSource)
        rules.append(Rule(
            id=str(v(TAX.id)),
            layer="regulation" if v(TAX.layer) == TAX.RegulationLayer else "company",
            modality=str(v(TAX.modality)),
            valid_from=v(TAX.validFrom).toPython(),
            valid_until=v(TAX.validUntil).toPython() if v(TAX.validUntil) else None,
            recorded_on=v(TAX.recordedOn).toPython(),
            produces=str(g.value(v(TAX.produces), TAX.name)),
            condition=parse(str(v(TAX.condition))) if v(TAX.condition) else None,
            expression=parse(str(v(TAX.expression))),
            source=str(g.value(article, TAX.label)) if article else "",
            supersedes=tuple(str(g.value(x, TAX.id)) for x in g.objects(n, TAX.supersedes))))
    return rules


def _read_tables(g):
    tables = []
    for n in g.subjects(RDF.type, TAX.Table):
        rows = []
        for b in g.objects(n, TAX.row):
            row = {k: str(g.value(b, TAX[k])) for k in ("key", "lower", "upper", "value") if g.value(b, TAX[k]) is not None}
            rows.append((int(g.value(b, TAX.order)), row))
        tables.append({"name": str(g.value(n, TAX.name)), "valid_from": g.value(n, TAX.validFrom).toPython(),
                       "recorded_on": g.value(n, TAX.recordedOn).toPython(), "rows": [r for _, r in sorted(rows)]})
    return tables


_CACHE = {}


def load(g):
    if id(g) not in _CACHE or _CACHE[id(g)][0] is not g:
        _CACHE[id(g)] = (g, _read_rules(g), _read_tables(g))
    return _CACHE[id(g)][1], _CACHE[id(g)][2]


@dataclass
class Result:
    values: dict
    trace: dict          # fact -> (winning rule id, source article)
    conflicts: frozenset # (fact, company rule id) overridden by a mandatory rule

    def outputs(self):
        return tuple(self.values.get(f) for f in OUTPUTS)


class _Context:
    """Evaluation context. The legacy evaluator calls nilai(), input(), and panggil(); they map to English methods."""

    def __init__(self, by_fact, tables, case):
        self.by_fact, self.tables, self.case = by_fact, tables, case
        self.memo, self.trace, self.conflicts, self._busy = {}, {}, set(), set()

    def value(self, fact):
        if fact in self.memo:
            return self.memo[fact]
        if fact not in self.by_fact:
            raise ReasoningError(f"fact '{fact}' is not produced by any rule in this period")
        if fact in self._busy:
            raise ReasoningError(f"cycle on fact '{fact}'")
        self._busy.add(fact)
        fired = [r for r in self.by_fact[fact] if r.condition is None or r.condition.evaluasi(self)]
        result = None
        if fired:
            top = max(r.rank for r in fired)
            group = [r for r in fired if r.rank == top]
            for key in (lambda r: _conjunct_count(r.condition), lambda r: r.valid_from):   # lex specialis, lex posterior
                best = max(key(r) for r in group)
                group = [r for r in group if key(r) == best]
            values = {r.expression.evaluasi(self) for r in group}
            if len(values) > 1:
                raise ReasoningError(f"AMBIGUOUS fact '{fact}': {[r.id for r in group]}")
            result = values.pop()
            if top == 3:
                self.conflicts.update((fact, r.id) for r in fired if r.layer == "company")
            self.trace[fact] = (group[0].id, group[0].source)
        self._busy.discard(fact)
        self.memo[fact] = result
        return result

    def input(self, path):
        key = path.split(".", 1)[1]
        if key not in self.case:
            raise ReasoningError(f"employee field '{key}' is missing")
        return self.case[key]

    def call(self, fn, args):
        if fn == "min":
            return min(args)
        if fn == "max":
            return max(args)
        if fn == "percent":
            return _percent(args[0])
        if fn == "round_down":
            return _round(args[0], "bawah")
        if fn == "floor_thousand":
            return _round(args[0], "bawah", 1000)
        table = self.tables.get(args[0])
        if table is None:
            raise ReasoningError(f"table '{args[0]}' is not in force in this period")
        x = args[1]
        if fn == "table_value":
            for row in table["rows"]:
                if row.get("key") == x:
                    return int(row["value"]) if row["value"].isdigit() else row["value"]
            raise ReasoningError(f"key '{x}' not found in table '{args[0]}'")
        if fn == "table_rate":
            for row in table["rows"]:
                if int(row["lower"]) < x and ("upper" not in row or x <= int(row["upper"])):
                    return Fraction(row["value"]) / 100
            raise ReasoningError(f"value {x} is outside table '{args[0]}'")
        if fn == "progressive_tax":
            tax = Fraction(0)
            for row in table["rows"]:
                lower = int(row["lower"])
                upper = int(row["upper"]) if "upper" in row else None
                if x > lower:
                    tax += ((min(x, upper) if upper is not None else x) - lower) * Fraction(row["value"]) / 100
            return tax
        raise ReasoningError(f"unknown function '{fn}'")

    # Names expected by the legacy evaluator (engine/ekspresi.py).
    nilai = value
    panggil = call


def select(g, t, knowledge_date=NOW):
    """Algorithm 1, step 1: rules and tables in force in period t, as known on knowledge_date, after repeal.
    Returns (rules in force, tables in force by name, ids of rules that are valid but superseded)."""
    rules, tables = load(g)
    active = [r for r in rules if r.active(t, knowledge_date)]
    superseded = {i for r in active for i in r.supersedes}
    in_force = {}
    for tb in tables:
        if (tb["valid_from"] <= t and tb["recorded_on"] <= knowledge_date
                and (tb["name"] not in in_force or tb["valid_from"] > in_force[tb["name"]]["valid_from"])):
            in_force[tb["name"]] = tb
    return [r for r in active if r.id not in superseded], in_force, superseded & {r.id for r in active}


def compute(g, case, knowledge_date=NOW):
    """Compute every fact for one employee in one tax period, with the knowledge base as known on knowledge_date."""
    rules, tables, _ = select(g, date(case["year"], case["month"], 1), knowledge_date)
    by_fact = defaultdict(list)
    for r in rules:
        by_fact[r.produces].append(r)
    ctx = _Context(by_fact, tables, case)
    for fact in sorted(by_fact):
        ctx.value(fact)
    return Result(ctx.memo, ctx.trace, frozenset(ctx.conflicts))


def _reads(rule):
    deps = rule.expression.dependensi() | (rule.condition.dependensi() if rule.condition else set())
    return deps - {EMPLOYEE}


def anomalies(g, t, knowledge_date=NOW):
    """Knowledge-base anomaly check for one period (used by gate G3 and by the RQ3 diagnostic 'KB anomalies').
    Returns (kind, rule id, detail) with kind in dangling, conflict, overridden, unused, superseded."""
    rules, _, superseded = select(g, t, knowledge_date)
    produced = {r.produces for r in rules}
    read = set().union(*(_reads(r) for r in rules)) if rules else set()
    found = []
    for r in sorted(rules, key=lambda r: r.id):
        for f in sorted(_reads(r) - produced):
            found.append(("dangling", r.id, f"reads '{f}', which no rule in force produces"))
        rivals = [x for x in rules if x.produces == r.produces and x.rank > r.rank and x.condition is None]
        if rivals and r.layer == "company":
            found.append(("conflict", r.id, f"overridden by mandatory rule {rivals[0].id} on '{r.produces}' (reported, A4)"))
        elif rivals:
            found.append(("overridden", r.id, f"never wins against {rivals[0].id} on '{r.produces}'"))
        if r.produces not in read and r.produces not in OUTPUTS:
            found.append(("unused", r.id, f"'{r.produces}' is not read by any rule in force and is not an output"))
    found += [("superseded", i, "valid in this period but repealed by a later rule") for i in sorted(superseded)]
    return found
