"""Overview: what the system is, how the parts fit, and the state of the knowledge base."""
import streamlit as st

import state
import widgets as ui

FLOW = """digraph F {
rankdir=LR; bgcolor=transparent; nodesep=0.3; ranksep=0.45;
node [fontname="Helvetica" fontsize=11 shape=box style="rounded,filled" fillcolor="#f7f7f5" color="#8a8984"];
edge [color="#8a8984"];
doc [label="Dokumen\\nregulasi / PKB" shape=note fillcolor="#eeeeec"];
llm [label="LLM\\nrelevansi + m kandidat Δ" fillcolor="#e8f1fc" color="#2a78d6"];
gates [label="Gerbang G1–G5\\nskema · kutipan · statis\\nregresi · non-vakuitas"];
cons [label="Konsensus perilaku\\n(atau abstain)"];
review [label="Review manusia" fillcolor="#fdeee7" color="#eb6834"];
kb [label="Knowledge base\\nbitemporal dua lapis\\n(knowledge graph)" shape=cylinder fillcolor="#fff7e0" color="#b98900"];
eng [label="Inference engine\\nhasil + jejak sampai pasal"];
calc [label="Kalkulator\\nslip · payroll" shape=component];
imp [label="Analisis dampak\\nlintas lapis" shape=component];
doc -> llm -> gates -> cons -> review -> kb -> eng -> calc;
kb -> imp; imp -> review [style=dashed label="laporan" fontsize=9];
}"""


def show():
    st.title("Sistem berbasis pengetahuan PPh 21")
    st.markdown("Knowledge base bitemporal dua lapis (regulasi dan kebijakan perusahaan) yang diperbarui dari dokumen "
                "oleh LLM, dijaga gerbang verifikasi, dan dihitung oleh inference engine dengan jejak sampai pasal.")
    st.graphviz_chart(FLOW, width="stretch")
    kb = state.kb()
    view = kb.view(state.TODAY)
    ws = state.workspace_files()
    c = st.columns(5)
    c[0].metric("Pembaruan", len(kb.updates), help="rantai emas + ruang kerja")
    c[1].metric("Rekaman", len(kb.records))
    c[2].metric("Aturan efektif", len(view.rules))
    c[3].metric("Kebijakan perusahaan", len(state.policy_deltas()))
    c[4].metric("Pembaruan ruang kerja", len(ws))
    st.markdown("### Halaman")
    c1, c2, c3, c4 = st.columns(4)
    with c1.container(border=True):
        st.markdown("**Kalkulator PPh 21**")
        st.caption("Slip gaji dengan diagram derivasi dan jejak sampai pasal; bandingkan versi dan tanggal pengetahuan; "
                   "satu pegawai lintas 2023–2026; payroll massal dengan CSV.")
    with c2.container(border=True):
        st.markdown("**Penampil knowledge base**")
        st.caption("Graf fakta–aturan, aturan dengan status per periode dan ω, versi tabel (TER, PTKP), timeline "
                   "bitemporal, pemeriksa kualitas, konsol SPARQL, ekspor RDF.")
    with c3.container(border=True):
        st.markdown("**Manajemen knowledge base**")
        st.caption("Kotak masuk dan alur akuisisi langkah demi langkah (putar ulang atau langsung dengan LLM), review, "
                   "Δ manual, editor kebijakan perusahaan, riwayat versi.")
    with c4.container(border=True):
        st.markdown("**Hasil penelitian**")
        st.caption("Ringkasan hipotesis H1–H4, perbandingan kondisi E2, regulation replay E3, dan detektor dampak E4.")
    ui.note("Semua angka pajak berasal dari knowledge base; aplikasi tidak menyimpan rumus pajak sendiri.")
