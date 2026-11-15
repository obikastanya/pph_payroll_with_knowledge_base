# GT3 — Kasus bertingkat

50 kasus PPh 21 pegawai tetap (tahun pajak 2023–2026), dihitung langkah demi langkah dari teks regulasi: 30 kasus bulanan dan 20 kasus setahun (Masa Pajak Terakhir), merata di empat rezim (PER-16 2023, TER 2024, TER + DTP 2025, TER + DTP 2026).

| Berkas | Isi |
|---|---|
| `GT3-001.json` … `GT3-050.json` | Satu kasus per berkas: `uraian`, `asumsi`, `input` (profil pegawai, pemberi kerja, komponen per bulan), `expected` (hasil per masa dan Masa Pajak Terakhir), `langkah` (rumus, nilai, pasal dan halaman PDF sumber), `cek_aritmetika` |
| `index.csv` | Satu baris per kasus |

Setiap langkah numerik dihitung ulang oleh pemeriksa terpisah dengan aritmetika pecahan eksak: 0 tidak cocok. Untuk pakar, kasus ini disajikan per kriteria di `review_pakar/uji_perhitungan_pph21.xlsx`.
