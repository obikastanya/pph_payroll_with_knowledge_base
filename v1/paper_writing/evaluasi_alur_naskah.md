# Evaluasi Alur dan Keterbacaan Naskah StaticKD

Evaluasi [paper_final/main.tex](../paper_final/main.tex) dari sudut pandang pembaca manusia yang baru pertama kali membaca paper ini. Fokusnya pada kesinambungan antarkalimat, hal yang tersirat atau tidak dijelaskan, dan istilah yang dipakai sebelum didefinisikan. Fakta, angka, dan klaim tidak diubah.

- **Tanggal:** 18 Oktober 2026
- **Rujukan blok:** ID blok (PEN-01, MET-01, dst.) sama dengan [paper_rewrite.md](paper_rewrite.md), dan nomor baris mengacu ke `main.tex` saat ini.
- **Usulan teks** ditulis dalam bahasa Inggris sebagai contoh arah perbaikan. Sesuai [paper_rewrite_steps.md](paper_rewrite_steps.md), teks ini boleh ditulis ulang dengan kalimat sendiri; yang penting isinya (urutan logika, definisi, kesimpulan) masuk.
- Semua angka dalam usulan sudah ada di naskah atau kode. Kalau ada angka yang diambil dari kode, sumbernya disebut.

---

## 1. Diagnosis umum

Masalahnya bukan kalimat yang salah, tetapi **langkah penalaran yang dilewati**. Ada lima pola yang berulang:

| # | Pola | Contoh |
|---|---|---|
| A | **Istilah dipakai sebelum diperkenalkan** | "the development set" (baris 114) baru didefinisikan di baris 150; "token coverage" (baris 586) tidak pernah didefinisikan; "outside XLM-R pre-training" (baris 403) tidak pernah dijelaskan; "cascade mode" muncul tiba-tiba di Hasil |
| B | **Alasan disembunyikan** | Kenapa label uji tidak boleh dari teacher; kenapa set LLM tidak dipakai; kenapa fine-tuning tetap dipakai walaupun embedding beku lebih baik di set uji |
| C | **Angka tanpa kesimpulan** | Bagian Validity (IV-B) menyajikan akurasi, Wilcoxon, dan korelasi, tetapi tidak pernah menyimpulkan "jadi label rubrik tidak lebih buruk daripada label manusia" |
| D | **Satu paragraf, dua topik** | PEM-01: analisis token baru dan selisih per label dicampur; kontribusi 3: temuan ablasi dan detail pinning CPU |
| E | **Peta data tidak ada** | Ada tujuh set data dengan peran berbeda (distilasi, validasi internal, dev, held-out, uji, set cek LLM, sampel rubrik Inggris), tetapi tidak ada satu tempat yang menjelaskan peran masing-masing |

Keluhan tentang Study Design (MET-01) adalah gabungan pola A, B, dan E. Keluhan tentang Pendahuluan adalah pola B: kalimat pertama paper menyatakan kesimpulan ("pipelines assign articles to standard topics early") tanpa menjelaskan kenapa.

---

## 2. Daftar perubahan berdasarkan prioritas

**Wajib** = pembaca tersesat atau salah paham tanpa perubahan ini. **Disarankan** = alur jauh lebih mudah diikuti. **Opsional** = penghalusan.

| # | Prioritas | Blok (baris) | Masalah singkat |
|---|---|---|---|
| 1 | Wajib | PEN-01 (50) | Latar belakang pipeline hanya satu kalimat |
| 2 | Wajib | PEN-02, PEN-03 (52, 54) | Biaya tidak dihubungkan ke volume pipeline; logika fastText bolong |
| 3 | Wajib | MET-01 (114) + tabel baru | Study Design tidak menjelaskan Fig. 1, data, label, dan peran tiap set |
| 4 | Wajib | MET-33, MET-34, MET-35 (297–305) | Uji dan istilah yang dipakai di Hasil tidak ada di protokol |
| 5 | Wajib | HAS-07 s.d. HAS-10 (444–450) | Validity tanpa logika uji dan tanpa kesimpulan |
| 6 | Wajib | PEM-01 (644) | Analisis baru muncul di Discussion; logika "gap" tercampur |
| 7 | Wajib | ABS (41) | 294 kata, batas IEEE 250 |
| 8 | Wajib | Istilah (lihat §4) | "editorial topics" vs "editorial labels", dan lain-lain |
| 9 | Disarankan | Struktur Bab III | Urutan subbab tidak mengikuti alur Fig. 1 |
| 10 | Disarankan | PEN-04, PEN-05 (56, 58) | Distilasi tidak dijelaskan; alasan label independen tidak ada |
| 11 | Disarankan | MET-03 s.d. MET-09 (150–159) | Tujuan held-out dan langkah 5 tidak jelas; CC-News vs CC-NEWS |
| 12 | Disarankan | MET-11 s.d. MET-13, MET-22 (164–182) | Mekanisme dulu, konsep belakangan; kode bahasa |
| 13 | Disarankan | MET-30, MET-31 (251, 291) | τ transformer yang terpilih tidak disebut; tujuan baseline GPT-4o |
| 14 | Disarankan | HAS-01, HAS-02, HAS-12 (346, 348, 503) | Penyebab penurunan dev→uji; "much more expensive"; fine-tuning |
| 15 | Disarankan | HAS-19, HAS-20 (591, 593) | Separuh Tabel XI tidak dibahas |
| 16 | Disarankan | PEM-02 (646) | Argumen "number of layers" tidak eksplisit |
| 17 | Opsional | PEN-11, KES-01, Fig. 1, MET-21 | Lihat §3.6 |

Bagian yang **tidak perlu diubah** karena alurnya sudah baik: Related Work (PT-01 s.d. PT-05), deskripsi student dan folding (MET-24 s.d. MET-29), Efficiency Protocol paragraf kedua, Limitations, dan sebagian besar Discussion PEM-03 s.d. PEM-10.

---

## 3. Rincian dan usulan

### 3.1 Pendahuluan

#### #1 PEN-01 (baris 50): latar belakang pipeline

**Sekarang:**
> News analytics pipelines assign articles to standard topics early, so that the more expensive stages only process the topics that matter. The taxonomy most used by news agencies is ...

**Masalah sebagai pembaca:**
- Apa itu "news analytics pipeline", dan apa "the more expensive stages"?
- Kenapa klasifikasi topik ditaruh di depan?
- Kenapa biayanya penting? Ini inti argumen paper, tetapi tidak pernah dikatakan: **klasifikator topik adalah satu-satunya tahap yang membaca semua artikel**, sehingga biayanya tumbuh bersama seluruh aliran berita, sedangkan tahap lain hanya membaca artikel yang lolos filter.
- Kenapa harus taksonomi standar? Setiap penerbit menamai rubriknya sendiri. Paper ini sendiri punya buktinya (814 nama rubrik), tetapi tidak dipakai untuk motivasi.

**Usulan (dua paragraf):**
```latex
\IEEEPARstart{N}{ews} analytics pipelines process a continuous stream of articles from many sources and languages. Many of their later stages, such as entity extraction, sentiment scoring, or event detection, are needed only for some topics; a pipeline that tracks the economy does not need to analyze football results. Topic classification is therefore placed first. It decides which articles each later stage receives, and it is the only stage that reads every incoming article. Its cost grows with the whole stream, whereas the cost of the later stages grows only with the articles that pass the filter. A topic classifier at the head of such a pipeline thus has to be cheap per article and has to work in every language of the stream.

Routing by topic also needs the same topics for every source, while publishers name their sections differently; the section-to-IPTC mapping built in this study alone covers 814 section names (Section~\ref{sec:testset}). The taxonomy most used by news agencies is the Media Topic taxonomy of the International Press Telecommunications Council (IPTC). Its top level has 17 topics, such as \emph{politics}, \emph{economy, business and finance}, and \emph{sport}~\cite{iptc2024mediatopics,kuzman2025llm}.
```

**Catatan:** Kalimat "Many of their later stages ... are needed only for some topics" adalah penjelasan umum, bukan klaim empiris. Kalau ingin diperkuat, tambahkan sitasi sistem media monitoring yang nyata, lalu verifikasi dengan `scripts/verify_references.py`. Contoh tahap pipeline (entity, sentiment, event) sebaiknya diganti dengan contoh yang benar-benar kamu kenal dari praktik.

#### #2a PEN-02 (baris 52): hubungkan biaya dengan volume

**Masalah:** Angka 1,239 ms per artikel tidak terasa sebagai masalah sampai pembaca tahu berapa artikel yang harus diproses. Perhitungan "15.1 cores per sejuta artikel per hari" sudah ada di Hasil (baris 549), tetapi baru muncul di halaman 10. Selain itu, kenapa targetnya CPU tidak pernah dijelaskan.

**Usulan:** ganti kalimat "An encoder with 559.9 million parameters is still expensive without a GPU. ... still needs 1,239~ms (Section~\ref{sec:res-eff})." menjadi:
```latex
An encoder with 559.9~million parameters is still expensive when no graphics processing unit (GPU) is available, and this study targets such CPU-only deployment. On one central processing unit (CPU) core the model needs 2,971~ms per article, and its fastest CPU configuration, an Open Neural Network Exchange (ONNX) export quantized to 8-bit integers (int8), still needs 1,239~ms. At these speeds, a stream of one million articles per day would occupy 15.1 to 34.8 CPU cores for topic classification alone (Section~\ref{sec:res-eff}).
```
Kalimat Luccioni sesudahnya tetap.

**Catatan:** Tambahkan alasan nyata kenapa CPU, misalnya server pipeline yang sudah ada tidak punya GPU, atau GPU tidak sepadan untuk tahap filter. Hanya penulis yang tahu alasan ini, dan reviewer akan menanyakannya.

#### #2b PEN-03 (baris 54): logika fastText

**Masalah:** Argumennya: fastText tidak bisa transfer lintas bahasa, dan ini masalah karena label IPTC hanya ada untuk empat bahasa. Pembaca yang teliti akan bertanya: *paper ini sendiri melabeli 69 bahasa dengan teacher, dan fastText + KD juga dilatih di sana, jadi kenapa empat bahasa itu masalah?* Jawabannya tidak tertulis: korpus berlabel otomatis pun tidak mencakup semua bahasa aliran berita (13 bahasa uji tidak punya data distilasi sama sekali), dan di bahasa seperti itu fastText runtuh. Kalimat pembuka "The target is ..." juga terlalu mendadak.

**Usulan:**
```latex
Such a pipeline needs a topic classifier that covers many languages, runs in milliseconds per article on an ordinary CPU, and has a small footprint and few dependencies. Existing options meet only part of this. Int8 quantization gives a factor of 2.3 over PyTorch fp32. Small distilled transformers~\cite{sanh2019distilbert,wang2021minilmv2} gain about one more order of magnitude: in the CPU benchmark of this study, MiniLM-L6 is 21 times faster than the ONNX int8 teacher but still needs 57.8~ms per article. fastText~\cite{joulin2017bag} needs about 2~ms, but it learns its word vectors from scratch and therefore knows only the languages and words of its training data. IPTC training labels released with the open classifier cover only four languages~\cite{emmediatopic2025}, and even a corpus labeled automatically cannot contain every language of a news stream. No available IPTC classifier is both multilingual and this cheap.
```

#### #10a PEN-04 (baris 56): distilasi belum dijelaskan

**Masalah:** "distills" dan "teacher/student" dipakai tanpa penjelasan; definisinya baru ada di Related Work II-B. Tiga properti tidak diberi penanda urutan, sehingga pembaca kehilangan hitungan: properti kedua dan ketiga terlihat seperti kalimat lanjutan biasa. Selain itu, alasan *kenapa* embedding yang selaras lintas bahasa penting (bahasa tanpa data latih tetap dekat dengan bahasa yang dilatih) tidak disebut, padahal itu temuan utama paper.

**Usulan:** ganti dua kalimat pertama dan penanda properti:
```latex
This paper proposes StaticKD, which distills~\cite{hinton2015distilling} the XLM-R-large IPTC classifier into a far simpler student. In knowledge distillation, an expensive model (the teacher) labels training data, and a cheap model (the student) is trained to reproduce the teacher outputs. Three properties of the problem allow a student that is much simpler than usual. The first is that a teacher that works across languages can label unlabeled news in any language, so training data for the student cost no annotation. The second is that multilingual static embeddings, distilled from sentence encoders~\cite{tulkens2024model2vec,wada2025static,chen2024bgem3}, give each token one fixed vector and place translation equivalents close to each other. Looking up such a vector costs almost nothing, and tokens of a language without training data still lie near related tokens of other languages. The third is that news topics are strongly tied to vocabulary, which is why bag-of-words representations remain competitive for topic classification~\cite{galke2022bow}.
```
Sisa paragraf ("The student therefore averages ...") tetap.

#### #10b PEN-05 (baris 58): kenapa label tidak boleh dari teacher

**Masalah:** Kalimat pertama menyatakan syaratnya ("labels that do not come from the teacher") tanpa alasan. Ini alasan yang sama yang hilang di MET-01. Kata "unified" juga tidak dijelaskan, dan "translated onto" tidak konsisten dengan "mapped" di bagian lain.

**Usulan:** sisipkan satu kalimat setelah kalimat pertama, dan ubah dua kalimat terakhir:
```latex
A multilingual claim also requires a multilingual test set whose labels do not come from the teacher. A student that is trained to imitate the teacher and then scored on teacher labels is scored only on imitation, and every teacher error it copies counts as correct.
...
To fill this gap, this study builds a test set of 12,744 articles in 47 languages that unifies several sources under the 17 IPTC topics.
...
These labels are editorial decisions of publishers or annotators, mapped onto the official IPTC taxonomy, and no model that reads the article text is involved. This paper calls them \emph{editorial labels} and the combined set the \emph{unified test set}.
```

---

### 3.2 Metodologi

#### #9 Struktur Bab III

**Masalah:** Urutan sekarang: Study Design → Problem Formulation → Distillation Data → **Unified Test Set** → Teacher → Student → Baselines → Protokol. Pembaca membaca data distilasi, lalu dua halaman tentang set uji, lalu kembali ke teacher yang melabeli data distilasi. Alur kiri-ke-kanan Fig. 1 terputus.

**Usulan urutan:**

| Baru | Subbab | Catatan |
|---|---|---|
| III-A | Problem Formulation | Tugas didefinisikan dulu |
| III-B | Study Overview | Pengganti Study Design (#3) |
| III-C | Distillation Data and Development Set | — |
| III-D | Teacher and Distillation Labels | Dipindah ke atas |
| III-E | The StaticKD Student | — |
| III-F | Baselines | — |
| III-G | Unified Test Set Construction | Dipindah ke bawah, sebelum protokol evaluasi |
| III-H s.d. III-J | Evaluation, Efficiency, Experimental Design | Tetap |

Semua rujukan memakai `\ref`, jadi nomor subbab ikut berubah otomatis. Tambahkan label `sec:distdata`, `sec:teacher`, `sec:student`, dan `sec:baselines` untuk dipakai di III-B.

#### #3 MET-01 (baris 114): Study Overview

Ini keluhan utama. Masalahnya, kalimat demi kalimat:

| Kalimat sekarang | Masalah |
|---|---|
| "Fig. 1 summarizes the study." | Fig. 1 adalah **pipeline StaticKD** (sesuai caption-nya), bukan ringkasan studi: baseline, dev set, held-out, dan benchmark tidak ada di gambar. Teks dan caption tidak cocok. |
| "The teacher labels a large set of unlabeled news articles once" | Artikel apa, berapa, bahasa apa? Label apa yang dihasilkan (17 logit)? |
| "StaticKD and all baselines learn from these labels." | Belajar dengan cara apa? StaticKD dan transformer memakai distribusi penuh, fastText dan SVM hanya label teratas, dan satu fastText malah memakai label GPT-4o. Kalimat ini juga tidak tepat untuk baseline GPT-4o. |
| "A separate test set, whose labels do not come from the teacher, ..." | Muncul tiba-tiba. Alasannya (label teacher hanya mengukur peniruan) tidak ada. |
| "A CPU benchmark measures inference cost." | Berdiri sendiri, tidak terhubung. |
| "fixed on the development set" | Development set belum pernah diperkenalkan (baru di baris 150). |
| "when τ=1 and the three-seed ensemble were chosen" | τ dan ensemble belum diperkenalkan. |
| "LLM labels resemble the labels the teacher was trained on, so no reported result uses this set." | Alasannya tersirat: teacher dilatih dengan label GPT-4o dari prompt yang sama, jadi label Claude tidak independen dari teacher. |

**Usulan:**
```latex
\subsection{Study Overview}
\label{sec:overview}
The study has three parts. The first builds the StaticKD student by distillation, the second measures its accuracy against labels that do not come from the teacher, and the third measures its inference cost on CPU.

Fig.~\ref{fig:pipeline} shows the pipeline that the first part produces. The teacher reads 285,999 unlabeled news articles in 69 languages once, offline, and its 17 topic logits for each article are stored (Sections~\ref{sec:distdata} and~\ref{sec:teacher}). StaticKD learns to reproduce the full teacher distribution over the 17 topics. The baselines learn from the same articles, the two small transformers from the full distribution and fastText and TF-IDF + SVM from the top teacher label only; one additional fastText reference is trained on GPT-4o labels instead (Section~\ref{sec:baselines}). After training, the linear head of StaticKD is folded into a table of 17 scores per token, and this table is the only model used at inference (Section~\ref{sec:student}).

Scores against teacher labels only show how closely a model imitates the teacher. The second part therefore uses a separate test set with editorial labels from newsroom sections, publisher categories, and human annotators (Section~\ref{sec:testset}). All accuracy comparisons, statistical tests, and subgroup analyses in Section~\ref{sec:results} use this set. The third part runs every model on the same sample of test articles on CPU only (Section~\ref{sec:effprotocol}).

Table~\ref{tab:datasets} lists every data set of the study and its role. All choices of the StaticKD recipe were made on the development set, the development split of EMMediaTopic (1,000 articles in four languages with GPT-4o labels), and the recipe was fixed \emph{before} the test set was built. No hyperparameter was selected on the test set. One further set informed two choices, the temperature $\tau=1$ and the three-seed ensemble (Section~\ref{sec:student}): 320 articles in 16 languages labeled by an LLM (Claude) with the prompt of~\cite{kuzman2025llm}. The teacher was trained on labels that an LLM produced with the same prompt, so these labels are not independent of the teacher, and no reported result uses this set.
```

**Tabel baru** (lebar satu kolom, diletakkan dekat III-B):
```latex
\begin{table}[!t]
\caption{Data Sets of the Study and Their Roles}
\label{tab:datasets}
\centering
\footnotesize
\setlength{\tabcolsep}{3pt}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{@{}lrrll@{}}
\toprule
Set & Docs & Lang. & Labels & Used for \\
\midrule
Distillation data & 285,999 & 69 & teacher logits & training all + KD models \\
\quad internal validation (3\%) & 8,579 & -- & teacher logits & choosing the epoch \\
Development set (EMMediaTopic dev) & 1,000 & 4 & GPT-4o & choosing the recipe \\
CC-News held-out & 12,554 & 63 & teacher & agreement on unseen sites \\
Unified test set & 12,744 & 47 & editorial & all accuracy results; CPU sample \\
LLM check set & 320 & 16 & Claude & informal check, not reported \\
English section sample & 754 & 1 & JSON-LD section & label validity only \\
\bottomrule
\end{tabular}}
\end{table}
```

**Opsional untuk Fig. 1:** beri label pada panah dari set uji ke tabel, misalnya `\draw[arr] (ts.north) -- node[lab, right]{evaluate} (tab.south);`, supaya pembaca tahu panah itu berarti evaluasi, bukan pelatihan.

#### MET-02 (baris 147): definisi "independent labels"

Istilah "independent labels" dipakai di baris 147, 160, dan caption Tabel IV tanpa definisi. Cukup ubah akhir kalimat menjadi: "... and whose accuracy against independent labels, i.e., labels that do not come from the teacher, is as close as possible to that of $f_T$."

#### #11 MET-03 s.d. MET-09 (baris 150–159): data distilasi

**Masalah:**
1. Paragraf dibuka langsung dengan EMMediaTopic tanpa menjelaskan apa yang dibutuhkan dari data distilasi (cakupan bahasa).
2. Tidak disebut bahwa EMMediaTopic train **dilabeli ulang oleh teacher** (sudah dicek di [scripts/label_with_teacher.py](../scripts/label_with_teacher.py)). Pembaca bisa mengira yang dipakai label GPT-4o.
3. Dev set hanya berisi empat bahasa. Ini menjadi argumen penting di Discussion ("a development set in the training languages cannot reveal this trade-off"), tetapi tidak disebut di sini.
4. Langkah 4: tujuan held-out per situs tidak disebut.
5. Langkah 5: dari mana 156,157 dokumen itu, dan kenapa batasnya berbeda dengan langkah 3 (150 vs 400 per situs)? Ini sebenarnya "extra CC-News" yang dibuang di ablasi "130k documents", tetapi hubungannya tidak ditulis.
6. "CC-News 2019–2021" vs "CC-NEWS 2024–2026": perbedaan kapitalisasi ini membingungkan dan tidak dijelaskan.

**Usulan MET-03:**
```latex
The distillation data have to cover many languages, because the student adapts only to the languages it sees in training. They come from two sources. EMMediaTopic 1.0~\cite{emmediatopic2025,kuzman2025llm} contains Catalan, Greek, Croatian, and Slovenian articles labeled by GPT-4o, on which the teacher was fine-tuned. Its training split (20,000 articles) is part of the distillation data and, like every other distillation document, is labeled by the teacher. Its development split (1,000 articles, median 218 words) was never used to train the teacher or the student and serves as the development set for choosing the recipe. This development set covers only the four EMMediaTopic languages.
```

**Usulan MET-04:**
```latex
Most of the distillation data come from CC-News 2019--2021, a multilingual split~\cite{cloversearch_ccnews} of the news archive of Common Crawl, which supplies unlabeled news in many more languages. The test set draws on a later period of the same archive with different sites; this paper writes CC-NEWS 2024--2026 for that part (Section~\ref{sec:testset}). CC-News 2019--2021 was processed with the following steps.
```

**Langkah 4 dan 5:**
```latex
\item Form a held-out split by site: all documents of some sites are set aside (at most 20\% per language), so that agreement with the teacher can be measured on sites that the student never saw.
\item Add 156,157 further documents from training sites only, with looser caps (at most 5,000 per language and 400 per site). The ablation with 130 thousand documents (Section~\ref{sec:res-abl}) leaves these documents out.
```

#### #12a MET-11 s.d. MET-13 (baris 164–168): set uji, konsep dulu

**Masalah:**
- Subbab dibuka dengan mekanisme (WARC per bulan, field JSON-LD) sebelum pembaca tahu **ide** labelnya. Ide intinya ("Section and category labels record where the newsroom placed an article ... not circular") baru muncul di paragraf ketiga.
- Baris 168 mendefinisikan "editorial **topics**", padahal seluruh paper memakai "editorial **labels**" (baris 67, 87, 132, 442, 656). Definisi menunjuk ke istilah yang tidak pernah dipakai lagi.
- "814 names mapped to 79 nodes" padahal labelnya 17 topik. Langkah dari node ke topik tingkat atas tidak disebut.

**Usulan paragraf pembuka baru** (sebelum paragraf "The first source ..."):
```latex
The test set uses labels that already exist: the section in which a newsroom published an article, the category that a publisher assigned to it, or the topic that human annotators of a public dataset chose. These editorial labels record editorial decisions, and no model that reads the article text produces them, so an evaluation on them is not circular with respect to the teacher. They come from two sources and need one added step, a mapping onto the IPTC taxonomy.
```
Lalu "The first source is CC-NEWS 2024–2026 ..." bisa diawali: "The first source uses page metadata, in which many news sites record the section of each article (Section~\ref{sec:related})." Sesudah itu paragraf sumber kedua. Paragraf pemetaan dimulai dari "Section names are normalized ...", dan tiga kalimat konsep yang sudah dipindah dihapus dari sana.

**Tambahan pada paragraf pemetaan:** "This gives 814 names mapped to 79 nodes; each node then counts as its top-level ancestor, which is one of the 17 labels."

**Catatan:** Angka "102 ambiguous, language-specific, and rejecting rules" dan "62 ambiguous names" mudah membingungkan (62 adalah bagian dari 102?). Kalau benar, tulis "102 other rules, among them the 62 ambiguous names". Cek dulu ke file tabel pemetaan.

#### #12b MET-21, MET-22 (baris 180–182): kelompok bahasa dan kode bahasa

**Masalah:**
- Pengelompokan "none / <500 / ≥500 dokumen distilasi" dipakai di seluruh Bab IV, tetapi tujuannya tidak disebut.
- Kelompok "outside XLM-R pre-training" (Tabel V, baris 403; dipakai di baris 450, 591, 654, 688) tidak pernah didefinisikan.
- Kode bahasa (ha, yo, ig, lg, ln, pcm, rn, sn, ti, ml, or, pa) tidak pernah diuraikan. Kebanyakan pembaca tidak tahu bahwa lg adalah Luganda atau rn adalah Kirundi.

**Usulan tambahan** setelah "... and 25 have at least 500.":
```latex
This grouping, used throughout Section~\ref{sec:results}, separates transfer to languages without distillation data from fit on languages with data. A second grouping follows the teacher: 1,750 test articles are in languages outside the 100 languages on which XLM-R was pre-trained~\cite{conneau2020xlmr}.
```
Untuk kode bahasa, uraikan nama bahasa saat pertama kali muncul, misalnya "Hausa (ha), Yoruba (yo), Igbo (ig), Bengali (bn), Punjabi (pa)". Pilihan lain: tambahkan daftar kode bahasa di caption Fig. 2.

**Opsional (MET-21):** alasan batas 50 artikel per pasangan bahasa–label dan urutan preferensi sumber tidak ditulis. Kalau alasannya memang agar beberapa pasangan yang sering muncul tidak mendominasi skor, dan label manusia lebih dipercaya, tulis itu dalam setengah kalimat.

#### #13 MET-30, MET-31 (baris 251, 291): compact dan baseline

**MET-30.** Kalimat pembuka "The internal structure of the Unigram tokenizer needs much more RAM than the table itself (16 MB)" tidak menyebut berapa RAM-nya. Usulan:
```latex
At inference, StaticKD occupies 501~MB of RAM (Section~\ref{sec:res-eff}), most of it for the internal structure of the Unigram tokenizer rather than for the 16~MB table.
```
Kalimat "Table~\ref{tab:hparams} lists the hyperparameters of all models." lebih cocok dipindah ke akhir paragraf Baselines.

**MET-31.**
- "with the temperature τ∈{1,2} chosen on the development set": nilai yang terpilih tidak disebut. Dari [models/baselines/*/train_meta.json](../models/baselines/), MiniLM terpilih τ=1, dan DistilmBERT memakai τ yang sama (lihat [scripts/train_transformers.py:74](../scripts/train_transformers.py#L74)). Tulis: "... trained with the loss of \eqref{eq:kd} on the teacher logits; of $\tau\in\{1,2\}$, the development set selected $\tau=1$. DistilmBERT + KD uses ... with the same recipe and $\tau=1$."
- Tujuan baseline GPT-4o tidak jelas ("As a reference equivalent to the labeled data available to [2]"). Usulan: "As a reference for the conventional route without a teacher, fastText is also trained only on the GPT-4o labels of the EMMediaTopic training split, the labeled data available to~\cite{kuzman2025llm}."

#### #4 MET-33 s.d. MET-35 (baris 297–305): protokol evaluasi

**Masalah:** Paragraf MET-34 adalah daftar uji yang padat tanpa menyebut uji mana menjawab pertanyaan apa. Selain itu, beberapa hal yang dipakai di Hasil **tidak ada sama sekali di protokol**:

| Dipakai di | Istilah atau uji | Status di Metodologi |
|---|---|---|
| Tabel XI, baris 581–587 | Spearman, Kruskal–Wallis | tidak disebut |
| Tabel XI, baris 586–587 | token coverage | tidak didefinisikan |
| Baris 585, 591 | accuracy gap (arahnya StaticKD − teacher?) | tidak didefinisikan |
| Tabel V, baris 403 | teacher pre-training coverage | tidak ada di daftar subgrup |
| IV-F, baris 633 | cascade mode, θ, effective throughput | tidak ada |
| PEM-01, baris 644 | token yang "favor one label most strongly" | tidak ada |

**Usulan MET-34** (tiga kalimat pertama tentang bootstrap tetap; sisanya diganti):
```latex
The tests follow the research questions. For RQ1, two models evaluated on the same documents are compared with a paired (cluster) bootstrap with 2,000 resamples for $\Delta$macro-F1~\cite{koehn2004significance} and an exact McNemar test for accuracy~\cite{mcnemar1947}, with Holm correction~\cite{holm1979} within each set. A Wilcoxon signed-rank test on per-language macro-F1 and accuracy checks whether a difference holds across languages~\cite{dror2018hitchhiker}. For RQ2, each ablation variant is trained with five seeds and the final recipe with ten, and each variant is compared with the final recipe by a Welch test over seeds, Holm-corrected. For RQ4, results are split by label origin, region, amount of distillation data in the language, teacher pre-training coverage, site diversity, script, language, and label. Per-language properties are related to performance with Spearman correlations and, for scripts, a Kruskal--Wallis test. Two per-language quantities serve there. The \emph{accuracy gap} is the StaticKD accuracy minus the teacher accuracy. The \emph{token coverage} is the share of token occurrences in the test articles of a language whose token occurs at least 10 times in the distillation data; tokens below this count are rarely updated in training (Section~\ref{sec:student}). Calibration is measured with the expected calibration error (ECE, 15 bins)~\cite{guo2017calibration}, because the cascade of Section~IV-F routes articles by the confidence of StaticKD.
```
Definisi token coverage sudah dicocokkan dengan kode di [src/notebook_build/part5.py:186-192](../src/notebook_build/part5.py#L186-L192) (`counts >= 10`, porsi kemunculan token per bahasa uji).

**Usulan tambahan untuk MET-35** (Efficiency Protocol), di akhir paragraf pertama:
```latex
In cascade mode, StaticKD decides the articles on which its top probability is at least $\theta$ and passes the rest to the ONNX int8 teacher. With a share $s$ decided by StaticKD and single-core throughputs $r_S$ and $r_T$, the effective throughput is $1/(1/r_S+(1-s)/r_T)$.
```
Rumus ini sama dengan kode di [src/notebook_build/part5.py:347](../src/notebook_build/part5.py#L347); dengan s = 60.3%, r_S = 473, dan r_T = 0.77 hasilnya sekitar 1.92 dok/detik, sesuai Tabel XII.

---

### 3.3 Hasil

#### #14 HAS-01, HAS-02, HAS-12

**HAS-01 (baris 346).** "Both scores lie far below the development scores ..., because most of the test set lies outside the languages, sources, and period of the teacher training data." Penurunan 0.822 → 0.598 sangat besar, dan pembaca akan curiga pada labelnya. Bagian IV-B sendiri menunjukkan bahwa sebagian penurunan berasal dari skema kategori sumber yang berbeda dengan IPTC. Usulan: "... because most of the test set lies outside the languages, sources, and period of the teacher training data, and because many test labels follow category schemes other than IPTC (Section~\ref{sec:res-validity})."

**HAS-02 (baris 348).**
- "DistilmBERT (0.534) is on par with StaticKD while being much more expensive." Ganti "much more expensive" dengan angka: "... while needing 198~ms per article against 2.03~ms (Section~\ref{sec:res-eff})."
- Setelah kalimat fastText GPT-4o (0.665 → 0.086), tambahkan kesimpulannya, yang sekarang dibiarkan tersirat: "Without teacher labels on multilingual news, a cheap model does not carry over beyond the four labeled languages."

**HAS-12 (baris 503).** Embedding beku lebih baik di set uji (+0.014, p<0.001). Pertanyaan pertama pembaca: *kenapa resep final tidak memakai embedding beku?* Jawabannya baru ada di Discussion PEM-04. Tambahkan penunjuk di akhir paragraf: "The final recipe was fixed on the development set before this effect was observed; Section~\ref{sec:discussion} explains why that set cannot reveal it." Ini juga mencegah kesan menyembunyikan hasil yang tidak menguntungkan.

**Opsional, HAS-06 (baris 413):** "the teacher itself reaches its lowest macro-F1 of all sources there" (MN-DS, satu-satunya sumber IPTC asli) adalah hasil yang mengejutkan, tetapi tidak dijelaskan. Tambahkan penunjuk ke IV-B, yang menyebut label *society* di MN-DS sulit bahkan bagi anotator.

#### #5 HAS-07 s.d. HAS-10 (baris 444–450): Validity

**Masalah:**
- **HAS-07:** logika ujinya tersirat. Kenapa membandingkan kesesuaian teacher dengan label rubrik dan label manusia bisa menunjukkan validitas label rubrik?
- **HAS-08:** "In English, every language–label pair of the test set is filled with human-labeled sources." Kalimat ini sulit dipahami. Maksudnya: karena sampling mengutamakan label manusia, bagian bahasa Inggris set uji tidak berisi label rubrik sama sekali, sehingga perlu sampel terpisah. Paragraf juga berakhir dengan angka tanpa kesimpulan.
- **HAS-09:** hanya angka, tanpa kesimpulan.
- **HAS-10:** baru di sini terlihat kenapa teacher justru lebih cocok dengan label rubrik daripada label manusia (kategori MasakhaNEWS lebih luas daripada target IPTC). Hubungan ini perlu ditulis eksplisit.

**Usulan:**

HAS-07, tambahkan di akhir paragraf:
```latex
If section labels were much noisier than human labels, the teacher would agree with them clearly less often than with human labels in the same language.
```

HAS-08, ganti kalimat pertama dan tambahkan kesimpulan:
```latex
The sampling prefers human-labeled sources (Section~\ref{sec:testset}), so the English part of the test set contains only human labels from MN-DS and MasakhaNEWS. A separate sample of 754 English CC-NEWS articles with JSON-LD section labels was therefore drawn from 306 sites outside the test set, at most 50 per label.
[... angka tetap ...]
In English, the teacher thus agrees with section labels at least as often as with human labels, and both label types find the same labels hard.
```

HAS-09:
```latex
French, the only other language with both label types in the test set, shows the same direction: the teacher reaches an accuracy of 0.716 on 208 articles with section labels and 0.500 on 200 human-labeled MasakhaNEWS articles.
```

HAS-10, kalimat pembuka baru:
```latex
The lower agreement on human labels comes mostly from the category schemes of the human-labeled sources.
```
Sesudah itu "A last check looks at each source category ..." tetap.

**Catatan:** Pastikan bahwa bahasa Prancis memang satu-satunya bahasa lain yang punya kedua jenis label di set uji, sebelum memakai frasa "the only other language".

#### #15 HAS-19, HAS-20 (baris 591–593): analisis per bahasa

**Masalah:**
- Tabel XI berisi tujuh baris, tetapi teks hanya membahas tiga. Baris "number of training sites" dan tiga baris uji (gap vs data, accuracy vs token coverage, gap vs token coverage) tidak dibahas.
- "accuracy gap of −0.024": arahnya tidak disebut.
- Paragraf India (HAS-20) sebenarnya adalah contoh token coverage rendah, tetapi tidak dihubungkan ke baris tabel itu.
- Kode bahasa tidak diuraikan.

**Usulan HAS-19:**
```latex
In a typical language StaticKD is close to the teacher, with a median per-language accuracy gap (StaticKD minus teacher) of $-$0.024 (Fig.~\ref{fig:lang}). Table~\ref{tab:factors} relates the agreement and the gap to properties of the language. On the held-out set (53 languages with at least 20 documents), the agreement of StaticKD with the teacher rises with the log amount of distillation data ($\rho=0.31$, $p=0.022$), with the number of training sites ($\rho=0.29$, $p=0.033$), and with teacher confidence ($\rho=0.71$, $p<0.001$), and it does not differ significantly across scripts (Kruskal--Wallis $H=10.37$, $p=0.065$). On the test set, the gap shrinks as the amount of distillation data grows ($\rho=0.52$, $p<0.001$) and as the token coverage rises ($\rho=0.49$, $p<0.001$). The weak spot is a group of African languages. On the eight languages that lie outside XLM-R pre-training and are also absent from the distillation data, Igbo (ig), Luganda (lg), Lingala (ln), Nigerian Pidgin (pcm), Kirundi (rn), Shona (sn), Tigrinya (ti), and Yoruba (yo), StaticKD reaches a mean accuracy of only 0.407, while the teacher reaches 0.643.
```

**Usulan HAS-20**, kalimat pertama:
```latex
The four languages with the lowest token coverage, Bengali (bn), Malayalam (ml), Odia (or), and Punjabi (pa), show how StaticKD handles text whose tokens it has hardly seen in training.
```
Sisa paragraf tetap.

**Paragraf baru** (dipindah dari PEM-01, lihat #6), letakkan setelah HAS-21 (per label):
```latex
The table also shows which tokens carry the topic signal. The specificity of a token is the largest difference between one entry of its table row and the mean of its other 16 entries. Keeping only the 10\% most specific tokens of each article (about 58 tokens) leaves the test macro-F1 almost unchanged (0.543 against 0.545), whereas a random 10\% of the tokens gives 0.435.
```
Definisi specificity sudah dicocokkan dengan sel 88 di [notebooks/StaticKD_IPTC_final.ipynb](../notebooks/StaticKD_IPTC_final.ipynb): `max_y (T[t,y] − mean_{y'≠y} T[t,y'])`.

**HAS-22 (baris 633).** Setelah definisi cascade masuk ke protokol (#4), tambahkan satu kalimat penghubung antara kalibrasi dan cascade: "Because the confidence of StaticKD is better calibrated than that of the teacher, it can decide which articles need the teacher."

---

### 3.4 Pembahasan

#### #6 PEM-01 (baris 644)

**Masalah:**
1. Analisis "10% token paling spesifik" adalah **hasil baru** yang tidak pernah muncul di Hasil, dan cara mengukur "favor one label most strongly" tidak dijelaskan. Discussion seharusnya menafsirkan hasil, bukan memperkenalkannya.
2. "The remaining gap to the teacher concentrates in two places. The first is labels whose vocabulary overlaps with other topics." Bukti yang diberikan mencampur dua hal berbeda:
   - label dengan **selisih terbesar terhadap teacher** (environment, religion, arts);
   - label yang **paling sulit secara absolut** (society, disaster, human interest, conflict), yang juga sulit bagi teacher, sehingga **bukan** bagian dari "gap to the teacher".

   Selain itu, klaim "vocabulary overlaps with other topics" tidak dibuktikan untuk environment, religion, dan arts.

**Usulan:**
```latex
A table lookup keeps about nine tenths of the teacher macro-F1 at an inference cost two to three orders of magnitude lower (Sections~\ref{sec:res-acc} and~\ref{sec:res-eff}). This agrees with the finding that order-free representations are already competitive for topic classification~\cite{galke2022bow}. The token analysis of Section~IV-E points to the reason: the 10\% most topic-specific tokens of an article carry almost all of its topic signal.

The remaining gap to the teacher has two sources. The first is a few labels: \emph{environment}, \emph{religion}, and \emph{arts} lose the most against the teacher (Fig.~\ref{fig:label}). The labels on which StaticKD scores lowest, \emph{society}, \emph{disaster}, \emph{human interest}, and \emph{conflict}, are a different case. They are also among the hardest labels for the teacher, and \emph{society} and \emph{human interest} are known to be difficult for human annotators as well~\cite{kuzman2025llm}, so their low scores reflect the label definitions more than the student. The second source is languages that are underrepresented in the distillation data (Table~\ref{tab:groups}).
```
Kalau ingin mempertahankan klaim "vocabulary overlap", berikan buktinya, misalnya pasangan kebingungan environment dengan label lain dari confusion matrix.

#### #16 PEM-02 (baris 646)

**Masalah:** "suggests that the quality of the initial multilingual representation matters more than the number of layers." Perbandingan jumlah layer tidak eksplisit: kedua transformer sama-sama 6 layer. Argumennya sebenarnya: DistilmBERT punya 6 layer tetapi tidak lebih baik daripada StaticKD yang tidak punya layer sama sekali.

**Usulan:**
```latex
With the same distillation data, MiniLM-L6 closes part of this gap, whereas DistilmBERT does not (Table~\ref{tab:sig}). Both have six transformer layers and cost one to two orders of magnitude more than StaticKD, which has none. MiniLM comes from a distillation of XLM-R-large and DistilmBERT from mBERT, which suggests that the starting multilingual representation matters more than the number of layers. Both transformers also read at most 256 tokens (Section~\ref{sec:baselines}), which may lower their scores.
```

**Opsional:** Discussion menjawab RQ dengan urutan RQ1, RQ2, RQ4, RQ3, dan hanya PEM-03 yang diberi tag "(RQ2)". Tag serupa di awal PEM-01 (RQ1), PEM-06 (RQ4), dan PEM-09 (RQ3) akan membantu pembaca menghubungkan pembahasan dengan pertanyaan riset.

---

### 3.5 Abstrak (#7)

Abstrak sekarang **294 kata**, sedangkan [paper_rules.md](paper_rules.md) mengutip IEEE: 150–250 kata. Abstrak juga belum menyebut peran klasifikasi dalam pipeline. Usulan (248 kata, dihitung dengan `wc -w`):

> News analytics pipelines classify every incoming article by topic before the expensive analysis stages, so the topic classifier must be cheap and work across languages. The open multilingual classifier for the International Press Telecommunications Council (IPTC) Media Topic taxonomy, based on XLM-RoBERTa-large, takes 1,239 to 2,971 milliseconds per article on one processor core. StaticKD uses this classifier as a teacher and distills it into a table with 17 scores for each vocabulary token, one per top-level IPTC topic, so classifying an article only requires tokenizing it and averaging the scores of its tokens. The table starts from multilingual static embeddings and learns from the teacher's outputs on 285,999 news articles in 69 languages. A new test set of 12,744 articles in 47 languages uses topics assigned by human annotators or newsroom editors and mapped onto IPTC, so no test label comes from a model that reads the article. On this test set StaticKD reaches a macro-F1 of 0.545, or 91.1% of the teacher score of 0.598, and is more accurate than fastText and a linear support vector machine trained on the same teacher labels. It classifies 473 articles per second per core, about 616 times faster than the 8-bit quantized teacher, with a 34-megabyte model. Ablations with five seeds show that accuracy comes mainly from multilingual training data and from pre-trained cross-lingual embeddings, and that the top teacher label works as well as the full teacher distribution. Fine-tuning the embeddings helps the training languages but hurts unseen languages.

**Yang dikorbankan:** kalimat terakhir versi lama ("StaticKD is weakest on languages covered neither by its training data nor by the pre-training data of the teacher"). Kalimat fine-tuning sudah menyinggung bahasa yang tidak dilatih. Kalau kelemahan ini dianggap lebih penting, tukar kedua kalimat itu.

---

### 3.6 Opsional

- **PEN-11, kontribusi 3 (baris 68):** item ini mencampur temuan ablasi dengan detail benchmark ("pinned to the fast cores of a hybrid CPU"). Pecah menjadi dua item, atau ganti kalimat keduanya dengan: "A CPU-only comparison of the accuracy and cost of nine configurations from six model families, StaticKD included, under one protocol (Section~\ref{sec:effprotocol})." Detail pinning sudah ada di Metodologi.
- **PEN-06 (baris 60):** "label sources" → "label origins", supaya sama dengan istilah di Metodologi.
- **KES-01 (baris 684):** Pendahuluan baru (#1) membuka dengan pipeline. Kesimpulan bisa menutup lingkaran itu dengan satu kalimat: "For a pipeline with one million articles per day, topic classification then needs 0.02 CPU cores instead of 15.1."

---

## 4. Konsistensi istilah

| Istilah | Lokasi | Perbaikan |
|---|---|---|
| "editorial topics" | 168 (satu-satunya, dan justru di definisinya) | → "editorial labels", seperti di baris 67, 87, 132, 442, 656 |
| "label sources" | 60 | → "label origins" (baris 68, 182, dst.) |
| "translated onto" | 58, 168 | → "mapped onto" |
| "the development set" | 114, sebelum definisi di 150 | definisikan di III-B (#3) |
| "independent labels" | 147, 160, caption Tabel IV | definisikan di 147 |
| "token coverage", "accuracy gap" | 585–587, 591 | definisikan di protokol (#4) |
| "outside XLM-R pre-training" | 403, 450, 591, 654, 688 | definisikan di MET-22 (#12b) |
| "cascade mode", θ | 611–633, 662, 678 | definisikan di protokol (#4) |
| kode bahasa | 182, 591, 593, 648, 654 | uraikan nama bahasa saat pertama muncul |
| "CC-News" vs "CC-NEWS" | 152 dan seterusnya | jelaskan sekali di MET-04 (#11) |

---

## 5. Dampak dan pengecekan setelah mengedit

- **Panjang:** perubahan wajib dan disarankan menambah sekitar 0.5–0.7 halaman, termasuk tabel peran data. Pemendekan abstrak dan beberapa kalimat yang dipindah (bukan diduplikasi) mengurangi sebagian.
- **Angka:** tidak ada angka baru. Beberapa angka lama muncul di tempat tambahan (15.1, 34.8, 57.8, 198, 2.03, 1,750, 501). `scripts/check_paper.py` mungkin melaporkan jumlah kemunculan yang berubah; itu memang disengaja.
- **Tabel:** tabel baru `tab:datasets` menggeser nomor tabel sesudahnya. Rujukan memakai `\ref`, jadi aman, tetapi cek ulang teks yang menyebut nomor tabel secara manual (misalnya di [paper_rewrite.md](paper_rewrite.md) yang menulis "Table IV").
- **Label baru:** `sec:overview`, `sec:distdata`, `sec:teacher`, `sec:student`, `sec:baselines`.
- **Compile:** `pdflatex main && bibtex main && pdflatex main && pdflatex main`, lalu pastikan tidak ada `??`.
- **Gaya:** jalankan daftar cek bagian 8 [ai_text_criteria_to_be_avoided.txt](ai_text_criteria_to_be_avoided.txt) pada paragraf yang ditulis ulang.
