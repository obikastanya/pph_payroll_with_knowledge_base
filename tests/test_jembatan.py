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
    # JSON sah tetapi bukan objek: tetap dijawab JSON, bukan traceback
    kode, jawab = _panggil("[1, 2]")
    assert kode == 2 and jawab == {"ok": False, "jenis": "permintaan_tidak_valid", "pesan": "permintaan harus objek JSON"}
    for permintaan in ('"hitung"', "null", "3"):
        assert jalankan(json.loads(permintaan))["jenis"] == "permintaan_tidak_valid", permintaan
    assert jalankan({"perintah": "hitung", "kasus": {"a": 1}}) == {"ok": False, "jenis": "permintaan_tidak_valid",
                                                                   "pesan": "kasus harus daftar"}


def test_kasus_bukan_objek_hanya_menggagalkan_kasus_itu():
    gagal, berhasil = jalankan({"perintah": "hitung", "kasus": ["teks", kasus_kar_a(2024)]})["hasil"]
    assert gagal == {"ok": False, "jenis": "data_tidak_sesuai",
                     "pesan": "Data belum lengkap atau tidak sesuai format: kasus harus objek JSON"}
    assert berhasil["ok"]


def test_contoh_dan_info():
    c = contoh()
    assert [x["id"] for x in c][:2] == ["KAR-A", "SINT-01"] and len(c) == 9
    assert all(x["kasus"].get("data_hr") for x in c)
    info = jalankan({"perintah": "info"})["audit"]
    assert {"versi_engine", "versi_kb", "hash_tabel"} <= set(info)


TRANSPORT = """
lapisan: perusahaan
id: transport
komponen:
  - {fakta: px_transport, jenis: tunjangan_transport, kategori: teratur, label: Uang transport}
masukan:
  - {kunci: uang_transport_per_hari, label: Uang transport per hari, tipe: rupiah, lingkup: tahun, wajib: true}
aturan:
  - id: PJT-TRANSPORT-01
    sifat: opsional
    berlaku: {mulai: 2016-01-01}
    lingkup: masa
    menghasilkan: px_transport
    maka: "hr('uang_transport_per_hari') * hr_masa('hk_aktual')"
    tipe_hasil: rupiah
    sumber: uji
"""
GANDA = """
lapisan: perusahaan
id: ganda
aturan:
  - id: PJG-GANDA-01
    sifat: opsional
    berlaku: {mulai: 2016-01-01}
    lingkup: masa
    menghasilkan: px_transport_ganda
    maka: "atau('px_transport', 0) * 2"
    tipe_hasil: rupiah
    sumber: uji
"""


def _berkas_kb(tmp_path, monkeypatch, **isi):
    import jembatan.__main__ as J
    monkeypatch.setattr(J, "DIR_TAMBAHAN", tmp_path.resolve())
    hasil = {}
    for nama, teks in isi.items():
        p = tmp_path / f"{nama}.yaml"
        p.write_text(teks, encoding="utf-8")
        hasil[nama] = str(p)
    return hasil


def test_periksa_kb_dasar():
    kode, jawab = _panggil(json.dumps({"perintah": "periksa"}))
    assert kode == 0 and jawab == {"ok": True, "periksa": {"ok": True, "galat": [], "tahun": [2023, 2024, 2025, 2026, 2027]}}


def test_periksa_mendeteksi_fakta_yang_hilang_setelah_berkas_dinonaktifkan(tmp_path, monkeypatch):
    b = _berkas_kb(tmp_path, monkeypatch, transport=TRANSPORT, ganda=GANDA, rusak="lapisan: [")
    # masukan wajib tanpa bawaan (uang_transport_per_hari) diberi nilai contoh, sehingga KB lengkap lolos
    assert jalankan({"perintah": "periksa", "berkas_tambahan": [b["transport"], b["ganda"]]})["periksa"]["ok"]
    # memuat saja lolos; fakta px_transport yang hilang baru ketahuan saat menghitung
    p = jalankan({"perintah": "periksa", "berkas_tambahan": [b["ganda"]]})["periksa"]
    assert not p["ok"] and len(p["galat"]) == 5
    assert p["galat"][0].startswith("Karyawan A 2023 tidak dapat dihitung: KesalahanKB: PJG-GANDA-01: fakta 'px_transport'")
    p = jalankan({"perintah": "periksa", "berkas_tambahan": [b["rusak"]]})["periksa"]
    assert not p["ok"] and p["galat"][0].startswith("KB tidak dapat dimuat: ")
    assert jalankan({"perintah": "periksa", "berkas_tambahan": ["kb/tidak_ada.yaml"]})["jenis"] == "permintaan_tidak_valid"


def test_masukan_wajib_efektif_lewat_jembatan(tmp_path, monkeypatch):
    longgar = TRANSPORT.replace("wajib: true", "wajib: false")   # wajib: false tanpa bawaan tetap wajib bagi engine
    b = _berkas_kb(tmp_path, monkeypatch, transport=longgar)
    [m] = jalankan({"perintah": "masukan", "berkas_tambahan": [b["transport"]]})["masukan"]
    assert m["kunci"] == "uang_transport_per_hari" and m["wajib"] is True
