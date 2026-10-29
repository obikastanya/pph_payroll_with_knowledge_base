"""Research results at a glance: hypothesis verdicts, E2 conditions, E3 regulation replay, E4 impact detectors.
Everything is read from the result files of the experiments (docs/hasil, experiments/)."""
import csv
import json
from collections import Counter

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import state
import widgets as ui

VERDICTS = [
    ("H1", "Representasi menyatakan perubahan tak terlihat tanpa mengubah engine (RA ≥ 0,70)",
     "16/16, batas bawah 0,829 (konservatif 15/16; tanpa konvensi pembulatan 8/16)", "diterima"),
    ("H2a", "Batas atas laju kesalahan senyap (SER) ≤ 0,25", "SER 3/18, batas atas 0,377", "tidak diterima"),
    ("H2b", "Pembaruan benar (CAR) usulan > B3 dan B4", "8/18 vs 8/18 dan 9/18", "tidak diterima"),
    ("H2b", "SER usulan tidak lebih buruk (δ = 0,10)", "vs B3 terpenuhi (0,004); vs B4 tidak (0,153)", "sebagian"),
    ("H3a", "Laju adaptif berantai (OAR) ≥ 0,75", "31/33 (batas bawah 0,821); bangkit ulang 23/33 (0,540)",
     "diterima, tidak kokoh"),
    ("H3b", "Kesalahan terpicu ≤ batas derau", "29 kasus vs 0", "tidak didukung"),
    ("H4a", "Recall detektor dampak ≥ 0,70", "0,91 (batas bawah 0,75)", "diterima"),
    ("H4b", "F2 detektor > pembanding B5", "+0,19 vs pindai teks; −0,006 vs tandai semua", "tidak diterima"),
]
RUNS = {"Usulan": ("e2-regulasi", "e2-pkb", "proposed"), "B3 (pertama lolos G1–G2)": ("e2-regulasi", "e2-pkb", "B3"),
        "B4 (mayoritas tanpa gerbang)": ("e2-regulasi", "e2-pkb", "B4"),
        "AB2 (tanpa konteks KB)": ("e2-ab2-regulasi", "e2-ab2-pkb", "proposed"),
        "m = 5": ("e2-regulasi-m5", "e2-pkb-m5", "proposed"),
        "Model kedua (GPT)": ("e2-model2-regulasi", "e2-model2-pkb", "proposed"),
        "Seleksi sempurna (batas atas)": ("e2-regulasi", "e2-pkb", "AB4_perfect")}


def _outcomes(run, cond):
    path = state.EXPERIMENTS / run / "scores.csv"
    if not path.exists():
        return Counter()
    return Counter(r["outcome"] for r in csv.DictReader(open(path, encoding="utf-8")) if r["condition"] == cond)


def show():
    st.title("Hasil penelitian")
    st.caption("Dibaca langsung dari berkas hasil eksperimen. Rincian dan keterbatasan: docs/BAHAN_PAPER.md dan "
               "paper/draft/paper.pdf.")
    st.markdown("### Putusan hipotesis")
    color = {"diterima": "ok", "tidak diterima": "no", "tidak didukung": "no", "sebagian": "na",
             "diterima, tidak kokoh": "na"}
    html = "<div class='card'><table style='width:100%'><tr><th>H</th><th>Pernyataan</th><th>Hasil</th><th>Putusan</th></tr>"
    for h, text, res, verdict in VERDICTS:
        html += f"<tr><td><b>{h}</b></td><td>{text}</td><td class='muted'>{res}</td><td>{ui.pill(verdict, color[verdict])}</td></tr>"
    st.markdown(html + "</table></div>", unsafe_allow_html=True)

    st.markdown("### E2 · akuisisi satu langkah (18 dokumen nyata)")
    rows = []
    for name, (reg, pkb, cond) in RUNS.items():
        c = _outcomes(reg, cond) + _outcomes(pkb, cond)
        if sum(c.values()):
            rows.append({"kondisi": name, "benar": c["benar"], "salah (senyap)": c["salah"], "abstain": c["abstain"]})
    df = pd.DataFrame(rows)
    fig = go.Figure()
    for col, colr in (("benar", "#2e7d32"), ("salah (senyap)", "#c62828"), ("abstain", "#9e9e9e")):
        fig.add_trace(go.Bar(y=df["kondisi"], x=df[col], name=col, orientation="h", marker_color=colr))
    fig.update_layout(barmode="stack", height=340, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="dokumen",
                      yaxis=dict(autorange="reversed"), legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig, width="stretch")
    ui.note("Gerbang dan konsensus menekan pembaruan salah (3 vs 7 pada B3), dibayar dengan abstain; pembaruan benar "
            "tidak bertambah. PKB tidak pernah benar di kondisi mana pun; usulan aman karena abstain.")

    st.markdown("### E3 · regulation replay (33 peristiwa)")
    fig = go.Figure()
    for run, name, colr in (("e3-tetap", "transplantasi (terdaftar)", ui.REG),
                            ("e3-bangkit-ulang", "pembangkitan ulang", ui.COMPANY)):
        path = state.EXPERIMENTS / run / "chain.csv"
        if not path.exists():
            continue
        ch = list(csv.DictReader(open(path, encoding="utf-8")))
        fig.add_trace(go.Scatter(x=[r["event"] for r in ch], y=[int(r["wrong"]) for r in ch], name=name,
                                 line=dict(color=colr)))
        summ = json.loads((state.EXPERIMENTS / run / "chain_summary.json").read_text(encoding="utf-8"))
        st.caption(f"{name}: OAR {summ['OAR']:.3f} (batas bawah {summ['OAR_lower_one_sided']:.3f}), "
                   f"kasus salah di akhir {summ['final_wrong_tuples']}")
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="kasus salah (dari ±600)",
                      legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig, width="stretch")
    ui.note("Pada rantai transplantasi, satu pengecoh yang salah diterapkan (P01, PP 49/2023) merusak hampir semua kasus "
            "sesudahnya; pada pembangkitan ulang kesalahan itu tidak terjadi, tetapi setiap abstain tampak sebagai "
            "kesalahan baru.")

    st.markdown("### E4 · deteksi dampak lintas lapis (134 pasangan)")
    path = state.ROOT / "docs" / "hasil" / "rq4_ringkasan.json"
    if path.exists():
        s = json.loads(path.read_text(encoding="utf-8"))
        names = {"detector": "Detektor statis (beku)", "detector_v2": "Detektor v2 (eksploratori)",
                 "b5_flag_all": "B5(i) tandai semua yang menyentuh F_Δ", "b5_flat_scan": "B5(ii) pindai teks datar"}
        st.dataframe(pd.DataFrame([{"pendeteksi": names[k], "presisi": round(s[k]["precision"], 3),
                                    "recall": round(s[k]["recall"], 3), "F2": round(s[k]["F2"], 3)}
                                   for k in names if k in s]), hide_index=True, width="stretch")
