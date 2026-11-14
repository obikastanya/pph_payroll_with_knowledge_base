# Paper Quality Check (Filled) — Target Jurnal Q1/Q2 (IEEE)

> Versi isian hasil audit naskah. Template kosongnya: [paper_quality_check.md](paper_quality_check.md).

Checklist kualitas naskah paper StaticKD (IPTC news topic classification) sebelum submit ke jurnal Q1/Q2 berformat IEEE (target: IEEE Access).

- **Naskah yang dicek:** [_archive/jurnal_latex_v1/main.tex](../_archive/jurnal_latex_v1/main.tex) dan [_archive/jurnal_latex_v1/sections/](../_archive/jurnal_latex_v1/sections/)
- **Fokus saat ini:** isi naskah paper (Bagian 1–7). Bagian 8 (pemilihan jurnal & submission) dicek nanti.
- **Asal kriteria:** setiap poin punya rujukan. **[MK]** = materi kuliah Metpen ([summary_all_presentation.txt](../materi_kuliah/summary_all_presentation.txt)), **[R]** = sumber resmi/primer, **[S]** = sumber sekunder.

> Catatan: Q1/Q2 adalah peringkat *jurnal* (Q1 = 25% teratas kategori subjeknya, Q2 = 25–50%), bukan peringkat paper. Jadi checklist ini memakai kriteria reviewer jurnal target (IEEE Access, IEEE Transactions) ditambah standar pelaporan riset ML/NLP.

## Info audit

- **Tanggal audit:** 2026-10-17
- **Versi naskah yang diaudit:** [_archive/jurnal_latex_v1/main.tex](../_archive/jurnal_latex_v1/main.tex) (28-09-2026, PDF 15 halaman) beserta `sections/*.tex` dan `generated/*.tex`. Ini draf terbaru, yang semua angkanya diambil dari notebook. [main_draft_v1.tex](../_archive/jurnal_latex_v1/main_draft_v1.tex) (27-09-2026) adalah versi lama yang belum memakai `\val{}`, jadi tidak dipakai sebagai acuan.
- **Pemeriksaan otomatis:** `python scripts/check_paper.py` → 207 kunci angka dipakai, 0 hilang; 9 tabel generated ada; 9 gambar ada; 0 error LaTeX; 0 referensi/sitasi tak terdefinisi.
- **📝 Catatan** = hal yang **sudah dilakukan dalam penelitian** (ada di kode, `results/`, `dist/`, atau `generated/`) tetapi **belum tertulis di paper**.
- **Evaluasi ulang (2026-10-17, putaran 2):**
  - Semua rujukan `file:baris` di dokumen ini dicek otomatis dan menunjuk ke isi yang benar.
  - Klaim paper tentang karya lain dicocokkan dengan sumber aslinya: Sparse Distillation, MasakhaNEWS, L3Cube-IndicNews, MN-DS, potion-multilingual, dan lisensi teacher.
  - Keputusan diskusi dimasukkan:
    - tidak ada anotasi manusia; diganti dengan definisi konstruk label (K-01);
    - aturan 30% referensi jurnal tidak dikejar dengan paksa (L-04);
    - Sparse Distillation dipetakan ke eksperimen yang sudah ada (M-04);
    - tabel pemetaan rubrik ditinjau penulis (M-02).

## Cara pakai

Alur kerja: **isi semua Value dulu → cek Status → baru tulis paper final dari Value**. Value berperan seperti variabel. Paper final menyusun teksnya dari variabel-variabel ini, sehingga setiap bagian paper punya isi yang sudah disepakati dan diperiksa.

Setiap poin punya isian berikut:

| Isian | Isi yang diharapkan |
|---|---|
| **Sumber** | Rujukan asal kriteria (sudah terisi). |
| **Value** | Variabel `ID.nama` = isi final yang akan dipakai di paper: kalimat, angka, daftar, URL, atau keputusan. Contoh: `W-01.title = "..."`, `M-09.efficiency_metrics = 34 MB, 473 docs/s/core, ...`. Untuk value yang panjang, isi dengan sub-list di bawahnya. |
| **Status** | ⏳ belum diisi/dicek · ✅ Value lengkap & memenuhi kriteria · ⚠️ sebagian · ❌ belum ada / tidak memenuhi · ➖ tidak berlaku |
| **Evidence** | Bukti bahwa Value benar: asal angka (`_archive/jurnal_latex_v1/generated/…`, `results/…`, notebook) atau lokasi di draft (`file.tex:baris`). Tanpa evidence, status tidak boleh ✅. |
| **Tindakan** | Pekerjaan yang masih perlu dilakukan kalau statusnya ⚠️ atau ❌ (eksperimen tambahan, tulis ulang, cari referensi, dll.). |

Aturan penulisan Value:
- Nama variabel tidak diubah setelah dipakai, supaya bisa dirujuk dari paper atau dari variabel lain (misalnya `N-05.main_claims` merujuk `M-09.efficiency_metrics`).
- Angka ditulis apa adanya dari sumber di Evidence, tanpa dibulatkan ulang secara manual.
- Value yang belum diputuskan ditulis `TBD` beserta alasannya di Tindakan.

## Ringkasan status

Status di bawah ini adalah hasil audit **naskah final bahasa Inggris** di `paper_final/` (2026-10-17). Setiap poin punya baris "Naskah final" di bagian Evidence.

| Bagian | Jumlah poin | ✅ | ⚠️ | ❌ | ⏳ | ➖ |
|---|---|---|---|---|---|---|
| 1. Masalah, gap & novelty | 6 | 5 | 1 | 0 | 0 | 0 |
| 2. Tinjauan pustaka & referensi | 5 | 3 | 2 | 0 | 0 | 0 |
| 3. Metodologi & eksperimen | 11 | 10 | 1 | 0 | 0 | 0 |
| 4. Reproducibility | 2 | 0 | 2 | 0 | 0 | 0 |
| 5. Penulisan & format IEEE | 8 | 5 | 2 | 0 | 1 | 0 |
| 6. Etika & integritas (isi naskah) | 4 | 2 | 1 | 1 | 0 | 0 |
| 7. Konsistensi internal naskah | 2 | 1 | 1 | 0 | 0 | 0 |
| 8. Jurnal & submission (nanti) | 8 | 2 | 1 | 0 | 4 | 1 |
| **Total** | **46** | **28** | **11** | **1** | **5** | **1** |

*Evaluasi ulang 2026-10-17:* N-05 ✅ → ⚠️ (klaim transfer), R-02 ✅ → ⚠️ (lisensi manifest MasakhaNEWS), W-03 ✅ → ⏳ (IEEE Thesaurus belum dicek). W-02 tetap ✅ setelah singkatan di abstrak diperbaiki.

## Ringkasan temuan

> **Riwayat:** ringkasan di bawah ini berasal dari audit draf lama (`_archive/jurnal_latex_v1/main.tex`). Sebagian besar sudah diperbaiki di naskah final `paper_final/`; status terkini ada di tabel Ringkasan status di atas.

**Sudah kuat (inti ilmiah):** gap, RQ, kontribusi, desain eksperimen, ablasi 5 seed, uji statistik (paired cluster bootstrap, McNemar, Holm, Welch), CI site-cluster bootstrap, efisiensi multi-indikator, limitations, dan keterlacakan angka. Isi ilmiah paper sudah setara standar jurnal; kekurangannya ada di format, referensi, dan kelengkapan administratif.

**❌ Belum memenuhi (wajib diperbaiki sebelum submit):**
1. **W-07** — Naskah masih berbahasa Indonesia. IEEE Access langsung menolak naskah yang grammar Inggrisnya buruk.
2. **W-08** — Naskah masih memakai template IEEEtran (Transactions). IEEE Access **mewajibkan template IEEE Access sendiri**.
3. **W-03** — Ada 8 keywords; IEEE menyarankan 3–5.
4. **E-02** — Cek similarity (Turnitin/iThenticate) belum dilakukan.

**⚠️ Prioritas tinggi:**
- **L-02** — Ada **kesalahan fakta**: [main.tex:111](../_archive/jurnal_latex_v1/main.tex#L111) menulis "MasakhaNEWS mencakup 16 bahasa Afrika serta en/fr", padahal 16 bahasa itu **sudah termasuk** en dan fr (data kita sendiri: 16 kode bahasa, termasuk en dan fr).
- **L-02 / L-04** — Hanya 29 referensi yang disitasi, dan baru 6 (21%) di antaranya artikel jurnal (aturan MK: minimal 30%). Beberapa metode dipakai tanpa sitasi: McNemar, Holm, ECE, DistilBERT, Trafilatura, MinHash, deep averaging network, dataset EMMediaTopic/CC-News. Entri bib-nya sebenarnya **sudah ada** di `references.bib`, hanya belum disitasi.
- **N-05 / K-02** — Ada dua klaim yang lebih kuat dari buktinya:
  - "DistilmBERT di bawah StaticKD", padahal p = 0,800 (tidak signifikan).
  - "τ ≥ 2 merugikan", padahal di set uji p = 0,059 (tidak signifikan).
- **K-01** — Ukuran sampel benchmark tidak dilaporkan dan timpang: transformer hanya diukur dengan 30 dokumen untuk latensi dan 48 untuk throughput, sedangkan model ringan dengan 500/3000. Benchmark juga hanya dijalankan sekali, tanpa variasi antar-run.
- **M-05** — Budget tuning antarmodel timpang (StaticKD 72 run, sedangkan fastText/TF-IDF memakai hiperparameter tetap) dan tidak dilaporkan.
- **R-01 / E-01 / E-04** — Masih ada TODO: URL GitHub dan Hugging Face, AI disclosure yang memenuhi format IEEE, afiliasi, dan email.

---

## 1. Masalah, research gap & novelty

### N-01 — Gap nyata, didukung data awal
- **Kriteria:** Pendahuluan menunjukkan kesenjangan antara kondisi ideal dan kondisi faktual (das sollen vs das sein), didukung data/angka awal. Contoh: biaya inferensi teacher vs kebutuhan pipeline real-time.
- **Sumber:** [MK] [L57](../materi_kuliah/summary_all_presentation.txt#L57), [L205](../materi_kuliah/summary_all_presentation.txt#L205)
- **Value:**
  - `N-01.gap_statement` = Satu-satunya pengklasifikasi IPTC multibahasa terbuka (Kuzman & Ljubešić 2025, XLM-R-large) terlalu mahal untuk pipeline real-time tanpa GPU, dan biaya inferensinya tidak dilaporkan oleh penelitian sebelumnya. Di sisi lain, alternatif yang ada belum memenuhi kebutuhan:
    - LoRA/PEFT hanya menurunkan biaya training.
    - Transformer kecil hanya mempercepat satu orde besaran.
    - fastText tidak punya transfer lintas bahasa.
  - `N-01.gap_evidence_numbers` = teacher 559,9 jt parameter; latensi p50 1 core: PyTorch 2.971 ms, ONNX int8 1.239 ms per artikel; 1 juta artikel/hari butuh 15,1 core (ONNX int8) sampai 34,8 core (PyTorch).
- **Status:** ✅
- **Evidence:** [main.tex:64](../_archive/jurnal_latex_v1/main.tex#L64) (angka latensi teacher + "Biaya inferensi ini tidak dilaporkan"); [main.tex:66-71](../_archive/jurnal_latex_v1/main.tex#L66-L71) (alternatif yang gagal); [results.tex:112](../_archive/jurnal_latex_v1/sections/results.tex#L112) (core per 1 juta artikel). Angka dari `generated/numbers.tex` (`eff.teacher.*`, `eff.teacher_onnx_int8.*`).
  - **Naskah final (2026-10-17):** [introduction.tex](../paper_final/main.tex) paragraf 2: latensi teacher dan biaya inferensi yang tidak dilaporkan; klaim "jutaan artikel" tanpa sumber sudah dihapus.
- **Tindakan:** Opsional: klaim "jutaan artikel setiap hari" di [main.tex:62](../_archive/jurnal_latex_v1/main.tex#L62) belum disitasi. Tambahkan sumber (misalnya statistik volume CC-NEWS), atau lunakkan kalimatnya.

### N-02 — Problem statement lengkap
- **Kriteria:** Problem statement memuat konteks + urgensi + tujuan.
- **Sumber:** [MK] [L63](../materi_kuliah/summary_all_presentation.txt#L63)
- **Value:**
  - `N-02.problem_context` = Industri data analitik memproses jutaan artikel berita per hari dalam puluhan bahasa; artikel perlu dikelompokkan ke taksonomi standar IPTC Media Topic (17 topik level atas) sedini mungkin di pipeline.
  - `N-02.problem_urgency` = Pengklasifikasi IPTC multibahasa yang ada membutuhkan 1,2–3,0 detik per artikel per core CPU, sedangkan inferensi mendominasi biaya dan energi model yang sudah di-deploy [luccioni2024power].
  - `N-02.research_objective` = Pengklasifikasi topik IPTC untuk banyak bahasa yang bekerja dalam hitungan milidetik per artikel di CPU biasa, dengan ukuran dan dependensi minimal, dan akurasinya terhadap label independen sedekat mungkin dengan teacher.
- **Status:** ✅
- **Evidence:** konteks [main.tex:62](../_archive/jurnal_latex_v1/main.tex#L62); urgensi [main.tex:64](../_archive/jurnal_latex_v1/main.tex#L64); tujuan [main.tex:66](../_archive/jurnal_latex_v1/main.tex#L66) dan formulasi formal [main.tex:181](../_archive/jurnal_latex_v1/main.tex#L181).
  - **Naskah final (2026-10-17):** [introduction.tex](../paper_final/main.tex) paragraf 1–3: konteks, urgensi, dan target.
- **Tindakan:** —

### N-03 — Novelty dinyatakan eksplisit terhadap prior work
- **Kriteria:** Ada kalimat novelty yang membandingkan langsung dengan penelitian sebelumnya ("penelitian A, B, C hanya fokus pada X… paper ini menawarkan Y"). Pendahuluan menunjukkan apa yang baru dan mengapa penting. Ada daftar kontribusi yang jelas.
- **Sumber:** [MK] [L105](../materi_kuliah/summary_all_presentation.txt#L105); [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)
- **Value:**
  - `N-03.novelty_statement` = StaticKD: knowledge distillation dari pengklasifikasi IPTC XLM-R-large ke student yang setelah training hanya berupa satu tabel berisi 17 logit per token. Tabel ini diinisialisasi dari static embedding multibahasa yang selaras lintas bahasa, dan kepala linearnya dilipat ke dalam tabel. Dibanding Sparse Distillation (karya terdekat), StaticKD berbeda dalam tiga hal:
    1. tabelnya diinisialisasi dari static embedding multibahasa, bukan dilatih dari nol;
    2. kepala linearnya dilipat sehingga setiap token hanya menyimpan 17 angka;
    3. sasarannya klasifikasi dokumen berita dalam 69 bahasa, termasuk bahasa yang tidak ada di data distilasi.
  - `N-03.contributions` =
    1. Resep StaticKD (34 MB, hanya numpy + tokenizers, 473 artikel/detik/core), beserta tiga sifat student berkapasitas sangat rendah: manfaat datang dari transfer set multibahasa dan inisialisasi yang selaras (bukan dari soft label); fine-tuning embedding menaikkan akurasi in-distribusi tetapi mengurangi transfer; ensemble seed dapat dilipat tanpa biaya.
    2. Set uji IPTC multibahasa: 12.744 artikel, 47 bahasa, label independen dari teacher, aturan pemetaan rubrik ke pohon IPTC yang tervalidasi, deduplikasi lintas sumber, kontrol kontaminasi, dan site-cluster bootstrap.
    3. Analisis empiris: ablasi 5 seed per varian, frontier akurasi–biaya untuk 9 konfigurasi dari 6 keluarga model (CPU saja, dengan pinning), serta analisis per bahasa, per label, dan per asal label.
    4. Rilis kode, notebook, model, dan manifest set uji.
- **Status:** ✅
- **Evidence:** [main.tex:73-79](../_archive/jurnal_latex_v1/main.tex#L73-L79) (usulan + dasar pemikiran); [main.tex:91-102](../_archive/jurnal_latex_v1/main.tex#L91-L102) (kontribusi); [main.tex:114-119](../_archive/jurnal_latex_v1/main.tex#L114-L119) (tiga perbedaan dengan Sparse Distillation); Tabel I [tab_related.tex](../_archive/jurnal_latex_v1/sections/tab_related.tex) (posisi terhadap 6 pendekatan).
  - **Naskah final (2026-10-17):** [introduction.tex](../paper_final/main.tex): usulan, daftar kontribusi; [related.tex](../paper_final/main.tex): tiga perbedaan dengan Sparse Distillation; Tabel I dirujuk.
  - **Pembaruan (2026-10-17, D21):** trainer classifier Model2Vec (`StaticModelForClassification`, model2vec 0.9.0) disebut di Related Work, dan baris Model2Vec di Tabel I menjadi "static embeddings, optional MLP classifier". 📝 Risiko sisa: novelty StaticKD sebagai *metode* tipis (pelipatan kepala adalah aljabar linear). Novelty utama ada pada set uji dan temuan analitis, sesuai urutan kontribusi.
- **Tindakan:** —

### N-04 — Kontribusi berbeda dari publikasi sebelumnya & sahih secara teknis
- **Kriteria:** Kontribusi jelas berbeda dari prior work dan didukung data yang cukup. IEEE Access tidak menuntut novelty tinggi, tetapi jurnal setingkat IEEE Transactions menolak paper yang "insufficient novelty" (metode atau pendekatan baru).
- **Sumber:** [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/); [R] [IEEE SPS – Guidelines for Reviewers](https://signalprocessingsociety.org/publications-resources/guidelines-reviewers)
- **Value:**
  - `N-04.closest_prior_work` = Sparse Distillation [ye2022sparse] (NAACL 2022, RoBERTa → DAN + tabel n-gram, hanya bahasa Inggris, satu kalimat); Kuzman & Ljubešić [kuzman2025llm] (IEEE Access 2025, sumber teacher); Model2Vec/potion [tulkens2024model2vec] (static embedding umum, bukan student KD).
  - `N-04.difference_from_prior_work` = Ada tiga perbedaan metode dengan Sparse Distillation (lihat `N-03.novelty_statement`), ditambah empat hal:
    - set uji IPTC multibahasa baru dengan label independen dari teacher;
    - pengukuran biaya CPU pengklasifikasi IPTC, yang belum pernah dilaporkan;
    - temuan empiris tentang soft label dan τ pada capacity gap ekstrem;
    - temuan representation drift pada fine-tuning sebagian kosakata.
- **Status:** ✅
- **Evidence:** [main.tex:114-123](../_archive/jurnal_latex_v1/main.tex#L114-L123); Tabel I [tab_related.tex:12-18](../_archive/jurnal_latex_v1/sections/tab_related.tex#L12-L18); ablasi 72 run (`generated/tab_ablation.tex`, `runs.total = 72`).
  - **Naskah final (2026-10-17):** Sama seperti sebelumnya; risiko novelty untuk jurnal setingkat Transactions tetap dicatat (lihat Tindakan).
- **Tindakan:** Risiko untuk jurnal Q1 yang lebih ketat (IEEE Transactions): metodenya bisa dinilai **inkremental**, karena menggabungkan komponen yang sudah ada (KD + Model2Vec + pelipatan kepala linear). Bila menargetkan Transactions, tonjolkan kontribusi set uji dan temuan analitis (soft label tidak berguna pada capacity gap ekstrem; transfer dibawa oleh baris embedding yang tidak pernah dilatih) sebagai kontribusi utama, bukan hanya "model cepat".

### N-05 — Klaim sesuai bukti, tidak dilebih-lebihkan
- **Kriteria:** Klaim di abstrak dan pendahuluan sesuai dengan kontribusi dan scope yang benar-benar dibuktikan. Kesimpulan tidak membesar-besarkan temuan.
- **Sumber:** [R] [NeurIPS Paper Checklist (1a)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist); [R] [IEEE Author Center](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/) ("Be careful not to inflate your findings")
- **Value:**
  - `N-05.main_claims` = (klaim → bukti → status)
    1. 473 artikel/detik/core, 616× lebih cepat dari teacher ONNX int8, 34 MB → `tab_eff` → ✅
    2. Mempertahankan 91,1% macro-F1 teacher (0,545 vs 0,598) → `tab_main` → ✅
    3. Lebih akurat daripada fastText + KD dan TF-IDF + SVM → Δ +0,110 [+0,042; +0,151] p < 0,001; Δ +0,059 [+0,009; +0,093] p = 0,030 → ✅
    4. "DistilmBERT justru berada di bawah StaticKD" ([results.tex:17](../_archive/jurnal_latex_v1/sections/results.tex#L17)) → Δ +0,010 [−0,026; +0,041], **p = 0,800** → ⚠️ tidak signifikan; seharusnya ditulis "setara"
    5. "label keras setara, dan τ ≥ 2 merugikan" ([main.tex:95](../_archive/jurnal_latex_v1/main.tex#L95)) dan "τ = 2 menurunkan kesepakatan held-out dan macro-F1 uji" ([discussion.tex:14](../_archive/jurnal_latex_v1/sections/discussion.tex#L14)) → label keras p = 0,433 ✅. Untuk τ = 2: held-out −0,007 (p < 0,001) tetapi uji −0,005 (**p = 0,059**) dan dev p = 0,705 → ⚠️. Lebih tepat: "τ = 2 menurunkan kesepakatan held-out; τ = 4 menurunkan semua metrik"
    6. Ensemble dilipat tanpa biaya inferensi → benar secara matematis (Persamaan 3), tetapi kenaikannya kecil (uji 0,542 → 0,544 untuk K = 3) dan tidak diuji signifikansinya → ✅, asal tidak dijual sebagai peningkatan akurasi
    7. Cascade θ = 0,8 menyamai teacher → akurasi 0,703 vs 0,699 → ✅
    8. Fakta yang belum diakui di teks: fastText + KD terkuantisasi lebih cepat (532 vs 473 artikel/detik), lebih kecil (18 vs 34 MB), dan RAM-nya lebih rendah (300 vs 501 MB) daripada StaticKD → ⚠️ perlu disebut eksplisit; keunggulan StaticKD ada di akurasi (+0,110)
    9. "frontier akurasi–biaya dari tujuh keluarga model" ([main.tex:100](../_archive/jurnal_latex_v1/main.tex#L100)) → Tabel eff dan Gbr. tradeoff berisi 9 konfigurasi dari 6 keluarga (teacher, DistilmBERT, MiniLM, StaticKD, fastText, TF-IDF + SVM). Angka "tujuh" hanya benar jika teacher PyTorch dan ONNX int8 dihitung terpisah → ⚠️ ambigu; sebutkan jumlah konfigurasi secara eksplisit
    10. ~~Keunggulan atas TF-IDF + SVM tidak konsisten per bahasa: lebih baik di 24/47 bahasa, Wilcoxon p = 0,127 … klaim di abstrak harus dibatasi.~~ **Dikoreksi (audit 2026-10-17):** diagnosa ini salah karena hanya memakai **akurasi** per bahasa, padahal metrik utama paper adalah macro-F1. Per bahasa dengan macro-F1, StaticKD lebih baik di 31/47 bahasa (Wilcoxon p 0.003). Dengan akurasi: 24 lebih baik, 1 seri, 22 lebih buruk (p 0.127). Pada set gabungan +0.059 [+0.009, +0.093], p 0.030; akurasi +0.074, McNemar p < 0.001. → ✅ Klaim "lebih akurat daripada fastText dan TF-IDF + SVM" didukung; kedua metrik per bahasa dilaporkan.
    11. **Audit 2026-10-17, DistilmBERT:** "on par" benar untuk macro-F1 (gabungan p 0.800, per bahasa p 0.604). Akurasi menguntungkan StaticKD (1,372 vs 1,143, McNemar p < 0.001), tetapi McNemar tidak memperhitungkan klaster situs, dan per bahasa p 0.322. → ✅ keduanya ditulis.
    12. **Audit 2026-10-17, energi:** sumber (Luccioni dkk. 2024) membahas energi dan kebutuhan komputasi (Google: 60% energi ML untuk inferensi; AWS: 80–90% kebutuhan komputasi ML di cloud; Meta: ±sepertiga jejak karbon). Versi sebelumnya ("most of the running cost") menyimpang dari sumber → diganti "a large share of the computing demand and energy use … 60% … Google". Klaim "dominant cost in a news pipeline" (sudah ada sejak draf lama) diganti dengan angka kita sendiri (15.1 vs 0.02 core per sejuta artikel).
    13. **Evaluasi ulang 2026-10-17, klaim transfer → ⚠️ belum diperbaiki.**
        - **Klaim di naskah:** abstrak, Introduction, Discussion, dan Conclusion menyatakan transfer ke bahasa yang tidak ada di data distilasi "is carried by embedding rows that training never updates".
        - **Yang diukur** ([part5.py](../src/notebook_build/part5.py), Results "fewer than half of the token occurrences belong to tokens seen at least 10 times"): hanya 4 bahasa (bn, ml, or, pa), dengan cakupan token yang muncul ≥ 10 kali paling banyak 32%. StaticKD 0.624, varian compact 0.013.
        - **Selisihnya:**
          - definisi yang diukur adalah "jarang muncul" (< 10 kali), bukan "tidak pernah di-update";
          - bahasa Afrika berhuruf Latin yang tidak ada di data distilasi berbagi subword dengan bahasa lain, jadi baris embedding-nya ikut ter-update;
          - bukti langsung hanya untuk 4 bahasa beraksara unik.
        - **Tindakan:** persempit kalimat di empat lokasi itu, menunggu keputusan penulis.
- **Status:** ⚠️ (diturunkan 2026-10-17 karena butir 13)
- **Evidence:** `generated/numbers.tex`: `sig.test.distilmbert_kd.p = 0,800`, `abl.tau2.test_macro.p = 0,059`, `abl.tau2.dev_macro.p = 0,705`, `abl.hard.test_macro.p = 0,433`, `ens.k1.test_macro = 0,542`, `ens.k3.test_macro = 0,544`, `eff.ft_kd_subword_q.docs_per_sec_1c = 532`, `eff.ft_kd_subword_q.size = 18`, `eff.ft_kd_subword_q.ram = 300`.
  - **Naskah final (2026-10-17):** Semua klaim diperbaiki di naskah final: DistilmBERT "on par / not significant" ([results.tex](../paper_final/main.tex)); τ = 2 hanya menurunkan held-out, τ = 4 menurunkan semua metrik ([discussion.tex](../paper_final/main.tex), kontribusi 1); "nine configurations from six model families"; fastText terkuantisasi lebih cepat dan kecil diakui. **Koreksi audit 2026-10-17:** kalimat "keunggulan atas TF-IDF tidak konsisten per bahasa" dan penghapusan TF-IDF dari abstrak adalah akibat diagnosa keliru (butir 10). Keduanya diperbaiki: abstrak kembali menyebut fastText dan TF-IDF + SVM, dan Results melaporkan Wilcoxon per bahasa untuk macro-F1 dan akurasi.
- **Tindakan:**
  - Ubah klaim DistilmBERT di [results.tex:17](../_archive/jurnal_latex_v1/sections/results.tex#L17) menjadi "setara (tidak berbeda signifikan)".
  - Ubah klaim τ di [main.tex:95](../_archive/jurnal_latex_v1/main.tex#L95) dan [discussion.tex:14](../_archive/jurnal_latex_v1/sections/discussion.tex#L14) sesuai butir 5. Kalimat di [conclusion.tex:5](../_archive/jurnal_latex_v1/sections/conclusion.tex#L5) ("soft label dan temperature tinggi tidak memberi manfaat") sudah sesuai bukti, jadi tidak perlu diubah.
  - Perjelas "tujuh keluarga model" di [main.tex:100](../_archive/jurnal_latex_v1/main.tex#L100) (butir 9).
  - Tambahkan satu kalimat di Subbagian Efisiensi bahwa fastText terkuantisasi sedikit lebih cepat dan kecil, tetapi macro-F1-nya 0,110 lebih rendah.

### N-06 — Research question / tujuan terhubung ke hasil
- **Kriteria:** Masalah (why), teori (what), dan metode (how) saling terhubung. Setiap pertanyaan penelitian atau tujuan dijawab di bagian hasil atau diskusi.
- **Sumber:** [MK] [L60](../materi_kuliah/summary_all_presentation.txt#L60), [L202](../materi_kuliah/summary_all_presentation.txt#L202)
- **Value:**
  - `N-06.research_questions` =
    - RQ1 (biaya CPU) → Subbagian IV-D Efisiensi CPU + Pembahasan paragraf 1
    - RQ2 (akurasi vs baseline) → Subbagian IV-A + uji berpasangan (Tabel sig)
    - RQ3 (komponen distilasi) → Subbagian IV-C Ablasi + Pembahasan "Dari mana pengetahuan student berasal"
    - RQ4 (generalisasi bahasa/label/sumber) → Subbagian IV-E + Pembahasan "Batas generalisasi lintas bahasa"
- **Status:** ✅
- **Evidence:** RQ di [main.tex:83-89](../_archive/jurnal_latex_v1/main.tex#L83-L89); judul subbagian berlabel RQ di [results.tex:1](../_archive/jurnal_latex_v1/sections/results.tex#L1), [:69](../_archive/jurnal_latex_v1/sections/results.tex#L69), [:107](../_archive/jurnal_latex_v1/sections/results.tex#L107), [:138](../_archive/jurnal_latex_v1/sections/results.tex#L138); pembahasan berlabel RQ di [discussion.tex:1](../_archive/jurnal_latex_v1/sections/discussion.tex#L1), [:8](../_archive/jurnal_latex_v1/sections/discussion.tex#L8), [:18](../_archive/jurnal_latex_v1/sections/discussion.tex#L18).
  - **Naskah final (2026-10-17):** RQ1–RQ4 dijawab di subbagian Results berlabel RQ dan di Discussion.
- **Tindakan:** —

---

## 2. Tinjauan pustaka & referensi

### L-01 — Literature review kritis → SotA → gap
- **Kriteria:** Related work dianalisis secara kritis (bukan sekadar daftar), memetakan state of the art, lalu menurunkan gap dan novelty. Lebih baik kalau pencarian literaturnya sistematis (database, kata kunci/Boolean, kriteria seleksi).
- **Sumber:** [MK] [L84–L99](../materi_kuliah/summary_all_presentation.txt#L84-L99)
- **Value:**
  - `L-01.related_work_groups` = Lima kelompok, masing-masing diakhiri gap:
    1. Klasifikasi topik berita multibahasa & IPTC → gap: belum ada pengklasifikasi IPTC murah yang dievaluasi pada berita nyata di banyak bahasa.
    2. Distilasi ke student ringkas → gap: hampir semua student berbentuk transformer; Sparse Distillation hanya untuk bahasa Inggris.
    3. Temperature & capacity gap → gap: perilaku τ/soft label pada kesenjangan ekstrem belum dikarakterisasi.
    4. Static embedding & inferensi CPU → gap: static embedding belum dipakai sebagai student KD untuk taksonomi tertentu; latensi CPU jarang dilaporkan.
    5. Set uji silver, kontaminasi, ketergantungan sampel → gap: `articleSection` belum pernah dipetakan ke taksonomi standar; uji yang ada mengasumsikan sampel independen.
    - Ditutup Tabel I (posisi StaticKD terhadap 6 pendekatan, 6 kriteria).
  - `L-01.search_protocol` = TBD — tidak ada protokol pencarian yang terdokumentasi (database, kata kunci, rentang tahun, kriteria inklusi).
- **Status:** ⚠️
- **Evidence:** [main.tex:107-131](../_archive/jurnal_latex_v1/main.tex#L107-L131); [tab_related.tex](../_archive/jurnal_latex_v1/sections/tab_related.tex). Tidak ada dokumen protokol pencarian di `docs/` ([RANCANGAN_PENELITIAN.md](../docs/RANCANGAN_PENELITIAN.md) dan [CHECKLIST_JURNAL.md](../docs/CHECKLIST_JURNAL.md) tidak memuatnya).
  - **Naskah final (2026-10-17):** Analisis kritis lima kelompok + Tabel I ada. Protokol pencarian literatur tidak ditulis karena tidak pernah dilakukan secara terstruktur (opsional; tidak dikarang).
- **Tindakan:**
  - Analisis kritis sudah baik. Yang kurang adalah jumlah referensi (lihat L-04) dan protokol pencarian.
  - Opsional untuk paper riset (bukan SLR): tulis satu kalimat protokol, misalnya "literatur dicari di Scopus/ACL Anthology/IEEE Xplore 2020–2026 dengan kata kunci …".
  - 📝 Catatan: memori proyek menyebut keputusan "peer-reviewed literature 2022–2026", tetapi keputusan ini tidak tertulis di paper.

### L-02 — Setiap sitasi dijelaskan kaitannya
- **Kriteria:** Setiap referensi dijelaskan hubungannya dengan paper. Referensi cukup dan relevan, dan tidak ada yang tidak sesuai topik.
- **Sumber:** [R] [IEEE SPS Reviewer Guidelines](https://signalprocessingsociety.org/publications-resources/guidelines-reviewers) ("lists of references without explanation are unacceptable"); [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/)
- **Value:**
  - `L-02.citation_map` = 29 referensi disitasi, semuanya dengan penjelasan peran (tidak ada sitasi berbentuk daftar tanpa penjelasan). **Metode/aset berikut dipakai tetapi tidak disitasi** (entri bib yang sudah ada ditulis dalam kurung):
    - uji McNemar (`mcnemar1947`)
    - koreksi Holm–Bonferroni (`holm1979`)
    - ECE / kalibrasi (`guo2017calibration`)
    - DistilmBERT (`sanh2019distilbert`)
    - Trafilatura (`barbaresi2021trafilatura`)
    - MinHash (`broder1997resemblance`)
    - dataset EMMediaTopic (`emmediatopic2025`)
    - korpus CC-News multibahasa (`cloversearch_ccnews`)
    - CC-NEWS Common Crawl (`commoncrawl2026ccnews`)
    - schema.org (`guha2016schema`)
    - IndoNews / Swahili / Amharic (`indonews2021`, `swahilinews2020`, `amharicnews2024`; saat ini hanya footnote URL)
    - panduan uji signifikansi NLP (`dror2018hitchhiker`)
    - deep averaging network di [main.tex:114](../_archive/jurnal_latex_v1/main.tex#L114) (`iyyer2015dan`)
    - fastText lid.176, uji Welch, Kruskal–Wallis, Spearman, ONNX Runtime — belum ada entri bib
  - `L-02.citation_accuracy` = Klaim tentang karya lain yang sudah dicocokkan dengan sumber aslinya (2026-10-17):
    - Sparse Distillation (RoBERTa-large, 6 tugas klasifikasi satu kalimat, speedup hingga 600×) ✅
    - L3Cube-IndicNews (10 bahasa India di versi ICON) ✅
    - MN-DS (IPTC level 1 dan 2, 17 kategori level atas, dianotasi manual) ✅
    - potion-multilingual (101 bahasa, didistilasi dari BGE-M3, dim 256) ✅
    - **MasakhaNEWS ❌**: [main.tex:111](../_archive/jurnal_latex_v1/main.tex#L111) menulis "16 bahasa Afrika serta en/fr", padahal abstrak MasakhaNEWS menyebut "16 languages widely spoken in Africa", yang sudah termasuk en dan fr. Benar: "16 bahasa yang banyak dipakai di Afrika (termasuk en dan fr)".
- **Status:** ✅
- **Evidence:** analisis `main.aux` vs `references.bib`: 98 entri bib, 29 disitasi, 69 tidak disitasi. Penggunaan metode tanpa sitasi: McNemar & Holm [main.tex:350-351](../_archive/jurnal_latex_v1/main.tex#L350-L351); ECE [main.tex:358](../_archive/jurnal_latex_v1/main.tex#L358); DistilmBERT [main.tex:331](../_archive/jurnal_latex_v1/main.tex#L331); Trafilatura [main.tex:204](../_archive/jurnal_latex_v1/main.tex#L204); EMMediaTopic [main.tex:184](../_archive/jurnal_latex_v1/main.tex#L184).
  - **Naskah final (2026-10-17):** Semua metode/dataset/tool disitasi (McNemar, Holm, ECE, DistilBERT, Trafilatura, MinHash, DAN, schema.org, EMMediaTopic, CC-News, Common Crawl, IndoNews, Amharik, Swahili, Dror dkk.); kalimat MasakhaNEWS diperbaiki ([related.tex](../paper_final/main.tex)).
- **Tindakan:**
  - Tambahkan sitasi untuk setiap metode, dataset, dan tool di atas. Sebagian besar hanya perlu `\cite{}` karena entri bib sudah ada.
  - Perbaiki kalimat MasakhaNEWS di [main.tex:111](../_archive/jurnal_latex_v1/main.tex#L111).
  - 📝 Catatan: entri-entri ini sudah dikumpulkan saat penelitian (ada di `references.bib`), tetapi belum dipakai di naskah.
- **Sumber verifikasi:** [Sparse Distillation (arXiv 2110.08536)](https://arxiv.org/abs/2110.08536), [MasakhaNEWS (arXiv 2304.09972)](https://arxiv.org/abs/2304.09972), [L3Cube-IndicNews](https://arxiv.org/html/2401.02254v2), [MN-DS (Data, MDPI)](https://www2.mdpi.com/2306-5729/8/5/74), [potion-multilingual-128M](https://huggingface.co/minishlab/potion-multilingual-128M).

### L-03 — Tidak ada citation padding / self-citation tidak relevan
- **Kriteria:** Hanya mengutip sumber yang benar-benar berkontribusi pada paper.
- **Sumber:** [R] [IEEE – Ethical Requirements](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/ethical-requirements/); [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)
- **Value:**
  - `L-03.irrelevant_refs_removed` = Tidak ada referensi yang tidak relevan; tidak ada self-citation (penulis belum punya publikasi terkait).
- **Status:** ✅
- **Evidence:** daftar 29 referensi yang disitasi (lihat L-04); setiap referensi dipakai untuk klaim spesifik di teks.
  - **Naskah final (2026-10-17):** 46 referensi, semuanya dipakai untuk klaim spesifik; tidak ada self-citation.
- **Tindakan:** Saat menambah referensi (L-02, L-04), pastikan setiap referensi baru benar-benar dipakai di teks, bukan untuk menambah jumlah saja.

### L-04 — Referensi terbaru & bereputasi
- **Kriteria:** Mayoritas referensi dari 3–5 tahun terakhir, dan minimal 30% dari jurnal bereputasi (Scopus Q1–Q4 / Sinta 1–2). Evidence: jumlah referensi per tahun dan per jenis venue dari `references.bib`.
- **Sumber:** [MK] [L72](../materi_kuliah/summary_all_presentation.txt#L72), [L208](../materi_kuliah/summary_all_presentation.txt#L208)
- **Value:**
  - `L-04.ref_stats` =
    - **Total disitasi:** 29.
    - **Tahun:** 2022–2026 = 22 (76%); 2023–2026 = 17 (59%); sebelum 2022 = 7 (Koehn 2004, Field 2007, Hinton 2015, Joulin 2017, Conneau 2020, Wang 2021, Stanton 2021; semuanya karya fondasi).
    - **Jenis:** artikel jurnal = **6 (21%)**: IEEE Access, Data, PLOS ONE ×2, J. Roy. Statist. Soc. B, Knowledge-Based Systems. Prosiding = 20 (69%): ACL, EMNLP, NAACL, EACL, ICLR, NeurIPS, CVPR, AAAI, FAccT, IJCNLP-AACL, ICON, workshop. Lainnya = 3 (software Zenodo, situs IPTC, Hinton arXiv/workshop).
- **Status:** ⚠️
- **Evidence:** analisis `main.aux` + `references.bib` (tahun dan field journal/booktitle).
  - **Naskah final (2026-10-17):** 46 referensi; artikel jurnal 11 (24%) < 30% (aturan MK). Penyimpangan diterima sesuai keputusan D6 (tidak menambah referensi demi kuota). 2022–2026: 26 dari 45 referensi bertahun (58%); referensi lama adalah karya fondasi metode dan statistik.
  - **Pembaruan 2026-10-18:** LoRA/PEFT dibuang karena tidak relevan ([change_log.md](change_log.md) §2.9). Sekarang 44 referensi, artikel jurnal 10 (22.7%). Kesegaran: 2022–2026 24 dari 43 referensi bertahun (56%); 2021–2026 29/43 (67%). Untuk Juknis akreditasi F.7, sumber primer (jurnal + prosiding) 34/44 = 77.3%.
- **Tindakan (diperbarui 2026-10-17):**
  - **Sudah dikerjakan:** kandidat jurnal yang relevan (`treviso2023efficient`, `yang2025kdsurvey`, McNemar, Holm) sudah disitasi. Total referensi naik dari 29 menjadi 46.
  - **Yang tersisa:** proporsi jurnal 24% masih di bawah aturan MK (30%). Kesegaran 58% (2022–2026) dari 45 referensi bertahun.
  - **Keputusan D6:** diterima. Aturan 30% berasal dari MK, bukan syarat IEEE Access, dan di ML/NLP venue utamanya konferensi bereputasi (ACL, EMNLP, NeurIPS). Tidak menambah referensi demi kuota, karena melanggar L-03.
  - Tidak ada tindakan lagi, kecuali menemukan referensi jurnal yang memang relevan saat penulisan ulang.

### L-05 — Tidak ada referensi yang sudah di-retract
- **Kriteria:** Tidak ada referensi yang sudah di-retract. IEEE Access mengembalikan naskah yang mengutip paper retracted.
- **Sumber:** [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/); [R] [IEEE Access – Preparing Your Article](https://ieeeaccess.ieee.org/authors/preparing-your-article/) (peringatan: konten AI bisa memuat referensi fiktif; artikel dengan konten fabrikasi langsung ditolak)
- **Value:**
  - `L-05.retracted_refs` = Selesai untuk identitas dan status retraksi (2026-10-17, `scripts/verify_references.py`):
    - **47/47 referensi terverifikasi**: 29 yang sudah disitasi + 18 yang direncanakan (L-02, L-04). Judul, tahun, dan venue cocok dengan Crossref/DataCite, arXiv, ACL Anthology, atau halaman resmi; 11 di antaranya dicek manual (web/perangkat lunak, JSTOR).
    - **Tidak ada retraksi.** Satu correction notice: `hossain2025banglanews` (PLOS ONE e0332710, 2025-09-17) hanya mengganti Gbr. 3–16 dan pernyataan pendanaan, jadi isi yang kita kutip tidak terdampak.
    - Catatan bib: `tulkens2024model2vec` memakai concept DOI Zenodo (semua versi; versi terbaru v0.10.0); eksperimen memakai model2vec 0.9.0, jadi sebutkan versi itu di catatan sitasi.
    - **PDF di `reference/`:** 37 referensi punya PDF (4 di antaranya diunduh penulis), dan 7 sitasi web/perangkat lunak tidak butuh PDF. 3 paper metode klasik (McNemar 1947, Holm 1979, Field & Welsh 2007) tidak tersedia di langganan penulis. Ketiganya hanya dikutip sebagai asal prosedur standar; identitasnya diverifikasi dari metadata, dan abstrak Field & Welsh sesuai dengan pemakaiannya (lihat [reference/INDEX.md](../reference/INDEX.md)).
- **Status:** ✅
- **Evidence:** [reference/INDEX.md](../reference/INDEX.md), [reference/verification.json](../reference/verification.json), [scripts/verify_references.py](../scripts/verify_references.py).
  - **Naskah final (2026-10-17):** 46/46 referensi yang disitasi terverifikasi ([reference/INDEX.md](../reference/INDEX.md)); tidak ada retraksi.
- **Tindakan:**
  - ~~Penulis menyimpan 7 PDF~~: selesai sejauh akses memungkinkan (4 diunduh, 3 tidak tersedia di langganan dan cukup diverifikasi lewat metadata).
  - Saat menulis paper final: setiap kalimat yang mengutip karya lain dicocokkan dengan PDF-nya. Kasus MasakhaNEWS (L-02) menunjukkan bahwa salah kutip memang terjadi.

---

## 3. Metodologi & eksperimen (ML/NLP)

### M-01 — Metode transparan & bisa direplikasi
- **Kriteria:** Metode dijelaskan cukup detail agar orang lain bisa mereplikasinya.
- **Sumber:** [MK] [L211](../materi_kuliah/summary_all_presentation.txt#L211); [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/) (analisis "described in sufficient detail")
- **Value:**
  - `M-01.method_summary` = Tujuh tahap: (1) korpus distilasi, (2) pelabelan teacher, (3) training StaticKD dan baseline pada data yang sama, (4) set uji independen, (5) evaluasi + uji statistik, (6) benchmark CPU, (7) analisis subkelompok. Resep ditetapkan dari set dev **sebelum** set uji dibangun; tidak ada hiperparameter yang dipilih dari set uji.
- **Status:** ✅
- **Evidence:** [main.tex:137-148](../_archive/jurnal_latex_v1/main.tex#L137-L148) (kerangka + pemisahan dev/uji); seluruh Bagian III [main.tex:134-386](../_archive/jurnal_latex_v1/main.tex#L134-L386) (data, set uji, teacher, student, loss, optimasi, baseline, protokol, versi pustaka).
  - **Naskah final (2026-10-17):** [method.tex](../paper_final/main.tex) seluruhnya.
- **Tindakan:** —

### M-02 — Data: pemilihan, sumber, preprocessing
- **Kriteria:** Menjelaskan bagaimana dan mengapa data dipilih, serta bagaimana data dipreprocess, difilter, dan dikategorikan.
- **Sumber:** [R] [ACM SIGSOFT Empirical Standards – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience)
- **Value:**
  - `M-02.data_sources` =
    - **Distilasi:** EMMediaTopic train (20.000 artikel, 4 bahasa) + CC-News multibahasa 2019–2021. Totalnya 285.999 dokumen, 69 bahasa, 2.960 situs, median 269 kata.
    - **Dev:** EMMediaTopic dev (1.000 artikel).
    - **Fidelity held-out:** 12.554 dokumen, 63 bahasa, 217 situs yang tidak pernah muncul di data distilasi.
    - **Set uji gabungan:** 12.744 artikel, 47 bahasa, 17 label, 1.227 situs/sumber. Asal label: anotasi manusia 32,1%, kategori penerbit 20,4%, rubrik JSON-LD 47,5%.
  - `M-02.preprocessing_steps` =
    - Filter LID: metadata harus cocok dengan fastText.
    - Panjang ≥ 75 kata, dipotong ke 512 kata.
    - Batas per situs: 150 / 400.
    - Split held-out per domain.
    - Pemetaan rubrik → IPTC: 814 nama → 79 node; 62 nama ambigu tidak dipetakan.
    - Filter tanggal, paywall, LID, dan panjang.
    - Dedup URL, teks identik, dan MinHash (Jaccard ≥ 0,7) lintas sumber.
    - Kontaminasi 8-gram ≥ 30% (membuang 50 artikel).
    - Sampling maksimal 50 per sel bahasa × label.
  - `M-02.mapping_review` = Selesai (2026-10-17). Tabel pemetaan 814 nama rubrik → 79 node IPTC ([iptc_map.py](../src/statickd/testset/iptc_map.py)) dibuat dengan bantuan AI, divalidasi otomatis terhadap pohon IPTC, lalu **ditinjau oleh penulis**:
    - 48 nama diterima otomatis, karena sama persis dengan node/label IPTC atau hanya bentuk jamak bahasa Inggrisnya.
    - 766 nama lainnya dan 102 aturan lain (nama ambigu, aturan khusus per bahasa, penolakan astrologi) diterima oleh penulis.
    - 0 perubahan.
    - Semua 11.989 artikel set uji non-MN-DS berlabel melalui nama-nama di tabel ini.
    - Kalimat untuk paper: "Tabel pemetaan dibuat dengan bantuan AI, divalidasi otomatis terhadap pohon IPTC resmi, dan seluruh 916 aturannya ditinjau oleh penulis."
- **Status:** ✅
- **Evidence:** [main.tex:183-245](../_archive/jurnal_latex_v1/main.tex#L183-L245); Tabel testset (`generated/tab_testset.tex`); Gbr. heatmap set uji; angka dari `generated/numbers.tex` (`data.*`, `ts.*`, `map.*`).
  - **Naskah final (2026-10-17):** [method.tex](../paper_final/main.tex): data distilasi, set uji, definisi label editorial, dan tinjauan tabel pemetaan oleh penulis.
- **Tindakan:**
  - ~~Penulis meninjau tabel pemetaan~~: selesai. Bukti: [mapping_review.xlsx](mapping_review.xlsx) (semua baris berstatus "ya") dan [mapping_review_record.json](../src/statickd/testset/iptc_reference/mapping_review_record.json).
  - Yang tersisa: tulis kalimat `M-02.mapping_review` di Subbagian Pemetaan ke IPTC pada paper final (Tahap 5). Kalau kebenaran label ada pada penerbit, langkah translasi inilah satu-satunya titik di mana kesalahan bisa masuk (lihat K-01).

### M-03 — Setup eksperimen & pendekatan model
- **Kriteria:** Setup eksperimen disajikan (misalnya dalam diagram alur) dan pendekatan model didefinisikan (misalnya dengan pseudocode atau persamaan).
- **Sumber:** [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience)
- **Value:**
  - `M-03.pipeline_figure` = Gbr. 1 (TikZ, figure*): CC-News + EMMediaTopic → teacher XLM-R-large → logit teacher → student (tokenizer, embedding potion, rata-rata, linear) → lipat W → tabel |V|×17 (fp16) → evaluasi pada set uji independen.
  - `M-03.model_definition` = Persamaan (1) student: h = rata-rata embedding, z = W·drop(h) + b. Persamaan (2) loss: τ²·KL(p^T ‖ p^S), τ = 1. Persamaan (3) pelipatan: T = E·Wᵀ. Ensemble: T̄ = rata-rata tabel K seed.
- **Status:** ✅
- **Evidence:** [main.tex:150-178](../_archive/jurnal_latex_v1/main.tex#L150-L178) (Gbr. pipeline); [main.tex:273-306](../_archive/jurnal_latex_v1/main.tex#L273-L306) (persamaan 1–3, ensemble, varian compact).
  - **Naskah final (2026-10-17):** Gbr. 1 (fig_pipeline dari TikZ terpisah), Persamaan (1)–(3), semuanya dirujuk di teks.
- **Tindakan:** Opsional: Persamaan (1) dan (2) tidak pernah dirujuk di teks (`eq:student`, `eq:kd` = 0 rujukan). Ini tidak wajib, tetapi lebih rapi bila dirujuk.

### M-04 — Baseline state-of-the-art yang kuat
- **Kriteria:** Dibandingkan dengan baseline SotA beserta keterbatasannya, atau ada justifikasi kuat kalau perbandingan tidak memungkinkan.
- **Sumber:** [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience)
- **Value:**
  - `M-04.baselines` = Semua baseline dilatih pada data distilasi yang sama, dengan target teacher yang sama:
    - teacher XLM-R-large (PyTorch fp32 dan ONNX int8)
    - MiniLM-L6 + KD
    - DistilmBERT + KD
    - fastText + KD (kata / subword / terkuantisasi)
    - TF-IDF + SVM + KD (baseline non-neural Kuzman & Ljubešić)
    - fastText berlabel GPT-4o (setara data yang tersedia bagi Kuzman & Ljubešić)
    - Ablasi "embedding beku" berfungsi sebagai baseline potion off-the-shelf + kepala linear.
- **Status:** ✅
- **Evidence:** [main.tex:324-333](../_archive/jurnal_latex_v1/main.tex#L324-L333); hasil di `generated/tab_main.tex`.
  - `M-04.sparse_distillation_mapping` = (keputusan: dipetakan, tidak diimplementasikan) Ide inti Sparse Distillation diwakili oleh dua eksperimen yang sudah ada:
    - **fastText + KD**: bag of n-gram + rata-rata + linear, dilatih dari label teacher pada transfer set yang sama;
    - **ablasi inisialisasi acak**: tabel embedding dilatih dari nol.
    - Perbedaan yang tersisa: DAN dengan hidden layer, target berupa logit soft, tabel n-gram berukuran miliaran parameter, dan cakupan hanya bahasa Inggris.
  - **Naskah final (2026-10-17):** Pemetaan Sparse Distillation ke fastText + KD dan ablasi inisialisasi acak, serta ablasi embedding beku sebagai baseline Model2Vec ([method.tex](../paper_final/main.tex), subbagian Baselines).
  - **Pembaruan (2026-10-17, D21):** trainer classifier Model2Vec **tidak dijalankan**. Naskah menjelaskan bahwa konfigurasi default-nya (label keras, hidden layer 512 unit, bobot per token) diuji per komponen lewat ablasi: label keras (dev p 1.000, uji p 0.433) dan kepala MLP 512 (dev p 1.000, uji p 0.281), keduanya tidak berbeda signifikan dari resep final. Kombinasinya dan bobot per token tidak diuji; hal ini ditulis di Limitations. 📝 Risiko sisa: reviewer bisa meminta trainer ini sebagai baseline (±4–6 jam), dan itu dikerjakan saat revisi.
- **Tindakan:**
  - Tulis pemetaan `M-04.sparse_distillation_mapping` di Subbagian Baseline, sebagai jawaban atas pertanyaan "mengapa karya terdekat tidak direproduksi".
  - Sebutkan eksplisit bahwa ablasi embedding beku = baseline "potion/Model2Vec off-the-shelf + kepala linear yang didistilasi".

### M-05 — Detail training & pemilihan hyperparameter
- **Kriteria:** Data split, hyperparameter, dan cara memilih hyperparameter dilaporkan. Budget tuning tiap metode juga dilaporkan agar perbandingan adil.
- **Sumber:** [R] [NeurIPS Checklist (3b)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist); [R] [Dodge et al., EMNLP 2019 – Show Your Work](https://aclanthology.org/D19-1224/)
- **Value:**
  - `M-05.data_split` =
    - Distilasi 285.999 dokumen, dengan 3% (8.579) sebagai validasi internal untuk memilih epoch.
    - Dev = EMMediaTopic dev (1.000).
    - Held-out domain-disjoint (12.554).
    - Set uji gabungan (12.744), dibangun setelah resep ditetapkan.
  - `M-05.hyperparameters` =
    - **StaticKD:** potion-multilingual-128M (500.353 × 256), maks. 1.024 token, dropout 0,1, KL τ = 1, token dropout 0,2, SparseAdam 1e-3 / AdamW 3e-3 (wd 1e-4), batch 64, 6 epoch, ensemble 3 seed.
    - **fastText:** dim 100, lr 0,5, 15 epoch (25 untuk label GPT-4o), 2-gram kata, 2 jt bucket.
    - **TF-IDF + SVM:** subword XLM-R uni+bigram, min df 3, maks. 1 jt fitur, LinearSVC C = 0,5.
    - **MiniLM / DistilmBERT:** AdamW 5e-5, wd 0,01, warmup 6%, batch 32, 2 epoch, maks. 256 token, τ ∈ {1, 2} dipilih pada dev.
  - `M-05.tuning_budget` = TBD. Fakta yang ada:
    - StaticKD: 72 run (ablasi + eksplorasi), resep dipilih pada dev.
    - Transformer: 2 nilai τ.
    - fastText dan TF-IDF + SVM: hiperparameter tetap, tanpa pencarian yang dilaporkan.
- **Status:** ⚠️
- **Evidence:** Tabel hparams `generated/tab_hparams.tex` ([main.tex:308-322](../_archive/jurnal_latex_v1/main.tex#L308-L322)); [main.tex:288-295](../_archive/jurnal_latex_v1/main.tex#L288-L295); `runs.total = 72`.
  - **Naskah final (2026-10-17):** Grid baseline dilewati atas permintaan penulis (poin baseline). Naskah menyatakan jujur bahwa hiperparameter fastText dan TF-IDF ditetapkan tanpa pencarian ([method.tex](../paper_final/main.tex), [limitations.tex](../paper_final/main.tex)).
- **Tindakan (diperbarui 2026-10-17):**
  - **Sudah dikerjakan:** Tabel hparams menandai fastText dan TF-IDF sebagai "fixed". Methodology menyatakan hiperparameternya ditetapkan sekali tanpa pencarian, dan Limitations menyebut budget tuning yang tidak setara (72 run StaticKD).
  - **Keputusan D21:** grid baseline (D3, baru 2 dari 41 konfigurasi) **ditunda ke tahap revisi**. Dua titik grid yang sudah jalan (token kata, lr 0.1) memberi dev macro-F1 0.358 dan 0.639, di bawah konfigurasi yang dipakai (0.743). Ini belum membuktikan konfigurasi sekarang optimal.
  - 📝 Risiko sisa: reviewer bisa meminta pencarian hiperparameter baseline. Jawabannya di tahap revisi: jalankan `scripts/tune_baselines.py` (resume otomatis). **Koreksi audit 2026-10-17:** sebelumnya keunggulan atas TF-IDF disebut "rapuh dan bisa hilang setelah grid", dan itu berlebihan. Keunggulannya signifikan pada set gabungan (p 0.030, cluster bootstrap + Holm) dan konsisten per bahasa pada macro-F1 (31/47, p 0.003). Untuk TF-IDF, grid hanya mengubah C. Dampak grid belum diketahui, bukan "kemungkinan besar menghapus".
  - **Belum ditulis:** asal nilai hiperparameter baseline (default library atau pilihan sendiri). Bisa ditambahkan satu frasa saat penulisan ulang, bila asalnya diketahui.

### M-06 — Variasi hasil (multi-seed, error bar / CI)
- **Kriteria:** Hasil tidak hanya satu angka. Sertakan error bar atau confidence interval (misalnya dari beberapa seed atau bootstrap), dan sebutkan cara menghitungnya.
- **Sumber:** [R] [NeurIPS Checklist (3c)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist); [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience) ("goes beyond single-dimensional summaries of performance")
- **Value:**
  - `M-06.n_seeds` = 5 seed per varian ablasi; 10 seed untuk resep final. Satu student tanpa ensemble: uji 0,542 ± 0,004, dev 0,755 ± 0,010.
  - `M-06.ci_method` = CI 95% dengan bootstrap percentile 1.000×. Pada set uji, yang di-resample adalah situs (site-cluster bootstrap); pada dev, dokumen. Contoh: StaticKD uji 0,545 [0,490–0,605].
- **Status:** ✅
- **Evidence:** [main.tex:345](../_archive/jurnal_latex_v1/main.tex#L345), [main.tex:354](../_archive/jurnal_latex_v1/main.tex#L354); [results.tex:12](../_archive/jurnal_latex_v1/sections/results.tex#L12); CI di setiap baris `generated/tab_main.tex`; SD per varian di `generated/tab_ablation.tex`; Gbr. temperature (titik per seed) dan ensemble (± SD).
  - **Naskah final (2026-10-17):** CI site-cluster bootstrap, 5/10 seed, SD di tabel ablasi.
- **Tindakan:** —

### M-07 — Uji signifikansi statistik yang tepat
- **Kriteria:** Perbedaan antar model diuji secara statistik dengan uji yang sesuai (Wilcoxon untuk dua model, Friedman + post-hoc untuk lebih dari dua model, atau uji yang cocok dengan metrik NLP).
- **Sumber:** [R] [Demšar, JMLR 2006](https://www.jmlr.org/papers/v7/demsar06a.html); [R] [Dror et al., ACL 2018](https://aclanthology.org/P18-1128/)
- **Value:**
  - `M-07.stat_test` =
    - Antarmodel pada dokumen yang sama: paired (cluster) bootstrap 2.000× untuk Δmacro-F1 dan McNemar eksak untuk akurasi, dengan koreksi Holm–Bonferroni per set.
    - Antarvarian: uji Welch pada tingkat seed, dengan koreksi Holm.
    - Analisis faktor: Spearman dan Kruskal–Wallis.
    - Validitas label: Wilcoxon.
  - `M-07.stat_results` = StaticKD vs:
    - teacher: −0,053 [−0,065; −0,033], p < 0,001
    - MiniLM: −0,021 [−0,038; −0,008], p = 0,004
    - DistilmBERT: +0,010 [−0,026; +0,041], p = 0,800
    - fastText + KD (q): +0,110, p < 0,001
    - TF-IDF + SVM: +0,059, p = 0,030
- **Status:** ✅
- **Evidence:** [main.tex:347-354](../_archive/jurnal_latex_v1/main.tex#L347-L354); [results.tex:22-30](../_archive/jurnal_latex_v1/sections/results.tex#L22-L30); Tabel sig `generated/tab_sig.tex`.
  - **Naskah final (2026-10-17):** Paired cluster bootstrap, McNemar, Holm, Welch, Wilcoxon antarbahasa (baru), Spearman, Kruskal–Wallis; semua disitasi bila perlu.
- **Tindakan:**
  - ~~Uji Wilcoxon signed-rank antarbahasa~~: sudah ditambahkan ke notebook (2026-10-17; kunci `lang.wilcoxon.*`, `lang.static_better.*`). Hasil (akurasi per bahasa, 47 bahasa):
    - StaticKD vs fastText + KD (q): lebih baik di 41/47 bahasa, p < 0,001.
    - StaticKD vs teacher: lebih baik di 7/47 bahasa, p < 0,001 (teacher lebih baik).
    - **StaticKD vs TF-IDF + SVM: lebih baik di 24/47 bahasa, p = 0,127 (tidak signifikan per bahasa)**, padahal pada set uji gabungan Δ +0,059, p = 0,030. Ini harus ditulis eksplisit (lihat N-05 butir 10).
  - Sitasi untuk McNemar, Holm, Welch, Wilcoxon, dan Kruskal–Wallis masih kurang (lihat L-02).

### M-08 — Ablation & sumber peningkatan
- **Kriteria:** Jelaskan dari mana peningkatan berasal melalui ablation, error analysis, dan uji robustness.
- **Sumber:** [R] [Lipton & Steinhardt – Troubling Trends in ML Scholarship](https://arxiv.org/abs/1807.03341)
- **Value:**
  - `M-08.ablations` =
    - **Ablasi satu faktor** (5 seed, Δ macro-F1 uji):
      - EMM saja: −0,051 (p < 0,001)
      - inisialisasi acak: −0,120 (p < 0,001)
      - embedding beku: +0,014 di uji (p < 0,001), tetapi −0,035 di dev
      - label keras: +0,005 (p = 0,433)
      - 130 ribu dokumen: −0,002
      - tanpa token dropout: +0,001
      - kepala MLP: +0,009 (p = 0,281)
      - τ = 0,5 / 2 / 4: +0,004 / −0,005 / −0,014
      - 4 varian eksplorasi: semuanya tidak memperbaiki
    - **Ablasi per tier data distilasi:** Tabel ablation-groups.
    - **Ukuran ensemble:** K = 1–10.
    - **Error analysis:** per bahasa, per label, confusion matrix, cakupan token, varian compact sebagai bukti mekanisme transfer.
    - **Robustness:** uji sensitivitas maksimal 5 artikel per situs (8.139 artikel, peringkat model sama); kalibrasi ECE.
- **Status:** ✅
- **Evidence:** [main.tex:373-386](../_archive/jurnal_latex_v1/main.tex#L373-L386); [results.tex:69-105](../_archive/jurnal_latex_v1/sections/results.tex#L69-L105), [:138-168](../_archive/jurnal_latex_v1/sections/results.tex#L138-L168), [:39](../_archive/jurnal_latex_v1/sections/results.tex#L39); `generated/tab_ablation.tex`, `tab_ablation_groups.tex`.
  - **Naskah final (2026-10-17):** Ablasi, analisis per bahasa/label, uji sensitivitas lima artikel per situs.
- **Tindakan:** —

### M-09 — Klaim efisiensi dengan beberapa indikator biaya + hardware
- **Kriteria:** Klaim "lightweight" atau "cepat" didukung lebih dari satu indikator biaya (jumlah parameter atau ukuran model, FLOPs, throughput/latency, memori). Hardware dan compute yang dipakai disebutkan.
- **Sumber:** [R] [Dehghani et al., ICLR 2022 – The Efficiency Misnomer](https://arxiv.org/abs/2110.12894); [R] [NeurIPS Checklist (3d)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist)
- **Value:**
  - `M-09.efficiency_metrics` = StaticKD:
    - latensi p50/p95 (1 core): 2,03 / 3,46 ms
    - throughput: 473 artikel/detik (1 core), 893 (4 core)
    - RAM model: 501 MB
    - ukuran file: 34 MB (tabel 16 MB)
    - parameter: 8,5 jt
    - dependensi: numpy + tokenizers
    - 1 juta artikel/hari: 0,02 core
    - profiling: tokenisasi = 98% waktu; pooling saja 28.755 artikel/detik
    - Pembanding: teacher ONNX int8 1.239 ms, 0,77 artikel/detik, 1.383 MB RAM, 537 MB file. Speedup 616× (ONNX int8) dan 1.420× (PyTorch).
  - `M-09.hardware` =
    - **Benchmark:** Intel Core Ultra 7 155H (6 P-core, 8 E-core, 2 LP E-core), RAM 31 GB, Windows 11, CPU saja, dipin ke P-core.
    - **Training:** RTX 4050, 5,2 menit per run StaticKD.
    - **Software:** Python 3.12, PyTorch 2.6, tokenizers 0.23, ONNX Runtime 1.30, scikit-learn 1.9, fastText 0.9.2.
- **Status:** ✅
- **Evidence:** Tabel eff `generated/tab_eff.tex`; [results.tex:107-136](../_archive/jurnal_latex_v1/sections/results.tex#L107-L136); [main.tex:360-371](../_archive/jurnal_latex_v1/main.tex#L360-L371), [main.tex:386](../_archive/jurnal_latex_v1/main.tex#L386); `results/final/environment.json`.
  - **Naskah final (2026-10-17):** Latensi p50/p95, throughput 1c/4c, RAM, ukuran, profiling; GPU RTX 4050 Laptop 6 GB, waktu pelabelan teacher, versi pustaka (NumPy, transformers) ditambahkan.
- **Tindakan:**
  - FLOPs tidak dilaporkan. Ini tidak wajib, karena sudah ada 5 indikator lain.
  - ~~Waktu pelabelan teacher~~: sudah diukur (2026-10-17, `label_with_teacher.py --time-sample 5000`): 50,1 dokumen/detik di RTX 4050 fp16, jadi ±1,58 jam GPU untuk 285.999 dokumen; argmax 100% sama dengan label tersimpan. Kunci `teacher.label_*`.
  - Lihat juga N-05 butir 8 (fastText terkuantisasi lebih cepat).

### M-10 — Metrik evaluasi dijustifikasi
- **Kriteria:** Metrik evaluasi (misalnya macro-F1, agreement dengan teacher) dijelaskan dan dijustifikasi.
- **Sumber:** [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience)
- **Value:**
  - `M-10.metrics` =
    - **Macro-F1** atas label yang hadir di referensi (metrik utama, karena label tidak seimbang; sama dengan kode evaluasi Kuzman & Ljubešić).
    - **Akurasi.**
    - **Macro-F1 per bahasa yang dirata-rata antarbahasa**, supaya bahasa besar tidak mendominasi.
    - **Kesepakatan dengan teacher** pada set fidelity.
    - **ECE** (15 bin) untuk kalibrasi.
- **Status:** ✅
- **Evidence:** [main.tex:337-343](../_archive/jurnal_latex_v1/main.tex#L337-L343), [main.tex:358](../_archive/jurnal_latex_v1/main.tex#L358).
  - **Naskah final (2026-10-17):** [method.tex](../paper_final/main.tex), subbagian Evaluation Protocol; macro-F1 dibaca sebagai kesesuaian dengan kategorisasi editorial.
- **Tindakan:** —

### M-11 — Limitations & threats to validity
- **Kriteria:** Ada pembahasan limitations dan threats to validity (validitas internal/eksternal, reliabilitas).
- **Sumber:** [R] [NeurIPS Checklist (1d)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist); [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience); [MK] [L160](../materi_kuliah/summary_all_presentation.txt#L160)
- **Value:**
  - `M-11.limitations` = Delapan butir:
    1. (ditulis ulang sesuai keputusan K-01) konvensi rubrik berbeda antarpenerbit, dan satu rubrik mewakili satu sudut pandang editorial atas artikel yang bisa multi-topik; skor pada label editorial mengukur kesesuaian dengan kategorisasi penerbit (saat ini di draf: "label silver tidak dianotasi ulang")
    2. MasakhaNEWS memakai skema sendiri; test set manusia Kuzman tidak publik
    3. cakupan label per bahasa timpang (median 7 label)
    4. keragaman penerbit terbatas (27 bahasa praktis satu penerbit)
    5. batas atas student adalah teacher
    6. benchmark hanya di satu perangkat
    7. keadilan antarbahasa dan dampaknya
    8. hanya IPTC level atas, single-label
  - `M-11.threats_to_validity` =
    - **Konstruk:** validitas label silver diperiksa tidak langsung (Subbagian IV-B).
    - **Internal:** resep dipilih di dev sebelum set uji dibangun; kontaminasi dan dedup dikontrol.
    - **Eksternal:** satu perangkat; publisher terbatas.
    - **Statistik:** site-cluster bootstrap.
- **Status:** ✅
- **Evidence:** [limitations.tex:1-10](../_archive/jurnal_latex_v1/sections/limitations.tex#L1-L10); [results.tex:50-67](../_archive/jurnal_latex_v1/sections/results.tex#L50-L67); [main.tex:148](../_archive/jurnal_latex_v1/main.tex#L148).
  - **Naskah final (2026-10-17):** [limitations.tex](../paper_final/main.tex): butir label editorial ditulis ulang; tuning baseline dan benchmark satu sesi ditambahkan.
- **Tindakan:**
  - Tulis ulang butir 1 di [limitations.tex:2](../_archive/jurnal_latex_v1/sections/limitations.tex#L2) sesuai Value.
  - Opsional: kelompokkan butir keterbatasan menurut jenis ancaman validitas (konstruk / internal / eksternal) supaya reviewer mudah membacanya.

---

## 4. Reproducibility (yang tertulis di naskah)

### R-01 — Ketersediaan kode, data & model
- **Kriteria:** Naskah menyebutkan di mana kode, data, model, dan instruksi reproduksi tersedia (URL atau DOI). IEEE Access memberi badge "Code Available" untuk repositori ber-DOI (misalnya Code Ocean).
- **Sumber:** [R] [IEEE Access – Reproducibility](https://ieeeaccess.ieee.org/authors/reproducibility/); [R] [NeurIPS Checklist (3a)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist)
- **Value:**
  - `R-01.code_url` = TBD (GitHub)
  - `R-01.model_url` = TBD (Hugging Face: `statickd-iptc-multilingual` dan `statickd-iptc-multilingual-compact`)
  - `R-01.data_url` = TBD. Isinya manifest set uji (URL/ID, label, asal label, SHA-1 teks) + skrip rekonstruksi; EMMediaTopic di CLARIN.SI (hdl 11356/1991).
- **Status:** ⚠️
- **Evidence:** Bagian "Ketersediaan Kode, Model, dan Data" sudah ada di [main.tex:409-410](../_archive/jurnal_latex_v1/main.tex#L409-L410), tetapi URL masih `\todo`.
  - **Naskah final (2026-10-17):** Bagian Code, Model, and Data Availability ada ([availability.tex](../paper_final/main.tex)); URL GitHub/Zenodo dan Hugging Face masih TODO (menunggu unggahan).
- **Tindakan:**
  - **Keputusan (2026-10-17): rilis sebelum submit.** Penulis mengunggah memakai akunnya (GitHub, Hugging Face, Zenodo DOI); Claude menyiapkan panduan langkah demi langkah. Setelah itu isi URL-nya.
  - Pertimbangkan Zenodo DOI (rilis GitHub) atau Code Ocean, agar memenuhi syarat badge IEEE Access.
  - 📝 Catatan: paket rilis **sudah dibangun** oleh `scripts/build_dist.py`:
    - `dist/github/`: README, LICENSE, CITATION.cff, src, scripts, notebooks, results, manifest data.
    - `dist/huggingface/statickd-iptc-multilingual{,-compact}/`.
    - Paket ini hanya belum diunggah, sehingga URL-nya belum ada di paper.
  - ⚠️ **Temuan 2026-10-17: paket `dist/` usang.** Paket dibangun 2026-09-28, sebelum perubahan Oktober:
    - judul di `CITATION.cff` dan `README.md` ("…at language-identification cost") berbeda dari judul paper;
    - skrip baru belum ada (`build_paper.py`, `check_style.py`, `tune_baselines.py`, `export_mapping_review.py`, `verify_references.py`), begitu juga `src/paper/`, `src/notebook_build/`, dan catatan tinjauan pemetaan;
    - notebook di dalamnya versi 28-09.

    **Bangun ulang dengan `scripts/build_dist.py` sebelum diunggah**, setelah memastikan skrip itu menyertakan file-file baru, lalu samakan judul dengan paper.

### R-02 — Lisensi aset yang dipakai
- **Kriteria:** Lisensi dataset dan model pihak ketiga (misalnya CC-News, model teacher, potion embeddings) disebutkan.
- **Sumber:** [R] [NeurIPS Checklist (4b)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist)
- **Value:**
  - `R-02.asset_licenses` =
    - **Di paper saat ini:** hanya MasakhaNEWS (CC BY-NC) dan hak cipta penerbit.
    - **Di `dist/` (belum di paper):** kode MIT; model StaticKD CC BY-SA 4.0 (diturunkan dari teacher); embedding potion MIT; manifest set uji CC BY-SA 4.0.
    - **Diverifikasi di sumber (2026-10-17):** teacher `classla/multilingual-IPTC-news-topic-classifier` = CC-BY-SA-4.0 ([model card](https://huggingface.co/classla/multilingual-IPTC-news-topic-classifier)); potion-multilingual-128M = MIT ([model card](https://huggingface.co/minishlab/potion-multilingual-128M)).
    - **Belum ada di mana pun:** lisensi CC-News/Common Crawl (terms of use), EMMediaTopic, MN-DS, L3Cube, Bangla, IndoNews, Amharic, Swahili.
    - **Evaluasi ulang 2026-10-17 (dicek langsung ke Hugging Face API):**
      - Bangla (`kawsarahmd/bangla-news-category-plos-one`): **tidak ada field lisensi**. Tabel di paper ("not stated on the dataset card") sudah benar.
      - MasakhaNEWS: mirror yang dipakai (`mteb/masakhanews`) = **CC BY-NC 4.0**, sedangkan dataset aslinya (`masakhane/masakhanews`) = **AFL-3.0**. Paper menulis CC BY-NC 4.0.
      - **Potensi bentrok:** manifest set uji direncanakan rilis dengan **CC BY-SA 4.0** dan memuat ID serta label MasakhaNEWS. Kalau lisensi NC yang berlaku, keduanya tidak kompatibel. Perlu keputusan penulis sebelum rilis (bukan nasihat hukum). Opsi: (a) bagian MasakhaNEWS dirilis terpisah dengan CC BY-NC 4.0; (b) untuk MasakhaNEWS hanya ID + skrip rekonstruksi; (c) ikuti lisensi repositori asli setelah dicek.
- **Status:** ⚠️ (diturunkan 2026-10-17: lisensi semua aset sudah disebut, tetapi lisensi manifest untuk bagian MasakhaNEWS belum diputuskan)
- **Evidence:** [main.tex:410](../_archive/jurnal_latex_v1/main.tex#L410); [dist/github/README.md](../dist/github/README.md) bagian "Licence"; [dist/huggingface/statickd-iptc-multilingual/README.md](../dist/huggingface/statickd-iptc-multilingual/README.md) (`license: cc-by-sa-4.0`).
  - **Naskah final (2026-10-17):** Tabel lisensi aset (dipakai dan dirilis) di bagian Availability; lisensi diverifikasi di kartu dataset/model.
- **Tindakan:** Tambahkan ke bagian Ketersediaan Data, misalnya sebagai tabel kecil, lisensi teacher, potion, setiap dataset sumber, dan lisensi rilis. 📝 Catatan: sebagian sudah ditulis di README `dist/`.

---

## 5. Penulisan & format IEEE

### W-01 — Judul
- **Kriteria:** Judul spesifik, ringkas, dan deskriptif, tanpa kata "new"/"novel" dan tanpa simbol matematika.
- **Sumber:** [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)
- **Value:**
  - `W-01.title` = "StaticKD: Knowledge Distillation Pengklasifikasi Topik Berita IPTC Multibahasa ke Tabel Logit Token Statis untuk Inferensi Ringan di CPU" (18 kata)
- **Status:** ✅
- **Evidence:** [main.tex:41](../_archive/jurnal_latex_v1/main.tex#L41). Tidak memuat "new"/"novel" atau simbol matematika; spesifik (metode, tugas, bentuk model, target perangkat).
  - **Naskah final (2026-10-17):** Judul bahasa Inggris, 17 kata, tanpa "new/novel".
- **Tindakan:** Terjemahkan saat naskah dialihkan ke bahasa Inggris (W-07). Usahakan tetap ≤ 15–18 kata, misalnya "StaticKD: Distilling a Multilingual IPTC News Topic Classifier into a Static Token-Logit Table for Lightweight CPU Inference".

### W-02 — Abstrak
- **Kriteria:** Satu paragraf, maksimal 250 kata, berdiri sendiri, tanpa singkatan, referensi, footnote, atau persamaan.
- **Sumber:** [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)
- **Value:**
  - `W-02.abstract` = (isi saat ini di [abstract.tex](../_archive/jurnal_latex_v1/sections/abstract.tex)) Masalah (biaya CPU teacher 1.239–2.971 ms) → usulan StaticKD (tabel 17 logit/token) → data (285.999 artikel, 69 bahasa) → set uji (12.744 artikel, 47 bahasa, label independen) → hasil (macro-F1 0,545 vs 0,598 = 91,1%; 473 artikel/detik/core; 616× ONNX int8; 34 MB) → lebih akurat dari fastText dan TF-IDF + SVM → temuan ablasi → kelemahan.
  - `W-02.abstract_word_count` = ±212 kata (angka dihitung sebagai satu kata).
- **Status:** ✅
- **Evidence:** [abstract.tex:1](../_archive/jurnal_latex_v1/sections/abstract.tex#L1): satu paragraf, tanpa referensi atau persamaan, 212 kata ≤ 250.
  - **Naskah final (2026-10-17):** Satu paragraf, 240 kata (≤ 250), tanpa referensi atau persamaan; singkatan dikurangi.
  - **Evaluasi ulang 2026-10-17:** perbaikan klaim TF-IDF sempat memasukkan lagi singkatan "TF-IDF + SVM" ke abstrak. Frasa itu sudah diganti dengan "a linear support vector machine distilled on the same data" (maknanya sama: baseline TF-IDF + SVM). Abstrak sekarang 244 kata. Singkatan yang tersisa hanya nama diri: IPTC (nama taksonomi), XLM-RoBERTa (nama model), dan macro-F1 (nama metrik). Status tetap ✅.
- **Tindakan:**
  - Abstrak memakai banyak singkatan (IPTC, CPU, XLM-RoBERTa, ONNX, TF-IDF, SVM, MB), padahal IEEE menyarankan menghindari singkatan. Kurangi atau tulis kepanjangannya bila memungkinkan; nama teknis seperti XLM-RoBERTa boleh tetap.
  - Setelah diterjemahkan, cek ulang jumlah kata dan aturan abstrak di template IEEE Access.

### W-03 — Keywords
- **Kriteria:** 3–5 keywords, sebaiknya istilah baku dari IEEE Thesaurus.
- **Sumber:** [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)
- **Value:**
  - `W-03.keywords` = saat ini 8: klasifikasi topik berita, IPTC Media Topic, knowledge distillation, static embedding, klasifikasi teks multibahasa, bahasa sumber daya rendah, efisiensi inferensi, CPU.
- **Status:** ⏳ (diubah dari ✅ pada 2026-10-17: jumlah keywords sudah sesuai, tetapi kecocokannya dengan IEEE Thesaurus belum pernah dicek)
- **Evidence:** [main.tex:56-58](../_archive/jurnal_latex_v1/main.tex#L56-L58).
  - **Naskah final (2026-10-17):** Lima keywords, alfabetis sesuai template IEEE Access: *Efficient inference, knowledge distillation, multilingual text classification, news topic classification, static embeddings*. Belum dicocokkan dengan IEEE Thesaurus.
- **Tindakan:** Pangkas ke 5 dan cocokkan dengan IEEE Thesaurus. Usulan: *Knowledge distillation; Text classification; Natural language processing; Multilingual; Inference efficiency* (verifikasi istilah di IEEE Thesaurus).

### W-04 — Diskusi
- **Kriteria:** Diskusi menginterpretasikan temuan, membandingkannya dengan riset terdahulu, dan memposisikan penelitian. Hasil berbasis bukti dipisahkan dari spekulasi.
- **Sumber:** [MK] [L192](../materi_kuliah/summary_all_presentation.txt#L192); [R] [Lipton & Steinhardt](https://arxiv.org/abs/1807.03341); [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience)
- **Value:**
  - `W-04.discussion_points` = Tujuh paragraf:
    1. Tabel token cukup untuk sebagian besar topik (dikaitkan dengan [galke2022bow]).
    2. Sisa kesenjangan ada pada label yang tumpang tindih dan bahasa yang kurang terwakili; MiniLM vs DistilmBERT → kualitas representasi awal lebih menentukan.
    3. Sumber pengetahuan student: data multibahasa ([ye2022sparse]), inisialisasi selaras + bukti dari varian compact, representation drift.
    4. Soft label tidak membantu (dikaitkan dengan [zhang2025law], [wang2026rckd], [zhao2022dkd]).
    5. Batas generalisasi lintas bahasa (bahasa Afrika di luar pra-latih).
    6. Fidelity ≠ akurasi ([stanton2021kd]).
    7. Posisi terhadap Sparse Distillation, LoRA, kuantisasi; implikasi praktis (core per 1 juta artikel, cascade, compact).
- **Status:** ✅
- **Evidence:** [discussion.tex:1-39](../_archive/jurnal_latex_v1/sections/discussion.tex#L1-L39). Spekulasi diberi penanda ("mungkin berkat subword yang dipakai bersama" di [discussion.tex:18](../_archive/jurnal_latex_v1/sections/discussion.tex#L18)).
  - **Naskah final (2026-10-17):** [discussion.tex](../paper_final/main.tex): prosa, interpretasi dibedakan dari dugaan ("we suspect", "suggests").
- **Tindakan:** Perbaiki klaim τ = 2 di [discussion.tex:14](../_archive/jurnal_latex_v1/sections/discussion.tex#L14) (lihat N-05 butir 5). Klaim DistilmBERT di [discussion.tex:6](../_archive/jurnal_latex_v1/sections/discussion.tex#L6) ("tidak menutupnya", p = 0,800) sudah akurat.

### W-05 — Kesimpulan
- **Kriteria:** Kesimpulan menyoroti implikasi dan future work tanpa melebih-lebihkan, dan didukung data.
- **Sumber:** [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/); [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/)
- **Value:**
  - `W-05.conclusion_points` =
    1. Biaya CPU turun 2–3 orde besaran.
    2. Macro-F1 0,545 (91,1% teacher).
    3. 473 artikel/detik/core, 616×, 34 MB.
    4. Kunci keberhasilan: transfer set multibahasa + embedding selaras; soft label dan τ tinggi tidak membantu; ensemble dilipat tanpa biaya.
    5. Fine-tuning embedding vs transfer.
    6. Set uji dapat dipakai ulang.
  - `W-05.future_work` =
    - perluasan transfer set ke bahasa lemah
    - regularisasi fine-tuning
    - kepala non-linear murah
    - tokenizer lebih cepat
    - pemangkasan tokenizer lintas bahasa
    - IPTC level 2 / multi-label
    - validasi anotasi manusia multibahasa
- **Status:** ✅
- **Evidence:** [conclusion.tex:1-19](../_archive/jurnal_latex_v1/sections/conclusion.tex#L1-L19); semua angka melalui `\val{}`.
  - **Naskah final (2026-10-17):** [conclusion.tex](../paper_final/main.tex).
- **Tindakan:** — (dicek ulang: butir soft label/τ di [conclusion.tex:5](../_archive/jurnal_latex_v1/sections/conclusion.tex#L5) sudah sesuai bukti)

### W-06 — Gambar & tabel mendukung teks
- **Kriteria:** Setiap gambar dan tabel dirujuk di teks dan mendukung argumen. Pembahasan topik komprehensif.
- **Sumber:** [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/)
- **Value:**
  - `W-06.figures_tables` =
    - **10 gambar:** pipeline, testset heatmap, groups, temperature, ensemble, tradeoff, latency, per language, per label, calibration. Semuanya dirujuk.
    - **11 tabel:** related, testset, hparams, main, sig, groups, ablation, ablation-groups, eff, factors, cascade. **`tab:related` (Tabel I) tidak dirujuk di teks.**
- **Status:** ✅
- **Evidence:** hitungan `\ref{}` per label di `main.tex` + `sections/*.tex` (`tab:related` = 0 rujukan); `check_paper.py`: semua file gambar dan tabel ada.
  - **Naskah final (2026-10-17):** Semua gambar dan tabel dirujuk, termasuk Tabel I dan tabel lisensi.
- **Tindakan:** Tambahkan rujukan ke Tabel~\ref{tab:related} di akhir Subbagian II-D atau II-E ([main.tex:131](../_archive/jurnal_latex_v1/main.tex#L131)).

### W-07 — Bahasa Inggris standar & kejelasan
- **Kriteria:** Ditulis dalam bahasa Inggris standar dengan grammar benar ("Articles with poor grammar will be immediately rejected"). Matematika dipakai untuk memperjelas, dan istilah teknis dipakai dengan tepat.
- **Sumber:** [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/); [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/); [R] [Lipton & Steinhardt](https://arxiv.org/abs/1807.03341)
- **Value:**
  - `W-07.paper_language` = Bahasa Inggris (D17); angka berformat Inggris (desimal titik).
  - `W-07.proofreading` = TBD (setelah penulisan ulang oleh penulis).
- **Status:** ⚠️
- **Evidence:** [main.tex:2](../_archive/jurnal_latex_v1/main.tex#L2), [main.tex:23-27](../_archive/jurnal_latex_v1/main.tex#L23-L27).
  - **Naskah final (2026-10-17):** Naskah sudah berbahasa Inggris (keputusan 2026-10-17). Masih perlu proofreading oleh penulis (misalnya Paperpal Preflight) dan, sesuai E-01, penulisan ulang oleh penulis.
- **Tindakan (diperbarui 2026-10-17):**
  - **Sudah dikerjakan:** naskah berbahasa Inggris, istilah Indonesia dihapus, desimal titik, matematika wajar (3 persamaan inti, semuanya dirujuk).
  - **Yang tersisa (penulis):**
    1. tulis ulang naskah dengan kalimat sendiri, sesuai [paper_rewrite_steps.md](paper_rewrite_steps.md); ini juga syarat E-01;
    2. proofreading, misalnya Paperpal Preflight dari IEEE Access;
    3. jalankan `scripts/check_paper.py` (angka) dan `scripts/check_style.py` (gaya) setelah menulis ulang.

### W-08 — Template IEEE & panjang naskah
- **Kriteria:** Memakai template IEEE (naskah yang tidak mengikuti guideline dikembalikan atau ditolak). Panjang di bawah 20 halaman untuk IEEE Access.
- **Sumber:** [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/); [R] [IEEE Access – Preparing Your Article](https://ieeeaccess.ieee.org/authors/preparing-your-article/) (naskah "must be submitted using one of the following IEEE Access templates")
- **Value:**
  - `W-08.template` = saat ini `IEEEtran` mode journal (D20); template IEEE Access tersimpan di [template_ieeeaccess/](template_ieeeaccess/).
  - `W-08.page_count` = 16 halaman (PDF terkompilasi, 2026-10-17).
- **Status:** ⚠️
- **Evidence:** [main.tex:8](../_archive/jurnal_latex_v1/main.tex#L8); `main.log`: "Output written on main.pdf (15 pages)"; folder [template_ieee/](../_archive/jurnal_latex_v1/template_ieee/) hanya berisi template IEEE Transactions.
  - **Naskah final (2026-10-17):** Atas keputusan penulis (D20) naskah memakai format lama IEEEtran journal, satu file `main.tex`, 16 halaman (< 20). Template wajib IEEE Access diterapkan saat submit.
- **Tindakan (diperbarui 2026-10-17):**
  - Saat submit, pindahkan naskah ke template LaTeX IEEE Access ([template_ieeeaccess/](template_ieeeaccess/), sumber: [ACCESS_latex_template_20260513](https://ieeeaccess.ieee.org/wp-content/uploads/2026/05/ACCESS_latex_template_20260513-1-1.zip)).
  - Siapkan biografi dan foto kedua penulis (wajib di template IEEE Access).
  - Catatan: diagram TikZ bentrok dengan `ieeeaccess.cls`. Saat pindah template, diagram pipeline perlu dijadikan file PDF terpisah.
  - Panjang 16 halaman aman (< 20). Hitung ulang setelah pindah template.

---

## 6. Etika & integritas (yang tertulis di naskah)

### E-01 — AI disclosure di Acknowledgments
- **Kriteria:** Penggunaan AI (teks, gambar, kode) diungkapkan di bagian Acknowledgments: nama tool, bagian yang memakai konten AI, dan tingkat penggunaannya. Penggunaan AI hanya untuk editing grammar tetap disarankan untuk diungkapkan.
- **Sumber:** [R] [IEEE – Guidelines for AI-Generated Text](https://open.ieee.org/author-guidelines-for-artificial-intelligence-ai-generated-text/); [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/)
- **Value:**
  - `E-01.ai_disclosure_text` = (keputusan penulis, 2026-10-17; ditempatkan di Acknowledgments) "Penulis menggunakan Claude (Anthropic) untuk membantu penulisan kode eksperimen, pengolahan data (termasuk penyusunan awal tabel pemetaan rubrik ke IPTC, yang seluruhnya ditinjau penulis), serta review dan penyuntingan minor naskah. Naskah ditulis oleh penulis, dan penulis bertanggung jawab atas seluruh isi dan klaim." Sebutkan versi model Claude yang dipakai saat submit.
  - `E-01.condition` = Pernyataan ini hanya akurat bila **teks final ditulis ulang oleh penulis** (keputusan penulis). Draf Tahap 5 dari Claude berfungsi sebagai bahan. Kalau ada paragraf draf yang dipakai tanpa ditulis ulang, pernyataan harus diperluas dengan menyebut "penyusunan draf naskah".
- **Status:** ⚠️
- **Evidence:** [main.tex:412-413](../_archive/jurnal_latex_v1/main.tex#L412-L413) (bagian terpisah "Pernyataan Penggunaan AI"); Ucapan Terima Kasih masih `\todo` di [main.tex:415-416](../_archive/jurnal_latex_v1/main.tex#L415-L416).
  - **Naskah final (2026-10-17):** Pernyataan AI ada di Acknowledgment ([acknowledgment.tex](../paper_final/main.tex)), tetapi kalimat "The manuscript was written by the authors" hanya akurat bila penulis menulis ulang teks bahasa Inggris dari Claude (lihat temuan review).
- **Tindakan (diperbarui 2026-10-17):**
  - **Sudah dikerjakan:** pernyataan ada di Acknowledgment, menyebut alat (Claude, Anthropic), bagian yang dibantu (kode, pengolahan data termasuk tabel pemetaan yang ditinjau penulis, review dan penyuntingan minor), dan tanggung jawab penulis. Isinya tidak diubah (keputusan penulis, D17/D18).
  - **Yang tersisa (penulis):**
    1. tulis ulang naskah (W-07). Kalau ada paragraf draf yang dipakai tanpa ditulis ulang, pernyataan harus diperluas dengan "drafting of the manuscript";
    2. saat submit, tambahkan versi model Claude yang dipakai.

### E-02 — Similarity / plagiarisme
- **Kriteria:** Lolos cek similarity (Turnitin/iThenticate), dengan target dari kuliah < 25%. Semua kutipan, parafrase, dan tabel/gambar dari pihak lain disitasi. Semua naskah IEEE disaring sebelum masuk Xplore.
- **Sumber:** [MK] [L75](../materi_kuliah/summary_all_presentation.txt#L75); [R] [IEEE – Ethical Requirements](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/ethical-requirements/)
- **Value:**
  - `E-02.similarity_score` = TBD — ditunda (keputusan penulis: "nanti saja"); dicek pada versi bahasa Inggris final.
- **Status:** ❌
- **Evidence:** tidak ada laporan similarity di repo.
  - **Naskah final (2026-10-17):** Turnitin ditunda (keputusan penulis).
- **Tindakan:** Jalankan Turnitin/iThenticate (lewat kampus) **pada versi bahasa Inggris final**. Targetnya < 25% (aturan MK). Semua gambar adalah buatan sendiri (`figures/`, dibuat oleh notebook), jadi tidak perlu izin pihak ketiga.

### E-03 — Tidak ada fabrikasi/falsifikasi
- **Kriteria:** Setiap angka di naskah bisa ditelusuri ke hasil eksperimen asli (notebook, `_archive/jurnal_latex_v1/generated/`).
- **Sumber:** [MK] [L17](../materi_kuliah/summary_all_presentation.txt#L17)
- **Value:**
  - `E-03.number_source` = Semua angka hasil memakai `\val{kunci}` dari `generated/numbers.tex` (1.014 kunci terdefinisi, 207 dipakai, 0 hilang). Sembilan tabel memakai `\rows{generated/tab_*.tex}`. Semuanya ditulis oleh `notebooks/StaticKD_IPTC_final.ipynb` (Bagian 11), dengan sumber data `results/final/*.json(l)`.
- **Status:** ✅
- **Evidence:** [main.tex:5-6](../_archive/jurnal_latex_v1/main.tex#L5-L6), [main.tex:34-35](../_archive/jurnal_latex_v1/main.tex#L34-L35); output `python scripts/check_paper.py` (0 missing, 0 error, 0 undefined).
  - **Naskah final (2026-10-17):** check_paper.py: 231 kunci dipakai, 0 hilang; 0 "??" di PDF; notebook dijalankan ulang, nilai sama.
- **Tindakan (diperbarui 2026-10-17):** Naskah final memakai angka literal (D20). `results/final/paper_number_map.json` mencatat 247 kunci angka di `main.tex`, dan `scripts/check_paper.py` melaporkan literal yang hilang atau berubah. Jalankan setelah penulisan ulang dan setelah setiap eksperimen baru.

### E-04 — Authorship & identitas penulis
- **Kriteria:** Setiap penulis memenuhi kriteria authorship IEEE (kontribusi intelektual signifikan, ikut menulis/merevisi, menyetujui versi final). Afiliasi lengkap.
- **Sumber:** [R] [IEEE – Ethical Requirements](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/ethical-requirements/)
- **Value:**
  - `E-04.authors` = Obi Kastanya (6025252015@student.its.ac.id, **penulis korespondensi**); Ananta Dwi Prayoga Alwy (6025252007@student.its.ac.id). Dosen pembimbing tidak menjadi penulis (keputusan penulis, 2026-10-17).
  - `E-04.affiliations` = Kedua penulis: Department of Informatics Engineering, Sepuluh Nopember Institute of Technology (Institut Teknologi Sepuluh Nopember), Surabaya, Indonesia. Sumber: [IEEE-conference-template-062824.tex](../IEEE-conference-template-062824.tex) baris 38–48.
- **Status:** ✅
- **Evidence:** [main.tex:43-44](../_archive/jurnal_latex_v1/main.tex#L43-L44) (afiliasi dan e-mail masih `\todo`).
  - **Naskah final (2026-10-17):** Penulis, afiliasi, e-mail, dan penulis korespondensi ada di halaman judul. Biografi masih TODO.
- **Tindakan (diperbarui 2026-10-17):** Afiliasi, e-mail, dan keputusan pembimbing sudah selesai (D13). Yang tersisa: pastikan Ananta ikut merevisi dan menyetujui versi final (kriteria authorship IEEE), dan siapkan biografi kedua penulis (W-08).

---

## 7. Konsistensi internal naskah

### K-01 — Validitas & reliabilitas pengukuran
- **Kriteria:** Pengukuran benar-benar mengukur yang diklaim (validitas) dan konsisten bila diulang (reliabilitas). Contoh: benchmark CPU diulang dan kondisinya dikontrol, dan test set mewakili klaim multibahasa.
- **Sumber:** [MK] [L160](../materi_kuliah/summary_all_presentation.txt#L160), [L180](../materi_kuliah/summary_all_presentation.txt#L180)
- **Value:**
  - `K-01.benchmark_protocol` =
    - **Yang dikontrol:** CPU saja (GPU disembunyikan); proses baru per model; thread dikunci di semua pustaka; pinning ke P-core (1 core: CPU 0; 4 core: 0, 10, 12, 14); 3 dokumen warm-up; satu sesi saat mesin idle; sampel teks acak tetap dari set uji, sama untuk semua model.
    - **Ukuran sampel (sudah ditulis di paper):** transformer dan teacher: 30 dokumen untuk latensi, 48 untuk throughput (batch 8). Model ringan: 500 untuk latensi, 3.000 untuk throughput (batch 64).
    - **Pengulangan:** setiap konfigurasi diukur sekali; tidak ada variasi antar-run.
    - **Validitas set uji:** label silver divalidasi terhadap label manusia bahasa Inggris (teacher: akurasi 0,646 pada silver vs 0,559 pada manusia; ρ tingkat kesulitan label = 0,63, p = 0,007) + pemeriksaan per kategori sumber.
  - `K-01.label_construct` = (keputusan: tanpa anotasi manusia tambahan) Label rubrik dan kategori adalah **topik editorial yang ditetapkan redaksi penerbit saat artikel dipublikasikan**, lalu diterjemahkan ke IPTC dengan tabel deterministik. Konsekuensinya:
    - label independen dari model mana pun yang membaca teks (teacher, LLM), sehingga tidak ada sirkularitas;
    - macro-F1 pada label ini dibaca sebagai **kesesuaian dengan kategorisasi editorial**;
    - perbedaan dengan teacher bisa berasal dari skema kategori yang berbeda, bukan dari label yang salah (contoh: MasakhaNEWS *politics* → alternatif *conflict* 29%).
- **Status:** ⚠️
- **Evidence:** [main.tex:360-371](../_archive/jurnal_latex_v1/main.tex#L360-L371); `src/statickd/benchmark.py:65-77` (warm-up, loop latensi dan throughput); `results/final/cpu_benchmark.jsonl` (`n_latency`, `n_throughput` per model); [results.tex:50-67](../_archive/jurnal_latex_v1/sections/results.tex#L50-L67).
  - **Naskah final (2026-10-17):** Definisi konstruk label dan ukuran sampel benchmark (30/48 dan 500/3.000) sudah ditulis. Pengulangan benchmark 3× dilewati (poin baseline/benchmark).
- **Tindakan (diperbarui 2026-10-17):**
  - **Sudah dikerjakan:**
    - ukuran sampel benchmark (30/48 dan 500/3,000) dan "satu sesi" ditulis di Protokol Efisiensi dan Limitations;
    - konstruk label editorial ditulis di Konstruksi Set Uji dan Discussion;
    - validasi bahasa Prancis dilaporkan ([main.tex:455](../paper_final/main.tex#L455): 0.716 pada 208 artikel berlabel rubrik vs 0.500 pada 200 artikel MasakhaNEWS);
    - hasil per sumber (MN-DS terpisah) ditambahkan.
  - **Keputusan D21:** benchmark 3× (D4) **ditunda ke tahap revisi**.
  - 📝 **Risiko sisa:**
    1. p50 latensi model berat diambil dari 30 dokumen dalam satu sesi. Arah rasio 616× hampir pasti tidak berubah, tetapi angka absolutnya bisa dipertanyakan.
    2. (Prioritas rendah, opsional) Tabel pemetaan rubrik → IPTC ditinjau oleh satu orang tanpa ukuran kesepakatan. **Koreksi audit 2026-10-17:** sebelumnya ini disebut "kelemahan paling rawan", dan itu keliru. Labelnya berasal dari rubrik dan breadcrumb dokumen sendiri, diterjemahkan dengan aturan presisi (62 nama ambigu dikecualikan, validasi otomatis ke pohon IPTC, artikel berlabel konflik ditolak), dan 916 aturan ditinjau penulis. Bukti empirisnya juga ada: teacher lebih akurat pada label rubrik daripada label manusia (en 0.646 vs 0.559; fr 0.716 vs 0.500), dengan ρ tingkat kesulitan 0.63. κ dari peninjau kedua hanya penguat tambahan.

### K-02 — Klaim kesimpulan didukung data
- **Kriteria:** Setiap klaim di kesimpulan dan abstrak punya tabel atau gambar pendukung di bagian hasil. Angka di abstrak, teks, dan tabel konsisten.
- **Sumber:** [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/) ("conclusions … supported by the data")
- **Value:**
  - `K-02.claim_evidence_map` = lihat `N-05.main_claims`. Konsistensi angka terjamin karena abstrak, teks, kesimpulan, dan tabel memakai kunci `\val{}` yang sama. Dua klaim belum sesuai bukti (DistilmBERT di [results.tex:17](../_archive/jurnal_latex_v1/sections/results.tex#L17); τ ≥ 2 di [main.tex:95](../_archive/jurnal_latex_v1/main.tex#L95) dan [discussion.tex:14](../_archive/jurnal_latex_v1/sections/discussion.tex#L14)), satu klaim ambigu ("tujuh keluarga model"), dan satu fakta pembanding belum diakui (fastText terkuantisasi lebih cepat dan kecil).
- **Status:** ✅
- **Evidence:** `check_paper.py` (0 kunci hilang); lihat Evidence N-05.
  - **Naskah final (2026-10-17):** Klaim abstrak dan kesimpulan dicocokkan ulang dengan hasil; tidak ada klaim berlebihan yang tersisa.
- **Tindakan (diperbarui 2026-10-17):** Selesai untuk naskah sekarang. Ulangi pencocokan klaim bila abstrak atau kesimpulan ditulis ulang, atau bila eksperimen baseline dijalankan saat revisi (klaim atas TF-IDF dan DistilmBERT paling mungkin berubah).

---

## 8. Jurnal & submission (dicek nanti, di luar isi naskah)

### J-01 — Quartile jurnal target diverifikasi
- **Kriteria:** Quartile dicek per kategori subjek pada tahun terbaru. Quartile versi SJR (Scopus) dan JCR (WoS) bisa berbeda.
- **Sumber:** [S] [CASRAI – JIF & quartile](https://casrai.org/guides/journal-impact-factor-and-quartile-rankings); cek langsung di [scimagojr.com](https://www.scimagojr.com)
- **Value:**
  - `J-01.target_journal` = IEEE Access
  - `J-01.quartile` = TBD. Data resmi IEEE Access: SJR 2025 = 0,884, Impact Factor 2025 = 4,2, CiteScore 2025 = 9,3. Quartile per kategori belum terverifikasi; agregator saling bertentangan (Q1 vs Q2).
- **Status:** ⏳
- **Evidence:** [IEEE Access – Bibliometrics](https://ieeeaccess.ieee.org/about/bibliometrics/) (dicek 2026-10-17); agregator: [researcher.life](https://researcher.life/amp/journal/ieee-access/516) (Q2), [paperguide.ai](https://paperguide.ai/journals/c38b5e81-156d-4e94-a69a-e5dbe8af726c) (Q1, tidak andal).
- **Tindakan:** (2026-10-17: belum dicek oleh penulis) **Lakukan paling awal**, sebelum pindah template (W-08). Cek di scimagojr.com dan simpan tangkapan layar beserta tanggalnya.

### J-02 — Jurnal masih aktif terindeks Scopus
- **Kriteria:** Jurnal tidak ada di daftar *discontinued titles* Scopus.
- **Sumber:** [R] [Elsevier – Scopus content policy](https://www.elsevier.com/ja-jp/products/scopus/content/content-policy-and-selection)
- **Value:**
  - `J-02.scopus_status` = TBD
- **Status:** ⏳
- **Evidence:** —
- **Tindakan:** Cek di Scopus Sources / daftar discontinued titles terbaru.

### J-03 — Bukan jurnal predator
- **Kriteria:** Jurnal lolos checklist Think.Check.Submit.
- **Sumber:** [R] [Think.Check.Submit (Taylor & Francis)](https://authorservices.taylorandfrancis.com/think-check-submit/)
- **Value:**
  - `J-03.tcs_result` = TBD
- **Status:** ⏳
- **Evidence:** —
- **Tindakan:** Isi checklist Think.Check.Submit. Hasilnya kemungkinan lolos (penerbit IEEE), tetapi tetap perlu dicatat.

### J-04 — Topik masuk scope jurnal
- **Kriteria:** Topik paper sesuai dengan scope jurnal target.
- **Sumber:** [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/); [MK] [L134](../materi_kuliah/summary_all_presentation.txt#L134)
- **Value:**
  - `J-04.scope_fit` = Sesuai. IEEE Access adalah jurnal multidisiplin, dan karya acuan utama paper ini (Kuzman & Ljubešić 2025, sumber teacher) juga terbit di IEEE Access.
- **Status:** ✅
- **Evidence:** `references.bib` → `kuzman2025llm`: journal = IEEE Access.
  - **Naskah final (2026-10-17):** Tetap.
- **Tindakan:** —

### S-01 — Tidak submit ganda; preprint diungkapkan
- **Kriteria:** Naskah tidak sedang disubmit ke jurnal lain. Versi preprint atau konferensi diungkapkan beserta perbedaannya. Jika diunggah ke arXiv, cantumkan "This work has been submitted to the IEEE for possible publication."
- **Sumber:** [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/); [R] [IEEE – Submission & Peer Review Policies](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/)
- **Value:**
  - `S-01.preprint_status` = Tidak ada preprint arXiv (keputusan penulis, 2026-10-17); tidak ada publikasi sebelumnya; naskah tidak dikirim ke jurnal lain.
- **Status:** ✅
- **Evidence:** —
  - **Naskah final (2026-10-17):** Tetap: tidak ada preprint.
- **Tindakan:** — (sudah diputuskan: tanpa arXiv, D15)

### S-02 — Cover letter
- **Kriteria:** Cover letter menjelaskan novelty, signifikansi, dan kecocokan dengan jurnal, serta menyatakan naskah tidak sedang direview di tempat lain. Tidak menyalin abstrak.
- **Sumber:** [R] [Elsevier Connect – "Dear Editor…"](https://www.elsevier.com/connect/dear-editor-we-enclose-our-paper-for-your-kind-consideration); [S] [CASRAI – cover letter](https://casrai.org/dictionary/term/cover-letter-for-journal-submission)
- **Value:**
  - `S-02.cover_letter_points` = TBD
- **Status:** ⏳
- **Evidence:** —
- **Tindakan:** Susun setelah naskah final; bahannya dari `N-03`, `N-04`, `J-04`.

### S-03 — Rilis artefak sebelum submit
- **Kriteria:** Kode, data, dan model sudah dirilis di repositori (sebaiknya ber-DOI) sesuai URL yang tertulis di naskah (lihat R-01).
- **Sumber:** [R] [IEEE Access – Reproducibility](https://ieeeaccess.ieee.org/authors/reproducibility/)
- **Value:**
  - `S-03.artifact_release` = Paket sudah dibangun di `dist/github/` dan `dist/huggingface/`; belum diunggah dan belum punya DOI.
- **Status:** ⚠️
- **Evidence:** folder [dist/](../dist/) (README, LICENSE MIT, CITATION.cff, model card CC BY-SA 4.0).
- **Tindakan:** (keputusan: sebelum submit)
  1. bangun ulang `dist/` karena paketnya usang (lihat temuan di R-01);
  2. unggah, buat rilis + DOI (Zenodo);
  3. isi `R-01.*` dan `[TODO]` di bagian Availability.

### S-04 — Respons reviewer saat resubmit
- **Kriteria:** Jika resubmit setelah reject, lampirkan daftar komentar reviewer, respons penulis, dan perubahan yang dilakukan.
- **Sumber:** [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/)
- **Value:**
  - `S-04.response_letter` = —
- **Status:** ➖ (belum relevan; baru berlaku jika resubmit)
- **Evidence:** —
- **Tindakan:** —

---

## Keputusan & rencana tindakan (2026-10-17)

### Keputusan

| # | Topik | Keputusan |
|---|---|---|
| D1 | Validitas label (K-01) | Tanpa anotasi manusia tambahan. Label rubrik/kategori didefinisikan sebagai topik editorial penerbit (`K-01.label_construct`). |
| D2 | Tabel pemetaan (M-02) | Penulis meninjau tabel 814 nama rubrik + 102 aturan lain. **Selesai 2026-10-17: semua diterima, 0 perubahan** ([mapping_review.xlsx](mapping_review.xlsx)). |
| D3 | Tuning baseline (M-05) | Grid kecil yang ditetapkan sebelum dijalankan; hasilnya dilaporkan apa pun hasilnya (lihat rancangan di bawah). |
| D4 | Benchmark (K-01) | Ulang 3× di sesi terpisah; teacher dan transformer memakai ≥ 100 dokumen latensi. Laporkan median dan rentang. |
| D5 | Sparse Distillation (M-04) | Dipetakan ke fastText + KD dan ablasi inisialisasi acak; tidak diimplementasikan. |
| D6 | Referensi jurnal (L-04) | Hanya tambah yang relevan; tidak mengejar kuota 30%. |
| D7 | Urutan | ~~Konten dulu (eksperimen, Value, referensi) → paper final ditulis di template IEEE Access → terjemahan oleh penulis → Turnitin dan audit akhir.~~ Digantikan oleh D17 (bahasa Inggris), D20 (IEEEtran satu file), dan D21 (tanpa eksperimen baru). Urutan terkini ada di tabel "Urutan kerja". |
| D8 | Gaya tulisan | Ikuti [ai_text_criteria_to_be_avoided.txt](ai_text_criteria_to_be_avoided.txt). Setelah menulis, cek ulang dengan daftar cek bagian 8 dan perbaiki tanpa merusak alur kalimat atau informasi. |
| D9 | Daftar & label tebal | Pendahuluan, Penelitian Terkait, Hasil, dan Pembahasan ditulis sebagai prosa. Daftar hanya untuk RQ, kontribusi, dan langkah prosedur. Tidak ada label tebal di tengah paragraf. Draf sekarang: 41 blok daftar, ±77 label tebal. |
| D10 | Gambar | Hanya dari script, bukan gambar buatan LLM. Kode gambar tetap di notebook `notebooks/StaticKD_IPTC_final.ipynb` + `src/statickd/viz.py`; sumber notebook yang masih di `scratch/nb_final/` dipindahkan ke `src/`. Diagram pipeline tetap TikZ. |
| D11 | Referensi PDF | Disimpan di `reference/` (root), ditambah file indeks (key bib → file PDF → status verifikasi). PDF yang tidak open access diminta ke penulis (akses IEEE/Elsevier). |
| D13 | Penulis & afiliasi (E-04) | Obi Kastanya (korespondensi) dan Ananta Dwi Prayoga Alwy, Department of Informatics Engineering, ITS, Surabaya. Pembimbing tidak menjadi penulis. Acknowledgments: Departemen Teknik Informatika ITS; tidak ada pendanaan. |
| D14 | Peran AI (E-01) | Kode, pengolahan data (termasuk tabel pemetaan yang ditinjau penulis), review dan penyuntingan minor. **Teks final ditulis ulang oleh penulis**; draf Tahap 5 hanya bahan. |
| D15 | Rilis & preprint (R-01, S-01) | Rilis kode/model/manifest sebelum submit (akun penulis, panduan dari Claude). Tidak ada preprint arXiv. |
| D16 | Ditunda | Quartile (J-01) belum dicek; Turnitin (E-02) nanti; grid baseline (M-05) dan benchmark 3× (K-01) ditunda (ke tahap revisi, lihat D21). |
| D17 | Bahasa paper | Naskah final `paper_final/` ditulis dalam bahasa Inggris; output notebook (angka, tabel, gambar) dalam format bahasa Inggris. Naskah ini **belum final**: versi final ditulis sendiri oleh penulis, sehingga pernyataan AI tetap seperti sekarang. |
| D18 | Review sebagai reviewer (temuan 1–8) | (1) Pernyataan AI tidak diubah. (2) Hasil per sumber ditambahkan (Tabel \ref{tab:sources}, MN-DS terpisah). (3) Embedding beku dibiarkan (model final tetap, dipilih di dev). (4) Set cek LLM16 ditulis di Study Design. (5) Throughput cascade diukur langsung **nanti**. (6) Batas token tiap model dan persentase artikel terpotong ditulis (teacher 60,7%, MiniLM 91,1%, DistilmBERT 93,2%, StaticKD 5,4%). (7) Motivasi energi dilunakkan menjadi biaya. (8) Kontribusi set uji dan temuan analitis ditonjolkan di abstrak dan pendahuluan. |
| D20 | Struktur & format naskah | `paper_final/` berisi **satu file `main.tex`** dengan angka literal, format lama **IEEEtran journal** (bukan template IEEE Access), `references.bib`, `IEEEtran.cls/.bst`, dan `figures/` yang hanya berisi 9 gambar yang dipakai. Sumber modular di `src/paper/`; `python scripts/build_paper.py` membangun `main.tex` (menolak menimpa bila `main.tex` sudah disunting, kecuali `--force`). `scripts/check_paper.py` melaporkan angka yang berubah setelah notebook dijalankan ulang. Template IEEE Access tersimpan di `paper_writing/template_ieeeaccess/` untuk dipakai saat submit. |
| D19 | Baseline 256 token | MiniLM-L6 dan DistilmBERT dilatih dengan 256 token; latih ulang dengan 512 token ditunda bersama grid baseline. Dinyatakan di Methodology dan Limitations. |
| D12 | File paper final | Ditulis di file/folder baru (`paper_final/`). `_archive/jurnal_latex_v1/main.tex` tetap utuh sebagai arsip. |
| D21 | Eksperimen sebelum submit | **Tidak ada eksperimen baru** karena keterbatasan waktu (estimasi ±27–33 jam mesin di laptop penulis). Grid baseline (M-05), transformer 512 token (D19), baseline trainer Model2Vec (M-04), benchmark 3× (K-01), dan pengukuran cascade langsung dikerjakan **saat revisi** bila diminta reviewer. Trainer Model2Vec ditangani lewat teks (Related Work, Tabel I, Baselines, Limitations). Rincian di [change_log.md](change_log.md). |

### Rancangan grid baseline (D3, ditetapkan sebelum dijalankan)

- **fastText + KD** (token kata dan subword): lr ∈ {0,1; 0,5; 1,0} × dim ∈ {100; 300} × epoch ∈ {5; 15; 25} → 18 konfigurasi per jenis token. Varian terkuantisasi dibuat dari konfigurasi subword terbaik.
- **TF-IDF + SVM + KD:** C ∈ {0,1; 0,25; 0,5; 1; 2} → 5 konfigurasi.
- **Kriteria pemilihan:** macro-F1 pada EMMediaTopic dev, sama dengan cara memilih resep StaticKD. Set uji tidak dipakai untuk memilih.
- **Pelaporan:** semua konfigurasi beserta skor dev-nya, dan konfigurasi terpilih masuk Tabel Hasil.

### Urutan kerja (diperbarui 2026-10-17)

**Sudah selesai:**
- Wilcoxon antarbahasa dan waktu pelabelan teacher (M-07, M-09);
- sumber notebook dipindah ke `src/notebook_build/`;
- tinjauan tabel pemetaan (M-02, D2);
- verifikasi 46 referensi dan isi `reference/` (L-02, L-04, L-05);
- data penulis (E-04, D13);
- naskah bahasa Inggris satu file di `paper_final/` (D17, D20);
- audit gaya dan audit 46 poin;
- penanganan Model2Vec lewat teks (D21).

**Yang tersisa:**

| Tahap | Pekerjaan | Pelaksana | Poin checklist |
|---|---|---|---|
| 1 | Cek quartile di scimagojr.com, status Scopus, dan Think.Check.Submit (lakukan paling awal) | Anda | J-01, J-02, J-03 |
| 2 | Tulis ulang naskah sesuai [paper_rewrite_steps.md](paper_rewrite_steps.md) → `check_paper.py` + `check_style.py` → proofreading | Anda (cek oleh saya) | W-07, E-01 |
| 3 | Bangun ulang `dist/` → unggah GitHub, Hugging Face, Zenodo → isi URL di Availability | Saya (paket) + Anda (unggah) | R-01, S-03 |
| 4 | Pindah ke template IEEE Access + biografi dan foto penulis | Anda + saya | W-08 |
| 5 | Turnitin pada versi final; cover letter; audit akhir | Anda + saya | E-02, S-02 |
| Revisi | Bila diminta reviewer: grid baseline, transformer 512 token, trainer Model2Vec, benchmark 3×, cascade langsung | Saya | M-05, K-01, M-04 (D21) |

## Catatan sumber

- Situs scimagojr.com menolak akses otomatis saat diverifikasi, jadi definisi quartile diambil dari CASRAI (sumber sekunder).
- Ambang similarity IEEE (sering disebut 30%) dan acceptance rate IEEE Access hanya ditemukan di sumber sekunder, sehingga tidak dijadikan kriteria.
- Kewajiban template IEEE Access dan peringatan referensi fiktif diverifikasi pada 2026-10-17 di [IEEE Access – Preparing Your Article](https://ieeeaccess.ieee.org/authors/preparing-your-article/).
- Materi kuliah ([summary_all_presentation.txt](../materi_kuliah/summary_all_presentation.txt)) adalah ringkasan AI dari slide kuliah.
