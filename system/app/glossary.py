"""Glossary of the terms on screen, and the hover marker for them.

term("PTKP") renders the word with a dotted underline and a small "?"; hovering shows a short, plain explanation.
tip("PTKP") is the same explanation for the help= tooltip of a widget or metric.
"""
import html
import re

import streamlit as st

# key: (label, explanation). Explanations are for a finance admin, not a tax lawyer: one or two sentences.
TERMS = {
    # tax calculation
    "PPh 21": ("PPh Pasal 21", "Pajak atas gaji, upah, dan imbalan lain yang diterima pegawai. Pemberi kerja memotongnya "
                               "dari gaji setiap bulan lalu menyetorkannya ke negara."),
    "masa pajak": ("Masa pajak", "Satu bulan kalender. PPh 21 dihitung, dipotong, dan dilaporkan per bulan."),
    "masa terakhir": ("Masa pajak terakhir", "Desember, atau bulan terakhir pegawai bekerja kalau ia keluar di tengah "
                                             "tahun. Di bulan ini pajak setahun dihitung ulang dengan tarif Pasal 17."),
    "TER": ("Tarif efektif bulanan (TER)", "Persentase siap pakai untuk bulan selain masa pajak terakhir: PPh sebulan = "
                                           "bruto sebulan × tarif TER. Tabelnya {since:ter_monthly}."),
    "kategori TER": ("Kategori TER (A, B, C)", "Tabel TER yang dipakai, ditentukan oleh status PTKP. "
                                               "{groups:ter_category}."),
    "bruto": ("Penghasilan bruto", "Semua penghasilan sebelum dipotong apa pun: gaji, tunjangan, lembur, THR, bonus, "
                                   "natura yang kena pajak, dan premi asuransi yang dibayar perusahaan."),
    "biaya jabatan": ("Biaya jabatan", "Pengurang otomatis {pct:job_expense_rate} dari bruto setahun, paling banyak "
                                       "{money:job_expense_max_year} setahun. Tidak perlu bukti."),
    "iuran pensiun": ("Iuran pensiun pegawai", "Iuran JHT dan JP yang dibayar pegawai sendiri. Mengurangi penghasilan "
                                               "yang kena pajak."),
    "neto": ("Penghasilan neto", "Bruto dikurangi biaya jabatan dan iuran pensiun pegawai."),
    "PTKP": ("Penghasilan tidak kena pajak (PTKP)", "Bagian penghasilan setahun yang bebas pajak. Besarnya tergantung "
                                                    "status kawin dan jumlah tanggungan per 1 Januari: {values:ptkp}."),
    "status PTKP": ("Status PTKP", "TK = tidak kawin, K = kawin; angka = jumlah tanggungan (0 sampai 3). Dipakai status "
                                   "pada 1 Januari; menikah atau punya anak di tengah tahun baru berlaku tahun depan."),
    "PKP": ("Penghasilan kena pajak (PKP)", "Neto setahun dikurangi PTKP, dibulatkan ke bawah ke ribuan. Inilah yang "
                                            "dikenai tarif Pasal 17."),
    "Pasal 17": ("Tarif Pasal 17", "Tarif bertingkat atas PKP setahun: {brackets:pasal17}."),
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
    "natura": ("Natura dan kenikmatan", "Imbalan dalam bentuk barang atau fasilitas (rumah, kendaraan, makan). Sebagian "
                                        "menjadi penghasilan yang kena pajak, sebagian dikecualikan sampai batas tertentu, "
                                        "misalnya kupon makanan sampai {money:natura_meal_coupon_cap} sebulan."),
    "THR": ("Tunjangan hari raya (THR)", "Penghasilan tidak teratur. Ditambahkan ke bruto bulan dibayarnya, sehingga TER "
                                         "bulan itu bisa naik."),
    "bonus": ("Bonus", "Penghasilan tidak teratur, ditambahkan ke bruto bulan dibayarnya."),
    "lembur": ("Upah lembur", "Penghasilan teratur yang besarnya bisa berbeda tiap bulan."),
    "tunjangan tetap": ("Tunjangan tetap", "Tunjangan yang dibayar tetap setiap bulan (jabatan, keluarga, transport)."),
    "JHT": ("Jaminan hari tua (JHT)", "Iuran BPJS Ketenagakerjaan. Bagian pegawai {pct:jht_employee_rate} dari upah "
                                      "mengurangi pajak; bagian perusahaan bukan penghasilan pegawai."),
    "JP": ("Jaminan pensiun (JP)", "Iuran BPJS Ketenagakerjaan. Bagian pegawai {pct:jp_employee_rate} dari upah sampai "
                                   "{money:jp_wage_cap} sebulan, mengurangi pajak."),
    "JKK": ("Jaminan kecelakaan kerja (JKK)", "Premi dibayar perusahaan, {range:jkk_rates} dari upah sesuai risiko "
                                              "pekerjaan. Premi ini menambah bruto pegawai."),
    "JKM": ("Jaminan kematian (JKM)", "Premi {pct:jkm_rate} dari upah dibayar perusahaan; menambah bruto pegawai."),
    "BPJS Kesehatan": ("BPJS Kesehatan", "Iuran dari upah sampai {money:health_wage_cap} sebulan: "
                                         "{pct:health_employer_rate} perusahaan (menambah bruto), {pct:health_employee_rate} pegawai."),
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
    "aturan": ("Aturan", "Satu cara menghitung satu nilai, misalnya 'biaya jabatan = {pct:job_expense_rate} × bruto, paling "
                       "banyak ...'."),
    "parameter": ("Parameter", "Satu angka yang dipakai aturan, misalnya tarif {pct:job_expense_rate} atau batas "
                               "{money:job_expense_max_year}. Saat angka berubah "
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
    # technical view of the knowledge base
    "knowledge graph": ("Knowledge graph", "Cara KB disimpan: setiap aturan, angka, fakta, dan pasal adalah titik, dan "
                                           "hubungannya (menghasilkan, membaca, bersumber dari) adalah garis."),
    "RDF": ("RDF", "Standar W3C untuk menyimpan graf sebagai kalimat tiga bagian (triple): subjek, hubungan, objek."),
    "named graph": ("Named graph", "Satu kelompok triple yang diberi nama. Di sini satu pembaruan = satu named graph, "
                                   "sehingga setiap versi KB bisa disusun ulang."),
    "ontologi": ("Ontologi", "Daftar jenis benda di KB (aturan, parameter, pasal, pembaruan, ...) dan hubungan yang boleh "
                             "ada di antaranya. Memakai standar ELI (peraturan), OWL-Time (waktu), dan PROV-O (asal-usul)."),
    "SHACL": ("SHACL", "Standar W3C untuk memeriksa bentuk graf, misalnya 'setiap aturan harus punya sumber dan tanggal "
                       "berlaku'. Dipakai sebagai pemeriksaan G1."),
    "SPARQL": ("SPARQL", "Bahasa kueri untuk graf RDF, seperti SQL untuk tabel."),
    "bitemporal": ("Bitemporal", "Setiap unsur punya dua waktu: kapan berlaku menurut peraturan, dan kapan dicatat ke KB. "
                                 "Dengan begitu hitungan bisa diulang 'seperti yang diketahui pada tanggal itu'."),
    "dua lapis": ("Dua lapis", "Aturan negara dan aturan perusahaan disimpan terpisah di KB yang sama, lalu engine "
                               "memutuskan mana yang dipakai saat keduanya mengatur nilai yang sama."),
    "jejak": ("Jejak perhitungan", "Catatan engine untuk setiap nilai: aturan yang dipakai, nilai lain yang dibacanya, "
                                   "aturan yang kalah, dan pasal sumbernya."),
    "resolusi konflik": ("Penyelesaian konflik", "Urutan engine memilih satu aturan bila beberapa aturan berlaku untuk "
                                                 "nilai yang sama: lebih tinggi kedudukannya, lebih khusus, lalu lebih baru."),
    "pemeriksa statis": ("Pemeriksa statis", "Pemeriksaan KB tanpa menghitung kasus: aturan yang tidak pernah terpakai, "
                                             "selalu kalah, atau bertentangan antarlapis. Dipakai sebagai pemeriksaan G3."),
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


# Facts that have a glossary entry, so a line about the fact can carry the hover explanation. Decoration only: a fact
# that is not here (for instance one added by a new regulation) is shown with its label from the knowledge base.
FOR_FACT = {"gross_income": "bruto", "ter_rate": "TER", "ter_category": "kategori TER", "job_expense": "biaya jabatan",
            "annual_net": "neto", "ptkp_amount": "PTKP", "ptkp_status_effective": "status PTKP", "taxable_income": "PKP",
            "annual_pph21": "PPh setahun", "withheld_before_final": "sudah dipotong", "pph21_dtp": "DTP",
            "take_home_pay": "gaji bersih", "tax_allowance": "gross-up", "thr": "THR", "bonus": "bonus",
            "overtime_pay": "lembur", "fixed_allowance": "tunjangan tetap", "jkk_premium": "JKK", "jkm_premium": "JKM",
            "health_premium_employer": "BPJS Kesehatan", "jht_employee": "JHT", "jp_employee": "JP",
            "annual_pension_contributions": "iuran pensiun", "zakat_paid": "zakat"}

SLOT = re.compile(r"\{(pct|money|brackets|range|groups|values|since):([a-z_0-9]+)\}")
MISSING = "(belum ada di knowledge base pada tanggal ini)"


def at():
    """The date the explanations speak about: set by the page (tax month in the calculator, the date chosen in the
    viewer), today otherwise."""
    import data as d
    return st.session_state.get("g_date") or d.TODAY


def _short_money(x):
    import data as d
    x = int(x)
    for unit, name in ((1_000_000_000, "M"), (1_000_000, "jt")):
        if x >= unit:
            v = x / unit
            return f"Rp{v:g} {name}".replace(".", ",")
    return d.money(x)


def _slot(m, t):
    import data as d
    kind, name = m.group(1), m.group(2)
    if kind in ("pct", "money"):
        p = d.param_at(name, t)
        return MISSING if p is None else (d.pct(p.value) if kind == "pct" else d.money(p.value))
    if kind == "since":
        versions = [r for r in d.current() if r.kind == "table" and r.name == name and r.valid_from]
        if not versions:
            return MISSING
        first = min(versions, key=lambda r: r.valid_from)
        src = d.short_doc(first.source[0].document) if first.source else ""
        when = "berlaku" if first.valid_from <= t else "baru berlaku"
        return f"{when} sejak {d.tgl(first.valid_from)} ({src})"
    tab = d.table_at(name, t)
    if tab is None or not tab.rows:
        return MISSING
    rows = list(tab.rows)
    if kind == "brackets":
        parts = [f"{d.pct(r['rate'])} sampai {_short_money(r['upper'])}" for r in rows if r.get("upper")]
        parts += [f"{d.pct(r['rate'])} di atasnya" for r in rows if not r.get("upper")]
        return ", ".join(parts)
    if kind == "range":
        vals = sorted(r["value"] for r in rows)
        return f"{d.pct(vals[0])} sampai {d.pct(vals[-1])}"
    if kind == "groups":
        groups = {}
        for r in rows:
            groups.setdefault(r["value"], []).append(r["key"])
        return ". ".join(f"{v}: {', '.join(ks)}" for v, ks in sorted(groups.items()))
    return f"{rows[0]['key']} {_short_money(rows[0]['value'])} sampai {rows[-1]['key']} {_short_money(rows[-1]['value'])}"


def explain(key):
    """(label, explanation) with the numbers of the knowledge base in force at the date of the page."""
    label, expl = TERMS[key]
    if "{" not in expl:
        return label, expl
    import data as d
    t = at()
    return label, SLOT.sub(lambda m: _slot(m, t), expl) + f" (menurut knowledge base, berlaku {d.tgl(t)})"


def term(key, text=None):
    """HTML: the word with a hover explanation. Use inside st.markdown(..., unsafe_allow_html=True)."""
    label, expl = explain(key)
    shown = html.escape(text or key)
    return (f'<span class="term">{shown}<span class="q">?</span>'
            f'<span class="tip"><b>{html.escape(label)}</b>{html.escape(expl)}</span></span>')


def tip(key):
    """Plain text explanation for help= of a widget or metric."""
    label, expl = explain(key)
    return f"**{label}**: {expl}"


def md(text, **kw):
    """st.markdown with HTML enabled, for lines that carry term() markers."""
    st.markdown(text, unsafe_allow_html=True, **kw)


def dictionary():
    """Searchable list of every term (sidebar)."""
    q = st.text_input("Cari istilah", "", placeholder="mis. PTKP, TER, natura", key="gl_q")
    shown = [(k, v) for k, v in TERMS.items() if q.lower() in (k + v[0] + v[1]).lower()] if q else []
    for k, _ in shown[:8]:
        label, expl = explain(k)
        st.markdown(f"**{label}**  \n{expl}")
    if q and not shown:
        st.caption("Tidak ditemukan.")
