"""The PPh 21 calculator: one employee, one grid of monthly values, and the result explained by the rules.

Everything the screen asks for comes from the knowledge base. The data to ask for is the case data that the rules in
force read (income('x'), benefit('x'), hr('x'), employee('x'), employer('x'), case('x'), zakat_paid()); how to ask for
it comes from input definitions (data/presets/input_defs.json for the starting knowledge base, later ones carried by
the approved update that first reads the data). Data without a definition still appears, under its technical name,
with a type guessed from how the rules use it.

An employee record holds the admin's words: profile and company fields by data key, company pay components by name,
and one grid of values per month (columns: component names, and "data:<key>" for non-money data such as HR data). Pay
components are mapped to knowledge-base data through the company catalog, so a record stays valid when the knowledge
base changes. The result cards are read from the engine trace: the steps under the PPh 21 of a month are the facts the
winning rules' formulas read, and the results shown are the facts the knowledge base marks as output, so a new
component or way of computing the tax shows up without changing this module.
"""
import calendar
import copy
import json
import re
from datetime import date, datetime

import pandas as pd
import streamlit as st

import common
import state
from pph21kbs import config

ROOT = "pph21_due"          # the value the calculator is for: the PPh 21 withheld in a month
CALL = re.compile(r"\b(income|benefit|hr|employee|employer|case)\('([a-z_0-9]+)'\)")
MONTH_NUMBERS = range(1, 13)
BASE_ORIGIN = "starting knowledge base"      # origin of the input definitions shipped with the starting knowledge base
DEFAULT_SCENARIO = "Employee A: operator, 1 year of service"
WITHHELD = "PPh 21 already withheld"         # grid column for PPh 21 actually withheld


# ====================================================================================================================
# Input definitions
# ====================================================================================================================
def _iso(x):
    return date.fromisoformat(x) if x else None


@st.cache_data
def _defs(signature):
    """{key: [definitions, oldest first]} from the starting file and the approved updates."""
    out = {}
    for df in json.loads((config.PRESETS / "input_defs.json").read_text(encoding="utf-8"))["defs"]:
        out.setdefault(df["key"], []).append(dict(df, origin=BASE_ORIGIN))
    for a in state.load()["approved"]:
        for df in a.get("inputs") or []:
            out.setdefault(df["key"], []).append(dict(df, origin=a["title"]))
    return out


def definition(key, at=None):
    """The definition valid at a date (the latest one if none is valid then), or None."""
    versions = _defs(state.signature()).get(key)
    if not versions:
        return None
    at = at or state.TODAY
    live = [v for v in versions if (not v.get("valid_from") or _iso(v["valid_from"]) <= at)
            and (not v.get("valid_until") or at <= _iso(v["valid_until"]))]
    return (live or versions)[-1]


def retired(key, at):
    df = definition(key, at)
    return bool(df and df.get("valid_until") and _iso(df["valid_until"]) < at)


# ====================================================================================================================
# Which data the rules read
# ====================================================================================================================
def _texts(r):
    return state.expr_text(r.expression) + " " + (state.expr_text(r.condition) if r.condition else "")


@st.cache_data
def _discover(signature, year, policy, omega):
    """{key: {"months": [..], "layer": .., "rules": [..]}} for the rules in force in each month of the year."""
    kb = state.kb()
    found = {}
    for r in kb.view(omega).rules.values():
        if r.layer == "company" and r.policy != policy:
            continue
        months = [m for m in MONTH_NUMBERS if (not r.valid_from or r.valid_from <= _month_end(year, m))
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
    return date(year, m, calendar.monthrange(year, m)[1])


def discover(year, policy=None, omega=None):
    return _discover(state.signature(), year, policy or None, omega or state.TODAY)


def years():
    """The four tax years the calculator offers, up to the later of this year and the year after the date the
    knowledge base is known until."""
    last = max(state.known_until().year + 1, state.TODAY.year)
    return list(range(last - 3, last + 1))


# ====================================================================================================================
# How to ask for the data
# ====================================================================================================================
@st.cache_data
def _usage(signature):
    """For every key: texts it is compared with, and whether it is compared with 1/True (yes/no)."""
    texts, flags = {}, set()
    for r in state.kb().view(state.TODAY).rules.values():
        t = _texts(r)
        for b, k, lit in re.findall(r"\b(income|benefit|hr|employee|employer|case)\('([a-z_0-9]+)'\)\s*[!=]=\s*"
                                    r"'([^']*)'", t):
            texts.setdefault(f"{b}.{k}", set()).add(lit)
        for b, k in re.findall(r"\b(income|benefit|hr|employee|employer|case)\('([a-z_0-9]+)'\)\s*[!=]=\s*"
                               r"(?:1\b|True|False)", t):
            flags.add(f"{b}.{k}")
    return {k: sorted(v) for k, v in texts.items()}, flags


def label(key, at=None):
    df = definition(key, at)
    return df["label"] if df else state.fact_label(key.split(".", 1)[1])     # else the label of the fact of that name


def help_text(key, at=None):
    df = definition(key, at)
    if df:
        return (df.get("help") or "") + (f"\n\nSource: {df['source']}" if df.get("source") else "")
    return ("This data has no definition in the knowledge base yet: its name and type are taken from the rules that "
            "read it.")


def kind(key, at=None):
    df = definition(key, at)
    if df:
        return df["type"]
    texts, flags = _usage(state.signature())
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
    texts, _ = _usage(state.signature())
    return [(t, t) for t in texts.get(key, [])]


def table_keys(name, year):
    at = date(year, 1, 1)
    best = None
    for r in state.kb().records:
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
    """Employee (group 'employee') or employer ('employer') data read by rules this year, core ones first."""
    found = discover(year, policy, omega)
    buckets = ("employee", "case") if group == "employee" else ("employer",)
    keys = [k for k in found if k.split(".")[0] in buckets]
    return sorted(keys, key=lambda k: (not (definition(k) or {}).get("core"), (definition(k) or {}).get("order", 99),
                                       k))


@st.cache_data
def _input_rules(signature):
    out = {}
    for r in state.kb().view(state.TODAY).rules.values():
        m = re.fullmatch(r"\s*(income|benefit|hr|employee|employer|case)\('([a-z_0-9]+)'\)\s*",
                         state.expr_text(r.expression))
        if m:
            out[f"{m.group(1)}.{m.group(2)}"] = (r.id, r.produces)
    return out


def input_rules():
    """{data key: (id of the rule that reads it as is, fact it produces)}."""
    return _input_rules(state.signature())


# ====================================================================================================================
# Employee record and engine case
# ====================================================================================================================
def _company_file():
    return json.loads((config.PRESETS / "catalog.json").read_text(encoding="utf-8"))


def company():
    """The sample company the calculator's employer data belongs to: {name, about}, or {}."""
    return _company_file().get("company") or {}


def catalog():
    """{component name: data key}: the company's pay components (the shipped ones plus those added in the app)."""
    out = {c["name"]: c["key"] for c in _company_file()["components"]}
    out.update({c["name"]: c["key"] for c in state.load()["catalog"]})
    return out


def scenarios():
    return {s["title"]: s
            for s in json.loads((config.PRESETS / "scenarios.json").read_text(encoding="utf-8"))["scenarios"]}


def _fill(spec, months):
    """{month: value} from a scenario value spec: from (carried forward), once, inc (counts up by 1 each month)."""
    out = {}
    carry = {int(k): v for k, v in (spec.get("from") or {}).items()}
    months = list(months)
    before = [k for k in carry if months and k <= months[0]]
    cur = carry[max(before)] if before else None
    for m in months:
        if m in carry:
            cur = carry[m]
        if cur is not None:
            out[m] = cur
    for k, v in (spec.get("once") or {}).items():
        if int(k) in months:
            out[int(k)] = v
    for k, v in (spec.get("inc") or {}).items():
        for i, m in enumerate(x for x in months if x >= int(k)):
            out[m] = v + i
    return out


def from_scenario(sc):
    months = range(sc["start"], sc["end"] + 1)
    cells = {m: {} for m in months}
    for name, spec in sc["values"].items():
        for m, v in _fill(spec, months).items():
            cells[m][name] = v
    for key, spec in sc["data"].items():
        for m, v in _fill(spec, months).items():
            cells[m][f"data:{key}"] = v
    return {"name": sc["name"], "year": sc["year"], "month": sc["month"], "start": sc["start"], "end": sc["end"],
            "policy": sc["policy"], "fields": dict(sc["fields"]), "components": list(sc["components"]),
            "grid": {str(m): r for m, r in cells.items()}, "withheld": dict(sc["withheld"]), "scenario": sc["title"],
            "component_keys": {c["name"]: c["key"] for c in sc.get("extra_components", [])}}


def ensure_components(sc):
    """Scenario components missing from the catalog are added (company data, kept until Start over in the version
    history of Knowledge base management)."""
    cat = catalog()
    for c in sc.get("extra_components", []):
        if c["name"] not in cat:
            state.add_component(c["name"], c["key"])


def cell(rec, m, col):
    return (rec["grid"].get(str(m)) or {}).get(col)


def to_case(rec, policy_installed=True, employer_pays_tax=False):
    """The engine case: the months from the start up to the month asked for (the engine knows the final month from the
    employment end and gives the year values only when it is reached). PPh 21 the admin says was actually withheld is
    sent as a recorded value; when the employer pays the tax (gross-up, borne by the employer, or a company policy
    that makes it so) the tax allowance of that month equals it and is recorded with it."""
    cat = {**rec.get("component_keys", {}), **catalog()}
    year, start, end = rec["year"], rec["start"], max(rec["end"], rec["start"])
    asked = min(max(rec["month"], start), end)
    periods = []
    for m in range(start, asked + 1):
        p = {"month": m, "income": {}, "benefits": {}, "hr": {}, "zakat": 0}
        for col, v in (rec["grid"].get(str(m)) or {}).items():
            if v in (None, "", 0, False):
                continue
            key = col[5:] if col.startswith("data:") else cat.get(col)
            if not key:
                continue
            b, k = key.split(".", 1)
            if b == "zakat":
                p["zakat"] += int(v)
            elif b in ("income", "benefit"):
                bucket = p["income" if b == "income" else "benefits"]
                bucket[k] = bucket.get(k, 0) + int(v)
            elif b == "hr":
                p["hr"][k] = int(v) if isinstance(v, (bool, int, float)) else str(v)
        w = rec["withheld"].get(str(m))
        if w is not None and m < end:
            p["recorded"] = {"pph21_due": int(w)}
            if employer_pays_tax:
                p["recorded"]["tax_allowance"] = int(w)
        periods.append(p)
    emp, er, method = {}, {"policy": rec.get("policy") if policy_installed else None}, "gross"
    for key, v in rec["fields"].items():
        if v is None or v == "":
            continue
        b, k = key.split(".", 1)
        if b == "employee":
            emp[k] = v
        elif b == "employer":
            er[k] = v
        elif key == "case.method":
            method = v
    return {"case_id": rec["name"] or "employee", "tax_year": year, "method": method, "employee": emp, "employer": er,
            "employment": {"start_month": start, "end_month": end}, "periods": periods}


def scenario_case(sc):
    rec = from_scenario(sc)
    return to_case(rec, policy_installed=bool(sc.get("policy")) and sc["policy"] in state.installed_policies())


def copy_record(rec):
    return copy.deepcopy(rec)


# ====================================================================================================================
# How a result was computed (from the knowledge base and the engine trace)
# ====================================================================================================================
@st.cache_resource(max_entries=2)
def _view(signature, omega):
    return state.kb().view(omega)


def view(omega):
    return _view(state.signature(), omega)


def rule(r, key, omega):
    t = (r.trace or {}).get(key)
    return view(omega).rules.get(t["rule"]) if t else None


def children(r, key, omega):
    """(fact, month) read directly by the formula of the rule that gave this value, in the order the formula names
    them. Year facts are read at month 0. Only values the engine computed for this case."""
    rl = rule(r, key, omega)
    if rl is None or rl.expression is None:
        return []
    text = rl.expression.text
    out = []
    for f in sorted(rl.expression.dependencies(), key=lambda f: (text.find(f) if f in text else len(text), f)):
        fd = view(omega).facts.get(f)
        k = (f, 0 if fd is not None and fd.fact_scope == "year" else key[1])
        if k in r.trace and k != key:
            out.append(k)
    return out


def value(r, key):
    t = (r.trace or {}).get(key)
    return t["value"] if t else None


def working(r, key, omega):
    """Skip rules that only pass one value on unchanged (the PPh 21 of the month = the PPh 21 of the final month):
    the rule that does the work."""
    seen = {key}
    while True:
        kids = [k for k in children(r, key, omega) if value(r, k) not in (None, 0, False, "")]
        if len(kids) == 1 and value(r, kids[0]) == value(r, key) and kids[0] not in seen:
            key = kids[0]
            seen.add(key)
            continue
        return key


def _number(v):
    return v not in (None, 0) and not isinstance(v, (bool, str))


def is_input(r, key):
    t = (r.trace or {}).get(key)
    return bool(t) and any(s.get("document") == "INPUT-CONVENTION" for s in t.get("source") or [])


def ladder(r, key, omega, scope_month=0, depth=8):
    """Post-order list of (key, depth) of the year values under key: the steps of the year calculation from the first
    one to the result. Stops at values of a single month (they are sums of months, shown as one line)."""
    out, seen = [], set()

    def go(k, level):
        if k in seen or level > depth:
            return
        seen.add(k)
        for c in children(r, k, omega):
            if c[1] == scope_month and value(r, c) not in (None, 0, ""):
                go(c, level + 1)
        out.append((k, level))
    go(key, 0)
    return out


def downstream(r, month, omega, source=ROOT):
    """Facts of the month that the knowledge base marks as output and whose rules read the source value, directly or
    through other values of the month (e.g. PPh 21 borne by the government, take-home pay)."""
    facts = view(omega).facts
    readers = {}
    for (f, m), t in r.trace.items():
        if m == month:
            for c in children(r, (f, m), omega):
                readers.setdefault(c[0], set()).add(f)
    found, todo = set(), [source]
    while todo:
        for f in readers.get(todo.pop(), ()):
            if f not in found:
                found.add(f)
                todo.append(f)
    return [f for f in sorted(found, key=lambda f: facts[f].seq if f in facts else 0)
            if f in facts and facts[f].output and (f, month) in r.trace]


def outputs(r, months, omega):
    """Output facts of a month (as the knowledge base marks them) that are non-zero in some of the months, in
    knowledge-base order."""
    facts = view(omega).facts
    names = {f for m in months for f, v in (r.periods.get(m) or {}).items() if _number(v)}
    return [f for f in sorted(names, key=lambda f: facts[f].seq if f in facts else 0)
            if f in facts and facts[f].output]


def source_of(r, key):
    t = (r.trace or {}).get(key)
    s = (t or {}).get("source") or []
    return s[0] if s else None


# ====================================================================================================================
# Calculator page: engine case and record state
# ====================================================================================================================
def case_of(rec, omega):
    """The case for the engine. When PPh 21 actually withheld is recorded and the employer pays the tax (method, or a
    company policy that sets it, read from the engine), the tax allowance of that month is recorded with it."""
    installed = rec.get("policy") in state.installed_policies()
    case = to_case(rec, policy_installed=installed)
    if not rec["withheld"]:
        return case
    r0, _ = state.compute(case, omega)
    method = (state.value(r0, "withholding_method") if r0 else None) or case["method"]
    pays = method != "gross" or bool(r0 and any(r0.periods[m].get("tax_allowance") for m in r0.periods))
    return to_case(rec, policy_installed=installed, employer_pays_tax=pays)


def _norm(rec):
    """The record as text, with empty cells left out (an empty cell and 0 mean the same)."""
    r = dict(rec)
    r["grid"] = {m: {c: v for c, v in row.items() if v not in (None, "", 0, False)} for m, row in rec["grid"].items()}
    r["grid"] = {m: row for m, row in r["grid"].items() if row}
    return json.dumps(r, sort_keys=True, default=str)


def _load(rec, origin):
    s = st.session_state
    s.rec = copy_record(rec)
    s.rec_origin = origin                      # ("scenario", title) or ("saved", name)
    s.rec_clean = _norm(s.rec)
    s.rec_ver = s.get("rec_ver", 0) + 1


def _dirty():
    s = st.session_state
    return _norm(s.rec) != s.get("rec_clean")


def _apply_scenario(title):
    sc = scenarios()[title]
    ensure_components(sc)
    _load(from_scenario(sc), ("scenario", title))


def _on_scenario():
    s = st.session_state
    title = s.get("k_scn_pick")
    if not title:
        return
    if _dirty():
        s.k_scn_pending = title
    else:
        _apply_scenario(title)
    s.k_scn_pick = None


def _on_open():
    s = st.session_state
    name = s.get("k_open_pick")
    saved = state.load()["employees"].get(name)
    if saved:
        _load(saved["record"], ("saved", name))
    s.k_open_pick = None


def _save(name):
    s = st.session_state
    s.rec["name"] = name
    r, _ = state.compute(case_of(s.rec, s.k_omega_v), s.k_omega_v)
    found = discover(s.rec["year"], s.rec.get("policy"), s.k_omega_v)
    state.save_employee(name, {"record": s.rec, "saved": datetime.now().strftime("%d/%m/%Y %H:%M"),
                               "approved": len(state.load()["approved"]),
                               "last": {str(m): r.periods[m].get("pph21_due") for m in r.periods} if r else {},
                               "keys": sorted(found)})
    s.rec_origin = ("saved", name)
    s.rec_clean = _norm(s.rec)


# ====================================================================================================================
# Top bar and period
# ====================================================================================================================
def top_bar():
    s = st.session_state
    rec = s.rec
    saved = state.load()["employees"]
    c = st.columns([1.3, 1.3, 1, 1])
    who = rec["name"] or "New employee"
    origin = s.rec_origin
    c[0].markdown(f"**{who}**{' ●' if _dirty() else ''}  \n<span class='muted'>"
                  + ("from scenario: " + origin[1] if origin[0] == "scenario" else "saved employee") + "</span>",
                  unsafe_allow_html=True, help="● = there are unsaved changes.")
    c[1].selectbox("Fill with a common scenario", list(scenarios()), index=None, key="k_scn_pick",
                   placeholder="Pick a scenario…", on_change=_on_scenario,
                   help="Fills this form with a complete example; everything can be changed afterwards.")
    c[2].selectbox("Open a saved employee", list(saved), index=None, key="k_open_pick", placeholder="Pick…",
                   on_change=_on_open, disabled=not saved)
    with c[3]:
        st.write("")
        with st.popover("Save", icon=":material/save:", width="stretch"):
            name = st.text_input("Employee name", rec["name"], key=f"k_save_name_{s.rec_ver}")
            if st.button("Save", type="primary", key="k_save_btn") and name.strip():
                _save(name.strip())
                st.rerun()
    if s.get("k_scn_pending"):
        with st.container(border=True):
            st.warning(f"There are unsaved changes. Fill the form with the scenario **{s.k_scn_pending}**?",
                       icon=":material/warning:")
            b1, b2, _ = st.columns([1, 1, 3])
            if b1.button("Yes, replace", type="primary"):
                _apply_scenario(s.k_scn_pending)
                s.k_scn_pending = None
                st.rerun()
            if b2.button("Cancel"):
                s.k_scn_pending = None
                st.rerun()
    sc = scenarios().get(origin[1]) if origin[0] == "scenario" else None
    if sc:
        st.caption(f"**{sc['title']}**: {sc['note']}")


def period_bar():
    s = st.session_state
    rec = s.rec
    v = s.rec_ver
    c = st.columns(5)
    ys = years()
    rec["year"] = c[0].selectbox("Tax year", ys, index=ys.index(rec["year"]) if rec["year"] in ys else len(ys) - 2,
                                 key=f"k_year_{v}")
    rec["start"] = c[1].selectbox("Started work", range(1, 13), index=rec["start"] - 1, key=f"k_start_{v}",
                                  format_func=lambda m: state.MONTHS[m - 1], help="The first month paid this year.")
    ends = list(range(rec["start"], 13))
    rec["end"] = c[2].selectbox("Works until", ends,
                                index=ends.index(rec["end"]) if rec["end"] in ends else len(ends) - 1,
                                key=f"k_end_{v}", format_func=lambda m: "December (still employed)" if m == 12
                                else state.MONTHS[m - 1] + " (leaves)",
                                help="The month of leaving becomes the final month: the tax of the year is "
                                     "recalculated in that month.")
    months = list(range(rec["start"], rec["end"] + 1))
    rec["month"] = c[3].selectbox("Calculate up to", months,
                                  index=months.index(rec["month"]) if rec["month"] in months else len(months) - 1,
                                  key=f"k_month_{v}",
                                  format_func=lambda m: state.MONTHS[m - 1] + (" · final" if m == rec["end"] else ""),
                                  help="Results are shown from the first month to this month. The annual "
                                       "recalculation appears only in the final month (December or the month of "
                                       "leaving).")
    s.k_omega_v = c[4].date_input("Rules as of", state.TODAY, key="k_omega",
                                  help=common.tip("knowledge date") + " The knowledge base is known up to "
                                       f"{state.fmt_date(state.known_until())}.")


# ====================================================================================================================
# Employee and company (asked for as the knowledge base defines)
# ====================================================================================================================
def _field(key, rec, year, v):
    tp = kind(key)
    lab = label(key)
    df = definition(key) or {}
    if df.get("show_if"):
        for k2, val in df["show_if"].items():
            if rec["fields"].get(k2) != val:
                return
    if df.get("origin", BASE_ORIGIN) != BASE_ORIGIN:
        lab += f" · new ({df['origin']})"
    if not has_def(key):
        lab += " ⚠"
    cur = rec["fields"].get(key, default(key))
    wkey = f"k_f_{key}_{v}"
    hp = help_text(key)
    if tp == "choice":
        opts = options(key, year)
        values = [o[0] for o in opts]
        names = dict(opts)
        val = st.selectbox(lab, values, index=values.index(cur) if cur in values else 0, key=wkey,
                           format_func=lambda x: names.get(x, x), help=hp) if values else None
    elif tp in ("bool", "flag"):
        val = st.toggle(lab, bool(cur), key=wkey, help=hp)
    elif tp == "text":
        val = st.text_input(lab, cur or "", key=wkey, help=hp)
    else:
        val = st.number_input(lab, 0, 10**11, int(cur) if cur not in (None, "") else None, key=wkey, help=hp,
                              placeholder="empty", step=1 if tp == "int" else 100_000)
    rec["fields"][key] = val


def profile():
    s = st.session_state
    rec, v = s.rec, s.rec_ver
    year, omega = rec["year"], s.k_omega_v
    with st.expander("Employee and company", expanded=True):
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("**Employee**")
            rec["name"] = st.text_input("Name", rec["name"], key=f"k_name_{v}")
            keys = profile_fields("employee", year, rec.get("policy"), omega)
            core = [k for k in keys if (definition(k) or {}).get("core")]
            more = [k for k in keys if k not in core]
            for k in core:
                _field(k, rec, year, v)
            with st.expander(f"Other employee data the rules read this year ({len(more)})"):
                st.caption("This list comes from the knowledge base: each item is read by at least one rule in force "
                           f"in {year}.")
                for k in more:
                    _field(k, rec, year, v)
        with right:
            st.markdown("**Company**")
            firm = company()
            if firm:
                st.caption(f"**{firm['name']}** · {firm.get('about', '')}")
            pols = state.installed_policies()
            opts = [""] + list(pols)
            cur = rec.get("policy") if rec.get("policy") in pols else ""
            pick = st.selectbox("Company policy", opts, index=opts.index(cur), key=f"k_pol_{v}",
                                format_func=lambda p: "None" if not p else f"{p} · {pols[p]}",
                                help=common.tip("company policy")
                                + " Only policies approved in Knowledge base management.")
            if rec.get("policy") and rec["policy"] not in pols:
                st.info(f"This form uses the policy **{rec['policy']}**, which is not in the knowledge base yet. "
                        "Approve it first in Knowledge base management; its data columns will then appear.",
                        icon=":material/info:")
            else:
                rec["policy"] = pick or None
            keys = profile_fields("employer", year, rec.get("policy"), omega)
            core = [k for k in keys if (definition(k) or {}).get("core")]
            more = [k for k in keys if k not in core]
            for k in core:
                _field(k, rec, year, v)
            klu = rec["fields"].get("employer.klu")
            if klu:
                lists = _lookup_tables("employer('klu')", year, omega)
                hit = [(n, rid) for n, rid in lists if klu in table_keys(n, year)]
                if not lists:
                    st.caption(f"No rule of {year} uses the KLU.")
                else:
                    def names(xs):
                        tabs = {n: state.table_at(n, date(year, 12, 31)) or state.table_at(n, date(year, 1, 1))
                                for n, _ in xs}
                        return ", ".join(f"'{(tabs[n].label if tabs[n] and tabs[n].label else n)}' ({rid})"
                                         for n, rid in xs)
                    st.caption(f"KLU {klu} " + (f"is in the list {names(hit)} of {year}." if hit else
                                                f"is not in the lists the rules of {year} use: {names(lists)}."))
            with st.expander(f"Other company data the rules read ({len(more)})"):
                for k in more:
                    _field(k, rec, year, v)


def _lookup_tables(read, year, omega):
    """(table, rule) for every table that a rule in force in the year looks this input up in, e.g. the KLU lists of
    the DTP rules. Read from the rules, so a new list in the knowledge base is found without changing the program."""
    lo, hi = date(year, 1, 1), date(year, 12, 31)
    out = []
    for r in state.kb().view(omega).rules.values():
        if (r.valid_from and r.valid_from > hi) or (r.valid_until and r.valid_until < lo):
            continue
        text = " ".join(e.text for e in (r.expression, r.condition) if e is not None)
        for name in re.findall(r"in_table\('([a-z0-9_]+)',\s*" + re.escape(read), text):
            out.append((name, r.id))
    return out


# ====================================================================================================================
# The grid of monthly values
# ====================================================================================================================
def _auto(key, r, shown):
    """When the rules compute this data in the months shown (the winning rule is not the one that reads the admin's
    input), its values and the rules that computed it; read from the engine's trace, so it follows the knowledge
    base."""
    entry = input_rules().get(key)
    if r is None or not entry:
        return None
    rid, fact = entry
    vals, by = {}, {}
    for m in shown:
        t = (r.trace or {}).get((fact, m))
        if t:
            vals[m] = int(t["value"] or 0)
            if t["rule"] != rid:
                by[t["rule"]] = t["layer"]
    return {"fact": fact, "vals": vals, "by": by} if by else None


def _columns(rec, omega, r):
    """[(col id, label, key, state)] state: edit | computed | unused | retired | nodef; and the computed values."""
    year, policy = rec["year"], rec.get("policy")
    cat = {**rec.get("component_keys", {}), **catalog()}
    found = discover(year, policy, omega)
    shown = list(range(rec["start"], rec["month"] + 1))
    cols, autos = [], {}
    for name in rec["components"]:
        key = cat.get(name)
        status = "edit"
        a = _auto(key, r, shown) if key else None
        if a:
            status, autos[name] = "computed", a
        elif key and retired(key, date(year, rec["month"], 1)):
            status = "retired"
        elif key not in found or not any(m in found[key]["months"] for m in shown):
            status = "unused"
        cols.append((name, name, key, status))
    mapped = {cat.get(n) for n in rec["components"]}
    for key in component_kinds(year, policy, omega):      # computed by the rules, not entered: shown, locked
        if key in mapped:
            continue
        a = _auto(key, r, shown)
        if a and any(a["vals"].values()):
            col = f"auto:{key}"
            autos[col] = a
            cols.append((col, state.fact_label(a["fact"]), key, "computed"))
    for key in monthly_data(year, policy, omega):
        cols.append((f"data:{key}", label(key), key, "edit" if has_def(key) else "nodef"))
    return cols, found, autos


def _range_note(found, key, shown):
    ms = [m for m in shown if key in found and m in found[key]["months"]]
    if not ms or len(ms) == len(shown):
        return ""
    return f" ({state.MON[ms[0] - 1]}–{state.MON[ms[-1] - 1]})"


def grid(prev_result):
    s = st.session_state
    rec, v = s.rec, s.rec_ver
    omega = s.k_omega_v
    shown = list(range(rec["start"], rec["month"] + 1))
    cols, found, autos = _columns(rec, omega, prev_result)
    with st.container(border=True):
        h1, h2, h3 = st.columns([3, 1, 1])
        span = f"{state.MONTHS[shown[0] - 1]}–{state.MONTHS[shown[-1] - 1]} {rec['year']}"
        h1.markdown(f"**Monthly details** · {span}")
        h1.caption("Double-click a cell to change the number, then press Enter. Amounts are recorded in the month they "
                   "are paid. The columns come from the company's pay components and the data the rules read this "
                   "year.")
        with h2.popover("Component", icon=":material/add:", width="stretch"):
            add_component(rec, shown)
        with h3.popover("Quick fill", icon=":material/auto_fix_high:", width="stretch"):
            quick_fill(rec, cols, shown)
        table, cfg = [], {"Month": st.column_config.TextColumn("Month", disabled=True)}
        for m in shown:
            row = {"Month": state.MONTHS[m - 1]}
            for col, lab, key, status in cols:
                tp = kind(key) if key else "money"
                if status == "computed":
                    row[col] = autos[col]["vals"].get(m, 0)
                else:
                    val = cell(rec, m, col)
                    row[col] = bool(val) if tp == "flag" else (val if tp == "choice" else (val or 0))
            row[WITHHELD] = rec["withheld"].get(str(m)) if m < rec["month"] else None
            table.append(row)
        for col, lab, key, status in cols:
            tp = kind(key) if key else "money"
            hp = help_text(key) if key else "This component is not mapped to knowledge-base data yet."
            if status == "computed":
                by = autos[col]["by"]
                who = ("company policy " + str(rec.get("policy"))) if "company" in by.values() else "the rules"
                title = f"{lab} ⚙"
                hp = (f"Computed automatically by {who} ({', '.join(list(by)[:3])}); it cannot be typed. To change "
                      "it, change the data that rule reads (e.g. the salary, the work risk, or HR data).")
            elif status == "unused":
                title = f"{lab} (not read by the rules)"
            elif status == "retired":
                title = f"{lab} (no longer used)"
            elif status == "nodef":
                title = f"{lab} ⚠"
            else:
                title = f"{lab} ✎" + _range_note(found, key, shown)
            dis = status == "computed"
            if tp == "flag":
                cfg[col] = st.column_config.CheckboxColumn(title, help=hp, disabled=dis)
            elif tp == "choice":
                cfg[col] = st.column_config.SelectboxColumn(title, help=hp, disabled=dis,
                                                            options=[o[0] for o in options(key, rec["year"])])
            else:
                cfg[col] = st.column_config.NumberColumn(title, help=hp, disabled=dis, min_value=0, format="localized",
                                                         step=1)
        cfg[WITHHELD] = st.column_config.NumberColumn(
            f"{WITHHELD} ✎", format="localized", min_value=0,
            help="Fill in only when the PPh 21 actually withheld that month differs from the system's calculation "
                 "(e.g. it was computed by an old system). Used in the final month.")
        sig = "|".join(c[0] for c in cols)
        auto_sig = hash(tuple(sorted((c, tuple(sorted(a["vals"].items()))) for c, a in autos.items())))
        gkey = f"k_grid_{v}_{rec['year']}_{rec['start']}_{rec['month']}_{hash(sig)}_{auto_sig}"
        # the editor keeps the user's edits relative to the data it was first given: give it the same data while its
        # key is the same; a new key (other columns, or new values computed by the rules) starts from the record
        if s.get("k_grid_base", (None,))[0] != gkey:
            s.k_grid_base = (gkey, table)
        frame = pd.DataFrame(s.k_grid_base[1])
        locked = [c[0] for c in cols if c[3] == "computed"]
        idle = [c[0] for c in cols if c[3] in ("unused", "retired")]
        styled = (frame.style
                  .set_properties(subset=["Month"], **{"background-color": "#f7f7f5", "font-weight": "600"})
                  .set_properties(subset=locked, **{"background-color": "#ecebe7", "color": "#6b6a66"})
                  .set_properties(subset=idle, **{"background-color": "#fff4d6", "color": "#8a6100"}))
        edited = st.data_editor(styled, key=gkey, hide_index=True, width="stretch", column_config=cfg)
        for m, (_, r) in zip(shown, edited.iterrows()):
            rowrec = rec["grid"].setdefault(str(m), {})
            for col, lab, key, status in cols:
                if status == "computed":
                    continue
                val = r[col]
                tp = kind(key) if key else "money"
                if tp == "flag":
                    rowrec[col] = 1 if val else 0
                elif tp == "choice":
                    rowrec[col] = val if isinstance(val, str) and val else None
                else:
                    rowrec[col] = int(val) if pd.notna(val) and val != "" else 0
            w = r[WITHHELD]
            if m < rec["month"] and pd.notna(w) and w != "":
                rec["withheld"][str(m)] = int(w)
            else:
                rec["withheld"].pop(str(m), None)
        if any(c[3] == "computed" for c in cols):
            st.caption("⚙ = computed automatically by the rules from other data; shown for reference, it cannot be "
                       "typed.")
    return cols, found, autos


def add_component(rec, shown):
    s = st.session_state
    year = rec["year"]
    cat = catalog()
    existing = [n for n in cat if n not in rec["components"]]
    mode = st.radio("Component", ["New", "From the company list"] if existing else ["New"], horizontal=True,
                    key="k_add_mode")
    if mode == "New":
        name = st.text_input("Component name", key="k_add_name", placeholder="e.g. Communication allowance")
        kinds = component_kinds(year, rec.get("policy"), s.k_omega_v)
        key = st.selectbox("What is it?", kinds, key="k_add_kind", format_func=label,
                           help="Pick the one closest to the nature of this component. The list comes from the data "
                                "the rules read this year; how it is taxed is decided by the rules, not by this "
                                "choice.")
        if key:
            st.caption(help_text(key))
    else:
        name = st.selectbox("Component", existing, key="k_add_existing")
        key = cat.get(name)
        st.caption(f"Mapped to: {label(key)}")
    c1, c2 = st.columns(2)
    amount = c1.number_input("Amount", 0, 10**11, 0, 50_000, key="k_add_value")
    start = c2.selectbox("From month", shown, key="k_add_start", format_func=lambda m: state.MONTHS[m - 1])
    repeat = st.checkbox("Paid every month from then on",
                         bool((definition(key) or {}).get("repeat")) if key else True, key=f"k_add_repeat_{key}")
    if st.button("Add", type="primary", key="k_add_btn", disabled=not (name and key)):
        if mode == "New":
            state.add_component(name, key)
        if name not in rec["components"]:
            rec["components"].append(name)
        for m in range(start, rec["end"] + 1):
            if m == start or repeat:
                rec["grid"].setdefault(str(m), {})[name] = int(amount)
        s.rec_ver += 1
        st.rerun()
    if rec["components"]:
        st.divider()
        keep = st.multiselect("Components shown", rec["components"], rec["components"],
                              key=f"k_keep_{s.rec_ver}")
        if st.button("Apply", key="k_keep_btn") and keep != rec["components"]:
            rec["components"] = keep
            s.rec_ver += 1
            st.rerun()


def quick_fill(rec, cols, shown):
    s = st.session_state
    editable = [c for c in cols if c[3] in ("edit", "nodef", "unused")]
    if not editable:
        st.caption("No column can be filled.")
        return
    labels = {c[0]: c[1] for c in editable}
    col = st.selectbox("Column", list(labels), format_func=labels.get, key="k_qf_col")
    key = next(c[2] for c in editable if c[0] == col)
    tp = kind(key) if key else "money"
    start = st.selectbox("From month", shown, key="k_qf_start", format_func=lambda m: state.MONTHS[m - 1])
    same, once, count = "Same value up to the last month", "This month only", "Up by 1 each month"
    mode = st.radio("How", [same, once] + ([count] if tp == "int" else []), key="k_qf_mode")
    amount = 1 if tp == "flag" else st.number_input("Value", 0, 10**11, 0, 1 if tp == "int" else 50_000,
                                                    key="k_qf_value")
    if st.button("Fill", type="primary", key="k_qf_btn"):
        for i, m in enumerate(range(start, rec["end"] + 1)):
            if mode == once and m != start:
                break
            rec["grid"].setdefault(str(m), {})[col] = int(amount) + (i if mode == count else 0)
        s.rec_ver += 1
        st.rerun()


# ====================================================================================================================
# Results
# ====================================================================================================================
def _fact_term(f):
    """The fact's label from the knowledge base, with a hover explanation when the glossary has one."""
    key = common.FOR_FACT.get(f)
    return common.term(key, state.fact_label(f)) if key else state.fact_label(f)


def _components(rec, cols, m):
    """Input fact -> names of the company components (and their values) that feed it in month m."""
    fact_of = {k: fact for k, (_, fact) in input_rules().items()}
    out = {}
    for col, lab, key, status in cols:
        val = cell(rec, m, col) if status != "computed" else None
        if key in fact_of and val:
            out.setdefault(fact_of[key], []).append((lab, val))
    return out


def _parts(r, key, omega, depth=0):
    """A subtotal split into the non-zero values it adds up, as deep as the formulas are plain sums."""
    kids = [k for k in children(r, key, omega) if k[1] == key[1] and _number(value(r, k))]
    if depth < 4 and kids and sum(value(r, k) for k in kids) == value(r, key):
        return [p for k in kids for p in _parts(r, k, omega, depth + 1)]
    return [key]


def _line(r, k, comps, op=""):
    f = k[0]
    names = comps.get(f) or []
    note = ""
    if names and not (len(names) == 1 and names[0][0].lower() == state.fact_label(f).lower()):
        note = " <span class='muted'>(" + ", ".join(n for n, _ in names) + ")</span>"
    return (f"<tr class='sub'><td>{op}</td><td>{_fact_term(f)}{note}</td>"
            f"<td class='r'>{state.fmt(f, value(r, k))}</td></tr>")


def month_card(r, rec, cols, m, omega):
    """The PPh 21 of month m, explained by the rules that computed it (read from the trace)."""
    root = (ROOT, m)
    due = value(r, root)
    work = working(r, root, omega)
    rl = rule(r, work, omega)
    comps = _components(rec, cols, m)
    rows = []
    kids = children(r, work, omega)
    split = {k: (_parts(r, k, omega) if k[1] == m else [k]) for k in kids}
    for k in sorted(kids, key=lambda k: len(split[k]) == 1):      # subtotals with their parts first, in formula order
        v = value(r, k)
        if v in (None, ""):
            continue
        parts = split[k]
        if len(parts) > 1:
            rows += [_line(r, p, comps, "+") for p in parts]
            rows.append(f"<tr><td class='op'>=</td><td>{_fact_term(k[0])}</td>"
                        f"<td class='r'>{state.fmt(k[0], v)}</td></tr>")
        else:
            rows.append(f"<tr><td class='op'></td><td>{_fact_term(k[0])}" + ("" if k[1] == m else
                        " <span class='muted'>(year)</span>") + f"</td><td class='r'>{state.fmt(k[0], v)}</td></tr>")
    rows.append(f"<tr class='sub'><td></td><td colspan=2><span class='muted'>Formula: {state.readable(rl.expression)}"
                f"</span></td></tr>" if rl is not None else "")
    rows.append(f"<tr class='total'><td class='op'>=</td><td>{common.term('PPh 21')} {state.MONTHS[m - 1]}</td>"
                f"<td class='r'>{state.money(due)}</td></tr>")
    for f in downstream(r, m, omega):
        v = value(r, (f, m))
        if _number(v):
            rows.append(f"<tr class='sub'><td>·</td><td>{_fact_term(f)}</td><td class='r'>{state.fmt(f, v)}</td></tr>")
    final = not r.partial and r.final_month == m
    src = source_of(r, work)
    where = f"{state.short_doc(src['document'])} {src['provision']}" if src else ""
    badge = (common.badge("Final month", "orange") + common.term("final period", "what is this?") if final
             else common.badge(f"Regular month · {state.short_doc(src['document'])}" if src else "Regular month",
                               "blue"))
    expl = (f"Computed with rule <code>{rl.id if rl else '-'}</code> ({where})."
            + (" The tax of the year is recalculated in the card below." if final else ""))
    neg = due is not None and due < 0
    common.html(f"<div class='card'><h4>{'Overpaid' if neg else 'PPh 21'} · {state.MONTHS[m - 1]} {rec['year']}</h4>"
                f"{badge}<div class='big{' neg' if neg else ''}'>{state.money(abs(due) if neg else due)}</div>"
                f"<table class='lines'>{''.join(rows)}</table><div class='explain'>{expl}</div></div>")
    return [work] + children(r, work, omega)


def year_card(r, rec, omega):
    """The year calculation of the final month: every year value under the PPh 21 of the final month, from the first
    step to the result, each with the formula of its rule. Read from the trace, not from a fixed list."""
    end = r.final_month
    top = working(r, (ROOT, end), omega)
    steps = ladder(r, top, omega)
    rows = []
    for k, level in steps:
        rl = rule(r, k, omega)
        has = any(c[1] == 0 for c in children(r, k, omega))
        formula = (f"<br><span class='muted'>{state.readable(rl.expression)}</span>" if rl is not None and has else "")
        cls = " class='total'" if k == top else ""
        rows.append(f"<tr{cls}><td class='op'>{'=' if has else ''}</td><td>{_fact_term(k[0])}{formula}</td>"
                    f"<td class='r'>{state.fmt(k[0], value(r, k))}</td></tr>")
    v = value(r, top)
    note = ""
    if rec["withheld"]:
        note = (f"The PPh 21 already withheld uses the entries in '{WITHHELD}' for "
                + ", ".join(state.MON[int(x) - 1] for x in sorted(rec["withheld"], key=int))
                + "; the other months come from the system's calculation.")
    if end < 12:
        note += f" The employee leaves in {state.MONTHS[end - 1]}: that month is the final month."
    if isinstance(v, (int,)) or hasattr(v, "denominator"):
        note = (f"{common.term('underpaid', 'Underpaid') if v >= 0 else common.term('overpaid', 'Overpaid')} "
                f"{state.MONTHS[end - 1]}: <b>{state.money(abs(v))}</b>. " + note)
    common.html(f"<div class='card'><h4>Annual recalculation {rec['year']}</h4><table class='lines'>{''.join(rows)}"
                "</table>" + (f"<div class='explain'>{note}</div>" if note else "") + "</div>")
    return [k for k, _ in steps]


def warnings(r, rec, cols, found):
    """Shows the warnings; returns True when results must not be shown."""
    shown = list(range(rec["start"], rec["month"] + 1))
    blocking = [f"Component **{lab}** is mapped to data that is no longer used ({label(key)}). Choose a new kind "
                "through '+ Component' so that its income does not drop out of gross income."
                for col, lab, key, status in cols if status == "retired" and any(cell(rec, m, col) for m in shown)]
    for b in blocking:
        st.error(b, icon=":material/block:")
    out = []
    for col, lab, key, status in cols:
        if not key:
            out.append(f"Component **{lab}** is not mapped to knowledge-base data yet; it is not counted.")
            continue
        if status == "unused" and any(cell(rec, m, col) for m in shown):
            out.append(f"**{lab}** is filled in, but no rule in force in these months reads it; it is not counted.")
        if col.startswith("data:") and key in found and found[key]["layer"] == "company" \
                and kind(key) in ("int", "choice", "money"):
            need = [] if (definition(key) or {}).get("optional") else [m for m in shown if m in found[key]["months"]]
            if need and all(cell(rec, m, col) in (None, "", 0) for m in need):
                out.append(f"**{lab}** is read by rules ({', '.join(found[key]['rules'][:2])}) but is empty; "
                           "it counts as 0.")
        if status == "nodef":
            out.append(f"**{lab}**: this data has no definition in the knowledge base yet; its name and type are "
                       "taken from the rules.")
    if r is not None:
        eff = state.value(r, "ptkp_status_effective")
        if eff and eff != rec["fields"].get("employee.ptkp_status"):
            out.append(f"The PTKP status used is **{eff}**: a married female employee uses the PTKP of an unmarried "
                       "person unless there is a statement that her husband has no income.")
        cat = {**rec.get("component_keys", {}), **catalog()}
        names = {}
        for n, k in cat.items():
            names.setdefault(k.split(".", 1)[1], []).append(n)
        for w in r.warnings:
            if str(w).startswith("UnreadInput"):
                bucket, k = str(w).split("(")[1].rstrip(")").split(".", 1)
                if bucket == "hr" and f"hr.{k}" not in found:
                    continue            # kept for a company policy; no rule in force reads it, and it is not shown
                who = ", ".join(n for n in names.get(k, [k]) if n in rec["components"]) or k
                out.append(f"**{who}** is filled in, but not used in this calculation (the conditions of its rule are "
                           "not met).")
    for n in out:
        st.info(n, icon=":material/lightbulb:")
    return bool(blocking)


def changed_banner(r, rec):
    s = st.session_state
    if s.rec_origin[0] != "saved" or r is None:
        return
    saved = state.load()["employees"].get(s.rec_origin[1])
    if not saved:
        return
    approved = state.load()["approved"][saved["approved"]:]
    found = discover(rec["year"], rec.get("policy"), s.k_omega_v)
    new_keys = [k for k in found if k not in saved["keys"]]
    if new_keys:
        st.warning("New data is needed since this employee was saved: " + ", ".join(
            f"**{label(k)}** ({(definition(k) or {}).get('origin', 'new rule')})" for k in new_keys)
            + ". Default values are used until it is filled in.", icon=":material/new_releases:")
    changed = [(int(m), old, r.periods[int(m)].get("pph21_due")) for m, old in saved["last"].items()
               if int(m) in r.periods and int(m) <= rec["month"] and old != r.periods[int(m)].get("pph21_due")]
    if changed and approved:
        st.warning(f"The results changed since saving ({saved['saved']}) because of the updates: "
                   + ", ".join(a["title"] for a in approved) + ". "
                   + "; ".join(f"{state.MON[m - 1]}: {state.money(o)} → {state.money(n)}" for m, o, n in changed[:6]),
                   icon=":material/update:")


def basis(r, nodes):
    """The rules behind the values shown in the cards, with what they read and their article and quote."""
    seen = set()
    for key in nodes:
        t = (r.trace or {}).get(key)
        if not t or key in seen or is_input(r, key) or t["value"] in (None, 0):
            continue
        seen.add(key)
        f, mm = key
        src = t["source"][0] if t["source"] else None
        reads = ", ".join(state.fact_label(k[0]) for k in children(r, key, st.session_state.k_omega_v)[:6])
        company = t["layer"] == "company"
        layer = common.badge("company policy", "orange") if company else ""
        common.html(f"<div class='rule{' company' if company else ''}'>{layer}<b>{state.fact_label(f)}</b> = "
                    f"{state.fmt(f, t['value'])} <span class='muted'>({state.MONTHS[mm - 1] if mm else 'year'})"
                    f"</span><br><span class='muted'>Reads: {reads or '-'} · {common.term('source', 'Source')}: "
                    f"{state.short_doc(src['document']) + ' · ' + src['provision'] if src else '-'} · rule "
                    f"<code>{t['rule']}</code></span>"
                    + (f"<div class='quote'>“{src['quote']}”</div>" if src else "") + "</div>")


def results(rec, cols, found, autos):
    s = st.session_state
    case = case_of(rec, s.k_omega_v)
    r, err = state.compute(case, s.k_omega_v)
    changed_banner(r, rec)
    blocked = warnings(r, rec, cols, found)
    if err:
        st.error(f"The calculation failed: {err}")
        return
    if blocked:
        return
    m = rec["month"]
    omega = s.k_omega_v
    shown = list(range(rec["start"], m + 1))
    final = not r.partial and r.final_month == m
    work = {x: working(r, (ROOT, x), omega) for x in shown}
    s.k_last = {"case": case, "month": m, "final": final, "due": {x: r.periods[x].get(ROOT) for x in shown},
                "work": {x: (getattr(rule(r, work[x], omega), "id", "-"),
                             getattr(rule(r, work[x], omega), "expression", None),
                             [(k, value(r, k)) for k in children(r, work[x], omega)]) for x in shown}}
    total = sum(rec["withheld"].get(str(x), r.periods[x].get(ROOT) or 0) for x in shown)
    after = [f for f in downstream(r, m, omega)
             if any(_number(r.periods[x].get(f)) for x in shown)][:2]      # e.g. PPh 21 borne by the government
    span = f"{state.MON[shown[0] - 1]}–{state.MON[m - 1]}"
    c = st.columns(2 + len(after))
    c[0].metric(f"PPh 21 {state.MONTHS[m - 1]}", state.money(r.periods[m].get(ROOT)), help=common.tip("PPh 21"))
    c[1].metric(f"Total {span}", state.money(total), help="The sum of PPh 21 up to this month.")
    for col, f in zip(c[2:], after):
        col.metric(f"{state.fact_label(f)} {span}", state.money(sum(r.periods[x].get(f) or 0 for x in shown)))
    left, right = st.columns([1, 1], gap="large")
    with left:
        nodes = month_card(r, rec, cols, m, omega)
        if final:
            nodes += year_card(r, rec, omega)
        else:
            st.caption("The annual recalculation appears in the final month "
                       f"({state.MONTHS[max(rec['end'], rec['start']) - 1]}).")
    with right:
        names = outputs(r, shown, omega)        # the results the knowledge base marks as output
        names = [f for f in names if f == ROOT] + [f for f in names if f != ROOT]
        rows = []
        for x in shown:
            p = r.periods[x]
            src = source_of(r, work[x])
            rows.append({"Month": state.MONTHS[x - 1], **{state.fact_label(f): state.fmt(f, p.get(f)) for f in names},
                         "Computed with": (state.short_doc(src["document"]) + " " + src["provision"]) if src else "",
                         "Already withheld (entered)":
                             state.money(rec["withheld"][str(x)]) if str(x) in rec["withheld"] else ""})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption("Table columns: the values the knowledge base marks as results that are not zero in these months.")
        st.download_button("Download details (CSV)", pd.DataFrame(rows).to_csv(index=False).encode(),
                           f"pph21_{rec['name'] or 'employee'}_{rec['year']}.csv", icon=":material/download:")
        with st.expander("Why is the amount this much? (rules and articles)"):
            basis(r, nodes)
        with st.expander("Data sent to the engine"):
            st.caption("Only the months up to the month of the calculation are sent; the engine knows the final month "
                       "from the month employment ends and gives the year values only in that month. PPh 21 entered "
                       f"under '{WITHHELD}' is sent as a recorded value.")
            st.json(case, expanded=False)


# ====================================================================================================================
# Page
# ====================================================================================================================
def show():
    s = st.session_state
    s.page_ctx = "calculator"
    if "rec" not in s:
        _apply_scenario(DEFAULT_SCENARIO)
    st.title("PPh 21 calculator")
    common.md(f"Calculate the {common.term('PPh 21')} of one employee up to a given month. Fill in the form or pick a "
              "scenario, then change any number in the table. The data asked for follows the rules in force; hover "
              "over a dotted word or the ⓘ icon for an explanation.")
    top_bar()
    period_bar()
    s.g_date = date(s.rec["year"], s.rec["month"], 1)     # the glossary explains the numbers of that tax month
    profile()
    rec = s.rec
    before = _norm(rec)
    pre, _ = state.compute(case_of(rec, s.k_omega_v), s.k_omega_v)
    cols, found, autos = grid(pre)
    if _norm(rec) != before and any(c[3] == "computed" for c in cols):
        st.rerun()        # an edit changed what the rules compute: show the locked columns up to date
    with st.expander("Cases not calculated here"):
        st.markdown("Only **permanent employees** of **one company** in **one tax year**. Not calculated: "
                    "non-permanent or daily workers, employees who moved from another company in the same year, "
                    "employees who return to work in the same year, payments after leaving, severance pay, pensioners, "
                    "foreign employees (PPh 26), foreign currency.")
    results(rec, cols, found, autos)
