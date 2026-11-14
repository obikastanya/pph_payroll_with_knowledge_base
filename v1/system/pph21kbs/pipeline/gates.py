"""Verification gates G1-G5 (akuisisi.md 4). Each gate returns a GateResult; messages are given to the repair round.

G1 structure: Delta schema (after conversion), strict application to the base, SHACL on K'.
G2 quotes, values, dates: every quote occurs in its document and at least one per element is from the event's
   documents; numbers >= 100 and rates are grounded in the element's quotes in an Indonesian notation; new or changed
   dates are grounded by the closed patterns; recorded_on = issue date.
G3 static consistency of K' (pph21kbs.static): errors fail, warnings are recorded.
G4 regression and execution on S^G (see sg.py): earlier periods unchanged at omega = issue date, everything unchanged
   one day before the issue date, no engine error on K'.
G5 non-vacuity: every added or content-changed element has an effect on some S^G tuple; closings are exempt;
   removed ids must have been active or dead; stated effective date and subjects are reflected.
"""
import ast
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from fractions import Fraction

from .. import static
from ..expr import Expression
from ..kb import apply_delta, shacl
from ..kb.delta import UpdateError
from ..kb.model import Rule, Tombstone
from ..text import find_quote, normalize, registry

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
    violations = shacl.validate(kb2, documents)
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
    """Dates a set of quotes supports: (valid_from candidates, valid_until candidates)."""
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
    rep = static.check(kb2, omega, policies, adopted)
    errs = [f"{f.kind} {', '.join(f.ids)} {f.fact}: {f.detail}" for f in rep.errors]
    warns = [f"{f.kind} {', '.join(f.ids)} {f.fact}: {f.detail}" for f in rep.warnings]
    return GateResult("G3", not errs, errs[:20], warns)


# ---------------------------------------------------------------------- start of effect s(u)
def effect_start(base, delta):
    """s(u) per element id and s(Delta) (akuisisi.md 4)."""
    out = {}
    content_keys = ("expression", "condition", "value", "rows", "rows_ref", "layer", "modality", "scope",
                    "overrides", "assertion", "produces", "fixed_point", "table_kind", "name")
    for e in delta["add"]:
        if e["kind"] == "fact":                # vocabulary: no validity, no effect of its own
            continue
        out[e["id"]] = _d(e.get("valid_from")) or date(2009, 1, 1)
    for e in delta["change"]:
        if e["kind"] == "fact":
            continue
        prev = [r for r in base.history(e["id"]) if not isinstance(r, Tombstone)]
        p = prev[-1] if prev else None
        new_vf, new_vu = _d(e.get("valid_from")), _d(e.get("valid_until"))
        if p is None:
            out[e["id"]] = new_vf or date(2009, 1, 1)
            continue
        old_vf, old_vu = p.valid_from, p.valid_until
        from ..kb.serialize import record_to_json
        old_json = record_to_json(p)
        content_changed = any(_norm(old_json.get(k)) != _norm(e.get(k)) for k in content_keys if k in e or k in old_json)
        if content_changed:
            out[e["id"]] = min(x for x in (old_vf, new_vf) if x) if (old_vf or new_vf) else date(2009, 1, 1)
        else:
            out[e["id"]] = _sym_diff_start(old_vf, old_vu, new_vf, new_vu)
    for e in delta["remove"]:
        prev = [r for r in base.history(e["id"]) if not isinstance(r, Tombstone)]
        out[e["id"]] = (prev[-1].valid_from if prev and prev[-1].valid_from else date(2009, 1, 1))
    return out, (min(out.values()) if out else None)


def closing_only(base, e):
    """Change that only shortens validity (sets or moves valid_until earlier)."""
    prev = [r for r in base.history(e["id"]) if not isinstance(r, Tombstone)]
    if not prev:
        return False
    from ..kb.serialize import record_to_json
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


# ---------------------------------------------------------------------- observations on S^G
def observe(kb, case, omega, extra=()):
    """(observations {(month or 0 for year facts, fact): value}, conflict keys, errors) on F_nilai, plus the extra
    facts given (for a policy update: the facts the policy defines, its own payroll outputs)."""
    from ..engine import evaluate_case
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
    name it, so A3t/A3w do not apply; only new engine errors are checked (akuisisi.md 4, G4 for the company layer)."""
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
                            f"effect {s_delta} (A3t): {o0.get((m, f))} -> {v}")
                break
        p1, _, _, _ = evals.get("K'", kb2, i, early)
        p0, _, _, _ = evals.get("K", base, i, early)
        if p1 != p0:
            diff = next(k for k in p1 if p1.get(k) != p0.get(k))
            msgs.append(f"{case['case_id']} y{case['tax_year']} {diff}: changed one day before the issue date (A3w)")
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
            msgs.append(f"{e['id']}: no effect on any S^G case (vacuous element)")
    view0 = base.view(late)
    dead = {f.ids[0] for f in static.check(base, late).findings if f.kind == "dead"}
    for e in delta["remove"]:
        fired = e["id"] in dead
        for i in range(n) if not fired else []:
            from ..engine import evaluate_case
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
            from .sg import YEARS      # S^G covers these tax years; an earlier start shows from the first covered month
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
                msgs.append(f"stated effective date {eff} is not reflected: no S^G case changes in that month")
    for s in (relevance or {}).get("subjects", []):
        if s.get("kind") != "klu":
            continue
        # the subject names codes ("14111") or describes a set ("codes in Lampiran A"): only named five-digit codes
        # can be checked, and one of them must appear in a changed case
        codes = set(re.findall(r"(?<!\d)\d{5}(?!\d)", str(s.get("value"))))
        if codes and not any(sgset.cases[i]["employer"].get("klu") in codes for i in changed):
            msgs.append(f"stated subject KLU {', '.join(sorted(codes))} is not reflected in a changed S^G case")
    return GateResult("G5", not msgs, msgs)
