# Ringkasan Penelitian: KBS Adaptif untuk Perhitungan PPh 21

Disusun 11 November 2026 dari:
- naskah `paper/final/` (IEEE Access, 8 Nov 2026);
- `docs/PRAREGISTRASI.md`, `docs/LOG_PENELITIAN.md` dan `docs/BAHAN_PAPER.md`;
- kode `system/` (sistem penelitian) dan `system_final/` (demo baru);
- isi `dataset/` dan log run di `experiments/`.

Bagian yang diberi tanda **Catatan** berisi temuan dari pemeriksaan kode dan data yang tidak tertulis, atau tidak tertulis lengkap, di naskah.

---

## 1. Judul

**Judul saat ini** (`paper/final/main.tex:75`, sama dengan `system_final/README.md`):
> An Adaptive Knowledge-Based System for PPh 21 Calculation with LLM-Assisted Knowledge Acquisition from Regulations and Company Policies

Versi Indonesia (draf v1–v8, dipakai sejak 27 Okt 2026):
> *Knowledge-Based System* Adaptif untuk Perhitungan PPh 21 dengan Akuisisi Pengetahuan Berbantuan LLM dari Regulasi dan Kebijakan Perusahaan

Penulis: Obi Kastanya dan Mahathir Muhammad (ITS).

**Judul sebelumnya:**
- Proposal (29 Sep 2026): "Sistem Perhitungan PPh Pasal 21 Berbasis Knowledge Base yang Dapat Disesuaikan dengan Kebijakan Penggajian Perusahaan Tanpa Mengubah Kode Program".
- Sebelum revisi 27 Okt: "*Knowledge Base* Dua Lapis Berversi Waktu untuk Perhitungan PPh Pasal 21 …". Judul ini diganti karena masukan dosen bahwa KB saja belum cukup (`feedback_and_revision/revision_27_10_26.md`).

---

## 2. Latar Belakang

**Masalah.**
- Aturan PPh 21 pegawai tetap berubah 13 kali pada 2023–2026. Tujuh perubahan terjadi pada 2025, dan lima di antaranya berlaku surut. Contohnya, PMK 10/2025 terbit 4 Feb 2025 tetapi berlaku sejak Januari (`introduction.tex`).
- Kalkulator payroll umumnya menanam aturan di kode. Dua kalkulator open-source butuh 26 dan 915 hari untuk menambahkan TER, dengan perubahan 163 dan 504 baris kode.
- Perusahaan juga punya kebijakan sendiri di atas regulasi: PKB, tunjangan, dan pajak ditanggung perusahaan (gross-up). Kebijakan ini bisa terdampak setiap kali regulasi berubah.

**Kenapa KBS dan LLM.**
- *Knowledge-based system* (KBS) memisahkan aturan dari kode. Bebannya pindah ke pekerjaan menjaga KB tetap mutakhir.
- LLM bisa membantu menyusun aturan dari teks hukum, tetapi tidak andal untuk menghitung pajak secara langsung.
- Gagasannya: LLM hanya membuat draf pembaruan KB. Perhitungan tetap dikerjakan mesin inferensi yang deterministik.

**Celah (gap).**
- Penelitian LLM dan pajak sebelumnya memformalkan hukum pada satu titik waktu.
- Penelitian terdekat (Gogani-Khiabani dkk.) hanya melakukan satu pembaruan, 2020→2021, dengan *majority voting*.
- Belum ada yang mengukur tiga hal berikut:
  1. apakah pembaruan berulang hasil draf LLM tetap menjaga hasil periode sebelumnya;
  2. apakah kesalahan satu pembaruan menjalar ke pembaruan berikutnya;
  3. bagaimana pembaruan regulasi memengaruhi lapisan kebijakan perusahaan.

**Pendekatan terdahulu yang dirujuk:** Catala, Mlang, DataLex, Logical English, Ripple-Down Rules, Veeramani dkk. (KG dan aturan simbolik untuk pajak India), Yadamsuren, Lorenzo, Jurayj, Prior dkk. (konsolidasi rantai amandemen), KoLEG, serta sistem PPh 21 prosedural di Indonesia (`related.tex`).

---

## 3. Novelty

**Yang diklaim** (`introduction.tex:16`, `related.tex:25`):
- Pembaruan berulang yang didrafkan LLM pada KB hukum yang dapat dieksekusi.
- Pengukuran apakah hasil periode sebelumnya terjaga, dan apakah kesalahan menjalar.
- Dampak pembaruan regulasi terhadap kebijakan perusahaan yang berlapis di atasnya.
- Tidak ada penelitian di tabel posisi yang melakukan ketiganya sekaligus.

Revisi 27 Okt secara eksplisit menyatakan bahwa hal-hal berikut **bukan** novelty: draf LLM ditambah mesin deterministik, KG untuk hukum pajak, *versioning* temporal, dan KB untuk PPh 21. Representasi bitemporal tetap dicantumkan sebagai kontribusi 1 (lihat bagian 4).

**Catatan: seberapa kuat bukti untuk tiap klaim**

| Klaim | Bukti di kode dan eksperimen | Kekuatan |
|---|---|---|
| Pembaruan berulang dan penjalaran kesalahan | Protokol ada dan dijalankan (`system/tools/run_chain.py`). Setiap rantai hanya dijalankan sekali (R=1). Rantai yang sesuai Definisi 3 (*regenerated*) ditambahkan lewat amandemen setelah hasil keluar. Semua draf berasal dari input yang dipotong (lihat 6.4). | Protokol valid, temuan lemah dan bercampur faktor lain |
| Dampak ke lapisan kebijakan | Detektor E4 dinilai memakai pembaruan *emas*, bukan keluaran pipeline. 27 dari 33 pasangan positif berasal dari kebijakan sintetis. Detektor tidak lebih baik daripada baseline "tandai semua kebijakan yang menyentuh fakta yang berubah" (H4b tidak diterima). Pipeline abstain di kelima PKB asli. | Lemah |
| Representasi dua lapis bitemporal | E1: 16/16 perubahan baru bisa diekspresikan tanpa mengubah mesin, tetapi hanya setelah konvensi pembulatan contoh diseragamkan (tanpa itu 8/16). Ke-16 perubahan ditulis oleh agen AI, bukan pakar. | Didukung, dengan syarat |
| Gate dan konsensus | Ablasi menunjukkan gate tidak mengubah hasil apa pun. Konsensus hanya menurunkan *silent error* sebagai estimasi titik (McNemar satu sisi p=0,0625) dan tidak menambah pembaruan yang benar. | Lemah |

---

## 4. Kontribusi

Kontribusi seperti yang tertulis di `introduction.tex:20-26`, beserta statusnya:

1. **Representasi.** Knowledge graph RDF dua lapis bitemporal (regulasi dan kebijakan perusahaan) dengan aturan yang dapat dieksekusi, resolusi konflik antarlapis, dan jejak ke pasal sumber. Representasi ini bisa mengekspresikan 16 perubahan yang belum pernah dilihat tanpa mengubah mesin, setelah konvensi pembulatan diseragamkan.
2. **Pipeline akuisisi inkremental.** LLM membuat draf pembaruan beserta kutipan pasal, gate deterministik dan konsensus perilaku menyaringnya, lalu reviewer menerima laporan dampak. Naskah sendiri menyatakan bahwa keunggulannya atas draf tunggal berasal dari konsensus dan abstain, bukan dari gate.
3. **Protokol *regulation replay*.** Mode terisolasi dan berantai, yang memisahkan kesalahan warisan, kesalahan baru, dan kesalahan yang terpicu.
4. **Evaluasi dan artefak.** Evaluasi pada 13 peristiwa regulasi dan 5 PKB yang menunjukkan jenis perubahan mana yang bisa dipercaya, beserta artefak yang dirilis.

**Catatan.**
- Kontribusi 2 dan 4 diukur pada input dokumen yang dipotong (bagian 6.4). Angka absolutnya kemungkinan meremehkan kemampuan pipeline, terutama untuk dokumen panjang dan PKB.
- KB emas dan semua "pembaca kedua" adalah agen AI. Belum ada pakar pajak manusia yang memeriksa.

---

## 5. Dataset

### 5.1 Gambaran peran data

| Peran | Isi |
|---|---|
| **Pengembangan** | 13 regulasi 2012–2022 (D01–D13), 5 regulasi fiktif (FR01–FR05), PKB TPK Koja, kasus pengembangan di `14_ruang_uji/pengembangan` |
| **Uji** | 13 peristiwa regulasi asli (E01–E13), 20 pengecoh (P01–P21), 5 PKB asli, 14 kebijakan sintetis (SP01–SP14), 4 kontrafaktual, 16 perubahan *unseen* (E1) |
| **Kebenaran acuan** | KB emas dan delta emas (`12_emas`), GT1 contoh resmi, GT2 kalkulator DJP, GT3 50 perhitungan independen, GT5 contoh kebijakan PKB, harapan ruang uji (`14_ruang_uji/harapan`) |
| **Pendukung** | tabel parameter, data upah BPS dan UMP, kasus sintetis, studi kasus Perusahaan X, implementasi pembanding |

Teks semua dokumen diekstrak sekali lalu dikunci di `dataset/13_teks/<dok>/` (`teks.txt`, `segmen.json`, `MANIFEST.sha256`). Teks inilah yang menjadi input LLM.

### 5.2 Ringkasan per folder

| Folder | Fungsi | Isi | Ukuran | Asal | Dipakai oleh |
|---|---|---|---|---|---|
| `01_regulasi` | Korpus regulasi dan tabel parameter | 69 PDF (4.129 hlm.), 16 CSV, OCR, 1 HTML | 247 MB | Resmi: JDIH BPK, JDIH Kemenkeu, pajak.go.id. Surat batas upah JP lewat mirror pihak ketiga. | `13_teks` → KB emas, E2/E3; GT3; generator |
| `02_studi_kasus` | Studi kasus Perusahaan X (baseline B0) | 1 pegawai dummy, 39 variabel × 12 bulan, kebijakan YAML | 24 KB | Spreadsheet kantor (`payroll_calculator.xlsx`); sheet berisi data pribadi tidak dibaca | Prototipe lama (`eksperimen/e8`) |
| `03_pembanding` | Implementasi pihak ketiga (GT4, baseline B1) | 7 repo (gitignored); CSV 35/22/15/10 baris | 147 MB | Clone GitHub, Packagist, npm | `system/tools/b1_maintenance.py` |
| `04_data_publik` | Kalibrasi upah, UMP, PTKP | 65 berkas: tabel Sakernas BPS, UMP Kemnaker 2018–2026, Satu Data, Kaggle, Zenodo | 64 MB | Publik; atribusi BPS | `testspace.py` (kasus operasional S^E), `08_pegawai_sintetis` |
| `05_katalog_kebijakan` | Katalog variasi kebijakan | 20 kebijakan (KP-01..KP-20) | 3 KB | Disusun manual | Prototipe lama (E7) |
| `06_kasus_uji_sintetis` | Profil sintetis S1–S8 | 2.600 rekaman, 21 field | 1,7 MB | Script, `--seed 42`; hanya input, tanpa nilai harapan | `eksperimen/v2`, sumber `11_acuan/b2_kasus` |
| `07_kasus_uji_resmi` | GT1: contoh hitung resmi | 46 kasus dalam lingkup (32 pengembangan / 14 holdout), 4 di luar lingkup ditranskripsi penuh, 38 entri singkat | 0,75 MB | Transkripsi manual dari PDF regulasi | `refs.py`, E0 holdout, tes |
| `08_pegawai_sintetis` | Pegawai demo | 8 pegawai | 38 KB | Script; gaji dari UMP/BPS | Prototipe lama, UI lama |
| `09_korpus_peristiwa` | Korpus peristiwa perubahan | 46 peristiwa, 5 regulasi fiktif, 21 spesifikasi kontrafaktual (4 dibuat), cutoff model | 176 KB | Tanggal dari PDF dan JDIH asli; FR ditulis Claude | `corpus.py` → E2–E4 |
| `10_kebijakan_perusahaan` | PKB asli, klausul, kebijakan sintetis | 6 PKB, 201 klausul, 14 kebijakan sintetis, 168 label dampak | 9,7 MB | PKB publik (gitignored); SP ditulis Claude | `gold_src`, `rq4_labels.py`, E2/E4 |
| `11_acuan` | GT2, GT3, GT5, uji diferensial | GT2 20+15 kasus, GT3 50, GT5 21, diferensial 743 baris, `b2_kasus` 100 | 4,4 MB | GT2 dari kalkulator DJP (manual); GT3 dihitung script Claude | `refs.py`, `check_refs.py` (E0) |
| `12_emas` | KB emas K* dan delta emas Δ* | 64 delta + 4 kontrafaktual; rantai 37 pembaruan, sisi 27; `kb.trig` 282 rekaman | 3,2 MB | Ditulis manual di `system/gold_src/` (dibantu AI), dikompilasi `build_gold.py`, tag `emas-v1` | Hampir semua tool `system/` |
| `13_teks` | Teks dokumen terkunci | 96 dokumen, sekitar 8,36 juta karakter | 17,9 MB | Diturunkan dari folder 01 dan 10 | Pipeline akuisisi (input LLM), KB emas |
| `13_teks_pengecoh_ringkas` | Pengecoh yang diringkas | 20 dokumen (3,09 juta → 150 ribu karakter) | 168 KB | Script dengan `system_final/pph21kbs/documents.py` | Belum dipakai (untracked) |
| `14_ruang_uji` | Ruang uji S^E dan nilai harapan | 2.398 kasus, 2.760 kasus kebijakan, 21 kasus mutasi terarah, 1.383 kasus pengembangan; 74.987 observasi harapan | 20 MB | `build_se.py`; harapan dari rantai emas | `score_run.py` (E2/E3), mutasi, E5 |

Di luar `dataset/`: set perubahan *unseen* (D07) ada di `review/unseen_changes/sealed/`. Isinya 16 perubahan dan 100 contoh, ditulis oleh agen terpisah dan disegel dengan hash.

### 5.3 Rincian data inti

**Korpus regulasi (`01_regulasi`).**
- Regulasi utama (37 PDF di root): UU 7/2021 HPP, UU 36/2008, PMK 101/2016 (PTKP), PER-16/PJ/2016 (hasil scan, di-OCR sendiri), PP 58/2023 (TER), PMK 168/2023, PMK 66/2023 (natura), PP 55/2022, PMK 10/2025, PMK 72/2025, PMK 105/2025, PMK 6/2026, PMK 28/2024, PMK 81/2024, PER-2/PJ/2024, PER-11/PJ/2025, PP 20/2026, regulasi BPJS, dan surat batas upah JP 2023–2026.
- `pengecoh/`: 12 PDF. `pengembangan/`: 13 PDF peristiwa 2012–2022. `pendukung/`: 7 PDF ketenagakerjaan.
- `tables/`: TER bulanan (125 baris), TER harian, tarif Pasal 17, PTKP, biaya jabatan, BPJS, pembulatan, KLU DTP (269).
- Mutu: tabel diekstrak dua kali secara independen (512 sel, 0 beda nilai). Teks OCR PER-16 perlu dicek angkanya terhadap PDF.

**Korpus peristiwa (`09_korpus_peristiwa/peristiwa.csv`, 46 baris).**
- **Uji, E01–E13 (13, semua relevan):** empat batas upah JP, PMK 66/2023, PP 58/2023, PMK 168/2023, PMK 10/72/105 tahun 2025, PP 7/2025 dan PP 36/2025, serta PER-11/PJ/2025 (pembulatan). Lima di antaranya berlaku surut.
- **Pengecoh, P01–P21 (20):** dokumen yang tampak terkait tetapi tidak mengubah PPh 21.
- **Pengembangan, D01–D13 (13):** tiga di antaranya tidak relevan.
- Setiap baris mencatat tanggal ditetapkan, diundangkan, terbit, berlaku, flag surut, jenis perubahan (T1–T10, X1–X5) dan halaman bukti.
- Tidak ada peristiwa uji yang terbit setelah cutoff kedua model: Claude Opus 5.5 (cutoff 2026-06) dan GPT-6.1 Sol (cutoff 2026-04-30). Artinya model mungkin sudah pernah melihat regulasi uji; ini dicatat di `contamination.py`.

**Kebijakan perusahaan (`10_kebijakan_perusahaan`).**
- **PKB asli:** WIKA 2025–26 (130 hlm.) dan AVCO 2024–26 (209 hlm.) sebagai PDF; Century Textile, Taekwang, Sansan dan TPK Koja sebagai halaman WageIndicator. Koja dipakai untuk pengembangan, lima lainnya untuk uji.
- **201 klausul diekstrak:** WIKA 43, AVCO 44, Century 34, Taekwang 34, Sansan 24, Koja 22. Semua kutipan dicocokkan otomatis dengan teks. Reviewer memeriksa 105 klausul dan mengoreksi 61 baris.
- **14 kebijakan sintetis (SP01–SP14):** ditulis Claude. Isinya 13 konflik, 3 kontrol negatif, 38 contoh hitung, dan 168 label dampak (46 "ya").

**Kebenaran acuan.**
- **GT1 (`07_kasus_uji_resmi`):** 46 contoh hitung resmi dari PER-16 (22), PMK 168 (13), PP 58 (1), PMK 10 (4), PMK 72 (3) dan PMK 105 (3).
  - Dibagi 32 pengembangan / 14 holdout, disegel 27 Okt dengan `random.Random(20261027)` dan SHA-256.
  - Ke-46 contoh sudah pernah dipakai pada prototipe lama, jadi holdout hanya bersih untuk sistem baru.
  - Ada 13 dugaan erratum di contoh resmi yang dibiarkan seperti aslinya.
- **GT2 (`11_acuan/gt2_kalkulator_djp`):** hasil kalkulator DJP yang dicatat manual. Kasus bulanan: 15 dari 20 sama persis, 5 selisih Rp1 karena DJP memotong desimal. Kasus akhir tahun: 90 dari 90 nilai cocok dengan GT3.
- **GT3:** 50 kasus (30 bulanan, 20 tahunan; gross, gross-up, ditanggung perusahaan), dihitung oleh script Claude dari teks regulasi, terpisah dari mesin. Reviewer mengoreksi 10 kasus.
- **GT5:** 21 contoh kebijakan dari 5 PKB.
- **KB emas (`12_emas`):** RDF/OWL dengan ELI, OWL-Time dan PROV-O, divalidasi SHACL (14 shape, 12 constraint SPARQL). Satu named graph per pembaruan.
  - Kesepakatan dengan agen pembaca kedua (`docs/hasil/kesepakatan_emas.json`):
    - regulasi: α keberadaan −0,09 (kesepakatan mentah 82%), α valid_from 0,61, kesepakatan nilai 90%;
    - kebijakan: α 0,46 (91%), κ kode konflik 0,73, kesepakatan nilai 100%.
  - Dokumen interpretasi tertulis: 18.
- **Ruang uji S^E (`14_ruang_uji`):** 2.398 kasus 2023–2026:
  - 1.200 operasional (upah ditarik dari tabel BPS provinsi × sektor);
  - 963 batas TER;
  - 175 kombinatorial (cakupan 2-arah 1,0);
  - 60 batas Pasal 17.

  Ditambah 2.760 kasus kebijakan dan 74.987 observasi harapan dari rantai emas. Status PTKP diambil seragam, dan ini dicatat sebagai asumsi.

### 5.4 Catatan dataset

- **Tidak ada pakar manusia.** Semua pemeriksaan "pembaca kedua" (korpus, klausul, KB emas, GT) dilakukan agen AI terpisah. `system_final/README.md` juga menyatakannya.
- **Data sintetis buatan LLM ikut menjadi data uji:** SP01–SP14, FR01–FR05 (khusus pengembangan), dan 16 perubahan *unseen*.
- **Kontrafaktual:** dari 21 spesifikasi, hanya 4 yang dibuat. Ini keputusan anggaran.
- **Kasus E5 tidak memakai `11_acuan/b2_kasus`.** E5 memakai 100 kasus operasional S^E tahun 2025, bukan 100 rekaman yang disiapkan di folder itu.
- **Dokumentasi tertinggal dari data:**
  - `dataset/README.md` tidak mencantumkan folder 12, 13, 13-ringkas dan 14.
  - `RENCANA_DATASET.md` §4 masih menandai D17 (emas) dan D21 (ruang uji) "belum", padahal keduanya sudah ada.
  - Angka diferensial GT3 di rencana (683/743 sama) adalah hasil sebelum koreksi; CSV saat ini 569 sama / 174 beda, dan semua beda sudah diadjudikasi.
- **Teks PKB asli dan repo pembanding di-gitignore** karena hak cipta, sehingga tidak ikut tersimpan di git.

---

## 6. Alur Metode Penelitian

### 6.1 Kerangka formal
- **Kondisi adaptivitas** (`formulation.tex`):
  - A1: mesin tidak diubah;
  - A2: hasil sama dengan emas untuk periode sejak tanggal berlaku, dan untuk tanggal pengetahuan sejak tanggal terbit;
  - A3_t: periode sebelumnya tidak berubah;
  - A3_ω: tanggal pengetahuan sebelumnya tidak berubah;
  - A4: laporan konflik sama dengan emas.
- **Adaptivitas operasional** mensyaratkan A2, A3_t dan A4 terpenuhi di semua kasus uji.

### 6.2 Representasi dan mesin inferensi
- **KB:** knowledge graph RDF dua lapis (regulasi dan kebijakan perusahaan) yang bitemporal, yaitu berdasarkan tanggal berlaku dan tanggal pengetahuan. Satu named graph per pembaruan, dengan jejak ke pasal.
- **Mesin** (`system/pph21kbs/engine/evaluator.py`; di demo baru `system_final/pph21kbs/engine.py`):
  - menyaring aturan menurut masa berlaku dan tanggal pengetahuan;
  - menyelesaikan konflik dengan urutan *lex superior* > aturan perusahaan > opsional > default, lalu *override* eksplisit, lalu *lex posterior*;
  - aritmetika eksak; gross-up dihitung sebagai *least fixed point*; masa pajak terakhir menghitung ulang setahun.
- Folder `engine/` di root adalah mesin YAML generasi pertama (prototipe 1–13 Okt). Mesin ini hanya dipakai untuk uji kesetaraan.

### 6.3 Pembangunan KB emas
- Disusun penulis dengan bantuan asisten AI di `system/gold_src/`, lalu dikompilasi ke `12_emas`.
- Divalidasi terhadap GT1, GT2, GT3 dan GT5 dengan adjudikasi.
- Dibekukan di tag `emas-v1`, dengan satu koreksi terdokumentasi pada 29 Okt.

### 6.4 Pipeline akuisisi berbantuan LLM (`system/pph21kbs/pipeline/`)
1. **Teks:** teks dokumen yang terkunci dipecah per pasal, lalu **dipangkas ke anggaran token** (rincian di bawah).
2. **Relevansi:** satu panggilan LLM menentukan apakah dokumen relevan, dan wajib mengutip dokumen.
3. **Draf:** m draf independen dalam JSON (m=3 untuk regulasi, m=2 untuk PKB), dengan konteks hingga 220 rekaman KB.
4. **Gate deterministik:**
   - G1: skema dan SHACL;
   - G2: kutipan verbatim, dan angka serta tanggal muncul di kutipan;
   - G3: cek statis;
   - G4: regresi pada maksimal 300 kasus;
   - G5: setiap elemen berpengaruh.
5. **Satu ronde perbaikan** untuk draf yang gagal gate.
6. **Konsensus perilaku:** kelompok draf yang hasilnya sama dan terbesar menang; jika seri, abstain.
7. **Detektor dampak statis** ke kebijakan perusahaan, lalu diteruskan ke reviewer.

**Catatan: pemotongan dokumen (step 1).**
- **Letak kode:** `system/pph21kbs/pipeline/select.py`, dengan `TOKEN_BUDGET = 14000` dan `ALWAYS_CAP = 3000` (token diperkirakan sebagai karakter ÷ 3,5). Fungsi `select()` melakukan tiga hal:
  - bagian pembuka dan penutup yang lebih dari 3.000 token dipotong pada 10.500 karakter, dengan penanda "[... truncated]";
  - lampiran yang tabelnya sudah diekstrak diganti dengan deskripsi berisi 6 baris pertama saja;
  - pasal dimasukkan berdasarkan kepadatan kata kunci sampai 14.000 token, dan sisanya **dibuang**. Model hanya diberi tahu "[segments not shown: …]".
- Pilihan segmen ini dipakai untuk panggilan relevansi maupun draf.
- **Baseline B2 dan ablasi AB1** memakai batas yang lebih kecil lagi, yaitu 4.000 token per dokumen.
- Anggaran LLM penelitian total USD 15 menurut praregistrasi. Biaya aktual: sekitar USD 81,6 untuk Claude dan USD 8,1 untuk model kedua.
- **Dampak yang tercatat di log run** (`experiments/*/results/*.json`, field `selection`):

| Dokumen | Teks penuh (token) | Terkirim | Bagian yang dibuang | Hasil |
|---|---|---|---|---|
| E02 PMK 66/2023 | 30.826 | 12.766 | Lampiran 1 (18.060 token; tabel batas pembebasan natura) | *silent error* (run 1), abstain (run 2) |
| E04 PMK 168/2023 | 46.310 | 13.999 | 10 segmen; penutup dipotong 6.746→3.000 | abstain (kedua run) |
| E13 PER-11/PJ/2025 | 78.960 | 13.995 | 126 dari 149 segmen | benar |
| PKB AVCO | 103.339 | 14.000 | 231 segmen | abstain |
| PKB Centex | 21.767 | 13.988 | 29 segmen | abstain |
| PKB Sansan | 40.967 | 13.968 | 75 segmen | abstain |
| PKB Taekwang | 43.304 | 13.970 | 69 segmen | abstain |
| PKB WIKA | 52.587 | 13.997 | 171 segmen; pembuka dipotong 7.317→3.000 | abstain |

  E01, E03 dan E05–E12 tidak kehilangan segmen. Di E03, E06, E10 dan E11, lampirannya diganti deskripsi tabel 6 baris.
- **E02:** isi Lampiran 1 yang dibuang (batas hadiah Rp3.000.000/tahun, fasilitas olahraga Rp1.500.000, rumah Rp2.000.000/bulan, dan kriteria kendaraan) persis bagian yang menurut naskah "terlewat" oleh pembaruan. Naskah menggolongkannya sebagai kegagalan konten, bukan input yang hilang (`discussion.tex:11`).
- **Spesifikasi menjanjikan kategori yang tidak muncul.** `docs/spesifikasi/akuisisi.md` §3.1 menjanjikan bahwa pembaruan yang terlewat karena pasalnya tidak terpilih dilaporkan sebagai jenis kesalahan tersendiri. Kategori itu tidak ada di naskah, dan pemangkasan hanya disebut sekilas (`system.tex:100`) tanpa angka dan tanpa dimasukkan ke ancaman validitas.

### 6.5 Eksperimen

| Eksperimen | Menguji | Run utama di `experiments/` |
|---|---|---|
| **E0** Validitas instrumen | KB emas terhadap GT1–GT3 dan GT5; skor mutasi | `e0_holdout.py`, `mutation_score.py` |
| **E1** Ekspresivitas (RQ1) | 16 perubahan *unseen* bisa diekspresikan tanpa mengubah mesin | `review/unseen_changes/hasil_E1/` |
| **E2** Akuisisi terisolasi (RQ2) | Satu pembaruan per dokumen dari K* yang benar | `e2-regulasi`, `e2-pkb`, `e2-pengecoh`, `e2-regulasi-ulang`, `*-m5`, `e2-model2-*`, `e2-kontrafaktual`, `e2-sintetis` |
| **E3** *Regulation replay* berantai (RQ3) | Pembaruan berurutan; kesalahan warisan, baru, terpicu | `e3-tetap`, `e3-sempurna`, `e3-bangkit-ulang`, `e3-interim-n24` |
| **E4** Deteksi dampak (RQ4) | Kebijakan mana yang terdampak suatu peristiwa (pakai pembaruan emas) | `rq4_labels.py` |
| **E5** Perbandingan | B1 biaya pemeliharaan kalkulator open-source; B2 LLM menghitung pajak langsung | `b1_maintenance.py`, `e5-b2` |

**Baseline:**
- B1: riwayat commit kalkulator open-source;
- B2: LLM menghitung langsung;
- B3: draf pertama yang lolos G1–G2;
- B4: *majority vote* tanpa gate;
- B5(i): tandai semua kebijakan yang menyentuh fakta yang berubah;
- B5(ii): pemindaian teks biasa.

**Ablasi:** AB1 (formalisasi dari nol), AB2 (tanpa konteks KB), AB3 (tanpa G5), AB4, AB5.

Run `devsub*` dan `dev-sub-v1-*` (8–9 Nov) adalah pengembangan v2 yang dijawab subagent Claude Code tanpa API, dan dinyatakan bukan hasil uji (`docs/hasil/pengembangan_v2.md`). Run `app-*` adalah run demo.

### 6.6 Perbedaan `system_final` (demo baru) dengan `system`
Perubahan "v2" (`system_final/README.md:253-258`):
- atribut data kasus ditunjukkan ke model, dengan gate input baru G6;
- temuan tanggal dan "tanpa efek" dari G5 diturunkan menjadi peringatan;
- panduan pemodelan dan checklist kebijakan ditambahkan di prompt;
- konsensus membandingkan konflik per fakta, bukan per id aturan.

**Catatan.**
- **`system_final` masih memotong dokumen persis seperti sistem lama.**
  - `system_final/pph21kbs/documents.py:294-295` memakai `TOKEN_BUDGET = 14000` dan `ALWAYS_CAP = 3000`, dengan `select()` yang logikanya identik. Fungsi ini dipanggil oleh `pipeline.py:334` dan `app/workflow.py:170`.
  - README-nya sendiri menulis "segments are chosen within a 14,000-token budget".
  - Commit terakhir (bd2135c, "teks dokumen penuh") hanya *menampilkan* teks penuh di UI, tidak mengirimkannya ke model.
- **v2 belum dievaluasi pada dokumen uji dengan API.** Klaim "silent error 5→1" berasal dari run subagent pada 7 kebijakan sintetis (SP01–03, SP08–11). Padahal kebijakan-kebijakan itu tercatat sebagai data **uji** di praregistrasi.

---

## 7. Metrik Evaluasi

### 7.1 Definisi
- **Pembaruan benar:** setiap nilai keluaran setiap kasus uji sama dengan KB emas sampai ke rupiah, pada kedua tanggal pengetahuan, dan laporan konfliknya sama. Satu nilai berbeda berarti salah (`design.tex:53`; kode `system/pph21kbs/analysis/evaluate.py`). Pembaruan kosong pada dokumen relevan dihitung *silent error*.
- **SER** (*silent error rate*) dan **CAR** (*correct acceptance rate*): proporsi dokumen nyata (18 = 13 regulasi + 5 PKB) dengan *silent error*, dan proporsi dengan pembaruan benar.
- **ABS** = 1 − SER − CAR (abstain).
- **Risiko selektif** = SER / (SER + CAR). Kode: `system/tools/score_run.py`.
- **pass@1, pass@m, 1@m:** dihitung pada draf sebelum seleksi, dengan rumus unbiased 1 − C(m−c, j)/C(m, j). **η** adalah efisiensi seleksi (`stats.py`).
- **RA** (*representational adequacy*): proporsi perubahan *unseen* yang pembaruannya mereproduksi semua contoh tanpa mengubah mesin.
- **OAR:** proporsi peristiwa dalam rantai yang tidak menambah kasus salah baru.
  - Kesalahan baru = kasus salah dikurangi kasus yang sudah salah sebelum peristiwa itu.
  - Kesalahan terpicu = kasus salah dikurangi (kesalahan mode terisolasi ∪ kesalahan warisan).
  - Batas noise = selisih simetris kesalahan antara dua run terisolasi (`run_chain.py`).
- **Recall, presisi, F2** atas pasangan kebijakan–peristiwa, dengan F_β = (1+β²)PR/(β²P+R) dan bootstrap per peristiwa (`stats.py`, `rq4_labels.py`).
- **Skor mutasi** pada mutan non-ekuivalen (ambang 0,80); **kesepakatan** dengan Krippendorff α dan Cohen κ.
- **E5:** hari dan baris kode untuk mengadopsi TER (B1); kecocokan persis perhitungan LLM langsung (B2).
- **Statistik:** Clopper–Pearson; McNemar eksak dengan koreksi Holm; CI berpasangan Newcombe untuk non-inferioritas (margin 0,10); bootstrap per klaster.
- **Metrik eksploratif** yang ditambahkan setelah hasil keluar: pita materialitas, jumlah pegawai terdampak, presisi dan recall per elemen, durasi panggilan.

### 7.2 Hipotesis praregistrasi dan hasilnya
Praregistrasi: commit c5983ff, dengan amandemen 2df0727. Hasil diambil dari `paper/final/sections/results.tex`.

| Hipotesis | Ambang | Hasil | Status |
|---|---|---|---|
| H1 (RQ1) | batas bawah RA ≥ 0,70 | 16/16 (batas bawah 0,829); 15/16 pada percobaan pertama; 8/16 tanpa penyeragaman pembulatan | Diterima, dengan syarat pembulatan |
| H2a (RQ2) | batas atas SER ≤ 0,25 | SER 3/18 (E02, E07, E11), batas atas 0,377 | Tidak diterima |
| H2b (RQ2) | CAR > B3 dan B4; SER non-inferior (margin 0,10) | CAR 8/18 vs 8/18 (B3) dan 9/18 (B4); Holm p=1; SER non-inferior hanya terhadap B3 | Tidak diterima / sebagian |
| H3a (RQ3) | batas bawah OAR ≥ 0,75 | rantai *transplanted* 31/33 (0,821, sebagian besar karena *masking*); rantai *regenerated* 23/33 (0,540) | Diterima di analisis terdaftar, tidak robust |
| H3b (RQ3) | kesalahan terpicu dalam batas noise | 29 kasus terpicu vs batas noise 0 | Tidak didukung |
| H4a (RQ4) | batas bawah recall ≥ 0,70 | recall 0,91 (CI 0,75–1,00) | Diterima |
| H4b (RQ4) | F2 > B5(i) dan B5(ii) | +0,193 vs B5(ii); −0,006 vs B5(i) | Tidak diterima |

Hasil lain:
- **E0:** GT3 50/50; holdout GT1 8/10 kasus (232/235 observasi) setelah satu koreksi emas; skor mutasi 1,00.
- **E5:** B2 tepat di 76 dari 100 kasus, dan dalam selisih Rp1 di 97 kasus.
- **PKB:** pipeline abstain di kelima PKB uji.

### 7.3 Catatan: hasil yang terpengaruh pemotongan dokumen

| Terpengaruh | Tidak terpengaruh |
|---|---|
| **E02:** *silent error* hampir pasti karena Lampiran 1 dibuang; ini juga menjadi sumber 15 kesalahan baru di rantai *transplanted* | **E0, E1:** tidak memakai selektor |
| **E04:** dipangkas dan abstain; naskah menyalahkan G5; peran pemangkasan belum terverifikasi | **E4:** input berupa pembaruan emas |
| **5 PKB:** hanya sekitar 13–64% teks yang terkirim, dan semuanya abstain; "tidak ada PKB yang benar" bukan ukuran bersih kemampuan LLM | Hasil yang hanya melibatkan mesin |
| **Temuan "ukuran pembaruan memprediksi kegagalan"** bercampur faktor: 7 dari 9 dokumen yang butuh ≥11 elemen kehilangan segmen, dibanding 1 dari 9 dokumen kecil | **E07** (atribut kasus yang dikarang) dan pengecoh **P01** (264 kesalahan rantai): tidak ada segmen yang dibuang |
| **CAR absolut** di semua kondisi (B3, B4, AB2, AB4, m=5, model kedua, run ulang, rantai *regenerated*) kemungkinan terlalu rendah. Perbandingan antarkondisi tetap konsisten karena inputnya sama-sama dipotong. | |
| **B2 dan AB1** (4.000 token per dokumen) lebih dirugikan lagi; kesimpulan "formalisasi dari nol gagal" bercampur faktor | |

**Ancaman validitas lain:**
- setiap rantai hanya dijalankan sekali (R=1);
- KB emas, GT3, kebijakan sintetis dan perubahan *unseen* disusun atau diperiksa oleh AI, tanpa pakar manusia;
- model kemungkinan pernah melihat regulasi uji (tidak ada peristiwa uji setelah cutoff);
- pemilihan segmen sempat dicek pada dokumen uji, yang tercatat sebagai "kebocoran desain" (`LOG_PENELITIAN.md:318`);
- pengembangan v2 memakai kebijakan sintetis yang di praregistrasi berstatus data uji.
