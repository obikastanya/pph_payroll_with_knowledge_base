"""V2 — differential testing KB vs B1 pada kasus sintetis (research_plan.md §9.2, E2).

Membandingkan setiap fakta kanonik per masa & per tahun. Selisih tidak diputuskan dengan voting:
setiap kelas selisih dicatat untuk diadjudikasi terhadap pasal (eksperimen/adjudikasi.md).

    env\\Scripts\\python.exe -m eksperimen.v2
"""
import importlib.util
from collections import Counter
from fractions import Fraction
from pathlib import Path

from baselines.b1_hardcoded import pph21_b1
from engine import kalkulator

ROOT = Path(__file__).resolve().parents[1]


def konverter():
    spec = importlib.util.spec_from_file_location("ke_kanonik", ROOT / "dataset/06_kasus_uji_sintetis/ke_kanonik.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

FAKTA_MASA = ["bruto", "kategori_ter", "tarif_ter", "pph21", "pph21_dtp", "tunjangan_pajak",
              "biaya_jabatan_bulanan", "neto_sebulan", "pkp_bulanan", "pph21_teratur"]
FAKTA_TAHUN = ["bruto_setahun", "biaya_jabatan", "iuran_pengurang", "zakat", "neto_setahun", "ptkp", "pkp",
               "pph21_setahun", "pph21_dipotong_sebelumnya", "pph21_masa_terakhir", "lebih_bayar_dikembalikan",
               "berhak_dtp"]


def _sama(a, b):
    if a is None or b is None:
        return a is b
    try:
        return Fraction(a) == Fraction(b)
    except (TypeError, ValueError):
        return a == b


def jalankan(kasus_iter, maks=None):
    selisih, galat, jumlah = [], [], 0
    satu_sisi = Counter()
    for i, k in enumerate(kasus_iter):
        if maks and i >= maks:
            break
        jumlah += 1
        hasil = {}
        for nama, fn in (("kb", kalkulator.hitung), ("b1", pph21_b1.hitung)):
            try:
                hasil[nama] = fn(k, None)
            except Exception as e:  # catat sebagai galat sistem
                hasil[nama] = None
                galat.append({"kasus": k["id"], "strata": k["strata"], "sistem": nama, "galat": f"{type(e).__name__}: {e}"})
        if not hasil["kb"] or not hasil["b1"]:
            continue
        for b in sorted(hasil["kb"]["per_masa"]):
            for f in FAKTA_MASA:
                a, c = hasil["kb"]["per_masa"][b].get(f), hasil["b1"]["per_masa"].get(b, {}).get(f)
                if a is None or c is None:
                    if (a is None) != (c is None):
                        satu_sisi[(f, "kb" if a is not None else "b1")] += 1
                    continue
                if not _sama(a, c):
                    selisih.append({"kasus": k["id"], "strata": k["strata"], "fakta": f, "bulan": b, "kb": a, "b1": c})
        for f in FAKTA_TAHUN:
            a, c = hasil["kb"]["tahunan"].get(f), hasil["b1"]["tahunan"].get(f)
            if a is None or c is None:
                if (a is None) != (c is None):
                    satu_sisi[(f, "kb" if a is not None else "b1")] += 1
                continue
            if not _sama(a, c):
                selisih.append({"kasus": k["id"], "strata": k["strata"], "fakta": f, "bulan": None, "kb": a, "b1": c})
    jalankan.satu_sisi = satu_sisi
    return jumlah, selisih, galat


if __name__ == "__main__":
    n, selisih, galat = jalankan(konverter().muat())
    print(f"{n} kasus | selisih={len(selisih)} | galat={len(galat)} | fakta satu sisi: {dict(jalankan.satu_sisi)}")
    for (sistem, pesan), c in Counter((g["sistem"], g["galat"][:110]) for g in galat).most_common(10):
        print(f"  GALAT {sistem} x{c}: {pesan}")
    kelas = Counter((s["fakta"], s["strata"]) for s in selisih)
    for (f, st), c in kelas.most_common(25):
        contoh = next(s for s in selisih if s["fakta"] == f and s["strata"] == st)
        print(f"  {f:28} {st:18} x{c:4} | contoh {contoh['kasus']}[{contoh['bulan']}] kb={contoh['kb']} b1={contoh['b1']}")
