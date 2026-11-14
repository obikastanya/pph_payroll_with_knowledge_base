"""Lapisan data UI: data pegawai dari dataset, konversi kasus <-> tabel isian, format tampilan.

Modul ini TIDAK menghitung pajak; angka pajak berasal dari mesin (ui/mesin.py). Yang dilakukan di sini hanya memuat
data default, menyusun kasus dari isian UI, dan memformat keluaran. Tanpa float/round (kontrak presisi).
"""
import copy
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR_KANONIK = ROOT / "dataset" / "07_kasus_uji_resmi" / "kanonik"
DIR_PERUSAHAAN = ROOT / "kb" / "perusahaan"
BERKAS_PX = DIR_PERUSAHAAN / "perusahaan_x.yaml"

NAMA_BULAN = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt",
              11: "Nov", 12: "Des", None: "Masa"}

STATUS_PTKP = ["TK/0", "TK/1", "TK/2", "TK/3", "K/0", "K/1", "K/2", "K/3", "K/I/0", "K/I/1", "K/I/2", "K/I/3"]
METODE = {"gross": "Gross (dipotong dari gaji)", "gross_up": "Gross-up (perusahaan beri tunjangan pajak)",
          "ditanggung_pemberi_kerja": "Ditanggung pemberi kerja (nett)"}
KATEGORI = {"teratur": "Teratur", "tidak_teratur": "Tidak teratur (bonus, THR)",
            "premi_objek": "Premi dibayar pemberi kerja", "natura": "Natura", "iuran_pengurang": "Iuran pegawai (pengurang)",
            "zakat": "Zakat / sumbangan wajib", "rapel": "Rapel"}
KATEGORI_BERULANG = {"teratur", "premi_objek", "iuran_pengurang", "zakat"}

# label fakta untuk tampilan; fakta lain ditampilkan dengan namanya
LABEL = {
    "bruto": "Penghasilan bruto", "kategori_ter": "Kategori TER", "tarif_ter": "Tarif TER", "pph21": "PPh 21",
    "pph21_dtp": "PPh 21 ditanggung pemerintah", "tunjangan_pajak": "Tunjangan pajak", "pph21_berjalan": "PPh 21 masa berjalan",
    "bruto_setahun": "Bruto setahun", "biaya_jabatan": "Biaya jabatan", "iuran_pengurang": "Iuran pensiun/JHT/JP pegawai",
    "zakat": "Zakat / sumbangan wajib", "neto_setahun": "Neto setahun", "neto_disetahunkan": "Neto disetahunkan",
    "ptkp": "PTKP", "pkp": "PKP (dibulatkan ke bawah ribuan)", "pph21_disetahunkan": "PPh 21 atas neto disetahunkan",
    "pph21_setahun": "PPh 21 terutang setahun", "pph21_dipotong_sebelumnya": "Sudah dipotong masa sebelumnya",
    "pph21_masa_terakhir": "PPh 21 masa terakhir", "lebih_bayar_dikembalikan": "Lebih bayar dikembalikan",
    "berhak_dtp": "Berhak DTP", "status_ptkp_efektif": "Status PTKP efektif", "n_subjektif": "Jumlah bulan subjektif",
    "gross_up": "Metode gross-up", "bruto_total_masa": "Bruto masa (termasuk tidak teratur)", "iuran_masa": "Iuran pegawai masa",
    "zakat_masa": "Zakat masa", "natura_objek": "Natura objek pajak", "tunjangan_pajak_akhir": "Tunjangan pajak masa terakhir",
    "tunjangan_pajak_berjalan": "Tunjangan pajak masa berjalan", "biaya_jabatan_bulanan": "Biaya jabatan sebulan",
    "neto_sebulan": "Neto sebulan", "pkp_bulanan": "PKP disetahunkan", "_bruto_dasar": "Bruto sebelum tunjangan pajak",
    "px_gaji": "Gaji (prorata)", "px_tunjangan": "Tunjangan", "px_thr": "THR", "px_kompensasi": "Kompensasi",
    "px_ota": "Insentif OTA", "px_lembur": "Lembur", "px_komisi": "Komisi", "px_premi_jkk": "Premi JKK (perusahaan)",
    "px_premi_jkm": "Premi JKM (perusahaan)", "px_premi_kes": "Premi BPJS Kes (perusahaan)",
    "px_premi_jht_pk": "JHT perusahaan (bukan objek)", "px_premi_jp_pk": "JP perusahaan (bukan objek)",
    "px_iuran_jht_pg": "Iuran JHT pegawai", "px_iuran_jp_pg": "Iuran JP pegawai", "px_iuran_kes_pg": "Iuran BPJS Kes pegawai",
}

# ---------------------------------------------------------------------------- sumber data pegawai (dataset)

DIR_SINTETIS = ROOT / "dataset" / "08_pegawai_sintetis"
GRUP_HR = "Data HR - Perusahaan X"
GRUP_RESMI = "Contoh resmi regulasi (komponen gaji sudah jadi)"

# komponen standar yang bisa ditambahkan admin pada mode "komponen sudah jadi": label -> (kode, kategori pajak).
# Kategori ditentukan oleh jenis komponen (klasifikasi regulasi), bukan dipilih admin.
KOMPONEN_STANDAR = {
    "Gaji pokok": ("gaji", "teratur"),
    "Tunjangan tetap": ("tunjangan", "teratur"),
    "Lembur": ("lembur", "teratur"),
    "Bonus": ("bonus", "tidak_teratur"),
    "THR": ("thr", "tidak_teratur"),
    "Premi JKK & JKM (dibayar perusahaan)": ("premi_jkk_jkm", "premi_objek"),
    "Premi BPJS Kesehatan (dibayar perusahaan)": ("premi_kes", "premi_objek"),
    "Iuran pensiun/JHT/JP (dibayar pegawai)": ("iuran_pensiun_pegawai", "iuran_pengurang"),
    "Zakat lewat pemberi kerja": ("zakat", "zakat"),
}
LABEL_KODE = {kode: lbl for lbl, (kode, _) in KOMPONEN_STANDAR.items()}
LABEL_KODE.update({
    "gaji_pokok": "Gaji pokok", "gaji_tunjangan": "Gaji + tunjangan", "gaji_tunjangan_tetap": "Gaji + tunjangan tetap",
    "tunjangan_istri_anak": "Tunjangan istri/anak", "tunjangan_jabatan": "Tunjangan jabatan",
    "tunjangan_kinerja": "Tunjangan kinerja", "tunjangan_pajak": "Tunjangan pajak", "gaji_ketiga_belas": "Gaji ke-13",
    "premi_jkk": "Premi JKK (dibayar perusahaan)", "premi_jkm": "Premi JKM (dibayar perusahaan)",
    "premi_jkk_sebulan": "Premi JKK (dibayar perusahaan)", "premi_jkm_sebulan": "Premi JKM (dibayar perusahaan)",
    "iuran_jht_pegawai": "Iuran JHT pegawai", "iuran_jht_pegawai_sebulan": "Iuran JHT pegawai",
    "iuran_pensiun_pegawai_sebulan": "Iuran pensiun pegawai", "sumbangan_keagamaan_wajib": "Sumbangan keagamaan wajib",
    "gaji_mingguan": "Upah mingguan", "gaji_harian": "Upah harian", "natura_beras": "Natura beras",
    "natura_gula": "Natura gula", "natura_beasiswa": "Natura beasiswa", "rapel_gaji_jan_mei": "Rapel gaji Jan-Mei",
    "rapel_tunjangan_kinerja": "Rapel tunjangan kinerja",
})
LABEL_KATEGORI_PAJAK = {"teratur": "penghasilan teratur", "tidak_teratur": "penghasilan tidak teratur",
                        "premi_objek": "premi dibayar pemberi kerja (objek pajak)", "natura": "natura",
                        "iuran_pengurang": "pengurang (iuran pegawai)", "zakat": "pengurang (zakat)", "rapel": "rapel"}


def label_komponen(kode):
    return LABEL_KODE.get(kode, kode.replace("_", " ").capitalize())


def _kanonik(kasus_id):
    return json.loads((DIR_KANONIK / f"{kasus_id}.json").read_text(encoding="utf-8"))


def semua_kanonik():
    hasil = []
    for p in sorted(DIR_KANONIK.glob("*.json")):
        if p.name != "indeks.json":
            hasil.append(json.loads(p.read_text(encoding="utf-8")))
    return hasil


def kasus_perusahaan_x(tahun=2023):
    from eksperimen.e8_perusahaan_x import kasus_kar_a
    return kasus_kar_a(tahun)


def daftar_data():
    """{id: {label, grup, jenis ('hr'|'komponen'), resmi, sumber}} dari dataset; urutan = urutan tampil."""
    hasil = {"KAR-A": {"label": "Karyawan A (xlsx kantor, anonim) - TK/0, 2023", "grup": GRUP_HR, "jenis": "hr", "resmi": False,
                       "sumber": "dataset/02_studi_kasus/input_karyawan_A_2023.json (payroll_calculator.xlsx v8, dianonimkan)"}}
    p = DIR_SINTETIS / "pegawai_sintetis.json"
    if p.exists():
        for d in json.loads(p.read_text(encoding="utf-8")):
            s = d["sumber_gaji"]
            hasil[d["id"]] = {"label": f"{d['id']} - {d['label']}", "grup": GRUP_HR, "jenis": "hr", "resmi": False,
                              "sumber": f"{s['keterangan']}: {s['nilai_sumber']} ({s['berkas']})"}
    for k in semua_kanonik():
        sb = k.get("sumber") or {}
        hasil[k["id"]] = {"label": f"{k['id']} - {sb.get('regulasi', '')} {sb.get('bagian', '')[:70]}", "grup": GRUP_RESMI,
                          "jenis": "komponen", "resmi": True,
                          "sumber": f"{sb.get('regulasi', '')} {sb.get('bagian', '')}, hlm. PDF {sb.get('halaman_pdf')}"}
    return hasil


def muat_data(data_id):
    """Salinan kasus dari dataset (edit di UI tidak pernah menulis ke berkas)."""
    if data_id == "KAR-A":
        return kasus_perusahaan_x(2023)
    if data_id.startswith("SINT-"):
        for d in json.loads((DIR_SINTETIS / "pegawai_sintetis.json").read_text(encoding="utf-8")):
            if d["id"] == data_id:
                return copy.deepcopy(d["kasus"])
        raise KeyError(data_id)
    return _kanonik(data_id)


def muat_kanonik(kasus_id):
    return _kanonik(kasus_id)


# ---------------------------------------------------------------------------- kasus <-> tabel

def _kunci_baris(c):
    return (c["kode"], c["kategori"], c.get("satuan_periode", "bulan"))


def kolom_bulan(b):
    return NAMA_BULAN[b]


def kasus_ke_tabel(kasus):
    """-> (baris, bulan, khusus). baris = [{kode, kategori, satuan, <NamaBulan>: int|None}], urut kemunculan.
    Komponen valas (tanpa nominal rupiah) tidak masuk tabel; dikembalikan sebagai `khusus` dan dipertahankan apa adanya."""
    bulan = [m["bulan"] for m in kasus["masa"]]
    baris, indeks, khusus = [], {}, []
    for m in kasus["masa"]:
        for c in m["komponen"]:
            if "nominal" not in c:
                khusus.append((m["bulan"], copy.deepcopy(c)))
                continue
            k = _kunci_baris(c)
            if k not in indeks:
                indeks[k] = len(baris)
                baris.append({"kode": k[0], "kategori": k[1], "satuan": k[2], **{kolom_bulan(b): None for b in bulan}})
            r = baris[indeks[k]]
            kol = kolom_bulan(m["bulan"])
            r[kol] = (r[kol] or 0) + c["nominal"]
    return baris, bulan, khusus


class IsianTidakValid(ValueError):
    pass


def rupiah_dari_sel(v, tempat):
    """Nilai sel isian -> int rupiah, atau None bila kosong. Pecahan/negatif ditolak dengan pesan yang jelas."""
    if v is None:
        return None
    try:
        import pandas as pd
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, bool):
        raise IsianTidakValid(f"{tempat}: nilai harus angka rupiah")
    if isinstance(v, str):
        s = v.strip().replace(".", "").replace(",", "")
        if not s:
            return None
        if not s.isdigit():
            raise IsianTidakValid(f"{tempat}: '{v}' bukan rupiah bulat")
        return int(s)
    if isinstance(v, int) or hasattr(v, "__index__"):
        n = int(v)
    elif isinstance(v, float) or hasattr(v, "is_integer"):
        if not v.is_integer():
            raise IsianTidakValid(f"{tempat}: {v} bukan rupiah bulat (sen tidak dipakai)")
        n = int(v)
    else:
        raise IsianTidakValid(f"{tempat}: nilai tidak dikenal {v!r}")
    if n < 0:
        raise IsianTidakValid(f"{tempat}: nominal tidak boleh negatif")
    return n


def tabel_ke_masa(baris, bulan, khusus=()):
    """Kebalikan kasus_ke_tabel. Urutan komponen per masa mengikuti urutan baris tabel."""
    masa = []
    for b in bulan:
        komp = []
        for i, r in enumerate(baris):
            kode = (r.get("kode") or "").strip()
            n = rupiah_dari_sel(r.get(kolom_bulan(b)), f"baris {i + 1} ({kode or 'tanpa kode'}), {kolom_bulan(b)}")
            if n is None:
                continue
            if not kode:
                raise IsianTidakValid(f"baris {i + 1}: kode komponen wajib diisi")
            if r.get("kategori") not in KATEGORI:
                raise IsianTidakValid(f"baris {i + 1} ({kode}): kategori wajib dipilih")
            komp.append({"kode": kode, "kategori": r["kategori"], "satuan_periode": r.get("satuan") or "bulan", "nominal": n})
        komp += [copy.deepcopy(c) for bk, c in khusus if bk == b]
        masa.append({"bulan": b, "komponen": komp})
    return masa


def baris_tetap(baris, bulan):
    """Indeks baris yang nilainya sama di semua bulan (bisa diedit sebagai satu angka 'per bulan')."""
    hasil = []
    for i, r in enumerate(baris):
        nilai = {r.get(kolom_bulan(b)) for b in bulan}
        if len(nilai) == 1 and None not in nilai and len(bulan) > 1:
            hasil.append(i)
    return hasil


def ubah_bulan(baris, bulan_lama, bulan_baru):
    """Tambah/hapus kolom bulan. Bulan baru menyalin nilai bulan pertama untuk komponen berulang (teratur, premi, iuran)."""
    acuan = kolom_bulan(bulan_lama[0]) if bulan_lama else None
    hasil = []
    for r in baris:
        r2 = {k: r[k] for k in ("kode", "kategori", "satuan")}
        for b in bulan_baru:
            kol = kolom_bulan(b)
            if b in bulan_lama:
                r2[kol] = r.get(kol)
            else:
                r2[kol] = r.get(acuan) if acuan and r["kategori"] in KATEGORI_BERULANG else None
        hasil.append(r2)
    return hasil


def normal(kasus):
    """Bentuk pembanding: komponen per masa diurutkan, tanpa harapan; untuk mendeteksi 'input belum diubah'."""
    k = copy.deepcopy(kasus)
    k.pop("harapan", None)
    for m in k.get("masa", []):
        m["komponen"] = sorted(m["komponen"], key=lambda c: json.dumps(c, sort_keys=True))
    return json.dumps(k, sort_keys=True, ensure_ascii=False)


# ---------------------------------------------------------------------------- format

def rp(v, awalan=True):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "ya" if v else "tidak"
    if not isinstance(v, int):
        return str(v)
    s = f"{abs(v):,}".replace(",", ".")
    s = ("Rp" + s) if awalan else s
    return f"-{s}" if v < 0 else s


def _desimal(fr, maks=4):
    """Fraction -> string desimal Indonesia, eksak bila berhingga dalam `maks` digit; bila tidak, ditandai '≈'."""
    tanda = "-" if fr < 0 else ""
    fr = abs(fr)
    bulat = fr.numerator // fr.denominator
    sisa = fr - bulat
    digit = ""
    for _ in range(maks):
        if sisa == 0:
            break
        sisa *= 10
        d = sisa.numerator // sisa.denominator
        digit += str(d)
        sisa -= d
    teks = f"{bulat:,}".replace(",", ".") + ("," + digit if digit else "")
    return ("≈ " if sisa else "") + tanda + teks


def persen(tarif):
    """'13/100' -> '13%'; '3/200' -> '1,5%'."""
    if tarif is None or tarif == "":
        return "-"
    try:
        fr = Fraction(str(tarif))
    except (ValueError, ZeroDivisionError):
        return str(tarif)
    return _desimal(fr * 100) + "%"


def rasio_persen(a, b, maks=2):
    if not isinstance(a, int) or not isinstance(b, int) or b == 0:
        return "-"
    return _desimal(Fraction(a, b) * 100, maks) + "%"


def label(fakta):
    return LABEL.get(fakta, fakta)


def persen_ke_desimal(teks, tempat):
    """'10' (persen) -> '0.1' (string desimal untuk data_hr). Kosong -> None."""
    if teks is None:
        return None
    s = str(teks).strip().replace(",", ".")
    if s in ("", "None", "nan", "<NA>"):
        return None
    try:
        fr = Fraction(s) / 100
    except (ValueError, ZeroDivisionError):
        raise IsianTidakValid(f"{tempat}: '{teks}' bukan persen")
    if fr < 0:
        raise IsianTidakValid(f"{tempat}: persen tidak boleh negatif")
    teks_des = _desimal(fr, 8).replace(".", "").replace(",", ".")
    if teks_des.startswith("≈"):
        raise IsianTidakValid(f"{tempat}: persen '{teks}' terlalu banyak desimal")
    return teks_des


def desimal_ke_persen(teks):
    if teks in (None, ""):
        return ""
    return _desimal(Fraction(str(teks)) * 100, 6).replace(".", "")
