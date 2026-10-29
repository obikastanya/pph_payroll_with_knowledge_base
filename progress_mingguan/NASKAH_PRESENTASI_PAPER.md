# Naskah presentasi draf paper (27 Oktober 2026)

Naskah ini khusus untuk membawakan draf paper `paper/draft/naskah_draf_v7/main.pdf` (8 halaman, format IEEE). Naskah untuk slide ada di [NASKAH_PRESENTASI.md](NASKAH_PRESENTASI.md). Bagian B di berkas itu hanya peta singkat, sedangkan berkas ini naskah lengkapnya. Kalimat dalam kutipan adalah contoh ucapan. Sesuaikan dengan gaya bicara sendiri, asalkan isinya tetap.

## Cara memakai

- **Waktu sempit, atau dosen hanya ingin gambaran:** Bagian A, versi singkat sekitar 3 menit.
- **Dosen ingin paper dibahas:** Bagian B, per bagian paper, sekitar 16 menit.
- **Dosen bertanya di mana feedback tertentu dijawab:** Bagian C.
- **Tanya jawab tentang isi paper:** Bagian D.

Nomor halaman di naskah ini mengikuti PDF v7.

**Tiga hal yang harus sampai ke dosen:**

1. Alur argumen paper: masalah, celah penelitian, usulan, definisi formal, lalu rancangan evaluasi.
2. Kebaruannya ada pada LLM yang memperbarui knowledge base yang sudah berjalan, diuji pada rangkaian amandemen nyata, dengan hasil periode lama terjaga dan kesalahan yang merambat diukur. Pola "LLM menyusun aturan, engine menghitung" tidak diklaim sebagai kebaruan.
3. Bagian I–VI sudah ditulis. Kalimat hasil di abstrak, Bagian VII, dan Bagian VIII masih teks abu-abu dalam kurung siku karena eksperimennya belum dijalankan.

### Peta halaman

| Hlm. | Isi | Yang ditunjuk |
|---|---|---|
| 1 | Judul, penulis, abstrak, awal Bagian I | Teks abu-abu di akhir abstrak |
| 2 | RQ1–RQ4, kontribusi K1–K4, Bagian II, awal Bagian III | Tabel I |
| 3 | Gambar 1, Bagian III-B dan III-C, Bagian IV-A | Gambar 1, Definisi 1–2 |
| 4 | Tabel II, Definisi 3, Bagian IV-B sampai IV-D, awal Bagian V | Tabel II, persamaan (1), Algoritma 1 |
| 5 | Gambar 2, Definisi 4–6, Bagian V-B dan V-C, awal Bagian VI | Gambar 2, Definisi 5, Tabel III |
| 6 | Bagian VI-A sampai VI-E | Tabel IV, Tabel V, persamaan (3) dan (4) |
| 7 | Tabel VI, Bagian VII dan VIII, pengungkapan AI, awal daftar pustaka | Tabel VI, teks abu-abu Bagian VII–VIII |
| 8 | Lanjutan daftar pustaka | Rujukan [10]–[37] |

---

## Bagian A. Versi singkat (±3 menit)

> "Ini draf paper kami, delapan halaman format IEEE.
>
> Masalahnya, PPh 21 dipotong setiap bulan dan regulasinya sering berubah, misalnya pergantian ke TER pada 2024 dan PPh 21 DTP yang berlaku surut pada 2025. Dalam praktik, aturannya tertanam di kode program atau spreadsheet. Akibatnya setiap perubahan menuntut pemrograman ulang, dan hasil periode lama bisa bergeser tanpa terdeteksi.
>
> Penelitian formalisasi pajak dengan LLM sudah ada, tetapi semuanya membangun aturan dari nol untuk satu keadaan hukum. Belum ada yang mengukur, pada basis aturan yang dieksekusi, apakah pembaruan berulang oleh LLM menjaga hasil periode lama, apakah kesalahannya merambat, dan apa dampaknya ke kebijakan perusahaan.
>
> Usulan kami ada di Gambar 1, halaman 3. Pengetahuan disimpan sebagai legal knowledge graph temporal dua lapis, yaitu regulasi dan kebijakan perusahaan. Semua perhitungan dijalankan inference engine deterministik. LLM hanya menyusun kandidat pembaruan. Kandidat itu disaring lima gerbang verifikasi lalu dipilih lewat konsensus perilaku. Kalau tidak ada yang lolos, sistem menolak memilih dan menyerahkannya ke manusia.
>
> Bagian IV dan V berisi definisi formalnya. Yang paling penting adalah Definisi 5 di halaman 5, yaitu syarat A1 sampai A4 untuk menyebut sebuah pembaruan benar.
>
> Bagian VI adalah rancangan evaluasinya, yaitu regulation replay atas sembilan peristiwa nyata 2023–2026, ruang uji yang mencakup semua batas lapisan tarif, dan satu metrik utama untuk setiap RQ. Semuanya dirangkum di Tabel VI, halaman 7.
>
> Kalimat hasil di abstrak, Bagian VII, dan Bagian VIII masih teks abu-abu karena eksperimennya belum dijalankan. Rujukannya 37."

---

## Bagian B. Versi lengkap per bagian paper (±16 menit)

### 1. Judul, penulis, dan abstrak (hlm. 1, ±1 menit)

*Tunjuk:* judul, lalu teks abu-abu di akhir abstrak.

> "Judul paper sama dengan judul penelitian di slide. Penulisnya kami berdua, dari Program Studi Teknik Informatika ITS.
>
> Abstraknya berisi empat hal, yaitu masalah, celah penelitian, usulan, dan rancangan evaluasi. Dua kalimat terakhir, kalimat hasil dan kalimat implikasi, masih teks abu-abu dalam kurung siku. Keduanya baru diisi setelah eksperimen, dengan RA, SER dan CAR beserta selang kepercayaan 95%, OAR, dan recall analisis dampak."

### 2. Pendahuluan, Bagian I (hlm. 1–2, ±2 menit)

*Tunjuk:* paragraf audit spreadsheet di halaman 1, lalu RQ1–RQ4 dan paragraf kontribusi di halaman 2.

> "Pendahuluan dibuka dengan masalah praktis. PPh 21 dipotong setiap bulan, jadi kesalahan hitung langsung muncul di slip gaji. Regulasinya juga sering berubah. Metode disetahunkan diganti TER pada 2024, DTP berlaku surut pada 2025 lalu diperpanjang untuk 2026, dan batas upah iuran pensiun berubah setiap tahun.
>
> Ada dua bukti dari lapangan. Audit spreadsheet payroll sebuah perusahaan menemukan konstanta regulasi di 254 sel rumus, dan uang lembur dicatat sebagai penghasilan tidak teratur padahal regulasi menggolongkannya teratur. Survei atas tujuh implementasi PPh 21 open source menemukan kesalahan terverifikasi di ketujuhnya.
>
> Lalu celahnya. KBS dan rules as code memisahkan aturan dari kode, tetapi bebannya pindah ke pemeliharaan knowledge base. Ripple-Down Rules menjaga kasus lama tetap benar, tetapi pakar tetap menulis setiap perubahan. Karya formalisasi pajak dengan LLM memformalkan satu keadaan hukum dari nol. Pembaruan berulang juga berisiko. Pada konsolidasi undang-undang dengan LLM, kemiripan teksnya 93 sampai 99 persen, tetapi yang benar-benar tepat hanya 50,3 persen, dan untuk rangkaian amandemen hanya 20,51 persen.
>
> Di halaman 2 ada empat RQ dan empat kontribusi, K1 sampai K4. Kalimat terakhir paragraf kontribusi adalah pernyataan kebaruan kami. Pola 'LLM menyusun aturan, engine menghitung' tidak kami klaim sebagai kebaruan. Kebaruannya ada pada pembaruan inkremental knowledge base yang dieksekusi, diuji pada rangkaian amandemen nyata, beserta perambatan kesalahan dan dampaknya terhadap kebijakan perusahaan."

### 3. Latar belakang dan rumusan masalah, Bagian II (hlm. 2, ±1,5 menit)

*Tunjuk:* Tabel I, lalu paragraf terakhir II-C.

> "Bagian II menjelaskan domainnya. II-A adalah cara menghitung PPh 21 pegawai tetap. Bruto dikurangi biaya jabatan dan iuran pensiun menjadi neto. Neto setahun dikurangi PTKP, dibulatkan ke bawah ke ribuan rupiah, menjadi PKP yang dikenai lima lapisan tarif Pasal 17. Sampai 2023 potongan bulanan dihitung dengan menyetahunkan penghasilan. Sejak 2024, Januari sampai November memakai TER dikali bruto bulanan, dan selisihnya dipotong di masa terakhir. Tabel I merangkum dimensi yang kami cakup. Cakupannya pegawai tetap dengan satu pemberi kerja, tahun pajak 2023–2026.
>
> II-B tentang kebijakan perusahaan. Perusahaan boleh menetapkan komponen seperti prorata gaji dan THR, tetapi tidak boleh menyimpangi ketentuan wajib, seperti pada kasus lembur tadi. Kalau bertentangan, yang berlaku regulasi, yaitu asas lex superior, dan konfliknya harus tercatat.
>
> II-C mengelompokkan sembilan jenis perubahan, dari perubahan parameter sampai pergantian metode dan ketentuan berlaku surut. Hasil nanti dilaporkan per jenis, supaya perubahan parameter yang mudah tidak menutupi pergantian metode yang sulit.
>
> Paragraf terakhir II-C adalah rumusan masalahnya. Masukannya knowledge base yang benar sebelum peristiwa ke-n beserta dokumen sumbernya. Keluarannya knowledge base yang benar sesudahnya, tanpa mengubah kode engine, tanpa mengubah hasil masa sebelum perubahan berlaku, dan dengan laporan kebijakan yang menjadi bertentangan. Masalah ini berulang, jadi kesalahan yang lolos bisa merambat ke peristiwa berikutnya."

### 4. Penelitian terkait, Bagian III (hlm. 2–4, ±1,5 menit)

*Tunjuk:* Tabel II di halaman 4, terutama tiga kolom terakhir.

> "Penelitian terkait kami bagi tiga. III-A adalah rules as code dan sistem pajak berbasis aturan, misalnya Catala, DataLex, Logical English, OpenFisca, dan formalisasi payroll Belgia oleh Dumancic dan kawan-kawan. Di semua karya itu pengetahuan ditulis manusia.
>
> III-B tentang akuisisi pengetahuan dengan LLM. NTOL untuk pajak India mencapai akurasi 80 persen pada 20 skenario. Ada juga penerjemahan Internal Revenue Code ke Prolog dan hukum pajak ke Catala. Semuanya memformalkan satu keadaan hukum dari nol. Yang paling dekat adalah Gogani-Khiabani dan kawan-kawan, yang mengusulkan LLM menerapkan perubahan ke versi perangkat lunak pajak sebelumnya, tetapi baru membahas tantangannya tanpa evaluasi atas rangkaian perubahan.
>
> III-C tentang pembaruan berulang. Penyuntingan pengetahuan LLM yang berurutan membuat model lupa bertahap. Dari sini kami mengambil evaluasi berbasis eksekusi, seperti pass@k, sebagai dasar metrik. Untuk representasi, standar ELI, OWL-Time, PROV-O, dan SHACL menyediakan kosakata waktu dan asal-usul, tetapi belum dipakai untuk aturan yang dieksekusi dan diperbarui mesin.
>
> Tabel II di halaman 4 merangkum posisi kami. Tiga kolom terakhir, yaitu pembaruan inkremental, perambatan kesalahan yang diukur, dan lapisan perusahaan, hanya terisi 'ya' untuk penelitian ini. Perlu kami sampaikan, isi tabel ini berdasarkan abstrak karya-karya tersebut. Naskah lengkapnya akan kami baca untuk memastikan."

### 5. Ikhtisar sistem, Gambar 1 (hlm. 3, ±1 menit)

> "Gambar 1 adalah ikhtisar sistemnya. Baris atas adalah alur akuisisi. Dokumen regulasi atau kebijakan baru masuk, lalu LLM menilai relevansinya dengan menyertakan kutipan. Kalau tidak relevan, pembaruannya kosong. Kalau relevan, LLM menyusun m kandidat pembaruan, yang diuji gerbang G1 sampai G5, lalu dipilih lewat konsensus perilaku. Kalau tidak ada yang lolos, dokumen diteruskan ke peninjau manusia.
>
> Baris bawah adalah knowledge graph temporal dua lapis dan inference engine deterministik yang menghitung PPh 21 per masa, lengkap dengan jejak sampai pasal. LLM hanya mengusulkan pembaruan dan tidak pernah menghitung pajak."

### 6. Representasi dan inference engine, Bagian IV (hlm. 3–5, ±2,5 menit)

*Tunjuk:* Definisi 1–3, persamaan (1) dan Algoritma 1 di halaman 4, lalu Gambar 2 di halaman 5.

> "Bagian IV menjawab feedback pertama tentang representasi final. Pengetahuan kami bagi dua. Pengetahuan struktural, seperti regulasi memuat pasal, aturan bersumber dari pasal, dan kebijakan berkonflik dengan aturan wajib, disimpan sebagai legal knowledge graph. Pengetahuan komputasional, seperti TER dikali bruto, pembulatan, dan gross-up, dijalankan inference engine. Alasannya, OWL dan SWRL tidak punya aritmetika eksak dengan pembulatan maupun iterasi titik tetap. Engine prototipe yang kami pakai ulang sudah tidak punya selisih tak terjelaskan pada 1.213 nilai dari 45 contoh perhitungan resmi.
>
> Definisi 1, knowledge base terdiri atas ontologi, aturan, parameter berversi, dan tabel berversi, dan masing-masing berada di lapisan regulasi atau lapisan perusahaan. Definisi 2, setiap aturan punya lapisan, sifat, masa berlaku, tanggal pencatatan, kondisi, ekspresi, dan pasal sumber. Sifatnya wajib, tafsir, default, atau opsional. Aturan wajib tidak bisa ditimpa perusahaan, sedangkan aturan default boleh ditimpa aturan opsional perusahaan.
>
> Definisi 3 memakai dua sumbu waktu. t adalah masa pajak yang dihitung. Omega adalah tanggal pengetahuan, yaitu apa yang sudah diketahui sistem pada tanggal itu. Dengan dua sumbu ini kami bisa membedakan aturan yang berlaku surut dari aturan yang baru dicatat.
>
> IV-B, ontologinya ada di Gambar 2, halaman 5. Kosakatanya memakai ulang ELI, OWL-Time, dan PROV-O. Kebijakan perusahaan dimodelkan setara dengan regulasi; yang membedakan hanya lapisan dan penerbitnya. SHACL menolak pembaruan yang strukturnya salah, misalnya aturan regulasi tanpa pasal sumber, sedangkan konflik kebijakan dengan aturan wajib dicatat sebagai peringatan.
>
> IV-C, persamaan (1). Kalau beberapa aturan bersaing, pemenangnya dipilih dengan kunci kappa yang mengikuti asas hukum, yaitu lex superior, penimpaan sah, lex specialis, lex posterior, lalu prioritas eksplisit. Kalau masih ada lebih dari satu pemenang dengan nilai berbeda, engine berhenti dengan status AMBIGU dan tidak memilih diam-diam.
>
> IV-D, Algoritma 1. Perhitungan bersiklus hanya diizinkan untuk aturan titik tetap seperti gross-up. Menurut teorema Knaster–Tarski titik tetapnya pasti ada, dan kalau ada lebih dari satu solusi, engine mencatatnya. Rupiah disimpan sebagai bilangan bulat, dan setiap nilai disertai jejak sampai pasal sumber."

### 7. Akuisisi berbantuan LLM, Bagian V (hlm. 4–5, ±2,5 menit)

*Tunjuk:* Definisi 5 di halaman 5, lalu Tabel III.

> "Bagian V adalah metode akuisisinya. Definisi 4 mendefinisikan peristiwa perubahan, yang punya tanggal terbit dan tanggal berlaku. Kalau tanggal berlaku lebih awal dari tanggal terbit, peristiwanya berlaku surut. Pembaruan berisi unsur yang ditambah, diubah, dan dicabut. Pembaruan emas disusun peneliti, sedangkan pembaruan sistem dihasilkan alur akuisisi. Untuk dokumen yang tidak mengubah perhitungan, jawaban yang benar adalah pembaruan kosong.
>
> Definisi 5 adalah jawaban kami untuk feedback kelima, yaitu definisi formal 'langsung bisa diterapkan'. A1, kode engine tidak berubah. A2, hasil sesudah perubahan berlaku sama dengan acuan. A3 dipecah dua. A3t, hasil untuk masa sebelum perubahan berlaku tidak berubah. A3 omega, hasil yang dihitung dengan pengetahuan sebelum regulasi terbit juga tidak berubah, jadi apa yang dulu diketahui sistem tetap bisa direproduksi. A4, setiap kebijakan yang berkonflik dengan aturan wajib dilaporkan.
>
> Definisi 6 membedakan dua jenis adaptivitas. Representasional, artinya ada pembaruan dalam bahasa representasi kami yang memenuhi A1 sampai A4, dan ini diuji di RQ1. Operasional, artinya pembaruan yang benar-benar dipilih sistem memenuhi A2, A3t, dan A4, dan ini diuji di RQ2 dan RQ3. A1 dan A3 omega dijamin arsitektur, karena LLM hanya menyunting knowledge base, tetapi tetap kami periksa sebagai invarian.
>
> V-B adalah alurnya. Dokumen dipotong per pasal, LLM menilai relevansinya dengan kutipan, lalu menyusun m kandidat secara independen. Setiap kandidat diuji lima gerbang di Tabel III. G1 memeriksa struktur dengan SHACL, G2 memeriksa bahwa kutipan benar-benar ada di dokumen, G3 memeriksa konsistensi dan konflik, G4 memeriksa regresi, dan G5 memeriksa bahwa pembaruan benar-benar berefek. G5 perlu karena pembaruan kosong lolos G1 sampai G4 tanpa menimbulkan regresi. G4 setara dengan cornerstone case pada Ripple-Down Rules. Kandidat yang gagal boleh diperbaiki dalam jumlah putaran terbatas.
>
> V-C tentang pemilihan. Setiap kandidat yang lolos dihitung hasilnya pada kasus uji gerbang. Kandidat dengan hasil identik dikelompokkan, dan wakil kelompok terbesar dipilih. Inilah konsensus perilaku, karena yang dibandingkan hasil hitungnya, bukan bentuk aturannya. Kalau tidak ada yang lolos, sistem abstain dan meneruskan dokumen ke manusia. Analisis dampak menandai kebijakan perusahaan yang nilai keluarannya berubah, aturan pemenangnya berubah, atau menjadi berkonflik dengan aturan wajib."

*Bila presentasi berdua, serah terima di sini (lihat Bagian F).*

### 8. Metodologi evaluasi, Bagian VI (hlm. 5–7, ±3 menit)

*Tunjuk:* Tabel IV dan Tabel V di halaman 6, persamaan (3) dan (4), lalu Tabel VI di halaman 7.

> "Bagian VI menjawab feedback ketiga dan keempat. Ada empat prinsip. Pertama, setiap RQ punya satu metrik utama yang ditetapkan sebelum eksperimen. Kedua, kebenaran diukur dari hasil hitung sampai rupiah, bukan kemiripan bentuk aturan, dan MAE tidak dipakai. Ketiga, data yang dipakai sistem terpisah dari data penilainya. Keempat, hasil dilaporkan dengan selang kepercayaan eksak karena jumlah peristiwa nyata kecil.
>
> VI-A, desainnya design science research. Hipotesis, metrik, ambang, dan pembagian data kami daftarkan ke layanan pra-registrasi sebelum eksperimen. Data pengembangan berisi regulasi fiktif, perubahan sebelum 2023, dan sebagian kecil kebijakan buatan. Data uji adalah semua peristiwa nyata 2023–2026, ditambah regulasi yang terbit sesudah pra-registrasi. Karena representasi dirancang ketika perubahan 2023–2026 sudah diketahui, kami juga menguji perubahan tak terlihat yang ditulis orang lain.
>
> VI-B, acuan dan ruang uji. Knowledge base acuan, K bintang, divalidasi terhadap lima acuan, yaitu contoh resmi di regulasi, kalkulator DJP, hitung manual independen, kalkulator pihak ketiga, dan contoh perhitungan kebijakan perusahaan. K bintang lalu menghasilkan nilai harapan kasus uji, yang ketajamannya diukur dengan mutation score. Ruang ujinya mencakup kombinasi dua arah dimensi di Tabel I, setiap batas lapisan di tiga titik, yaitu 48 titik Pasal 17 dan 366 titik TER, serta sedikitnya 2.995 kasus acak dari distribusi upah BPS. Kalau semua kasus acak lulus, laju kesalahan bisa diklaim di bawah 0,1 persen dengan keyakinan 95 persen.
>
> VI-C, korpusnya di Tabel IV. Baris pertama, batas upah iuran pensiun, berubah setiap Maret 2023–2026, jadi ada empat peristiwa. Ditambah lima regulasi di baris berikutnya, totalnya sembilan peristiwa. Ada juga dokumen pengecoh seperti ketentuan Coretax, yang jawaban benarnya pembaruan kosong, dan dokumen kontrafaktual yang nilai dan tanggalnya kami ubah untuk memeriksa apakah LLM membaca dokumen atau hanya mengingat data latihnya.
>
> VI-D, ada dua mode. Mode terisolasi untuk RQ2, yaitu setiap pembaruan diterapkan pada knowledge base acuan yang benar. Mode berantai untuk RQ3, yaitu pembaruan diterapkan pada hasil sistem sendiri sebelumnya, sehingga kesalahan bisa menumpuk. Keduanya tanpa peninjau manusia, jadi hasilnya batas bawah kinerja. Pembanding dan ablasinya ada di Tabel V, misalnya B3 dengan satu kandidat dan gerbang G1–G2 saja, dan B4 dengan banyak kandidat dan suara terbanyak tanpa gerbang.
>
> VI-E, metriknya. SER adalah proporsi dokumen yang salah diterapkan tanpa terdeteksi, CAR proporsi yang benar diterapkan, dan keduanya selalu dilaporkan bersama. Persamaan (4) adalah kesalahan terpicu, yaitu kesalahan yang muncul di mode berantai tetapi tidak muncul di mode terisolasi dan belum ada sebelumnya. Untuk RQ4 recall diutamakan, dan F2 memberi bobot recall dua kali precision.
>
> Tabel VI di halaman 7 menghubungkan setiap RQ dengan hipotesis, metrik utama, dan analisisnya. Satu catatan jujur tentang jumlah data. Sepuluh dokumen tanpa kesalahan hanya membuktikan SER paling tinggi 26 persen, dan klaim SER di bawah 5 persen butuh sedikitnya 59 dokumen. Karena itu ambang hipotesis kami tetapkan sesuai jumlah data, sebelum eksperimen."

### 9. Hasil, ancaman validitas, dan kesimpulan, Bagian VII–VIII (hlm. 7, ±1 menit)

*Tunjuk:* teks abu-abu Bagian VII, subbagian Ancaman terhadap validitas, lalu teks abu-abu Bagian VIII.

> "Bagian VII masih teks abu-abu. Isinya nanti, untuk setiap RQ, metrik utama dengan selang kepercayaan 95% dan putusan hipotesisnya menurut Tabel VI, hasil per jenis perubahan dan per lapisan, perbandingan dengan pembanding dan ablasi, serta analisis kesalahan LLM.
>
> Yang sudah kami tulis adalah ancaman terhadap validitas. Pertama, acuan dan engine disusun tim yang sama. Ini kami mitigasi dengan acuan pihak ketiga, holdout contoh resmi, dan pengadjudikasi kedua. Kedua, representasi dirancang setelah perubahan 2023–2026 diketahui, karena itu ada pengujian perubahan tak terlihat dan peristiwa prospektif. Ketiga, cocok dengan acuan belum tentu sesuai hukum, karena kami tidak melibatkan pakar hukum pajak. Keempat, cakupannya satu yurisdiksi, satu jenis pajak, dan jumlah peristiwa yang kecil. Kelima, regulasi 2023–2026 mungkin ada di data latih LLM, dan ini kami periksa dengan dokumen kontrafaktual.
>
> Bagian VIII, kesimpulan, juga masih teks abu-abu dan baru ditulis setelah hasil ada."

### 10. Daftar pustaka (hlm. 7–8, ±30 detik)

> "Daftar pustakanya 37 rujukan. Kriterianya terbit 2021 ke atas, ber-peer review, dan ber-DOI. Regulasi dan standar seperti OWL-Time dan SHACL dipakai sebagai sumber primer. Ada tiga pengecualian, yaitu karya terdekat Gogani-Khiabani yang masih berupa preprint arXiv, buku Ripple-Down Rules, dan sumber rumus pass@k."

---

## Bagian C. Bila dosen bertanya di mana feedback dijawab

| Feedback | Tunjukkan di paper | Halaman |
|---|---|---|
| 1. Representasi final | Bagian IV, Definisi 1–3, dan Gambar 2 | 3–5 |
| 2. Kontribusi | Paragraf kontribusi K1–K4 dan Tabel II | 2 dan 4 |
| 3. Ground truth | Tabel I dan Bagian VI-B | 2 dan 6 |
| 4. Metrik | Bagian VI-E dan Tabel VI | 6–7 |
| 5. Bukti penerapan | Definisi 5 (A1–A4) dan Tabel IV | 5 dan 6 |

---

## Bagian D. Pertanyaan yang mungkin muncul tentang isi paper

### "Apa bedanya t dan ω?"

> "t adalah masa pajak yang dihitung, sedangkan omega adalah tanggal pengetahuan. Contohnya PMK 10/2025, yang terbit Februari tetapi berlaku sejak Januari. Gaji Januari 2025 yang dihitung dengan pengetahuan per akhir Januari tetap memakai aturan lama, karena PMK-nya belum terbit. Kalau dihitung ulang dengan pengetahuan sesudah Februari, fasilitas DTP ikut diperhitungkan untuk pegawai yang memenuhi syarat. Dua-duanya bisa direproduksi, dan ini penting untuk audit."

### "Apa beda adaptif representasional dan operasional?"

> "Representasional berarti bahasa representasi kami mampu menyatakan perubahan itu tanpa mengubah kode engine, dan ini RQ1. Operasional berarti pembaruan yang benar-benar dipilih sistem dengan LLM memang benar, dan ini RQ2 dan RQ3. Yang pertama soal kemampuan representasi, yang kedua soal kinerja sistem."

### "Kenapa A1 dan A3ω tidak diuji seperti syarat lain?"

> "Keduanya dijamin arsitektur. LLM hanya menyunting knowledge base, bukan kode engine, dan unsur baru dicatat dengan tanggal pencatatan sama dengan tanggal terbit, sehingga perhitungan dengan pengetahuan lama tidak melihatnya. Walaupun begitu, keduanya tetap kami periksa sebagai invarian di semua eksperimen, di baris pertama Tabel VI."

### "Kenapa urutan kunci κ seperti itu?"

> "Urutannya mengikuti asas hukum. Lex superior paling depan, jadi aturan wajib regulasi tidak bisa dikalahkan perusahaan. Lalu penimpaan sah, yaitu aturan opsional perusahaan atas aturan default. Lalu lex specialis, lex posterior, dan terakhir prioritas eksplisit. Kalau masih ada pemenang ganda dengan nilai berbeda, statusnya AMBIGU."

### "Kenapa gross-up butuh teorema titik tetap?"

> "Pada gross-up, tunjangan pajak bergantung pada PPh, padahal PPh bergantung pada tunjangan itu. Jadi tunjangan T harus sama dengan PPh dari bruto B ditambah T. Fungsi itu tidak turun pada rupiah bulat yang terbatas, sehingga menurut teorema Knaster–Tarski titik tetapnya pasti ada. Engine mencarinya dari batas bawah dan batas atas, dan kalau hasilnya berbeda, solusi ganda dicatat."

### "Kenapa kandidat dipilih lewat hasil hitung, bukan bentuk aturannya?"

> "Dua kandidat bisa ditulis berbeda tetapi menghasilkan pajak yang sama, atau mirip tetapi hasilnya berbeda. Yang penting bagi slip gaji adalah hasilnya. Karena itu kandidat dikelompokkan menurut hasil hitung pada kasus uji gerbang. Pembanding B4 dan ablasi cara pemilihan lain di Tabel V menguji apakah cara ini memang lebih baik."

### "Kenapa kasus uji gerbang dan kasus uji penilaian dipisah?"

> "Kasus uji gerbang, S-G, dibangkitkan otomatis untuk menyaring dan memilih kandidat. Kasus uji penilaian, S-E, hanya dipakai untuk menilai sistem. Keduanya tidak beririsan, supaya sistem tidak dinilai dengan kasus yang dipakainya sendiri untuk memilih."

### "Apa beda mode terisolasi dan berantai?"

> "Di mode terisolasi, setiap pembaruan diterapkan pada knowledge base acuan yang benar, jadi kami mengukur kualitas akuisisi per dokumen. Di mode berantai, pembaruan diterapkan pada hasil sistem sendiri, seperti pemakaian nyata, sehingga kesalahan bisa menumpuk. Kesalahan yang hanya muncul di mode berantai itulah kesalahan terpicu."

### "Apa hubungannya dengan Ripple-Down Rules?"

> "Ripple-Down Rules menambah aturan secara inkremental dan menjaga kasus lama, yang disebut cornerstone case, tetap benar. Gerbang G4 kami berperan sama. Bedanya, di Ripple-Down Rules pakar manusia yang menulis setiap perubahan, sedangkan di sini LLM yang mengusulkan dan gerbang yang menyaring."

### "Bagaimana memastikan acuan K* benar?"

> "Ada lima acuan independen, GT1 sampai GT5, dan sebagian contoh resmi disimpan sebagai holdout. Ketajaman kasus uji diukur dengan mutation score. Eksperimen E0 khusus memvalidasi acuan dan kasus uji sebelum E1 sampai E4 dijalankan. Keterbatasannya kami tulis di ancaman validitas, yaitu tidak ada pakar hukum pajak, jadi cocok dengan acuan belum tentu sesuai hukum."

### "Angka 254 sel dan tujuh implementasi itu dari mana?"

> "Dua-duanya studi pendahuluan kami sendiri. Angka 254 sel berasal dari studi kasus kami atas spreadsheet payroll sebuah perusahaan. Survei tujuh repo open source tercatat di jurnal penelitian kami. Ketujuhnya punya kesalahan terverifikasi, dan dari empat yang bisa dijalankan, hanya satu yang memberi angka benar pada kasus acuan."

Sumbernya di repo: `dataset/02_studi_kasus/README.md` dan `journal.md`.

### "Kenapa B2, LLM menghitung langsung, hanya motivasi?"

> "B2 bukan pesaing di RQ mana pun. Gunanya menunjukkan kenapa LLM tidak dipakai untuk menghitung. Apakah B2 perlu dijalankan penuh adalah salah satu hal yang kami mohon keputusan Bapak/Ibu."

### "Ambang θ dan jumlah kandidat m berapa?"

> "Belum kami tetapkan. Keduanya akan dikunci sebelum pra-registrasi, menyesuaikan jumlah data yang benar-benar tersedia."

### "Kenapa ada paragraf pengungkapan penggunaan AI?"

> "Kebijakan IEEE mewajibkan pengungkapan bila AI dipakai dalam penyusunan naskah. Draf ini dibantu asisten AI untuk menyusun kalimat dari kerangka penelitian dan menyiapkan kode LaTeX. Isi, klaim, angka, dan rujukannya kami periksa dan menjadi tanggung jawab kami."

### "Kenapa paper berbahasa Indonesia?"

> "Karena target publikasinya belum diputuskan. Kalau targetnya IEEE Access, naskah akan kami tulis dalam bahasa Inggris. Ini juga salah satu keputusan yang kami mohon dari Bapak/Ibu."

---

## Bagian E. Yang jangan diklaim saat membahas paper

- Jangan menyebut angka hasil apa pun. Teks abu-abu berarti hasilnya belum ada.
- Jangan bilang knowledge graph, gerbang, korpus, atau eksperimen sudah jadi. Yang sudah ada baru prototipe engine dan knowledge base YAML yang cocok dengan 45 contoh resmi.
- Jangan bilang Tabel II hasil membaca naskah lengkap. Isinya berdasarkan abstrak.
- Jangan bilang LLM menghitung pajak. LLM hanya mengusulkan pembaruan.
- Jangan menyebut nilai ambang θ atau jumlah kandidat m. Keduanya belum ditetapkan.
- Sebut karya ini "penelitian", bukan "makalah", dan sumber kebenaran "acuan", bukan "oracle".

## Bagian F. Bila dibawakan berdua

- **Pembicara pertama, halaman 1–5:** judul dan abstrak, Pendahuluan, Latar belakang, Penelitian terkait, Gambar 1, Representasi, dan Akuisisi.
- **Pembicara kedua, halaman 5–8:** Metodologi evaluasi, Hasil dan ancaman validitas, Kesimpulan, dan daftar pustaka.
- Serah terima di akhir Bagian V, misalnya: "Untuk bagaimana semua ini dievaluasi, akan dijelaskan oleh rekan saya."
