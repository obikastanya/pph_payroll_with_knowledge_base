"""Rancangan dari LLM -> berkas KB YAML -> validasi oleh engine (skema, verifikasi statis, simulasi dampak).

Validasi di sini sama dengan yang dialami berkas KB tulisan tangan, ditambah pemeriksaan asisten yang lebih ketat:
setiap kunci hr()/hr_masa() baru wajib dideklarasikan sebagai `masukan` agar aplikasi dapat menampilkan isiannya.
"""
import re
import tempfile
from datetime import date
from pathlib import Path

import yaml

from eksperimen.e12_tanpa_kb import BERKAS_PX
from eksperimen.e8_perusahaan_x import kasus_kar_a
from engine.angka import PelanggaranPresisi
from engine.ekspresi import KesalahanEkspresi
from engine.inferensi import Ambigu, KasusTidakDidukung
from engine.kalkulator import hitung
from engine.kb import _iso, muat_kb, rujukan_masukan
from engine.muat import KesalahanKB, muat_yaml
from engine.waktu import InputTidakValid
from jembatan.kontrak import KUNCI_INTI_BULAN, KUNCI_INTI_TAHUN

TAHUN_SIMULASI = (2023, 2024, 2025, 2026)
GALAT_KB = (KesalahanKB, PelanggaranPresisi, KesalahanEkspresi, ValueError, TypeError, KeyError)
GALAT_HITUNG = GALAT_KB + (Ambigu, KasusTidakDidukung, InputTidakValid)


# ------------------------------------------------------------------------------------------- usulan -> YAML

def _bawaan(tipe, teks):
    teks = (teks or "").strip()
    if teks == "":
        return None
    if tipe in ("rupiah", "bilangan") and re.fullmatch(r"-?\d+", teks):
        return int(teks)
    if tipe == "ya_tidak":
        return teks.lower() in ("true", "ya", "1")
    return teks


def _tgl(teks):
    """Teks ISO -> date agar YAML berisi tanggal biasa; teks tak sah dibiarkan (ditolak validasi skema)."""
    try:
        return date.fromisoformat(teks.strip())
    except (AttributeError, ValueError):
        return teks


def _berlaku(mulai, sampai):
    b = {"mulai": _tgl(mulai)}
    if (sampai or "").strip():
        b["sampai"] = _tgl(sampai)
    return b


def ke_berkas(u):
    """Usulan terstruktur dari LLM -> struktur berkas KB (dict) sesuai kb/skema/aturan.schema.json."""
    d = {"lapisan": u["lapisan"], "id": u.get("id_berkas") or "tambahan"}
    if u.get("keterangan"):
        d["keterangan"] = u["keterangan"]
    if u.get("komponen"):
        d["komponen"] = [{"fakta": k["fakta"], "jenis": k["jenis"], "kategori": k["kategori"],
                          **({"label": k["label"]} if k.get("label") else {})} for k in u["komponen"]]
    if u.get("masukan"):
        d["masukan"] = []
        for m in u["masukan"]:
            e = {"kunci": m["kunci"], "label": m["label"], "tipe": m["tipe"], "lingkup": m["lingkup"], "wajib": m["wajib"]}
            bawaan = _bawaan(m["tipe"], m.get("bawaan"))
            if bawaan is not None:
                e["bawaan"] = bawaan
            if m["tipe"] == "pilihan" and m.get("pilihan"):
                e["pilihan"] = list(m["pilihan"])
            for f in ("keterangan", "sumber"):
                if m.get(f):
                    e[f] = m[f]
            d["masukan"].append(e)
    if u.get("parameter"):
        d["parameter"] = [{"nama": p["nama"],
                           "nilai": int(p["nilai"]) if p["jenis_nilai"] == "rupiah" and re.fullmatch(r"-?\d+", p["nilai"].strip())
                           else p["nilai"].strip(),
                           "berlaku": _berlaku(p["mulai"], p.get("sampai")), "sumber": p["sumber"]} for p in u["parameter"]]
    if u.get("pembulatan"):
        d["pembulatan"] = [{k: e[k] for k in ("id", "titik", "satuan", "mode", "urutan", "status", "dasar")} for e in u["pembulatan"]]
    if u.get("klasifikasi_wajib"):
        d["klasifikasi_wajib"] = [{"jenis": k["jenis"], "kategori": k["kategori"], "berlaku": _berlaku(k["mulai"], k.get("sampai")),
                                   "sumber": k["sumber"]} for k in u["klasifikasi_wajib"]]
    d["aturan"] = []
    for a in u.get("aturan") or []:
        e = {"id": a["id"], "sifat": a["sifat"], "berlaku": _berlaku(a["mulai"], a.get("sampai")), "lingkup": a["lingkup"],
             "menghasilkan": a["menghasilkan"]}
        if (a.get("jika") or "").strip():
            e["jika"] = a["jika"].strip()
        e["maka"] = a["maka"].strip()
        e["tipe_hasil"] = a["tipe_hasil"]
        if (a.get("pembulatan") or "").strip():
            e["pembulatan"] = a["pembulatan"].strip()
        e["sumber"] = a["sumber"]
        if a.get("catatan"):
            e["catatan"] = a["catatan"]
        d["aturan"].append(e)
    return d


def ke_yaml(berkas, judul="", model=""):
    kepala = ["# Rancangan berkas KB dari dokumen peraturan" + (f": {judul}" if judul else ""),
              f"# Disusun asisten KB{f' ({model})' if model else ''} pada {date.today().isoformat()}; WAJIB ditinjau manusia sebelum diterapkan."]
    isi = yaml.safe_dump(berkas, allow_unicode=True, sort_keys=False, width=120, default_flow_style=False)
    return "\n".join(kepala) + "\n" + isi


# ------------------------------------------------------------------------------------------- masukan tambahan

def masukan_tambahan(kb, hanya_berkas=None):
    """Masukan yang diminta aturan selain isian inti aplikasi: dideklarasikan (`masukan`) dan/atau dirujuk lewat
    hr()/hr_masa(). Rujukan tanpa deklarasi diberi label & tipe tebakan dan ditandai dideklarasikan=False."""
    rujuk = rujukan_masukan(kb)
    asal_aturan = {a.id: a.berkas for a in kb.aturan}
    aturan = {a.id: a for a in kb.aturan}
    hasil = []
    for kunci in sorted(set(kb.masukan) | set(rujuk)):
        r = rujuk.get(kunci, {"lingkup": set(), "aturan": [], "bawaan_di_aturan": False})
        m = kb.masukan.get(kunci)
        lingkup = m.lingkup if m else ("bulan" if "bulan" in r["lingkup"] else "tahun")
        if (lingkup == "tahun" and kunci in KUNCI_INTI_TAHUN) or (lingkup == "bulan" and kunci in KUNCI_INTI_BULAN):
            continue
        berkas = {m.berkas} if m else set()
        berkas |= {asal_aturan[i] for i in r["aturan"]}
        if hanya_berkas and not (berkas & set(hanya_berkas)):
            continue
        if m:
            e = {"kunci": kunci, "label": m.label, "tipe": m.tipe, "lingkup": m.lingkup,
                 "wajib": m.wajib and m.bawaan is None and not r["bawaan_di_aturan"], "bawaan": m.bawaan,
                 "pilihan": list(m.pilihan), "keterangan": m.keterangan, "sumber": m.sumber, "dideklarasikan": True}
        else:
            e = {"kunci": kunci, "label": kunci.replace("_", " ").capitalize(), "tipe": "bilangan", "lingkup": lingkup,
                 "wajib": not r["bawaan_di_aturan"], "bawaan": None, "pilihan": [], "keterangan": "", "sumber": "",
                 "dideklarasikan": False}
        e["berkas"] = sorted(berkas)
        e["aturan"] = r["aturan"]
        # rentang berlaku aturan yang membacanya: aplikasi hanya meminta isian ini untuk masa di dalam rentang
        ats = [aturan[i] for i in r["aturan"]]
        e["mulai"] = min(a.mulai for a in ats).isoformat() if ats else None
        e["sampai"] = (None if not ats or any(a.sampai is None for a in ats) else max(a.sampai for a in ats).isoformat())
        hasil.append(e)
    return hasil


# ------------------------------------------------------------------------------------------- validasi

def _nilai_contoh(m, tahun):
    """Nilai contoh untuk simulasi: bawaan bila bermakna, selain itu nilai rekaan agar dampak aturan terlihat."""
    if m["bawaan"] not in (None, 0, "0", "", False):
        return m["bawaan"]
    return {"rupiah": 100_000, "bilangan": 1, "persen": "10", "desimal": "0.1", "tanggal": f"{tahun}-06-01",
            "pilihan": (m["pilihan"] or [""])[0], "ya_tidak": True}[m["tipe"]]


def _ringkas(h):
    pm = h["per_masa"].values()
    return {"bruto_setahun": h["tahunan"].get("bruto_setahun"), "pph21_setahun": h["tahunan"].get("pph21_setahun"),
            "thp_setahun": sum(m.get("px_thp") or 0 for m in pm)}


def _tahun_berlaku(data):
    tahun = set()
    for e in list(data.get("aturan") or []) + list(data.get("parameter") or []):
        b = e.get("berlaku") or {}
        mulai = str(b.get("mulai", "2016-01-01"))[:4]
        sampai = str(b.get("sampai") or "9999")[:4]
        tahun |= {t for t in TAHUN_SIMULASI if mulai.isdigit() and int(mulai) <= t <= int(sampai if sampai.isdigit() else 9999)}
    return sorted(tahun)


def validasi(teks_yaml, berkas_aktif=(), nama_berkas="rancangan.yaml"):
    """-> {ok, galat[], peringatan[], ringkasan{}, isi{}, masukan[], dampak[]}. Tidak pernah melempar untuk galat isi."""
    hasil = {"ok": False, "galat": [], "peringatan": [], "ringkasan": {}, "isi": {}, "masukan": [], "dampak": []}
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / nama_berkas
        p.write_text(teks_yaml, encoding="utf-8")
        try:
            data = muat_yaml(p)
        except (yaml.YAMLError, PelanggaranPresisi, KesalahanKB) as e:   # sintaks, float literal, kunci duplikat
            hasil["galat"].append(f"YAML tidak dapat dibaca: {e}")
            return hasil
        if not isinstance(data, dict):
            hasil["galat"].append("isi berkas harus berupa objek YAML (lapisan, aturan, ...)")
            return hasil
        hasil["isi"] = _iso(data)   # untuk halaman tinjau: mencerminkan YAML yang sudah diubah admin
        hasil["ringkasan"] = {"lapisan": data.get("lapisan"), "aturan": len(data.get("aturan") or []),
                              "komponen": len(data.get("komponen") or []), "masukan": len(data.get("masukan") or []),
                              "parameter": len(data.get("parameter") or []), "pembulatan": len(data.get("pembulatan") or [])}
        if not (data.get("aturan") or data.get("parameter") or data.get("klasifikasi_wajib")):
            hasil["galat"].append("rancangan tidak berisi aturan, parameter, atau klasifikasi apa pun")
            return hasil

        dasar = [*BERKAS_PX, *berkas_aktif]
        try:
            kb_dasar = muat_kb(dasar)
            kb = muat_kb([*dasar, p])
        except GALAT_KB as e:
            hasil["galat"].append(f"ditolak verifikasi KB: {e}")
            return hasil

        # asisten lebih ketat dari engine: setiap masukan baru wajib dideklarasikan (label & tipe untuk form aplikasi)
        masukan = masukan_tambahan(kb, hanya_berkas=[p.name])
        for m in masukan:
            if not m["dideklarasikan"]:
                hasil["galat"].append(f"hr('{m['kunci']}') dipakai aturan {m['aturan']} tetapi belum dideklarasikan di 'masukan'")
        if data.get("lapisan") == "perusahaan":
            baru = {a["menghasilkan"] for a in data.get("aturan") or []} - {a.menghasilkan for a in kb_dasar.aturan}
            for f in sorted(baru):
                if not f.startswith(("px_", "_")):
                    hasil["peringatan"].append(f"fakta baru '{f}' sebaiknya berawalan px_ (lapisan perusahaan)")
        hasil["masukan"] = masukan

        # simulasi dampak pada Karyawan A di tahun-tahun yang tersentuh rancangan
        for tahun in _tahun_berlaku(data) or [TAHUN_SIMULASI[-1]]:
            kasus = kasus_kar_a(tahun)
            contoh = {}
            for m in masukan:
                contoh[m["kunci"]] = v = _nilai_contoh(m, tahun)
                if m["lingkup"] == "tahun":
                    kasus["data_hr"][m["kunci"]] = v
                else:
                    for per in kasus["data_hr"]["per_masa"].values():
                        per[m["kunci"]] = v
            try:
                sebelum = _ringkas(hitung(kasus_kar_a(tahun), kb=kb_dasar))
                h = hitung(kasus, kb=kb)
            except GALAT_HITUNG as e:
                hasil["galat"].append(f"simulasi Karyawan A {tahun} gagal: {type(e).__name__}: {e}")
                continue
            fakta_baru = sorted({a["menghasilkan"] for a in data.get("aturan") or []})
            nilai_baru = {f: (sum(v for m in h["per_masa"].values() if isinstance(v := m.get(f), int))
                              if any(f in m for m in h["per_masa"].values()) else h["tahunan"].get(f)) for f in fakta_baru}
            hasil["dampak"].append({"pegawai": "Karyawan A (contoh)", "tahun": tahun, "nilai_contoh": contoh,
                                    "sebelum": sebelum, "sesudah": _ringkas(h), "fakta_baru": nilai_baru})
            for pr in h["peringatan"]:
                if pr.get("kode") == "KONFLIK_WAJIB" and (pr.get("berkas") == p.name or set(pr.get("ditolak") or []) & {a["id"] for a in data.get("aturan") or []}):
                    teks = f"konflik dengan aturan wajib regulasi pada {pr.get('fakta')}: aturan regulasi yang dipakai"
                    if teks not in hasil["peringatan"]:
                        hasil["peringatan"].append(teks)
    hasil["ok"] = not hasil["galat"]
    return hasil
