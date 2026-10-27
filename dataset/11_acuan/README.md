# 11_acuan — Acuan kebenaran

Acuan dipakai untuk memvalidasi KB emas (E0) sebelum KB emas dipakai menilai sistem. Setiap acuan disusun dari sumber yang berbeda, supaya kesalahan satu sumber tertangkap oleh sumber lain.

| Folder / berkas | Acuan | Isi |
|---|---|---|
| [gt2_kalkulator_djp/](gt2_kalkulator_djp/README.md) | GT2 | 18 kasus dihitung dengan kalkulator resmi DJP (rezim 2026), tangkapan layar formulir dan hasil, perbandingan dengan GT3 dan tabel TER (kategori, tarif, dan *gross-up* cocok 18/18; pembulatan berbeda Rp1 di 4 kasus) |
| [gt3_kasus_bertingkat/](gt3_kasus_bertingkat/README.md) | GT3 | 50 kasus bertingkat 2023–2026 dihitung dari teks regulasi, langkah hitung beserta pasal dan halaman |
| [gt5_contoh_kebijakan/](gt5_contoh_kebijakan/README.md) | GT5 | 21 contoh hitungan yang ditentukan kebijakan perusahaan (5 PKB nyata) |
| [diferensial_gt3.md](diferensial_gt3.md) | uji diferensial | GT3 dibandingkan dengan kalkulator prototipe lama; putusan atas setiap selisih |
| [b2_kasus/](b2_kasus/README.md) | masukan B2 | 100 kasus operasional untuk pembanding "LLM menghitung langsung" |

GT1 (contoh resmi) ada di [../07_kasus_uji_resmi/](../07_kasus_uji_resmi/README.md), GT4 (implementasi pihak ketiga) di [../03_pembanding/](../03_pembanding/README.md).

Aturan tafsir yang dipakai acuan dan sistem (pembulatan, kriteria DTP, natura, *gross-up*, dan lainnya) ditetapkan di [docs/spesifikasi/tafsir_perhitungan.md](../../docs/spesifikasi/tafsir_perhitungan.md).
