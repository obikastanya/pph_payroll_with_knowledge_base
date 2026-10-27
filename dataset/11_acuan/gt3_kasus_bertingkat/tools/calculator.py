"""GT3 calculator: turns a case spec into input, expected results and cited steps.

Every numeric step carries a `formula` string made only of numbers, + - * /, floor(),
min() and max(), so check_gt3.py can re-evaluate it independently with exact fractions.
"""
import math
from fractions import Fraction as F

from rules import (SRC, JKK_NORMAL, dec, floor_thousand, jkk_relief_active, jp_cap,
                    klu_info, pasal17_layers, pct, ptkp, round_formula, round_pph, round_src, rp,
                    ter_category, ter_lookup, ter_page)

REGULAR_KEYS = ["gaji", "tunjangan_tetap", "lembur"]
IRREGULAR_KEYS = ["thr", "bonus"]
NATURA_KEYS = ["natura_rumah_individual", "kupon_makan_dinas_luar",
               "bingkisan_non_hari_raya", "kendaraan_dinas"]
MONTH_NAMES = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
         "September", "Oktober", "November", "Desember"]


def _int(x, what):
    x = F(x)
    assert x.denominator == 1, f"{what} tidak bulat: {x}"
    return int(x)


def fsum(vals):
    vals = [v for v in vals if v != 0]
    return " + ".join(str(int(v)) for v in vals) if vals else "0"


class Builder:
    def __init__(self, spec):
        self.s = spec
        self.year = spec["tahun"]
        self.status = spec["status"]
        self.steps = []
        self.ter = self.year >= 2024
        self.metode = spec["metode"]

    # ------------------------------------------------------------ steps
    def step(self, text, formula, value, sumber):
        if isinstance(value, F):
            value = int(value) if value.denominator == 1 else float(dec(value))
        self.steps.append({"no": len(self.steps) + 1, "text": text, "formula": formula,
                           "value": value, "sumber": sumber})
        return value

    # ------------------------------------------------------------ facts
    def ptkp_value(self):
        if self.s.get("karyawati_kawin"):
            return ptkp("TK/0")
        return ptkp(self.status)

    def ptkp_status_for_category(self):
        return "TK/0" if self.s.get("karyawati_kawin") else self.status

    def months(self):
        return sorted(self.s["masa"].keys())

    def last_month(self):
        if self.s["stratum"] != "tahunan":
            return None
        return self.s.get("bulan_keluar") or 12

    def n_factor_2023(self):
        start = self.s.get("bulan_masuk") or 1
        return 13 - start

    def dtp_employee(self):
        """Employee criterion (fixed regular gross in January / first month <= Rp10 juta).
        Returns (ok, fixed, bulan_ukur) or None outside 2025-2026."""
        y = self.year
        if y not in (2025, 2026):
            return None
        first = self.s.get("bulan_masuk") or 1
        if "dtp_tetap_bulan_ukur" in self.s:
            fixed = self.s["dtp_tetap_bulan_ukur"]
        else:
            mfirst = self.s["masa"].get(first) or self.s["masa"][min(self.s["masa"])]
            fixed = mfirst.get("gaji", 0) + mfirst.get("tunjangan_tetap", 0)
        bulan_ukur = f"Januari {y}" if first == 1 else f"bulan pertama bekerja ({MONTH_NAMES[first]} {y})"
        if first == 1 and 1 not in self.s["masa"] and "dtp_tetap_bulan_ukur" not in self.s:
            bulan_ukur += " (diasumsikan sama dengan gaji + tunjangan tetap masa kasus ini)"
        return fixed <= 10_000_000, fixed, bulan_ukur

    def dtp_sector_step(self, month):
        klu = self.s["sektor"]["klu"]
        y = self.year
        tag = "25" if y == 2025 else "26"
        info = klu_info(klu, y, month)
        par = ("; " + SRC["dtp25_pariwisata"]) if y == 2025 else ""
        if info is None:
            self.step(f"Kelayakan DTP {MONTH_NAMES[month]} {y}: KLU {klu} tidak tercantum di Lampiran A yang berlaku untuk masa ini",
                      None, "sektor tidak layak", SRC["dtp%s_sektor" % tag] + par)
            return False
        sektor, reg, page = info
        par = par if sektor == "pariwisata" else ""
        self.step(f"Kelayakan DTP {MONTH_NAMES[month]} {y}: KLU {klu} ({sektor}) tercantum di {reg} untuk masa ini",
                  None, "sektor layak", SRC["dtp%s_sektor" % tag] + f"; {reg}, PDF hlm. {page}" + par)
        return True

    # ------------------------------------------------------------ components
    def derive(self, month, raw):
        """Return komponen dict (input) and object breakdown (for bruto)."""
        s = self.s
        comp = {}
        for k in REGULAR_KEYS + IRREGULAR_KEYS:
            if raw.get(k):
                comp[k] = raw[k]
        W = raw.get("gaji", 0) + raw.get("tunjangan_tetap", 0)
        risk = s["sektor"]["risiko_jkk"]
        jkk_rate = JKK_NORMAL[risk]
        relief = s["sektor"].get("padat_karya_pp7") and jkk_relief_active(self.year, month)
        if relief:
            jkk_rate = jkk_rate / 2
        if raw.get("bpjs_tk", True):
            comp["premi_jkk"] = _int(jkk_rate / 100 * W, "premi JKK")
            comp["premi_jkm"] = _int(F("0.3") / 100 * W, "premi JKM")
            comp["iuran_jht_pemberi_kerja"] = _int(F("3.7") / 100 * W, "JHT PK")
            cap = jp_cap(self.year, month)
            comp["iuran_jp_pemberi_kerja"] = _int(F(2) / 100 * min(W, cap), "JP PK")
            comp["iuran_jht_pegawai"] = _int(F(2) / 100 * W, "JHT")
            comp["iuran_jp_pegawai"] = _int(F(1) / 100 * min(W, cap), "JP")
        if raw.get("jkn", True):
            comp["premi_bpjs_kesehatan_pemberi_kerja"] = _int(F(4) / 100 * min(W, 12_000_000), "JKN PK")
            comp["iuran_bpjs_kesehatan_pegawai"] = _int(F(1) / 100 * min(W, 12_000_000), "JKN")
        for k in NATURA_KEYS + ["zakat"]:
            if raw.get(k):
                comp[k] = raw[k]
        return comp, W, jkk_rate, relief

    def natura_taxable(self, month, comp, cum_bingkisan):
        """Return (regular_taxable, irregular_taxable, notes, new_cum)."""
        notes = []
        reg = irr = 0
        active = (self.year, month) >= (2023, 7)
        for k in NATURA_KEYS:
            if not comp.get(k):
                continue
            v = comp[k]
            if not active:
                label = {"natura_rumah_individual": "natura tempat tinggal individual", "kupon_makan_dinas_luar": "kupon makan dinas luar",
                         "bingkisan_non_hari_raya": "bingkisan selain hari raya", "kendaraan_dinas": "fasilitas kendaraan dinas"}[k]
                notes.append((f"{label} {rp(v)} diterima Masa {MONTH_NAMES[month]} 2023 (sebelum 1 Juli 2023): tidak dipotong PPh 21 "
                               f"oleh pemberi kerja (dibayar sendiri oleh pegawai di SPT)", "0", 0, SRC["natura_h1"]))
                if k == "bingkisan_non_hari_raya":
                    cum_bingkisan += v
                continue
            if k == "natura_rumah_individual":
                t = max(0, v - 2_000_000)
                notes.append((f"natura tempat tinggal individual {rp(v)}; batas dikecualikan Rp2.000.000/bulan; "
                              f"selisih lebih menjadi objek", f"max(0, {v} - 2000000)", t, SRC["natura_rumah"]))
                reg += t
            elif k == "kupon_makan_dinas_luar":
                t = max(0, v - 2_000_000)
                notes.append((f"kupon makan pegawai dinas luar {rp(v)}; batas dikecualikan Rp2.000.000/bulan; "
                              f"selisih lebih menjadi objek", f"max(0, {v} - 2000000)", t, SRC["natura_kupon"]))
                reg += t
            elif k == "bingkisan_non_hari_raya":
                prev = cum_bingkisan
                cum_bingkisan += v
                t = max(0, cum_bingkisan - 3_000_000) - max(0, prev - 3_000_000)
                notes.append((f"bingkisan selain hari raya {rp(v)}; kumulatif tahun ini {rp(cum_bingkisan)} "
                              f"(sebelumnya {rp(prev)}); batas Rp3.000.000/tahun",
                              f"max(0, {cum_bingkisan} - 3000000) - max(0, {prev} - 3000000)", t,
                              SRC["natura_bingkisan"]))
                irr += t
            elif k == "kendaraan_dinas":
                notes.append((f"fasilitas kendaraan dinas senilai {rp(v)}: dikecualikan (pegawai tanpa penyertaan modal, "
                               f"rata-rata bruto 12 bulan <= Rp100.000.000/bulan)", "0", 0, SRC["natura_kendaraan"]))
        return reg, irr, notes, cum_bingkisan

    # ------------------------------------------------------------ TER helpers
    def ter_pph(self, cat, bruto):
        rate, row = ter_lookup(cat, bruto)
        return rate, row, round_pph(rate * bruto, self.year)

    def solve_ter_gross_up(self, cat, x):
        t = 0
        for _ in range(200):
            b = x + t
            rate, _, p = self.ter_pph(cat, b)
            if p == t:
                return t
            t = p
        raise RuntimeError("gross-up TER tidak konvergen")

    # ------------------------------------------------------------ 2023 helpers
    def p16_regular_tax(self, reg_bruto, iuran, n):
        bj = min(F(5) / 100 * reg_bruto, 500_000)
        neto = reg_bruto - bj - iuran
        neto_a = n * neto
        pkp = max(0, floor_thousand(neto_a - self.ptkp_value()))
        _, tax = pasal17_layers(pkp)
        return bj, neto, neto_a, pkp, tax

    def solve_p16_gross_up(self, x_reg, iuran, n):
        t = 0
        for _ in range(500):
            *_, tax = self.p16_regular_tax(x_reg + t, iuran, n)
            p = math.floor(F(tax) / n)
            if p == t:
                return t
            t = p
        raise RuntimeError("gross-up 2023 tidak konvergen")

    # ------------------------------------------------------------ annual
    def annual(self, brutos, iurans, zakats, prior, n_months, last):
        bruto = sum(brutos)
        bj_cap = 500_000 * n_months
        bj = min(F(5) / 100 * bruto, bj_cap)
        iur = sum(iurans)
        zak = sum(zakats) if self.ter else 0
        neto = bruto - bj - iur - zak
        pt = self.ptkp_value()
        pkp_raw = neto - pt
        pkp = max(0, floor_thousand(pkp_raw))
        layers, tax = pasal17_layers(pkp)
        return dict(bruto=bruto, bj=bj, bj_cap=bj_cap, iur=iur, zak=zak, neto=neto, ptkp=pt,
                    pkp_raw=pkp_raw, pkp=pkp, layers=layers, tax=tax, akhir=tax - prior)

    def solve_annual_gross_up(self, brutos_wo, iurans, zakats, prior, n):
        t = 0
        for _ in range(500):
            a = self.annual(brutos_wo[:-1] + [brutos_wo[-1] + t], iurans, zakats, prior, n, None)
            v = _int(a["akhir"], "PPh akhir")
            if v <= 0:
                return 0, a
            if v == t:
                return t, a
            t = v
        raise RuntimeError("gross-up masa terakhir tidak konvergen")

    # ------------------------------------------------------------ main
    def build(self):
        s = self.s
        cat = ter_category(self.ptkp_status_for_category()) if self.ter else None
        months = self.months()
        last = self.last_month()
        per_masa, masa_in = [], []
        brutos, iurans, zakats = [], [], []
        prior = 0
        cum_bingkisan = 0
        dtp_months = set()
        self._intro_steps(cat)
        emp = self.dtp_employee()
        dtp_ok = None
        if emp is not None:
            dtp_ok, fixed, bulan_ukur = emp
            tag = "25" if self.year == 2025 else "26"
            self.step(f"Kriteria pegawai DTP: penghasilan bruto tetap dan teratur (gaji + tunjangan tetap) Masa {bulan_ukur} = "
                      f"{rp(fixed)} {'<=' if dtp_ok else '>'} Rp10.000.000; NPWP/NIK terintegrasi; tidak menerima DTP lain",
                      None, "memenuhi" if dtp_ok else "tidak memenuhi", SRC["dtp%s_peg" % tag])
        sector_prev = None

        for m in months:
            raw = s["masa"][m]
            comp, W, jkk_rate, relief = self.derive(m, raw)
            masa_in.append({"bulan": m, "komponen": dict(comp)})
            self._component_steps(m, comp, W, jkk_rate, relief)
            nreg, nirr, nnotes, cum_bingkisan = self.natura_taxable(m, comp, cum_bingkisan)
            for text, formula, val, src in nnotes:
                self.step(f"{MONTH_NAMES[m]}: {text}", formula, val, src)
            base_reg = sum(comp.get(k, 0) for k in REGULAR_KEYS) + comp.get("premi_jkk", 0) \
                + comp.get("premi_jkm", 0) + comp.get("premi_bpjs_kesehatan_pemberi_kerja", 0) + nreg
            base_irr = sum(comp.get(k, 0) for k in IRREGULAR_KEYS) + nirr
            iuran = comp.get("iuran_jht_pegawai", 0) + comp.get("iuran_jp_pegawai", 0)
            zakat = comp.get("zakat", 0)
            parts = [comp.get(k, 0) for k in REGULAR_KEYS] + [comp.get("premi_jkk", 0), comp.get("premi_jkm", 0),
                                                               comp.get("premi_bpjs_kesehatan_pemberi_kerja", 0), nreg] \
                + [comp.get(k, 0) for k in IRREGULAR_KEYS] + [nirr]
            is_last = (m == last)
            row = {"bulan": m}
            month_elig = False
            tag = "25" if self.year == 2025 else "26"
            if emp is not None:
                listed = klu_info(s["sektor"]["klu"], self.year, m) is not None
                if listed != sector_prev:
                    self.dtp_sector_step(m)
                    sector_prev = listed
                month_elig = bool(dtp_ok) and listed
            if not is_last:
                if self.ter:
                    row.update(self._ter_month(m, cat, parts, base_reg + base_irr))
                else:
                    row.update(self._p16_month(m, base_reg, base_irr, iuran, parts))
                if month_elig:
                    row["pph21_dtp"] = row["pph21"]
                    row["pph21_dipotong"] = 0
                    dtp_months.add(m)
                    self.step(f"{MONTH_NAMES[m]}: PPh 21 DTP = seluruh PPh 21 terutang masa ini; dibayarkan tunai ke pegawai "
                              f"dan tidak menambah penghasilan", f"{row['pph21']}", row["pph21"],
                              SRC["dtp%s_masa" % tag] + "; " + SRC["dtp%s_tunai" % tag] + "; " + SRC["dtp_bukan_penghasilan"])
                else:
                    row["pph21_dtp"] = 0
                    row["pph21_dipotong"] = row["pph21"]
                    if emp is not None:
                        self.step(f"{MONTH_NAMES[m]}: tidak ada PPh 21 DTP masa ini; seluruh PPh 21 dipotong/disetor", "0", 0,
                                  SRC["dtp%s_peg" % tag] + "; " + SRC["dtp%s_sektor" % tag])
                prior += row["pph21"]
                brutos.append(row["bruto"])
            else:
                row.update(self._last_month(m, cat, parts, brutos, iurans + [iuran], zakats + [zakat], prior))
                brutos.append(row["bruto"])
                if month_elig:
                    dtp_months.add(m)
                    v = row["pph21"]
                    row["pph21_dtp"] = v
                    row["pph21_dipotong"] = 0
                    if v >= 0:
                        self.step(f"{MONTH_NAMES[m]} (Masa Pajak Terakhir): PPh 21 kurang potong {rp(v)} seluruhnya DTP",
                                  f"{v}", v, SRC["dtp%s_masa" % tag] + "; " + SRC["dtp%s_tunai" % tag])
                    else:
                        self.step(f"{MONTH_NAMES[m]} (Masa Pajak Terakhir): lebih potong {rp(-v)} berasal dari PPh 21 DTP; "
                                  f"tidak dikembalikan kepada pegawai", f"{v}", v, SRC["dtp%s_lebih" % tag])
                else:
                    row["pph21_dtp"] = 0
                    row["pph21_dipotong"] = row["pph21"]
                    if row["pph21"] < 0:
                        self.step(f"{MONTH_NAMES[m]}: lebih potong {rp(-row['pph21'])} dikembalikan kepada pegawai paling lambat "
                                  f"akhir bulan berikutnya", f"{row['pph21']}", row["pph21"],
                                  SRC["lebih_potong"] if self.ter else SRC["p16_leaver"])
            iurans.append(iuran)
            zakats.append(zakat)
            per_masa.append(row)

        tahunan = getattr(self, "_tahunan", None)
        if tahunan is not None and dtp_months:
            tahunan["pph21_dtp_setahun"] = sum(r["pph21_dtp"] for r in per_masa)
            tahunan["kelebihan_dikembalikan_ke_pegawai"] = 0 if per_masa[-1]["pph21"] >= 0 else 0
        elif tahunan is not None:
            v = per_masa[-1]["pph21"]
            tahunan["pph21_dtp_setahun"] = 0
            tahunan["kelebihan_dikembalikan_ke_pegawai"] = -v if v < 0 else 0
        expected = {"per_masa": [self._clean_row(r) for r in per_masa], "tahunan": tahunan}
        if self.year in (2025, 2026):
            expected["berhak_dtp"] = bool(dtp_months)
        return masa_in, expected, self.steps

    def _clean_row(self, r):
        keys = ["bulan", "bruto", "kategori_ter", "tarif_ter", "pph21", "pph21_dtp", "pph21_dipotong"]
        out = {k: r.get(k) for k in keys}
        for k in ("tunjangan_pajak", "pph21_ditanggung_pemberi_kerja", "keterangan", "rincian_metode_lama"):
            if k in r:
                out[k] = r[k]
        return out

    # ------------------------------------------------------------ step groups
    def _intro_steps(self, cat):
        s = self.s
        if s.get("karyawati_kawin"):
            src = SRC["karyawati"] if self.ter else SRC["p16_karyawati"]
            self.step(f"Karyawati kawin: PTKP yang dipakai pemotong = PTKP diri sendiri (setara TK/0), "
                      f"walaupun status keluarga {self.status}", "54000000", 54_000_000, src)
        else:
            src = SRC["ptkp"] + "; " + (SRC["ptkp_awal"] if self.ter else SRC["p16_ptkp"])
            self.step(f"PTKP setahun status {self.status} (keadaan awal tahun {self.year})",
                      self._ptkp_formula(self.status), self.ptkp_value(), src)
        if self.ter:
            self.step(f"Kategori TER untuk status PTKP {self.ptkp_status_for_category()}", None, cat, SRC["ter_kat"])

    def _ptkp_formula(self, st):
        n = int(st.split("/")[-1])
        k = st.startswith("K/")
        parts = ["54000000"] + (["4500000"] if k else []) + ([f"{n} * 4500000"] if n else [])
        return " + ".join(parts)

    def _component_steps(self, m, comp, W, jkk_rate, relief):
        if "premi_jkk" not in comp and "premi_bpjs_kesehatan_pemberi_kerja" not in comp:
            return
        y, tag = self.year, MONTH_NAMES[m]
        if "premi_jkk" in comp:
            src = SRC["jkk"]
            if relief:
                src = SRC["jkk_relief"] + ("; " + SRC["jkk_relief_ext"] if (y, m) >= (2025, 8) else "")
            self.step(f"{tag}: premi JKK dibayar pemberi kerja = {pct(jkk_rate / 100)} x upah sebulan {rp(W)}"
                      + (" (tarif keringanan 50% industri padat karya)" if relief else ""),
                      f"{dec(jkk_rate / 100)} * {W}", comp["premi_jkk"], src)
            self.step(f"{tag}: premi JKM dibayar pemberi kerja = 0,3% x {rp(W)}", f"0.003 * {W}", comp["premi_jkm"], SRC["jkm"])
            cap = jp_cap(y, m)
            self.step(f"{tag}: iuran JHT pegawai 2% x {rp(W)} (pengurang neto; JHT 3,7% pemberi kerja bukan objek)",
                      f"0.02 * {W}", comp["iuran_jht_pegawai"], SRC["jht"])
            self.step(f"{tag}: iuran JP pegawai 1% x min(upah {rp(W)}, batas upah JP {rp(cap)}) "
                      f"(pengurang neto; JP 2% pemberi kerja bukan objek)",
                      f"0.01 * min({W}, {cap})", comp["iuran_jp_pegawai"], SRC["jp"])
        if "premi_bpjs_kesehatan_pemberi_kerja" in comp:
            self.step(f"{tag}: premi BPJS Kesehatan pemberi kerja 4% x min({rp(W)}, Rp12.000.000) (objek); "
                      f"iuran 1% pegawai {rp(comp['iuran_bpjs_kesehatan_pegawai'])} bukan pengurang",
                      f"0.04 * min({W}, 12000000)", comp["premi_bpjs_kesehatan_pemberi_kerja"],
                      SRC["jkn"] + "; " + (SRC["jkn_obj"] if self.ter else SRC["p16_bruto"]) + "; " + SRC["jkn_bukan_peng"])

    def _ter_month(self, m, cat, parts, x):
        tag = MONTH_NAMES[m]
        out = {}
        src_b = SRC["bruto_pt"] + "; " + SRC["jkk_jkm_obj"] + "; " + SRC["jkn_obj"] + "; " + SRC["iuran_pk_bukan"]
        if self.metode in ("gross_up", "ditanggung"):
            self.step(f"{tag}: bruto sebelum tunjangan/PPh ditanggung (gaji, tunjangan, lembur, THR/bonus, premi JKK/JKM/BPJS "
                      f"Kesehatan pemberi kerja, natura objek)", fsum(parts), x, src_b)
            t = self.solve_ter_gross_up(cat, x)
            b = x + t
            rate, row, p = self.ter_pph(cat, b)
            label = "tunjangan pajak" if self.metode == "gross_up" else "PPh 21 ditanggung pemberi kerja (kenikmatan, objek)"
            src_t = (SRC["tunj_pajak"] if self.metode == "gross_up" else SRC["kenikmatan_pph"]) + "; " + SRC["gross_up"] + "; " + round_src(self.year)
            rnote = "dibulatkan ke bawah" if self.year <= 2024 else "dibulatkan ke rupiah terdekat"
            self.step(f"{tag}: {label} T dicari sehingga T = PPh 21 TER atas (bruto sebelum T + T), {rnote}; "
                      f"hasil T = {rp(t)} (tarif {pct(rate)}; titik tetap terkecil)", round_formula(f"{dec(rate)} * ({x} + {t})", self.year), t, src_t)
            self.step(f"{tag}: penghasilan bruto masa = {rp(x)} + {rp(t)}", f"{x} + {t}", b, src_b)
            if self.metode == "gross_up":
                out["tunjangan_pajak"] = t
            else:
                out["pph21_ditanggung_pemberi_kerja"] = t
        else:
            b = x
            self.step(f"{tag}: penghasilan bruto masa (gaji, tunjangan, lembur, THR/bonus, premi JKK/JKM/BPJS Kesehatan "
                      f"pemberi kerja, natura objek; iuran JHT/JP pemberi kerja tidak termasuk)", fsum(parts), b, src_b)
            rate, row, p = self.ter_pph(cat, b)
        lo, hi = int(row["batas_bawah"]), row["batas_atas"]
        rng = f"di atas {rp(lo)} s.d. {rp(int(hi))}" if hi else f"di atas {rp(lo)}"
        self.step(f"{tag}: tarif efektif bulanan kategori {cat} untuk bruto {rp(b)} (lapisan {rng})", None,
                  float(dec(rate)), f"PP 58/2023 Lampiran huruf {cat}, PDF hlm. {ter_page(row)}; " + SRC["ter_kat"])
        exact = rate * b
        rtext = "dibulatkan ke bawah ke rupiah penuh" if self.year <= 2024 else "dibulatkan ke rupiah penuh terdekat (0,50 ke atas)"
        self.step(f"{tag}: PPh 21 = {pct(rate)} x {rp(b)} = {rp(exact)}" + (f"; {rtext}" if exact.denominator != 1 else ""),
                  round_formula(f"{dec(rate)} * {b}", self.year), p, SRC["ter_masa"] + ("; " + round_src(self.year) if exact.denominator != 1 else ""))
        out.update({"bruto": b, "kategori_ter": cat, "tarif_ter": float(dec(rate)), "pph21": p})
        return out

    def _p16_month(self, m, reg, irr, iuran, parts):
        tag = MONTH_NAMES[m]
        n = self.n_factor_2023()
        out = {}
        src_b = SRC["p16_bruto"] + "; " + SRC["p16_iuran_pk"]
        if self.metode == "gross_up":
            self.step(f"{tag}: penghasilan teratur sebelum tunjangan pajak", fsum(parts[:7]), reg, src_b)
            t = self.solve_p16_gross_up(reg, iuran, n)
            reg_t = reg + t
            *_, tax_t = self.p16_regular_tax(reg_t, iuran, n)
            self.step(f"{tag}: tunjangan pajak T dicari sehingga T = PPh 21 sebulan atas penghasilan teratur termasuk T; "
                      f"hasil T = {rp(t)} (titik tetap terkecil; dibuktikan pada langkah PPh 21 masa di bawah yang harus sama dengan T)", f"{t}", t, SRC["p16_tunj"] + "; " + SRC["gross_up"] + "; " + SRC["bulat_p16"])
            out["tunjangan_pajak"] = t
            reg = reg_t
            self.step(f"{tag}: penghasilan teratur termasuk tunjangan pajak", f"{reg - t} + {t}", reg, src_b)
        else:
            self.step(f"{tag}: penghasilan bruto teratur sebulan (gaji, tunjangan, lembur, premi JKK/JKM/BPJS Kesehatan, "
                      f"natura teratur objek)", fsum(parts[:7]), reg, src_b)
        bj, neto, neto_a, pkp, tax = self.p16_regular_tax(reg, iuran, n)
        self.step(f"{tag}: biaya jabatan sebulan = min(5% x {rp(reg)}, Rp500.000)", f"min(0.05 * {reg}, 500000)", bj, SRC["p16_bj"])
        self.step(f"{tag}: iuran JHT + JP dibayar pegawai", f"{iuran}", iuran, SRC["p16_iuran"])
        self.step(f"{tag}: penghasilan neto sebulan", f"{reg} - {dec(bj)} - {iuran}", neto, SRC["p16_bj"] + "; " + SRC["p16_iuran"])
        src_n = SRC["p16_setahun"] if n == 12 else SRC["p16_joiner"]
        self.step(f"{tag}: penghasilan neto disetahunkan ({n} x neto sebulan)", f"{n} * ({reg} - {dec(bj)} - {iuran})", neto_a, src_n)
        self.step(f"{tag}: PKP = neto setahun - PTKP {rp(self.ptkp_value())}, dibulatkan ke bawah hingga ribuan",
                  f"max(0, floor(({dec(neto_a)} - {self.ptkp_value()}) / 1000) * 1000)", pkp, SRC["p16_pkp"])
        self.step(f"{tag}: PPh 21 setahun atas penghasilan teratur (tarif Pasal 17)", self._p17_formula(pkp), tax, SRC["tarif17"])
        p_reg = math.floor(F(tax) / n)
        exact = F(tax) / n
        self.step(f"{tag}: PPh 21 atas penghasilan teratur = PPh setahun / {n}", f"floor({tax} / {n})", p_reg,
                  (SRC["p16_bulan"] if n == 12 else SRC["p16_joiner"]) + ("; " + SRC["bulat_p16"] if exact.denominator != 1 else ""))
        p_irr = 0
        rincian = {"faktor_pengali": n, "neto_disetahunkan": _int(neto_a, "neto"), "pkp_teratur": pkp, "pph_setahun_teratur": int(tax)}
        if irr:
            b_a = n * reg + irr
            bj_a = min(F(5) / 100 * b_a, 500_000 * n)
            neto2 = b_a - bj_a - n * iuran
            pkp2 = max(0, floor_thousand(neto2 - self.ptkp_value()))
            _, tax2 = pasal17_layers(pkp2)
            self.step(f"{tag}: bruto teratur disetahunkan + penghasilan tidak teratur {rp(irr)}", f"{n} * {reg} + {irr}", b_a, SRC["p16_irr"])
            self.step(f"{tag}: biaya jabatan atas jumlah tersebut = min(5% x bruto, {n} x Rp500.000)",
                      f"min(0.05 * {b_a}, {500000 * n})", bj_a, SRC["p16_bj"] + "; " + SRC["p16_irr"])
            self.step(f"{tag}: neto termasuk penghasilan tidak teratur", f"{b_a} - {dec(bj_a)} - {n} * {iuran}", neto2, SRC["p16_irr"])
            self.step(f"{tag}: PKP termasuk penghasilan tidak teratur (dibulatkan ke bawah ribuan)",
                      f"max(0, floor(({dec(neto2)} - {self.ptkp_value()}) / 1000) * 1000)", pkp2, SRC["p16_pkp"])
            self.step(f"{tag}: PPh setahun termasuk penghasilan tidak teratur", self._p17_formula(pkp2), tax2, SRC["tarif17"])
            p_irr = int(tax2 - tax)
            self.step(f"{tag}: PPh 21 atas penghasilan tidak teratur = selisih PPh setahun", f"{tax2} - {tax}", p_irr, SRC["p16_irr"])
            rincian.update({"pkp_dengan_tidak_teratur": pkp2, "pph_setahun_dengan_tidak_teratur": int(tax2),
                            "pph21_tidak_teratur": p_irr})
        total = p_reg + p_irr
        if irr:
            self.step(f"{tag}: PPh 21 masa = PPh teratur + PPh tidak teratur", f"{p_reg} + {p_irr}", total, SRC["p16_irr"])
        b = reg + irr
        self.step(f"{tag}: penghasilan bruto masa (teratur + tidak teratur)", f"{reg} + {irr}", b, SRC["p16_bruto"])
        if self.metode == "ditanggung":
            self.step(f"{tag}: PPh 21 {rp(total)} ditanggung pemberi kerja; merupakan kenikmatan (PER-16 Pasal 8 ayat (2)) yang "
                      f"untuk Masa Januari-Juni 2023 dikecualikan dari pemotongan, sehingga tidak ditambahkan ke bruto (tanpa gross-up)",
                      f"{total}", total, SRC["p16_ditanggung"])
            out["pph21_ditanggung_pemberi_kerja"] = total
        rincian["pph21_teratur"] = p_reg
        out.update({"bruto": b, "kategori_ter": None, "tarif_ter": None, "pph21": total, "rincian_metode_lama": rincian})
        return out

    def _p17_formula(self, pkp):
        layers, _ = pasal17_layers(pkp)
        if not layers:
            return "0"
        return " + ".join(f"{dec(r)} * {b}" for r, b, _, _ in layers)

    def _last_month(self, m, cat, parts, brutos_prev, iurans, zakats, prior):
        tag = MONTH_NAMES[m]
        s = self.s
        n = len(brutos_prev) + 1
        x = sum(parts)
        ter = self.ter
        if ter:
            src_b = SRC["bruto_pt"] + "; " + SRC["jkk_jkm_obj"] + "; " + SRC["jkn_obj"]
        else:
            src_b = SRC["p16_bruto"]
        reason = "Desember" if m == 12 else f"bulan berhenti bekerja ({tag})"
        self.step(f"{tag} adalah Masa Pajak Terakhir ({reason}): PPh 21 dihitung ulang setahun dengan tarif Pasal 17",
                  None, "masa terakhir", (SRC["masa_akhir_def"] + "; " + SRC["masa_akhir"]) if ter else SRC["p16_akhir"])
        out = {}
        if self.metode in ("gross_up", "ditanggung") and not (self.year == 2023 and self.metode == "ditanggung"):
            self.step(f"{tag}: bruto masa sebelum tunjangan pajak/PPh ditanggung", fsum(parts), x, src_b)
            t, a = self.solve_annual_gross_up(brutos_prev + [x], iurans, zakats, prior, n)
            b = x + t
            label = "tunjangan pajak" if self.metode == "gross_up" else "PPh 21 ditanggung pemberi kerja (kenikmatan)"
            src_t = (SRC["tunj_pajak"] if (ter and self.metode == "gross_up") else SRC["p16_tunj"] if not ter
                     else SRC["kenikmatan_pph"]) + "; " + SRC["gross_up"]
            self.step(f"{tag}: {label} T Masa Pajak Terakhir dicari sehingga T = PPh 21 setahun (bruto termasuk T) - "
                      f"PPh 21 masa sebelumnya; hasil T = {rp(t)} (titik tetap terkecil; dibuktikan pada langkah PPh Masa Pajak Terakhir di bawah yang harus sama dengan T)", f"{t}", t, src_t)
            self.step(f"{tag}: bruto masa termasuk T", f"{x} + {t}", b, src_b)
            if self.metode == "gross_up":
                out["tunjangan_pajak"] = t
            else:
                out["pph21_ditanggung_pemberi_kerja"] = t
        else:
            b = x
            self.step(f"{tag}: penghasilan bruto masa", fsum(parts), b, src_b)
        brutos = brutos_prev + [b]
        a = self.annual(brutos, iurans, zakats, prior, n, m)
        self.step("Penghasilan bruto " + ("setahun" if n == 12 else f"{n} bulan bekerja") + " (jumlah bruto seluruh masa)",
                  fsum(brutos), a["bruto"], (SRC["neto"] if ter else SRC["p16_akhir"])
                  + ("; " + (SRC["bagian_tahun"] if ter else SRC["p16_leaver"]) if n < 12 else ""))
        self.step(f"Biaya jabatan = min(5% x bruto, {n} x Rp500.000)", f"min(0.05 * {a['bruto']}, {a['bj_cap']})", a["bj"],
                  SRC["bj"] if ter else SRC["p16_bj"])
        self.step("Iuran JHT + JP dibayar pegawai setahun", fsum(iurans), a["iur"], SRC["iuran_peng"] if ter else SRC["p16_iuran"])
        if sum(zakats):
            if ter:
                self.step("Zakat melalui pemberi kerja setahun (pengurang)", fsum(zakats), a["zak"], SRC["zakat"])
            else:
                self.step(f"Zakat melalui pemberi kerja {rp(sum(zakats))} tidak dikurangkan dalam pemotongan 2023", "0", 0, SRC["p16_zakat"])
        self.step("Penghasilan neto", f"{a['bruto']} - {dec(a['bj'])} - {a['iur']} - {a['zak']}", a["neto"],
                  SRC["neto"] if ter else SRC["p16_akhir"])
        self.step(f"PKP sebelum pembulatan = neto - PTKP {rp(a['ptkp'])}", f"{dec(a['neto'])} - {a['ptkp']}", a["pkp_raw"],
                  SRC["pkp"] if ter else SRC["p16_pkp"])
        self.step("PKP dibulatkan ke bawah hingga ribuan rupiah penuh", f"max(0, floor(({dec(a['neto'])} - {a['ptkp']}) / 1000) * 1000)",
                  a["pkp"], SRC["pkp"] if ter else SRC["p16_pkp"])
        for r_, base, lo, hi in a["layers"]:
            self.step(f"Lapisan {pct(r_)} (PKP di atas {rp(lo)}" + (f" s.d. {rp(hi)}" if hi else "") + f"): {pct(r_)} x {rp(base)}",
                      f"{dec(r_)} * {base}", r_ * base, SRC["tarif17"])
        self.step("PPh 21 terutang setahun (tarif Pasal 17)", self._p17_formula(a["pkp"]), a["tax"], SRC["tarif17"])
        self.step("PPh 21 yang telah dipotong pada masa sebelumnya" + (" (termasuk yang DTP)" if self.year in (2025, 2026) else ""),
                  f"{prior}", prior, SRC["masa_akhir"] if ter else SRC["p16_akhir"])
        akhir = _int(a["akhir"], "akhir")
        self.step(f"{tag}: PPh 21 Masa Pajak Terakhir = PPh setahun - PPh telah dipotong", f"{a['tax']} - {prior}", akhir,
                  SRC["masa_akhir"] if ter else SRC["p16_akhir"])
        if self.metode == "ditanggung" and self.year == 2023:
            self.step(f"{tag}: PPh 21 {rp(akhir)} ditanggung pemberi kerja (kenikmatan, bukan objek, tanpa gross-up)",
                      f"{akhir}", akhir, SRC["p16_ditanggung"])
            out["pph21_ditanggung_pemberi_kerja"] = akhir
        self._tahunan = {
            "bulan_masa_terakhir": m, "jumlah_bulan": n,
            "bruto_setahun": _int(a["bruto"], "bruto"), "biaya_jabatan": float(dec(a["bj"])) if F(a["bj"]).denominator != 1 else int(a["bj"]),
            "iuran_jht_jp_pegawai": int(a["iur"]), "zakat": int(a["zak"]),
            "neto_setahun": float(dec(a["neto"])) if F(a["neto"]).denominator != 1 else int(a["neto"]),
            "ptkp": a["ptkp"], "pkp": a["pkp"],
            "pph21_lapisan": [{"tarif": float(dec(r_)), "dasar": base, "pph": _int(r_ * base, "lapisan")} for r_, base, _, _ in a["layers"]],
            "pph21_setahun": _int(a["tax"], "tax"), "pph21_dipotong_sebelumnya": prior, "pph21_masa_terakhir": akhir,
        }
        out.update({"bruto": _int(b, "bruto"), "kategori_ter": None, "tarif_ter": None, "pph21": akhir,
                    "keterangan": "Masa Pajak Terakhir (tarif Pasal 17)"})
        return out
