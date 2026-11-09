"""Calculator v4 (mini_demo/RANCANGAN_KALKULATOR.md): one employee, one grid as the only source of numbers.

Rows are the months up to the month asked for; columns are the company's pay components and the other monthly data the
rules read. Everything the screen asks for comes from the knowledge base (inputs.py): the profile and company fields,
the kinds a pay component can be, the HR data columns, their labels and types, which components a company policy
computes, and the choices. Scenarios fill the form in company words; the employee can be saved and reopened, and is
told when the knowledge base changed its results.
"""
import json
import re
from datetime import date, datetime

import pandas as pd
import streamlit as st

import data as d
import employee as emp
import explain as ex
import glossary as g
import inputs
import store
import ui


# ---------------------------------------------------------------- engine case
def case_of(rec, omega):
    """The case for the engine. When PPh 21 actually withheld is recorded and the employer pays the tax (method, or a
    company policy that sets it, read from the engine), the tax allowance of that month is recorded with it."""
    installed = rec.get("policy") in store.installed_policies()
    case = emp.to_case(rec, policy_installed=installed)
    if not rec["withheld"]:
        return case
    r0, _ = d.compute(case, omega)
    method = (d.value(r0, "withholding_method") if r0 else None) or case["method"]
    pays = method != "gross" or bool(r0 and any(r0.periods[m].get("tax_allowance") for m in r0.periods))
    return emp.to_case(rec, policy_installed=installed, employer_pays_tax=pays)


# ---------------------------------------------------------------- record state
def _norm(rec):
    """The record as text, with empty cells left out (an empty cell and 0 mean the same)."""
    r = dict(rec)
    r["grid"] = {m: {c: v for c, v in row.items() if v not in (None, "", 0, False)} for m, row in rec["grid"].items()}
    r["grid"] = {m: row for m, row in r["grid"].items() if row}
    return json.dumps(r, sort_keys=True, default=str)


def _load(rec, origin):
    s = st.session_state
    s.rec = emp.copy_record(rec)
    s.rec_origin = origin                      # ("scenario", title) or ("saved", name)
    s.rec_clean = _norm(s.rec)
    s.rec_ver = s.get("rec_ver", 0) + 1


def _dirty():
    s = st.session_state
    return _norm(s.rec) != s.get("rec_clean")


def _apply_scenario(title):
    sc = emp.scenarios()[title]
    emp.ensure_components(sc)
    _load(emp.from_scenario(sc), ("scenario", title))


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
    saved = store.load()["employees"].get(name)
    if saved:
        _load(saved["record"], ("saved", name))
    s.k_open_pick = None


def _save(name):
    s = st.session_state
    s.rec["name"] = name
    r, _ = d.compute(case_of(s.rec, s.k_omega_v), s.k_omega_v)
    found = inputs.discover(s.rec["year"], s.rec.get("policy"), s.k_omega_v)
    store.save_employee(name, {"record": s.rec, "saved": datetime.now().strftime("%Y-%m-%d %H:%M"),
                              "approved": len(store.load()["approved"]),
                              "last": {str(m): r.periods[m].get("pph21_due") for m in r.periods} if r else {},
                              "keys": sorted(found)})
    s.rec_origin = ("saved", name)
    s.rec_clean = _norm(s.rec)


# ---------------------------------------------------------------- top bar
def top_bar():
    s = st.session_state
    rec = s.rec
    saved = store.load()["employees"]
    c = st.columns([1.3, 1.3, 1, 1])
    who = rec["name"] or "New employee"
    origin = s.rec_origin
    c[0].markdown(f"**{who}**{' ●' if _dirty() else ''}  \n<span class='muted'>"
                  + ("from scenario: " + origin[1] if origin[0] == "scenario" else "saved employee") + "</span>",
                  unsafe_allow_html=True, help="● = there are unsaved changes.")
    c[1].selectbox("Fill with a common scenario", list(emp.scenarios()), index=None, key="k_scn_pick",
                   placeholder="Choose a scenario…", on_change=_on_scenario,
                   help="Fills this form with a complete example; after that everything can be changed.")
    c[2].selectbox("Open saved employee", list(saved), index=None, key="k_open_pick", placeholder="Choose…",
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
    sc = emp.scenarios().get(origin[1]) if origin[0] == "scenario" else None
    if sc:
        st.caption(f"**{sc['title']}**: {sc['note']}")


def period_bar():
    s = st.session_state
    rec = s.rec
    v = s.rec_ver
    c = st.columns(5)
    ys = inputs.years()
    rec["year"] = c[0].selectbox("Tax year", ys, index=ys.index(rec["year"]) if rec["year"] in ys else len(ys) - 2,
                                 key=f"k_year_{v}")
    rec["start"] = c[1].selectbox("Starts work", range(1, 13), index=rec["start"] - 1, key=f"k_start_{v}",
                                  format_func=lambda m: d.MONTHS[m - 1], help="First month paid this year.")
    ends = list(range(rec["start"], 13))
    rec["end"] = c[2].selectbox("Works until", ends, index=ends.index(rec["end"]) if rec["end"] in ends else len(ends) - 1,
                                key=f"k_end_{v}", format_func=lambda m: "December (still employed)" if m == 12
                                else d.MONTHS[m - 1] + " (leaves)",
                                help="The month of leaving becomes the closing month: the annual tax is recalculated in that month.")
    months = list(range(rec["start"], rec["end"] + 1))
    rec["month"] = c[3].selectbox("Calculate up to month", months,
                                  index=months.index(rec["month"]) if rec["month"] in months else len(months) - 1,
                                  key=f"k_month_{v}",
                                  format_func=lambda m: d.MONTHS[m - 1] + (" · closing" if m == rec["end"] else ""),
                                  help="Results are shown from the first month to this month. The annual recalculation only "
                                       "appears in the closing month (December or the month of leaving).")
    s.k_omega_v = c[4].date_input("Rules as of date", store.TODAY, key="k_omega",
                                  help="Calculates with the rules the system already knew on this date. Useful for "
                                       "seeing an old calculation from before a retroactive rule existed. "
                                       f"The knowledge base is known up to {d.tgl(store.known_until())}.")


# ---------------------------------------------------------------- profile and company (from the knowledge base)
def _field(key, rec, year, v):
    tp = inputs.kind(key)
    lab = inputs.label(key)
    df = inputs.definition(key) or {}
    if df.get("show_if"):
        for k2, val in df["show_if"].items():
            if rec["fields"].get(k2) != val:
                return
    if df.get("origin", "keadaan awal") != "keadaan awal":
        lab += f" · new ({df['origin']})"
    if not inputs.has_def(key):
        lab += " ⚠"
    cur = rec["fields"].get(key, inputs.default(key))
    wkey = f"k_f_{key}_{v}"
    hp = inputs.help_text(key)
    if tp == "choice":
        opts = inputs.options(key, year)
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
            keys = inputs.profile_fields("pegawai", year, rec.get("policy"), omega)
            core = [k for k in keys if (inputs.definition(k) or {}).get("core")]
            more = [k for k in keys if k not in core]
            for k in core:
                _field(k, rec, year, v)
            with st.expander(f"Other employee data read by this year's rules ({len(more)})"):
                st.caption("This list is built from the knowledge base: each data item is read by at least one rule "
                           f"in force in {year}.")
                for k in more:
                    _field(k, rec, year, v)
        with right:
            st.markdown("**Company**")
            pols = store.installed_policies()
            opts = [""] + list(pols)
            cur = rec.get("policy") if rec.get("policy") in pols else ""
            pick = st.selectbox("Company policy", opts, index=opts.index(cur), key=f"k_pol_{v}",
                                format_func=lambda p: "None" if not p else f"{p} · {pols[p]}",
                                help=g.tip("kebijakan perusahaan") + " Only policies already approved in Knowledge base management.")
            if rec.get("policy") and rec["policy"] not in pols:
                st.info(f"This form uses the policy **{rec['policy']}**, which is not in the knowledge base yet. Approve it "
                        "first in Knowledge base management; its data columns will appear automatically.", icon=":material/info:")
            else:
                rec["policy"] = pick or None
            keys = inputs.profile_fields("perusahaan", year, rec.get("policy"), omega)
            core = [k for k in keys if (inputs.definition(k) or {}).get("core")]
            more = [k for k in keys if k not in core]
            for k in core:
                _field(k, rec, year, v)
            klu = rec["fields"].get("employer.klu")
            if klu:
                lists = _lookup_tables("employer('klu')", year, omega)
                hit = [(n, rid) for n, rid in lists if klu in inputs.table_keys(n, year)]
                if not lists:
                    st.caption(f"No rule in {year} uses KLU.")
                else:
                    def names(xs):
                        tabs = {n: d.table_at(n, date(year, 12, 31)) or d.table_at(n, date(year, 1, 1)) for n, _ in xs}
                        return ", ".join(f"'{(d.label_of(tabs[n]) or n) if tabs[n] else n}' ({rid})"
                                         for n, rid in xs)
                    st.caption(f"KLU {klu} " + (f"is in the list {names(hit)} in {year}." if hit else
                                                f"is not in the lists used by the rules in {year}: {names(lists)}."))
            with st.expander(f"Other company data read by the rules ({len(more)})"):
                for k in more:
                    _field(k, rec, year, v)


def _lookup_tables(read, year, omega):
    """(table, rule) for every table that a rule in force in the year looks this input up in, e.g. the KLU lists of
    the DTP rules. Read from the rules, so a new list in the knowledge base is found without changing the program."""
    lo, hi = date(year, 1, 1), date(year, 12, 31)
    out = []
    for r in d.kb().view(omega).rules.values():
        if (r.valid_from and r.valid_from > hi) or (r.valid_until and r.valid_until < lo):
            continue
        text = " ".join(e.text for e in (r.expression, r.condition) if e is not None)
        for name in re.findall(r"in_table\('([a-z0-9_]+)',\s*" + re.escape(read), text):
            out.append((name, r.id))
    return out


# ---------------------------------------------------------------- the grid
def _auto(key, r, shown):
    """When the rules compute this data in the months shown (the winning rule is not the one that reads the admin's
    input), its values and the rules that computed it; read from the engine's trace, so it follows the knowledge base."""
    rule = inputs.input_rules().get(key)
    if r is None or not rule:
        return None
    rid, fact = rule
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
    cat = {**rec.get("component_keys", {}), **emp.catalog()}
    found = inputs.discover(year, policy, omega)
    shown = list(range(rec["start"], rec["month"] + 1))
    cols, autos = [], {}
    for name in rec["components"]:
        key = cat.get(name)
        state = "edit"
        a = _auto(key, r, shown) if key else None
        if a:
            state, autos[name] = "computed", a
        elif key and inputs.retired(key, date(year, rec["month"], 1)):
            state = "retired"
        elif key not in found or not any(m in found[key]["months"] for m in shown):
            state = "unused"
        cols.append((name, name, key, state))
    mapped = {cat.get(n) for n in rec["components"]}
    for key in inputs.component_kinds(year, policy, omega):      # computed by the rules, not entered: shown, locked
        if key in mapped:
            continue
        a = _auto(key, r, shown)
        if a and any(a["vals"].values()):
            col = f"auto:{key}"
            autos[col] = a
            cols.append((col, d.fact_label(a["fact"]), key, "computed"))
    for key in inputs.monthly_data(year, policy, omega):
        cols.append((f"data:{key}", inputs.label(key), key, "edit" if inputs.has_def(key) else "nodef"))
    return cols, found, autos


def _range_note(found, key, shown):
    ms = [m for m in shown if key in found and m in found[key]["months"]]
    if not ms or len(ms) == len(shown):
        return ""
    return f" ({d.MON[ms[0] - 1]}–{d.MON[ms[-1] - 1]})"


def grid(prev_result):
    s = st.session_state
    rec, v = s.rec, s.rec_ver
    omega = s.k_omega_v
    shown = list(range(rec["start"], rec["month"] + 1))
    cols, found, autos = _columns(rec, omega, prev_result)
    with st.container(border=True):
        h1, h2, h3 = st.columns([3, 1, 1])
        h1.markdown(f"**Monthly breakdown** · {d.MONTHS[shown[0] - 1]}–{d.MONTHS[shown[-1] - 1]} {rec['year']}")
        h1.caption("Double-click a cell to change the number, then press Enter. Numbers are recorded in the month they are "
                   "paid. Columns come from the company's pay components and the data read by this year's rules.")
        with h2.popover("Component", icon=":material/add:", width="stretch"):
            add_component(rec, shown)
        with h3.popover("Quick fill", icon=":material/auto_fix_high:", width="stretch"):
            quick_fill(rec, cols, shown)
        table, cfg = [], {"Month": st.column_config.TextColumn("Month", disabled=True)}
        for m in shown:
            row = {"Month": d.MONTHS[m - 1]}
            for col, lab, key, state in cols:
                tp = inputs.kind(key) if key else "money"
                if state == "computed":
                    row[col] = autos[col]["vals"].get(m, 0)
                else:
                    val = emp.cell(rec, m, col)
                    row[col] = bool(val) if tp == "flag" else (val if tp == "choice" else (val or 0))
            row["PPh already withheld"] = rec["withheld"].get(str(m)) if m < rec["month"] else None
            table.append(row)
        for col, lab, key, state in cols:
            tp = inputs.kind(key) if key else "money"
            hp = inputs.help_text(key) if key else "This component is not mapped to knowledge base data yet."
            if state == "computed":
                by = autos[col]["by"]
                who = ("company policy " + str(rec.get("policy"))) if "company" in by.values() else "the rules"
                title = f"{lab} ⚙"
                hp = (f"Computed automatically by {who} ({', '.join(list(by)[:3])}), cannot be typed. To change it, "
                      "change the data that rule reads (e.g. salary, job risk, or HR data).")
            elif state == "unused":
                title = f"{lab} (not read by rules)"
            elif state == "retired":
                title = f"{lab} (no longer used)"
            elif state == "nodef":
                title = f"{lab} ⚠"
            else:
                title = f"{lab} ✎" + _range_note(found, key, shown)
            dis = state == "computed"
            if tp == "flag":
                cfg[col] = st.column_config.CheckboxColumn(title, help=hp, disabled=dis)
            elif tp == "choice":
                cfg[col] = st.column_config.SelectboxColumn(title, help=hp, disabled=dis,
                                                            options=[o[0] for o in inputs.options(key, rec["year"])])
            else:
                cfg[col] = st.column_config.NumberColumn(title, help=hp, disabled=dis, min_value=0, format="localized",
                                                         step=1)
        cfg["PPh already withheld"] = st.column_config.NumberColumn(
            "PPh already withheld ✎", format="localized", min_value=0,
            help="Fill in only if the PPh actually withheld that month differs from the system's calculation (e.g. it "
                 "was calculated by an old system). Used in the closing month.")
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
            for col, lab, key, state in cols:
                if state == "computed":
                    continue
                val = r[col]
                tp = inputs.kind(key) if key else "money"
                if tp == "flag":
                    rowrec[col] = 1 if val else 0
                elif tp == "choice":
                    rowrec[col] = val if isinstance(val, str) and val else None
                else:
                    rowrec[col] = int(val) if pd.notna(val) and val != "" else 0
            w = r["PPh already withheld"]
            if m < rec["month"] and pd.notna(w) and w != "":
                rec["withheld"][str(m)] = int(w)
            else:
                rec["withheld"].pop(str(m), None)
        if any(c[3] == "computed" for c in cols):
            st.caption("⚙ = computed automatically by the rules from other data; shown for reference, cannot be typed.")
    return cols, found, autos


def add_component(rec, shown):
    s = st.session_state
    year = rec["year"]
    cat = emp.catalog()
    existing = [n for n in cat if n not in rec["components"]]
    mode = st.radio("Component", ["New", "From company list"] if existing else ["New"], horizontal=True,
                    key="k_add_mode")
    if mode == "New":
        name = st.text_input("Component name", key="k_add_name", placeholder="e.g. Communication allowance")
        kinds = inputs.component_kinds(year, rec.get("policy"), s.k_omega_v)
        key = st.selectbox("What is this?", kinds, key="k_add_kind", format_func=inputs.label,
                           help="Choose what best fits the nature of this component. The list comes from the data read "
                                "by this year's rules; how it is taxed is decided by the rules, not by this choice.")
        if key:
            st.caption(inputs.help_text(key))
    else:
        name = st.selectbox("Component", existing, key="k_add_existing")
        key = cat.get(name)
        st.caption(f"Mapped to: {inputs.label(key)}")
    c1, c2 = st.columns(2)
    value = c1.number_input("Value", 0, 10**11, 0, 50_000, key="k_add_value")
    start = c2.selectbox("Start month", shown, key="k_add_start", format_func=lambda m: d.MONTHS[m - 1])
    repeat = st.checkbox("Paid every month from then on",
                         bool((inputs.definition(key) or {}).get("repeat")) if key else True, key=f"k_add_repeat_{key}")
    if st.button("Add", type="primary", key="k_add_btn", disabled=not (name and key)):
        if mode == "New":
            store.add_component(name, key)
        if name not in rec["components"]:
            rec["components"].append(name)
        for m in range(start, rec["end"] + 1):
            if m == start or repeat:
                rec["grid"].setdefault(str(m), {})[name] = int(value)
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
        st.caption("No columns can be filled.")
        return
    labels = {c[0]: c[1] for c in editable}
    col = st.selectbox("Column", list(labels), format_func=labels.get, key="k_qf_col")
    key = next(c[2] for c in editable if c[0] == col)
    tp = inputs.kind(key) if key else "money"
    start = st.selectbox("Start month", shown, key="k_qf_start", format_func=lambda m: d.MONTHS[m - 1])
    modes = ["Fill the same up to the last month", "This month only"] + (["Increase by 1 each month"] if tp == "int" else [])
    mode = st.radio("Mode", modes, key="k_qf_mode")
    value = 1 if tp == "flag" else st.number_input("Value", 0, 10**11, 0, 1 if tp == "int" else 50_000, key="k_qf_value")
    if st.button("Fill", type="primary", key="k_qf_btn"):
        for i, m in enumerate(range(start, rec["end"] + 1)):
            if mode == "This month only" and m != start:
                break
            rec["grid"].setdefault(str(m), {})[col] = int(value) + (i if mode == "Increase by 1 each month" else 0)
        s.rec_ver += 1
        st.rerun()


# ---------------------------------------------------------------- results
def _label(f):
    """The fact's label from the KB, with a hover explanation when the glossary has one."""
    key = g.FOR_FACT.get(f)
    return g.term(key, d.fact_label(f)) if key else d.fact_label(f)


def _components(rec, cols, m):
    """Input fact -> names of the company components (and their values) that feed it in month m."""
    fact_of = {k: fact for k, (_, fact) in inputs.input_rules().items()}
    out = {}
    for col, lab, key, state in cols:
        val = emp.cell(rec, m, col) if state != "computed" else None
        if key in fact_of and val:
            out.setdefault(fact_of[key], []).append((lab, val))
    return out


def _parts(r, key, omega, depth=0):
    """A subtotal split into the non-zero values it adds up, as deep as the formulas are plain sums."""
    kids = [k for k in ex.children(r, key, omega) if k[1] == key[1] and ex._number(ex.value(r, k))]
    if depth < 4 and kids and sum(ex.value(r, k) for k in kids) == ex.value(r, key):
        return [p for k in kids for p in _parts(r, k, omega, depth + 1)]
    return [key]


def _line(r, k, comps, op=""):
    f = k[0]
    names = comps.get(f) or []
    note = ""
    if names and not (len(names) == 1 and names[0][0].lower() == d.fact_label(f).lower()):
        note = " <span class='muted'>(" + ", ".join(n for n, _ in names) + ")</span>"
    return (f"<tr class='sub'><td>{op}</td><td>{_label(f)}{note}</td>"
            f"<td class='r'>{d.fmt(f, ex.value(r, k))}</td></tr>")


def month_card(r, rec, cols, m, omega):
    """The PPh 21 of month m, explained by the rules that computed it (read from the trace)."""
    root = (ex.ROOT, m)
    due = ex.value(r, root)
    work = ex.working(r, root, omega)
    rule = ex.rule(r, work, omega)
    comps = _components(rec, cols, m)
    rows = []
    kids = ex.children(r, work, omega)
    split = {k: (_parts(r, k, omega) if k[1] == m else [k]) for k in kids}
    for k in sorted(kids, key=lambda k: len(split[k]) == 1):      # subtotals with their parts first, in formula order
        v = ex.value(r, k)
        if v in (None, ""):
            continue
        parts = split[k]
        if len(parts) > 1:
            rows += [_line(r, p, comps, "+") for p in parts]
            rows.append(f"<tr><td class='op'>=</td><td>{_label(k[0])}</td><td class='r'>{d.fmt(k[0], v)}</td></tr>")
        else:
            rows.append(f"<tr><td class='op'></td><td>{_label(k[0])}" + ("" if k[1] == m else
                        " <span class='muted'>(annual)</span>") + f"</td><td class='r'>{d.fmt(k[0], v)}</td></tr>")
    rows.append(f"<tr class='sub'><td></td><td colspan=2><span class='muted'>Formula: {d.readable(rule.expression)}"
                f"</span></td></tr>" if rule is not None else "")
    rows.append(f"<tr class='total'><td class='op'>=</td><td>{g.term('PPh 21')} {d.MONTHS[m - 1]}</td>"
                f"<td class='r'>{d.money(due)}</td></tr>")
    for f in ex.downstream(r, m, omega):
        v = ex.value(r, (f, m))
        if ex._number(v):
            rows.append(f"<tr class='sub'><td>·</td><td>{_label(f)}</td><td class='r'>{d.fmt(f, v)}</td></tr>")
    final = not r.partial and r.final_month == m
    src = ex.source_of(r, work)
    where = f"{d.short_doc(src['document'])} {src['provision']}" if src else ""
    badge = (ui.badge("Closing month", "orange") + g.term("masa terakhir", "what is this?") if final
             else ui.badge(f"Regular month · {d.short_doc(src['document'])}" if src else "Regular month", "blue"))
    expl = (f"Computed with rule <code>{rule.id if rule else '-'}</code> ({where})."
            + (" The annual tax is recalculated in the card below." if final else ""))
    neg = due is not None and due < 0
    ui.html(f"<div class='card'><h4>{'Over-withheld' if neg else 'PPh 21'} · {d.MONTHS[m - 1]} {rec['year']}</h4>{badge}"
            f"<div class='big{' neg' if neg else ''}'>{d.money(abs(due) if neg else due)}</div>"
            f"<table class='lines'>{''.join(rows)}</table><div class='explain'>{expl}</div></div>")
    return [work] + ex.children(r, work, omega)


def year_card(r, rec, omega):
    """The year calculation of the final month: every year value under the PPh of the final month, from the first
    step to the result, each with the formula of its rule. Read from the trace, not from a fixed list."""
    end = r.final_month
    top = ex.working(r, (ex.ROOT, end), omega)
    steps = ex.ladder(r, top, omega)
    rows = []
    for k, level in steps:
        rl = ex.rule(r, k, omega)
        has = any(c[1] == 0 for c in ex.children(r, k, omega))
        formula = (f"<br><span class='muted'>{d.readable(rl.expression)}</span>" if rl is not None and has else "")
        cls = " class='total'" if k == top else ""
        rows.append(f"<tr{cls}><td class='op'>{'=' if has else ''}</td><td>{_label(k[0])}{formula}</td>"
                    f"<td class='r'>{d.fmt(k[0], ex.value(r, k))}</td></tr>")
    v = ex.value(r, top)
    note = ""
    if rec["withheld"]:
        note = ("Withheld PPh takes the 'PPh already withheld' entries for "
                + ", ".join(d.MON[int(x) - 1] for x in sorted(rec["withheld"], key=int)) + "; other months come from the system's calculation.")
    if end < 12:
        note += f" The employee leaves in {d.MONTHS[end - 1]}: that month is the closing month."
    if isinstance(v, (int,)) or hasattr(v, "denominator"):
        note = (f"{g.term('kurang bayar', 'Under-withheld') if v >= 0 else g.term('lebih bayar', 'Over-withheld')} in {d.MONTHS[end - 1]}: "
                f"<b>{d.money(abs(v))}</b>. " + note)
    ui.html(f"<div class='card'><h4>Annual recalculation {rec['year']}</h4><table class='lines'>{''.join(rows)}</table>"
            + (f"<div class='explain'>{note}</div>" if note else "") + "</div>")
    return [k for k, _ in steps]


def warnings(r, rec, cols, found):
    """Shows the warnings; returns True when results must not be shown."""
    shown = list(range(rec["start"], rec["month"] + 1))
    blocking = [f"Component **{lab}** is mapped to data that is no longer used ({inputs.label(key)}). Choose a new kind "
                "through '+ Component' so its income is not lost from gross income."
                for col, lab, key, state in cols if state == "retired" and any(emp.cell(rec, m, col) for m in shown)]
    for b in blocking:
        st.error(b, icon=":material/block:")
    out = []
    for col, lab, key, state in cols:
        if not key:
            out.append(f"Component **{lab}** is not mapped to knowledge base data yet; it is not counted.")
            continue
        if state == "unused" and any(emp.cell(rec, m, col) for m in shown):
            out.append(f"**{lab}** is filled in, but no rule in force in these months reads it; it is not counted.")
        if col.startswith("data:") and key in found and found[key]["layer"] == "company"                 and inputs.kind(key) in ("int", "choice", "money"):
            need = [] if (inputs.definition(key) or {}).get("optional") else [m for m in shown if m in found[key]["months"]]
            if need and all(emp.cell(rec, m, col) in (None, "", 0) for m in need):
                out.append(f"**{lab}** is read by rules ({', '.join(found[key]['rules'][:2])}) but is empty; counted as 0.")
        if state == "nodef":
            out.append(f"**{lab}**: the definition of this data is not in the knowledge base yet; its name and type are taken from the rules.")
    if r is not None:
        eff = d.value(r, "ptkp_status_effective")
        if eff and eff != rec["fields"].get("employee.ptkp_status"):
            out.append(f"The PTKP status used is **{eff}**: a married female employee uses the unmarried PTKP unless there is a "
                       "statement that the husband has no income.")
        cat = {**rec.get("component_keys", {}), **emp.catalog()}
        names = {}
        for n, k in cat.items():
            names.setdefault(k.split(".", 1)[1], []).append(n)
        for w in r.warnings:
            if str(w).startswith("UnreadInput"):
                k = str(w).split("(")[1].rstrip(")").split(".", 1)[1]
                who = ", ".join(n for n in names.get(k, [k]) if n in rec["components"]) or k
                out.append(f"**{who}** is filled in, but not used in this calculation (the rule's conditions are not met).")
    for n in out:
        st.info(n, icon=":material/lightbulb:")
    return bool(blocking)


def changed_banner(r, rec):
    s = st.session_state
    if s.rec_origin[0] != "saved" or r is None:
        return
    saved = store.load()["employees"].get(s.rec_origin[1])
    if not saved:
        return
    approved = store.load()["approved"][saved["approved"]:]
    found = inputs.discover(rec["year"], rec.get("policy"), s.k_omega_v)
    new_keys = [k for k in found if k not in saved["keys"]]
    if new_keys:
        st.warning("New data has been needed since this employee was saved: " + ", ".join(
            f"**{inputs.label(k)}** ({(inputs.definition(k) or {}).get('origin', 'new rule')})" for k in new_keys)
            + ". Default values are used until it is filled in.", icon=":material/new_releases:")
    changed = [(int(m), old, r.periods[int(m)].get("pph21_due")) for m, old in saved["last"].items()
               if int(m) in r.periods and int(m) <= rec["month"] and old != r.periods[int(m)].get("pph21_due")]
    if changed and approved:
        st.warning(f"Results have changed since it was saved ({saved['saved']}) because of updates: "
                   + ", ".join(a["title"] for a in approved) + ". "
                   + "; ".join(f"{d.MON[m - 1]}: {d.money(o)} → {d.money(n)}" for m, o, n in changed[:6]),
                   icon=":material/update:")


def basis(r, nodes):
    """The rules behind the values shown in the cards, with what they read and their article and quote."""
    seen = set()
    for key in nodes:
        t = (r.trace or {}).get(key)
        if not t or key in seen or ex.is_input(r, key) or t["value"] in (None, 0):
            continue
        seen.add(key)
        f, mm = key
        src = t["source"][0] if t["source"] else None
        reads = ", ".join(d.fact_label(k[0]) for k in ex.children(r, key, st.session_state.k_omega_v)[:6])
        layer = ui.badge("company policy", "orange") if t["layer"] == "company" else ""
        ui.html(f"<div class='rule{' company' if t['layer'] == 'company' else ''}'>{layer}<b>{d.fact_label(f)}</b> = "
                f"{d.fmt(f, t['value'])} <span class='muted'>({'month of ' + d.MONTHS[mm - 1] if mm else 'annual'})</span><br>"
                f"<span class='muted'>Reads: {reads or '-'} · {g.term('sumber', 'Source')}: "
                f"{d.short_doc(src['document']) + ' · ' + src['provision'] if src else '-'} · rule <code>{t['rule']}</code>"
                f"</span>" + (f"<div class='quote'>“{src['quote']}”</div>" if src else "") + "</div>")


def results(rec, cols, found, autos):
    s = st.session_state
    case = case_of(rec, s.k_omega_v)
    r, err = d.compute(case, s.k_omega_v)
    changed_banner(r, rec)
    blocked = warnings(r, rec, cols, found)
    if err:
        st.error(f"Calculation failed: {err}")
        return
    if blocked:
        return
    m = rec["month"]
    omega = s.k_omega_v
    shown = list(range(rec["start"], m + 1))
    final = not r.partial and r.final_month == m
    work = {x: ex.working(r, (ex.ROOT, x), omega) for x in shown}
    s.k_last = {"case": case, "month": m, "final": final, "due": {x: r.periods[x].get(ex.ROOT) for x in shown},
                "work": {x: (getattr(ex.rule(r, work[x], omega), "id", "-"), getattr(ex.rule(r, work[x], omega), "expression", None),
                             [(k, ex.value(r, k)) for k in ex.children(r, work[x], omega)]) for x in shown}}
    total = sum(rec["withheld"].get(str(x), r.periods[x].get(ex.ROOT) or 0) for x in shown)
    after = [f for f in ex.downstream(r, m, omega)
             if any(ex._number(r.periods[x].get(f)) for x in shown)][:2]      # e.g. PPh borne by the government
    c = st.columns(2 + len(after))
    c[0].metric(f"PPh 21 {d.MONTHS[m - 1]}", d.money(r.periods[m].get(ex.ROOT)), help=g.tip("PPh 21"))
    c[1].metric(f"Total {d.MON[shown[0] - 1]}–{d.MON[m - 1]}", d.money(total), help="Total PPh 21 up to this month.")
    for col, f in zip(c[2:], after):
        col.metric(f"{d.fact_label(f)} {d.MON[shown[0] - 1]}–{d.MON[m - 1]}",
                   d.money(sum(r.periods[x].get(f) or 0 for x in shown)))
    left, right = st.columns([1, 1], gap="large")
    with left:
        nodes = month_card(r, rec, cols, m, omega)
        if final:
            nodes += year_card(r, rec, omega)
        else:
            st.caption(f"The annual recalculation appears in the closing month ({d.MONTHS[max(rec['end'], rec['start']) - 1]}).")
    with right:
        names = ex.outputs(r, shown, omega)        # the results the knowledge base marks as output
        names = [f for f in names if f == ex.ROOT] + [f for f in names if f != ex.ROOT]
        rows = []
        for x in shown:
            p = r.periods[x]
            src = ex.source_of(r, work[x])
            rows.append({"Month": d.MONTHS[x - 1], **{d.fact_label(f): d.fmt(f, p.get(f)) for f in names},
                         "Computed with": (d.short_doc(src["document"]) + " " + src["provision"]) if src else "",
                         "Already withheld (entered)": d.money(rec["withheld"][str(x)]) if str(x) in rec["withheld"] else ""})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption("Table columns: values the knowledge base marks as results that are not zero in these months.")
        st.download_button("Download breakdown (CSV)", pd.DataFrame(rows).to_csv(index=False).encode(),
                           f"pph21_{rec['name'] or 'employee'}_{rec['year']}.csv", icon=":material/download:")
        with st.expander("Why this number? (rules and articles)"):
            basis(r, nodes)
        with st.expander("Data sent to the engine"):
            st.caption("Only the months up to the calculation month are sent; the engine recognizes the closing month from "
                       "the month employment ends and only gives annual values in that month. PPh entered in "
                       "'PPh already withheld' is sent as a recorded value.")
            st.json(case, expanded=False)


def show():
    s = st.session_state
    s.page_ctx = "kalkulator"
    if "rec" not in s:
        _apply_scenario("Regular employee")
    st.title("PPh 21 calculator")
    g.md(f"Calculate {g.term('PPh 21')} for one employee up to a given month. Fill in the form or choose a scenario, "
         "then change any number in the table. The data asked for follows the rules in force; hover over dotted "
         "words or ⓘ icons for explanations.")
    top_bar()
    period_bar()
    s.g_date = date(s.rec["year"], s.rec["month"], 1)     # glossary numbers of that tax month
    profile()
    rec = s.rec
    before = _norm(rec)
    pre, _ = d.compute(case_of(rec, s.k_omega_v), s.k_omega_v)
    cols, found, autos = grid(pre)
    if _norm(rec) != before and any(c[3] == "computed" for c in cols):
        st.rerun()        # an edit changed what the rules compute: show the locked columns up to date
    with st.expander("Cases not calculated here"):
        st.markdown("Only **permanent employees** at **one company** in **one tax year**. Not calculated: non-permanent or "
                    "daily employees, transfers from another company in the same year, returning to work in the same "
                    "year, payments after leaving, severance, retirees, foreign employees (PPh 26), foreign currency.")
    results(rec, cols, found, autos)
