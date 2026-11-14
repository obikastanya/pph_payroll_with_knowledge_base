# Paper Quality Check — Target Jurnal Q1/Q2 (IEEE)

Checklist kualitas naskah paper StaticKD (IPTC news topic classification) sebelum submit ke jurnal Q1/Q2 berformat IEEE (target: IEEE Access).

- **Naskah yang dicek:** [_archive/jurnal_latex_v1/main.tex](../_archive/jurnal_latex_v1/main.tex) dan [_archive/jurnal_latex_v1/sections/](../_archive/jurnal_latex_v1/sections/)
- **Fokus saat ini:** isi naskah paper (Bagian 1–7). Bagian 8 (pemilihan jurnal & submission) dicek nanti.
- **Asal kriteria:** setiap poin punya rujukan. **[MK]** = materi kuliah Metpen ([summary_all_presentation.txt](../materi_kuliah/summary_all_presentation.txt)), **[R]** = sumber resmi/primer, **[S]** = sumber sekunder.

> Catatan: Q1/Q2 adalah peringkat *jurnal* (Q1 = 25% teratas kategori subjeknya, Q2 = 25–50%), bukan peringkat paper. Jadi checklist ini memakai kriteria reviewer jurnal target (IEEE Access, IEEE Transactions) ditambah standar pelaporan riset ML/NLP.

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

| Bagian | Jumlah poin | ✅ | ⚠️ | ❌ | ⏳ |
|---|---|---|---|---|---|
| 1. Masalah, gap & novelty | 6 | 0 | 0 | 0 | 6 |
| 2. Tinjauan pustaka & referensi | 5 | 0 | 0 | 0 | 5 |
| 3. Metodologi & eksperimen | 11 | 0 | 0 | 0 | 11 |
| 4. Reproducibility | 2 | 0 | 0 | 0 | 2 |
| 5. Penulisan & format IEEE | 8 | 0 | 0 | 0 | 8 |
| 6. Etika & integritas (isi naskah) | 4 | 0 | 0 | 0 | 4 |
| 7. Konsistensi internal naskah | 2 | 0 | 0 | 0 | 2 |
| 8. Jurnal & submission (nanti) | 8 | 0 | 0 | 0 | 8 |
| **Total** | **46** | **0** | **0** | **0** | **46** |

---

## 1. Masalah, research gap & novelty

### N-01 — Gap nyata, didukung data awal
- **Kriteria:** Pendahuluan menunjukkan kesenjangan antara kondisi ideal dan kondisi faktual (das sollen vs das sein), didukung data/angka awal. Contoh: biaya inferensi teacher vs kebutuhan pipeline real-time.
- **Sumber:** [MK] [L57](../materi_kuliah/summary_all_presentation.txt#L57), [L205](../materi_kuliah/summary_all_presentation.txt#L205)
- **Value:**
  - `N-01.gap_statement` =
  - `N-01.gap_evidence_numbers` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### N-02 — Problem statement lengkap
- **Kriteria:** Problem statement memuat konteks + urgensi + tujuan.
- **Sumber:** [MK] [L63](../materi_kuliah/summary_all_presentation.txt#L63)
- **Value:**
  - `N-02.problem_context` =
  - `N-02.problem_urgency` =
  - `N-02.research_objective` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### N-03 — Novelty dinyatakan eksplisit terhadap prior work
- **Kriteria:** Ada kalimat novelty yang membandingkan langsung dengan penelitian sebelumnya ("penelitian A, B, C hanya fokus pada X… paper ini menawarkan Y"). Pendahuluan menunjukkan apa yang baru dan mengapa penting. Ada daftar kontribusi yang jelas.
- **Sumber:** [MK] [L105](../materi_kuliah/summary_all_presentation.txt#L105); [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)
- **Value:**
  - `N-03.novelty_statement` =
  - `N-03.contributions` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### N-04 — Kontribusi berbeda dari publikasi sebelumnya & sahih secara teknis
- **Kriteria:** Kontribusi jelas berbeda dari prior work dan didukung data yang cukup. IEEE Access tidak menuntut novelty tinggi, tetapi jurnal setingkat IEEE Transactions menolak paper yang "insufficient novelty" (metode atau pendekatan baru).
- **Sumber:** [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/); [R] [IEEE SPS – Guidelines for Reviewers](https://signalprocessingsociety.org/publications-resources/guidelines-reviewers)
- **Value:**
  - `N-04.closest_prior_work` =
  - `N-04.difference_from_prior_work` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### N-05 — Klaim sesuai bukti, tidak dilebih-lebihkan
- **Kriteria:** Klaim di abstrak dan pendahuluan sesuai dengan kontribusi dan scope yang benar-benar dibuktikan. Kesimpulan tidak membesar-besarkan temuan.
- **Sumber:** [R] [NeurIPS Paper Checklist (1a)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist); [R] [IEEE Author Center](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/) ("Be careful not to inflate your findings")
- **Value:**
  - `N-05.main_claims` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### N-06 — Research question / tujuan terhubung ke hasil
- **Kriteria:** Masalah (why), teori (what), dan metode (how) saling terhubung. Setiap pertanyaan penelitian atau tujuan dijawab di bagian hasil atau diskusi.
- **Sumber:** [MK] [L60](../materi_kuliah/summary_all_presentation.txt#L60), [L202](../materi_kuliah/summary_all_presentation.txt#L202)
- **Value:**
  - `N-06.research_questions` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

---

## 2. Tinjauan pustaka & referensi

### L-01 — Literature review kritis → SotA → gap
- **Kriteria:** Related work dianalisis secara kritis (bukan sekadar daftar), memetakan state of the art, lalu menurunkan gap dan novelty. Lebih baik kalau pencarian literaturnya sistematis (database, kata kunci/Boolean, kriteria seleksi).
- **Sumber:** [MK] [L84–L99](../materi_kuliah/summary_all_presentation.txt#L84-L99)
- **Value:**
  - `L-01.related_work_groups` =
  - `L-01.search_protocol` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### L-02 — Setiap sitasi dijelaskan kaitannya
- **Kriteria:** Setiap referensi dijelaskan hubungannya dengan paper. Referensi cukup dan relevan, dan tidak ada yang tidak sesuai topik.
- **Sumber:** [R] [IEEE SPS Reviewer Guidelines](https://signalprocessingsociety.org/publications-resources/guidelines-reviewers) ("lists of references without explanation are unacceptable"); [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/)
- **Value:**
  - `L-02.citation_map` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### L-03 — Tidak ada citation padding / self-citation tidak relevan
- **Kriteria:** Hanya mengutip sumber yang benar-benar berkontribusi pada paper.
- **Sumber:** [R] [IEEE – Ethical Requirements](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/ethical-requirements/); [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)
- **Value:**
  - `L-03.irrelevant_refs_removed` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### L-04 — Referensi terbaru & bereputasi
- **Kriteria:** Mayoritas referensi dari 3–5 tahun terakhir, dan minimal 30% dari jurnal bereputasi (Scopus Q1–Q4 / Sinta 1–2). Evidence: jumlah referensi per tahun dan per jenis venue dari `references.bib`.
- **Sumber:** [MK] [L72](../materi_kuliah/summary_all_presentation.txt#L72), [L208](../materi_kuliah/summary_all_presentation.txt#L208)
- **Value:**
  - `L-04.ref_stats` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### L-05 — Tidak ada referensi yang sudah di-retract
- **Kriteria:** Tidak ada referensi yang sudah di-retract. IEEE Access mengembalikan naskah yang mengutip paper retracted.
- **Sumber:** [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/)
- **Value:**
  - `L-05.retracted_refs` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

---

## 3. Metodologi & eksperimen (ML/NLP)

### M-01 — Metode transparan & bisa direplikasi
- **Kriteria:** Metode dijelaskan cukup detail agar orang lain bisa mereplikasinya.
- **Sumber:** [MK] [L211](../materi_kuliah/summary_all_presentation.txt#L211); [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/) (analisis "described in sufficient detail")
- **Value:**
  - `M-01.method_summary` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### M-02 — Data: pemilihan, sumber, preprocessing
- **Kriteria:** Menjelaskan bagaimana dan mengapa data dipilih, serta bagaimana data dipreprocess, difilter, dan dikategorikan.
- **Sumber:** [R] [ACM SIGSOFT Empirical Standards – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience)
- **Value:**
  - `M-02.data_sources` =
  - `M-02.preprocessing_steps` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### M-03 — Setup eksperimen & pendekatan model
- **Kriteria:** Setup eksperimen disajikan (misalnya dalam diagram alur) dan pendekatan model didefinisikan (misalnya dengan pseudocode atau persamaan).
- **Sumber:** [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience)
- **Value:**
  - `M-03.pipeline_figure` =
  - `M-03.model_definition` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### M-04 — Baseline state-of-the-art yang kuat
- **Kriteria:** Dibandingkan dengan baseline SotA beserta keterbatasannya, atau ada justifikasi kuat kalau perbandingan tidak memungkinkan.
- **Sumber:** [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience)
- **Value:**
  - `M-04.baselines` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### M-05 — Detail training & pemilihan hyperparameter
- **Kriteria:** Data split, hyperparameter, dan cara memilih hyperparameter dilaporkan. Budget tuning tiap metode juga dilaporkan agar perbandingan adil.
- **Sumber:** [R] [NeurIPS Checklist (3b)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist); [R] [Dodge et al., EMNLP 2019 – Show Your Work](https://aclanthology.org/D19-1224/)
- **Value:**
  - `M-05.data_split` =
  - `M-05.hyperparameters` =
  - `M-05.tuning_budget` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### M-06 — Variasi hasil (multi-seed, error bar / CI)
- **Kriteria:** Hasil tidak hanya satu angka. Sertakan error bar atau confidence interval (misalnya dari beberapa seed atau bootstrap), dan sebutkan cara menghitungnya.
- **Sumber:** [R] [NeurIPS Checklist (3c)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist); [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience) ("goes beyond single-dimensional summaries of performance")
- **Value:**
  - `M-06.n_seeds` =
  - `M-06.ci_method` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### M-07 — Uji signifikansi statistik yang tepat
- **Kriteria:** Perbedaan antar model diuji secara statistik dengan uji yang sesuai (Wilcoxon untuk dua model, Friedman + post-hoc untuk lebih dari dua model, atau uji yang cocok dengan metrik NLP).
- **Sumber:** [R] [Demšar, JMLR 2006](https://www.jmlr.org/papers/v7/demsar06a.html); [R] [Dror et al., ACL 2018](https://aclanthology.org/P18-1128/)
- **Value:**
  - `M-07.stat_test` =
  - `M-07.stat_results` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### M-08 — Ablation & sumber peningkatan
- **Kriteria:** Jelaskan dari mana peningkatan berasal melalui ablation, error analysis, dan uji robustness.
- **Sumber:** [R] [Lipton & Steinhardt – Troubling Trends in ML Scholarship](https://arxiv.org/abs/1807.03341)
- **Value:**
  - `M-08.ablations` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### M-09 — Klaim efisiensi dengan beberapa indikator biaya + hardware
- **Kriteria:** Klaim "lightweight" atau "cepat" didukung lebih dari satu indikator biaya (jumlah parameter atau ukuran model, FLOPs, throughput/latency, memori). Hardware dan compute yang dipakai disebutkan.
- **Sumber:** [R] [Dehghani et al., ICLR 2022 – The Efficiency Misnomer](https://arxiv.org/abs/2110.12894); [R] [NeurIPS Checklist (3d)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist)
- **Value:**
  - `M-09.efficiency_metrics` =
  - `M-09.hardware` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### M-10 — Metrik evaluasi dijustifikasi
- **Kriteria:** Metrik evaluasi (misalnya macro-F1, agreement dengan teacher) dijelaskan dan dijustifikasi.
- **Sumber:** [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience)
- **Value:**
  - `M-10.metrics` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### M-11 — Limitations & threats to validity
- **Kriteria:** Ada pembahasan limitations dan threats to validity (validitas internal/eksternal, reliabilitas).
- **Sumber:** [R] [NeurIPS Checklist (1d)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist); [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience); [MK] [L160](../materi_kuliah/summary_all_presentation.txt#L160)
- **Value:**
  - `M-11.limitations` =
  - `M-11.threats_to_validity` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

---

## 4. Reproducibility (yang tertulis di naskah)

### R-01 — Ketersediaan kode, data & model
- **Kriteria:** Naskah menyebutkan di mana kode, data, model, dan instruksi reproduksi tersedia (URL atau DOI). IEEE Access memberi badge "Code Available" untuk repositori ber-DOI (misalnya Code Ocean).
- **Sumber:** [R] [IEEE Access – Reproducibility](https://ieeeaccess.ieee.org/authors/reproducibility/); [R] [NeurIPS Checklist (3a)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist)
- **Value:**
  - `R-01.code_url` =
  - `R-01.model_url` =
  - `R-01.data_url` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### R-02 — Lisensi aset yang dipakai
- **Kriteria:** Lisensi dataset dan model pihak ketiga (misalnya CC-News, model teacher, potion embeddings) disebutkan.
- **Sumber:** [R] [NeurIPS Checklist (4b)](https://neurips.cc/Conferences/2022/PaperInformation/PaperChecklist)
- **Value:**
  - `R-02.asset_licenses` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

---

## 5. Penulisan & format IEEE

### W-01 — Judul
- **Kriteria:** Judul spesifik, ringkas, dan deskriptif, tanpa kata "new"/"novel" dan tanpa simbol matematika.
- **Sumber:** [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)
- **Value:**
  - `W-01.title` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### W-02 — Abstrak
- **Kriteria:** Satu paragraf, maksimal 250 kata, berdiri sendiri, tanpa singkatan, referensi, footnote, atau persamaan.
- **Sumber:** [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)
- **Value:**
  - `W-02.abstract` =
  - `W-02.abstract_word_count` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### W-03 — Keywords
- **Kriteria:** 3–5 keywords, sebaiknya istilah baku dari IEEE Thesaurus.
- **Sumber:** [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/)
- **Value:**
  - `W-03.keywords` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### W-04 — Diskusi
- **Kriteria:** Diskusi menginterpretasikan temuan, membandingkannya dengan riset terdahulu, dan memposisikan penelitian. Hasil berbasis bukti dipisahkan dari spekulasi.
- **Sumber:** [MK] [L192](../materi_kuliah/summary_all_presentation.txt#L192); [R] [Lipton & Steinhardt](https://arxiv.org/abs/1807.03341); [R] [SIGSOFT – Data Science](https://www2.sigsoft.org/EmpiricalStandards/docs/standards?standard=DataScience)
- **Value:**
  - `W-04.discussion_points` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### W-05 — Kesimpulan
- **Kriteria:** Kesimpulan menyoroti implikasi dan future work tanpa melebih-lebihkan, dan didukung data.
- **Sumber:** [R] [IEEE Author Center – Structure your article](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/); [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/)
- **Value:**
  - `W-05.conclusion_points` =
  - `W-05.future_work` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### W-06 — Gambar & tabel mendukung teks
- **Kriteria:** Setiap gambar dan tabel dirujuk di teks dan mendukung argumen. Pembahasan topik komprehensif.
- **Sumber:** [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/)
- **Value:**
  - `W-06.figures_tables` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### W-07 — Bahasa Inggris standar & kejelasan
- **Kriteria:** Ditulis dalam bahasa Inggris standar dengan grammar benar ("Articles with poor grammar will be immediately rejected"). Matematika dipakai untuk memperjelas, dan istilah teknis dipakai dengan tepat. *Saat ini naskah masih berbahasa Indonesia.*
- **Sumber:** [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/); [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/); [R] [Lipton & Steinhardt](https://arxiv.org/abs/1807.03341)
- **Value:**
  - `W-07.paper_language` =
  - `W-07.proofreading` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### W-08 — Template IEEE & panjang naskah
- **Kriteria:** Memakai template IEEE (naskah yang tidak mengikuti guideline dikembalikan atau ditolak). Panjang di bawah 20 halaman untuk IEEE Access.
- **Sumber:** [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/)
- **Value:**
  - `W-08.template` =
  - `W-08.page_count` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

---

## 6. Etika & integritas (yang tertulis di naskah)

### E-01 — AI disclosure di Acknowledgments
- **Kriteria:** Penggunaan AI (teks, gambar, kode) diungkapkan di bagian Acknowledgments: nama tool, bagian yang memakai konten AI, dan tingkat penggunaannya. Penggunaan AI hanya untuk editing grammar tetap disarankan untuk diungkapkan.
- **Sumber:** [R] [IEEE – Guidelines for AI-Generated Text](https://open.ieee.org/author-guidelines-for-artificial-intelligence-ai-generated-text/); [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/)
- **Value:**
  - `E-01.ai_disclosure_text` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### E-02 — Similarity / plagiarisme
- **Kriteria:** Lolos cek similarity (Turnitin/iThenticate), dengan target dari kuliah < 25%. Semua kutipan, parafrase, dan tabel/gambar dari pihak lain disitasi. Semua naskah IEEE disaring sebelum masuk Xplore.
- **Sumber:** [MK] [L75](../materi_kuliah/summary_all_presentation.txt#L75); [R] [IEEE – Ethical Requirements](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/ethical-requirements/)
- **Value:**
  - `E-02.similarity_score` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### E-03 — Tidak ada fabrikasi/falsifikasi
- **Kriteria:** Setiap angka di naskah bisa ditelusuri ke hasil eksperimen asli (notebook, `_archive/jurnal_latex_v1/generated/`).
- **Sumber:** [MK] [L17](../materi_kuliah/summary_all_presentation.txt#L17)
- **Value:**
  - `E-03.number_source` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### E-04 — Authorship & identitas penulis
- **Kriteria:** Setiap penulis memenuhi kriteria authorship IEEE (kontribusi intelektual signifikan, ikut menulis/merevisi, menyetujui versi final). Afiliasi lengkap.
- **Sumber:** [R] [IEEE – Ethical Requirements](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/ethical-requirements/)
- **Value:**
  - `E-04.authors` =
  - `E-04.affiliations` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

---

## 7. Konsistensi internal naskah

### K-01 — Validitas & reliabilitas pengukuran
- **Kriteria:** Pengukuran benar-benar mengukur yang diklaim (validitas) dan konsisten bila diulang (reliabilitas). Contoh: benchmark CPU diulang dan kondisinya dikontrol, dan test set mewakili klaim multibahasa.
- **Sumber:** [MK] [L160](../materi_kuliah/summary_all_presentation.txt#L160), [L180](../materi_kuliah/summary_all_presentation.txt#L180)
- **Value:**
  - `K-01.benchmark_protocol` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### K-02 — Klaim kesimpulan didukung data
- **Kriteria:** Setiap klaim di kesimpulan dan abstrak punya tabel atau gambar pendukung di bagian hasil. Angka di abstrak, teks, dan tabel konsisten.
- **Sumber:** [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/) ("conclusions … supported by the data")
- **Value:**
  - `K-02.claim_evidence_map` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

---

## 8. Jurnal & submission (dicek nanti, di luar isi naskah)

### J-01 — Quartile jurnal target diverifikasi
- **Kriteria:** Quartile dicek per kategori subjek pada tahun terbaru. Quartile versi SJR (Scopus) dan JCR (WoS) bisa berbeda.
- **Sumber:** [S] [CASRAI – JIF & quartile](https://casrai.org/guides/journal-impact-factor-and-quartile-rankings); cek langsung di [scimagojr.com](https://www.scimagojr.com)
- **Value:**
  - `J-01.target_journal` =
  - `J-01.quartile` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### J-02 — Jurnal masih aktif terindeks Scopus
- **Kriteria:** Jurnal tidak ada di daftar *discontinued titles* Scopus.
- **Sumber:** [R] [Elsevier – Scopus content policy](https://www.elsevier.com/ja-jp/products/scopus/content/content-policy-and-selection)
- **Value:**
  - `J-02.scopus_status` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### J-03 — Bukan jurnal predator
- **Kriteria:** Jurnal lolos checklist Think.Check.Submit.
- **Sumber:** [R] [Think.Check.Submit (Taylor & Francis)](https://authorservices.taylorandfrancis.com/think-check-submit/)
- **Value:**
  - `J-03.tcs_result` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### J-04 — Topik masuk scope jurnal
- **Kriteria:** Topik paper sesuai dengan scope jurnal target.
- **Sumber:** [R] [IEEE Access Reviewer Guidelines](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/); [MK] [L134](../materi_kuliah/summary_all_presentation.txt#L134)
- **Value:**
  - `J-04.scope_fit` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### S-01 — Tidak submit ganda; preprint diungkapkan
- **Kriteria:** Naskah tidak sedang disubmit ke jurnal lain. Versi preprint atau konferensi diungkapkan beserta perbedaannya. Jika diunggah ke arXiv, cantumkan "This work has been submitted to the IEEE for possible publication."
- **Sumber:** [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/); [R] [IEEE – Submission & Peer Review Policies](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/)
- **Value:**
  - `S-01.preprint_status` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### S-02 — Cover letter
- **Kriteria:** Cover letter menjelaskan novelty, signifikansi, dan kecocokan dengan jurnal, serta menyatakan naskah tidak sedang direview di tempat lain. Tidak menyalin abstrak.
- **Sumber:** [R] [Elsevier Connect – "Dear Editor…"](https://www.elsevier.com/connect/dear-editor-we-enclose-our-paper-for-your-kind-consideration); [S] [CASRAI – cover letter](https://casrai.org/dictionary/term/cover-letter-for-journal-submission)
- **Value:**
  - `S-02.cover_letter_points` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### S-03 — Rilis artefak sebelum submit
- **Kriteria:** Kode, data, dan model sudah dirilis di repositori (sebaiknya ber-DOI) sesuai URL yang tertulis di naskah (lihat R-01).
- **Sumber:** [R] [IEEE Access – Reproducibility](https://ieeeaccess.ieee.org/authors/reproducibility/)
- **Value:**
  - `S-03.artifact_release` =
- **Status:** ⏳
- **Evidence:**
- **Tindakan:**

### S-04 — Respons reviewer saat resubmit
- **Kriteria:** Jika resubmit setelah reject, lampirkan daftar komentar reviewer, respons penulis, dan perubahan yang dilakukan.
- **Sumber:** [R] [IEEE Access Submission Guidelines](https://ieeeaccess.ieee.org/authors/submission-guidelines/)
- **Value:**
  - `S-04.response_letter` =
- **Status:** ⏳ (relevan hanya jika resubmit)
- **Evidence:**
- **Tindakan:**

---

## Catatan sumber

- Situs scimagojr.com menolak akses otomatis saat diverifikasi, jadi definisi quartile diambil dari CASRAI (sumber sekunder).
- Ambang similarity IEEE (sering disebut 30%) dan acceptance rate IEEE Access hanya ditemukan di sumber sekunder, sehingga tidak dijadikan kriteria.
- Materi kuliah ([summary_all_presentation.txt](../materi_kuliah/summary_all_presentation.txt)) adalah ringkasan AI dari slide kuliah.
