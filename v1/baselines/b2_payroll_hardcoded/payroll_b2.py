"""Baseline B2: payroll calculator Perusahaan X gaya hard-coded (TANPA knowledge base).

Pembanding "tanpa KB" untuk demo: seluruh kebijakan perusahaan (prorata hari kerja, kenaikan gaji tengah bulan,
tunjangan tetap/prorata, BPJS, THR, kompensasi, OTA, lembur, komisi, take home pay) dan konstantanya DITANAM DI KODE,
seperti kalkulator payroll pada umumnya. Pajak dihitung oleh baseline B1 (pph21_b1, dibekukan di tag `b1-frozen`,
tidak diubah). Ditulis dari spesifikasi xlsx v8 (research_plan.md Lampiran D, dataset/02_studi_kasus) dan teks
regulasi, tidak memakai engine/ maupun berkas KB. Kontrak presisi: uang int, Fraction, tanpa float/round().

    from baselines.b2_payroll_hardcoded.payroll_b2 import hitung
    hasil = hitung(kasus)        # kasus dengan data_hr (format sama dengan kalkulator KB)

Perbedaan mekanisme dengan versi KB: perubahan aturan (mis. batas upah JP baru, tarif BPJS, cara prorata) di sini
berarti MENGUBAH KODE ini; di versi KB cukup mengubah berkas YAML.
"""
import calendar
from datetime import date, timedelta
from fractions import Fraction

from baselines.b1_hardcoded import konstanta as K1
from baselines.b1_hardcoded import pph21_b1 as B1

# ---------------------------------------------------------------- konstanta BPJS (ditanam)
JKM_PK = Fraction(3, 1000)          # PP 44/2015 Ps. 18(1): 0,30%
JHT_PK = Fraction(37, 1000)         # PP 46/2015 Ps. 16(1): 3,7%
JHT_PG = Fraction(2, 100)           # PP 46/2015 Ps. 16(2): 2%
JP_PK = Fraction(2, 100)            # PP 45/2015 Ps. 28: 2%
JP_PG = Fraction(1, 100)            # PP 45/2015 Ps. 28: 1%
KES_PK = Fraction(4, 100)           # Perpres 75/2019: 4%
KES_PG = Fraction(1, 100)           # Perpres 75/2019: 1%
KES_BATAS_UPAH = 12_000_000         # Perpres 75/2019: batas atas upah Rp12 juta
# PP 45/2015 Ps. 29 + surat BPJS TK tahunan: batas upah JP berlaku mulai 1 Maret
JP_BATAS_UPAH = [
    (date(2022, 3, 1), 9_077_600),
    (date(2023, 3, 1), 9_559_600),
    (date(2024, 3, 1), 10_042_300),
    (date(2025, 3, 1), 10_547_400),
    (date(2026, 3, 1), 11_086_300),
]

# kategori pajak komponen (regulasi: lembur = teratur, PER-16 Ps. 1 angka 15 / PMK 168 Ps. 5(3)a; komisi, kompensasi,
# insentif OTA = tidak teratur menurut kebijakan perusahaan; iuran JKN pegawai bukan pengurang; JHT/JP pemberi kerja
# bukan objek)
KATEGORI = {
    "gaji": "teratur", "tunjangan": "teratur", "lembur": "teratur",
    "premi_jkk": "premi_objek", "premi_jkm": "premi_objek", "premi_kes": "premi_objek",
    "iuran_jht_pegawai": "iuran_pengurang", "iuran_jp_pegawai": "iuran_pengurang",
    "thr": "tidak_teratur", "kompensasi": "tidak_teratur", "insentif_ota": "tidak_teratur", "komisi": "tidak_teratur",
}

SEPARUH = Fraction(1, 2)


def bulat(x):
    """Excel ROUND(x, 0): setengah menjauhi nol (kebijakan Perusahaan X, temuan K-12)."""
    x = Fraction(x)
    b = x.numerator // x.denominator
    s = x - b
    if x >= 0:
        return b + 1 if s >= SEPARUH else b
    return b if s <= SEPARUH else b + 1


def _tgl(s):
    return s if isinstance(s, date) else date.fromisoformat(s)


def _edate(t, n):
    m = t.month - 1 + n
    y, m = t.year + m // 12, m % 12 + 1
    return date(y, m, min(t.day, calendar.monthrange(y, m)[1]))


def _datedif_bulan(a, c):
    n = (c.year - a.year) * 12 + (c.month - a.month)
    return n - 1 if c.day < a.day else n


def jp_batas_upah(tgl):
    berlaku = [v for mulai, v in JP_BATAS_UPAH if mulai <= tgl]
    if not berlaku:
        raise ValueError(f"batas upah JP tidak tersedia untuk {tgl}")
    return berlaku[-1]


def _persen(teks):
    return Fraction(str(teks)) / 100


# ---------------------------------------------------------------- komponen gaji per bulan

def gaji(hr, tahun, b, per):
    """Gaji: gaji pokok x hari kerja aktual / hari kerja penuh; bulan kenaikan di tengah bulan dipecah per hari kerja."""
    naik = _tgl(hr["kenaikan_tanggal"])
    bulan_naik = naik.month if naik.year == tahun else 0
    gp, nom = hr["gaji_pokok"], hr["kenaikan_nominal"]
    if bulan_naik and b == bulan_naik and naik.day > 1:
        return bulat(Fraction(gp * hr["kenaikan_hk_sebelum"] + (gp + nom) * hr["kenaikan_hk_sesudah"], per["hk_penuh"]))
    return bulat(Fraction(gaji_berlaku(hr, tahun, b) * per["hk_aktual"], per["hk_penuh"]))


def gaji_berlaku(hr, tahun, b):
    naik = _tgl(hr["kenaikan_tanggal"])
    bulan_naik = naik.month if naik.year == tahun else 0
    sudah = bulan_naik and (b > bulan_naik or (b == bulan_naik and naik.day == 1))
    return hr["gaji_pokok"] + (hr["kenaikan_nominal"] if sudah else 0)


def tunjangan(hr, tahun, b, per):
    """Tunjangan tetap dibayar penuh, tunjangan prorata x hari kerja aktual / penuh."""
    naik = _tgl(hr["kenaikan_tanggal"])
    bulan_naik = naik.month if naik.year == tahun else 0
    if bulan_naik and b == bulan_naik and naik.day > 1:
        return bulat(Fraction(hr["tunjangan_tetap_lama"] * hr["kenaikan_hari_sebelum"]
                              + hr["tunjangan_prorata_lama"] * hr["kenaikan_hk_sebelum"]
                              + hr["tunjangan_tetap_baru"] * hr["kenaikan_hari_sesudah"]
                              + hr["tunjangan_prorata_baru"] * hr["kenaikan_hk_sesudah"], per["hk_penuh"]))
    if bulan_naik and (b > bulan_naik or (b == bulan_naik and naik.day == 1)):
        tetap, pro = hr["tunjangan_tetap_baru"], hr["tunjangan_prorata_baru"]
    else:
        tetap, pro = hr["tunjangan_tetap_lama"], hr["tunjangan_prorata_lama"]
    return bulat(tetap + Fraction(pro * per["hk_aktual"], per["hk_penuh"]))


def bpjs(hr, tahun, b, bulan_terakhir):
    """Premi (pemberi kerja) dan iuran (pegawai) BPJS; dasar upah = gaji pokok berlaku."""
    upah = gaji_berlaku(hr, tahun, b)
    tk = b >= hr["bpjs_tk_mulai_bulan"]
    kes = b >= hr["bpjs_kes_mulai_bulan"] and not (b == bulan_terakhir and bulan_terakhir != 12)  # tidak dibayar di bulan resign
    batas_jp = jp_batas_upah(date(tahun, b, 1))
    nol = lambda x, aktif: bulat(x) if aktif else 0
    return {
        "premi_jkk": nol(_persen(hr["kelas_jkk_persen"]) * upah, tk),
        "premi_jkm": nol(JKM_PK * upah, tk),
        "premi_kes": nol(KES_PK * min(upah, KES_BATAS_UPAH), kes),
        "premi_jht_pk": nol(JHT_PK * upah, tk),
        "premi_jp_pk": nol(JP_PK * min(upah, batas_jp), tk),
        "iuran_jht_pegawai": nol(JHT_PG * upah, tk),
        "iuran_jp_pegawai": nol(JP_PG * min(upah, batas_jp), tk),
        "iuran_kes_pegawai": nol(KES_PG * min(upah, KES_BATAS_UPAH), kes),
    }


def bulan_thr(hr):
    """THR masuk masa pajak saat terutang: tanggal bayar atau Lebaran, mana yang lebih dahulu."""
    return min(_tgl(hr["tanggal_thr_bayar"]), _tgl(hr["tanggal_lebaran"])).month


def thr(hr):
    """THR = gaji pokok (termasuk kenaikan bila efektif > 1 bulan sebelum Lebaran) x hari kerja s.d. Lebaran / hari setahun."""
    lebaran, masuk, naik = _tgl(hr["tanggal_lebaran"]), _tgl(hr["tanggal_masuk"]), _tgl(hr["kenaikan_tanggal"])
    dasar = hr["gaji_pokok"] + (hr["kenaikan_nominal"] if _edate(lebaran, -1) > naik else 0)
    awal_setahun = _edate(lebaran + timedelta(days=1), -12)
    hari_setahun = (lebaran - awal_setahun).days
    hari_kerja = min((lebaran - masuk).days, hari_setahun)
    return bulat(Fraction(dasar * hari_kerja, hari_setahun))


def kompensasi(hr, tahun, b, per):
    """Kompensasi = persen x gaji pokok x min(bulan masa kerja, 12) / 12."""
    p = Fraction(str(per.get("kompensasi_persen", "0")))
    masa_kerja = min(_datedif_bulan(_tgl(hr["tanggal_masuk_awal_bulan"]), date(tahun, b, 1)) + 1, 12)
    return bulat(p * hr["gaji_pokok"] * masa_kerja / 12)


# ---------------------------------------------------------------- pintu masuk

def komponen_bulan(kasus):
    """{bulan: {komponen: rupiah}} menurut kebijakan Perusahaan X."""
    hr, tahun = kasus["data_hr"], kasus["tahun_pajak"]
    bulan = [m["bulan"] for m in kasus["masa"]]
    terakhir = kasus["pegawai"].get("bulan_terakhir_bekerja") or 12
    b_thr = bulan_thr(hr)
    hasil = {}
    for b in bulan:
        per = hr["per_masa"][str(b)]
        k = {"gaji": gaji(hr, tahun, b, per), "tunjangan": tunjangan(hr, tahun, b, per)}
        k.update(bpjs(hr, tahun, b, terakhir))
        k["thr"] = thr(hr) if b == b_thr else 0
        k["kompensasi"] = kompensasi(hr, tahun, b, per)
        k["insentif_ota"] = per.get("ota", 0)
        k["lembur"] = per.get("lembur", 0)
        k["komisi"] = per.get("komisi", 0)
        hasil[b] = k
    return hasil


def ke_kasus_pajak(kasus, komp):
    """Kasus kanonik untuk B1: komponen bernilai > 0 dengan kategori pajaknya."""
    k = {x: kasus[x] for x in ("id", "tahun_pajak", "cakupan", "metode", "pegawai", "pemberi_kerja") if x in kasus}
    k.update(kurs=kasus.get("kurs", {}), dtp=kasus.get("dtp", {}), masa=[])
    for b, nilai in komp.items():
        k["masa"].append({"bulan": b, "komponen": [{"kode": kode, "kategori": KATEGORI[kode], "satuan_periode": "bulan",
                                                     "nominal": v} for kode, v in nilai.items() if kode in KATEGORI and v > 0]})
    return k


TUNAI = ("gaji", "tunjangan", "thr", "kompensasi", "insentif_ota", "lembur", "komisi")
IURAN_PEGAWAI = ("iuran_jht_pegawai", "iuran_jp_pegawai", "iuran_kes_pegawai")


def rincian_pasal17(pkp, tahun):
    """[(bawah, atas, tarif, dasar, pajak)] memakai tabel Pasal 17 yang ditanam di B1."""
    lapisan = K1.PASAL17_PRA_HPP if tahun <= 2021 else K1.PASAL17_HPP
    hasil, bawah = [], 0
    for atas, persen in lapisan:
        if pkp <= bawah:
            break
        sampai = pkp if atas is None else min(pkp, atas)
        tarif = Fraction(persen, 100)
        hasil.append((bawah, atas, tarif, sampai - bawah, (sampai - bawah) * tarif))
        if atas is None:
            break
        bawah = atas
    return hasil


def _keluaran(v):
    if isinstance(v, Fraction):
        return v.numerator if v.denominator == 1 else str(v)
    return v


def hitung(kasus):
    if not kasus.get("data_hr"):
        h = B1.hitung(kasus)                      # komponen sudah jadi (contoh resmi): langsung pajak
        komp = None
    else:
        komp = komponen_bulan(kasus)
        h = B1.hitung(ke_kasus_pajak(kasus, komp))
    per = {}
    for b, m in h["per_masa"].items():
        r = {f: _keluaran(v) for f, v in m.items()}
        if komp is not None:
            c = komp[b]
            r.update({f"px_{x}": c[x] for x in ("gaji", "tunjangan", "premi_jkk", "premi_jkm", "premi_kes", "premi_jht_pk",
                                                 "premi_jp_pk", "kompensasi", "lembur", "komisi")})
            r.update(px_thr=c["thr"], px_ota=c["insentif_ota"], px_iuran_jht_pg=c["iuran_jht_pegawai"],
                     px_iuran_jp_pg=c["iuran_jp_pegawai"], px_iuran_kes_pg=c["iuran_kes_pegawai"])
            tunai = sum(c[x] for x in TUNAI)
            iuran = sum(c[x] for x in IURAN_PEGAWAI)
            r["px_penghasilan_tunai"] = tunai
            if kasus["metode"] == "ditanggung_pemberi_kerja":
                r["px_thp"] = tunai - iuran
            else:
                r["px_thp"] = tunai + (m.get("tunjangan_pajak") or 0) - iuran - m["pph21"] + (m.get("pph21_dtp") or 0)
        per[b] = r
    t = {f: _keluaran(v) for f, v in h["tahunan"].items()}
    rinci = None
    pkp = t.get("pkp")
    if isinstance(pkp, int):
        rinci = {"pkp": pkp, "lapisan": [{"bawah": lo, "atas": hi, "tarif": str(tr), "dasar": d,
                                          "pajak": pj.numerator if pj.denominator == 1 else str(pj)}
                                         for lo, hi, tr, d, pj in rincian_pasal17(pkp, kasus["tahun_pajak"])]}
    return {"per_masa": per, "tahunan": t, "rincian_pasal17": rinci}
