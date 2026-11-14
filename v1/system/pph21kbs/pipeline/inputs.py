"""Case-data interface for the LLM context and the input check (pipeline v2, development).

The case data that rules read through income(), benefit(), hr(), employee(), employer() and case() are the payroll
system's input interface. v1 showed the model the accessor functions but not the attribute names, so a draft could
invent a name that no case carries (the silent error on E07). v2 lists the attributes that exist at the knowledge
date: the fixed fields of the case schema and the keys read by the rules of the base knowledge base. A draft that
reads an attribute outside this list is reported to the reviewer as a new payroll input.
"""
import ast
import json
from functools import lru_cache

from ..config import REPO
from ..kb.model import Constraint, Rule

ACCESSORS = ("income", "benefit", "hr", "employee", "employer", "case")
EXPR_FIELDS = ("expression", "condition", "assertion", "fixed_point_lower", "fixed_point_upper")


@lru_cache(maxsize=1)
def schema_fields():
    s = json.loads((REPO / "system" / "schemas" / "case.schema.json").read_text(encoding="utf-8"))["properties"]
    return {"employee": set(s["employee"]["properties"]), "employer": set(s["employer"]["properties"]) - {"policy"},
            "case": {"tax_year", "method", "start_month", "end_month"}}


def reads(text):
    """(accessor, key) pairs read with a constant key in an expression text."""
    out = set()
    try:
        tree = ast.parse(text.strip(), mode="eval")
    except (SyntaxError, AttributeError):
        return out
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ACCESSORS and n.args
                and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)):
            out.add((n.func.id, n.args[0].value))
    return out


def known(view):
    """Attributes that exist at the knowledge date: schema fields plus keys read by the base rules."""
    k = {a: set() for a in ACCESSORS}
    for a, fields in schema_fields().items():
        k[a] |= fields
    for r in view.records:
        if isinstance(r, (Rule, Constraint)):
            for e in (getattr(r, "expression", None), getattr(r, "condition", None), getattr(r, "assertion", None)):
                if e is not None:
                    for a, key in reads(e.text):
                        k[a].add(key)
    return k


def context_text(view):
    k = known(view)
    lines = ["CASE DATA (the payroll inputs that exist; rules read them with these accessors and exact names):"]
    for a in ACCESSORS:
        lines.append(f"- {a}(...): " + (", ".join(f"'{x}'" for x in sorted(k[a])) or "(none yet)"))
    lines.append("Use these names exactly. If the document needs an input that is not listed (for example a company "
                 "allowance or an eligibility status), you may introduce it with a plain descriptive name; it will be "
                 "reported to the reviewer as a new payroll input.")
    return "\n".join(lines)


def new_inputs(view, delta):
    """Attributes a Delta reads that are not in known(view)."""
    k = known(view)
    found = set()
    for el in (delta.get("add") or []) + (delta.get("change") or []):
        for f in EXPR_FIELDS:
            v = el.get(f)
            if isinstance(v, str):
                found |= reads(v)
    return sorted(f"{a}('{key}')" for a, key in found if key not in k[a])
