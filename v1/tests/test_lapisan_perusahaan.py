"""Lapisan perusahaan tunduk pada kontrak presisi yang sama (research_plan.md §6.9)."""
from pathlib import Path

from engine.muat import muat_yaml, validasi_skema
from engine.pembulatan import RegistriPembulatan, bulatkan

ROOT = Path(__file__).resolve().parents[1]
KEBIJAKAN_X = ROOT / "dataset/02_studi_kasus/kebijakan_perusahaan_x.yaml"


def test_kebijakan_x_bebas_float_dan_registri_valid():
    data = muat_yaml(KEBIJAKAN_X)  # gagal bila ada float literal / kunci duplikat
    validasi_skema({"pembulatan": data["pembulatan"]}, "registri_pembulatan.schema.json")
    reg = RegistriPembulatan.dari_data(data["pembulatan"])
    e = reg.entri("PX-BULAT-PRO")
    assert e.status == "kebijakan"


def test_mode_excel_round_untuk_negatif():
    """Excel ROUND(-2.5) = -3 (menjauhi nol); setengah_atas akan memberi -2 -> nama mode penting."""
    from fractions import Fraction
    assert bulatkan(Fraction(-5, 2), "setengah_menjauhi_nol") == -3
    assert bulatkan(Fraction(-5, 2), "setengah_atas") == -2
