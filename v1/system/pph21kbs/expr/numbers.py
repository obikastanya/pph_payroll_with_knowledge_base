"""Exact numbers and rounding (representasi.md 6.2 and 11.3).

All arithmetic is exact: integers for rupiah amounts and counts, Fraction for everything else. Binary floats never
enter the system. Rounding happens only through round_value, with an explicit unit and mode.
"""
import math
from fractions import Fraction
from decimal import Decimal, InvalidOperation


class PrecisionError(ValueError):
    """A float, or a non-numeric operand, reached exact arithmetic."""


ROUNDING_MODES = ("down", "up", "truncate", "half_up", "half_even")


def decimal_value(text):
    """Exact value of a decimal or fraction literal written as text: "0.0024" -> 3/1250, "1/3" -> 1/3."""
    if isinstance(text, bool) or not isinstance(text, (str, int, Fraction)):
        raise PrecisionError(f"decimal literal must be text, got {text!r}")
    if isinstance(text, (int, Fraction)):
        return normalize(Fraction(text))
    s = text.strip().replace("_", "")
    try:
        if "/" in s:
            num, den = s.split("/", 1)
            return normalize(Fraction(Decimal(num.strip())) / Fraction(Decimal(den.strip())))
        return normalize(Fraction(Decimal(s)))
    except (InvalidOperation, ValueError, ZeroDivisionError):
        raise PrecisionError(f"not a decimal literal: {text!r}") from None


def normalize(value):
    """Fractions with denominator 1 become int, so that money stays int."""
    if isinstance(value, Fraction) and value.denominator == 1:
        return value.numerator
    return value


def check_number(value, what="operand"):
    if isinstance(value, bool) or value is None or isinstance(value, float):
        raise PrecisionError(f"invalid arithmetic {what}: {value!r}")
    if not isinstance(value, (int, Fraction)):
        raise PrecisionError(f"invalid arithmetic {what}: {value!r} ({type(value).__name__})")
    return value


def round_value(value, unit, mode):
    """Round value to a multiple of unit. Modes for negative numbers: down -> towards -inf, up -> towards +inf,
    truncate -> towards zero, half_up -> halves away from zero, half_even -> halves to the even multiple."""
    value = Fraction(check_number(value, "value to round"))
    unit = Fraction(check_number(unit, "rounding unit"))
    if unit <= 0:
        raise PrecisionError(f"rounding unit must be positive, got {unit}")
    if mode not in ROUNDING_MODES:
        raise PrecisionError(f"unknown rounding mode {mode!r}; use one of {', '.join(ROUNDING_MODES)}")
    q = value / unit
    if mode == "down":
        n = math.floor(q)
    elif mode == "up":
        n = math.ceil(q)
    elif mode == "truncate":
        n = math.trunc(q)
    elif mode == "half_up":
        n = math.floor(abs(q) + Fraction(1, 2)) * (1 if q >= 0 else -1)
    else:
        n = round(q)  # Fraction.__round__ rounds halves to even
    return normalize(n * unit)
