# Naskah presentasi progres mingguan, versi 2 (27 Oktober 2026)

Versi ini untuk slide v6 dan paper v8, yang sudah memuat temuan mini demo. Versi pertama, untuk slide v5, ada di [NASKAH_PRESENTASI.md](NASKAH_PRESENTASI.md).

Naskah ini berisi apa yang diucapkan saat presentasi, slide demi slide, beserta cara menjelaskan draf paper bila dosen membukanya. Kalimat dalam kutipan adalah contoh ucapan; sesuaikan dengan gaya bicara sendiri, asalkan isinya tetap.

**Yang dibuka saat presentasi:**

- Slide: `progress_mingguan_draf_v6.pptx` (14 slide).
- Paper: `paper/draft/naskah_draf_v8/main.pdf` (8 halaman), disiapkan di tab lain. Naskah khusus paper ada di [NASKAH_PRESENTASI_PAPER_v2.md](NASKAH_PRESENTASI_PAPER_v2.md).
- Mini demo (opsional): `env\Scripts\streamlit run mini_demo\app\main.py`, lalu buka http://localhost:8501.

**Durasi:** sekitar 20 menit presentasi, lalu tanya jawab.

**Tiga pesan yang harus sampai ke dosen:**

1. Kelima feedback sudah dijawab, masing-masing dengan satu perubahan konsep.
2. Kebaruan penelitian bukan "LLM membuat aturan", tetapi LLM *memperbarui* knowledge base yang sudah berjalan mengikuti perubahan regulasi nyata, dengan hasil periode lama terjaga dan kesalahan yang merambat diukur.
3. Sistem penuh masih rancangan. Sudah ada prototipe mini dengan LLM tiruan, draf paper Bagian I–VI sudah ditulis, dan hasil menunggu eksperimen.

---

## Bagian A. Naskah per slide

### Slide 1 — Judul (±30 detik)

> "Selamat pagi/siang, Bapak/Ibu. Kami Obi Kastanya dan Mahathir Muhammad. Hari ini kami melaporkan dua hal: perubahan konsep penelitian setelah feedback Bapak/Ibu, dan progres draf paper.
>
> Judul penelitian kami sekarang *Knowledge-Based System Adaptif untuk Perhitungan PPh 21 dengan Akuisisi Pengetahuan Berbantuan LLM dari Regulasi dan Kebijakan Perusahaan*. Gambar di kanan merangkum idenya. LLM hanya mengusulkan pembaruan. Pengetahuan disimpan dalam dua lapis, yaitu regulasi dan kebijakan perusahaan. Yang menghitung pajak tetap inference engine."

*Transisi:* "Saya mulai dari ringkasan feedback dan perubahannya."

### Slide 2 — Lima feedback, lima perubahan (±1,5 menit)

> "Ada lima feedback dari Bapak/Ibu, dan masing-masing kami jawab dengan satu perubahan.
>
> Pertama, soal representasi final yang dinilai terlalu sederhana. YAML kami ganti dengan legal knowledge graph, dan perhitungannya tetap di engine deterministik.
>
> Kedua, soal kontribusi. Usulan adaptive tax calculation kami adopsi. Novelty-nya kami letakkan pada LLM yang memperbarui knowledge base yang sudah berjalan mengikuti perubahan regulasi nyata.
>
> Ketiga, ground truth. Ruang uji mencakup semua lapisan tarif dan kombinasi dimensinya.
>
> Keempat, metrik. Satu metrik utama untuk setiap pertanyaan penelitian.
>
> Kelima, bukti bahwa perubahan regulasi bisa langsung diterapkan. Kami rancang eksperimen regulation replay.
>
> Perlu kami sampaikan dari awal, semua ini masih rancangan. Buktinya menunggu eksperimen."

*Transisi:* "Perubahan pertama yang paling terlihat ada di judul."

### Slide 3 — Pergantian judul (±1 menit)

> "Judul lama menonjolkan bentuk knowledge base-nya, yaitu dua lapis dan berversi waktu, ditambah aplikasi web dan metodologi validasi. Sesuai feedback kedua, knowledge base saja tidak cukup, jadi judul baru menonjolkan kemampuan sistem mengikuti perubahan regulasi.
>
> Ada empat unsur di judul baru:
>
> - Knowledge-Based System, karena wujudnya KB ditambah inference engine, bukan rumus spreadsheet.
> - Adaptif, karena perubahan regulasi diterapkan lewat pembaruan KB tanpa mengubah kode engine.
> - Akuisisi berbantuan LLM, karena LLM mengubah teks peraturan menjadi rancangan aturan.
> - Regulasi dan kebijakan perusahaan, karena ada dua lapis pengetahuan dan deteksi konflik di antara keduanya.
>
> Unsur judul lama tidak hilang. Dua lapis dan versi waktu pindah ke bagian representasi, aplikasi web ke implementasi dan tidak lagi kami klaim sebagai kontribusi, dan validasi tanpa domain expert ke bagian evaluasi."

### Slide 4 — Feedback 1: representasi final (±2 menit)

> "Untuk feedback pertama, representasi final kami adalah legal knowledge graph berbasis RDF/OWL.
>
> Pengetahuan PPh 21 kami bagi dua. Yang struktural, misalnya regulasi memuat pasal, aturan bersumber dari pasal, PMK baru mengubah PMK lama, atau kebijakan berkonflik dengan aturan wajib, disimpan di graf. Yang komputasional, misalnya TER dikali bruto, pembulatan, dan gross-up, tetap dijalankan inference engine.
>
> Alasannya, OWL dan SWRL tidak punya aritmetika eksak dengan pembulatan per pasal. Engine prototipe kami sudah tidak punya selisih yang tidak terjelaskan pada 1.213 nilai dari 45 contoh perhitungan resmi, dan ketepatan itu ingin kami pertahankan.
>
> Representasinya terdiri atas tiga komponen. Ontologi memakai standar ELI, OWL-Time, dan PROV-O. SHACL menjadi gerbang validasi. SPARQL dipakai untuk analisis dampak.
>
> Contoh di kanan: Perusahaan X menggolongkan lembur sebagai penghasilan tidak teratur, padahal regulasi menggolongkannya teratur. Di graf, konflik ini menjadi relasi eksplisit antara aturan perusahaan dan aturan wajib beserta pasal sumbernya. Engine memakai aturan wajib, yaitu lex superior, dan konfliknya tercatat di jejak."

### Slide 5 — Feedback 2: novelty (±2 menit)

> "Untuk feedback kedua, soal kontribusi. Usulan adaptive tax calculation kami terima. Setelah kami telusuri pustaka 2025–2026, pola 'LLM menyusun aturan lalu engine menghitung' ternyata sudah dikerjakan, misalnya NTOL untuk pajak India, formalisasi Internal Revenue Code Amerika, dan penerjemahan hukum pajak ke Catala. Gagasan LLM memperbarui kode pajak juga sudah diajukan Gogani-Khiabani dan kawan-kawan, tetapi baru berupa kajian tantangan, tanpa pengujian berantai.
>
> Karena itu novelty kami letakkan di kotak biru tua. LLM memperbarui knowledge base yang sudah berjalan, mengikuti rangkaian amandemen nyata, dijaga gerbang verifikasi, dan hasil periode lama tidak rusak.
>
> Ada dua penguat. Pertama, dampak lintas lapis: kebijakan perusahaan yang menjadi melanggar setelah regulasi berubah terdeteksi otomatis. Kedua, pengujian pada perubahan struktural nyata, yaitu pergantian metode disetahunkan PER-16 ke TER, bukan sekadar perubahan parameter.
>
> Satu catatan jujur: karya pembanding ini baru kami baca dari abstraknya. Naskah lengkapnya akan kami baca untuk memastikan klaim ini."

### Slide 6 — Arsitektur (±1,5 menit)

> "Ini alur sistemnya. Dokumen regulasi atau kebijakan baru masuk, lalu LLM menilai apakah dokumen itu mengubah perhitungan PPh 21, dengan menyertakan kutipan pasal. Kalau tidak relevan, tidak ada yang diubah.
>
> Kalau relevan, LLM menyusun beberapa kandidat pembaruan, dan setiap kandidat diuji lima gerbang:
>
> - G1 memeriksa struktur graf dengan SHACL.
> - G2 memeriksa bahwa kutipan, termasuk setiap tanggal di dalamnya, benar-benar ada di dokumen.
> - G3 memeriksa konsistensi dan konflik.
> - G4 memeriksa bahwa hasil masa lama tidak berubah.
> - G5 memeriksa bahwa pembaruan benar-benar berefek, atau menimbulkan konflik yang dilaporkan. Tanpa G5, pembaruan kosong lolos semua gerbang karena tidak menimbulkan regresi.
>
> Kandidat yang lolos dipilih lewat konsensus perilaku. Kandidat dikelompokkan menurut hasil hitungnya, bukan menurut bentuk aturannya. Kalau tidak ada yang lolos, atau dua kelompok terbesar sama besar, sistem menolak memilih dan meneruskan dokumen ke peninjau manusia. Jadi LLM tidak pernah menghitung pajak."

### Slide 7 — Feedback 3: ruang uji (±1,5 menit)

> "Untuk feedback ketiga, Bapak/Ibu menyebut lapisan 5, 15, 25, 35 persen. Setelah UU HPP lapisannya ada lima. Lapisan 30 persen, untuk PKP 500 juta sampai 5 miliar, juga kami uji.
>
> Dimensi yang diuji ada di kiri: rezim, lapisan Pasal 17, kategori TER, status PTKP, metode, pola kerja, dan jenis penghasilan.
>
> Jumlahnya di kanan. Setiap batas lapisan diuji di tiga titik, yaitu tepat di batas, sedikit di bawah, dan sedikit di atas. Untuk Pasal 17 ada 48 titik selama empat tahun pajak. Untuk TER ada 366 titik dari 122 batas. Lalu kombinasi dua arah semua dimensi, dan sedikitnya 2.995 kasus acak dari distribusi upah BPS. Kalau semua kasus acak itu lulus, laju kesalahan bisa kami klaim di bawah 0,1 persen dengan keyakinan 95 persen.
>
> Kebenarannya dibandingkan dengan lima acuan: contoh resmi, kalkulator DJP, hitung manual independen, kalkulator pihak ketiga, dan contoh perhitungan kebijakan perusahaan."

### Slide 8 — Feedback 4: metrik (±2 menit)

> "Untuk feedback keempat, setiap pertanyaan penelitian punya satu metrik utama.
>
> - RQ1 memakai RA, yaitu proporsi perubahan yang bisa dinyatakan tanpa mengubah kode engine. RA diuji pada perubahan yang ditulis orang lain, supaya kami tidak menilai pekerjaan sendiri.
> - RQ2 memakai SER dan CAR. SER mengukur keamanan, yaitu berapa pembaruan salah yang lolos tanpa terdeteksi. CAR mengukur kegunaan, yaitu berapa pembaruan benar yang diterapkan. Keduanya selalu dilaporkan bersama, karena sistem yang selalu menolak bekerja punya SER nol tetapi tidak berguna.
> - RQ3 memakai OAR dan kesalahan terpicu, untuk melihat apakah kesalahan merambat dari satu perubahan ke perubahan berikutnya.
> - RQ4 memakai recall dan F2, karena kebijakan terdampak yang terlewat lebih berbahaya daripada peringatan palsu.
>
> Prinsipnya, kebenaran diukur dari hasil hitung sampai rupiah, bukan dari kemiripan bentuk aturan. MAE tidak kami pakai, karena rata-rata yang kecil bisa menyembunyikan kasus yang salah. Ada bukti dari literatur: pada konsolidasi undang-undang dengan LLM, kemiripan teksnya 93 sampai 99 persen, tetapi yang benar-benar tepat hanya 50,3 persen, dan untuk amandemen berantai hanya 20,51 persen.
>
> Karena jumlah peristiwa nyata sedikit, hasil kami laporkan dengan selang kepercayaan eksak. Contohnya, sepuluh dokumen tanpa kesalahan hanya membuktikan SER paling tinggi 26 persen."

### Slide 9 — Feedback 5: regulation replay (±2 menit)

> "Untuk feedback kelima, bukti bahwa perubahan regulasi bisa langsung diterapkan, kami rancang regulation replay. Sistem dimulai dari knowledge base yang hanya mengenal hukum awal 2023. Lalu setiap regulasi sesudahnya diberikan berurutan, dalam bentuk dokumen aslinya:
>
> - batas upah iuran pensiun setiap Maret;
> - PMK 66 tentang natura pada Juli 2023;
> - pergantian ke TER pada Januari 2024;
> - DTP 2025 yang terbit Februari tetapi berlaku surut ke Januari;
> - perluasan DTP ke sektor pariwisata;
> - perpanjangan DTP untuk 2026.
>
> Sesudah setiap regulasi kami periksa empat syarat. A1, kode engine tidak berubah. A2, hasil sesudah regulasi berlaku sama dengan acuan. A3, hasil sebelum regulasi berlaku tidak berubah. A4, kebijakan perusahaan yang menjadi berkonflik dilaporkan.
>
> Ada juga dokumen pengecoh, misalnya aturan Coretax, yang jawaban benarnya adalah tidak mengubah apa pun. Karena engine dikembangkan saat perubahan 2023–2026 sudah diketahui, kami juga menguji perubahan tak terlihat yang ditulis orang lain, dan regulasi baru yang terbit sesudah rancangan eksperimen didaftarkan."

### Slide 10 — Sebelum dan sesudah revisi (±1 menit)

Cukup bacakan empat baris kunci, tidak semuanya:

> "Ringkasnya, ada empat perubahan besar. Representasi berubah dari YAML menjadi legal knowledge graph. Peran LLM berubah dari di luar inti menjadi objek penelitian yang dijaga gerbang. Novelty berubah dari dua lapis menjadi pembaruan inkremental yang diuji pada amandemen nyata. Bukti adaptasi berubah dari empat perubahan sintetis menjadi regulation replay atas perubahan nyata 2023–2026."

### Slide 11 — Progres draf paper (±1,5 menit)

> "Untuk progres paper, drafnya sekarang 8 halaman format IEEE dan fokus ke argumen penelitian. Versi terbarunya, v8, sudah memuat koreksi metode dari temuan mini demo yang kami tunjukkan di slide 13. Bagian I sampai VI sudah ditulis: pendahuluan, latar belakang dan rumusan masalah, penelitian terkait, representasi, akuisisi, dan metodologi evaluasi. Beberapa parameter, seperti ambang hipotesis dan jumlah kandidat LLM, akan kami kunci sebelum pra-registrasi.
>
> Abstrak dan bagian hasil masih menunggu eksperimen. Teks abu-abu di PDF menandai bagian itu, dan kami sengaja tidak mengisi angka hasil apa pun.
>
> Rujukannya 37, dengan kriteria terbit 2021 ke atas, ber-peer review, dan ber-DOI. Ada tiga pengecualian, yaitu karya terdekat Gogani-Khiabani, buku Ripple-Down Rules, dan sumber rumus pass@k."

Bila dosen ingin melihat paper, pindah ke Bagian B.

### Slide 12 — Status implementasi (±1 menit)

> "Supaya posisi kami jelas. Yang sudah ada, pertama, prototipe engine deterministik dan knowledge base YAML dengan 90 aturan regulasi dan 32 aturan Perusahaan X, yang sudah cocok dengan 45 contoh resmi. Kedua, mini demo yang menjalankan seluruh alur sekali, dari knowledge base awal sampai E4, lengkap dengan knowledge graph RDF, validasi SHACL, query SPARQL, gerbang G1 sampai G5, dan konsensus. Tetapi LLM di mini demo masih tiruan dengan jawaban yang sudah disiapkan, dan kasus ujinya hanya 75, jadi angkanya bukan hasil penelitian.
>
> Yang masih rancangan adalah alur dengan LLM sungguhan, korpus dan pembaruan emas lengkap, ruang uji penuh sekitar 3.000 kasus, dan eksperimen pada data sebenarnya sesudah pra-registrasi."

### Slide 13 — Temuan mini demo (±2 menit)

> "Nilai mini demo bukan pada angkanya, tetapi pada kelemahan rancangan yang ketahuan. Ada lima.
>
> 1. Tanggal berlaku yang salah lolos semua gerbang. Pada perubahan kebijakan K1, kandidat LLM memakai 1 Januari, padahal yang benar 1 Juli, dan tidak ada gerbang yang menangkapnya. Karena itu G2 sekarang juga memeriksa bahwa setiap tanggal ada di kutipan.
> 2. Untuk regulasi yang berlaku surut, LLM tergoda mencatat aturannya pada tanggal berlaku, bukan tanggal terbit. Akibatnya hasil yang dulu dihitung sebelum regulasinya terbit ikut berubah. Karena itu tanggal pencatatan diisi sistem, bukan LLM, dan omega kami tegaskan sebagai pengetahuan hukum.
> 3. Kebijakan perusahaan yang dikalahkan aturan wajib tidak mengubah angka, jadi G5 versi lama akan menolaknya, padahal A4 mewajibkan konflik itu disimpan dan dilaporkan. G5 sekarang menerima konflik yang dilaporkan sebagai efek.
> 4. Konsensus bisa seri. Usulan kami, sistem menolak memilih bila seri, dan urutan kandidat diacak.
> 5. E0 gagal karena kasus uji tidak menjangkau bulan berlaku perubahan. Itu memang tugas E0, dan generator ruang uji nanti wajib menyasar bulan berlaku dan setiap batas lapisan.
>
> Temuan satu sampai empat sudah masuk draf paper v8. Kalau Bapak/Ibu berkenan, demonya bisa kami tunjukkan langsung."

### Slide 14 — Langkah berikutnya (±1,5 menit)

> "Rencana kami mengikuti panduan penelitian. Tahap 0, menjawab keputusan terbuka dan mencari kolaborator untuk peran independen. Tahap 1, membaca utuh karya terdekat untuk memastikan novelty. Tahap 2, spesifikasi domain dan taksonomi perubahan. Tahap 3 dan 4, spesifikasi ontologi, syarat A1–A4, dan gerbang. Sesudah itu kami ingin berdiskusi lagi dengan Bapak/Ibu sebelum mulai membangun, karena mengubah definisi sesudah dibangun jauh lebih mahal.
>
> Ada lima hal yang kami mohon keputusan Bapak/Ibu:
>
> 1. Target publikasinya tugas mata kuliah, jurnal nasional, atau IEEE Access? Kalau IEEE Access, naskahnya harus berbahasa Inggris.
> 2. Apakah kriteria rujukan kami, yaitu 2021 ke atas, ber-peer review, dan ber-DOI dengan tiga pengecualian, sudah sesuai?
> 3. Apakah perlu pembanding berupa LLM yang menghitung PPh 21 langsung?
> 4. Apakah ada akses ke praktisi pajak atau tax center untuk memeriksa ground truth peristiwa TER?
> 5. Apakah Bapak/Ibu setuju dengan dua usulan dari mini demo, yaitu cek tanggal di gerbang G2 dan menolak memilih bila konsensus seri?
>
> Demikian progres kami. Terima kasih, Bapak/Ibu. Kami siap menerima masukan."

---

## Bagian B. Bila dosen membuka draf paper

Arahkan dosen ke tempat setiap feedback dijawab. Nomor halaman mengikuti PDF v8.

| Feedback | Tunjukkan di paper | Yang diucapkan |
|---|---|---|
| 1. Representasi final | Bagian IV: Definisi 1–3 (hlm. 3–4) dan Gambar 2, ontologi (hlm. 5) | "Representasi final kami definisikan secara formal di sini. Gambar 2 menunjukkan kelas dan relasinya." |
| 2. Kontribusi | Paragraf terakhir Bagian I, kontribusi K1–K4 (hlm. 1–2), dan Tabel II di Bagian III (hlm. 4) | "Tabel II menunjukkan posisi kami terhadap karya terdekat. Kolom pembaruan inkremental dan perambatan kesalahan hanya terisi untuk penelitian ini." |
| 3. Ground truth | Tabel I di Bagian II (hlm. 2) dan Bagian VI-B (hlm. 6) | "Tabel I adalah dimensi yang diuji. Jumlah titik ujinya ada di Bagian VI-B." |
| 4. Metrik | Tabel VI di Bagian VI-E (hlm. 7) | "Tabel VI menghubungkan setiap RQ dengan hipotesis, metrik, dan cara analisisnya." |
| 5. Bukti penerapan | Definisi 5, syarat A1–A4 (hlm. 5), dan Tabel IV, korpus (hlm. 6) | "Syarat A1–A4 adalah definisi formal dari 'langsung bisa diterapkan'. Tabel IV adalah peristiwa nyata yang akan diputar ulang." |

Bila ditanya kenapa bagian hasil kosong:

> "Eksperimennya belum dijalankan. Kami sengaja tidak mengisi angka apa pun supaya tidak ada hasil yang dikarang. Urutan kerja kami: definisi dulu, lalu membangun, memvalidasi instrumen, baru eksperimen."

---

## Bagian C. Antisipasi pertanyaan dosen

### "Kenapa tidak LLM saja yang menghitung pajak?"

> "LLM tidak andal untuk hitungan yang harus tepat sampai rupiah; penelitian 2023 dan 2024 menunjukkan LLM masih membuat kesalahan penalaran pajak. Engine deterministik kami sudah tepat pada 1.213 nilai contoh resmi. LLM kami pakai hanya untuk menyusun usulan pembaruan aturan, dan usulan itu disaring gerbang."

### "Apa bedanya dengan NTOL atau penelitian formalisasi lain?"

> "Penelitian itu memformalkan satu keadaan hukum dari nol. Kami memperbarui knowledge base yang sudah berjalan setiap kali regulasi berubah, lalu mengukur apakah hasil lama terjaga, apakah kesalahan merambat, dan dampaknya ke kebijakan perusahaan."

### "Kenapa harus knowledge graph? Apa tidak cukup database biasa?"

> "Dengan graf, hubungan seperti sumber pasal, amandemen, dan konflik menjadi eksplisit. SHACL bisa menolak usulan LLM yang strukturnya salah sebelum diterapkan, dan SPARQL bisa mencari kebijakan yang terdampak dengan satu query. Manfaatnya kami ukur lewat ablasi, yaitu sistem yang sama tanpa graf."

### "Bagaimana tahu hasilnya benar kalau tidak ada pakar pajak?"

> "Kami memakai lima acuan independen, menyimpan sebagian contoh resmi sebagai holdout, mengukur ketajaman kasus uji dengan mutation score, dan memakai pengadjudikasi kedua. Kalau ada akses ke praktisi pajak, kami ingin melibatkannya."

### "Kalau LLM salah, apa yang terjadi?"

> "Usulannya harus lolos lima gerbang. Kalau tidak ada yang lolos, sistem tidak menerapkan apa pun dan meneruskan dokumen ke peninjau manusia. Kesalahan yang tetap lolos itulah yang kami hitung sebagai SER."

### "Sembilan peristiwa itu sedikit, apa cukup?"

> "Betul, karena itu hasilnya kami laporkan dengan selang kepercayaan eksak, bukan klaim signifikan. Cakupannya kami tambah dengan dokumen kontrafaktual, perubahan tak terlihat yang ditulis orang lain, dan regulasi baru yang terbit nanti."

### "Kenapa ada lapisan kebijakan perusahaan?"

> "Karena besar pajak juga ditentukan kebijakan perusahaan, misalnya prorata gaji dan THR. Kebijakan itu tidak boleh menyimpangi aturan wajib. Kasus nyata yang kami temukan, perusahaan menggolongkan lembur sebagai penghasilan tidak teratur, padahal regulasi menggolongkannya teratur."

### "Apakah sistemnya sudah jalan?"

> "Engine dan knowledge base prototipe sudah jalan dan sudah diuji dengan contoh resmi. Mini demo juga sudah menjalankan seluruh alur sekali, tetapi dengan LLM tiruan dan 75 kasus uji. Sistem penuh dengan LLM sungguhan dan eksperimennya masih rancangan, dan baru kami bangun sesudah definisinya disepakati."

### "Angka di mini demo itu hasil penelitian?"

> "Bukan. Jawaban LLM di mini demo sudah disiapkan supaya setiap gerbang punya sesuatu untuk ditangkap. Gunanya menemukan kelemahan rancangan, bukan mengukur kinerja."

### Bila ditanya hal yang belum ada jawabannya

> "Itu belum kami putuskan, Bapak/Ibu. Saat ini kami condong ke [pilihan], dengan alasan [alasan]. Kami catat dan akan kami putuskan sebelum pra-registrasi."

---

## Bagian D. Angka yang perlu diingat

| Angka | Arti |
|---|---|
| 5 lapisan Pasal 17 | 5%, 15%, 25%, 30%, 35% |
| 125 lapisan TER | kategori A 44, B 40, C 41 |
| 48 dan 366 | titik batas Pasal 17 (4 tahun) dan TER (122 batas) |
| 2.995 | kasus acak untuk klaim laju kesalahan di bawah 0,1% (keyakinan 95%) |
| 9 | peristiwa perubahan nyata 2023–2026 di korpus |
| 1.213 / 45 | nilai harapan dari 45 contoh resmi, tanpa selisih tak terjelaskan |
| 254 | sel rumus spreadsheet perusahaan yang berisi konstanta regulasi |
| 7 dari 7 | implementasi open source PPh 21 yang memuat kesalahan |
| 93–99% vs 50,3% dan 20,51% | kemiripan teks vs kecocokan persis (Prior dkk. 2025) |
| 26% | batas atas SER bila 10 dokumen tanpa kesalahan |
| 8 halaman, 37 rujukan | ukuran draf paper sekarang (v8) |
| 75 | kasus uji di mini demo (LLM tiruan, angkanya bukan hasil) |

## Bagian E. Yang jangan diklaim

- Jangan bilang sistem penuh **sudah jadi**. Yang ada baru prototipe mini dengan LLM tiruan; LLM sungguhan, korpus lengkap, dan eksperimen masih "dirancang" atau "akan".
- Jangan menyebut angka SER, CAR, RA, atau OAR sebagai hasil. Angka di mini demo berasal dari LLM tiruan.
- Jangan bilang karya pembanding sudah dibaca lengkap. Baru dari abstraknya.
- Sebut karya ini "penelitian", bukan "makalah", dan sumber kebenaran "acuan", bukan "oracle".

## Bagian F. Bila presentasi dibagi dua orang

- **Pembicara pertama, slide 1–6 (konsep):** judul, ringkasan feedback, representasi, novelty, arsitektur.
- **Pembicara kedua, slide 7–14 (evaluasi dan progres):** ruang uji, metrik, regulation replay, perbandingan konsep, progres paper, status, temuan mini demo, rencana.
- Serah terima di akhir slide 6, misalnya: "Untuk bagaimana sistem ini dievaluasi, akan dijelaskan oleh rekan saya."
