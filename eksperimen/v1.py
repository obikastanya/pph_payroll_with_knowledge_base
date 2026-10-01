"""Runner V1 — kasus uji resmi kanonik vs sebuah sistem (research_plan.md §9.1, §11.1).

Protokol per harapan:
  - harapan biasa      : hasil default == nilai tercetak               -> cocok
  - harapan erratum    : hasil default == terkoreksi (dan != tercetak) -> cocok_terkoreksi
  - harapan tafsir     : hasil dengan varian tercatat == nilai tercetak -> cocok_tafsir
                         (selisih hasil default dicatat sebagai lebar rentang tafsir)
  - lainnya            : SELISIH (tak terjelaskan) / TIDAK_DIHASILKAN
Kriteria lulus: STJ (SELISIH + TIDAK_DIHASILKAN) = 0.

    env\\Scripts\\python.exe -m eksperimen.v1 b1      # ringkasan untuk baseline B1
"""
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR_KANONIK = ROOT / "dataset" / "07_kasus_uji_resmi" / "kanonik"


def muat_kasus():
    for f in sorted(DIR_KANONIK.glob("*.json")):
        if f.name == "indeks.json":
            continue
        yield json.loads(f.read_text(encoding="utf-8"))


def _setara(aktual, harapan):
    if aktual is None:
        return False
    if isinstance(harapan, str) and "/" in harapan or isinstance(aktual, Fraction):
        try:
            return Fraction(aktual) == Fraction(harapan)
        except (TypeError, ValueError):
            return False
    return aktual == harapan


def bandingkan(kasus, hitung, fakta):
    """hitung(kasus, varian) -> hasil; fakta(hasil, nama, bulan) -> nilai."""
    hasil = hitung(kasus, None)
    keluaran = []
    cache = {}
    for h in kasus["harapan"]:
        a = fakta(hasil, h["fakta"], h["bulan"])
        rec = {"kasus": kasus["id"], "fakta": h["fakta"], "bulan": h["bulan"], "harapan": h["nilai"],
               "aktual": a if not isinstance(a, Fraction) else str(a)}
        if "tafsir" in h:
            kunci = json.dumps(h["tafsir"], sort_keys=True)
            if kunci not in cache:
                cache[kunci] = hitung(kasus, h["tafsir"])
            av = fakta(cache[kunci], h["fakta"], h["bulan"])
            rec["aktual_varian"] = av if not isinstance(av, Fraction) else str(av)
            rec["status"] = "cocok_tafsir" if _setara(av, h["nilai"]) else "SELISIH"
            rec["rentang_tafsir"] = None if a is None or av is None or isinstance(a, (str, bool)) \
                else abs(Fraction(a) - Fraction(av))
        elif "terkoreksi" in h:
            rec["terkoreksi"] = h["terkoreksi"]
            rec["status"] = "cocok_terkoreksi" if _setara(a, h["terkoreksi"]) else "SELISIH"
        elif a is None:
            rec["status"] = "TIDAK_DIHASILKAN"
        else:
            rec["status"] = "cocok" if _setara(a, h["nilai"]) else "SELISIH"
        keluaran.append(rec)
    return keluaran


def jalankan(hitung, fakta):
    semua = []
    for k in muat_kasus():
        try:
            semua += bandingkan(k, hitung, fakta)
        except Exception as e:  # kasus gagal dihitung = semua harapannya tak terjelaskan
            semua += [{"kasus": k["id"], "fakta": h["fakta"], "bulan": h["bulan"], "harapan": h["nilai"],
                       "aktual": None, "status": "TIDAK_DIHASILKAN", "galat": f"{type(e).__name__}: {e}"}
                      for h in k["harapan"]]
    return semua


def ringkas(hasil):
    c = Counter(r["status"] for r in hasil)
    stj = c["SELISIH"] + c["TIDAK_DIHASILKAN"]
    return c, stj


def _sistem(nama):
    if nama == "b1":
        from baselines.b1_hardcoded.pph21_b1 import fakta, hitung
        return hitung, fakta
    if nama == "kb":
        from engine.kalkulator import fakta, hitung
        return hitung, fakta
    raise SystemExit(f"sistem tidak dikenal: {nama}")


if __name__ == "__main__":
    nama = sys.argv[1] if len(sys.argv) > 1 else "b1"
    hasil = jalankan(*_sistem(nama))
    c, stj = ringkas(hasil)
    print(f"[{nama}] {len(hasil)} harapan | " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())) + f" | STJ={stj}")
    per_kasus = Counter(r["kasus"] for r in hasil if r["status"] in ("SELISIH", "TIDAK_DIHASILKAN"))
    for kasus, n in sorted(per_kasus.items()):
        contoh = [r for r in hasil if r["kasus"] == kasus and r["status"] in ("SELISIH", "TIDAK_DIHASILKAN")][:4]
        print(f"  {kasus}: {n} | " + "; ".join(
            f"{r['fakta']}[{r['bulan']}] harap={r.get('terkoreksi', r['harapan'])} aktual={r.get('aktual_varian', r['aktual'])}"
            + (f" ({r['galat']})" if r.get("galat") else "") for r in contoh))
