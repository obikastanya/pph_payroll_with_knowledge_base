"""Payroll calculator: one payslip with its trace, comparison across knowledge-base versions and knowledge dates,
results across periods, and a batch payroll run."""
import calendar
import csv
import io
import json
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import kg
import state
import widgets as ui
from reasoner import NOW, OUTPUTS, ReasoningError, compute


def _employee_form():
    with st.container(border=True):
        st.markdown("**Employee**")
        name = st.text_input("Name", "Employee B", key="c_name")
        status = st.selectbox("PTKP status", ui.STATUSES, key="c_status")
        salary = st.number_input("Basic salary", 0, 200_000_000, 9_500_000, 50_000, key="c_salary")
        allowance = st.number_input("Fixed allowance", 0, 100_000_000, 0, 50_000, key="c_allow")
        overtime = st.number_input("Overtime pay", 0, 100_000_000, 500_000, 50_000, key="c_ot")
        dtp = st.toggle("Employer in a DTP sector (PMK 10/2025)", True, key="c_dtp")
    return {"name": name, "ptkp_status": status, "salary": int(salary), "allowance": int(allowance),
            "overtime": int(overtime), "dtp_sector": dtp}


def _case(emp, year, month):
    return {k: v for k, v in emp.items() if k != "name"} | {"year": year, "month": month}


def _try(g, case, w):
    try:
        return compute(g, case, w), None
    except (ReasoningError, ValueError, TypeError) as e:
        return None, str(e)


def _payslip(emp, case, result, version, w):
    v = result.values
    rows = [("Basic salary", case["salary"]), ("Fixed allowance", case["allowance"]), ("Overtime", case["overtime"])]
    deductions = [("PPh 21 due", v.get("pph21")), ("Borne by government (DTP)", -(v.get("pph21_dtp") or 0)),
                  ("PPh 21 withheld", v.get("pph21_withheld"))]
    known = "everything known today" if w == NOW else f"knowledge as of {w:%d %b %Y}"
    html = [f"<div class='slip'><h4>Payslip · {ui.MONTHS[case['month'] - 1]} {case['year']}</h4>",
            f"<div class='muted'>{emp['name']} · {case['ptkp_status']} · {version} · {known}</div><table>"]
    html += [f"<tr><td>{k}</td><td class='r'>{ui.rp(x)}</td></tr>" for k, x in rows]
    html.append(f"<tr class='total'><td>Gross income</td><td class='r'>{ui.rp(v.get('gross_income'))}</td></tr>")
    html += [f"<tr><td>{k}</td><td class='r'>{ui.rp(x)}</td></tr>" for k, x in deductions]
    html.append(f"<tr class='total'><td>Take-home pay</td><td class='r'>{ui.rp(v.get('take_home_pay'))}</td></tr></table></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _trace_table(g, result):
    records = {r["id"]: r for r in kg.rule_records(g)}
    rows = []
    for fact in sorted(result.trace, key=lambda f: (f not in OUTPUTS, f)):
        rid, _ = result.trace[fact]
        r = records[rid]
        rows.append({"fact": fact, "value": ui.number(result.values.get(fact)), "rule": rid, "layer": r["layer"],
                     "modality": r["modality"], "source": r["article"], "quote": r["quote"] or "",
                     "expression": r["expression"]})
    return pd.DataFrame(rows)


def _references(case, w, result):
    refs = json.loads((kg.DATA / "reference" / "references.json").read_text(encoding="utf-8"))["references"]
    hits = []
    for ref in refs:
        ref_w = date.fromisoformat(ref["knowledge_date"]) if "knowledge_date" in ref else NOW
        if ref["case"] == case and ref_w == w:
            got = {k: result.values.get(k) for k in ref["expected"]}
            hits.append((ref, got))
    return hits


def tab_payslip(emp, versions):
    c1, c2 = st.columns([1, 1])
    with c1:
        year, month = ui.period_picker("p", (2024, 8))
    with c2:
        w = ui.knowledge_picker("p")
    name, g = state.version_picker("Knowledge base version", "p_version")
    case = _case(emp, year, month)
    result, err = _try(g, case, w)
    if err:
        st.error(f"The engine cannot compute this case with {name}: {err}")
        return
    left, right = st.columns([1, 1.3])
    with left:
        _payslip(emp, case, result, name.split(" · ")[0], w)
        for fact, pid in sorted(result.conflicts):
            st.warning(f"Company policy **{pid}** sets `{fact}`, but a mandatory regulation overrides it. "
                       "The engine applies the regulation and reports the conflict (condition A4).", icon=":material/gavel:")
        for ref, got in _references(case, w, result):
            ok = got == ref["expected"]
            (st.success if ok else st.error)(f"Reference {ref['id']} ({ref['source']}): expected {ref['expected']}, "
                                             f"engine {got}. {ref['working']}", icon=":material/fact_check:")
    with right:
        st.markdown("**Why these numbers**")
        st.graphviz_chart(ui.calc_dot(g, result, case), width="stretch")
        ui.where("Every output fact has a trace to the rule and article that produced it (RQ1 diagnostic: trace completeness).")
    st.markdown("**Calculation trace**")
    st.dataframe(_trace_table(g, result), hide_index=True, width="stretch")


def tab_compare(emp):
    st.markdown("Same employee and period, computed with several knowledge bases or knowledge dates. "
                "Rows that differ are highlighted.")
    year, month = ui.period_picker("cmp", (2025, 1))
    options = list(state.catalog())
    chosen = st.multiselect("Knowledge-base versions", options, default=[o for o in options if o.startswith(("v0", "v3", "Gold"))][:3]
                            or options[:2], key="cmp_versions")
    as_known = st.toggle("Also show each version as known at payroll time (end of that month)", False, key="cmp_known")
    case = _case(emp, year, month)
    run_date = date(year, month, calendar.monthrange(year, month)[1])
    columns, notes = {}, {}
    for name in chosen:
        g = state.catalog()[name]
        for w, suffix in [(NOW, "")] + ([(run_date, f" · known {run_date:%d %b %Y}")] if as_known else []):
            label = name.split(" · ")[0] + suffix if name.startswith("v") else name + suffix
            result, err = _try(g, case, w)
            if err:
                columns[label] = {f: "error" for f in OUTPUTS} | {"pph21 rule": err[:40], "conflicts": ""}
                continue
            columns[label] = {f: ui.number(result.values.get(f)) for f in OUTPUTS}
            columns[label]["pph21 rule"] = "{} ({})".format(*result.trace.get("pph21", ("-", "-")))
            columns[label]["withheld rule"] = result.trace.get("pph21_withheld", ("-",))[0]
            columns[label]["conflicts"] = ", ".join(p for _, p in sorted(result.conflicts)) or "-"
            notes[label] = name
    if not columns:
        return
    df = pd.DataFrame(columns)
    df.index = [ui.OUTPUT_LABELS.get(i, i) for i in df.index]
    differs = df.nunique(axis=1) > 1
    st.dataframe(df.style.apply(lambda row: ["background-color: #fff3cd" if differs[row.name] else "" for _ in row], axis=1),
                 width="stretch")
    ui.where("Version comparison is how A2 (agreement with gold) and A3 (isolation) are checked by eye; "
             "the experiments do the same over all of S^E.")


def tab_periods(emp):
    st.markdown("One employee across every month from 2023 to 2026. Regime changes appear as steps. The dotted line uses "
                "only what was known at the end of each month, so a retroactive regulation shows up as a gap.")
    options = list(state.catalog())
    chosen = st.multiselect("Versions", options, default=options[:1] + [state.GOLD], key="per_versions")
    fact = st.radio("Fact", OUTPUTS, index=3, horizontal=True, format_func=lambda f: ui.OUTPUT_LABELS[f], key="per_fact")
    months = [(y, m) for y in range(2023, 2027) for m in range(1, 13)]
    x = [date(y, m, 1) for y, m in months]
    fig = go.Figure()
    gaps = []
    for name in chosen:
        g = state.catalog()[name]
        now = [(_try(g, _case(emp, y, m), NOW)[0] or None) for y, m in months]
        fig.add_scatter(x=x, y=[r.values.get(fact) if r else None for r in now], name=name.split(" · ")[0], mode="lines",
                        line_shape="hv")
        then = [_try(g, _case(emp, y, m), date(y, m, calendar.monthrange(y, m)[1]))[0] for y, m in months]
        fig.add_scatter(x=x, y=[r.values.get(fact) if r else None for r in then], name=name.split(" · ")[0] + " (as known then)",
                        mode="lines", line_shape="hv", line_dash="dot")
        for (y, m), a, b in zip(months, now, then):
            if a and b and a.values.get(fact) != b.values.get(fact):
                gaps.append({"version": name, "period": f"{y}-{m:02d}", "as known then": ui.number(b.values.get(fact)),
                             "as known today": ui.number(a.values.get(fact)),
                             "difference": ui.number((b.values.get(fact) or 0) - (a.values.get(fact) or 0))})
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), yaxis_title=ui.OUTPUT_LABELS[fact],
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, width="stretch")
    if gaps:
        st.markdown("**Periods where later knowledge changes the result (retroactive regulation)**")
        st.dataframe(pd.DataFrame(gaps), hide_index=True, width="stretch")
        ui.mockup("How the difference is settled (refund, or recalculation in December) follows the legal mechanism, which "
                  "the skeleton requires to be defined before the gold values of retroactive events exist (PANDUAN stage 4). "
                  "The mini engine only shows the gap.")


def _roster():
    return json.loads((kg.DATA / "roster.json").read_text(encoding="utf-8"))["employees"]


def tab_batch():
    st.markdown("Monthly payroll for every employee of Company X with one knowledge-base version.")
    c1, c2 = st.columns([1, 1])
    with c1:
        year, month = ui.period_picker("b", (2025, 1))
    with c2:
        w = ui.knowledge_picker("b")
    name, g = state.version_picker("Knowledge base version", "b_version")
    base_name = st.selectbox("Compare with", ["(none)"] + list(state.catalog()), key="b_base")
    upload = st.file_uploader("Upload a roster (CSV)", type="csv", key="b_upload",
                              help="Columns: name, ptkp_status, salary, allowance, overtime, dtp_sector")
    roster = _roster()
    if upload is not None:
        roster = [{"name": r["name"], "ptkp_status": r["ptkp_status"], "salary": int(r["salary"]),
                   "allowance": int(r.get("allowance") or 0), "overtime": int(r.get("overtime") or 0),
                   "dtp_sector": str(r.get("dtp_sector", "")).lower() in ("1", "true", "yes")}
                  for r in csv.DictReader(io.StringIO(upload.getvalue().decode("utf-8")))]
    rows = []
    for emp in roster:
        case = _case(emp, year, month)
        result, err = _try(g, case, w)
        row = {"employee": emp["name"], "status": emp["ptkp_status"]}
        if err:
            rows.append(row | {"error": err})
            continue
        row |= {ui.OUTPUT_LABELS[f]: result.values.get(f) for f in OUTPUTS}
        row["pph21 rule"] = result.trace.get("pph21", ("-",))[0]
        row["conflicts"] = ", ".join(p for _, p in sorted(result.conflicts)) or ""
        if base_name != "(none)":
            base, berr = _try(state.catalog()[base_name], case, w)
            row["Δ withheld vs comparison"] = None if berr else (result.values.get("pph21_withheld") or 0) - (base.values.get("pph21_withheld") or 0)
        rows.append(row)
    df = pd.DataFrame(rows)
    m1, m2, m3 = st.columns(3)
    m1.metric("Gross payroll", ui.rp(df[ui.OUTPUT_LABELS["gross_income"]].sum()))
    m2.metric("PPh 21 withheld", ui.rp(df[ui.OUTPUT_LABELS["pph21_withheld"]].sum()))
    m3.metric("Borne by government", ui.rp(df[ui.OUTPUT_LABELS["pph21_dtp"]].fillna(0).sum()))
    st.dataframe(df, hide_index=True, width="stretch",
                 column_config={c: st.column_config.NumberColumn(format="localized") for c in df.columns
                                if c in ui.OUTPUT_LABELS.values() or c.startswith("Δ")})
    st.download_button("Download payroll (CSV)", df.to_csv(index=False), f"payroll_{year}_{month:02d}.csv", "text/csv")
    template = io.StringIO()
    csv.DictWriter(template, ["name", "ptkp_status", "salary", "allowance", "overtime", "dtp_sector"]).writeheader()
    st.download_button("Download roster template", template.getvalue(), "roster_template.csv", "text/csv")
    ui.mockup("The full payroll covers the whole year: December recalculation, irregular income (THR, bonus), gross-up, "
              "BPJS, proration, and the bukti potong. The mini engine computes one regular month.")


def show():
    st.title("Payroll calculator")
    st.markdown("One engine, many knowledge bases. Pick the version and the knowledge date, and every number comes with the "
                "rule and the article it came from.")
    left, right = st.columns([1, 3.2])
    with left:
        emp = _employee_form()
    with right:
        t1, t2, t3, t4 = st.tabs([":material/receipt_long: Payslip", ":material/compare_arrows: Compare versions",
                                  ":material/timeline: Across periods", ":material/groups: Batch payroll"])
        with t1:
            tab_payslip(emp, state.catalog())
        with t2:
            tab_compare(emp)
        with t3:
            tab_periods(emp)
        with t4:
            tab_batch()
