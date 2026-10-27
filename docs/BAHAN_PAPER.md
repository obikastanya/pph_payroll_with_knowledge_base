# Bahan paper

Peta dari setiap bagian *skeleton* (`paper/draft/skeleton.tex`) ke berkas, angka, dan catatan log yang dipakai untuk
menulis ulang paper. Semua angka berasal dari berkas yang disebut; log rinci tiap tahap ada di
`docs/LOG_PENELITIAN.md`, keputusan di tabel keputusan `PANDUAN_PENELITIAN.md`, dan rancangan terkunci di
`docs/PRAREGISTRASI.md` (*tag* `prareg`).

Status per 2026-10-28: Tahap 3–13, E2, E3, dan E4 (label eksekusi dan detektor) selesai; E1 belum (perubahan tak
terlihat masih tersegel dan harus dibuka peneliti atau kolaborator); E5 (model kedua) tidak dijalankan karena anggaran
habis. Anggaran LLM: USD 15,016 dari 15 (lebih 1,6 sen karena permintaan *batch* yang selesai saat dibatalkan).

## Penanda versi (git *tag*)

| *Tag* | Isi |
|---|---|
| `representasi-v1` | spesifikasi representasi |
| `alur-beku` | alur akuisisi dibekukan sesudah kalibrasi |
| `engine-v1` | *engine* dibekukan |
| `prareg` | pra-registrasi; batas peristiwa prospektif |
| `emas-v1` | emas dan $S^E$ sebelum koreksi E0 (koreksi sesudahnya ada di *commit* afd97b0) |

## III. Representasi pengetahuan dan *inference engine*

- Spesifikasi: `docs/spesifikasi/representasi.md`, `tafsir_perhitungan.md` (K1–K18), ontologi
  `system/ontology/ontology.ttl`, *shapes* `shapes.ttl`, gambar `docs/gambar/ontologi.pdf`.
- *Engine*: `system/pph21kbs/engine/` (titik tetap terkecil, siklus *gross-up* K3.4, resolusi konflik peringkat
  wajib 4 > perusahaan 3 > opsional diadopsi 2 > bawaan 1, lalu *override*, lalu *lex posterior*).
- Kesetaraan dengan *engine* lama: `docs/hasil/kesetaraan_engine_lama.csv`; riwayat dan fitur `riwayat_engine.csv`,
  `fitur_engine.csv`. Log Tahap 5.

## IV. Akuisisi berbantuan LLM

- Alur, gerbang G1–G5, $S^G$, konsensus: `docs/spesifikasi/akuisisi.md` v3, kode `system/pph21kbs/pipeline/`.
- Detektor dampak: `system/ontology/queries/impact_*.rq`, `system/pph21kbs/impact.py`.
- Konfigurasi LLM: `claude-opus-5-5`, *effort* relevansi `medium`, penyusunan `high`, keluaran terstruktur skema v2
  (`docs/spesifikasi/format_data.md` §2.3; v1 ditolak API karena tata bahasa terlalu besar), *prompt caching*.
  Sebagian besar token keluaran adalah penalaran (rasio karakter JSON per token 1,1–1,5).

## V. Metodologi

- Desain, ambang, batas yang dapat dicapai, efek minimum: `docs/PRAREGISTRASI.md`.
- Korpus: `dataset/09_korpus_peristiwa/peristiwa.csv` (13 uji, 20 pengecoh, 13 pengembangan), fiktif FR01–FR05,
  kebijakan `dataset/10_kebijakan_perusahaan/peristiwa_kebijakan.csv` (5 PKB uji, 14 buatan, Koja pengembangan),
  kontrafaktual `dataset/09_korpus_peristiwa/kontrafaktual/INDEX.csv` (4 dibangun, tidak dijalankan).
- Emas: `system/gold_src/` → `dataset/12_emas/` (37 pembaruan rantai utama, 280 rekaman, 27 pembaruan sisi).
  Keandalan: `docs/hasil/kesepakatan_emas.json` (α `valid_from` 0,79; `valid_until` 1,00; nilai 90%; kode konflik
  α 0,73). Log Tahap 7.
- Ruang uji $S^E$: `dataset/14_ruang_uji/laporan.json` (2.398 kasus; cakupan 2-way 100%, 3-way 0,62–0,64; batas TER
  321/tahun; Pasal 17 15/tahun; operasional 300/tahun dari sel upah BPS), kasus kebijakan (19 × 120–180), kasus
  terarah (17 dari mutasi + 4 dari koreksi emas).
- Kalibrasi: log Tahap 11 (D05, FR01, Koja; lima perubahan alur sebelum pembekuan; *pass@1* 3/6).

## VI. Hasil

### Validasi instrumen (E0)

- Acuan pengembangan: GT3 50/50 kasus (2.107/2.107 observasi); GT1 22/26 (14 selisih = ralat contoh resmi);
  GT2 15/20 bulanan (5 selisih pembulatan) + 90/90 tahunan; GT5 67/79 (12 dijelaskan). `docs/hasil/acuan_*.csv`.
- GT1 *holdout* sekali pakai: 6/10 kasus, 221/235 observasi; sesudah satu koreksi emas 7/10, 226/235
  (`acuan_gt1_holdout*.csv`). Tabel adjudikasi di log Tahap 13.
- *Mutation score*: 290 mutan; 0,54 mentah; 116 kemungkinan setara; non-setara 0,90 → 1,00 sesudah 17 kasus
  terarah (`docs/hasil/mutasi_ringkasan.json`).

### RQ1 (E1)

Belum dijalankan: perubahan tak terlihat tersegel (`review/unseen_changes/sealed/`). RA korpus nyata dan kebijakan
dari Tahap 7: semua 13 perubahan nyata dan 20 kebijakan dapat dinyatakan tanpa mengubah *engine* (emas lolos G1–G5,
`docs/hasil/gerbang_emas.csv`), dengan satu kesalahan latar 2016 (pegawai pensiun, log Tahap 13).

### RQ2 (E2)

- Regulasi ($m = 3$): [diisi dari `experiments/e2-regulasi/summary.json`]
- PKB ($m = 2$): usulan *abstain* 5/5 (SER 0, CAR 0); B3 SER 3/5 = 0,6 (semua salah di hampir semua tupel);
  `experiments/e2-pkb/summary.json`.
- Pengecoh: 11 dijalankan, positif palsu 5/11 = 0,45 (CI 0,17–0,77), salah diterapkan 1/11 (P01, PP 49/2023,
  pengecoh sulit tafsir_korpus A1); empat positif palsu lain tidak mengubah perilaku pada $S^E$.
  `experiments/e2-pengecoh/summary.json`.

### RQ3 (E3)

`experiments/e3-tetap/`, `experiments/e3-sempurna/`: OAR 22/24 = 0,917 (CI 0,730–0,990; batas bawah satu sisi
0,760 ≥ θ₃ = 0,75); OAR regulasi 12/13. Kesalahan baru hanya di E02 (15 tupel) dan P01 (264 tupel); P01 bertahan
sampai akhir rantai, sehingga *drift* akhir 579 tupel salah (sampel 150 kasus per tahun). Varian peninjau sempurna
sama, karena E04 dan E06 (*abstain*) hanya menyentuh tupel yang sudah salah. 9 pengecoh tidak dijalankan (anggaran)
dan tidak dihitung.

### RQ4 (E4)

`docs/hasil/rq4_label.csv`, `rq4_ringkasan.json` (alat `system/tools/rq4_labels.py`; query detektor yang sama
dijalankan di GraphDB). 134 pasangan kebijakan uji × peristiwa uji, 33 positif menurut label eksekusi (prevalensi
0,25; pola: abc 16, a 7, ac 7, b 3).

| Pendeteksi | Presisi | *Recall* (CI klaster) | $F_2$ (CI klaster) |
|---|---|---|---|
| Detektor statis | 0,71 | 0,91 (0,75–1,00) | 0,862 (0,683–0,951) |
| B5(i) tandai semua yang menyentuh $F_\Delta$ | 0,57 | 1,00 | 0,868 (0,745–0,939) |
| B5(ii) pindai teks datar | 0,84 | 0,64 (0,31–0,82) | 0,669 (0,341–0,833) |
| Tandai semuanya (rujukan) | 0,25 | 1,00 | 0,620 |

H4a diterima (batas bawah *recall* 0,75 ≥ θ₄ = 0,70). H4b tidak: selisih $F_2$ terhadap B5(ii) +0,193 (CI 0,062–0,400),
terhadap B5(i) −0,006 (CI −0,110–0,058). Detektor melewatkan 3 pasangan (SP01×E05, SP01×E08, SP03×E10; semua label
(a); dua di antaranya peristiwa batas upah JP. Mekanismenya belum dianalisis: periksa jalur baca SP01/SP03 ke fakta
yang diubah E05, E08, E10). κ label eksekusi terhadap label
manual kebijakan buatan ≈ 0 (88 pasangan): label manual menandai "membaca fakta yang berubah" (46), label eksekusi
menuntut nilai benar-benar berubah pada kasus sampel (13 dari 46): dua pengertian dampak yang berbeda.

## VII. Pembahasan: bahan

- Konsensus mencegah pembaruan salah pada PKB (usulan *abstain* 5/5, B3 salah 3/5): bukti nilai seleksi berbasis
  perilaku, dibayar dengan CAR nol.
- Pengecoh sulit adalah sumber kesalahan terbesar di mode berantai: satu positif palsu (P01) merusak hampir semua
  tupel sesudahnya. Gerbang tidak menangkapnya karena $\Delta$ konsisten dengan dokumen; yang salah adalah
  penilaian relevansi.
- Koreksi emas oleh *holdout* (DTP menurut kontrak): kesalahan yang lolos semua acuan pengembangan dan pembaca kedua.
- Kandidat lolos gerbang tetapi salah perilaku sudah terlihat di kalibrasi (D05 syarat NPWP; Koja definisi upah).

## VIII. Ancaman terhadap validitas dan keterbatasan

- Anggaran: $m$ 3/2 (bukan 5), tanpa ablasi AB1/AB2/AB5, tanpa model kedua, tanpa kebijakan buatan dan kontrafaktual
  di E2, 9 pengecoh tidak dijalankan, E3 $R = 1$ tanpa pembangkitan ulang (komponen kontekstual tidak diukur).
- Batch API tidak memproses permintaan dalam 20–50 menit; seluruh jalan memakai panggilan sinkron.
- Daya H2b rendah (efek minimum ~0,45).
- Emas: kesalahan latar 2016 belum dikoreksi; tafsir bersama penyusun dan pembaca kedua.
- Kebocoran desain kecil: pemeriksaan awal pemilihan segmen pada beberapa dokumen uji (log Tahap 9).
- E1 belum ada.
