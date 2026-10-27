"""Inference engine: one employee, one tax year (representasi.md 8 and 11, Algorithm 1).

Facts are evaluated on demand with memoisation, which visits the fact dependency graph in topological order. A fact
is selected by scope and evaluation date, filtered by its rules' conditions, resolved by lex superior (rank), lex
specialis (explicit overrides), and lex posterior (recorded_on, then valid_from). Rules marked fixed_point compute the
least fixed point by iteration from their lower bound. All arithmetic is exact; money facts must come out whole.
"""
from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction

from ..expr import CONTEXT_FACTS, ExpressionError, PrecisionError
from ..expr.numbers import check_number, normalize, round_value
from ..kb.store import KnowledgeBase

YEAR = 0          # context key of year-scope facts
MAX_FIXED_POINT_ROUNDS = 200


class EngineError(Exception):
    kind = "EngineError"

    def __init__(self, message, fact=None, month=None, rule=None):
        super().__init__(message)
        self.fact, self.month, self.rule = fact, month, rule

    def describe(self):
        where = f"{self.fact}@{'year' if self.month == YEAR else self.month}" if self.fact else ""
        rule = f" [{self.rule}]" if self.rule else ""
        return f"{self.kind}({where}){rule}: {self}"


class MissingRule(EngineError):
    kind = "MissingRule"


class UnresolvedConflict(EngineError):
    kind = "UnresolvedConflict"


class CircularDefinition(EngineError):
    kind = "CircularDefinition"


class FixedPointError(EngineError):
    kind = "FixedPointError"


class TypeViolation(EngineError):
    kind = "TypeViolation"


class MissingParameter(EngineError):
    kind = "MissingParameter"


class MissingTable(EngineError):
    kind = "MissingTable"


class EvaluationError(EngineError):
    kind = "EvaluationError"


class UnknownFact(EngineError):
    kind = "UnknownFact"


class _Failed:
    """Memo entry of a fact whose evaluation failed; reading it re-raises the root cause."""
    __slots__ = ("error",)

    def __init__(self, error):
        self.error = error


@dataclass
class Result:
    case_id: str
    omega: date
    periods: dict = field(default_factory=dict)      # month -> {fact: value}
    year: dict = field(default_factory=dict)          # fact -> value
    conflicts: list = field(default_factory=list)     # dicts (see conflict_key)
    errors: list = field(default_factory=list)        # strings
    winners: dict = field(default_factory=dict)       # (fact, month|0) -> rule id
    warnings: list = field(default_factory=list)
    trace: dict | None = None

    def conflict_keys(self):
        return {conflict_key(c) for c in self.conflicts}


def conflict_key(c):
    """Stable key of a conflict entry (representasi.md 8): independent of the regulation element names chosen by
    whoever wrote the Delta."""
    if c["kind"] == "override":
        return ("override", c["source"], c.get("fact"), c.get("month"))
    return ("constraint", c.get("company_rules") or (), c.get("month"), c.get("code"))


ERROR_VALUE = "ERROR"


class Evaluator:
    def __init__(self, view, case, trace=False):
        self.view = view
        self.case = case
        self.year = int(case["tax_year"])
        policy = (case.get("employer") or {}).get("policy")
        self.policies = set(policy if isinstance(policy, (list, tuple)) else ([policy] if policy else []))
        self.adopted = set()
        for p in self.policies:
            self.adopted |= set(view.kb.adoptions.get(p, ()))
        self.read_inputs = set()
        self.periods = {int(p["month"]): p for p in case["periods"]}
        self.months = sorted(self.periods)
        if not self.months:
            raise ValueError(f"case {case.get('case_id')} has no periods")
        self.first, self.final = self.months[0], self.months[-1]
        self.memo = {}
        self.in_progress = {}      # key -> stack of fixed-point levels at which evaluation of the key started
        self.fp_level = 0          # depth of nested fixed-point iterations
        self.fixed = {}
        self.winners = {}
        self.conflicts = {}
        self.warnings = []
        self.trace = {} if trace else None
        self._reads = []
        self._envs = {}
        self.year_start = date(self.year, self.first, 1)
        self.year_end = _month_end(self.year, self.final)

    # ------------------------------------------------------------------ dates and contexts
    def eval_date(self, ctx):
        return date(self.year, self.final if ctx == YEAR else ctx, 1)

    def env(self, ctx):
        e = self._envs.get(ctx)
        if e is None:
            e = self._envs[ctx] = _Env(self, ctx)
        return e

    # ------------------------------------------------------------------ facts
    def builtin(self, name, ctx):
        if name == "month":
            if ctx == YEAR:
                raise EvaluationError("built-in 'month' read in a year-scope rule", fact=name, month=ctx)
            return ctx
        if name == "tax_year":
            return self.year
        if name == "is_final_period":
            return True if ctx == YEAR else ctx == self.final
        if name == "first_month":
            return self.first
        if name == "final_month":
            return self.final
        if name == "months_employed":
            return len(self.months)
        raise UnknownFact(f"unknown built-in {name}")

    def key_of(self, name, ctx):
        fdef = self.view.facts.get(name)
        if fdef is None:
            raise UnknownFact(f"fact {name!r} is not in the vocabulary", fact=name, month=ctx)
        if fdef.fact_scope == "year":
            return (name, YEAR)
        if ctx == YEAR:
            raise EvaluationError(f"period fact {name!r} read in a year-scope rule; use sum_periods/value_in",
                                  fact=name, month=ctx)
        return (name, ctx)

    def fact(self, name, ctx):
        if name in CONTEXT_FACTS:
            return self.builtin(name, ctx)
        key = self.key_of(name, ctx)
        return self._value(key)

    def _value(self, key):
        if self._reads:
            self._reads[-1].add(key)
        if key in self.fixed:
            return self.fixed[key]
        v = self.memo.get(key, _MISSING)
        if v is not _MISSING:
            if isinstance(v, _Failed):
                raise v.error
            return v
        levels = self.in_progress.get(key)
        if levels and levels[-1] >= self.fp_level:
            # A key that started outside the current fixed-point iteration may be recomputed inside it: its
            # dependency on the fixed-point fact is satisfied by the iterate. Anything else is a real cycle.
            raise CircularDefinition(f"{key[0]} depends on itself", fact=key[0], month=key[1])
        self.in_progress.setdefault(key, []).append(self.fp_level)
        try:
            v = self._compute(key)
        except EngineError as e:
            self.memo[key] = _Failed(e)
            raise
        finally:
            stack = self.in_progress[key]
            stack.pop()
            if not stack:
                del self.in_progress[key]
        self.memo[key] = v
        return v

    def active_rules(self, name, ctx):
        """Rules that produce the fact, are valid on the evaluation date, are adopted if optional, and whose
        condition holds."""
        d = self.eval_date(ctx)
        fdef = self.view.facts.get(name)
        scope = fdef.fact_scope if fdef else ("year" if ctx == YEAR else "period")
        out = []
        for r in self.view.rules_by_fact.get(name, ()):
            if r.scope != scope or not self._valid(r, ctx, d):
                continue
            if r.layer == "company" and r.policy not in self.policies:
                continue
            if r.layer == "regulation" and r.modality == "optional" and r.id not in self.adopted:
                continue
            if r.condition is not None:
                try:
                    ok = _truth(self._eval(r.condition, ctx, r, (name, ctx)))
                except (ExpressionError, PrecisionError) as e:
                    raise EvaluationError(f"condition: {e}", fact=name, month=ctx, rule=r.id) from None
                if not ok:
                    continue
            out.append(r)
        return out

    def _valid(self, r, ctx, d):
        """Period scope: valid on the first day of the month. Year scope: validity intersects the employment span of
        the tax year (representasi.md 7)."""
        if ctx != YEAR:
            return r.valid_on(d)
        return (r.valid_from is None or r.valid_from <= self.year_end) and \
            (r.valid_until is None or r.valid_until >= self.year_start)

    def _compute(self, key):
        name, ctx = key
        active = self.active_rules(name, ctx)
        if not active:
            raise MissingRule(f"no active rule produces {name}", fact=name, month=ctx)
        winner, losers = self._resolve(active, key)
        reads = set()
        self._reads.append(reads)
        try:
            if winner.fixed_point:
                value = self._fixed_point(winner, key)
            else:
                value = self._eval(winner.expression, ctx, winner, key)
        except (ExpressionError, PrecisionError) as e:
            raise EvaluationError(str(e), fact=name, month=ctx, rule=winner.id) from None
        finally:
            self._reads.pop()
            if self._reads:
                self._reads[-1] |= reads
        value = self._check_type(name, value, ctx, winner)
        self.winners[key] = winner.id
        if self.trace is not None:
            self.trace[key] = {"rule": winner.id, "layer": winner.layer, "modality": winner.modality,
                               "value": value, "reads": sorted(reads, key=str), "losers": losers,
                               "source": [s.to_json() for s in winner.source]}
        return value

    def _eval(self, expr, ctx, rule, key):
        return expr.evaluate(self.env(ctx))

    # ------------------------------------------------------------------ resolution
    def _rank(self, r):
        return r.rank

    def _resolve(self, active, key):
        losers = []
        top = max(self._rank(r) for r in active)
        remaining = [r for r in active if self._rank(r) == top]
        for r in active:
            if self._rank(r) != top:
                losers.append((r.id, "lex superior"))
        if top == 4:
            for r in active:
                if r.layer == "company":
                    self._record_override(r, remaining, key)
        if len(remaining) > 1:
            beaten = set()
            for r in remaining:
                beaten |= self.view.overrides_closure(r.id) & {x.id for x in remaining if x.id != r.id}
            if beaten and len(beaten) < len(remaining):
                losers += [(x, "lex specialis") for x in sorted(beaten)]
                remaining = [r for r in remaining if r.id not in beaten]
        if len(remaining) > 1:
            def posterior(r):
                return (r.valid_from or date.min, self.view.first_recorded.get(r.id) or r.recorded_on)
            best = max(posterior(r) for r in remaining)
            nxt = [r for r in remaining if posterior(r) == best]
            losers += [(r.id, "lex posterior") for r in remaining if r not in nxt]
            remaining = nxt
        if len(remaining) > 1:
            values = []
            for r in remaining:
                try:
                    values.append(self._eval(r.expression, key[1], r, key))
                except (ExpressionError, PrecisionError, EngineError):
                    values.append(_MISSING)
            if all(v == values[0] and v is not _MISSING for v in values):
                ordered = sorted(remaining, key=lambda r: r.seq)
                self.warnings.append(f"RedundantRules({key[0]}): {', '.join(r.id for r in ordered)}")
                return ordered[0], losers + [(r.id, "redundant") for r in ordered[1:]]
            raise UnresolvedConflict(
                f"no unique winner among {', '.join(sorted(r.id for r in remaining))}", fact=key[0], month=key[1])
        return remaining[0], losers

    def _record_override(self, company_rule, mandatory_rules, key):
        """A company rule loses to a mandatory regulation rule: report a conflict when the values differ (A4)."""
        name, ctx = key
        try:
            company_value = self._eval(company_rule.expression, ctx, company_rule, key)
        except (ExpressionError, PrecisionError, EngineError) as e:
            company_value = f"ERROR: {e}"
        winner = mandatory_rules[0] if len(mandatory_rules) == 1 else None
        try:
            reg_value = self._eval(winner.expression, ctx, winner, key) if winner and not winner.fixed_point else None
        except (ExpressionError, PrecisionError, EngineError):
            reg_value = None
        if winner is not None and winner.fixed_point is None and reg_value == company_value:
            return
        c = {"kind": "override", "source": company_rule.id, "target": winner.id if winner else None,
             "fact": name, "month": ctx, "code": company_rule.conflict_code or "C?",
             "policy": company_rule.policy}
        self.conflicts[conflict_key(c)] = c

    # ------------------------------------------------------------------ fixed point
    def _fixed_point(self, rule, key):
        name, ctx = key
        lower = self._eval(rule.fixed_point[0], ctx, rule, key)
        upper = self._eval(rule.fixed_point[1], ctx, rule, key)
        t = lower
        for _ in range(MAX_FIXED_POINT_ROUNDS):
            before = set(self.memo)
            before_w = set(self.winners)
            self.fixed[key] = t
            self.fp_level += 1
            try:
                new = self._eval(rule.expression, ctx, rule, key)
            except EngineError:
                for k in set(self.memo) - before:
                    del self.memo[k]
                raise
            finally:
                self.fp_level -= 1
                del self.fixed[key]
            if new == t:
                return t
            for k in set(self.memo) - before:
                del self.memo[k]
            for k in set(self.winners) - before_w:
                del self.winners[k]
            check_number(new, "fixed point iterate")
            if new < lower or new > upper:
                raise FixedPointError(f"iterate {new} left [{lower}, {upper}]", fact=name, month=ctx, rule=rule.id)
            t = new
        raise FixedPointError(f"no convergence in {MAX_FIXED_POINT_ROUNDS} rounds", fact=name, month=ctx,
                              rule=rule.id)

    # ------------------------------------------------------------------ types
    def _check_type(self, name, value, ctx, rule):
        fdef = self.view.facts[name]
        t = fdef.fact_type
        if t == "money" or t == "int":
            if isinstance(value, bool) or not isinstance(value, int):
                if isinstance(value, Fraction):
                    raise TypeViolation(f"{t} fact computed as fraction {value}; rounding is not stated",
                                        fact=name, month=ctx, rule=rule.id)
                raise TypeViolation(f"{t} fact computed as {value!r}", fact=name, month=ctx, rule=rule.id)
        elif t in ("exact", "rate"):
            if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
                raise TypeViolation(f"{t} fact computed as {value!r}", fact=name, month=ctx, rule=rule.id)
        elif t == "bool":
            if not isinstance(value, bool):
                raise TypeViolation(f"bool fact computed as {value!r}", fact=name, month=ctx, rule=rule.id)
        elif t == "category":
            if value is not None and not isinstance(value, str):
                raise TypeViolation(f"category fact computed as {value!r}", fact=name, month=ctx, rule=rule.id)
        return value

    # ------------------------------------------------------------------ functions
    def call(self, fname, args, ctx):
        d = self.eval_date(ctx)
        if fname in ("min", "max"):
            nums = [check_number(a, f"argument of {fname}") for a in args]
            return normalize(min(nums) if fname == "min" else max(nums))
        if fname == "abs":
            return normalize(abs(check_number(args[0])))
        if fname == "round":
            return round_value(args[0], args[1], args[2])
        if fname == "param":
            return self._param(args[0], d, ctx)
        if fname in ("lookup", "bracket", "progressive", "in_table", "table_attr"):
            return self._table_fn(fname, args, d, ctx)
        if fname == "startswith":
            if not isinstance(args[0], str) or not isinstance(args[1], str):
                raise ExpressionError(f"startswith needs text, got {args!r}")
            return args[0].startswith(args[1])
        if fname in ("income", "benefit", "hr", "zakat_paid"):
            if ctx == YEAR:
                raise ExpressionError(f"{fname}() used in a year-scope rule")
            p = self.periods[ctx]
            if fname == "zakat_paid":
                return int(p.get("zakat", 0) or 0)
            bucket = {"income": "income", "benefit": "benefits", "hr": "hr"}[fname]
            self.read_inputs.add((bucket, args[0]))
            return (p.get(bucket) or {}).get(args[0], 0)
        if fname in ("employee", "employer"):
            return (self.case.get(fname) or {}).get(args[0])
        if fname == "case":
            a = args[0]
            if a in ("start_month", "end_month"):
                return (self.case.get("employment") or {}).get(a)
            return self.case.get(a)
        if fname in ("sum_periods", "sum_periods_before_final"):
            months = self.months if fname == "sum_periods" else self.months[:-1]
            return self._sum(args[0], months)
        if fname in ("sum_to_date", "sum_before"):
            if ctx == YEAR:
                raise ExpressionError(f"{fname}() used in a year-scope rule")
            months = [m for m in self.months if (m <= ctx if fname == "sum_to_date" else m < ctx)]
            return self._sum(args[0], months)
        if fname == "value_in":
            m = args[1]
            if m not in self.periods:
                return None
            return self._value(self.key_of(args[0], m))
        if fname == "year_value":
            return self._value(self.key_of(args[0], YEAR))
        if fname in ("defined", "value_or"):
            key = self.key_of(args[0], ctx)
            if key in self.memo and not isinstance(self.memo[key], _Failed):
                return True if fname == "defined" else self.memo[key]
            if key in self.fixed:
                return True if fname == "defined" else self.fixed[key]
            has = bool(self.active_rules(key[0], key[1]))
            if fname == "defined":
                return has
            return self._value(key) if has else args[1]
        raise ExpressionError(f"function {fname} not implemented")

    def _sum(self, name, months):
        total = 0
        for m in months:
            v = self._value(self.key_of(name, m))
            total += check_number(v, f"value of {name} in month {m}")
        return normalize(total)

    def _pick(self, records, what, d, ctx=None):
        """Among same-name parameters/tables valid in the context: latest valid_from, then first recording date,
        then application order (representasi.md 3)."""
        valid = [r for r in records if self._valid(r, ctx if ctx is not None else -1, d)]
        if not valid:
            return None
        return max(valid, key=lambda r: (r.valid_from or date.min, self.view.first_recorded.get(r.id) or r.recorded_on,
                                         r.seq))

    def _param(self, name, d, ctx):
        rec = self._pick(self.view.params.get(name, ()), "parameter", d, ctx)
        if rec is None:
            raise MissingParameter(f"parameter {name!r} has no value valid on {d}", fact=name, month=ctx)
        return rec.value

    def _table_fn(self, fname, args, d, ctx):
        name = args[0]
        rec = self._pick(self.view.tables.get(name, ()), "table", d, ctx)
        if rec is None:
            raise MissingTable(f"table {name!r} has no version valid on {d}", fact=name, month=ctx)
        rows = rec.rows
        if fname == "lookup":
            key = str(args[1])
            for r in rows:
                if r["key"] == key:
                    return r["value"]
            raise ExpressionError(f"key {key!r} not in lookup table {name}")
        if fname == "bracket":
            key, amount = (None if args[1] is None else str(args[1])), check_number(args[2], "bracket amount")
            for r in rows:
                if (r["key"] is None or r["key"] == key) and r["lower"] < amount and \
                        (r["upper"] is None or amount <= r["upper"]):
                    return r["value"]
            if amount <= 0:
                for r in rows:
                    if (r["key"] is None or r["key"] == key) and r["lower"] == 0:
                        return r["value"]
            raise ExpressionError(f"no bracket of {name} for key {key!r} and amount {amount}")
        if fname == "progressive":
            amount = check_number(args[1], "progressive amount")
            total = Fraction(0)
            for r in rows:
                if amount > r["lower"]:
                    top = amount if r["upper"] is None else min(amount, r["upper"])
                    total += Fraction(r["rate"]) * (top - r["lower"])
            return normalize(total)
        if fname == "in_table":
            key = str(args[1])
            return any(r.get("key") == key for r in rows)
        key = str(args[1])
        for r in rows:
            if r.get("key") == key:
                return r.get(args[2])
        return None

    # ------------------------------------------------------------------ constraints and outputs
    def check_constraints(self):
        errors = []
        for c in self.view.constraints:
            ctxs = [YEAR] if c.scope == "year" else self.months
            for ctx in ctxs:
                if not c.valid_on(self.eval_date(ctx)):
                    continue
                try:
                    env = self.env(ctx)
                    if c.condition is not None and not _truth(c.condition.evaluate(env)):
                        continue
                    ok = _truth(c.assertion.evaluate(env))
                except (ExpressionError, PrecisionError, EngineError) as e:
                    errors.append(f"Constraint {c.id}@{ctx}: {e}")
                    continue
                if not ok:
                    src = tuple(sorted({self.winners.get(k) for k in self._constraint_reads(c, ctx)
                                        if (self.winners.get(k) or "").startswith("PRS.")} - {None}))
                    conflict = {"kind": "constraint", "source": c.id, "target": None, "company_rules": src,
                                "fact": None, "month": ctx, "code": c.conflict_code}
                    self.conflicts[conflict_key(conflict)] = conflict
        return errors

    def _constraint_reads(self, c, ctx):
        keys = []
        for name in c.assertion.dependencies() | (c.condition.dependencies() if c.condition else set()):
            try:
                keys.append(self.key_of(name, ctx))
            except EngineError:
                pass
        return keys

    def run(self, outputs=None):
        """Evaluate output facts for every period and the year; then constraints."""
        res = Result(case_id=self.case.get("case_id", ""), omega=self.view.omega)
        errors = []
        period_out = [f.id for f in self.view.output_facts("period")] if outputs is None else \
            [n for n in outputs if self.view.facts.get(n) and self.view.facts[n].fact_scope == "period"]
        year_out = [f.id for f in self.view.output_facts("year")] if outputs is None else \
            [n for n in outputs if self.view.facts.get(n) and self.view.facts[n].fact_scope == "year"]
        for m in self.months:
            row = {}
            for name in period_out:
                row[name] = self._output(name, m, errors)
            res.periods[m] = row
        for name in year_out:
            res.year[name] = self._output(name, YEAR, errors)
        errors += self.check_constraints()
        res.conflicts = sorted(self.conflicts.values(), key=lambda c: str(conflict_key(c)))
        res.errors = errors
        res.winners = dict(self.winners)
        for p in self.case["periods"]:
            for bucket in ("income", "benefits", "hr"):
                for k, v in (p.get(bucket) or {}).items():
                    if v and (bucket, k) not in self.read_inputs:
                        self.warnings.append(f"UnreadInput({bucket}.{k})")
        res.warnings = sorted(set(self.warnings))
        res.trace = self.trace
        return res

    def _output(self, name, ctx, errors):
        try:
            if not self.active_rules(name, ctx):
                return None
            return self._value((name, ctx))
        except EngineError as e:
            msg = e.describe()
            if msg not in errors:
                errors.append(msg)
            return ERROR_VALUE


class _Env:
    __slots__ = ("ev", "ctx")

    def __init__(self, ev, ctx):
        self.ev, self.ctx = ev, ctx

    def fact(self, name):
        return self.ev.fact(name, self.ctx)

    def call(self, name, args):
        return self.ev.call(name, args, self.ctx)


class _Missing:
    pass


_MISSING = _Missing()


def _month_end(year, month):
    if month == 12:
        return date(year, 12, 31)
    from datetime import timedelta
    return date(year, month + 1, 1) - timedelta(days=1)


def _truth(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    if isinstance(v, (int, Fraction)):
        return v != 0
    raise ExpressionError(f"value {v!r} used as a condition is not boolean")


def evaluate_case(kb_or_view, case, omega=None, outputs=None, trace=False):
    """hasil(K, x, ., omega) for all periods of the case's tax year."""
    if isinstance(kb_or_view, KnowledgeBase):
        if omega is None:
            raise ValueError("omega is required when a KnowledgeBase is given")
        view = kb_or_view.view(omega)
    else:
        view = kb_or_view
    return Evaluator(view, case, trace=trace).run(outputs)
