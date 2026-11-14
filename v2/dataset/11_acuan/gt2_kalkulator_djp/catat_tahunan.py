"""Catat satu hasil formulir PPh 21 Tahunan (A1/A2) kalkulator DJP ke hasil_tahunan.csv dan salin tangkapan layarnya.

    env\\Scripts\\python dataset\\11_acuan\\gt2_kalkulator_djp\\catat_tahunan.py GT2-21 "<isian>" "<baris>" <layar_atas> <layar_bawah> [catatan]

<isian> adalah teks dropdown seperti tampil ("jnsPphTahunan=... | ptkpTahunan=K/1 - 63000000 | ..."), <baris> adalah
nilai baris 1-20 seperti tampil ("b1=216.000.000 b2=0 ... b20=8.941.400"). Keduanya disimpan apa adanya; angka bersih
diturunkan dari teks itu.
"""
import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
BARIS = [f"b{i}" for i in range(1, 21)]


def angka(teks):
    """Rupiah: titik adalah pemisah ribuan ('8.941.400' -> '8941400', '-3.551.690' -> '-3551690')."""
    return teks.replace(".", "").replace(",", ".").strip()


def main(gt2_id, isian, baris, layar_atas, layar_bawah, catatan=""):
    rencana = {r["gt2_id"]: r for r in csv.DictReader(open(HERE / "rencana_tahunan.csv", encoding="utf-8"))}[gt2_id]
    pilihan = dict(p.strip().split("=", 1) for p in isian.split("|"))
    nilai = dict(p.split("=", 1) for p in baris.split())
    bukti = []
    for sumber, akhiran in ((layar_atas, "atas"), (layar_bawah, "bawah")):
        tujuan = HERE / "bukti" / f"{gt2_id}_{akhiran}.jpg"
        if sumber and Path(sumber).exists() and Path(sumber).resolve() != tujuan.resolve():
            shutil.copyfile(sumber, tujuan)
        bukti.append(f"bukti/{tujuan.name}" if tujuan.exists() else "")
    row = {"gt2_id": gt2_id, "waktu_akses": datetime.now().astimezone().isoformat(timespec="seconds"),
           "url": "https://kalkulator.pajak.go.id/", "jenis": pilihan.get("jnsPphTahunan", ""),
           "ptkp": pilihan.get("ptkpTahunan", "").split(" - ")[0], "penghitungan": pilihan.get("statusPenghitungan", ""),
           "masa_awal": pilihan.get("msPjkAwal", ""), "masa_akhir": pilihan.get("msPjkAkhir", "")}
    row.update({b: angka(nilai[b]) for b in BARIS})
    row.update({"teks_isian": isian, "teks_baris": baris, "bukti_atas": bukti[0], "bukti_bawah": bukti[1],
                "captcha_oleh": "tidak diminta", "catatan": catatan})
    for kolom, b in (("ptkp", None), ("masa_awal", None), ("masa_akhir", None)):
        if row[kolom] != rencana[kolom]:
            sys.exit(f"{gt2_id}: {kolom} tampil '{row[kolom]}', rencana '{rencana[kolom]}'")
    for b in ("b1", "b2", "b3", "b4", "b5", "b6", "b7", "b9", "b10", "b11", "b14", "b19"):
        kolom = next(k for k in rencana if k.startswith(b + "_"))
        if row[b] != rencana[kolom]:
            sys.exit(f"{gt2_id}: baris {b} tampil {row[b]}, rencana {rencana[kolom]}")
    path = HERE / "hasil_tahunan.csv"
    baru = not path.exists()
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(row), lineterminator="\n")
        if baru:
            w.writeheader()
        w.writerow(row)
    print(f"{gt2_id}: PKP {row['b17']}, PPh setahun {row['b18']}, PPh terutang {row['b20']}")


if __name__ == "__main__":
    main(*sys.argv[1:])
