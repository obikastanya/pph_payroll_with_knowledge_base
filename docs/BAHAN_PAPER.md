# Bahan paper

Peta dari setiap bagian *skeleton* (`paper/draft/skeleton.tex`) ke berkas, angka, dan catatan yang dipakai untuk menulis
paper. Semua angka berasal dari berkas yang disebut. Log rinci ada di `docs/LOG_PENELITIAN.md`, keputusan di tabel
keputusan `PANDUAN_PENELITIAN.md`, rancangan terkunci di `docs/PRAREGISTRASI.md` (*tag* `prareg`, amandemen §10 *tag*
`prareg-amandemen-1`).

Status 2026-10-29: semua eksperimen E0–E5 selesai, kecuali AB1 keadaan 2025 (dihentikan untuk menghemat kredit).
Biaya LLM: Claude ±USD 81,6 kumulatif (USD 15 pertama + ±USD 66,6 tambahan; ±USD 20 kredit disisakan untuk demo),
OpenAI USD 8,1.

## Penanda versi (git *tag*)

| *Tag* | Isi |
|---|---|
| `representasi-v1` | spesifikasi representasi |
| `alur-beku`, `engine-v1` | alur akuisisi dan *engine* dibekukan sesudah kalibrasi |
| `prareg`, `prareg-amandemen-1` | pra-registrasi; amandemen sebelum jalan tambahan |
| `emas-v1` | emas dan $S^E$ sebelum koreksi E0 |
| `hasil-v1` | hasil sesudah anggaran pertama (USD 15) |
| `hasil-v2` | hasil akhir |

## Ringkasan putusan hipotesis

| Hipotesis | Hasil | Putusan |
|---|---|---|
| H1 RA perubahan tak terlihat ≥ 0,70 | 16/16, batas bawah 0,829 (konservatif 15/16, 0,736; tanpa konvensi pembulatan 8/16) | diterima |
| H2a batas atas SER ≤ 0,25 | SER 3/18, batas atas 0,377 | tidak diterima |
| H2b CAR usulan > B3, B4 | 8/18 vs 8/18 dan 9/18; Holm p = 1 | tidak diterima |
| H2b non-inferioritas SER (δ = 0,10) | vs B3: batas atas 0,004 (terpenuhi); vs B4: 0,153 (tidak) | sebagian |
| H3a OAR ≥ 0,75 | transplantasi 31/33, batas bawah 0,821 (terdaftar); pembangkitan ulang 23/33, 0,540 | diterima pada analisis terdaftar, tidak kokoh |
| H3b kesalahan terpicu ≤ batas derau | 29 tupel vs batas derau 0 | tidak didukung |
| H4a *recall* ≥ 0,70 | 0,91, batas bawah 0,75 | diterima |
| H4b $F_2$ detektor > B5(i), B5(ii) | +0,193 vs B5(ii); −0,006 vs B5(i) | tidak diterima |

## III. Representasi pengetahuan dan *inference engine*

- Spesifikasi: `docs/spesifikasi/representasi.md`, `tafsir_perhitungan.md` (K1–K18), ontologi
  `system/ontology/ontology.ttl`, *shapes* `shapes.ttl`, gambar `docs/gambar/ontologi.pdf`.
- *Engine*: `system/pph21kbs/engine/` (titik tetap terkecil, siklus *gross-up* K3.4, resolusi konflik peringkat wajib
  4 > perusahaan 3 > opsional diadopsi 2 > bawaan 1, lalu *override*, lalu *lex posterior*); jejak sampai pasal.
- Kesetaraan dengan *engine* lama: `docs/hasil/kesetaraan_engine_lama.csv`; `riwayat_engine.csv`, `fitur_engine.csv`.
- Batas representasi yang ditemukan E1 (`review/unseen_changes/hasil_E1/RINGKASAN.md` §7): tanpa aritmetika tanggal,
  tanpa pembentukan teks, lapis perusahaan tidak mengganti fakta wajib (sesuai *lex superior*), golongan per tahun,
  satu Δ satu dokumen, tanpa operasi "perpanjang", komponen baru hanya diperingatkan, syarat tanpa atribut kasus.
- Kalkulator di atas *engine* penelitian: `system/tools/calculate.py`, `system/app/calculator_app.py`.

## IV. Akuisisi berbantuan LLM

- Alur, gerbang G1–G5, $S^G$, konsensus: `docs/spesifikasi/akuisisi.md` v3, `system/pph21kbs/pipeline/`.
- Detektor dampak: `system/ontology/queries/impact_policy.rq` (beku), `impact_policy_v2.rq` (eksploratori).
- Konfigurasi LLM: `claude-opus-5-5` (relevansi *effort* `medium`, penyusunan `high`), keluaran terstruktur skema v2,
  *prompt caching*, sinkron (Batch API tidak memproses dalam 20–50 menit). Model kedua `gpt-6.1-sol`. Sebagian besar
  token keluaran adalah penalaran (rasio karakter JSON per token 1,1–1,5).
- Biaya per dokumen (m = 3): regulasi USD 0,12–1,87; PKB 0,47–0,90 (m = 2); pengecoh 0,04–0,45.

## V. Metodologi

- Desain, ambang, batas yang dapat dicapai, efek minimum (~0,45 untuk H2b): `docs/PRAREGISTRASI.md`.
- Korpus: 13 peristiwa uji, 20 pengecoh, 13 pengembangan, 5 fiktif; 5 PKB uji, 14 kebijakan buatan, PKB Koja
  pengembangan; 4 kontrafaktual; 16 perubahan tak terlihat (U01–U16, T1–T10).
- Emas: `system/gold_src/` → `dataset/12_emas/` (37 pembaruan rantai utama, 282 rekaman, 27 pembaruan sisi). Keandalan:
  `docs/hasil/kesepakatan_emas.json` (α `valid_from` 0,79; `valid_until` 1,00; nilai 90%; kode konflik α 0,73).
- Ruang uji $S^E$ (`dataset/14_ruang_uji/laporan.json`): 2.398 kasus (cakupan 2-way 100%, 3-way 0,62–0,64; batas TER
  321/tahun; Pasal 17 15/tahun; operasional 300/tahun dari sel upah BPS), kasus kebijakan 19 × 120–180, kasus terarah 21.
- Kalibrasi: log Tahap 11 (D05, FR01, Koja; lima perubahan alur sebelum pembekuan; *pass@1* 3/6).
- Protokol koreksi emas dipakai tiga kali sesudah pembekuan (DTP menurut kontrak; latar 2016 pegawai pensiun; aturan
  metode kebijakan buatan SP04/07/11/14), plus satu perbaikan alat ukur (penyelarasan kunci konflik, representasi.md §8).

## VI. Hasil

### Validasi instrumen (E0)

- Acuan pengembangan: GT3 50/50 (2.107/2.107); GT1 22/26 (14 selisih = ralat resmi); GT2 15/20 bulanan (5 pembulatan) +
  90/90 tahunan; GT5 67/79 (12 dijelaskan). `docs/hasil/acuan_*.csv`.
- GT1 *holdout*: 6/10 kasus, 221/235 observasi; sesudah koreksi 8/10, 232/235 (`acuan_gt1_holdout*.csv`). Sisa selisih:
  pemetaan iuran pensiun (2) dan pembulatan setengah rupiah (1).
- *Mutation score*: 290 mutan; 0,54 mentah; 116 kemungkinan setara; non-setara 0,90 → 1,00 sesudah 17 kasus terarah
  (`docs/hasil/mutasi_ringkasan.json`).
- Ketepatan kutipan (28 unsur, agen independen): mendukung 23, sebagian 5 (0,82; CI 0,63–0,94),
  `docs/hasil/ketepatan_kutipan.json`.

### RQ1 (E1)

`review/unseen_changes/hasil_E1/` (agen independen; tinjauan kedua `_review/TINJAUAN.md`): 16/16 perubahan, 100/100
contoh, 2.609 nilai; CP 95% [0,794; 1,000], batas bawah satu sisi 0,829. Bergantung pada Δ konvensi pembulatan
(contoh memakai pembulatan ke bawah, KB memakai PER-11/PJ/2025): konservatif 15/16 (0,736), tanpa konvensi 8/16
(0,279; semua selisih ≤ Rp11). Perubahan nyata dan kebijakan: emas semuanya lolos G1–G5 tanpa perubahan *engine*.

### RQ2 (E2)

Gabungan 18 dokumen nyata, model utama (`docs/hasil/e2_ringkasan.json`):

| Kondisi | SER | CAR | ABS |
|---|---|---|---|
| Usulan | 3/18 | 8/18 | 7/18 |
| B3 (pertama lolos G1–G2) | 7/18 | 8/18 | 3/18 |
| B4 (mayoritas tanpa gerbang) | 3/18 | 9/18 | 6/18 |
| AB2 tanpa konteks KB | 5/18 | 6/18 | 7/18 |
| AB4 seleksi sempurna (batas atas) | 0/18 | 8/18 | 10/18 |
| Sensitivitas $m = 5$ | 3/18 (2 regulasi + Taekwang) | 8/18 | 7/18 |
| Model kedua `gpt-6.1-sol`, usulan | 3/18 | 7/18 | 8/18 |
| Model kedua, B3 | 7/18 | 6/18 | 5/18 |

- Regulasi (13): usulan benar 8, salah 3 (E02 natura pada bruto 52 tupel; E07 premi JKK keringanan 42; E11 natura
  kendaraan dalam uji DTP 2), *abstain* 2 (E04, E06). Jalan kedua: 8/2/3 (E07 dan E11 salah lagi: sistematis).
- PKB (5): usulan *abstain* 5/5 (juga dengan konsensus berkunci selaras); B3 salah 3/5.
- *pass@1* 0,667, *pass@m* 0,692, *1@m* 0,615 (regulasi).
- Pengecoh 20: positif palsu 7/20 = 0,35 (CI 0,15–0,59); salah diterapkan 1/20 (P01 PP 49/2023, pengecoh sulit).
- Kontrafaktual 4: benar 1, salah 1, *abstain* 2; hafalan 0 dari 6 kandidat bernilai (semua memakai nilai dokumen).
- Kebijakan buatan 14 (strata terpisah): benar 5 (2 tidak teruji), salah 6, *abstain* 3; B3 salah 7, B4 salah 2.
- AB1 formalisasi dari nol (2023, 2024): tidak ada kandidat lolos gerbang; dari 6 kandidat 1 dapat diterapkan dan salah
  di 150/150 kasus (`experiments/e2-ab1/`).
- AB5: SHACL menolak 7/319 draf yang lolos skema (`docs/hasil/ab5_shacl.json`).
- Kontaminasi: semua peristiwa uji terbit sebelum *cutoff* kedua model, sehingga perbandingan sebelum/sesudah tidak
  mungkin; bukti dari kontrafaktual (hafalan 0) dan regulasi fiktif FR01 (kalibrasi 3/3 benar).
  `docs/hasil/kontaminasi.json`.

### RQ3 (E3)

| Rantai | OAR | Batas bawah | Kesalahan akhir |
|---|---|---|---|
| Transplantasi Δ terisolasi (`e3-tetap`, `e3-sempurna`; terdaftar) | 31/33 | 0,821 | 579 tupel |
| Pembangkitan ulang (`e3-bangkit-ulang`) | 23/33 | 0,540 | 93 tupel |

Transplantasi: kesalahan baru hanya E02 (15) dan P01 (264), P01 bertahan sampai akhir. Pembangkitan ulang: P01 tidak
salah, tetapi *abstain* E04, E06, E10, E11 tampak sebagai kesalahan baru. H3b: kesalahan terpicu 29 tupel (E03, E09,
E10, E11) vs batas derau 0. Interim $N = 24$ disimpan di `experiments/e3-interim-n24/`.

### RQ4 (E4)

`docs/hasil/rq4_label.csv`, `rq4_ringkasan.json`. 134 pasangan, 33 positif (prevalensi 0,25; pola abc 16, a 7, ac 7, b 3).

| Pendeteksi | Presisi | *Recall* (CI klaster) | $F_2$ (CI klaster) |
|---|---|---|---|
| Detektor statis (beku) | 0,71 | 0,91 (0,75–1,00) | 0,862 (0,683–0,951) |
| Detektor v2 (+ jenis d, eksploratori) | 0,57 | 1,00 | 0,868 (0,745–0,939) |
| B5(i) tandai semua yang menyentuh $F_\Delta$ | 0,57 | 1,00 | 0,868 (0,745–0,939) |
| B5(ii) pindai teks datar | 0,84 | 0,64 (0,31–0,82) | 0,669 (0,341–0,833) |
| Tandai semuanya (rujukan) | 0,25 | 1,00 | 0,620 |

Selisih $F_2$ detektor: +0,193 (CI 0,062–0,400) vs B5(ii); −0,006 (CI −0,110–0,058) vs B5(i). Tiga pasangan terlewat
(SP01×E05, SP01×E08, SP03×E10): kebijakan *menghasilkan* fakta di $F_\Delta$ yang berubah lewat parameter atau aturan
hulu. Detektor v2 menutupnya, tetapi menjadi identik dengan B5(i). κ label eksekusi vs label manual ≈ 0 (pengertian
dampak berbeda: "membaca fakta yang berubah" vs "nilai benar-benar berubah").

### E5 (B2, motivasi)

LLM menghitung langsung dari 26 dokumen yang berlaku (100 kasus operasional 2025, `experiments/e5-b2/`): tepat 76/100
(CI 0,66–0,84), dalam Rp1 97/100, USD 0,068 per kasus per perhitungan; tanpa jejak dan tidak deterministik.

### B1

`docs/hasil/b1_pemeliharaan.csv`: kalkulator *hand-coded* memasukkan TER 26 dan 915 hari sesudah PP 58/2023.

## VII. Pembahasan: bahan

- Gerbang + konsensus menekan pembaruan salah (SER 3/18 vs B3 7/18, pada kedua model), dibayar dengan *abstain*;
  tidak menaikkan CAR (8/18 = B3). Seleksi sempurna (AB4) menunjukkan ruang perbaikan: SER 0 dengan CAR sama.
- Konteks KB penting: AB2 SER 5/18, CAR 6/18; AB1 (tanpa KB, formalisasi utuh) gagal total. Akuisisi inkremental
  dengan konteks lebih mudah daripada formalisasi dari nol.
- PKB adalah titik lemah: tidak ada PKB yang benar di kondisi mana pun; usulan aman karena *abstain*.
- Kesalahan sistematis (E07, E11 di dua jalan; kandidat sepakat tapi salah) tidak dapat ditangkap konsensus.
- Pengecoh sulit (P01) adalah sumber kerusakan terbesar di mode berantai; relevansi adalah titik rawan.
- OAR rantai transplantasi tertutup kesalahan yang sudah ada; ukuran berantai harus memisahkan efek *masking*.
- *Holdout* dan keluaran LLM menemukan kesalahan emas yang lolos semua acuan pengembangan (DTP kontrak, pensiun 2016,
  metode kebijakan buatan): bukti nilai protokol koreksi emas.
- LLM langsung (B2) cukup akurat untuk kasus sederhana (97% dalam Rp1) tetapi tanpa jejak, tidak deterministik, dan
  biaya berulang per perhitungan.

## VIII. Ancaman terhadap validitas dan keterbatasan

- $m$ utama 3/2 karena anggaran; ablasi dan model kedua dijalankan sesudah hasil awal terlihat (amandemen 1, tidak
  buta); AB1 hanya dua keadaan.
- Daya H2b rendah (efek minimum ~0,45; $N = 18$).
- E1 bergantung pada konvensi pembulatan contoh; perubahan tak terlihat ditulis agen, bukan pakar manusia, dan belum
  diperiksa pakar (`SEGEL.md` aturan 3).
- Emas kebijakan buatan dan bahan ahli ditinjau agen independen, bukan pakar *payroll* manusia.
- Pelabel kutipan sempat membuka spesifikasi tafsir proyek (2 label mungkin terpengaruh).
- Kebocoran desain kecil: pemeriksaan awal pemilihan segmen pada beberapa dokumen uji (log Tahap 9).
- Penyelarasan kunci konflik tidak ada di konsensus alur beku (sensitivitas menunjukkan hasil sama).
- Batch API tidak dapat dipakai; GPT sangat lambat untuk draf panjang (24 menit per draf).
- Kontaminasi tidak dapat diuji dengan pemisahan *cutoff* (semua peristiwa sebelum *cutoff*).
