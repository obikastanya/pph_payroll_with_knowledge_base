# GT5 — Contoh hitungan kebijakan perusahaan

21 contoh nilai yang ditentukan oleh klausul lima PKB nyata (THR, lembur, potongan, bonus, uang pisah, PPh ditanggung, dan lainnya), beserta PPh 21 yang timbul.

| Berkas | Contoh | Tahun pajak |
|---|---|---|
| `PKB_WIKA_2025_2026.json` | 5 | 2025 |
| `PKB_Century_Textile_2024_2026.json` | 4 | 2025, 2026 |
| `PKB_AVCO_2024_2026.json` | 4 | 2025 |
| `PKB_Taekwang_2024_2026.json` | 4 | 2025 |
| `PKB_Sansan_2021_2024.json` | 4 | 2024 |

Setiap contoh memuat `judul`, `menguji`, `klausul` (id di `10_kebijakan_perusahaan/klausul/`), `masukan`, `asumsi`, `langkah` (`uraian`, `ekspresi` berangka literal, `hasil`, `sumber`), `nilai_harapan` beserta keterangannya, serta `ambiguitas` dan `putusan` yang dipakai. Untuk pakar, contoh ini ada di sheet "Kebijakan PKB" pada `review_pakar/uji_perhitungan_pph21.xlsx`.
