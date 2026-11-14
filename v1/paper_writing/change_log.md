# Change Log: Draf Lama → Naskah Final

Catatan perubahan dari draf lama [_archive/jurnal_latex_v1/main.tex](../_archive/jurnal_latex_v1/main.tex) (28-09-2026) ke naskah final [paper_final/main.tex](../paper_final/main.tex) (17-10-2026), beserta pekerjaan yang belum dilakukan.

Rujukan keputusan (D1–D21) dan status setiap poin kualitas ada di [paper_quality_check_filled.md](paper_quality_check_filled.md).

## Ringkasan

| Aspek | Draf lama | Naskah final |
|---|---|---|
| Lokasi | `_archive/jurnal_latex_v1/` (dibekukan sebagai arsip) | `paper_final/` |
| Bahasa | Indonesia | **Inggris** |
| Struktur file | `main.tex` + 7 file `sections/` + `generated/` | **satu file `main.tex`** |
| Angka | `\val{kunci}` dari notebook | **angka literal**, dicek dengan `scripts/check_paper.py` |
| Format | IEEEtran journal | IEEEtran journal (format lama dipertahankan) |
| Halaman | 15 | 16 |
| Gaya | 41 blok daftar, ±77 label tebal di tengah paragraf | **prosa**, 4 blok daftar (RQ, kontribusi, 2 prosedur) |
| Referensi disitasi | 29 | **46** (17 baru, semua terverifikasi) |
| Tabel | 11 | 13 |
| Gambar | 10 (9 PDF + diagram TikZ) | 10 (sama, label diterjemahkan ke Inggris) |
| Angka hasil penelitian | 1,013 kunci | **nilai lama tidak ada yang berubah**; 128 kunci analisis baru (1,141 total) |

## 1. Perubahan isi naskah

### 1.1 Klaim yang diperbaiki agar sesuai bukti

| Lokasi lama | Draf lama | Naskah final | Alasan |
|---|---|---|---|
| Hasil, perbandingan baseline | "DistilmBERT justru berada di bawah StaticKD" | DistilmBERT "on par with StaticKD", selisih "not significant" | Δ +0.010, p = 0.800 |
| Kontribusi; Pembahasan | "τ ≥ 2 merugikan"; "τ = 2 menurunkan macro-F1 uji" | τ = 2 hanya menurunkan kesepakatan held-out; τ = 4 menurunkan semua metrik | Untuk τ = 2: uji p = 0.059, dev p = 0.705 (tidak signifikan) |
| Kontribusi | "tujuh keluarga model" | "nine configurations from six model families" | Tabel efisiensi berisi 9 konfigurasi dari 6 keluarga |
| Efisiensi | fastText terkuantisasi tidak dibahas | Disebut eksplisit: fastText terkuantisasi sedikit lebih cepat (532 vs 473 dok/s), lebih kecil (18 vs 34 MB), tetapi macro-F1-nya 0.110 lebih rendah | Agar tidak terkesan menyembunyikan pembanding |
| Abstrak; Hasil | StaticKD "lebih akurat daripada fastText dan TF-IDF + SVM" | ~~Keunggulan atas TF-IDF tidak konsisten per bahasa~~ → **dikoreksi (audit §2.5):** abstrak kembali menyebut fastText dan TF-IDF + SVM; Results melaporkan Wilcoxon per bahasa untuk macro-F1 (31/47, p 0.003) dan akurasi (24/47, p 0.127) | Perubahan awal **salah**: memakai akurasi per bahasa, bukan metrik utama |
| Penelitian terkait | "MasakhaNEWS mencakup 16 bahasa Afrika serta en/fr" | "16 languages widely spoken in Africa, English and French included" | Salah fakta; dicek ke sumber asli |
| Pendahuluan | "jutaan artikel berita setiap hari" | Dihapus | Klaim tanpa sumber |
| Pendahuluan; Related Work; Discussion | Inferensi mendominasi "biaya dan energi" [Luccioni] | ~~"running cost"~~ → **dikoreksi (audit §2.5):** "a large share of the computing demand and energy use … 60% … Google" [Luccioni]; di Discussion diganti angka kita sendiri (15.1 vs 0.02 core per sejuta artikel) | Perubahan awal **salah diagnosa**: klaim bersitasi tidak perlu diukur sendiri, dan sumbernya membahas energi |
| Validitas label | Skor pada label non-IPTC disebut "batas bawah akurasi yang sebenarnya" | Skor dibaca sebagai kesesuaian dengan kategorisasi editorial | Konsisten dengan definisi label editorial (D1) |

### 1.2 Isi yang ditambahkan

- **Definisi label editorial (D1):** label rubrik dan kategori didefinisikan sebagai keputusan redaksi penerbit, bukan hasil model, sehingga tidak ada sirkularitas dengan teacher.
- **Tinjauan tabel pemetaan (D2):** kalimat bahwa tabel pemetaan rubrik → IPTC disusun dengan bantuan AI dan seluruh 916 aturannya ditinjau tanpa perubahan. **Dikoreksi (audit §2.5):** "the authors reviewed" → "the first author reviewed all 916 rules (814 mapped names and 102 …)", sesuai catatan tinjauan.
- **Set cek LLM16:** pengakuan bahwa set kecil 320 artikel dalam 16 bahasa berlabel Claude ikut dipakai saat eksplorasi untuk memilih τ = 1 dan ensemble 3 seed, lalu ditinggalkan.
- **Hasil per sumber set uji (tabel baru):** MN-DS (satu-satunya label manusia IPTC asli) dilaporkan terpisah; di sana StaticKD mempertahankan 97.4% skor teacher. Tabel ini juga menunjukkan fastText dan TF-IDF runtuh pada Bangla (0.150 dan 0.010), sedangkan StaticKD 0.748.
- **Batas token tiap model:**
  - teacher 512 token: 60.7% artikel terpotong;
  - MiniLM 256 token: 91.1%;
  - DistilmBERT 256 token: 93.2%;
  - StaticKD 1,024 token: 5.4%.
  - Ditambah catatan bahwa perbandingan kecepatan tidak menguntungkan StaticKD.
- **Uji Wilcoxon antarbahasa:** awalnya hanya pada akurasi: StaticKD vs fastText (41/47 bahasa, p < 0.001), vs TF-IDF (24/47, p = 0.127), vs teacher (7/47, p < 0.001). **Dilengkapi (audit §2.5)** dengan macro-F1 dan DistilmBERT.
- **Spesifikasi dan biaya komputasi:**
  - GPU RTX 4050 Laptop 6 GB;
  - waktu pelabelan teacher ±1.58 jam GPU (50.1 dok/detik, diukur pada 5,000 dokumen);
  - versi NumPy dan transformers;
  - ukuran sampel benchmark (30/48 dan 500/3,000 dokumen).
- **Sparse Distillation:** penjelasan kenapa tidak direproduksi, beserta pemetaannya ke fastText + KD dan ablasi inisialisasi acak. Ablasi embedding beku disebut sebagai baseline Model2Vec siap pakai.
- **Pernyataan jujur tentang baseline:** hiperparameter fastText dan TF-IDF ditetapkan tanpa pencarian.
- **Keterbatasan baru:** budget tuning yang tidak setara, batas 256 token pada transformer, dan benchmark hanya satu sesi.
- **Tabel lisensi aset:** lisensi teacher, potion, setiap dataset, dan rilis; diverifikasi dari kartu dataset dan model.
- **Penekanan kontribusi (temuan review 8):** paragraf temuan analitis di Pendahuluan, urutan kontribusi diubah (set uji → temuan → model StaticKD → rilis), dan abstrak menyebut temuan transfer lintas bahasa.
- **Data penulis:** afiliasi Department of Informatics Engineering ITS, e-mail, dan penulis korespondensi (Obi Kastanya). Ucapan terima kasih untuk Departemen Teknik Informatika ITS; tidak ada pendanaan.
- **Pernyataan penggunaan AI** dipindah ke Acknowledgment (D14). Isinya tidak diubah atas keputusan penulis, karena teks final akan ditulis ulang sendiri.

### 1.3 Format dan gaya

- **Judul bahasa Inggris:** "StaticKD: Distilling a Multilingual IPTC News Topic Classifier into a Static Token-Logit Table for Lightweight CPU Inference".
- **Keywords:** dari 8 menjadi 5, disusun alfabetis.
- **Abstrak:** 239 kata (maks. 250), tanpa referensi atau persamaan.
- **Prosa:** Pendahuluan, Penelitian Terkait, Hasil, dan Pembahasan ditulis ulang sebagai prosa (D9). Label tebal di tengah paragraf dihapus.
- **Gaya teks sesuai [ai_text_criteria_to_be_avoided.txt](ai_text_criteria_to_be_avoided.txt):**
  - 0 kata dari daftar terlarang dan 0 em-dash;
  - 0 kata transisi berulang di awal kalimat;
  - pengumuman "tiga hal" dihapus;
  - titik koma dikurangi dari 42 menjadi 12 dan titik dua dari 60 menjadi 13 (dihitung pada prosa saja, di luar tabel, persamaan, dan math).
- **Tabel I (posisi terhadap karya terkait)** kini dirujuk di teks, dan baris DistilBERT ditambahkan.
- **Persamaan:** (1)–(3) semuanya dirujuk. Persamaan pelipatan dipecah supaya tidak melewati lebar kolom.

### 1.4 Referensi

- **17 referensi baru:**
  - `amharicnews2024`, `barbaresi2021trafilatura`, `broder1997resemblance`, `cloversearch_ccnews`, `commoncrawl2026ccnews`, `dror2018hitchhiker`, `emmediatopic2025`, `guha2016schema`, `guo2017calibration`, `holm1979`, `indonews2021`, `iyyer2015dan`, `mcnemar1947`, `sanh2019distilbert`, `swahilinews2020`, `treviso2023efficient`, `yang2025kdsurvey`;
  - tidak ada referensi lama yang dihapus.
- **Verifikasi 46/46 referensi:** identitas dicek ke Crossref/DataCite, arXiv, ACL Anthology, atau halaman resmi; tidak ada retraksi. Hasilnya di [reference/INDEX.md](../reference/INDEX.md).
- **PDF di [reference/](../reference/):** 37 referensi punya PDF. 3 paper metode klasik tidak tersedia di langganan dan diverifikasi lewat metadata.
- **Catatan bib Model2Vec:** concept DOI, dengan versi 0.9.0 yang dipakai eksperimen.

## 2. Perubahan kode, data, dan alur kerja

### 2.1 Struktur dan alur

| Bagian | Sebelum | Sesudah |
|---|---|---|
| Sumber notebook | `scratch/nb_final/` (di-ignore git, tidak tersimpan) | [src/notebook_build/](../src/notebook_build/) (tersimpan di git) |
| Sumber naskah modular | `_archive/jurnal_latex_v1/sections/` | [src/paper/](../src/paper/) |
| Output angka dan tabel notebook | `_archive/jurnal_latex_v1/generated/` | `results/final/paper_generated/` |
| Output gambar notebook | `_archive/jurnal_latex_v1/figures/` | `results/final/figures/`; hanya 9 gambar yang dipakai yang disalin ke `paper_final/figures/` |
| Pembangun naskah | – | [scripts/build_paper.py](../scripts/build_paper.py): menggabungkan sumber menjadi satu `main.tex` berangka literal; menolak menimpa naskah yang sudah disunting |
| Format angka output | Indonesia (0,545; 12.744) | Inggris (0.545; 12,744) |
| Teks tabel dan gambar | Indonesia | Inggris (nilai internal yang membentuk kunci angka tidak diubah) |
| Notebook | 92 sel | 97 sel (+ sel batas token, + sel hasil per sumber) |

### 2.2 Skrip baru dan yang diubah

| Skrip | Fungsi |
|---|---|
| [scripts/tune_baselines.py](../scripts/tune_baselines.py) (baru) | grid baseline yang ditetapkan sebelum dijalankan (D3), dengan resume; **baru 2 dari 41 konfigurasi** |
| [scripts/train_baselines.py](../scripts/train_baselines.py) | memakai konfigurasi terpilih dari grid bila sudah ada |
| [scripts/label_with_teacher.py](../scripts/label_with_teacher.py) | opsi `--time-sample` untuk mengukur waktu pelabelan tanpa menimpa label |
| [src/statickd/benchmark.py](../src/statickd/benchmark.py), [scripts/run_benchmarks.py](../scripts/run_benchmarks.py) | sampel teacher dan transformer menjadi 100/96 dokumen; id pengulangan `--run` (belum dijalankan) |
| [src/statickd/baselines.py](../src/statickd/baselines.py) | fungsi fit/prediksi fastText dan TF-IDF dipisah; hasilnya terbukti identik |
| [scripts/export_mapping_review.py](../scripts/export_mapping_review.py) (baru) | membuat [mapping_review.xlsx](mapping_review.xlsx) untuk tinjauan penulis |
| [scripts/verify_references.py](../scripts/verify_references.py) (baru) | verifikasi referensi dan pengunduhan PDF open access |
| [scripts/check_style.py](../scripts/check_style.py) (baru) | pemindai pola teks AI pada `main.tex` |
| [scripts/build_paper.py](../scripts/build_paper.py) (baru) | membangun naskah satu file |
| [scripts/check_paper.py](../scripts/check_paper.py) (ditulis ulang) | memastikan naskah mandiri, gambar lengkap, log bersih, dan melaporkan angka yang berubah sejak build |

### 2.3 Data dan hasil baru

- `results/final/teacher_labeling_time.json`: waktu pelabelan teacher.
- `results/final/baseline_grid.jsonl`: 2 konfigurasi grid yang sudah selesai.
- `src/statickd/testset/iptc_reference/mapping_review_record.json`: catatan tinjauan tabel pemetaan (916 aturan diterima, 0 perubahan).
- `src/statickd/testset/iptc_reference/section_names_en.json`: terjemahan bantu baca nama rubrik (hanya untuk tinjauan).
- `results/final/paper_number_map.json`: peta 246 kunci angka di `main.tex`.

**Verifikasi:** setelah semua perubahan kode, notebook dijalankan ulang. Jumlah kunci angka naik dari 1,013 menjadi 1,141 (128 kunci baru). Ke-1,013 kunci lama tetap ada dan nilainya sama. Perbedaannya hanya format:
- desimal koma → titik;
- pemisah selang kepercayaan `;` → `,`;
- "sama" → "unchanged".

### 2.4 Pembaruan 2026-10-17 (keputusan D21: tanpa eksperimen baru sebelum submit)

- **Related Work:** trainer classifier Model2Vec disebut. Trainer ini melakukan fine-tuning embedding dan bobot per token, memakai hidden layer 512 unit, dan dilatih dengan cross-entropy pada label keras (diverifikasi dari kode `model2vec` 0.9.0).
- **Tabel I:** baris Model2Vec diubah dari "static embeddings (general)" menjadi "static embeddings, optional MLP classifier".
- **Methodology (Baselines):** trainer Model2Vec tidak dijalankan. Komponen default-nya diuji satu per satu lewat ablasi label keras dan kepala MLP 512 unit, dan keduanya tidak berbeda signifikan dari resep final di dev maupun uji. Kombinasinya dan bobot per token tidak diuji. Hidden layer juga membuat model tidak bisa dilipat ke satu tabel.
- **Limitations:** satu kalimat bahwa trainer Model2Vec tidak dijalankan sebagai baseline.
- **Results (efisiensi):** "lower by +0.110" diganti dengan "0.435 against 0.545 for StaticKD".
- **Tabel hparams:** "wd 0,01" → "wd 0.01". Diperbaiki di [part3.py](../src/notebook_build/part3.py), sel notebook (1 byte), dan `results/final/paper_generated/tab_hparams.tex`.
- **Pemeriksaan setelah build ulang:**
  - 0 error LaTeX, 16 halaman;
  - 247 kunci angka, 0 yang berubah;
  - scan gaya bersih.

### 2.5 Audit perubahan klaim (2026-10-17)

Setiap perubahan klaim di §1.1–1.2 dicek ulang terhadap teks draf lama, teks naskah final, angka notebook, data mentah, dan PDF sumber. Beberapa perubahan ternyata lahir dari diagnosa Claude yang keliru.

**Benar dan diperlukan (draf lama memang salah):**
- "tujuh keluarga model" → 9 konfigurasi dari 6 keluarga (dicek ke tabel efisiensi lama dan baru);
- MasakhaNEWS: 16 bahasa sudah termasuk en dan fr (16 folder bahasa di data mentah). Docstring [external.py](../src/statickd/testset/external.py) yang ikut salah juga diperbaiki;
- τ = 2 tidak menurunkan macro-F1 uji secara signifikan (p 0.059);
- DistilmBERT tidak "di bawah" StaticKD pada macro-F1 (p 0.800).

**Benar tetapi tidak wajib:** penghapusan "jutaan artikel per hari", "batas bawah" → kesesuaian editorial (D1), pengakuan fastText-q, urutan kontribusi.

**Salah, akibat diagnosa keliru, kini dikoreksi:**

| # | Perubahan awal | Kesalahan | Koreksi |
|---|---|---|---|
| 1 | TF-IDF dihapus dari abstrak; "not consistently across languages" | Wilcoxon per bahasa hanya memakai akurasi, padahal metrik utama paper adalah macro-F1 | Notebook menghitung Wilcoxon per bahasa untuk kedua metrik ([part5.py](../src/notebook_build/part5.py)). Abstrak kembali menyebut fastText dan TF-IDF + SVM. Results melaporkan macro-F1 (31/47) dan akurasi (24/47). |
| 2 | "energi" → "running cost" | Klaim bersitasi tidak perlu diukur sendiri, dan sumbernya membahas energi | Kalimat kembali setia pada sumber (60% energi ML Google). "dominant cost in a news pipeline" diganti dengan angka kita sendiri. |
| 3 | "the authors reviewed all of its rules" (Method) dan "reviewed by the authors" (kontribusi 1, Introduction) | Peninjaunya hanya penulis pertama | Method: "the first author reviewed all 916 rules …", dengan angka dari notebook (`map.review.*`, [part1.py](../src/notebook_build/part1.py)). Kontribusi 1 (Introduction) dan Limitations: "reviewed by the first author" (diperbaiki terpisah pada 2026-10-17, karena awalnya terlewat). Kalimat di Acknowledgment ("all of which the authors reviewed") **sengaja tidak diubah**, karena isi pernyataan AI dikunci penulis (D17/D18). Perlu diselaraskan saat penulis menulis ulang. |
| 4 | DistilmBERT hanya disebut "not significant" | Tidak menyebut akurasi yang menguntungkan StaticKD | Ditambah McNemar p < 0.001 beserta keterbatasannya (tidak memperhitungkan klaster). Per bahasa: macro-F1 p 0.604, akurasi p 0.322. |

**Penilaian Claude kepada penulis yang ditarik** (tidak tertulis di naskah):
- "validitas label = kelemahan paling rawan";
- "keunggulan atas TF-IDF rapuh dan bisa hilang setelah grid" (kutipan dev +0.006 juga menyesatkan, karena dev hanya 4 bahasa);
- "DistilmBERT 512 token mungkin melampaui StaticKD" (spekulasi).

### 2.6 Kepatuhan aturan penulisan IEEE (paper_rules.md), 2026-10-17

Hasil pemindaian `main.tex` terhadap [paper_rules.md](paper_rules.md) dan [ai_text_criteria_to_be_avoided.txt](ai_text_criteria_to_be_avoided.txt). Temuan diverifikasi di kalimat aslinya, dan *false positive* dibuang. Yang diperbaiki:

| # | Aturan | Sebelum | Sesudah |
|---|---|---|---|
| A2 | §7 rentang sitasi | PDF mencetak [12]–[14] dan [18]–[21] | `\usepackage[nocompress]{cite}` → [12], [13], [14] |
| A3 | §3 singkatan | IPTC di abstrak; CPU, GPU, RAM, KD, KL, MLP, LLM, ONNX, NLP, PEFT, LoRA, TF-IDF, SVM, SVC, AI, URL, IT tidak pernah dipanjangkan | Dipanjangkan pada pemakaian pertama. Singkatan yang hanya dipakai sekali (SVC, AI, IT) ditulis lengkap tanpa akronim. RQ2 ditulis ulang tanpa kurung agar definisi TF-IDF/SVM tidak bertumpuk. DOI hanya ada di placeholder `[TODO]`, jadi tidak diubah. |
| A5 | §2 "from … to" | "from 2024--2026" | "from 2024 to 2026" |
| A6 | §4 tanggal | "2024-01-01" | "1 January 2024" |
| A7 | §2 kurung bertumpuk | "(society (0.16), …)" | Dipecah menjadi dua kalimat. Daftar dari notebook kini memakai "and" sebelum unsur terakhir (`join_and` di [part5.py](../src/notebook_build/part5.py)); hanya 3 string daftar yang berubah. |
| A8 | §6 caption | "The StaticKD pipeline." | "StaticKD pipeline." |

Belum diperbaiki (keputusan penulis): A1 pemisah ribuan (koma → tanpa pemisah untuk 4 digit, spasi tipis untuk ≥ 5 digit) dan A4 angka di bawah 11 yang ditulis sebagai digit.

Hasil: 0 error LaTeX, 0 *overfull*, 16 halaman, abstrak 248 kata, scan gaya bersih.

### 2.7 Gaya impersonal tanpa kata ganti orang pertama (D22), 2026-10-17

Keputusan penulis: naskah kembali ke gaya draf lama, yaitu impersonal atau pasif tanpa "we/our". Naskah final sebelumnya memuat 42 "we/our" (±4 per 1,000 kata), sedangkan draf lama hanya 6 "kami" (±0.8 per 1,000 kata).

- **Semua 42 "we/our" dan satu "ours" diganti.** Campuran yang dipakai:
  - subjek "this paper/this study" (usulan, RQ, kontribusi);
  - subjek benda yang aktif ("Its training split … is part of the distillation data", "Internal validation uses 3% …", "The evaluation also reports …");
  - pasif pendek untuk langkah teknis ("Each process is therefore pinned …");
  - frasa impersonal untuk dugaan dan saran ("A plausible explanation is …", "accuracy should be monitored …").
- **Tidak ada informasi yang dibuang.** Abstrak tetap 247 kata.
- **Paragraf yang menjadi pasif beruntun dihaluskan** (Study Design, label editorial, protokol evaluasi), sehingga paling banyak tiga kalimat pasif berturut-turut.
- **Diperbaiki sekalian:** Evaluation Protocol kini menulis Wilcoxon "on per-language macro-F1 and accuracy", sesuai Results setelah audit §2.5.
- **Tidak diubah:** "they/their" (mengacu ke benda) dan Acknowledgment (sudah orang ketiga).

### 2.8 Konsistensi throughput teacher di mode cascade, 2026-10-17

Throughput teacher ONNX int8 satu core tertulis **0.8** di Results (paragraf cascade) dan Tabel XII, tetapi **0.77** di Discussion dan Tabel X. Nilainya sama; hanya presisinya yang berbeda. Tabel cascade di [part5.py](../src/notebook_build/part5.py) kini memakai aturan presisi yang sama dengan tabel efisiensi: 2 desimal untuk nilai < 10, 1 desimal untuk < 100, bilangan bulat di atasnya. Hasilnya:
- "Teacher only" = 0.77 di Results, Discussion, Tabel X, dan Tabel XII;
- throughput cascade di θ = 0.8 menjadi 1.92 (sebelumnya 1.9);
- kolom throughput Tabel XII lainnya menjadi 3.97, 2.93, 2.34, dan 1.58.

Tidak ada nilai lain yang berubah.

### 2.9 Pembuangan LoRA/PEFT (tidak relevan), 2026-10-18

Diverifikasi terhadap naskah. Masalah paper ini adalah biaya **inference** di CPU, sedangkan LoRA/PEFT adalah metode menghemat biaya **training**. LoRA/PEFT tidak dipakai di eksperimen, RQ, maupun hasil mana pun, dan teacher tidak dilatih dengan LoRA. Kalimat-kalimatnya adalah sisa arah penelitian lama: LoRA sudah dibuang dari topik.

Yang dibuang:
- **Pendahuluan:** kalimat "Low-rank adaptation (LoRA) and other parameter-efficient fine-tuning (PEFT) methods … reduce the cost of training, not of inference …".
- **Related Work:** kalimat "PEFT methods such as LoRA … do not belong to this group …".
- **Tabel I:** baris "LoRA/PEFT".
- **Discussion:** kalimat "Compared with LoRA and PEFT …, StaticKD lowers the cost of inference rather than of training." Kalimat berikutnya ("Inference is the recurring cost in a news pipeline …") tetap.

Akibatnya:
- dua referensi tidak lagi disitasi (`hu2022lora`, `razuvayevskaya2024peft`), sehingga total referensi 46 → **44** dan artikel jurnal 11 → **10** (22.7%);
- nomor sitasi setelah [5] bergeser dua.

Lembar rewrite (`paper_rewrite.md`) dan PDF bacaan bahasa Indonesia ikut diperbarui dan divalidasi ulang.

Yang **tidak** dibuang setelah diverifikasi:
- Sparse Distillation: karya terdekat; dasar klaim pembeda dan pemetaan baseline;
- trainer classifier Model2Vec: menjawab risiko novelty;
- baseline LLM: memang tidak pernah ada di naskah.

## 3. Yang belum dilakukan

> **Keputusan D21 (2026-10-17):** tidak ada eksperimen baru sebelum submit karena keterbatasan waktu. Eksperimen di 3.1 dikerjakan **saat revisi**, bila reviewer memintanya. Limitations sudah menyebut setiap batasannya.

### 3.1 Eksperimen (ditunda ke tahap revisi)

| Pekerjaan | Poin | Catatan |
|---|---|---|
| **Grid baseline fastText dan TF-IDF** | M-05 | Baru 2 dari 41 konfigurasi; estimasi ±16 jam dengan 8 thread (atau ±10 jam dengan 16 thread). Lanjutkan dengan `python scripts/tune_baselines.py` (resume otomatis), lalu `scripts/train_baselines.py`. Selisih StaticKD vs fastText/TF-IDF bisa berubah. |
| **Latih ulang MiniLM dan DistilmBERT dengan 512 token** | D19 | Sekarang 256 token (91–93% artikel terpotong); ±4–6 jam GPU untuk 3 run (MiniLM τ=1, τ=2, DistilmBERT), atau ±2–3 jam bila hanya DistilmBERT. Dikerjakan bersama grid baseline. |
| **Baseline trainer classifier Model2Vec** | M-04 | Belum dijalankan; ±4–6 jam (1–2.5 jam GPU). Perlu `pip install model2vec[train]`. |
| **Benchmark CPU 3× dengan sampel lebih besar** | K-01 | Kode siap (`run_benchmarks.py --run 1/2/3`); ±1.5 jam CPU, mesin harus idle. Jalankan setelah baseline dilatih ulang, karena model fastText/TF-IDF ikut berubah. |
| **Throughput mode cascade diukur langsung** | temuan review 5 | Sekarang dihitung dengan rumus dari throughput masing-masing model; belum ada kode benchmark end-to-end. |

Setelah eksperimen di atas selesai:
1. jalankan ulang notebook;
2. jalankan `python scripts/check_paper.py` untuk melihat angka mana yang berubah di `main.tex`;
3. perbarui angka-angka itu, lalu cek ulang klaim yang menyangkut baseline (N-05: fastText, TF-IDF, MiniLM, DistilmBERT) dan bagian Limitations.

### 3.2 Naskah

| Pekerjaan | Poin | Catatan |
|---|---|---|
| **Penulisan ulang oleh penulis** | W-07, E-01 | Naskah ini **belum final**. Pernyataan AI ("The manuscript was written by the authors") hanya akurat bila teks final ditulis ulang oleh penulis. |
| Proofreading bahasa Inggris | W-07 | Misalnya Paperpal Preflight dari IEEE Access. |
| Pindah ke template IEEE Access dan biografi penulis | W-08, D20 | Template wajib saat submit tersimpan di [template_ieeeaccess/](template_ieeeaccess/); biografi dan foto belum ada. |
| URL rilis kode, model, dan DOI | R-01, S-03 | Masih `[TODO]` di bagian Availability. Paket rilis sudah ada di `dist/`, tinggal diunggah (GitHub, Hugging Face, Zenodo). |
| Lisensi dataset Bangla | R-02 | Kartu dataset tidak menyatakan lisensi; perlu dicek sebelum manifest set uji dirilis. |
| Protokol pencarian literatur | L-01 | Opsional. Tidak ditulis karena tidak pernah dilakukan secara terstruktur. |
| Proporsi referensi jurnal | L-04 | 24% (< 30% aturan mata kuliah). Diterima sesuai D6; tambah hanya bila ada referensi jurnal yang relevan. |
| 3 PDF referensi klasik | L-05 | McNemar 1947, Holm 1979, Field & Welsh 2007; opsional bila ada akses perpustakaan. |

### 3.3 Submission

| Pekerjaan | Poin |
|---|---|
| Cek quartile IEEE Access di scimagojr.com | J-01 |
| Cek status Scopus (bukan *discontinued*) | J-02 |
| Checklist Think.Check.Submit | J-03 |
| Cek similarity (Turnitin/iThenticate) pada versi final | E-02 |
| Cover letter | S-02 |

### 3.4 Verifikasi teknis

- **Notebook belum dijalankan penuh sejak jalur output dipindah** ke `results/final/`. File hasil sudah dipindah secara manual, dan jalurnya sudah dicek lewat impor modul. Lakukan satu kali jalankan penuh untuk memastikan semuanya tertulis ke lokasi baru.
- **Kalau naskah disunting di Overleaf**, unduh kembali `main.tex` ke `paper_final/` sebelum menjalankan `scripts/check_paper.py`.
