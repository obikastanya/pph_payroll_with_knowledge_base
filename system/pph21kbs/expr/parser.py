"""Parse, statically check, compile, and canonicalise expressions (representasi.md 6 and 9).

The language is a subset of Python expressions. Parsing rejects everything outside the subset, so a rule that would
call arbitrary code, read attributes, or use binary floats never reaches evaluation. Compilation turns the checked
AST into nested closures, which evaluate an order of magnitude faster than walking the AST each time.
"""
import ast
from fractions import Fraction

from .functions import CONTEXT_FACTS, FUNCTIONS
from .numbers import PrecisionError, check_number, decimal_value, normalize

_BINOPS = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/"}
_CMPOPS = {ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
           ast.In: "in", ast.NotIn: "not in"}
_COMMUTATIVE_CALLS = {"min", "max"}


class ExpressionError(ValueError):
    """Static or evaluation error in an expression."""


class Expression:
    """A parsed, checked, and compiled expression.

    Attributes after parsing:
      text       the source text
      facts      fact names read directly (excluding built-in context facts)
      fact_args  fact names read through aggregation functions (sum_periods('x'), value_in('x', 3), ...)
      params     parameter names read with param('name')
      tables     table names read by table functions
      functions  functions called
      context    built-in context facts read
    """

    __slots__ = ("text", "tree", "facts", "fact_args", "params", "tables", "functions", "context", "_fn")

    def __init__(self, text):
        if not isinstance(text, str) or not text.strip():
            raise ExpressionError(f"expression must be non-empty text, got {text!r}")
        self.text = text
        self.facts, self.fact_args, self.params, self.tables = set(), set(), set(), set()
        self.functions, self.context = set(), set()
        try:
            self.tree = ast.parse(text.strip(), mode="eval").body
        except SyntaxError as e:
            raise ExpressionError(f"syntax error in {text!r}: {e.msg}") from None
        except (RecursionError, MemoryError):
            raise ExpressionError(f"expression too deeply nested: {text[:80]!r}") from None
        self._check(self.tree)
        self._fn = _compile(self.tree)

    # ------------------------------------------------------------------ static check
    def _check(self, n):
        if isinstance(n, ast.Constant):
            if isinstance(n.value, float):
                raise PrecisionError(f"binary float literal in {self.text!r}; write 5 / 100 or dec('0.05')")
            if not isinstance(n.value, (int, str, bool, type(None))):
                raise ExpressionError(f"unsupported literal {n.value!r} in {self.text!r}")
        elif isinstance(n, ast.Name):
            if n.id in CONTEXT_FACTS:
                self.context.add(n.id)
            elif n.id in FUNCTIONS:
                raise ExpressionError(f"function {n.id} used without call in {self.text!r}")
            else:
                if n.id != n.id.lower() or n.id.startswith("__") or not n.id.replace("_", "").isalnum():
                    raise ExpressionError(f"invalid fact name {n.id!r} in {self.text!r}")
                self.facts.add(n.id)
        elif isinstance(n, ast.BinOp):
            if type(n.op) not in _BINOPS:
                raise ExpressionError(f"operator {type(n.op).__name__} not allowed in {self.text!r}")
            self._check(n.left)
            self._check(n.right)
        elif isinstance(n, ast.UnaryOp):
            if not isinstance(n.op, (ast.Not, ast.USub)):
                raise ExpressionError(f"unary operator {type(n.op).__name__} not allowed in {self.text!r}")
            self._check(n.operand)
        elif isinstance(n, ast.BoolOp):
            for v in n.values:
                self._check(v)
        elif isinstance(n, ast.Compare):
            for op in n.ops:
                if type(op) not in _CMPOPS:
                    raise ExpressionError(f"comparison {type(op).__name__} not allowed in {self.text!r}")
            self._check(n.left)
            for c in n.comparators:
                self._check(c)
        elif isinstance(n, ast.IfExp):
            self._check(n.test)
            self._check(n.body)
            self._check(n.orelse)
        elif isinstance(n, ast.Tuple):
            for e in n.elts:
                self._check(e)
        elif isinstance(n, ast.Call):
            if not isinstance(n.func, ast.Name):
                raise ExpressionError(f"only registered functions may be called, in {self.text!r}")
            spec = FUNCTIONS.get(n.func.id)
            if spec is None:
                raise ExpressionError(f"unknown function {n.func.id}() in {self.text!r}")
            if n.keywords:
                raise ExpressionError(f"keyword arguments not supported in {self.text!r}")
            k = len(n.args)
            if k < spec.min_args or (spec.max_args is not None and k > spec.max_args):
                want = str(spec.min_args) if spec.min_args == spec.max_args else (
                    f"{spec.min_args}..{spec.max_args}" if spec.max_args is not None else f"at least {spec.min_args}")
                raise ExpressionError(f"{spec.name}() takes {want} arguments, got {k}, in {self.text!r}")
            self.functions.add(spec.name)
            if spec.fact_arg or spec.table_arg or spec.param_arg:
                first = n.args[0]
                if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
                    raise ExpressionError(f"first argument of {spec.name}() must be a name in quotes, in {self.text!r}")
                (self.fact_args if spec.fact_arg else self.tables if spec.table_arg else self.params).add(first.value)
            if spec.name == "dec":
                arg = n.args[0]
                if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                    raise ExpressionError(f"dec() takes a decimal written as text, in {self.text!r}")
                decimal_value(arg.value)
            for a in n.args:
                self._check(a)
        else:
            raise ExpressionError(f"construct {type(n).__name__} not allowed in {self.text!r}")

    # ------------------------------------------------------------------ API
    def evaluate(self, env):
        """Evaluate with an environment exposing fact(name) and call(name, args)."""
        try:
            return self._fn(env)
        except RecursionError:
            raise ExpressionError(f"expression too deeply nested: {self.text[:80]!r}") from None

    def dependencies(self):
        """Every fact the expression may read, directly or through functions."""
        return self.facts | self.fact_args

    def canonical(self):
        return canonical(self.tree)

    def __repr__(self):
        return f"Expression({self.text!r})"


def parse(text):
    return Expression(text)


# ---------------------------------------------------------------------- compilation
def _compile(n):
    if isinstance(n, ast.Constant):
        v = n.value
        return lambda env: v
    if isinstance(n, ast.Name):
        name = n.id
        return lambda env: env.fact(name)
    if isinstance(n, ast.BinOp):
        left, right, op = _compile(n.left), _compile(n.right), type(n.op)
        if op is ast.Add:
            return lambda env: normalize(check_number(left(env)) + check_number(right(env)))
        if op is ast.Sub:
            return lambda env: normalize(check_number(left(env)) - check_number(right(env)))
        if op is ast.Mult:
            return lambda env: normalize(check_number(left(env)) * check_number(right(env)))

        def div(env):
            a, b = check_number(left(env)), check_number(right(env))
            if b == 0:
                raise ExpressionError("division by zero")
            return normalize(Fraction(a) / Fraction(b))
        return div
    if isinstance(n, ast.UnaryOp):
        operand = _compile(n.operand)
        if isinstance(n.op, ast.Not):
            return lambda env: not _truth(operand(env))
        return lambda env: normalize(-check_number(operand(env)))
    if isinstance(n, ast.BoolOp):
        parts = [_compile(v) for v in n.values]
        if isinstance(n.op, ast.And):
            def all_true(env):
                for p in parts:
                    if not _truth(p(env)):
                        return False
                return True
            return all_true

        def any_true(env):
            for p in parts:
                if _truth(p(env)):
                    return True
            return False
        return any_true
    if isinstance(n, ast.Compare):
        left = _compile(n.left)
        pairs = [(type(op), _compile(c)) for op, c in zip(n.ops, n.comparators)]

        def compare(env):
            a = left(env)
            for op, right in pairs:
                b = right(env)
                if not _compare(op, a, b):
                    return False
                a = b
            return True
        return compare
    if isinstance(n, ast.IfExp):
        test, body, orelse = _compile(n.test), _compile(n.body), _compile(n.orelse)
        return lambda env: body(env) if _truth(test(env)) else orelse(env)
    if isinstance(n, ast.Tuple):
        elts = [_compile(e) for e in n.elts]
        return lambda env: tuple(e(env) for e in elts)
    if isinstance(n, ast.Call):
        name = n.func.id
        if name == "dec":
            value = decimal_value(n.args[0].value)
            return lambda env: value
        spec = FUNCTIONS[name]
        if spec.fact_arg or spec.table_arg or spec.param_arg:
            first = n.args[0].value
            rest = [_compile(a) for a in n.args[1:]]
            return lambda env: env.call(name, [first] + [r(env) for r in rest])
        args = [_compile(a) for a in n.args]
        return lambda env: env.call(name, [a(env) for a in args])
    raise ExpressionError(f"cannot compile {type(n).__name__}")


def _truth(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    if isinstance(v, (int, Fraction)):
        return v != 0
    raise ExpressionError(f"value {v!r} used as a condition is not boolean")


def _compare(op, a, b):
    if op is ast.Eq:
        return a == b
    if op is ast.NotEq:
        return a != b
    if op in (ast.In, ast.NotIn):
        if not isinstance(b, tuple):
            raise ExpressionError(f"right side of 'in' must be a tuple, got {b!r}")
        return (a in b) if op is ast.In else (a not in b)
    if a is None or b is None or isinstance(a, bool) or isinstance(b, bool):
        raise ExpressionError(f"cannot order {a!r} and {b!r}")
    if isinstance(a, str) != isinstance(b, str):
        raise ExpressionError(f"cannot order {a!r} and {b!r}")
    if op is ast.Lt:
        return a < b
    if op is ast.LtE:
        return a <= b
    if op is ast.Gt:
        return a > b
    return a >= b


# ---------------------------------------------------------------------- canonical form
def canonical(n):
    """Deterministic text of an AST with commutative operands sorted, numeric constants folded, and > / >= flipped
    to < / <= (representasi.md 9)."""
    folded = _fold(n)
    if folded is not None:
        return _fmt_const(folded)
    if isinstance(n, ast.Constant):
        return _fmt_const(n.value)
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.BinOp):
        op = _BINOPS[type(n.op)]
        if op in ("+", "*"):
            terms = sorted(canonical(t) for t in _flatten(n, type(n.op)))
            return "(" + f" {op} ".join(terms) + ")"
        return f"({canonical(n.left)} {op} {canonical(n.right)})"
    if isinstance(n, ast.UnaryOp):
        return f"(not {canonical(n.operand)})" if isinstance(n.op, ast.Not) else f"(-{canonical(n.operand)})"
    if isinstance(n, ast.BoolOp):
        word = "and" if isinstance(n.op, ast.And) else "or"
        terms = sorted(canonical(v) for v in _flatten_bool(n, type(n.op)))
        return "(" + f" {word} ".join(terms) + ")"
    if isinstance(n, ast.Compare):
        parts = []
        left = n.left
        for op, right in zip(n.ops, n.comparators):
            sym = _CMPOPS[type(op)]
            a, b = canonical(left), canonical(right)
            if sym in (">", ">="):
                a, b, sym = b, a, "<" if sym == ">" else "<="
            elif sym in ("==", "!=") and b < a:
                a, b = b, a
            parts.append(f"({a} {sym} {b})")
            left = right
        return parts[0] if len(parts) == 1 else "(" + " and ".join(parts) + ")"
    if isinstance(n, ast.IfExp):
        return f"({canonical(n.body)} if {canonical(n.test)} else {canonical(n.orelse)})"
    if isinstance(n, ast.Tuple):
        return "(" + ", ".join(canonical(e) for e in n.elts) + ("," if len(n.elts) == 1 else "") + ")"
    if isinstance(n, ast.Call):
        args = [canonical(a) for a in n.args]
        if n.func.id in _COMMUTATIVE_CALLS:
            args = sorted(args)
        return f"{n.func.id}({', '.join(args)})"
    return ast.dump(n)


def _flatten(n, op):
    if isinstance(n, ast.BinOp) and type(n.op) is op:
        return _flatten(n.left, op) + _flatten(n.right, op)
    return [n]


def _flatten_bool(n, op):
    if isinstance(n, ast.BoolOp) and type(n.op) is op:
        out = []
        for v in n.values:
            out += _flatten_bool(v, op)
        return out
    return [n]


def _fold(n):
    """Numeric value of a constant subexpression, or None."""
    if isinstance(n, ast.Constant) and isinstance(n.value, int) and not isinstance(n.value, bool):
        return n.value
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "dec" and n.args \
            and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
        try:
            return decimal_value(n.args[0].value)
        except PrecisionError:
            return None
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
        v = _fold(n.operand)
        return None if v is None else normalize(-Fraction(v))
    if isinstance(n, ast.BinOp) and type(n.op) in _BINOPS:
        a, b = _fold(n.left), _fold(n.right)
        if a is None or b is None:
            return None
        op = type(n.op)
        if op is ast.Add:
            return normalize(Fraction(a) + b)
        if op is ast.Sub:
            return normalize(Fraction(a) - b)
        if op is ast.Mult:
            return normalize(Fraction(a) * b)
        if b == 0:
            return None
        return normalize(Fraction(a) / Fraction(b))
    return None


def _fmt_const(v):
    if isinstance(v, Fraction):
        return f"{v.numerator}/{v.denominator}"
    return repr(v)
