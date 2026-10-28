# Panduan tahapan penelitian

Panduan ini mengurutkan seluruh pekerjaan dari keadaan sekarang sampai paper siap dikirim. Acuannya adalah kerangka paper di [paper/draft/skeleton.tex](paper/draft/skeleton.tex) (PDF: [skeleton.pdf](paper/draft/skeleton.pdf)). Bila panduan ini dan *skeleton* berbeda, *skeleton* yang berlaku, lalu panduan ini diperbaiki.

Judul penelitian: *Knowledge-Based System* Adaptif untuk Perhitungan PPh 21 dengan Akuisisi Pengetahuan Berbantuan LLM dari Regulasi dan Kebijakan Perusahaan.

## Cara memakai panduan ini

- Kerjakan tahap secara berurutan. Sebuah tahap baru dimulai bila kriteria selesai tahap sebelumnya terpenuhi.
- Setiap tahap berisi tujuan, prasyarat, langkah, perubahan pada proyek, keluaran, dan kriteria selesai.
- Centang langkah yang sudah selesai (`- [x]`). Catat setiap keputusan di bagian *Log keputusan* di akhir dokumen.
- Rujukan seperti "*skeleton* Bagian VI" menunjuk bagian kerangka paper yang dipenuhi oleh langkah itu.
- Proyek yang sudah ada diperlakukan sebagai prototipe. Bagian yang sesuai dengan *skeleton* dipakai, dan bagian yang tidak sesuai diubah. Peta aset proyek ada di Lampiran A.

## Prinsip yang berlaku di semua tahap

1. **Kebenaran dinilai dari perilaku.** Pembaruan dinilai benar bila hasil perhitungannya sama dengan acuan, bukan bila bentuk aturannya mirip dengan aturan emas.
2. **Data untuk sistem terpisah dari data untuk menilai sistem.** Kasus uji gerbang ($S^G$) dan kasus uji evaluasi ($S^E$) tidak boleh beririsan, dan kode alur akuisisi tidak boleh membaca $S^E$.
3. **Instrumen divalidasi sebelum dipakai.** *Knowledge base* emas dan $S^E$ harus lulus validasi (E0) sebelum eksperimen utama.
4. **Rancangan dikunci sebelum eksperimen.** Hipotesis, metrik, ambang, dan pembagian data didaftarkan ke layanan pra-registrasi sebelum data uji disentuh. Hipotesis yang terbantah dilaporkan sebagai terbantah.
5. **Materi tersembunyi tidak masuk repo publik.** Perubahan tak terlihat, konflik buatan, contoh perhitungan kebijakan (GT5), subset *holdout* contoh resmi, dan nilai harapan $S^E$ disimpan di repo privat. Hash SHA-256 berkasnya di-*commit* ke repo ini sebagai bukti waktu.
6. **Istilah.** Karya ini disebut "penelitian", bukan "makalah". Sumber kebenaran disebut "acuan" (GT1–GT5), bukan "oracle". Istilah teknis bahasa Inggris tidak diterjemahkan dan ditulis miring.
7. **Penggunaan AI dicatat.** Setiap pemakaian asisten AI untuk menulis kode atau teks dicatat di [journal.md](journal.md), karena IEEE mewajibkan pengungkapannya.

## Peta tahap

| Tahap | Nama | Bagian *skeleton* | Keluaran utama |
|---|---|---|---|
| 0 | Persiapan dan keputusan terbuka | Rencana kerja, keputusan terbuka | Log keputusan, repo privat, kolaborator |
| 1 | Kajian pustaka | III | Tabel posisi, bibliografi |
| 2 | Definisi domain dan rumusan masalah | II | Ruang lingkup, dimensi, taksonomi |
| 3 | Spesifikasi representasi pengetahuan | IV | Definisi formal, ontologi, bahasa ekspresi |
| 4 | Spesifikasi akuisisi dan kontrak antarmuka | V | Syarat A1–A4, spesifikasi gerbang, format data |
| 5 | Pembangunan representasi dan *engine* | IV | *Knowledge graph*, *engine* baru |
| 6 | Penyusunan korpus | VI (Korpus) | Korpus peristiwa, pengecoh, kontrafaktual, kebijakan, perubahan tak terlihat |
| 7 | Penyusunan emas | VI (Rantai kepercayaan) | $\mathcal{K}^\star_n$, $\Delta^\star_n$ |
| 8 | Ruang uji dan acuan | VI (Ruang uji, Rantai kepercayaan) | $S^E$, GT1–GT5, operator mutasi |
| 9 | Pembangunan alur akuisisi | V | Alur LLM dengan gerbang G1–G5 |
| 10 | Pembanding, ablasi, dan skrip analisis | VI (Pembanding, Analisis statistik) | B1–B5, AB1–AB5, skrip statistik |
| 11 | Kalibrasi pada data pengembangan | VI (Pembagian data) | Alur yang dibekukan, perkiraan biaya |
| 12 | Pra-registrasi | VI (Desain penelitian) | Pendaftaran OSF, *tag* git |
| 13 | E0, validasi instrumen | VI (Rantai kepercayaan), VII | Instrumen lulus |
| 14 | E1, adaptivitas representasi (RQ1) | VII | RA |
| 15 | E2, akuisisi terisolasi (RQ2) | VII | SER, CAR |
| 16 | E3, *regulation replay* (RQ3) | VII | OAR, kesalahan terpicu |
| 17 | E4, analisis dampak (RQ4) | VII | *Recall*, F2 |
| 18 | E5, pembanding motivasi | VII | Hasil B2 |
| 19 | Peristiwa prospektif | VI, VII | Hasil peristiwa baru |
| 20 | Analisis dan penyajian hasil | VII, VIII | Tabel, gambar, putusan hipotesis |
| 21 | Penulisan naskah | Semua | Draf lengkap |
| 22 | Telaah dan revisi | Semua | Draf yang sudah ditelaah |
| 23 | Rilis artefak | K4 | Repo bersih, DOI arsip |
| 24 | Finalisasi dan pengiriman | Semua | Paper siap kirim |

---

## Tahap 0. Persiapan dan keputusan terbuka

**Tujuan.** Menjawab semua keputusan yang memengaruhi rancangan, dan menyiapkan sarana kerja.

**Prasyarat.** *Skeleton* dan [catatan revisi](feedback_and_revision/revision_27_10_26.md) sudah dibaca.

**Langkah**
- [ ] Jawab sembilan keputusan terbuka di *skeleton* (kotak oranye di Bagian X) dan catat di Log keputusan:
  - [ ] target publikasi (tugas mata kuliah, jurnal nasional, atau IEEE Access);
  - [ ] apakah *preprint* boleh dikutip;
  - [ ] ukuran *lex specialis*, yaitu sintaks kondisi atau relasi superioritas eksplisit;
  - [ ] model LLM utama, model kedua (*open-weight*), dan anggaran API;
  - [ ] apakah pembanding B2 (LLM menghitung langsung) disertakan;
  - [ ] apakah LLM boleh memakai alat ekstraksi tabel PDF;
  - [ ] kolaborator untuk peran independen (lihat langkah berikut);
  - [ ] ambang hipotesis (diputuskan final di Tahap 12, tetapi arahnya ditetapkan di sini);
  - [ ] pembaca kedua $\Delta^\star$ dan praktisi pajak.
- [ ] Cari kolaborator, paling banyak dua orang, untuk peran yang menuntut independensi. Peran itu adalah penulis perubahan tak terlihat, penulis konflik buatan, penulis contoh perhitungan kebijakan (GT5), pembaca kedua $\Delta^\star$, pengadjudikasi kedua, pelabel kedua RQ4, dan bila ada, praktisi pajak. Catat nama dan perkiraan jam kerjanya.
- [ ] Untuk setiap peran yang tidak terisi, tulis rencana cadangan dan cara melaporkannya sebagai keterbatasan (*skeleton* Bagian VI, Kolaborator dan rencana cadangan).
- [ ] Buat repo privat untuk materi tersembunyi, lalu siapkan skrip yang menghitung hash SHA-256 setiap berkas di dalamnya.
- [ ] Tetapkan konvensi *tag* git (Lampiran C) dan format pesan *commit*.
- [ ] Siapkan akun di layanan pra-registrasi (OSF atau AsPredicted).
- [ ] Siapkan kunci API dan batas biaya bulanan di penyedia LLM.

**Perubahan pada proyek**
- Tambahkan bagian Log keputusan di dokumen ini, atau berkas terpisah bila panjang.
- Pastikan `.env` tetap tidak di-*commit*.

**Keluaran.** Log keputusan terisi, daftar kolaborator, repo privat, akun pra-registrasi.

**Kriteria selesai.** Semua keputusan terbuka punya jawaban atau tanggal keputusan, dan setiap peran independen punya nama atau rencana cadangan.

---

## Tahap 1. Kajian pustaka

**Tujuan.** Memastikan celah penelitian memang ada dan mengisi *skeleton* Bagian III.

**Prasyarat.** Keputusan tentang *preprint* (Tahap 0).

**Langkah**
- [ ] Baca utuh karya terdekat, bukan hanya abstraknya:
  - [ ] NTOL (*Frontiers in Artificial Intelligence*, 2026);
  - [ ] formalisasi IRC dengan LLM (*Artificial Intelligence and Law*, 2026);
  - [ ] LLM ke Catala (NLLP 2025, ProLaLa 2024);
  - [ ] Graus (ICAIL 2026);
  - [ ] Law&Order (arXiv 2026), bila *preprint* boleh dikutip.
- [ ] Cari dan baca pustaka yang belum ada di bibliografi:
  - [ ] *Ripple-Down Rules* dan *cornerstone case* (Compton dan Jansen);
  - [ ] perubahan hukum dalam *defeasible logic* temporal (Governatori dan Rotolo);
  - [ ] OpenFisca;
  - [ ] penyuntingan pengetahuan LLM secara berurutan;
  - [ ] CodeUpdateArena;
  - [ ] *pass@k* (Chen dkk., 2021) dan *n@k* (AlphaCode);
  - [ ] *selective prediction* dan kurva risiko–cakupan (Geifman dan El-Yaniv);
  - [ ] *benchmark* penalaran hukum temporal 2026;
  - [ ] standar ELI, OWL-Time, PROV-O, SHACL, dan LegalRuleML.
- [ ] Tambahkan entri ke [paper/latex/references.bib](paper/latex/references.bib) dengan metadata dari Crossref, sesuai kriteria di [paper/reference/README.md](paper/reference/README.md). Standar dicatat sebagai sumber primer, seperti regulasi.
- [ ] Isi Tabel posisi (*skeleton* Bagian III) untuk setiap karya terdekat: domain, representasi, penyusun pengetahuan, pembaruan inkremental, perambatan kesalahan diukur, lapisan perusahaan, dan evaluasi.
- [ ] Tulis satu kalimat penutup per subbagian Bagian III tentang apa yang belum dikerjakan kelompok penelitian itu.
- [ ] Periksa ulang klaim *novelty* di [catatan revisi](feedback_and_revision/revision_27_10_26.md) bagian 3. Bila ada karya yang sudah mengerjakan pembaruan inkremental, rumuskan ulang *novelty* sebelum lanjut.

**Keluaran.** Draf Bagian III, Tabel posisi terisi, bibliografi bertambah.

**Kriteria selesai.** Setiap sel "pembaruan inkremental" dan "perambatan kesalahan diukur" di Tabel posisi terisi berdasarkan naskah lengkap, dan *novelty* tetap berdiri.

---

## Tahap 2. Definisi domain dan rumusan masalah

**Tujuan.** Menetapkan ruang lingkup, dimensi, dan taksonomi yang dipakai semua tahap berikutnya (*skeleton* Bagian II).

**Prasyarat.** Tahap 0.

**Langkah**
- [ ] Tetapkan batas ruang lingkup beserta alasannya: subjek pajak (pegawai tetap), jenis penghasilan, dan hal yang di luar lingkup.
- [ ] Finalkan dimensi ruang pajak (Tabel dimensi di Bagian II): rezim, lapisan Pasal 17, kategori TER, status PTKP, metode, pola kerja, dan jenis penghasilan.
- [ ] Verifikasi jumlah lapisan TER per kategori langsung dari lampiran PP 58/2023. Angka di repo saat ini A 44, B 40, C 41.
- [ ] Tulis batasan antardimensi, misalnya status PTKP menentukan kategori TER, DTP hanya ada sejak 2025, dan metode disetahunkan hanya sampai 2023.
- [ ] Tetapkan taksonomi jenis perubahan: parameter, tabel tarif, klasifikasi, aturan atau fasilitas baru, pergantian metode, pencabutan, berlaku surut, dan perubahan kebijakan perusahaan.
- [ ] Tetapkan taksonomi konflik antara kebijakan perusahaan dan aturan wajib, sebagai dasar konflik buatan (Tahap 6) dan label RQ4.
- [ ] Tetapkan taksonomi kesalahan LLM sebelum ada keluaran LLM: nilai salah, masa berlaku salah, kondisi atau cakupan salah, pengecualian terlewat, pencabutan terlewat, lapisan atau sifat salah, kutipan karangan, dan perubahan pada pengecoh.
- [ ] Tulis subbagian kebijakan perusahaan dan batas kewenangannya, dengan satu contoh konflik konkret.
- [ ] Tulis rumusan masalah formal (subbagian Rumusan masalah).

**Perubahan pada proyek.** Tulis spesifikasi di folder baru, misalnya `docs/spesifikasi/domain.md`.

**Keluaran.** Spesifikasi domain, tiga taksonomi, draf Bagian II.

**Kriteria selesai.** Dimensi dan batasannya cukup jelas untuk membangun generator ruang uji tanpa keputusan tambahan, dan ketiga taksonomi tertulis.

---

## Tahap 3. Spesifikasi representasi pengetahuan

**Tujuan.** Menetapkan representasi final *knowledge base* secara formal (*skeleton* Bagian IV), menjawab feedback no. 1.

**Prasyarat.** Tahap 2.

**Langkah**
- [ ] Tulis Definisi *knowledge base* dan Definisi aturan secara formal, termasuk lapisan, sifat (wajib, *default*, opsional), masa berlaku $[t_s, t_e]$, tanggal pencatatan $t_c$, kondisi, ekspresi, dan sumber hukum.
- [ ] Tulis Definisi hasil perhitungan $\mathit{hasil}(\mathcal{K}, x, t, \omega)$, dan tetapkan himpunan fakta keluaran yang dinilai. Fakta utamanya PPh 21 yang dipotong per pegawai per masa; fakta pendukungnya PPh setahun, bruto, PKP, dan *take home pay*.
- [ ] Rancang ontologi: kelas (Regulasi, Pasal, Aturan, Konsep, Parameter, Tabel, Kebijakan Perusahaan, Versi), relasi (memuat, bersumber, mengubah, mencabut, menghasilkan, membaca, berkonflik), dan standar yang dipakai ulang (ELI, OWL-Time, PROV-O).
- [ ] Tetapkan bahasa ekspresi: daftar fungsi yang diizinkan dan sistem tipenya.
- [ ] Tetapkan semantik temporal: arti $[t_s, t_e]$, $t_c$, dan sumbu waktu yang menentukan aturan berlaku pada suatu masa.
- [ ] Tetapkan relasi superioritas secara formal, ukuran *lex specialis* sesuai keputusan Tahap 0, dan perilaku bila tidak ada pemenang tunggal.
- [ ] Tetapkan bentuk kanonik unsur, yaitu normalisasi aturan agar unsur dapat dicocokkan.
- [ ] Tetapkan batas ekspresivitas, yaitu jenis ketentuan yang sengaja tidak dapat dinyatakan.
- [ ] Tulis langkah inferensi (Algoritma 1 di *skeleton*): seleksi aturan menurut waktu, graf dependensi, urutan evaluasi, resolusi konflik, definisi melingkar, dan jejak penjelasan.
- [ ] Gambar ontologi untuk Gambar ontologi di Bagian IV.

**Perubahan pada proyek**
- Bandingkan spesifikasi dengan *engine* sekarang ([engine/kb.py](engine/kb.py), [engine/inferensi.py](engine/inferensi.py)). Catat setiap perbedaan yang harus diubah di Tahap 5, misalnya ukuran *lex specialis* yang saat ini dihitung dari jumlah konjungsi.
- Tulis spesifikasi di `docs/spesifikasi/representasi.md`.

**Keluaran.** Spesifikasi representasi, daftar perubahan *engine*, draf Bagian IV, gambar ontologi.

**Kriteria selesai.** Semua butir kotak "Harus didefinisikan" di Bagian IV terjawab.

---

## Tahap 4. Spesifikasi akuisisi dan kontrak antarmuka

**Tujuan.** Menetapkan definisi pembaruan dan adaptivitas, spesifikasi alur akuisisi, dan format data bersama (*skeleton* Bagian V).

**Prasyarat.** Tahap 3.

**Langkah: definisi**
- [ ] Tulis Definisi peristiwa perubahan, pembaruan $\Delta = \langle \Delta^+, \Delta^\sim, \Delta^- \rangle$, syarat adaptif A1–A4, adaptivitas representasional, dan adaptivitas operasional.
- [ ] Untuk setiap syarat A1, A2, A3$_t$, A3$_\omega$, dan A4, tulis prosedur uji otomatisnya.
- [ ] Tetapkan semantik berlaku surut menurut mekanisme hukumnya. Baca PMK 10/2025 untuk menentukan bagaimana fasilitas DTP yang terbit sesudah masa berlakunya diselesaikan, lalu tetapkan nilai *sebagaimana seharusnya* untuk masa sebelum tanggal terbit.

**Langkah: alur akuisisi**
- [ ] Spesifikasikan delapan tahap alur: pemotongan dokumen per pasal, penilaian relevansi berkutipan, penyusunan konteks dari graf, $m$ kandidat, gerbang, pemilihan konsensus atau *abstain*, peninjauan manusia, dan penerapan.
- [ ] Spesifikasikan setiap gerbang:
  - [ ] G1: daftar *shape constraint* (SHACL);
  - [ ] G2: cara mencocokkan kutipan dengan teks sumber;
  - [ ] G3: pemeriksaan tipe, dependensi, konflik, dan anomali;
  - [ ] G4: regresi pada $S^G$ untuk masa sebelum $t_\mathit{berlaku}$;
  - [ ] G5: non-vakuitas untuk unsur yang ditambah, diubah, dan dicabut, serta pemeriksaan tanggal dan subjek.
- [ ] Spesifikasikan generator $S^G$ otomatis yang menyasar kondisi $\varphi$ setiap unsur yang berubah.
- [ ] Tetapkan nilai $m$, batas putaran perbaikan, dan cara mengelompokkan kandidat menurut hasilnya pada $S^G$.
- [ ] Tetapkan arti *terdampak* untuk RQ4: (a) nilai fakta keluaran berubah, (b) aturan pemenang berubah, (c) kebijakan menjadi berkonflik dengan aturan wajib.
- [ ] Tetapkan konfigurasi LLM yang dicatat: model, versi, tanggal akses, *training cutoff*, parameter pembangkitan, format keluaran.

**Langkah: kontrak antarmuka**
- [ ] Format $\Delta$ sebagai skema JSON, dipakai alur, emas, pembanding, dan skrip penilaian.
- [ ] Format kasus uji dan nilai harapan, yaitu tupel kasus, masa, tanggal pengetahuan, fakta, dan nilai.
- [ ] Format tabel peristiwa perubahan: dokumen, tanggal terbit, tanggal berlaku, jenis, ukuran $\Delta^\star$, bagian data.
- [ ] Format log eksperimen: *prompt*, keluaran, token, biaya, waktu, hasil setiap gerbang.

**Perubahan pada proyek.** Tulis `docs/spesifikasi/akuisisi.md` dan `docs/spesifikasi/format_data.md`, serta skema JSON di folder skema yang dipakai bersama.

**Keluaran.** Spesifikasi akuisisi, kontrak antarmuka, draf Bagian V.

**Kriteria selesai.** Semua butir "Harus didefinisikan" di Bagian V terjawab, dan setiap syarat A1–A4 punya prosedur uji yang dapat diotomatisasi.

**Titik periksa dosen (disarankan).** Tunjukkan definisi Tahap 2–4 ke dosen sebelum membangun. Perubahan definisi sesudah Tahap 5 jauh lebih mahal.

---

## Tahap 5. Pembangunan representasi dan *engine*

**Tujuan.** Mewujudkan representasi Tahap 3 tanpa kehilangan ketepatan perhitungan yang sudah dicapai prototipe.

**Prasyarat.** Tahap 3 dan 4.

**Langkah**
- [ ] Bekukan keadaan prototipe sekarang dengan *tag* git, lalu simpan keluaran semua eksperimen lama sebagai acuan regresi migrasi.
- [ ] Bangun ontologi dalam RDF/OWL dan *shape* SHACL untuk G1.
- [ ] Tulis pemigrasi dari YAML ([kb/regulasi/](kb/regulasi/), [kb/perusahaan/](kb/perusahaan/)) ke graf. Ekspresi perhitungan menjadi atribut *node* aturan.
- [ ] Ubah *engine* agar membaca aturan dari graf. Pemuat YAML hanya dipertahankan untuk pemeriksaan kesetaraan.
- [ ] Terapkan perubahan *engine* dari daftar Tahap 3, misalnya ukuran *lex specialis*.
- [ ] Periksa kesetaraan: hasil semua kasus lama dari *engine* baru harus sama persis dengan acuan regresi. Setiap selisih dijelaskan sebelum lanjut.
- [ ] Tulis uji unit *engine* yang terpisah dari *knowledge base*, terhadap aritmetika yang dihitung tangan, sebagai syarat E0.
- [ ] Bangun pemeriksa anomali *knowledge base*: aturan redundan, berkonflik, tercakup, mati, dan rujukan menggantung. Dipakai G3 dan metrik RQ3.
- [ ] Bangun *test suite* resolusi konflik: pasangan aturan dengan pemenang hukum yang diketahui untuk setiap asas.
- [ ] Bangun pemeriksa kelengkapan jejak: setiap fakta keluaran harus punya jejak sampai sumber hukum.
- [ ] Bangun *query* SPARQL untuk analisis dampak lintas lapis sesuai definisi *terdampak*.
- [ ] Bangun ekspor riwayat pengembangan *engine*: setiap *commit* yang mengubah *engine* dipetakan ke regulasi pemicunya (bahan mitigasi bias pandangan belakang, E1).

**Perubahan pada proyek.** [engine/](engine/), [kb/](kb/), dan [tests/](tests/) berubah. [web/](web/), [ui/](ui/), dan [jembatan/](jembatan/) tidak termasuk paper; sesuaikan hanya bila demo masih dibutuhkan.

**Keluaran.** *Knowledge graph*, *engine* yang membaca graf, uji unit *engine*, pemeriksa anomali, *test suite* resolusi konflik, *query* dampak.

**Kriteria selesai.** Pemeriksaan kesetaraan lulus tanpa selisih tak terjelaskan, dan seluruh uji lulus.

---

## Tahap 6. Penyusunan korpus

**Tujuan.** Menyiapkan semua dokumen masukan untuk eksperimen (*skeleton* Bagian VI, Korpus dan Pembagian data).

**Prasyarat.** Tahap 2 (taksonomi) dan Tahap 4 (format tabel peristiwa).

**Langkah: korpus uji**
- [ ] Susun daftar peristiwa perubahan nyata dalam rentang penelitian yang memengaruhi PPh 21 pegawai tetap. Kandidatnya ada di [catatan revisi](feedback_and_revision/revision_27_10_26.md) bagian 6. Verifikasi setiap kandidat terhadap teks regulasinya.
- [ ] Pastikan setiap jenis perubahan pada taksonomi terwakili minimal satu peristiwa. Jenis yang tidak terwakili dicatat sebagai keterbatasan.
- [ ] Arsipkan dokumen sumber setiap peristiwa beserta *checksum*-nya, lalu potong per pasal.
- [ ] Susun dokumen pengecoh, termasuk pengecoh sulit: regulasi yang menyebut PPh 21 tetapi tidak mengubah perhitungan pegawai tetap.
- [ ] Isi Tabel korpus di *skeleton*, kecuali kolom $|\Delta^\star|$ yang diisi di Tahap 7.

**Langkah: korpus pengembangan**
- [ ] Susun regulasi fiktif dan perubahan historis sebelum rentang penelitian, misalnya perubahan PTKP dan lapisan Pasal 17 sebelum 2023.
- [ ] Sisihkan sebagian kecil dokumen kebijakan buatan untuk pengembangan, agar *prompt* juga disetel untuk dokumen kebijakan.
- [ ] Pastikan tidak ada peristiwa uji di korpus pengembangan.

**Langkah: dokumen kontrafaktual**
- [ ] Bangun generator yang mengubah nilai, tanggal, atau ambang di dokumen nyata secara konsisten, dan yang menurunkan $\Delta^\star$ kontrafaktual secara terprogram dari $\Delta^\star$ asli.
- [ ] Catat setiap nilai yang diubah, untuk menghitung laju hafalan.

**Langkah: materi tersembunyi (oleh kolaborator)**
- [ ] Kolaborator menulis perubahan tak terlihat dari taksonomi perubahan, minimal 15 bila memungkinkan, masing-masing dengan 5–10 contoh perhitungan yang sudah dihitung.
- [ ] Kolaborator menulis konflik buatan dari taksonomi konflik, sebelum detektor dampak dibekukan.
- [ ] Semua materi ini disimpan di repo privat. Hash SHA-256 setiap berkas di-*commit* ke repo ini.

**Langkah: korpus kebijakan perusahaan**
- [ ] Kumpulkan dokumen kebijakan nyata yang terbuka untuk umum, misalnya perjanjian kerja bersama atau peraturan perusahaan yang dipublikasikan.
- [ ] Lengkapi dengan kebijakan buatan untuk jenis konflik yang tidak muncul di dokumen nyata. [dataset/05_katalog_kebijakan/](dataset/05_katalog_kebijakan/) bisa menjadi bahan awal.
- [ ] Tandai kebijakan nyata dan buatan agar dapat dilaporkan terpisah.
- [ ] Siapkan setiap dokumen kebijakan sebagai masukan akuisisi (E2), dengan *checksum* dan pemotongan per pasal seperti dokumen regulasi.
- [ ] Kolaborator menulis 5–10 contoh perhitungan untuk setiap dokumen kebijakan (GT5), sebelum peneliti menyusun $\Delta^\star$-nya. Contoh ini disimpan di repo privat dan hash-nya di-*commit*.

**Perubahan pada proyek.** Korpus baru di folder terpisah, misalnya `korpus/`. Dokumen regulasi di [dataset/01_regulasi/](dataset/01_regulasi/) dipakai ulang.

**Keluaran.** Korpus uji, korpus pengembangan, generator kontrafaktual, korpus kebijakan, materi tersembunyi beserta hash-nya, Tabel korpus.

**Kriteria selesai.** Tabel korpus lengkap, setiap dokumen ber-*checksum*, dan hash materi tersembunyi sudah di-*commit*.

---

## Tahap 7. Penyusunan emas

**Tujuan.** Menyusun $\mathcal{K}^\star_n$ untuk setiap keadaan hukum dan $\Delta^\star_n$ untuk setiap peristiwa (*skeleton* Bagian V dan VI).

**Prasyarat.** Tahap 5 dan 6.

**Langkah**
- [ ] Pecah *knowledge base* yang ada, yang saat ini mencakup 2023–2026 sekaligus, menjadi keadaan awal (awal rentang penelitian) dan rangkaian $\Delta^\star_n$ per peristiwa. Pastikan $\mathcal{K}^\star_0 \oplus \Delta^\star_1 \oplus \dots \oplus \Delta^\star_N$ menghasilkan perilaku yang sama dengan *knowledge base* lengkap.
- [ ] Susun keadaan awal dan $\Delta^\star$ untuk peristiwa pengembangan, termasuk perubahan historis sebelum 2023.
- [ ] Susun $\Delta^\star$ untuk setiap peristiwa uji dari teks sumbernya.
- [ ] Susun $\Delta^\star$ untuk setiap dokumen kebijakan, yaitu pembaruan pada lapisan perusahaan.
- [ ] Pembaca kedua memeriksa setiap $\Delta^\star$ terhadap teks yang sama. Catat ketidaksepakatan dan keputusannya.
- [ ] Hitung kesepakatan atas keputusan unsur dengan Krippendorff's $\alpha$.
- [ ] Untuk regulasi berlaku surut, susun emas sesuai semantik mekanisme hukum dari Tahap 4.
- [ ] Turunkan $\Delta^\star$ kontrafaktual dengan generator Tahap 6.
- [ ] Kunci semua $\Delta^\star$ uji dengan stempel waktu (hash di-*commit*) sebelum LLM dijalankan pada data uji.
- [ ] Isi kolom $|\Delta^\star|$ di Tabel korpus.
- [ ] Untuk RQ1, nilai adaptivitas representasional setiap peristiwa nyata dan setiap dokumen kebijakan: apakah $\Delta^\star$-nya dapat dinyatakan tanpa mengubah *engine*.

**Keluaran.** $\mathcal{K}^\star_n$, $\Delta^\star_n$, log pemeriksaan, nilai $\alpha$, hash emas.

**Kriteria selesai.** Semua $\Delta^\star$ sudah diperiksa pembaca kedua dan dikunci.

---

## Tahap 8. Ruang uji dan acuan

**Tujuan.** Membangun $S^E$ beserta acuan kebenarannya, dan alat ukur ketajamannya (*skeleton* Bagian VI, Ruang uji dan Rantai kepercayaan). Menjawab feedback no. 3.

**Prasyarat.** Tahap 2 (dimensi), Tahap 4 (format kasus), Tahap 7 (emas).

**Langkah: generator $S^E$**
- [ ] Kombinasi 2-arah berbatasan, dihitung hanya atas kombinasi yang sah, dengan alat seperti PICT atau ACTS. Laporkan cakupan 3-arah.
- [ ] Cakupan batas: setiap batas lapisan Pasal 17 dan TER diuji di $b-1$, $b$, dan $b+1$. Kasus Pasal 17 dibangkitkan terbalik dari PKP ke penghasilan bruto.
- [ ] Sampel operasional: kasus pegawai-tahun acak dari distribusi upah dan status PTKP menurut data BPS. Tetapkan ukurannya dari batas laju kegagalan yang ingin diklaim (2.995 kasus untuk di bawah 0,1%).
- [ ] Bangun $S^E_{\leq n}$ untuk setiap peristiwa, termasuk masa lampau dan tanggal pengetahuan sebelum tanggal terbit, agar A3 dapat diuji.
- [ ] Hitung nilai harapan dari $\mathcal{K}^\star_n$ dan simpan di repo privat.
- [ ] Pastikan $S^E$ dan $S^G$ tidak beririsan, dengan pemeriksaan otomatis.
- [ ] Isi Tabel ruang uji di *skeleton* (jumlah sel, sel teruji, acuan).

**Langkah: acuan**
- [ ] GT1: daftar contoh perhitungan resmi. Pisahkan contoh yang sudah dipakai selama pengembangan dari subset *holdout* yang belum pernah dipakai. Ke-45 contoh di [dataset/07_kasus_uji_resmi/](dataset/07_kasus_uji_resmi/) sudah dipakai selama pengembangan, jadi *holdout* harus dicari dari contoh resmi lain.
- [ ] GT2: kalkulator DJP untuk sampel kasus, bila tersedia untuk rezim yang diuji. Catat tanggal dan hasilnya.
- [ ] GT3: protokol perhitungan manual oleh penghitung independen pada sampel bertingkat per lapisan, termasuk siapa, berapa kasus, dan cara memutuskan selisih.
- [ ] GT4: kalkulator pihak ketiga (*open source* dan publik), dengan versi dan tanggal. [dataset/03_pembanding/](dataset/03_pembanding/) bisa menjadi bahan awal.
- [ ] GT5: acuan untuk angka yang ditentukan kebijakan perusahaan, seperti gaji prorata, THR, dan *take home pay*. Isinya contoh perhitungan dari kolaborator (Tahap 6) ditambah contoh yang tercantum di dokumen kebijakan. Kalkulator xlsx Perusahaan X hanya referensi dan bukan acuan, karena diketahui mengandung kesalahan.
- [ ] Susun matriks acuan terhadap sel ruang uji, yang menunjukkan sel yang punya acuan independen dan sel yang tidak.

**Langkah: alat ukur ketajaman**
- [ ] Tulis operator mutasi: ubah nilai, ubah tanggal, ubah kondisi, ubah lapisan, ubah sifat, dan cabut aturan.
- [ ] Bangun penghitung *mutation score* global dan *mutation score* terfokus-$\Delta$ per peristiwa.
- [ ] Tetapkan ambang minimum *mutation score* (dikunci di Tahap 12).

**Perubahan pada proyek.** Generator di [dataset/06_kasus_uji_sintetis/](dataset/06_kasus_uji_sintetis/) dan data di [dataset/08_pegawai_sintetis/](dataset/08_pegawai_sintetis/) menjadi bahan awal, lalu diperluas dengan kombinatorial berbatasan dan batas terbalik. Operator mutasi lama di [eksperimen/mutasi.py](eksperimen/mutasi.py) disesuaikan dengan graf.

**Keluaran.** Generator $S^E$, nilai harapan, acuan GT1–GT5, matriks acuan, penghitung *mutation score*, Tabel ruang uji terisi.

**Kriteria selesai.** Jumlah titik uji setiap kriteria diketahui, dan setiap sel punya minimal satu acuan.

---

## Tahap 9. Pembangunan alur akuisisi

**Tujuan.** Mewujudkan alur akuisisi Tahap 4 (*skeleton* Bagian V).

**Prasyarat.** Tahap 4, 5, dan 8 (generator $S^G$ memakai pola generator kasus).

**Langkah**
- [ ] Pemotong dokumen per pasal.
- [ ] Penilaian relevansi berkutipan. Dokumen yang dinilai tidak relevan, dengan kutipan yang lolos G2, menghasilkan pembaruan kosong.
- [ ] Penyusun konteks dari graf: bagian *knowledge base* yang relevan dengan dokumen.
- [ ] Pembangkit $m$ kandidat independen dengan keluaran terstruktur sesuai skema $\Delta$. Setiap unsur disertai kutipan sumber.
- [ ] Alat ekstraksi tabel PDF, bila diputuskan di Tahap 0.
- [ ] Gerbang G1–G5 sesuai spesifikasi, termasuk G5 untuk unsur yang dicabut.
- [ ] Generator $S^G$ otomatis.
- [ ] Putaran perbaikan dengan umpan balik gerbang dan batas putaran.
- [ ] Pemilihan konsensus perilaku dan *abstain*.
- [ ] Laporan dampak lintas lapis untuk peninjau.
- [ ] Klien untuk model utama dan model kedua, dengan parameter pembangkitan yang dicatat.
- [ ] Pencatat eksperimen: semua *prompt*, keluaran, token, biaya, waktu, dan hasil setiap gerbang.
- [ ] Penjalan mode terisolasi (pembaruan diterapkan pada $\mathcal{K}^\star_{n-1}$) dan mode berantai (pembaruan diterapkan pada $\mathcal{K}^\mathrm{sis}_{n-1}$).
- [ ] Dua varian *abstain* untuk mode berantai: *knowledge base* lama dipertahankan, atau peninjau sempurna menyisipkan $\Delta^\star_n$.
- [ ] Penjalan dekomposisi kesalahan mekanis, yaitu $\hat{\Delta}_n$ dari mode terisolasi diterapkan pada $\mathcal{K}^\mathrm{sis}_{n-1}$.
- [ ] Pemeriksaan bahwa kode alur tidak membaca $S^E$ maupun nilai harapannya.

**Perubahan pada proyek.** [asisten_kb/](asisten_kb/) menjadi dasar. Keluarannya diubah dari berkas YAML menjadi $\Delta$ pada graf, lalu ditambah penilaian relevansi, $m$ kandidat, G5, generator $S^G$, konsensus, *abstain*, dan pencatat. Uji di [tests/test_asisten_kb.py](tests/test_asisten_kb.py) diperbarui dengan klien LLM tiruan.

**Keluaran.** Alur akuisisi lengkap dengan uji otomatis.

**Kriteria selesai.** Alur berjalan dari dokumen sampai $\mathcal{K}'$ pada satu dokumen pengembangan dengan LLM sungguhan, dan semua uji dengan klien tiruan lulus.

---

## Tahap 10. Pembanding, ablasi, dan skrip analisis

**Tujuan.** Menyiapkan semua kondisi pembanding dan skrip yang menghitung metrik (*skeleton* Bagian VI, Pembanding dan ablasi, Metrik, Analisis statistik).

**Prasyarat.** Tahap 9.

**Langkah: pembanding**
- [ ] B1: pilih kalkulator PPh 21 *open source* yang punya riwayat *commit* di sekitar pergantian ke TER. Ukur waktu sampai diperbarui sejak regulasi terbit, jumlah baris dan berkas yang berubah, dan *bug* regresi.
- [ ] B2 (bila diputuskan): harness yang meminta LLM menghitung PPh 21 langsung dari dokumen untuk ±100 kasus operasional.
- [ ] B3: satu kandidat dengan gerbang G1–G2 saja.
- [ ] B4: $m(1+\bar{r})$ kandidat, setara jumlah panggilan usulan, dipilih dengan suara terbanyak tanpa gerbang.
- [ ] B5: tiga pembanding analisis dampak, yaitu tandai semua kebijakan yang menyentuh fakta yang berubah, penelusuran dependensi tanpa eksekusi, dan penilaian LLM.

**Langkah: ablasi**
- [ ] AB1: formalisasi dari nol pada 2–3 keadaan hukum terpilih (sebelum TER, sesudah TER, masa DTP), dengan penilaian A2 dan hilangnya riwayat.
- [ ] AB2: tanpa konteks *knowledge base*.
- [ ] AB3: tanpa G5, tanpa G4, dan tanpa putaran perbaikan.
- [ ] AB4: pemilihan pertama lolos, konsensus, dan pilihan sempurna.
- [ ] AB5: validasi skema biasa dibanding *shape constraint*, dan pemindaian dependensi datar dibanding *query* graf.

**Langkah: skrip penilaian dan analisis**
- [ ] Penilai hasil per dokumen: benar-diterapkan, salah-diterapkan, atau *abstain*, dengan A2, A3$_t$, dan A4 pada $S^E$.
- [ ] Metrik utama: RA, SER, CAR, ABS, OAR (tanpa tupel $H_n$), kesalahan terpicu, *recall*, dan F2.
- [ ] Metrik diagnostik sesuai Tabel metrik diagnostik di *skeleton*, termasuk:
  - [ ] *pass@k* pada kandidat sebelum perbaikan dan efisiensi pemilihan $\eta$;
  - [ ] matriks konfusi dan MCC per gerbang;
  - [ ] kesepakatan perilaku dan kebenaran per unsur lewat uji tukar unsur;
  - [ ] laju hafalan dan kesetiaan kontrafaktual;
  - [ ] penilaian relevansi (*false positive* dan pembaruan terlewat);
  - [ ] upaya koreksi dengan penyelarasan unsur (Hungarian);
  - [ ] rasio perambatan, persistensi, pemulihan, penguncian kesalahan;
  - [ ] *drift* akhir dalam rupiah;
  - [ ] anomali *knowledge base* per versi;
  - [ ] metrik penerapan langsung.
- [ ] Skrip statistik sesuai Tabel rencana analisis: Clopper–Pearson, selisih risiko berpasangan Newcombe, McNemar eksak, non-inferioritas, Wilcoxon, *bootstrap* klaster, Cohen's $\kappa$, Krippendorff's $\alpha$, dan koreksi Holm.
- [ ] Uji semua skrip pada data tiruan dengan jawaban yang diketahui.
- [ ] Skrip yang membuat semua tabel dan gambar hasil dari log eksperimen, tanpa memanggil LLM lagi.

**Perubahan pada proyek.** Skrip evaluasi lama di [eksperimen/](eksperimen/) diganti atau disesuaikan. [baselines/b1_hardcoded](baselines/) dan [baselines/b2_payroll_hardcoded](baselines/b2_payroll_hardcoded/) ditulis tim sendiri, jadi bukan acuan pihak ketiga. Keduanya boleh dipakai sebagai pemeriksaan selisih tambahan.

**Keluaran.** Semua pembanding dan ablasi siap dijalankan, skrip metrik dan statistik teruji.

**Kriteria selesai.** Setiap metrik utama dan diagnostik dapat dihitung dari log tiruan, dan hasilnya cocok dengan jawaban yang diketahui.

---

## Tahap 11. Kalibrasi pada data pengembangan

**Tujuan.** Menyetel alur hanya dengan data pengembangan, lalu membekukannya (*skeleton* Bagian VI, Pembagian data).

**Prasyarat.** Tahap 9 dan 10.

**Langkah**
- [ ] Jalankan alur pada korpus pengembangan. Setel *prompt*, gerbang, dan aturan pemilihan.
- [ ] Pastikan G5 menerima $\Delta^\star$ semua peristiwa pengembangan (laju penolakan keliru nol).
- [ ] Kumpulkan kesalahan nyata LLM. Masukkan ke taksonomi kesalahan, dan tambahkan sebagai mutan realistis untuk *mutation score*.
- [ ] Perkirakan *pass@1*, rata-rata putaran perbaikan $\bar{r}$, dan token per panggilan.
- [ ] Hitung perkiraan biaya total per eksperimen dalam rupiah, sesuai rumus di *skeleton* Bagian VI (Biaya dan kelayakan).
- [ ] Bila biaya melebihi anggaran, kurangi sesuai urutan penghematan di *skeleton*: ablasi pada satu model, model kedua hanya pada usulan dan B3, *prompt caching*.
- [ ] Bekukan *prompt*, gerbang, aturan pemilihan, dan parameter dengan *tag* git.

**Keluaran.** Alur yang dibekukan, perkiraan biaya, mutan realistis, perkiraan *pass@1* untuk analisis daya.

**Kriteria selesai.** *Tag* pembekuan alur dibuat, dan tidak ada peristiwa uji yang pernah dijalankan.

---

## Tahap 12. Pra-registrasi

**Tujuan.** Mengunci rancangan evaluasi sebelum data uji disentuh (*skeleton* Bagian VI, Desain penelitian).

**Prasyarat.** Tahap 11.

**Langkah**
- [ ] Hitung jumlah dokumen dan peristiwa uji final.
- [ ] Untuk setiap hipotesis, hitung batas terbaik yang dapat dicapai jumlah data itu, lalu tetapkan ambang $\theta_1$–$\theta_4$ pada atau di atas batas tersebut. Bila tidak ada ambang yang bermakna, ganti hipotesis dengan estimasi dan selang kepercayaan saja.
- [ ] Tetapkan margin non-inferioritas $\delta_S$, nilai $m$, $R$, dan parameter pembangkitan.
- [ ] Hitung efek minimum yang dapat dideteksi dengan simulasi, memakai perkiraan *pass@1* dari Tahap 11.
- [ ] Tetapkan keluarga Holm per RQ, daftar analisis konfirmatori, dan daftar analisis eksploratori.
- [ ] Tetapkan ambang *mutation score* dan syarat lulus E0.
- [ ] Tuliskan protokol koreksi emas.
- [ ] Tuliskan daftar kolaborator, jam kerja, dan rencana cadangan.
- [ ] Cantumkan perkiraan biaya dalam rupiah.
- [ ] Daftarkan semuanya ke OSF atau AsPredicted. Tautkan *tag* git pra-registrasi.
- [ ] Mulai catat tanggal pra-registrasi sebagai batas peristiwa prospektif.

**Keluaran.** Dokumen pra-registrasi, tautan OSF, *tag* git.

**Kriteria selesai.** Pendaftaran diterima layanan pihak ketiga dengan stempel waktu.

**Titik periksa dosen (disarankan).** Tunjukkan pra-registrasi ke dosen sebelum eksperimen.

---

## Tahap 13. E0, validasi instrumen

**Tujuan.** Membuktikan bahwa $\mathcal{K}^\star$ dan $S^E$ layak dipakai sebagai alat ukur (*skeleton* Bagian VI, Rantai kepercayaan).

**Prasyarat.** Tahap 12.

**Langkah**
- [ ] Bandingkan hasil $\mathcal{K}^\star$ dengan GT1 (termasuk *holdout*), GT2, GT3, dan GT4 pada semua sel ruang uji, dan dengan GT5 untuk angka lapisan perusahaan.
- [ ] Adjudikasi setiap selisih: *knowledge base* salah, acuan salah, atau hukum ambigu. Catat dasar pasalnya. Contoh resmi yang keliru dicatat sebagai erratum.
- [ ] Pengadjudikasi kedua memeriksa ulang sampel acak secara buta.
- [ ] Jalankan uji unit *engine*.
- [ ] Hitung *mutation score* global dan terfokus-$\Delta$.
- [ ] Laporkan batas atas laju kegagalan pada sampel operasional.
- [ ] Laporkan Krippendorff's $\alpha$ untuk $\Delta^\star$.
- [ ] Periksa syarat lulus E0: tidak ada selisih "*knowledge base* salah" yang belum diselesaikan, dan *mutation score* mencapai ambang.
- [ ] Bila tidak lulus, perbaiki emas atau $S^E$, lalu ulangi Tahap 13.

**Keluaran.** Laporan validasi instrumen untuk subbagian Validasi instrumen di Bagian VII.

**Kriteria selesai.** Syarat lulus E0 terpenuhi.

---

## Tahap 14. E1, adaptivitas representasi (RQ1)

**Tujuan.** Mengukur RA pada perubahan nyata dan perubahan tak terlihat.

**Prasyarat.** Tahap 13.

**Langkah**
- [ ] Laporkan RA perubahan nyata dan RA korpus kebijakan dari Tahap 7, secara terpisah. Untuk kebijakan, keberhasilan berarti $\Delta^\star$ mereproduksi contoh GT5.
- [ ] Laporkan riwayat pengembangan *engine* dan jumlah perubahan *engine* yang dipicu regulasi.
- [ ] Buka perubahan tak terlihat dari repo privat, dan cocokkan hash-nya dengan yang di-*commit*.
- [ ] Untuk setiap perubahan tak terlihat, susun $\Delta$ dalam batas waktu yang ditetapkan, tanpa mengubah *engine*.
- [ ] Hitung keberhasilan: sebuah perubahan berhasil bila seluruh contoh perhitungan dari penulisnya tereproduksi.
- [ ] Hitung RA perubahan tak terlihat dengan selang kepercayaan Clopper–Pearson, lalu putuskan H1.
- [ ] Jalankan *test suite* resolusi konflik dan pemeriksa kelengkapan jejak.

**Keluaran.** Hasil RQ1.

**Kriteria selesai.** Putusan H1 dan semua angka RQ1 tercatat.

---

## Tahap 15. E2, akuisisi terisolasi (RQ2)

**Tujuan.** Mengukur kualitas satu langkah akuisisi (*skeleton* Bagian VI, Mode evaluasi).

**Prasyarat.** Tahap 13.

**Langkah**
- [ ] Jalankan setiap dokumen uji, baik regulasi maupun kebijakan, pada kondisi usulan, B3, B4, dan AB2–AB5 dengan model utama.
- [ ] Jalankan usulan dan B3 dengan model kedua.
- [ ] Jalankan AB1 pada keadaan hukum terpilih.
- [ ] Jalankan satu jalan terisolasi tambahan untuk batas derau.
- [ ] Jalankan dokumen kontrafaktual dan dokumen pengecoh.
- [ ] Periksa invarian A1 dan A3$_\omega$ pada setiap pembaruan yang diterapkan. Pelanggarannya harus nol.
- [ ] Nilai setiap dokumen sumber nyata dengan satu hasil per dokumen dari jalan pertama.
- [ ] Bila keluaran LLM menyingkap kesalahan emas, terapkan protokol koreksi emas dan nilai ulang semua kondisi.
- [ ] Hitung SER, CAR, dan ABS dengan selang kepercayaan eksak, per lapisan (regulasi dan perusahaan). Uji H2a dan H2b, termasuk non-inferioritas SER. Kebijakan buatan dilaporkan sebagai strata terpisah.
- [ ] Hitung semua metrik diagnostik RQ2, termasuk kontaminasi dengan membandingkan peristiwa sebelum dan sesudah *training cutoff* model.
- [ ] Beri label ketepatan kutipan pada sampel unsur.

**Keluaran.** Hasil RQ2.

**Kriteria selesai.** Putusan H2a dan H2b serta semua metrik diagnostik tercatat.

---

## Tahap 16. E3, *regulation replay* (RQ3)

**Tujuan.** Membuktikan bahwa perubahan regulasi dapat langsung diterapkan, dan mengukur perambatan kesalahan. Menjawab feedback no. 5.

**Prasyarat.** Tahap 15 (dekomposisi memakai hasil terisolasi).

**Langkah**
- [ ] Jalankan mode berantai dari keadaan awal sampai peristiwa terakhir, untuk dua varian *abstain*, sebanyak $R$ pengulangan.
- [ ] Sesudah setiap peristiwa, periksa A2, A3$_t$, dan A4 pada $S^E_{\leq n}$ di luar tupel $H_n$. Periksa juga invarian A1 dan A3$_\omega$.
- [ ] Hitung OAR dan uji H3a.
- [ ] Hitung dekomposisi kesalahan: bawaan, baru, terpicu mekanis, dan terpicu kontekstual. Bandingkan dengan batas derau, lalu uji H3b.
- [ ] Hitung rasio perambatan, persistensi, pemulihan, dan penguncian kesalahan.
- [ ] Hitung *drift* akhir $D_N$ dalam proporsi pegawai-bulan dan rupiah.
- [ ] Hitung anomali *knowledge base* setiap versi.
- [ ] Hitung metrik penerapan langsung: peristiwa tanpa suntingan manusia, peristiwa dengan paling banyak $k$ suntingan, dan waktu dari dokumen tersedia sampai *knowledge base* benar.
- [ ] Bandingkan dengan B1 dan AB1.

**Keluaran.** Hasil RQ3 dan data untuk gambar *regulation replay*.

**Kriteria selesai.** Putusan H3a dan H3b serta semua metrik RQ3 tercatat.

---

## Tahap 17. E4, analisis dampak lintas lapis (RQ4)

**Tujuan.** Mengukur kemampuan sistem menemukan kebijakan perusahaan yang terdampak.

**Prasyarat.** Tahap 15 (masukan $\hat{\Delta}$).

**Langkah**
- [ ] Turunkan label dampak jenis (a) dan (b) dari eksekusi $\mathcal{K}^\star$ pada $S^E$.
- [ ] Buka konflik buatan dari repo privat dan cocokkan hash-nya.
- [ ] Beri label dampak jenis (c) pada kebijakan nyata oleh dua pelabel, lalu hitung Cohen's $\kappa$.
- [ ] Jalankan detektor dengan masukan $\Delta^\star$ dan dengan masukan $\hat{\Delta}$.
- [ ] Jalankan pembanding B5.
- [ ] Hitung *recall*, F2, *precision*, MCC, dan AUPRC untuk pembanding yang menghasilkan skor. Pakai *bootstrap* klaster per peristiwa.
- [ ] Uji H4a dan H4b.

**Keluaran.** Hasil RQ4.

**Kriteria selesai.** Putusan H4a dan H4b tercatat.

---

## Tahap 18. E5, pembanding motivasi

**Tujuan.** Menunjukkan mengapa LLM tidak dipakai untuk menghitung pajak.

**Prasyarat.** Keputusan B2 di Tahap 0. Lewati tahap ini bila B2 tidak disertakan.

**Langkah**
- [ ] Jalankan B2 pada ±100 kasus operasional dengan satu model.
- [ ] Hitung proporsi kasus yang tepat sampai rupiah dan sebaran selisihnya.

**Keluaran.** Hasil B2 untuk Pendahuluan atau Pembahasan.

**Kriteria selesai.** Hasil B2 tercatat.

---

## Tahap 19. Peristiwa prospektif

**Tujuan.** Menguji sistem pada regulasi yang belum pernah dilihat perancang maupun LLM.

**Prasyarat.** Tahap 12. Tahap ini berjalan terus sejak pra-registrasi sampai naskah dikirim.

**Langkah**
- [ ] Pantau regulasi PPh 21 yang terbit sesudah tanggal pra-registrasi.
- [ ] Untuk setiap regulasi baru yang relevan, susun $\Delta^\star$ dan kunci dengan hash sebelum menjalankan alur.
- [ ] Jalankan E2 dan E3 untuk peristiwa itu.
- [ ] Laporkan terpisah dari peristiwa uji, karena peristiwa ini tidak didaftarkan sejak awal.

**Keluaran.** Hasil peristiwa prospektif, bila ada.

**Kriteria selesai.** Semua peristiwa prospektif yang terbit sebelum naskah dikirim sudah diuji, atau tidak ada yang terbit. Keadaan ini dicatat di paper.

---

## Tahap 20. Analisis dan penyajian hasil

**Tujuan.** Mengubah semua keluaran eksperimen menjadi tabel, gambar, dan putusan hipotesis (*skeleton* Bagian VII dan VIII).

**Prasyarat.** Tahap 13–18.

**Langkah**
- [ ] Jalankan skrip statistik sesuai rencana yang didaftarkan. Analisis di luar rencana diberi label eksploratori.
- [ ] Tuliskan putusan setiap hipotesis: diterima atau terbantah.
- [ ] Laporkan hasil per jenis perubahan. Jenis mudah dan jenis struktural tidak digabung.
- [ ] Buat gambar yang direncanakan *skeleton*: ikhtisar sistem, ontologi, alur akuisisi, rantai kepercayaan, bidang risiko–cakupan RQ2, dan *regulation replay* RQ3.
- [ ] Isi semua tabel: keterlacakan, ruang uji, korpus, metrik utama, dan metrik diagnostik.
- [ ] Beri label setiap kesalahan LLM dengan taksonomi Tahap 2. Hitung frekuensi per jenis dan gerbang yang menangkapnya.
- [ ] Tuliskan ancaman validitas dan keterbatasan berdasarkan apa yang benar-benar terjadi, termasuk peran yang tidak terisi.

**Keluaran.** Semua tabel dan gambar final, putusan hipotesis, analisis kesalahan.

**Kriteria selesai.** Setiap kontribusi K1–K4 punya bukti di hasil, atau dihapus dari daftar kontribusi.

---

## Tahap 21. Penulisan naskah

**Tujuan.** Mengubah *skeleton* menjadi naskah lengkap.

**Prasyarat.** Tahap 20.

**Langkah**
- [ ] Salin *skeleton* menjadi berkas naskah, misalnya `paper/draft/main.tex`. *Skeleton* tetap disimpan sebagai acuan.
- [ ] Tulis dengan urutan berikut, karena bagian awal bergantung pada bagian akhir:
  - [ ] Bagian II, IV, V, dan VI (definisi dan metode);
  - [ ] Bagian VII (hasil);
  - [ ] Bagian VIII (pembahasan);
  - [ ] Bagian III (penelitian terkait), disesuaikan dengan hasil;
  - [ ] Bagian I (pendahuluan), dengan angka motivasi dari korpus dan B1;
  - [ ] Bagian IX (kesimpulan);
  - [ ] abstrak, 150–250 kata, satu paragraf, berisi angka metrik utama.
- [ ] Ganti setiap isian abu-abu dengan teks, dan setiap rujukan merah dengan sitasi.
- [ ] Hapus semua kotak arahan (`\rancanganfalse`) dan bagian Rencana kerja turunan.
- [ ] Periksa konsistensi: angka di abstrak, pendahuluan, hasil, dan kesimpulan sama; notasi sama di seluruh naskah; setiap definisi dirujuk dengan nomor yang benar.
- [ ] Pastikan setiap klaim di pendahuluan punya bukti di hasil.
- [ ] Jalankan *skill* unslop pada seluruh naskah.
- [ ] Periksa istilah: "penelitian", "acuan", dan istilah asing yang miring.
- [ ] Periksa daftar pustaka: DOI benar, tidak ada karya yang ditarik (*retracted*), dan semua sitasi di naskah ada di bibliografi.

**Keluaran.** Draf naskah lengkap.

**Kriteria selesai.** Naskah terkompilasi tanpa galat, tanpa isian kosong, dan tanpa kotak arahan.

---

## Tahap 22. Telaah dan revisi

**Tujuan.** Memperbaiki naskah sebelum dikirim.

**Prasyarat.** Tahap 21.

**Langkah**
- [ ] Telaah mandiri dengan daftar periksa di Lampiran B.
- [ ] Minta telaah dari kolaborator atau rekan yang belum membaca naskah.
- [ ] Serahkan ke dosen pembimbing.
- [ ] Catat setiap feedback dan tanggapannya di berkas revisi baru di [feedback_and_revision/](feedback_and_revision/), dengan format seperti [revision_27_10_26.md](feedback_and_revision/revision_27_10_26.md).
- [ ] Bila revisi mengubah analisis, jalankan ulang skrip dari log eksperimen. Jangan menjalankan ulang LLM kecuali memang perlu, dan bila perlu, catat alasannya.

**Keluaran.** Naskah yang sudah direvisi dan berkas tanggapan feedback.

**Kriteria selesai.** Dosen menyetujui naskah untuk dikirim.

---

## Tahap 23. Rilis artefak

**Tujuan.** Menyediakan artefak terbuka sesuai kontribusi K4.

**Prasyarat.** Tahap 22.

**Langkah**
- [ ] Rapikan repo: hapus berkas sementara, perbarui [README.md](README.md) dengan cara mereproduksi setiap tabel dan gambar.
- [ ] Pindahkan materi tersembunyi dari repo privat ke repo publik, dan pastikan hash-nya cocok.
- [ ] Arsipkan *knowledge base*, korpus beserta $\Delta^\star$, *test suite* dan nilai harapannya, *prompt*, keluaran LLM, dan skrip analisis.
- [ ] Pastikan tidak ada data pribadi yang ikut dirilis, termasuk `payroll_calculator.xlsx` dan `.env`.
- [ ] Periksa lisensi setiap komponen. Dokumen regulasi dan PDF referensi berlisensi beragam dan tidak semuanya boleh disebarkan.
- [ ] Unggah arsip ke Zenodo untuk memperoleh DOI.
- [ ] Tambahkan DOI dan tautan repo ke naskah.

**Keluaran.** Repo publik yang dapat direproduksi, DOI arsip.

**Kriteria selesai.** Orang lain dapat membuat ulang semua tabel dan gambar dari arsip tanpa memanggil LLM.

---

## Tahap 24. Finalisasi dan pengiriman

**Tujuan.** Menyiapkan naskah sesuai syarat tujuan publikasi.

**Prasyarat.** Tahap 23.

**Langkah: semua tujuan**
- [ ] Pernyataan penggunaan AI sesuai catatan di [journal.md](journal.md).
- [ ] Pernyataan ketersediaan data dengan DOI dari Tahap 23.
- [ ] Ucapan terima kasih, termasuk kolaborator dan praktisi pajak bila ada.

**Langkah: bila tujuannya IEEE Access**
- [ ] Terjemahkan naskah ke bahasa Inggris.
- [ ] Pindahkan ke template resmi IEEE Access (`ieeeaccess.cls`) dari situs IEEE Access.
- [ ] Abstrak 150–250 kata dalam satu paragraf, tanpa rumus, tabel, atau rujukan.
- [ ] Kata kunci 3–10, urut abjad.
- [ ] Panjang naskah di bawah 20 halaman. Bila lebih, siapkan justifikasi.
- [ ] Biografi singkat setiap penulis di bawah daftar pustaka.
- [ ] Pengungkapan teks buatan AI di bagian ucapan terima kasih.
- [ ] Siapkan berkas sumber LaTeX dan PDF dengan isi yang sama, masing-masing di bawah 40 MB.
- [ ] Siapkan *cover letter*.
- [ ] Periksa daftar periksa pengiriman IEEE Access.

**Langkah: bila tujuannya tugas mata kuliah atau jurnal nasional**
- [ ] Ikuti format yang diminta dosen atau jurnal tujuan.

**Keluaran.** Paket pengiriman lengkap.

**Kriteria selesai.** Naskah terkirim.

---

## Lampiran A. Peta aset proyek terhadap *skeleton*

| Aset yang ada | Dipakai untuk | Perubahan yang dibutuhkan | Tahap |
|---|---|---|---|
| [engine/](engine/) | *Inference engine* | Membaca aturan dari graf; ukuran *lex specialis* sesuai keputusan; uji unit terpisah | 5 |
| [kb/regulasi/](kb/regulasi/), [kb/perusahaan/](kb/perusahaan/) | Bahan $\mathcal{K}^\star$ | Dimigrasikan ke graf, lalu dipecah menjadi keadaan awal dan $\Delta^\star$ per peristiwa | 5, 7 |
| [asisten_kb/](asisten_kb/) | Dasar alur akuisisi | Keluaran menjadi $\Delta$ pada graf; tambah relevansi, $m$ kandidat, G5, $S^G$, konsensus, *abstain*, pencatat | 9 |
| [kb/skema/](kb/skema/) | Dasar skema | Diganti atau dilengkapi skema $\Delta$ dan *shape* SHACL | 4, 5 |
| [dataset/01_regulasi/](dataset/01_regulasi/) | Dokumen korpus | Dipilih, diberi *checksum*, dipotong per pasal | 6 |
| [dataset/07_kasus_uji_resmi/](dataset/07_kasus_uji_resmi/) | GT1 bagian pengembangan | Sudah dipakai selama pengembangan, jadi tidak dapat menjadi *holdout* | 8 |
| [dataset/06_kasus_uji_sintetis/](dataset/06_kasus_uji_sintetis/) | Dasar generator $S^E$ | Ditambah kombinatorial berbatasan dan batas terbalik | 8 |
| [dataset/08_pegawai_sintetis/](dataset/08_pegawai_sintetis/), [dataset/04_data_publik/](dataset/04_data_publik/) | Sampel operasional | Distribusi upah dan PTKP dari data BPS | 8 |
| [dataset/05_katalog_kebijakan/](dataset/05_katalog_kebijakan/) | Bahan kebijakan buatan | Ditulis sebagai dokumen kebijakan, sebagian untuk pengembangan | 6 |
| `payroll_calculator.xlsx` (Perusahaan X) | Referensi kebijakan | Bukan acuan GT5 karena mengandung kesalahan; tidak di-*commit* karena berisi data pribadi | 6, 8 |
| [dataset/03_pembanding/](dataset/03_pembanding/) | Kandidat GT4 dan B1 | Dipilih yang punya riwayat *commit* di sekitar TER | 8, 10 |
| [baselines/](baselines/) | Pemeriksaan selisih tambahan | Bukan acuan pihak ketiga | 10 |
| [eksperimen/](eksperimen/) | Bahan skrip evaluasi | Diganti dengan skrip metrik baru; operator mutasi disesuaikan | 8, 10 |
| [tests/](tests/) | Uji otomatis | Diperluas untuk graf, gerbang, dan alur | 5, 9 |
| [paper/latex/](paper/latex/) | Bibliografi | Draf lama digantikan *skeleton*; `references.bib` dipakai ulang | 1, 21 |
| [web/](web/), [ui/](ui/), [jembatan/](jembatan/) | Tidak dipakai di paper | Disesuaikan hanya bila demo dibutuhkan | – |
| [research_plan.md](research_plan.md) | Riwayat | Digantikan *skeleton* sebagai rencana | – |
| [journal.md](journal.md) | Catatan penggunaan AI | Terus diperbarui | Semua |

## Lampiran B. Daftar periksa naskah sebelum dikirim

- [ ] Judul, abstrak, pendahuluan, dan kesimpulan memakai angka yang sama.
- [ ] Setiap RQ dijawab di Hasil dan Pembahasan, dengan putusan hipotesis yang eksplisit.
- [ ] Setiap kontribusi punya bukti di Hasil.
- [ ] Setiap metrik utama dilaporkan dengan selang kepercayaan.
- [ ] Hipotesis yang terbantah dilaporkan sebagai terbantah.
- [ ] Analisis di luar pra-registrasi diberi label eksploratori.
- [ ] Hasil dilaporkan per jenis perubahan dan per lapisan (regulasi dan perusahaan).
- [ ] Peristiwa prospektif dilaporkan terpisah.
- [ ] Setiap peran yang tidak terisi dilaporkan sebagai keterbatasan.
- [ ] Ancaman validitas mencakup internal, bias pandangan belakang, konstruk, eksternal, kesimpulan, dan kontaminasi.
- [ ] Tidak ada kata "makalah" atau "oracle".
- [ ] Istilah asing ditulis miring dan tidak diterjemahkan.
- [ ] Semua sitasi ada di bibliografi, dengan DOI yang benar.
- [ ] Semua tabel dan gambar dirujuk di teks.
- [ ] Naskah sudah melewati *skill* unslop.
- [ ] Tautan pra-registrasi dan DOI arsip tercantum.

## Lampiran C. Daftar *tag* git

| *Tag* | Dibuat di | Arti |
|---|---|---|
| `prototipe-akhir` | Tahap 5 | Keadaan proyek sebelum disesuaikan dengan *skeleton* |
| `definisi-v1` | Tahap 4 | Definisi Tahap 2–4 dibekukan |
| `representasi-v1` | Tahap 5 | *Knowledge graph* dan *engine* baru lulus kesetaraan |
| `emas-v1` | Tahap 7 | $\Delta^\star$ uji dikunci |
| `alur-beku` | Tahap 11 | Alur akuisisi dibekukan |
| `prareg` | Tahap 12 | Rancangan evaluasi didaftarkan |
| `e0-lulus` | Tahap 13 | Instrumen tervalidasi |
| `hasil-v1` | Tahap 20 | Semua hasil final |
| `naskah-v1` | Tahap 21 | Draf lengkap pertama |
| `rilis` | Tahap 23 | Artefak dirilis |

## Log keputusan

| Tanggal | Keputusan | Pilihan | Alasan |
|---|---|---|---|
| 2026-10-27 | Judul penelitian | *Knowledge-Based System* Adaptif untuk Perhitungan PPh 21 dengan Akuisisi Pengetahuan Berbantuan LLM dari Regulasi dan Kebijakan Perusahaan | Feedback dosen no. 2 |
| 2026-10-27 | Representasi final | *Legal knowledge graph* (RDF/OWL, SHACL, SPARQL) dengan aturan yang dijalankan *engine* | Feedback dosen no. 1 |
| 2026-10-27 | Cakupan kebijakan perusahaan | Dokumen kebijakan diuji di E1 (RA) dan E2 (SER/CAR per lapisan), dengan acuan GT5. Perubahan kebijakan tidak disisipkan ke rangkaian *regulation replay* | Judul menjanjikan akuisisi dari kebijakan perusahaan. Perubahan kebijakan di *replay* bersifat opsional dan menambah biaya |
| 2026-10-27 | Urutan kerja | Sistem dibangun dan diuji lebih dulu; *skeleton* dan naskah ditulis ulang setelah sistem jadi | Keputusan di bawah mengubah beberapa bagian *skeleton*; perubahannya dikumpulkan dan diterapkan sekaligus |
| 2026-10-27 | Cakupan *engine* | Setahun penuh: masa Januari–Desember, perhitungan ulang Desember, penghasilan tidak teratur, *gross-up*, masuk dan keluar di tengah tahun | Sesuai Tabel dimensi; setara kalkulator lama di `engine/` |
| 2026-10-27 | Makna ω dan $t_c$ | Tanggal terbit dokumen. Tanggal persetujuan peninjau disimpan terpisah sebagai metadata | A3$_\omega$ berlaku karena konstruksi dan *replay* dapat diulang persis |
| 2026-10-27 | Semantik berlaku surut | Mengikuti mekanisme di teks PMK 10/2025, dibaca dan ditetapkan di Tahap 4 | *Ground truth* harus mengikuti hukum, bukan penyederhanaan mini demo |
| 2026-10-27 | Pencabutan dan perubahan aturan | Rekaman aturan berversi; $\Delta$ mendukung *add*, *change*, *remove* | Riwayat bitemporal tetap utuh; sesuai $\Delta = \langle \Delta^+, \Delta^\sim, \Delta^- \rangle$ |
| 2026-10-27 | Seri pada konsensus | *Abstain* | Tanpa mayoritas, sistem tidak yakin; menekan SER |
| 2026-10-27 | *Date grounding* | Perluasan G2: setiap tanggal di $\Delta$ harus muncul di kutipan | Mini demo: tanggal salah K1 lolos semua gerbang |
| 2026-10-27 | $m$ dan perbaikan | $m = 5$, satu putaran perbaikan | Usulan *skeleton* |
| 2026-10-27 | Aturan pembantu yang mati | Pencabutannya opsional di $\Delta^\star$; dihitung di metrik anomali RQ3 | Tidak memengaruhi A2 |
| 2026-10-27 | Model LLM | Utama: Claude Opus 5.5, *effort* high. Kedua: GPT-6.1 Sol (`gpt-6.1-sol`), *effort* high | Pilihan peneliti. Model kedua bukan *open-weight* seperti di *skeleton*, melainkan model penyedia lain |
| 2026-10-27 | Anggaran API | USD 15, hemat maksimal: Batch API, *prompt caching*, kandidat dipakai ulang untuk B3, B4, AB3, AB4; $m = 5$ hanya pada dokumen nyata; E3 dengan $R = 1$; kontrafaktual sedikit; AB1 dan AB2 dipangkas; model kedua hanya pada usulan | Perkiraan rencana penuh dengan Opus *high* sekitar USD 120–150; batasannya dicatat sebagai keterbatasan |
| 2026-10-27 | Pembanding B2 | Disertakan dalam skala kecil (E5) | Reviewer akan menanyakannya; ukurannya menyesuaikan anggaran |
| 2026-10-27 | *Lex specialis* | Relasi eksplisit antaraturan di graf | Tidak bergantung pada cara menulis kondisi; diperiksa G3 |
| 2026-10-27 | Pengambilan teks PDF | pdfplumber, tabel lewat alat ekstraksi, dicek manual sekali per dokumen lalu dikunci | Sudah ada di `env`; kutipan G2 tetap dapat dicocokkan |
| 2026-10-27 | Praktisi | Pegawai *finance* memeriksa $\Delta^\star$ TER dan sekitar 50 kasus | Tersedia; bukan konsultan pajak bersertifikat, sehingga disebut praktisi *payroll* |
| 2026-10-27 | Penyimpanan graf | GraphDB Free (Ontotext) sebagai *triple store*: satu *named graph* per versi KB, validasi SHACL di *repository*, *endpoint* SPARQL untuk *engine* dan aplikasi. Log $\Delta$ tetap disimpan di git sebagai jejak audit dan untuk membangun ulang *repository*. Alternatif *open source*: Apache Jena Fuseki | Sistem graf sungguhan menambah kredibilitas; GraphDB populer di riset *knowledge graph* hukum, punya penjelajah graf visual dan SHACL bawaan. Dipasang di luar `env` |
| 2026-10-27 | Penyusun materi independen | Claude menyusun semua materi lebih dulu: $\Delta^\star$, kasus bertingkat, adjudikasi, label RQ4, kebijakan dan konflik buatan, perubahan tak terlihat. Teman peneliti dan pakar *payroll* (pegawai *finance*) memeriksanya lewat folder [review/](review/) sebelum materi dipakai di eksperimen | Pekerjaan bisa jalan tanpa menunggu kolaborator. Risikonya, penyusun emas dan model yang diuji berasal dari keluarga yang sama; mitigasinya tinjauan manusia wajib dan pemeriksaan terhadap acuan yang tidak disusun Claude (GT1, GT4) |
| 2026-10-27 | Pemeriksaan materi `review/` | Materi diperiksa oleh peninjau independen (agen terpisah dari penyusun) terhadap teks regulasi, lalu dipakai sebagai acuan. Status "siap dipakai". Bila pakar tersedia, materi diuji ulang dan selisihnya dilaporkan | Pengembangan tidak menunggu ketersediaan pakar |
| 2026-10-27 | Perubahan tak terlihat | Disusun *agent* terpisah yang hanya membaca taksonomi perubahan, disegel dengan `system/tools/seal.py` (manifes hash di-*commit*) sebelum representasi dibekukan, dan diperiksa manusia setelah dibuka | Menjaga sebagian independensi dari perancang representasi |
| 2026-10-27 | Materi tersegel | Boleh disimpan di repo publik ini; tidak perlu repo privat. Kepastian tidak diubah diberikan manifes hash dan *tag* git | Keputusan peneliti. Konsekuensinya, materi itu bisa terbaca siapa pun, termasuk ikut data latih model di masa depan; dicatat sebagai keterbatasan kontaminasi |
| 2026-10-27 | Lokasi sistem penuh | Folder baru [system/](system/README.md) berbahasa Inggris. Kode lama (`engine/`, `kb/`, `ui/`, `web/`) tidak diubah dan menjadi acuan pemeriksaan kesetaraan | Kode lama tetap bisa dibandingkan |
| 2026-10-27 | Aplikasi | Streamlit, melanjutkan `mini_demo/app/`. Aplikasi Laravel `web/` tidak dikembangkan untuk penelitian ini | Fokus pada penelitian utama |
| 2026-10-27 | Kunci API dan GraphDB | Kunci dibaca dari `.env` (`CLAUDE_API_KEY`, `OPENAI_API_KEY`) oleh `system/pph21kbs/config.py`, tanpa variabel OS. GraphDB 11.5.1 berjalan lewat Docker (`graphdb/docker-compose.yml`) dengan lisensi Free. *Repository* `pph21`: validasi SHACL aktif, tanpa inferensi (*ruleset* `empty`), *context index* aktif; ontologi dimuat bersama data agar `sh:class` mengikuti subkelas. Disiapkan ulang dengan `system/tools/graphdb_setup.py` | `.env` dan lisensi tidak di-*commit*. Tanpa inferensi, hasil *query* tidak bergantung pada *reasoner* |
| 2026-10-27 | Varian model kedua | `gpt-6.1-sol`, *cutoff* 30 April 2026, USD 2/10 per 1 juta token masukan/keluaran | Satu-satunya model keluarga GPT-6 di akun API; menurut OpenAI kinerjanya mendekati GPT-6 Astra dengan biaya lebih rendah; *cutoff* sama dengan Astra sehingga pembagian peristiwa sebelum/sesudah *cutoff* tidak berubah |
| 2026-10-27 | Koreksi korpus: P07 menjadi E13 | PER-11/PJ/2025 Ps. 129–130 mengubah pembulatan PPh 21 mulai Masa Januari 2025 (dasar tafsir K1), sehingga dokumen itu peristiwa uji (T9, S1), bukan pengecoh. Uji 13, pengecoh 20 | Ditemukan saat menyusun spesifikasi representasi (Tahap 3) |
| 2026-10-27 | Nilai yang dinilai untuk peristiwa berlaku surut | Setiap masa bernilai *nilai seharusnya* untuk ω ≥ $t_\mathit{terbit}$; masa pajak terakhir menjumlahkan nilai seharusnya; mekanisme penyelesaian tunai dicatat di jejak tetapi tidak dinilai (tafsir_korpus B0–B5) | Entri penyelesaian bergantung pada apa yang benar-benar dipotong pada tanggal penggajian, yang bukan masukan kasus; penyimpangan sadar dari bunyi *skeleton* |
| 2026-10-27 | Lapisan perusahaan | Aturan perusahaan milik satu kebijakan dan dipasang hanya untuk kasus yang menyebut kebijakan itu; ω menyaring lapisan regulasi saja | Tinjauan spesifikasi temuan 1; kebijakan diuji terhadap regulasi pada ω mana pun |
| 2026-10-27 | Spesifikasi versi 2 | 41 temuan tinjauan independen ditanggapi; rincian di `review/specs/spesifikasi.tanggapan.md` | Tahap 3–4 |
| 2026-10-27 | Emas dibangun sebagai kode | Semua $\Delta^\star$ (latar, uji, pengembangan, fiktif, kebijakan) ditulis di `system/gold_src/`, kutipannya diverifikasi otomatis terhadap teks terkunci, dan dibangun ke `dataset/12_emas/` oleh `build_gold.py` (rantai utama dan pembaruan sisi) | Kutipan yang tidak ditemukan menghentikan *build*; emas dapat diperiksa ulang dan diubah dengan riwayat git |
| 2026-10-27 | Regulasi fiktif dan kebijakan sebagai pembaruan sisi | FR01–FR05 diterapkan pada prefiks rantai pada tanggal terbitnya; kebijakan dipasang pada rantai regulasi lengkap; keduanya tidak masuk rantai utama | Regulasi fiktif tidak boleh mengubah sejarah nyata; kebijakan diuji terhadap setiap $\mathcal{K}^\star_n$ (RQ4) |
| 2026-10-27 | Gerbang terhadap emas (spesifikasi akuisisi versi 3) | Setiap $\Delta^\star$ pengembangan dan uji harus lolos G1–G5. Penyesuaian yang diperlukan: pendaratan nilai turunan, kata bilangan, desimal pendek, huruf OCR; pola tanggal "(sampai) dengan"; G4 hanya galat baru; untuk kebijakan G4 hanya galat dan evaluasi pada ω = 2026-10-27; G5 membebaskan definisi fakta dan mengamati fakta milik kebijakan; generator $S^G$ diperluas (3-arah bila muat, pasangan semua dimensi, baris terarah masa terakhir, atribut aturan pesaing sampai tiga langkah, isian acak sampai 250) | Syarat pembekuan Tahap 11 (laju penolakan keliru nol) diterapkan sejak awal; penyesuaian dibuat atas emas, bukan atas keluaran LLM |
| 2026-10-27 | Koreksi emas dari pemeriksaan gerbang dan contoh kebijakan | E02 tanpa aturan pencatat natura yang dikecualikan (tidak berefek); E06/E11 `REG.DTP.NO_GROSSUP` hanya untuk metode ditanggung dan `REG.DTP.THP_CASH` baru (tafsir K18); D07/D11 tanpa perpanjangan aturan tahun `REG.COVID_DTP.REFUND` (tidak berefek); kutipan E02–E12 diperpanjang dan memuat tanggal berlakunya | Ditemukan oleh G2/G5 dan oleh contoh SP06 dan GT5-CENTEX; GT1–GT3 tidak berubah |
| 2026-10-27 | Siklus titik tetap (tafsir K3 butir 4) | Bila iterasi *gross-up* masuk siklus, dipakai nilai terkecil dalam siklus yang menutup pajaknya sendiri; peringatan `FixedPointCycle` | Pembulatan dalam metode selisih membuat fungsi tidak monoton; ditemukan oleh $S^G$ |
| 2026-10-27 | Perbaikan *engine* sebelum pembekuan | Konflik *override* dibandingkan dengan pemenang wajib yang sebenarnya (bukan bila ada dua aturan wajib aktif); rekaman pembaruan kebijakan (termasuk fakta milik kebijakan) tidak disaring ω; pemeriksa statis membedakan aturan perusahaan yang selalu kalah (konflik aktif) dari aturan mati dan membaca fakta yang dibaca batasan | Temuan dari penyusunan emas kebijakan; *tag* `engine-v1` belum dibuat |
| 2026-10-28 | Batch API hanya untuk satu putaran (pengecoh) | Dokumen nyata dijalankan sinkron dengan *prompt caching*; pengecoh (putaran relevansi saja) lewat Message Batches | Terukur: draf kedua dan seterusnya dengan *cache* USD 0,074, setara draf *batch* tanpa *cache* (~USD 0,08); *batch* pertama tidak diproses sama sekali dalam 33 menit sehingga tiga putaran berurutan tidak muat dalam waktu kerja |
| 2026-10-28 | Relevansi tanpa *cache* | Panggilan relevansi tidak memasang `cache_control` | Awalan relevansi tidak pernah dibaca ulang (draf memakai *system prompt* lain); penulisan *cache* 1,25 × harga masukan |
| 2026-10-28 | Kasus terarah dari analisis mutan | Mutan yang lolos $S^E$ diuji pada $S^G$ emas dan mutan; yang terbedakan menambah satu kasus terarah ke $S^E$, sisanya "kemungkinan setara" | Prareg butir 5; kasus hanya dari emas, ditambahkan sebelum peristiwa uji dijalankan |
| 2026-10-28 | Pengecoh dijalankan sinkron, $m = 1$ | *Batch* pengecoh (20 permintaan) dibatalkan sesudah 50 menit tanpa satu permintaan pun diproses; pengecoh dijalankan sinkron tanpa *cache* dengan $m = 1$ bila dinilai relevan | Ketiga *batch* di akun ini tidak diproses dalam 20–50 menit; sisa anggaran USD 2,45 tidak cukup untuk $m = 3$ pada positif palsu |
| 2026-10-28 | Detektor dampak dievaluasi di GraphDB | Query `impact_*.rq` yang sama dijalankan di GraphDB untuk evaluasi RQ4 | rdflib butuh ~10 menit per pasangan (jalur properti tanpa ikatan); kesetaraan hasil diuji pada skenario uji detektor |
| 2026-10-28 | Anggaran tambahan | Paling banyak USD 100 lagi per penyedia (Claude API, OpenAI), dijaga per penyedia di `config.BUDGET_USD`; API hanya untuk eksperimen rancangan | Keputusan peneliti; amandemen pra-registrasi §10 (*tag* `prareg-amandemen-1`) |
| 2026-10-28 | E1 oleh agen independen | Perubahan tersegel dibuka dan dikerjakan agen terpisah yang tidak ikut merancang representasi; perancang hanya menerima hasil | Menjaga independensi uji RQ1 sesudah pembekuan |
| 2026-10-28 | Sensitivitas $m = 5$ | Kandidat tambahan dengan *prompt* dan awalan sama, konsensus dihitung ulang (`extend_candidates.py`); analisis utama tetap $m = 3$/2 | Tidak membuang kandidat yang sudah dibayar; hasil utama tidak dipilih sesudah melihat hasil |
| 2026-10-28 | AB1 dengan kosakata fakta | Basis AB1 berisi definisi fakta saja | Tanpa nama fakta bersama, keluaran tidak bisa dinilai pada $S^E$ |
| 2026-10-28 | `Config.max_tokens` | Parameter baru, bawaan 32.000 (perilaku alur beku tidak berubah); AB1 memakai 64.000 | Keluaran AB1 adalah KB utuh |
| 2026-10-28 | AB1: *prompt* formalisasi dan G1–G4 | Pesan penyusunan AB1 meminta KB utuh dari dokumen yang berlaku; G5 tidak dipakai | Dengan pesan penyusunan alur, model hanya menulis pembaruan dokumen terbaru (1 unsur; jalan pertama disimpan di `results_prompt_v1`); G5 dirancang untuk Δ inkremental |
| 2026-10-28 | Detektor dampak v2 (eksploratori) | `impact_policy_v2.rq` menambah jenis (d): aturan kebijakan menghasilkan fakta di $F_\Delta$; dilaporkan berdampingan dengan detektor beku | Menutup celah yang ditemukan pada RQ4; tidak menggantikan hasil H4 |
