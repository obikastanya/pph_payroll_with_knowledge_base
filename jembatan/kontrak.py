"""Kontrak data HR antara aplikasi web (web/, form data HR Perusahaan X) dan engine.

Kunci-kunci ini sudah punya isian khusus di form aplikasi web. Masukan lain yang diminta aturan KB lewat
hr('kunci') / hr_masa('kunci') ditampilkan aplikasi sebagai "masukan tambahan" secara otomatis.
"""
KUNCI_INTI_TAHUN = frozenset({
    "gaji_pokok", "kenaikan_tanggal", "kenaikan_nominal", "kenaikan_hk_sebelum", "kenaikan_hk_sesudah",
    "kenaikan_hari_sebelum", "kenaikan_hari_sesudah", "tunjangan_tetap_lama", "tunjangan_prorata_lama",
    "tunjangan_tetap_baru", "tunjangan_prorata_baru", "tanggal_masuk", "tanggal_masuk_awal_bulan",
    "tanggal_lebaran", "tanggal_thr_bayar", "bpjs_tk_mulai_bulan", "bpjs_kes_mulai_bulan", "kelas_jkk_persen",
})
KUNCI_INTI_BULAN = frozenset({"hk_penuh", "hk_aktual", "kompensasi_persen", "ota", "lembur", "komisi"})

# Tipe (sama dengan tipe `masukan` KB) dan cara membaca tiap kunci inti di ekspresi, sesuai
# web/modules/Payroll/Services/PenyusunKasus.php dan kb/perusahaan/perusahaan_x.yaml. Dipakai prompt asisten KB
# agar LLM membaca isian inti dengan konversi yang benar (mis. persen() vs desimal()).
TIPE_INTI = {
    "gaji_pokok": ("rupiah", "hr('gaji_pokok')", "gaji pokok sebulan (sebelum kenaikan)"),
    "kenaikan_tanggal": ("tanggal", "tanggal(hr('kenaikan_tanggal'))", "tanggal kenaikan gaji (selalu terisi)"),
    "kenaikan_nominal": ("rupiah", "hr('kenaikan_nominal')", "besar kenaikan gaji pokok (0 bila tidak naik)"),
    "kenaikan_hk_sebelum": ("bilangan", "hr('kenaikan_hk_sebelum')", "hari kerja aktual sebelum kenaikan di bulan kenaikan"),
    "kenaikan_hk_sesudah": ("bilangan", "hr('kenaikan_hk_sesudah')", "hari kerja aktual sesudah kenaikan di bulan kenaikan"),
    "kenaikan_hari_sebelum": ("bilangan", "hr('kenaikan_hari_sebelum')", "hari kerja total sebelum kenaikan"),
    "kenaikan_hari_sesudah": ("bilangan", "hr('kenaikan_hari_sesudah')", "hari kerja total sesudah kenaikan"),
    "tunjangan_tetap_lama": ("rupiah", "hr('tunjangan_tetap_lama')", "tunjangan tetap sebulan sebelum kenaikan"),
    "tunjangan_prorata_lama": ("rupiah", "hr('tunjangan_prorata_lama')", "tunjangan prorata hari kerja sebelum kenaikan"),
    "tunjangan_tetap_baru": ("rupiah", "hr('tunjangan_tetap_baru')", "tunjangan tetap sebulan sesudah kenaikan"),
    "tunjangan_prorata_baru": ("rupiah", "hr('tunjangan_prorata_baru')", "tunjangan prorata hari kerja sesudah kenaikan"),
    "tanggal_masuk": ("tanggal", "tanggal(hr('tanggal_masuk'))", "tanggal mulai bekerja"),
    "tanggal_masuk_awal_bulan": ("tanggal", "tanggal(hr('tanggal_masuk_awal_bulan'))", "tanggal 1 bulan mulai bekerja"),
    "tanggal_lebaran": ("tanggal", "tanggal(hr('tanggal_lebaran'))", "tanggal Idul Fitri tahun pajak"),
    "tanggal_thr_bayar": ("tanggal", "tanggal(hr('tanggal_thr_bayar'))", "tanggal THR dibayar"),
    "bpjs_tk_mulai_bulan": ("bilangan", "hr('bpjs_tk_mulai_bulan')", "nomor bulan (1-12) mulai terdaftar BPJS Ketenagakerjaan"),
    "bpjs_kes_mulai_bulan": ("bilangan", "hr('bpjs_kes_mulai_bulan')", "nomor bulan (1-12) mulai terdaftar BPJS Kesehatan"),
    "kelas_jkk_persen": ("persen", "persen(hr('kelas_jkk_persen'))", "tarif JKK sebagai angka persen, '0.24' = 0,24%"),
    "hk_penuh": ("bilangan", "hr_masa('hk_penuh')", "hari kerja penuh di bulan itu"),
    "hk_aktual": ("bilangan", "hr_masa('hk_aktual')", "hari kerja yang benar-benar dijalani di bulan itu"),
    "kompensasi_persen": ("desimal", "desimal(hr_masa('kompensasi_persen', '0'))",
                          "pecahan desimal, '0.1' = 10% gaji; hanya terisi di bulan pembayaran kompensasi"),
    "ota": ("rupiah", "hr_masa('ota', 0)", "insentif OTA; hanya terisi di bulan yang ada"),
    "lembur": ("rupiah", "hr_masa('lembur', 0)", "upah lembur; hanya terisi di bulan yang ada"),
    "komisi": ("rupiah", "hr_masa('komisi', 0)", "komisi; hanya terisi di bulan yang ada"),
}
