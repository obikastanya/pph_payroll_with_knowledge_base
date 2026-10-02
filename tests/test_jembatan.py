"""Jembatan JSON untuk aplikasi web (web/, Laravel): protokol stdin/stdout dan kesetaraan dengan engine langsung.

Jembatan tidak boleh mengubah angka: keluarannya harus sama persis dengan engine.kalkulator.hitung.
"""
import json
import subprocess
import sys
from pathlib import Path

from eksperimen.e12_tanpa_kb import BERKAS_PX
from eksperimen.e8_perusahaan_x import kasus_kar_a
from engine.kalkulator import hitung
from jembatan.__main__ import contoh, jalankan

ROOT = Path(__file__).resolve().parents[1]


def _panggil(teks):
    p = subprocess.run([sys.executable, "-m", "jembatan"], input=teks.encode("utf-8"), capture_output=True, cwd=ROOT,
                       timeout=300)
    return p.returncode, json.loads(p.stdout.decode("ascii"))


def test_proses_stdin_stdout_sama_dengan_engine_langsung():
    kasus = kasus_kar_a(2023)
    kode, jawab = _panggil(json.dumps({"perintah": "hitung", "kasus": [kasus], "cek_silang": True}))
    assert kode == 0 and jawab["ok"]
    [r] = jawab["hasil"]
    assert r["ok"] and r["cek_silang"]["status"] == "identik"
    langsung = json.loads(json.dumps(hitung(kasus, berkas_perusahaan=BERKAS_PX), default=str))
    assert r["hasil"]["per_masa"] == langsung["per_masa"]
    assert r["hasil"]["tahunan"] == langsung["tahunan"]
    assert r["hasil"]["tahunan"]["pph21_setahun"] == 7_341_750


def test_galat_satu_kasus_tidak_menggagalkan_batch():
    jawab = jalankan({"perintah": "hitung", "kasus": [{"tahun_pajak": 2024}, kasus_kar_a(2024)]})
    gagal, berhasil = jawab["hasil"]
    assert not gagal["ok"] and gagal["jenis"] == "data_tidak_sesuai"
    assert berhasil["ok"] and "cek_silang" not in berhasil


def test_bom_utf8_diterima():
    kode, jawab = _panggil('﻿{"perintah": "info"}')
    assert kode == 0 and jawab["ok"]


def test_permintaan_tidak_valid():
    kode, jawab = _panggil("bukan json")
    assert kode == 2 and jawab == {"ok": False, "jenis": "permintaan_tidak_valid", "pesan": jawab["pesan"]}
    assert jalankan({"perintah": "hapus"})["jenis"] == "perintah_tidak_dikenal"


def test_contoh_dan_info():
    c = contoh()
    assert [x["id"] for x in c][:2] == ["KAR-A", "SINT-01"] and len(c) == 9
    assert all(x["kasus"].get("data_hr") for x in c)
    info = jalankan({"perintah": "info"})["audit"]
    assert {"versi_engine", "versi_kb", "hash_tabel"} <= set(info)
