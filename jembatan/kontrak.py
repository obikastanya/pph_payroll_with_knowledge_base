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
