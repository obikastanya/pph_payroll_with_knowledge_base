"""Look, formatting, pickers and Graphviz diagrams shared by the pages."""
import re
from datetime import date
from fractions import Fraction

import streamlit as st

import state

REG, COMPANY, PARAM = "#2a78d6", "#eb6834", "#b98900"
REG_FILL, COMPANY_FILL, PARAM_FILL = "#e8f1fc", "#fdeee7", "#fff7e0"
MONTHS = ("Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des")
STATUSES = ("TK/0", "TK/1", "TK/2", "TK/3", "K/0", "K/1", "K/2", "K/3")
METHODS = {"gross": "Gross (dipotong dari pegawai)", "gross_up": "Gross-up (tunjangan pajak)",
           "employer_borne": "Ditanggung pemberi kerja"}
JKK = {"very_low": "Sangat rendah (0,24%)", "low": "Rendah (0,54%)", "medium": "Sedang (0,89%)",
       "high": "Tinggi (1,27%)", "very_high": "Sangat tinggi (1,74%)"}
FACT_LABELS = {
    "base_salary": "Gaji pokok", "fixed_allowance": "Tunjangan tetap", "overtime_pay": "Lembur", "thr": "THR",
    "bonus": "Bonus", "other_regular_income": "Penghasilan teratur lain", "jkk_premium": "Premi JKK (pemberi kerja)",
    "jkm_premium": "Premi JKM (pemberi kerja)", "health_premium_employer": "Premi BPJS Kesehatan (pemberi kerja)",
    "tax_allowance": "Tunjangan pajak", "gross_income": "Penghasilan bruto", "pph21_due": "PPh 21 terutang",
    "pph21_dtp": "PPh 21 ditanggung pemerintah (DTP)", "jht_employee": "Iuran JHT pegawai",
    "jp_employee": "Iuran JP pegawai", "take_home_pay": "Take-home pay", "annual_pph21": "PPh 21 setahun",
    "annual_gross": "Bruto setahun", "taxable_income": "Penghasilan kena pajak", "ptkp_amount": "PTKP",
    "job_expense": "Biaya jabatan", "refund_to_employee": "Lebih potong dikembalikan"}

CSS = """
<style>
.block-container { padding-top: 1.5rem; max-width: 1500px; }
div[data-testid="stMetricValue"], div[data-testid="stDataFrame"] { font-variant-numeric: tabular-nums; }
.card { border: 1px solid #e3e2de; border-radius: 12px; padding: 1rem 1.2rem; background: var(--background-color, #fff); }
.slip h4 { margin: 0 0 .3rem 0; }
.slip table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
.slip td { padding: .22rem 0; border-bottom: 1px solid rgba(128,128,128,.15); }
.slip td.r { text-align: right; }
.slip tr.total td { font-weight: 700; border-top: 2px solid rgba(128,128,128,.6); border-bottom: none; }
.slip tr.sub td { color: #6b6a66; font-size: .9rem; }
.muted { color: #6b6a66; font-size: .86rem; }
.pill { display: inline-block; padding: .05rem .5rem; border-radius: 999px; font-size: .78rem; margin-right: .25rem; }
.pill.reg { background: #e8f1fc; color: #1b5aa6; } .pill.com { background: #fdeee7; color: #b5481d; }
.pill.ok { background: #e6f4ea; color: #1e7b34; } .pill.no { background: #fdecea; color: #b3261e; }
.pill.na { background: #f1f1ef; color: #6b6a66; }
.step { font-weight: 650; font-size: 1.02rem; margin-top: .8rem; }
</style>
"""


def setup():
    st.markdown(CSS, unsafe_allow_html=True)


def number(x):
    if x is None:
        return "-"
    if isinstance(x, bool):
        return "ya" if x else "tidak"
    if isinstance(x, Fraction):
        return f"{int(x):,}".replace(",", ".") if x.denominator == 1 else f"{float(x):.4g}".replace(".", ",")
    if isinstance(x, int):
        return f"{x:,}".replace(",", ".")
    if isinstance(x, float):
        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(x)


def frame(rows):
    """DataFrame for display: exact fractions become decimals (Arrow cannot hold Fraction)."""
    import pandas as pd

    def conv(v):
        return float(v) if isinstance(v, Fraction) else v
    return pd.DataFrame([{k: conv(v) for k, v in dict(r).items()} for r in rows])


def rp(x):
    return "-" if x is None else f"Rp{number(x)}"


def label(fact):
    return FACT_LABELS.get(fact, fact)


def pill(text, kind):
    return f"<span class='pill {kind}'>{text}</span>"


def note(text):
    st.caption(f":blue-badge[Penelitian] {text}")


# ---------------------------------------------------------------------------------------------------------- pickers
def knowledge_picker(key, default=None):
    mode = st.radio("Tanggal pengetahuan ω", ("Semua yang diketahui hari ini", "Seperti diketahui pada tanggal"),
                    key=f"{key}_mode", horizontal=True, index=0 if default is None else 1,
                    help="Tampilan bitemporal: aturan yang dicatat sesudah tanggal ini diabaikan, seolah-olah "
                         "perhitungan dijalankan pada hari itu.")
    if mode.startswith("Semua"):
        return state.TODAY
    return st.date_input("Diketahui pada", value=default or date(2024, 1, 31), key=f"{key}_date",
                         min_value=date(2013, 1, 1), max_value=state.TODAY, format="DD/MM/YYYY")


def version_picker(key, label_text="Versi knowledge base"):
    options = state.versions()
    labels = [o[0] for o in options]
    choice = st.selectbox(label_text, labels, index=len(labels) - 1, key=key,
                          help="Setiap pembaruan yang diterapkan membuat versi baru; versi terakhir adalah KB kini.")
    return dict(options)[choice]


def policy_picker(key, allow_none=True):
    names = sorted(state.policy_deltas())
    opts = (["(tanpa kebijakan perusahaan)"] if allow_none else []) + names
    choice = st.selectbox("Kebijakan perusahaan", opts, key=key,
                          help="Lapis perusahaan: aturan kebijakan dipasang di atas regulasi; aturan wajib selalu "
                               "menang dan pelanggarannya dilaporkan.")
    return None if choice.startswith("(") else choice


def period_picker(key, year=2025, month=1):
    c1, c2 = st.columns(2)
    years = list(range(2013, 2027))
    y = c1.selectbox("Tahun pajak", years, index=years.index(year), key=f"{key}_y")
    m = c2.selectbox("Bulan", range(1, 13), index=month - 1, format_func=lambda i: MONTHS[i - 1], key=f"{key}_m")
    return y, m


# ---------------------------------------------------------------------------------------------------------- status
def status(rec, t, omega):
    """Status of a record for period t (a date) as known on omega."""
    if rec.recorded_on > omega and getattr(rec, "layer", "") != "company":
        return "belum diketahui"
    if rec.valid_from and rec.valid_from > t:
        return "belum berlaku"
    if rec.valid_until and rec.valid_until < t:
        return "sudah berakhir"
    return "berlaku"


def sources(rec):
    return "; ".join(dict.fromkeys(f"{s.document} {s.provision}" for s in rec.source or ()))


def quotes(rec):
    return " | ".join(f"“{s.quote}”" for s in rec.source or ())


def text_of(expr):
    return "" if expr is None else expr.text


# ---------------------------------------------------------------------------------------------------------- diagrams
def _q(text):
    return '"' + str(text).replace("\\", "\\\\").replace('"', "'") + '"'


def derivation_dot(result, month, fact, depth=2, max_nodes=18, skip_zero=True):
    """How one value was derived: facts with their values and the rule that produced each (from the engine trace).
    Inputs that are zero or empty are left out so the picture stays readable."""
    trace = result.trace or {}

    def entry(f, m):
        return trace.get((f, m)) or trace.get((f, 0))

    def shown(f, m):
        t = entry(f, m)
        return t is not None and not (skip_zero and t["value"] in (0, None, "", False) and (f, m) != (fact, month))

    out = ["digraph D {", "rankdir=RL; bgcolor=transparent; nodesep=0.25; ranksep=0.45;",
           'node [fontname="Helvetica" fontsize=11 shape=box style="rounded,filled" margin="0.12,0.06"];',
           'edge [color="#8a8984" arrowsize=0.7];']
    seen, frontier = set(), [((fact, month), 0)]
    while frontier and len(seen) < max_nodes:
        (f, m), d = frontier.pop(0)
        t = entry(f, m)
        if t is None or (f, m) in seen:
            continue
        seen.add((f, m))
        line, fill = (REG, REG_FILL) if t["layer"] == "regulation" else (COMPANY, COMPANY_FILL)
        pen = " penwidth=2.2" if (f, m) == (fact, month) else ""
        when = "" if m == month else ("  (setahun)" if m == 0 else f"  ({MONTHS[m - 1]})")
        lab = f"{label(f)}|{number(t['value'])}{when}|{t['rule']}"
        out.append(f'{_q(f"{f}@{m}")} [color="{line}" fillcolor="{fill}"{pen} '
                   f'label={_q(lab).replace("|", chr(92) + "n")}];')
        if d >= depth:
            continue
        for dep in t.get("reads") or []:
            df, dm = dep if isinstance(dep, (list, tuple)) else (dep, m)
            if shown(df, dm) and len(seen) + len(frontier) < max_nodes * 2:
                out.append(f'{_q(f"{df}@{dm}")} -> {_q(f"{f}@{m}")};')
                frontier.append(((df, dm), d + 1))
    out.append("}")
    # keep only edges whose both ends were drawn
    nodes = {f"{f}@{m}" for f, m in seen}
    kept = [x for x in out if "->" not in x or all(n.strip('" ;') in nodes for n in x.split("->"))]
    return "\n".join(kept)


_NAMES = re.compile(r"(param|lookup|in_table|rate_of|table_rows|progressive)\('([a-z0-9_]+)'")


def dependency_dot(view, focus, depth=2, upstream=True, downstream=False, layers=("regulation", "company"),
                   t=None, omega=None, only_in_force=False, max_rules=45):
    """Part of the knowledge graph around one fact: rules that produce it and the facts, parameters and tables they
    read (upstream), and the rules that read it (downstream)."""
    rules = [r for r in view.rules.values() if r.layer in layers]
    if only_in_force and t is not None:
        rules = [r for r in rules if status(r, t, omega or state.TODAY) == "berlaku"]
    by_fact, readers = {}, {}
    for r in rules:
        by_fact.setdefault(r.produces, []).append(r)
        for e in (r.expression, r.condition):
            for f in (e.dependencies() if e is not None else ()):
                readers.setdefault(f, []).append(r)
    chosen, facts, frontier = {}, {focus}, [(focus, 0)]
    while frontier and len(chosen) < max_rules:
        f, d = frontier.pop(0)
        if d >= depth:
            continue
        nxt = []
        if upstream:
            nxt += [(r, "up") for r in by_fact.get(f, [])]
        if downstream:
            nxt += [(r, "down") for r in readers.get(f, [])]
        for r, way in nxt:
            if r.id in chosen:
                continue
            chosen[r.id] = r
            if way == "up":
                for e in (r.expression, r.condition):
                    for g in (e.dependencies() if e is not None else ()):
                        if g not in facts:
                            facts.add(g)
                            frontier.append((g, d + 1))
            else:
                if r.produces not in facts:
                    facts.add(r.produces)
                    frontier.append((r.produces, d + 1))
    out = ["digraph K {", "rankdir=LR; bgcolor=transparent; nodesep=0.22; ranksep=0.5;",
           'node [fontname="Helvetica" fontsize=10];', 'edge [fontname="Helvetica" fontsize=8 color="#8a8984"];']
    involved = {r.produces for r in chosen.values()} | {g for r in chosen.values() for e in (r.expression, r.condition)
                                                         if e is not None for g in e.dependencies()} | {focus}
    for f in sorted(involved):
        out_fact = view.facts.get(f)
        pen = "penwidth=2.2" if f == focus else ("penwidth=1.5" if out_fact is not None and out_fact.output else "")
        out.append(f'{_q("f:" + f)} [shape=ellipse style=filled fillcolor="#f7f7f5" color="#6b6a66" {pen} label={_q(f)}];')
    names = set()
    for r in chosen.values():
        line, fill = (REG, REG_FILL) if r.layer == "regulation" else (COMPANY, COMPANY_FILL)
        stt = status(r, t, omega or state.TODAY) if t is not None else "berlaku"
        style = "rounded,filled" + ("" if stt == "berlaku" else ",dashed")
        lab = f"{r.id}\\n{r.modality} · {r.valid_from:%Y-%m}" + (f"..{r.valid_until:%Y-%m}" if r.valid_until else "")
        if stt != "berlaku":
            lab += f"\\n({stt})"
        out.append(f'{_q(r.id)} [shape=box style="{style}" color="{line}" fillcolor="{fill if stt == "berlaku" else "#f4f4f2"}" '
                   f'label={_q(lab)}];')
        out.append(f'{_q(r.id)} -> {_q("f:" + r.produces)} [color="#3b3a37"];')
        for e in (r.expression, r.condition):
            if e is None:
                continue
            for g in e.dependencies():
                out.append(f'{_q("f:" + g)} -> {_q(r.id)} [style=dashed];')
            for kind, name in _NAMES.findall(e.text):
                names.add(name)
                out.append(f'{_q("p:" + name)} -> {_q(r.id)} [style=dotted color="{PARAM}"];')
        for o in r.overrides:
            if o in chosen:
                out.append(f'{_q(r.id)} -> {_q(o)} [color="#c62828" fontcolor="#c62828" label="override"];')
    for name in sorted(names):
        out.append(f'{_q("p:" + name)} [shape=cylinder style=filled fillcolor="{PARAM_FILL}" color="{PARAM}" label={_q(name)}];')
    out.append("}")
    return "\n".join(out), len(chosen)
