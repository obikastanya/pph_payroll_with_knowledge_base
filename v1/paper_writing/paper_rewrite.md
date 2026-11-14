# Paper Rewrite (StaticKD)

Lembar kerja untuk menulis ulang naskah paragraf demi paragraf. Untuk setiap blok:

1. Baca **Current** (teks paragraf sekarang) dan **Makna** (artinya dalam bahasa Indonesia).
2. Tulis versi Anda di bawah **Paraphrase:** (ganti tulisan "(tulis di sini)"). Cukup teks biasa; sitasi ditulis seperti di Current, misalnya [2], dan rujukan seperti "Section IV-D" atau "Table IV".
3. Pastikan semua yang ada di **Locked** muncul lagi di tulisan Anda: angka sama persis, nomor sitasi tetap menempel pada klaim yang sama.

Aturan singkat: mudah dipahami dan benar; gaya impersonal, tanpa subjek orang (*I, you, we, they*); istilah teknis tetap bahasa Inggris; definisikan singkatan saat pertama muncul; hindari pola di [ai_text_criteria_to_be_avoided.txt](ai_text_criteria_to_be_avoided.txt). Tabel, gambar, dan persamaan hanya placeholder.

Membangun ulang file ini (`python scripts/rewrite_lock.py && python scripts/build_rewrite_md.py`) tidak menghapus Paraphrase yang sudah diisi.

## Judul, penulis, abstrak, kata kunci

---

### JDL · Title · main.tex baris 30

**Current:**
StaticKD: Distilling a Multilingual IPTC News Topic Classifier into a Static Token-Logit Table for Lightweight CPU Inference

**Makna:**
StaticKD: men-distill classifier topik berita IPTC multibahasa menjadi satu tabel logit per token (static token-logit table) untuk inference ringan di CPU.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### PNL · Authors · main.tex baris 32

**Current:**
Obi Kastanya and Ananta Dwi Prayoga Alwy (O. Kastanya and A. D. P. Alwy are with the Department of Informatics Engineering, Sepuluh Nopember Institute of Technology, Surabaya, Indonesia (e-mail: 6025252015@student.its.ac.id; 6025252007@student.its.ac.id). Corresponding author: O. Kastanya. This work received no specific funding.

**Makna:**
Penulis: Obi Kastanya dan Ananta Dwi Prayoga Alwy. Catatan kaki afiliasi: keduanya dari Department of Informatics Engineering, Institut Teknologi Sepuluh Nopember (ITS), Surabaya, Indonesia; e-mail 6025252015@student.its.ac.id dan 6025252007@student.its.ac.id; penulis korespondensi O. Kastanya; penelitian ini tidak menerima pendanaan khusus.

**Locked:** angka 6025252015, 6025252007

**Paraphrase:**
(tulis di sini)

---

### ABS · Abstract · main.tex baris 40

**Current:**
Filtering news by the International Press Telecommunications Council (IPTC) Media Topic taxonomy needs a classifier cheap enough for a multilingual stream of articles. The open multilingual IPTC classifier, based on XLM-RoBERTa-large, takes 1,239 to 2,971 milliseconds per article on one processor core. StaticKD uses this classifier as a teacher and stores 17 scores for each vocabulary token, one per top-level IPTC topic. Classifying an article then only requires tokenizing it and averaging its token scores. The student starts from multilingual static embeddings (one fixed vector per token) and learns from teacher outputs on 285,999 articles in 69 languages. A new test set of 12,744 articles in 47 languages uses topics assigned by human annotators or newsroom editors and mapped onto IPTC, so no test label comes from a model that reads the article. On this test set StaticKD reaches a macro-F1 of 0.545, or 91.1% of the teacher score of 0.598. It classifies 473 articles per second per core, about 616 times faster than the 8-bit quantized teacher, with a 34-megabyte model, and is more accurate than fastText and a linear support vector machine trained on the same teacher labels. Ablations with five seeds show that accuracy comes mainly from multilingual training data and from pre-trained cross-lingual embeddings, and that the top teacher label works as well as the full distribution. Fine-tuning the embeddings helps the training languages but hurts unseen languages. StaticKD is weakest on languages absent from both its training data and the teacher's pre-training data.

**Makna:**
Penyaringan berita dengan taksonomi Media Topic dari International Press Telecommunications Council (IPTC) membutuhkan classifier yang cukup murah untuk aliran artikel multibahasa. XLM-RoBERTa-large menjadi dasar classifier IPTC multibahasa terbuka yang tersedia. Classifier ini memerlukan 1,239 sampai 2,971 milidetik per artikel pada satu core prosesor. Dengan model itu sebagai teacher, StaticKD menyimpan 17 skor untuk setiap token kosakata, masing-masing untuk satu topik IPTC level atas. Klasifikasi sebuah artikel kemudian hanya memerlukan tokenisasi dan perataan skor token-tokennya. Student diinisialisasi dari static embedding multibahasa (satu vektor tetap per token), lalu belajar dari output teacher pada 285,999 artikel dalam 69 bahasa. Pengujian dilakukan pada test set baru berisi 12,744 artikel dalam 47 bahasa. Topik artikelnya ditetapkan oleh anotator manusia atau redaksi lalu dipetakan ke IPTC, jadi tidak ada label uji yang berasal dari model yang membaca artikel. Pada test set ini macro-F1 StaticKD mencapai 0.545, atau 91.1% dari skor teacher (0.598). Model berukuran 34 megabyte ini mengklasifikasi 473 artikel per detik per core, sekitar 616 kali lebih cepat daripada teacher yang dikuantisasi 8-bit. Akurasinya juga lebih tinggi daripada fastText dan linear support vector machine yang dilatih dengan label teacher yang sama. Ablasi dengan lima seed menunjukkan bahwa akurasi terutama berasal dari data training multibahasa dan dari embedding lintas bahasa pra-latih. Menurut ablasi yang sama, label teratas teacher sama baiknya dengan distribusi penuh. Fine-tuning embedding menguntungkan bahasa training, tetapi merugikan bahasa yang tidak dilihat selama training. Kelemahan terbesar StaticKD ada pada bahasa yang tidak terdapat di data training-nya maupun di data pre-training teacher.

**Locked:** angka 1,239, 2,971, 17, 285,999, 69, 12,744, 47, 0.545, 91.1%, 0.598, 473, 616, 8, 34

**Paraphrase:**
(tulis di sini)

---

### KK · Index Terms · main.tex baris 44

**Current:**
Efficient inference, knowledge distillation, multilingual text classification, news topic classification, static embeddings.

**Makna:**
Lima index terms (urut alfabet, huruf kapital hanya di kata pertama): efficient inference, knowledge distillation, multilingual text classification, news topic classification, static embeddings.

**Locked:** —

**Paraphrase:**
(tulis di sini)

## I. Introduction

---

### PEN-01 · main.tex baris 50

**Current:**
News analytics pipelines process a continuous stream of articles from many sources and languages. Many of their later stages, such as entity extraction, sentiment scoring, or event detection, are needed only for some topics. Topic classification therefore comes first and decides which articles each later stage receives, which makes it the only stage that reads every incoming article. Its cost grows with the whole stream, whereas the cost of the later stages grows only with the articles that pass the filter. A topic classifier at the head of a pipeline thus has to be cheap per article and has to work in every language of the stream. Routing by topic also needs the same topics for all sources, while publishers name their sections in different ways; the mapping table built in this study alone covers 814 section names (Section III-D). The taxonomy most used by news agencies is the Media Topic taxonomy of the International Press Telecommunications Council (IPTC). Its top level has 17 topics, such as politics, economy, business and finance, and sport [1], [2].

**Makna:**
Pipeline analitik berita memproses aliran artikel dari banyak sumber dan bahasa secara terus-menerus. Banyak tahap lanjutan di dalamnya hanya diperlukan untuk topik tertentu. Contohnya ekstraksi entitas, penilaian sentimen, atau deteksi peristiwa. Karena itu klasifikasi topik dijalankan paling awal dan menentukan artikel mana yang diterima setiap tahap berikutnya. Peran sebagai filter ini menjadikannya satu-satunya tahap yang membaca setiap artikel yang masuk. Biaya klasifikasi topik bertambah mengikuti volume seluruh aliran, sedangkan biaya tahap lanjutan hanya bertambah mengikuti jumlah artikel yang lolos filter. Classifier topik di awal pipeline dengan demikian harus murah per artikel dan mampu bekerja di setiap bahasa dalam aliran. Routing berdasarkan topik juga memerlukan topik yang sama untuk semua sumber, padahal penerbit menamai rubriknya dengan cara yang berbeda-beda. Tabel pemetaan yang dibangun di studi ini saja sudah mencakup 814 nama rubrik (Bagian III-D). Kantor berita paling banyak memakai taksonomi Media Topic dari International Press Telecommunications Council (IPTC). Level atasnya terdiri atas 17 topik, antara lain politics, economy, business and finance, dan sport [1], [2]. Singkatan yang didefinisikan: IPTC.

**Locked:** angka 814, 17 · sitasi [1] (IPTC) 2024; [2] Kuzman & Ljubešić 2025 · rujukan Section III-D

**Paraphrase:**
News analytic pipeline membutuhkan filterisasi topik untuk mencegah berita tidak relevant diproses ke tahapan berikutnya dan menyebabkan tambahan biaya. Sebelum difilterisasi, berita harus diklasifikasikan ke kategory topik yang sudah di standarisasi, salah satunya adalah Media Topic of the International Press Telecommunications Council (IPTC). IPTC membagi topik berita menjadi 17 category utama dengan banyak sub-kategory di dalamnya.

---

### PEN-02 · main.tex baris 52

**Current:**
Kuzman and Ljubešić [2] released the first open multilingual IPTC classifier. Articles in four languages were labeled with GPT-4o, and these labels were used to fine-tune XLM-RoBERTa-large [3]. The resulting model matches GPT-4o on a human-annotated test set. A follow-up study by the same group concluded that fine-tuned encoders are more practical than large language models (LLMs) for large-scale annotation [4]. An encoder with 559.9 million parameters is still expensive without a graphics processing unit (GPU), and this study targets servers without one, where the classifier shares central processing unit (CPU) cores with the rest of the pipeline. On one CPU core the model needs 2,971 ms per article, and its fastest CPU configuration, an Open Neural Network Exchange (ONNX) export quantized to 8-bit integers (int8), still needs 1,239 ms. A stream of one million articles per day would then occupy 15.1 (ONNX int8) to 34.8 (PyTorch) CPU cores for topic classification alone (Section IV-D). Neither study reports this inference cost, although inference accounts for a large share of the computing demand and energy use of machine learning in production, for example 60% of the machine learning energy use reported by Google [5].

**Makna:**
Classifier IPTC multibahasa terbuka pertama dirilis oleh Kuzman dan Ljubešić [2]. GPT-4o dipakai untuk melabeli artikel dalam empat bahasa, lalu label itu menjadi data untuk fine-tuning XLM-RoBERTa-large [3]. Pada test set beranotasi manusia, model hasilnya setara dengan GPT-4o. Studi lanjutan dari kelompok yang sama menyimpulkan bahwa encoder hasil fine-tuning lebih praktis daripada large language model (LLM) untuk anotasi skala besar [4]. Tanpa graphics processing unit (GPU), encoder dengan 559.9 juta parameter tetap mahal. Target studi ini adalah server tanpa GPU, tempat classifier berbagi core central processing unit (CPU) dengan bagian pipeline lainnya. Model ini memerlukan 2,971 ms per artikel pada satu core CPU. Konfigurasi CPU tercepatnya adalah export Open Neural Network Exchange (ONNX) yang dikuantisasi ke bilangan bulat 8-bit (int8), dan konfigurasi ini masih memerlukan 1,239 ms. Dengan latensi sebesar itu, klasifikasi topik saja akan menyita 15.1 (ONNX int8) sampai 34.8 (PyTorch) core CPU untuk aliran satu juta artikel per hari (Bagian IV-D). Kedua studi di atas tidak melaporkan biaya inference ini, padahal inference menyumbang porsi besar dari kebutuhan komputasi dan pemakaian energi machine learning di produksi. Google misalnya melaporkan bahwa 60% pemakaian energi machine learning-nya berasal dari inference [5]. Singkatan yang didefinisikan di paragraf ini: LLM, GPU, CPU, ONNX, int8.

**Locked:** angka 559.9, 2,971 ms, 8, 1,239 ms, 15.1, 34.8, 60% · sitasi [2] Kuzman & Ljubešić 2025; [3] Conneau et al. 2020; [4] Kuzman Pungeršek et al. 2026; [5] Luccioni et al. 2024 · rujukan Section IV-D

**Paraphrase:**
(tulis di sini)

---

### PEN-03 · main.tex baris 54

**Current:**
Such a pipeline needs a topic classifier that covers many languages, runs in milliseconds per article on an ordinary CPU, and has a small footprint and few dependencies. Small distilled transformers [6], [7] gain about one order of magnitude. In the CPU benchmark of this study, MiniLM-L6 is 21 times faster than the ONNX int8 teacher. Int8 quantization alone gives a factor of 2.3 over PyTorch fp32. fastText [8] is much faster, but it learns its word vectors from scratch and therefore does not transfer across languages. This is a serious restriction here. The IPTC training labels released with the open classifier cover only four languages [9], and even a corpus labeled automatically by a multilingual teacher cannot contain every language of a news stream. No available IPTC classifier is both multilingual and this cheap.

**Makna:**
Pipeline seperti ini memerlukan classifier topik yang mencakup banyak bahasa dan berjalan dalam hitungan milidetik per artikel di CPU biasa. Ukurannya juga harus kecil dan dependensinya sedikit. Transformer kecil hasil distilasi [6], [7] memberi percepatan sekitar satu orde besaran. Benchmark CPU di studi ini mencatat MiniLM-L6 21 kali lebih cepat daripada teacher ONNX int8. Kuantisasi int8 saja mempercepat 2.3 kali dibanding PyTorch fp32. fastText [8] jauh lebih cepat, tetapi vektor katanya dipelajari dari nol sehingga model ini tidak mendukung transfer lintas bahasa. Di sini, hambatan itu serius. Label training IPTC yang dirilis bersama classifier terbuka itu hanya mencakup empat bahasa [9]. Korpus yang dilabeli otomatis oleh teacher multibahasa pun tidak mungkin memuat setiap bahasa dalam aliran berita. Di antara classifier IPTC yang tersedia, tidak ada yang multibahasa sekaligus semurah ini.

**Locked:** angka 21, 2.3 · sitasi [6] Sanh et al. 2019; [7] Wang et al. 2021; [8] Joulin et al. 2017; [9] Kuzman & Ljubešić 2025

**Paraphrase:**
(tulis di sini)

---

### PEN-04 · main.tex baris 56

**Current:**
This paper proposes StaticKD, which distills [10] the XLM-R-large IPTC classifier into a far simpler student. Three properties of the problem make this possible. A teacher that works across languages can label unlabeled news in any language, so training data for the student cost no annotation. Multilingual static embeddings, distilled from sentence encoders [11], [12], [13], give each token one fixed vector and place translation equivalents close to each other, and looking up such a vector costs almost nothing. News topics are also strongly tied to vocabulary, which is why bag-of-words representations remain competitive for topic classification [14]. The student therefore averages the embeddings of the tokens in an article and applies one linear layer. Since both steps are linear, the linear layer can be applied to every embedding once, before deployment. This paper calls this step folding. It turns the model into a table that stores 17 topic scores (logits) per token. Classifying an article then reduces to tokenizing it and averaging the table rows of its tokens, which NumPy handles without a deep learning library. Fig. 6 in Section IV-D shows where the resulting model lies in accuracy and speed relative to the other models.

**Makna:**
StaticKD yang diusulkan dalam paper ini men-distill [10] classifier IPTC XLM-R-large menjadi student yang jauh lebih sederhana. Ada tiga sifat masalah yang memungkinkan hal ini. Berita tak berlabel dalam bahasa apa pun bisa dilabeli oleh teacher yang bekerja lintas bahasa, sehingga data training untuk student tidak memerlukan biaya anotasi. Static embedding multibahasa hasil distilasi sentence encoder [11], [12], [13] memberi setiap token satu vektor tetap dan menempatkan padanan terjemahan saling berdekatan. Mengambil vektor seperti itu hampir tidak memakan biaya. Topik berita juga sangat terkait dengan kosakata. Hal ini menjelaskan mengapa representasi bag-of-words tetap kompetitif untuk klasifikasi topik [14]. Karena itu student merata-rata embedding token dalam artikel, lalu menerapkan satu layer linear. Kedua langkah ini linear, sehingga layer linear itu bisa diterapkan satu kali ke setiap embedding sebelum deployment. Penerapan sebelum deployment ini disebut folding (pelipatan) dalam paper ini. Folding mengubah model menjadi tabel yang menyimpan 17 skor topik (logit) per token. Klasifikasi artikel kemudian tinggal berupa tokenisasi dan perataan baris tabel dari token-tokennya. Perhitungan ini dikerjakan NumPy tanpa library deep learning. Perbandingan akurasi dan kecepatan model ini dengan model lain dapat dilihat pada Gambar 6 di Bagian IV-D.

**Locked:** angka 17 · sitasi [10] Hinton et al. 2015; [11] Tulkens & van Dongen 2024; [12] Wada et al. 2025; [13] Chen et al. 2024; [14] Galke & Scherp 2022 · rujukan Fig. 6, Section IV-D

**Paraphrase:**
(tulis di sini)

---

### PEN-05 · main.tex baris 58

**Current:**
A multilingual claim also requires a multilingual evaluation with labels that do not come from the teacher. The human test set of Kuzman and Ljubešić is not public and covers four languages. SIB-200 [15] covers 205 languages, but its items are short sentences with a non-IPTC taxonomy. To fill this gap, a unified test set of 12,744 articles in 47 languages is built. It combines news pages from 2024 to 2026 whose publishers record the newsroom section of the article in the page metadata (schema.org [16]) with public datasets labeled by human annotators or with publisher categories [17], [18], [19], [20]. These labels are editorial decisions of publishers or annotators, translated onto the official IPTC taxonomy. No model that reads the article text is involved.

**Makna:**
Klaim multibahasa juga menuntut evaluasi multibahasa dengan label yang tidak berasal dari teacher. Test set beranotasi manusia milik Kuzman dan Ljubešić tidak dibuka untuk publik, dan cakupannya empat bahasa. SIB-200 [15] mencakup 205 bahasa, tetapi butir datanya berupa kalimat pendek dan taksonominya bukan IPTC. Celah ini diisi dengan membangun unified test set berisi 12,744 artikel dalam 47 bahasa. Sebagian artikelnya diambil dari halaman berita tahun 2024 sampai 2026 yang penerbitnya mencatat rubrik redaksi artikel di metadata halaman (schema.org [16]). Halaman-halaman ini digabung dengan dataset publik yang dilabeli anotator manusia atau diberi kategori penerbit [17], [18], [19], [20]. Setiap label adalah keputusan editorial dari penerbit atau anotator, yang kemudian diterjemahkan ke taksonomi IPTC resmi. Proses ini tidak melibatkan model apa pun yang membaca teks artikel.

**Locked:** angka 200, 205, 12,744, 47, 2024, 2026 · sitasi [15] Adelani et al. 2024; [16] Guha et al. 2016; [17] Adelani et al. 2023; [18] Petukhova & Fachada 2023; [19] Mirashi et al. 2023; [20] Hossain et al. 2025

**Paraphrase:**
(tulis di sini)

---

### PEN-06 · main.tex baris 60

**Current:**
The study answers four research questions (RQs). RQ1 asks how much of the teacher accuracy StaticKD retains on labels that do not come from the teacher. The comparison includes two baselines of similar cost, fastText and a support vector machine (SVM) on term frequency–inverse document frequency (TF-IDF) features, and two more expensive small transformers, MiniLM-L6 and DistilmBERT. RQ2 examines which parts of the training recipe matter for this very small student. The parts tested are soft labels, multilingual data, embedding initialization, embedding fine-tuning, token dropout, temperature, and ensembling. RQ3 measures the CPU inference cost of the teacher and how far StaticKD reduces it. RQ4 looks for the languages, labels, and label sources on which StaticKD is weak, and for the factors behind these weaknesses.

**Makna:**
Studi ini menjawab empat research question (RQ). RQ1 menanyakan seberapa besar bagian akurasi teacher yang dipertahankan StaticKD pada label yang tidak berasal dari teacher. Sebagai pembanding dipakai dua baseline berbiaya serupa, yaitu fastText dan support vector machine (SVM) dengan fitur term frequency–inverse document frequency (TF-IDF). Pembanding lainnya adalah MiniLM-L6 dan DistilmBERT, dua transformer kecil yang lebih mahal. RQ2 menelaah bagian mana dari resep training yang penting bagi student yang sangat kecil ini. Bagian yang diuji meliputi soft label, data multibahasa, inisialisasi embedding, fine-tuning embedding, token dropout, temperature, dan ensemble. Pada RQ3, yang diukur adalah biaya inference teacher di CPU dan seberapa jauh StaticKD menurunkan biaya itu. RQ4 mencari bahasa, label, dan sumber label tempat StaticKD lemah, beserta faktor di balik kelemahan itu. Singkatan yang didefinisikan: RQ, SVM, TF-IDF.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### PEN-07 · main.tex baris 62

**Current:**
The answers also show where the accuracy of such a small student comes from. What matters is how many languages and sites the teacher-labeled data cover, and whether the embeddings start from a space shared across languages. The exact probabilities that the teacher assigns to the other topics matter little. Training on the top teacher label alone works as well as training on the full teacher distribution, and a high distillation temperature hurts. Languages that never occur in the training data are classified through embeddings that training leaves largely unchanged, which works because these embeddings share one space with those of the trained languages. Fine-tuning the embeddings therefore helps the training languages but hurts the unseen ones, and a development set in the training languages cannot reveal this trade-off.

**Makna:**
Jawaban-jawaban itu juga menunjukkan dari mana student sekecil ini memperoleh akurasinya. Yang berpengaruh adalah berapa banyak bahasa dan situs yang tercakup dalam data berlabel teacher, dan apakah embedding berangkat dari ruang yang sama untuk semua bahasa. Nilai persis probabilitas teacher untuk topik-topik lain tidak banyak berpengaruh. Melatih student hanya dengan label teratas teacher memberi hasil yang sama baiknya dengan melatihnya memakai distribusi penuh teacher. Temperature distilasi yang tinggi merugikan. Bahasa yang tidak pernah muncul di data training diklasifikasi lewat embedding yang sebagian besar tidak diubah oleh training. Cara ini berhasil karena embedding itu berada di satu ruang dengan embedding bahasa yang dilatih. Akibatnya, fine-tuning embedding membantu bahasa training tetapi merugikan bahasa yang tidak terlihat saat training. Development set dalam bahasa training tidak bisa memperlihatkan trade-off ini.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### PEN-08 · main.tex baris 64

**Current:**
The contributions of this paper are as follows.

**Makna:**
Kalimat pengantar: kontribusi paper ini adalah sebagai berikut.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### PEN-09 · main.tex baris 65

**Current:**
StaticKD, a recipe that distills a multilingual transformer teacher into a table of 17 logits per token, initialized from multilingual static embeddings. The final model takes 34 MB, needs only the numpy and tokenizers libraries, and processes 473 articles per second per core. An ensemble of several trained students folds into the same single table, so it adds no inference cost.

**Makna:**
Kontribusi 1: StaticKD. Resep ini men-distill teacher transformer multibahasa menjadi tabel berisi 17 logit per token, dengan inisialisasi dari static embedding multibahasa. Model finalnya berukuran 34 MB dan hanya membutuhkan library numpy dan tokenizers. Kecepatannya 473 artikel per detik per core. Ensemble dari beberapa student terlatih dilipat menjadi satu tabel yang sama, sehingga tidak menambah biaya inference.

**Locked:** angka 17, 34 MB, 473 · nama numpy, tokenizers

**Paraphrase:**
(tulis di sini)

---

### PEN-10 · main.tex baris 65

**Current:**
A multilingual IPTC test set of 12,744 articles in 47 languages whose editorial labels do not come from the teacher. It comes with a section-to-IPTC mapping table that is checked automatically and reviewed by the first author, deduplication across sources, a contamination check against all training data, and confidence intervals that account for articles from the same site being related. It can be reused to evaluate other IPTC classifiers.

**Makna:**
Kontribusi 2: test set IPTC multibahasa berisi 12,744 artikel dalam 47 bahasa, dengan label editorial yang tidak berasal dari teacher. Test set ini disertai tabel pemetaan rubrik ke IPTC. Tabel itu diperiksa secara otomatis dan ditinjau oleh penulis pertama. Duplikat lintas sumber sudah dihapus, dan kontaminasi diperiksa terhadap seluruh data training. Confidence interval-nya memperhitungkan keterkaitan antarartikel dari situs yang sama. Classifier IPTC lain dapat dievaluasi dengan test set yang sama.

**Locked:** angka 12,744, 47

**Paraphrase:**
(tulis di sini)

---

### PEN-11 · main.tex baris 65

**Current:**
The findings above on where the accuracy of the student comes from, supported by ablations with five seeds per variant and by analyses by language, label, label origin, and source dataset, including languages that are absent from the training data. The accuracy and cost of nine configurations from six model families, StaticKD included, are measured on CPU only, with each process pinned to the fast cores of a hybrid CPU.

**Makna:**
Kontribusi 3: temuan di atas tentang asal akurasi student. Temuan ini didukung oleh ablasi dengan lima seed per varian. Dukungan lain datang dari analisis per bahasa, label, asal label, dan dataset sumber. Bahasa yang tidak ada di data training ikut dianalisis. Akurasi dan biaya diukur hanya di CPU untuk sembilan konfigurasi dari enam keluarga model, dan StaticKD termasuk di dalamnya. Setiap proses dikunci (pinned) ke core cepat pada CPU hybrid.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### PEN-12 · main.tex baris 65

**Current:**
A release of the code, a notebook that reproduces every number in this paper, the models, and the test-set manifest.

**Makna:**
Kontribusi 4: rilis kode, notebook yang mereproduksi setiap angka di paper ini, model, dan manifest test set.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### PEN-13 · main.tex baris 72

**Current:**
Section II reviews related work, Section III describes the data, test set, method, and evaluation protocol, Section IV presents the results, Section V discusses them, Section VI lists the limitations, and Section VII concludes.

**Makna:**
Peta paper: Bagian II membahas penelitian terkait. Data, test set, metode, dan protokol evaluasi dijelaskan di Bagian III. Hasil disajikan di Bagian IV dan dibahas di Bagian V. Bagian VI memuat keterbatasan studi, lalu Bagian VII menutup paper dengan kesimpulan.

**Locked:** rujukan Section II, Section III, Section IV, Section V, Section VI, Section VII

**Paraphrase:**
(tulis di sini)

## II. Related Work

---

### PT-01 · Multilingual News Topic Classification and the IPTC Scheme · main.tex baris 77

**Current:**
Resources for news topic classification usually define their own taxonomy and cover a single language or region. MasakhaNEWS covers 16 languages widely spoken in Africa, English and French included, with seven human-annotated categories [17]. L3Cube-IndicNews uses publisher site categories for 10 Indian languages [19], and a Bangla news dataset also relies on publisher categories [20]. MN-DS is the only public dataset annotated directly with top-level IPTC topics, and it is English only [18]. SIB-200 spans 205 languages, but its items are Flores-200 sentences with seven non-IPTC topics [15]. Kuzman and Ljubešić [2] showed that GPT-4o labels can replace human annotation for training an IPTC classifier, and their follow-up work found fine-tuned encoders more practical than LLMs for large-scale annotation [4]. The only open multilingual IPTC classifier is an encoder with 559.9 million parameters, and no inexpensive IPTC classifier has been evaluated on real news in many languages.

**Makna:**
Subbagian: klasifikasi topik berita multibahasa dan skema IPTC. Sumber data untuk klasifikasi topik berita biasanya memakai taksonomi buatan sendiri dan mencakup satu bahasa atau satu wilayah saja. Pada MasakhaNEWS [17], anotator manusia melabeli berita dengan tujuh kategori. Dataset ini mencakup 16 bahasa yang banyak dituturkan di Afrika, termasuk bahasa Inggris dan Prancis. Dua dataset lain mengambil label dari kategori situs penerbit, yaitu L3Cube-IndicNews untuk 10 bahasa India [19] dan sebuah dataset berita Bangla [20]. Di antara dataset publik, hanya MN-DS [18] yang dianotasi langsung dengan topik IPTC level atas. Isinya berbahasa Inggris saja. SIB-200 [15] mencakup 205 bahasa, tetapi datanya berupa kalimat Flores-200 dengan tujuh topik non-IPTC. Kuzman dan Ljubešić [2] menunjukkan bahwa label GPT-4o bisa menggantikan anotasi manusia untuk melatih classifier IPTC. Studi lanjutan mereka menemukan bahwa encoder hasil fine-tuning lebih praktis daripada LLM untuk anotasi skala besar [4]. Satu-satunya classifier IPTC multibahasa yang terbuka adalah encoder dengan 559.9 juta parameter. Belum ada classifier IPTC murah yang dievaluasi pada berita nyata dalam banyak bahasa.

**Locked:** angka 16, 10, 200, 205, 559.9 · sitasi [17] Adelani et al. 2023; [19] Mirashi et al. 2023; [20] Hossain et al. 2025; [18] Petukhova & Fachada 2023; [15] Adelani et al. 2024; [2] Kuzman & Ljubešić 2025; [4] Kuzman Pungeršek et al. 2026

**Paraphrase:**
(tulis di sini)

---

### PT-02 · Distilling Transformer Classifiers into Compact Students · main.tex baris 80

**Current:**
Knowledge distillation (KD) trains a cheap student model to imitate the output distribution of an expensive teacher model [10], [21]. Both logit vectors are divided by a temperature τ before the softmax. A higher τ flattens the distribution, so the student also learns how probable the teacher finds the wrong classes. The full distribution is called a soft label, and the top class alone is called a hard label. In text classification the student is almost always a transformer, for example DistilBERT [6] or MiniLMv2 [7], including cross-lingual distillation that moves teacher knowledge to languages with little data [22]. The closest prior work is Sparse Distillation [23], which distills RoBERTa-large into a deep averaging network [24] with a very large n-gram table and runs hundreds of times faster on English single-sentence classification tasks. StaticKD differs in three ways. Its table starts from multilingual static embeddings that are already aligned across languages instead of being trained from scratch. Its linear head is folded so that each token stores only 17 numbers. It targets news documents in 69 languages and is evaluated on languages that are missing from the distillation data.

**Makna:**
Subbagian: men-distill classifier transformer menjadi student kecil. Knowledge distillation (KD) melatih model student yang murah untuk meniru distribusi output model teacher yang mahal [10], [21]. Sebelum softmax, vektor logit teacher dan student sama-sama dibagi dengan temperature τ. Nilai τ yang lebih tinggi membuat distribusi lebih rata, sehingga student juga belajar seberapa besar peluang yang diberikan teacher kepada kelas-kelas yang salah. Distribusi penuh disebut soft label, sedangkan kelas teratasnya saja disebut hard label. Pada klasifikasi teks, student hampir selalu berupa transformer, misalnya DistilBERT [6] atau MiniLMv2 [7]. Hal ini juga berlaku pada distilasi lintas bahasa yang memindahkan pengetahuan teacher ke bahasa dengan data sedikit [22]. Di antara penelitian sebelumnya, yang paling dekat dengan StaticKD adalah Sparse Distillation [23]. Metode ini men-distill RoBERTa-large menjadi deep averaging network [24] dengan tabel n-gram yang sangat besar. Pada tugas klasifikasi kalimat tunggal berbahasa Inggris, model hasilnya berjalan ratusan kali lebih cepat. StaticKD berbeda dari metode itu dalam tiga hal. Tabelnya tidak dilatih dari nol, tetapi dimulai dari static embedding multibahasa yang sudah selaras lintas bahasa. Setiap token hanya menyimpan 17 angka karena kepala linearnya dilipat. Sasarannya adalah dokumen berita dalam 69 bahasa, dan evaluasinya juga mencakup bahasa yang tidak ada di data distilasi. Singkatan yang didefinisikan: KD.

**Locked:** angka 17, 69 · sitasi [10] Hinton et al. 2015; [21] Yang et al. 2025; [6] Sanh et al. 2019; [7] Wang et al. 2021; [22] Piperno et al. 2025; [23] Ye et al. 2022; [24] Iyyer et al. 2015 · simbol τ

**Paraphrase:**
(tulis di sini)

---

### PT-03 · Temperature and the Capacity Gap · main.tex baris 82

**Current:**
The success of distillation depends on the capacity gap between teacher and student, which grows as the teacher becomes larger and more expressive than the student. For language models, the optimal teacher size even follows an empirical law with respect to the student size [25]. Temperature is treated as an important hyperparameter that can be learned [26]. The Kullback–Leibler (KL) divergence can be split into a target-class part and a non-target part (dark knowledge) [27], and recent analysis shows that KL under a capacity mismatch distorts the ranking of classes [28]. High agreement between student and teacher (fidelity) also does not always come with better generalization [29]. Nearly all of these findings come from deep students. How temperature and soft labels behave at an extreme gap, from 559.9 million parameters to one linear layer over averaged embeddings, has not been characterized.

**Makna:**
Subbagian: temperature dan capacity gap. Keberhasilan distilasi bergantung pada capacity gap antara teacher dan student. Gap ini melebar ketika teacher menjadi lebih besar dan lebih ekspresif daripada student. Pada language model, ukuran teacher yang optimal bahkan mengikuti hukum empiris terhadap ukuran student [25]. Temperature diperlakukan sebagai hyperparameter penting yang bisa dipelajari [26]. Divergensi Kullback–Leibler (KL) dapat dipecah menjadi bagian kelas target dan bagian non-target (dark knowledge) [27]. Analisis terbaru [28] menunjukkan bahwa KL mendistorsi urutan kelas bila kapasitas teacher dan student tidak sepadan. Ada pula temuan bahwa generalisasi tidak selalu membaik ketika kesesuaian student dengan teacher (fidelity) tinggi [29]. Hampir semua temuan ini berasal dari student yang dalam (deep). Belum ada studi yang mengkarakterisasi perilaku temperature dan soft label pada gap ekstrem, yaitu dari 559.9 juta parameter ke satu layer linear di atas embedding rata-rata. Singkatan yang didefinisikan: KL.

**Locked:** angka 559.9 · sitasi [25] Zhang et al. 2025; [26] Li et al. 2023; [27] Zhao et al. 2022; [28] Wang et al. 2026; [29] Stanton et al. 2021

**Paraphrase:**
(tulis di sini)

---

### PT-04 · Static Embeddings and Efficient CPU Inference · main.tex baris 85

**Current:**
A static embedding gives each token one fixed vector, independent of the surrounding words, so a text vector is simply the mean of its token vectors. Model2Vec [11] and Wada et al. [12] extract such embeddings from sentence transformers, and their averages are competitive sentence embeddings. The potion-multilingual variant of Model2Vec is distilled from BGE-M3 [13] and covers 101 languages. The Model2Vec library also offers a classifier trainer, which adds a 512-unit hidden layer and learns from hard labels [11]. Static embeddings are usually evaluated as general-purpose embeddings, not as distillation students for a specific taxonomy. A survey of efficient natural language processing (NLP) methods recommends reporting inference cost next to accuracy [30], since inference makes up a large share of the energy use of deployed models [5]. Few studies, however, report CPU latency at low thread counts against a quantized teacher.

**Makna:**
Subbagian: static embedding dan inference CPU yang efisien. Static embedding memberi setiap token satu vektor tetap yang tidak bergantung pada kata di sekitarnya, sehingga vektor sebuah teks cukup berupa rata-rata vektor token-tokennya. Embedding semacam ini diekstrak dari sentence transformer oleh Model2Vec [11] dan Wada dkk. [12]. Rata-rata embedding ini menjadi sentence embedding yang kompetitif. Model2Vec memiliki varian multibahasa bernama potion-multilingual. Varian ini di-distill dari BGE-M3 [13] dan mencakup 101 bahasa. Library Model2Vec juga menyediakan trainer classifier yang menambahkan hidden layer 512 unit dan belajar dari hard label [11]. Static embedding biasanya dievaluasi sebagai embedding serbaguna, bukan sebagai student distilasi untuk taksonomi tertentu. Survei metode natural language processing (NLP) yang efisien menganjurkan agar biaya inference dilaporkan bersama akurasi [30], karena inference menyumbang porsi besar penggunaan energi model yang sudah di-deploy [5]. Namun, jarang ada studi yang melaporkan latency CPU pada jumlah thread kecil dengan teacher yang dikuantisasi sebagai pembanding. Singkatan yang didefinisikan: NLP.

**Catatan:** Catatan review: kalimat terakhir adalah klaim literatur tanpa sitasi.

**Locked:** angka 101, 512 · sitasi [11] Tulkens & van Dongen 2024; [12] Wada et al. 2025; [13] Chen et al. 2024; [30] Treviso et al. 2023; [5] Luccioni et al. 2024

**Paraphrase:**
(tulis di sini)

---

### PT-05 · Test Sets with Editorial Labels, Contamination, and Sample Dependence · main.tex baris 88

**Current:**
Publisher site categories have been used as topic labels before [19], usually for one publisher or one region. Many news sites also store the section of each article in machine-readable page metadata, the schema.org articleSection field [16]. This field has not yet been mapped to a standard taxonomy across dozens of languages. Leakage between training and test data also has to be controlled, and near-duplicate removal with MinHash [31] has become standard practice [32]. Significance tests in NLP such as the paired bootstrap [33] usually assume independent samples [34], while articles from the same site are dependent. The cluster bootstrap [35] handles this dependence by resampling clusters instead of documents. Table I summarizes how StaticKD relates to these approaches.

**Makna:**
Subbagian: test set dengan label editorial, kontaminasi, dan dependensi sampel. Kategori situs penerbit sudah pernah dipakai sebagai label topik [19], biasanya untuk satu penerbit atau satu wilayah. Banyak situs berita juga mencatat rubrik setiap artikel di metadata halaman yang bisa dibaca mesin. Metadata itu berupa field articleSection dari schema.org [16]. Sampai sekarang field ini belum dipetakan ke taksonomi standar lintas puluhan bahasa. Kebocoran antara data training dan data test juga harus dikendalikan. Penghapusan near-duplicate dengan MinHash [31] sudah menjadi praktik standar [32]. Di NLP, uji signifikansi seperti paired bootstrap [33] biasanya mengasumsikan sampel yang independen [34], padahal artikel dari situs yang sama saling bergantung. Cluster bootstrap [35] mengatasi dependensi ini dengan me-resample klaster, bukan dokumen. Posisi StaticKD terhadap pendekatan-pendekatan ini dirangkum di Tabel I.

**Locked:** sitasi [19] Mirashi et al. 2023; [16] Guha et al. 2016; [31] Broder 1997; [32] Lee et al. 2022; [33] Koehn 2004; [34] Dror et al. 2018; [35] Field & Welsh 2007 · rujukan Table I · nama articleSection

**Paraphrase:**
(tulis di sini)

[TABEL I — placeholder] Posisi StaticKD dibanding pendekatan terkait (kolom: pendekatan, model saat inference, multibahasa, transfer lintas bahasa, tanpa library deep learning, biaya CPU dilaporkan, label IPTC).

## III. Methodology

---

### MET-01 · Study Design · main.tex baris 114

**Current:**
The study has three parts: building the StaticKD student by distillation, measuring its accuracy against labels that do not come from the teacher, and measuring its inference cost on CPU.

**Makna:**
Subbagian: desain studi. Studi ini terdiri dari tiga bagian: membangun student StaticKD lewat distilasi, mengukur akurasinya terhadap label yang tidak berasal dari teacher, dan mengukur biaya inference-nya di CPU.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### MET-02 · Study Design · main.tex baris 116

**Current:**
Fig. 1 shows the StaticKD pipeline built in the first part. The teacher reads 285,999 unlabeled news articles in 69 languages once, offline, and its 17 topic logits for each article are stored (Sections III-C and III-E). StaticKD is trained to reproduce the full teacher distribution over the 17 topics (Section III-F). The baselines learn from the same articles: the two small transformers from the full distribution, and fastText and TF-IDF + SVM from the top teacher label only. One further fastText model is trained on GPT-4o labels instead, as a reference without the teacher (Section III-G). After training, the linear head of StaticKD is folded into a table of 17 scores per token, and this table is the only part used at inference.

**Makna:**
Gambar 1 menunjukkan pipeline StaticKD yang dibangun pada bagian pertama. Teacher membaca 285,999 artikel berita tak berlabel dalam 69 bahasa satu kali secara offline, dan 17 logit topiknya untuk setiap artikel disimpan (Bagian III-C dan Bagian III-E). StaticKD dilatih untuk mereproduksi distribusi penuh teacher atas 17 topik (Bagian III-F). Baseline belajar dari artikel yang sama: dua transformer kecil dari distribusi penuh, serta fastText dan TF-IDF + SVM dari label teratas teacher saja. Satu model fastText lain dilatih dengan label GPT-4o sebagai pembanding tanpa teacher (Bagian III-G). Setelah training, kepala linear StaticKD dilipat menjadi tabel 17 skor per token, dan hanya tabel ini yang dipakai saat inference.

**Locked:** angka 285,999, 69, 17 · rujukan Fig. 1, Section III-C, Section III-E, Section III-F, Section III-G

**Paraphrase:**
(tulis di sini)

---

### MET-03 · Study Design · main.tex baris 118

**Current:**
Scores against teacher labels show only how closely a model imitates the teacher, and every teacher error that a student copies would count as correct. The second part therefore uses a separate test set whose editorial labels come from newsroom sections, publisher categories, and human annotators (Section III-D). All accuracy comparisons, statistical tests, and subgroup analyses in Section IV use this set. The third part runs every model on the same sample of test articles, on CPU only (Section III-I).

**Makna:**
Skor terhadap label teacher hanya menunjukkan seberapa dekat sebuah model meniru teacher, dan setiap kesalahan teacher yang ditiru student akan terhitung benar. Karena itu bagian kedua memakai test set terpisah yang label editorialnya berasal dari rubrik redaksi, kategori penerbit, dan anotator manusia (Bagian III-D). Semua perbandingan akurasi, uji statistik, dan analisis subgrup di Bagian IV memakai set ini. Bagian ketiga menjalankan setiap model pada sampel artikel uji yang sama, hanya di CPU (Bagian III-I).

**Locked:** rujukan Section III-D, Section IV, Section III-I

**Paraphrase:**
(tulis di sini)

---

### MET-04 · Study Design · main.tex baris 120

**Current:**
Table II lists every data set of the study and its role. All choices of the StaticKD recipe were made on the development set, the development split of EMMediaTopic (1,000 articles in four languages with GPT-4o labels), and the recipe was fixed before the test set was built. No hyperparameter was selected on the test set. One further set informed two choices, the temperature τ=1 and the three-seed ensemble (Section III-F): 320 articles in 16 languages labeled by an LLM (Claude) with the prompt of [2]. The teacher was trained on labels that an LLM (GPT-4o) produced with the same prompt, so these labels are not independent of the teacher, and no reported result uses this set.

**Makna:**
Tabel II mencantumkan setiap set data dalam studi ini beserta perannya. Semua pilihan resep StaticKD dibuat pada development set, yaitu split development EMMediaTopic (1,000 artikel dalam empat bahasa dengan label GPT-4o), dan resep itu sudah ditetapkan sebelum test set dibangun. Tidak ada hyperparameter yang dipilih memakai test set. Satu set lain ikut menentukan dua pilihan, yaitu temperature τ=1 dan ensemble tiga seed (Bagian III-F): 320 artikel dalam 16 bahasa yang dilabeli LLM (Claude) dengan prompt dari [2]. Teacher dilatih dengan label yang dihasilkan LLM (GPT-4o) dengan prompt yang sama, jadi label ini tidak independen dari teacher, dan tidak ada hasil yang dilaporkan memakai set ini.

**Locked:** angka 1,000, 320, 16 · sitasi [2] Kuzman & Ljubešić 2025 · rujukan Table II, Section III-F · simbol τ=1

**Paraphrase:**
(tulis di sini)

[TABEL II — placeholder] Set data dalam studi ini beserta perannya.

[GAMBAR 1 — placeholder] Pipeline StaticKD. Teacher melabeli korpus berita tak berlabel satu kali, secara offline. Student belajar meniru distribusi teacher, lalu kepala linearnya dilipat ke tabel token, sehingga inference hanya mencari dan merata-rata baris tabel. Evaluasi final memakai test set yang labelnya tidak berasal dari teacher. (Diagram TikZ di main.tex; tidak perlu digambar ulang.)

---

### MET-05 · Problem Formulation · main.tex baris 175

**Current:**
Given a news article d in any language, consisting of its title and body truncated to the first 512 words as in [2], a model predicts one label y∈Y among the 17 top-level IPTC topics. The teacher f_T outputs logits z^T(d)∈ℝ^17. The goal is a student f_S whose inference costs O(n) additions for n tokens, without matrix multiplication and without a deep learning library, and whose accuracy against independent labels is as close as possible to that of f_T.

**Makna:**
Subbagian: formulasi masalah. Diberikan artikel berita d dalam bahasa apa pun (judul dan isi, dipotong ke 512 kata pertama seperti di [2]), model memprediksi satu label y dari 17 topik IPTC level atas. Teacher f_T mengeluarkan logit z^T(d) berdimensi 17. Tujuannya student f_S yang biaya inference-nya O(n) penjumlahan untuk n token, tanpa perkalian matriks dan tanpa library deep learning, dan akurasinya terhadap label independen sedekat mungkin dengan f_T.

**Locked:** angka 512, 17 · sitasi [2] Kuzman & Ljubešić 2025 · simbol d, y∈Y, f_T, z^T(d)∈ℝ^17, f_S, O(n), n

**Paraphrase:**
(tulis di sini)

---

### MET-06 · Distillation Data and Development Set · main.tex baris 179

**Current:**
EMMediaTopic 1.0 [9], [2] contains Catalan, Greek, Croatian, and Slovenian articles labeled by GPT-4o. Its training split (20,000 articles) is part of the distillation data. Its development split (1,000 articles, median 218 words) was never used to train the teacher or the student and serves as the development set for choosing the recipe.

**Makna:**
Subbagian: data distilasi dan development set. EMMediaTopic 1.0 [9] [2] berisi artikel berbahasa Katalan, Yunani, Kroasia, dan Slovenia yang dilabeli GPT-4o. Split training-nya (20,000 artikel) menjadi bagian data distilasi. Split development-nya (1,000 artikel, median 218 kata) tidak pernah dipakai untuk melatih teacher maupun student, dan menjadi development set untuk memilih resep.

**Locked:** angka 1.0, 20,000, 1,000, 218 · sitasi [9] Kuzman & Ljubešić 2025; [2] Kuzman & Ljubešić 2025

**Paraphrase:**
(tulis di sini)

---

### MET-07 · Distillation Data and Development Set · main.tex baris 181

**Current:**
Most of the distillation data come from CC-News 2019–2021, a multilingual split [36] of the news archive of Common Crawl. The test set later draws on the same archive for 2024–2026 (CC-NEWS 2024–2026, Section III-D). CC-News 2019–2021 was processed with the following steps.

**Makna:**
Sebagian besar data distilasi berasal dari CC-News 2019-2021, split multibahasa [36] dari arsip berita Common Crawl. Test set nanti mengambil dari arsip yang sama untuk 2024-2026 (CC-NEWS 2024-2026, Bagian III-D). CC-News 2019-2021 diproses dengan langkah-langkah berikut.

**Locked:** angka 2019, 2021, 2024, 2026 · sitasi [36] CloverSearch n.d. · rujukan Section III-D

**Paraphrase:**
(tulis di sini)

---

### MET-08 · Distillation Data and Development Set · main.tex baris 182

**Current:**
Keep only documents whose metadata language agrees with fastText language identification [8].

**Makna:**
Langkah 1: simpan hanya dokumen yang bahasa di metadatanya sama dengan hasil identifikasi bahasa fastText [8].

**Locked:** sitasi [8] Joulin et al. 2017

**Paraphrase:**
(tulis di sini)

---

### MET-09 · Distillation Data and Development Set · main.tex baris 182

**Current:**
Take the title and body with at least 75 words (200 characters for ja, zh, th, my) and truncate to 512 words.

**Makna:**
Langkah 2: ambil judul dan isi dengan minimal 75 kata (200 karakter untuk ja, zh, th, my), lalu potong ke 512 kata.

**Locked:** angka 75, 200, 512

**Paraphrase:**
(tulis di sini)

---

### MET-10 · Distillation Data and Development Set · main.tex baris 182

**Current:**
Keep at most 150 documents per site.

**Makna:**
Langkah 3: simpan paling banyak 150 dokumen per situs.

**Locked:** angka 150

**Paraphrase:**
(tulis di sini)

---

### MET-11 · Distillation Data and Development Set · main.tex baris 182

**Current:**
Form a held-out split by domain: all documents of some sites are set aside, at most 20% per language.

**Makna:**
Langkah 4: bentuk split held-out berdasarkan domain: semua dokumen dari sebagian situs disisihkan, paling banyak 20% per bahasa.

**Locked:** angka 20%

**Paraphrase:**
(tulis di sini)

---

### MET-12 · Distillation Data and Development Set · main.tex baris 182

**Current:**
Add 156,157 documents from training sites only (at most 5,000 per language and 400 per site).

**Makna:**
Langkah 5: tambahkan 156,157 dokumen hanya dari situs training (paling banyak 5,000 per bahasa dan 400 per situs).

**Locked:** angka 156,157, 5,000, 400

**Paraphrase:**
(tulis di sini)

---

### MET-13 · Distillation Data and Development Set · main.tex baris 189

**Current:**
The distillation data contain 285,999 documents in 69 languages from 2,960 sites, with a median of 269 words. A few multilingual sites (for example bbc.com) were set aside in one language but also appear in another language of the distillation data, so their articles were removed from the held-out split. The resulting held-out set has 12,554 documents in 63 languages from 217 sites that never occur in the distillation data. This set has no independent labels, so it measures only agreement with the teacher, defined as the share of documents on which a model predicts the same top label as the teacher.

**Makna:**
Data distilasi berisi 285,999 dokumen dalam 69 bahasa dari 2,960 situs, dengan median 269 kata. Beberapa situs multibahasa (misalnya bbc.com) disisihkan di satu bahasa tetapi juga muncul di bahasa lain dalam data distilasi, jadi artikelnya dibuang dari split held-out. Held-out set yang dihasilkan berisi 12,554 dokumen dalam 63 bahasa dari 217 situs yang tidak pernah muncul di data distilasi. Set ini tidak punya label independen, jadi hanya mengukur agreement dengan teacher, yaitu porsi dokumen yang label teratas prediksinya sama dengan label teratas teacher.

**Locked:** angka 285,999, 69, 2,960, 269, 12,554, 63, 217

**Paraphrase:**
(tulis di sini)

---

### MET-14 · Unified Test Set Construction · main.tex baris 193

**Current:**
The first source is CC-NEWS 2024–2026, sampled as one archive file (WARC) per month from January 2024 to August 2026 (32 files) of the Common Crawl CC-NEWS archive [37]. From each page, the structured metadata blocks in schema.org JSON-LD format [16] of type NewsArticle and its subtypes were extracted, with the fields articleSection, BreadcrumbList, inLanguage, datePublished, isAccessibleForFree, and articleBody. The text comes from articleBody when it has at least 30 words and is otherwise extracted with Trafilatura [38]. Sites that occur in the distillation data or in another evaluation set were removed, which leaves 399,468 articles from new sites.

**Makna:**
Subbagian: konstruksi unified test set. Sumber pertama adalah CC-NEWS 2024-2026, diambil satu file arsip (WARC) per bulan dari Januari 2024 sampai Agustus 2026 (32 file) dari arsip Common Crawl CC-NEWS [37]. Dari setiap halaman diekstrak blok metadata terstruktur berformat schema.org JSON-LD [16] bertipe NewsArticle dan subtipenya, dengan field articleSection, BreadcrumbList, inLanguage, datePublished, isAccessibleForFree, dan articleBody. Teks diambil dari articleBody bila minimal 30 kata; kalau tidak, diekstrak dengan Trafilatura [38]. Situs yang muncul di data distilasi atau di set evaluasi lain dibuang, sehingga tersisa 399,468 artikel dari situs baru.

**Locked:** angka 2024, 2026, 32, 30, 399,468 · sitasi [37] Foundation 2026; [16] Guha et al. 2016; [38] Barbaresi 2021 · nama NewsArticle, articleSection, BreadcrumbList, inLanguage, datePublished, isAccessibleForFree, articleBody

**Paraphrase:**
(tulis di sini)

---

### MET-15 · Unified Test Set Construction · main.tex baris 195

**Current:**
The second source is public datasets. MasakhaNEWS [17] and MN-DS [18] are labeled by humans. L3Cube-IndicNews (LDC split) [19], Bangla news [20], and IndoNews [39] carry publisher categories.

**Makna:**
Sumber kedua adalah dataset publik. MasakhaNEWS [17] dan MN-DS [18] dilabeli manusia. L3Cube-IndicNews (split LDC) [19], berita Bangla [20], dan IndoNews [39] membawa kategori penerbit.

**Locked:** sitasi [17] Adelani et al. 2023; [18] Petukhova & Fachada 2023; [19] Mirashi et al. 2023; [20] Hossain et al. 2025; [39] Research 2021

**Paraphrase:**
(tulis di sini)

---

### MET-16 · Unified Test Set Construction · main.tex baris 197

**Current:**
Section and category labels record where the newsroom placed an article when it was published. Such labels are called editorial labels in this paper. No model that reads the article text produces these labels, so an evaluation on them is not circular with respect to the teacher. The only added step is translating section names onto the official IPTC Media Topic tree (1,085 active nodes). Section names are normalized (case, diacritics) and mapped conservatively. A name is mapped only if the content usually found under that section belongs to one top-level topic. This gives 814 names mapped to 79 nodes. The table deliberately leaves 62 ambiguous names unmapped, for example tech, which can be science and technology or the information technology industry under economy. Likewise, entertainment can be arts or lifestyle, and terrorism can be conflict or crime. Astrology sections are rejected. An automatic check verifies that every target node exists in the IPTC tree, is not retired, and lies under the intended top-level topic. Articles whose sections map to different labels are rejected. MN-DS needs no mapping, because its labels already are IPTC topics. The mapping table was drafted with artificial intelligence assistance, and the first author reviewed all of its 916 rules (814 mapped names and 102 ambiguous, language-specific, and rejecting rules) and accepted them without changes.

**Makna:**
Label rubrik (section) dan kategori mencatat di mana redaksi menempatkan artikel saat diterbitkan. Paper ini menyebut label seperti itu label editorial (editorial labels). Tidak ada model yang membaca teks artikel yang menghasilkan label ini, jadi evaluasi memakai label ini tidak sirkular terhadap teacher. Satu-satunya langkah tambahan adalah menerjemahkan nama rubrik ke pohon IPTC Media Topic resmi (1,085 node aktif). Nama rubrik dinormalisasi (huruf besar-kecil, diakritik) dan dipetakan secara konservatif: sebuah nama hanya dipetakan bila isi yang biasa ada di rubrik itu masuk ke satu topik level atas. Hasilnya 814 nama dipetakan ke 79 node. Tabel pemetaan sengaja membiarkan 62 nama ambigu tidak dipetakan, misalnya tech (bisa science and technology, atau industri teknologi informasi di bawah economy); begitu juga entertainment (arts atau lifestyle) dan terrorism (conflict atau crime). Rubrik astrologi ditolak. Pemeriksaan otomatis memastikan setiap node tujuan ada di pohon IPTC, tidak retired, dan berada di bawah topik level atas yang dimaksud. Artikel yang rubrik-rubriknya terpetakan ke label berbeda ditolak. MN-DS tidak perlu dipetakan karena labelnya sudah topik IPTC. Tabel pemetaan disusun dengan bantuan artificial intelligence, dan penulis pertama meninjau seluruh 916 aturannya (814 nama terpetakan dan 102 aturan ambigu, khusus bahasa, dan penolakan) lalu menerimanya tanpa perubahan.

**Locked:** angka 1,085, 814, 79, 62, 916, 102

**Paraphrase:**
(tulis di sini)

---

### MET-17 · Unified Test Set Construction · main.tex baris 199

**Current:**
Quality and leakage filters are applied in order.

**Makna:**
Kalimat pengantar daftar: filter kualitas dan kebocoran diterapkan secara berurutan.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### MET-18 · Unified Test Set Construction · main.tex baris 200

**Current:**
Publication date on or after 1 January 2024 (CC-NEWS only).

**Makna:**
Filter 1: tanggal terbit pada atau setelah 1 Januari 2024 (hanya CC-NEWS). Tulis tanggal dalam format IEEE: 1 January 2024.

**Locked:** angka 1, 2024

**Paraphrase:**
(tulis di sini)

---

### MET-19 · Unified Test Set Construction · main.tex baris 200

**Current:**
Not behind a paywall.

**Makna:**
Filter 2: tidak berada di balik paywall.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### MET-20 · Unified Test Set Construction · main.tex baris 200

**Current:**
Declared language agrees with fastText language identification when the language is supported.

**Makna:**
Filter 3: bahasa yang dideklarasikan sama dengan identifikasi bahasa fastText, bila bahasanya didukung fastText.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### MET-21 · Unified Test Set Construction · main.tex baris 200

**Current:**
At least 75 words.

**Makna:**
Filter 4: minimal 75 kata.

**Locked:** angka 75

**Paraphrase:**
(tulis di sini)

---

### MET-22 · Unified Test Set Construction · main.tex baris 200

**Current:**
Deduplication of uniform resource locators (URLs), identical texts, and near-duplicates (MinHash [31], Jaccard ≥ 0.7 [32]) across all sources.

**Makna:**
Filter 5: deduplikasi URL, teks identik, dan near-duplicate (MinHash [31], Jaccard >= 0.7 [32]) lintas semua sumber. Singkatan URL didefinisikan di sini (uniform resource locator).

**Locked:** sitasi [31] Broder 1997; [32] Lee et al. 2022 · simbol ≥ 0.7

**Paraphrase:**
(tulis di sini)

---

### MET-23 · Unified Test Set Construction · main.tex baris 200

**Current:**
Contamination: an article is dropped when ≥ 30% of its word 8-grams occur in any of about 300 thousand training or evaluation documents. This filter removed 50 articles, mostly from MasakhaNEWS, which also draws on BBC.

**Makna:**
Filter 6, kontaminasi: artikel dibuang bila >= 30% word 8-gram-nya muncul di salah satu dari sekitar 300 ribu dokumen training atau evaluasi. Filter ini membuang 50 artikel, sebagian besar dari MasakhaNEWS, yang juga mengambil dari BBC.

**Locked:** angka 8, 300, 50 · simbol ≥ 30

**Paraphrase:**
(tulis di sini)

---

### MET-24 · Unified Test Set Construction · main.tex baris 209

**Current:**
Sampling takes at most 50 articles for each pair of language and label, preferring human-labeled sources, then publisher categories, then JSON-LD sections. Languages with fewer than 30 articles are dropped. The number of articles per site is not capped, because most language–label pairs come from few sites and such a cap would discard data without adding diversity. Articles from the same site tend to resemble each other, so the evaluation resamples whole sites when it computes confidence intervals (Section III-H), and Section IV-A repeats the comparison with at most five articles per site.

**Makna:**
Sampling mengambil paling banyak 50 artikel untuk setiap pasangan bahasa dan label, dengan urutan prioritas: sumber berlabel manusia, lalu kategori penerbit, lalu rubrik JSON-LD. Bahasa dengan kurang dari 30 artikel dibuang. Jumlah artikel per situs tidak dibatasi, karena kebanyakan pasangan bahasa-label hanya berasal dari sedikit situs, dan batas seperti itu hanya membuang data tanpa menambah keragaman. Artikel dari situs yang sama cenderung mirip, jadi evaluasi me-resample situs secara utuh saat menghitung confidence interval (Bagian III-H), dan Bagian IV-A mengulang perbandingan dengan paling banyak lima artikel per situs.

**Locked:** angka 50, 30 · rujukan Section III-H, Section IV-A

**Paraphrase:**
(tulis di sini)

---

### MET-25 · Unified Test Set Construction · main.tex baris 211

**Current:**
The final test set contains 12,744 articles in 47 languages, with 17 labels and 1,227 sites or sources and a median of 313 words. Of these, 4,094 articles (32.1%) carry human annotations, 2,600 (20.4%) publisher categories, and 6,050 (47.5%) JSON-LD sections. The type of label of an article (human annotation, publisher category, or JSON-LD section) is called its label origin. By the amount of distillation data in their language, 13 languages have none (for example ha, yo, ig, bn, pa), 9 have fewer than 500 documents, and 25 have at least 500. Site diversity is measured by the effective number of sites, 1/Σ_s q_s^2, where q_s is the share of the articles of a language that come from site s. A source dataset without URLs counts as one site. By this measure, 13 languages have at least 10 effective sites, while 27 languages come from practically one publisher. Table III summarizes the sources and Fig. 2 shows how many articles each language has per label.

**Makna:**
Test set final berisi 12,744 artikel dalam 47 bahasa, dengan 17 label dan 1,227 situs atau sumber, median 313 kata. Dari jumlah itu, 4,094 artikel (32.1%) berlabel anotasi manusia, 2,600 (20.4%) kategori penerbit, dan 6,050 (47.5%) rubrik JSON-LD. Jenis label sebuah artikel (anotasi manusia, kategori penerbit, atau rubrik JSON-LD) disebut asal label (label origin). Menurut jumlah data distilasi di bahasanya: 13 bahasa tidak punya data sama sekali (misalnya ha, yo, ig, bn, pa), 9 bahasa punya kurang dari 500 dokumen, dan 25 bahasa punya minimal 500. Keragaman situs diukur dengan jumlah situs efektif, 1/Σ q_s^2, dengan q_s porsi artikel suatu bahasa yang berasal dari situs s. Dataset sumber tanpa URL dihitung sebagai satu situs. Dengan ukuran ini, 13 bahasa punya minimal 10 situs efektif, sedangkan 27 bahasa praktis hanya dari satu penerbit. Tabel III merangkum sumbernya dan Gambar 2 menunjukkan jumlah artikel setiap bahasa per label.

**Locked:** angka 12,744, 47, 17, 1,227, 313, 4,094, 32.1%, 2,600, 20.4%, 6,050, 47.5%, 13, 9, 500, 25, 10, 27 · rujukan Table III, Fig. 2 · simbol 1/Σ_s q_s^2, q_s, s

**Paraphrase:**
(tulis di sini)

[TABEL III — placeholder] Komposisi unified test set per sumber.

[GAMBAR 2 — placeholder] Jumlah artikel di unified test set per bahasa dan label (paling banyak 50 per pasangan bahasa-label). Asal label di dalam kurung adalah asal label dominan untuk bahasa tersebut.

---

### MET-26 · Teacher and Distillation Labels · main.tex baris 245

**Current:**
The teacher is the IPTC classifier of [2], published as classla/multilingual-IPTC-news-topic-classifier. It is an XLM-RoBERTa-large model with 24 layers and 559.9 million parameters, and its architecture limits the input to 512 XLM-R tokens. The 512-word input of 60.7% of the test articles exceeds this limit, and for those articles the teacher reads about 287 of 438 words (medians). For every distillation document the teacher produces a logit vector z^T(d)∈ℝ^17, which is stored in full. Labeling ran once in fp16 on an NVIDIA RTX 4050 Laptop GPU (6 GB), with batches sorted by text length. Measured on a fixed sample of 5,000 documents, the teacher labels 50.1 documents per second, so labeling the whole distillation data takes about 1.58 GPU hours. The teacher label distribution on CC-News 2019–2021 is plausible (politics 16.5%, economy 12.7%, sport 11.6%, weather 1.3%), and its mean confidence per language ranges from 0.90 to 1.00.

**Makna:**
Subbagian: teacher dan label distilasi. Teacher adalah classifier IPTC dari [2], dipublikasikan sebagai classla/multilingual-IPTC-news-topic-classifier. Model ini XLM-RoBERTa-large dengan 24 layer dan 559.9 juta parameter, dan arsitekturnya membatasi input ke 512 token XLM-R. Input 512 kata dari 60.7% artikel uji melebihi batas ini, dan untuk artikel tersebut teacher hanya membaca sekitar 287 dari 438 kata (median). Untuk setiap dokumen distilasi, teacher menghasilkan vektor logit z^T(d) berdimensi 17, yang disimpan utuh. Pelabelan dijalankan sekali dalam fp16 di GPU NVIDIA RTX 4050 Laptop (6 GB), dengan batch diurutkan menurut panjang teks. Diukur pada sampel tetap 5,000 dokumen, teacher melabeli 50.1 dokumen per detik, sehingga melabeli seluruh data distilasi butuh sekitar 1.58 jam GPU. Distribusi label teacher di CC-News 2019-2021 masuk akal (politics 16.5%, economy 12.7%, sport 11.6%, weather 1.3%), dan rata-rata confidence per bahasa berkisar 0.90 sampai 1.00.

**Locked:** angka 24, 559.9, 512, 60.7%, 287, 438, 4050, 6 GB, 5,000, 50.1, 1.58, 2019, 2021, 16.5%, 12.7%, 11.6%, 1.3%, 0.90, 1.00 · sitasi [2] Kuzman & Ljubešić 2025 · simbol z^T(d)∈ℝ^17 · nama classla/multilingual-IPTC-news-topic-classifier

**Paraphrase:**
(tulis di sini)

---

### MET-27 · The StaticKD Student · main.tex baris 249

**Current:**
The student is built on potion-multilingual-128M, the multilingual static embedding model of Model2Vec [11], hereafter called potion. A document d is tokenized into t_1,…,t_n with the Unigram tokenizer of potion, which has 500,353 tokens, so that every token has a pre-trained embedding. Special tokens are not used, unknown tokens are dropped, and the length is capped at 1,024 tokens. Averaging has no position limit, so the cap only bounds the cost, and only 5.4% of the test articles exceed it. Each token has an embedding e_t∈ℝ^256, and

**Makna:**
Subbagian: student StaticKD. Student dibangun di atas potion-multilingual-128M, model static embedding multibahasa dari Model2Vec [11], yang selanjutnya disebut potion. Dokumen d ditokenisasi menjadi t_1 ... t_n dengan Unigram tokenizer milik potion, yang punya 500,353 token, sehingga setiap token punya embedding pra-latih. Special token tidak dipakai, token tak dikenal dibuang, dan panjang dibatasi 1,024 token. Perataan tidak punya batas posisi, jadi batas ini hanya membatasi biaya, dan hanya 5.4% artikel uji yang melebihinya. Tiap token punya embedding e_t berdimensi 256, dan [kalimat berlanjut ke Persamaan (1)].

**Locked:** angka 500,353, 1,024, 5.4% · sitasi [11] Tulkens & van Dongen 2024 · simbol d, t_1,…,t_n, e_t∈ℝ^256

**Paraphrase:**
(tulis di sini)

[PERSAMAAN (1) — placeholder] Persamaan student: h(d) = rata-rata embedding token dokumen; z^S(d) = W dikali dropout(h(d)) ditambah b. Jangan ditulis ulang; salin persamaannya apa adanya.

---

### MET-28 · The StaticKD Student · main.tex baris 255

**Current:**
with W∈ℝ^17× 256 and dropout 0.1 during training. The embedding matrix E is initialized from potion, whose embeddings for 101 languages are distilled from BGE-M3 [13]. This initialization places the tokens of these 101 languages in one shared space before training starts. Section IV-C compares it with a random initialization.

**Makna:**
Lanjutan setelah Persamaan (1): dengan W berukuran 17 x 256 dan dropout 0.1 saat training. Matriks embedding E diinisialisasi dari potion, yang embedding-nya untuk 101 bahasa di-distill dari BGE-M3 [13]. Inisialisasi ini menempatkan token dari 101 bahasa tersebut di satu ruang yang sama sebelum training dimulai. Bagian IV-C membandingkannya dengan inisialisasi acak.

**Locked:** angka 0.1, 101 · sitasi [13] Chen et al. 2024 · rujukan Section IV-C · simbol W∈ℝ^17× 256, E

**Paraphrase:**
(tulis di sini)

---

### MET-29 · The StaticKD Student · main.tex baris 257

**Current:**
The student learns from the stored teacher logits with the loss

**Makna:**
Student belajar dari logit teacher yang disimpan dengan loss pada persamaan berikut.

**Locked:** —

**Paraphrase:**
(tulis di sini)

[PERSAMAAN (2) — placeholder] Loss distilasi: L_KD = tau^2 dikali divergensi KL antara p^T dan p^S, dengan tau = 1. Salin apa adanya.

---

### MET-30 · The StaticKD Student · main.tex baris 262

**Current:**
where p^T=softmax(z^T/τ) and p^S=softmax(z^S/τ) are the teacher and student distributions. The value τ=1 was chosen during development, and Section IV-C reports τ∈{0.5,2,4}. E, W, and b are trained together. E uses SparseAdam (η=10^-3), which updates only the rows of tokens that occur in the current batch. Tokens that never occur in the training documents therefore keep their potion embeddings, a property that Section V returns to. W and b use AdamW (η=3· 10^-3, weight decay 10^-4). The batch size is 64 and training runs for 6 epochs. As a cheap augmentation, each token of a training document is dropped with probability 0.2 at every step (token dropout), so that the model does not rely on a few keywords. Internal validation uses 3% of the distillation data (8,579 documents), and the epoch with the highest agreement with the teacher is kept.

**Makna:**
Lanjutan setelah Persamaan (2): p^T = softmax(z^T/τ) dan p^S = softmax(z^S/τ) adalah distribusi teacher dan student. Nilai τ=1 dipilih selama pengembangan, dan Bagian IV-C melaporkan τ ∈ {0.5, 2, 4}. E, W, dan b dilatih bersama. E memakai SparseAdam (η = 10^-3), yang hanya meng-update baris token yang muncul di batch saat itu. Karena itu token yang tidak pernah muncul di dokumen training tetap memakai embedding potion-nya, sifat yang dibahas lagi di Bagian V. W dan b memakai AdamW (η = 3·10^-3, weight decay 10^-4). Batch size 64 dan training berjalan 6 epoch. Sebagai augmentasi murah, setiap token dokumen training dibuang dengan probabilitas 0.2 di setiap langkah (token dropout), supaya model tidak bergantung pada sedikit kata kunci. Validasi internal memakai 3% data distilasi (8,579 dokumen), dan epoch dengan agreement tertinggi terhadap teacher yang disimpan.

**Locked:** angka 64, 6, 0.2, 3%, 8,579 · rujukan Section IV-C, Section V · simbol p^T=softmax(z^T/τ), p^S=softmax(z^S/τ), τ=1, τ∈{0.5,2,4}, E, W, b, η=10^-3, η=3· 10^-3, 10^-4

**Paraphrase:**
(tulis di sini)

---

### MET-31 · The StaticKD Student · main.tex baris 264

**Current:**
Because the classification head is linear, (1) can be rewritten as

**Makna:**
Kalimat pengantar Persamaan (3): karena kepala klasifikasi linear, Persamaan (1) bisa ditulis ulang sebagai [Persamaan (3)].

**Locked:** rujukan (1)

**Paraphrase:**
(tulis di sini)

[PERSAMAAN (3) — placeholder] Pelipatan kepala: W dikali rata-rata embedding ditambah b sama dengan rata-rata baris tabel T ditambah b. Salin apa adanya.

---

### MET-32 · The StaticKD Student · main.tex baris 269

**Current:**
with the table T=EW^ᵀ∈ℝ^|V|× 17. The folding step computes T once after training. Row T_t then holds the 17 topic scores that token t contributes to every article that contains it. The production model consists only of T (fp16), b, and the tokenizer, and Algorithm 1 lists the whole inference procedure. The same argument covers an ensemble. Averaging the logits of K students trained with different seeds gives the same result as one student with table T̄=1/KΣ_k T^(k) and bias b̄, because (3) is linear in T. Three seeds (0, 1, and 2) were trained during development, and the final StaticKD model averages their tables (K=3). It has 8.5 million parameters and a size of 34 MB.

**Makna:**
Lanjutan setelah Persamaan (3): dengan tabel T = E W^T berukuran |V| x 17. Langkah folding menghitung T satu kali setelah training. Baris T_t lalu berisi 17 skor topik yang disumbangkan token t ke setiap artikel yang memuatnya. Model produksi hanya terdiri dari T (fp16), b, dan tokenizer, dan Algoritma 1 mencantumkan seluruh prosedur inference. Argumen yang sama berlaku untuk ensemble. Merata-ratakan logit dari K student dengan seed berbeda memberi hasil yang sama dengan satu student bertabel T-bar = (1/K) jumlah T^(k) dan bias b-bar, karena Persamaan (3) linear terhadap T. Tiga seed (0, 1, dan 2) dilatih selama pengembangan, dan model StaticKD final merata-ratakan tabel ketiganya (K=3). Model ini punya 8.5 juta parameter dan berukuran 34 MB.

**Locked:** angka 17, 0, 1, 2, 8.5, 34 MB · rujukan Algorithm 1, (3) · simbol T=EW^ᵀ∈ℝ^|V|× 17, T, T_t, t, b, K, T̄=1/KΣ_k T^(k), b̄, K=3

**Paraphrase:**
(tulis di sini)

[ALGORITMA 1 — placeholder] Algoritma inference StaticKD untuk satu artikel: tokenisasi artikel (dengan batas panjang token dan tanpa token tak dikenal), rata-ratakan baris tabel T-bar untuk token-token itu lalu tambahkan bias b-bar, kemudian ambil topik IPTC dengan skor tertinggi. Salin apa adanya.

---

### MET-33 · The StaticKD Student · main.tex baris 282

**Current:**
The internal structure of the Unigram tokenizer needs much more random-access memory (RAM) than the table itself (16 MB). A compact variant shrinks that structure by removing token pieces that occur fewer than 10 times in the distillation data, keeping single characters. Its vocabulary has 335,441 tokens and the model takes 23 MB. Table IV lists the hyperparameters of all models.

**Makna:**
Struktur internal Unigram tokenizer butuh RAM jauh lebih besar daripada tabelnya sendiri (16 MB). Varian compact mengecilkan struktur itu dengan membuang potongan token yang muncul kurang dari 10 kali di data distilasi, tetapi tetap menyimpan karakter tunggal. Vocabulary-nya 335,441 token dan modelnya 23 MB. Tabel IV mencantumkan hyperparameter semua model. Singkatan RAM (random-access memory) didefinisikan di sini.

**Locked:** angka 16 MB, 10, 335,441, 23 MB · rujukan Table IV

**Paraphrase:**
(tulis di sini)

[TABEL IV — placeholder] Hyperparameter semua model.

---

### MET-34 · Baselines · main.tex baris 323

**Current:**
All baselines marked + KD are trained on the same distillation data (285,999 documents) with targets from the same teacher. fastText + KD [8] is trained on the top teacher label with word tokens (plus character n-grams) or XLM-R subwords, together with a quantized variant (.ftz). As a reference equivalent to the labeled data available to [2], fastText is also trained only on the GPT-4o labels of the EMMediaTopic training split. TF-IDF + SVM + KD is the non-neural baseline of Kuzman and Ljubešić (TF-IDF features with a support vector classifier), trained on the top teacher label over XLM-R subwords. The hyperparameters of these non-transformer baselines were set once, as listed in Table IV, without a search. MiniLM-L6 + KD uses mMiniLMv2-L6-H384, distilled from XLM-R-large [7], with the temperature τ∈{1,2} chosen on the development set. DistilmBERT + KD uses distilbert-base-multilingual-cased [6] with the same recipe. Both transformers read at most 256 tokens, which truncates 91.1% (MiniLM-L6) and 93.2% (DistilmBERT) of the test articles to about 142 and 116 words. Both are exported to ONNX fp32 for the CPU benchmark. The ONNX int8 teacher is a dynamic int8 quantized export of the teacher and is its fastest CPU configuration.

**Makna:**
Subbagian: baseline. Semua baseline bertanda + KD dilatih pada data distilasi yang sama (285,999 dokumen) dengan target dari teacher yang sama. fastText + KD [8] dilatih pada label teratas teacher dengan token kata (plus character n-gram) atau subword XLM-R, ditambah varian terkuantisasi (.ftz). Sebagai pembanding yang setara dengan data berlabel yang dimiliki [2], fastText juga dilatih hanya pada label GPT-4o dari split training EMMediaTopic. TF-IDF + SVM + KD adalah baseline non-neural milik Kuzman dan Ljubešić (fitur TF-IDF dengan support vector classifier), dilatih pada label teratas teacher di atas subword XLM-R. Hyperparameter baseline non-transformer ini ditetapkan sekali, seperti di Tabel IV, tanpa pencarian. MiniLM-L6 + KD memakai mMiniLMv2-L6-H384 (hasil distilasi dari XLM-R-large) [7], dengan temperature τ ∈ {1, 2} yang dipilih pada development set. DistilmBERT + KD memakai distilbert-base-multilingual-cased [6] dengan resep yang sama. Kedua transformer hanya membaca paling banyak 256 token, sehingga memotong 91.1% (MiniLM-L6) dan 93.2% (DistilmBERT) artikel uji menjadi sekitar 142 dan 116 kata. Keduanya di-export ke ONNX fp32 untuk benchmark CPU. Teacher ONNX int8 adalah export teacher yang dikuantisasi int8 secara dinamis, dan merupakan konfigurasi CPU tercepatnya.

**Locked:** angka 285,999, 256, 91.1%, 93.2%, 142, 116 · sitasi [8] Joulin et al. 2017; [2] Kuzman & Ljubešić 2025; [7] Wang et al. 2021; [6] Sanh et al. 2019 · rujukan Table IV · simbol τ∈{1,2} · nama .ftz, distilbert-base-multilingual-cased

**Paraphrase:**
(tulis di sini)

---

### MET-35 · Baselines · main.tex baris 325

**Current:**
Sparse Distillation [23], the closest prior work, and the classifier trainer of Model2Vec were not run as separate baselines (Section VI). Parts of both are still covered. fastText + KD is a bag-of-n-grams model with averaging and a linear head, trained on the same teacher labels, and the random-initialization ablation (Section III-J) trains the embedding table from scratch, as Sparse Distillation does. The frozen-embedding ablation trains only a linear head on top of potion and thus acts as an off-the-shelf Model2Vec baseline with a distilled head.

**Makna:**
Sparse Distillation [23], karya terdekat, dan trainer classifier Model2Vec tidak dijalankan sebagai baseline tersendiri (Bagian VI). Sebagian keduanya tetap tercakup. fastText + KD adalah model bag-of-n-grams dengan perataan dan kepala linear, dilatih dengan label teacher yang sama, dan ablasi inisialisasi acak (Bagian III-J) melatih tabel embedding dari nol, seperti Sparse Distillation. Ablasi embedding beku hanya melatih kepala linear di atas potion, sehingga berperan sebagai baseline Model2Vec siap pakai dengan kepala hasil distilasi.

**Locked:** sitasi [23] Ye et al. 2022 · rujukan Section VI, Section III-J

**Paraphrase:**
(tulis di sini)

---

### MET-36 · Evaluation Protocol and Statistical Tests · main.tex baris 329

**Current:**
The main metric is macro-F1 over the labels present in the reference, as in the evaluation code of [2], because the label distribution is imbalanced. The evaluation also reports accuracy, macro-F1 per language averaged over languages so that large languages do not dominate, and agreement with the teacher on the held-out set.

**Makna:**
Subbagian: protokol evaluasi dan uji statistik. Metrik utama adalah macro-F1 atas label yang ada di referensi, seperti kode evaluasi [2], karena distribusi label tidak seimbang. Evaluasi juga melaporkan akurasi, macro-F1 per bahasa yang dirata-rata antarbahasa (supaya bahasa besar tidak mendominasi), dan agreement dengan teacher pada held-out set.

**Locked:** sitasi [2] Kuzman & Ljubešić 2025

**Paraphrase:**
(tulis di sini)

---

### MET-37 · Evaluation Protocol and Statistical Tests · main.tex baris 331

**Current:**
95% confidence intervals come from a percentile bootstrap with 1,000 resamples. On the test set, the resampling unit is the site, or the source dataset when no URL is available. This site-cluster bootstrap [35] draws whole sites, so related articles from one site stay together and the intervals are not made too narrow by treating them as independent. On the development set, the unit is the document. Two models on the same documents are compared with a paired (cluster) bootstrap with 2,000 resamples for Δmacro-F1 [33] and an exact McNemar test for accuracy [40], with Holm correction [41] within each set. Each ablation variant uses five seeds, and the final recipe uses ten. Differences between variants are tested with Welch tests at the seed level, Holm-corrected. Whether a difference holds consistently across languages is tested with a Wilcoxon signed-rank test on per-language macro-F1 and accuracy [34]. Subgroup analyses cover label origin, region, the amount of distillation data of the language, teacher pre-training coverage (whether the language is among the 100 languages on which XLM-R was pre-trained [3]), site diversity, script, language, and label. Per-language properties are related to performance with Spearman correlations and, across scripts, with a Kruskal–Wallis test. Two per-language quantities are used there. The accuracy gap is the StaticKD accuracy minus the teacher accuracy, so a negative gap means that StaticKD is less accurate. The token coverage is the share of token occurrences in the test articles of a language whose token occurs at least 10 times in the distillation data; the embeddings of rarer tokens are rarely updated during training (Section III-F). Calibration is measured with the expected calibration error (ECE, 15 bins) [42], because the cascade mode (Section III-I) routes articles by the confidence of StaticKD.

**Makna:**
Confidence interval 95% berasal dari percentile bootstrap dengan 1,000 resample. Di test set, unit resample-nya adalah situs, atau dataset sumber bila tidak ada URL. Site-cluster bootstrap [35] ini mengambil situs secara utuh, sehingga artikel yang saling terkait dari satu situs tetap bersama dan interval tidak menjadi terlalu sempit karena dianggap independen. Di development set, unitnya dokumen. Dua model pada dokumen yang sama dibandingkan dengan paired (cluster) bootstrap 2,000 resample untuk selisih macro-F1 [33] dan uji McNemar exact untuk akurasi [40], dengan koreksi Holm [41] di dalam setiap set. Setiap varian ablasi memakai lima seed, dan resep final sepuluh. Perbedaan antarvarian diuji dengan uji Welch di level seed, dikoreksi Holm. Konsistensi perbedaan antarbahasa diuji dengan Wilcoxon signed-rank pada macro-F1 dan akurasi per bahasa [34]. Analisis subgrup mencakup asal label, wilayah, jumlah data distilasi bahasa, cakupan pre-training teacher (apakah bahasa itu termasuk 100 bahasa yang dipakai untuk pre-training XLM-R [3]), keragaman situs, aksara, bahasa, dan label. Sifat per bahasa dikaitkan dengan kinerja memakai korelasi Spearman dan, antaraksara, uji Kruskal-Wallis. Dua besaran per bahasa dipakai di sana. Accuracy gap adalah akurasi StaticKD dikurangi akurasi teacher, jadi gap negatif berarti StaticKD kurang akurat. Token coverage adalah porsi kemunculan token di artikel uji suatu bahasa yang tokennya muncul minimal 10 kali di data distilasi; embedding token yang lebih jarang jarang di-update selama training (Bagian III-F). Kalibrasi diukur dengan expected calibration error (ECE, 15 bin) [42], karena mode cascade (Bagian III-I) mengarahkan artikel berdasarkan confidence StaticKD. Singkatan yang didefinisikan: ECE.

**Locked:** angka 95%, 1,000, 2,000, 100, 10, 15 · sitasi [35] Field & Welsh 2007; [33] Koehn 2004; [40] McNemar 1947; [41] Holm 1979; [34] Dror et al. 2018; [3] Conneau et al. 2020; [42] Guo et al. 2017 · rujukan Section III-F, Section III-I · simbol Δ

**Paraphrase:**
(tulis di sini)

---

### MET-38 · Efficiency Protocol · main.tex baris 335

**Current:**
The benchmark runs on CPU only, with the GPU hidden. Each model runs in a fresh process, and the thread count is pinned in every library (OMP, MKL, OpenBLAS, ONNX Runtime, tokenizers). Latency is measured with one article per call, as in a streaming setting (p50 and p95), and throughput with batches of 64, or 8 for transformers. Model RAM is the increase in resident set size after loading the model. The text sample is drawn at random from the unified test set and is the same for every model: 30 latency and 48 throughput documents for the teacher and the transformers, and 500 and 3,000 for the light models. All models are measured in one session on an idle machine. StaticKD reads up to 1,024 tokens per article while the teacher stops at 512, so the speed comparison does not favor StaticKD. In cascade mode, StaticKD decides the articles on which its top probability is at least a threshold θ and passes the rest to the ONNX int8 teacher. With a share s of articles decided by StaticKD and single-core throughputs r_S of StaticKD and r_T of the teacher, the effective throughput of the cascade is 1/(1/r_S+(1-s)/r_T).

**Makna:**
Subbagian: protokol efisiensi. Benchmark berjalan hanya di CPU dengan GPU disembunyikan. Setiap model dijalankan di proses baru, dan jumlah thread dikunci di semua library (OMP, MKL, OpenBLAS, ONNX Runtime, tokenizers). Latency diukur dengan satu artikel per panggilan seperti skenario streaming (p50 dan p95), dan throughput dengan batch 64, atau 8 untuk transformer. RAM model adalah kenaikan resident set size setelah model dimuat. Sampel teks diambil acak dari unified test set dan sama untuk semua model: 30 dokumen latency dan 48 dokumen throughput untuk teacher dan transformer, serta 500 dan 3,000 untuk model ringan. Semua model diukur dalam satu sesi pada mesin yang idle. StaticKD membaca sampai 1,024 token per artikel sementara teacher berhenti di 512, jadi perbandingan kecepatan ini tidak menguntungkan StaticKD. Dalam mode cascade, StaticKD memutuskan artikel yang probabilitas tertingginya minimal ambang θ dan meneruskan sisanya ke teacher ONNX int8. Dengan porsi s artikel yang diputuskan StaticKD serta throughput single-core r_S untuk StaticKD dan r_T untuk teacher, throughput efektif cascade adalah 1/(1/r_S + (1-s)/r_T).

**Locked:** angka 64, 8, 30, 48, 500, 3,000, 1,024, 512 · simbol θ, s, r_S, r_T, 1/(1/r_S+(1-s)/r_T) · nama tokenizers

**Paraphrase:**
(tulis di sini)

---

### MET-39 · Efficiency Protocol · main.tex baris 337

**Current:**
The machine is a laptop with an Intel Core Ultra 7 155H, 31 GB of RAM, and Windows 11. This CPU is hybrid, with 6 performance cores (P-cores), 8 slower efficiency cores (E-cores), and 2 low-power E-cores. Without pinning, the operating system moves threads to the slow cores. Each process is therefore pinned to physical P-cores (logical CPU 0 for one core; logical CPUs 0, 10, 12, and 14 for four cores), which approximates a small server with uniform cores.

**Makna:**
Mesinnya laptop dengan Intel Core Ultra 7 155H, RAM 31 GB, dan Windows 11. CPU ini hybrid: 6 performance core (P-core), 8 efficiency core (E-core) yang lebih lambat, dan 2 low-power E-core. Tanpa pinning, sistem operasi memindahkan thread ke core yang lambat. Karena itu setiap proses di-pin ke P-core fisik (logical CPU 0 untuk satu core; logical CPU 0, 10, 12, dan 14 untuk empat core), yang mendekati server kecil dengan core seragam.

**Locked:** angka 7, 31 GB, 11, 6, 8, 2, 0, 10, 12, 14

**Paraphrase:**
(tulis di sini)

---

### MET-40 · Experimental Design and Implementation Details · main.tex baris 341

**Current:**
Table IX lists the 60 runs of the final recipe and its ablations. Each ablation variant changes one factor of the final recipe: hard labels instead of soft labels; EMMediaTopic data only (4 languages, 10 epochs); 130 thousand documents without the extra CC-News 2019–2021 data; random initialization with the same standard deviation as potion; frozen embeddings; no token dropout; a 512-unit multilayer perceptron (MLP) head; and τ∈{0.5, 2, 4}. Twelve further runs during development tested four additions to the recipe with three seeds each (bigram features, idf-weighted pooling, documents weighted by teacher confidence, and an extra loss on the GPT-4o labels). None of them differs significantly from the final recipe on the development set, and none changes the test macro-F1 by more than 0.004, so these variants are left out of the recipe and of Table IX. One StaticKD run takes 5.2 minutes on average on the same GPU. The implementation uses Python 3.12, NumPy 2.5, PyTorch 2.6, transformers 5.17, tokenizers 0.23, ONNX Runtime 1.30, scikit-learn 1.9, and fastText 0.9.2. The seed, library versions, and training history of every run are stored with the model.

**Makna:**
Subbagian: desain eksperimen dan detail implementasi. Tabel IX mencantumkan 60 run resep final dan ablasinya. Setiap varian ablasi mengubah satu faktor dari resep final: hard label alih-alih soft label; hanya data EMMediaTopic (4 bahasa, 10 epoch); 130 ribu dokumen tanpa data tambahan CC-News 2019-2021; inisialisasi acak dengan standar deviasi yang sama dengan potion; embedding beku; tanpa token dropout; kepala multilayer perceptron (MLP) 512 unit; dan τ ∈ {0.5, 2, 4}. Dua belas run lain selama pengembangan menguji empat tambahan pada resep dengan tiga seed masing-masing (fitur bigram, pooling berbobot idf, dokumen berbobot confidence teacher, dan loss tambahan pada label GPT-4o). Tidak satu pun berbeda signifikan dari resep final di development set, dan tidak satu pun mengubah macro-F1 uji lebih dari 0.004, sehingga varian-varian ini tidak dimasukkan ke resep maupun ke Tabel IX. Satu run StaticKD rata-rata butuh 5.2 menit di GPU yang sama. Implementasinya memakai Python 3.12, NumPy 2.5, PyTorch 2.6, transformers 5.17, tokenizers 0.23, ONNX Runtime 1.30, scikit-learn 1.9, dan fastText 0.9.2. Seed, versi library, dan riwayat training setiap run disimpan bersama modelnya.

**Locked:** angka 60, 4, 10, 130, 2019, 2021, 512, 0.004, 5.2, 3.12, 2.5, 2.6, 5.17, 0.23, 1.30, 1.9, 0.9 · rujukan Table IX · simbol τ∈{0.5, 2, 4} · nama tokenizers

**Paraphrase:**
(tulis di sini)

## IV. Results

[TABEL V — placeholder] Hasil utama: macro-F1 [95% CI] dan akurasi di development set (EMMediaTopic dev, label GPT-4o), agreement dengan teacher di held-out CC-News, dan hasil di unified test set (47 bahasa, label independen). CI uji dari site-cluster bootstrap.

---

### HAS-01 · Accuracy of All Models (RQ1) · main.tex baris 378

**Current:**
StaticKD keeps 91.1% of the teacher macro-F1 on the unified test set, with 0.545 [0.490–0.605] against 0.598 [0.546–0.643] (Table V). Both scores lie far below the development scores (0.761 and 0.822), because most of the test set lies outside the languages, sources, and period of the teacher training data. On the development set StaticKD keeps 92.6% of the teacher score, and on the 63 held-out languages it agrees with the teacher on 81.1% of the documents. A single student without ensembling reaches 0.542 ± 0.004 on the test set (10 seeds).

**Makna:**
Subbagian: akurasi semua model (RQ1). StaticKD mempertahankan 91.1% macro-F1 teacher di unified test set, yaitu 0.545 [0.490-0.605] dibanding 0.598 [0.546-0.643] (Tabel V). Kedua skor jauh di bawah skor development (0.761 dan 0.822), karena sebagian besar test set berada di luar bahasa, sumber, dan periode data training teacher. Di development set, StaticKD mempertahankan 92.6% skor teacher, dan di 63 bahasa held-out StaticKD sama dengan teacher pada 81.1% dokumen. Satu student tanpa ensemble mencapai 0.542 ± 0.004 di test set (10 seed).

**Locked:** angka 91.1%, 0.545, 0.490, 0.605, 0.598, 0.546, 0.643, 0.761, 0.822, 92.6%, 63, 81.1%, 0.542, 0.004, 10 · rujukan Table V · simbol ±

**Paraphrase:**
(tulis di sini)

---

### HAS-02 · Accuracy of All Models (RQ1) · main.tex baris 380

**Current:**
MiniLM-L6 (0.566), which starts from a distillation of XLM-R-large, lies between StaticKD and the teacher. DistilmBERT (0.534) is on par with StaticKD while being much more expensive. The two baselines of similar cost, fastText + KD and TF-IDF + SVM + KD, fall below StaticKD. The last two rows show what happens without teacher labels in other languages. fastText trained only on the GPT-4o labels of four languages reaches 0.665 on the development set but only 0.086 on the test set.

**Makna:**
MiniLM-L6 (0.566), yang berawal dari distilasi XLM-R-large, berada di antara StaticKD dan teacher. DistilmBERT (0.534) setara (on par) dengan StaticKD padahal jauh lebih mahal. Dua baseline berbiaya serupa, fastText + KD dan TF-IDF + SVM + KD, berada di bawah StaticKD. Dua baris terakhir memperlihatkan apa yang terjadi tanpa label teacher di bahasa lain. fastText yang hanya dilatih pada label GPT-4o dari empat bahasa mencapai 0.665 di development set tetapi hanya 0.086 di test set.

**Locked:** angka 0.566, 0.534, 0.665, 0.086

**Paraphrase:**
(tulis di sini)

[TABEL VI — placeholder] Uji berpasangan StaticKD terhadap model lain di unified test set (delta = StaticKD dikurangi model pembanding; p dikoreksi Holm atas semua perbandingan; b/c = dokumen yang benar hanya untuk StaticKD / hanya untuk model pembanding).

---

### HAS-03 · Accuracy of All Models (RQ1) · main.tex baris 405

**Current:**
The paired tests in Table VI confirm this ranking. Against the teacher, Δmacro-F1 is −0.053 [−0.065, −0.033], and against MiniLM-L6 it is −0.021 [−0.038, −0.008] (p=0.004). The difference from DistilmBERT (+0.010, p=0.800) is not significant. StaticKD is correct on more test articles than DistilmBERT (McNemar p<0.001), but the McNemar test treats articles as independent and ignores the dependence between articles of the same site. StaticKD is better than the quantized fastText + KD by +0.110 [+0.042, +0.151] and than TF-IDF + SVM by +0.059 [+0.009, +0.093] (p=0.030).

**Makna:**
Uji berpasangan di Tabel VI menegaskan urutan ini. Terhadap teacher, Δmacro-F1 adalah -0.053 [-0.065, -0.033], dan terhadap MiniLM-L6 -0.021 [-0.038, -0.008] (p=0.004). Selisih dengan DistilmBERT (+0.010, p=0.800) tidak signifikan. StaticKD benar pada lebih banyak artikel uji daripada DistilmBERT (McNemar p<0.001), tetapi uji McNemar menganggap artikel independen dan mengabaikan dependensi antarartikel dari situs yang sama. StaticKD lebih baik daripada fastText + KD terkuantisasi sebesar +0.110 [+0.042, +0.151] dan daripada TF-IDF + SVM sebesar +0.059 [+0.009, +0.093] (p=0.030).

**Locked:** angka 0.053, 0.065, 0.033, 0.021, 0.038, 0.008, +0.010, +0.110, +0.042, +0.151, +0.059, +0.009, +0.093 · rujukan Table VI · simbol Δ, −, p=0.004, p=0.800, p<0.001, p=0.030

**Paraphrase:**
(tulis di sini)

---

### HAS-04 · Accuracy of All Models (RQ1) · main.tex baris 407

**Current:**
The advantage over fastText + KD holds in almost every language, since StaticKD has the higher macro-F1 in 43 of 47 languages (Wilcoxon p<0.001). The advantage over TF-IDF + SVM is narrower. StaticKD has the higher macro-F1 in 31 of 47 languages (Wilcoxon p=0.003), but per-language accuracy is higher in 24 languages and lower in 22 (Wilcoxon p=0.127), so the two models are close on accuracy. Against DistilmBERT neither metric differs consistently across languages (Wilcoxon p=0.604 for macro-F1 and 0.322 for accuracy). StaticKD beats the teacher in only 7 of 47 languages.

**Makna:**
Keunggulan atas fastText + KD berlaku di hampir semua bahasa, karena macro-F1 StaticKD lebih tinggi di 43 dari 47 bahasa (Wilcoxon p<0.001). Keunggulan atas TF-IDF + SVM lebih tipis. Macro-F1 StaticKD lebih tinggi di 31 dari 47 bahasa (Wilcoxon p=0.003), tetapi akurasi per bahasanya lebih tinggi di 24 bahasa dan lebih rendah di 22 (Wilcoxon p=0.127), jadi akurasi kedua model berdekatan. Terhadap DistilmBERT, tidak ada metrik yang berbeda secara konsisten antarbahasa (Wilcoxon p=0.604 untuk macro-F1 dan 0.322 untuk akurasi). StaticKD hanya mengalahkan teacher di 7 dari 47 bahasa.

**Locked:** angka 43, 47, 31, 24, 22, 0.322, 7 · simbol p<0.001, p=0.003, p=0.127, p=0.604

**Paraphrase:**
(tulis di sini)

---

### HAS-05 · Accuracy of All Models (RQ1) · main.tex baris 409

**Current:**
The share of the teacher score that StaticKD keeps varies far more with the amount of distillation data in the language of the article than with the type of label (Table VII, Fig. 3). By label origin it ranges from 89.5% (publisher categories) to 95.8% (JSON-LD sections). By the amount of distillation data in the language, it falls from 97.5% in languages with at least 500 documents to 72.3% in languages with none. Limiting the test set to at most five articles per site and language–label pair (8,139 articles) leaves the model ranking unchanged (StaticKD 0.587, teacher 0.627).

**Makna:**
Porsi skor teacher yang dipertahankan StaticKD jauh lebih bervariasi menurut jumlah data distilasi di bahasa artikel daripada menurut jenis label (Tabel VII, Gambar 3). Menurut asal label, porsinya berkisar dari 89.5% (kategori penerbit) sampai 95.8% (rubrik JSON-LD). Menurut jumlah data distilasi di bahasanya, porsinya turun dari 97.5% di bahasa dengan minimal 500 dokumen menjadi 72.3% di bahasa tanpa data. Membatasi test set ke paling banyak lima artikel per situs dan per pasangan bahasa-label (8,139 artikel) tidak mengubah urutan model (StaticKD 0.587, teacher 0.627).

**Locked:** angka 89.5%, 95.8%, 97.5%, 500, 72.3%, 8,139, 0.587, 0.627 · rujukan Table VII, Fig. 3

**Paraphrase:**
(tulis di sini)

[TABEL VII — placeholder] Macro-F1 uji per subgrup. Kolom terakhir: macro-F1 StaticKD sebagai persentase macro-F1 teacher di subgrup yang sama.

---

### HAS-06 · Accuracy of All Models (RQ1) · main.tex baris 445

**Current:**
Table VIII splits the test set by source. On MN-DS, the only source annotated directly with IPTC topics, StaticKD keeps 97.4% of the teacher score (0.535 against 0.549), and the teacher itself reaches its lowest macro-F1 of all sources there. StaticKD keeps the smallest share on MasakhaNEWS (80.0%). Its human labels follow a non-IPTC scheme, and 10 of its 16 languages are absent from the distillation data. Bangla is absent as well, and Bangla news shows most clearly what the pre-trained embeddings contribute. There, fastText + KD and TF-IDF + SVM collapse to 0.150 and 0.010, while StaticKD reaches 0.748.

**Makna:**
Tabel VIII memecah test set menurut sumber. Di MN-DS, satu-satunya sumber yang dianotasi langsung dengan topik IPTC, StaticKD mempertahankan 97.4% skor teacher (0.535 vs 0.549), dan teacher sendiri mendapat macro-F1 terendahnya di sana dibanding sumber lain. StaticKD mempertahankan porsi terkecil di MasakhaNEWS (80.0%). Label manusianya memakai skema non-IPTC, dan 10 dari 16 bahasanya tidak ada di data distilasi. Bahasa Bangla juga tidak ada di data distilasi, dan berita Bangla paling jelas memperlihatkan sumbangan embedding pra-latih. Di sana fastText + KD dan TF-IDF + SVM jatuh ke 0.150 dan 0.010, sedangkan StaticKD mencapai 0.748.

**Locked:** angka 97.4%, 0.535, 0.549, 80.0%, 10, 16, 0.150, 0.010, 0.748 · rujukan Table VIII

**Paraphrase:**
(tulis di sini)

[TABEL VIII — placeholder] Macro-F1 uji per sumber unified test set. MN-DS satu-satunya sumber yang dianotasi langsung dengan topik IPTC; MasakhaNEWS dianotasi manusia dengan skemanya sendiri. Kolom terakhir: StaticKD sebagai persentase teacher.

[GAMBAR 3 — placeholder] Macro-F1 uji menurut asal label (kiri) dan menurut jumlah data distilasi di bahasa artikel (kanan).

---

### HAS-07 · Validity of the Editorial Labels · main.tex baris 476

**Current:**
Two thirds of the test labels are section and category labels, which record newsroom decisions rather than annotation under a labeling guideline. This subsection checks whether such labels behave like human labels in the same language. The check compares how well the same teacher agrees with each label type, so the teacher acts only as a fixed reference. If section labels were much noisier than human labels, the teacher would agree with them clearly less often than with human labels in the same language.

**Makna:**
Subbagian: validitas label editorial. Dua pertiga label uji adalah label rubrik dan kategori, yang mencatat keputusan redaksi, bukan anotasi berdasarkan pedoman pelabelan. Subbagian ini memeriksa apakah label seperti itu berperilaku seperti label manusia dalam bahasa yang sama. Pemeriksaan ini membandingkan seberapa sesuai teacher yang sama dengan setiap jenis label, jadi teacher hanya berperan sebagai acuan tetap. Kalau label rubrik jauh lebih berisik daripada label manusia, teacher akan jelas lebih jarang sesuai dengan label rubrik dibanding dengan label manusia dalam bahasa yang sama.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### HAS-08 · Validity of the Editorial Labels · main.tex baris 478

**Current:**
Because the sampling prefers human-labeled sources (Section III-D), the English part of the test set contains only human labels. For a comparison within English, a separate sample of 754 English CC-NEWS articles with JSON-LD section labels was therefore drawn from 306 sites outside the test set, at most 50 per label. The teacher reaches an accuracy of 0.646 on the section labels (macro-F1 0.617) and 0.559 on the MN-DS and MasakhaNEWS human labels (macro-F1 0.565). Accuracy on section labels is higher for 12 of the 17 labels (Wilcoxon p=0.033), and the ranking of label difficulty correlates between the two label types (ρ=0.63, p=0.007). The hard labels, society, human interest, and religion, are hard under both. By this measure, section labels are not noisier than human labels in English.

**Makna:**
Karena sampling mengutamakan sumber berlabel manusia (Bagian III-D), bagian bahasa Inggris dari test set hanya berisi label manusia. Karena itu, untuk perbandingan di dalam bahasa Inggris diambil sampel terpisah berisi 754 artikel CC-NEWS bahasa Inggris berlabel rubrik JSON-LD dari 306 situs di luar test set, paling banyak 50 per label. Teacher mencapai akurasi 0.646 pada label rubrik (macro-F1 0.617) dan 0.559 pada label manusia MN-DS dan MasakhaNEWS (macro-F1 0.565). Akurasi pada label rubrik lebih tinggi untuk 12 dari 17 label (Wilcoxon p=0.033), dan urutan tingkat kesulitan label berkorelasi antara kedua jenis label (ρ=0.63, p=0.007). Label yang sulit, yaitu society, human interest, dan religion, sulit di kedua jenis label. Dengan ukuran ini, label rubrik tidak lebih berisik daripada label manusia di bahasa Inggris.

**Locked:** angka 754, 306, 50, 0.646, 0.617, 0.559, 0.565, 12, 17 · rujukan Section III-D · simbol p=0.033, ρ=0.63, p=0.007

**Paraphrase:**
(tulis di sini)

---

### HAS-09 · Validity of the Editorial Labels · main.tex baris 480

**Current:**
French offers a second comparison inside the test set. The teacher reaches an accuracy of 0.716 on 208 articles with section labels and 0.500 on 200 human-labeled MasakhaNEWS articles, the same direction as in English.

**Makna:**
Bahasa Prancis memberi perbandingan kedua di dalam test set. Teacher mencapai akurasi 0.716 pada 208 artikel berlabel rubrik dan 0.500 pada 200 artikel MasakhaNEWS berlabel manusia, arahnya sama dengan di bahasa Inggris.

**Locked:** angka 0.716, 208, 0.500, 200

**Paraphrase:**
(tulis di sini)

---

### HAS-10 · Validity of the Editorial Labels · main.tex baris 482

**Current:**
A last check looks at each source category, restricted to languages covered by XLM-R pre-training, to see why agreement is lower on the human-labeled sources. The median agreement of the teacher with the mapped label per category is 0.46 for MasakhaNEWS, 0.50 for MN-DS, 0.81 for L3Cube, and 0.87 for CC-NEWS sections. The lowest agreement occurs for source categories that are broader than their IPTC target. For example, only 45% of MasakhaNEWS politics articles are predicted as politics, with conflict (29%) as the main alternative. Agreement is also low for labels whose boundaries are unclear even to human annotators, such as society in MN-DS, in line with the low inter-annotator agreement reported for that label [2]. Such mismatches reflect differences between the category scheme of a source and IPTC. Since every model is scored against the same labels, comparisons between models are unaffected, and absolute scores read as agreement with the editorial categorization.

**Makna:**
Pemeriksaan terakhir melihat tiap kategori sumber, dibatasi pada bahasa yang tercakup pre-training XLM-R, untuk melihat mengapa agreement lebih rendah pada sumber berlabel manusia. Median agreement teacher dengan label hasil pemetaan per kategori adalah 0.46 untuk MasakhaNEWS, 0.50 untuk MN-DS, 0.81 untuk L3Cube, dan 0.87 untuk rubrik CC-NEWS. Agreement terendah terjadi pada kategori sumber yang lebih luas daripada target IPTC-nya. Misalnya hanya 45% artikel politics MasakhaNEWS yang diprediksi politics, dengan conflict (29%) sebagai alternatif utama. Agreement juga rendah untuk label yang batasnya tidak jelas bahkan bagi anotator manusia, seperti society di MN-DS, sejalan dengan rendahnya inter-annotator agreement yang dilaporkan untuk label itu [2]. Ketidakcocokan seperti ini mencerminkan perbedaan skema kategori sumber dengan IPTC. Karena semua model dinilai terhadap label yang sama, perbandingan antarmodel tidak terpengaruh, dan skor absolut dibaca sebagai kesesuaian dengan kategorisasi editorial.

**Locked:** angka 0.46, 0.50, 0.81, 0.87, 45%, 29% · sitasi [2] Kuzman & Ljubešić 2025

**Paraphrase:**
(tulis di sini)

[TABEL IX — placeholder] Ablasi dan temperature (satu student, tanpa ensemble). Rata-rata ± standar deviasi antar-seed; tanda bintang: berbeda dari resep final (Welch, Holm, p < 0.05).

[TABEL X — placeholder] Macro-F1 varian terpilih menurut jumlah data distilasi di bahasa artikel (test set; rata-rata antar-seed).

---

### HAS-11 · Ablation, Temperature, and Ensembling (RQ2) · main.tex baris 533

**Current:**
Two components carry most of the accuracy: multilingual distillation data and the pre-trained embeddings (Table IX, five seeds per variant). Distilling on EMMediaTopic alone (4 languages) lowers the test macro-F1 by 0.051 and the held-out agreement by 0.077. Starting from random embeddings instead of potion lowers the test macro-F1 by 0.120 (p<0.001), the largest drop of all variants.

**Makna:**
Subbagian: ablasi, temperature, dan ensemble (RQ2). Dua komponen membawa sebagian besar akurasi: data distilasi multibahasa dan embedding pra-latih (Tabel IX, lima seed per varian). Distilasi hanya dengan EMMediaTopic (4 bahasa) menurunkan macro-F1 uji sebesar 0.051 dan held-out agreement sebesar 0.077. Memulai dari embedding acak, bukan potion, menurunkan macro-F1 uji sebesar 0.120 (p<0.001), penurunan terbesar dari semua varian.

**Locked:** angka 4, 0.051, 0.077, 0.120 · rujukan Table IX · simbol p<0.001

**Paraphrase:**
(tulis di sini)

---

### HAS-12 · Ablation, Temperature, and Ensembling (RQ2) · main.tex baris 535

**Current:**
Freezing the embeddings, so that only the linear head on top of potion is trained, gives a mixed result. It lowers the development score by 0.035 (p<0.001) and the held-out agreement by 0.020 (p<0.001), but raises the test macro-F1 by +0.014 (p<0.001). Table X locates this gain in languages with little distillation data (+0.059) and with none (+0.037). In languages with at least 500 documents the frozen embeddings are slightly weaker (−0.007). The final recipe was fixed on the development set before this effect was observed, and Section V explains why that set cannot reveal it.

**Makna:**
Membekukan embedding, sehingga hanya kepala linear di atas potion yang dilatih, memberi hasil campuran. Varian ini menurunkan skor development sebesar 0.035 (p<0.001) dan held-out agreement sebesar 0.020 (p<0.001), tetapi menaikkan macro-F1 uji sebesar +0.014 (p<0.001). Tabel X menunjukkan kenaikan ini berasal dari bahasa dengan data distilasi sedikit (+0.059) dan tanpa data (+0.037). Di bahasa dengan minimal 500 dokumen, embedding beku sedikit lebih lemah (-0.007). Resep final sudah ditetapkan pada development set sebelum efek ini terlihat, dan Bagian V menjelaskan mengapa set itu tidak bisa mengungkapnya.

**Locked:** angka 0.035, 0.020, +0.014, +0.059, +0.037, 500, 0.007 · rujukan Table X, Section V · simbol p<0.001, −

**Paraphrase:**
(tulis di sini)

---

### HAS-13 · Ablation, Temperature, and Ensembling (RQ2) · main.tex baris 537

**Current:**
None of the remaining changes moves the test macro-F1 significantly. Hard teacher labels change the test macro-F1 by +0.005 (p=0.433) and the development score by −0.006 (p=1.000), so hard labels work as well as soft labels. Reducing the data to 130 thousand documents changes the test macro-F1 by −0.002 (p=1.000), removing token dropout by +0.001 (p=1.000), and an MLP head that cannot be folded by +0.009 (p=0.281).

**Makna:**
Tidak satu pun perubahan lainnya menggeser macro-F1 uji secara signifikan. Hard label dari teacher mengubah macro-F1 uji sebesar +0.005 (p=0.433) dan skor development sebesar -0.006 (p=1.000), jadi hard label sama baiknya dengan soft label. Mengurangi data menjadi 130 ribu dokumen mengubah macro-F1 uji sebesar -0.002 (p=1.000), menghapus token dropout +0.001 (p=1.000), dan kepala MLP yang tidak bisa dilipat +0.009 (p=0.281).

**Locked:** angka +0.005, 0.006, 130, 0.002, +0.001, +0.009 · simbol p=0.433, −, p=1.000, p=0.281

**Paraphrase:**
(tulis di sini)

---

### HAS-14 · Ablation, Temperature, and Ensembling (RQ2) · main.tex baris 539

**Current:**
A higher temperature does not help (Fig. 4). Compared with τ=1, the common choice τ=2 [10] lowers the held-out agreement by 0.007 (p<0.001), and its changes on the test macro-F1 (−0.005, p=0.059) and on the development set (−0.006, p=0.705) are not significant. With τ=4 all three metrics drop, the test macro-F1 by 0.014 (p<0.001).

**Makna:**
Temperature yang lebih tinggi tidak membantu (Gambar 4). Dibanding τ=1, pilihan umum τ=2 [10] menurunkan held-out agreement sebesar 0.007 (p<0.001), dan perubahannya di macro-F1 uji (-0.005, p=0.059) dan di development set (-0.006, p=0.705) tidak signifikan. Dengan τ=4, ketiga metrik turun, macro-F1 uji sebesar 0.014 (p<0.001).

**Locked:** angka 0.007, 0.005, 0.006, 0.014 · sitasi [10] Hinton et al. 2015 · rujukan Fig. 4 · simbol τ=1, τ=2, p<0.001, −, p=0.059, p=0.705, τ=4

**Paraphrase:**
(tulis di sini)

---

### HAS-15 · Ablation, Temperature, and Ensembling (RQ2) · main.tex baris 541

**Current:**
Averaged over seed combinations, growing the ensemble from one to three seeds moves the test macro-F1 from 0.542 to 0.544 and the held-out agreement from 0.808 to 0.810 (Fig. 5), and ten seeds give 0.546. The gain is small, but it costs nothing at inference time because every ensemble size is still one table.

**Makna:**
Dirata-rata atas kombinasi seed, memperbesar ensemble dari satu ke tiga seed menggeser macro-F1 uji dari 0.542 ke 0.544 dan held-out agreement dari 0.808 ke 0.810 (Gambar 5), dan sepuluh seed memberi 0.546. Kenaikannya kecil, tetapi tanpa biaya saat inference karena berapa pun ukuran ensemble-nya tetap satu tabel.

**Locked:** angka 0.542, 0.544, 0.808, 0.810, 0.546 · rujukan Fig. 5

**Paraphrase:**
(tulis di sini)

[GAMBAR 4 — placeholder] Efek temperature distilasi. Tiap titik adalah satu seed; garis menghubungkan rata-ratanya.

[GAMBAR 5 — placeholder] Efek ukuran ensemble tabel (rata-rata ± standar deviasi antar-kombinasi seed).

[TABEL XI — placeholder] Efisiensi CPU (P-core di-pin; sampel dari unified test set; 1c/4c = 1/4 core).

---

### HAS-16 · CPU Efficiency (RQ3) · main.tex baris 581

**Current:**
The teacher is too slow for a large stream on CPU, and StaticKD removes this cost almost entirely (Table XI, Figs. 6 and 7). In PyTorch fp32 the teacher needs 2,971 ms per article on one core, with a throughput of 0.33 articles per second. Its best CPU configuration, ONNX int8, needs 1,239 ms with a throughput of 0.77 articles per second. Classifying one million articles per day would take 15.1 cores (ONNX int8) to 34.8 cores (PyTorch) for this step alone.

**Makna:**
Subbagian: efisiensi CPU (RQ3). Teacher terlalu lambat untuk aliran artikel yang besar di CPU, dan StaticKD hampir sepenuhnya menghilangkan biaya ini (Tabel XI, Gambar 6 dan Gambar 7). Dengan PyTorch fp32, teacher butuh 2,971 ms per artikel di satu core, dengan throughput 0.33 artikel per detik. Konfigurasi CPU terbaiknya, ONNX int8, butuh 1,239 ms dengan throughput 0.77 artikel per detik. Mengklasifikasi satu juta artikel per hari akan butuh 15.1 core (ONNX int8) sampai 34.8 core (PyTorch) hanya untuk langkah ini.

**Locked:** angka 2,971 ms, 0.33, 1,239 ms, 0.77, 15.1, 34.8 · rujukan Table XI, Fig. 6, Fig. 7

**Paraphrase:**
(tulis di sini)

---

### HAS-17 · CPU Efficiency (RQ3) · main.tex baris 583

**Current:**
StaticKD needs 2.03 ms per article and processes 473 articles per second per core. This is about 616 times faster than the ONNX int8 teacher, 1,420 times faster than the PyTorch teacher, and 29 times faster than MiniLM-L6. Its file is 16 times smaller than the ONNX int8 teacher, and one million articles per day need 0.02 cores. Its model RAM is 501 MB, mostly for the tokenizer structure. The compact variant reduces it to 277 MB. With one thread, tokenization (579 tokens per article on average) takes 98% of the prediction time, while averaging the table rows alone runs at 28,755 articles per second. The speed of StaticKD is thus limited by the tokenizer, not by the model.

**Makna:**
StaticKD butuh 2.03 ms per artikel dan memproses 473 artikel per detik per core. Ini sekitar 616 kali lebih cepat daripada teacher ONNX int8, 1,420 kali lebih cepat daripada teacher PyTorch, dan 29 kali lebih cepat daripada MiniLM-L6. Ukuran file-nya 16 kali lebih kecil daripada teacher ONNX int8, dan satu juta artikel per hari hanya butuh 0.02 core. RAM modelnya 501 MB, sebagian besar untuk struktur tokenizer. Varian compact menurunkannya ke 277 MB. Dengan satu thread, tokenisasi (rata-rata 579 token per artikel) memakan 98% waktu prediksi, sementara merata-rata baris tabel saja berjalan 28,755 artikel per detik. Jadi kecepatan StaticKD dibatasi oleh tokenizer, bukan oleh modelnya.

**Locked:** angka 2.03 ms, 473, 616, 1,420, 29, 16, 0.02, 501 MB, 277 MB, 579, 98%, 28,755

**Paraphrase:**
(tulis di sini)

---

### HAS-18 · CPU Efficiency (RQ3) · main.tex baris 585

**Current:**
StaticKD is not the fastest model in the table. The quantized fastText + KD is slightly faster (532 articles per second), smaller (18 MB), and uses less RAM (300 MB), but its test macro-F1 is 0.435 against 0.545 for StaticKD. Of the four models with comparable latency (StaticKD, its compact variant, fastText, and TF-IDF + SVM), StaticKD is the most accurate (Fig. 6).

**Makna:**
StaticKD bukan model tercepat di tabel. fastText + KD terkuantisasi sedikit lebih cepat (532 artikel per detik), lebih kecil (18 MB), dan memakai RAM lebih sedikit (300 MB), tetapi macro-F1 ujinya 0.435 dibanding 0.545 untuk StaticKD. Dari empat model dengan latency sebanding (StaticKD, varian compact-nya, fastText, dan TF-IDF + SVM), StaticKD paling akurat (Gambar 6).

**Locked:** angka 532, 18 MB, 300 MB, 0.435, 0.545 · rujukan Fig. 6

**Paraphrase:**
(tulis di sini)

[GAMBAR 6 — placeholder] Macro-F1 uji di unified test set terhadap throughput CPU satu core (skala log).

[GAMBAR 7 — placeholder] Latency per artikel, RAM model, dan ukuran file (skala log).

[TABEL XII — placeholder] Faktor-faktor di balik kinerja per bahasa.

---

### HAS-19 · Analysis by Language and Label (RQ4) · main.tex baris 624

**Current:**
In a typical language StaticKD is close to the teacher, with a median per-language accuracy gap of −0.024 (Fig. 8). Table XII relates the gap to properties of the language. On the held-out set (53 languages with at least 20 documents), the agreement of StaticKD with the teacher rises with the log amount of distillation data (ρ=0.31, p=0.022) and with teacher confidence (ρ=0.71, p<0.001). It does not differ significantly across scripts (Kruskal–Wallis H=10.37, p=0.065). The weak spot is a group of African languages. On languages outside XLM-R pre-training that are also absent from the distillation data (ig, lg, ln, pcm, rn, sn, ti, yo), StaticKD reaches a mean accuracy of only 0.407, while the teacher reaches 0.643.

**Makna:**
Subbagian: analisis per bahasa dan label (RQ4). Di bahasa pada umumnya StaticKD dekat dengan teacher, dengan median selisih akurasi per bahasa -0.024 (Gambar 8). Tabel XII mengaitkan selisih ini dengan sifat bahasa. Di held-out set (53 bahasa dengan minimal 20 dokumen), agreement StaticKD dengan teacher naik seiring log jumlah data distilasi (ρ=0.31, p=0.022) dan seiring confidence teacher (ρ=0.71, p<0.001). Agreement ini tidak berbeda signifikan antaraksara (Kruskal-Wallis H=10.37, p=0.065). Titik lemahnya adalah sekelompok bahasa Afrika. Pada bahasa di luar pre-training XLM-R yang juga tidak ada di data distilasi (ig, lg, ln, pcm, rn, sn, ti, yo), rata-rata akurasi StaticKD hanya 0.407, sedangkan teacher 0.643.

**Locked:** angka 0.024, 53, 20, 0.407, 0.643 · rujukan Fig. 8, Table XII · simbol −, ρ=0.31, p=0.022, ρ=0.71, p<0.001, H=10.37, p=0.065

**Paraphrase:**
(tulis di sini)

---

### HAS-20 · Analysis by Language and Label (RQ4) · main.tex baris 626

**Current:**
Four Indian languages (bn, ml, or, pa) show how StaticKD handles text whose tokens it has hardly seen in training. In these languages at least 68% of the token occurrences come from tokens seen fewer than 10 times in the distillation data. StaticKD still reaches a mean accuracy of 0.624 in these languages (teacher 0.738). The compact variant removes these rare tokens from the tokenizer, and its accuracy in these languages falls to 0.013. In the remaining languages the compact variant reaches 0.578 against 0.640 for the full StaticKD.

**Makna:**
Empat bahasa India (bn, ml, or, pa) memperlihatkan cara StaticKD menangani teks yang token-tokennya hampir tidak pernah dilihat saat training. Di bahasa-bahasa ini, minimal 68% kemunculan token berasal dari token yang muncul kurang dari 10 kali di data distilasi. StaticKD tetap mencapai rata-rata akurasi 0.624 di bahasa-bahasa ini (teacher 0.738). Varian compact membuang token-token langka ini dari tokenizer, dan akurasinya di bahasa ini jatuh ke 0.013. Di bahasa lainnya, varian compact mencapai 0.578 dibanding 0.640 untuk StaticKD penuh.

**Locked:** angka 68%, 10, 0.624, 0.738, 0.013, 0.578, 0.640

**Paraphrase:**
(tulis di sini)

[GAMBAR 8 — placeholder] Kiri: akurasi StaticKD terhadap akurasi teacher per bahasa uji (warna = data distilasi bahasa, ukuran = jumlah artikel). Kanan: held-out agreement per bahasa terhadap jumlah data distilasi, untuk StaticKD dan fastText + KD.

---

### HAS-21 · Analysis by Language and Label (RQ4) · main.tex baris 635

**Current:**
Per label (Fig. 9), the hardest labels for StaticKD are society (0.16), disaster (0.29), human interest (0.32), and conflict (0.37), and the easiest are sport (0.88), weather (0.84), and education (0.75). The largest gaps to the teacher occur for environment (−0.17), religion (−0.15), and arts (−0.08), and the most frequent confusions are society → human interest, human interest → arts, and society → politics (20% each).

**Makna:**
Per label (Gambar 9), label tersulit bagi StaticKD adalah society (0.16), disaster (0.29), human interest (0.32), dan conflict (0.37); yang termudah sport (0.88), weather (0.84), dan education (0.75). Selisih terbesar terhadap teacher ada pada environment (-0.17), religion (-0.15), dan arts (-0.08), dan kebingungan paling sering adalah society -> human interest, human interest -> arts, dan society -> politics (masing-masing 20%).

**Locked:** angka 0.16, 0.29, 0.32, 0.37, 0.88, 0.84, 0.75, 0.17, 0.15, 0.08, 20% · rujukan Fig. 9 · simbol −, →

**Paraphrase:**
(tulis di sini)

---

### HAS-22 · Analysis by Language and Label (RQ4) · main.tex baris 637

**Current:**
The table also shows which tokens carry the topic signal of an article. The specificity of a token is defined as the largest difference between one entry of its table row and the mean of the other 16 entries. Keeping only the 10% most specific tokens of each article (about 58 tokens per article) leaves the test macro-F1 almost unchanged (0.543 against 0.545), whereas a random 10% of the tokens gives 0.435.

**Makna:**
Tabel ini juga menunjukkan token mana yang membawa sinyal topik sebuah artikel. Spesifisitas sebuah token didefinisikan sebagai selisih terbesar antara satu entri di baris tabelnya dan rata-rata 16 entri lainnya. Hanya memakai 10% token paling spesifik di setiap artikel (sekitar 58 token per artikel) hampir tidak mengubah macro-F1 uji (0.543 dibanding 0.545), sedangkan 10% token acak hanya memberi 0.435.

**Catatan:** Catatan: angka 10%, 58, 0.543, dan 0.435 berasal dari cell analisis sinyal token di notebook bagian 10.3.

**Locked:** angka 16, 10%, 58, 0.543, 0.545, 0.435

**Paraphrase:**
(tulis di sini)

[GAMBAR 9 — placeholder] F1 per label di test set (kiri) dan confusion matrix StaticKD yang dinormalisasi per label referensi (kanan).

[TABEL XIII — placeholder] Cascade StaticKD ke teacher ONNX int8 di test set (throughput efektif satu core).

---

### HAS-23 · Calibration and Cascade Mode · main.tex baris 668

**Current:**
The ECE of StaticKD is 0.041 on the development set and 0.139 on the test set, lower than that of the teacher (0.090 and 0.245). Both models become overconfident on the test set, which lies outside the training distribution (Fig. 10). In cascade mode, StaticKD decides the articles on which its confidence is at least θ and sends the rest to the teacher (Table XIII). With θ=0.8, StaticKD decides 60.3% of the articles with an accuracy of 0.813. The cascade reaches an overall accuracy of 0.703 and a macro-F1 of 0.602, against 0.699 and 0.600 for the teacher alone, at an effective throughput of 1.92 articles per second per core against 0.77.

**Makna:**
Subbagian: kalibrasi dan mode cascade. ECE StaticKD 0.041 di development set dan 0.139 di test set, lebih rendah daripada teacher (0.090 dan 0.245). Kedua model menjadi overconfident di test set, yang berada di luar distribusi training (Gambar 10). Dalam mode cascade, StaticKD memutuskan artikel yang confidence-nya minimal θ dan mengirim sisanya ke teacher (Tabel XIII). Dengan θ=0.8, StaticKD memutuskan 60.3% artikel dengan akurasi 0.813. Cascade mencapai akurasi keseluruhan 0.703 dan macro-F1 0.602, dibanding 0.699 dan 0.600 untuk teacher saja, dengan throughput efektif 1.92 artikel per detik per core dibanding 0.77.

**Locked:** angka 0.041, 0.139, 0.090, 0.245, 60.3%, 0.813, 0.703, 0.602, 0.699, 0.600, 1.92, 0.77 · rujukan Fig. 10, Table XIII · simbol θ, θ=0.8

**Paraphrase:**
(tulis di sini)

[GAMBAR 10 — placeholder] Reliability diagram StaticKD di development set dan test set.

## V. Discussion

---

### PEM-01 · main.tex baris 679

**Current:**
A table lookup keeps about nine tenths of the teacher macro-F1 at an inference cost two to three orders of magnitude lower (Sections IV-A and IV-D). This agrees with the finding that order-free representations are already competitive for topic classification [14]. The token analysis in Section IV-E shows why a table suffices: a small share of topic-specific tokens carries almost all of the topic signal of an article. The remaining gap to the teacher has two sources. The first is a few labels, environment, religion, and arts, on which StaticKD loses the most against the teacher (Fig. 9). The labels on which StaticKD scores lowest, society, disaster, human interest, and conflict, are a separate matter. They are also among the hardest labels for the teacher, and society and human interest are known to be difficult for human annotators as well [2], so their low scores are not specific to the student. The second source of the gap is languages that are underrepresented in the distillation data (Table VII).

**Makna:**
Lookup tabel mempertahankan sekitar sembilan per sepuluh macro-F1 teacher dengan biaya inference dua sampai tiga orde besaran lebih rendah (Bagian IV-A dan Bagian IV-D). Ini sejalan dengan temuan bahwa representasi tanpa urutan kata (order-free) sudah kompetitif untuk klasifikasi topik [14]. Analisis token di Bagian IV-E menunjukkan mengapa tabel sudah cukup: sebagian kecil token yang spesifik-topik membawa hampir seluruh sinyal topik sebuah artikel. Selisih yang tersisa terhadap teacher punya dua sumber. Pertama, beberapa label, yaitu environment, religion, dan arts, tempat StaticKD paling banyak kalah dari teacher (Gambar 9). Label dengan skor StaticKD terendah, yaitu society, disaster, human interest, dan conflict, adalah persoalan lain. Label-label ini juga termasuk yang tersulit bagi teacher, dan society serta human interest diketahui sulit juga bagi anotator manusia [2], jadi skor rendahnya tidak khas student. Sumber kedua adalah bahasa yang kurang terwakili di data distilasi (Tabel VII).

**Locked:** sitasi [14] Galke & Scherp 2022; [2] Kuzman & Ljubešić 2025 · rujukan Section IV-A, Section IV-D, Section IV-E, Fig. 9, Table VII

**Paraphrase:**
(tulis di sini)

---

### PEM-02 · main.tex baris 681

**Current:**
With the same distillation data, MiniLM-L6 closes part of this gap, whereas DistilmBERT does not (Table VI). Both cost one to two orders of magnitude more than StaticKD. MiniLM comes from a distillation of XLM-R-large and DistilmBERT from mBERT, which suggests that the quality of the initial multilingual representation matters more than the number of layers.

**Makna:**
Dengan data distilasi yang sama, MiniLM-L6 menutup sebagian selisih ini, sedangkan DistilmBERT tidak (Tabel VI). Keduanya satu sampai dua orde besaran lebih mahal daripada StaticKD. MiniLM berasal dari distilasi XLM-R-large dan DistilmBERT dari mBERT, yang mengisyaratkan bahwa kualitas representasi multibahasa awal lebih menentukan daripada jumlah layer.

**Locked:** rujukan Table VI

**Paraphrase:**
(tulis di sini)

---

### PEM-03 · main.tex baris 683

**Current:**
The ablations show where the knowledge of the student comes from (RQ2). The largest source is the pre-trained multilingual initialization, whose removal lowers the test macro-F1 by 0.120, against 0.051 for the removal of the multilingual data. The multilingual distillation data labeled by the teacher come next, consistent with Sparse Distillation [23], which also relies on a large set of teacher-labeled text. The compact variant gives the most direct evidence for the role of the initialization. In Indian languages that hardly occur in the distillation data (for example bn, pa, or), most token occurrences come from tokens seen fewer than 10 times in the distillation data, so their embeddings are rarely or never updated and stay close to their potion values. StaticKD still classifies these languages with a mean accuracy of 0.624, yet the accuracy falls to 0.013 once the compact tokenizer removes those tokens. Transfer to languages without data therefore relies on embeddings that training hardly changes. These embeddings lie in the same space as the trained ones, so the linear head learned on data-rich languages also applies to them.

**Makna:**
Ablasi menunjukkan dari mana pengetahuan student berasal (RQ2). Sumber terbesar adalah inisialisasi multibahasa pra-latih: menghapusnya menurunkan macro-F1 uji sebesar 0.120, dibanding 0.051 bila data multibahasa yang dihapus. Data distilasi multibahasa yang dilabeli teacher berada di urutan berikutnya, sejalan dengan Sparse Distillation [23] yang juga bergantung pada teks berlabel teacher dalam jumlah besar. Varian compact memberi bukti paling langsung untuk peran inisialisasi. Di bahasa India yang hampir tidak ada di data distilasi (misalnya bn, pa, or), sebagian besar kemunculan token berasal dari token yang muncul kurang dari 10 kali di data distilasi, sehingga embedding-nya jarang atau tidak pernah di-update dan tetap dekat dengan nilai potion-nya. StaticKD masih mengklasifikasi bahasa-bahasa ini dengan rata-rata akurasi 0.624, tetapi akurasinya jatuh ke 0.013 begitu tokenizer compact membuang token-token itu. Jadi transfer ke bahasa tanpa data bergantung pada embedding yang hampir tidak diubah training. Embedding ini berada di ruang yang sama dengan embedding yang dilatih, sehingga kepala linear yang dipelajari dari bahasa kaya data juga berlaku untuknya.

**Catatan:** Catatan: bukti mekanisme transfer hanya dari 4 bahasa India beraksara sendiri.

**Locked:** angka 0.120, 0.051, 10, 0.624, 0.013 · sitasi [23] Ye et al. 2022

**Paraphrase:**
(tulis di sini)

---

### PEM-04 · main.tex baris 685

**Current:**
The frozen-embedding ablation shows the other side of the same mechanism. Fine-tuning moves the embeddings of tokens from the training languages and improves the fit on these languages, which is why freezing lowers the development score. Tokens of other languages stay where potion put them, and the head, which has adapted to the moved embeddings, fits them less well. This is why frozen embeddings are better in languages with little or no distillation data. The final recipe keeps fine-tuning because the recipe was selected on a development set in the training languages, which cannot reveal this effect. For deployments that target languages without distillation data, frozen embeddings or a regularizer that keeps the embeddings close to potion are the safer choice, and both still fold into a table.

**Makna:**
Ablasi embedding beku memperlihatkan sisi lain dari mekanisme yang sama. Fine-tuning menggeser embedding token dari bahasa training dan memperbaiki kecocokan pada bahasa-bahasa itu, itulah sebabnya membekukannya menurunkan skor development. Token bahasa lain tetap di posisi yang diberikan potion, dan kepala yang sudah menyesuaikan diri dengan embedding yang bergeser kurang cocok untuknya. Itulah sebabnya embedding beku lebih baik di bahasa dengan data distilasi sedikit atau tanpa data. Resep final tetap memakai fine-tuning karena resep dipilih pada development set dalam bahasa training, yang tidak bisa memperlihatkan efek ini. Untuk deployment yang menyasar bahasa tanpa data distilasi, embedding beku atau regularizer yang menjaga embedding dekat dengan potion adalah pilihan yang lebih aman, dan keduanya tetap bisa dilipat ke tabel.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### PEM-05 · main.tex baris 687

**Current:**
Soft labels, by contrast, add little or nothing. Hard teacher labels do not differ significantly from soft labels at τ=1. Raising the temperature to τ=2 lowers the held-out agreement without a significant change on the test set, and τ=4 lowers every metric (Section IV-C). This pattern fits the capacity-gap literature [25], [28]. A plausible explanation is that one linear layer over averaged embeddings cannot represent the inter-class structure in the tail of the teacher distribution (dark knowledge) [27]. A sharp distribution (τ=1) or hard labels give an attainable target, whereas a high τ asks the student to imitate a distribution shape beyond its capacity. For very-low-capacity students, effort is better spent on the coverage of the distillation data (languages, sites, topics) and on a multilingual initialization than on shaping the soft labels.

**Makna:**
Sebaliknya, soft label hampir tidak menambah apa-apa. Hard label dari teacher tidak berbeda signifikan dari soft label pada τ=1. Menaikkan temperature ke τ=2 menurunkan held-out agreement tanpa perubahan signifikan di test set, dan τ=4 menurunkan semua metrik (Bagian IV-C). Pola ini sejalan dengan literatur capacity gap [25], [28]. Penjelasan yang masuk akal: satu layer linear di atas embedding rata-rata tidak mampu merepresentasikan struktur antarkelas di ekor distribusi teacher (dark knowledge) [27]. Distribusi yang tajam (τ=1) atau hard label memberi target yang bisa dicapai, sedangkan τ tinggi meminta student meniru bentuk distribusi di luar kapasitasnya. Untuk student berkapasitas sangat rendah, usaha lebih baik dicurahkan pada cakupan data distilasi (bahasa, situs, topik) dan inisialisasi multibahasa daripada membentuk soft label.

**Locked:** sitasi [25] Zhang et al. 2025; [28] Wang et al. 2026; [27] Zhao et al. 2022 · rujukan Section IV-C · simbol τ=1, τ=2, τ=4, τ

**Paraphrase:**
(tulis di sini)

---

### PEM-06 · main.tex baris 689

**Current:**
Per-language performance is driven mainly by how well a language is represented in the distillation and pre-training data, not by its script (Kruskal–Wallis p=0.065). The weakest languages are African languages outside XLM-R pre-training that are also missing from the distillation data (ig, lg, ln, pcm, rn, sn, ti, yo). The teacher still reaches an accuracy of 0.643 on them, perhaps thanks to subwords shared with other languages and to sentence context, while StaticKD reaches only 0.407. The cheapest fix needs no change of architecture. News in these languages can simply be added to the distillation data and labeled by the teacher. The data ablation and the correlation between agreement and the amount of data (ρ=0.31) support this step.

**Makna:**
Kinerja per bahasa terutama ditentukan oleh seberapa baik bahasa itu terwakili di data distilasi dan data pre-training, bukan oleh aksaranya (Kruskal-Wallis p=0.065). Bahasa terlemah adalah bahasa Afrika di luar pre-training XLM-R yang juga tidak ada di data distilasi (ig, lg, ln, pcm, rn, sn, ti, yo). Teacher masih mencapai akurasi 0.643 di bahasa-bahasa ini, mungkin berkat subword yang dibagi dengan bahasa lain dan konteks kalimat, sedangkan StaticKD hanya 0.407. Perbaikan termurah tidak butuh perubahan arsitektur. Berita dalam bahasa-bahasa ini cukup ditambahkan ke data distilasi dan dilabeli teacher. Ablasi data dan korelasi antara agreement dan jumlah data (ρ=0.31) mendukung langkah ini.

**Catatan:** Catatan: 'terutama ditentukan oleh' lebih kuat dari buktinya, yang berupa korelasi, rho = 0.31 di held-out dan 0.52 di test. Aksara hanya tidak signifikan, p 0.065, bukan terbukti tidak berpengaruh. Teacher sendiri hanya mencapai 0.643 di bahasa-bahasa ini, jadi label distilasinya juga lebih lemah.

**Locked:** angka 0.643, 0.407 · simbol p=0.065, ρ=0.31

**Paraphrase:**
(tulis di sini)

---

### PEM-07 · main.tex baris 691

**Current:**
Agreement with the teacher does not always predict accuracy on editorial labels. Frozen embeddings lower the held-out agreement (−0.020) but raise the test macro-F1 (+0.014). Cutting the data to 130 thousand documents lowers the agreement (−0.009) without a significant change on the test set (−0.002). In line with [29], students should be selected with labels that do not come from the teacher and with a development set outside the training distribution, not with agreement with the teacher alone.

**Makna:**
Agreement dengan teacher tidak selalu memprediksi akurasi pada label editorial. Embedding beku menurunkan held-out agreement (-0.020) tetapi menaikkan macro-F1 uji (+0.014). Memangkas data menjadi 130 ribu dokumen menurunkan agreement (-0.009) tanpa perubahan signifikan di test set (-0.002). Sejalan dengan [29], student sebaiknya dipilih dengan label yang tidak berasal dari teacher dan dengan development set di luar distribusi training, bukan hanya dengan agreement terhadap teacher.

**Locked:** angka 0.020, +0.014, 130, 0.009, 0.002 · sitasi [29] Stanton et al. 2021 · simbol −

**Paraphrase:**
(tulis di sini)

---

### PEM-08 · main.tex baris 693

**Current:**
Test scores should be read according to the nature of the labels. An article about a criminal case involving an athlete can rightly sit in a sports section while a model labels it crime. Both answers are plausible under IPTC, which allows several topics per article. Comparisons between models remain fair because all models are scored against the same labels, and the model ranking does not change on the subset with capped site counts.

**Makna:**
Skor uji sebaiknya dibaca sesuai sifat labelnya. Artikel tentang kasus kriminal yang melibatkan atlet bisa saja dengan benar ditaruh di rubrik olahraga, sementara model melabelinya crime. Kedua jawaban masuk akal menurut IPTC, yang memperbolehkan beberapa topik per artikel. Perbandingan antarmodel tetap adil karena semua model dinilai terhadap label yang sama, dan urutan model tidak berubah pada subset dengan jumlah per situs dibatasi.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### PEM-09 · main.tex baris 695

**Current:**
Compared with Sparse Distillation [23], StaticKD replaces an n-gram table trained from scratch with pre-trained multilingual embeddings folded into 17 logits per token. The model becomes far smaller and transfers to languages that are missing from the distillation data. Inference is the recurring cost in a news pipeline, since every incoming article is classified, and one million articles per day need 15.1 cores with the ONNX int8 teacher against 0.02 with StaticKD (Section IV-D).

**Makna:**
Dibanding Sparse Distillation [23], StaticKD mengganti tabel n-gram yang dilatih dari nol dengan embedding multibahasa pra-latih yang dilipat menjadi 17 logit per token. Modelnya jadi jauh lebih kecil dan bisa transfer ke bahasa yang tidak ada di data distilasi. Inference adalah biaya berulang dalam pipeline berita karena setiap artikel yang masuk diklasifikasi, dan satu juta artikel per hari butuh 15.1 core dengan teacher ONNX int8 dibanding 0.02 dengan StaticKD (Bagian IV-D).

**Locked:** angka 17, 15.1, 0.02 · sitasi [23] Ye et al. 2022 · rujukan Section IV-D

**Paraphrase:**
(tulis di sini)

---

### PEM-10 · main.tex baris 697

**Current:**
For a real-time pipeline on servers without a GPU, StaticKD needs a 34 MB file and only numpy and tokenizers as dependencies. Its probabilities are better calibrated than those of the teacher (test ECE 0.139 against 0.245), which makes a cascade possible. With θ=0.8, the cascade accuracy (0.703) equals that of the teacher alone (0.699) at 1.92 articles per second per core, against 0.77 for the teacher alone. This mode suits batch jobs that need teacher-level accuracy. The compact variant lowers RAM but is only advisable when all target languages are covered by the distillation data.

**Makna:**
Untuk pipeline real-time di server tanpa GPU, StaticKD butuh file 34 MB dan hanya bergantung pada numpy dan tokenizers. Probabilitasnya lebih terkalibrasi daripada teacher (ECE uji 0.139 vs 0.245), sehingga mode cascade bisa dipakai. Dengan θ = 0.8, akurasi cascade (0.703) setara teacher saja (0.699) pada 1.92 artikel per detik per core, dibanding 0.77 untuk teacher saja. Mode ini cocok untuk batch job yang butuh akurasi setingkat teacher. Varian compact menurunkan RAM, tetapi hanya disarankan bila semua bahasa target tercakup data distilasi.

**Catatan:** Catatan: throughput cascade dihitung dari porsi artikel dan throughput tiap model, bukan diukur langsung; ini belum disebut di Limitations. RAM StaticKD 501 MB juga tidak disebut di sini.

**Locked:** angka 34 MB, 0.139, 0.245, 0.703, 0.699, 1.92, 0.77 · simbol θ=0.8 · nama numpy, tokenizers

**Paraphrase:**
(tulis di sini)

## VI. Limitations

---

### BTS-01 · main.tex baris 701

**Current:**
Of the test articles, 47.5% carry JSON-LD section labels and 20.4% publisher categories. Section conventions differ between publishers, and one section reflects one editorial view of an article that may cover several topics. The mapping table is conservative, validated against the IPTC tree, and reviewed by the first author, but the articles were not re-annotated by humans. Absolute scores on these labels therefore measure agreement with the categorization of publishers, especially for labels with unclear boundaries (society, human interest, lifestyle).

**Makna:**
Dari artikel uji, 47.5% berlabel rubrik JSON-LD dan 20.4% kategori penerbit. Konvensi rubrik berbeda antarpenerbit, dan satu rubrik hanya mencerminkan satu sudut pandang redaksi atas artikel yang bisa mencakup beberapa topik. Tabel pemetaannya konservatif, divalidasi terhadap pohon IPTC, dan ditinjau penulis pertama, tetapi artikelnya tidak dianotasi ulang oleh manusia. Karena itu skor absolut pada label ini mengukur kesesuaian dengan kategorisasi penerbit, terutama untuk label yang batasnya tidak jelas (society, human interest, lifestyle).

**Locked:** angka 47.5%, 20.4%

**Paraphrase:**
(tulis di sini)

---

### BTS-02 · main.tex baris 703

**Current:**
MasakhaNEWS labels were assigned by human annotators under their own scheme and then mapped to IPTC. Only MN-DS is annotated directly with IPTC topics, and it is English only. The multilingual IPTC test set of Kuzman and Ljubešić [2] is not public, so it was not available for this study.

**Makna:**
Label MasakhaNEWS diberikan anotator manusia dengan skema mereka sendiri, lalu dipetakan ke IPTC. Hanya MN-DS yang dianotasi langsung dengan topik IPTC, dan hanya bahasa Inggris. Test set IPTC multibahasa milik Kuzman dan Ljubešić [2] tidak publik, sehingga tidak tersedia untuk studi ini.

**Locked:** sitasi [2] Kuzman & Ljubešić 2025

**Paraphrase:**
(tulis di sini)

---

### BTS-03 · main.tex baris 705

**Current:**
Label coverage per language is uneven, with a median of 7 labels per language, and the African languages cover only four or five broad topics. Macro-F1 is computed over the labels present, so per-language scores are not directly comparable between languages with different label coverage. Publisher diversity is also limited, as 27 languages come from practically one publisher. These are BBC/VOA for the African languages, L3Cube for the Indian languages, and a single site for several CC-NEWS languages. Claims for these languages are limited to those publishers, and the site-cluster bootstrap widens their confidence intervals accordingly.

**Makna:**
Cakupan label per bahasa tidak merata, dengan median 7 label per bahasa, dan bahasa Afrika hanya mencakup empat atau lima topik luas. Macro-F1 dihitung atas label yang ada, jadi skor per bahasa tidak bisa dibandingkan langsung antarbahasa dengan cakupan label berbeda. Keragaman penerbit juga terbatas, karena 27 bahasa praktis hanya dari satu penerbit. Penerbit itu adalah BBC/VOA untuk bahasa Afrika, L3Cube untuk bahasa India, dan satu situs untuk beberapa bahasa CC-NEWS. Klaim untuk bahasa-bahasa ini terbatas pada penerbit tersebut, dan site-cluster bootstrap melebarkan confidence interval-nya sesuai keadaan itu.

**Locked:** angka 7, 27

**Paraphrase:**
(tulis di sini)

---

### BTS-04 · main.tex baris 707

**Current:**
The teacher bounds the student from above, and its errors and biases are copied. The held-out set measures agreement with the teacher, not correctness.

**Makna:**
Teacher menjadi batas atas bagi student, dan kesalahan serta biasnya ikut tersalin. Held-out set mengukur agreement dengan teacher, bukan kebenaran.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### BTS-05 · main.tex baris 709

**Current:**
The hyperparameters of fastText and TF-IDF + SVM were set once without a search, whereas the StaticKD recipe was selected from 72 runs on the development set. This unequal tuning budget may widen the accuracy gap to these two baselines. Two related methods were not run as baselines. Sparse Distillation [23] differs from fastText + KD and from the random-initialization ablation by the hidden layers of its deep averaging network, its soft-logit targets, and its billion-parameter n-gram table designed for English. The classifier trainer of Model2Vec [11] trains on hard labels, adds a 512-unit hidden layer, and learns a weight per token. The ablations test hard labels and a 512-unit hidden layer one at a time, and neither differs significantly from the final recipe on the development or test set (Table IX), but the two together and the learned token weights were not tested. A hidden layer would also prevent folding the model into one table. MiniLM-L6 and DistilmBERT were trained and evaluated with at most 256 tokens and therefore see less than half of most test articles, so their accuracy may be underestimated.

**Makna:**
Hyperparameter fastText dan TF-IDF + SVM ditetapkan sekali tanpa pencarian, sedangkan resep StaticKD dipilih dari 72 run pada development set. Budget tuning yang tidak setara ini bisa memperlebar selisih akurasi terhadap kedua baseline itu. Dua metode terkait tidak dijalankan sebagai baseline. Sparse Distillation [23] berbeda dari fastText + KD dan dari ablasi inisialisasi acak pada hidden layer deep averaging network-nya, target soft-logit-nya, dan tabel n-gram miliaran parameter yang dirancang untuk bahasa Inggris. Trainer classifier Model2Vec [11] dilatih pada hard label, menambah hidden layer 512 unit, dan mempelajari bobot per token. Ablasi menguji hard label dan hidden layer 512 unit satu per satu, dan keduanya tidak berbeda signifikan dari resep final di development set maupun test set (Tabel IX), tetapi kombinasi keduanya dan bobot token yang dipelajari belum diuji. Hidden layer juga akan membuat model tidak bisa dilipat menjadi satu tabel. MiniLM-L6 dan DistilmBERT dilatih dan dievaluasi dengan paling banyak 256 token, sehingga hanya melihat kurang dari separuh sebagian besar artikel uji, dan akurasinya mungkin terlalu rendah (underestimated).

**Locked:** angka 72, 512, 256 · sitasi [23] Ye et al. 2022; [11] Tulkens & van Dongen 2024 · rujukan Table IX

**Paraphrase:**
(tulis di sini)

---

### BTS-06 · main.tex baris 711

**Current:**
The benchmark ran on one machine in one session, with 30 latency documents for the teacher and the transformers. Absolute numbers on a server will differ and the latency sample of the heavy models is small, but ratios between models measured under the same protocol remain informative.

**Makna:**
Benchmark dijalankan di satu mesin dalam satu sesi, dengan 30 dokumen latency untuk teacher dan transformer. Angka absolut di server akan berbeda, dan sampel latency model berat kecil, tetapi rasio antarmodel yang diukur dengan protokol yang sama tetap informatif.

**Locked:** angka 30

**Paraphrase:**
(tulis di sini)

---

### BTS-07 · main.tex baris 713

**Current:**
StaticKD is much less accurate on African languages that are absent from both the distillation data and pre-training (Section V). Used as a topic filter, it could misclassify or drop news in these languages more often. During deployment, accuracy should be monitored per language, and low-confidence articles should be routed to the teacher through the cascade mode.

**Makna:**
StaticKD jauh kurang akurat pada bahasa Afrika yang tidak ada di data distilasi maupun pre-training (Bagian V). Bila dipakai sebagai filter topik, StaticKD bisa lebih sering salah mengklasifikasi atau membuang berita dalam bahasa-bahasa ini. Selama deployment, akurasi perlu dipantau per bahasa, dan artikel dengan confidence rendah perlu dialihkan ke teacher lewat mode cascade.

**Locked:** rujukan Section V

**Paraphrase:**
(tulis di sini)

---

### BTS-08 · main.tex baris 715

**Current:**
The study covers only top-level IPTC labels and single-label classification. Deeper levels and multi-topic articles remain untested.

**Makna:**
Studi ini hanya mencakup label IPTC level atas dan klasifikasi single-label. Level yang lebih dalam dan artikel multi-topik belum diuji.

**Locked:** —

**Paraphrase:**
(tulis di sini)

## VII. Conclusion

---

### KES-01 · main.tex baris 719

**Current:**
The open multilingual IPTC classifier needs 1.2 to 3 seconds per article on one CPU core. StaticKD distills it into a table of 17 logits per token, initialized from multilingual static embeddings and trained on 285,999 teacher-labeled articles in 69 languages. On 12,744 test articles in 47 languages, with labels that do not come from the teacher, StaticKD reaches a macro-F1 of 0.545, or 91.1% of the teacher. It processes 473 articles per second per CPU core, about 616 times the speed of the ONNX int8 teacher, with a 34 MB model that needs no deep learning library.

**Makna:**
Classifier IPTC multibahasa terbuka butuh 1.2 sampai 3 detik per artikel di satu core CPU. StaticKD men-distill-nya menjadi tabel 17 logit per token, diinisialisasi dari static embedding multibahasa dan dilatih pada 285,999 artikel berlabel teacher dalam 69 bahasa. Pada 12,744 artikel uji dalam 47 bahasa, dengan label yang tidak berasal dari teacher, StaticKD mencapai macro-F1 0.545, atau 91.1% dari teacher. StaticKD memproses 473 artikel per detik per core CPU, sekitar 616 kali kecepatan teacher ONNX int8, dengan model 34 MB yang tidak butuh library deep learning.

**Locked:** angka 1.2, 3, 17, 285,999, 69, 12,744, 47, 0.545, 91.1%, 473, 616, 34 MB

**Paraphrase:**
(tulis di sini)

---

### KES-02 · main.tex baris 721

**Current:**
The accuracy of this very small student comes mainly from multilingual distillation data and from pre-trained multilingual embeddings, while soft labels are no better than hard labels. Fine-tuning the embeddings raises accuracy in the training languages but lowers it in languages without distillation data, whose embeddings training rarely or never updates. The test set can be reused to evaluate other IPTC classifiers.

**Makna:**
Akurasi student yang sangat kecil ini terutama berasal dari data distilasi multibahasa dan dari embedding multibahasa pra-latih, sedangkan soft label tidak lebih baik daripada hard label. Fine-tuning embedding menaikkan akurasi di bahasa training tetapi menurunkannya di bahasa tanpa data distilasi, yang embedding-nya jarang atau tidak pernah di-update training. Test set ini bisa dipakai ulang untuk mengevaluasi classifier IPTC lain.

**Catatan:** Catatan: kesimpulan belum merangkum jawaban RQ4, yaitu bahasa, label, dan sumber tempat StaticKD lemah.

**Locked:** —

**Paraphrase:**
(tulis di sini)

---

### KES-03 · main.tex baris 723

**Current:**
Several directions follow from these results. The distillation data should be extended to the weak languages, especially the African languages outside XLM-R pre-training. A fine-tuning regularizer that keeps embeddings close to the pre-trained space could give in-distribution accuracy and cross-lingual transfer at the same time. Tokenization takes 98% of the inference time, so a faster tokenizer, for instance a direct word-to-table lookup, is the next source of speed. Any pruning of the vocabulary has to keep cross-lingual tokens. Cheap non-linear heads with quantized embeddings, hierarchical classification into IPTC level 2, multi-label classification, and human IPTC annotation of a multilingual sample of the test set remain open.

**Makna:**
Beberapa arah lanjutan mengikuti hasil ini. Data distilasi sebaiknya diperluas ke bahasa yang lemah, terutama bahasa Afrika di luar pre-training XLM-R. Regularizer fine-tuning yang menjaga embedding dekat ruang pra-latih bisa memberi akurasi in-distribution sekaligus transfer lintas bahasa. Tokenisasi memakan 98% waktu inference, jadi tokenizer yang lebih cepat, misalnya lookup langsung kata ke tabel, adalah sumber kecepatan berikutnya. Pemangkasan vocabulary apa pun harus mempertahankan token lintas bahasa. Kepala non-linear murah dengan embedding terkuantisasi, klasifikasi hierarkis ke IPTC level 2, klasifikasi multi-label, dan anotasi IPTC manusia untuk sampel multibahasa test set masih terbuka.

**Locked:** angka 98%, 2

**Paraphrase:**
(tulis di sini)

## Code, Model, and Data Availability

---

### KTS-01 · main.tex baris 726

**Current:**
The code for data collection, test-set construction, teacher labeling, training, evaluation, and benchmarking, together with a notebook that reproduces every number, table, and figure of this paper, is available at [TODO: GitHub URL and Zenodo DOI]. The StaticKD models are available at [TODO: Hugging Face URL]. The test set is released as a manifest of article URLs or IDs, labels, label origins, and text hashes, with a reconstruction script. Article texts are not redistributed because of publisher copyright and the licenses of the source datasets. The section-to-IPTC mapping table is released with the code. EMMediaTopic is available from the CLARIN.SI repository [9]. Table XIV lists the licenses of the assets used and released in this study.

**Makna:**
Kode untuk pengumpulan data, konstruksi test set, pelabelan teacher, training, evaluasi, dan benchmark, beserta notebook yang mereproduksi setiap angka, tabel, dan gambar di paper ini, tersedia di [TODO: URL GitHub dan DOI Zenodo]. Model StaticKD tersedia di [TODO: URL Hugging Face]. Test set dirilis sebagai manifest berisi URL atau ID artikel, label, asal label, dan hash teks, beserta skrip rekonstruksi. Teks artikel tidak didistribusikan ulang karena hak cipta penerbit dan lisensi dataset sumber. Tabel pemetaan rubrik ke IPTC dirilis bersama kode. EMMediaTopic tersedia di repositori CLARIN.SI [9]. Tabel XIV mencantumkan lisensi aset yang dipakai dan dirilis dalam studi ini.

**Locked:** sitasi [9] Kuzman & Ljubešić 2025 · rujukan Table XIV

**Paraphrase:**
(tulis di sini)

[TABEL XIV — placeholder] Lisensi aset yang dipakai dan dirilis.

## Acknowledgment

---

### UCP-01 · main.tex baris 755

**Current:**
The authors thank the Department of Informatics Engineering, Sepuluh Nopember Institute of Technology, for its support of this work. The authors used Claude (Anthropic) to assist with writing the experiment code, with data processing (including the first draft of the section-to-IPTC mapping table, all of which the authors reviewed), and with reviewing and minor editing of the manuscript. The manuscript was written by the authors, who take full responsibility for its content and claims.

**Makna:**
Ucapan terima kasih kepada Departemen Teknik Informatika, Institut Teknologi Sepuluh Nopember, atas dukungannya. Pernyataan penggunaan AI: penulis memakai Claude (Anthropic) untuk membantu penulisan kode eksperimen, pengolahan data (termasuk draf pertama tabel pemetaan rubrik ke IPTC, yang seluruhnya ditinjau penulis), serta review dan penyuntingan minor naskah. Naskah ditulis oleh penulis, yang bertanggung jawab penuh atas isi dan klaimnya.

**Catatan:** Catatan: kalimat 'all of which the authors reviewed' perlu disamakan menjadi penulis pertama; pernyataan AI dikunci penulis, sesuaikan saat menulis ulang dan tambahkan versi model Claude saat submit.

**Locked:** —

**Paraphrase:**
(tulis di sini)
