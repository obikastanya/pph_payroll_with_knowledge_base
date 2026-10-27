# Penjelasan draf paper dan draf PPT (27 Oktober 2026)

Dokumen ini menjelaskan isi draf paper dan slide progres mingguan setelah revisi konsep berdasarkan feedback dosen 27 Oktober 2026. Catatan status, keputusan terbuka, dan rincian implementasi sengaja ditaruh di sini, bukan di naskah, supaya paper tetap fokus ke penelitian.

## 1. Berkas yang dipakai

| Berkas | Lokasi | Keterangan |
|---|---|---|
| Draf paper | [paper/draft/naskah_draf_v6/main.pdf](paper/draft/naskah_draf_v6/main.pdf) | 8 halaman, format IEEE dua kolom, 37 rujukan. Sumber LaTeX ada di folder yang sama |
| Slide progres | [progress_mingguan/progress_mingguan_draf_v4.pptx](progress_mingguan/progress_mingguan_draf_v4.pptx) | 13 slide, sekitar 20 menit. Versi PDF: [progress_mingguan_draf_v4.pdf](progress_mingguan/progress_mingguan_draf_v4.pdf) |

Versi sebelumnya tetap disimpan sebagai riwayat dan tidak perlu dipakai:

| Versi | Perubahan |
|---|---|
| Paper v1 | Draf pertama dari skeleton: 21 halaman, dengan kotak status dan keputusan terbuka di dalam naskah |
| Paper v2 | Rujukan difilter dengan kriteria `paper/reference/README.md` |
| Paper v3 | Tiga pengecualian rujukan: Gogani-Khiabani dkk. 2025, buku *Ripple-Down Rules* 2021, Chen dkk. 2021 |
| Paper v4, v5 | Nama, NRP, email, dan program studi penulis |
| **Paper v6** | **Versi ringkas yang fokus ke penelitian (dipakai)** |
| PPT v1–v3 | Versi awal, penyesuaian rujukan, dan nama penulis |
| **PPT v4** | **Program studi, tanggal, dan slide 11 yang menunjuk paper v6 (dipakai)** |

## 2. Draf paper

### 2.1 Gambaran singkat

- **Judul:** *Knowledge-Based System* Adaptif untuk Perhitungan PPh 21 dengan Akuisisi Pengetahuan Berbantuan LLM dari Regulasi dan Kebijakan Perusahaan.
- **Penulis:** Obi Kastanya (6025252015) dan Mahathir Muhammad (6025252008), Program Studi Teknik Informatika, Institut Teknologi Sepuluh Nopember.
- **Argumen utama:** LLM mengusulkan pembaruan *knowledge base* setiap kali regulasi berubah, gerbang verifikasi menyaringnya, dan *engine* deterministik yang menghitung. Kebaruannya ada pada pembaruan inkremental yang diuji berantai pada perubahan regulasi nyata 2023–2026 (*regulation replay*), termasuk perambatan kesalahan dan dampaknya ke kebijakan perusahaan. Pola "LLM menyusun aturan, *engine* menghitung" tidak diklaim sebagai kebaruan, karena sudah dipakai karya lain.

### 2.2 Isi per bagian

| Bagian | Isi utama | Menjawab feedback | Status |
|---|---|---|---|
| Abstrak | Masalah, celah, usulan, dan cara evaluasi | – | Kalimat hasil menunggu eksperimen |
| I Pendahuluan | Masalah aturan pajak yang tertanam di kode; celah penelitian LLM untuk formalisasi; usulan; RQ1–RQ4; kontribusi K1–K4 | No. 2 | Lengkap |
| II Latar belakang | Cara menghitung PPh 21; Tabel I dimensi yang dicakup; batas kewenangan kebijakan perusahaan dengan contoh konflik lembur; jenis perubahan; rumusan masalah | No. 3 | Lengkap |
| III Penelitian terkait | *Rules as code*, LLM untuk formalisasi pajak, pembaruan berulang, dan representasi temporal; Tabel II posisi penelitian | No. 2 | Lengkap |
| IV Representasi | *Legal knowledge graph* untuk pengetahuan struktural dan *engine* untuk aritmetika; Definisi 1–3; ontologi (Gambar 2); SHACL dan SPARQL; resolusi konflik; Algoritma 1 | No. 1 | Lengkap; beberapa parameter terbuka |
| V Akuisisi | Definisi peristiwa, pembaruan, syarat adaptif A1–A4, dan adaptivitas; alur akuisisi; gerbang G1–G5 (Tabel III); konsensus perilaku; analisis dampak | No. 2, 5 | Lengkap; beberapa parameter terbuka |
| VI Metodologi evaluasi | Desain dan pembagian data; acuan GT1–GT5 dan ruang uji; korpus (Tabel IV); pembanding (Tabel V); hipotesis dan metrik utama (Tabel VI); analisis statistik | No. 3, 4, 5 | Lengkap; ambang hipotesis terbuka |
| VII Hasil dan pembahasan | Ancaman terhadap validitas | – | Hasil menunggu eksperimen |
| VIII Kesimpulan | Pengungkapan penggunaan AI | – | Menunggu hasil |

**Metrik utama per RQ**

| RQ | Pertanyaan singkat | Metrik |
|---|---|---|
| RQ1 | Dapatkah representasi menyatakan perubahan tanpa mengubah kode *engine*? | RA (*representational adaptability*) |
| RQ2 | Seberapa sering LLM menerapkan pembaruan benar, dan seberapa sering kesalahan lolos? | CAR (kegunaan) dan SER (keamanan) |
| RQ3 | Pada rangkaian perubahan nyata, apakah kesalahan merambat? | OAR dan kesalahan terpicu $I_n$ |
| RQ4 | Seberapa lengkap kebijakan perusahaan yang terdampak ditemukan? | *Recall* dan F2 |

### 2.3 Arti teks abu-abu di PDF

Teks abu-abu dalam kurung siku, misalnya di abstrak dan Bagian VII–VIII, adalah **isian**: tempat kalimat yang baru bisa ditulis setelah eksperimen E1–E4 dijalankan. Teks itu bukan bagian dari naskah final. Angka hasil sengaja tidak diisi agar tidak ada angka yang dikarang. Naskah yang akan dikirim tidak boleh memuat isian lagi.

### 2.4 Keputusan yang belum diambil

Daftar ini sebelumnya berupa kotak oranye di naskah v1–v5:

1. **Target publikasi.** Tugas mata kuliah, jurnal nasional, atau IEEE Access. Kalau IEEE Access, naskah harus berbahasa Inggris.
2. **Ukuran *lex specialis*.** Jumlah konjungsi di kondisi aturan, seperti di prototipe, atau relasi superioritas eksplisit di graf.
3. **Model LLM.** Model utama, model kedua (*open-weight*), dan anggaran API.
4. **Pembanding B2.** Perlu atau tidak menyertakan LLM yang menghitung PPh 21 langsung.
5. **Alat ekstraksi tabel PDF.** Boleh atau tidak dipakai LLM untuk menyalin tabel tarif seperti TER.
6. **Kolaborator.** Paling banyak dua orang untuk peran independen: penulis perubahan tak terlihat (usulan sedikitnya 15), penulis konflik buatan, penulis contoh perhitungan kebijakan (GT5), pembaca kedua pembaruan emas, dan pelabel kedua. Setiap peran yang tidak terisi perlu rencana cadangan.
7. **Parameter eksperimen.** Ambang hipotesis $\theta_1$–$\theta_4$, margin $\delta_S$, jumlah kandidat $m$ (usulan 5), dan jumlah pengulangan $R$ (usulan 3). Semuanya dikunci lewat pra-registrasi.
8. **Praktisi pajak.** Apakah ada akses ke praktisi pajak atau *tax center* untuk memeriksa pembaruan emas peristiwa TER.
9. **Usulan draf yang perlu disetujui:**
   - sifat aturan *tafsir* sebagai sifat keempat;
   - perlakuan bila dua kelompok konsensus sama besar (usulan: *abstain*);
   - apakah *gross-up* pada rezim disetahunkan (2023) masuk lingkup.
10. **Semantik berlaku surut.** Cara menetapkan nilai "sebagaimana seharusnya" untuk masa sebelum PMK 10/2025 terbit.

### 2.5 Status implementasi

| Sudah ada di prototipe | Masih rancangan |
|---|---|
| *Inference engine* deterministik: resolusi konflik, *fixed point gross-up*, aritmetika eksak, jejak sampai pasal | *Knowledge graph* (RDF/OWL), *shape* SHACL, *query* SPARQL |
| *Knowledge base* YAML: 90 aturan regulasi (85 wajib, 5 tafsir) dan 32 aturan Perusahaan X | Gerbang G1–G5, konsensus perilaku, *abstain* |
| 45 contoh resmi dengan 1.213 nilai harapan, 0 selisih tak terjelaskan | Korpus: peristiwa nyata, pengecoh, kontrafaktual, perubahan tak terlihat |
| 52 mutan pada *knowledge base* | Korpus kebijakan nyata (kandidat: sekitar 238 PKB publik di WageIndicator; lisensi belum dicek) |
| Asisten KB (PDF ke rancangan aturan lewat LLM), baru diuji sekali pada PDF fiktif | Pembaruan emas, generator ruang uji, pra-registrasi, eksperimen E0–E5 |

### 2.6 Sumber angka di naskah

| Angka | Sumber di repositori |
|---|---|
| 254 sel rumus; lembur dicatat tidak teratur | `dataset/02_studi_kasus/README.md` |
| Tujuh implementasi *open source*, semuanya memuat kesalahan | `dataset/03_pembanding/README.md` |
| 45 contoh resmi dan 1.213 nilai harapan | `README.md` bagian 5 |
| Lapisan Pasal 17, TER 44/40/41, DTP, batas upah pensiun | `dataset/01_regulasi/README.md` |
| 48 dan 366 titik batas; 2.995 kasus acak; batas SER 26% | Dihitung dari rumus di skeleton |
| Kemiripan teks 93–99% vs kecocokan persis 50,3% dan 20,51% | Abstrak Prior dkk. (NLLP 2025), sudah diverifikasi |

### 2.7 Kebijakan rujukan

Rujukan baru harus terbit 2021 ke atas, ber-*peer review*, dan ber-DOI Crossref. Standar seperti ELI, OWL-Time, PROV-O, dan SHACL dicatat sebagai sumber primer. Ada tiga pengecualian:
- Gogani-Khiabani dkk. (2025), karya yang paling dekat dengan *novelty*;
- buku *Ripple-Down Rules* (2021);
- Chen dkk. (2021), sumber rumus *pass@k*.

Rincian setiap rujukan ada di [FILTER_RUJUKAN.md](paper/draft/naskah_draf_v3/FILTER_RUJUKAN.md). Karya 2025–2026 baru dibaca dari abstraknya; naskah lengkapnya perlu dibaca sebelum klaim kebaruan dianggap final.

### 2.8 Cara kompilasi

Dari folder `paper/draft/naskah_draf_v6/`, jalankan `pdflatex main`, `bibtex main`, lalu `pdflatex main` dua kali, atau `tectonic -X compile main.tex`. Bibliografi memakai `paper/latex/references.bib`, `paper/latex/regulasi.bib`, dan `rujukan_tambahan.bib` di folder itu.

## 3. Draf PPT

### 3.1 Alur presentasi

| No. | Judul slide | Pesan utama | Poin bicara |
|---|---|---|---|
| 1 | Judul | Judul baru penelitian | Presentasi ini berisi perubahan konsep setelah feedback 27 Oktober dan progres draf paper |
| 2 | Lima feedback dosen, lima perubahan konsep | Setiap feedback punya satu perubahan | Semua perubahan masih rancangan; buktinya menunggu eksperimen |
| 3 | Fokus judul pindah ke kemampuan beradaptasi | Judul lama menonjolkan bentuk KB; judul baru menonjolkan adaptasi | Unsur judul lama tidak hilang, hanya pindah bagian |
| 4 | Representasi final: *legal knowledge graph* | YAML diganti *knowledge graph*; aritmetika tetap di *engine* | Contoh konflik lembur menjadi relasi eksplisit yang bisa dicari dengan satu *query* |
| 5 | *Novelty*: memperbarui KB yang sudah berjalan | Yang sudah dikerjakan orang lain vs kebaruan penelitian ini | Karya terdekat Gogani-Khiabani dkk. baru berupa gagasan tanpa uji berantai |
| 6 | LLM mengusulkan, gerbang menyaring, *engine* menghitung | Arsitektur dan lima gerbang | Tanpa G5, pembaruan kosong lolos semua gerbang |
| 7 | Ruang uji mencakup semua lapisan tarif | Lima lapisan Pasal 17 (termasuk 30%), 125 lapisan TER, uji batas, sampel acak | Acuan GT1–GT5; generator ruang uji belum dibangun |
| 8 | Satu metrik utama untuk setiap pertanyaan penelitian | RA, SER/CAR, OAR/$I_n$, *recall*/F2 | MAE tidak dipakai; contoh Prior dkk.: kemiripan teks tinggi menyembunyikan hasil salah |
| 9 | *Regulation replay* atas perubahan 2023–2026 | Garis waktu peristiwa dan syarat A1–A4 | Pengecoh, perubahan tak terlihat, dan peristiwa prospektif |
| 10 | Konsep sebelum dan sesudah revisi | Tabel perbandingan delapan aspek | Ringkasan semua perubahan konsep |
| 11 | Draf paper: 8 halaman, fokus ke penelitian | Status setiap bagian paper | Bagian I–VI lengkap; hasil menunggu eksperimen |
| 12 | Yang sudah ada di prototipe dan yang masih rancangan | Status implementasi yang jujur | Aplikasi web dan demo tidak lagi diklaim sebagai kontribusi |
| 13 | Langkah berikutnya dan keputusan yang perlu disepakati | Tahap 0–4 dan empat pertanyaan untuk dosen | Titik periksa dosen sebelum membangun *knowledge graph* |

Catatan pembicara yang lebih lengkap ada di setiap slide (menu *Notes* di PowerPoint).

### 3.2 Pertanyaan yang mungkin diajukan dosen

**Kenapa tidak LLM saja yang menghitung pajak?**
LLM tidak andal untuk penalaran pajak yang menuntut ketepatan (Blair-Stanek dkk. 2023; Nay dkk. 2024). *Engine* deterministik prototipe sudah tidak menghasilkan selisih yang tidak terjelaskan pada 1.213 nilai contoh resmi. LLM hanya dipakai untuk menyusun pembaruan aturan, dan pembaruan itu disaring gerbang.

**Apa bedanya dengan NTOL atau formalisasi IRC?**
Karya-karya itu memformalkan satu keadaan hukum dari nol. Penelitian ini memperbarui *knowledge base* yang sudah berjalan mengikuti rangkaian amandemen nyata, mengukur apakah kesalahan merambat, dan memeriksa dampaknya ke kebijakan perusahaan.

**Kenapa harus *knowledge graph*?**
Relasi seperti sumber pasal, amandemen, dan konflik menjadi eksplisit. SHACL dapat memvalidasi usulan LLM sebelum diterapkan, dan SPARQL dapat menemukan kebijakan yang terdampak dengan satu *query*. Nilai tambahnya diukur lewat ablasi AB5, yaitu skema biasa tanpa graf.

**Bagaimana memastikan hasil benar tanpa pakar pajak?**
Ada lima acuan independen (GT1–GT5), contoh resmi yang disimpan sebagai *holdout*, *mutation score* untuk menguji ketajaman kasus uji, dan pengadjudikasi kedua. Praktisi pajak akan dilibatkan bila ada aksesnya.

**Berapa skema yang diuji?**
Lima lapisan Pasal 17, termasuk 30%, dan 125 lapisan TER. Setiap batas diuji di tiga titik, yaitu 48 titik untuk Pasal 17 dan 366 titik untuk TER. Ditambah kombinasi 2-arah semua dimensi dan sedikitnya 2.995 kasus acak.

**Apa yang terjadi kalau LLM salah?**
Lima gerbang menyaring usulan. Bila tidak ada kandidat yang lolos, sistem *abstain* dan meneruskan dokumen ke peninjau manusia. Kesalahan yang tetap lolos dihitung sebagai SER.

**Apa buktinya perubahan regulasi bisa langsung diterapkan?**
Eksperimen *regulation replay* (E3) memeriksa syarat A1–A4 setelah setiap peristiwa, menghitung peristiwa yang berhasil diterapkan tanpa suntingan manusia, dan mengukur waktu dari dokumen terbit sampai sistem benar.

**Bukankah sembilan peristiwa terlalu sedikit?**
Karena itu hasil dilaporkan dengan selang kepercayaan eksak dan ambang yang dapat dicapai jumlah data. Contohnya, sepuluh dokumen tanpa kesalahan hanya membuktikan SER paling tinggi 26%. Cakupan ditambah lewat dokumen kontrafaktual, perubahan tak terlihat, dan peristiwa prospektif.

## 4. Yang perlu dikerjakan berikutnya

1. Baca utuh karya terdekat: Gogani-Khiabani dkk. (2025), NTOL, formalisasi IRC, dan LLM ke Catala. Sesudahnya, cek ulang Tabel II.
2. Catat kebijakan rujukan dan keputusan yang sudah diambil di Log keputusan `PANDUAN_PENELITIAN.md`.
3. Salin entri `CATATAN_AI.md` dari folder `paper/draft/naskah_draf_v1/` sampai `naskah_draf_v6/` ke `journal.md`.
4. Jalankan `git pull` sebelum *commit*, karena cabang lokal tertinggal dua *commit* dari `origin/main`.
