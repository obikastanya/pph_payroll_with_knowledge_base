"""Teks peringatan engine di panel hasil UI demo (ui/hasil.py): setiap bentuk peringatan tampil tanpa galat.

KONFLIK_WAJIB punya dua bentuk (tingkat klasifikasi dan tingkat aturan); bentuk tingkat aturan dulu melempar KeyError
dan menggagalkan seluruh panel hasil.
"""
from ui.hasil import teks_peringatan


def test_konflik_wajib_tingkat_klasifikasi():
    teks, jenis = teks_peringatan({"kode": "KONFLIK_WAJIB", "fakta": "px_lembur", "jenis": "lembur",
                                   "kategori_perusahaan": "tidak_teratur", "kategori_wajib": "teratur", "sumber": "PMK 168/2023"})
    assert jenis == "konflik"
    assert "`px_lembur` (lembur)" in teks and "*tidak teratur*" in teks and "*teratur* (PMK 168/2023)" in teks


def test_konflik_wajib_tingkat_aturan():
    teks, jenis = teks_peringatan({"kode": "KONFLIK_WAJIB", "fakta": "px_transport", "ditolak": ["PX-TRANSPORT-01"],
                                   "pemenang": ["REG-TRANSPORT-01", "REG-TRANSPORT-02"]})
    assert jenis == "konflik"
    assert "aturan PX-TRANSPORT-01 untuk px_transport tidak dipakai" in teks
    assert "aturan wajib REG-TRANSPORT-01, REG-TRANSPORT-02 berlaku" in teks
    # kunci opsional yang hilang tidak menggagalkan panel
    teks, jenis = teks_peringatan({"kode": "KONFLIK_WAJIB"})
    assert jenis == "konflik" and "aturan ? untuk ? tidak dipakai" in teks


def test_grossup_ganda():
    teks, jenis = teks_peringatan({"kode": "GROSSUP_GANDA", "bulan": 12, "terkecil": 1_000, "terbesar": 1_001,
                                   "dipilih": "terbesar"})
    assert jenis == "grossup" and "(Des)" in teks and teks.endswith("dipakai yang terbesar.")
    teks, _ = teks_peringatan({"kode": "GROSSUP_GANDA"})
    assert "(Masa)" in teks and "atau -" in teks and teks.endswith("dipakai yang terkecil.")


def test_klasifikasi_tidak_diatur_diringkas_terpisah_dan_kode_lain_ditampilkan_apa_adanya():
    assert teks_peringatan({"kode": "KLASIFIKASI_TIDAK_DIATUR", "fakta": "px_x"}) is None
    teks, jenis = teks_peringatan({"kode": "LAIN", "x": 1})
    assert jenis == "info" and teks.startswith("**LAIN**: ")
