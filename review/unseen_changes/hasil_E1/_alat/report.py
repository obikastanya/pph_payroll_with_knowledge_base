"""Write ../hasil.csv from ../detail/*.json and ../delta/*.json, and print the aggregates for RINGKASAN.md."""
import csv
import json

from common import OUT, SEALED
from pph21kbs.analysis.stats import clopper_pearson, upper_bound

ATTEMPTS = {"U15": 2}
NOTES = {
    "U01": "Tabel ptkp versi 2027 (berlaku surut 1 Jan 2027, dicatat 19 Mar 2027) + change menutup TAB.PTKP.2016",
    "U02": "Dua parameter baru (batas biaya jabatan bulanan dan tahunan) mulai 2027",
    "U03": "Tabel ter_category dan ter_monthly versi 2027 (A/B/C tetap + lapisan D dari Lampiran E)",
    "U04": "Fakta dan aturan baru Tapera; change REG.PREMIUMS.TAXABLE dan REG.YEAR.DEDUCTIONS",
    "U05": "Fakta internet_taxable dengan syarat hari kerja jarak jauh per bulan; change REG.GROSS.REGULAR",
    "U06": "Fasilitas DTP baru (usia dari tanggal, uji bulan pertama, syarat jumlah pegawai per bulan, batas "
           "pengembalian)",
    "U07": "Salinan aturan DTP PMK 105/2025 untuk Jan-Jun 2027, tabel KLU 2027, aturan pengembalian 2027",
    "U08": "Aturan status PTKP efektif K/n -> TK/n lewat tabel lookup, mengungguli aturan karyawati lama",
    "U09": "Dua dokumen dalam satu Delta; tarif TER atas bruto teratur dan metode selisih Pasal 17",
    "U10": "Satu change: masa berlaku REG.ZAKAT.DEDUCTIBLE ditutup 31 Des 2026",
    "U11": "Fakta ter_base (bruto dibulatkan ke ribuan) dan dua aturan TER pengganti",
    "U12": "Bruto setara bulan pertama; jumlah hari bulan lewat tabel + aturan tahun kabisat; tanggal mulai dipecah "
           "di data kasus",
    "U13": "Aturan ptkp_amount proporsional untuk masa kerja < 12 bulan",
    "U14": "Lapisan perusahaan: metode gross-up untuk golongan I-III memakai aturan gross-up KB; lebih potong "
           "Desember tidak dibayarkan",
    "U15": "Lapisan perusahaan: gaji baru, rapel, premi baru dan rapel premi. Percobaan 1: galat G3 (masa berlaku "
           "old_bpjs_wage) dan selisih Rp1 premi C5 (konvensi pembulatan premi contoh); diperbaiki di percobaan 2",
    "U16": "Tabel ter_monthly versi 2027 dari Lampiran A, B, C",
}


def main():
    index = {r["id"]: r for r in csv.DictReader(open(SEALED / "INDEX.csv", encoding="utf-8", newline=""))}
    rows, k, n_ex, n_ok, n_val = [], 0, 0, 0, 0
    sizes = {}
    for i in range(1, 17):
        uid = f"U{i:02d}"
        d = json.loads((OUT / "detail" / f"{uid}.json").read_text(encoding="utf-8"))
        delta = json.loads((OUT / "delta" / f"{uid}.json").read_text(encoding="utf-8"))
        ok = sum(e["ok"] for e in d["examples"])
        total = len(d["examples"])
        success = d["apply"] == "ok" and d["shacl"] == "ok" and not d["g3_errors"] and ok == total
        k += success
        n_ex += total
        n_ok += ok
        n_val += sum(e["n_values"] for e in d["examples"])
        kinds = {}
        for e in delta["add"]:
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        sizes[uid] = (len(delta["add"]), len(delta["change"]), len(delta["remove"]), kinds)
        rows.append({"id": uid, "jenis": index[uid]["jenis_utama"], "berhasil": "ya" if success else "tidak",
                     "contoh_cocok": f"{ok}/{total}", "kategori_gagal": "", "percobaan": ATTEMPTS.get(uid, 1),
                     "catatan": NOTES[uid]})
    with open(OUT / "hasil.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    n = 16
    lo, hi = clopper_pearson(k, n)
    print(f"RA = {k}/{n} = {k / n:.4f}; CP95 = [{lo:.4f}, {hi:.4f}]; one-sided lower = {1 - upper_bound(n - k, n):.4f}")
    print(f"examples {n_ok}/{n_ex}; stated values compared {n_val}")
    for uid, (a, c, r, kinds) in sizes.items():
        print(uid, "add", a, "change", c, "remove", r, kinds)


if __name__ == "__main__":
    main()
