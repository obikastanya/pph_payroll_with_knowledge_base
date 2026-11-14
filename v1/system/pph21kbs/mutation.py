"""Mutation operators and mutation score (PANDUAN Tahap 8, skeleton "Kecukupan S^E").

A mutant is a gold Delta with one element changed by one operator; it is applied to the chain before the event and
evaluated on S^E of that event. The mutant is killed when some observation or conflict report differs from the
expected value of the gold. Delta-focused score: mutants of the elements of Delta*_n only. Global score: mutants of
records anywhere in the final chain, evaluated on all of S^E at omega = 2026-10-27.

Operators: value (parameter value, one table row, an integer constant of an expression), date (valid_from one month
later, valid_until one month earlier), condition (negated, or dropped), layer (moved to the company layer of a policy
no case names), modality (mandatory -> default), revoke (element removed). Mutants that do not parse or cannot be
applied are reported as stillborn, not counted. Equivalent mutants cannot be recognised automatically: survivors are
listed for inspection.
"""
import ast
import copy
import json
from dataclasses import dataclass
from datetime import date, timedelta
from fractions import Fraction

from .engine import evaluate_case
from .kb import apply_delta
from .kb.delta import UpdateError


@dataclass
class Mutant:
    element: str
    operator: str
    delta: dict
    detail: str = ""


def _month_shift(text, months):
    d = date.fromisoformat(text)
    y, m = d.year + (d.month - 1 + months) // 12, (d.month - 1 + months) % 12 + 1
    if d.day == 1:
        return date(y, m, 1).isoformat()
    nxt = date(y + (m == 12), m % 12 + 1, 1)
    return (nxt - timedelta(days=1)).isoformat()


def _perturb_value(v, vtype):
    if vtype in ("money", "int"):
        return int(v) + max(1, abs(int(v)) // 10)
    if vtype in ("rate", "exact"):
        x = Fraction(str(v))
        return str(x * Fraction(11, 10) if x else Fraction(1, 100))
    if vtype == "bool":
        return not v
    return f"{v}_X"


def _perturb_expression(text):
    """Change the first integer constant >= 2 that is not a rounding unit (x -> x + max(1, x // 10))."""
    tree = ast.parse(text, mode="eval")
    skip = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "round" and len(n.args) == 3:
            skip.add(id(n.args[1]))

    class T(ast.NodeTransformer):
        done = False

        def visit_Constant(self, node):
            if (not self.done and type(node.value) is int and node.value >= 2 and id(node) not in skip):
                self.done = True
                return ast.copy_location(ast.Constant(node.value + max(1, node.value // 10)), node)
            return node
    t = T()
    new = t.visit(tree)
    return ast.unparse(new) if t.done else None


def mutants_of(delta):
    """All single-element mutants of a Delta."""
    out = []
    for op in ("add", "change"):
        for i, e in enumerate(delta[op]):
            if e["kind"] == "fact":
                continue

            def make(name, change, detail=""):
                d = copy.deepcopy(delta)
                if change is None:
                    d[op].pop(i)
                else:
                    change(d[op][i])
                d["delta_id"] = f"{delta['delta_id']}-M-{e['id']}-{name}"
                out.append(Mutant(e["id"], name, d, detail))
            if e["kind"] == "parameter":
                make("value", lambda x: x.update(value=_perturb_value(x["value"], x["value_type"])))
            if e["kind"] == "table" and e.get("rows"):
                def row_change(x):
                    r = x["rows"][len(x["rows"]) // 2]
                    for k in ("value", "rate", "upper"):
                        if r.get(k) not in (None, ""):
                            if k == "upper":
                                r[k] = int(r[k]) + 1000
                            elif isinstance(r[k], (int, float)) or str(r[k]).replace(".", "", 1).replace("/", "", 1).isdigit():
                                r[k] = str(Fraction(str(r[k])) * Fraction(11, 10))
                            else:
                                r[k] = f"{r[k]}_X"
                            break
                make("value", row_change, "middle row")
            if e["kind"] in ("rule", "constraint"):
                field = "expression" if e["kind"] == "rule" else "assertion"
                new = _perturb_expression(e[field])
                if new:
                    make("value", lambda x, new=new, field=field: x.update({field: new}), "constant +10%")
                if e.get("condition"):
                    make("condition", lambda x: x.update(condition=f"not ({x['condition']})"), "negated")
                    make("condition_drop", lambda x: x.pop("condition"), "dropped")
            if e["kind"] == "rule" and e.get("layer") == "regulation":
                make("layer", lambda x: x.update(layer="company", modality="default", policy="MUTANT",
                                                id="PRS.MUT." + x["id"][4:]), "to company layer")
                if e.get("modality") == "mandatory":
                    make("modality", lambda x: x.update(modality="default"), "mandatory -> default")
            if e.get("valid_from"):
                make("date", lambda x: x.update(valid_from=_month_shift(x["valid_from"], 1)), "valid_from +1 month")
            if e.get("valid_until"):
                make("date_end", lambda x: x.update(valid_until=_month_shift(x["valid_until"], -1)),
                     "valid_until -1 month")
            if op == "add":
                make("revoke", None, "element left out")
    return out


def observations(kb, case, omega):
    r = evaluate_case(kb, case, omega)
    obs = {f"{m}:{f}": (str(v) if isinstance(v, Fraction) else v) for m, row in r.periods.items()
           for f, v in row.items()}
    obs.update({f"0:{f}": (str(v) if isinstance(v, Fraction) else v) for f, v in r.year.items()})
    return obs, sorted(map(str, r.conflict_keys()))


def killed(base, mutant, tuples, cases):
    """(status, first differing tuple): status killed | survived | stillborn."""
    try:
        kb = apply_delta(base, mutant.delta)
    except (UpdateError, ValueError, KeyError, SyntaxError) as e:
        return "stillborn", str(e)[:120]
    for t in tuples:
        case = cases[t["case_id"]]
        omega = date.fromisoformat(t["omega"])
        try:
            obs, conflicts = observations(kb, case, omega)
        except Exception as e:  # noqa: BLE001 - an engine failure on the mutant is a detection
            return "killed", f"{t['case_id']} error {type(e).__name__}"
        if obs != t["obs"] or conflicts != t["conflicts"]:
            return "killed", t["case_id"]
    return "survived", ""
