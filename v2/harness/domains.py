"""Company payroll fields: which HR data a company's policy reads, the values those fields take (inferred from the
gold rules: compared constants, table keys, booleans, thresholds), and the company's payroll data dictionary.

The dictionary also lists common HR fields that the policy does not read, so that it describes a company's HR data
and does not point at the rules."""
import ast
import json

from pph21kbs import draft  # noqa: E402

COMMON = {
    "employee": {"job_grade": "job grade in the company's grading", "division": "division or department",
                 "work_location": "work location", "employment_status": "permanent, contract, or probation"},
    "hr": {"days_present_month": "days present this month", "annual_leave_taken": "annual leave days taken this month",
           "sick_days": "sick days this month", "overtime_hours_total": "total overtime hours this month"},
}
COUNTS = (0, 1, 3)
EVENTS = (0, 1, 2)                 # a count multiplied by a rupiah amount in a rule: deaths, births, claims
DAYS = (0, 2, 5, 10)
HOURS = (0, 2, 6, 12)
AMOUNTS = (0, 250_000, 1_500_000)
MONEY_WORDS = ("claim", "paid", "grant", "aid", "amount", "value", "allowance", "fee", "cost")


def company_inputs(update):
    """(accessor, key) -> expression texts, for the inputs of `update` that are not in the case schema or the
    standard payroll dictionary."""
    standard = draft.payroll_dictionary()
    schema = draft.schema_fields()
    out = {}
    for op in ("add", "change"):
        for el in update.get(op, []):
            for f in draft.EXPR_FIELDS:
                text = el.get(f)
                if isinstance(text, str):
                    for a, k in draft.reads(text):
                        if k not in schema.get(a, set()) and k not in standard.get(a, {}):
                            out.setdefault((a, k), []).append(text)
    return out


def _accessor(node):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in draft.ACCESSORS
            and node.args and isinstance(node.args[0], ast.Constant)):
        return node.func.id, node.args[0].value
    return None


def _holds(node, field):
    """The node is the field's accessor, possibly behind a None default: (x if x != None else d)."""
    if _accessor(node) == field:
        return True
    return isinstance(node, ast.IfExp) and _accessor(node.body) == field


def _constant(node):
    """The value of a constant expression (numbers, dec('...'), arithmetic of them, strings, booleans), or None."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "dec" and node.args and isinstance(
            node.args[0], ast.Constant):
        return float(node.args[0].value)
    if isinstance(node, ast.BinOp):
        a, b = _constant(node.left), _constant(node.right)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
            ops = {ast.Mult: a * b, ast.Add: a + b, ast.Sub: a - b, ast.Div: a / b if b else None}
            return ops.get(type(node.op))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _constant(node.operand)
        return -v if isinstance(v, (int, float)) else None
    return None


def domain(field, texts, view):
    """Values a field takes: constants it is compared with (and one value outside them), keys of the tables it is
    looked up in, both booleans, or values around numeric thresholds; else typical values by its name."""
    strings, numbers, booleans, tables, prefixes, per_unit = set(), set(), False, set(), set(), False
    for text in texts:
        tree = ast.parse(text.strip(), mode="eval")
        for n in ast.walk(tree):
            if isinstance(n, ast.Compare):
                sides = [n.left] + list(n.comparators)
                if any(_holds(x, field) for x in sides):
                    for x in sides:
                        if _holds(x, field):
                            continue
                        items = x.elts if isinstance(x, (ast.Tuple, ast.List, ast.Set)) else [x]
                        for item in items:
                            v = _constant(item)
                            if isinstance(v, bool):
                                booleans = True
                            elif isinstance(v, str):
                                strings.add(v)
                            elif isinstance(v, (int, float)):
                                numbers.add(int(v) if float(v).is_integer() else v)
            elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult) and (
                    (_holds(n.left, field) and isinstance(_constant(n.right), (int, float))
                     and _constant(n.right) >= 1000) or
                    (_holds(n.right, field) and isinstance(_constant(n.left), (int, float))
                     and _constant(n.left) >= 1000)):
                per_unit = True
            elif isinstance(n, ast.IfExp) and _accessor(n.test) == field:
                booleans = True
            elif isinstance(n, ast.BoolOp) and any(_accessor(v) == field for v in n.values):
                booleans = True
            elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not) and _accessor(n.operand) == field:
                booleans = True
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                if (n.func.id in ("lookup", "in_table") and len(n.args) >= 2 and isinstance(n.args[0], ast.Constant)
                        and any(_accessor(x) == field for x in ast.walk(n.args[1]))):
                    tables.add(n.args[0].value)
                if (n.func.id == "startswith" and len(n.args) == 2 and isinstance(n.args[1], ast.Constant)
                        and any(_holds(x, field) for x in ast.walk(n.args[0]))):
                    prefixes.add(n.args[1].value)
    for t in tables:
        for version in view.tables.get(t, ()):
            for r in version.rows:
                k = r.get("key")
                if isinstance(k, (int, float)) or (isinstance(k, str) and k.lstrip("-").isdigit()):
                    numbers.add(int(k))
                elif k is not None:
                    strings.add(str(k))
    if prefixes and not strings:              # a code tested only by its prefix
        strings = {f"{p}1" for p in prefixes} | {"Z1"}
    accessor, key = field
    if "days_in_month" in key or "calendar_days" in key:
        return [28, 30, 31]
    if "workdays" in key or "working_days" in key:
        return [20, 21, 22, 25]
    if "minimum_wage" in key:
        return [4_000_000, 5_500_000]
    if strings:
        return sorted(strings) + ["lainnya"]
    if numbers:
        return sorted({max(0, x + d) for x in numbers for d in (-1, 0, 1)})[:9]
    if booleans:
        return [True, False]
    if per_unit:
        return list(EVENTS)
    if accessor in ("income", "benefit") or any(w in key for w in MONEY_WORDS):
        return list(AMOUNTS)
    if "day" in key or "shift" in key or "saturday" in key:
        return list(DAYS)
    if key.startswith("ot_") or "hour" in key:
        return list(HOURS)
    return list(COUNTS)


def company_fields(updates, kb):
    """(accessor, key) -> values, over the gold updates of one company, with the tables of `kb`."""
    texts = {}
    for u in updates:
        for f, ts in company_inputs(u).items():
            texts.setdefault(f, []).extend(ts)
    view = kb.view(max(u.recorded_on for u in kb.updates if u.recorded_on))
    return {f: domain(f, ts, view) for f, ts in texts.items()}


def dictionary(fields):
    """The company's payroll data dictionary: its fields with a plain meaning (and the codes of a categorical
    field), plus the common HR fields."""
    out = {a: dict(v) for a, v in COMMON.items()}
    for (a, k), values in sorted(fields.items()):
        meaning = k.replace("_", " ")
        if values and all(isinstance(v, str) for v in values):
            meaning += " (codes: " + ", ".join(v for v in values if v != "lainnya") + ")"
        elif values == [True, False]:
            meaning += " (yes or no)"
        out.setdefault(a, {})[k] = meaning
    return out


def write_dictionary(path, fields):
    path.write_text(json.dumps(dictionary(fields), ensure_ascii=False, indent=1), encoding="utf-8")
