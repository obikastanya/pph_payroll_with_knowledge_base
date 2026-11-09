"""Verification gates G1-G6 and the generated test cases they run on.

G1 schema, application and SHACL; G2 verbatim quotes and numbers; G3 static consistency; G4 behaviour on generated
cases (no new engine errors, no change before the start of effect); G5 effect of every element; G6 case-data inputs
that exist in the payroll data. A failure returns messages that the repair round shows to the model.
"""
import ast
import itertools
import random
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from fractions import Fraction

from . import config, consistency, graph
from .documents import find_quote, normalize, registry
from .engine import evaluate_case
from .expr import Expression
from .kb import Parameter, Rule, TableVersion, Tombstone, UpdateError, apply_delta


# ====================================================================================================================
# Generated test cases (S^G in the paper)
# ====================================================================================================================
PTKP_ALL = ("TK/0", "TK/1", "TK/2", "TK/3", "K/0", "K/1", "K/2", "K/3")
METHODS = ("gross", "gross_up", "employer_borne")
DEFAULT_SALARIES = (4_800_000, 9_000_000, 16_000_000, 45_000_000)
MAX_CASES = 300
MAX_COMBOS = 6000           # 3-way coverage only when it has at most this many value combinations
FILL = 250                  # random combinations are added until the generated set has this many cases
MAX_THRESHOLDS = 24
MARKER = 7                  # amount of the other_regular income that marks a generated case
YEARS = (2013, config.LAST_TAX_YEAR)      # tax years of the generated cases
EARLIEST = date(2009, 1, 1)               # start of the starting knowledge base


@dataclass
class SGSet:
    cases: list          # case dicts
    omegas: tuple        # (issued - 1 day, issued)
    start: date          # start of effect of the whole update


TABLE_FUNCS = ("lookup", "in_table", "table_attr", "bracket")


NUMERIC_DEFAULT = 5_000_000      # amount given to a case attribute that is used in arithmetic and has no literal


def _attrs(expr_texts, tables=None, numeric=None, none_compared=None):
    """(function, attribute) -> literals compared with it, for employee()/employer()/case()/hr() reads. When the
    attribute is the key argument of a table function, its table name is recorded in tables[(function, attribute)]."""
    out = {}
    tables = {} if tables is None else tables
    numeric = set() if numeric is None else numeric
    none_compared = set() if none_compared is None else none_compared
    for text in expr_texts:
        try:
            tree = ast.parse(text, mode="eval")
        except SyntaxError:
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in (
                    "employee", "employer", "case", "hr") and n.args and isinstance(n.args[0], ast.Constant):
                out.setdefault((n.func.id, n.args[0].value), set())
            if isinstance(n, ast.BinOp):
                for side in (n.left, n.right):
                    if (isinstance(side, ast.Call) and isinstance(side.func, ast.Name)
                            and side.func.id in ("employee", "employer", "case") and side.args
                            and isinstance(side.args[0], ast.Constant)):
                        numeric.add((side.func.id, side.args[0].value))
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in TABLE_FUNCS
                    and len(n.args) >= 2 and isinstance(n.args[0], ast.Constant)):
                a = n.args[1]
                if (isinstance(a, ast.Call) and isinstance(a.func, ast.Name)
                        and a.func.id in ("employee", "employer", "case", "hr") and a.args
                        and isinstance(a.args[0], ast.Constant)):
                    tables[(a.func.id, a.args[0].value)] = (n.func.id, n.args[0].value)
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("startswith", "endswith")
                    and len(n.args) == 2 and isinstance(n.args[1], ast.Constant)):
                # a text prefix test: the attribute is text and takes the prefix as a value (e.g. a grade 'A')
                for s in ast.walk(n.args[0]):
                    if (isinstance(s, ast.Call) and isinstance(s.func, ast.Name)
                            and s.func.id in ("employee", "employer", "case") and s.args
                            and isinstance(s.args[0], ast.Constant)):
                        out.setdefault((s.func.id, s.args[0].value), set()).add(n.args[1].value)
            if isinstance(n, ast.Compare):
                sides = [n.left] + list(n.comparators)
                calls = [s for s in sides if isinstance(s, ast.Call) and isinstance(s.func, ast.Name)
                         and s.func.id in ("employee", "employer", "case", "hr") and s.args
                         and isinstance(s.args[0], ast.Constant)]
                consts = [s.value for s in sides if isinstance(s, ast.Constant)]
                for c in calls:
                    out.setdefault((c.func.id, c.args[0].value), set()).update(
                        x for x in consts if x is not None)
                    if any(x is None for x in consts):
                        none_compared.add((c.func.id, c.args[0].value))
    return out


def _numbers(text):
    out = set()
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError:
        return out
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and type(n.value) is int and n.value >= 100_000:
            out.add(n.value)
    return out


def _scaled_fact(node, view):
    """(fact, factor) when node is a money period fact, optionally multiplied or divided by a constant."""
    if isinstance(node, ast.Name) and _is_money_period(view, node.id):
        return node.id, Fraction(1)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mult, ast.Div)):
        a, b = node.left, node.right
        if isinstance(a, ast.Name) and isinstance(b, ast.Constant) and isinstance(b.value, int) and b.value:
            if _is_money_period(view, a.id):
                return a.id, Fraction(b.value) if isinstance(node.op, ast.Mult) else Fraction(1, b.value)
        if isinstance(b, ast.Name) and isinstance(a, ast.Constant) and isinstance(a.value, int) and isinstance(
                node.op, ast.Mult) and _is_money_period(view, b.id):
            return b.id, Fraction(a.value)
    return None


def _bound_value(node, view, start):
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "param" and node.args
            and isinstance(node.args[0], ast.Constant)):
        vals = [p.value for p in view.params.get(node.args[0].value, ()) if p.valid_on(start)
                and isinstance(p.value, int)]
        return vals[-1] if vals else None
    return None


def _thresholds(kb2, delta_records, view, start):
    """(fact, target value of the fact) pairs: comparisons of a money period fact (possibly times a constant) with a
    constant or a money parameter, and bounds of bracket/progressive tables the Delta adds or changes, watched on the
    amount passed to the table function (gross_income when unknown)."""
    out = set()
    table_amount = {}
    for r in delta_records:
        for e in (getattr(r, "expression", None), getattr(r, "condition", None), getattr(r, "assertion", None)):
            if e is None:
                continue
            tree = ast.parse(e.text, mode="eval")
            for n in ast.walk(tree):
                if isinstance(n, ast.Compare) and len(n.ops) == 1:
                    left, right = n.left, n.comparators[0]
                    for a, b in ((left, right), (right, left)):
                        sf, bound = _scaled_fact(a, view), _bound_value(b, view, start)
                        if sf and bound and bound >= 100_000:
                            out.add((sf[0], int(Fraction(bound) / sf[1])))
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("bracket", "progressive")
                        and isinstance(n.args[0], ast.Constant)):
                    amount = n.args[-1]
                    if isinstance(amount, ast.Name) and _is_money_period(view, amount.id):
                        table_amount[n.args[0].value] = amount.id
    for r in delta_records:
        if isinstance(r, Parameter) and r.value_type == "money" and isinstance(r.value, int) and r.value >= 100_000:
            for rule in view.rules.values():
                for e in (rule.expression, rule.condition):
                    if e is not None and r.name in e.params:
                        for f, t in _thresholds(kb2, [rule], view, start):
                            out.add((f, t))
        if isinstance(r, TableVersion) and r.table_kind in ("bracket", "progressive"):
            fact = table_amount.get(r.name)
            if fact is None:
                for rule in view.rules.values():
                    if r.name in rule.expression.tables:
                        tree = ast.parse(rule.expression.text, mode="eval")
                        for n in ast.walk(tree):
                            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                                    and n.func.id in ("bracket", "progressive") and isinstance(n.args[-1], ast.Name)):
                                fact = n.args[-1].id
            fact = fact if fact and _is_money_period(view, fact) else "gross_income"
            for row in r.rows:
                for k in ("lower", "upper"):
                    if isinstance(row.get(k), int) and row[k] > 0:
                        out.add((fact, row[k]))
    return sorted(out)


def _is_money_period(view, name):
    f = view.facts.get(name)
    return f is not None and f.fact_type == "money" and f.fact_scope == "period"


def _case(year, start, end, salary, ptkp="TK/0", method="gross", attrs=None, variant="base", s_month=1,
          benefit_kinds=(), case_id="SG", policy=None):
    employee = {"ptkp_status": ptkp, "sex": "M", "tax_id_valid": True}
    employer = {"klu": None, "jkk_risk_group": "very_low", "jkk_relief_eligible": False, "policy": policy}
    case_extra, hr = {}, {}
    for (fn, name), v in (attrs or {}).items():
        if fn == "employee":
            employee[name] = v
        elif fn == "employer":
            employer[name] = v
        elif fn == "hr":
            hr[name] = v
        else:
            case_extra[name] = v
    periods = []
    for m in range(start, end + 1):
        income = {"base_salary": salary, "fixed_allowance": salary // 10, "other_regular": MARKER}
        benefits = {}
        zakat = 0
        if m == s_month and variant == "irregular":
            income["thr"] = salary
            income["bonus"] = salary // 2
        if m == end and variant == "irregular_final":      # large irregular income in the final period
            income["thr"] = salary
            income["bonus"] = salary * 4
        if variant == "benefits":
            for k in benefit_kinds:
                benefits[k] = 2_500_000
        if variant == "zakat":
            zakat = salary * 25 // 1000
        p = {"month": m, "income": income, "benefits": benefits, "zakat": zakat}
        if hr:
            p["hr"] = dict(hr)
        periods.append(p)
    case = {"case_id": case_id, "tax_year": year, "method": method, "employee": employee, "employer": employer,
            "employment": {"start_month": start, "end_month": end}, "periods": periods}
    case.update(case_extra)
    return case


def _find_salary(kb2, omega, year, month, fact, target):
    """Base salary such that fact(month) is as close as possible to target from below and above (bisection)."""
    def value(s):
        c = _case(year, month, min(12, month + 1), s)
        r = evaluate_case(kb2, c, omega, outputs=[fact])
        v = (r.periods.get(month) or {}).get(fact)
        return v if isinstance(v, (int, Fraction)) else None
    lo, hi = 0, max(target * 2, 1_000_000)
    v_hi = value(hi)
    if v_hi is None or v_hi < target:
        return None
    for _ in range(40):
        if hi - lo <= 1:
            break
        mid = (lo + hi) // 2
        v = value(mid)
        if v is None:
            return None
        if v < target:
            lo = mid
        else:
            hi = mid
    return lo, hi


def generate(base, kb2, delta, s_delta, issued, relevance=None, seed=20261027, starts=None, omega=None):
    """Generated test cases for one draft. base: the knowledge base before the update; kb2: with the update;
    s_delta: start of effect of the update; issued: issue date of the document; starts: start of effect per element
    id (gates.effect_start). omega is the knowledge date the cases are evaluated at: the issue date for
    regulation updates, the acquisition date of the full regulation chain for company policies."""
    rng = random.Random(seed)
    omega_eval = omega or issued
    view = kb2.view(omega_eval)
    policies = sorted({e.get("policy") for e in delta["add"] + delta["change"]
                       if e.get("kind") == "rule" and e.get("layer") == "company" and e.get("policy")})
    policy = policies[0] if len(policies) == 1 else (policies or None)
    ids = {e["id"] for e in delta["add"] + delta["change"]}
    recs = [r for r in kb2.records if r.update_id == kb2.updates[-1].update_id and r.id in ids]
    texts = [x.text for r in recs for x in (getattr(r, "expression", None), getattr(r, "condition", None),
                                            getattr(r, "assertion", None)) if x is not None]
    # rules of K' that produce the same facts as the update's rules compete with them (e.g. mandatory DTP rules
    # against a company rule that withholds the DTP): their case attributes and benefit kinds are varied too
    produced = {r.produces for r in recs if isinstance(r, Rule)}
    competitors = [r for r in view.rules.values() if r.produces in produced and r.id not in ids]
    # ... and the rules those competitors depend on, up to three steps (e.g. the KLU read by DTP eligibility)
    frontier, seen_rules = set(), {r.id for r in competitors}
    for r in competitors:
        frontier |= {f for x in (r.expression, r.condition) if x is not None for f in x.dependencies()}
    for _ in range(3):
        nxt = set()
        for r in view.rules.values():
            if r.produces in frontier and r.id not in seen_rules and r.layer == "regulation":
                seen_rules.add(r.id)
                competitors.append(r)
                nxt |= {f for x in (r.expression, r.condition) if x is not None for f in x.dependencies()}
        frontier = nxt
    texts += [x.text for r in competitors for x in (r.expression, r.condition) if x is not None]
    # time
    start = s_delta or issued
    years = {min(max(start.year, YEARS[0]), YEARS[1])}
    for r in recs:
        if r.valid_until:
            years.add(min(max(r.valid_until.year, YEARS[0]), YEARS[1]))
        else:
            years.add(min(start.year + 1, YEARS[1]))
    eff = None
    if relevance and relevance.get("effective_from"):
        try:
            eff = date.fromisoformat(relevance["effective_from"])
            years.add(min(max(eff.year, YEARS[0]), YEARS[1]))
        except ValueError:
            eff = None
    s_month = start.month
    # joining and leaving around the start of every element (not only the earliest), up to three distinct months
    months = [s_month] + sorted({d.month for d in (starts or {}).values() if d and d.year == start.year} - {s_month})
    patterns = [("full", 1, 12)]
    for m in months[:3]:
        patterns += [("join", m, 12), ("leave", 1, min(12, m + 1))]
    # attributes
    attr_values = {}
    table_of = {}
    numeric, none_cmp = set(), set()
    for key, lits in _attrs(texts, table_of, numeric, none_cmp).items():
        fn, name = key
        if name == "ptkp_status":
            continue
        if key in table_of:                    # key of a table: its keys (and one outside key for set tables)
            func, tname = table_of[key]
            versions = [t for t in view.tables.get(tname, ()) if t.valid_on(start)] or view.tables.get(tname, [])
            keys = sorted({_typed(r.get("key")) for t in versions for r in t.rows if r.get("key") is not None},
                          key=str)
            if keys:
                sample = keys if len(keys) <= 6 else [keys[0], keys[-1]] + rng.sample(keys[1:-1], 4)
                attr_values[key] = sample + (["99999"] if func == "in_table" else [])
            continue
        vals = sorted({v for v in lits if not isinstance(v, bool)}, key=str)
        if any(isinstance(v, bool) for v in lits):
            attr_values[key] = [True, False]
        elif vals and all(isinstance(v, (int, float)) for v in vals):
            attr_values[key] = sorted({v for x in vals for v in (x - 1, x, x + 1)})
        elif vals:
            attr_values[key] = vals + (["OTHER"] if isinstance(vals[0], str) else [])
        elif fn == "hr":                      # HR quantities (hours, days, months): none, some, many
            attr_values[key] = [0, 3, 12, 40]
        elif key in numeric:                  # an amount the case must state (e.g. a regional minimum wage)
            attr_values[key] = [NUMERIC_DEFAULT]
        elif key in none_cmp:                 # optional data compared with None: absent, or a mid-year month
            attr_values[key] = [None, 6]
        # other attributes without literals or table use keep the default case value
    for r in recs:
        if isinstance(r, TableVersion) and r.table_kind == "set":
            keys = sorted({row["key"] for row in r.rows})
            old = set()
            for t in base.view(issued).tables.get(r.name, ()):
                old |= {row["key"] for row in t.rows}
            changed_keys = sorted((set(keys) ^ old) if old else set())
            # keys the update adds or drops carry its effect; then a few common keys and one key outside the table
            sample = (rng.sample(changed_keys, min(4, len(changed_keys))) if changed_keys else [])
            common = [k for k in keys if k not in sample]
            sample += common if len(common) <= 3 else [common[0], common[-1]] + rng.sample(common[1:-1], 1)
            attr_values[("employer", "klu")] = sample + ["99999"]
    ptkps = sorted({c for t in texts for c in PTKP_ALL if f"'{c}'" in t}) or ["TK/0", "K/1", "K/3"]
    benefit_kinds = sorted({a for t in texts for a in _benefit_kinds(t)})
    variants = ["base", "irregular", "irregular_final", "zakat"] + (["benefits"] if benefit_kinds else [])
    # salaries at thresholds
    omega = omega_eval
    thresholds = _thresholds(kb2, recs, view, start)
    if len(thresholds) > MAX_THRESHOLDS:
        thresholds = sorted(rng.sample(thresholds, MAX_THRESHOLDS))
    salaries = set(DEFAULT_SALARIES)
    month = s_month if s_month < 12 else 11
    for fact, b in thresholds:
        found = _find_salary(kb2, omega, min(max(start.year, YEARS[0]), YEARS[1]), month, fact, b)
        if found:
            salaries |= {found[0], found[1], found[1] + 1}
    salaries = sorted(salaries)
    # combinations: pairwise over small dimensions, then every value of large dimensions at least once
    small = {"year": sorted(years), "pattern": patterns, "ptkp": ptkps, "method": list(METHODS),
             "variant": variants}
    small.update({k: v for k, v in attr_values.items() if len(v) <= 6})
    large = {"salary": salaries}
    large.update({k: v for k, v in attr_values.items() if len(v) > 6})
    rows = _covering(small, rng, 3) if _combos(small, 3) <= MAX_COMBOS else None
    if rows is None or len(rows) > MAX_CASES // 2:      # 3-way too large: pairwise
        rows = _covering(small, rng, 2)
    out = []
    for i, row in enumerate(rows):
        row = dict(row)
        for k, vals in large.items():
            row[k] = vals[i % len(vals)]
        out.append(row)
    # pairwise coverage of all dimensions together, so that large dimensions (salaries at thresholds, table keys)
    # meet every value of the others
    alldims = dict(small)
    alldims.update(large)
    seen = {_row_key(r) for r in out}
    for row in _covering(alldims, rng, 2):
        if len(out) >= MAX_CASES:
            break
        if _row_key(row) not in seen:
            seen.add(_row_key(row))
            out.append(row)
    # rules that act in the final period: leavers with large irregular income in their last month, for every salary
    # level and every value of the largest attribute dimension (final-period effects need this combination)
    final_starts = sorted({(starts or {}).get(r.id) or start for r in recs
                           if any("is_final_period" in x.text for x in (getattr(r, "expression", None),
                                                                         getattr(r, "condition", None)) if x)})
    for su in final_starts:
        attr_dims = sorted(((k, v) for k, v in alldims.items() if isinstance(k, tuple)), key=lambda kv: -len(kv[1]))
        widest = attr_dims[0] if attr_dims else None
        leave = ("leave", 1, min(12, su.month + 1))
        for sal in salaries:
            for val in (widest[1] if widest else [None]):
                if len(out) >= MAX_CASES:
                    break
                row = {k: v[0] for k, v in alldims.items()}
                row.update({"pattern": leave, "variant": "irregular_final", "salary": sal,
                            "year": min(max(su.year, YEARS[0]), YEARS[1])})
                for k, v in alldims.items():          # boolean attributes on their first literal (usually True)
                    if isinstance(k, tuple) and v and isinstance(v[0], bool):
                        row[k] = v[0]
                if widest:
                    row[widest[0]] = val
                if _row_key(row) not in seen:
                    seen.add(_row_key(row))
                    out.append(row)
    # eligibility usually hinges on an attribute value and a salary level together (e.g. a KLU in a facility table
    # and income under a cap): every value of the widest attribute dimension with every salary, full year
    attr_dims = sorted(((k, v) for k, v in alldims.items() if isinstance(k, tuple)), key=lambda kv: -len(kv[1]))
    if attr_dims:
        wkey, wvals = attr_dims[0]
        for val in wvals:
            for sal in salaries:
                if len(out) >= MAX_CASES:
                    break
                row = {k: v[0] for k, v in alldims.items()}
                for k, v in alldims.items():
                    if isinstance(k, tuple) and v and isinstance(v[0], bool):
                        row[k] = v[0]
                row.update({"pattern": patterns[0], "variant": "base", "salary": sal, "year": min(years), wkey: val})
                if _row_key(row) not in seen:
                    seen.add(_row_key(row))
                    out.append(row)
    # seeded random combinations up to FILL cases, for effects that need more than three values together
    tries = 0
    while len(out) < FILL and tries < FILL * 5:
        tries += 1
        row = {k: rng.choice(v) for k, v in alldims.items()}
        if _row_key(row) not in seen:
            seen.add(_row_key(row))
            out.append(row)
    out = out[:MAX_CASES]
    cases = []
    for n, row in enumerate(out):
        _, a, b = row["pattern"]
        attrs = {k: row[k] for k in attr_values}
        cases.append(_case(row["year"], a, b, row["salary"], row["ptkp"], row["method"], attrs, row["variant"],
                           s_month, benefit_kinds, case_id=f"SG-{n:03d}", policy=policy))
    return SGSet(cases, (omega_eval - timedelta(days=1), omega_eval), start)


def _typed(v):
    """Table keys are stored as text; a key made of digits is given back as a number (e.g. years of service)."""
    return int(v) if isinstance(v, str) and v.isdigit() and not v.startswith("0") else v


def _row_key(row):
    return repr(sorted((str(k), repr(v)) for k, v in row.items()))


def _benefit_kinds(text):
    out = set()
    tree = ast.parse(text, mode="eval")
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "benefit" and n.args:
            if isinstance(n.args[0], ast.Constant):
                out.add(n.args[0].value)
    return out


def _combos(dims, t):
    sizes = [len(v) for v in dims.values()]
    total = 0
    for idx in itertools.combinations(range(len(sizes)), min(t, len(sizes))):
        n = 1
        for i in idx:
            n *= sizes[i]
        total += n
    return total


def _covering(dims, rng, t):
    """Greedy t-way covering array over the given dimensions (every combination of t values appears)."""
    names = list(dims)
    t = min(t, len(names))
    uncovered = set()
    for idx in itertools.combinations(range(len(names)), t):
        for vals in itertools.product(*(range(len(dims[names[i]])) for i in idx)):
            uncovered.add(tuple(zip(idx, vals)))
    rows = []
    while uncovered and len(rows) < MAX_CASES:
        best, best_cov = None, -1
        target = next(iter(uncovered))
        for _ in range(30):
            cand = [rng.randrange(len(dims[n])) for n in names]
            for i, v in target:
                cand[i] = v
            cov = sum(1 for combo in uncovered if all(cand[i] == v for i, v in combo))
            if cov > best_cov:
                best, best_cov = cand, cov
        uncovered = {combo for combo in uncovered if not all(best[i] == v for i, v in combo)}
        rows.append({n: dims[n][i] for n, i in zip(names, best)})
    if not rows:
        rows.append({n: dims[n][0] for n in names})
    return rows


# ====================================================================================================================
# Gates
# ====================================================================================================================
MONTHS = {"januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6, "juli": 7, "agustus": 8,
          "september": 9, "oktober": 10, "november": 11, "desember": 12}
MIN_QUOTE = 20


@dataclass
class GateResult:
    gate: str
    passed: bool
    messages: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def summary(self):
        return "pass" if self.passed else "fail: " + "; ".join(self.messages)[:500]


def month_end(d):
    nxt = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return nxt - timedelta(days=1)


# ---------------------------------------------------------------------- G1
def g1(base, delta, documents=None):
    """(GateResult, K' or None)."""
    try:
        kb2 = apply_delta(base, delta)
    except (UpdateError, ValueError) as e:
        return GateResult("G1", False, [f"application: {e}"]), None
    violations = graph.validate(kb2, documents)
    if violations:
        return GateResult("G1", False, [f"SHACL {eid}: {msg}" for eid, msg in violations[:20]]), kb2
    return GateResult("G1", True), kb2


# ---------------------------------------------------------------------- G2
def _number_forms(n):
    s = f"{n:,}".replace(",", ".")
    return {s, str(n)}


def _rate_forms(v):
    """Notations of a fraction: p% and p persen with a decimal comma for p = 100 v, and the decimal itself."""
    out = set()
    pct = v * 100
    for x, suffix in ((pct, "%"), (pct, " persen"), (v, "")):
        txt = _decimal(x)
        if txt is None:
            continue
        out.add(txt.replace(".", ",") + suffix)
        if suffix == "" and "," not in txt.replace(".", ","):
            continue
    return {normalize(o) for o in out}


def _decimal(x):
    x = Fraction(x)
    d, k = x.denominator, 0
    while d % 2 == 0 or d % 5 == 0:
        d //= 2 if d % 2 == 0 else 5
        k += 1
    if d != 1 or k > 8:
        return None
    s = f"{x.numerator * 10 ** k // x.denominator:0{k + 1}d}" if k else str(x.numerator)
    if k:
        s = s[:-k] + "." + s[-k:]
    return s.rstrip("0").rstrip(".") if "." in s else s


def _constants(text):
    """Numbers written in an expression: integers, dec('...') values, and constant quotients (5 / 100)."""
    out = []
    tree = ast.parse(text, mode="eval")
    skip = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "dec" and n.args:
            out.append(Fraction(n.args[0].value))
            skip.add(id(n.args[0]))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "round" and len(n.args) == 3:
            skip.add(id(n.args[1]))          # rounding unit
        elif (isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div) and isinstance(n.left, ast.Constant)
              and isinstance(n.right, ast.Constant) and isinstance(n.left.value, int)
              and isinstance(n.right.value, int) and n.right.value):
            out.append(Fraction(n.left.value, n.right.value))
            skip |= {id(n.left), id(n.right)}
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and type(n.value) is int and id(n) not in skip:
            out.append(Fraction(n.value))
    return out


DIGIT_WORDS = {"nol": "0", "satu": "1", "dua": "2", "tiga": "3", "empat": "4", "lima": "5", "enam": "6",
               "tujuh": "7", "delapan": "8", "sembilan": "9"}
_WORD_RATE = re.compile(r"\b((?:" + "|".join(DIGIT_WORDS) + r")(?: (?:" + "|".join(DIGIT_WORDS)
                        + r"))*) koma ((?:" + "|".join(DIGIT_WORDS) + r")(?: (?:" + "|".join(DIGIT_WORDS)
                        + r"))*) persen")
_INT = re.compile(r"(?<![\d.,])(\d{1,3}(?:\.\d{3})+|\d{3,})(?:,\d+)?(?![\d.])")
_PCT = re.compile(r"(?<![\d.,])(\d+(?:,\d+)?)(?:%| persen)")


def ocr_digits(q):
    """Letters that OCR puts in amounts: l for 1 and o for 0 next to digits or after rp ("rpl.500.000" = 1.500.000)."""
    q = re.sub(r"(?<=rp)[l](?=[\d.,lo])", "1", q)
    for _ in range(3):
        q = re.sub(r"(?<=[\d.,])[l](?=[\d.,lo])", "1", q)
        q = re.sub(r"(?<=[\d.,])[o](?=[\d.,lo])", "0", q)
        q = re.sub(r"(?<=rp1)[o]", "0", q)
    return q


_DECIMAL = re.compile(r"(?<![\d.,])(\d{1,2})[.,](\d{1,3})(?![\d.,])")
_UNITS = {"satu": 1, "dua": 2, "tiga": 3, "empat": 4, "lima": 5, "enam": 6, "tujuh": 7, "delapan": 8,
          "sembilan": 9, "sepuluh": 10, "sebelas": 11, "seratus": 100}
_SCALE = {"ribu": 1000, "juta": 10 ** 6, "miliar": 10 ** 9, "milyar": 10 ** 9}
_NUMWORD = re.compile(r"\b(?:(?:" + "|".join(list(_UNITS) + list(_SCALE) + ["seribu", "sejuta", "belas", "puluh",
                                                                            "ratus"]) + r")\b ?)+")


def words_to_int(text):
    """Integer written in Indonesian words ("dua puluh tiga ribu" = 23000), or None."""
    total, group, part, seen = 0, 0, 0, False
    for w in text.split():
        seen = True
        if w in ("sepuluh", "sebelas", "seratus"):
            group += _UNITS[w]
        elif w in _UNITS:
            part += _UNITS[w]
        elif w == "belas":
            group += part + 10
            part = 0
        elif w == "puluh":
            group += part * 10
            part = 0
        elif w == "ratus":
            group += part * 100
            part = 0
        elif w == "seribu":
            total += 1000
        elif w == "sejuta":
            total += 10 ** 6
        elif w in _SCALE:
            total += ((group + part) or 1) * _SCALE[w]
            group = part = 0
        else:
            return None
    return total + group + part if seen else None


def quoted_numbers(quotes_norm):
    """Integers (>= 100) and rates written in the quotes: digits in Indonesian notation, percentages, decimal
    percentages spelled with digit words ("nol koma dua empat persen" = 0,24%), amounts in words ("dua puluh tiga
    ribu rupiah"), and short decimals that are not thousands groups ("1.6", "1,25") read as factors."""
    ints, rates = set(), set()
    for q in (ocr_digits(x) for x in quotes_norm):
        for m in _INT.finditer(q):
            ints.add(int(m.group(1).replace(".", "")))
        for m in _PCT.finditer(q):
            rates.add(Fraction(m.group(1).replace(",", ".")) / 100)
        for m in _WORD_RATE.finditer(q):
            a = "".join(DIGIT_WORDS[w] for w in m.group(1).split())
            b = "".join(DIGIT_WORDS[w] for w in m.group(2).split())
            rates.add(Fraction(f"{a}.{b}") / 100)
        for m in _DECIMAL.finditer(q):
            point_thousands = q[m.start(2) - 1] == "." and len(m.group(2)) == 3
            if not point_thousands and not (q[m.end():m.end() + 1] == "%" or q[m.end():m.end() + 7] == " persen"):
                rates.add(Fraction(f"{m.group(1)}.{m.group(2)}"))
        for m in _NUMWORD.finditer(q):
            n = words_to_int(m.group(0).strip())
            if n is not None and n >= 100:
                ints.add(n)
    return ints, rates


def _grounded(value, quotes_norm, numbers=None):
    """A number is grounded when it is written in a quote of the element, or derived from written numbers by the
    arithmetic regulations state in words: sums of components (a + k*b, a + b + k*c, k <= 12, as in PTKP tables),
    a share of a written rate (r1 * r2), or the remainder of a written share (1 - r)."""
    v = Fraction(value)
    if v.denominator == 1:
        n = abs(v.numerator)
        if n < 100 or n == 1000:
            return True
        if any(f in q for f in _number_forms(n) for q in quotes_norm):
            return True
    elif any(f in q for f in _rate_forms(abs(v)) for q in quotes_norm):
        return True
    ints, rates = numbers if numbers is not None else quoted_numbers(quotes_norm)
    v = abs(v)
    if v in rates or v in ints:
        return True
    if v.denominator == 1 and (v in (100, 10000) or any(
            Fraction(v, 10 ** k) in rates or Fraction(v, 10 ** k) / 100 in rates for k in range(1, 5))):
        return True                    # a written rate as integer over a power of ten: 1,27% -> 127 / 10000
    if v.denominator == 1:
        g = sorted(ints)
        for b in g:
            for k in range(1, 13):
                if v - k * b in ints or v == k * b:
                    return True
                for a in g:
                    if v - a - k * b in ints:
                        return True
        return False
    rl = list(rates)
    return any(v == r1 * r2 for r1 in rl for r2 in rl) or any(v == 1 - r for r in rl)


def _element_numbers(e):
    nums = []
    for k in ("expression", "condition", "assertion"):
        if e.get(k):
            try:
                nums += _constants(e[k])
            except (SyntaxError, ValueError):
                pass
    if e.get("kind") == "parameter" and e.get("value_type") in ("money", "int", "rate", "exact"):
        try:
            nums.append(Fraction(str(e["value"])))
        except (ValueError, ZeroDivisionError):
            pass
    for r in e.get("rows") or []:
        for k in ("lower", "upper", "value", "rate"):
            v = r.get(k)
            if v is None or isinstance(v, bool):
                continue
            try:
                nums.append(Fraction(str(v)))
            except (ValueError, ZeroDivisionError):
                pass
    return nums


def _year(tok):
    """A four-character year token; OCR letters o (0) and l, i, t (1) are read as digits."""
    tok = tok.replace("o", "0").replace("l", "1").replace("i", "1").replace("t", "1")
    return int(tok) if re.fullmatch(r"(19|20)\d\d", tok) else None


def date_anchors(quotes_norm, issued):
    """Dates a set of quotes supports: (possible valid_from dates, possible valid_until dates)."""
    vf, vu = set(), set()
    years = set()
    for q in quotes_norm:
        for m in re.finditer(r"\b(\d{1,2}) (" + "|".join(MONTHS) + r") ([0-9olit]{4})\b", q):
            y = _year(m.group(3))
            if y:
                d = date(y, MONTHS[m.group(2)], int(m.group(1)))
                vf.add(d)
                vu.add(d)
                vu.add(d - timedelta(days=1))
        for m in re.finditer(r"\b(" + "|".join(MONTHS) + r") ([0-9olit]{4})\b", q):
            y = _year(m.group(2))
            if y:
                years.add(y)
                first = date(y, MONTHS[m.group(1)], 1)
                vf.add(first)
                vu.add(month_end(first))
        for m in re.finditer(r"\bdengan (?:masa pajak |bulan |iuran \w+ bulan )?(" + "|".join(MONTHS)
                             + r") ([0-9olit]{4})\b", q):
            y = _year(m.group(2))
            if y:                              # "(sampai) dengan <month> <year>": old rule ends, new one starts after
                first = date(y, MONTHS[m.group(1)], 1)
                vf.add(month_end(first) + timedelta(days=1))
        for m in re.finditer(r"\b(tahun pajak|tahun anggaran) ([0-9olit]{4})\b", q):
            y = _year(m.group(2))
            if y:
                years.add(y)
                vf.add(date(y, 1, 1))
                vu.add(date(y, 12, 31))
        if re.search(r"berlaku pada tanggal (diundangkan|ditetapkan)", q) and issued:
            vf.add(date(issued.year, issued.month, 1))
            nxt = date(issued.year + (issued.month == 12), issued.month % 12 + 1, 1)
            vf.add(nxt)
    for q in quotes_norm:                      # month names without a year take a year from another quote
        for m in re.finditer(r"\b(" + "|".join(MONTHS) + r")\b(?! [0-9olit]{4})", q):
            for y in years:
                first = date(y, MONTHS[m.group(1)], 1)
                vf.add(first)
                vu.add(month_end(first))
    return vf, vu


def g2(base, delta, event_docs, issued):
    msgs = []
    reg = registry()
    old = {}
    for e in delta["change"]:
        prev = [r for r in base.history(e["id"]) if not isinstance(r, Tombstone)]
        old[e["id"]] = prev[-1] if prev else None
    all_vf = set()
    all_vu = set()
    elements = delta["add"] + delta["change"]
    for e in elements:
        qn = [normalize(s["quote"]) for s in e.get("source", [])]
        a, b = date_anchors(qn, issued)
        all_vf |= a
        all_vu |= b
    for e in elements + delta["remove"]:
        eid = e["id"]
        sources = e.get("source", [])
        own = False
        for s in sources:
            if s["document"] not in reg:
                msgs.append(f"{eid}: unknown document {s['document']}")
                continue
            if len(normalize(s["quote"])) < MIN_QUOTE:
                msgs.append(f"{eid}: quote shorter than {MIN_QUOTE} characters: {s['quote']!r}")
                continue
            if find_quote(s["document"], s["quote"]) is None:
                msgs.append(f"{eid}: quote not found in {s['document']}: {s['quote'][:80]!r}")
                continue
            own |= s["document"] in event_docs
        if not own:
            msgs.append(f"{eid}: no verified quote from the document of this event")
        if e.get("recorded_on") != issued.isoformat():
            msgs.append(f"{eid}: recorded_on {e.get('recorded_on')} differs from the issue date {issued}")
        if e in delta["remove"]:
            continue
        qn = [normalize(s["quote"]) for s in sources]
        prev = old.get(eid)
        prev_consts = set()
        if prev is not None:
            for k in ("expression", "condition"):
                x = getattr(prev, k, None)
                if isinstance(x, Expression):
                    prev_consts |= set(_constants(x.text))
            if getattr(prev, "value", None) is not None and not isinstance(prev.value, (str, bool)):
                prev_consts.add(Fraction(prev.value))
        numbers = quoted_numbers(qn)
        for v in _element_numbers(e):
            if v in prev_consts or _grounded(v, qn, numbers):
                continue
            msgs.append(f"{eid}: number {_decimal(v) or v} is not in a quote of this element")
        vf_q, vu_q = date_anchors(qn, issued)
        for k, anchors, also in (("valid_from", vf_q, set()), ("valid_until", vu_q, {d - timedelta(days=1)
                                                                                     for d in all_vf})):
            text = e.get(k)
            if not text:
                continue
            d = date.fromisoformat(text)
            if prev is not None and getattr(prev, k) == d:
                continue
            if d not in anchors and d not in also:
                msgs.append(f"{eid}: {k} {text} is not supported by a quote of this element")
    return GateResult("G2", not msgs, msgs)


# ---------------------------------------------------------------------- G3
def g3(kb2, omega, policies=(), adopted=()):
    rep = consistency.check(kb2, omega, policies, adopted)
    errs = [f"{f.kind} {', '.join(f.ids)} {f.fact}: {f.detail}" for f in rep.errors]
    warns = [f"{f.kind} {', '.join(f.ids)} {f.fact}: {f.detail}" for f in rep.warnings]
    return GateResult("G3", not errs, errs[:20], warns)


# ---------------------------------------------------------------------- start of effect
def effect_start(base, delta):
    """Start of effect per element id (the first month whose result the element can change) and of the update."""
    out = {}
    content_keys = ("expression", "condition", "value", "rows", "rows_ref", "layer", "modality", "scope",
                    "overrides", "assertion", "produces", "fixed_point", "table_kind", "name")
    for e in delta["add"]:
        if e["kind"] == "fact":                # vocabulary: no validity, no effect of its own
            continue
        out[e["id"]] = _d(e.get("valid_from")) or EARLIEST
    for e in delta["change"]:
        if e["kind"] == "fact":
            continue
        prev = [r for r in base.history(e["id"]) if not isinstance(r, Tombstone)]
        p = prev[-1] if prev else None
        new_vf, new_vu = _d(e.get("valid_from")), _d(e.get("valid_until"))
        if p is None:
            out[e["id"]] = new_vf or EARLIEST
            continue
        old_vf, old_vu = p.valid_from, p.valid_until
        from .kb import record_to_json
        old_json = record_to_json(p)
        content_changed = any(_norm(old_json.get(k)) != _norm(e.get(k))
                              for k in content_keys if k in e or k in old_json)
        if content_changed:
            out[e["id"]] = min(x for x in (old_vf, new_vf) if x) if (old_vf or new_vf) else EARLIEST
        else:
            out[e["id"]] = _sym_diff_start(old_vf, old_vu, new_vf, new_vu)
    for e in delta["remove"]:
        prev = [r for r in base.history(e["id"]) if not isinstance(r, Tombstone)]
        out[e["id"]] = (prev[-1].valid_from if prev and prev[-1].valid_from else EARLIEST)
    return out, (min(out.values()) if out else None)


def closing_only(base, e):
    """Change that only shortens validity (sets or moves valid_until earlier)."""
    prev = [r for r in base.history(e["id"]) if not isinstance(r, Tombstone)]
    if not prev:
        return False
    from .kb import record_to_json
    old = record_to_json(prev[-1])
    for k, v in e.items():
        if k in ("valid_until", "recorded_on", "source", "label", "label_id"):
            continue
        if _norm(old.get(k)) != _norm(v):
            return False
    vu = _d(e.get("valid_until"))
    return vu is not None and (prev[-1].valid_until is None or vu < prev[-1].valid_until)


def _sym_diff_start(a0, a1, b0, b1):
    lo, hi = date(1900, 1, 1), date(2999, 12, 31)
    a0, a1, b0, b1 = a0 or lo, a1 or hi, b0 or lo, b1 or hi
    starts = []
    if a0 != b0:
        starts.append(min(a0, b0))
    if a1 != b1:
        starts.append(min(a1, b1) + timedelta(days=1))
    return min(starts) if starts else min(a0, b0)


def _d(text):
    return date.fromisoformat(text) if text else None


def _norm(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return str(v)
    if isinstance(v, list):
        return [_norm(x) for x in v]
    if isinstance(v, dict):
        return {k: _norm(x) for k, x in v.items()}
    return v


# ---------------------------------------------------------------------- observations on generated cases
def observe(kb, case, omega, extra=()):
    """(observations {(month or 0 for year facts, fact): value}, conflict keys, errors, final month) of the output
    facts, plus the extra facts given (for a policy update: the facts the policy defines, its own payroll outputs)."""
    from .engine import evaluate_case
    outputs = None
    if extra:
        view = kb.view(omega)
        outputs = sorted({f.id for f in view.facts.values() if f.output} | {f for f in extra if f in view.facts})
    r = evaluate_case(kb, case, omega, outputs=outputs)
    obs = {}
    final = max(r.periods) if r.periods else 0
    for m, row in r.periods.items():
        for f, v in row.items():
            obs[(m, f)] = v
    for f, v in r.year.items():
        obs[(0, f)] = v
    return obs, r.conflict_keys(), list(r.errors), final


def _month_date(case, m, final):
    return date(int(case["tax_year"]), m or final, 1)


class Evaluations:
    """Memo of observations per (knowledge base label, case index, omega)."""

    def __init__(self, cases, extra=()):
        self.cases = cases
        self.extra = tuple(extra)
        self.memo = {}

    def get(self, label, kb, i, omega):
        key = (label, i, omega)
        if key not in self.memo:
            self.memo[key] = observe(kb, self.cases[i], omega, self.extra)
        return self.memo[key]


# ---------------------------------------------------------------------- G4
def g4(base, kb2, sgset, evals, s_delta, company=False):
    """company=True (policy update): the company layer is not filtered by omega and a policy applies to the cases that
    name it, so changes before the start of effect are not checked; only new engine errors are."""
    msgs = []
    early, late = sgset.omegas
    for i, case in enumerate(sgset.cases):
        o1, c1, e1, final = evals.get("K'", kb2, i, late)
        o0, _, e0, _ = evals.get("K", base, i, late)
        new_errors = [e for e in e1 if e not in e0]
        if new_errors:
            # errors that the base already has on the same case are not caused by the update (e.g. a gross-up
            # without fixed point under the difference method); only new ones count
            msgs.append(f"{case['case_id']} y{case['tax_year']}: engine error on K': {new_errors[0][:160]}")
            continue
        if e1 or company:
            continue
        for (m, f), v in o1.items():
            if s_delta and _month_date(case, m, final) < s_delta and o0.get((m, f)) != v:
                msgs.append(f"{case['case_id']} y{case['tax_year']} m{m or final} {f}: changed before the start of "
                            f"effect {s_delta}: {o0.get((m, f))} -> {v}")
                break
        p1, _, _, _ = evals.get("K'", kb2, i, early)
        p0, _, _, _ = evals.get("K", base, i, early)
        if p1 != p0:
            diff = next(k for k in p1 if p1.get(k) != p0.get(k))
            msgs.append(f"{case['case_id']} y{case['tax_year']} {diff}: changed one day before the issue date")
        if len(msgs) >= 15:
            break
    return GateResult("G4", not msgs, msgs)


# ---------------------------------------------------------------------- G5
def _without(base, delta, eid):
    d = dict(delta)
    d["add"] = [e for e in delta["add"] if e["id"] != eid]
    d["change"] = [e for e in delta["change"] if e["id"] != eid]
    d["remove"] = [e for e in delta["remove"] if e["id"] != eid]
    d["delta_id"] = delta["delta_id"] + "-without"
    try:
        return apply_delta(base, d)
    except (UpdateError, ValueError):
        return None


def g5(base, kb2, delta, sgset, evals, starts, relevance=None):
    if not (delta["add"] or delta["change"] or delta["remove"]):
        return GateResult("G5", True)
    msgs = []
    late = sgset.omegas[1]
    n = len(sgset.cases)
    changed = []
    for i in range(n):
        o1, c1, _, _ = evals.get("K'", kb2, i, late)
        o0, c0, _, _ = evals.get("K", base, i, late)
        if o1 != o0 or c1 != c0:
            changed.append(i)
    order = changed + [i for i in range(n) if i not in set(changed)]
    for e in delta["add"] + delta["change"]:
        if e["kind"] == "fact":                # facts only name values; their rules carry the effect
            continue
        if e in delta["change"] and closing_only(base, e):
            vu = _d(e.get("valid_until"))
            s_d = min(starts.values()) if starts else None
            if s_d and vu and vu < s_d - timedelta(days=1):
                msgs.append(f"{e['id']}: closing ends before the start of effect of the update")
            continue
        su = starts.get(e["id"])
        kbu = _without(base, delta, e["id"])
        effect = kbu is None
        for i in order if not effect else []:
            case = sgset.cases[i]
            o1, c1, _, final = evals.get("K'", kb2, i, late)
            try:
                ou, cu, eu, _ = observe(kbu, case, late, evals.extra)
            except Exception:  # noqa: BLE001 - failure without u counts as an effect
                effect = True
                break
            if eu and not evals.get("K'", kb2, i, late)[2]:
                effect = True
                break
            if cu != c1 or any(ou.get(k) != v for k, v in o1.items()
                               if su is None or _month_date(case, k[0], final) >= su):
                effect = True
                break
        if not effect:
            msgs.append(f"{e['id']}: no effect on any generated case (vacuous element)")
    view0 = base.view(late)
    dead = {f.ids[0] for f in consistency.check(base, late).findings if f.kind == "dead"}
    for e in delta["remove"]:
        fired = e["id"] in dead
        for i in range(n) if not fired else []:
            from .engine import evaluate_case
            r = evaluate_case(base, sgset.cases[i], late)
            if e["id"] in set(r.winners.values()):
                fired = True
                break
        if not fired:
            msgs.append(f"{e['id']}: removed element never applied in K and is not dead")
    if relevance and relevance.get("effective_from"):
        try:
            eff = date.fromisoformat(relevance["effective_from"])
        except ValueError:
            eff = None
        if eff:
            eff = max(eff, date(YEARS[0], 1, 1))
            hit = False
            for i in changed:
                case = sgset.cases[i]
                o1, _, _, final = evals.get("K'", kb2, i, late)
                o0, _, _, _ = evals.get("K", base, i, late)
                if any(_month_date(case, k[0], final) == date(eff.year, eff.month, 1) and o0.get(k) != v
                       for k, v in o1.items()):
                    hit = True
                    break
            if not hit:
                msgs.append(f"stated effective date {eff} is not reflected: no generated case changes in that month")
    for s in (relevance or {}).get("subjects", []):
        if s.get("kind") != "klu":
            continue
        # the subject names codes ("14111") or describes a set ("codes in Lampiran A"): only named five-digit codes
        # can be checked, and one of them must appear in a changed case
        codes = set(re.findall(r"(?<!\d)\d{5}(?!\d)", str(s.get("value"))))
        if codes and not any(sgset.cases[i]["employer"].get("klu") in codes for i in changed):
            msgs.append(f"stated subject KLU {', '.join(sorted(codes))} is not reflected in a changed generated case")
    # A stated date or subject that no generated case shows, and an element without effect, are reported to the
    # reviewer instead of rejecting the draft: a policy often shows its effect only in some months (bonus, THR, the
    # final period), and a policy may restate a value equal to the regulation that it keeps binding.
    soft = [m for m in msgs if m.startswith(("stated effective date", "stated subject"))
            or m.endswith("(vacuous element)")]
    hard = [m for m in msgs if m not in soft]
    return GateResult("G5", not hard, hard, soft)


# ---------------------------------------------------------------------- G6
def g6(view, delta):
    """Case-data inputs read by the update must exist in the payroll data. The generated cases supply whatever a draft
    reads, so an invented attribute name passes G4 and G5 and then never fires on real payroll data. A failure goes
    to the repair round; an update that needs a genuinely new input goes to the reviewer, who adds it first."""
    from .draft import new_inputs
    new = new_inputs(view, delta)
    if not new:
        return GateResult("G6", True)
    return GateResult("G6", False, [
        "reads case-data inputs that do not exist in the payroll data: " + ", ".join(new)
        + ". If an input listed under CASE DATA has the same meaning, use it. Otherwise keep the provision and its new "
          "input unchanged: do not remove or simplify a provision to pass this check; the update then goes to the "
          "reviewer, who adds the input to the payroll data"])
