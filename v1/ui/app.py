"""Demo UI: kalkulator payroll PPh 21 dengan dan tanpa knowledge base, serta penjelajah knowledge base.

    env\\Scripts\\streamlit.exe run ui\\app.py

UI hanya menyusun isian dan menampilkan keluaran mesin; pengetahuan pajak ada di kb/ (versi KB) atau di kode (versi tanpa KB).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

st.set_page_config(page_title="Kalkulator Payroll PPh 21", page_icon=":material/account_balance:", layout="wide",
                   initial_sidebar_state="collapsed")

from ui import kalkulator, tab_kb  # noqa: E402
from ui import mesin as M  # noqa: E402

CSS = """
<style>
:root { --biru: #2a78d6; --oranye: #eb6834; --teks2: #52514e; }
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1680px; }
.judul h1 { margin: 0; padding: 0; font-size: 2.2rem; letter-spacing: -0.02em; }
.sub { color: var(--teks2); font-size: 1.05rem; margin: .15rem 0 .6rem 0; }
.cerita { background: #f7f7f5; border-left: 4px solid var(--biru); padding: .7rem 1rem; border-radius: 6px;
          color: #2b2a28; font-size: 1.02rem; margin: .2rem 0 .9rem 0; }
.alur { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem; margin: .3rem 0 1rem 0; }
.alur .langkah { padding: .45rem .85rem; border-radius: 8px; background: #f4f4f2; border: 1px solid #e3e2de; font-weight: 600; }
.alur .langkah.regulasi { background: #e8f1fc; border-color: #b9d3f4; color: #1c5cab; }
.alur .langkah.perusahaan { background: #fdeee7; border-color: #f6c9b4; color: #a3431c; }
.alur .panah { color: #a3a29d; font-size: 1.2rem; }
.mekanisme { padding: .55rem .9rem; border-radius: 8px; margin: .1rem 0 .8rem 0; font-size: 1rem; }
.mekanisme.kb { background: #e8f1fc; color: #173f73; }
.mekanisme.tanpa { background: #f4f4f2; color: #2b2a28; }
div[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
div[data-testid="stMetricValue"] > div { white-space: normal !important; overflow: visible !important; text-overflow: clip !important; }
button[role="tab"] p { font-size: 1.06rem !important; }
div[data-testid="stDataFrame"] { font-variant-numeric: tabular-nums; }
</style>
"""

KET_MESIN = {
    M.KB: "<div class='mekanisme kb'><b>Dengan knowledge base.</b> Aturan pajak pemerintah dan kebijakan Perusahaan X dibaca dari "
          "berkas KB (YAML/CSV). Setiap angka bisa ditelusuri ke aturan dan pasalnya; konflik kebijakan terdeteksi otomatis.</div>",
    M.TANPA_KB: "<div class='mekanisme tanpa'><b>Tanpa knowledge base.</b> Kalkulator payroll biasa: aturan pajak dan kebijakan "
                "perusahaan ditulis langsung di kode Python. Hasilnya harus sama dengan versi KB, tetapi perubahan aturan berarti "
                "mengubah kode.</div>",
}


def main():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown("<div class='judul'><h1>Kalkulator Payroll PPh 21</h1></div>"
                "<div class='sub'>Gaji, BPJS, THR, dan PPh 21 pegawai tetap, tahun pajak 2023-2026: regulasi pemerintah + "
                "kebijakan perusahaan.</div>", unsafe_allow_html=True)
    t_kalk, t_kb = st.tabs([":material/calculate: Kalkulator", ":material/schema: Knowledge Base"])
    with t_kalk:
        s_kb, s_tanpa = st.tabs([":material/hub: Dengan KB", ":material/terminal: Tanpa KB"])
        for wadah, mesin in ((s_kb, M.KB), (s_tanpa, M.TANPA_KB)):
            with wadah:
                st.markdown(KET_MESIN[mesin], unsafe_allow_html=True)
                kalkulator.tampilkan(mesin)
    with t_kb:
        tab_kb.tampilkan()


main()
