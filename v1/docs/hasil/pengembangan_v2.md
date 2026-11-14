# Pengembangan pipeline v2 dengan subagen buta (8–9 November 2026)

Tujuan: menemukan perubahan rancangan yang menaikkan tingkat keberhasilan akuisisi sebelum diuji ulang dengan API.
Tanpa biaya API. Setiap panggilan LLM pipeline diganti berkas permintaan (`FileClient`) yang dijawab oleh subagen
Claude Code (model yang sama, Opus 5.5). Subagen hanya membaca berkas permintaannya dan skema, tidak melihat repositori
atau acuan. Hasil ini untuk merancang, bukan untuk dilaporkan sebagai hasil uji.

Data: hanya set pengembangan (D05, D10, D11, SP01, SP02, SP03, SP08, SP09, SP10, SP11). Set uji (E01–E13, lima PKB)
tidak disentuh, sehingga tetap buta untuk uji API berikutnya.

## Hasil per iterasi

| Run | Konfigurasi | Kebijakan (7) | Regulasi (3) |
|---|---|---|---|
| e2-sintetis (API, hasil asli) | v1 | 0 benar, 5 salah, 2 abstain | – |
| devsub1-* | v1, subagen | (4 dok.) 1 benar, 3 salah | 2 benar, 1 salah |
| devsub2-* | v2 + putaran tinjau-diri | 0 benar, 4 salah, 3 abstain | 2 benar, 1 salah |
| devsub3c/3d/3e-pol, devsub3r-reg | v2 tanpa tinjau-diri, daftar periksa kebijakan, G5 lunak, konsensus selaras, G6 | **2 benar, 1 salah, 4 abstain** | 2 benar, 1 salah |

Per draf kebijakan (sebelum konsensus): benar sepenuhnya v1 0/8, v2 1/14, v3 5/14; nilai uang benar v1 4/8, v2 6/14,
v3 8/14. Alat: `system/tools/score_exchange.py`, `diagnose_update.py`, `reconsensus.py`.

## Temuan dan keputusan

1. **Antarmuka data kasus.** Model menulis nama atribut karangan (`employee('npwp')` di D05, `hr('attendance_days')` di
   SP01), pola yang sama dengan E07. S^G menyesuaikan diri dengan atribut yang dibaca draf, jadi G1–G5 tidak bisa
   mendeteksinya. Keputusan: daftar atribut data kasus di konteks (`pipeline/inputs.py`) dan gerbang G6: membaca input
   yang tidak ada adalah kegagalan yang boleh diperbaiki; input yang benar-benar baru diteruskan ke peninjau. Pesan
   perbaikan G6 harus melarang menghapus ketentuan, karena tanpa larangan itu model membuang tunjangan kehadiran SP01
   untuk lolos.
2. **G5 terlalu ketat.** Pemeriksaan tanggal berlaku menolak semua draf kebijakan v1 (dampak kebijakan sering hanya
   terlihat di bulan tertentu), dan perbaikan yang dipaksakannya memberi hasil campuran (1 membaik, 2 memburuk).
   Pemeriksaan elemen tanpa dampak menolak draf yang benar (SP09, SP10), sama dengan E04. Keputusan: keduanya menjadi
   peringatan bagi peninjau (`g5_date_warn`, `g5_vacuous_warn`).
3. **Konsensus peka terhadap ID aturan.** Tanda tangan perilaku memuat ID aturan di laporan konflik, sehingga dua draf
   yang sama perilakunya tetapi berbeda nama aturan tidak pernah sepakat. Keputusan: laporan konflik diselaraskan
   menurut fakta yang dihasilkan (`consensus_align`). Pada run API asli (e2-pkb, e2-sintetis) hasilnya tidak berubah
   (`experiments/*/reconsensus.json`), jadi angka di paper tidak terpengaruh.
4. **Panduan pemodelan.** "Ubah fakta yang paling spesifik, jangan menulis ulang total" menghilangkan kesalahan THP
   (SP08, SP11). Daftar periksa butir kebijakan (metode pemotongan, iuran, tarif JKK, perlakuan iuran pemberi kerja,
   pembulatan, pegawai keluar), dicatat walaupun nilainya sama dengan regulasi, menaikkan draf benar dari 1/14 ke 5/14.
   Contoh "jangan mengubah siapa yang menanggung pajak" dihapus karena menyesatkan.
5. **Putaran tinjau-diri dengan umpan balik eksekusi tidak dipakai.** Dari 12 tinjauan kebijakan, 3 memburuk dan tidak
   ada yang membaik; pada regulasi tidak ada perubahan. Kode tetap ada (`review.py`, `review=False`).
6. **Banyak "salah" pada kebijakan hanya beda laporan konflik.** Nilai pajak dan THP benar, tetapi fakta yang dilaporkan
   sebagai penyimpangan berbeda dari acuan (konvensi pemodelan). Untuk paper berikutnya, laporkan dua ukuran: nilai uang
   benar dan laporan konflik sama.
7. **Sisa kegagalan adalah pemahaman isi dokumen**, bukan antarmuka: D05 (DTP hanya untuk penghasilan teratur;
   `== True` vs `!= False`) dan SP03 (klausul DTP tidak diteruskan terlewat). Tidak ada perbaikan prompt umum yang
   menangkapnya; jalurnya adalah peninjau atau gerbang contoh perhitungan dari dokumen (belum dibuat).

## Konfigurasi untuk uji API berikutnya

`Config.v2(review=False)`: `case_inputs`, `prompt_v2` (panduan + daftar periksa kebijakan), `g5_date_warn`,
`g5_vacuous_warn`, `consensus_align`, `input_gate`. Bawaan `Config()` tetap v1 yang dibekukan, sehingga hasil paper
dapat diulang.

Batasan: set pengembangan kecil dan sebagian dokumennya dipakai untuk mendiagnosis, sehingga angka di atas optimistis.
Uji yang sah adalah run API v2 pada dokumen yang tidak dipakai di sini, dengan hipotesis yang dicatat sebelum run.
