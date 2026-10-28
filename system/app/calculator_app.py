r"""PPh 21 calculator on the research knowledge base (Streamlit).

    env\Scripts\streamlit.exe run system\app\calculator_app.py

The same computation as system/tools/calculate.py: the gold knowledge base (dataset/12_emas/kb.trig), a knowledge date,
optionally a company policy of the corpus, and the rule trace behind any value. The legacy prototype in ui/ is not used.
"""
import sys
from argparse import Namespace
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "system", ROOT / "system" / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import streamlit as st  # noqa: E402

import build_gold  # noqa: E402
from calculate import COLUMNS, build_case, knowledge_base  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402

st.set_page_config(page_title="Kalkulator PPh 21 (KB penelitian)", layout="wide")
st.title("Kalkulator PPh 21")
st.caption("Knowledge base penelitian (emas, dataset/12_emas). Hasil mengikuti peraturan yang diketahui pada tanggal "
           "pengetahuan yang dipilih.")


@st.cache_resource
def kb_for(policy):
    return knowledge_base(policy)


@st.cache_data
def policies():
    return [""] + sorted(u.doc.id for u in build_gold.collect_side() if u.kind == "policy")


with st.sidebar:
    year = st.number_input("Tahun pajak", 2013, 2027, 2025)
    salary = st.number_input("Gaji pokok per bulan", 0, 10**10, 12_000_000, step=500_000)
    allowance = st.number_input("Tunjangan tetap per bulan", 0, 10**10, 0, step=100_000)
    ptkp = st.selectbox("Status PTKP", ["TK/0", "TK/1", "TK/2", "TK/3", "K/0", "K/1", "K/2", "K/3"])
    sex = st.selectbox("Jenis kelamin", ["M", "F"])
    method = st.selectbox("Metode", ["gross", "gross_up", "employer_borne"])
    klu = st.text_input("KLU pemberi kerja", "") or None
    jkk = st.selectbox("Kelompok risiko JKK", ["very_low", "low", "medium", "high", "very_high"])
    thr = st.number_input("THR", 0, 10**10, 0, step=500_000)
    thr_month = st.number_input("Bulan THR", 1, 12, 4)
    bonus = st.number_input("Bonus", 0, 10**10, 0, step=500_000)
    bonus_month = st.number_input("Bulan bonus", 1, 12, 12)
    vehicle = st.number_input("Natura kendaraan per bulan", 0, 10**9, 0, step=100_000)
    start, end = st.slider("Bulan bekerja", 1, 12, (1, 12))
    no_npwp = st.checkbox("Tanpa NPWP")
    policy = st.selectbox("Kebijakan perusahaan", policies()) or None
    omega = st.date_input("Tanggal pengetahuan", date.today())

args = Namespace(year=int(year), salary=int(salary), allowance=int(allowance), ptkp=ptkp, sex=sex, method=method,
                 klu=klu, jkk_risk=jkk, thr=int(thr), thr_month=int(thr_month), bonus=int(bonus),
                 bonus_month=int(bonus_month), vehicle=int(vehicle), start_month=start, end_month=end,
                 no_npwp=no_npwp, policy=policy)
case = build_case(args)
result = evaluate_case(kb_for(policy), case, omega, trace=True)

rows = [{"bulan": m, **{c: result.periods[m].get(c) for c in COLUMNS}} for m in sorted(result.periods)]
st.subheader("Per bulan")
st.dataframe(rows, width="stretch", hide_index=True)
st.subheader("Setahun")
st.json({k: result.year[k] for k in ("annual_gross", "job_expense", "ptkp_amount", "taxable_income", "annual_pph21",
                                       "refund_to_employee") if k in result.year})
for c in result.conflicts:
    st.warning(f"Konflik: {c}")
for e in result.errors:
    st.error(e)

st.subheader("Jejak")
month = st.selectbox("Bulan (0 = setahun)", [0] + sorted(result.periods), index=1 if result.periods else 0)
fact = st.text_input("Fakta", "pph21_due")


def lines(m, f, depth=0, seen=None):
    seen = set() if seen is None else seen
    t = (result.trace or {}).get((f, m)) or (result.trace or {}).get((f, 0))
    if t is None or (f, m) in seen:
        return []
    seen.add((f, m))
    src = "; ".join(dict.fromkeys(f"{s['document']} {s['provision']}" for s in t.get("source") or []))
    out = [f"{'    ' * depth}{f} = {t['value']}   [{t['rule']}]   {src}"]
    for dep in t.get("reads") or []:
        dep_f, dep_m = dep if isinstance(dep, (list, tuple)) else (dep, m)
        out += lines(dep_m, dep_f, depth + 1, seen)
    return out


st.code("\n".join(lines(int(month), fact)) or "tidak ada jejak untuk fakta ini", language=None)
