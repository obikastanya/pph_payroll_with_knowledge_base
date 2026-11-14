# Langkah Menulis Ulang Paper ke Versi Sendiri

Panduan untuk menulis ulang draf paper StaticKD (dibuat dengan bantuan AI) menjadi tulisan sendiri, dengan usaha sekecil mungkin dan tanpa mengubah fakta.

- **Naskah:** [_archive/jurnal_latex_v1/main.tex](../_archive/jurnal_latex_v1/main.tex) dan [_archive/jurnal_latex_v1/sections/](../_archive/jurnal_latex_v1/sections/)
- **Fakta yang dikunci** (angka, tabel, sitasi, persamaan): dokumen [Fakta Terkunci Paper StaticKD](https://claude.ai/code/artifact/5154d6e0-5827-4e95-9e8a-db4294caab9c)
- **Gaya yang dihindari:** [ai_text_criteria_to_be_avoided.txt](ai_text_criteria_to_be_avoided.txt)
- **Isi yang harus ada:** [paper_quality_check.md](paper_quality_check.md)

## Prinsip

- **Jangan minta AI untuk "memanusiakan" teks.** Hasilnya hanya gaya AI yang lain, dan kamu tidak memiliki teksnya sehingga sulit membelanya di depan reviewer atau dosen.
- **Jangan menulis ulang dari nol.** Struktur, angka, dan sitasi sudah benar; yang diganti hanya kalimatnya.
- **AI dipakai sebagai pemeriksa, bukan penulis.** AI boleh menandai masalah, tetapi perbaikannya kamu tulis sendiri.

## Langkah

### 1. Kunci fakta

Semua angka di naskah berasal dari `\val{...}` ([generated/numbers.tex](../_archive/jurnal_latex_v1/generated/numbers.tex)), dan isi tabel berasal dari `generated/tab_*.tex`. Keduanya dihasilkan notebook, jadi menulis ulang prosa tidak akan merusak angka.

Yang **tidak** diubah saat menulis ulang:
- `\val{...}`, `\rows{...}`, `\input{generated/...}`
- `\cite{...}` (tetap menempel pada klaim yang sama)
- persamaan dan label `eq:`, `tab:`, `fig:`, `sec:`

Yang perlu diwaspadai: angka yang diketik langsung di kalimat (bukan `\val`). Daftarnya ada di bagian "Angka yang ditulis langsung" pada dokumen fakta.

### 2. Buat kerangka balik per paragraf

Untuk setiap paragraf, tulis satu baris: **klaimnya apa, dan buktinya apa** (`\val`, tabel, gambar, atau sitasi).

- Kerangka ini boleh dibuat dengan bantuan AI, karena isinya hanya struktur.
- Yang wajib kamu kerjakan sendiri: memeriksa kerangka itu, mencoret klaim yang tidak kamu yakini, dan menambahkan hal yang hanya kamu tahu. Contohnya alasan memilih suatu metode, eksperimen yang gagal, dan hasil yang mengejutkan. Bagian inilah yang membuat tulisan terdengar seperti tulisan peneliti.

### 3. Tutup draf AI, lalu tulis dari kerangka

- Jangan biarkan draf lama terbuka. Kalau terbuka, kamu akan memparafrasenya tanpa sadar.
- Tulis cepat dan kasar dulu, seperti menjelaskan ke teman atau dosen pembimbing.
- Kalau ingin lebih cepat, dikte dengan voice typing lalu rapikan. Gaya bicara alami biasanya sudah lolos dari pola tulisan AI.
- Biarkan semua `\val`, `\cite`, dan referensi tabel di tempatnya; tulis kalimat di sekitarnya.

### 4. Periksa dengan AI, perbaiki sendiri

Minta AI menandai kalimat yang melanggar [ai_text_criteria_to_be_avoided.txt](ai_text_criteria_to_be_avoided.txt), **tanpa** memberi versi perbaikannya. Kamu yang memperbaiki kalimat yang ditandai.

### 5. Pengecekan akhir

1. Compile LaTeX; pastikan tidak ada `??` merah (kunci `\val` hilang) dan tidak ada referensi tabel/gambar yang rusak.
2. Cocokkan setiap kalimat yang menyebut angka dengan baris di dokumen fakta: apakah maknanya sama (dev vs uji, akurasi vs macro-F1, StaticKD vs teacher)?
3. Isi kolom Status cek sitasi di dokumen fakta.
4. Jalankan daftar cek di bagian 8 [ai_text_criteria_to_be_avoided.txt](ai_text_criteria_to_be_avoided.txt).

## Urutan prioritas

Jumlah kata dihitung dengan `wc -w` per file; angka `main.tex` termasuk preamble dan kode gambar TikZ, jadi prosanya lebih sedikit.

| Urutan | Bagian | Kata | Perlakuan | Alasan |
|---|---|---|---|---|
| 1 | Pendahuluan, Related Work (`main.tex`) | bagian dari 3.742 | Tulis ulang penuh | Bagian yang paling terasa "AI" dan paling menentukan kesan pertama reviewer |
| 2 | [discussion.tex](../_archive/jurnal_latex_v1/sections/discussion.tex) | 953 | Tulis ulang penuh | Tempat interpretasi dan pendapatmu paling dibutuhkan |
| 3 | [limitations.tex](../_archive/jurnal_latex_v1/sections/limitations.tex), [conclusion.tex](../_archive/jurnal_latex_v1/sections/conclusion.tex) | 333 + 299 | Tulis ulang penuh | Pendek; limitasi harus spesifik untuk studi ini |
| 4 | Metode (`main.tex`) | bagian dari 3.742 | Edit sedang | Isinya prosedur; cukup buang pola AI dan pastikan angka langsung tetap sama |
| 5 | [results.tex](../_archive/jurnal_latex_v1/sections/results.tex) | 1.499 | Edit ringan | Isinya deskripsi angka; buang kata dan pola dari daftar kriteria |
| 6 | Caption tabel dan gambar ([tables.tex](../_archive/jurnal_latex_v1/sections/tables.tex), `main.tex`, `results.tex`) | – | Edit ringan | Caption ditulis tangan walaupun isi tabel otomatis |
| 7 | [abstract.tex](../_archive/jurnal_latex_v1/sections/abstract.tex) | 210 | Tulis ulang penuh, **terakhir** | Abstrak merangkum versi final, jadi ditulis setelah bagian lain selesai |

## Pengungkapan penggunaan AI

Walaupun sudah ditulis ulang, AI tetap dipakai dalam proses penulisan. Cantumkan pengungkapannya di bagian Acknowledgment sesuai kebijakan IEEE: alat yang dipakai, dan untuk bagian mana (lihat bagian 7 di [ai_text_criteria_to_be_avoided.txt](ai_text_criteria_to_be_avoided.txt)).
