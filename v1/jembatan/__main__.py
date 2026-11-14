"""Protokol jembatan: satu permintaan JSON di stdin, satu jawaban JSON di stdout.

    env\\Scripts\\python.exe -m jembatan < permintaan.json

Permintaan:
    {"perintah": "hitung", "kasus": [<kasus kanonik>, ...], "cek_silang": true, "berkas_tambahan": ["kb/tambahan/x.yaml"]}
    {"perintah": "contoh"}     data pegawai contoh dari dataset (Karyawan A + pegawai sintetis)
    {"perintah": "info"}       versi engine, versi KB, hash tabel
    {"perintah": "masukan", "berkas_tambahan": [...]}
                               isian tambahan yang diminta KB aktif + metadata komponen gaji perusahaan
    {"perintah": "usulkan", "pdf": "<path>", "lapisan": "perusahaan", "catatan": "", "model": "gpt-5.6-sol", "berkas_tambahan": [...]}
                               PDF peraturan -> rancangan berkas KB lewat LLM, lalu divalidasi. Butuh OPENAI_API_KEY
                               (model gpt-..., bawaan) atau ANTHROPIC_API_KEY (model claude-...). Lapisan berkas selalu
                               = `lapisan` permintaan; pilihan LLM disimpan di usulan.lapisan_llm
    {"perintah": "validasi", "yaml": "<isi berkas>", "nama": "x.yaml", "lapisan": "perusahaan", "berkas_tambahan": [...]}
                               validasi rancangan (skema, verifikasi statis, simulasi dampak) tanpa LLM; `lapisan`
                               (opsional) = lapisan pilihan unggah, peringatan bila YAML berbeda
    {"perintah": "periksa", "berkas_tambahan": [...]}
                               KB dasar + berkas tambahan dapat dimuat dan menghitung Karyawan A 2023-2027?
                               -> {"periksa": {"ok", "galat": [...], "tahun": [...]}}

`berkas_tambahan` = berkas KB yang sudah disetujui, relatif terhadap akar repo dan harus berada di bawah kb/tambahan/.
Jawaban selalu {"ok": true, ...} atau {"ok": false, "jenis": ..., "pesan": ...}. Untuk "hitung", setiap kasus
dijawab sendiri-sendiri, sehingga satu kasus yang galat tidak menggagalkan kasus lain dalam satu batch.
Keluaran ASCII murni (ensure_ascii) agar tidak bergantung pada code page konsol Windows.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

from baselines.b1_hardcoded import pph21_b1 as B1
from baselines.b2_payroll_hardcoded.payroll_b2 import hitung as hitung_tanpa_kb
from eksperimen.e12_tanpa_kb import BERKAS_PX, SINTETIS, selisih, teradjudikasi
from engine.audit import metadata_audit
from engine.inferensi import Ambigu, KasusTidakDidukung
from engine.kalkulator import hitung as hitung_kb
from engine.kalkulator import kb_aktif
from engine.muat import ROOT, KesalahanKB
from engine.waktu import InputTidakValid

GALAT = (
    (InputTidakValid, "input_tidak_valid", "Isian tidak valid"),
    ((KasusTidakDidukung, B1.KasusTidakDidukung), "di_luar_cakupan", "Kasus di luar cakupan kalkulator"),
    (Ambigu, "ambigu", "Aturan ambigu"),
    (KesalahanKB, "kesalahan_kb", "Data belum lengkap atau tidak sesuai"),
    ((KeyError, TypeError, ValueError), "data_tidak_sesuai", "Data belum lengkap atau tidak sesuai format"),
)
DIR_TAMBAHAN = (ROOT / "kb" / "tambahan").resolve()


class PermintaanTidakValid(ValueError):
    pass


def berkas_tambahan(permintaan):
    """Daftar berkas KB tambahan dari permintaan: hanya *.yaml di bawah kb/tambahan/ (berkas yang diterapkan lewat
    aplikasi web). KB dasar di kb/regulasi/ dan kb/perusahaan/ selalu dimuat engine sendiri; jembatan tidak membaca
    berkas lain."""
    daftar = permintaan.get("berkas_tambahan") or []
    if not isinstance(daftar, list) or not all(isinstance(b, str) for b in daftar):
        raise PermintaanTidakValid("berkas_tambahan harus daftar path berkas (teks)")
    hasil = []
    for b in daftar:
        # path UNC (\\server\berbagi\...) ditolak sebelum resolve(): resolve() akan menghubungi server berbagi berkas
        if len(b) > 1 and b[0] in "\\/" and b[1] in "\\/":
            raise PermintaanTidakValid(f"berkas KB tambahan harus *.yaml di bawah kb/tambahan/: {b}")
        p = (ROOT / b).resolve()
        if p.suffix != ".yaml" or not p.is_relative_to(DIR_TAMBAHAN):
            raise PermintaanTidakValid(f"berkas KB tambahan harus *.yaml di bawah kb/tambahan/: {b}")
        if not p.is_file():
            raise PermintaanTidakValid(f"berkas KB tambahan tidak ditemukan: {b}")
        hasil.append(p)
    return hasil


def sidik_kb(berkas):
    """Sidik isi berkas KB tambahan (urutan berpengaruh); '' bila tidak ada. Hasil lama dengan sidik berbeda = usang."""
    if not berkas:
        return ""
    h = hashlib.sha256()
    for p in berkas:
        h.update(p.name.encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def _cek_silang(kasus, h_kb):
    """E12 untuk satu kasus: bandingkan dengan kalkulator tanpa KB (B2 + B1)."""
    try:
        h_tanpa = hitung_tanpa_kb(kasus)
    except Exception as e:  # noqa: BLE001 - cek silang tidak boleh menggagalkan hasil utama
        return {"status": "galat", "selisih": [], "pesan": f"{type(e).__name__}: {e}"}
    beda = selisih(h_kb, h_tanpa)
    status = "identik" if not beda else "sah_titik_tetap_ganda" if teradjudikasi(beda, h_kb) else "berbeda"
    return {"status": status, "selisih": [{"bulan": b, "fakta": f, "kb": a, "tanpa_kb": c} for b, f, a, c in beda]}


def _petakan_galat(e):
    for kelas, jenis, awalan in GALAT:
        if isinstance(e, kelas):
            return {"ok": False, "jenis": jenis, "pesan": f"{awalan}: {e}"}
    return {"ok": False, "jenis": "galat_internal", "pesan": f"{type(e).__name__}: {e}"}


def _komponen(kb):
    return [{"fakta": k.fakta, "jenis": k.jenis, "kategori": k.kategori, "label": k.label, "berkas": k.berkas} for k in kb.komponen]


def hitung_satu(kasus, cek_silang=False, tambahan=()):
    if not isinstance(kasus, dict):
        return {"ok": False, "jenis": "data_tidak_sesuai", "pesan": "Data belum lengkap atau tidak sesuai format: "
                                                                     "kasus harus objek JSON"}
    berkas = [*BERKAS_PX, *tambahan] if kasus.get("data_hr") else list(tambahan)
    try:
        h = hitung_kb(kasus, berkas_perusahaan=berkas, audit=True)
    except Exception as e:  # noqa: BLE001 - dipetakan ke pesan yang bisa ditampilkan; sisanya diteruskan apa adanya
        return _petakan_galat(e)
    h["komponen"] = _komponen(kb_aktif(berkas))  # label komponen gaji (termasuk dari berkas tambahan) untuk slip
    jawab = {"ok": True, "hasil": h}
    if cek_silang:
        # kalkulator tanpa KB tidak mengenal aturan tambahan -> perbandingan tidak bermakna
        jawab["cek_silang"] = (_cek_silang(kasus, h) if not tambahan else
                               {"status": "dilewati", "selisih": [], "pesan": "ada berkas KB tambahan"})
    return jawab


def contoh():
    from eksperimen.e8_perusahaan_x import kasus_kar_a
    hasil = [{"id": "KAR-A", "label": "Karyawan A (xlsx kantor, anonim)", "kasus": kasus_kar_a(2023)}]
    for d in json.loads(SINTETIS.read_text(encoding="utf-8")):
        hasil.append({"id": d["id"], "label": d["label"], "kasus": d["kasus"]})
    return hasil


def masukan(tambahan):
    from asisten_kb.rancangan import masukan_tambahan
    kb = kb_aktif([*BERKAS_PX, *tambahan])
    return {"masukan": masukan_tambahan(kb), "komponen": _komponen(kb)}


def _lapisan(permintaan, bawaan=None):
    lapisan = permintaan.get("lapisan") or bawaan
    if lapisan not in (None, "regulasi", "perusahaan"):
        raise PermintaanTidakValid(f"lapisan tidak dikenal: {lapisan!r}")
    return lapisan


def _paksa_lapisan(usulan, lapisan):
    """Lapisan pilihan unggah yang berlaku, bukan pilihan LLM (instruksi hanya kalimat; LLM bisa memilih lain).
    Pilihan LLM disimpan agar peninjau melihat ketidaksepakatannya."""
    usulan["lapisan_llm"] = usulan.get("lapisan")
    usulan["lapisan"] = lapisan
    if usulan["lapisan_llm"] != lapisan:
        catatan = usulan.get("catatan_peninjau")
        catatan = list(catatan) if isinstance(catatan, list) else ([str(catatan)] if catatan else [])
        catatan.append(f"LLM menilai dokumen ini lapisan {usulan['lapisan_llm']}; berkas dibuat sebagai lapisan {lapisan} "
                       "sesuai pilihan unggahan")
        usulan["catatan_peninjau"] = catatan
    return usulan


def usulkan(permintaan, tambahan, klien=None):
    from asisten_kb.konteks import instruksi, prompt_sistem
    from asisten_kb.llm import KUNCI_API, MODEL_BAWAAN, GagalLLM, minta_usulan, penyedia
    from asisten_kb.rancangan import ke_berkas, ke_yaml, validasi

    pdf = Path(permintaan.get("pdf") or "")
    if pdf.suffix.lower() != ".pdf" or not pdf.is_file():
        raise PermintaanTidakValid(f"berkas PDF tidak ditemukan: {pdf}")
    lapisan = _lapisan(permintaan, "perusahaan")
    model = permintaan.get("model") or MODEL_BAWAAN
    kunci = KUNCI_API[penyedia(model)]
    if klien is None and not os.environ.get(kunci):
        raise PermintaanTidakValid(f"{kunci} belum diatur di .env aplikasi (model {model})")

    kb = kb_aktif([*BERKAS_PX, *tambahan])
    usulan, info = minta_usulan(pdf.read_bytes(), prompt_sistem(kb), instruksi(lapisan, permintaan.get("catatan") or ""),
                                model=model, klien=klien)
    if not isinstance(usulan, dict):
        raise GagalLLM("keluaran model bukan objek JSON")
    usulan = _paksa_lapisan(usulan, lapisan)
    jawab = {"usulan": usulan, "info": info, "yaml": "", "validasi": None}
    if usulan.get("dapat_dikodifikasi") and (usulan.get("aturan") or usulan.get("parameter") or usulan.get("klasifikasi_wajib")):
        # usulan sudah dibayar: galat apa pun setelah ini menjadi galat validasi, usulan & info tetap dikembalikan
        try:
            jawab["yaml"] = ke_yaml(ke_berkas(usulan), usulan.get("keterangan") or "", info.get("model") or model)
        except Exception as e:  # noqa: BLE001 - struktur usulan di luar skema
            jawab["validasi"] = {"ok": False, "galat": [f"usulan tidak dapat diubah menjadi berkas KB: {type(e).__name__}: {e}"],
                                 "peringatan": [], "ringkasan": {}, "isi": {}, "masukan": [], "dampak": [],
                                 "perubahan": [], "belum_teruji": []}
            return jawab
        jawab["validasi"] = validasi(jawab["yaml"], tambahan, _nama_berkas(usulan.get("id_berkas")), lapisan)
    return jawab


def _nama_berkas(id_berkas):
    nama = "".join(c if c.isalnum() or c in "_-" else "_" for c in (id_berkas or "rancangan")).strip("_") or "rancangan"
    return f"{nama[:60]}.yaml"


def jalankan(permintaan, klien=None):
    if not isinstance(permintaan, dict):
        return {"ok": False, "jenis": "permintaan_tidak_valid", "pesan": "permintaan harus objek JSON"}
    perintah = permintaan.get("perintah")
    try:
        if perintah == "hitung":
            tambahan = berkas_tambahan(permintaan)
            kasus = permintaan.get("kasus") or []
            if not isinstance(kasus, list):
                raise PermintaanTidakValid("kasus harus daftar")
            cek = bool(permintaan.get("cek_silang"))
            return {"ok": True, "sidik_kb": sidik_kb(tambahan), "hasil": [hitung_satu(k, cek, tambahan) for k in kasus]}
        if perintah == "contoh":
            return {"ok": True, "contoh": contoh()}
        if perintah == "info":
            return {"ok": True, "audit": metadata_audit()}
        if perintah == "masukan":
            tambahan = berkas_tambahan(permintaan)
            return {"ok": True, "sidik_kb": sidik_kb(tambahan), **masukan(tambahan)}
        if perintah == "usulkan":
            return {"ok": True, **usulkan(permintaan, berkas_tambahan(permintaan), klien)}
        if perintah == "validasi":
            from asisten_kb.rancangan import validasi
            return {"ok": True, "validasi": validasi(str(permintaan.get("yaml") or ""), berkas_tambahan(permintaan),
                                                     _nama_berkas(Path(str(permintaan.get("nama") or "")).stem),
                                                     _lapisan(permintaan))}
        if perintah == "periksa":
            from asisten_kb.rancangan import periksa_kb
            return {"ok": True, "periksa": periksa_kb(berkas_tambahan(permintaan))}
    except PermintaanTidakValid as e:
        return {"ok": False, "jenis": "permintaan_tidak_valid", "pesan": str(e)}
    except Exception as e:  # noqa: BLE001 - galat LLM / KB aktif yang rusak tetap dijawab sebagai JSON
        from asisten_kb.llm import GagalLLM
        if isinstance(e, GagalLLM):
            return {"ok": False, "jenis": "gagal_llm", "pesan": str(e)}
        return _petakan_galat(e)
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
