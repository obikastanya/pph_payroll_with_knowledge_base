"""Rancangan dari LLM -> berkas KB YAML -> validasi oleh engine (skema, verifikasi statis, simulasi dampak).

Validasi di sini sama dengan yang dialami berkas KB tulisan tangan, ditambah pemeriksaan asisten yang lebih ketat:
setiap kunci hr()/hr_masa() baru wajib dideklarasikan sebagai `masukan` agar aplikasi dapat menampilkan isiannya.
Validasi tidak pernah melempar: setiap galat (termasuk galat tak terduga) menjadi entri `galat`, karena di jembatan
keluaran LLM yang sudah dibayar dan di aplikasi web suntingan admin harus tetap kembali utuh.
"""
import ast
import functools
import re
import tempfile
from dataclasses import replace
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path

import yaml

from eksperimen.e12_tanpa_kb import BERKAS_PX
from eksperimen.e8_perusahaan_x import kasus_kar_a
from engine.inferensi import Konteks
from engine.kalkulator import hitung, kb_aktif
from engine.kb import _iso, masa_berlaku_efektif, muat_kb, rujukan_masukan
from engine.muat import muat_yaml
from jembatan.kontrak import KUNCI_INTI_BULAN, KUNCI_INTI_TAHUN

from .konteks import _teks_nilai

# Jangkauan simulasi: aturan lama disimulasikan sampai TAHUN_RUJUKAN, aturan baru minimal dua tahun pertamanya.
TAHUN_AWAL, TAHUN_RUJUKAN, TAHUN_AKHIR, TAHUN_LEWAT, MAKS_TAHUN = 2023, 2026, 2030, 2031, 8
TAHUN_PERIKSA = tuple(range(2023, 2028))


# ------------------------------------------------------------------------------------------- usulan -> YAML

def _rupiah(teks):
    """Teks rupiah -> int. Pemisah ribuan ("500.000", "12.000.000", "1,500,000") diterima karena lazim di dokumen;
    selain bilangan bulat dibiarkan teks agar engine menolaknya (jenis nilai tidak cocok), bukan ditebak."""
    t = str(teks).strip()
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if re.fullmatch(r"-?[1-9]\d{0,2}(\.\d{3})+", t) or re.fullmatch(r"-?[1-9]\d{0,2}(,\d{3})+", t):
        return int(re.sub(r"[.,]", "", t))
    return t


def _bawaan(tipe, teks):
    teks = (teks or "").strip()
    if teks == "":
        return None
    if tipe == "rupiah":
        return _rupiah(teks)
    if tipe == "bilangan" and re.fullmatch(r"-?\d+", teks):
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
                           "nilai": _rupiah(p["nilai"]) if p["jenis_nilai"] == "rupiah" else str(p["nilai"]).strip(),
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
        diganti = list(dict.fromkeys(i.strip() for i in a.get("menggantikan") or [] if i.strip()))
        if diganti:   # field hanya ditulis bila ada yang diganti (skema KB menolak daftar kosong)
            e["menggantikan"] = diganti
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


def _satu_baris(teks):
    return " ".join(str(teks or "").split())


def ke_yaml(berkas, judul="", model=""):
    # judul/model masuk komentar kepala: baris baru di dalamnya akan memutus komentar dan merusak YAML
    judul, model = _satu_baris(judul), _satu_baris(model)
    kepala = ["# Rancangan berkas KB dari dokumen peraturan" + (f": {judul}" if judul else ""),
              f"# Disusun asisten KB{f' ({model})' if model else ''} pada {date.today().isoformat()}; WAJIB ditinjau manusia sebelum diterapkan."]
    isi = yaml.safe_dump(berkas, allow_unicode=True, sort_keys=False, width=120, default_flow_style=False)
    return "\n".join(kepala) + "\n" + isi


# ------------------------------------------------------------------------------------------- masukan tambahan

def masukan_tambahan(kb, hanya_berkas=None):
    """Masukan yang diminta aturan selain isian inti aplikasi: dideklarasikan (`masukan`) dan/atau dirujuk lewat
    hr()/hr_masa(). Rujukan tanpa deklarasi diberi label & tipe tebakan dan ditandai dideklarasikan=False.

    `wajib` = perilaku engine, bukan sekadar deklarasi: masukan yang dibaca aturan tanpa `bawaan` dan tanpa bawaan
    di aturan (hr_masa('k', 0)) membuat setiap perhitungan gagal (DATA_KURANG) bila dikosongkan."""
    rujuk = rujukan_masukan(kb)
    asal_aturan = {a.id: a.berkas for a in kb.aturan}
    efektif = masa_berlaku_efektif(kb)   # aturan yang dicabut permanen (`menggantikan`) berhenti meminta isiannya
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
            # tidak dibaca aturan mana pun -> tidak pernah gagal; deklarasinya saja yang menentukan
            wajib = m.bawaan is None and (not r["bawaan_di_aturan"] if kunci in rujuk else m.wajib)
            e = {"kunci": kunci, "label": m.label, "tipe": m.tipe, "lingkup": m.lingkup,
                 "wajib": wajib, "bawaan": m.bawaan,
                 "pilihan": list(m.pilihan), "keterangan": m.keterangan, "sumber": m.sumber, "dideklarasikan": True}
        else:
            e = {"kunci": kunci, "label": kunci.replace("_", " ").capitalize(), "tipe": "bilangan", "lingkup": lingkup,
                 "wajib": not r["bawaan_di_aturan"], "bawaan": None, "pilihan": [], "keterangan": "", "sumber": "",
                 "dideklarasikan": False}
        e["berkas"] = sorted(berkas)
        e["aturan"] = r["aturan"]
        # rentang berlaku aturan yang membacanya: aplikasi hanya meminta isian ini untuk masa di dalam rentang
        masa = [efektif[i] for i in r["aturan"]]
        e["mulai"] = min(m for m, _ in masa).isoformat() if masa else None
        e["sampai"] = (None if not masa or any(s is None for _, s in masa) else max(s for _, s in masa).isoformat())
        hasil.append(e)
    return hasil


# ------------------------------------------------------------------------------------------- pegawai contoh

def kasus_masuk_juli(tahun):
    """Karyawan A yang baru masuk 1 Juli (masa Juli-Desember): menyentuh aturan masa kerja, bulan pertama, dan
    prorata yang tidak pernah menyala pada pegawai setahun penuh. Kenaikan gaji (Maret) dan THR (April) jatuh
    sebelum ia masuk, sehingga tidak ada data hari kerja yang hilang."""
    k = kasus_kar_a(tahun)
    k["id"] = f"PX-MASUK-JULI-{tahun}"
    k["pegawai"]["bulan_masuk"] = 7
    k["masa"] = [m for m in k["masa"] if m["bulan"] >= 7]
    hr = k["data_hr"]
    hr["per_masa"] = {b: v for b, v in hr["per_masa"].items() if int(b) >= 7}
    hr["tanggal_masuk"] = hr["tanggal_masuk_awal_bulan"] = f"{tahun}-07-01"
    hr["bpjs_tk_mulai_bulan"] = hr["bpjs_kes_mulai_bulan"] = 7
    return k


PROFIL = (("Karyawan A", kasus_kar_a), ("Pegawai masuk Juli", kasus_masuk_juli))


def _gross_up(kasus):
    """Pegawai contoh memakai metode gross; aturan titik tetap (tunjangan pajak) baru menyala pada metode gross-up."""
    kasus["metode"] = "gross_up"
    return kasus


@functools.lru_cache(maxsize=None)
def _dasar_bisa_gross_up(tahun):
    """KB dasar sendiri dapat menghitung Karyawan A dengan metode gross-up di tahun ini? (2023: rezim PER-16 di luar
    model.) Hanya tahun seperti itu yang diperiksa gross-up-nya, agar yang dilaporkan memang akibat berkas tambahan."""
    try:
        hitung(_gross_up(kasus_kar_a(tahun)), kb=kb_aktif(BERKAS_PX))
    except Exception:  # noqa: BLE001
        return False
    return True


def _nilai_contoh(m, tahun):
    """Nilai contoh untuk simulasi: bawaan bila bermakna, selain itu nilai rekaan agar dampak aturan terlihat."""
    if m["bawaan"] not in (None, 0, "0", "", False):
        return m["bawaan"]
    return {"rupiah": 100_000, "bilangan": 1, "persen": "10", "desimal": "0.1", "tanggal": f"{tahun}-06-01",
            "pilihan": (m["pilihan"] or [""])[0], "ya_tidak": True}.get(m["tipe"], 1)


def nilai_contoh(daftar, tahun, tetap=None):
    """{kunci: nilai contoh} untuk setiap masukan tambahan. `tetap`: nilai yang sudah dipilih untuk KB lain, agar
    kunci yang sama bernilai sama di simulasi sebelum & sesudah (angka dampaknya sebanding)."""
    tetap = tetap or {}
    return {m["kunci"]: tetap[m["kunci"]] if m["kunci"] in tetap else _nilai_contoh(m, tahun) for m in daftar}


def isi_contoh(kasus, daftar, nilai):
    """Isi data_hr kasus dengan nilai contoh untuk SEMUA masukan tambahan KB, termasuk milik berkas yang sudah
    aktif: tanpa ini masukan wajib berkas lain membuat simulasi gagal DATA_KURANG."""
    hr = kasus["data_hr"]
    for m in daftar:
        if m["lingkup"] == "tahun":
            hr[m["kunci"]] = nilai[m["kunci"]]
        else:
            for per in hr["per_masa"].values():
                per[m["kunci"]] = nilai[m["kunci"]]
    return kasus


# ------------------------------------------------------------------------------------------- validasi

def _teks_galat(e):
    return f"{type(e).__name__}: {e}"


def _aturan_gagal(e):
    """id aturan yang sedang dievaluasi saat galat terjadi (Konteks terdalam di traceback), bila ada. Galat Python
    biasa (AttributeError, OverflowError, ...) dari ekspresi tidak menyebut aturannya sendiri."""
    id_, tb = None, e.__traceback__
    while tb is not None:
        for v in list(tb.tb_frame.f_locals.values()):
            if isinstance(v, Konteks) and getattr(v, "aturan", None) is not None:
                id_ = v.aturan.id
        tb = tb.tb_next
    return id_


def _galat_hitung(e):
    id_ = _aturan_gagal(e)
    return (f" (aturan {id_})" if id_ else "") + f": {_teks_galat(e)}"


def _banyak(x):
    return len(x) if isinstance(x, list) else 0


def _json(v):
    if isinstance(v, Fraction):
        return str(v)
    if isinstance(v, date):
        return v.isoformat()
    return v


def _bulat(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _ringkas(h):
    pm = h["per_masa"].values()
    return {"bruto_setahun": h["tahunan"].get("bruto_setahun"), "pph21_setahun": h["tahunan"].get("pph21_setahun"),
            "thp_setahun": sum(m.get("px_thp") or 0 for m in pm)}


def _ke_tanggal(v):
    return v if isinstance(v, date) else date.fromisoformat(str(v))


def tahun_simulasi(data):
    """Tahun pajak yang disimulasikan: untuk setiap aturan, parameter, dan klasifikasi, tahun max(2023, mulai) s.d.
    min(2030, max(2026, mulai + 1)) yang ada di masa berlakunya, ditambah tahun sesudah `sampai` (s.d. 2031).
    Tahun pertama tiap entri dan tahun sesudah `sampai` didahulukan bila dibatasi MAKS_TAHUN."""
    utama, lain = [], []
    for e in [*(data.get("aturan") or []), *(data.get("parameter") or []), *(data.get("klasifikasi_wajib") or [])]:
        b = e.get("berlaku") or {}
        try:
            mulai = _ke_tanggal(b["mulai"])
            sampai = _ke_tanggal(b["sampai"]) if b.get("sampai") else None
        except (KeyError, TypeError, ValueError):
            continue
        akhir = min(TAHUN_AKHIR, max(TAHUN_RUJUKAN, mulai.year + 1))
        rentang = [t for t in range(max(TAHUN_AWAL, mulai.year), akhir + 1) if sampai is None or t <= sampai.year]
        utama += rentang[:1]
        lain += rentang[1:]
        if sampai is not None and TAHUN_AWAL <= sampai.year + 1 <= TAHUN_LEWAT:
            utama.append(sampai.year + 1)   # nilai/aturan lama harus jalan lagi setelah amandemen sementara berakhir
    return sorted(list(dict.fromkeys(utama + lain))[:MAKS_TAHUN])


def _fakta_baru(jejak, ids, fakta):
    """Nilai yang dihasilkan aturan rancangan saja (dari jejak), bukan nilai fakta yang dihasilkan aturan lama."""
    nilai = {f: None for f in fakta}
    for j in jejak:
        if j["aturan"] not in ids:
            continue
        v, f = j["nilai"], j["fakta"]
        if _bulat(v):
            nilai[f] = (nilai[f] if _bulat(nilai.get(f)) else 0) + v
        else:
            nilai[f] = _json(v)
    return nilai


def _teks_rupiah_atau_tarif(v):
    return f"{v:,}".replace(",", ".") if _bulat(v) else _teks_nilai(v)


def _versi_pada(versi, tgl):
    """Versi (mulai, sampai, nilai, ...) yang berlaku pada tgl; yang mulai terakhir bila lebih dari satu."""
    cocok = [v for v in versi if v[0] <= tgl and (v[1] is None or tgl <= v[1])]
    return max(cocok, key=lambda v: v[0]) if cocok else None


def _rentang(mulai, sampai):
    return f"mulai {mulai}" + (f" sampai {sampai}" if sampai else " (tanpa batas akhir)")


def _sesudah(sampai, akhir, versi, lama_teks, teks):
    """Lanjutan kalimat perubahan: apa yang berlaku sesudah amandemen ini berakhir. `sampai` = akhir yang ditulis
    rancangan, `akhir` = akhir efektif di KB. Keduanya berbeda bila versi lain yang mulai lebih baru sudah ada (amandemen
    berlaku surut): tanpa keterangan ini peninjau mengira amandemen berlaku tanpa batas. lama_teks None = tidak perlu
    menyebut nilai sesudah amandemen sementara."""
    if akhir is not None and (not sampai or _ke_tanggal(sampai) != akhir):
        lanjut = _versi_pada(versi, akhir + timedelta(days=1))
        return (f"; efektif hanya sampai {akhir}: versi yang mulai {akhir + timedelta(days=1)} sudah ada"
                + (f" ({teks(lanjut)})" if lanjut else ""))
    if not sampai or lama_teks is None:
        return ""
    lanjut = _versi_pada(versi, _ke_tanggal(sampai) + timedelta(days=1))
    if lanjut is None or teks(lanjut) == lama_teks:
        return f"; setelah {sampai} kembali {lama_teks}"
    return f"; setelah {sampai} berlaku {teks(lanjut)} (versi lain yang sudah ada)"


def _pemakaian(id_aturan, jejak, jejak_gross_up=()):
    """(jumlah instance yang dimenangkan aturan, [entri jejak tempat ia kalah], nama simulasinya). jejak_gross_up: jejak
    simulasi metode gross-up, dipakai untuk aturan yang tidak pernah menyala pada metode gross."""
    menang = sum(1 for j in jejak if j["aturan"] == id_aturan)
    kalah = [j for j in jejak if id_aturan in (j["ditolak"] or [])]
    if not menang and not kalah:   # mis. pengganti aturan tunjangan pajak: hanya menyala pada metode gross-up
        menang_gu = sum(1 for j in jejak_gross_up if j["aturan"] == id_aturan)
        kalah_gu = [j for j in jejak_gross_up if id_aturan in (j["ditolak"] or [])]
        if menang_gu or kalah_gu:
            return menang_gu, kalah_gu, "simulasi metode gross-up"
    return menang, kalah, "simulasi"


def _satuan(a):
    return "masa" if a["lingkup"] == "masa" else "tahun"


def _perubahan(d, kb_dasar, kb, jejak, jejak_gross_up=()):
    """Apa yang diganti rancangan pada KB aktif: aturan yang dicabut eksplisit (`menggantikan`), aturan untuk fakta yang
    sudah ada, amandemen parameter, dan klasifikasi wajib. Satu-satunya sinyal bagi peninjau bahwa ketentuan pajak yang
    ada sedang diganti."""
    hasil = []
    per_fakta = {}
    for a in kb_dasar.aturan:
        per_fakta.setdefault(a.menghasilkan, []).append(a)
    efektif = masa_berlaku_efektif(kb)
    for a in d.get("aturan") or []:
        satuan = _satuan(a)
        menang, kalah, simulasi = _pemakaian(a["id"], jejak, jejak_gross_up)
        diganti = a.get("menggantikan") or []
        if diganti:
            sampai = a["berlaku"].get("sampai")
            hasil.append({"jenis": "aturan", "teks": (
                f"{a['id']} menggantikan {', '.join(diganti)} (fakta '{a['menghasilkan']}') mulai {a['berlaku']['mulai']}"
                + (f" sampai {sampai}; sesudahnya aturan lama berlaku lagi" if sampai else "")
                + f"; pada {simulasi} dipakai di {menang} {satuan}")})
        # aturan yang dicabut (oleh aturan ini, atau permanen sebelum aturan ini mulai) bukan pesaing lagi
        mulai = _ke_tanggal(a["berlaku"]["mulai"])
        lama = [x for x in per_fakta.get(a["menghasilkan"]) or []
                if x.id not in diganti and not (efektif[x.id][1] != x.sampai and efektif[x.id][1] < mulai)]
        if not lama:
            continue
        pemenang = sorted({j["aturan"] for j in kalah})
        hasil.append({"jenis": "aturan", "teks": (
            f"{a['id']} menghasilkan '{a['menghasilkan']}' yang sudah dihasilkan "
            + ", ".join(f"{x.id} ({x.lapisan}/{x.sifat})" for x in lama)
            + f"; pada {simulasi} dipakai di {menang} {satuan}, kalah di {len(kalah)} {satuan}"
            + (f" (dikalahkan {', '.join(pemenang)})" if pemenang else ""))})
    for p in d.get("parameter") or []:
        versi_lama = kb_dasar.parameter.get(p["nama"])
        if not versi_lama:
            continue
        mulai = _ke_tanggal(p["berlaku"]["mulai"])
        sampai = p["berlaku"].get("sampai")
        sebelum = _versi_pada(versi_lama, mulai - timedelta(days=1))
        baru = _versi_pada(kb.parameter[p["nama"]], mulai)
        lama_teks = _teks_rupiah_atau_tarif(sebelum[2]) if sebelum else "(belum ada)"
        hasil.append({"jenis": "parameter", "teks": (
            f"parameter {p['nama']}: {lama_teks} -> {_teks_rupiah_atau_tarif(baru[2]) if baru else p['nilai']} "
            f"{_rentang(mulai, sampai)}"
            + _sesudah(sampai, baru[1] if baru else None, kb.parameter[p["nama"]], lama_teks if sebelum else None,
                       lambda v: _teks_rupiah_atau_tarif(v[2])))})
    for k in d.get("klasifikasi_wajib") or []:
        mulai = _ke_tanggal(k["berlaku"]["mulai"])
        sampai = k["berlaku"].get("sampai")
        ada = [(w.mulai, w.sampai, w) for w in kb_dasar.klasifikasi if w.jenis == k["jenis"]]
        if ada:
            sebelum = _versi_pada(ada, mulai - timedelta(days=1))
            lama_teks = sebelum[2].kategori if sebelum else "(belum diatur)"
            kini = [(w.mulai, w.sampai, w) for w in kb.klasifikasi if w.jenis == k["jenis"]]
            baru = _versi_pada(kini, mulai)
            hasil.append({"jenis": "klasifikasi", "teks": (
                f"klasifikasi wajib {k['jenis']}: {lama_teks} -> {k['kategori']} {_rentang(mulai, sampai)}"
                + _sesudah(sampai, baru[1] if baru else None, kini, None, lambda v: v[2].kategori))})
            continue
        # jenis baru tetap mengubah perlakuan pajak komponen perusahaan yang jenisnya sama
        kena = [f"{x.fakta} ({x.kategori})" for x in kb_dasar.komponen if x.jenis == k["jenis"]]
        if kena:
            hasil.append({"jenis": "klasifikasi", "teks": (
                f"klasifikasi wajib baru {k['jenis']} -> {k['kategori']} {_rentang(mulai, sampai)}; komponen "
                f"perusahaan yang terkena: {', '.join(kena)}")})
    return hasil


def _belum_teruji(ids, jejak):
    terpakai = {j["aturan"] for j in jejak}
    hasil = []
    for i in ids:
        if i in terpakai:
            continue
        kalah = next((j for j in jejak if i in (j["ditolak"] or [])), None)
        if kalah is not None:
            alasan = f"kalah dari {kalah['aturan']} ({', '.join(kalah['alasan']) or 'resolusi konflik'})"
        else:
            alasan = "tidak pernah menyala pada simulasi (syarat atau masa berlaku tidak terpenuhi)"
        hasil.append({"aturan": i, "alasan": alasan})
    return hasil


def _tambah(daftar, teks):
    if teks not in daftar:
        daftar.append(teks)


def _teks_bawaan(v, tipe):
    if isinstance(v, bool):
        return "true" if v else "false"
    return _teks_rupiah_atau_tarif(v) if tipe == "rupiah" and _bulat(v) else str(v)   # bilangan 2026 bukan "2.026"


def _peringatan_bawaan(hasil, e, rujuk):
    """Masukan rancangan yang punya `bawaan`: engine memakai bawaan setiap kali nilainya kosong dan tidak pernah
    melihat `wajib` (engine/inferensi.py _hr), sehingga pegawai yang belum diisi dihitung diam-diam. `e` = entri
    mentah berkas, agar `wajib: true` yang ditulis dapat dibedakan dari bawaan skema. `rujuk` = rujukan_masukan(kb)."""
    if e.get("bawaan") is None:
        return
    b = _teks_bawaan(e["bawaan"], e.get("tipe"))
    r = rujuk.get(e["kunci"])
    if r and r["bawaan_di_aturan"]:
        # engine mendahulukan bawaan di aturan: angka di deklarasi bukan angka yang dipakai, jadi tidak disebut "dihitung"
        hasil["peringatan"].append(
            f"masukan '{e['kunci']}' punya bawaan {b}, tetapi bawaan itu tidak pernah dipakai: aturan yang membacanya "
            f"({', '.join(r['aturan'])}) memberi bawaan sendiri lewat hr_masa('{e['kunci']}', ...), dan engine "
            f"mendahulukan bawaan di aturan; pegawai yang nilainya kosong dihitung dengan bawaan di aturan tanpa tanda "
            f"apa pun; hapus 'bawaan' di deklarasi, atau hapus bawaan di aturan bila {b} yang dimaksud")
    elif e.get("wajib") is True:
        hasil["peringatan"].append(
            f"masukan '{e['kunci']}' dideklarasikan wajib: true tetapi punya bawaan {b}; keduanya bertentangan: engine "
            f"memakai bawaan bila nilainya kosong, sehingga pegawai yang belum diisi dihitung dengan {b} tanpa galat; "
            f"hapus 'bawaan' bila nilainya memang wajib diisi, atau tulis wajib: false")
    else:
        hasil["peringatan"].append(
            f"masukan '{e['kunci']}' punya bawaan {b}: pegawai yang nilainya kosong dihitung dengan {b} tanpa tanda apa "
            f"pun; nilai yang sama untuk seluruh perusahaan lebih tepat menjadi parameter perusahaan (parameter px_... "
            f"di berkas lapisan perusahaan, dibaca dengan parameter('...')), bukan masukan per pegawai")


def _peringatan_tanpa_efek(hasil, d, kb, per_fakta):
    """Fakta rupiah per masa yang baru, bukan komponen, dan tidak dibaca aturan mana pun: muncul di hasil tetapi
    tidak mengubah satu angka pun. Lazim terjadi bila peraturan pemerintah yang memperkenalkan komponen gaji baru
    diunggah sebagai lapisan regulasi (komponen hanya boleh dideklarasikan lapisan perusahaan)."""
    komponen = {k.fakta for k in kb.komponen}
    dibaca = set()
    for a in kb.aturan:   # sama dengan graf dependensi engine: jika/maka/batas + nama fakta di argumen fungsi
        dibaca |= set(a.dependensi()) - {a.menghasilkan}
    penghasil = {}
    for a in d.get("aturan") or []:
        if a["lingkup"] == "masa" and a["tipe_hasil"] == "rupiah":
            penghasil.setdefault(a["menghasilkan"], []).append(a["id"])
    if d.get("lapisan") == "perusahaan":
        jalan = "daftarkan di komponen berkas ini"
    else:
        jalan = ("tulis tarif dan klasifikasi_wajib di berkas lapisan regulasi, lalu komponen dan aturannya di berkas "
                 "perusahaan terpisah")
    for f, ids in penghasil.items():
        if f in per_fakta or f.startswith("_") or f in komponen or f in dibaca:
            continue
        hasil["peringatan"].append(
            f"aturan {', '.join(ids)} menghasilkan fakta baru '{f}' yang bukan komponen dan tidak dibaca aturan mana pun, "
            f"sehingga tidak ikut bruto, PPh 21, maupun take home pay; {jalan}")


def _konstan_salah(teks):
    """Ekspresi tanpa nama, atribut, dan pemanggilan fungsi (jadi aman dinilai) yang bernilai salah."""
    try:
        return not eval(compile(teks, "<syarat konstan>", "eval"), {"__builtins__": {}})   # noqa: S307
    except Exception:  # noqa: BLE001 - mis. 1 / 0: bukan urusan peringatan ini
        return False


def _peringatan_syarat_konstan(hasil, d, kb):
    """Operand `and` tingkat atas di `jika` yang konstan (True, 1 == 1, 'x'): tidak menguji apa pun, tetapi ikut
    dihitung sebagai konjungsi (engine/ekspresi.py jumlah_konjungsi), jadi hanya menaikkan peringkat lex specialis."""
    per_id = {a.id: a for a in kb.aturan}
    for a in d.get("aturan") or []:
        x = per_id.get(a["id"])
        if x is None or x.jika is None:
            continue
        b = x.jika.pohon.body
        operan = b.values if isinstance(b, ast.BoolOp) and isinstance(b.op, ast.And) else [b]
        konstan = [ast.unparse(n) for n in operan
                   if not any(isinstance(t, (ast.Name, ast.Attribute, ast.Call)) for t in ast.walk(n))]
        salah = [k for k in konstan if _konstan_salah(k)]
        if salah:   # `False and ...`: bukan soal peringkat, aturannya mati
            hasil["peringatan"].append(
                f"aturan {a['id']}: `jika` memuat syarat konstan ({', '.join(salah)}) yang selalu salah, sehingga aturan ini "
                f"tidak akan pernah menyala; hapus syarat itu")
        elif konstan:
            hasil["peringatan"].append(
                f"aturan {a['id']}: `jika` memuat syarat konstan ({', '.join(konstan)}) yang tidak menguji apa pun; jumlah "
                f"konjungsi `and` menentukan lex specialis, sehingga syarat itu hanya menaikkan peringkat aturan; hapus "
                f"syarat itu, dan bila {a['id']} dimaksudkan mengganti aturan lain tulis menggantikan: [id aturan itu]")


def _peringatan_kalah(hasil, d, kb_dasar, jejak, jejak_gross_up):
    """Penggantian sebagian tanpa `menggantikan`: aturan rancangan yang pada sebagian instance simulasi kalah dari aturan
    KB aktif yang tidak disebutnya. Hanya untuk pemenang yang memang dapat dicabut lewat `menggantikan` (lapisan sama,
    bukan tafsir, mulai lebih awal); kalah antar-lapisan sudah dilaporkan sebagai lex superior / override sah."""
    lama = {x.id: x for x in kb_dasar.aturan}
    for a in d.get("aturan") or []:
        if a["sifat"] == "tafsir" or a.get("tafsir"):
            continue
        per_pemenang = {}
        for j in _pemakaian(a["id"], jejak, jejak_gross_up)[1]:
            per_pemenang.setdefault(j["aturan"], []).append(j)
        for id_y in sorted(per_pemenang):
            y = lama.get(id_y)
            if (y is None or id_y in (a.get("menggantikan") or []) or y.lapisan != d.get("lapisan") or y.sifat == "tafsir"
                    or y.tafsir or y.mulai >= _ke_tanggal(a["berlaku"]["mulai"])):
                continue
            alasan = list(dict.fromkeys(s for j in per_pemenang[id_y] for s in j["alasan"] or []))
            hasil["peringatan"].append(
                f"aturan {a['id']} kalah di {len(per_pemenang[id_y])} {_satuan(a)} dari {id_y} "
                f"({', '.join(alasan) or 'resolusi konflik'}); bila {a['id']} dimaksudkan mengganti {id_y}, tulis "
                f"menggantikan: [{id_y}]")


def _catat_hilang(hilang, kb, pengganti, nama, tahun, sebelum, sesudah):
    """Fakta yang punya nilai di `sebelum` dan tidak lagi dihasilkan di `sesudah`, di tempat yang sama, selama aturan
    pengganti berlaku: `jika` aturan pengganti lebih sempit daripada aturan yang dicabutnya. Engine tidak menebak nilai
    untuk kasus yang tidak tercakup. Pada rantai (Z mencabut X, X mencabut Y) yang dicatat hanya pengganti yang pada
    tanggal itu tidak sedang dicabut: X yang dicabut Z tidak ikut menentukan nilai, jadi bukan penyebabnya.
    hilang: {id pengganti: [(pegawai, tahun, bulan | None untuk fakta tahunan)]}."""
    akhir = max(sebelum["per_masa"])   # fakta tahunan dinilai pada tanggal 1 masa terakhir
    for f in sorted({x.menghasilkan for x in pengganti}):
        calon = [x for x in pengganti if x.menghasilkan == f]
        if calon[0].lingkup == "masa":
            tempat = [b for b, m in sebelum["per_masa"].items() if f in m and f not in sesudah["per_masa"].get(b, {})]
        else:
            tempat = [None] if f in sebelum["tahunan"] and f not in sesudah["tahunan"] else []
        for b in tempat:
            tgl = date(tahun, b or akhir, 1)
            berlaku = [x for x in calon if x.berlaku_pada(tgl)]
            teratas = [x for x in berlaku if not any(z.berlaku_pada(tgl) and x.id in z.menggantikan for z in kb.aturan)]
            for x in teratas or berlaku:
                if (nama, tahun, b) not in hilang.setdefault(x.id, []):
                    hilang[x.id].append((nama, tahun, b))


def _tanpa_cabut_sendiri(kb, ids):
    """KB pembanding untuk aturan rancangan yang mencabut aturan dari rancangan yang sama: fakta aturan lama itu belum
    ada di KB aktif, jadi simulasi-sebelum tidak dapat menunjukkan bahwa ia hilang. Di KB ini pencabutan di dalam
    rancangan ditiadakan (aturan lamanya tetap berlaku); pencabutan aturan KB aktif tidak diubah. None bila tidak ada."""
    ids = set(ids)
    if not any(a.id in ids and set(a.menggantikan) & ids for a in kb.aturan):
        return None
    return replace(kb, aturan=[replace(a, menggantikan=tuple(i for i in a.menggantikan if i not in ids)) if a.id in ids
                               else a for a in kb.aturan])


def _selalu_dihasilkan(kb, x):
    """Ada aturan lain tanpa `jika` untuk fakta yang sama, yang tidak dicabut aturan mana pun dan berlaku sepanjang masa
    berlaku x? Maka faktanya tetap dihasilkan pada kasus di luar `jika` x."""
    dicabut = {i for a in kb.aturan for i in a.menggantikan}
    return any(c.id != x.id and c.jika is None and not c.tafsir and c.id not in dicabut and c.mulai <= x.mulai
               and (c.sampai is None or (x.sampai is not None and c.sampai >= x.sampai))
               for c in kb.aturan_untuk(x.menghasilkan))


def _galat_hilang(hasil, kb, pengganti, hilang, hilang_gross_up, hilang_rancangan):
    """Galat untuk setiap aturan pengganti yang membuat faktanya hilang; contohnya pegawai contoh biasa lebih dulu.
    Bila fakta itu dibaca aturan lain, simulasinya gagal sebelum hasilnya dapat dibandingkan: galat simulasi itu diberi
    keterangan kemungkinan penyebabnya (peringatan), karena pesan engine tidak menyebut aturan pengganti.
    Simulasi hanya mencakup pegawai contoh: pengganti ber-`jika` yang lolos tetap diberi peringatan, karena pada kasus
    yang tidak disimulasikan (mis. metode pajak lain) faktanya dapat hilang tanpa terlihat di sini."""
    gagal = any(g.startswith("simulasi ") for g in hasil["galat"])
    for x in pengganti:
        lama = hilang.get(x.id, []) + hilang_gross_up.get(x.id, [])
        tempat = lama + [t for t in hilang_rancangan.get(x.id, []) if t not in lama]
        nama_lama = ", ".join(x.menggantikan)
        jalan = ((f"perluas atau hapus `jika` {x.id}, atau " if x.jika is not None else "")
                 + "tambahkan aturan untuk kasus yang tidak tercakup")
        if not tempat:
            if x.jika is None:
                continue
            pembaca = sorted(a.id for a in kb.aturan if x.menghasilkan in a.dependensi() and a.menghasilkan != x.menghasilkan)
            if gagal and pembaca:
                hasil["peringatan"].append(
                    f"kemungkinan penyebab simulasi gagal: aturan {x.id} menggantikan {nama_lama} tetapi "
                    f"ber-`jika`, sehingga pada kasus di luar `jika` itu fakta '{x.menghasilkan}' tidak lagi dihasilkan, "
                    f"padahal dibaca {', '.join(pembaca)}; {jalan}")
            elif not _selalu_dihasilkan(kb, x):
                hasil["peringatan"].append(
                    f"aturan {x.id} menggantikan {nama_lama} tetapi ber-`jika`: pada kasus di luar `jika` itu fakta "
                    f"'{x.menghasilkan}' tidak lagi dihasilkan. Simulasi hanya menguji pegawai contoh (metode gross dan "
                    f"gross-up), jadi kasus lain yang dicakup {nama_lama} (mis. metode pajak atau status pegawai lain) "
                    f"tidak teruji; pastikan `jika` {x.id} mencakup semuanya, atau hapus `jika` itu")
            continue
        nama, tahun, bulan = tempat[0]
        contoh = f"{nama} {tahun}" + (f" bulan {bulan}" if bulan else "")
        satuan = "masa" if x.lingkup == "masa" else "tahun"
        asal = "sebelumnya bernilai" if lama else "dihasilkan aturan yang digantikannya (dari rancangan ini juga)"
        hasil["galat"].append(
            f"aturan {x.id} menggantikan {nama_lama} tetapi tidak mencakup semua kasusnya: fakta "
            f"'{x.menghasilkan}' yang {asal} tidak lagi dihasilkan di {len(tempat)} {satuan} simulasi, mis. "
            f"{contoh}; {jalan}")


def validasi(teks_yaml, berkas_aktif=(), nama_berkas="rancangan.yaml", lapisan=None):
    """-> {ok, galat[], peringatan[], ringkasan{}, isi{}, masukan[], dampak[], perubahan[], belum_teruji[]}.

    Tidak pernah melempar. `isi` hanya terisi bila KB (aktif + rancangan) berhasil dimuat, karena halaman tinjau
    menyusun tabel dari strukturnya. `lapisan`: lapisan yang dipilih saat unggah (peringatan bila berbeda)."""
    hasil = {"ok": False, "galat": [], "peringatan": [], "ringkasan": {}, "isi": {}, "masukan": [], "dampak": [],
             "perubahan": [], "belum_teruji": []}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / nama_berkas
            p.write_text(str(teks_yaml), encoding="utf-8")
            _validasi(hasil, p, list(berkas_aktif), lapisan)
    except Exception as e:  # noqa: BLE001 - lapis terakhir: validasi tidak boleh membuang rancangan
        hasil["galat"].append(f"galat internal validasi: {_teks_galat(e)}")
    hasil["ok"] = not hasil["galat"]
    return hasil


def _validasi(hasil, p, berkas_aktif, lapisan):
    try:
        data = muat_yaml(p)
    except Exception as e:  # noqa: BLE001 - sintaks, float literal, kunci duplikat, tanggal mustahil (2026-02-30)
        hasil["galat"].append(f"YAML tidak dapat dibaca: {_teks_galat(e)}")
        return
    if not isinstance(data, dict):
        hasil["galat"].append("isi berkas harus berupa objek YAML (lapisan, aturan, ...)")
        return
    # struktur belum divalidasi skema: hitung dengan aman (mis. "aturan: 5")
    hasil["ringkasan"] = {"lapisan": _json(data.get("lapisan")),
                          **{k: _banyak(data.get(k)) for k in ("aturan", "komponen", "masukan", "parameter", "pembulatan",
                                                               "klasifikasi_wajib")}}
    if lapisan and data.get("lapisan") != lapisan:
        hasil["peringatan"].append(f"lapisan berkas '{data.get('lapisan')}' berbeda dengan lapisan yang dipilih saat "
                                   f"unggah '{lapisan}'")
    if not (data.get("aturan") or data.get("parameter") or data.get("klasifikasi_wajib")):
        hasil["galat"].append("rancangan tidak berisi aturan, parameter, atau klasifikasi apa pun")
        return

    dasar = [*BERKAS_PX, *berkas_aktif]
    try:
        kb_dasar = muat_kb(dasar)
    except Exception as e:  # noqa: BLE001
        hasil["galat"].append(f"KB aktif tidak dapat dimuat (bukan galat rancangan): {_teks_galat(e)}")
        return
    try:
        kb = muat_kb([*dasar, p])
    except Exception as e:  # noqa: BLE001 - skema, verifikasi statis, dan galat Python tak terduga dari isi berkas
        hasil["galat"].append(f"ditolak verifikasi KB: {_teks_galat(e)}")
        return
    d = _iso(data)   # sudah lolos skema: strukturnya dapat dipercaya mulai di sini
    hasil["isi"] = d   # untuk halaman tinjau: mencerminkan YAML yang sudah diubah admin

    semua = masukan_tambahan(kb)
    semua_dasar = masukan_tambahan(kb_dasar)
    masukan = masukan_tambahan(kb, hanya_berkas=[p.name])
    hasil["masukan"] = masukan
    # asisten lebih ketat dari engine: setiap masukan baru wajib dideklarasikan (label & tipe untuk form aplikasi)
    for m in masukan:
        if not m["dideklarasikan"]:
            hasil["galat"].append(f"hr('{m['kunci']}') dipakai aturan {m['aturan']} tetapi belum dideklarasikan di 'masukan'")
    efektif = {m["kunci"]: m for m in semua}
    rujuk = rujukan_masukan(kb)
    for e in d.get("masukan") or []:
        m = kb.masukan.get(e["kunci"])
        if m is not None and m.berkas == p.name and not m.wajib and efektif.get(e["kunci"], {}).get("wajib"):
            hasil["peringatan"].append(
                f"masukan '{e['kunci']}' dideklarasikan wajib: false tetapi tanpa bawaan, sehingga bila dikosongkan setiap "
                f"perhitungan gagal (DATA_KURANG); isi 'bawaan' atau ubah menjadi wajib: true")
        _peringatan_bawaan(hasil, e, rujuk)

    aturan_rancangan = d.get("aturan") or []
    ids = [a["id"] for a in aturan_rancangan]
    fakta = sorted({a["menghasilkan"] for a in aturan_rancangan})
    per_fakta = {}
    for a in kb_dasar.aturan:
        per_fakta.setdefault(a.menghasilkan, []).append(a)
    if d.get("lapisan") == "perusahaan":
        for f in fakta:
            if f not in per_fakta and not f.startswith(("px_", "_")):
                hasil["peringatan"].append(f"fakta baru '{f}' sebaiknya berawalan px_ (lapisan perusahaan)")
        for a in aturan_rancangan:
            lama = per_fakta.get(a["menghasilkan"]) or []
            if lama and all(x.lapisan == "regulasi" for x in lama):
                akibat = ("aturan regulasi wajib tetap dipakai (lex superior)" if any(x.sifat in ("wajib", "tafsir") for x in lama)
                          else "aturan perusahaan ini MENGGANTIKAN ketentuan regulasi tersebut (override sah)")
                hasil["peringatan"].append(
                    f"aturan perusahaan {a['id']} menulis fakta '{a['menghasilkan']}' yang di KB aktif hanya dihasilkan "
                    f"aturan regulasi ({', '.join(x.id for x in lama)}); {akibat}")

    _peringatan_tanpa_efek(hasil, d, kb, per_fakta)
    _peringatan_syarat_konstan(hasil, d, kb)

    _simulasi(hasil, d, p, kb_dasar, kb, semua_dasar, semua, masukan, ids, fakta)


def _simulasi(hasil, d, p, kb_dasar, kb, semua_dasar, semua, masukan, ids, fakta):
    """Dampak pada pegawai contoh di tahun-tahun yang tersentuh rancangan, lalu cakupan uji dan perubahan."""
    sendiri = {m["kunci"] for m in masukan} - {m["kunci"] for m in semua_dasar}
    daftar_tahun = tahun_simulasi(d)
    if not daftar_tahun:
        hasil["peringatan"].append(f"masa berlaku rancangan di luar jangkauan simulasi ({TAHUN_AWAL}-{TAHUN_LEWAT}); "
                                   "tidak ada simulasi yang dijalankan")
    jejak, jejak_gross_up, berhasil = [], [], 0
    pengganti = [a for a in kb.aturan if a.menggantikan and a.id in set(ids)]
    kb_tanpa = _tanpa_cabut_sendiri(kb, ids)   # pembanding kedua, hanya bila rancangan mencabut aturannya sendiri
    hilang, hilang_gross_up, hilang_rancangan = {}, {}, {}
    for tahun in daftar_tahun:
        contoh = nilai_contoh(semua, tahun)
        contoh_dasar = nilai_contoh(semua_dasar, tahun, contoh)
        gross_up = _simulasi_gross_up(hasil, tahun, kb_dasar, kb, semua_dasar, contoh_dasar, semua, contoh)
        if gross_up is not None:
            jejak_gross_up += gross_up[1]["jejak"]
            _catat_hilang(hilang_gross_up, kb, pengganti, "Karyawan A metode gross-up", tahun, *gross_up)
        for nama, buat in PROFIL:
            try:
                sebelum = hitung(isi_contoh(buat(tahun), semua_dasar, contoh_dasar), kb=kb_dasar)
            except Exception as e:  # noqa: BLE001 - KB aktif rusak: bukan kesalahan rancangan
                hasil["galat"].append(f"KB aktif tidak dapat dihitung: {nama} {tahun}{_galat_hitung(e)}")
                continue
            try:
                h = hitung(isi_contoh(buat(tahun), semua, contoh), kb=kb)
            except Exception as e:  # noqa: BLE001 - siklus, tipe, nama tak dikenal, overflow, ... dari rancangan
                hasil["galat"].append(f"simulasi {nama} {tahun} gagal{_galat_hitung(e)}")
                continue
            berhasil += 1
            jejak += h["jejak"]
            _catat_hilang(hilang, kb, pengganti, nama, tahun, sebelum, h)
            if kb_tanpa is not None:
                try:
                    tanpa = hitung(isi_contoh(buat(tahun), semua, contoh), kb=kb_tanpa)
                except Exception:  # noqa: BLE001 - pembanding saja: tanpa pencabutan itu rancangan boleh jadi tidak terhitung
                    tanpa = None
                if tanpa is not None:
                    _catat_hilang(hilang_rancangan, kb, pengganti, nama, tahun, tanpa, h)
            hasil["dampak"].append({"pegawai": f"{nama} (contoh)", "tahun": tahun,
                                    "nilai_contoh": {k: v for k, v in contoh.items() if k in sendiri},
                                    "sebelum": _ringkas(sebelum), "sesudah": _ringkas(h),
                                    "fakta_baru": _fakta_baru(h["jejak"], set(ids), fakta)})
            for pr in h["peringatan"]:
                if pr.get("kode") != "KONFLIK_WAJIB":
                    continue
                if set(pr.get("pemenang") or []) & set(ids):
                    _tambah(hasil["peringatan"], f"aturan regulasi rancangan {', '.join(sorted(set(pr['pemenang']) & set(ids)))} "
                                                 f"mengalahkan aturan perusahaan {', '.join(pr.get('ditolak') or [])} pada "
                                                 f"'{pr.get('fakta')}' (lex superior): kebijakan perusahaan itu tidak lagi dipakai")
                if pr.get("berkas") == p.name or set(pr.get("ditolak") or []) & set(ids):
                    _tambah(hasil["peringatan"],
                            f"konflik dengan aturan wajib regulasi pada {pr.get('fakta')}: aturan regulasi yang dipakai")

    if berhasil or not daftar_tahun:
        alasan_luar = "masa berlaku di luar jangkauan simulasi"
        hasil["belum_teruji"] = (_belum_teruji(ids, jejak + jejak_gross_up) if berhasil
                                 else [{"aturan": i, "alasan": alasan_luar} for i in ids])
        for b in hasil["belum_teruji"]:
            hasil["peringatan"].append(f"aturan {b['aturan']} belum teruji: {b['alasan']}")
    _galat_hilang(hasil, kb, pengganti, hilang, hilang_gross_up, hilang_rancangan)
    if berhasil:
        _peringatan_kalah(hasil, d, kb_dasar, jejak, jejak_gross_up)
    hasil["perubahan"] = _perubahan(d, kb_dasar, kb, jejak, jejak_gross_up)


def _simulasi_gross_up(hasil, tahun, kb_dasar, kb, semua_dasar, contoh_dasar, semua, contoh):
    """Karyawan A dengan metode gross-up. Aturan titik tetap (tunjangan pajak) tidak pernah menyala pada pegawai
    contoh yang bermetode gross, sehingga rancangan yang merusaknya lolos simulasi lalu menggagalkan setiap pegawai
    gross-up. Hasilnya tidak masuk tabel dampak; jejaknya dipakai untuk cakupan uji dan hasilnya untuk memeriksa fakta
    yang hilang. -> (hasil sebelum, hasil sesudah); None bila dilewati/gagal."""
    if not _dasar_bisa_gross_up(tahun):
        return None
    try:
        sebelum = hitung(_gross_up(isi_contoh(kasus_kar_a(tahun), semua_dasar, contoh_dasar)), kb=kb_dasar)
    except Exception as e:  # noqa: BLE001 - KB aktif rusak: bukan kesalahan rancangan
        hasil["galat"].append(f"KB aktif tidak dapat dihitung: Karyawan A {tahun} metode gross-up{_galat_hitung(e)}")
        return None
    try:
        return sebelum, hitung(_gross_up(isi_contoh(kasus_kar_a(tahun), semua, contoh)), kb=kb)
    except Exception as e:  # noqa: BLE001
        hasil["galat"].append(f"simulasi Karyawan A {tahun} metode gross-up gagal{_galat_hitung(e)}")
        return None


# ------------------------------------------------------------------------------------------- periksa KB aktif

def periksa_kb(berkas_tambahan=(), tahun=TAHUN_PERIKSA):
    """KB dasar + berkas tambahan dapat dimuat DAN menghitung Karyawan A (nilai contoh untuk setiap masukan
    tambahan), dengan metode gross dan, di tahun yang didukung KB dasar, gross-up? Memuat saja tidak cukup: fakta
    yang hilang karena berkas lain dinonaktifkan baru ketahuan saat graf per tahun dibangun.
    -> {ok, galat[], tahun[]}; tidak pernah melempar."""
    hasil = {"ok": False, "galat": [], "tahun": list(tahun)}
    try:
        try:
            kb = muat_kb([*BERKAS_PX, *berkas_tambahan])
        except Exception as e:  # noqa: BLE001
            hasil["galat"].append(f"KB tidak dapat dimuat: {_teks_galat(e)}")
            return hasil
        semua = masukan_tambahan(kb)
        for t in tahun:
            try:
                hitung(isi_contoh(kasus_kar_a(t), semua, nilai_contoh(semua, t)), kb=kb)
            except Exception as e:  # noqa: BLE001
                hasil["galat"].append(f"Karyawan A {t} tidak dapat dihitung{_galat_hitung(e)}")
                continue
            if not _dasar_bisa_gross_up(t):
                continue
            try:   # aturan titik tetap hanya menyala pada metode gross-up
                hitung(_gross_up(isi_contoh(kasus_kar_a(t), semua, nilai_contoh(semua, t))), kb=kb)
            except Exception as e:  # noqa: BLE001
                hasil["galat"].append(f"Karyawan A {t} metode gross-up tidak dapat dihitung{_galat_hitung(e)}")
    except Exception as e:  # noqa: BLE001
        hasil["galat"].append(f"galat internal pemeriksaan: {_teks_galat(e)}")
    finally:
        hasil["ok"] = not hasil["galat"]
    return hasil
