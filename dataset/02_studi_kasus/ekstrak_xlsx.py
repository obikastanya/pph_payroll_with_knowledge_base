"""Ekstrak studi kasus "Perusahaan X" dari payroll_calculator.xlsx.

Hanya membaca sheet 'Calculator PPh21 v8' (karyawan dummy) dan sheet parameternya.
Sheet tersembunyi yang berisi data pribadi (Timesheet QDN - 2023, Data Gaji,
PPh 21 2023 EX, Calc1/Calc2) SENGAJA tidak dibaca.

Jalankan dari root proyek:
    env\\Scripts\\python.exe dataset\\02_studi_kasus\\ekstrak_xlsx.py
"""
import csv
import json
from datetime import date, datetime
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SRC = ROOT / "payroll_calculator.xlsx"
CALC = "Calculator PPh21 v8"
MONTH_COLS = "DEFGHIJKLMNO"
MONTH_SHEETS = ["January", "February", "March", "April", "May", "June", "July",
                "August", "September", "October", "November", "December"]

# baris output di sheet kalkulator -> nama variabel netral
OUTPUT_ROWS = {
    5: "gaji_prorata", 6: "lembur_teratur", 7: "komisi_teratur", 8: "tunjangan",
    9: "premi_jkm_perusahaan", 10: "premi_jkk_perusahaan", 11: "premi_bpjs_kes_perusahaan",
    15: "premi_jht_perusahaan_non_objek", 16: "premi_jp_perusahaan_non_objek",
    17: "bruto_teratur_sebulan", 19: "biaya_jabatan", 20: "iuran_jp_pegawai",
    21: "iuran_jht_pegawai", 23: "total_pengurang", 24: "neto_sebulan",
    25: "neto_disetahunkan", 26: "ptkp", 27: "pkp", 28: "pkp_dibulatkan",
    31: "pph21_setahun", 33: "pph21_teratur_sebulan", 34: "thr", 35: "pph21_thr",
    36: "kompensasi", 37: "pph21_kompensasi", 38: "insentif_ota", 39: "pph21_ota",
    40: "lembur", 41: "pph21_lembur", 42: "komisi", 43: "pph21_komisi",
    44: "pph21_dipotong", 47: "iuran_bpjs_kes_pegawai", 48: "transfer_gaji",
    49: "transfer_thr", 50: "transfer_ota", 51: "transfer_kompensasi",
    52: "transfer_lembur", 53: "transfer_komisi",
}


def iso(x):
    if isinstance(x, (datetime, date)):
        return x.date().isoformat() if isinstance(x, datetime) else x.isoformat()
    return x


def rows(ws, first=2):
    for r in ws.iter_rows(min_row=first, values_only=True):
        if any(c is not None for c in r):
            yield r


def main():
    wb = openpyxl.load_workbook(SRC, data_only=True)
    c = wb[CALC]

    allowance = wb["Allowance"]
    def tunjangan(name_col, type_col, val_col, r0, r1):
        out = []
        for r in range(r0, r1 + 1):
            nama = allowance[f"{name_col}{r}"].value
            if nama:
                out.append({"nama": nama.lower(),
                            "tipe": (allowance[f"{type_col}{r}"].value or "").lower() or None,
                            "nilai": allowance[f"{val_col}{r}"].value or 0})
        return out

    hari_kerja = []
    for i, sheet in enumerate(MONTH_SHEETS):
        hari_kerja.append({
            "bulan": i + 1,
            "hari_kerja_penuh": c[f"DQ{22 + i}"].value,
            "hari_kerja_aktual": c[f"DR{22 + i}"].value,
        })

    inp = {
        "_catatan": "Karyawan dummy dari sheet 'Calculator PPh21 v8'. Nama dan NPWP dianonimkan.",
        "tahun_pajak": int(c["DP6"].value),
        "karyawan": {
            "id": "KAR-A",
            "status_ptkp": c["DQ3"].value,
            "punya_npwp": c["DQ2"].value not in (None, ""),
            "tanggal_masuk": iso(c["DP7"].value),
            "tanggal_efektif_terakhir": iso(c["DP8"].value),
            "tanggal_daftar_bpjs_kes": iso(c["DP36"].value),
            "tanggal_daftar_bpjs_tk": iso(c["DP37"].value),
            "gaji_pokok": c["DP1"].value,
            "metode_pajak": "gross",
        },
        "kenaikan_gaji": {
            "tanggal": iso(c["DP14"].value),
            "nominal": c["DP13"].value,
            "hari_kerja_aktual_sebelum": c["DP15"].value,
            "hari_kerja_aktual_sesudah": c["DP16"].value,
        },
        "tunjangan_sebelum_kenaikan": tunjangan("A", "B", "C", 2, 5),
        "tunjangan_sesudah_kenaikan": tunjangan("E", "F", "G", 6, 9),
        "thr": {"tanggal_transfer": iso(c["DP19"].value), "tanggal_lebaran": iso(c["DP20"].value)},
        "kompensasi": [{"tanggal": iso(r[0]), "persen_gaji": r[1]} for r in rows(wb["Compensation"])],
        "insentif_ota": [{"tanggal": iso(r[0]), "nominal": r[1]} for r in rows(wb["OTA"])],
        "lembur": [{"periode": iso(r[0]), "nominal": r[1] or 0} for r in rows(wb["Overtime"])],
        "komisi": [{"periode": iso(r[0]), "nominal": r[1] or 0} for r in rows(wb["Commission"])],
        "cuti": [{"tanggal": iso(r[0]), "jenis": r[2]} for r in rows(wb["Leave"]) if r[0]],
        "hari_libur": [{"tanggal": iso(r[0]), "nama": r[2]} for r in rows(wb["Public Holiday"]) if r[0]],
        "hari_kerja_per_bulan": hari_kerja,
    }
    (OUT / "input_karyawan_A_2023.json").write_text(
        json.dumps(inp, indent=2, ensure_ascii=False), encoding="utf-8")

    with open(OUT / "output_xlsx_karyawan_A_2023.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["variabel", "baris_xlsx"] + [f"bulan_{i:02d}" for i in range(1, 13)] + ["setahun"])
        for r, name in OUTPUT_ROWS.items():
            vals = [c[f"{col}{r}"].value or 0 for col in MONTH_COLS]
            q = c[f"Q{r}"].value
            w.writerow([name, r] + [round(v) if isinstance(v, (int, float)) else v for v in vals]
                       + [round(q) if isinstance(q, (int, float)) else ""])

    params = {
        "ptkp_xlsx": {r[0]: r[1] for r in rows(wb["PTKP"])},
        "tarif_pasal17_xlsx": [{"bawah": r[0], "atas": r[1], "tarif": r[2]}
                               for r in rows(wb["PPh21 Gov"]) if isinstance(r[0], (int, float))],
    }
    (OUT / "parameter_xlsx_2023.json").write_text(
        json.dumps(params, indent=2, ensure_ascii=False), encoding="utf-8")
    print("ok:", [p.name for p in OUT.iterdir()])


if __name__ == "__main__":
    main()
