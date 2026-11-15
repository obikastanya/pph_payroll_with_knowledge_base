# Bahan review pakar pajak

| File | Yang diminta dari pakar |
|---|---|
| `uji_perhitungan_pph21.xlsx` | Memeriksa hasil hitung PPh 21 yang dipakai penelitian sebagai jawaban benar. Satu sheet per kriteria (PPh bulanan TER, PPh bulanan 2023, gross-up, Masa Pajak Terakhir, kebijakan PKB); satu baris per pegawai per masa. Isi kolom kuning: Status verifikasi (pass/failed) dan Catatan |

File dibangun ulang dengan `env\Scripts\python -m v2.tools.review_calculations` dari `dataset/11_acuan` (GT3 dan GT5).
