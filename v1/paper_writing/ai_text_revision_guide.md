# Panduan Revisi Teks agar Tidak Terbaca sebagai Tulisan AI

Acuan tunggal untuk agent atau sesi mana pun yang menulis, memparafrasekan, atau merevisi naskah StaticKD. File ini menggantikan `ai_text_criteria_to_be_avoided.txt` dan menggabungkan aturan yang sebelumnya tersebar di memori sesi.

- **Diperbarui:** 18 Oktober 2026
- **Naskah bahasa Inggris:** [paper_final/main.tex](../paper_final/main.tex)
- **Lembar parafrase:** [paper_rewrite_mod.md](paper_rewrite_mod.md) (dibuat dari [paper_rewrite.md](paper_rewrite.md))
- **Isi yang wajib ada:** [paper_quality_check_filled.md](paper_quality_check_filled.md)
- **Aturan tata bahasa dan gaya IEEE:** [paper_rules.md](paper_rules.md)
- **Pemindai otomatis:** [scripts/check_style.py](../scripts/check_style.py) (gaya) dan [scripts/check_paper.py](../scripts/check_paper.py) (angka)

**Cara pakai singkat:** baca bagian 1–2 sekali. Saat menulis, ikuti alur di bagian 9. Sebelum menyerahkan teks, jalankan daftar cek di bagian 11. Kalau detektor pengguna menandai pola baru, catat di bagian 4 beserta tanggal dan contohnya.

---

## 1. Tujuan dan batasan

Tujuannya adalah tulisan yang **memang** terbaca seperti tulisan peneliti: spesifik, jujur, punya alasan, dan dapat diverifikasi. Detektor AI menandai teks yang mudah ditebak. Ciri-cirinya: pilihan kata paling umum, ritme kalimat seragam, kerangka wacana bertemplat, dan isi generik. Revisi yang efektif menghilangkan ciri-ciri itu dengan **menambah isi dan mengubah struktur**, bukan dengan menyamarkan teks.

**Dilarang**, karena tidak etis dan juga merugikan naskah:
- Sengaja menyisipkan salah ketik atau tata bahasa yang salah. IEEE Access langsung menolak naskah dengan tata bahasa buruk.
- Karakter tersembunyi, homoglyph, atau spasi aneh.
- Alat *spinner* atau *humanizer* yang mengganti kata secara acak, atau kata langka yang mengubah makna.
- Mengubah angka, menghapus sitasi, atau melemahkan klaim yang sudah didukung bukti, hanya supaya lolos detektor.
- Menghapus atau melewatkan pernyataan penggunaan AI di Acknowledgment (bagian 10).

**Batas detektor.** Detektor itu probabilistik dan sering salah menandai tulisan penulis non-native English. Liang et al. (2023, *Patterns*) mencatat rata-rata *false positive* 61,3% pada esai TOEFL. Lolos di satu detektor tidak menjamin lolos di detektor lain. Tidak ada teknik yang menjamin 0% terdeteksi. Yang bisa dijamin hanyalah teks yang spesifik dan bebas pola di bawah.

## 2. Gaya rujukan proyek

Gaya naskah mengikuti paper Dr. Dwi Sunaryono (ITS Informatika): [*Trust Region Plug-and-Play*](Trust_Region_Plug-and-Play_With_Provable_Convergence_for_Image_Restoration.pdf) dan [ADLC, IEEE Access 2025](../reference/Augmented_Data_Low_Confidence_ADLC_A_Confidence-Driven_Data_Augmentation_Framework_With_Ensemble_Optimization_for_Enhanced_Machine_Learning_Performance.pdf). Hasil hitungan ulang pada kedua PDF (±12.000 dan ±13.000 kata, 18 Oktober 2026):

| Ciri | Trust Region PnP | ADLC | Aturan untuk naskah |
|---|---|---|---|
| "we/our/us" | 0 | 0 | **Tidak ada kata ganti orang pertama** (keputusan D22). Tidak ada subjek orang (*I, you, we, they*). |
| "This study/paper/work …" | 10 | 30 | Dipakai untuk tujuan, usulan, RQ, dan kontribusi. |
| "aims to" | 0 | 6 | Boleh, misalnya "This study aims to …". |
| "In terms of" | 3 | 1 | Boleh, sesekali. |
| "Furthermore" | 11 | 2 | Kata transisi **boleh**, asal tidak menumpuk (lihat bagian 4). |
| em-dash | 1 | 6 | Hindari di naskah ini. |

Ciri lain yang dicatat dari kedua paper: "Let X denote …" untuk notasi, pasif pendek untuk langkah teknis, dan alasan selalu disebut untuk setiap pilihan metode.

Cara mengganti "we" tanpa membuat teks kaku. Campurannya diambil dari [change_log.md](change_log.md) §2.7:
- **Subjek "this study/this paper":** untuk usulan, RQ, dan kontribusi.
- **Subjek benda yang aktif:** "Internal validation uses 3% …", "The evaluation also reports …".
- **Pasif pendek:** untuk langkah teknis ("Each process is pinned …").
- **Frasa impersonal:** untuk dugaan dan saran ("A plausible explanation is …").
- **Batas pasif:** paling banyak tiga kalimat pasif berturut-turut.

Istilah teknis tetap dalam bahasa Inggris (teacher, student, distillation, macro-F1, dan seterusnya). Singkatan didefinisikan saat pertama muncul.

## 3. Kata yang dihindari

Frekuensi kata-kata ini melonjak sejak LLM banyak dipakai:
- Kobak et al., "Delving into LLM-assisted writing in biomedical publications through excess vocabulary," *Science Advances*, 2025. Penelitian ini menganalisis lebih dari 15 juta abstrak PubMed.
- Liang et al., ICML 2024. Di review ICLR 2024, "commendable" naik 9,8×, "meticulous" 34,7×, dan "intricate" 11,2×.

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

## 4. Pola kalimat yang dihindari

Satu kemunculan belum tentu salah; yang terdeteksi adalah **penumpukan** pola. Pola bertanda ★ sudah pernah ditandai detektor pengguna pada naskah ini.

**Ritme dan struktur**
- Panjang kalimat seragam. Campur kalimat pendek dengan kalimat panjang yang membawa detail.
- ★ Kalimat pendek yang sejajar dan seimbang, berderet-deret.
- Pola tiga hal yang berulang ("efisien, akurat, dan skalabel"). Sebut jumlah yang memang ada.
- "Tidak hanya X, tetapi juga Y", "Bukan sekadar X, melainkan Y", "not only … but also". Paling banyak sekali di seluruh naskah, lebih baik tidak sama sekali.
- Kata transisi di awal kalimat (Selain itu, Lebih lanjut, Dengan demikian, Furthermore, Moreover, Additionally) paling banyak satu per paragraf.
- Em-dash (—) tidak dipakai; titik dua dan titik koma dipakai seperlunya. Pakai titik dan kalimat baru.
- Pertanyaan retoris ("Namun, bagaimana jika …?").

**Kerangka yang terdeteksi (★)**
- **Kerangka enumerasi:** "… seeks X that satisfies two requirements. The first requirement concerns cost. … The second requirement concerns accuracy."
    - Lipat syarat-syarat itu ke dalam satu atau dua kalimat yang lebih panjang.
    - Jangan memakai "first/second" kecuali sumbernya memang berupa daftar.
- **Dua glos dalam satu paragraf**, misalnya "that is, one score for each topic" ditambah "i.e., labels that do not come from the teacher". Paling banyak satu glos per paragraf.
- **Kalimat yang mengulang klaim sebelumnya** dengan kata lebih sederhana ("so the number of operations grows in proportion to the article length"). Hapus.
- **3–4 klausa yang disambung koma** dalam satu kalimat.
- **Klausa ekor** ", and on …" di akhir kalimat.
- **Aposisi di dalam subjek** ("The teacher, an XLM-R model with …, labels …").
- **Banyak kalimat diawali "This …"/"These …"**, terutama pada bahasa Inggris hasil terjemahan dari bahasa Indonesia.
- **Kerangka pelaporan hasil:** "When the data are reduced to X, the test macro-F1 shifts by −0.002. The difference is +0.001 when token dropout is removed …". Ciri-cirinya:
    - klausa syarat di depan atau di belakang;
    - kata kerja netral (*shifts, moves, changes, is*) diikuti angka bertanda;
    - subjek tiruan ("The difference is");
    - pasif di klausa syarat;
    - frasa metrik yang diulang-ulang.

  Versi yang lolos memakai aksi sebagai subjek, kata kerja berarah, dan elipsis:

  > Reducing the data to X lowers the test score by 0.002. Removing token dropout gives +0.001 and an MLP head +0.009.

  **Variasikan bentuk penggantinya**, supaya pola "Gerund … lowers …" tidak menjadi templat baru.

- ★ **Rantai konsesi–kontras–kesimpulan** (18 Oktober 2026):
    > Its macro-F1 does not differ significantly from that of DistilmBERT (+0.010, p = 0.800), even though StaticKD gets more test articles right (McNemar p < 0.001). McNemar's test treats every article as independent, but articles from the same site are not. Its result therefore counts for less than the site-clustered macro-F1 test.

  Ini tiga kalimat yang masing-masing satu langkah logika (even though → but → therefore). Kalimat ketiga hanya menafsirkan kalimat kedua, dan kalimat-kalimatnya beruntun dibuka dengan "Its". Versi yang diusulkan:
    > StaticKD and DistilmBERT do not differ significantly in macro-F1 (+0.010, p = 0.800). McNemar's test, which treats articles from the same site as independent, does favor StaticKD on accuracy (p < 0.001).

**Translationese Indonesia → Inggris**
- ★ "yang merupakan" → "which is", dan "serta" → "as well as/and" di setiap kalimat.
- ★ "Hal ini …" → "This …" sebagai pembuka kalimat beruntun.
- Nominalisasi dari "dilakukan" ("Evaluation is carried out on …"). Pakai kata kerja langsung: "The evaluation uses …".

## 5. Pola paragraf dan wacana yang dihindari

- Semua paragraf berpola sama: kalimat topik, tiga poin, kalimat kesimpulan.
- Paragraf ditutup kalimat rangkuman ("Secara keseluruhan, …", "Overall, …", "Hal ini menunjukkan pentingnya …"). Akhiri dengan fakta atau implikasi yang spesifik.
- Penanda arah tanpa isi ("Pada bagian ini akan dibahas …"). Cukup satu kalimat peta di akhir Pendahuluan.
- Gagasan yang sama diulang dengan kata lain di paragraf yang sama.
- Hedging berlapis ("berpotensi dapat mungkin meningkatkan"). Satu tingkat hedging saja, dan hanya bila memang tidak pasti.
- Nada yang selalu positif dan seimbang. Sebut kelemahan dengan tegas dan spesifik.
- Klaim umum tanpa rujukan atau angka ("model transformer sangat populer").
- Satu paragraf membahas dua topik.
- Istilah dipakai sebelum didefinisikan.
- Angka disajikan tanpa kesimpulan.
- Alasan sebuah pilihan tidak disebut. Daftar kasus nyatanya ada di [evaluasi_alur_naskah.md](evaluasi_alur_naskah.md).

## 6. Ciri khusus paper yang wajib dihindari

- **Sitasi halusinasi:** paper tidak ada, DOI salah, atau tahun/venue/penulis keliru. Setiap entri `.bib` harus dapat diverifikasi ([scripts/verify_references.py](../scripts/verify_references.py)). IEEE Access langsung menolak konten fabrikasi, termasuk referensi yang tidak ada.
- **Sitasi yang tidak mendukung klaim.** Jangan mengutip paper hanya karena judulnya cocok.
- **Angka yang tidak konsisten** antara abstrak, teks, tabel, dan gambar. Angka diambil dari keluaran notebook (`results/final/paper_generated/numbers.tex`, dicek dengan `check_paper.py`), bukan diketik dari ingatan.
- **Kontribusi generik** ("a new framework that significantly improves performance"). Tulis: metode apa, dibandingkan baseline apa, naik berapa, pada data apa.
- **Tinjauan pustaka berupa daftar ringkasan** ("A et al. did X. B et al. did Y."). Kelompokkan per pendekatan, bandingkan, lalu tunjukkan celahnya.
- **Limitasi dan saran yang klise** ("future work could use larger datasets"). Tulis limitasi yang spesifik untuk studi ini beserta konsekuensinya.
- **"To the best of our knowledge"** paling banyak sekali, dan hanya untuk klaim kebaruan yang sudah dicek ke literatur.
- **Detail teknis yang hilang:** hyperparameter, seed, hardware (CPU, jumlah thread), ukuran tiap split.
- **Artefak keluaran LLM:** "Certainly! Here is …", "As an AI language model", "[insert citation]", "[citation needed]", "as of my knowledge cutoff", "Berikut adalah …", placeholder "XX", atau "TODO".

## 7. Format yang dihindari

- Bullet point di bagian yang seharusnya berupa prosa (Pendahuluan, Penelitian Terkait, Hasil, Pembahasan). Daftar hanya untuk RQ, kontribusi, dan langkah prosedur (keputusan D9).
- Label tebal di tengah paragraf ("\textbf{Efisiensi:} …").
- Sisa markdown di file `.tex`: `**`, `##`, backtick, emoji.
- Judul subbab yang tidak mengikuti template IEEE.
- Karakter Unicode yang belum dikonversi ke LaTeX (“ ” — …).

## 8. Teknik revisi yang efektif

Urutkan dari yang paling berdampak:

1. **Tambahkan hal yang hanya diketahui penulis.** Contohnya alasan memilih sebuah metode, eksperimen yang gagal, batasan nyata (CPU, RTX 4050, waktu), dan hasil yang mengejutkan. Pertanyaan "Wawancara" di lembar parafrase ada untuk menggali hal-hal ini. Detail seperti ini tidak bisa ditebak oleh model bahasa.
2. **Mulai dari temuan atau angka, bukan dari kerangka.** "StaticKD keeps 91.1% of the teacher's test macro-F1 and classifies 473 articles per second per core" lebih baik daripada "This section presents the results of …".
3. **Lipat enumerasi** menjadi satu atau dua kalimat panjang dengan anak kalimat. Contohnya ada di gaya paper rujukan: "This study aims to …", "In terms of …".
4. **Hapus kalimat yang tidak menambah informasi baru:** penegasan ulang, glos kedua, dan kalimat penutup rangkuman.
5. **Ganti kata umum dengan istilah domain yang tepat:** "site-cluster bootstrap", bukan "a robust statistical method".
6. **Variasikan ritme sesuai isi.** Kalimat pendek untuk temuan utama; kalimat panjang untuk prosedur dan syaratnya. Jangan memotong semua kalimat menjadi sama pendek.
7. **Untuk laporan hasil,** pakai aksi sebagai subjek dan kata kerja berarah (lowers, raises, halves, matches), lalu pakai elipsis untuk deret angka. Ganti bentuknya dari kalimat ke kalimat.
8. **Variasikan setiap perbaikan.** Pengganti yang sama, bila dipakai berulang, akan menjadi templat baru yang juga terdeteksi.

## 9. Alur kerja revisi

1. **Kunci fakta.**
    - Baris **Locked** di setiap blok lembar parafrase memuat angka, sitasi, rujukan, dan simbol yang wajib muncul lagi persis sama.
    - Nomor sitasi tetap menempel pada klaim yang sama.
    - Daftar fakta lengkap ada di dokumen [Fakta Terkunci Paper StaticKD](https://claude.ai/code/artifact/5154d6e0-5827-4e95-9e8a-db4294caab9c). Angka di dokumen itu masih memakai format Indonesia dari `_archive/jurnal_latex_v1/`; sumber kebenaran untuk naskah Inggris adalah `results/final/paper_generated/numbers.tex`.
2. **Pahami maknanya.** Baca **Current** dan **Makna**. Klaim, penekanan, dan hubungan sebab-akibat harus tetap sama.
3. **Tulis versi Indonesia dulu.** Versi Inggris dibuat atas permintaan, dengan struktur yang sama.
4. **Isi dengan detail penulis** (bagian 8, butir 1). Kalau detailnya belum ada, tanyakan ke pengguna lewat daftar Wawancara; jangan mengarang.
5. **Verifikasi dua kali sebelum ditulis ke file atau dilaporkan:**
    - **Pass makna:** bandingkan dengan sumber. Periksa klaim, angka, penekanan, kausalitas, dan pelaku. Contoh kesalahan lama: menambahkan kata "hanya", atau pelaku yang tertukar.
    - **Pass gaya AI:** periksa terhadap bagian 3–7. Sebaiknya dilakukan oleh verifier independen, bukan oleh penulis teks itu sendiri.
    - Laporkan apa yang diubah oleh setiap pass.
6. **Jalankan skrip:**
    - `python scripts/check_style.py` untuk daftar kata, transisi, pola, em-dash, label tebal, pertanyaan retoris, artefak, dan sebaran panjang kalimat.
    - Setelah teks masuk ke `main.tex`, jalankan `python scripts/check_paper.py` untuk angka.
    - Setiap temuan skrip tetap dinilai manual, karena pemindai hanya saringan pertama.
7. **Uji per paragraf di detektor pengguna.** Catat pola yang masih ditandai ke bagian 4 (dengan tanda ★, tanggal, dan contoh).

**Aturan kerja di lembar parafrase**
- **Blok tulisan pengguna:** MET-01 s.d. MET-04 ditulis pengguna dan tidak boleh ditimpa. Penghapusan di Paraphrase pengguna disengaja; jangan dikembalikan, tetapi jangan juga membawa klaim yang bertentangan dengan paper.
- **Nomor baris di header blok** ("main.tex baris N") sudah usang. Cocokkan blok dengan `main.tex` berdasarkan isi.
- **File yang boleh diedit:**
    - Yang diedit adalah `paper_rewrite_mod.md`.
    - LaTeX (`paper_final/`) tidak diedit kecuali diminta.
    - Kalau pengguna meminta "tes", berikan teksnya di chat saja.
- **Tambahan kecil juga dicek.** Menyisipkan satu kalimat pun ke naskah tetap harus melewati pengecekan pola sebelum compile.

## 10. Integritas dan kebijakan IEEE

- **Pengungkapan AI:** IEEE mewajibkan penggunaan konten hasil AI (teks, gambar, kode) diungkapkan di Acknowledgment, termasuk sistem AI yang dipakai, bagian mana, dan sejauh mana. Penyuntingan tata bahasa dengan AI umumnya di luar kebijakan ini, tetapi pengungkapannya tetap direkomendasikan. Pernyataan ini tidak boleh dihapus.
- **Konten fabrikasi:** naskah dengan konten fabrikasi, termasuk referensi yang tidak ada, langsung ditolak (IEEE Access).
- **Tata bahasa:** naskah dengan tata bahasa buruk juga langsung ditolak (IEEE Access). Ini alasan larangan "salah ketik sengaja" di bagian 1.
- **Gambar dan grafik:** tidak boleh berupa gambar buatan LLM. Semuanya harus dihasilkan skrip, dan skripnya disimpan di folder kode.
- **Referensi:**
    - PDF referensi disimpan di [reference/](../reference/).
    - Paper berbayar (IEEE, Elsevier, Springer) diminta ke pengguna, yang punya akses dan akan menaruhnya di folder itu.
- **Verifikasi sebelum melapor:** setiap klaim, nomor baris, dan angka dicek ke sumbernya sebelum dilaporkan. Kalau ada koreksi atas laporan sebelumnya, laporkan koreksinya.

## 11. Daftar cek sebelum menyerahkan teks

**Fakta**
- [ ] Semua isi baris Locked muncul lagi persis sama, dan setiap sitasi menempel pada klaim yang sama.
- [ ] Makna, penekanan, kausalitas, dan pelaku sama dengan sumber (pass makna).
- [ ] Setiap klaim punya angka, rujukan, atau lokasi evidence.

**Kata dan kalimat**
- [ ] Tidak ada kata dari bagian 3 (atau ada alasan kuat untuk memakainya).
- [ ] Tidak ada "we/our/kami"; paling banyak tiga kalimat pasif berturut-turut.
- [ ] Kata transisi di awal kalimat paling banyak satu per paragraf; tidak ada "not only … but also".
- [ ] Tidak ada kerangka enumerasi, glos ganda, kalimat pengulang, atau rangkaian koma 3–4 klausa.
- [ ] Laporan hasil tidak memakai kerangka "shifts by / The difference is", dan bentuk penggantinya bervariasi.
- [ ] Tidak ada translationese ("which is", "as well as" beruntun, pembuka "This/These" beruntun).
- [ ] Panjang kalimat bervariasi; cek SD di keluaran `check_style.py`.

**Paragraf dan format**
- [ ] Paragraf tidak ditutup kalimat rangkuman generik dan hanya membahas satu topik.
- [ ] Limitasi dan saran spesifik untuk studi ini.
- [ ] Tidak ada artefak LLM, placeholder, sisa markdown, emoji, atau em-dash.

**Penutup**
- [ ] `check_style.py` sudah dijalankan dan setiap temuannya dinilai.
- [ ] Hasil kedua pass dan apa yang diubah sudah dilaporkan ke pengguna.

## Sumber

- D. Kobak, R. González-Márquez, E.-Á. Horvát, and J. Lause, "Delving into LLM-assisted writing in biomedical publications through excess vocabulary," *Science Advances*, 2025. [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12219543/), [arXiv:2406.07016](https://arxiv.org/abs/2406.07016v5)
- W. Liang et al., "Monitoring AI-modified content at scale: A case study on the impact of ChatGPT on AI conference peer reviews," ICML 2024. [PMLR](https://proceedings.mlr.press/v235/liang24b.html), [arXiv:2403.07183](https://arxiv.org/html/2403.07183v1)
- W. Liang, M. Yuksekgonul, Y. Mao, E. Wu, and J. Zou, "GPT detectors are biased against non-native English writers," *Patterns*, 2023. [arXiv:2304.02819](https://arxiv.org/abs/2304.02819v1)
- IEEE Access, [Preparing Your Article](https://ieeeaccess.ieee.org/authors/preparing-your-article/), dan IEEE Editorial Style Manual (lihat [paper_rules.md](paper_rules.md)).
- Riwayat proyek: [change_log.md](change_log.md) §1.3 dan §2.7, [paper_quality_check_filled.md](paper_quality_check_filled.md) keputusan D8, D9, D14, D17 (D22 tercatat di change_log §2.7), dan catatan detektor dari sesi parafrase 18 Oktober 2026.
