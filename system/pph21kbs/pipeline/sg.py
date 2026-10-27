"""Generator of S^G, the cases a candidate Delta is verified on (akuisisi.md 5). Built from K (+) Delta and the
relevance assessment only; never reads the gold or S^E.

Dimensions: tax year, work pattern (full year, joins in the month the Delta starts having effect, leaves one month
after it), salary level (default levels plus salaries whose watched fact lands on b - 1, b, b + 1 for each threshold b,
found by bisection with the engine), PTKP status, withholding method, case attributes read by the Delta (booleans
both ways, categories each literal plus one other value, numbers at their thresholds; KLU each key of a set table the
Delta adds or changes plus one key outside), and component variant (salary only, with THR and bonus in the start
month, with each benefit kind the Delta reads, with zakat). Pairwise (2-way) coverage of the small dimensions is
built greedily; large dimensions (many table keys or thresholds) are covered one value at a time. At most 300 cases;
every case carries the marker income.other_regular = 7 that S^E never uses.
"""
import ast
import itertools
import random
from dataclasses import dataclass
from datetime import date, timedelta
from fractions import Fraction

from ..engine import evaluate_case
from ..kb.model import Parameter, Rule, TableVersion

PTKP_ALL = ("TK/0", "TK/1", "TK/2", "TK/3", "K/0", "K/1", "K/2", "K/3")
METHODS = ("gross", "gross_up", "employer_borne")
DEFAULT_SALARIES = (4_800_000, 9_000_000, 16_000_000, 45_000_000)
MAX_CASES = 300
MAX_COMBOS = 6000           # 3-way coverage only when it has at most this many value combinations
FILL = 250                  # random combinations are added until S^G has this many cases
MAX_THRESHOLDS = 24
MARKER = 7
YEARS = (2013, 2027)


@dataclass
class SGSet:
    cases: list          # case dicts
    omegas: tuple        # (issued - 1 day, issued)
    start: date          # s(Delta)


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
    """S^G for a candidate: base = K, kb2 = K (+) Delta, s_delta = s(Delta), issued = t_terbit, starts = s(u) per
    element id (gates.effect_start). omega is the knowledge date the cases are evaluated at: the issue date for
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
    if rows is None or len(rows) > MAX_CASES // 2:      # 3-way too large: pairwise (akuisisi.md 5 item 6)
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
