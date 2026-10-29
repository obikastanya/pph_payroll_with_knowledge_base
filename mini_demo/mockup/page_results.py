"""Research results for people who are not researchers: four questions, a plain answer each, the numbers as
"x out of y", what it means for the user, and the technical detail folded away.

All numbers come from docs/BAHAN_PAPER.md (final results, tag hasil-v2).
"""
import streamlit as st

import glossary as g
import ui

GREEN, RED, YELLOW, GREY = "#2e9e5b", "#d64545", "#e8b730", "#d9d8d4"


def dots(parts, per_row=20):
    """Unit chart: [(count, colour, label)] as small squares, one per item."""
    cells = "".join(f"<span title='{label}' style='display:inline-block;width:14px;height:14px;border-radius:3px;"
                    f"margin:2px;background:{colour}'></span>" for n, colour, label in parts for _ in range(n))
    legend = " &nbsp; ".join(f"<span style='display:inline-block;width:10px;height:10px;border-radius:2px;"
                             f"background:{c};margin-right:4px'></span>{n} {label}" for n, c, label in parts)
    total = sum(n for n, _, _ in parts)
    width = min(total, per_row) * 18
    return f"<div style='max-width:{width}px;line-height:0'>{cells}</div><div class='muted' style='margin-top:.35rem'>{legend}</div>"


def question(n, q, verdict, colour, answer, picture, meaning, detail):
    with st.container(border=True):
        left, right = st.columns([1.25, 1], gap="large")
        with left:
            ui.html(f"<span class='muted'>Pertanyaan {n}</span><div style='font-size:1.15rem;font-weight:650;"
                    f"margin:.1rem 0 .45rem 0;line-height:1.35'>{q}</div>"
                    f"{ui.badge(verdict, colour)}<div class='answer'>{answer}</div>")
            ui.html(f"<div class='explain'><b>Artinya bagi pengguna:</b> {meaning}</div>")
        with right:
            ui.html(picture)
        with st.expander("Detail untuk peneliti"):
            st.markdown(detail)


def show():
    st.title("Hasil penelitian")
    g.md("Penelitian ini menguji satu gagasan: kalkulator PPh 21 yang pengetahuannya disimpan sebagai "
         f"{g.term('knowledge base')} (aturan, angka, dan tabel dengan tanggal berlaku dan sumber pasal), lalu diperbarui "
         "dari peraturan baru dengan bantuan AI dan pemeriksaan otomatis. Empat pertanyaan, dijawab dengan peraturan "
         "nyata 2023–2026.")
    c = st.columns(4)
    c[0].metric("Peraturan nyata diuji", "13", help="Peristiwa perubahan PPh 21 dan BPJS 2023–2026.")
    c[1].metric("Dokumen perusahaan (PKB)", "5", help=g.tip("kebijakan perusahaan"))
    c[2].metric("Dokumen yang tidak relevan", "20", help="Peraturan yang mirip tetapi tidak mengubah PPh 21 pegawai tetap.")
    c[3].metric("Kasus pegawai uji", "2.398", help="Kombinasi gaji, status, sektor, bulan, dan komponen penghasilan.")

    question(1, "Bisakah perubahan aturan dimasukkan tanpa mengubah program?", "Ya", "green",
             "16 dari 16 perubahan aturan yang belum pernah dilihat berhasil dimasukkan, dan 100 dari 100 contoh "
             "hitungan cocok.",
             dots([(16, GREEN, "perubahan berhasil")], per_row=16) +
             "<div class='muted' style='margin-top:.6rem'>2.609 angka hasil hitung diperiksa.</div>",
             "Saat peraturan berubah, yang diperbarui hanya isi knowledge base (aturan, angka, tabel), bukan kode "
             "program. Itu yang memungkinkan halaman Manajemen KB.",
             "- Hipotesis H1 (RA ≥ 0,70): 16/16, CP 95% [0,794; 1,000], batas bawah satu sisi 0,829. **Diterima.**\n"
             "- Bergantung pada aturan pembulatan: tanpa konvensi pembulatan PER-11/PJ/2025, 8/16 (semua selisih ≤ Rp11); "
             "konservatif 15/16.\n- Perubahan ditulis oleh agen independen, belum oleh pakar payroll manusia.")

    question(2, "Bisakah AI membaca peraturan baru dan mengusulkan pembaruan yang benar?", "Sebagian", "yellow",
             "Dari 18 dokumen nyata: 8 diusulkan benar, 3 salah, dan untuk 7 sistem ragu sehingga tidak mengusulkan apa pun.",
             dots([(8, GREEN, "benar"), (3, RED, "salah"), (7, YELLOW, "sistem ragu")], per_row=9) +
             "<div class='muted' style='margin-top:.8rem'><b>Tanpa cek kesepakatan</b> (usulan pertama yang lolos "
             "pemeriksaan dasar):</div>" +
             dots([(8, GREEN, "benar"), (7, RED, "salah"), (3, YELLOW, "sistem ragu")], per_row=9),
             "AI menghemat kerja untuk peraturan negara, tetapi setiap usulan tetap harus direview. Pemeriksaan "
             f"otomatis dan {g.term('kesepakatan', 'cek kesepakatan')} menurunkan usulan salah dari 7 menjadi 3; "
             f"gantinya sistem lebih sering {g.term('ragu')}. Untuk PKB perusahaan, tulis aturannya sendiri: kelima PKB ditahan.",
             "- Regulasi 13: benar 8, salah 3 (E02, E07, E11), abstain 2. PKB 5: abstain 5/5.\n"
             "- H2a (batas atas SER ≤ 0,25): SER 3/18, batas atas 0,377. **Tidak diterima.**\n"
             "- H2b CAR usulan 8/18 = B3 8/18, B4 9/18. **Tidak diterima**; non-inferioritas SER vs B3 terpenuhi.\n"
             "- Pengecoh: 7/20 dianggap relevan, 1/20 sampai salah diterapkan (PP 49/2023).\n"
             "- Model kedua (gpt-6.1-sol): SER 3/18, CAR 7/18. Biaya per dokumen regulasi USD 0,12–1,87.")

    question(3, "Kalau pembaruan masuk terus-menerus, apakah hitungan tetap benar?", "Belum kokoh", "red",
             "31 dari 33 dokumen yang masuk berurutan tidak menambah kesalahan. Tetapi 2 yang salah terbawa terus: "
             "di akhir rantai 579 dari 600 kasus uji menjadi salah.",
             dots([(31, GREEN, "tidak menambah kesalahan"), (2, RED, "menambah kesalahan")], per_row=11) +
             "<div class='muted' style='margin-top:.8rem'>Kasus uji salah di akhir rantai tanpa koreksi</div>" +
             "<div style='background:#f0efec;border-radius:6px;height:16px;width:100%;margin-top:4px'>"
             "<div style='background:#d64545;height:16px;border-radius:6px;width:96.5%'></div></div>"
             "<div class='muted'>579 dari 600</div>",
             "Satu pembaruan salah (di sini dokumen yang sebenarnya tidak relevan tetapi keliru diterima) merusak hitungan berikutnya sampai "
             "diperbaiki. Karena itu sistem menyimpan semua versi, bisa dikembalikan, dan menolak mengubah hitungan "
             "masa lalu.",
             "- OAR (proporsi peristiwa tanpa kesalahan baru), transplantasi Δ terisolasi: 31/33, batas bawah 0,821, "
             "H3a **diterima** pada analisis terdaftar. Pembangkitan ulang: 23/33, 0,540 (**tidak kokoh**).\n"
             "- Kesalahan baru dari E02 (15 kasus) dan P01 (264 kasus); P01 bertahan sampai akhir.\n"
             "- H3b kesalahan terpicu 29 kasus vs batas derau 0: **tidak didukung**; 26 dari 29 berasal dari abstain.")

    question(4, "Bisakah sistem memberi tahu kebijakan perusahaan mana yang ikut terdampak?", "Ya", "green",
             "Dari 33 pasangan kebijakan dan peraturan yang benar-benar terdampak, 30 ditandai. Dari 42 peringatan, "
             "30 tepat.",
             dots([(30, GREEN, "terdampak dan ditandai"), (3, RED, "terlewat")], per_row=11) +
             "<div class='muted' style='margin-top:.8rem'>Peringatan yang muncul</div>" +
             dots([(30, GREEN, "tepat"), (12, GREY, "alarm palsu")], per_row=14),
             "Saat peraturan berubah, Anda mendapat daftar kebijakan perusahaan yang perlu dicek. Sekitar 3 dari 10 "
             "peringatan ternyata tidak perlu diubah, dan sesekali ada yang terlewat.",
             "- H4a recall ≥ 0,70: 0,91 (CI 0,75–1,00). **Diterima.** Presisi 0,71; F₂ 0,862.\n"
             "- H4b F₂ > pembanding: +0,193 vs pindai teks; −0,006 vs tandai semua yang menyentuh nilai berubah. "
             "**Tidak diterima.**\n- 134 pasangan, 33 positif; 27 dari 33 dari kebijakan buatan.")

    st.subheader("Dibandingkan cara lain")
    c = st.columns(3)
    with c[0].container(border=True):
        st.markdown("**Kalkulator yang dikodekan tangan**")
        ui.html("<div class='answer'>26 dan 915 hari</div>")
        st.caption("Keterlambatan dua kalkulator terbuka memasukkan tarif TER sesudah PP 58/2023 terbit. Di knowledge "
                   "base, perubahan itu satu pembaruan data.")
    with c[1].container(border=True):
        st.markdown("**AI langsung menghitung dari peraturan**")
        ui.html("<div class='answer'>76 dari 100 tepat</div>")
        st.caption("97 dari 100 selisih paling banyak Rp1. Tetapi tanpa jejak pasal, hasil bisa berbeda tiap kali, dan "
                   "biayanya USD 0,068 untuk setiap hitungan.")
    with c[2].container(border=True):
        st.markdown("**AI menyusun aturan dari nol**")
        ui.html("<div class='answer'>0 lolos pemeriksaan</div>")
        st.caption("Tanpa knowledge base sebagai konteks, tidak ada usulan yang lolos. Memperbarui sedikit demi sedikit "
                   "jauh lebih mudah daripada menulis ulang semuanya.")

    st.subheader("Yang perlu diketahui")
    st.markdown("- Pakar pembanding dan pemeriksa adalah agen AI independen, belum pakar payroll manusia.\n"
                "- Jumlah dokumen kecil (18 nyata), jadi selisih antar-metode sulit dibuktikan secara statistik.\n"
                "- Cakupan: pegawai tetap, satu pemberi kerja, satu tahun pajak.\n"
                "- Semua peraturan uji terbit sebelum batas pengetahuan model AI, sehingga hafalan tidak dapat "
                "disingkirkan sepenuhnya; uji dengan peraturan kontrafaktual tidak menemukan hafalan.")
    ui.mock("Rincian teknis lengkap tetap tersedia di paper dan docs/BAHAN_PAPER.md.")
