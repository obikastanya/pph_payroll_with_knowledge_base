"""E3 — skenario perubahan aturan (research_plan.md §11.2, Lampiran B, RQ3).

Untuk setiap skenario: KB_lama -> KB_baru (salinan), kode engine TIDAK diubah.
Metrik: baris KB berubah, berkas engine berubah (harus 0), impact precision/recall/F1 terhadap S*
(himpunan keluaran yang SEHARUSNYA berubah, diturunkan analitis dari aturan), dan regresi (tahun lain identik).

    env\\Scripts\\python.exe -m eksperimen.perubahan
"""
import copy
import csv
import difflib
import hashlib
import io
import json
import shutil
from datetime import date
from pathlib import Path

from eksperimen.e8_perusahaan_x import BERKAS_PX, kasus_kar_a
from eksperimen.mutasi import salin
from eksperimen.v1 import DIR_KANONIK
from eksperimen.v2 import konverter
from engine.kalkulator import hitung
from engine.kb import muat_kb

ROOT = Path(__file__).resolve().parents[1]


def _hash_engine():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / "engine").glob("*.py"))}


def _baris_berubah(dir_a, dir_b):
    n = 0
    for pa in sorted(dir_a.rglob("*")):
        if pa.is_file() and pa.suffix in (".yaml", ".csv"):
            pb = dir_b / pa.relative_to(dir_a)
            a, b = pa.read_text(encoding="utf-8").splitlines(), pb.read_text(encoding="utf-8").splitlines()
            n += sum(1 for d in difflib.ndiff(a, b) if d[:2] in ("+ ", "- "))
    return n


def _f1(s, s_bintang):
    tp = len(s & s_bintang)
    p = tp / len(s) if s else 1.0
    r = tp / len(s_bintang) if s_bintang else 1.0
    return {"|S|": len(s), "|S*|": len(s_bintang), "presisi": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else 0.0}


def _perbarui_hash(tmp, nama):
    p = tmp / "dataset" / "01_regulasi" / "tables" / f"{nama}.csv"
    m = tmp / "kb" / "regulasi" / "tabel_manifest.yaml"
    teks = m.read_text(encoding="utf-8").splitlines()
    i = next(j for j, l in enumerate(teks) if l.strip().endswith(f"/{nama}.csv"))
    teks[i + 1] = f"    sha256: {hashlib.sha256(p.read_bytes()).hexdigest()}"
    m.write_text("\n".join(teks) + "\n", encoding="utf-8")


def _tambah_baris(tmp, nama, baris_baru):
    p = tmp / "dataset" / "01_regulasi" / "tables" / f"{nama}.csv"
    baris = list(csv.DictReader(open(p, encoding="utf-8", newline="")))
    kolom = list(baris[0].keys())
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=kolom, lineterminator="\r\n" if b"\r\n" in p.read_bytes() else "\n")
    w.writeheader()
    w.writerows(baris + baris_baru)
    p.write_text(buf.getvalue(), encoding="utf-8", newline="")
    _perbarui_hash(tmp, nama)


def _sampel(tahun, n=240):
    hasil = []
    for k in konverter().muat():
        if k["metode"] == "gross" and k["pemberi_kerja"]["klu"] is None:
            k2 = copy.deepcopy(k)
            k2["tahun_pajak"] = tahun
            k2["id"] = f"{k['id']}@{tahun}"
            hasil.append(k2)
        if len(hasil) >= n:
            break
    return hasil


def _identik(kasus, kb_a, kb_b):
    return all(hitung(k, kb=kb_a)["per_masa"] == hitung(k, kb=kb_b)["per_masa"] and
               hitung(k, kb=kb_a)["tahunan"] == hitung(k, kb=kb_b)["tahunan"] for k in kasus)


# ------------------------------------------------------------------ C03: batas upah JP 2026 (regulasi nyata)

def c03():
    lama, baru = salin(), salin()
    p = lama / "kb" / "regulasi" / "parameter.yaml"
    s = p.read_text(encoding="utf-8")
    s = s.replace("    berlaku: {mulai: 2025-03-01, sampai: 2026-02-28}\n", "    berlaku: {mulai: 2025-03-01}\n")
    s = s.replace('''  - nama: jp_batas_upah
    nilai: 11086300
    berlaku: {mulai: 2026-03-01}
    sumber: "Surat BPJS TK B/1226/022026"
''', "")
    p.write_text(s, encoding="utf-8")
    kb_l = muat_kb(berkas_tambahan=BERKAS_PX, dir_regulasi=lama / "kb" / "regulasi")
    kb_b = muat_kb(berkas_tambahan=BERKAS_PX, dir_regulasi=baru / "kb" / "regulasi")
    s_set, s_bintang = set(), set()
    regresi = 0
    for gaji in (9_000_000, 10_500_000, 10_600_000, 11_000_000, 13_000_000, 20_000_000):
        for tahun in (2025, 2026):
            k = kasus_kar_a(tahun)
            k["data_hr"]["gaji_pokok"] = gaji
            a, b = hitung(k, kb=kb_l), hitung(k, kb=kb_b)
            for m in range(1, 13):
                if a["per_masa"][m]["px_iuran_jp_pg"] != b["per_masa"][m]["px_iuran_jp_pg"]:
                    s_set.add((gaji, tahun, m))
                upah = b["per_masa"][m]["px_gaji_berlaku"]
                if tahun == 2026 and m >= 3 and upah > 10_547_400:
                    s_bintang.add((gaji, tahun, m))
            if tahun == 2025 and (a["per_masa"] != b["per_masa"] or a["tahunan"] != b["tahunan"]):
                regresi += 1
    hasil = {"skenario": "C03 batas upah JP Maret 2026 (Rp11.086.300)", "baris_kb": _baris_berubah(lama, baru),
             "impact_px_iuran_jp_pg": _f1(s_set, s_bintang), "regresi_2025": regresi,
             "pembanding_B0_xlsx": "24 sel rumus menanam batas JP (temuan K-01)"}
    shutil.rmtree(lama), shutil.rmtree(baru)
    return hasil


# ------------------------------------------------------------------ C04: DTP berlaku surut (knowledge time)

def c04():
    k = json.loads((DIR_KANONIK / "PMK10-B-1.json").read_text(encoding="utf-8"))
    saat_itu = hitung(k, per_tanggal_kb=date(2025, 1, 31))
    seharusnya = hitung(k, per_tanggal_kb=date(2025, 2, 5))
    return {"skenario": "C04 PMK 10/2025 ditetapkan 4-2-2025, berlaku masa Januari 2025 (bitemporal)", "baris_kb": 0,
            "pph21_dtp_jan_dihitung_31jan": saat_itu["per_masa"][1].get("pph21_dtp"),
            "pph21_dtp_jan_seharusnya_5feb": seharusnya["per_masa"][1].get("pph21_dtp"),
            "pph21_jan_sama": saat_itu["per_masa"][1]["pph21"] == seharusnya["per_masa"][1]["pph21"],
            "koreksi_dtp_setahun": sum(m.get("pph21_dtp", 0) for m in seharusnya["per_masa"].values())}


# ------------------------------------------------------------------ C14: PTKP 2027 (HIPOTETIS)

def c14():
    lama, baru = salin(), salin()
    p = baru / "dataset" / "01_regulasi" / "tables" / "ptkp.csv"
    rows = list(csv.DictReader(open(p, encoding="utf-8", newline="")))
    baris_baru = []
    for r in rows:
        r2 = dict(r)
        r2["ptkp_setahun"] = str(int(r["ptkp_setahun"]) + 6_000_000)
        r2["berlaku"] = "2027-01-01 (HIPOTETIS uji E3)"
        baris_baru.append(r2)
    _tambah_baris(baru, "ptkp", baris_baru)
    kb_l, kb_b = muat_kb(dir_regulasi=lama / "kb" / "regulasi"), muat_kb(dir_regulasi=baru / "kb" / "regulasi")
    s_set, s_bintang = set(), set()
    for k in _sampel(2027):
        a, b = hitung(k, kb=kb_l), hitung(k, kb=kb_b)
        if a["tahunan"]["pph21_setahun"] != b["tahunan"]["pph21_setahun"]:
            s_set.add(k["id"])
        if a["tahunan"]["pkp"] > 0:          # S*: PPh setahun berubah tepat bila PKP lama > 0
            s_bintang.add(k["id"])
    hasil = {"skenario": "C14 PTKP naik Rp6 jt mulai 2027 (HIPOTETIS)", "baris_kb": _baris_berubah(lama, baru),
             "impact_pph21_setahun": _f1(s_set, s_bintang),
             "regresi_2023_2026_identik": _identik(_sampel(2024, 40) + _sampel(2026, 40) + _sampel(2023, 40), kb_l, kb_b)}
    shutil.rmtree(lama), shutil.rmtree(baru)
    return hasil


# ------------------------------------------------------------------ C15: revisi tabel TER 2027 (HIPOTETIS)

def c15():
    lama, baru = salin(), salin()
    p = baru / "dataset" / "01_regulasi" / "tables" / "ter_bulanan.csv"
    rows = list(csv.DictReader(open(p, encoding="utf-8", newline="")))
    diubah = {("A", 10), ("A", 11), ("A", 12)}
    baris_baru = []
    for r in rows:
        r2 = dict(r)
        r2["berlaku_mulai"] = "2027-01-01"
        if (r["kategori"], int(r["urutan"])) in diubah:
            from fractions import Fraction
            t = Fraction(r["tarif_desimal"]) - Fraction("0.005")
            r2["tarif_desimal"] = f"{t.numerator * (10 ** 4 // t.denominator) / 10 ** 4:.4f}"
            r2["tarif_persen"] = r2["tarif_desimal"]
        baris_baru.append(r2)
    _tambah_baris(baru, "ter_bulanan", baris_baru)
    kb_l, kb_b = muat_kb(dir_regulasi=lama / "kb" / "regulasi"), muat_kb(dir_regulasi=baru / "kb" / "regulasi")
    batas = {int(r["urutan"]): (int(r["batas_bawah"]), int(r["batas_atas"])) for r in rows if r["kategori"] == "A" and int(r["urutan"]) in (10, 11, 12)}
    s_set, s_bintang = set(), set()
    for k in _sampel(2027):
        a, b = hitung(k, kb=kb_l), hitung(k, kb=kb_b)
        for m, v in a["per_masa"].items():
            if "pph21_berjalan" not in v:
                continue
            if v["pph21_berjalan"] != b["per_masa"][m]["pph21_berjalan"]:
                s_set.add((k["id"], m))
            if v.get("kategori_ter") == "A" and any(lo < v["bruto"] <= hi for lo, hi in batas.values()) and v["pph21_berjalan"] > 0:
                s_bintang.add((k["id"], m))
    hasil = {"skenario": "C15 tabel TER 2027: kategori A lapisan 10-12 turun 0,5% (HIPOTETIS)", "baris_kb": _baris_berubah(lama, baru),
             "impact_pph21_berjalan": _f1(s_set, s_bintang),
             "regresi_2023_2026_identik": _identik(_sampel(2024, 40) + _sampel(2025, 40) + _sampel(2026, 40), kb_l, kb_b)}
    shutil.rmtree(lama), shutil.rmtree(baru)
    return hasil


def jalankan():
    sebelum = _hash_engine()
    hasil = [c03(), c04(), c14(), c15()]
    for h in hasil:
        h["berkas_engine_berubah"] = sum(1 for k, v in _hash_engine().items() if sebelum.get(k) != v)
    return hasil


if __name__ == "__main__":
    hasil = jalankan()
    (ROOT / "eksperimen" / "hasil").mkdir(exist_ok=True)
    (ROOT / "eksperimen" / "hasil" / "perubahan.json").write_text(json.dumps(hasil, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(hasil, indent=1, ensure_ascii=False))
