# Pantauan peristiwa prospektif

Disusun 2026-10-27 (RENCANA_DATASET.md, D26). Peristiwa prospektif adalah perubahan yang terbit **sesudah tanggal pra-registrasi**. Peristiwa ini bebas kontaminasi data latih, karena terbit setelah *cutoff* kedua model (Claude Opus 5.5: Juni 2026; GPT-6 Astra: 30 April 2026; lihat [model_cutoff.csv](model_cutoff.csv)), dan tidak pernah dilihat perancang sistem.

Saat ini **tidak ada peristiwa uji yang terbit sesudah kedua *cutoff***: peristiwa uji terakhir terbit 25 Februari 2026 (E12). Karena itu analisis kontaminasi bergantung pada dokumen kontrafaktual dan pada peristiwa di daftar ini.

## Yang dipantau

| Calon peristiwa | Kepastian | Perkiraan waktu | Jenis | Sumber pemantauan |
|---|---|---|---|---|
| Surat batas upah JP BPJS TK 2027 | **pasti**: terbit setiap tahun menurut rumus PP 45/2015 Ps. 29 ayat (3) | akhir Februari 2027, berlaku iuran Maret 2027 | T1 parameter | kantor cabang BPJS TK; mirror surat (lihat 01_regulasi/README.md) |
| PMK PTKP baru | rencana (berita Kompas, 25 Oktober 2026: masih difinalkan) | belum diketahui | T1 parameter | jdih.kemenkeu.go.id |
| PMK PPh 21 DTP TA 2027 (direncanakan untuk semua sektor) | rencana (diumumkan 30 September 2026) | akhir 2026 atau awal 2027 | T4 atau T5 | jdih.kemenkeu.go.id, peraturan.bpk.go.id |
| Perpanjangan keringanan iuran JKK sesudah Januari 2026 | belum ada tanda | - | T6 | peraturan.bpk.go.id |
| Perubahan iuran atau batas upah JKN | belum ada tanda | - | T1 | peraturan.bpk.go.id |
| Perubahan PMK 168/2023 atau PP 58/2023 | belum ada tanda | - | T2 atau T7 | status di JDIH BPK |

## Cara memantau

1. Setiap bulan, cari di JDIH Kemenkeu dan JDIH BPK dengan kata kunci "Pajak Penghasilan Pasal 21", "ditanggung pemerintah", "penghasilan tidak kena pajak", "iuran jaminan".
2. Setiap dokumen baru dicatat ke [peristiwa.csv](peristiwa.csv) dengan `bagian = prospektif`, tanggal diverifikasi ke teks, lalu PDF diunduh lewat `dataset/unduh_dataset.py`.
3. Δ\* peristiwa prospektif disusun dan dikunci (hash) **sebelum** alur LLM dijalankan pada dokumen itu.
EOF
echo ok