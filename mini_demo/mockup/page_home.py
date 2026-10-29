"""Home: what the system is, how it works, the menus and their main features, the state of the demo, the demo steps,
and the reset to the initial state."""
import streamlit as st

import data as d
import demo
import glossary as g
import ui

FLOW = """digraph F { rankdir=LR; bgcolor=transparent; nodesep=.3; ranksep=.4;
node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=11 color="#b4b3ae" fillcolor="#ffffff"];
edge [color="#8a8984" arrowsize=.7 fontname="Helvetica" fontsize=9 fontcolor="#6b6a66"];
doc [label="Dokumen baru\\nperaturan / kebijakan\\nperusahaan" shape=note fillcolor="#f0efec"];
ai [label="AI membaca dan\\nmenyusun beberapa\\nversi usulan" fillcolor="#e8f1fc" color="#2a78d6"];
chk [label="Pemeriksaan otomatis\\n+ cek kesepakatan\\n(atau sistem ragu)"];
rev [label="Review manusia\\nsetujui / perbaiki / tolak" fillcolor="#fdeee7" color="#eb6834"];
kb [label="Knowledge base\\naturan + tanggal berlaku\\n+ sumber pasal" shape=cylinder fillcolor="#fff7e0" color="#b98900"];
eng [label="Mesin hitung\\nhasil + alasan\\nsampai pasal"];
calc [label="Kalkulator\\nPPh 21 pegawai" penwidth=2];
imp [label="Dampak ke kebijakan\\nperusahaan" style="rounded,dashed"];
doc -> ai -> chk -> rev -> kb -> eng -> calc; kb -> imp -> rev [style=dashed];
asst [label="Asisten AI\\nmembantu review\\ndan mengerjakan" shape=oval fillcolor="#e8f1fc" color="#2a78d6"];
asst -> rev [style=dotted arrowhead=none]; }"""

MENUS = [
    ("Kalkulator PPh 21", ":material/calculate:", ["Profil pegawai bawaan yang bisa diubah", "Rincian bulan-bulan sebelumnya bisa diubah",
                                                  "Hasil sampai bulan yang dipilih, hitung setahun di masa terakhir",
                                                  "Skenario umum mengisi semua data sekaligus",
                                                  "Kolom data dibentuk dari aturan yang berlaku"]),
    ("Penampil knowledge base", ":material/hub:", ["Peta topik dan alur perhitungan", "Angka dari waktu ke waktu",
                                                  "Riwayat dan perbandingan dua tanggal",
                                                  "Data yang dibutuhkan aturan", "Pencarian"]),
    ("Manajemen knowledge base", ":material/edit_document:", ["Dokumen baru dengan hasil kerja AI",
                                                             "Review: setujui, sunting, minta AI perbaiki, tolak",
                                                             "Contoh sebelum/sesudah dan dampak kebijakan",
                                                             "Tambah, ubah, cabut: manual atau minta AI",
                                                             "Cek KB dan riwayat versi"]),
    ("Asisten AI", ":material/forum:", ["Jendela pop-up di semua halaman", "Chat tersimpan, bisa dihapus",
                                        "Pilih model; bawaan yang murah", "Menyiapkan draf, tidak pernah menyetujui"]),
]

STEPS = [
    ("Hitung pegawai pabrik pakaian jadi, Januari 2026 (skenario 'DTP padat karya 2026'): belum ada DTP.",
     lambda s: False),
    ("Review PMK 105/2025: temukan kesalahan usulan AI, minta AI memperbaiki, lalu setujui.",
     lambda s: s["decided"].get("E11") == "disetujui"),
    ("Hitung lagi skenario yang sama: DTP muncul, lengkap dengan pasalnya.", lambda s: False),
    ("Setujui kebijakan SP14: kolom data HR muncul sendiri di kalkulator (skenario 'THR menurut kebijakan perusahaan').",
     lambda s: s["decided"].get("SP14") == "disetujui"),
    ("Setujui PER-11/PJ/2025 (berlaku surut) dan bandingkan hitungan 'per tanggal pengetahuan' di kalkulator.",
     lambda s: s["decided"].get("E13") == "disetujui"),
    ("PKB WIKA: sistem ragu. Minta AI mengerjakan ulang atau tulis manual.",
     lambda s: s["decided"].get("PKB-WIKA-2025") in ("disetujui", "ditolak")),
    ("Minta asisten membuat draf (mis. batas upah JP 2027), review, setujui.",
     lambda s: any(a["id"].startswith("ANGKA") for a in s["approved"])),
    ("Kembalikan ke keadaan awal demo.", lambda s: False),
]


def reset_button(key):
    with st.popover("Kembalikan ke keadaan awal demo", icon=":material/restart_alt:", width="stretch"):
        st.markdown("Semua yang dilakukan selama demo dihapus: pembaruan yang disetujui, draf, suntingan, unggahan, dan "
                    "chat asisten. Knowledge base kembali ke keadaan awal.")
        if st.button("Ya, kembalikan", type="primary", key=key, icon=":material/restart_alt:"):
            demo.reset()
            st.rerun()


def show():
    st.session_state.page_ctx = "beranda"
    st.title("Sistem PPh 21 berbasis knowledge base")
    g.md(f"Sistem menghitung {g.term('PPh 21')} pegawai tetap dari {g.term('knowledge base')}: aturan, angka, dan tabel "
         f"pajak yang masing-masing punya {g.term('berlaku', 'tanggal berlaku')} dan {g.term('sumber', 'sumber pasal')}. "
         "Saat peraturan atau kebijakan perusahaan berubah, AI membaca dokumennya dan menyusun usulan pembaruan; "
         "pemeriksaan otomatis menyaringnya dan manusia menyetujuinya. Programnya tidak perlu diubah.")
    s = demo.load()
    c = st.columns(4)
    c[0].metric("Knowledge base diketahui sampai", d.tgl(demo.known_until()), help=g.tip("dicatat"))
    c[1].metric("Aturan berlaku hari ini", len([r for r in d.kb().view(demo.TODAY).rules.values()
                                                if not d.is_input_convention(r)]), help=g.tip("aturan"))
    c[2].metric("Disetujui selama demo", len(s["approved"]), help=g.tip("pembaruan"))
    c[3].metric("Dokumen menunggu", sum(demo.status(p["id"], s) in ("review", "ragu") for p in demo.PENDING),
                help="Dokumen baru yang belum disetujui atau ditolak.")
    st.markdown("#### Alur sistem")
    st.graphviz_chart(FLOW, width="stretch")
    st.markdown("#### Menu")
    cols = st.columns(4)
    for col, (title, icon, feats) in zip(cols, MENUS):
        with col.container(border=True):
            st.markdown(f"**{icon} {title}**")
            st.markdown("\n".join(f"- {f}" for f in feats))
    st.markdown("#### Demo")
    left, right = st.columns([2, 1], gap="large")
    with left:
        g.md(f"Keadaan awal demo: knowledge base penelitian per **{demo.BASE_LABEL}**, tanpa kebijakan perusahaan, dan "
             "delapan dokumen menunggu di Manajemen KB: lima peraturan 2025–2026, satu kebijakan perusahaan, satu PKB, "
             "dan satu dokumen tidak relevan. Hasil kerja AI-nya diambil dari penelitian, jadi demo tidak memakai "
             "kredit API.")
        for i, (text, done) in enumerate(STEPS, 1):
            mark = ":material/check_circle:" if done(s) else ":material/radio_button_unchecked:"
            st.markdown(f"{mark} **{i}.** {text}")
    with right:
        with st.container(border=True):
            st.markdown("**Keadaan demo**")
            st.caption(f"{len(s['approved'])} pembaruan disetujui, {len(s['drafts'])} draf, "
                       f"{len(demo.chat_load()) // 2} pertanyaan ke asisten.")
            reset_button("home_reset")
