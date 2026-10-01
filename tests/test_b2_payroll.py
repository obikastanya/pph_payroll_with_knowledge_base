"""E12: kalkulator payroll tanpa KB (B2 + B1) harus identik dengan kalkulator dengan KB (engine + Perusahaan X).

Satu-satunya selisih yang diterima adalah titik tetap gross-up ganda (adjudikasi A-02) yang dilaporkan KB lewat
GROSSUP_GANDA. B2 harus independen dari engine/ dan KB, serta tunduk pada kontrak presisi.
"""
import ast
import itertools
from pathlib import Path

import pytest

from eksperimen.e12_tanpa_kb import cek_silang, kasus_uji
from eksperimen.e8_perusahaan_x import kasus_kar_a
from eksperimen.v1 import muat_kasus

ROOT = Path(__file__).resolve().parents[1]
B2 = ROOT / "baselines" / "b2_payroll_hardcoded"
KASUS = list(kasus_uji())


@pytest.mark.parametrize("nama,kasus", KASUS, ids=[n for n, _ in KASUS])
def test_data_hr_identik(nama, kasus):
    r = cek_silang(kasus)
    assert r["status"] == "identik", r["selisih"][:5]


@pytest.mark.parametrize("kasus", list(muat_kasus()), ids=lambda k: k["id"])
def test_contoh_resmi_komponen_jadi(kasus):
    r = cek_silang(kasus)
    assert r["status"] in ("identik", "sah_titik_tetap_ganda"), r["selisih"][:5]


VARIASI = list(itertools.product((2023, 2024, 2026), (3_000_000, 25_000_000), ("gross", "gross_up", "ditanggung_pemberi_kerja"),
                                 (None, 9), (1, 23)))


@pytest.mark.parametrize("tahun,gaji,metode,resign,hari_naik", VARIASI)
def test_variasi_isian_admin(tahun, gaji, metode, resign, hari_naik):
    if tahun == 2023 and metode == "gross_up":
        pytest.skip("gross-up rezim PER-16 di luar model (README)")
    k = kasus_kar_a(tahun)
    hr = k["data_hr"]
    hr.update(gaji_pokok=gaji, kenaikan_tanggal=f"{tahun}-03-{hari_naik:02d}", tunjangan_prorata_baru=0)
    k["metode"] = metode
    if resign:
        k["pegawai"]["bulan_terakhir_bekerja"] = resign
        k["masa"] = [m for m in k["masa"] if m["bulan"] <= resign]
        hr["per_masa"] = {b: v for b, v in hr["per_masa"].items() if int(b) <= resign}
    r = cek_silang(k)
    if metode == "gross":
        assert r["status"] == "identik", r["selisih"][:5]
    else:
        assert r["status"] in ("identik", "sah_titik_tetap_ganda"), r["selisih"][:5]


def test_b2_independen_dari_engine_dan_kb():
    for p in B2.rglob("*.py"):
        teks = p.read_text(encoding="utf-8")
        pohon = ast.parse(teks)
        for node in ast.walk(pohon):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith(("engine", "eksperimen", "ui")), f"{p.name}: {node.module}"
            if isinstance(node, ast.Import):
                assert not any(a.name.startswith(("engine", "eksperimen", "ui")) for a in node.names)
        assert ".yaml" not in teks, f"{p.name} tidak boleh membaca berkas KB"


def test_b2_tanpa_float_dan_round():
    for p in B2.rglob("*.py"):
        for node in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            assert not (isinstance(node, ast.Constant) and isinstance(node.value, float)), p.name
            assert not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("float", "round")), p.name


def test_rincian_pasal17_sama_dan_berjumlah_pph():
    for _, k in KASUS:
        r = cek_silang(k)
        kb = [x for x in r["kb"]["rincian_pasal17"] if x["bulan"] is None and x["fakta"] in ("pph21_setahun", "pph21_disetahunkan")]
        tk = r["tanpa_kb"]["rincian_pasal17"]
        assert kb and tk
        assert kb[0]["lapisan"] == tk["lapisan"]
        total = sum(l["pajak"] for l in tk["lapisan"])
        t = r["kb"]["tahunan"]
        assert total == t.get("pph21_disetahunkan", t["pph21_setahun"])
