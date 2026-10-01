"""Pemeriksaan keluaran (MR11) dan metadata audit (research_plan.md §6.9.8)."""
import subprocess
from fractions import Fraction
from pathlib import Path

from . import VERSI_ENGINE
from .angka import PelanggaranPresisi
from .muat import ROOT, muat_yaml, sha256_berkas


def periksa_keluaran(obj, jalur="keluaran"):
    """MR11: tidak boleh ada float di mana pun, dan tidak ada Fraction di keluaran final.

    Nilai uang final harus sudah dibulatkan lewat registri pembulatan menjadi int.
    """
    if isinstance(obj, float):
        raise PelanggaranPresisi(f"float di {jalur}: {obj!r}")
    if isinstance(obj, Fraction):
        raise PelanggaranPresisi(f"nilai belum dibulatkan (Fraction) di {jalur}: {obj}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            periksa_keluaran(v, f"{jalur}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            periksa_keluaran(v, f"{jalur}[{i}]")
    return obj


def versi_kb():
    """Commit git saat ini (+ penanda bila ada perubahan belum di-commit)."""
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True, check=True).stdout.strip()
        kotor = subprocess.run(["git", "status", "--porcelain", "--", "kb", "engine"], cwd=ROOT,
                               capture_output=True, text=True, check=True).stdout.strip()
        return commit + ("+belum-dikomit" if kotor else "")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "belum-dikomit"


def metadata_audit(manifest_path=None, asumsi=()):
    manifest_path = Path(manifest_path or ROOT / "kb" / "regulasi" / "tabel_manifest.yaml")
    manifest = muat_yaml(manifest_path)
    return {
        "versi_engine": VERSI_ENGINE,
        "versi_kb": versi_kb(),
        "tanggal_kebaruan_kb": str(manifest["tanggal_kebaruan_kb"]),
        "hash_tabel": {e["nama"]: e["sha256"] for e in manifest["tabel"]},
        "status_verifikasi_tabel": {e["nama"]: e["status_verifikasi"] for e in manifest["tabel"]},
        "asumsi_dipakai": list(asumsi),
    }


def verifikasi_semua_tabel(manifest_path=None):
    """Kembalikan daftar (nama, cocok) untuk setiap tabel di manifest."""
    manifest_path = Path(manifest_path or ROOT / "kb" / "regulasi" / "tabel_manifest.yaml")
    manifest = muat_yaml(manifest_path)
    return [(e["nama"], sha256_berkas((manifest_path.parent / e["path"]).resolve()) == e["sha256"])
            for e in manifest["tabel"]]
