# 02_studi_kasus — Perusahaan X (anonim)

Sumber: `payroll_calculator.xlsx` (artefak kantor), sheet **Calculator PPh21 v8** beserta sheet parameternya (PTKP, PPh21 Gov, Compensation, OTA, Overtime, Commission, Allowance, Public Holiday, Leave).

> ⚠️ **Data pribadi.** Sheet tersembunyi *Timesheet QDN - 2023*, *Data Gaji*, *PPh 21 2023 EX*, dan *Calc1/Calc2* berisi nama lengkap, NIK, dan NPWP yang tampak riil. Sheet-sheet tersebut **tidak dibaca** oleh `ekstrak_xlsx.py`. File xlsx asli **tidak boleh** diunggah atau dipublikasikan.

| File | Isi |
|---|---|
| `ekstrak_xlsx.py` | Skrip ekstraksi (dapat dijalankan ulang): `env\Scripts\python.exe dataset\02_studi_kasus\ekstrak_xlsx.py` |
| `input_karyawan_A_2023.json` | Seluruh input karyawan dummy KAR-A (TK/0, masuk 2022-02-02, tahun pajak 2023): gaji, kenaikan gaji 2023-03-23, tunjangan sebelum/sesudah kenaikan, THR, kompensasi, OTA, lembur, komisi, cuti, hari libur, hari kerja per bulan |
| `output_xlsx_karyawan_A_2023.csv` | Output xlsx per bulan (43 variabel × 12 bulan + setahun). **Ini output baseline B0, bukan kebenaran.** |
| `parameter_xlsx_2023.json` | Tabel PTKP dan Pasal 17 sebagaimana tertulis di xlsx (termasuk nilai K/I yang keliru) |
| `kebijakan_perusahaan_x.yaml` | Rekonstruksi kebijakan perusahaan dalam DSL lapisan perusahaan (draf v0) |

Temuan audit (K-01..K-10) ada di `research_plan.md` Lampiran D. Ringkasnya:
- lembur diperlakukan sebagai penghasilan tidak teratur, bertentangan dengan PER-16 Ps. 1 angka 15;
- BPJS Kesehatan Desember = 0;
- PTKP K/I keliru;
- batas upah JP Jan–Feb 2023 keliru;
- 254 sel menanam konstanta regulasi.

Catatan: "OTA" dipertahankan sebagai nama komponen generik (insentif tidak teratur), karena kepanjangannya tidak tercantum di xlsx.
