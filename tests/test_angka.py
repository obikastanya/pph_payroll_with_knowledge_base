"""Kontrak aritmetika (research_plan.md §6.9.1) dan bukti mengapa float dilarang (ablasi A8)."""
import csv
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest

from engine.angka import PelanggaranPresisi, eksak, pastikan_rupiah, persen, rupiah, tarif
from engine.pembulatan import bulatkan

ROOT = Path(__file__).resolve().parents[1]


def test_tarif_eksak_dari_string():
    assert tarif("0.29") == Fraction(29, 100)
    assert tarif("0.29") * 3000 == 870
    assert persen("1.5") == Fraction(3, 200)


@pytest.mark.parametrize("buruk", [0.29, 1, "0,29", "1e-2", "", " ", None, "abc"])
def test_tarif_menolak_bukan_string_desimal(buruk):
    with pytest.raises(PelanggaranPresisi):
        tarif(buruk)


@pytest.mark.parametrize("buruk", [1.0, 10.5, True, False, "1.5", "1e3", None])
def test_rupiah_menolak_bukan_bulat(buruk):
    with pytest.raises(PelanggaranPresisi):
        rupiah(buruk)


def test_rupiah_menerima_int_dan_string_bulat():
    assert rupiah(5_400_000) == 5_400_000
    assert rupiah(" -1200 ") == -1200


def test_eksak_menolak_float_menerima_decimal():
    with pytest.raises(PelanggaranPresisi):
        eksak(0.1)
    assert eksak(Decimal("0.1")) == Fraction(1, 10)


@pytest.mark.parametrize("buruk", [1.0, Fraction(1, 2), True, "1"])
def test_pastikan_rupiah(buruk):
    with pytest.raises(PelanggaranPresisi):
        pastikan_rupiah(buruk)


def test_bukti_bahaya_float_pada_tarif_ter():
    """Dokumentasi temuan A8: float salah Rp1 pada pembulatan ke bawah; aritmetika eksak tidak.

    Grid: seluruh tarif TER x bruto Rp1.000 s.d. Rp1.999.000 (kelipatan Rp1.000).
    """
    with open(ROOT / "dataset/01_regulasi/tables/ter_bulanan.csv", encoding="utf-8") as f:
        tarif_teks = sorted({r["tarif_desimal"] for r in csv.DictReader(f)})
    selisih_float = 0
    for t in tarif_teks:
        tf, tq = float(t), tarif(t)
        for x in range(1_000, 2_000_000, 1_000):
            eksak_bawah = bulatkan(tq * x, "bawah")
            float_bawah = int(tf * x // 1)
            selisih_float += float_bawah != eksak_bawah
    assert selisih_float > 0, "float seharusnya menimbulkan selisih (temuan A8)"
    assert selisih_float == 700  # angka yang dilaporkan di research_plan.md §6.9.1
