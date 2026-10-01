"""E4 — mutation testing pada KB (research_plan.md §11.4).

Setiap mutan = satu kesalahan yang disuntikkan ke SALINAN lapisan regulasi (aturan, registri, parameter,
klasifikasi, tabel). Untuk mutan tabel, hash manifest ikut diperbarui (mensimulasikan pemelihara yang
mencatat perubahan tetapi salah isi), sehingga pemeriksaan integritas tidak membunuhnya secara gratis.

Detektor kebenaran (berurutan):  D1 verifikasi statis | D2 V1 kasus resmi | D3 properti V3 | D4 E8 perusahaan
Pembeda ekuivalen:               golden master (keluaran sistem asli pada sampel) — mutan yang lolos D1-D4
                                 dan tidak mengubah keluaran apa pun = ekuivalen; jika mengubah = SELAMAT (celah tes).

    env\\Scripts\\python.exe -m eksperimen.mutasi
"""
import csv
import hashlib
import io
import json
import shutil
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from eksperimen import v1
from eksperimen.e8_perusahaan_x import BERKAS_PX, kasus_kar_a, keluaran_xlsx, bandingkan
from eksperimen.v2 import konverter
from engine.kalkulator import fakta, hitung
from engine.kb import muat_kb

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "kb" / "regulasi"
TABEL = ROOT / "dataset" / "01_regulasi" / "tables"


# ------------------------------------------------------------------------ penyiapan salinan

def salin():
    tmp = Path(tempfile.mkdtemp(prefix="mutan_"))
    shutil.copytree(REG, tmp / "kb" / "regulasi")
    shutil.copytree(TABEL, tmp / "dataset" / "01_regulasi" / "tables")
    return tmp


def ganti_teks(tmp, berkas, lama, baru):
    p = tmp / "kb" / "regulasi" / berkas
    s = p.read_text(encoding="utf-8")
    if s.count(lama) != 1:
        raise ValueError(f"mutan tidak unik di {berkas}: {lama!r} ({s.count(lama)}x)")
    p.write_text(s.replace(lama, baru), encoding="utf-8")


def ubah_tabel(tmp, nama, fungsi):
    p = tmp / "dataset" / "01_regulasi" / "tables" / f"{nama}.csv"
    baris = list(csv.DictReader(open(p, encoding="utf-8", newline="")))
    kolom = list(baris[0].keys())
    fungsi(baris)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=kolom, lineterminator="\n" if b"\r\n" not in p.read_bytes() else "\r\n")
    w.writeheader()
    w.writerows(baris)
    p.write_text(buf.getvalue(), encoding="utf-8", newline="")
    m = tmp / "kb" / "regulasi" / "tabel_manifest.yaml"
    s = m.read_text(encoding="utf-8")
    lama = next(l for l in s.splitlines() if f"/{nama}.csv" in l)
    i = s.splitlines().index(lama)
    hash_lama = s.splitlines()[i + 1].split(":")[1].strip()
    m.write_text(s.replace(hash_lama, hashlib.sha256(p.read_bytes()).hexdigest()), encoding="utf-8")


def _baris(kategori=None, urutan=None, **kriteria):
    def cocok(r):
        return all(r.get(k) == v for k, v in kriteria.items()) and (kategori is None or r["kategori"] == kategori) \
            and (urutan is None or r["urutan"] == str(urutan))
    return cocok


def tabel_set(nama, cocok, kolom, nilai):
    def f(baris):
        kena = [r for r in baris if cocok(r)]
        assert len(kena) == 1, (nama, len(kena))
        kena[0][kolom] = nilai(kena[0][kolom]) if callable(nilai) else nilai
    return lambda tmp: ubah_tabel(tmp, nama, f)


def ter_geser_batas(kategori, urutan, delta):
    """Geser batas atas lapisan i dan batas bawah lapisan i+1 bersamaan (tetap bersambung)."""
    def f(baris):
        a = next(r for r in baris if r["kategori"] == kategori and r["urutan"] == str(urutan))
        b = next(r for r in baris if r["kategori"] == kategori and r["urutan"] == str(urutan + 1))
        a["batas_atas"] = str(int(a["batas_atas"]) + delta)
        b["batas_bawah"] = str(int(b["batas_bawah"]) + delta)
    return lambda tmp: ubah_tabel(tmp, "ter_bulanan", f)


def teks(berkas, lama, baru):
    return lambda tmp: ganti_teks(tmp, berkas, lama, baru)


# ------------------------------------------------------------------------ daftar mutan

MUTAN = [
    # tabel TER (tarif & batas)
    ("TER_TARIF", "TER A lapisan 10 tarif +0,25%", tabel_set("ter_bulanan", _baris("A", 10), "tarif_desimal", lambda v: str(round_dec(v, "0.0025")))),
    ("TER_TARIF", "TER B lapisan 5 tarif +0,25%", tabel_set("ter_bulanan", _baris("B", 5), "tarif_desimal", lambda v: str(round_dec(v, "0.0025")))),
    ("TER_TARIF", "TER C lapisan 20 tarif +1%", tabel_set("ter_bulanan", _baris("C", 20), "tarif_desimal", lambda v: str(round_dec(v, "0.01")))),
    ("TER_TARIF", "TER A lapisan 30 tarif -1%", tabel_set("ter_bulanan", _baris("A", 30), "tarif_desimal", lambda v: str(round_dec(v, "-0.01")))),
    ("TER_BATAS", "TER A batas lapisan 6/7 +1.000", ter_geser_batas("A", 6, 1000)),
    ("TER_BATAS", "TER B batas lapisan 10/11 -50.000", ter_geser_batas("B", 10, -50000)),
    ("TER_BATAS", "TER A batas lapisan 1/2 +1 (off-by-one)", ter_geser_batas("A", 1, 1)),
    ("TER_CELAH", "TER C celah: batas atas lapisan 3 +1 saja", tabel_set("ter_bulanan", _baris("C", 3), "batas_atas", lambda v: str(int(v) + 1))),
    ("TER_MONOTON", "TER A lapisan 12 tarif = 0 (tidak monoton)", tabel_set("ter_bulanan", _baris("A", 12), "tarif_desimal", "0.0")),
    # Pasal 17 & PTKP
    ("P17_TARIF", "Pasal 17 HPP lapisan 2: 15% -> 16%", tabel_set("tarif_pasal17", _baris(rezim="UU HPP", lapisan="2"), "tarif_persen", "16")),
    ("P17_BATAS", "Pasal 17 HPP batas 60 jt -> 50 jt", lambda tmp: ubah_tabel(tmp, "tarif_pasal17", _p17_batas)),
    ("P17_VERSI", "Pasal 17 pra-HPP berlaku s.d. 2023", tabel_set("tarif_pasal17", _baris(rezim="UU 36/2008 (pra-HPP)", lapisan="1"), "berlaku_sampai", "2023-12-31")),
    ("PTKP_NILAI", "PTKP TK/0 54 jt -> 54,5 jt", tabel_set("ptkp", _baris(status="TK/0"), "ptkp_setahun", "54500000")),
    ("PTKP_NILAI", "PTKP K/3 72 jt -> 70,5 jt", tabel_set("ptkp", _baris(status="K/3"), "ptkp_setahun", "70500000")),
    ("PTKP_KATEGORI", "kategori TER K/1 B -> A", tabel_set("ptkp", _baris(status="K/1"), "kategori_ter", "A")),
    ("KLU", "KLU 55110 dihapus dari daftar pariwisata 2025", tabel_set("klu_dtp", _baris(klu="55110", masa_mulai="2025-10"), "klu", "99999")),
    # parameter
    ("PARAM", "plafon biaya jabatan bulanan 500.000 -> 550.000", teks("parameter.yaml", "nilai: 500000\n", "nilai: 550000\n")),
    ("PARAM", "biaya jabatan 5% -> 6%", teks("parameter.yaml", 'nama: bj_persen\n    nilai: "5"', 'nama: bj_persen\n    nilai: "6"')),
    ("PARAM", "plafon biaya jabatan tahunan 6 jt -> 5 jt", teks("parameter.yaml", "nilai: 6000000\n", "nilai: 5000000\n")),
    ("PARAM", "batas DTP 10 jt -> 9,5 jt", teks("parameter.yaml", "nilai: 10000000\n", "nilai: 9500000\n")),
    ("PARAM", "pengali tanpa NPWP 120% -> 110%", teks("parameter.yaml", 'nilai: "1.2"', 'nilai: "1.1"')),
    ("PARAM", "batas upah JP 2023 9.559.600 -> 9.000.000", teks("parameter.yaml", "nilai: 9559600", "nilai: 9000000")),
    ("PARAM", "JKM 0,3% -> 0,24%", teks("parameter.yaml", 'nama: jkm_pk_persen\n    nilai: "0.3"', 'nama: jkm_pk_persen\n    nilai: "0.24"')),
    ("PARAM", "batas upah BPJS Kes 12 jt -> 8 jt", teks("parameter.yaml", "nilai: 12000000\n", "nilai: 8000000\n")),
    # registri pembulatan
    ("BULAT", "PKP dibulatkan per rupiah (satuan 1000 -> 1)", teks("pembulatan.yaml", "satuan: 1000", "satuan: 1")),
    ("BULAT", "PKP setengah-menjauhi-nol (bukan ke bawah)", teks("pembulatan.yaml", "    satuan: 1000\n    mode: bawah", "    satuan: 1000\n    mode: setengah_menjauhi_nol")),
    ("BULAT", "TER x bruto dibulatkan ke atas", teks("pembulatan.yaml", "titik: \"PPh masa = tarif TER x bruto masa\"\n    satuan: 1\n    mode: bawah",
                                                    "titik: \"PPh masa = tarif TER x bruto masa\"\n    satuan: 1\n    mode: atas")),
    ("BULAT", "proporsi n/12 dibulatkan ke atas", teks("pembulatan.yaml", "    mode: bawah\n    urutan: \"sekali, setelah perkalian proporsi", "    mode: atas\n    urutan: \"sekali, setelah perkalian proporsi")),
    # aturan: ekspresi
    ("EKSPR", "neto setahun tanpa pengurangan zakat", teks("aturan_umum.yaml", "bruto_setahun - biaya_jabatan - iuran_pengurang - zakat", "bruto_setahun - biaya_jabatan - iuran_pengurang")),
    ("EKSPR", "neto setahun tanpa pengurangan iuran", teks("aturan_umum.yaml", "bruto_setahun - biaya_jabatan - iuran_pengurang - zakat", "bruto_setahun - biaya_jabatan - zakat")),
    ("EKSPR", "PKP tanpa max(0, .)", teks("aturan_umum.yaml", "maka: \"max(0, bulatkan('BULAT-PKP-01', neto_setahun - ptkp))\"", "maka: \"bulatkan('BULAT-PKP-01', neto_setahun - ptkp)\"")),
    ("EKSPR", "plafon biaya jabatan tanpa n bulan kerja", teks("aturan_umum.yaml", "parameter('bj_maks_bulan') * n_bulan_kerja, ", "")),
    ("EKSPR", "PPh TER atas bruto tanpa tunjangan pajak", teks("aturan_ter.yaml", "maka: \"tarif_ter * bruto_berjalan\"", "maka: \"tarif_ter * _bruto_dasar\"")),
    ("EKSPR", "bruto TER tanpa premi objek", teks("aturan_ter.yaml", " + komponen('premi_objek', 'bulan')", "")),
    ("EKSPR", "PPh masa terakhir = setahun (tanpa kredit dipotong)", teks("aturan_umum.yaml", "maka: \"pph21_setahun - pph21_dipotong_sebelumnya\"", "maka: \"pph21_setahun\"")),
    ("EKSPR", "proporsi n/12 dihapus", teks("aturan_umum.yaml", "maka: \"pph21_disetahunkan * n_subjektif / 12\"", "maka: \"pph21_disetahunkan\"")),
    ("EKSPR", "karyawati: aturan PTKP diri sendiri tidak dipakai", teks("aturan_umum.yaml", "maka: \"'TK/0'\"", "maka: \"status_ptkp_input\"")),
    ("TAFSIR", "PER-16: default tafsir R16-05-N diganti 12 (asumsi tersembunyi)", teks("aturan_per16.yaml", 'maka: "n_disetahunkan"', 'maka: "12"')),
    ("EKSPR", "PER-16: plafon BJ tidak teratur pakai plafon bulanan", teks("aturan_per16.yaml", "_bruto_dengan_tt), parameter('bj_maks_tahun'))", "_bruto_dengan_tt), parameter('bj_maks_bulan'))")),
    ("EKSPR", "DTP: lebih bayar tanpa dikurangi DTP berjalan", teks("aturan_dtp.yaml", " - jumlah_masa_selain_terakhir('pph21_dtp_berjalan'))", ")")),
    ("OFF_BY_ONE", "PER-16 n disetahunkan pegawai baru: 12 - bulan_masuk (tanpa +1)", teks("aturan_per16.yaml", "maka: \"12 - bulan_masuk + 1\"", "maka: \"12 - bulan_masuk\"")),
    ("OFF_BY_ONE", "n subjektif mulai: 12 - mulai (tanpa +1)", teks("aturan_umum.yaml", "maka: \"12 - subjektif_mulai + 1\"", "maka: \"12 - subjektif_mulai\"")),
    ("OPERATOR", "DTP: batas penghasilan <= menjadi <", teks("aturan_dtp.yaml", "_penghasilan_tetap_awal <= parameter", "_penghasilan_tetap_awal < parameter")),
    ("OPERATOR", "masa pajak terakhir: >= 0 menjadi > 0 (DTP)", teks("aturan_dtp.yaml", "masa_terakhir and pph21 >= 0", "masa_terakhir and pph21 > 0")),
    # aturan: kondisi & masa berlaku & sifat
    ("KONDISI", "pemotongan berjalan juga di masa terakhir (negasi kondisi)", teks("aturan_umum.yaml", "    menghasilkan: pph21\n    jika: \"not masa_terakhir\"", "    menghasilkan: pph21\n    jika: \"masa_terakhir or not masa_terakhir\"")),
    ("KONDISI", "gross-up tidak berlaku untuk PPh ditanggung pemberi kerja", teks("aturan_ter.yaml", "metode in ('gross_up', 'ditanggung_pemberi_kerja')", "metode == 'gross_up'")),
    ("BERLAKU", "aturan PPh TER berlaku mulai Februari 2024", teks("aturan_ter.yaml", "  - id: R24-02b\n    sifat: wajib\n    berlaku: {mulai: 2024-01-01}", "  - id: R24-02b\n    sifat: wajib\n    berlaku: {mulai: 2024-02-01}")),
    ("BERLAKU", "natura objek (PMK 66) mulai 2024-07-01", teks("aturan_umum.yaml", "berlaku: {mulai: 2023-07-01}", "berlaku: {mulai: 2024-07-01}")),
    ("BERLAKU", "zakat pengurang (PMK 168) mulai 2025", teks("aturan_ter.yaml", "  - id: R24-PENG-02\n    sifat: wajib\n    berlaku: {mulai: 2024-01-01}", "  - id: R24-PENG-02\n    sifat: wajib\n    berlaku: {mulai: 2025-01-01}")),
    ("KLASIFIKASI", "klasifikasi wajib lembur = tidak_teratur", teks("klasifikasi.yaml", "{jenis: lembur, kategori: teratur,", "{jenis: lembur, kategori: tidak_teratur,")),
    ("KLASIFIKASI", "klasifikasi wajib premi JKN = bukan objek", teks("klasifikasi.yaml", "{jenis: premi_jkn, kategori: premi_objek,", "{jenis: premi_jkn, kategori: bukan_objek,")),
    ("TITIK_TETAP", "batas atas gross-up bulanan = 0", teks("aturan_ter.yaml", 'batas_titik_tetap: {bawah: "0", atas: "_bruto_dasar"}', 'batas_titik_tetap: {bawah: "0", atas: "0"}')),
]


def round_dec(v, delta):
    from fractions import Fraction
    x = Fraction(v) + Fraction(delta)
    # representasi desimal eksak (penyebut 10^k)
    for k in range(1, 9):
        if (x * 10 ** k).denominator == 1:
            n = int(x * 10 ** k)
            neg = "-" if n < 0 else ""
            n = abs(n)
            return f"{neg}{n // 10 ** k}.{str(n % 10 ** k).zfill(k)}"
    raise ValueError(v)


def _p17_batas(baris):
    a = next(r for r in baris if r["rezim"] == "UU HPP" and r["lapisan"] == "1")
    b = next(r for r in baris if r["rezim"] == "UU HPP" and r["lapisan"] == "2")
    a["pkp_batas_atas"] = "50000000"
    b["pkp_batas_bawah"] = "50000000"


# ------------------------------------------------------------------------ detektor

def sampel_sintetis(n=150):
    return [k for i, k in enumerate(konverter().muat()) if i % max(1, 2201 // n) == 0][:n]


def d0_double_entry(tmp):
    """Tabel KB (salinan termutasi) vs ekstraksi kedua dari gambar halaman + konsistensi parameter."""
    import tests.test_tabel_double_entry as de
    t = tmp / "dataset" / "01_regulasi" / "tables"
    return bool(de.bandingkan_ter(t) or de.bandingkan_pasal17(t) or de.bandingkan_ptkp(t)
                or de.parameter_konsisten(tmp / "kb" / "regulasi"))


def d2_v1(kb):
    hasil = v1.jalankan(lambda k, var: hitung(k, var, kb=kb), fakta)
    return v1.ringkas(hasil)[1] > 0


def d3_properti(kb, sampel):
    for k in sampel:
        h = hitung(k, kb=kb)
        t = h["tahunan"]
        if sum(m["pph21"] for m in h["per_masa"].values()) != t["pph21_setahun"]:
            return True
        if t["neto_setahun"] != t["bruto_setahun"] - t["biaya_jabatan"] - t["iuran_pengurang"] - t["zakat"]:
            return True
        if t["pkp"] < 0 or t["pkp"] % 1000 or (t["neto_setahun"] <= t["ptkp"] and t["pph21_setahun"] != 0):
            return True
        if t["biaya_jabatan"] > 6_000_000 or t["biaya_jabatan"] > 500_000 * len(h["per_masa"]):
            return True
    # REG-DITANGGUNG-02: ditanggung pemberi kerja == gross-up (2024-); DTP terdefinisi tiap masa
    for k in sampel[:20]:
        if k["tahun_pajak"] >= 2024:
            a = hitung(dict(k, metode="gross_up"), kb=kb)
            b = hitung(dict(k, metode="ditanggung_pemberi_kerja"), kb=kb)
            if a["per_masa"] != b["per_masa"]:
                return True
        if k["tahun_pajak"] in (2025, 2026):
            h = hitung(dict(k, pemberi_kerja={"klu": "13111", "jenis": "biasa"}), kb=kb)
            if any("pph21_dtp" not in m for m in h["per_masa"].values()):
                return True
    return False


def d4_e8(kb_path):
    kbp = muat_kb(berkas_tambahan=BERKAS_PX, dir_regulasi=kb_path)
    h = hitung(kasus_kar_a(2023), kb=kbp)
    komponen = ["px_gaji", "px_tunjangan", "px_premi_jkm", "px_premi_jkk", "px_premi_jht_pk", "px_premi_jp_pk",
                "px_iuran_jp_pg", "px_iuran_jht_pg", "px_kompensasi", "px_ota", "px_lembur", "px_komisi"]
    baris = bandingkan(h, keluaran_xlsx())
    if [r for r in baris if r["fakta"] in komponen and not r["sama"]]:
        return True
    if [r for r in baris if r["fakta"] in ("px_premi_kes", "px_iuran_kes_pg") and r["bulan"] < 12 and not r["sama"]]:
        return True
    konflik = [p for p in h["peringatan"] if p["kode"] == "KONFLIK_WAJIB"]
    return not (len(konflik) == 1 and konflik[0]["fakta"] == "px_lembur")


def golden(kb, kb_px, sampel, ref):
    keluaran = []
    for k in v1.muat_kasus():
        keluaran.append(json.dumps(_ringkas(hitung(k, kb=kb)), sort_keys=True, default=str))
    for k in sampel:
        keluaran.append(json.dumps(_ringkas(hitung(k, kb=kb)), sort_keys=True, default=str))
    keluaran.append(json.dumps(_ringkas(hitung(kasus_kar_a(2023), kb=kb_px)), sort_keys=True, default=str))
    return keluaran if ref is None else keluaran != ref


def _ringkas(h):
    return {"per_masa": h["per_masa"], "tahunan": h["tahunan"]}


def jalankan():
    sampel = sampel_sintetis()
    ref = golden(muat_kb(), muat_kb(berkas_tambahan=BERKAS_PX), sampel, None)
    hasil = []
    for operator, deskripsi, fungsi in MUTAN:
        tmp = salin()
        rec = {"operator": operator, "mutan": deskripsi}
        try:
            fungsi(tmp)
            dreg = tmp / "kb" / "regulasi"
            if d0_double_entry(tmp):
                rec.update(status="terbunuh", detektor="D0_double_entry")
                hasil.append(rec)
                continue
            try:
                kb = muat_kb(dir_regulasi=dreg)
            except Exception as e:
                rec.update(status="terbunuh", detektor="D1_statis", bukti=f"{type(e).__name__}: {str(e)[:120]}")
                hasil.append(rec)
                continue
            for nama, uji in (("D2_V1", lambda: d2_v1(kb)), ("D3_properti", lambda: d3_properti(kb, sampel)),
                              ("D4_E8", lambda: d4_e8(dreg))):
                try:
                    if uji():
                        rec.update(status="terbunuh", detektor=nama)
                        break
                except Exception as e:
                    rec.update(status="terbunuh", detektor=nama, bukti=f"{type(e).__name__}: {str(e)[:120]}")
                    break
            else:
                kb_px = muat_kb(berkas_tambahan=BERKAS_PX, dir_regulasi=dreg)
                berubah = golden(kb, kb_px, sampel, ref)
                rec.update(status="SELAMAT" if berubah else "ekuivalen_menurut_sampel", detektor=None)
        except ValueError as e:
            rec.update(status="tidak_sah", detektor=None, bukti=str(e)[:120])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        hasil.append(rec)
    return hasil


def ringkasan(hasil):
    sah = [r for r in hasil if r["status"] != "tidak_sah"]
    ekuivalen = [r for r in sah if r["status"] == "ekuivalen_menurut_sampel"]
    terbunuh = [r for r in sah if r["status"] == "terbunuh"]
    selamat = [r for r in sah if r["status"] == "SELAMAT"]
    skor = len(terbunuh) / (len(sah) - len(ekuivalen)) if len(sah) > len(ekuivalen) else 1
    return {"total": len(hasil), "sah": len(sah), "terbunuh": len(terbunuh), "selamat": len(selamat),
            "ekuivalen": len(ekuivalen), "mutation_score": skor,
            "per_detektor": dict(Counter(r["detektor"] for r in terbunuh)),
            "per_operator": {op: dict(Counter(r["status"] for r in sah if r["operator"] == op))
                             for op in sorted({r["operator"] for r in sah})}}


if __name__ == "__main__":
    hasil = jalankan()
    (ROOT / "eksperimen" / "hasil").mkdir(exist_ok=True)
    (ROOT / "eksperimen" / "hasil" / "mutasi.json").write_text(json.dumps(hasil, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(ringkasan(hasil), indent=1, ensure_ascii=False))
    for r in hasil:
        if r["status"] in ("SELAMAT", "ekuivalen_menurut_sampel", "tidak_sah"):
            print(" ", r["status"], "|", r["operator"], "|", r["mutan"], "|", r.get("bukti", ""))
