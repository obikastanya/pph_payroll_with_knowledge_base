"""Integritas tabel (research_plan.md §9.6) dan pemuatan eksak."""
import shutil
from fractions import Fraction
from pathlib import Path

import pytest

from engine.audit import verifikasi_semua_tabel
from engine.muat import KesalahanKB, muat_json_eksak, muat_tabel, muat_yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "kb" / "regulasi" / "tabel_manifest.yaml"


def test_semua_hash_tabel_cocok():
    hasil = verifikasi_semua_tabel()
    assert hasil and all(cocok for _, cocok in hasil), hasil


def test_tabel_dimuat_dengan_tipe_eksak():
    ter = muat_tabel("ter_bulanan")
    assert len(ter) == 125
    for b in ter:
        assert isinstance(b["batas_bawah"], int)
        assert b["batas_atas"] is None or isinstance(b["batas_atas"], int)
        assert isinstance(b["tarif_desimal"], Fraction)
    p17 = muat_tabel("tarif_pasal17")
    assert {b["tarif_persen"] for b in p17 if b["rezim"] == "UU HPP"} == {
        Fraction(5, 100), Fraction(15, 100), Fraction(25, 100), Fraction(30, 100), Fraction(35, 100)}


def test_ptkp_nilai_regulasi():
    ptkp = {b["status"]: b["ptkp_setahun"] for b in muat_tabel("ptkp")}
    assert ptkp["TK/0"] == 54_000_000 and ptkp["K/3"] == 72_000_000
    assert ptkp["K/I/0"] == 112_500_000  # xlsx Perusahaan X keliru menulis 108.000.000 (temuan K-05)
    for status, nilai in ptkp.items():
        assert isinstance(nilai, int)


def _salin_kb(tmp_path):
    """Salin manifest + tabel ke tmp agar bisa diubah tanpa menyentuh data asli."""
    kb = tmp_path / "kb" / "regulasi"
    tabel = tmp_path / "dataset" / "01_regulasi" / "tables"
    kb.mkdir(parents=True)
    tabel.mkdir(parents=True)
    shutil.copy(MANIFEST, kb / "tabel_manifest.yaml")
    for f in (ROOT / "dataset/01_regulasi/tables").glob("*.csv"):
        shutil.copy(f, tabel / f.name)
    return kb / "tabel_manifest.yaml", tabel


def test_tabel_yang_diubah_ditolak(tmp_path):
    manifest, tabel = _salin_kb(tmp_path)
    muat_tabel("ter_bulanan", manifest)  # salinan utuh: lolos
    p = tabel / "ter_bulanan.csv"
    p.write_text(p.read_text(encoding="utf-8").replace("0.0025", "0.0026", 1), encoding="utf-8")
    with pytest.raises(KesalahanKB, match="hash"):
        muat_tabel("ter_bulanan", manifest)


def test_tabel_tidak_terdaftar_ditolak():
    with pytest.raises(KesalahanKB, match="tidak ada di manifest"):
        muat_tabel("tabel_rekaan")


def test_json_dibaca_eksak():
    d = muat_json_eksak(ROOT / "dataset/07_kasus_uji_resmi/PP58_Penj_Ps2_1.json")
    t = d["expected"]["per_masa"][0]["tarif_ter"]
    assert isinstance(t, Fraction) and t == Fraction(2, 100)


def test_manifest_mencatat_status_verifikasi():
    m = muat_yaml(MANIFEST)
    assert all(e["status_verifikasi"] in ("ekstraksi_1", "double_entry") for e in m["tabel"])
