"""Double-entry permanen (research_plan.md §9.6): tabel KB == ekstraksi kedua dari GAMBAR halaman PDF.

Menutup celah yang ditemukan mutation testing E4: kesalahan nilai di lapisan/batas yang tidak tersentuh
contoh resmi. Juga memeriksa parameter KB (parameter.yaml) konsisten dengan tabel terverifikasi.
"""
import csv
from fractions import Fraction
from pathlib import Path

import pytest

from engine.kb import DIR_REGULASI, _muat_parameter

ROOT = Path(__file__).resolve().parents[1]
E1 = ROOT / "dataset" / "01_regulasi" / "tables"
E2 = ROOT / "dataset" / "01_regulasi" / "tables_ekstraksi2"


def _baca(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def _f(v):
    return Fraction(v) if v not in ("", None) else None


def bandingkan_ter(dir_kb=E1):
    a = {(r["kategori"], int(r["urutan"])): r for r in _baca(dir_kb / "ter_bulanan.csv")}
    b = {(r["kategori"], int(r["urutan"])): r for r in _baca(E2 / "ter_bulanan.csv")}
    beda = [k for k in a.keys() | b.keys()
            if k not in a or k not in b or any(_f(a[k][c]) != _f(b[k][c]) for c in ("batas_bawah", "batas_atas", "tarif_desimal"))]
    return sorted(beda)


def bandingkan_pasal17(dir_kb=E1):
    a = [r for r in _baca(dir_kb / "tarif_pasal17.csv") if r["rezim"] == "UU HPP"]
    b = _baca(E2 / "tarif_pasal17.csv")
    pa = {int(r["lapisan"]): (_f(r["pkp_batas_bawah"]), _f(r["pkp_batas_atas"]), _f(r["tarif_persen"])) for r in a}
    pb = {int(r["lapisan"]): (_f(r["pkp_batas_bawah"]), _f(r["pkp_batas_atas"]), _f(r["tarif_persen"])) for r in b}
    return sorted(k for k in pa.keys() | pb.keys() if pa.get(k) != pb.get(k))


def bandingkan_ptkp(dir_kb=E1):
    a = {r["status"]: (int(r["ptkp_setahun"]), r["kategori_ter"]) for r in _baca(dir_kb / "ptkp.csv")}
    b = {r["status"]: int(r["ptkp_setahun"]) for r in _baca(E2 / "ptkp.csv")}
    kat = {r["status_ptkp"]: r["kategori"] for r in _baca(E2 / "kategori_ter.csv")}
    beda = [s for s in b if a.get(s, (None,))[0] != b[s]]
    beda += [s for s in kat if a.get(s, (None, None))[1] != kat[s]]
    return sorted(set(beda))


def test_ter_bulanan_sama_dengan_ekstraksi_kedua():
    assert bandingkan_ter() == []


def test_pasal17_sama_dengan_ekstraksi_kedua():
    assert bandingkan_pasal17() == []


def test_ptkp_dan_kategori_sama_dengan_ekstraksi_kedua():
    assert bandingkan_ptkp() == []


def parameter_konsisten(dir_reg=DIR_REGULASI):
    """Parameter skalar KB vs tabel terverifikasi (bpjs.csv, biaya_jabatan.csv)."""
    p = _muat_parameter(Path(dir_reg) / "parameter.yaml")
    nilai = lambda n: {v for _, _, v, _ in p[n]}
    bpjs = _baca(E2 / "bpjs.csv")
    salah = []
    harap = {
        "jkm_pk_persen": {_f(r["tarif_pemberi_kerja_persen"]) for r in bpjs if r["program"].endswith("JKM")},
        "jht_pk_persen": {_f(r["tarif_pemberi_kerja_persen"]) for r in bpjs if r["program"].endswith("JHT")},
        "jht_pg_persen": {_f(r["tarif_pekerja_persen"]) for r in bpjs if r["program"].endswith("JHT")},
        "jp_pk_persen": {_f(r["tarif_pemberi_kerja_persen"]) for r in bpjs if r["program"] == "JP"},
        "jp_pg_persen": {_f(r["tarif_pekerja_persen"]) for r in bpjs if r["program"] == "JP"},
        "jp_batas_upah": {int(r["batas_upah_bulanan"]) for r in bpjs if r["program"] == "JP"
                          and r["batas_upah_bulanan"] and (r["berlaku_mulai"] or "9999") >= "2022"},
        "kes_pk_persen": {_f(r["tarif_pemberi_kerja_persen"]) for r in bpjs if r["program"] == "JKN"},
        "kes_pg_persen": {_f(r["tarif_pekerja_persen"]) for r in bpjs if r["program"] == "JKN"},
        "kes_batas_upah": {int(r["batas_upah_bulanan"]) for r in bpjs if r["program"] == "JKN"
                           and r["batas_upah_bulanan"] and (r["berlaku_mulai"] or "") >= "2020"},
    }
    for nama, h in harap.items():
        if not nilai(nama) <= h:
            salah.append((nama, sorted(nilai(nama)), sorted(h)))
    bj = [r for r in _baca(E2 / "biaya_jabatan.csv") if r["komponen"] == "biaya_jabatan"]
    if nilai("bj_persen") != {_f(bj[0]["persen"])} or nilai("bj_maks_bulan") != {int(bj[0]["maks_bulanan"])} \
            or nilai("bj_maks_tahun") != {int(bj[0]["maks_tahunan"])}:
        salah.append(("biaya_jabatan", "parameter.yaml tidak cocok dengan biaya_jabatan.csv"))
    return salah


def test_parameter_konsisten_dengan_tabel_terverifikasi():
    assert parameter_konsisten() == []
