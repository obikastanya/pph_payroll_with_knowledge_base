# -*- coding: utf-8 -*-
"""Build contoh.json for the sealed unseen changes U01..U16.

DOKUMEN FIKTIF UNTUK PENELITIAN. Every change is applied ALONE on top of
the rules in force in 2026 (class Engine in mesin.py). For every example the
same input is also run through the 2026 rules; the flag
"perubahan_berpengaruh" must agree with whether the outputs differ.
"""
import datetime as dt
import json
import sys
from pathlib import Path

from mesin import (BULAN, Engine, KAT, PTKP, TABLES, Rec, pct, rp, sum_expr,
                   ter_lookup, PENSION, IRREGULAR, LABEL, pension_expr)

SEALED = Path(__file__).resolve().parents[1]

KONVENSI = [
    "Setiap perubahan diterapkan sendiri-sendiri di atas aturan yang berlaku pada 2026 (PP 58/2023, PMK 168/2023, PMK 101/2016, UU HPP); perubahan lain dalam set ini tidak ikut berlaku.",
    "Hasil TER x bruto dibulatkan ke bawah ke rupiah penuh (asumsi implementasi; PP 58/2023 dan PMK 168/2023 tidak mengatur), kecuali perubahan menyatakan lain.",
    "Komponen rupiah pada input adalah nilai final yang dibayar/dipotong. Premi BPJS dihitung dari tabel bpjs.csv: JKK risiko sangat rendah 0,24%, JKM 0,30%, JKN pemberi kerja 4% (batas upah Rp12.000.000), JHT pegawai 2%, JP pegawai 1% (batas upah Rp11.086.300 sejak Maret 2026; untuk 2027-2028 diasumsikan tetap karena angka baru belum terbit; Januari-Februari 2026 Rp10.547.400).",
    "Masa Pajak Terakhir = Desember, atau bulan yang disebut pada field masa_terakhir (bulan terakhir bekerja). Jika tidak ada Desember dan tidak ada masa_terakhir, contoh hanya memuat masa selain Masa Pajak Terakhir.",
    "Biaya jabatan untuk bagian tahun pajak: paling banyak batas bulanan x jumlah bulan bekerja.",
    "Nilai negatif pada pph21 Masa Pajak Terakhir berarti lebih potong yang dikembalikan kepada pegawai (kecuali dinyatakan tidak dikembalikan).",
    "Kecuali disebut lain, pemberi kerja bukan penerima insentif PPh 21 DTP PMK 105/2025 dan pegawai memiliki NIK/NPWP valid dan terintegrasi.",
    "Ekspresi memakai notasi Python: // adalah pembagian bulat ke bawah; 'x * 225 // 10000' berarti 2,25% x x dibulatkan ke bawah.",
]


# ------------------------------------------------------------ helpers
def jp_cap(tahun, bulan):
    if tahun == 2026 and bulan <= 2:
        return 10547400
    if tahun < 2026:
        return 10547400
    return 11086300


def komp(g, t=0, tahun=2027, bulan=1, bpjs=True, **extra):
    u = g + t
    d = {"gaji_pokok": g}
    if t:
        d["tunjangan_tetap"] = t
    if bpjs:
        d["premi_jkk"] = u * 24 // 10000
        d["premi_jkm"] = u * 30 // 10000
        d["premi_jkn"] = min(u, 12000000) * 4 // 100
        d["iuran_jht_pegawai"] = u * 2 // 100
        d["iuran_jp_pegawai"] = min(u, jp_cap(tahun, bulan)) // 100
    for k, v in extra.items():
        if v:
            d[k] = v
    return d


def masa_range(b0, b1, g, t=0, tahun=2027, bpjs=True, per_bulan=None, **extra):
    out = []
    for b in range(b0, b1 + 1):
        ex = dict(extra)
        if per_bulan and b in per_bulan:
            ex.update(per_bulan[b])
        gg = ex.pop("_g", g)
        tt = ex.pop("_t", t)
        mfields = {k[1:]: ex.pop(k) for k in list(ex) if k.startswith("@")}
        m = {"bulan": b, "komponen": komp(gg, tt, tahun, b, bpjs, **ex)}
        m.update(mfields)
        out.append(m)
    return out


def inp(status, tahun, masa, metode="gross", **kw):
    d = {"status_ptkp": status, "metode": metode, "tahun_pajak": tahun}
    d.update(kw)
    d["masa"] = masa
    return d


def outputs_key(res):
    rows = [(r["bulan"], r["bruto"], r["pph21"], r["pph21_dipotong"]) for r in res["per_masa"]]
    st = res.get("setahun", {}).get("pph21_setahun")
    return rows, st


# ===================================================================== U01
PTKP_U01_DIRI, PTKP_U01_TAMBAH = 60000000, 5400000


class U01(Engine):
    def ptkp(self, n):
        if self.year < 2027:
            return super().ptkp(n)
        st, why = self.status_efektif()
        if why:
            self.R.note(why)
        kawin = st.startswith("K/")
        tg = int(st.split("/")[1])
        expr = f"{PTKP_U01_DIRI}" + (f" + {PTKP_U01_TAMBAH}" if kawin else "") + (f" + {PTKP_U01_TAMBAH} * {tg}" if tg else "")
        return self.R.calc(f"PTKP setahun status {st} menurut PMK fiktif 27/2027 Pasal 1 (diri Rp60.000.000, kawin Rp5.400.000, tiap tanggungan Rp5.400.000)", expr)


# ===================================================================== U02
class U02(Engine):
    def bj_cap_month(self):
        return 750000 if self.year >= 2027 else 500000

    def biaya_jabatan(self, bs, n):
        if self.year >= 2027:
            self.R.note("Biaya jabatan menurut Pasal 10 ayat (2) PMK 168/2023 sebagaimana diubah PMK fiktif 104/2026: 5%, paling banyak Rp9.000.000 setahun atau Rp750.000 sebulan")
        return super().biaya_jabatan(bs, n)


# ===================================================================== U03
def build_table_d():
    rows = []
    for lo, hi, bp in TABLES["PP58/A"]:
        nlo = lo - 400000 if 0 < lo < 100000000 else lo
        nhi = hi - 400000 if hi is not None and hi < 100000000 else hi
        rows.append((nlo, nhi, bp))
    return rows


TABLES["U03/D"] = build_table_d()


class U03(Engine):
    def kategori(self):
        st, _ = self.status_efektif()
        if self.year >= 2027 and st == "TK/0":
            return "D"
        return KAT[st]

    def ter_table(self, kat):
        return "U03/D" if kat == "D" else f"PP58/{kat}"


# ===================================================================== U16
def build_u16():
    new = {}
    spec = {"A": 6000000, "B": 6850000, "C": 7350000}
    for kat, zero_top in spec.items():
        rows = [(0, zero_top, 0)]
        for lo, hi, bp in TABLES["PP58/" + kat]:
            if hi is not None and hi <= zero_top:
                continue
            if lo < zero_top:
                lo = zero_top
            rows.append((lo, hi, bp))
        new[kat] = rows
    return new


for _k, _rows in build_u16().items():
    TABLES["U16/" + _k] = _rows


class U16(Engine):
    def ter_table(self, kat):
        return f"U16/{kat}" if self.year >= 2027 else f"PP58/{kat}"


# ===================================================================== U04
TAPERA_CAP_BULAN = 200000


class U04(Engine):
    def income_items(self, m):
        items = super().income_items(m)
        if self.year >= 2027 and "iuran_tapera_pemberi_kerja" in m["komponen"]:
            self.R.note(f"Masa {BULAN[m['bulan']]}: iuran Tapera dibayar pemberi kerja {rp(m['komponen']['iuran_tapera_pemberi_kerja'])} bukan penghasilan (PMK fiktif 115/2026 Pasal 2), tidak masuk bruto")
            items = [(k, v) for k, v in items if k != "iuran_tapera_pemberi_kerja"]
        return items

    def deductions(self, months, n):
        out = super().deductions(months, n)
        vals = [m["komponen"].get("iuran_tapera_pegawai", 0) for m in months]
        if self.year >= 2027 and any(vals):
            tot = self.R.calc("Iuran Tapera dibayar pegawai selama masa bekerja", sum_expr(vals))
            nb = sum(1 for v in vals if v)
            v = self.R.calc(f"Pengurang iuran Tapera = paling banyak Rp200.000 x {nb} bulan iuran (PMK fiktif 115/2026 Pasal 3)", f"min({tot}, {TAPERA_CAP_BULAN} * {nb})")
            out.append(("iuran Tapera pegawai", v))
        elif any(vals):
            self.R.note("Iuran Tapera dibayar pegawai bukan pengurang menurut PMK 168/2023 Pasal 10 ayat (1) (aturan 2026)")
        return out


# ===================================================================== U05
INTERNET_CAP = 400000


class U05(Engine):
    def bruto(self, m):
        k = m["komponen"]
        if self.year >= 2027 and "penggantian_internet" in k:
            hari = m.get("hari_kerja_jarak_jauh", 0)
            if hari >= 8:
                ex = self.R.calc(f"Masa {BULAN[m['bulan']]}: {hari} hari kerja jarak jauh (>= 8), bagian penggantian internet yang dikecualikan = paling banyak Rp400.000", f"min({k['penggantian_internet']}, {INTERNET_CAP})")
                items = super().income_items(m)
                expr = " + ".join(str(v) for _, v in items) + f" - {ex}"
                lab = " + ".join(LABEL[kk] for kk, _ in items)
                return self.R.calc(f"Penghasilan bruto masa {BULAN[m['bulan']]} = {lab} - bagian yang dikecualikan", expr)
            self.R.note(f"Masa {BULAN[m['bulan']]}: hanya {hari} hari kerja jarak jauh (< 8), penggantian internet seluruhnya penghasilan")
        return super().bruto(m)


# ===================================================================== U06
def age_on(birth, day):
    b = dt.date.fromisoformat(birth)
    d = dt.date.fromisoformat(day)
    return d.year - b.year - ((d.month, d.day) < (b.month, b.day))


class U06(Engine):
    MASA_MULAI, MASA_AKHIR, BATAS = 3, 12, 9000000

    def has_dtp(self):
        return self.year == 2027

    def no_cache(self, m):
        return True

    def pegawai_eligible(self):
        if hasattr(self, "_peg"):
            return self._peg
        i = self.inp
        R = self.R
        ok = True
        start = i["tanggal_mulai_bekerja"]
        if start < "2027-01-01":
            R.note(f"Kriteria a: mulai bekerja {start}, sebelum 1 Januari 2027 -> tidak memenuhi")
            ok = False
        else:
            R.note(f"Kriteria a: mulai bekerja {start} (paling cepat 1 Januari 2027) -> memenuhi")
        b = dt.date.fromisoformat(i["tanggal_lahir"])
        d = dt.date.fromisoformat(start)
        age = R.calc(f"Kriteria b: usia pada tanggal mulai bekerja (lahir {i['tanggal_lahir']})",
                     f"{d.year} - {b.year} - {1 if (d.month, d.day) < (b.month, b.day) else 0}")
        if age > 30:
            R.note(f"Usia {age} tahun > 30 -> tidak memenuhi")
            ok = False
        else:
            R.note(f"Usia {age} tahun <= 30 -> memenuhi")
        if not i.get("nik_npwp_terintegrasi", True):
            R.note("Kriteria c: NIK/NPWP tidak terintegrasi -> tidak memenuhi")
            ok = False
        m0 = self.masa[0]["komponen"]
        tt = R.calc(f"Kriteria d: penghasilan bruto tetap dan teratur bulan pertama bekerja = gaji pokok + tunjangan tetap (tanpa premi)",
                    f"{m0['gaji_pokok']} + {m0.get('tunjangan_tetap', 0)}")
        if tt > self.BATAS:
            R.note(f"{rp(tt)} > Rp9.000.000 -> tidak memenuhi")
            ok = False
        else:
            R.note(f"{rp(tt)} <= Rp9.000.000 -> memenuhi")
        if i.get("menerima_dtp_lain"):
            R.note("Kriteria e: menerima insentif PPh 21 DTP lain -> tidak memenuhi")
            ok = False
        self._peg = ok
        R.note("Pegawai memenuhi seluruh kriteria pegawai" if ok else "Pegawai tidak memenuhi kriteria; seluruh PPh 21 dipotong normal")
        return ok

    def dtp(self, m, pph, terakhir):
        if self.year != 2027:
            return 0
        if not self.pegawai_eligible():
            return 0
        b = m["bulan"]
        if not (self.MASA_MULAI <= b <= self.MASA_AKHIR):
            self.R.note(f"Masa {BULAN[b]} di luar Masa Pajak Maret-Desember 2027 -> tanpa DTP")
            return 0
        n0 = self.inp["pemberi_kerja"]["jumlah_pegawai_tetap_31_desember_2026"]
        n1 = m["jumlah_pegawai_tetap_akhir_bulan"]
        if n1 <= n0:
            self.R.note(f"Masa {BULAN[b]}: jumlah pegawai tetap akhir bulan {n1} tidak lebih banyak dari {n0} (31 Desember 2026) -> tanpa DTP")
            return 0
        if pph <= 0:
            self.R.note(f"Masa {BULAN[b]}: PPh 21 terutang tidak positif -> tidak ada DTP")
            return 0
        self.R.note(f"Masa {BULAN[b]}: jumlah pegawai tetap {n1} > {n0} -> PPh 21 terutang {rp(pph)} ditanggung pemerintah")
        return pph


# ===================================================================== U07
class U07(Engine):
    SEKTOR = ("padat_karya", "pariwisata")

    def has_dtp(self):
        return self.year == 2027

    def no_cache(self, m):
        return True

    def eligible(self):
        if hasattr(self, "_el"):
            return self._el
        i = self.inp
        R = self.R
        ok = True
        sek = i.get("sektor", "lainnya")
        if sek not in self.SEKTOR:
            R.note(f"Pemberi kerja sektor '{sek}' (KLU {i.get('klu', '-')}) tidak tercantum di Lampiran A PMK 105/2025 -> tanpa DTP")
            ok = False
        else:
            R.note(f"Pemberi kerja sektor '{sek}', KLU {i.get('klu')} tercantum di Lampiran A PMK 105/2025 per 1 Januari 2027 -> memenuhi")
        m0 = self.masa[0]
        k = m0["komponen"]
        tt = R.calc(f"Penghasilan bruto tetap dan teratur Masa Pajak {BULAN[m0['bulan']]} 2027 (Januari, atau bulan pertama bekerja) = gaji pokok + tunjangan tetap",
                    f"{k['gaji_pokok']} + {k.get('tunjangan_tetap', 0)}")
        if tt > 10000000:
            R.note(f"{rp(tt)} > Rp10.000.000 -> tidak memenuhi")
            ok = False
        else:
            R.note(f"{rp(tt)} <= Rp10.000.000 -> memenuhi")
        self._el = ok
        return ok

    def dtp(self, m, pph, terakhir):
        if self.year != 2027 or not self.eligible():
            return 0
        b = m["bulan"]
        if b > 6:
            if terakhir or b in (7,):
                self.R.note(f"Masa {BULAN[b]} di luar Masa Pajak Januari-Juni 2027 -> tanpa DTP")
            return 0
        if pph <= 0:
            return 0
        self.R.note(f"Masa {BULAN[b]}: PPh 21 terutang {rp(pph)} ditanggung pemerintah (PMK 105/2025 sebagaimana diubah PMK fiktif 12/2027)")
        return pph


# ===================================================================== U08
class U08(Engine):
    def status_efektif(self):
        st = self.status
        i = self.inp
        if (self.year >= 2027 and i.get("jenis_kelamin") == "P" and st.startswith("K/")
                and not i.get("keterangan_suami_tidak_berpenghasilan")
                and i.get("surat_pernyataan_tanggungan")):
            tg = st.split("/")[1]
            return f"TK/{tg}", f"karyawati kawin dengan surat pernyataan tanggungan (PMK 168/2023 Pasal 9 ayat (2) huruf a, ayat (2a), dan ayat (2b) sebagaimana diubah PMK fiktif 112/2026): PTKP diri + {tg} tanggungan, kategori TER mengikuti status TK/{tg}"
        return super().status_efektif()


# ===================================================================== U09
class U09(Engine):
    def pph_masa(self, m, bruto, idx):
        k = m["komponen"]
        irr = [(kk, k[kk]) for kk in IRREGULAR if kk in k]
        if self.year < 2027 or not irr:
            return super().pph_masa(m, bruto, idx)
        R = self.R
        B = BULAN[m["bulan"]]
        R.note(f"Masa {B} memuat penghasilan tidak teratur: dipakai PP fiktif 52/2026 Pasal 2 ayat (2a) jo. PMK fiktif 118/2026 Pasal 3")
        tt = R.calc(f"Penghasilan tidak teratur masa {B}", " + ".join(str(v) for _, v in irr))
        bt = R.calc(f"Penghasilan bruto teratur masa {B} = bruto - penghasilan tidak teratur", f"{bruto} - {tt}")
        kat = self.kategori()
        tab = self.ter_table(kat)
        st, why = self.status_efektif()
        bp = R.lookup(f"TER kategori {kat} (status {st}) untuk bruto teratur {rp(bt)}", tab, bt)
        p_t = R.calc(f"PPh 21 atas penghasilan teratur = {pct(bp)} x {rp(bt)}", f"{bt} * {bp} // 10000")
        ptkp = PTKP[st]
        R.calc(f"PTKP setahun status {st}", f"{ptkp}")
        bts = R.calc("Bruto teratur disetahunkan", f"{bt} * 12")
        iur_e = pension_expr([m])
        iurs = R.calc("Iuran JHT + JP pegawai masa ini disetahunkan", f"({iur_e}) * 12" if iur_e else "0")
        bj1 = R.calc("Biaya jabatan atas bruto teratur disetahunkan (5%, maks Rp6.000.000)", f"min({bts} * 5 // 100, 6000000)")
        pkp1 = R.calc("PKP tanpa penghasilan tidak teratur", f"max(0, ({bts} - {bj1} - {iurs} - {ptkp}) // 1000 * 1000)")
        t1 = self.pasal17(pkp1, "PPh Pasal 17 tanpa penghasilan tidak teratur")
        bts2 = R.calc("Bruto teratur disetahunkan + penghasilan tidak teratur", f"{bts} + {tt}")
        bj2 = R.calc("Biaya jabatan (5%, maks Rp6.000.000)", f"min({bts2} * 5 // 100, 6000000)")
        pkp2 = R.calc("PKP dengan penghasilan tidak teratur", f"max(0, ({bts2} - {bj2} - {iurs} - {ptkp}) // 1000 * 1000)")
        t2 = self.pasal17(pkp2, "PPh Pasal 17 dengan penghasilan tidak teratur")
        p_tt = R.calc("PPh 21 atas penghasilan tidak teratur = selisih", f"{t2} - {t1}")
        return R.calc(f"PPh 21 masa {B} = PPh teratur + PPh tidak teratur", f"{p_t} + {p_tt}")


# ===================================================================== U10
class U10(Engine):
    def zakat(self, months):
        vals = [m["komponen"].get("zakat", 0) for m in months]
        if self.year >= 2027 and any(vals):
            self.R.note("Zakat melalui pemberi kerja tidak lagi dikurangkan dalam pemotongan (Pasal 10 ayat (1) huruf c PMK 168/2023 dihapus oleh PMK fiktif 110/2026)")
            return []
        return super().zakat(months)


# ===================================================================== U11
class U11(Engine):
    def ter_base(self, m, bruto):
        if self.year < 2027:
            return bruto
        return self.R.calc(f"Dasar TER masa {BULAN[m['bulan']]} = bruto dibulatkan ke bawah hingga ribuan rupiah (PMK fiktif 116/2026 Pasal 15A ayat (1))",
                           f"{bruto} // 1000 * 1000")

    def pph_masa(self, m, bruto, idx):
        if self.year < 2027:
            return super().pph_masa(m, bruto, idx)
        base = self.ter_base(m, bruto)
        kat = self.kategori()
        tab = self.ter_table(kat)
        st, _ = self.status_efektif()
        bp = self.R.lookup(f"Tarif efektif bulanan kategori {kat} (status {st}) untuk dasar {rp(base)}", tab, base)
        return self.R.calc(f"PPh 21 masa {BULAN[m['bulan']]} = {pct(bp)} x {rp(base)}, dibulatkan ke bawah ke rupiah penuh (Pasal 15A ayat (2))",
                           f"{base} * {bp} // 10000")


# ===================================================================== U12
import calendar


class U12(Engine):
    def ter_base(self, m, bruto):
        start = self.inp.get("tanggal_mulai_bekerja")
        if self.year < 2027 or not start or m is not self.masa[0]:
            return bruto
        d = dt.date.fromisoformat(start)
        if d.year != self.year or d.month != m["bulan"] or d.day == 1:
            return bruto
        R = self.R
        H = calendar.monthrange(d.year, d.month)[1]
        h = R.calc(f"Jumlah hari kalender sejak mulai bekerja {start} s.d. akhir bulan (bulan {H} hari)", f"{H} - {d.day} + 1")
        k = m["komponen"]
        irr = sum(k.get(x, 0) for x in IRREGULAR)
        bt = R.calc("Penghasilan bruto teratur masa pertama", f"{bruto} - {irr}") if irr else bruto
        return R.calc("Bruto setara sebulan penuh = bruto teratur x hari kalender bulan / hari bekerja (dibulatkan ke bawah) + penghasilan tidak teratur (PMK fiktif 120/2026 Pasal 15B)",
                      f"{bt} * {H} // {h}" + (f" + {irr}" if irr else ""))


# ===================================================================== U13
class U13(Engine):
    def ptkp(self, n):
        v = super().ptkp(n)
        if self.year >= 2027 and n < 12 and not self.inp.get("kewajiban_subjektif_tengah_tahun"):
            return self.R.calc(f"PTKP proporsional = PTKP setahun x {n} bulan bekerja / 12 (PMK fiktif 106/2026 Pasal 15 ayat (2a))", f"{v} * {n} // 12")
        return v


# ===================================================================== U14
GOL_GROSSUP = ("I", "II", "III")


class U14(Engine):
    def applies(self):
        return self.year >= 2027 and self.inp.get("golongan") in GOL_GROSSUP

    def bruto(self, m):
        if not self.applies():
            if self.year >= 2027 and m is self.masa[0]:
                self.R.note(f"Golongan {self.inp.get('golongan')}: tidak termasuk golongan I-III, metode gross (tanpa tunjangan PPh 21)")
            return super().bruto(m)
        b = super().bruto(m)
        R = self.R
        idx = self.masa.index(m)
        terakhir = (m["bulan"] == self.masa_terakhir())
        T = 0
        it = 0
        Tstep = None
        if terakhir:
            months = self.masa[:idx + 1]
            self._prev = R.calc("PPh 21 (tunjangan PPh 21) masa-masa sebelumnya", sum_expr(self.terutang)) if self.terutang else 0
            self._prevb = R.calc("Jumlah bruto masa-masa sebelumnya", sum_expr(self.brutos)) if self.brutos else 0
            ie = pension_expr(months)
            self._iur = R.calc("Iuran JHT + JP pegawai dalam tahun berjalan", ie) if ie else 0
        while True:
            it += 1
            if not terakhir:
                tot = R.calc(f"Iterasi {it} masa {BULAN[m['bulan']]}: bruto + tunjangan PPh 21 {rp(T)}", f"{b} + {T}")
                kat = self.kategori()
                bp = R.lookup(f"TER kategori {kat} untuk {rp(tot)}", self.ter_table(kat), tot)
                T2 = R.calc(f"Iterasi {it}: PPh 21 atas {rp(tot)}", f"{tot} * {bp} // 10000")
            else:
                T2 = self._annual_T(m, idx, b, T, it)
            Tstep = R.last
            if T2 == T:
                R.note(f"Iterasi {it}: hasil sama dengan tunjangan sebelumnya -> tunjangan PPh 21 masa {BULAN[m['bulan']]} = {rp(T)}")
                break
            T = T2
            assert it < 30
        m["komponen"]["tunjangan_pph21"] = T
        self._T = getattr(self, "_T", {})
        self._T[idx] = (T, Tstep)
        return R.calc(f"Penghasilan bruto masa {BULAN[m['bulan']]} termasuk tunjangan PPh 21", f"{b} + {T}")

    def _annual_T(self, m, idx, b, T, it):
        R = self.R
        months = self.masa[:idx + 1]
        n = len(months)
        bs = R.calc(f"Iterasi {it} Masa Pajak Terakhir: bruto {n} bulan dengan tunjangan PPh 21 Desember {rp(T)}", f"{self._prevb} + {b} + {T}")
        bj = R.calc(f"Iterasi {it}: biaya jabatan", f"min({bs} * 5 // 100, 500000 * {n})")
        iur = self._iur
        st, _ = self.status_efektif()
        pk = R.calc(f"Iterasi {it}: PKP = bruto - biaya jabatan - iuran JHT/JP {rp(iur)} - PTKP {rp(PTKP[st])}", f"max(0, ({bs} - {bj} - {iur} - {PTKP[st]}) // 1000 * 1000)")
        tax = self.pasal17(pk, f"Iterasi {it}: PPh 21 setahun")
        prev = self._prev
        return R.calc(f"Iterasi {it}: tunjangan PPh 21 Desember = PPh setahun - PPh masa sebelumnya {rp(prev)}, paling sedikit nol (SK Direksi Pasal 4 ayat (3))", f"max(0, {tax} - {prev})")

    def run(self):
        res = super().run()
        if self.applies():
            for idx, (T, no) in getattr(self, "_T", {}).items():
                res["per_masa"][idx]["tunjangan_pph21"] = T
                self.bind[f"per_masa[{idx}].tunjangan_pph21"] = no
            if "setahun" in res and res["per_masa"][-1]["pph21"] < 0:
                v = -res["per_masa"][-1]["pph21"]
                self.R.calc("Lebih potong Masa Pajak Terakhir menjadi hak perusahaan karena PPh 21 ditanggung melalui tunjangan (SK Direksi Pasal 4 ayat (4))", f"0 - ({res['per_masa'][-1]['pph21']})")
                res["setahun"]["lebih_potong_menjadi_hak_perusahaan"] = v
                self.bind["setahun.lebih_potong_menjadi_hak_perusahaan"] = self.R.last
                # Lebih potong tidak dibayarkan kepada pegawai, sehingga PPh 21
                # yang dikembalikan kepada pegawai pada Masa Pajak Terakhir nol
                # (konsisten dengan perlakuan kelebihan DTP pada U06/U07).
                last = len(res["per_masa"]) - 1
                pph_last = res["per_masa"][last]["pph21"]
                res["per_masa"][last]["pph21_dipotong"] = self.R.calc(
                    f"PPh 21 yang dipotong dari/dikembalikan kepada pegawai masa {BULAN[res['per_masa'][last]['bulan']]}: lebih potong tidak dibayarkan kepada pegawai",
                    f"{pph_last} + {v}")
                self.bind[f"per_masa[{last}].pph21_dipotong"] = self.R.last
        return res

    def no_cache(self, m):
        return True


# ===================================================================== U15
class U15(Engine):
    TTD = "2027-04-12"

    def __init__(self, i):
        super().__init__(i)
        self.derived = {}
        if self.year == 2027:
            self._apply_pkb()

    def _apply_pkb(self):
        R = self.R
        i = self.inp
        dp = i["data_pegawai"]
        stop = dp.get("tanggal_berhenti")
        if stop and stop < self.TTD:
            R.note(f"Pegawai berhenti {stop}, sebelum PKB ditandatangani {self.TTD}: tidak berhak atas kenaikan maupun rapel (PKB Pasal 5 ayat (3))")
            return
        g0 = dp["gaji_pokok_lama"]
        g1 = R.calc(f"Gaji pokok baru = gaji pokok lama {rp(g0)} x 108%, dibulatkan ke atas hingga ribuan rupiah (PKB Pasal 5 ayat (1))",
                    f"({g0} * 108 + 99999) // 100000 * 1000")
        t = dp.get("tunjangan_tetap", 0)
        u0 = R.calc("Upah lama (gaji pokok lama + tunjangan tetap)", f"{g0} + {t}")
        u1 = R.calc("Upah baru (gaji pokok baru + tunjangan tetap) sebagai dasar iuran BPJS", f"{g1} + {t}")
        start = dp.get("tanggal_mulai_bekerja", "2026-01-01")
        first = 1 if start < "2027-01-01" else int(start[5:7])
        rapel_months = [m for m in self.masa if first <= m["bulan"] <= 3]
        nr = len(rapel_months)
        for m in self.masa:
            b = m["bulan"]
            k = m["komponen"]
            if b < 4:
                continue
            k["gaji_pokok"] = g1
            k["premi_jkk"] = R.calc(f"Premi JKK {BULAN[b]} = 0,24% x upah baru", f"{u1} * 24 // 10000")
            k["premi_jkm"] = R.calc(f"Premi JKM {BULAN[b]} = 0,30% x upah baru", f"{u1} * 30 // 10000")
            k["premi_jkn"] = R.calc(f"Iuran JKN pemberi kerja {BULAN[b]} = 4% x min(upah baru, Rp12.000.000)", f"min({u1}, 12000000) * 4 // 100")
            k["iuran_jht_pegawai"] = R.calc(f"Iuran JHT pegawai {BULAN[b]} = 2% x upah baru", f"{u1} * 2 // 100")
            k["iuran_jp_pegawai"] = R.calc(f"Iuran JP pegawai {BULAN[b]} = 1% x min(upah baru, Rp11.086.300)", f"min({u1}, 11086300) // 100")
            if b == 4 and nr:
                k["rapel_gaji"] = R.calc(f"Rapel gaji Januari-Maret dibayar April = selisih gaji x {nr} bulan (PKB Pasal 6)", f"({g1} - {g0}) * {nr}")
                d_jkk = (u1 * 24 // 10000 - u0 * 24 // 10000) * nr
                k["rapel_premi_jkk"] = R.calc("Rapel premi JKK = selisih premi bulanan x bulan rapel", f"({u1} * 24 // 10000 - {u0} * 24 // 10000) * {nr}")
                k["rapel_premi_jkm"] = R.calc("Rapel premi JKM = selisih premi bulanan x bulan rapel", f"({u1} * 30 // 10000 - {u0} * 30 // 10000) * {nr}")
                v = R.calc("Rapel iuran JKN pemberi kerja = selisih iuran bulanan x bulan rapel", f"(min({u1}, 12000000) * 4 // 100 - min({u0}, 12000000) * 4 // 100) * {nr}")
                if v:
                    k["rapel_premi_jkn"] = v
                k["iuran_jht_pegawai"] = R.calc("Iuran JHT pegawai April termasuk kekurangan Januari-Maret", f"{u1} * 2 // 100 + ({u1} * 2 // 100 - {u0} * 2 // 100) * {nr}")
                k["iuran_jp_pegawai"] = R.calc("Iuran JP pegawai April termasuk kekurangan Januari-Maret", f"min({u1}, 11086300) // 100 + (min({u1}, 11086300) // 100 - min({u0}, 11086300) // 100) * {nr}")
            self.derived[b] = dict(k)

    def run(self):
        res = super().run()
        for row in res["per_masa"]:
            if row["bulan"] in self.derived:
                row["komponen_setelah_pkb"] = self.derived[row["bulan"]]
        return res


ENGINES = {f"U{i:02d}": c for i, c in enumerate(
    [None, U01, U02, U03, U04, U05, U06, U07, U08, U09, U10, U11, U12, U13, U14, U15, U16])
    if c}


# ===================================================================== cases
def C(judul, berpengaruh, alasan, i):
    return dict(judul=judul, perubahan_berpengaruh=berpengaruh, alasan=alasan, input=i)


def cases():
    X = {}
    # ---------------- U01 PTKP
    X["U01"] = [
        C("K/0, gaji Rp10 juta dan iuran pensiun Rp100 ribu, setahun penuh 2027", True,
          "PTKP baru dipakai di Masa Pajak Terakhir 2027",
          inp("K/0", 2027, [{"bulan": b, "komponen": {"gaji_pokok": 10000000, "iuran_jp_pegawai": 100000}} for b in range(1, 13)])),
        C("Kasus yang sama pada tahun pajak 2026", False, "Sebelum tahun pajak 2027: PTKP PMK 101/2016",
          inp("K/0", 2026, [{"bulan": b, "komponen": {"gaji_pokok": 10000000, "iuran_jp_pegawai": 100000}} for b in range(1, 13)])),
        C("TK/0 upah Rp5,5 juta dengan BPJS, setahun penuh 2027 (lebih potong di Desember)", True,
          "PTKP baru membuat PPh setahun lebih kecil dari PPh Januari-November",
          inp("TK/0", 2027, masa_range(1, 12, 5500000))),
        C("K/3 upah Rp35 juta dan bonus Maret Rp20 juta, 2027", True, "PTKP K/3 naik Rp9.600.000",
          inp("K/3", 2027, masa_range(1, 12, 30000000, 5000000, per_bulan={3: {"bonus": 20000000}}))),
        C("TK/1 berhenti akhir Februari 2027, sebelum PMK diundangkan (berlaku surut)", True,
          "Masa Pajak Terakhir Februari 2027 dihitung ulang dengan PTKP baru melalui pembetulan SPT Masa (Pasal 3 ayat (2))",
          inp("TK/1", 2027, masa_range(1, 2, 40000000), masa_terakhir=2, tanggal_berhenti="2027-02-28")),
        C("K/2 upah Rp15 juta, tahun pajak 2028", True, "Berlaku untuk tahun pajak 2027 dan seterusnya",
          inp("K/2", 2028, masa_range(1, 12, 13000000, 2000000, tahun=2028))),
        C("TK/0 upah Rp4 juta tanpa BPJS, 2027 (PKP nihil dengan PTKP lama maupun baru)", False,
          "Neto setahun di bawah PTKP lama, sehingga PKP tetap nol",
          inp("TK/0", 2027, [{"bulan": b, "komponen": {"gaji_pokok": 4000000}} for b in range(1, 13)])),
    ]
    # ---------------- U02 biaya jabatan
    X["U02"] = [
        C("TK/0 upah Rp20 juta, setahun penuh 2027", True, "5% bruto melebihi Rp6 juta; batas baru Rp9 juta",
          inp("TK/0", 2027, masa_range(1, 12, 20000000))),
        C("Kasus yang sama pada 2026", False, "Sebelum berlaku", inp("TK/0", 2026, masa_range(1, 12, 20000000, tahun=2026))),
        C("K/1 upah Rp8 juta, 2027 (5% bruto di bawah Rp6 juta)", False, "Biaya jabatan 5% tidak mencapai batas lama",
          inp("K/1", 2027, masa_range(1, 12, 8000000))),
        C("K/0 upah Rp11 juta, 2027 (5% bruto di antara Rp6 juta dan Rp9 juta)", True, "Batas lama memotong biaya jabatan, batas baru tidak",
          inp("K/0", 2027, masa_range(1, 12, 10000000, 1000000))),
        C("TK/2 mulai bekerja Juli 2027, upah Rp25 juta", True, "Batas bulanan Rp750.000 x 6 bulan",
          inp("TK/2", 2027, masa_range(7, 12, 22000000, 3000000), tanggal_mulai_bekerja="2027-07-01")),
        C("TK/0 upah Rp20 juta, hanya Masa Pajak Januari-Maret 2027", False, "Biaya jabatan hanya dipakai di Masa Pajak Terakhir; TER tidak berubah",
          inp("TK/0", 2027, masa_range(1, 3, 20000000))),
    ]
    # ---------------- U03 kategori D
    X["U03"] = [
        C("TK/0 gaji Rp10 juta tanpa BPJS, Januari-Maret 2027", True, "TK/0 pindah ke kategori D",
          inp("TK/0", 2027, [{"bulan": b, "komponen": {"gaji_pokok": 10000000}} for b in (1, 2, 3)])),
        C("TK/1 gaji Rp10 juta, Januari-Maret 2027", False, "TK/1 tetap kategori A",
          inp("TK/1", 2027, [{"bulan": b, "komponen": {"gaji_pokok": 10000000}} for b in (1, 2, 3)])),
        C("TK/0 gaji Rp10 juta, Januari-Maret 2026", False, "Sebelum berlaku",
          inp("TK/0", 2026, [{"bulan": b, "komponen": {"gaji_pokok": 10000000}} for b in (1, 2, 3)])),
        C("TK/0 gaji Rp5,2 juta, Januari 2027", True, "Lapisan 0% kategori D hanya sampai Rp5.000.000",
          inp("TK/0", 2027, [{"bulan": 1, "komponen": {"gaji_pokok": 5200000}}])),
        C("TK/0 upah Rp12,9 juta dengan BPJS, setahun penuh 2027", True, "Potongan Januari-November naik; Desember menyesuaikan; PPh setahun sama",
          inp("TK/0", 2027, masa_range(1, 12, 12900000))),
        C("TK/0 gaji Rp110 juta tanpa BPJS, Januari 2027", False, "Batas lapisan di atas Rp100 juta tidak bergeser; tarif sama 25%",
          inp("TK/0", 2027, [{"bulan": 1, "komponen": {"gaji_pokok": 110000000}}])),
        C("Karyawati kawin (status keluarga K/1) tanpa keterangan suami tidak berpenghasilan, gaji Rp8,3 juta, Januari 2027", True,
          "PTKP-nya sebesar PTKP diri sendiri, sehingga masuk kategori D",
          inp("K/1", 2027, [{"bulan": 1, "komponen": {"gaji_pokok": 8300000}}], jenis_kelamin="P",
              keterangan_suami_tidak_berpenghasilan=False)),
    ]
    # ---------------- U16 TER lapisan bawah
    X["U16"] = [
        C("TK/0 gaji Rp5,9 juta tanpa BPJS, Januari 2027", True, "Lapisan 0% kategori A diperluas sampai Rp6.000.000",
          inp("TK/0", 2027, [{"bulan": 1, "komponen": {"gaji_pokok": 5900000}}])),
        C("Kasus yang sama, Januari 2026", False, "Sebelum berlaku", inp("TK/0", 2026, [{"bulan": 1, "komponen": {"gaji_pokok": 5900000}}])),
        C("K/1 gaji Rp7 juta, Januari 2027", False, "Di atas lapisan yang diubah, tarif tetap 0,75%",
          inp("K/1", 2027, [{"bulan": 1, "komponen": {"gaji_pokok": 7000000}}])),
        C("K/2 gaji Rp6,6 juta, Januari 2027", True, "Lapisan 0% kategori B diperluas sampai Rp6.850.000",
          inp("K/2", 2027, [{"bulan": 1, "komponen": {"gaji_pokok": 6600000}}])),
        C("K/3 gaji Rp7,2 juta, Januari 2027", True, "Lapisan 0% kategori C diperluas sampai Rp7.350.000",
          inp("K/3", 2027, [{"bulan": 1, "komponen": {"gaji_pokok": 7200000}}])),
        C("TK/0 upah Rp5,6 juta dengan BPJS, setahun penuh 2027", True, "Potongan Januari-November menjadi nol; Desember menyesuaikan",
          inp("TK/0", 2027, masa_range(1, 12, 5600000))),
        C("TK/1 gaji Rp15 juta, Januari 2027", False, "Lapisan atas tidak berubah",
          inp("TK/1", 2027, [{"bulan": 1, "komponen": {"gaji_pokok": 15000000}}])),
    ]
    # ---------------- U04 Tapera
    tap = lambda u: {"iuran_tapera_pegawai": u * 25 // 1000, "iuran_tapera_pemberi_kerja": u * 5 // 1000}
    X["U04"] = [
        C("K/1 upah Rp10 juta, peserta Tapera, setahun penuh 2027", True,
          "Iuran Tapera pemberi kerja keluar dari bruto; iuran pegawai menjadi pengurang (dibatasi Rp200.000/bulan)",
          inp("K/1", 2027, masa_range(1, 12, 10000000, **tap(10000000)))),
        C("TK/0 upah Rp6 juta, peserta Tapera, setahun penuh 2027", True, "Iuran pegawai Rp150.000/bulan di bawah batas",
          inp("TK/0", 2027, masa_range(1, 12, 6000000, **tap(6000000)))),
        C("K/1 upah Rp10 juta, iuran Tapera, setahun penuh 2026", False, "Sebelum berlaku: iuran pemberi kerja masuk bruto, iuran pegawai bukan pengurang",
          inp("K/1", 2026, masa_range(1, 12, 10000000, tahun=2026, **tap(10000000)))),
        C("K/1 upah Rp10 juta, bukan peserta Tapera, 2027", False, "Tidak ada iuran Tapera",
          inp("K/1", 2027, masa_range(1, 12, 10000000))),
        C("TK/1 upah Rp9,5 juta, peserta Tapera, Januari-Februari 2027", True, "Bruto bulanan turun karena iuran pemberi kerja dikeluarkan",
          inp("TK/1", 2027, masa_range(1, 2, 9500000, **tap(9500000)))),
        C("K/0 mulai bekerja Oktober 2027, upah Rp12 juta, peserta Tapera", True, "Batas pengurang Rp200.000 x 3 bulan",
          inp("K/0", 2027, masa_range(10, 12, 12000000, **tap(12000000)), tanggal_mulai_bekerja="2027-10-01")),
    ]
    # ---------------- U05 internet
    X["U05"] = [
        C("TK/0 gaji Rp9 juta, penggantian internet berbukti Rp350.000, 10 hari kerja jarak jauh, Januari-Februari 2027", True,
          "Seluruh penggantian dikecualikan",
          inp("TK/0", 2027, masa_range(1, 2, 9000000, bpjs=False, penggantian_internet=350000, **{"@hari_kerja_jarak_jauh": 10}))),
        C("Penggantian Rp600.000, 12 hari kerja jarak jauh, Januari 2027", True, "Hanya Rp400.000 dikecualikan",
          inp("TK/0", 2027, masa_range(1, 1, 9000000, bpjs=False, penggantian_internet=600000, **{"@hari_kerja_jarak_jauh": 12}))),
        C("Penggantian Rp600.000, hanya 5 hari kerja jarak jauh, Januari 2027", False, "Syarat paling sedikit 8 hari tidak terpenuhi",
          inp("TK/0", 2027, masa_range(1, 1, 9000000, bpjs=False, penggantian_internet=600000, **{"@hari_kerja_jarak_jauh": 5}))),
        C("Tunjangan internet tunai tetap Rp400.000, 15 hari kerja jarak jauh, Januari 2027", False,
          "Tunjangan tunai tanpa bukti tagihan tidak termasuk pengecualian",
          inp("TK/0", 2027, masa_range(1, 1, 9000000, bpjs=False, tunjangan_internet=400000, **{"@hari_kerja_jarak_jauh": 15}))),
        C("Penggantian Rp350.000, 10 hari kerja jarak jauh, Januari 2026", False, "Sebelum berlaku",
          inp("TK/0", 2026, masa_range(1, 1, 9000000, tahun=2026, bpjs=False, penggantian_internet=350000, **{"@hari_kerja_jarak_jauh": 10}))),
        C("K/0 upah Rp15 juta dengan BPJS, penggantian internet Rp450.000 setiap bulan, hari kerja jarak jauh berubah-ubah, setahun 2027", True,
          "Pengecualian hanya pada bulan dengan >= 8 hari; Desember ikut berubah",
          inp("K/0", 2027, masa_range(1, 12, 15000000, penggantian_internet=450000,
                                      per_bulan={b: {"@hari_kerja_jarak_jauh": h} for b, h in
                                                 zip(range(1, 13), [10, 10, 6, 12, 8, 7, 10, 10, 10, 4, 9, 10])}))),
    ]
    # ---------------- U06 DTP pegawai muda
    pk = {"jumlah_pegawai_tetap_31_desember_2026": 120}

    def hc(b0, b1, drop=()):
        return {b: {"@jumlah_pegawai_tetap_akhir_bulan": (115 if b in drop else 124 + b)} for b in range(b0, b1 + 1)}

    X["U06"] = [
        C("TK/0 mulai 1 Maret 2027, usia 25, upah Rp7,5 juta, pemberi kerja menambah pegawai setiap bulan", True,
          "Seluruh kriteria terpenuhi; DTP Maret-Desember; kelebihan DTP di Desember tidak dikembalikan",
          inp("TK/0", 2027, masa_range(3, 12, 7500000, per_bulan=hc(3, 12)), tanggal_lahir="2001-05-10",
              tanggal_mulai_bekerja="2027-03-01", nik_npwp_terintegrasi=True, menerima_dtp_lain=False, pemberi_kerja=pk)),
        C("Sama, tetapi usia 31 pada tanggal mulai bekerja", False, "Kriteria usia tidak terpenuhi",
          inp("TK/0", 2027, masa_range(3, 12, 7500000, per_bulan=hc(3, 12)), tanggal_lahir="1995-12-01",
              tanggal_mulai_bekerja="2027-03-01", nik_npwp_terintegrasi=True, menerima_dtp_lain=False, pemberi_kerja=pk)),
        C("Usia 26, gaji dan tunjangan tetap bulan pertama Rp9,5 juta", False, "Melebihi Rp9.000.000",
          inp("K/0", 2027, masa_range(3, 12, 8500000, 1000000, per_bulan=hc(3, 12)), tanggal_lahir="2000-08-17",
              tanggal_mulai_bekerja="2027-03-01", nik_npwp_terintegrasi=True, menerima_dtp_lain=False, pemberi_kerja=pk)),
        C("Usia 24, mulai bekerja November 2026", False, "Mulai bekerja sebelum 1 Januari 2027",
          inp("TK/0", 2027, masa_range(1, 12, 7000000, per_bulan=hc(1, 12)), tanggal_lahir="2002-02-02",
              tanggal_mulai_bekerja="2026-11-01", nik_npwp_terintegrasi=True, menerima_dtp_lain=False, pemberi_kerja=pk)),
        C("TK/0 mulai 1 Januari 2027, usia 22, upah Rp8 juta, THR Maret; jumlah pegawai turun di Juli-Agustus", True,
          "Januari-Februari di luar masa insentif; Juli-Agustus syarat pemberi kerja tidak terpenuhi",
          inp("TK/0", 2027, masa_range(1, 12, 8000000, per_bulan={**hc(1, 12, drop=(7, 8)), 3: {**hc(3, 3)[3], "thr": 8000000}}),
              tanggal_lahir="2004-09-30", tanggal_mulai_bekerja="2027-01-01", nik_npwp_terintegrasi=True,
              menerima_dtp_lain=False, pemberi_kerja=pk)),
        C("K/1 mulai 1 April 2027, usia 28, upah Rp8,5 juta lalu naik menjadi Rp11 juta sejak Agustus", True,
          "Batas Rp9 juta hanya diuji pada bulan pertama bekerja",
          inp("K/1", 2027, masa_range(4, 12, 8500000, per_bulan={**hc(4, 12), **{b: {**hc(b, b)[b], "_g": 11000000} for b in range(8, 13)}}),
              tanggal_lahir="1999-01-15", tanggal_mulai_bekerja="2027-04-01", nik_npwp_terintegrasi=True,
              menerima_dtp_lain=False, pemberi_kerja=pk)),
        C("TK/0 memenuhi kriteria a-d tetapi sudah menerima insentif PPh 21 DTP lain", False, "Kriteria e tidak terpenuhi",
          inp("TK/0", 2027, masa_range(3, 5, 7500000, per_bulan=hc(3, 5)), tanggal_lahir="2001-05-10",
              tanggal_mulai_bekerja="2027-03-01", nik_npwp_terintegrasi=True, menerima_dtp_lain=True, pemberi_kerja=pk)),
    ]
    # ---------------- U07 perpanjangan DTP
    X["U07"] = [
        C("K/1 industri tekstil (padat karya), upah Rp8 juta, setahun 2027", True,
          "DTP Januari-Juni 2027; Juli-Desember normal",
          inp("K/1", 2027, masa_range(1, 12, 8000000), sektor="padat_karya", klu="13111")),
        C("TK/0 hotel (pariwisata), upah Rp9,5 juta, THR Maret, setahun 2027", True, "DTP Januari-Juni termasuk THR",
          inp("TK/0", 2027, masa_range(1, 12, 9000000, 500000, per_bulan={3: {"thr": 9500000}}), sektor="pariwisata", klu="55110")),
        C("K/1 perusahaan perdagangan (bukan sektor Lampiran A), upah Rp8 juta, 2027", False, "Sektor tidak memenuhi",
          inp("K/1", 2027, masa_range(1, 12, 8000000), sektor="lainnya", klu="46100")),
        C("TK/1 padat karya, gaji dan tunjangan tetap Januari 2027 Rp10,5 juta", False, "Melebihi Rp10.000.000 pada Masa Pajak Januari 2027",
          inp("TK/1", 2027, masa_range(1, 6, 10000000, 500000), sektor="padat_karya", klu="15201")),
        C("K/3 padat karya, upah Rp7,2 juta, setahun 2027 (lebih potong Desember)", True,
          "DTP Januari-Juni; lebih potong Desember dikembalikan sebatas PPh yang benar-benar dipotong Juli-November",
          inp("K/3", 2027, masa_range(1, 12, 7200000), sektor="padat_karya", klu="31001")),
        C("TK/0 pariwisata, mulai bekerja 1 Maret 2027, upah Rp9 juta, Maret-Agustus", True,
          "Kriteria diukur pada bulan pertama bekerja; DTP Maret-Juni",
          inp("TK/0", 2027, masa_range(3, 8, 9000000), sektor="pariwisata", klu="55110", tanggal_mulai_bekerja="2027-03-01")),
    ]
    # ---------------- U08 karyawati
    X["U08"] = [
        C("Karyawati K/2 dengan surat pernyataan tanggungan, upah Rp12 juta, setahun 2027", True,
          "Kategori B (TK/2) dan PTKP Rp63.000.000",
          inp("K/2", 2027, masa_range(1, 12, 12000000), jenis_kelamin="P", keterangan_suami_tidak_berpenghasilan=False,
              surat_pernyataan_tanggungan=True)),
        C("Sama, tanpa surat pernyataan", False, "Syarat surat pernyataan tidak terpenuhi",
          inp("K/2", 2027, masa_range(1, 12, 12000000), jenis_kelamin="P", keterangan_suami_tidak_berpenghasilan=False,
              surat_pernyataan_tanggungan=False)),
        C("Sama dengan contoh 1, tahun 2026", False, "Sebelum berlaku",
          inp("K/2", 2026, masa_range(1, 12, 12000000, tahun=2026), jenis_kelamin="P", keterangan_suami_tidak_berpenghasilan=False,
              surat_pernyataan_tanggungan=True)),
        C("Karyawati K/3 dengan surat pernyataan, upah Rp9 juta, Januari-Februari 2027", True, "Kategori B (TK/3)",
          inp("K/3", 2027, masa_range(1, 2, 9000000), jenis_kelamin="P", keterangan_suami_tidak_berpenghasilan=False,
              surat_pernyataan_tanggungan=True)),
        C("Pegawai laki-laki K/2, upah Rp12 juta, setahun 2027", False, "Ketentuan hanya untuk karyawati kawin",
          inp("K/2", 2027, masa_range(1, 12, 12000000), jenis_kelamin="L")),
        C("Karyawati K/1 dengan keterangan kecamatan suami tidak berpenghasilan, upah Rp10 juta, setahun 2027", False,
          "Sudah memakai PTKP K/1 penuh (Pasal 9 ayat (3)); ketentuan baru tidak dipakai",
          inp("K/1", 2027, masa_range(1, 12, 10000000), jenis_kelamin="P", keterangan_suami_tidak_berpenghasilan=True,
              surat_pernyataan_tanggungan=True)),
        C("Karyawati K/0 dengan surat pernyataan (tanpa tanggungan), upah Rp10 juta, Januari 2027", False,
          "Tidak ada tanggungan; status tetap setara TK/0",
          inp("K/0", 2027, masa_range(1, 1, 10000000), jenis_kelamin="P", keterangan_suami_tidak_berpenghasilan=False,
              surat_pernyataan_tanggungan=True)),
    ]
    # ---------------- U09 penghasilan tidak teratur
    X["U09"] = [
        C("K/0 upah Rp15 juta, THR Rp15 juta di Maret, Januari-Maret 2027", True, "Masa Maret memakai metode baru",
          inp("K/0", 2027, masa_range(1, 3, 15000000, per_bulan={3: {"thr": 15000000}}))),
        C("Kasus yang sama, 2026", False, "Sebelum berlaku",
          inp("K/0", 2026, masa_range(1, 3, 15000000, tahun=2026, per_bulan={3: {"thr": 15000000}}))),
        C("K/0 upah Rp15 juta tanpa penghasilan tidak teratur, Januari 2027", False, "Tidak ada penghasilan tidak teratur",
          inp("K/0", 2027, masa_range(1, 1, 15000000))),
        C("TK/1 upah Rp20 juta, THR Maret Rp20 juta, bonus Desember Rp40 juta, setahun 2027", True,
          "Potongan Maret berubah; Desember menyesuaikan; PPh setahun sama",
          inp("TK/1", 2027, masa_range(1, 12, 18000000, 2000000, per_bulan={3: {"thr": 20000000}, 12: {"bonus": 40000000}}))),
        C("K/3 upah Rp8 juta, bonus Juni Rp3 juta, Januari-Juni 2027", True, "Masa Juni memakai metode baru",
          inp("K/3", 2027, masa_range(1, 6, 8000000, per_bulan={6: {"bonus": 3000000}}))),
        C("TK/0 upah Rp50 juta, bonus Juni Rp100 juta, Juni 2027", True, "Penghasilan besar: selisih lapisan Pasal 17",
          inp("TK/0", 2027, masa_range(6, 6, 45000000, 5000000, per_bulan={6: {"bonus": 100000000}}))),
    ]
    # ---------------- U10 zakat
    X["U10"] = [
        C("K/1 upah Rp10 juta, zakat Rp250.000/bulan melalui pemberi kerja, setahun 2027", True, "Zakat tidak lagi pengurang",
          inp("K/1", 2027, masa_range(1, 12, 10000000, zakat=250000))),
        C("Kasus yang sama, 2026", False, "Sebelum berlaku", inp("K/1", 2026, masa_range(1, 12, 10000000, tahun=2026, zakat=250000))),
        C("K/1 upah Rp10 juta tanpa zakat, 2027", False, "Tidak ada zakat", inp("K/1", 2027, masa_range(1, 12, 10000000))),
        C("TK/0 upah Rp20 juta, zakat Rp500.000, Januari-Maret 2027", False, "Zakat hanya berpengaruh di Masa Pajak Terakhir",
          inp("TK/0", 2027, masa_range(1, 3, 20000000, zakat=500000))),
        C("TK/0 upah Rp20 juta, zakat Rp500.000, berhenti akhir Juni 2027", True, "Masa Pajak Terakhir Juni tanpa pengurang zakat",
          inp("TK/0", 2027, masa_range(1, 6, 20000000, zakat=500000), masa_terakhir=6, tanggal_berhenti="2027-06-30")),
    ]
    # ---------------- U11 pembulatan
    X["U11"] = [
        C("TK/0 gaji Rp5.390.000 + lembur Rp10.700 (bruto Rp5.400.700), Januari 2027", True,
          "Pembulatan dasar ke ribuan memindahkan bruto ke lapisan 0%",
          inp("TK/0", 2027, [{"bulan": 1, "komponen": {"gaji_pokok": 5390000, "lembur": 10700}}])),
        C("Kasus yang sama, Januari 2026", False, "Sebelum berlaku",
          inp("TK/0", 2026, [{"bulan": 1, "komponen": {"gaji_pokok": 5390000, "lembur": 10700}}])),
        C("K/0 gaji Rp10 juta tanpa BPJS, Januari 2027", False, "Bruto sudah kelipatan ribuan dan hasil TER bulat",
          inp("K/0", 2027, [{"bulan": 1, "komponen": {"gaji_pokok": 10000000}}])),
        C("TK/0 upah Rp10.010.000 dengan BPJS, Januari 2027", True, "Dasar TER dibulatkan ke ribuan",
          inp("TK/0", 2027, masa_range(1, 1, 10010000))),
        C("TK/0 gaji Rp9.640.000 + lembur Rp10.400 (bruto Rp9.650.400), Januari 2027", True,
          "Pembulatan memindahkan bruto ke lapisan lebih rendah (1,75%)",
          inp("TK/0", 2027, [{"bulan": 1, "komponen": {"gaji_pokok": 9640000, "lembur": 10400}}])),
        C("K/2 upah Rp12.345.000 dengan BPJS, setahun 2027", True, "Potongan Januari-November turun sedikit; Desember menyesuaikan",
          inp("K/2", 2027, masa_range(1, 12, 12345000))),
    ]
    # ---------------- U12 bulan pertama tidak penuh
    X["U12"] = [
        C("TK/0 mulai 16 September 2027, gaji sebulan Rp12 juta dibayar prorata Rp6 juta; September-Oktober", True,
          "Tarif bulan pertama memakai bruto setara sebulan penuh",
          inp("TK/0", 2027, [{"bulan": 9, "komponen": komp(6000000, bulan=9)}, {"bulan": 10, "komponen": komp(12000000, bulan=10)}],
              tanggal_mulai_bekerja="2027-09-16")),
        C("TK/0 mulai 1 September 2027, gaji Rp12 juta", False, "Bulan pertama penuh",
          inp("TK/0", 2027, [{"bulan": 9, "komponen": komp(12000000, bulan=9)}], tanggal_mulai_bekerja="2027-09-01")),
        C("TK/0 mulai 16 September 2026, gaji prorata Rp6 juta", False, "Sebelum berlaku",
          inp("TK/0", 2026, [{"bulan": 9, "komponen": komp(6000000, tahun=2026, bulan=9)}], tanggal_mulai_bekerja="2026-09-16")),
        C("K/1 mulai 20 Februari 2027 (9 dari 28 hari), gaji sebulan Rp9 juta dibayar prorata Rp2.892.857", True,
          "Bruto setara dihitung dengan 28 hari kalender",
          inp("K/1", 2027, [{"bulan": 2, "komponen": {"gaji_pokok": 2892857}}], tanggal_mulai_bekerja="2027-02-20")),
        C("K/0 mulai 10 Juli 2027, gaji sebulan Rp20 juta (Juli prorata 22/31), Juli-Desember", True,
          "Hanya Juli yang berubah; Desember menyesuaikan; PPh setahun sama",
          inp("K/0", 2027, [{"bulan": 7, "komponen": komp(14193548, bulan=7)}] + masa_range(8, 12, 20000000),
              tanggal_mulai_bekerja="2027-07-10")),
        C("TK/1 mulai 15 Maret 2027 (17 dari 31 hari), gaji prorata Rp5.483.870 dan bonus penandatanganan Rp5 juta", True,
          "Hanya penghasilan teratur yang disetarakan; bonus ditambahkan tanpa penyetaraan",
          inp("TK/1", 2027, [{"bulan": 3, "komponen": {"gaji_pokok": 5483870, "bonus": 5000000}}], tanggal_mulai_bekerja="2027-03-15")),
    ]
    # ---------------- U13 PTKP proporsional
    X["U13"] = [
        C("K/1 mulai 1 Juli 2027, upah Rp15 juta, Juli-Desember", True, "Bekerja 6 bulan: PTKP x 6/12",
          inp("K/1", 2027, masa_range(7, 12, 15000000), tanggal_mulai_bekerja="2027-07-01", kewajiban_subjektif_tengah_tahun=False)),
        C("TK/0 upah Rp10 juta, berhenti akhir September 2027", True, "Bekerja 9 bulan: PTKP x 9/12",
          inp("TK/0", 2027, masa_range(1, 9, 10000000), masa_terakhir=9, tanggal_berhenti="2027-09-30",
              kewajiban_subjektif_tengah_tahun=False)),
        C("K/1 upah Rp15 juta, setahun penuh 2027", False, "Bekerja 12 bulan", inp("K/1", 2027, masa_range(1, 12, 15000000))),
        C("K/1 mulai 1 Juli 2026, upah Rp15 juta", False, "Sebelum berlaku",
          inp("K/1", 2026, masa_range(7, 12, 15000000, tahun=2026), tanggal_mulai_bekerja="2026-07-01", kewajiban_subjektif_tengah_tahun=False)),
        C("K/1 mulai 1 Juli 2027, Juli-September saja (belum Masa Pajak Terakhir)", False, "PTKP hanya dipakai di Masa Pajak Terakhir",
          inp("K/1", 2027, masa_range(7, 9, 15000000), tanggal_mulai_bekerja="2027-07-01", kewajiban_subjektif_tengah_tahun=False)),
        C("TK/0 mulai 1 November 2027, upah Rp6 juta, November-Desember", True, "PKP menjadi positif karena PTKP hanya 2/12",
          inp("TK/0", 2027, masa_range(11, 12, 6000000), tanggal_mulai_bekerja="2027-11-01", kewajiban_subjektif_tengah_tahun=False)),
    ]
    # ---------------- U14 gross-up perusahaan
    X["U14"] = [
        C("Golongan II, K/0, upah Rp10 juta, Januari-Februari 2027", True, "Tunjangan PPh 21 (gross-up) untuk golongan I-III",
          inp("K/0", 2027, masa_range(1, 2, 10000000), metode="sesuai_kebijakan_perusahaan", golongan="II")),
        C("Golongan IV, K/0, upah Rp10 juta, Januari-Februari 2027", False, "Golongan IV tetap metode gross",
          inp("K/0", 2027, masa_range(1, 2, 10000000), metode="sesuai_kebijakan_perusahaan", golongan="IV")),
        C("Golongan II, K/0, upah Rp10 juta, Januari-Februari 2026", False, "Kebijakan berlaku sejak masa Januari 2027",
          inp("K/0", 2026, masa_range(1, 2, 10000000, tahun=2026), metode="sesuai_kebijakan_perusahaan", golongan="II")),
        C("Golongan III, TK/1, upah Rp12 juta, THR Maret Rp12 juta, setahun 2027", True, "Gross-up bulanan dan gross-up Masa Pajak Terakhir",
          inp("TK/1", 2027, masa_range(1, 12, 11000000, 1000000, per_bulan={3: {"thr": 12000000}}),
              metode="sesuai_kebijakan_perusahaan", golongan="III")),
        C("Golongan I, TK/0, upah Rp5 juta, Januari 2027", False, "PPh 21 nol sehingga tunjangan PPh 21 nol",
          inp("TK/0", 2027, masa_range(1, 1, 5000000), metode="sesuai_kebijakan_perusahaan", golongan="I")),
        C("Golongan II, K/2, upah Rp6,97 juta, Januari-Februari 2027 (tarif berpindah lapisan karena tunjangan)", True,
          "Iterasi gross-up melewati batas lapisan TER",
          inp("K/2", 2027, masa_range(1, 2, 6570000, 400000), metode="sesuai_kebijakan_perusahaan", golongan="II")),
    ]
    # ---------------- U15 PKB rapel
    def pkb(g, t, b0=1, b1=12, tahun=2027, **dp):
        return masa_range(b0, b1, g, t, tahun=tahun), {"gaji_pokok_lama": g, "tunjangan_tetap": t, **dp}

    m1, d1 = pkb(10000000, 1000000)
    m2, d2 = pkb(10000000, 1000000, 1, 2, tanggal_berhenti="2027-02-28")
    m3, d3 = pkb(8000000, 500000, 2, 12, tanggal_mulai_bekerja="2027-02-01")
    m4, d4 = pkb(10000000, 1000000, tahun=2026)
    m5, d5 = pkb(9876000, 0, 1, 4)
    m6, d6 = pkb(15000000, 2000000)
    X["U15"] = [
        C("K/1 gaji pokok Rp10 juta + tunjangan tetap Rp1 juta, setahun 2027", True,
          "Gaji naik sejak April; rapel Januari-Maret dan rapel premi dibayar April",
          inp("K/1", 2027, m1, metode="gross", data_pegawai=d1)),
        C("Pegawai yang berhenti akhir Februari 2027", False, "Berhenti sebelum PKB ditandatangani: tidak berhak rapel",
          inp("TK/0", 2027, m2, masa_terakhir=2, data_pegawai=d2)),
        C("TK/1 mulai bekerja 1 Februari 2027, gaji pokok Rp8 juta + tunjangan Rp500 ribu", True, "Rapel Februari-Maret saja",
          inp("TK/1", 2027, m3, data_pegawai=d3)),
        C("Pegawai yang sama dengan contoh 1, tahun 2026", False, "PKB berlaku sejak 1 Januari 2027",
          inp("K/1", 2026, m4, data_pegawai=d4)),
        C("TK/0 gaji pokok Rp9.876.000, Januari-April 2027", True, "Pembulatan gaji baru ke atas ribuan; April memuat rapel",
          inp("TK/0", 2027, m5, data_pegawai=d5)),
        C("K/2 gaji pokok Rp15 juta + tunjangan Rp2 juta (di atas batas upah JKN), setahun 2027", True,
          "Rapel iuran JKN nihil karena upah lama dan baru di atas Rp12 juta",
          inp("K/2", 2027, m6, data_pegawai=d6)),
    ]
    return X


# ===================================================================== build
def run_one(uid, case):
    Eng = ENGINES[uid]
    i_new = json.loads(json.dumps(case["input"]))
    e = Eng(i_new)
    res = e.run()
    steps = e.steps_with_bindings(res)
    b = Engine(json.loads(json.dumps(case["input"])))
    base = b.run()
    differs = outputs_key(res) != outputs_key(base)
    if uid in ("U14", "U15"):
        differs = differs or any("tunjangan_pph21" in r and r["tunjangan_pph21"] for r in res["per_masa"]) \
            or any("komponen_setelah_pkb" in r for r in res["per_masa"])
    assert differs == case["perubahan_berpengaruh"], (uid, case["judul"], res, base)
    out = {
        "judul": case["judul"],
        "perubahan_berpengaruh": case["perubahan_berpengaruh"],
        "alasan": case["alasan"],
        "input": case["input"],
        "keluaran_diharapkan": res,
        "keluaran_menurut_aturan_2026": {
            "per_masa": [{k: r[k] for k in ("bulan", "bruto", "pph21", "pph21_dipotong")} for r in base["per_masa"]],
            **({"pph21_setahun": base["setahun"]["pph21_setahun"]} if "setahun" in base else {}),
        },
        "langkah": steps,
    }
    return out


def main():
    X = cases()
    summary = {}
    for uid, lst in X.items():
        ex = []
        for n, c in enumerate(lst, 1):
            o = run_one(uid, c)
            o = {"id": f"{uid}-C{n}", **o}
            ex.append(o)
        tabs = {}
        if uid == "U03":
            tabs["U03/D"] = TABLES["U03/D"]
        if uid == "U16":
            tabs.update({k: v for k, v in TABLES.items() if k.startswith("U16/")})
        doc = {
            "id": uid,
            "catatan": "DOKUMEN FIKTIF UNTUK PENELITIAN. Contoh perhitungan untuk perubahan tak terlihat " + uid + ".",
            "konvensi": KONVENSI,
            "tabel_perubahan": {k: [[lo, hi, bp] for lo, hi, bp in v] for k, v in tabs.items()},
            "contoh": ex,
        }
        d = SEALED / uid
        d.mkdir(parents=True, exist_ok=True)
        (d / "contoh.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        summary[uid] = len(ex)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
