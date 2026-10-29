"""Glossary of the terms on screen, and the hover marker for them.

term("PTKP") renders the word with a dotted underline and a small "?"; hovering shows a short, plain explanation.
tip("PTKP") is the same explanation for the help= tooltip of a widget or metric.
"""
import html

import streamlit as st

# key: (label, explanation). Explanations are for a finance admin, not a tax lawyer: one or two sentences.
TERMS = {
    # tax calculation
    "PPh 21": ("PPh Pasal 21", "Pajak atas gaji, upah, dan imbalan lain yang diterima pegawai. Pemberi kerja memotongnya "
                               "dari gaji setiap bulan lalu menyetorkannya ke negara."),
    "masa pajak": ("Masa pajak", "Satu bulan kalender. PPh 21 dihitung, dipotong, dan dilaporkan per bulan."),
    "masa terakhir": ("Masa pajak terakhir", "Desember, atau bulan terakhir pegawai bekerja kalau ia keluar di tengah "
                                             "tahun. Di bulan ini pajak setahun dihitung ulang dengan tarif Pasal 17."),
    "TER": ("Tarif efektif bulanan (TER)", "Persentase siap pakai untuk Januari sampai November: PPh sebulan = bruto "
                                           "sebulan × tarif TER. Berlaku sejak 2024 (PP 58/2023)."),
    "kategori TER": ("Kategori TER (A, B, C)", "Tabel TER yang dipakai, ditentukan oleh status PTKP. A: TK/0, TK/1, "
                                               "K/0. B: TK/2, TK/3, K/1, K/2. C: K/3."),
    "bruto": ("Penghasilan bruto", "Semua penghasilan sebelum dipotong apa pun: gaji, tunjangan, lembur, THR, bonus, "
                                   "natura yang kena pajak, dan premi asuransi yang dibayar perusahaan."),
    "biaya jabatan": ("Biaya jabatan", "Pengurang otomatis 5% dari bruto setahun, paling banyak Rp6.000.000 setahun "
                                       "(Rp500.000 sebulan). Tidak perlu bukti."),
    "iuran pensiun": ("Iuran pensiun pegawai", "Iuran JHT dan JP yang dibayar pegawai sendiri. Mengurangi penghasilan "
                                               "yang kena pajak."),
    "neto": ("Penghasilan neto", "Bruto dikurangi biaya jabatan dan iuran pensiun pegawai."),
    "PTKP": ("Penghasilan tidak kena pajak (PTKP)", "Bagian penghasilan setahun yang bebas pajak. Besarnya tergantung "
                                                    "status kawin dan jumlah tanggungan (paling banyak 3) per 1 Januari."),
    "status PTKP": ("Status PTKP", "TK = tidak kawin, K = kawin; angka = jumlah tanggungan (0 sampai 3). Dipakai status "
                                   "pada 1 Januari; menikah atau punya anak di tengah tahun baru berlaku tahun depan."),
    "PKP": ("Penghasilan kena pajak (PKP)", "Neto setahun dikurangi PTKP, dibulatkan ke bawah ke ribuan. Inilah yang "
                                            "dikenai tarif Pasal 17."),
    "Pasal 17": ("Tarif Pasal 17", "Tarif bertingkat atas PKP setahun: 5% sampai Rp60 jt, 15% sampai Rp250 jt, 25% sampai "
                                   "Rp500 jt, 30% sampai Rp5 M, 35% di atasnya."),
    "PPh setahun": ("PPh 21 setahun", "Pajak yang seharusnya untuk seluruh tahun: PKP × tarif Pasal 17."),
    "sudah dipotong": ("Sudah dipotong", "Jumlah PPh 21 yang dipotong pada bulan-bulan sebelum masa pajak terakhir."),
    "kurang bayar": ("Kurang bayar", "PPh setahun lebih besar daripada yang sudah dipotong; selisihnya dipotong di masa "
                                     "pajak terakhir."),
    "lebih bayar": ("Lebih bayar (lebih potong)", "Yang sudah dipotong lebih besar daripada PPh setahun; kelebihannya "
                                                  "dikembalikan ke pegawai oleh pemberi kerja di masa pajak terakhir."),
    "gross": ("Metode gross", "Pajak dipotong dari gaji pegawai. Gaji bersih = bruto − PPh − iuran pegawai."),
    "gross-up": ("Metode gross-up", "Perusahaan memberi tunjangan pajak sebesar PPh-nya, jadi pegawai tidak menanggung "
                                    "pajak. Tunjangan itu sendiri ikut menambah bruto."),
    "ditanggung": ("Ditanggung pemberi kerja", "Perusahaan membayar pajaknya tanpa memberi tunjangan. Bagi pegawai tidak "
                                               "ada potongan; bagi perusahaan biaya ini bukan pengurang pajak."),
    "DTP": ("PPh 21 ditanggung pemerintah (DTP)", "Insentif: negara menanggung PPh 21 pegawai tertentu, sehingga pajaknya "
                                                  "dibayarkan ke pegawai bersama gaji. Syaratnya antara lain sektor "
                                                  "usaha (KLU) dan batas penghasilan."),
    "KLU": ("Klasifikasi lapangan usaha (KLU)", "Kode 5 digit bidang usaha pemberi kerja. Menentukan apakah pegawai bisa "
                                               "mendapat insentif DTP."),
    "NPWP": ("NPWP / NIK valid", "Pegawai yang tidak punya NPWP atau NIK yang terdaftar dapat dikenai tarif lebih tinggi "
                                 "atau tidak berhak atas insentif."),
    "natura": ("Natura dan kenikmatan", "Imbalan dalam bentuk barang atau fasilitas (rumah, kendaraan, makan). Sejak 2023 "
                                        "sebagian menjadi penghasilan yang kena pajak, sebagian dikecualikan sampai batas tertentu."),
    "THR": ("Tunjangan hari raya (THR)", "Penghasilan tidak teratur. Ditambahkan ke bruto bulan dibayarnya, sehingga TER "
                                         "bulan itu bisa naik."),
    "bonus": ("Bonus", "Penghasilan tidak teratur, ditambahkan ke bruto bulan dibayarnya."),
    "lembur": ("Upah lembur", "Penghasilan teratur yang besarnya bisa berbeda tiap bulan."),
    "tunjangan tetap": ("Tunjangan tetap", "Tunjangan yang dibayar tetap setiap bulan (jabatan, keluarga, transport)."),
    "JHT": ("Jaminan hari tua (JHT)", "Iuran BPJS Ketenagakerjaan: 2% dibayar pegawai (mengurangi pajak), 3,7% dibayar "
                                      "perusahaan (bukan penghasilan pegawai)."),
    "JP": ("Jaminan pensiun (JP)", "Iuran BPJS Ketenagakerjaan: 1% dibayar pegawai, 2% perusahaan, dari upah sampai batas "
                                   "upah JP yang naik setiap tahun."),
    "JKK": ("Jaminan kecelakaan kerja (JKK)", "Premi dibayar perusahaan, 0,24% sampai 1,74% dari upah sesuai risiko "
                                              "pekerjaan. Premi ini menambah bruto pegawai."),
    "JKM": ("Jaminan kematian (JKM)", "Premi 0,3% dibayar perusahaan; menambah bruto pegawai."),
    "BPJS Kesehatan": ("BPJS Kesehatan", "Iuran 5% dari upah sampai batas tertentu: 4% perusahaan (menambah bruto), "
                                         "1% pegawai."),
    "risiko JKK": ("Kelompok risiko JKK", "Tingkat risiko pekerjaan di perusahaan yang menentukan tarif premi JKK."),
    "zakat": ("Zakat lewat pemberi kerja", "Zakat atau sumbangan keagamaan wajib yang dipotong lewat perusahaan; boleh "
                                           "mengurangi penghasilan neto."),
    "gaji bersih": ("Gaji bersih (take-home pay)", "Yang diterima pegawai: bruto tunai dikurangi PPh yang ditanggung "
                                                   "pegawai, iuran pegawai, dan potongan lain."),
    "karyawati": ("Karyawati kawin", "Karyawati kawin memakai PTKP tidak kawin, kecuali ada keterangan suami tidak "
                                     "berpenghasilan; tanggungan ikut suami."),
    "bukti potong": ("Bukti potong 1721-A1", "Dokumen tahunan untuk pegawai berisi penghasilan dan PPh 21 setahun; dipakai "
                                             "pegawai untuk SPT Tahunan."),
    # knowledge base
    "knowledge base": ("Knowledge base (KB)", "Kumpulan aturan, angka, dan tabel pajak yang dipakai sistem untuk menghitung. "
                                              "Setiap isinya punya tanggal berlaku dan sumber pasal."),
    "aturan": ("Aturan", "Satu cara menghitung satu nilai, misalnya 'biaya jabatan = 5% × bruto, paling banyak ...'."),
    "parameter": ("Parameter", "Satu angka yang dipakai aturan, misalnya tarif 5% atau batas Rp6.000.000. Saat angka berubah "
                               "cukup parameternya yang diganti."),
    "tabel": ("Tabel", "Daftar nilai yang dipakai aturan, misalnya tabel PTKP atau tabel tarif TER."),
    "berlaku": ("Tanggal berlaku", "Sejak kapan (dan sampai kapan) aturan berlaku untuk perhitungan, sesuai peraturannya."),
    "dicatat": ("Tanggal dicatat", "Kapan aturan dimasukkan ke knowledge base. Bisa sesudah tanggal berlaku, misalnya "
                                   "peraturan yang berlaku surut."),
    "tanggal pengetahuan": ("Tanggal pengetahuan", "Menghitung 'seperti pada tanggal itu': aturan yang baru dicatat "
                                                   "sesudahnya diabaikan. Berguna untuk memeriksa ulang hitungan lama."),
    "regulasi": ("Aturan negara", "Aturan dari peraturan negara (UU, PP, PMK, PER Dirjen). Wajib diikuti."),
    "kebijakan perusahaan": ("Kebijakan perusahaan", "Aturan dari perusahaan sendiri, misalnya PKB atau peraturan "
                                                           "perusahaan (THR, bonus, lembur). Tidak boleh melanggar regulasi."),
    "wajib": ("Wajib", "Aturan yang harus dipakai; mengalahkan aturan perusahaan bila bertentangan."),
    "standar": ("Standar", "Aturan cadangan yang dipakai bila tidak ada aturan lain, misalnya cara membaca data input."),
    "pilihan": ("Pilihan", "Aturan opsional dari peraturan yang hanya berlaku bila perusahaan memilih memakainya."),
    "sumber": ("Sumber", "Dokumen, pasal, dan kutipan kalimat tempat aturan ini tertulis."),
    "versi": ("Versi KB", "Keadaan knowledge base sesudah satu pembaruan disetujui. Versi lama tetap tersimpan dan bisa "
                          "dipakai untuk menghitung ulang."),
    "pembaruan": ("Pembaruan", "Paket perubahan dari satu dokumen: aturan yang ditambah, diubah, atau dicabut."),
    "pencabutan": ("Pencabutan", "Aturan diberi tanggal akhir berlaku. Tidak dihapus, supaya hitungan lama tetap bisa "
                                 "diulang."),
    "dokumen baru": ("Dokumen baru", "Peraturan atau kebijakan perusahaan yang diunggah dan menunggu dibaca AI atau "
                                     "direview."),
    "keadaan awal": ("Keadaan awal demo", "Titik tetap tempat demo dimulai. Semua yang dilakukan selama demo bisa dihapus "
                                          "dengan tombol 'Kembalikan ke keadaan awal demo'."),
    "usulan": ("Usulan", "Rancangan pembaruan yang disusun AI dari dokumen. Belum dipakai sampai disetujui manusia."),
    "pemeriksaan": ("Pemeriksaan otomatis", "Lima pemeriksaan sebelum usulan sampai ke Anda: format, kutipan ada di "
                                            "dokumen, tidak bertabrakan, tidak mengubah hitungan masa lalu, setiap aturan "
                                            "berpengaruh."),
    "versi usulan": ("Versi usulan", "AI menyusun beberapa versi usulan secara terpisah dari dokumen yang sama. Kalau versi-versi itu "
                             "sepakat, kepercayaannya lebih tinggi."),
    "kesepakatan": ("Kesepakatan", "Usulan dipilih bila sebagian besar versi usulan menghasilkan perhitungan yang sama."),
    "ragu": ("Sistem ragu", "Versi-versi usulan tidak sepakat, jadi sistem tidak mengusulkan apa pun dan meminta "
                                          "manusia menulis pembaruannya. Lebih aman daripada menebak."),
    "dampak": ("Dampak", "Kebijakan perusahaan yang membaca nilai yang berubah, sehingga mungkin ikut perlu diperbarui."),
    "review": ("Review", "Manusia memeriksa usulan lalu menyetujui, memperbaiki, atau menolaknya."),
    "kutipan": ("Kutipan", "Kalimat persis dari dokumen yang menjadi dasar aturan. Sistem memeriksa kalimat ini benar-"
                           "benar ada di dokumen."),
    "relevan": ("Relevan", "Dokumen berisi sesuatu yang mengubah perhitungan PPh 21. Dokumen lain diabaikan."),
    "asisten": ("Asisten AI", "Chat AI di jendela pop-up yang membantu memeriksa usulan, memperbaikinya sesuai catatan "
                              "Anda, dan menyiapkan draf perubahan. Semua perubahan tetap lewat review Anda."),
}


CSS = """
<style>
.term { border-bottom: 1px dotted #8a8984; cursor: help; position: relative; display: inline-block; }
.term .q { font-size: .62em; vertical-align: super; color: #2a78d6; margin-left: 1px; font-weight: 600; }
[data-testid="stAppViewContainer"] { overflow-x: hidden; }
.term .tip { visibility: hidden; opacity: 0; position: absolute; z-index: 9999; left: 50%; top: 135%;
             transform: translateX(-50%); width: 250px; background: #24231f; color: #f7f7f5; padding: .55rem .7rem; border-radius: 8px;
             font-size: .82rem; font-weight: 400; line-height: 1.4; transition: opacity .12s; white-space: normal;
             box-shadow: 0 6px 18px rgba(0,0,0,.18); text-align: left; }
.term .tip b { color: #fff; display: block; margin-bottom: .15rem; }
.term:hover .tip { visibility: visible; opacity: 1; }
</style>
"""


def setup():
    st.markdown(CSS, unsafe_allow_html=True)


def term(key, text=None):
    """HTML: the word with a hover explanation. Use inside st.markdown(..., unsafe_allow_html=True)."""
    label, expl = TERMS[key]
    shown = html.escape(text or key)
    return (f'<span class="term">{shown}<span class="q">?</span>'
            f'<span class="tip"><b>{html.escape(label)}</b>{html.escape(expl)}</span></span>')


def tip(key):
    """Plain text explanation for help= of a widget or metric."""
    label, expl = TERMS[key]
    return f"**{label}**: {expl}"


def md(text, **kw):
    """st.markdown with HTML enabled, for lines that carry term() markers."""
    st.markdown(text, unsafe_allow_html=True, **kw)


def dictionary():
    """Searchable list of every term (sidebar)."""
    q = st.text_input("Cari istilah", "", placeholder="mis. PTKP, TER, natura", key="gl_q")
    shown = [(k, v) for k, v in TERMS.items() if q.lower() in (k + v[0] + v[1]).lower()] if q else []
    for _, (label, expl) in shown[:8]:
        st.markdown(f"**{label}**  \n{expl}")
    if q and not shown:
        st.caption("Tidak ditemukan.")
