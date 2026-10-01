"""AR-3 (research_plan.md §6.9.1): float dan round() bawaan dilarang di engine dan baseline B1.

Tes statis (AST) atas kode, dan tes muat atas seluruh berkas YAML di kb/.
"""
import ast
from pathlib import Path

import pytest

from engine.angka import PelanggaranPresisi
from engine.muat import KesalahanKB, muat_yaml

ROOT = Path(__file__).resolve().parents[1]
DIREKTORI_KODE = [ROOT / "engine", ROOT / "baselines" / "b1_hardcoded"]
NAMA_TERLARANG = {"float", "round"}
MODUL_TERLARANG = {"math", "statistics", "numpy"}


def _berkas_kode():
    for d in DIREKTORI_KODE:
        if d.exists():
            yield from sorted(d.rglob("*.py"))


def _pelanggaran(path):
    pohon = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    temuan = []
    for node in ast.walk(pohon):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            temuan.append(f"{path.name}:{node.lineno} float literal {node.value!r}")
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id in NAMA_TERLARANG):
            # pemanggilan float()/round() dilarang; isinstance(x, float) untuk MENOLAK float tetap boleh
            temuan.append(f"{path.name}:{node.lineno} memanggil {node.func.id}()")
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in MODUL_TERLARANG:
                    temuan.append(f"{path.name}:{node.lineno} import {a.name}")
        elif isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in MODUL_TERLARANG:
            temuan.append(f"{path.name}:{node.lineno} from {node.module} import ...")
    return temuan


def test_ada_kode_yang_diperiksa():
    assert list(_berkas_kode()), "tidak ada berkas engine yang ditemukan"


@pytest.mark.parametrize("path", list(_berkas_kode()), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_kode_bebas_float_dan_round(path):
    assert _pelanggaran(path) == []


def test_pemindai_menangkap_pelanggaran(tmp_path):
    contoh = tmp_path / "buruk.py"
    contoh.write_text("import math\nx = 0.29 * 3000\ny = round(x)\nz = float('1')\n", encoding="utf-8")
    temuan = _pelanggaran(contoh)
    assert len(temuan) == 4  # import math, literal 0.29, round(), float()


@pytest.mark.parametrize("path", sorted((ROOT / "kb").rglob("*.yaml")), ids=lambda p: p.name)
def test_semua_yaml_kb_bebas_float(path):
    muat_yaml(path)  # LoaderKetat melempar PelanggaranPresisi bila ada float literal


def test_yaml_float_ditolak(tmp_path):
    p = tmp_path / "x.yaml"
    p.write_text("tarif: 0.29\n", encoding="utf-8")
    with pytest.raises(PelanggaranPresisi, match="float literal"):
        muat_yaml(p)


@pytest.mark.parametrize("teks", ["tarif: 1.0e+3\n", "tarif: .inf\n", "tarif: -0.5\n", "a: [1, 2.0]\n"])
def test_yaml_berbagai_bentuk_float_ditolak(tmp_path, teks):
    p = tmp_path / "x.yaml"
    p.write_text(teks, encoding="utf-8")
    with pytest.raises(PelanggaranPresisi):
        muat_yaml(p)


@pytest.mark.parametrize("teks", ["1e3", "1.0e3"])
def test_yaml_notasi_ilmiah_tanpa_tanda_menjadi_string_lalu_ditolak_tarif(tmp_path, teks):
    """PyYAML (YAML 1.1) mewajibkan tanda pada eksponen: `1e3`/`1.0e3` dibaca sebagai STRING.

    Lapisan berikutnya (tarif()) menolaknya, jadi kedua jalur tetap tertutup.
    """
    from engine.angka import tarif
    p = tmp_path / "x.yaml"
    p.write_text(f"tarif: {teks}\n", encoding="utf-8")
    nilai = muat_yaml(p)["tarif"]
    assert nilai == teks
    with pytest.raises(PelanggaranPresisi):
        tarif(nilai)


def test_yaml_string_desimal_diterima(tmp_path):
    p = tmp_path / "x.yaml"
    p.write_text('tarif: "0.29"\nbatas: 5400000\n', encoding="utf-8")
    assert muat_yaml(p) == {"tarif": "0.29", "batas": 5400000}


def test_yaml_kunci_duplikat_ditolak(tmp_path):
    p = tmp_path / "x.yaml"
    p.write_text("mode: bawah\nmode: atas\n", encoding="utf-8")
    with pytest.raises(KesalahanKB, match="duplikat"):
        muat_yaml(p)
