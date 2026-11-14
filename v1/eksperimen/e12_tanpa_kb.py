"""E12: kalkulator payroll DENGAN KB (engine + lapisan Perusahaan X) vs TANPA KB (B2 hard-coded + B1).

Dipakai oleh tes (tests/test_b2_payroll.py) dan tanda "cek silang" di UI. Selisih dinyatakan SAH hanya bila
terjelaskan oleh adjudikasi A-02 (eksperimen/adjudikasi.md): gross-up punya lebih dari satu titik tetap integer,
KB memberi peringatan GROSSUP_GANDA, dan nilai tanpa KB sama dengan salah satu titik tetap yang dilaporkan KB.

    env\\Scripts\\python.exe -m eksperimen.e12_tanpa_kb
"""
import json
from pathlib import Path

from baselines.b2_payroll_hardcoded.payroll_b2 import hitung as hitung_tanpa_kb
from engine.kalkulator import hitung

ROOT = Path(__file__).resolve().parents[1]
BERKAS_PX = [ROOT / "kb" / "perusahaan" / "perusahaan_x.yaml"]
SINTETIS = ROOT / "dataset" / "08_pegawai_sintetis" / "pegawai_sintetis.json"

FAKTA_MASA = ["px_gaji", "px_tunjangan", "px_premi_jkk", "px_premi_jkm", "px_premi_kes", "px_premi_jht_pk", "px_premi_jp_pk",
              "px_iuran_jht_pg", "px_iuran_jp_pg", "px_iuran_kes_pg", "px_thr", "px_kompensasi", "px_ota", "px_lembur",
              "px_komisi", "px_penghasilan_tunai", "px_thp", "bruto", "kategori_ter", "tarif_ter", "pph21", "pph21_dtp",
              "tunjangan_pajak"]
NOL_SAMA_DENGAN_KOSONG = {"px_thr", "pph21_dtp", "tunjangan_pajak"}   # representasi: KB tidak membuat fakta, B1 menulis 0
FAKTA_GROSSUP = {"tunjangan_pajak", "pph21", "bruto", "px_thp", "pph21_setahun", "pph21_dipotong_sebelumnya",
                 "pph21_masa_terakhir", "pkp", "bruto_setahun", "neto_setahun", "biaya_jabatan", "lebih_bayar_dikembalikan",
                 "pph21_disetahunkan", "neto_disetahunkan"}


def hitung_kb(kasus):
    return hitung(kasus, berkas_perusahaan=BERKAS_PX if kasus.get("data_hr") else ())


def selisih(h_kb, h_tanpa):
    """[(bulan|None, fakta, nilai_kb, nilai_tanpa_kb)] untuk fakta yang dihasilkan kedua mesin."""
    beda = []
    for b in sorted(set(h_kb["per_masa"]) | set(h_tanpa["per_masa"]), key=lambda x: (x is None, x or 0)):
        a, c = h_kb["per_masa"].get(b) or {}, h_tanpa["per_masa"].get(b) or {}
        for f in FAKTA_MASA:
            va, vc = a.get(f), c.get(f)
            if f in NOL_SAMA_DENGAN_KOSONG:
                va, vc = va or 0, vc or 0
            if va is None or vc is None:
                continue
            if va != vc:
                beda.append((b, f, va, vc))
    for f in sorted(set(h_kb["tahunan"]) & set(h_tanpa["tahunan"])):
        if h_kb["tahunan"][f] != h_tanpa["tahunan"][f]:
            beda.append((None, f, h_kb["tahunan"][f], h_tanpa["tahunan"][f]))
    return beda


def teradjudikasi(beda, h_kb):
    """True bila setiap selisih terjelaskan oleh titik tetap gross-up ganda yang dilaporkan KB (A-02)."""
    ganda = [p for p in h_kb["peringatan"] if p.get("kode") == "GROSSUP_GANDA"]
    if not beda or not ganda:
        return not beda
    if any(f not in FAKTA_GROSSUP for _, f, _, _ in beda):
        return False
    titik = {(p["bulan"], v) for p in ganda for v in (p["terkecil"], p["terbesar"])}
    for b, f, _, vc in beda:
        if f == "tunjangan_pajak":
            bulan_kunci = None if b is None else b
            if (bulan_kunci, vc) not in titik and (None, vc) not in titik:
                return False
    return True


def cek_silang(kasus):
    """-> dict(status: 'identik'|'sah_titik_tetap_ganda'|'berbeda', selisih: [...])."""
    h_kb, h_tanpa = hitung_kb(kasus), hitung_tanpa_kb(kasus)
    beda = selisih(h_kb, h_tanpa)
    if not beda:
        status = "identik"
    elif teradjudikasi(beda, h_kb):
        status = "sah_titik_tetap_ganda"
    else:
        status = "berbeda"
    return {"status": status, "selisih": beda, "kb": h_kb, "tanpa_kb": h_tanpa}


def kasus_uji():
    from eksperimen.e8_perusahaan_x import kasus_kar_a
    for t in (2023, 2024, 2025, 2026):
        yield f"KAR-A-{t}", kasus_kar_a(t)
    for d in json.loads(SINTETIS.read_text(encoding="utf-8")):
        yield d["id"], d["kasus"]


if __name__ == "__main__":
    for nama, k in kasus_uji():
        r = cek_silang(k)
        print(f"{nama:12} {r['status']:24} {len(r['selisih'])} selisih")
