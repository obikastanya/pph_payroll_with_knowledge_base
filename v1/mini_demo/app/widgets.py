"""Formatting, status labels, and Graphviz diagrams shared by the pages."""
import re
from datetime import date
from fractions import Fraction

import streamlit as st

import kg
import reasoner

REG, COMPANY = "#2a78d6", "#eb6834"
REG_FILL, COMPANY_FILL = "#e8f1fc", "#fdeee7"
OUTPUT_LABELS = {"gross_income": "Gross income", "pph21": "PPh 21 due", "pph21_dtp": "PPh 21 borne by government (DTP)",
                 "pph21_withheld": "PPh 21 withheld", "take_home_pay": "Take-home pay"}
STATUSES = ("TK/0", "TK/1", "TK/2", "TK/3", "K/0", "K/1", "K/2", "K/3")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

CSS = """
<style>
.block-container { padding-top: 1.6rem; max-width: 1500px; }
div[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
div[data-testid="stDataFrame"] { font-variant-numeric: tabular-nums; }
.slip { border: 1px solid #e3e2de; border-radius: 10px; padding: 1rem 1.2rem; background: #fff; }
.slip h4 { margin: 0 0 .4rem 0; }
.slip table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
.slip td { padding: .22rem 0; border-bottom: 1px solid #f0efec; }
.slip td.r { text-align: right; }
.slip tr.total td { font-weight: 700; border-top: 2px solid #0b0b0b; border-bottom: none; }
.slip .muted { color: #6b6a66; font-size: .86rem; }
.step { font-weight: 650; font-size: 1.05rem; margin-top: .6rem; }
</style>
"""


def setup():
    st.markdown(CSS, unsafe_allow_html=True)


def number(x):
    if x is None:
        return "-"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, (int, Fraction)):
        return f"{int(x):,}" if Fraction(x).denominator == 1 else f"{float(x):,.2f}"
    return str(x)


def rp(x):
    return "-" if x is None else f"Rp{number(x)}"


def mockup(text):
    """Marks a part of the screen that only shows what the full system will do."""
    st.caption(f":orange-badge[Mockup] {text}")


def where(text):
    """Links a screen element to the skeleton and the guide."""
    st.caption(f":blue-badge[Paper] {text}")


def period_picker(key, default=(2024, 8)):
    c1, c2 = st.columns(2)
    year = c1.selectbox("Tax year", (2023, 2024, 2025, 2026), index=(2023, 2024, 2025, 2026).index(default[0]), key=f"{key}_y")
    month = c2.selectbox("Month", range(1, 13), index=default[1] - 1, format_func=lambda m: MONTHS[m - 1], key=f"{key}_m")
    return year, month


def knowledge_picker(key, default=None):
    mode = st.radio("Knowledge date ω", ("Everything known today", "As known on a date"), key=f"{key}_mode",
                    horizontal=True, index=0 if default is None else 1,
                    help="Bitemporal view: rules recorded after this date are ignored, as if the calculation ran on that day.")
    if mode == "Everything known today":
        return reasoner.NOW
    return st.date_input("Known on", value=default or date(2025, 1, 31), key=f"{key}_date",
                         min_value=date(2016, 1, 1), max_value=date(2026, 12, 31))


def rule_status(rec, t, w, superseded):
    if rec["valid_from"] > t or (rec["valid_until"] and t > rec["valid_until"]):
        return "not in force"
    if rec["recorded_on"] > w:
        return "not yet known"
    if rec["id"] in superseded:
        return "superseded"
    return "in force"


def _q(text):
    return '"' + str(text).replace('"', "'") + '"'


def kb_dot(g, t, w, mode="Data flow", only_in_force=False, layers=("regulation", "company")):
    """Diagram of the knowledge graph at period t and knowledge date w.
    Data flow: facts and the rules that produce and read them. Provenance: documents, articles, and rules. Full: both."""
    records = [r for r in kg.rule_records(g) if r["layer"] in layers]
    _, _, superseded = reasoner.select(g, t, w)
    status = {r["id"]: rule_status(r, t, w, superseded) for r in records}
    if only_in_force:
        records = [r for r in records if status[r["id"]] == "in force"]
    ids = {r["id"] for r in records}
    out = ["digraph KB {", "rankdir=TB; bgcolor=transparent; nodesep=0.3; ranksep=0.4;",
           'node [fontname="Helvetica" fontsize=12 margin="0.08,0.04"];', 'edge [fontname="Helvetica" fontsize=8 color="#8a8984"];']
    for r in records:
        st_ = status[r["id"]]
        line, fill = (REG, REG_FILL) if r["layer"] == "regulation" else (COMPANY, COMPANY_FILL)
        style = "rounded,filled" + ("" if st_ == "in force" else ",dashed")
        if st_ != "in force":
            fill = "#f4f4f2"
        label = f"{r['id']}\\n{r['modality']} · {r['valid_from']:%Y-%m}" + (f"..{r['valid_until']:%Y-%m}" if r["valid_until"] else "")
        if st_ != "in force":
            label += f"\\n({st_})"
        out.append(f'{_q(r["id"])} [shape=box style="{style}" color="{line}" fillcolor="{fill}" label={_q(label)}];')
    if mode in ("Data flow", "Full"):
        facts = {r["produces"] for r in records} | {f for r in records for f in r["reads"]}
        for f in sorted(facts):
            bold = "penwidth=2" if f in reasoner.OUTPUTS else ""
            out.append(f'{_q("f:" + f)} [shape=ellipse style=filled fillcolor="#f7f7f5" color="#6b6a66" {bold} label={_q(f)}];')
        for r in records:
            out.append(f'{_q(r["id"])} -> {_q("f:" + r["produces"])} [color="#3b3a37"];')
            for f in r["reads"]:
                out.append(f'{_q("f:" + f)} -> {_q(r["id"])} [style=dashed];')
            for name in re.findall(r"'([A-Z][A-Z0-9-]+)'", r["expression"]):
                out.append(f'{_q("t:" + name)} [shape=cylinder style=filled fillcolor="#fff7e0" color="#b98900" label={_q(name)}];')
                out.append(f'{_q("t:" + name)} -> {_q(r["id"])} [style=dotted color="#b98900"];')
    if mode in ("Provenance", "Full"):
        for r in records:
            doc, art = "d:" + r["document"], "a:" + r["article"]
            out.append(f'{_q(doc)} [shape=folder style=filled fillcolor="#eeeeec" label={_q(r["document"])}];')
            out.append(f'{_q(art)} [shape=note label={_q(r["article"].replace(r["document"], "").strip() or r["article"])}];')
            out.append(f'{_q(doc)} -> {_q(art)} [arrowhead=none color="#b4b3ae"];')
            out.append(f'{_q(art)} -> {_q(r["id"])} [style=dotted color="#b4b3ae"];')
    for r in records:
        for old in r["supersedes"]:
            if old in ids:
                out.append(f'{_q(r["id"])} -> {_q(old)} [color="#c62828" fontcolor="#c62828" label="supersedes"];')
    for rid, pid, fact in kg.static_conflicts(g):
        if rid in ids and pid in ids:
            out.append(f'{_q(pid)} -> {_q(rid)} [dir=none style=dashed color="#c62828" fontcolor="#c62828" label="conflict"];')
    out.append("}")
    return "\n".join(out)


def calc_dot(g, result, case):
    """How one result was derived: inputs, facts with values, and the winning rule on every edge."""
    records = {r["id"]: r for r in kg.rule_records(g)}
    out = ["digraph C {", "rankdir=TB; bgcolor=transparent; nodesep=0.2; ranksep=0.3;",
           'node [fontname="Helvetica" fontsize=10];', 'edge [fontname="Helvetica" fontsize=8 color="#8a8984"];']
    for fact, (rid, _) in result.trace.items():
        r = records[rid]
        line, fill = (REG, REG_FILL) if r["layer"] == "regulation" else (COMPANY, COMPANY_FILL)
        pen = "penwidth=2" if fact in reasoner.OUTPUTS else ""
        out.append(f'{_q(fact)} [shape=box style="rounded,filled" color="{line}" fillcolor="{fill}" {pen} '
                   f'label={_q(fact + chr(92) + "n" + number(result.values.get(fact)))}];')
        for f in r["reads"]:
            out.append(f'{_q(f)} -> {_q(fact)} [label={_q(rid)}];')
        for field in sorted(set(re.findall(r"employee\.(\w+)", (r["condition"] or "") + r["expression"]))):
            out.append(f'{_q("in:" + field)} [shape=plaintext label={_q(field + " = " + number(case.get(field)))}];')
            out.append(f'{_q("in:" + field)} -> {_q(fact)} [label={_q(rid)} style=dashed];')
    out.append("}")
    return "\n".join(out)
