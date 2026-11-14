"""Catat satu hasil kalkulator DJP ke hasil.csv dan salin tangkapan layarnya ke bukti/.

    env\\Scripts\\python dataset\\11_acuan\\gt2_kalkulator_djp\\catat.py GT2-01 "6.600.000" "0 %" "0" <layar_formulir> <layar_hasil> [catatan]

Nilai keluaran disalin persis seperti tampil di kalkulator; angka bersih diturunkan dari teks itu.
"""
import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent


def angka(teks):
    """Rupiah: titik adalah pemisah ribuan ('6.600.001' -> '6600001')."""
    return teks.replace(".", "").replace(",", ".").strip()


def persen(teks):
    """Tarif: titik adalah tanda desimal ('0.25 %' -> '0.25')."""
    return teks.replace("%", "").replace(",", ".").strip()


def main(gt2_id, dpp, tarif, pph21, layar_formulir, layar_hasil, catatan=""):
    rencana = {r["gt2_id"]: r for r in csv.DictReader(open(HERE / "rencana_kasus.csv", encoding="utf-8"))}[gt2_id]
    bukti = []
    for sumber, akhiran in ((layar_formulir, "formulir"), (layar_hasil, "hasil")):
        tujuan = HERE / "bukti" / f"{gt2_id}_{akhiran}.jpg"
        if sumber and Path(sumber).exists() and Path(sumber).resolve() != tujuan.resolve():
            shutil.copyfile(sumber, tujuan)
        bukti.append(f"bukti/{tujuan.name}" if tujuan.exists() else "")
    row = {"gt2_id": gt2_id, "waktu_akses": datetime.now().astimezone().isoformat(timespec="seconds"),
           "url": "https://kalkulator.pajak.go.id/", "jenis": rencana["jenis"], "kode_objek": rencana["kode_objek"],
           "skema": rencana["skema"], "ptkp": rencana["ptkp"], "bruto_diisi": rencana["bruto_diisi"],
           "dpp": angka(dpp), "tarif": persen(tarif), "pph21": angka(pph21), "tunjangan_pajak": "",
           "teks_hasil": f"DPP '{dpp}' | Tarif '{tarif}' | PPh 21 '{pph21}'", "bukti_formulir": bukti[0],
           "bukti_hasil": bukti[1], "captcha_oleh": "peneliti", "catatan": catatan}
    with open(HERE / "hasil.csv", "a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, list(row)).writerow(row)
    print(row["gt2_id"], row["waktu_akses"], row["teks_hasil"])


if __name__ == "__main__":
    main(*sys.argv[1:])
