"""Pemuat KB yang menegakkan kontrak presisi (research_plan.md §6.9.1 AR-2, §9.6).

- YAML: float literal DITOLAK (PyYAML default membaca ``0.29`` sebagai float) dan kunci
  duplikat DITOLAK (PyYAML default diam-diam menimpa nilai pertama).
- CSV tabel parameter: integritas dicek dengan SHA-256 terhadap manifest; kolom rupiah -> int,
  kolom tarif -> Fraction dari string.
- JSON (kasus uji resmi): angka pecahan dibaca sebagai Fraction lewat string, bukan float.
"""
import csv
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import yaml

from .angka import PelanggaranPresisi, persen, rupiah, tarif

ROOT = Path(__file__).resolve().parents[1]


class KesalahanKB(ValueError):
    """Berkas KB tidak valid (format, integritas, atau struktur)."""


class LoaderKetat(yaml.SafeLoader):
    """SafeLoader yang menolak float dan kunci duplikat."""


def _tolak_float(loader, node):
    raise PelanggaranPresisi(
        f"float literal di YAML ({node.value!r}, baris {node.start_mark.line + 1}); "
        f"tulis sebagai string, mis. \"{node.value}\"")


def _mapping_tanpa_duplikat(loader, node, deep=False):
    loader.flatten_mapping(node)
    hasil = {}
    for k_node, v_node in node.value:
        k = loader.construct_object(k_node, deep=deep)
        if k in hasil:
            raise KesalahanKB(f"kunci duplikat {k!r} di baris {k_node.start_mark.line + 1}")
        hasil[k] = loader.construct_object(v_node, deep=deep)
    return hasil


LoaderKetat.add_constructor("tag:yaml.org,2002:float", _tolak_float)
LoaderKetat.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping_tanpa_duplikat)


def muat_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, Loader=LoaderKetat)


def muat_json_eksak(path):
    """JSON dengan angka pecahan sebagai Fraction (lewat string desimal), bukan float."""
    with open(path, encoding="utf-8") as f:
        return json.load(f, parse_float=lambda s: Fraction(s))


def sha256_berkas(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 16), b""):
            h.update(blok)
    return h.hexdigest()


def _konversi(baris, kolom_rupiah, kolom_tarif, kolom_persen, boleh_kosong):
    out = dict(baris)
    for kolom, fungsi in ((kolom_rupiah, rupiah), (kolom_tarif, tarif), (kolom_persen, persen)):
        for k in kolom:
            v = (baris.get(k) or "").strip()
            if v == "":
                if k not in boleh_kosong:
                    raise KesalahanKB(f"kolom {k!r} kosong padahal wajib")
                out[k] = None
            else:
                out[k] = fungsi(v)
    return out


def muat_tabel(nama, manifest_path=None):
    """Muat tabel parameter sesuai entri manifest; tolak bila hash tidak cocok."""
    manifest_path = Path(manifest_path or ROOT / "kb" / "regulasi" / "tabel_manifest.yaml")
    manifest = muat_yaml(manifest_path)
    entri = {e["nama"]: e for e in manifest["tabel"]}
    if nama not in entri:
        raise KesalahanKB(f"tabel {nama!r} tidak ada di manifest")
    e = entri[nama]
    path = (manifest_path.parent / e["path"]).resolve()
    aktual = sha256_berkas(path)
    if aktual != e["sha256"]:
        raise KesalahanKB(
            f"hash tabel {nama!r} tidak cocok (manifest {e['sha256'][:12]}…, aktual {aktual[:12]}…). "
            f"Tabel berubah tanpa pencatatan versi.")
    with open(path, encoding="utf-8", newline="") as f:
        baris = list(csv.DictReader(f))
    return [
        _konversi(b, e.get("kolom_rupiah", []), e.get("kolom_tarif", []),
                  e.get("kolom_persen", []), set(e.get("boleh_kosong", [])))
        for b in baris
    ]


def validasi_skema(data, nama_skema):
    import jsonschema
    skema = json.loads((ROOT / "kb" / "skema" / nama_skema).read_text(encoding="utf-8"))
    try:
        jsonschema.validate(data, skema)
    except jsonschema.ValidationError as e:
        jalur = "/".join(str(p) for p in e.absolute_path)
        raise KesalahanKB(f"{nama_skema}: {e.message} (di {jalur or 'akar'})") from None


def muat_registri_pembulatan(path=None):
    from .pembulatan import RegistriPembulatan
    data = muat_yaml(path or ROOT / "kb" / "regulasi" / "pembulatan.yaml")
    validasi_skema(data, "registri_pembulatan.schema.json")
    return RegistriPembulatan.dari_data(data["pembulatan"])
