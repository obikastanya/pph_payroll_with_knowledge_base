"""Independent arithmetic check of GT3 cases: python check_gt3.py [--tulis]

Two checks, written separately from calculator.py (no import of it):
 1. every langkah with a numeric formula is re-evaluated with exact fractions;
 2. headline results (bruto, TER category/rate, PPh per masa, DTP, annual recalculation)
    are recomputed from `input` and the CSV tables with a second, simpler implementation.
With --tulis the result is written into each case's `cek_aritmetika` fields.
"""
import csv
import glob
import json
import math
import os
import re
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
CASES_DIR = os.path.dirname(HERE)
TABLES = os.path.abspath(os.path.join(CASES_DIR, "..", "..", "01_regulasi", "tables"))

NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)")


def ev(formula):
    expr = NUM.sub(lambda mo: f"Fr('{mo.group(1)}')", formula)
    return eval(expr, {"__builtins__": {}}, {"Fr": Fr, "floor": math.floor, "min": min, "max": max})


def rows(name):
    with open(os.path.join(TABLES, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


TER = rows("ter_bulanan.csv")
PTKP = {r["status"]: (int(r["ptkp_setahun"]), r["kategori_ter"]) for r in rows("ptkp.csv")}
P17 = [(int(r["pkp_batas_bawah"]), int(r["pkp_batas_atas"] or 10 ** 15), Fr(r["tarif_persen"]) / 100)
       for r in rows("tarif_pasal17.csv") if r["rezim"] == "UU HPP"]
KLU = rows("klu_dtp.csv")


def ter_rate(cat, b):
    for r in TER:
        if r["kategori"] == cat:
            lo, hi = int(r["batas_bawah"]), int(r["batas_atas"] or 10 ** 15)
            if lo < b <= hi or (lo == 0 and b == 0):
                return Fr(r["tarif_persen"]) / 100
    raise ValueError


def tax17(pkp):
    return sum(rate * max(0, min(pkp, hi) - lo) for lo, hi, rate in P17)


def pkp_of(neto, ptkp):
    return max(0, math.floor(Fr(neto - ptkp) / 1000) * 1000)


def jp_cap(y, m):
    for (yy, mm), cap in [((2026, 3), 11086300), ((2025, 3), 10547400), ((2024, 3), 10042300), ((2023, 3), 9559600)]:
        if (y, m) >= (yy, mm):
            return cap
    return 9077600


JKK = {"sangat rendah": Fr("0.0024"), "rendah": Fr("0.0054"), "sedang": Fr("0.0089"), "tinggi": Fr("0.0127"), "sangat tinggi": Fr("0.0174")}


class Check:
    def __init__(self, cid):
        self.cid, self.n, self.bad = cid, 0, []

    def eq(self, item, got, exp):  # got = nilai di berkas, exp = hasil hitung ulang
        self.n += 1
        if Fr(str(got)) != Fr(str(exp)):
            self.bad.append(f"{item}: berkas {got} vs hitung ulang {exp}")


def natura(y, m, k, cum):
    """Return (regular taxable, irregular taxable, cum)."""
    reg = irr = 0
    if (y, m) < (2023, 7):
        # tidak dipotong pemberi kerja, tetapi bingkisan tetap dihitung dalam batas Rp3 juta setahun
        return 0, 0, cum + k.get("bingkisan_non_hari_raya", 0)
    if k.get("natura_rumah_individual"):
        reg += max(0, k["natura_rumah_individual"] - 2000000)
    if k.get("kupon_makan_dinas_luar"):
        reg += max(0, k["kupon_makan_dinas_luar"] - 2000000)
    if k.get("bingkisan_non_hari_raya"):
        new = cum + k["bingkisan_non_hari_raya"]
        irr += max(0, new - 3000000) - max(0, cum - 3000000)
        cum = new
    return reg, irr, cum


def recompute(case, ck):
    y = case["tahun_pajak"]
    inp = case["input"]
    exp = case["expected"]
    pm = {r["bulan"]: r for r in exp["per_masa"]}
    ptkp_val = 54000000 if inp["karyawati_kawin_suami_berpenghasilan"] else PTKP[inp["status_ptkp"]][0]
    cat = "A" if inp["karyawati_kawin_suami_berpenghasilan"] else PTKP[inp["status_ptkp"]][1]
    metode = inp["metode"]
    masa = inp["masa"]
    months = [x["bulan"] for x in masa]
    last = (inp["bulan_keluar"] or 12) if case["stratum"] == "tahunan" else None
    start = inp["bulan_masuk"] or 1
    sek = inp["sektor"]
    # DTP eligibility (independent)
    dtp_emp = None
    if y in (2025, 2026):
        if "info_dtp" in inp:
            fixed = inp["info_dtp"]["penghasilan_tetap_teratur_bulan_ukur"]
        else:
            k0 = masa[0]["komponen"]
            fixed = k0.get("gaji", 0) + k0.get("tunjangan_tetap", 0)
        dtp_emp = fixed <= 10000000

    def listed(m):
        ym = f"{y}-{m:02d}"
        return any(r["klu"] == sek["klu"] and r["masa_mulai"] <= ym <= r["masa_akhir"] for r in KLU)

    cum = 0
    brutos, iur, zak, prior = [], 0, 0, 0
    any_dtp = False
    for x in masa:
        m, k = x["bulan"], x["komponen"]
        r = pm[m]
        W = k.get("gaji", 0) + k.get("tunjangan_tetap", 0)
        # component derivation
        rate = JKK[sek["kelompok_risiko_jkk"]]
        if sek["padat_karya_pp7_2025"] and (2025, 2) <= (y, m) <= (2026, 1):
            rate /= 2
        ck.eq(f"{m}: premi JKK", k["premi_jkk"], rate * W)
        ck.eq(f"{m}: premi JKM", k["premi_jkm"], Fr("0.003") * W)
        ck.eq(f"{m}: iuran JHT pegawai", k["iuran_jht_pegawai"], Fr("0.02") * W)
        ck.eq(f"{m}: iuran JP pegawai", k["iuran_jp_pegawai"], Fr("0.01") * min(W, jp_cap(y, m)))
        ck.eq(f"{m}: premi BPJS Kes PK", k["premi_bpjs_kesehatan_pemberi_kerja"], Fr("0.04") * min(W, 12000000))
        nreg, nirr, cum = natura(y, m, k, cum)
        reg = sum(k.get(c, 0) for c in ("gaji", "tunjangan_tetap", "lembur", "premi_jkk", "premi_jkm",
                                       "premi_bpjs_kesehatan_pemberi_kerja")) + nreg
        irr = k.get("thr", 0) + k.get("bonus", 0) + nirr
        i_m = k["iuran_jht_pegawai"] + k["iuran_jp_pegawai"]
        T = r.get("tunjangan_pajak", 0) if metode == "gross_up" else (r.get("pph21_ditanggung_pemberi_kerja", 0) if (metode == "ditanggung" and y >= 2024) else 0)
        b = reg + irr + T
        ck.eq(f"{m}: bruto", r["bruto"], b)
        if m != last:
            if y >= 2024:
                ck.eq(f"{m}: kategori", 1, int(r["kategori_ter"] == cat))
                rt = ter_rate(cat, b)
                ck.eq(f"{m}: tarif TER", r["tarif_ter"], rt)
                # tafsir K1: s.d. 2024 dibuang desimalnya; mulai Masa Januari 2025 pembulatan 0,50 ke atas
                p = math.floor(rt * b) if y <= 2024 else math.floor(rt * b + Fr(1, 2))
                if T:
                    ck.eq(f"{m}: titik tetap T = PPh", T, p)
            else:
                n = 13 - start
                regT = reg + T

                def ptax(rg):
                    bj = min(Fr(5, 100) * rg, 500000)
                    return tax17(pkp_of(n * (rg - bj - i_m), ptkp_val))
                t_reg = ptax(regT)
                p = math.floor(Fr(t_reg) / n)
                if irr:
                    ba = n * regT + irr
                    bja = min(Fr(5, 100) * ba, 500000 * n)
                    t2 = tax17(pkp_of(ba - bja - n * i_m, ptkp_val))
                    p += int(t2 - t_reg)
                if T:
                    ck.eq(f"{m}: titik tetap tunjangan pajak 2023", T, p)
            ck.eq(f"{m}: PPh 21", r["pph21"], p)
            elig = bool(dtp_emp) and listed(m)
            any_dtp |= elig
            ck.eq(f"{m}: DTP", r["pph21_dtp"], p if elig else 0)
            ck.eq(f"{m}: dipotong", r["pph21_dipotong"], 0 if elig else p)
            prior += p
        else:
            nm = len(brutos) + 1
            tb = sum(brutos) + b
            bj = min(Fr(5, 100) * tb, 500000 * nm)
            iur_t = iur + i_m
            zak_t = (zak + k.get("zakat", 0)) if y >= 2024 else 0
            neto = tb - bj - iur_t - zak_t
            pk = pkp_of(neto, ptkp_val)
            tx = tax17(pk)
            akhir = tx - prior
            t = exp["tahunan"]
            ck.eq("bruto setahun", t["bruto_setahun"], tb)
            ck.eq("biaya jabatan", t["biaya_jabatan"], bj)
            ck.eq("iuran", t["iuran_jht_jp_pegawai"], iur_t)
            ck.eq("zakat", t["zakat"], zak_t)
            ck.eq("neto", t["neto_setahun"], neto)
            ck.eq("ptkp", t["ptkp"], ptkp_val)
            ck.eq("pkp", t["pkp"], pk)
            ck.eq("pph setahun", t["pph21_setahun"], tx)
            ck.eq("dipotong sebelumnya", t["pph21_dipotong_sebelumnya"], prior)
            ck.eq("pph masa terakhir", r["pph21"], akhir)
            ck.eq("pph masa terakhir (tahunan)", t["pph21_masa_terakhir"], akhir)
            if T and metode in ("gross_up", "ditanggung"):
                ck.eq("titik tetap T masa terakhir", T, akhir)
            elig = bool(dtp_emp) and listed(m)
            any_dtp |= elig
            ck.eq("DTP masa terakhir", r["pph21_dtp"], akhir if elig else 0)
            ck.eq("dipotong masa terakhir", r["pph21_dipotong"], 0 if elig else akhir)
            ck.eq("dikembalikan ke pegawai", t["kelebihan_dikembalikan_ke_pegawai"], (-akhir if (akhir < 0 and not elig) else 0))
        brutos.append(b)
        iur += i_m
        zak += k.get("zakat", 0)
    if y in (2025, 2026):
        ck.eq("berhak_dtp", int(exp["berhak_dtp"]), int(any_dtp))


def main():
    write = "--tulis" in sys.argv
    tot_steps = tot_bad_steps = tot_rc = tot_bad_rc = 0
    report = []
    for path in sorted(glob.glob(os.path.join(CASES_DIR, "GT3-*.json"))):
        with open(path, encoding="utf-8") as f:
            case = json.load(f)
        st = Check(case["id"])
        for s in case["langkah"]:
            if s["formula"] is None:
                continue
            st.eq(f"langkah {s['no']}", s["value"], ev(s["formula"]))
        rc = Check(case["id"])
        recompute(case, rc)
        tot_steps += st.n
        tot_bad_steps += len(st.bad)
        tot_rc += rc.n
        tot_bad_rc += len(rc.bad)
        status = "cocok" if not (st.bad or rc.bad) else "; ".join(st.bad + rc.bad)
        report.append((case["id"], st.n, len(st.bad), rc.n, len(rc.bad), status))
        if write:
            case["cek_aritmetika"] = status
            case["cek_aritmetika_rinci"] = {
                "alat": "tools/check_gt3.py (pecahan eksak, terpisah dari tools/calculator.py)",
                "langkah_numerik_dievaluasi_ulang": st.n, "langkah_tidak_cocok": len(st.bad),
                "hitung_ulang_independen_item": rc.n, "hitung_ulang_independen_tidak_cocok": len(rc.bad),
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(case, f, ensure_ascii=False, indent=2)
    for r in report:
        if r[2] or r[4]:
            print(r)
    print(f"kasus={len(report)} langkah_dicek={tot_steps} langkah_tidak_cocok={tot_bad_steps} "
          f"hitung_ulang_item={tot_rc} hitung_ulang_tidak_cocok={tot_bad_rc}")


if __name__ == "__main__":
    main()
