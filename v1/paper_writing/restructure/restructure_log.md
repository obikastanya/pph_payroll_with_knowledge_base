# Log Restrukturisasi Naskah StaticKD (1 November 2026)

- **Sumber:** `paper_final/main.tex` pada commit `b4bf5e6` (IEEEtran, 17 hlm; 18 hlm bila dipindah ke template IEEE Access).
- **Hasil:** `paper_final/main.tex` (kelas `ieeeaccess`, **15 hlm** termasuk referensi dan biografi) dan `paper_final/supplementary.tex` (6 hlm).
- **Cara membuat:** `paper_writing/restructure/assemble_restructure.py --force`. Skrip menyalin paragraf per rentang baris dari `b4bf5e6`. Setiap penggantian teks harus cocok tepat satu kali. Sejak commit restrukturisasi, `main.tex` diedit manual. Kompilasi cukup dengan `bash paper_writing/restructure/build.sh`.
- **Rancangan:** [rancangan_struktur.tex](rancangan_struktur.tex) (peta paragraf lama ke baru).

## 1. Perubahan struktur

| Baru | Isi (baris lama) |
|---|---|
| I. Introduction | L48–L60, L64–L70, peta naskah baru |
| II. Related Work | L74–L109. Subbab "Temperature and the Capacity Gap" (L81) dilebur ke II-B; judulnya dihapus, teks L82 utuh |
| III. The StaticKD Method | A. Study Overview (L114–L118, Fig. 1); B. Problem Formulation (L174–L175); C. Teacher (L243–L245); D. Student (L247–L262); E. Folding, Table Ensemble, and Compact Variant (L264–L269, L282) |
| IV. Data and Test Set | A. Data Sets and Their Roles (L120, Tabel datasets); B. Distillation Data (L177–L189); C. Unified Test Set (L191–L234); D. Validity of the Editorial Labels (L474–L482, dulu Hasil IV-B) |
| V. Experimental Setup | A. Baselines (L321–L325); B. Evaluation Protocol (L327–L331); C. Efficiency Protocol (L333–L337); D. Ablation Design (L341 bagian awal); E. Implementation Details (L341 bagian akhir) |
| VI. Results | A. Accuracy (RQ1) (L343–L407, kalimat sensitivitas dari L409); B. CPU Efficiency (RQ2) (L557–L592); C. Ablation (RQ3) (L484–L541); D. Language, Label, and Source (RQ4) (kalimat subkelompok L409, L411–L445, L624–L637); E. Calibration and Cascade (L646–L668) |
| VII. Discussion | A. What a Token Table Retains (L679, L681); B. Where the Accuracy Comes From (L683–L687); C. Weak Languages and Model Selection (L689–L693); D. Practical Implications (L695, L697); E. Limitations (L701–L715, dulu bab VI) |
| VIII. Conclusion dan sesudahnya | L717–L758 |

**Nomor RQ.** RQ2 dan RQ3 ditukar agar urutan Pendahuluan, Hasil, dan Pembahasan sama. RQ2 sekarang biaya CPU (dulu RQ3), dan RQ3 komponen resep (dulu RQ2). Isi pertanyaannya tidak berubah.

## 2. Pindah ke berkas suplemen (isi identik)

| Suplemen | Asal | Alasan |
|---|---|---|
| Algorithm S1 | Algorithm 1 (L271–L280) | Isinya sama dengan persamaan (3) dan teks III-D |
| Tabel S1 | Hyperparameter (L284–L319) | Detail reproduksi |
| Tabel S2 | Macro-F1 per sumber (L447–L465) | Angka yang dibahas tetap di teks VI-D |
| Tabel S3 | Faktor per bahasa (L603–L623) | Angka utama tetap di teks VI-D |
| Tabel S4 | Lisensi (L728–L752) | Detail rilis |
| Fig. S1 | Heatmap test set (L236–L241) | Ringkasan ada di Tabel komposisi |
| Fig. S2 | Latensi, RAM, ukuran (L594–L599) | Sama dengan Tabel efisiensi |
| Fig. S3 | Temperature (L543–L548) | Sama dengan Tabel ablasi |
| Fig. S4 | Ukuran ensemble (L550–L555) | Angka ada di teks VI-C |
| Fig. S5 | Subkelompok (L467–L472) | Sama dengan Tabel subkelompok |
| Fig. S6 | F1 per label dan confusion matrix (L639–L644) | Angka utama ada di teks VI-D |
| Fig. S7 | Reliability diagram (L670–L675) | ECE ada di teks VI-E |

Semua float dicek identik dengan versi lama. Fig. 1 hanya berganti cara kompilasi: TikZ-nya bentrok dengan `ieeeaccess.cls`, jadi dipindah ke `figures/fig_pipeline.tex` dan dimasukkan sebagai PDF.

## 3. Perubahan teks (lengkap)

**Rujukan ke suplemen** (11 kalimat). Bentuknya "Table~\ref{x}" atau "Fig.~\ref{x}" diganti "Table~Sn in/of the supplementary material" atau "Fig.~Sn in the supplementary material". Lokasinya: L211, L269, L282, L323, L409, L445, L539, L541, L581, L624, L635, L668, L679, L726.

**RQ:**
- L60: kalimat RQ2 (komponen) dan RQ3 (biaya) ditukar urutan dan nomornya.
- L484, L557: tag RQ di judul subbab disesuaikan.
- L683: "For RQ2, the ablations" menjadi "For RQ3, the ablations".
- L601: judul "Analysis by Language and Label (RQ4)" menjadi "Analysis by Language, Label, and Source (RQ4)", karena tabel per sumber kini ada di subbab ini.

**Peta naskah (L72) ditulis ulang** mengikuti bab baru:
> Section~\ref{sec:related} reviews related work. Section~\ref{sec:method} describes StaticKD, and Section~\ref{sec:data} describes the data and the test set. The baselines and the evaluation protocol are given in Section~\ref{sec:setup}. The results are presented in Section~\ref{sec:results} and discussed together with the limitations of the study in Section~\ref{sec:discussion}. Section~\ref{sec:conclusion} concludes the paper.

**Judul subbab baru:**
- Study Overview
- Folding, Table Ensemble, and Compact Variant
- Data Sets and Their Roles
- Ablation Design
- Implementation Details
- What a Token Table Retains
- Where the Accuracy Comes From
- Weak Languages and Model Selection
- Practical Implications
- Limitations (dulu judul bab)

**Front matter.** Disesuaikan dengan template IEEE Access: `\address`, `\corresp`, `\tfootnote` ("This work received no specific funding."), `\history`/`\doi` placeholder, dan biografi `\todo`.

## 4. Kalimat yang dihapus (isinya masih ada di tempat lain)

| ID | Teks lama | Isinya masih ada di |
|---|---|---|
| D1 | L62 (4 kalimat): "The answers to RQ2 and RQ4 show that the accuracy of StaticKD depends on how many languages and sites the teacher-labeled data cover and on whether the embeddings start from a space shared by all languages. Training the student on the top teacher label alone gives results as good as training it on the full teacher distribution. Fine-tuning the embeddings helps on the development set but hurts languages with little or no distillation data. A development set in the training languages cannot reveal this trade-off." | Abstrak, VII-B (L683–L687), VIII (L721) |
| D2 | L695: "For one million articles per day, the ONNX int8 teacher needs 15.1 cores, whereas StaticKD needs only 0.02 cores (Section~\ref{sec:res-eff})." | I (L52: 15.1), VI-B (L581: 15.1; L583: 0.02) |
| D3 | L697: "At $\theta=0.8$, the cascade accuracy of 0.703 is on par with that of the teacher alone (0.699). The cascade throughput is 1.92 articles per second per core compared with 0.77 for the teacher alone." | VI-E (L668) dan Tabel cascade |

## 5. Format

- Tabel lebar `tab:main`, `tab:sig`, `tab:eff`, `tab:ablation`, dan `tab:groups` memakai `\scriptsize` (sebelumnya `\footnotesize`).
- Fig. per bahasa dikecilkan dari 0.9 menjadi 0.8 `\textwidth`.

## 6. Verifikasi

- `verify_restructure.py`: semua kalimat lama ada di `main.tex` atau `supplementary.tex`. Pengecualiannya hanya kalimat di bagian 3 (rujukan dan RQ) dan bagian 4 (D1–D3).
- Pemeriksaan float per `\label`: 25 float identik dengan versi lama. Fig. 1 hanya berganti sumber gambar.
- `scripts/check_paper.py`: 0 error LaTeX, 0 rujukan atau sitasi yang tidak terdefinisi, 0 angka yang berubah dari notebook.
  - 20 kunci yang "tidak ditemukan" memang sudah tidak ada sejak sebelum restrukturisasi.
  - Penurunan jumlah kemunculan angka berasal dari D1–D3 atau dari angka di kode TikZ Fig. 1, yang kini ada di `figures/fig_pipeline.tex`.
- `scripts/check_style.py`: 0 temuan. Sebaran panjang kalimat setara dengan versi lama.

## 7. Belum tercapai: 14 halaman

Naskah 15 halaman, dan biografi masih *placeholder*. Biografi asli (±100 kata dan foto per penulis) menambah sekitar 0,3 halaman. Turun ke 14 halaman membutuhkan pemangkasan **isi** sekitar 1,2–1,5 halaman, dan itu di luar batas "tanpa mengubah makna". Rencana pemangkasannya, bersama tambahan isi dari review, ada di `rencana_perubahan.tex` (bagian anggaran halaman).
