"""Protokol jembatan: satu permintaan JSON di stdin, satu jawaban JSON di stdout.

    env\\Scripts\\python.exe -m jembatan < permintaan.json

Permintaan:
    {"perintah": "hitung", "kasus": [<kasus kanonik>, ...], "cek_silang": true}
    {"perintah": "contoh"}     data pegawai contoh dari dataset (Karyawan A + pegawai sintetis)
    {"perintah": "info"}       versi engine, versi KB, hash tabel

Jawaban selalu {"ok": true, ...} atau {"ok": false, "jenis": ..., "pesan": ...}. Untuk "hitung", setiap kasus
dijawab sendiri-sendiri, sehingga satu kasus yang galat tidak menggagalkan kasus lain dalam satu batch.
Keluaran ASCII murni (ensure_ascii) agar tidak bergantung pada code page konsol Windows.
"""
import json
import sys

from baselines.b1_hardcoded import pph21_b1 as B1
from baselines.b2_payroll_hardcoded.payroll_b2 import hitung as hitung_tanpa_kb
from eksperimen.e12_tanpa_kb import BERKAS_PX, SINTETIS, selisih, teradjudikasi
from engine.audit import metadata_audit
from engine.inferensi import Ambigu, KasusTidakDidukung
from engine.kalkulator import hitung as hitung_kb
from engine.muat import KesalahanKB
from engine.waktu import InputTidakValid

GALAT = (
    (InputTidakValid, "input_tidak_valid", "Isian tidak valid"),
    ((KasusTidakDidukung, B1.KasusTidakDidukung), "di_luar_cakupan", "Kasus di luar cakupan kalkulator"),
    (Ambigu, "ambigu", "Aturan ambigu"),
    (KesalahanKB, "kesalahan_kb", "Data belum lengkap atau tidak sesuai"),
    ((KeyError, TypeError, ValueError), "data_tidak_sesuai", "Data belum lengkap atau tidak sesuai format"),
)


def _cek_silang(kasus, h_kb):
    """E12 untuk satu kasus: bandingkan dengan kalkulator tanpa KB (B2 + B1)."""
    try:
        h_tanpa = hitung_tanpa_kb(kasus)
    except Exception as e:  # noqa: BLE001 - cek silang tidak boleh menggagalkan hasil utama
        return {"status": "galat", "selisih": [], "pesan": f"{type(e).__name__}: {e}"}
    beda = selisih(h_kb, h_tanpa)
    status = "identik" if not beda else "sah_titik_tetap_ganda" if teradjudikasi(beda, h_kb) else "berbeda"
    return {"status": status, "selisih": [{"bulan": b, "fakta": f, "kb": a, "tanpa_kb": c} for b, f, a, c in beda]}


def hitung_satu(kasus, cek_silang=False):
    try:
        h = hitung_kb(kasus, berkas_perusahaan=BERKAS_PX if kasus.get("data_hr") else (), audit=True)
    except Exception as e:  # noqa: BLE001 - dipetakan ke pesan yang bisa ditampilkan; sisanya diteruskan apa adanya
        for kelas, jenis, awalan in GALAT:
            if isinstance(e, kelas):
                return {"ok": False, "jenis": jenis, "pesan": f"{awalan}: {e}"}
        return {"ok": False, "jenis": "galat_internal", "pesan": f"{type(e).__name__}: {e}"}
    jawab = {"ok": True, "hasil": h}
    if cek_silang:
        jawab["cek_silang"] = _cek_silang(kasus, h)
    return jawab


def contoh():
    from eksperimen.e8_perusahaan_x import kasus_kar_a
    hasil = [{"id": "KAR-A", "label": "Karyawan A (xlsx kantor, anonim)", "kasus": kasus_kar_a(2023)}]
    for d in json.loads(SINTETIS.read_text(encoding="utf-8")):
        hasil.append({"id": d["id"], "label": d["label"], "kasus": d["kasus"]})
    return hasil


def jalankan(permintaan):
    perintah = permintaan.get("perintah")
    if perintah == "hitung":
        cek = bool(permintaan.get("cek_silang"))
        return {"ok": True, "hasil": [hitung_satu(k, cek) for k in permintaan.get("kasus", [])]}
    if perintah == "contoh":
        return {"ok": True, "contoh": contoh()}
    if perintah == "info":
        return {"ok": True, "audit": metadata_audit()}
    return {"ok": False, "jenis": "perintah_tidak_dikenal", "pesan": f"perintah tidak dikenal: {perintah!r}"}


def main():
    try:
        permintaan = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))  # -sig: pipa PowerShell menambah BOM
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        jawab = {"ok": False, "jenis": "permintaan_tidak_valid", "pesan": f"permintaan bukan JSON UTF-8: {e}"}
    else:
        jawab = jalankan(permintaan)
    sys.stdout.write(json.dumps(jawab, ensure_ascii=True, default=str))
    sys.stdout.flush()
    return 0 if jawab["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
