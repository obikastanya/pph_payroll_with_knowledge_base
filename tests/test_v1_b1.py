"""V1 untuk baseline B1: 0 selisih tak terjelaskan pada seluruh kasus resmi kanonik (§9.1, H2a)."""
from baselines.b1_hardcoded.pph21_b1 import fakta, hitung
from eksperimen.v1 import jalankan, ringkas


def test_b1_stj_nol_pada_kasus_resmi():
    hasil = jalankan(hitung, fakta)
    c, stj = ringkas(hasil)
    gagal = [r for r in hasil if r["status"] in ("SELISIH", "TIDAK_DIHASILKAN")]
    assert stj == 0, gagal[:10]
    assert c["cocok"] >= 1185 and c["cocok_terkoreksi"] == 20 and c["cocok_tafsir"] == 8


def test_erratum_terdeteksi_tepat_di_lokasinya():
    """Selisih terhadap angka TERCETAK harus muncul persis di harapan bertanda erratum."""
    hasil = jalankan(hitung, fakta)
    for r in hasil:
        if r["status"] == "cocok_terkoreksi":
            assert r["aktual"] != r["harapan"], r
