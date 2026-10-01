"""UI demo (ui/): tidak boleh mengubah angka mesin dan tidak boleh memuat aritmetika float.

1. Konversi kasus -> isian -> kasus mempertahankan input untuk semua data di dataset (contoh resmi + data HR), sehingga
   angka yang tampil pada isian default identik dengan hasil mesin atas berkas dataset.
2. Pemindai AST: kode UI tidak memanggil float()/round() dan tidak mengimpor math/statistics/numpy.
3. Smoke test Streamlit (AppTest): kedua kalkulator (dengan/tanpa KB) dan tab KB berjalan untuk setiap data pegawai;
   mengubah isian admin mengubah hasil; badge kebenaran hanya muncul untuk isian yang belum diubah.
"""
import ast
from pathlib import Path

import pytest

from engine.kalkulator import hitung
from ui import data as D

ROOT = Path(__file__).resolve().parents[1]
DAFTAR = D.daftar_data()
RESMI = [i for i, d in DAFTAR.items() if d["jenis"] == "komponen"]
HR = [i for i, d in DAFTAR.items() if d["jenis"] == "hr"]


def test_dataset_tersedia():
    assert len(RESMI) == 45
    assert "KAR-A" in HR and sum(1 for i in HR if i.startswith("SINT-")) == 8


@pytest.mark.parametrize("data_id", RESMI)
def test_tabel_isian_mempertahankan_input(data_id):
    k = D.muat_data(data_id)
    baris, bulan, khusus = D.kasus_ke_tabel(k)
    k2 = dict(k, masa=D.tabel_ke_masa(baris, bulan, khusus))
    assert D.normal(k2) == D.normal(k)
    a, b = hitung(k), hitung(k2)
    assert (a["per_masa"], a["tahunan"]) == (b["per_masa"], b["tahunan"])


def test_sintetis_bersumber_data_publik():
    import json
    for d in json.loads((ROOT / "dataset" / "08_pegawai_sintetis" / "pegawai_sintetis.json").read_text(encoding="utf-8")):
        s = d["sumber_gaji"]
        assert (ROOT / s["berkas"]).exists(), s
        assert d["kasus"]["data_hr"]["gaji_pokok"] >= int(s["nilai_sumber"].split(".")[0])
        assert d["sumber_tanggal_lebaran"]


def test_isian_pecahan_dan_negatif_ditolak():
    baris = [{"kode": "gaji", "kategori": "teratur", "satuan": "bulan", "Jan": 1.5}]
    with pytest.raises(D.IsianTidakValid):
        D.tabel_ke_masa(baris, [1])
    baris[0]["Jan"] = -1
    with pytest.raises(D.IsianTidakValid):
        D.tabel_ke_masa(baris, [1])
    baris[0]["Jan"] = 10_000_000.0
    n = D.tabel_ke_masa(baris, [1])[0]["komponen"][0]["nominal"]
    assert n == 10_000_000 and isinstance(n, int)


def test_format_eksak():
    assert D.persen("13/100") == "13%"
    assert D.persen("3/200") == "1,5%"
    assert D.rp(-1234567) == "-Rp1.234.567"
    assert D.persen_ke_desimal("10", "x") == "0.1"
    assert D.persen_ke_desimal("12,5", "x") == "0.125"
    assert D.desimal_ke_persen("0.1") == "10"
    assert D.rasio_persen(1, 3) == "≈ 33,33%"


def test_ui_tanpa_float_dan_round():
    temuan = []
    for p in sorted((ROOT / "ui").rglob("*.py")):
        for node in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("float", "round"):
                temuan.append(f"{p.name}:{node.lineno} {node.func.id}()")
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                temuan += [f"{p.name}:{node.lineno} import {m}" for m in mods if m.split(".")[0] in ("math", "statistics", "numpy")]
    assert temuan == []


# ---------------------------------------------------------------------------- smoke test Streamlit

@pytest.fixture(scope="module")
def app():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "ui" / "app.py"), default_timeout=300)
    at.run()
    return at


def _ok(at):
    assert [e.value for e in at.exception] == []
    assert [e.value for e in at.error] == []


def test_app_default_karyawan_a(app):
    _ok(app)
    m = [(x.label, x.value) for x in app.metric]
    assert m[0] == ("PPh 21 setahun", "Rp7.341.750")          # dengan KB
    assert ("PPh 21 setahun", "Rp7.341.750") in m[4:8]        # tanpa KB
    assert sum("identik sampai rupiah" in s.value for s in app.success) == 2


def test_ubah_gaji_mengubah_hasil_kedua_mesin(app):
    for mesin in ("kb", "tanpa_kb"):
        w = next(x for x in app.number_input if x.key and x.key.startswith(f"{mesin}:") and x.key.endswith(":gaji"))
        w.set_value(15_000_000).run()
        _ok(app)
    m = [(x.label, x.value) for x in app.metric]
    assert m[0][1] != "Rp7.341.750" and m[0] == m[4]          # berubah, dan kedua mesin tetap sama
    assert sum("identik sampai rupiah" in s.value for s in app.success) == 2
    for mesin in ("kb", "tanpa_kb"):
        app.button(key=f"{mesin}:reset").click().run()
    assert [(x.label, x.value) for x in app.metric][0] == ("PPh 21 setahun", "Rp7.341.750")


@pytest.mark.parametrize("mesin", ["kb", "tanpa_kb"])
def test_semua_data_hr(app, mesin):
    kd = f"{mesin}:data:{D.GRUP_HR}"
    for i in HR:
        app.selectbox(key=kd).set_value(i).run()
        _ok(app)


@pytest.mark.parametrize("mesin", ["kb", "tanpa_kb"])
def test_semua_contoh_resmi_cocok(app, mesin):
    app.segmented_control(key=f"{mesin}:grup").set_value(D.GRUP_RESMI).run()
    kd = f"{mesin}:data:{D.GRUP_RESMI}"
    for i in RESMI:
        app.selectbox(key=kd).set_value(i).run()
        _ok(app)
        teks = [s.value for s in app.success]
        assert any("cocok sampai rupiah" in t for t in teks), (mesin, i)
    app.segmented_control(key=f"{mesin}:grup").set_value(D.GRUP_HR).run()


def test_tab_kb_semua_tahun(app):
    for th in (2023, 2024, 2025, 2026):
        app.selectbox(key="kb:tahun").set_value(th).run()
        _ok(app)
    app.button(key="kb:verif").click().run()
    _ok(app)
    m = dict((x.label, x.value) for x in app.metric)
    assert m["Selisih tak terjelaskan"] == "0"
