# Panduan Revisi Naskah Ilmiah agar Natural dan Tidak Terbaca sebagai Tulisan AI

Panduan mandiri untuk agent AI (Claude atau agent lain) dan manusia yang menulis, memparafrasekan, atau merevisi naskah ilmiah. Semua aturan, prosedur, dan alat cek yang diperlukan ada di file ini. Tidak ada skrip, memori sesi, atau dokumen lain yang wajib dibaca.

- **Versi:** final, 18 Oktober 2026
- **Asal:** gabungan dua panduan revisi dan aturan gaya IEEE dari proyek StaticKD (naskah target IEEE Access), ditambah pelajaran dari uji detektor AI pada naskah itu. Contoh di file ini diambil dari naskah tersebut. Aturannya berlaku untuk naskah lain.
- **Bahasa:** aturan ditulis dalam bahasa Indonesia; contoh kalimat naskah dalam bahasa Inggris.
- **Tanda ★:** pola yang **terbukti** ditandai detektor AI pengguna pada naskah nyata. Pola tanpa ★ berasal dari literatur atau review gaya.

---

## Daftar isi

0. [Mulai cepat untuk agent](#0-mulai-cepat-untuk-agent)
1. [Tujuan, batasan, dan larangan](#1-tujuan-batasan-dan-larangan)
2. [Lima prinsip yang terbukti](#2-lima-prinsip-yang-terbukti)
3. [Parameter naskah yang ditetapkan sebelum mulai](#3-parameter-naskah-yang-ditetapkan-sebelum-mulai)
4. [Kosakata yang dihindari](#4-kosakata-yang-dihindari)
5. [Pola kalimat yang dihindari](#5-pola-kalimat-yang-dihindari)
6. [Pola paragraf dan wacana yang dihindari](#6-pola-paragraf-dan-wacana-yang-dihindari)
7. [Kalimat yang tidak diperlukan](#7-kalimat-yang-tidak-diperlukan)
8. [Kesalahan penulisan yang sering muncul](#8-kesalahan-penulisan-yang-sering-muncul)
9. [Aturan gaya IEEE yang relevan untuk revisi](#9-aturan-gaya-ieee-yang-relevan-untuk-revisi)
10. [Fakta, angka, sitasi, dan klaim](#10-fakta-angka-sitasi-dan-klaim)
11. [Teknik revisi yang efektif](#11-teknik-revisi-yang-efektif)
12. [Alur kerja langkah demi langkah](#12-alur-kerja-langkah-demi-langkah)
13. [Pemeriksaan mekanis (tanpa skrip proyek)](#13-pemeriksaan-mekanis-tanpa-skrip-proyek)
14. [Cara melapor dan menyajikan revisi](#14-cara-melapor-dan-menyajikan-revisi)
15. [Integritas dan kebijakan IEEE](#15-integritas-dan-kebijakan-ieee)
16. [Daftar cek akhir](#16-daftar-cek-akhir)
17. [Log pola detektor](#17-log-pola-detektor)
- [Lampiran A. Contoh profil naskah (StaticKD)](#lampiran-a-contoh-profil-naskah-statickd)
- [Sumber](#sumber)

---

## 0. Mulai cepat untuk agent

Baca bagian 1–3 sekali sebelum menyentuh teks. Setelah itu, setiap tugas revisi mengikuti urutan ini:

1. **Tetapkan parameter naskah** (bagian 3). Kalau ada yang belum diketahui, tanyakan ke pengguna.
2. **Kunci fakta:** catat angka, sitasi, rujukan silang, dan simbol yang wajib tetap sama (bagian 10).
3. **Tentukan cakupan.** Kalau pengguna membawa hasil detektor, ubah **hanya** kalimat yang ditandai (bagian 2, prinsip 1–2). Kalau tugasnya review gaya, baca seluruh naskah dulu.
4. **Usulkan dulu, terapkan setelah disetujui** (bagian 12, langkah 4–6).
5. **Verifikasi dua kali:** pass makna, lalu pass gaya (bagian 12, langkah 7).
6. **Jalankan pemeriksaan mekanis** (bagian 13).
7. **Laporkan** dalam format before/after yang ringkas (bagian 14).

---

## 1. Tujuan, batasan, dan larangan

**Tujuan.** Tulisan yang **memang** terbaca sebagai tulisan peneliti: spesifik, jujur, punya alasan, dan dapat diverifikasi. Detektor AI menandai teks yang mudah ditebak. Ciri-cirinya adalah pilihan kata paling umum, ritme kalimat yang seragam, kerangka wacana bertemplat, dan isi yang generik. Revisi yang efektif menghilangkan ciri-ciri itu dengan **menambah isi dan mengubah struktur**, bukan dengan menyamarkan teks.

**Batas detektor.**
- Detektor bersifat probabilistik. Liang et al. (2023, *Patterns*) mencatat rata-rata *false positive* 61,3% pada esai TOEFL, karena detektor bias terhadap penulis non-native English.
- Lolos di satu detektor tidak menjamin lolos di detektor lain.
- Potongan pendek yang padat angka (misalnya 2–4 kalimat hasil uji statistik) memberi skor yang tidak stabil. Uji per paragraf atau per bagian.
- Teks yang disalin dari PDF sering kehilangan spasi ("thedataare"). Rapikan dulu sebelum diuji.
- **Tidak ada teknik yang menjamin 0% terdeteksi.** Yang bisa dijamin hanyalah teks yang spesifik dan bebas dari pola di file ini.

**Dilarang**, karena tidak etis dan juga merugikan naskah:
- Sengaja menyisipkan salah ketik atau tata bahasa yang salah. IEEE Access langsung menolak naskah dengan tata bahasa buruk.
- Karakter tersembunyi, homoglyph, atau spasi aneh.
- Alat *spinner* atau *humanizer* yang mengganti kata secara acak, atau kata langka yang mengubah makna.
- Mengubah angka, menghapus sitasi, atau melemahkan klaim yang sudah didukung bukti, hanya supaya lolos detektor.
- Menghapus atau melewatkan pernyataan penggunaan AI di Acknowledgment (bagian 15).

---

## 2. Lima prinsip yang terbukti

Prinsip ini berasal dari kejadian nyata saat merevisi naskah bersama pengguna.

1. **Ubah sesedikit mungkin.** Ubah hanya kalimat yang ditandai detektor atau yang memang salah. Kalimat lain dibiarkan persis seperti tulisan penulis.
   - *Kasus:* pengguna meminta satu paragraf yang "natural dan lolos detektor". Agent menulis ulang seluruh paragraf, dan skor detektor justru **memburuk**. Teks yang dipoles model bahasa makin mirip teks model bahasa.
   - *Yang akhirnya diterima:* dua kalimat yang ditandai diganti, dua kalimat lain tetap utuh.
2. **Jangan menebak kalimat mana yang terdeteksi.** Minta sorotan dari detektor pengguna.
   - *Kasus:* agent menilai kalimat "…, so hard labels work as well as soft labels" berisiko tinggi. Ternyata detektor hanya menandai kalimat berawalan "When …" dan kalimat sesudahnya. Tebakan berdasarkan pola bisa salah.
3. **Teks buatan agent tetap teks AI.** Tidak ada versi yang dijamin lolos. Kalau teks agent dipakai apa adanya, pernyataan penggunaan AI di Acknowledgment harus mencakupnya. Sampaikan hal ini sekali dan singkat.
4. **Jangan menambah tafsiran supaya kalimat terdengar alami.** Setiap tafsiran baru adalah klaim baru.
   - *Kasus:* "Data size matters little" hanya benar untuk macro-F1 test. Pada varian yang sama, skor development dan agreement turun signifikan. Tafsiran harus dicek ke **semua** metrik yang dilaporkan.
5. **Usulkan dulu, baru terapkan.** Untuk review atau perubahan gaya, tampilkan usulan beserta nomor baris, lalu tunggu persetujuan. Terapkan hanya nomor yang disetujui.

---

## 3. Parameter naskah yang ditetapkan sebelum mulai

Setiap naskah punya keputusan gaya sendiri. Tetapkan parameter berikut sebelum menulis. Kalau belum ada, tanyakan ke pengguna. Contoh lengkapnya ada di Lampiran A.

| Parameter | Pertanyaan | Contoh nilai |
|---|---|---|
| Venue target | Jurnal atau konferensi apa? Template apa? | IEEE Access, template IEEEtran |
| Bahasa naskah | Inggris, Indonesia, atau keduanya? Siapa yang menerjemahkan? | Inggris; penulis menulis ulang sendiri |
| Kata ganti orang | Boleh "we/our/kami"? | Tidak boleh; tanpa subjek orang (*I, you, we, they*) |
| Batas abstrak | Berapa kata? | 150–250 kata, satu paragraf |
| Gaya rujukan | Paper mana yang dijadikan contoh gaya? | Dua paper dari pembimbing atau venue target |
| Sumber angka | File atau notebook mana yang menjadi sumber kebenaran angka? | Keluaran notebook eksperimen |
| Format angka | Desimal titik atau koma? Pemisah ribuan? | Desimal titik; 285,999 |
| Bagian yang tidak boleh ditimpa | Paragraf mana yang sudah ditulis pengguna sendiri? | Daftar ID blok dari pengguna |
| File yang boleh diedit | Naskah utama, lembar parafrase, atau hanya chat? | Diedit hanya bila diminta |
| Pernyataan AI | Apa isi Acknowledgment saat ini tentang AI? | "reviewing and minor editing" |

### 3.1 Cara memakai paper rujukan gaya

1. Pilih 1–2 paper dari venue target atau dari pembimbing.
2. Hitung ciri-ciri berikut di keduanya, lalu jadikan aturan naskah. Contoh hitungan pada dua paper rujukan (±12.000 dan ±13.000 kata):

| Ciri | Paper rujukan 1 | Paper rujukan 2 | Aturan yang diturunkan |
|---|---|---|---|
| "we/our/us" | 0 | 0 | Tidak ada kata ganti orang pertama |
| "This study/paper/work …" | 10 | 30 | Dipakai untuk tujuan, usulan, RQ, kontribusi |
| "aims to" | 0 | 6 | Boleh ("This study aims to …") |
| "In terms of" | 3 | 1 | Boleh, sesekali |
| "Furthermore" | 11 | 2 | Transisi boleh, asal tidak menumpuk |
| em-dash | 1 | 6 | Hindari |

3. Catat juga kebiasaan lainnya. Contohnya "Let X denote …" untuk notasi, pasif pendek untuk langkah teknis, dan alasan yang selalu disebut untuk setiap pilihan metode.

### 3.2 Menulis tanpa "we" tanpa membuat teks kaku

Campurkan bentuk-bentuk ini:
- **Subjek "this study/this paper":** untuk usulan, RQ, dan kontribusi.
- **Subjek benda yang aktif:** "Internal validation uses 3% …", "The evaluation also reports …".
- **Pasif pendek:** untuk langkah teknis ("Each process is pinned …").
- **Frasa impersonal:** untuk dugaan dan saran ("A plausible explanation is …").
- **Batas pasif:** paling banyak tiga kalimat pasif berturut-turut.
- **"They" sebagai subjek kalimat** juga dihindari bila parameter naskah melarang subjek orang. Ganti dengan nama bendanya.

Istilah teknis tetap dalam bahasa Inggris (teacher, student, distillation, macro-F1, dan seterusnya), juga di naskah berbahasa Indonesia. Singkatan didefinisikan saat pertama muncul.

---

## 4. Kosakata yang dihindari

Frekuensi kata-kata ini melonjak sejak LLM banyak dipakai:
- Kobak et al. (*Science Advances*, 2025) menganalisis lebih dari 15 juta abstrak PubMed.
- Liang et al. (ICML 2024) mencatat bahwa di review ICLR 2024, "commendable" naik 9,8×, "meticulous" 34,7×, dan "intricate" 11,2×.

Kata-kata ini hanya boleh dipakai kalau maknanya benar-benar tepat dan tidak ada padanan yang lebih sederhana.

**Bahasa Inggris:** delve, intricate, pivotal, underscore, showcase, leverage (sebagai kata kerja umum), seamless, robust (tanpa uji robustness), comprehensive, meticulous, commendable, notably, multifaceted, paramount, landscape, realm, tapestry, shed light on, pave the way, a testament to, harness, unlock, elevate, crucial (role), game-changer, cutting-edge, groundbreaking, in today's fast-paced world, it is worth noting that, novel/new (di judul; aturan IEEE).

**Bahasa Indonesia:**

| Hindari | Ganti dengan |
|---|---|
| "memainkan peran krusial/penting" | sebutkan perannya secara langsung |
| "menyoroti", "menggarisbawahi" | "menunjukkan", atau langsung sebut temuannya |
| "lanskap penelitian" | "penelitian tentang X" |
| "komprehensif", "holistik" | sebutkan cakupannya (mis. "17 label, 47 bahasa") |
| "memberikan wawasan berharga" | sebutkan wawasannya |
| "membuka jalan bagi" | "memungkinkan X", atau hapus |
| "secara signifikan" | hanya bila ada uji statistik; sertakan p atau CI |
| "inovatif", "mutakhir", "revolusioner" | hapus; biarkan hasil yang berbicara |
| "sangat efektif", "sangat efisien" | angka: "macro-F1 0.545", "34 MB", "473 dok/s" |
| "mulus" (seamless), "tangguh" (robust) | jelaskan kondisi ujinya |
| "di era digital saat ini" | hapus; mulai langsung dari masalah |
| "perlu dicatat bahwa", "penting untuk dicatat bahwa" | hapus; tulis faktanya saja |

---

## 5. Pola kalimat yang dihindari

Satu kemunculan belum tentu salah. Yang terdeteksi adalah **penumpukan** pola.

### 5.1 Ritme dan struktur umum

- Panjang kalimat seragam. Campur kalimat pendek dengan kalimat panjang yang membawa detail.
- ★ Kalimat pendek yang sejajar dan seimbang, berderet-deret. Kalau semua kalimat dipotong sama pendek, itu juga pola.
- Pola tiga hal yang berulang ("efisien, akurat, dan skalabel"). Sebut jumlah yang memang ada.
- "Tidak hanya X, tetapi juga Y", "Bukan sekadar X, melainkan Y", "not only … but also". Paling banyak sekali di seluruh naskah, lebih baik tidak sama sekali.
- Kata transisi di awal kalimat (Selain itu, Lebih lanjut, Dengan demikian, Oleh karena itu, Furthermore, Moreover, Additionally, Therefore, However) paling banyak satu per paragraf.
- Em-dash (—) tidak dipakai. Titik dua dan titik koma dipakai seperlunya. Lebih baik pakai titik dan kalimat baru.
- Pertanyaan retoris ("Namun, bagaimana jika …?").

### 5.2 ★ Rangkaian klausa yang disambung koma

Pola paling sering ditandai adalah **kalimat yang masing-masing berisi 2–4 klausa yang disambung koma, lalu diulang di beberapa kalimat berturut-turut**:
- "X, so Y"
- "When X, Y"
- "X, and Y" atau ", and on …" di ekor kalimat
- "X, which Y"

Satu kemunculan biasanya tidak ditandai. Pada kasus nyata, kalimat "…, so hard labels work as well as soft labels" lolos, sedangkan dua kalimat sesudahnya yang ditandai.

Cara memecahnya tanpa membuat semua kalimat pendek:
- **Satu klausa per kalimat**, dengan objek ganda yang disambung "and" tanpa koma: "change it by +0.005 and the development score by −0.006".
- **Kesimpulan menjadi kalimat sendiri:** "Hard labels therefore work as well as soft labels."
- **Klausa "When X," diganti subjek gerund:** "Reducing the data to X lowers …".
- **Gapping:** kata kerja kedua dihilangkan ("… gives +0.001 and an MLP head +0.009").
- **Tetap variasikan panjang kalimat.**

### 5.3 ★ Kerangka pelaporan hasil

Kalimat asli yang ditandai:

> When the data are reduced to 130 thousand documents, the test macro-F1 shifts by −0.002 (p=1.000). The difference is +0.001 (p=1.000) when token dropout is removed and +0.009 (p=0.281) with an MLP head that cannot be folded.

Ciri-cirinya:
- klausa syarat "When X," di depan, disambung koma ke klausa utama;
- pasif di dalam klausa syarat ("are reduced");
- kata kerja netral (*shifts, moves, changes, is*) diikuti angka bertanda;
- subjek tiruan "The difference is …" yang dipakai untuk beberapa hasil sekaligus;
- keterangan yang tidak sejajar ("when …" dan "with …");
- frasa metrik ("test macro-F1") diulang di setiap kalimat.

Perbaikan yang **diterima** pengguna:

> Reducing the data to 130 thousand documents lowers the test score by 0.002 (p=1.000). Removing token dropout gives +0.001 (p=1.000) and an MLP head that cannot be folded +0.009 (p=0.281).

- Aksi dijadikan subjek, jadi kalimatnya satu klausa tanpa koma.
- Kata kerja berarah (*lowers, raises, halves, matches*). Tanda minus dibuang karena arahnya sudah ada di kata kerja (bagian 8, butir 1).
- Dua subjek sejajar, dengan kata kerja kedua dihilangkan.
- **Variasikan bentuknya.** Kalau setiap hasil ditulis "Gerund … lowers …", itu menjadi templat baru yang juga terdeteksi.

### 5.4 ★ Kerangka lain yang terdeteksi

- **Kerangka enumerasi:** "… seeks X that satisfies two requirements. The first requirement concerns cost. … The second requirement concerns accuracy."
    - Lipat syarat-syarat itu ke dalam satu atau dua kalimat yang lebih panjang.
    - Jangan memakai "first/second" kecuali sumbernya memang berupa daftar.
- **Dua glos dalam satu paragraf**, misalnya "that is, one score for each topic" ditambah "i.e., labels that do not come from the teacher". Paling banyak satu glos per paragraf.
- **Kalimat yang mengulang klaim sebelumnya** dengan kata lebih sederhana ("so the number of operations grows in proportion to the article length"). Hapus.
- **Aposisi di dalam subjek** ("The teacher, an XLM-R model with …, labels …").
- **Banyak kalimat diawali "This …"/"These …"** secara beruntun.

### 5.5 ★ Translationese Indonesia → Inggris

- "yang merupakan" diterjemahkan menjadi "which is", dan "serta" menjadi "as well as/and", di setiap kalimat.
- "Hal ini …" diterjemahkan menjadi "This …" sebagai pembuka kalimat beruntun.
- Nominalisasi dari "dilakukan" ("Evaluation is carried out on …"). Pakai kata kerja langsung: "The evaluation uses …".

---

## 6. Pola paragraf dan wacana yang dihindari

- Semua paragraf berpola sama: kalimat topik, tiga poin, kalimat kesimpulan.
- Paragraf ditutup kalimat rangkuman ("Secara keseluruhan, …", "Overall, …", "Hal ini menunjukkan pentingnya …"). Akhiri dengan fakta atau implikasi yang spesifik.
- Penanda arah tanpa isi ("Pada bagian ini akan dibahas …"). Cukup satu kalimat peta di akhir Pendahuluan.
- Gagasan yang sama diulang dengan kata lain di paragraf yang sama.
- Hedging berlapis ("berpotensi dapat mungkin meningkatkan"). Satu tingkat hedging saja, dan hanya bila memang tidak pasti.
- Nada yang selalu positif dan seimbang. Sebut kelemahan dengan tegas dan spesifik.
- Klaim umum tanpa rujukan atau angka ("model transformer sangat populer").
- Satu paragraf membahas dua topik.
- Istilah dipakai sebelum didefinisikan.
- Angka disajikan tanpa kesimpulan. Bagian validasi yang hanya berisi akurasi, uji, dan korelasi tanpa kalimat "jadi label X tidak lebih buruk dari Y" membuat pembaca menarik kesimpulan sendiri.
- Alasan sebuah pilihan tidak disebut. Contohnya: kenapa label uji tidak boleh berasal dari teacher, atau kenapa set tertentu tidak dipakai untuk hasil.
- Tidak ada peta data. Kalau naskah memakai banyak set data dengan peran berbeda (training, validasi, development, held-out, uji, set cek), jelaskan peran semuanya di satu tempat, misalnya satu tabel.

---

## 7. Kalimat yang tidak diperlukan

Buang kalimat yang tidak menambah informasi dan tidak memperjelas. Jenis yang ditemukan pada review naskah nyata:

| Jenis | Contoh | Alasan dibuang |
|---|---|---|
| Penanda arah yang isinya diulang di kalimat penutup | "Existing options fall short of this." (penutupnya: "No available IPTC classifier is both multilingual and this cheap.") | Penutup sudah menyatakannya dengan lebih spesifik |
| Penegasan ulang dalam satu paragraf | "This is a one-time cost." setelah "Labeling ran once" | Informasinya sudah ada |
| Fakta yang sudah tersirat dari nama | "The two periods do not overlap" untuk data 2019–2021 dan 2024–2026 | Tahunnya sudah eksplisit |
| Gagasan yang sama di banyak bagian | "absolute scores read as agreement with the publisher categorization" muncul 4 kali (Metode, Hasil, Diskusi, Limitasi) | Pertahankan di tempat yang paling cocok, buang sisanya |
| Kalimat rangkuman di penutup paragraf | "Sending about two fifths of the articles to the teacher is enough to match the teacher" | Bisa diturunkan dari angka sebelumnya, dan Diskusi sudah menyatakannya |
| Penunjuk ke bagian lain | "Section V discusses the mechanism behind this pattern." | Bagian itu langsung menyusul |
| Tautologi | "is not public, so it was not available for this study" | Cukup "is not public" |
| Kalimat yang hanya membawa sitasi | "A recent survey covers the development of KD [x]." | Pindahkan sitasinya ke kalimat definisi |
| Kalimat tanpa makna | "Int8 quantization only gives a constant-factor speed-up" (padahal 616× juga faktor konstan) | Tidak membedakan apa pun |

**Jangan dibuang** walaupun tampak berulang:
- **Pengulangan yang perannya berbeda di tiap bagian.** Contoh: "no model reads the article" sebagai motivasi di Pendahuluan dan sebagai definisi di Metode.
- **Daftar atau angka yang menopang argumen di Diskusi.** Contoh: daftar label dengan gap terbesar dipakai untuk membuktikan letak gap.
- **Kalimat framing pendek yang membantu pembaca** ("Parts of both are still covered."). Tandai sebagai **opsional**, jangan langsung dibuang.

---

## 8. Kesalahan penulisan yang sering muncul

| # | Kesalahan | Contoh salah | Perbaikan |
|---|---|---|---|
| 1 | Negatif ganda: kata kerja turun + angka bertanda minus | "lowers the test macro-F1 by −0.051"; "is below the teacher by −0.053" | "lowers … by 0.051". Kalau CI-nya bertanda, pakai bentuk netral: "Δmacro-F1 is −0.053 [−0.065, −0.033]" |
| 2 | Preposisi | "its difference to X" | "the difference from X" |
| 3 | Proporsi dan persen dicampur | "agrees on 0.811 of the documents"; "only 0.45 of … articles, with conflict (29%)" | "81.1% of the documents"; "45%" |
| 4 | Rujukan ambigu setelah kalimat yang menyebut himpunan sebaliknya | "at most 32% … come from tokens seen at least 10 times. … removes **those tokens**" (yang dimaksud token yang jarang) | Ubah kalimat sebelumnya ke himpunan yang dirujuk: "at least 68% … fewer than 10 times … removes these rare tokens" |
| 5 | Singkatan dari gambar dipakai di prosa; format label tidak konsisten | "human int.", daftar dipisah titik koma, label tidak dimiringkan | "human interest", koma + "and", format sama dengan bagian lain; "(20% each)" untuk angka yang sama |
| 6 | Penghubung sebab yang tidak bersebab | "As a result, the only open classifier is … and no inexpensive classifier has been evaluated" | Hapus "As a result," |
| 7 | Generalisasi yang dibantah kalimat berikutnya | "All baselines are trained with targets from the same teacher", lalu disebut baseline berlabel GPT-4o | "All baselines marked + KD …" |
| 8 | Istilah yang bertentangan dengan protokol | "students should be selected … with test data" (padahal tidak ada pemilihan memakai test set) | "with a development set outside the training distribution" |
| 9 | Kalimat topik yang tidak cocok dengan contohnya | "move … in opposite directions", padahal salah satu contoh tidak berlawanan arah | "Agreement with the teacher does not always predict accuracy on editorial labels." |
| 10 | Urutan waktu yang tidak logis | "Before deployment, accuracy should be monitored" | "During deployment" |
| 11 | Notasi p | "($p$ 0.004)", "$p$ $<$0.001" | "$p=0.004$", "$p<0.001$". Header tabel ("$p$ bootstrap") tidak diubah |
| 12 | Kata kerja tidak sejajar dalam daftar | "… when token dropout is removed and … with an MLP head" | Dua subjek sejajar dengan kata kerja yang sama |
| 13 | Panjang abstrak melebihi batas | 311 kata, padahal batasnya 250 | Padatkan kalimat dulu. Kalau masih lebih, bagian isi yang dibuang adalah keputusan penulis |
| 14 | Kalimat diawali nama produk berhuruf kecil | "fastText trained only on …" sebagai awal kalimat | Susun ulang: "Without teacher labels (last two rows), fastText trained only on …" |

---

## 9. Aturan gaya IEEE yang relevan untuk revisi

Ringkasan dari IEEE Editorial Style Manual [SM], IEEE Reference Style Guide [RG, V 3.28.2025], IEEE Editing Mathematics [MG], IEEE Author Center [AC], dan IEEE Access [IA]. Untuk venue lain, cek aturannya sendiri.

### 9.1 Isi tiap bagian
- **Judul:** spesifik, ringkas, deskriptif. Tanpa "new/novel" dan tanpa simbol matematika [AC].
- **Abstrak:** satu paragraf, 150–250 kata [SM] ("up to 250 words" [AC]). Tanpa persamaan bernomor, sitasi, atau catatan kaki. Singkatan didefinisikan bila dipakai. Merangkum riset, kesimpulan, implikasi, dan apa yang baru.
- **Index Terms:** 3–5 istilah baku [AC], urut alfabetis, hanya kata pertama kapital kecuali istilah yang memang kapital [SM].
- **Introduction:** tempatkan riset di literatur, tunjukkan kebaruan, jelaskan pertanyaan riset [AC].
- **Metode:** cukup rinci untuk direproduksi [AC].
- **Results** melaporkan; **Discussion** menjelaskan arti [AC].
- **Conclusion:** boleh menyebut implikasi luas, tetapi jangan membesar-besarkan temuan [AC].
- **Acknowledgment:** dieja "Acknowledgment", tanpa nomor, orang ketiga. Dana ditulis di catatan kaki pertama, bukan di sini [SM].

### 9.2 Bahasa
- Ejaan Amerika (behavior, center); tanpa kontraksi (do not, cannot) [SM].
- "Data" jamak ("The data were"); "a series of" tunggal [SM].
- **That vs which:** klausa pembatas memakai "that" tanpa koma; klausa tidak membatasi memakai "which" dengan koma [SM].
- Serial comma sebelum "and/or" dalam deret tiga unsur atau lebih [SM].
- "i.e.," dan "e.g.," diikuti koma [SM].
- Titik koma menghubungkan dua klausa bebas tanpa kata sambung [SM].
- Kata yang sering tertukar: affect/effect, compare to/compare with, compose/comprise, fewer/less, imply/infer, number/amount, principal/principle [SM].
- Pengubah majemuk diberi tanda hubung bila di depan kata benda ("a 34-MB model"). Kata keterangan "-ly" tidak diberi tanda hubung [SM].
- En dash (–) untuk rentang ("2019–2021"). Bila memakai "from", pasangannya "to" [SM].

### 9.3 Akronim, angka, satuan
- Akronim didefinisikan saat pertama muncul di abstrak **dan** di badan naskah [SM]. Bentuk jamak tanpa apostrof (GPUs) [SM].
- Angka bersama satuan selalu berupa digit. Angka di bawah 11 tanpa satuan dieja ("four languages") [SM].
- Desimal memakai titik dengan nol di depan (0.25) [SM].
- Persen dengan simbol, diulang dalam rentang ("20%–30%") [SM].
- Spasi di antara angka dan satuan ("34 MB") [SM].
- Tanggal: "4 June 2002" [SM].

### 9.4 Persamaan, rujukan silang, sitasi
- Persamaan adalah bagian kalimat dan diberi tanda baca. Rujuk dengan "(1)"; kata "Equation" hanya di awal kalimat [SM], [MG].
- "Section II-A" (tanpa "Subsection"), "Fig. 1" (selalu disingkat), tabel bernomor Romawi [SM].
- Caption tabel tidak diakhiri titik [SM].
- Sitasi dalam kurung siku dan boleh dipakai sebagai kata benda ("as shown in [4]"). Tulis "in [1]", bukan "in reference [1]" [SM], [RG].
- **Rentang sitasi tidak lagi memakai en dash:** "[1]–[4]" ditulis "[1], [2], [3], [4]" [RG V 3.28.2025]. Di LaTeX, pakai `\usepackage[nocompress]{cite}`.
- Satu nomor untuk satu referensi. Dataset dan perangkat lunak juga dikutip (penulis, tahun, versi, penerbit, DOI/URL) [RG].
- Kutip hanya sumber yang langsung mendukung klaim; sitasi berlebihan adalah pelanggaran etika [AC].

### 9.5 Daftar
- Daftar hanya untuk RQ, kontribusi, dan langkah prosedur. Bagian prosa (Pendahuluan, Penelitian Terkait, Hasil, Pembahasan) tidak memakai bullet.
- Unsur daftar sejajar secara tata bahasa. Daftar frasa memakai huruf kecil, titik koma, dan titik di akhir; daftar kalimat lengkap memakai huruf kapital dan titik [SM].

---

## 10. Fakta, angka, sitasi, dan klaim

### 10.1 Kunci fakta sebelum menulis ulang
Untuk setiap paragraf, catat item yang wajib muncul lagi persis sama:
- **angka** apa adanya (0.545, 2,971, 91.1%);
- **sitasi** beserta klaim yang ditopangnya (nomor sitasi tetap menempel pada klaim yang sama);
- **rujukan silang** (Table IV, Fig. 3, Section III-D);
- **simbol** (τ=1, θ) dan **nama** model atau dataset.

Setelah menulis ulang, cocokkan teks baru dengan daftar itu satu per satu.

### 10.2 Klaim saat merapikan gaya
- **Kekuatan klaim harus tetap sama.** Penulisan ulang tidak boleh menguatkan atau melemahkan klaim tanpa data.
- **Melemahkan klaim butuh bukti setara dengan membuat klaim.** Uji di metrik utama, baca sumber yang dikutip, dan tandai spekulasi sebagai spekulasi.
- **Urutan atau peringkat harus sesuai metrik utama.**
  - *Kasus:* Diskusi menyebut data sebagai "the largest source" dan inisialisasi "comes next". Pada macro-F1 test (metrik utama), menghapus inisialisasi menurunkan skor 0.120, sedangkan menghapus data menurunkan 0.051. Held-out agreement menunjukkan arah sebaliknya (−0.069 dan −0.077).
  - Laporkan **kedua metrik** dan minta penulis memutuskan. Jangan memilih sendiri.
- **Inkonsistensi klaim antarbagian** dilaporkan sebagai temuan "di luar gaya", bukan diperbaiki diam-diam.

### 10.3 Ciri khusus paper yang wajib dihindari
- **Sitasi halusinasi:** paper yang tidak ada, DOI salah, atau tahun/venue/penulis keliru. IEEE Access langsung menolak konten fabrikasi. Prosedur pengecekannya ada di bagian 13.4.
- **Sitasi yang tidak mendukung klaim.** Jangan mengutip paper hanya karena judulnya cocok. Baca bagian yang relevan dari PDF-nya.
- **Angka yang tidak konsisten** antara abstrak, teks, tabel, dan gambar. Ambil angka dari sumber kebenaran (bagian 3), bukan dari ingatan. Prosedurnya ada di bagian 13.3.
- **Kontribusi generik** ("a new framework that significantly improves performance"). Tulis: metode apa, dibandingkan baseline apa, naik berapa, pada data apa.
- **Tinjauan pustaka berupa daftar ringkasan** ("A et al. did X. B et al. did Y."). Kelompokkan per pendekatan, bandingkan, lalu tunjukkan celahnya.
- **Limitasi dan saran yang klise** ("future work could use larger datasets"). Tulis limitasi spesifik untuk studi itu beserta konsekuensinya.
- **"To the best of our knowledge"** paling banyak sekali, dan hanya untuk klaim kebaruan yang sudah dicek ke literatur.
- **Detail teknis yang hilang:** hyperparameter, seed, hardware (CPU, jumlah thread), ukuran tiap split.
- **Artefak keluaran LLM:** "Certainly! Here is …", "As an AI language model", "[insert citation]", "[citation needed]", "as of my knowledge cutoff", "Berikut adalah …", placeholder "XX", atau "TODO".

---

## 11. Teknik revisi yang efektif

Diurutkan dari yang paling berdampak:

1. **Ubah sesedikit mungkin** (bagian 2, prinsip 1). Teks penulis yang tidak ditandai adalah aset, bukan bahan poles.
2. **Tambahkan hal yang hanya diketahui penulis:** alasan memilih metode, eksperimen yang gagal, batasan nyata (hardware, waktu), dan hasil yang mengejutkan. Tanyakan ke penulis; jangan mengarang. Detail seperti ini tidak bisa ditebak model bahasa.
3. **Mulai dari temuan atau angka, bukan dari kerangka.** "StaticKD keeps 91.1% of the teacher's test macro-F1 and classifies 473 articles per second per core" lebih baik daripada "This section presents the results of …".
4. **Lipat enumerasi** menjadi satu atau dua kalimat panjang dengan anak kalimat.
5. **Hapus kalimat yang tidak menambah informasi baru** (bagian 7).
6. **Ganti kata umum dengan istilah domain yang tepat:** "site-cluster bootstrap", bukan "a robust statistical method".
7. **Variasikan ritme sesuai isi.** Kalimat pendek untuk temuan utama; kalimat panjang untuk prosedur dan syaratnya.
8. **Untuk laporan hasil,** pakai aksi sebagai subjek, kata kerja berarah, dan elipsis untuk deret angka (bagian 5.3).
9. **Variasikan setiap perbaikan.** Pengganti yang sama, bila dipakai berulang, menjadi templat baru yang juga terdeteksi.
10. **Kalau pengguna menulis sendiri,** beri arahan, bukan kalimat jadi: tulis seperti menjelaskan ke teman satu lab lalu rapikan tata bahasanya, hindari cetakan yang diulang, masukkan alasan yang dipahami, dan jangan memoles berlebihan.

---

## 12. Alur kerja langkah demi langkah

1. **Tetapkan parameter naskah** (bagian 3).
2. **Baca seluruh teks dulu**, termasuk tabel dan caption, sebelum menilai redundansi. Banyak pengulangan baru terlihat lintas bagian.
3. **Kunci fakta** (bagian 10.1).
4. **Susun usulan dalam enam kelompok:**
   1. kesalahan penulisan;
   2. kalimat yang bisa dibuang;
   3. penggabungan kalimat;
   4. opsional;
   5. di luar gaya, perlu keputusan penulis (klaim, peringkat, isi yang dibuang dari abstrak);
   6. sengaja tidak disentuh, beserta alasannya.

   Setiap butir memuat nomor baris, teks lama, teks usulan, dan alasan satu kalimat.
5. **Tunggu persetujuan.** Pengguna bisa memilih kelompok atau nomor tertentu.
6. **Terapkan hanya yang disetujui.** Waspadai jebakan edit:
   - Menghapus kalimat di **akhir paragraf** dengan alat edit (teks pengganti kosong) bisa ikut menghapus baris kosong sesudahnya. Di LaTeX, dua paragraf jadi menyatu. Lakukan pengecekan di bagian 13.2.
   - Saat mengganti teks massal lewat skrip, pertahankan akhir baris (CRLF/LF). Di Python, baca dan tulis dengan `newline=''`.
   - Penggantian massal (misalnya notasi p) jangan mengenai header tabel. Batasi pola ke konteks yang tepat.
7. **Verifikasi dua kali sebelum ditulis ke file atau dilaporkan:**
   - **Pass makna:** bandingkan dengan teks asli. Periksa klaim, angka, penekanan, kausalitas, dan pelaku. Contoh kesalahan lama: kata "hanya" ditambahkan, atau pelaku tertukar.
   - **Pass gaya:** periksa terhadap bagian 4–8. Sebaiknya dilakukan oleh verifier independen, bukan oleh penulis teks itu sendiri.
   - Laporkan apa yang diubah oleh setiap pass.
8. **Jalankan pemeriksaan mekanis** (bagian 13). Setiap temuan tetap dinilai manual, karena pemindai hanya saringan pertama.
9. **Kompilasi salinan** naskah di folder sementara. Pastikan 0 error, tidak ada referensi atau sitasi yang tidak ditemukan, dan jumlah kata abstrak sesuai batas.
10. **Perbarui file turunan** (lembar parafrase, terjemahan, daftar fakta) yang dibuat dari naskah:
    - Kalau isi file turunan dikunci per ID blok berurutan (PEN-01, MET-02, …), ID akan **bergeser** begitu ada paragraf baru. Cocokkan blok lama dan baru berdasarkan **teks**, bukan ID.
    - Bawa terjemahan atau catatan hanya untuk teks yang identik. Tulis ulang sisanya.
    - Buang catatan review yang masalahnya sudah diperbaiki.
    - Pastikan isian yang sudah ditulis penulis tetap menempel di paragraf yang benar.
11. **Uji per paragraf di detektor pengguna.** Pola yang masih ditandai dicatat di bagian 17.
12. **Laporkan apa adanya** (bagian 14), termasuk kesalahan agent sendiri dan cara memperbaikinya.

---

## 13. Pemeriksaan mekanis (tanpa skrip proyek)

### 13.1 Pemindai gaya

Simpan sebagai `scan_style.py` di folder sementara, lalu jalankan `python scan_style.py naskah.tex`. Pemindai ini berlaku untuk LaTeX maupun teks biasa. Hasilnya daftar temuan per paragraf dan statistik panjang kalimat; setiap temuan tetap dinilai manual.

```python
"""Pemindai gaya sederhana untuk naskah LaTeX atau teks biasa. Pakai: python scan_style.py naskah.tex"""
import re
import statistics
import sys

WORDS = ["delve", "intricate", "pivotal", "underscore", "showcase", "leverag", "seamless", "robust", "comprehensive",
         "meticulous", "commendable", "notably", "multifaceted", "paramount", "landscape", "realm", "tapestry",
         "shed light", "pave the way", "testament", "harness", "unlock", "elevate", "crucial", "game-changer",
         "cutting-edge", "groundbreaking", "fast-paced", "worth noting", "novel",
         "memainkan peran", "peran krusial", "menyoroti", "menggarisbawahi", "lanskap", "komprehensif", "holistik",
         "wawasan berharga", "membuka jalan", "inovatif", "mutakhir", "revolusioner", "sangat efektif",
         "sangat efisien", "era digital", "perlu dicatat", "penting untuk dicatat"]
TRANSITIONS = ["Furthermore", "Moreover", "Additionally", "Therefore", "However", "Selain itu", "Lebih lanjut",
               "Dengan demikian", "Oleh karena itu", "Namun demikian", "Di sisi lain"]
CLOSERS = ["Overall", "In summary", "In conclusion", "Secara keseluruhan", "Kesimpulannya", "Singkatnya"]
ARTEFACTS = ["Certainly", "As an AI", "insert citation", "citation needed", "knowledge cutoff", "Berikut adalah",
             "TODO", "XX"]

raw = open(sys.argv[1], encoding="utf8").read()
text = re.sub(r"(?<!\\)%.*", "", raw)  # komentar LaTeX
text = re.sub(r"\\begin\{(table\*?|figure\*?|equation|align|algorithm|tikzpicture)\}.*?\\end\{\1\}", " ", text, flags=re.S)
text = re.sub(r"\\(emph|textit|texttt|textbf|url)\{([^{}]*)\}", r"\2", text)
text = re.sub(r"\\(cite|ref|eqref|label)\{[^}]*\}", "", text)
text = re.sub(r"\$[^$]*\$", "X", text)
paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.split()) > 8]


def sentences(par):
    par = re.sub(r"\b(e\.g|i\.e|et al|Fig|vs|No|dkk|mis)\.", lambda m: m.group(0).replace(".", "~"), par)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", par) if len(s.split()) > 2]


lengths = []
for i, par in enumerate(paragraphs, 1):
    sents = sentences(par)
    lengths += [len(s.split()) for s in sents]
    hits = []
    low = par.lower()
    hits += [f"kata '{w}'" for w in WORDS if re.search(r"\b" + re.escape(w), low)]
    starts = [s.split()[0] for s in sents if any(s.startswith(t) for t in TRANSITIONS)]
    if len(starts) > 1:
        hits.append(f"{len(starts)} kalimat diawali transisi {starts}")
    if sents and any(sents[-1].startswith(c) for c in CLOSERS):
        hits.append("penutup paragraf generik")
    if re.search(r"not only\b.*?\bbut also|tidak hanya\b.*?\btetapi juga|bukan sekadar\b.*?\bmelainkan", low, re.S):
        hits.append("not only ... but also")
    if re.search(r"—|---", par):
        hits.append("em-dash")
    hits += [f"pertanyaan retoris: {s[:60]}" for s in sents if s.endswith("?")]
    hits += [f"artefak LLM '{a}'" for a in ARTEFACTS if a in par]
    # pola yang terbukti ditandai detektor (bagian 5)
    commas = [s for s in sents if s.count(",") - s.count("(") >= 2 and len(s.split()) > 18]
    if len(commas) >= 2:
        hits.append(f"{len(commas)} kalimat berisi rangkaian klausa dengan koma")
    hits += [f"klausa syarat di depan: {s[:60]}" for s in sents if re.match(r"(When|If|Ketika|Jika|Apabila)\b[^,]{3,80},", s)]
    if re.search(r"\b(shifts|moves|changes) by\b|\bThe difference is\b", par):
        hits.append("kerangka laporan hasil (shifts by / The difference is)")
    if re.search(r"\b(lower|lowers|drop|drops|falls|decreases|below|reduces)\b[^.]{0,70}\bby (\$-\$|−|-)\s?\d", par):
        hits.append("negatif ganda (kata kerja turun + angka minus)")
    this_starts = [s for s in sents if re.match(r"(This|These|Hal ini)\b", s)]
    if len(this_starts) >= 2:
        hits.append(f"{len(this_starts)} kalimat diawali This/These/Hal ini")
    if hits:
        print(f"paragraf {i} ({par[:50]}...):")
        for h in hits:
            print("   -", h)

for m in re.finditer(r"\$p\$\s+(\$<\$)?\d", raw):
    print("notasi p tanpa '=' atau '<':", raw[m.start():m.start() + 20])
for c in "“”‘’…—":
    if c in raw:
        print(f"karakter Unicode '{c}' (konversi ke LaTeX)")
for line in raw.splitlines():
    if "\\textbf{" in line and "&" not in line and not line.lstrip().startswith(("\\item", "%")):
        print("label tebal di paragraf:", line.strip()[:80])
if lengths:
    print(f"panjang kalimat: n={len(lengths)}, median {statistics.median(lengths):.0f}, "
          f"min {min(lengths)}, maks {max(lengths)}, SD {statistics.pstdev(lengths):.1f} (SD kecil = ritme seragam)")
```

### 13.2 Cek setelah menghapus atau memindahkan kalimat

```bash
wc -l naskah.tex                                  # bandingkan dengan jumlah baris sebelum edit
git diff naskah.tex | grep -cE '^[-+]\s*$'        # baris kosong yang bertambah atau hilang; harus 0 kecuali disengaja
git diff --word-diff=plain naskah.tex             # lihat perubahan per kata
```

Kalau naskah tidak memakai git, simpan salinan sebelum edit lalu bandingkan dengan `diff -u lama.tex baru.tex`.

### 13.3 Konsistensi angka

1. Tetapkan satu sumber kebenaran angka (keluaran notebook, file hasil, atau tabel).
2. Ambil semua angka dari naskah, misalnya dengan pola `(?<![\w.])[-+]?\d(?:[\d,]*\d)?(?:\.\d+)?%?`.
3. Cocokkan setiap angka dengan sumbernya. Perhatikan pembulatan: selisih yang dihitung dari nilai yang belum dibulatkan bisa berbeda 0.001 dari selisih nilai di tabel. Itu wajar, asal sumbernya sama.
4. Cek angka yang muncul di beberapa tempat (abstrak, Pendahuluan, Hasil, Kesimpulan) agar nilainya sama di semua tempat.
5. Setelah eksperimen dijalankan ulang, ulangi langkah 2–4 dan daftar angka yang berubah.

### 13.4 Verifikasi referensi

Untuk setiap entri daftar pustaka:
1. **Ada DOI:** buka `https://api.crossref.org/works/<DOI>`. Cocokkan judul, penulis pertama, tahun, dan venue. Periksa field `updated-by` untuk retraksi atau koreksi.
2. **Tanpa DOI, ada arXiv ID:** buka `http://export.arxiv.org/api/query?id_list=<ID>` dan cocokkan judul serta penulis. Kalau versi terbit (konferensi atau jurnal) ada, kutip versi terbitnya.
3. **Lainnya** (ACL Anthology, halaman resmi dataset atau software): cocokkan ke halaman resminya. Dataset dan software juga perlu versi dan tanggal.
4. **Baca bagian yang dikutip** di PDF untuk memastikan sumber itu benar-benar mendukung klaim di naskah.
5. **Paper berbayar** (IEEE, Elsevier, Springer): minta PDF-nya ke pengguna. Jangan menyimpulkan isi dari judul atau abstrak saja.
6. Simpan PDF referensi di satu folder proyek, dan catat hasil verifikasi setiap entri.

### 13.5 Jumlah kata abstrak

Hapus perintah LaTeX dan simbol `{}~\$`, lalu hitung kata dengan `len(teks.split())`. Bandingkan dengan batas venue (IEEE: 150–250).

---

## 14. Cara melapor dan menyajikan revisi

- **Untuk usulan review:** gunakan enam kelompok di bagian 12, langkah 4. Sertakan tautan atau nomor baris untuk setiap butir.
- **Untuk revisi kalimat:** tampilkan before/after **hanya untuk kalimat yang berubah**, dengan catatan singkat (pola apa, diganti dengan apa).
- **Paragraf lengkap lama dan baru** diberikan kalau diminta. Sebutkan kalimat mana yang tidak berubah.
- **Jangan membuat tabel analisis panjang untuk perubahan kecil.** Pengguna pada kasus nyata menolak format itu ("cukup 2 kalimat saja").
- **Penilaian risiko deteksi** ditandai sebagai **perkiraan berdasarkan pola**, bukan hasil detektor.
- **Penjelasan konsep** (misalnya "logit itu apa"): beri satu contoh angka kecil yang benar secara matematis, dan bedakan ilustrasi dari data asli.
- **Laporkan kesalahan sendiri** beserta perbaikannya, misalnya "baris kosong sempat terhapus di 4 tempat; sudah dikembalikan".
- **Sebut yang belum selesai** atau yang menunggu keputusan pengguna, misalnya abstrak yang masih di atas batas kata.

---

## 15. Integritas dan kebijakan IEEE

- **Pengungkapan AI** [SM], [IA]:
    - Konten hasil AI (teks, gambar, kode) wajib diungkapkan di Acknowledgment: sistem AI yang dipakai, bagian mana, dan sejauh mana.
    - Penyuntingan tata bahasa dengan AI umumnya di luar kebijakan ini, tetapi pengungkapannya tetap direkomendasikan.
    - Pernyataan ini tidak boleh dihapus. Kalau teks buatan agent dipakai apa adanya, pernyataannya harus diperluas.
- **Konten fabrikasi**, termasuk referensi yang tidak ada, membuat naskah langsung ditolak [IA].
- **Tata bahasa buruk** juga membuat naskah langsung ditolak [IA]. Ini alasan larangan "salah ketik sengaja".
- **Plagiarisme:** semua naskah dipindai, termasuk kemiripan dengan karya sendiri [IA].
- **Gambar dan grafik** tidak boleh berupa gambar buatan LLM. Semuanya dihasilkan skrip, dan skripnya disimpan bersama kode proyek.
- **Reproduksibilitas:** metodologi rinci; kode dan data dibagikan di repositori bila memungkinkan [RR].
- **Verifikasi sebelum melapor:** setiap klaim, nomor baris, dan angka dicek ke sumbernya sebelum dilaporkan. Kalau ada koreksi atas laporan sebelumnya, laporkan koreksinya.

---

## 16. Daftar cek akhir

**Sebelum mengubah**
- [ ] Parameter naskah sudah ditetapkan (bagian 3).
- [ ] Ada sorotan detektor dari pengguna atau kesalahan yang jelas; bukan tebakan.
- [ ] Fakta terkunci sudah dicatat per paragraf.
- [ ] Usulan sudah disetujui.

**Fakta**
- [ ] Semua angka, sitasi, rujukan, simbol, dan nama muncul lagi persis sama; setiap sitasi menempel pada klaim yang sama.
- [ ] Makna, penekanan, kausalitas, dan pelaku sama dengan sumber (pass makna).
- [ ] Tidak ada tafsiran baru; peringkat sesuai metrik utama.

**Kata dan kalimat**
- [ ] Tidak ada kata dari bagian 4 (atau ada alasan kuat untuk memakainya).
- [ ] Sesuai kebijakan kata ganti; paling banyak tiga kalimat pasif berturut-turut.
- [ ] Transisi di awal kalimat paling banyak satu per paragraf; tidak ada "not only … but also".
- [ ] Tidak ada deretan kalimat berisi rangkaian klausa dengan koma, klausa "When X," + pasif, atau "shifts by / The difference is".
- [ ] Tidak ada kerangka enumerasi, glos ganda, kalimat pengulang, atau pembuka "This/These" beruntun.
- [ ] Tidak ada negatif ganda; notasi p "p=…"; proporsi dan persen konsisten.
- [ ] Panjang kalimat bervariasi (SD tidak kecil); bentuk perbaikan tidak membentuk templat baru.
- [ ] Hanya kalimat yang ditandai atau salah yang diubah; kalimat lain persis sama.

**Paragraf dan format**
- [ ] Paragraf tidak ditutup rangkuman generik dan hanya membahas satu topik.
- [ ] Limitasi dan saran spesifik untuk studi ini.
- [ ] Tidak ada artefak LLM, placeholder, sisa markdown, emoji, em-dash, atau karakter Unicode yang belum dikonversi.
- [ ] Aturan IEEE di bagian 9 terpenuhi (abstrak, akronim, angka, rujukan, sitasi).

**Sesudah mengubah**
- [ ] Jumlah baris dan baris kosong tidak berubah tanpa sengaja; paragraf tidak menyatu.
- [ ] Kompilasi bersih; abstrak ≤ batas kata.
- [ ] File turunan dibangun ulang dan dicocokkan berdasarkan teks.
- [ ] Pemindai gaya (bagian 13.1) sudah dijalankan dan setiap temuannya dinilai.
- [ ] Laporan before/after singkat sudah diberikan, termasuk catatan pengungkapan AI bila teks agent dipakai apa adanya.

---

## 17. Log pola detektor

Setiap pola baru yang ditandai detektor pengguna dicatat di sini dengan format berikut, lalu ditambahkan ke bagian 5 dengan tanda ★.

| Tanggal | Detektor | Kalimat yang ditandai | Pola | Perbaikan yang diterima |
|---|---|---|---|---|
| 18 Okt 2026 | detektor pengguna | "When the data are reduced to 130 thousand documents, the test macro-F1 shifts by −0.002 (p=1.000). The difference is +0.001 (p=1.000) when token dropout is removed and +0.009 (p=0.281) with an MLP head that cannot be folded." | Klausa syarat + koma, pasif, "shifts by", "The difference is", keterangan tidak sejajar (5.2, 5.3) | "Reducing the data to 130 thousand documents lowers the test score by 0.002 (p=1.000). Removing token dropout gives +0.001 (p=1.000) and an MLP head that cannot be folded +0.009 (p=0.281)." |
| 18 Okt 2026 | detektor pengguna | Penulisan ulang satu paragraf penuh oleh agent | Teks yang dipoles agent lebih terbaca sebagai AI daripada versi penulis | Kembali ke teks penulis; hanya kalimat yang ditandai yang diganti (bagian 2) |
| sebelum 18 Okt 2026 | detektor pengguna | Kalimat pendek sejajar berderet; kerangka "two requirements … The first … The second …"; dua glos per paragraf; "which is"/"as well as" dan "This …" beruntun | 5.1, 5.4, 5.5 | Lipat enumerasi, satu glos per paragraf, variasikan pembuka kalimat |

---

## Lampiran A. Contoh profil naskah (StaticKD)

Contoh pengisian bagian 3 untuk naskah asal panduan ini. Untuk naskah lain, buat profil serupa.

| Parameter | Nilai |
|---|---|
| Naskah | "StaticKD: Distilling a Multilingual IPTC News Topic Classifier into a Static Token-Logit Table for Lightweight CPU Inference", satu file LaTeX dengan layout IEEEtran journal |
| Venue target | IEEE Access |
| Bahasa | Naskah bahasa Inggris; catatan kerja dan penjelasan ke pengguna dalam bahasa Indonesia |
| Kata ganti | Tanpa "we/our/kami"; tanpa subjek orang (*I, you, we, they*), termasuk "they" untuk benda |
| Abstrak | 150–250 kata (versi awal 311 kata, sehingga perlu dipangkas) |
| Metrik utama | macro-F1 di test set; accuracy dan held-out agreement sebagai metrik pendukung |
| Format angka | Desimal titik, pemisah ribuan koma (285,999), notasi p "p=0.004" |
| Gaya rujukan | Dua paper dari pembimbing: 0 "we", "This study …" untuk tujuan dan kontribusi, alasan untuk setiap pilihan metode |
| Alur parafrase | Lembar kerja per paragraf berisi Current (teks sekarang), Makna (arti dalam bahasa Indonesia), Locked (angka, sitasi, rujukan, simbol, nama), dan Paraphrase (diisi penulis). Penulis menulis ulang sendiri; agent mengecek fakta dan pola |
| Pernyataan AI | Acknowledgment menyebut Claude untuk kode eksperimen, pengolahan data (draf tabel pemetaan), serta review dan penyuntingan ringan |

---

## Sumber

- D. Kobak, R. González-Márquez, E.-Á. Horvát, and J. Lause, "Delving into LLM-assisted writing in biomedical publications through excess vocabulary," *Science Advances*, 2025. [PMC12219543](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12219543/), [arXiv:2406.07016](https://arxiv.org/abs/2406.07016)
- W. Liang et al., "Monitoring AI-modified content at scale: A case study on the impact of ChatGPT on AI conference peer reviews," ICML 2024. [PMLR](https://proceedings.mlr.press/v235/liang24b.html), [arXiv:2403.07183](https://arxiv.org/abs/2403.07183)
- W. Liang, M. Yuksekgonul, Y. Mao, E. Wu, and J. Zou, "GPT detectors are biased against non-native English writers," *Patterns*, 2023. [arXiv:2304.02819](https://arxiv.org/abs/2304.02819)
- [SM] IEEE Editorial Style Manual for Authors (via [IEEE Author Center](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/ieee-editorial-style-manual/)).
- [RG] IEEE Reference Style Guide for Authors, V 3.28.2025.
- [MG] IEEE Editing Mathematics, V 10.27.2023.
- [AC] [IEEE Author Center: Structure Your Article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/).
- [IA] [IEEE Access: Preparing Your Article](https://ieeeaccess.ieee.org/authors/preparing-your-article/).
- [RR] [IEEE Author Center: Research Reproducibility](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/research-reproducibility/).
