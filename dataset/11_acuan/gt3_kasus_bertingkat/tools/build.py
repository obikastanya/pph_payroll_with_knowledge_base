"""Build GT3 case files: python build.py  (writes ../GT3-NNN.json and ../index.csv)."""
import copy
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from rules import JKK_NORMAL, jp_cap, pct, ptkp, rp  # noqa: E402
from calculator import MONTH_NAMES, Builder  # noqa: E402
from cases import CASES, SECTORS  # noqa: E402

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def prepare(c):
    s = copy.deepcopy(c)
    s["sektor"] = dict(SECTORS[c["sektor"]])
    masa = s["masa"]
    for mo in masa:
        if s.get("zakat_all"):
            masa[mo]["zakat"] = s["zakat_all"]
        for k, v in (s.get("extra_all") or {}).items():
            masa[mo][k] = v
        for k, v in (s.get("extra_merge") or {}).get(mo, {}).items():
            masa[mo][k] = v
    if "dtp_tetap" in s:
        s["dtp_tetap_bulan_ukur"] = s["dtp_tetap"]
    return s


def run(s):
    b = Builder(s)
    return b, b.build()


def solve(s):
    kind, target, month, comp = s["solve"]
    for _ in range(60):
        b, (masa_in, exp, steps) = run(s)
        if kind == "ter":
            row = [r for r in exp["per_masa"] if r["bulan"] == month][0]
            diff = target - row["bruto"]
        else:
            t = exp["tahunan"]
            pkp_raw = [st for st in steps if st["text"].startswith("PKP sebelum pembulatan")][0]["value"]
            diff = target - pkp_raw
        if diff == 0:
            return
        s["masa"][month][comp] = s["masa"][month].get(comp, 0) + diff
    raise RuntimeError(f"solve gagal {s['id']}")


def asumsi(s, exp):
    y = s["tahun"]
    sek = s["sektor"]
    rate = JKK_NORMAL[sek["risiko_jkk"]]
    out = [
        "Pegawai tetap, Wajib Pajak orang pribadi dalam negeri sejak awal tahun (kewajiban subjektif sepanjang tahun), hanya satu pemberi kerja, tidak menerima penghasilan lain dari pemberi kerja ini selain yang tercantum.",
        "Memiliki NPWP/NIK yang valid dan terintegrasi; tarif lebih tinggi 20% tanpa NPWP tidak berlaku (di luar lingkup, taksonomi.md bagian 0).",
        f"Status PTKP {s['status']} pada 1 Januari {y} dan tidak berubah sepanjang tahun" + (
            "; karyawati kawin yang suaminya berpenghasilan sehingga PTKP yang dipakai pemotong hanya PTKP diri sendiri (Rp54.000.000, kategori TER/perlakuan setara TK/0)." if s.get("karyawati_kawin") else "."),
        f"Pemberi kerja: {sek['uraian']}, KLU utama {sek['klu']} (per 1 Januari {y}). Kelompok risiko JKK: {sek['risiko_jkk']} ({pct(rate / 100)} dari upah sebulan)."
        + (" Perusahaan memenuhi syarat keringanan iuran JKK 50% PP 7/2025 (industri padat karya tertentu, >= 50 pekerja aktif) dan telah melunasi iuran JKK s.d. Januari 2025; keringanan berlaku iuran Februari 2025 s.d. Januari 2026 (PP 36/2025)." if sek.get("padat_karya_pp7") else ""),
        "Upah sebulan dasar iuran BPJS = gaji pokok + tunjangan tetap (PP 44/2015 Pasal 19 ayat (2)), tidak di bawah upah minimum; lembur, THR, bonus, dan natura bukan dasar iuran.",
        "Ikut seluruh program: JKK & JKM (dibayar pemberi kerja, objek PPh 21), JHT 3,7% pemberi kerja / 2% pegawai, JP 2% / 1% dengan batas upah JP sesuai bulan iuran, BPJS Kesehatan 4% pemberi kerja / 1% pegawai dengan batas Rp12.000.000. Iuran pegawai dipotong dari gaji; iuran JHT/JP pemberi kerja dicantumkan di input untuk menguji bahwa keduanya bukan objek.",
        "Nilai premi/iuran sudah bulat rupiah (tidak perlu pembulatan).",
        "Lembur diperlakukan sebagai penghasilan teratur; THR, bonus, dan bingkisan sebagai penghasilan tidak teratur.",
    ]
    if y == 2023:
        out.append("Tahun 2023 memakai metode PER-16/PJ/2016 (penghasilan disetahunkan setiap masa) dengan lapisan tarif Pasal 17 UU HPP; PPh sebulan dibulatkan ke bawah ke rupiah penuh (asumsi A2).")
        out.append("Iuran JP 1% pegawai ke BPJS Ketenagakerjaan diperlakukan sebagai pengurang (PER-16 Lampiran I.1.a.1 angka 1 huruf c, PDF hlm. 21).")
    else:
        out.append("PPh 21 masa selain Masa Pajak Terakhir = tarif efektif bulanan x bruto masa, dibulatkan ke bawah ke rupiah penuh (asumsi A1; pembulatan tidak diatur).")
        out.append("Biaya jabatan pada Masa Pajak Terakhir = min(5% x bruto, jumlah bulan bekerja x Rp500.000), sesuai pola contoh PMK 168/2023 Lampiran B.")
    if s["metode"] == "gross_up":
        out.append("Metode gross-up: pemberi kerja membayar tunjangan pajak tunai sebesar PPh 21 terutang pada masa yang sama; tunjangan pajak = titik tetap terkecil (rupiah penuh) dari persamaan T = PPh21(bruto tanpa T + T) (asumsi A3).")
    if s["metode"] == "ditanggung":
        if y == 2023:
            out.append("Metode ditanggung pemberi kerja (2023, semester I): PPh 21 yang ditanggung adalah kenikmatan yang dikecualikan dari pemotongan (PER-16 Pasal 8 ayat (2)); tidak ditambahkan ke bruto.")
        else:
            out.append("Metode ditanggung pemberi kerja (2024+): PPh 21 yang ditanggung adalah kenikmatan dan objek PPh 21, dihitung full gross-up (PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44); numerik sama dengan gross-up, tetapi PPh tidak dipotong dari gaji pegawai.")
    if s.get("bulan_masuk"):
        out.append(f"Mulai bekerja 1 {MONTH_NAMES[s['bulan_masuk']]} {y}; sebelumnya tidak bekerja pada pemberi kerja lain di tahun ini (tidak ada bukti potong lain).")
    if s.get("bulan_keluar"):
        out.append(f"Berhenti bekerja akhir {MONTH_NAMES[s['bulan_keluar']]} {y} dan tetap Subjek Pajak dalam negeri; Masa {MONTH_NAMES[s['bulan_keluar']]} adalah Masa Pajak Terakhir; PTKP penuh setahun, penghasilan tidak disetahunkan.")
    if any("zakat" in v for v in s["masa"].values()):
        if y == 2023:
            out.append("Zakat dibayar melalui pemberi kerja ke BAZNAS; pada 2023 (PER-16) zakat bukan pengurang dalam pemotongan PPh 21 (dikurangkan sendiri oleh pegawai di SPT Tahunan).")
        else:
            out.append("Zakat dibayar melalui pemberi kerja ke BAZNAS (lembaga yang disahkan pemerintah); hanya mengurangi neto pada Masa Pajak Terakhir.")
    if any(k in v for v in s["masa"].values() for k in ("natura_rumah_individual", "kupon_makan_dinas_luar", "bingkisan_non_hari_raya", "kendaraan_dinas")):
        out.append("Natura dinilai dengan biaya yang dikeluarkan pemberi kerja per bulan (PMK 66/2023 Pasal 22); rumah dinas individual (bukan mes komunal); kupon makan hanya untuk pegawai pemasaran/dinas luar dan pemberi kerja tidak menyediakan makan di kantor senilai > Rp2.000.000; kendaraan dinas diberikan kepada pegawai tanpa penyertaan modal dengan rata-rata bruto <= Rp100.000.000/bulan; bingkisan selain hari raya keagamaan.")
        if y == 2023:
            out.append("Natura yang diterima Januari-Juni 2023 tidak dipotong pemberi kerja (PMK 66/2023 Pasal 23 ayat (4)); pemotongan natura mulai Masa Juli 2023.")
    if y in (2025, 2026):
        if "dtp_tetap_bulan_ukur" in s:
            out.append(f"Untuk kriteria DTP: pegawai sudah bekerja sebelum {y}; gaji + tunjangan tetap Masa Januari {y} = {rp(s['dtp_tetap_bulan_ukur'])} (lihat input.info_dtp).")
        out.append("Penghasilan bruto tetap dan teratur untuk kriteria DTP Rp10.000.000 = gaji + tunjangan tetap saja; lembur, premi JKK/JKM/BPJS Kesehatan yang dibayar pemberi kerja, THR, dan bonus tidak dihitung (pembacaan GT3 atas PMK 10/2025 Pasal 4 ayat (3) / PMK 105/2025 Pasal 4 ayat (4); lihat ketidakpastian K5).")
        out.append("Pegawai tidak menerima insentif PPh 21 DTP lain; pemberi kerja melaporkan pemanfaatan DTP tepat waktu.")
    for k, v in s.get("asumsi_extra", []):
        out.append(v)
    return out


def main():
    rows = []
    allcases = []
    for c in CASES:
        s = prepare(c)
        if "solve" in s:
            solve(s)
        b, (masa_in, exp, steps) = run(s)
        months = sorted(s["masa"])
        inp = {
            "status_ptkp": s["status"], "jenis_kelamin": s["jk"],
            "karyawati_kawin_suami_berpenghasilan": bool(s.get("karyawati_kawin")),
            "npwp_nik_valid": True, "metode": s["metode"],
            "sektor": {"klu": s["sektor"]["klu"], "uraian": s["sektor"]["uraian"],
                       "kelompok_risiko_jkk": s["sektor"]["risiko_jkk"],
                       "padat_karya_pp7_2025": s["sektor"]["padat_karya_pp7"]},
            "bulan_masuk": s.get("bulan_masuk"), "bulan_keluar": s.get("bulan_keluar"),
            "masa": masa_in,
        }
        if "dtp_tetap_bulan_ukur" in s:
            inp["info_dtp"] = {"bulan_ukur": f"Januari {s['tahun']}", "penghasilan_tetap_teratur_bulan_ukur": s["dtp_tetap_bulan_ukur"]}
        case = {
            "id": s["id"], "stratum": s["stratum"], "tahun_pajak": s["tahun"],
            "rezim": "PER16_2023" if s["tahun"] == 2023 else ("TER_DTP_" + str(s["tahun"]) if s["tahun"] in (2025, 2026) else "TER_2024"),
            "uraian": s["uraian"], "asumsi": asumsi(s, exp), "input": inp, "expected": exp,
            "langkah": steps, "cek_aritmetika": "belum dicek",
        }
        with open(os.path.join(OUT, f"{s['id']}.json"), "w", encoding="utf-8") as f:
            json.dump(case, f, ensure_ascii=False, indent=2)
        bl = f"{months[0]}" if len(months) == 1 else f"{months[0]}-{months[-1]}"
        rows.append({"id": s["id"], "stratum": s["stratum"], "tahun": s["tahun"], "status": s["status"],
                     "metode": s["metode"], "bulan": bl, "ringkas": s["ringkas"]})
        allcases.append(case)
    with open(os.path.join(OUT, "index.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "stratum", "tahun", "status", "metode", "bulan", "ringkas"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} kasus ditulis")


if __name__ == "__main__":
    main()
