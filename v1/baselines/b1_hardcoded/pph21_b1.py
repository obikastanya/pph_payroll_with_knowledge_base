"""Baseline B1: kalkulator PPh 21 pegawai tetap gaya hard-coded (research_plan.md §10, WP6).

Ditulis langsung dari kb/regulasi/KODIFIKASI.md, TANPA memakai engine/ maupun KB YAML, agar
menjadi versi independen untuk differential testing (V2). Aturan dan konstanta ada di kode.
Tunduk pada kontrak presisi: uang int, pecahan eksak (Fraction), tanpa float/round().

Pemakaian:
    from baselines.b1_hardcoded.pph21_b1 import hitung
    hasil = hitung(kasus_kanonik)            # varian tafsir default
    hasil = hitung(kasus_kanonik, {"REG-BJ-02": "b"})
"""
from fractions import Fraction

from . import konstanta as K

VARIAN_DEFAULT = {
    "BULAT-TER-01": "bawah", "BULAT-BRUTO-01": "bawah", "BULAT-BJ-01": "bawah",
    "BULAT-PROPORSI-01": "bawah", "BULAT-P16-01": "setengah_menjauhi_nol", "BULAT-GU-01": "bawah",
    "BULAT-P17-01": "bawah", "REG-BJ-02": "a", "REG-DITANGGUNG-T": "a",
}
SEPARUH = Fraction(1, 2)


class KasusTidakDidukung(ValueError):
    pass


# ---------------------------------------------------------------- aritmetika & pembulatan

def _lantai(x):
    x = Fraction(x)
    return x.numerator // x.denominator


def bulat(x, mode):
    x = Fraction(x)
    b = _lantai(x)
    s = x - b
    if s == 0 or mode == "bawah":
        return b
    if mode == "atas":
        return b + 1
    if mode == "setengah_atas":
        return b + 1 if s >= SEPARUH else b
    if mode == "setengah_menjauhi_nol":
        if x >= 0:
            return b + 1 if s >= SEPARUH else b
        return b if s <= SEPARUH else b + 1
    if mode == "setengah_genap":
        if s != SEPARUH:
            return b + 1 if s > SEPARUH else b
        return b if b % 2 == 0 else b + 1
    raise ValueError(f"mode pembulatan tidak dikenal: {mode}")


def _ribuan_bawah(x):
    return _lantai(Fraction(x) / 1000) * 1000


# ---------------------------------------------------------------- tabel

def tarif_ter(kategori, bruto):
    if not isinstance(bruto, int):
        raise ValueError("bruto wajib int sebelum lookup TER")
    for bawah, atas, t in K.TER[kategori]:
        if (bruto >= 0 if bawah == 0 else bruto > bawah) and (atas is None or bruto <= atas):
            return Fraction(t)
    raise ValueError(f"bruto {bruto} tidak tercakup TER {kategori}")


def pasal17(pkp, tahun):
    lapisan = K.PASAL17_PRA_HPP if tahun <= 2021 else K.PASAL17_HPP
    pajak, bawah = Fraction(0), 0
    for atas, persen in lapisan:
        if pkp <= bawah:
            break
        bagian = (pkp if atas is None else min(pkp, atas)) - bawah
        pajak += Fraction(bagian * persen, 100)
        if atas is None:
            break
        bawah = atas
    return pajak


# ---------------------------------------------------------------- PTKP & kategori

def status_efektif(pegawai):
    """REG-PTKP-03: karyawati kawin hanya PTKP diri, kecuali suami terbukti tidak berpenghasilan."""
    status = pegawai["status_ptkp"]
    if pegawai.get("jenis_kelamin") == "P" and status.startswith("K/") \
            and not pegawai.get("suami_tidak_berpenghasilan_terbukti", False):
        return "TK/0"
    return status


def ptkp(status):
    kawin = status.startswith("K/")
    n = int(status.split("/")[-1])
    return K.PTKP_DIRI + (K.PTKP_KAWIN if kawin else 0) + K.PTKP_TANGGUNGAN * min(n, 3)


# ---------------------------------------------------------------- komponen

def _nilai_komponen(k, kasus, sebulan):
    if "valas" in k:
        v = k["valas"]
        n = v["jumlah"] * kasus["kurs"][v["mata_uang"]]
    else:
        n = k["nominal"]
    if sebulan and k.get("satuan_periode") == "minggu":
        n = n * 4
    elif sebulan and k.get("satuan_periode") == "hari":
        n = n * kasus["pegawai"]["hari_kerja_sebulan"]
    return n


def _natura_objek(kasus, bulan):
    tahun = kasus["tahun_pajak"]
    if (tahun, bulan or 12) >= (2023, 7):        # PMK 66/2023 berlaku 1-7-2023
        return True
    return kasus["pemberi_kerja"].get("jenis") == "deemed_profit"   # PER-16 (contoh I.10)


def _rincian_masa(kasus, masa):
    r = {"teratur": 0, "tidak_teratur": 0, "premi": 0, "natura": 0, "iuran_pensiun": 0,
         "iuran_jht": 0, "zakat": 0, "rapel": 0}
    for k in masa["komponen"]:
        n = _nilai_komponen(k, kasus, sebulan=True)
        kat = k["kategori"]
        if kat == "teratur":
            r["teratur"] += n
        elif kat == "tidak_teratur":
            r["tidak_teratur"] += n
        elif kat == "premi_objek":
            r["premi"] += n
        elif kat == "natura":
            if _natura_objek(kasus, masa["bulan"]):
                r["natura"] += n
        elif kat == "iuran_pengurang":
            r["iuran_jht" if "jht" in k["kode"] else "iuran_pensiun"] += n
        elif kat == "zakat":
            r["zakat"] += n
        elif kat == "rapel":
            r["rapel"] += n
        else:
            raise KasusTidakDidukung(f"kategori {kat}")
    return r


def _n_subjektif(p):
    a, b = p.get("subjektif_mulai_bulan"), p.get("subjektif_akhir_bulan")
    if a and b:
        return b - a + 1
    if a:
        return 12 - a + 1
    if b:
        return b
    return 12


def _bulan_terakhir(kasus, daftar_bulan):
    if kasus["cakupan"] != "setahun":
        return None
    return kasus["pegawai"].get("bulan_terakhir_bekerja") or 12


def _berhak_dtp(kasus, bulan_pertama, rincian_pertama):
    tahun, klu = kasus["tahun_pajak"], kasus["pemberi_kerja"].get("klu")
    if not klu:
        return False, set()
    masa = set()
    for reg, sektor, mulai, akhir, kumpulan in K.DTP_KLU:
        if klu in kumpulan and int(mulai[:4]) == tahun:
            masa |= set(range(int(mulai[5:7]), int(akhir[5:7]) + 1))
    if not masa:
        return False, set()
    kontrak = kasus.get("dtp", {}).get("penghasilan_tetap_teratur_kontrak_januari")
    tetap = kontrak if kontrak is not None else rincian_pertama["teratur"]
    return tetap <= K.DTP_BATAS_PENGHASILAN_TETAP, masa


def _biaya_jabatan_setahun(bruto_per_bulan, varian):
    n = len(bruto_per_bulan)
    total = sum(bruto_per_bulan)
    if varian["REG-BJ-02"] == "b":
        return sum(min(bulat(Fraction(b * K.BJ_PERSEN, 100), varian["BULAT-BJ-01"]), K.BJ_MAKS_BULAN)
                   for b in bruto_per_bulan)
    return min(bulat(Fraction(total * K.BJ_PERSEN, 100), varian["BULAT-BJ-01"]),
               K.BJ_MAKS_BULAN * n, K.BJ_MAKS_TAHUN)


def _tahunan(kasus, bruto_bulan, iuran, zakat, varian, status):
    """Perhitungan setahun/bagian tahun (REG-MT-*, R24-04, R16-08). Kembalikan dict fakta."""
    tahun = kasus["tahun_pajak"]
    t = {"bruto_setahun": sum(bruto_bulan)}
    t["biaya_jabatan"] = _biaya_jabatan_setahun(bruto_bulan, varian)
    t["iuran_pengurang"] = iuran
    t["zakat"] = zakat
    t["neto_setahun"] = t["bruto_setahun"] - t["biaya_jabatan"] - iuran - zakat
    t["ptkp"] = ptkp(status)
    n_sub = _n_subjektif(kasus["pegawai"])
    if n_sub < 12:
        neto_dis = Fraction(t["neto_setahun"] * 12, n_sub)
        t["neto_disetahunkan"] = bulat(neto_dis, "bawah") if neto_dis.denominator != 1 else int(neto_dis)
        t["pkp"] = max(0, _ribuan_bawah(neto_dis - t["ptkp"]))
        t["pph21_disetahunkan"] = bulat(pasal17(t["pkp"], tahun), varian["BULAT-P17-01"])
        t["pph21_setahun"] = bulat(Fraction(t["pph21_disetahunkan"] * n_sub, 12), varian["BULAT-PROPORSI-01"])
    else:
        t["pkp"] = max(0, _ribuan_bawah(t["neto_setahun"] - t["ptkp"]))
        t["pph21_setahun"] = bulat(pasal17(t["pkp"], tahun), varian["BULAT-P17-01"])
    return t


# ---------------------------------------------------------------- rezim TER (2024-)

def _pph_ter(kategori, bruto, varian):
    r = tarif_ter(kategori, bruto)
    return r, bulat(r * bruto, varian["BULAT-TER-01"])


def _grossup_ter(kategori, b, varian):
    """Titik tetap terkecil T = PPh_int(b + T) (iterasi Kleene dari 0)."""
    t = 0
    for _ in range(10_000):
        _, baru = _pph_ter(kategori, b + t, varian)
        if baru == t:
            return t
        t = baru
    raise RuntimeError("gross-up TER tidak konvergen")


def _hitung_ter(kasus, varian):
    peg = kasus["pegawai"]
    status = status_efektif(peg)
    kategori = K.KATEGORI_TER[status]
    masa = sorted(kasus["masa"], key=lambda m: m["bulan"])
    bulan = [m["bulan"] for m in masa]
    terakhir = _bulan_terakhir(kasus, bulan)
    gross_up = kasus["metode"] in ("gross_up", "ditanggung_pemberi_kerja")
    rinci = {m["bulan"]: _rincian_masa(kasus, m) for m in masa}
    per = {}
    for b in bulan:
        r = rinci[b]
        bruto = bulat(r["teratur"] + r["tidak_teratur"] + r["premi"] + r["natura"] + r["rapel"],
                      varian["BULAT-BRUTO-01"])
        per[b] = {"bruto": bruto}
        if (terakhir is not None and b == terakhir):
            continue
        if gross_up:
            tunj = _grossup_ter(kategori, bruto, varian)
            per[b]["tunjangan_pajak"] = tunj
            per[b]["bruto"] = bruto = bruto + tunj
        tarif, pph = _pph_ter(kategori, bruto, varian)
        per[b].update(kategori_ter=kategori, tarif_ter=tarif, pph21=pph)
    tahunan = {}
    if terakhir is not None:
        iuran = sum(r["iuran_pensiun"] + r["iuran_jht"] for r in rinci.values())
        zakat = sum(r["zakat"] for r in rinci.values())
        dipotong = sum(per[b]["pph21"] for b in bulan if not (terakhir is not None and b == terakhir))
        dasar_terakhir = per[terakhir]["bruto"]

        def hitung_akhir(tunj):
            per[terakhir]["bruto"] = dasar_terakhir + tunj
            t = _tahunan(kasus, [per[b]["bruto"] for b in bulan], iuran, zakat, varian, status)
            return t, t["pph21_setahun"] - dipotong

        tunj = 0
        tahunan, akhir = hitung_akhir(0)
        if gross_up:
            for _ in range(10_000):
                if akhir == tunj:
                    break
                tunj = akhir
                tahunan, akhir = hitung_akhir(tunj)
            per[terakhir]["tunjangan_pajak"] = tunj
        tahunan["pph21_dipotong_sebelumnya"] = dipotong
        tahunan["pph21_masa_terakhir"] = akhir
        per[terakhir]["pph21"] = akhir
    # DTP (R24-DTP-01..03)
    if bulan:
        berhak, masa_dtp = _berhak_dtp(kasus, bulan[0], rinci[bulan[0]])
        if kasus["pemberi_kerja"].get("klu"):
            tahunan["berhak_dtp"] = berhak
        dtp_lalu = 0
        for b in bulan:
            pph = per[b].get("pph21")
            if pph is None:
                continue
            fasilitas = berhak and b in masa_dtp
            if not (terakhir is not None and b == terakhir):
                per[b]["pph21_dtp"] = pph if fasilitas else 0
                dtp_lalu += per[b]["pph21_dtp"]
            elif pph >= 0:
                per[b]["pph21_dtp"] = pph if fasilitas else 0
                tahunan["lebih_bayar_dikembalikan"] = 0
            else:
                kembali = max(0, -pph - dtp_lalu)
                per[b]["pph21_dtp"] = pph + kembali if berhak else 0
                tahunan["lebih_bayar_dikembalikan"] = kembali
    return {"per_masa": per, "tahunan": tahunan}


# ---------------------------------------------------------------- rezim disetahunkan (PER-16; s.d. 2023)

def _n_disetahunkan(peg):
    if peg.get("bulan_kerja_diketahui"):
        return peg["bulan_kerja_diketahui"]
    if peg.get("bulan_masuk") and not peg.get("subjektif_mulai_bulan"):
        return 12 - peg["bulan_masuk"] + 1
    return 12


def _pph_setahun_dari(bruto_setahun, iuran_setahun, status, tahun, varian):
    bj = min(bulat(Fraction(bruto_setahun * K.BJ_PERSEN, 100), varian["BULAT-BJ-01"]), K.BJ_MAKS_TAHUN)
    neto = bruto_setahun - bj - iuran_setahun
    pkp = max(0, _ribuan_bawah(neto - ptkp(status)))
    return pkp, bulat(pasal17(pkp, tahun), varian["BULAT-P17-01"])


def _hitung_per16(kasus, varian):
    peg = kasus["pegawai"]
    tahun = kasus["tahun_pajak"]
    status = status_efektif(peg)
    n_tahun = _n_disetahunkan(peg)
    masa = sorted(kasus["masa"], key=lambda m: (m["bulan"] is None, m["bulan"] or 0))
    bulan = [m["bulan"] for m in masa]
    terakhir = _bulan_terakhir(kasus, bulan)
    rinci = {m["bulan"]: _rincian_masa(kasus, m) for m in masa}
    pembagi_periode = {"mingguan": 4, "harian": peg.get("hari_kerja_sebulan")}.get(peg.get("periode_gaji"))
    per, tahunan = {}, {}
    for b in bulan:
        r = rinci[b]
        bt = r["teratur"] + r["premi"] + r["natura"]
        f = {"bruto": bt + r["tidak_teratur"] if (terakhir is not None and b == terakhir) else bt}
        per[b] = f
        if (terakhir is not None and b == terakhir):
            continue
        bj = min(bulat(Fraction(bt * K.BJ_PERSEN, 100), varian["BULAT-BJ-01"]), K.BJ_MAKS_BULAN)
        iuran = r["iuran_pensiun"] + r["iuran_jht"]
        f.update(biaya_jabatan_bulanan=bj, iuran_pensiun_bulanan=r["iuran_pensiun"],
                 iuran_jht_bulanan=r["iuran_jht"], total_pengurang_bulanan=bj + iuran,
                 neto_sebulan=bt - bj - iuran, ptkp=ptkp(status))
        f["neto_disetahunkan_bulanan"] = n_tahun * f["neto_sebulan"]
        f["pkp_bulanan"] = max(0, _ribuan_bawah(f["neto_disetahunkan_bulanan"] - f["ptkp"]))
        f["pph21_setahun_bulanan"] = bulat(pasal17(f["pkp_bulanan"], tahun), varian["BULAT-P17-01"])
        n_sub = _n_subjektif(peg)
        if n_sub < 12 and peg.get("subjektif_mulai_bulan"):
            f["pph21_bagian_tahun"] = bulat(Fraction(f["pph21_setahun_bulanan"] * n_sub, 12),
                                            varian["BULAT-PROPORSI-01"])
            teratur = bulat(Fraction(f["pph21_bagian_tahun"], n_sub), varian["BULAT-P16-01"])
        else:
            teratur = bulat(Fraction(f["pph21_setahun_bulanan"], n_tahun), varian["BULAT-P16-01"])
        f["pph21_teratur"] = teratur
        pph = teratur
        if r["tidak_teratur"]:
            iuran_setahun = n_tahun * iuran
            pkp_d, pph_d = _pph_setahun_dari(n_tahun * bt + r["tidak_teratur"], iuran_setahun, status, tahun, varian)
            pkp_t, pph_t = _pph_setahun_dari(n_tahun * bt, iuran_setahun, status, tahun, varian)
            tahunan.update(pkp_dengan_tidak_teratur=pkp_d, pph21_setahun_dengan_tidak_teratur=pph_d,
                           pkp_tanpa_tidak_teratur=pkp_t, pph21_setahun_tanpa_tidak_teratur=pph_t,
                           pph21_tidak_teratur=pph_d - pph_t)
            pph += pph_d - pph_t
        if r["rapel"] and kasus.get("riwayat", {}).get("rapel"):
            rp = kasus["riwayat"]["rapel"]
            tahunan["pph21_rapel"] = sum(teratur - rp["pph21_dipotong_per_bulan"] for _ in rp["bulan"])
        f["pph21_tanpa_npwp"] = bulat(Fraction(pph * 6, 5), varian["BULAT-P16-01"])
        if not peg.get("punya_npwp", True):
            pph = f["pph21_tanpa_npwp"]
        if pembagi_periode:
            f["pph21_periode"] = bulat(Fraction(pph, pembagi_periode), varian["BULAT-P16-01"])
        f["pph21"] = pph
    if terakhir is not None:
        bruto_bulan = [per[b]["bruto"] if (terakhir is not None and b == terakhir) else per[b]["bruto"] + rinci[b]["tidak_teratur"]
                       for b in bulan]
        iuran = sum(r["iuran_pensiun"] + r["iuran_jht"] for r in rinci.values())
        t = _tahunan(kasus, bruto_bulan, iuran, 0, varian, status)
        dipotong = sum(per[b]["pph21"] for b in bulan if not (terakhir is not None and b == terakhir)) + tahunan.get("pph21_rapel", 0)
        t["pph21_dipotong_sebelumnya"] = dipotong
        t["pph21_masa_terakhir"] = t["pph21_setahun"] - dipotong
        per[terakhir]["pph21"] = t["pph21_masa_terakhir"]
        tahunan.update(t)
    return {"per_masa": per, "tahunan": tahunan}


# ---------------------------------------------------------------- pintu masuk

def hitung(kasus, varian=None):
    v = dict(VARIAN_DEFAULT)
    v.update(varian or {})
    if kasus["tahun_pajak"] >= 2024:
        return _hitung_ter(kasus, v)
    if kasus["tahun_pajak"] == 2023 and kasus["metode"] == "ditanggung_pemberi_kerja" and v["REG-DITANGGUNG-T"] == "b":
        raise KasusTidakDidukung("varian gross-up 2023 untuk PPh ditanggung belum diimplementasikan di B1")
    if kasus["metode"] == "gross_up":
        raise KasusTidakDidukung("gross-up rezim PER-16 tidak diimplementasikan di B1")
    return _hitung_per16(kasus, v)


def fakta(hasil, nama, bulan=None):
    if bulan is None and nama in hasil["tahunan"]:
        return hasil["tahunan"][nama]
    m = hasil["per_masa"].get(bulan)
    if m is not None and nama in m:
        return m[nama]
    if bulan is None:
        return hasil["tahunan"].get(nama)
    return None
