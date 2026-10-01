"""Registri pembulatan (research_plan.md §6.9.2).

Oracle independen untuk mode pembulatan: modul ``decimal`` standar Python (implementasi terpisah
dari engine/pembulatan.py), dengan nilai uji berupa pecahan desimal agar konversi eksak.
"""
import glob
from decimal import (ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_EVEN, ROUND_HALF_UP,
                     Decimal, localcontext)
from fractions import Fraction
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.angka import PelanggaranPresisi
from engine.muat import KesalahanKB, muat_json_eksak, muat_registri_pembulatan
from engine.pembulatan import MODE, EntriPembulatan, RegistriPembulatan, bulatkan

ROOT = Path(__file__).resolve().parents[1]

# ROUND_HALF_UP pada decimal = setengah menjauhi nol (sama dengan Excel ROUND)
ORACLE_DECIMAL = {
    "bawah": ROUND_FLOOR, "atas": ROUND_CEILING, "menuju_nol": ROUND_DOWN,
    "setengah_menjauhi_nol": ROUND_HALF_UP, "setengah_genap": ROUND_HALF_EVEN,
}


def _oracle(nilai_sen, mode, satuan):
    """nilai_sen/100 dibulatkan ke kelipatan satuan, dihitung dengan decimal."""
    with localcontext() as ctx:
        ctx.prec = 60
        x = Decimal(nilai_sen) / Decimal(100) / Decimal(satuan)
        if mode == "setengah_atas":  # menuju +tak hingga untuk tepat setengah
            bawah = x.to_integral_value(rounding=ROUND_FLOOR)
            n = bawah + 1 if x - bawah >= Decimal("0.5") else bawah
        else:
            n = x.to_integral_value(rounding=ORACLE_DECIMAL[mode])
        return int(n) * satuan


TABEL_KASUS = [
    # (nilai, mode, satuan, harapan)
    (Fraction(25, 10), "bawah", 1, 2), (Fraction(25, 10), "atas", 1, 3),
    (Fraction(25, 10), "setengah_atas", 1, 3), (Fraction(25, 10), "setengah_menjauhi_nol", 1, 3),
    (Fraction(25, 10), "setengah_genap", 1, 2), (Fraction(35, 10), "setengah_genap", 1, 4),
    (Fraction(-25, 10), "bawah", 1, -3), (Fraction(-25, 10), "atas", 1, -2),
    (Fraction(-25, 10), "menuju_nol", 1, -2), (Fraction(-25, 10), "setengah_atas", 1, -2),
    (Fraction(-25, 10), "setengah_menjauhi_nol", 1, -3), (Fraction(-25, 10), "setengah_genap", 1, -2),
    (4_249_200, "bawah", 1000, 4_249_000), (4_249_999, "bawah", 1000, 4_249_000),
    (4_249_500, "setengah_menjauhi_nol", 1000, 4_250_000), (-1_500, "bawah", 1000, -2_000),
    (7, "bawah", 1, 7), (Fraction(13_777_062_39, 100), "bawah", 1, 13_777_062),
]


@pytest.mark.parametrize("nilai,mode,satuan,harapan", TABEL_KASUS)
def test_tabel_kasus(nilai, mode, satuan, harapan):
    assert bulatkan(nilai, mode, satuan) == harapan


@settings(max_examples=3000, deadline=None)
@given(sen=st.integers(-10**13, 10**13), mode=st.sampled_from(MODE), satuan=st.sampled_from([1, 1000]))
def test_sesuai_oracle_decimal(sen, mode, satuan):
    assert bulatkan(Fraction(sen, 100), mode, satuan) == _oracle(sen, mode, satuan)


@settings(max_examples=2000, deadline=None)
@given(n=st.integers(-10**12, 10**12), d=st.integers(1, 10**6), satuan=st.sampled_from([1, 1000]))
def test_sifat_umum(n, d, satuan):
    x = Fraction(n, d)
    b, a = bulatkan(x, "bawah", satuan), bulatkan(x, "atas", satuan)
    assert b <= x <= a and a - b in (0, satuan)
    for m in MODE:
        r = bulatkan(x, m, satuan)
        assert isinstance(r, int) and r % satuan == 0 and b <= r <= a


@pytest.mark.parametrize("buruk", [dict(nilai=0.5, mode="bawah"), dict(nilai=1, mode="bulat"),
                                   dict(nilai=1, mode="bawah", satuan=0), dict(nilai=1, mode="bawah", satuan=1.0)])
def test_bulatkan_menolak_input_buruk(buruk):
    with pytest.raises(PelanggaranPresisi):
        bulatkan(**buruk)


# --- registri ---------------------------------------------------------------------------------

TITIK_WAJIB_ADA = ["BULAT-PKP-01", "BULAT-TER-01", "BULAT-BRUTO-01", "BULAT-P17-01", "BULAT-PROPORSI-01",
                   "BULAT-BJ-01", "BULAT-BPJS-01", "BULAT-P16-01", "BULAT-GU-01"]


@pytest.fixture(scope="module")
def registri():
    return muat_registri_pembulatan()


def test_registri_memuat_seluruh_titik(registri):
    for id_ in TITIK_WAJIB_ADA:
        assert id_ in registri, id_


def test_hanya_pkp_yang_wajib(registri):
    wajib = {e.id for e in registri if e.status == "wajib"}
    assert wajib == {"BULAT-PKP-01"}
    assert registri.entri("BULAT-PKP-01").satuan == 1000 and registri.entri("BULAT-PKP-01").mode == "bawah"


def test_semua_varian(registri):
    v = registri.semua_varian("BULAT-TER-01", Fraction(1_377_706_239, 100))
    assert v == {"bawah": 13_777_062, "setengah_menjauhi_nol": 13_777_062}
    with pytest.raises(PelanggaranPresisi):
        registri.terapkan("BULAT-TER-01", 1, mode="atas")  # bukan default/alternatif
    with pytest.raises(PelanggaranPresisi):
        registri.terapkan("BULAT-TIDAK-ADA", 1)


def _entri(**ubah):
    dasar = dict(id="BULAT-X-01", titik="t", satuan=1, mode="bawah", urutan="u",
                 status="tafsir", dasar="d", alternatif=("setengah_genap",))
    dasar.update(ubah)
    return EntriPembulatan(**dasar)


@pytest.mark.parametrize("ubah", [
    dict(status="wajib"),                         # wajib dengan alternatif
    dict(alternatif=()),                          # tafsir tanpa alternatif
    dict(alternatif=("bawah",)),                  # default muncul di alternatif
    dict(mode="bulat"), dict(satuan=0), dict(dasar=" "),
])
def test_entri_tidak_valid_ditolak(ubah):
    with pytest.raises(PelanggaranPresisi):
        RegistriPembulatan([_entri(**ubah)])


def test_id_duplikat_ditolak():
    with pytest.raises(PelanggaranPresisi, match="duplikat"):
        RegistriPembulatan([_entri(), _entri()])


def test_skema_menolak_field_asing(tmp_path):
    p = tmp_path / "r.yaml"
    p.write_text('pembulatan:\n  - {id: BULAT-X-01, titik: t, satuan: 1, mode: bawah, urutan: u,'
                 ' status: wajib, dasar: d, toleransi: 1}\n', encoding="utf-8")
    with pytest.raises(KesalahanKB, match="toleransi"):
        muat_registri_pembulatan(p)


# --- bukti dari contoh resmi (V1) -------------------------------------------------------------

def _pasangan_pkp():
    for f in sorted(glob.glob(str(ROOT / "dataset/07_kasus_uji_resmi/*.json"))):
        d = muat_json_eksak(f)
        if not isinstance(d, dict):
            continue
        exp = d.get("expected") or {}
        for t in [exp.get("tahunan") or {}, *(exp.get("per_masa") or [])]:
            if "pkp_sebelum_pembulatan" in t and "pkp" in t:
                yield d["id"], t["pkp_sebelum_pembulatan"], t["pkp"]


def test_pkp_resmi_direproduksi(registri):
    pasangan = list(_pasangan_pkp())
    assert len(pasangan) >= 3
    for id_, sebelum, sesudah in pasangan:
        assert registri.terapkan("BULAT-PKP-01", sebelum) == sesudah, id_


def test_per16_tidak_konsisten_tidak_ada_mode_tunggal():
    """PER16-I.1.2: 1.515.450/12 -> 126.288; PER16-I.1.4: 1.237.050/12 -> 103.087.

    Tidak ada satu mode pun yang menghasilkan keduanya -> BULAT-P16-01 harus berstatus tafsir.
    """
    a, b = Fraction(1_515_450, 12), Fraction(1_237_050, 12)
    cocok = [m for m in MODE if bulatkan(a, m) == 126_288 and bulatkan(b, m) == 103_087]
    assert cocok == []
    assert muat_registri_pembulatan().entri("BULAT-P16-01").status == "tafsir"
