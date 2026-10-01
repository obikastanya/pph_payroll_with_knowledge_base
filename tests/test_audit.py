"""MR11 (keluaran tanpa float/pecahan) dan metadata audit (research_plan.md §6.9.8)."""
from fractions import Fraction

import pytest

from engine import VERSI_ENGINE
from engine.angka import PelanggaranPresisi
from engine.audit import metadata_audit, periksa_keluaran
from engine.muat import muat_tabel


@pytest.mark.parametrize("buruk", [
    {"pph21": 156810.0}, {"rincian": {"bruto": Fraction(1, 2)}}, {"masa": [1, 2, 3.5]},
])
def test_mr11_menolak_float_dan_pecahan(buruk):
    with pytest.raises(PelanggaranPresisi):
        periksa_keluaran(buruk)


def test_mr11_menerima_keluaran_bersih():
    periksa_keluaran({"pph21": 156_810, "kategori": "B", "masa": [{"bulan": 1, "pph21": 0}], "dtp": None})


@pytest.mark.parametrize("nama", ["ter_bulanan", "ter_harian", "tarif_pasal17", "ptkp", "biaya_jabatan", "bpjs"])
def test_tabel_dimuat_tanpa_float(nama):
    for baris in muat_tabel(nama):
        for k, v in baris.items():
            assert not isinstance(v, float), (nama, k, v)


def test_metadata_audit_lengkap():
    m = metadata_audit(asumsi=["BULAT-TER-01=bawah"])
    assert m["versi_engine"] == VERSI_ENGINE
    assert m["versi_kb"]
    assert len(m["hash_tabel"]) == 8 and all(len(h) == 64 for h in m["hash_tabel"].values())
    assert set(m["status_verifikasi_tabel"].values()) <= {"ekstraksi_1", "double_entry"}
    assert m["asumsi_dipakai"] == ["BULAT-TER-01=bawah"]
    periksa_keluaran(m)
