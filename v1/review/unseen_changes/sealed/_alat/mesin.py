# -*- coding: utf-8 -*-
"""Base PPh 21 engine (rules in force in 2026) with a step recorder.

DOKUMEN FIKTIF UNTUK PENELITIAN - tool used only to build and check the
worked examples of the sealed unseen changes U01..U16.

Base rules: TER per PP 58/2023 (tables/ter_bulanan.csv), PMK 168/2023,
PTKP per PMK 101/2016 (tables/ptkp.csv), Pasal 17 per UU HPP
(tables/tarif_pasal17.csv). Change-specific behaviour lives in subclasses
(see buat_contoh.py).
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TABLES_DIR = ROOT / "dataset" / "01_regulasi" / "tables"

BULAN = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def rp(v):
    s = f"{abs(v):,}".replace(",", ".")
    return ("-" if v < 0 else "") + "Rp" + s


def pct(bp):
    s = f"{bp / 100:g}".replace(".", ",")
    return s + "%"


# ---------------------------------------------------------------- tables
def load_ter():
    tabs = {}
    with open(TABLES_DIR / "ter_bulanan.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lo = int(r["batas_bawah"])
            hi = int(r["batas_atas"]) if r["batas_atas"] else None
            bp = round(float(r["tarif_persen"]) * 100)
            tabs.setdefault("PP58/" + r["kategori"], []).append((lo, hi, bp))
    return tabs


def load_ptkp():
    out = {}
    with open(TABLES_DIR / "ptkp.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["status"]] = int(r["ptkp_setahun"])
    return out


def load_p17():
    rows = []
    with open(TABLES_DIR / "tarif_pasal17.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["rezim"] == "UU HPP":
                hi = int(r["pkp_batas_atas"]) if r["pkp_batas_atas"] else None
                rows.append((int(r["pkp_batas_bawah"]), hi, int(r["tarif_persen"])))
    return rows


TABLES = load_ter()
PTKP = load_ptkp()
P17 = load_p17()
KAT = {"TK/0": "A", "TK/1": "A", "K/0": "A", "TK/2": "B", "TK/3": "B",
       "K/1": "B", "K/2": "B", "K/3": "C"}


def ter_lookup(tab, base):
    for lo, hi, bp in TABLES[tab]:
        if (base > lo or lo == 0) and (hi is None or base <= hi):
            return bp
    raise ValueError((tab, base))


def ter_layer(tab, base):
    for lo, hi, bp in TABLES[tab]:
        if (base > lo or lo == 0) and (hi is None or base <= hi):
            return lo, hi
    raise ValueError((tab, base))


def p17_value(pkp):
    tax = 0
    for lo, hi, r in P17:
        if pkp > lo:
            top = pkp if hi is None else min(pkp, hi)
            tax += (top - lo) * r // 100
    return tax


def sum_expr(values):
    """'a * k + b' style expression grouping consecutive equal values."""
    parts = []
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[j + 1] == values[i]:
            j += 1
        k = j - i + 1
        parts.append(f"{values[i]} * {k}" if k > 1 else f"{values[i]}")
        i = j + 1
    return " + ".join(parts) if parts else "0"


def pension_expr(months):
    parts = []
    for k in PENSION_KEYS:
        vals = [m["komponen"].get(k, 0) for m in months]
        if any(vals):
            parts.append(sum_expr(vals))
    return " + ".join(parts)


PENSION_KEYS = ["iuran_jht_pegawai", "iuran_jp_pegawai"]


# ---------------------------------------------------------------- recorder
class Rec:
    def __init__(self):
        self.steps = []

    def _add(self, d):
        d = {"no": len(self.steps) + 1, **d}
        self.steps.append(d)
        return d

    def calc(self, uraian, expr):
        v = eval(expr, {"__builtins__": {}}, {"min": min, "max": max})
        assert isinstance(v, int), (expr, v)
        self._add({"uraian": uraian, "ekspresi": expr, "hasil": v})
        return v

    def lookup(self, uraian, tab, nilai):
        bp = ter_lookup(tab, nilai)
        lo, hi = ter_layer(tab, nilai)
        hi_s = "tanpa batas" if hi is None else rp(hi)
        self._add({"uraian": f"{uraian} -> lapisan di atas {rp(lo)} s.d. {hi_s}",
                   "tabel": tab, "nilai": nilai, "hasil": pct(bp),
                   "tarif_basis_poin": bp})
        return bp

    def note(self, uraian):
        self._add({"uraian": uraian})

    @property
    def last(self):
        return self.steps[-1]["no"]


LABEL = {
    "gaji_pokok": "gaji pokok", "tunjangan_tetap": "tunjangan tetap",
    "tunjangan_tidak_tetap": "tunjangan tidak tetap", "lembur": "lembur",
    "premi_jkk": "premi JKK (pemberi kerja)", "premi_jkm": "premi JKM (pemberi kerja)",
    "premi_jkn": "iuran JKN (pemberi kerja)",
    "iuran_tapera_pemberi_kerja": "iuran Tapera dibayar pemberi kerja",
    "tunjangan_internet": "tunjangan internet tunai",
    "penggantian_internet": "penggantian biaya internet berbukti",
    "rapel_gaji": "rapel gaji", "rapel_premi_jkk": "rapel premi JKK",
    "rapel_premi_jkm": "rapel premi JKM", "rapel_premi_jkn": "rapel iuran JKN",
    "thr": "THR", "bonus": "bonus", "tunjangan_pph21": "tunjangan PPh 21",
}
INCOME = list(LABEL.keys())
IRREGULAR = ["thr", "bonus"]
PENSION = ["iuran_jht_pegawai", "iuran_jp_pegawai"]


class Engine:
    """Base rules in force in 2026 (no unseen change)."""
    CHANGE = None

    def __init__(self, inp):
        self.inp = inp
        self.year = inp["tahun_pajak"]
        self.status = inp["status_ptkp"]
        self.R = Rec()
        self.bind = {}
        self.masa = inp["masa"]
        self.extra_out = {}

    # ------------------------------------------------ hooks (overridable)
    def status_efektif(self):
        """PMK 168/2023 Pasal 9 ayat (2)-(3): karyawati kawin."""
        st = self.status
        if (self.inp.get("jenis_kelamin") == "P" and st.startswith("K/")
                and not self.inp.get("keterangan_suami_tidak_berpenghasilan")):
            return "TK/0", "karyawati kawin tanpa keterangan suami tidak berpenghasilan: PTKP diri sendiri saja (PMK 168/2023 Pasal 9 ayat (2) huruf a), setara TK/0"
        return st, None

    def kategori(self):
        st, _ = self.status_efektif()
        return KAT[st]

    def ter_table(self, kat):
        return f"PP58/{kat}"

    def income_items(self, m):
        return [(k, m["komponen"][k]) for k in INCOME if k in m["komponen"]]

    def bruto(self, m):
        items = self.income_items(m)
        expr = " + ".join(str(v) for _, v in items) if items else "0"
        lab = " + ".join(LABEL[k] for k, _ in items)
        return self.R.calc(f"Penghasilan bruto masa {BULAN[m['bulan']]} = {lab}", expr)

    def ter_base(self, m, bruto):
        return bruto

    def pph_masa(self, m, bruto, idx):
        kat = self.kategori()
        tab = self.ter_table(kat)
        base = self.ter_base(m, bruto)
        st, _ = self.status_efektif()
        bp = self.R.lookup(f"Tarif efektif bulanan kategori {kat} (status {st}) untuk dasar {rp(base)} (tabel {tab})", tab, base)
        return self.R.calc(f"PPh 21 masa {BULAN[m['bulan']]} = {pct(bp)} x {rp(bruto)}, dibulatkan ke bawah ke rupiah penuh",
                           f"{bruto} * {bp} // 10000")

    def ptkp(self, n_bulan):
        st, why = self.status_efektif()
        v = PTKP[st]
        if why:
            self.R.note(why)
        self.R.calc(f"PTKP setahun status {st} (PMK 101/2016)", f"{v}")
        return v

    def bj_cap_month(self):
        return 500000

    def biaya_jabatan(self, bs, n):
        cap = self.bj_cap_month() * n
        return self.R.calc(f"Biaya jabatan = 5% x bruto, paling banyak {rp(self.bj_cap_month())} x {n} bulan",
                           f"min({bs} * 5 // 100, {self.bj_cap_month()} * {n})")

    def deductions(self, months, n):
        """Return list of (label, value) for pengurang other than biaya jabatan."""
        out = []
        expr = pension_expr(months)
        if expr:
            v = self.R.calc("Iuran JHT + JP dibayar pegawai setahun (PMK 168/2023 Pasal 10 ayat (1) huruf b)", expr)
            out.append(("iuran pensiun/JHT", v))
        out += self.zakat(months)
        return out

    def zakat(self, months):
        vals = [m["komponen"].get("zakat", 0) for m in months]
        if any(vals):
            v = self.R.calc("Zakat melalui pemberi kerja setahun (PMK 168/2023 Pasal 10 ayat (1) huruf c)", sum_expr(vals))
            return [("zakat", v)]
        return []

    def pasal17(self, pkp, label="PPh 21 setahun"):
        parts = []
        for lo, hi, r in P17:
            if pkp > lo:
                top = pkp if hi is None else min(pkp, hi)
                parts.append(f"({top} - {lo}) * {r} // 100" if lo else f"{top} * {r} // 100")
        expr = " + ".join(parts) if parts else "0"
        return self.R.calc(f"{label} = tarif Pasal 17 UU HPP x PKP {rp(pkp)}", expr)

    def masa_terakhir(self):
        if "masa_terakhir" in self.inp:
            return self.inp["masa_terakhir"]
        return 12 if any(m["bulan"] == 12 for m in self.masa) else None

    # DTP hook: returns DTP amount for a masa given computed PPh terutang
    def dtp(self, m, pph, terakhir):
        return 0

    # --------------------------------------------------- annual computation
    def annual(self, months, brutos, pph_prev, label="Masa Pajak Terakhir"):
        R = self.R
        n = len(months)
        R.note(f"Perhitungan {label} ({BULAN[months[-1]['bulan']]}): PMK 168/2023 Pasal 15 ayat (1) huruf b dan ayat (2)")
        bs = R.calc(f"Jumlah penghasilan bruto {n} bulan", sum_expr(brutos))
        self.bind["setahun.bruto_setahun"] = R.last
        bj = self.biaya_jabatan(bs, n)
        self.bind["setahun.biaya_jabatan"] = R.last
        ded = self.deductions(months, n)
        expr = f"{bs} - {bj}" + "".join(f" - {v}" for _, v in ded)
        neto = R.calc("Penghasilan neto = bruto - biaya jabatan" + "".join(f" - {l}" for l, _ in ded), expr)
        self.bind["setahun.neto"] = R.last
        ptkp = self.ptkp(n)
        self.bind["setahun.ptkp"] = R.last
        pkp = R.calc("PKP = neto - PTKP, dibulatkan ke bawah hingga ribuan rupiah (minimal 0)",
                     f"max(0, ({neto} - {ptkp}) // 1000 * 1000)")
        self.bind["setahun.pkp"] = R.last
        tax = self.pasal17(pkp)
        self.bind["setahun.pph21_setahun"] = R.last
        prev = R.calc("PPh 21 terutang masa-masa sebelumnya", sum_expr(pph_prev)) if pph_prev else 0
        if not pph_prev:
            R.calc("PPh 21 terutang masa-masa sebelumnya", "0")
        last = R.calc(f"PPh 21 {label} = PPh 21 setahun - PPh 21 masa sebelumnya", f"{tax} - {prev}")
        return dict(bruto_setahun=bs, biaya_jabatan=bj, neto=neto, ptkp=ptkp, pkp=pkp,
                    pph21_setahun=tax), last

    # ------------------------------------------------------------- run
    def run(self):
        R = self.R
        out_masa = []
        terakhir = self.masa_terakhir()
        brutos, terutang, dipotong = [], [], []
        self.brutos, self.terutang, self.dipotong = brutos, terutang, dipotong
        cache = {}
        for idx, m in enumerate(self.masa):
            is_last = (m["bulan"] == terakhir)
            key = repr(sorted(m["komponen"].items())) + repr({k: v for k, v in m.items() if k not in ("bulan", "komponen")})
            row = {"bulan": m["bulan"]}
            if is_last:
                b = self.bruto(m)
                bstep = R.last
                brutos.append(b)
                ann, last = self.annual(self.masa[:idx + 1], brutos, terutang)
                lstep = R.last
                d = self.dtp(m, last, True)
                if last >= 0:
                    pot = last - d
                else:
                    refundable = min(-last, sum(dipotong))
                    pot = -refundable
                    if refundable != -last:
                        R.calc("Kelebihan yang tidak dikembalikan kepada pegawai (berasal dari PPh 21 DTP)",
                               f"{-last} - {refundable}")
                        self.extra_out["kelebihan_dtp_tidak_dikembalikan"] = -last - refundable
                        self.bind["setahun.kelebihan_dtp_tidak_dikembalikan"] = R.last
                if pot != last:
                    R.calc(f"PPh 21 yang dipotong dari pegawai masa {BULAN[m['bulan']]}", f"{last} - {last - pot}")
                    pstep = R.last
                else:
                    pstep = lstep
                row.update(bruto=b, pph21=last, pph21_dipotong=pot)
                self.bind[f"per_masa[{idx}].bruto"] = bstep
                self.bind[f"per_masa[{idx}].pph21"] = lstep
                self.bind[f"per_masa[{idx}].pph21_dipotong"] = pstep
                if self.has_dtp():
                    row["pph21_dtp"] = d
                    if d:
                        self.bind[f"per_masa[{idx}].pph21_dtp"] = lstep
                out_masa.append(row)
                self.setahun = ann
                break
            if key in cache and not self.no_cache(m):
                j = cache[key]
                prow = out_masa[j]
                R.note(f"Masa {BULAN[m['bulan']]}: komponen sama dengan masa {BULAN[prow['bulan']]}, sehingga bruto {rp(prow['bruto'])} dan PPh 21 {rp(prow['pph21'])} sama")
                for fld in ("bruto", "pph21", "pph21_dipotong", "pph21_dtp"):
                    if f"per_masa[{j}].{fld}" in self.bind:
                        self.bind[f"per_masa[{idx}].{fld}"] = self.bind[f"per_masa[{j}].{fld}"]
                row.update({k: v for k, v in prow.items() if k != "bulan"})
                d = row.get("pph21_dtp", 0)
                if self.has_dtp() and self.dtp_masa_changes(m):
                    # eligibility may differ per masa: recompute
                    d = self.dtp(m, row["pph21"], False)
                    row["pph21_dtp"] = d
                    row["pph21_dipotong"] = row["pph21"] - d
                    R.calc(f"PPh 21 dipotong dari pegawai masa {BULAN[m['bulan']]}", f"{row['pph21']} - {d}")
                    self.bind[f"per_masa[{idx}].pph21_dipotong"] = R.last
                    if d:
                        self.bind[f"per_masa[{idx}].pph21_dtp"] = self.bind[f"per_masa[{j}].pph21"]
                    else:
                        self.bind.pop(f"per_masa[{idx}].pph21_dtp", None)
            else:
                b = self.bruto(m)
                self.bind[f"per_masa[{idx}].bruto"] = R.last
                p = self.pph_masa(m, b, idx)
                self.bind[f"per_masa[{idx}].pph21"] = R.last
                d = self.dtp(m, p, False)
                if d:
                    R.calc(f"PPh 21 dipotong dari pegawai masa {BULAN[m['bulan']]} = terutang - DTP", f"{p} - {d}")
                    self.bind[f"per_masa[{idx}].pph21_dipotong"] = R.last
                    self.bind[f"per_masa[{idx}].pph21_dtp"] = self.bind[f"per_masa[{idx}].pph21"]
                else:
                    self.bind[f"per_masa[{idx}].pph21_dipotong"] = self.bind[f"per_masa[{idx}].pph21"]
                row.update(bruto=b, pph21=p, pph21_dipotong=p - d)
                if self.has_dtp():
                    row["pph21_dtp"] = d
                cache[key] = idx
            out_masa.append(row)
            brutos.append(row["bruto"])
            terutang.append(row["pph21"])
            dipotong.append(row["pph21_dipotong"])
        res = {"per_masa": out_masa}
        if getattr(self, "setahun", None):
            res["setahun"] = dict(self.setahun)
            res["setahun"].update(self.extra_out)
            # bind per_masa row of last masa already handled
        return res

    def has_dtp(self):
        return False

    def dtp_masa_changes(self, m):
        return False

    def no_cache(self, m):
        return False

    def steps_with_bindings(self, res):
        steps = [dict(s) for s in self.R.steps]
        byno = {s["no"]: s for s in steps}
        for path, no in self.bind.items():
            byno[no].setdefault("keluaran", []).append(path)
        return steps
