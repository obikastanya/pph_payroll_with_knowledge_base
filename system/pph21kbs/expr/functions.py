"""Function catalogue of the expression language (representasi.md 6.3).

Only the signature lives here. The engine implements each function, because most of them read the case, the
evaluation date, or other facts. Adding a function is an engine change (A1); adding facts, parameters, tables, or case
attributes is not.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class FunctionSpec:
    name: str
    min_args: int
    max_args: int | None
    scope: str            # "any", "period" (only inside period-scope rules), "year"
    returns: str          # "number", "bool", "category", "any"
    fact_arg: bool = False   # first argument is a fact name written as a string literal
    table_arg: bool = False  # first argument is a table name
    param_arg: bool = False  # first argument is a parameter name
    doc: str = ""


_SPECS = [
    FunctionSpec("min", 1, None, "any", "number", doc="smallest argument"),
    FunctionSpec("max", 1, None, "any", "number", doc="largest argument"),
    FunctionSpec("abs", 1, 1, "any", "number", doc="absolute value"),
    FunctionSpec("round", 3, 3, "any", "number",
                 doc="round(x, unit, mode); mode in down, up, truncate, half_up, half_even"),
    FunctionSpec("dec", 1, 1, "any", "number", doc="exact value of a decimal written as text, dec('0.0024')"),
    FunctionSpec("param", 1, 1, "any", "any", param_arg=True,
                 doc="value of a versioned parameter valid on the evaluation date"),
    FunctionSpec("lookup", 2, 2, "any", "any", table_arg=True, doc="lookup(table, key) on a lookup table"),
    FunctionSpec("bracket", 3, 3, "any", "number", table_arg=True,
                 doc="bracket(table, key, amount): value of the row with lower < amount <= upper for that key"),
    FunctionSpec("progressive", 2, 2, "any", "number", table_arg=True,
                 doc="progressive(table, amount): sum of rate x part of amount in each layer, exact"),
    FunctionSpec("in_table", 2, 2, "any", "bool", table_arg=True, doc="in_table(table, key) for a set table"),
    FunctionSpec("table_attr", 3, 3, "any", "any", table_arg=True,
                 doc="table_attr(table, key, attribute) of a set table row"),
    FunctionSpec("startswith", 2, 2, "any", "bool", doc="startswith(text, prefix)"),
    FunctionSpec("income", 1, 1, "period", "number", doc="income component of this period from the case (0 if absent)"),
    FunctionSpec("benefit", 1, 1, "period", "number", doc="benefit-in-kind value of this period by kind (0 if absent)"),
    FunctionSpec("hr", 1, 1, "period", "any", doc="HR data of this period (0 if absent)"),
    FunctionSpec("zakat_paid", 0, 0, "period", "number", doc="zakat paid through the employer this period"),
    FunctionSpec("employee", 1, 1, "any", "any", doc="employee attribute from the case (None if absent)"),
    FunctionSpec("employer", 1, 1, "any", "any", doc="employer attribute from the case (None if absent)"),
    FunctionSpec("case", 1, 1, "any", "any", doc="case attribute: tax_year, method, start_month, end_month"),
    FunctionSpec("sum_periods", 1, 1, "year", "number", fact_arg=True, doc="sum of a period fact over all employment months"),
    FunctionSpec("sum_periods_before_final", 1, 1, "year", "number", fact_arg=True,
                 doc="sum of a period fact over the employment months before the final period"),
    FunctionSpec("sum_to_date", 1, 1, "period", "number", fact_arg=True,
                 doc="sum of a period fact from the first employment month up to this month"),
    FunctionSpec("sum_before", 1, 1, "period", "number", fact_arg=True,
                 doc="sum of a period fact from the first employment month up to the month before this one"),
    FunctionSpec("value_in", 2, 2, "any", "any", fact_arg=True, doc="value_in(fact, month) of a period fact"),
    FunctionSpec("year_value", 1, 1, "period", "any", fact_arg=True, doc="value of a year fact inside a period rule"),
    FunctionSpec("defined", 1, 1, "any", "bool", fact_arg=True, doc="whether an active rule produces the fact here"),
    FunctionSpec("value_or", 2, 2, "any", "any", fact_arg=True, doc="value of the fact, or the fallback if no active rule"),
]

FUNCTIONS = {spec.name: spec for spec in _SPECS}

# Built-in context facts (representasi.md 6.3); always available, never produced by rules.
CONTEXT_FACTS = {
    "month": ("int", "period"),
    "tax_year": ("int", "any"),
    "is_final_period": ("bool", "period"),
    "first_month": ("int", "any"),
    "final_month": ("int", "any"),
    "months_employed": ("int", "any"),
}
