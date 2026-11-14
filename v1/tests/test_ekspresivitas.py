"""E7 — setiap kebijakan 'native' di katalog dieksekusi dan angkanya cocok dengan perhitungan tangan."""
from eksperimen.ekspresivitas import jalankan


def test_katalog_native_terverifikasi_dan_cakupan():
    t = jalankan()
    assert not [r for r in t if r["status"] == "GAGAL"]
    tanpa_kode = sum(r["status"] in ("native", "input") for r in t)
    assert tanpa_kode / len(t) >= 0.85
    assert {r["kebijakan"] for r in t if r["status"] == "tidak_bisa"} == {"KP-03", "KP-04"}
