"""The data the knowledge base asks for, read from the knowledge base itself.

- Which data: the rules in force in each month (regulation layer plus the chosen company policy, as known on the chosen
  date) read case data with income('x'), benefit('x'), hr('x'), employee('x'), employer('x'), case('x') and
  zakat_paid(). A new rule that reads new data adds it; data no longer read disappears.
- How to ask for it: input definitions (label, help, type, options, valid from/until, ...). They are part of the
  knowledge base: the initial ones in kb_ext/input_defs.json, later ones carried by the approved update that first
  reads the data (kb_ext/pending/<document>.json, or the draft's own definitions). There is no list of data in this
  code.
- Data without a definition still appears, under its technical name, with a type guessed from how the rules use it
  (compared with text -> choice of those texts; compared with 1/True -> yes/no; otherwise a number).
"""
import json
import re
from datetime import date
from pathlib import Path

import streamlit as st

import data as d
import demo

EXT = Path(__file__).resolve().parent / "kb_ext"
CALL = re.compile(r"\b(income|benefit|hr|employee|employer|case)\('([a-z_0-9]+)'\)")
MONTHS = range(1, 13)


def _iso(x):
    return date.fromisoformat(x) if x else None


@st.cache_data
def _defs(signature):
    """{key: [definitions, oldest first]} from the initial file and the approved updates."""
    out = {}
    for df in json.loads((EXT / "input_defs.json").read_text(encoding="utf-8"))["defs"]:
        out.setdefault(df["key"], []).append(dict(df, origin="keadaan awal"))
    for a in demo.load()["approved"]:
        for df in a.get("inputs") or []:
            out.setdefault(df["key"], []).append(dict(df, origin=a["title"]))
    return out


def pending_defs(pid):
    p = EXT / "pending" / f"{pid}.json"
    return json.loads(p.read_text(encoding="utf-8"))["defs"] if p.exists() else []


def definition(key, at=None):
    """The definition valid at a date (the latest one if none is valid then), or None."""
    versions = _defs(demo.signature()).get(key)
    if not versions:
        return None
    at = at or demo.TODAY
    live = [v for v in versions if (not v.get("valid_from") or _iso(v["valid_from"]) <= at)
            and (not v.get("valid_until") or at <= _iso(v["valid_until"]))]
    return (live or versions)[-1]


def retired(key, at):
    df = definition(key, at)
    return bool(df and df.get("valid_until") and _iso(df["valid_until"]) < at)


# ---------------------------------------------------------------- which data, from the rules
def _texts(r):
    return d.expr_text(r.expression) + " " + (d.expr_text(r.condition) if r.condition else "")


@st.cache_data
def _discover(signature, year, policy, omega):
    """{key: {"months": [..], "layer": .., "rules": [..]}} for the rules in force in each month of the year."""
    kb = demo.kb()
    found = {}
    for r in kb.view(omega).rules.values():
        if r.layer == "company" and r.policy != policy:
            continue
        months = [m for m in MONTHS if (not r.valid_from or r.valid_from <= _month_end(year, m))
                  and (not r.valid_until or r.valid_until >= date(year, m, 1))]
        if not months:
            continue
        text = _texts(r)
        keys = {f"{b}.{k}" for b, k in CALL.findall(text)}
        if "zakat_paid()" in text:
            keys.add("zakat.zakat")
        for key in keys:
            e = found.setdefault(key, {"months": set(), "layer": r.layer, "rules": []})
            e["months"] |= set(months)
            e["rules"].append(r.id)
            if r.layer == "company":
                e["layer"] = "company"
    return {k: dict(v, months=sorted(v["months"])) for k, v in found.items()}


def _month_end(year, m):
    import calendar
    return date(year, m, calendar.monthrange(year, m)[1])


def discover(year, policy=None, omega=None):
    return _discover(demo.signature(), year, policy or None, omega or demo.TODAY)


def years():
    """Tax years the knowledge base can be asked about (from the rules' own dates, last four)."""
    last = max(demo.known_until().year + 1, demo.TODAY.year)
    return list(range(last - 3, last + 1))


# ---------------------------------------------------------------- how to ask, from the definitions
@st.cache_data
def _usage(signature):
    """For every key: texts it is compared with, and whether it is compared with 1/True (yes/no)."""
    texts, flags = {}, set()
    for r in demo.kb().view(demo.TODAY).rules.values():
        t = _texts(r)
        for b, k, lit in re.findall(r"\b(income|benefit|hr|employee|employer|case)\('([a-z_0-9]+)'\)\s*[!=]=\s*'([^']*)'", t):
            texts.setdefault(f"{b}.{k}", set()).add(lit)
        for b, k in re.findall(r"\b(income|benefit|hr|employee|employer|case)\('([a-z_0-9]+)'\)\s*[!=]=\s*(?:1\b|True|False)", t):
            flags.add(f"{b}.{k}")
    return {k: sorted(v) for k, v in texts.items()}, flags


def label(key, at=None):
    df = definition(key, at)
    return df["label"] if df else key.split(".", 1)[1].replace("_", " ")


def help_text(key, at=None):
    df = definition(key, at)
    if df:
        return (df.get("help") or "") + (f"\n\nSumber: {df['source']}" if df.get("source") else "")
    return "Definisi data ini belum ada di knowledge base: nama dan tipenya diambil dari aturan yang membacanya."


def kind(key, at=None):
    df = definition(key, at)
    if df:
        return df["type"]
    texts, flags = _usage(demo.signature())
    if key in texts:
        return "choice"
    if key in flags:
        return "flag" if key.startswith("hr.") else "bool"
    return "money" if key.split(".")[0] in ("income", "benefit", "zakat") else "int"


def options(key, year):
    """[(value, label)] for a choice."""
    df = definition(key, date(year, 1, 1)) or {}
    if df.get("options"):
        return [tuple(o) for o in df["options"]]
    src = df.get("options_from") or "usage"
    if src.startswith("table:"):
        names = df.get("labels") or {}
        return [(k, names.get(k, k)) for k in table_keys(src.split(":", 1)[1], year)]
    texts, _ = _usage(demo.signature())
    return [(t, t) for t in texts.get(key, [])]


def table_keys(name, year):
    at = date(year, 1, 1)
    best = None
    for r in demo.kb().records:
        if r.kind == "table" and r.name == name and r.valid_from and r.valid_from <= date(year, 12, 31) \
                and (not r.valid_until or r.valid_until >= at) and (best is None or r.seq > best.seq):
            best = r
    return [row.get("key") for row in (best.rows or [])] if best else []


def default(key, at=None):
    df = definition(key, at)
    return df.get("default") if df else None


def has_def(key):
    return definition(key) is not None


def component_kinds(year, policy=None, omega=None):
    """What a company pay component can be: monthly money data read by rules this year, labelled by definition."""
    found = discover(year, policy, omega)
    keys = [k for k in found if k.split(".")[0] in ("income", "benefit", "zakat") and kind(k) == "money"]
    return sorted(keys, key=lambda k: ((definition(k) or {}).get("order", 99), label(k)))


def monthly_data(year, policy=None, omega=None):
    """Monthly data that is not money (asked as its own column): HR data read by rules."""
    found = discover(year, policy, omega)
    keys = [k for k in found if k.startswith("hr.")]
    return sorted(keys, key=lambda k: ((definition(k) or {}).get("order", 99), label(k)))


def profile_fields(group, year, policy=None, omega=None):
    """Employee (group 'pegawai') or employer ('perusahaan') data read by rules this year, core ones first."""
    found = discover(year, policy, omega)
    buckets = ("employee", "case") if group == "pegawai" else ("employer",)
    keys = [k for k in found if k.split(".")[0] in buckets]
    return sorted(keys, key=lambda k: (not (definition(k) or {}).get("core"), (definition(k) or {}).get("order", 99), k))


@st.cache_data
def _input_rules(signature):
    out = {}
    for r in demo.kb().view(demo.TODAY).rules.values():
        m = re.fullmatch(r"\s*(income|benefit|hr|employee|employer|case)\('([a-z_0-9]+)'\)\s*", d.expr_text(r.expression))
        if m:
            out[f"{m.group(1)}.{m.group(2)}"] = (r.id, r.produces)
    return out


def input_rules():
    """{data key: (id of the rule that reads it as is, fact it produces)}."""
    return _input_rules(demo.signature())


def input_fact(key):
    """The fact an input rule turns this data into (income('thr') -> thr), if any."""
    for r in demo.kb().view(demo.TODAY).rules.values():
        if d.expr_text(r.expression).strip() == f"{key.split('.')[0]}('{key.split('.', 1)[1]}')":
            return r.produces
    return None


def policy_computed(year, policy, omega=None):
    """{key: fact} for data whose value the chosen company policy computes this year (read from the rules)."""
    if not policy:
        return {}
    out = {}
    produced = {r.produces for r in demo.kb().view(omega or demo.TODAY).rules.values()
                if r.layer == "company" and r.policy == policy
                and (not r.valid_from or r.valid_from <= date(year, 12, 31))
                and (not r.valid_until or r.valid_until >= date(year, 1, 1))}
    for key in discover(year, policy, omega):
        f = input_fact(key)
        if f and f in produced:
            out[key] = f
    return out
