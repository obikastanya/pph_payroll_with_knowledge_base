# 01_regulasi — Dokumen regulasi asli

PDF/HTML asli dari JDIH BPK, JDIH Kemenkeu, dan pajak.go.id. Sistem tidak membaca folder ini secara langsung; teksnya diekstrak ke `13_teks/` (lihat kolom `files` di `13_teks/dokumen.csv`). URL unduhan dan SHA-256 ada di `manifest_tambahan.csv`.

| Lokasi | Isi | Peran di v2 |
|---|---|---|
| (akar folder) | 13 regulasi uji 2023–2026 dan regulasi dasar (UU PPh, UU HPP, PER-16/2016, PP BPJS 2015, Perpres JKN, PMK PTKP, dan lainnya) | Aliran dokumen tiap instans; sumber KB acuan |
| `pengecoh/` | Regulasi yang tidak mengubah PPh 21 pegawai tetap | Pengecoh di aliran dokumen |
| `pengembangan/` | 13 regulasi 2012–2022 | Membentuk KB dasar (pembaruan GOLD-D01–D13 di `12_emas`); set pengembangan, tidak dipakai di run terukur |
| `bpjs_tk_batas_upah_jp/` | Surat BPJS TK tentang batas upah JP 2023–2026 | Regulasi uji E01, E05, E08, E12 |
| `pendukung/` | UU Ketenagakerjaan, PP pengupahan, PP PKWT/PHK, PP pesangon, Permenaker THR | Dokumen pendukung (peran `support` di `13_teks`) |
