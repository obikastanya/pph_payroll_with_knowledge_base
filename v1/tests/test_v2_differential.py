"""V2: setiap selisih KB vs B1 pada data sintetis harus termasuk kelas teradjudikasi (eksperimen/adjudikasi.md)."""
import pytest

from eksperimen.v2 import jalankan, konverter
from engine.kalkulator import hitung


@pytest.fixture(scope="module")
def v2():
    kasus = {k["id"]: k for k in konverter().muat()}
    n, selisih, galat = jalankan(kasus.values())
    return kasus, n, selisih, galat


def test_tidak_ada_galat_sistem(v2):
    _, n, _, galat = v2
    assert n > 2000 and galat == []


def test_semua_selisih_adalah_gross_up_ganda_tahunan(v2):
    """A-02: kasus berselisih hanya kasus gross-up dengan solusi ganda di masa terakhir, dan nilai B1
    adalah salah satu titik tetap yang dilaporkan KB."""
    kasus, _, selisih, _ = v2
    from baselines.b1_hardcoded import pph21_b1
    for kid in {s["kasus"] for s in selisih}:
        k = kasus[kid]
        assert k["metode"] == "gross_up", kid
        h = hitung(k)
        ganda = [p for p in h["peringatan"] if p["kode"] == "GROSSUP_GANDA" and p["fakta"] == "tunjangan_pajak_akhir"]
        assert ganda, kid
        akhir = max(h["per_masa"])
        tb = pph21_b1.hitung(k)["per_masa"][akhir]["tunjangan_pajak"]
        assert tb in (ganda[0]["terkecil"], ganda[0]["terbesar"]), (kid, tb, ganda[0])
