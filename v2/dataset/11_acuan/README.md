# 11_acuan — Acuan untuk validasi KB acuan

Acuan dipakai untuk memvalidasi KB acuan (`12_emas`) sebelum KB itu menilai sistem. Setiap acuan berasal dari sumber berbeda.

| Folder | Acuan | Isi |
|---|---|---|
| `gt2_kalkulator_djp/` | GT2 | Kasus yang dihitung dengan kalkulator resmi DJP, dengan tangkapan layar |
| `gt3_kasus_bertingkat/` | GT3 | 50 kasus PPh 21 2023–2026 dihitung langkah demi langkah dari teks regulasi |
| `gt5_contoh_kebijakan/` | GT5 | 21 contoh hitungan dari klausul lima PKB nyata |

GT1 (contoh resmi dalam regulasi) ada di `../07_kasus_uji_resmi/`. GT3 dan GT5 disajikan untuk pakar di `review_pakar/uji_perhitungan_pph21.xlsx` (dibangun oleh `tools/review_calculations.py`).
