# Pra-registrasi penelitian

Status: **draf**, dikunci dengan *tag* git `prareg` sebelum peristiwa uji pertama dijalankan. Pendaftaran ke OSF atau
AsPredicted dilakukan oleh peneliti (layanan pihak ketiga, akun peneliti); sampai saat itu stempel waktu yang berlaku
adalah *commit* bertanda `prareg`. Tanggal *tag* juga menjadi batas awal peristiwa prospektif.

Rujukan: *skeleton* Bagian VI (desain), `docs/spesifikasi/akuisisi.md` (alur, gerbang, konsensus), PANDUAN Tahap 12.

## 1. Pembagian data

| Bagian | Isi | Dipakai untuk |
|---|---|---|
| Pengembangan | D01–D13 (regulasi 2012–2022), FR01–FR05 (regulasi fiktif), PKB Koja 2012 | penyetelan dan kalibrasi (Tahap 9, 11) |
| Uji regulasi | E01–E13 (13 peristiwa nyata 2023–2026) | E2, E3 |
| Uji kebijakan nyata | 5 PKB (WIKA, Centex, AVCO, Taekwang, Sansan) | E2 lapisan perusahaan, E1 |
| Uji kebijakan buatan | SP01–SP14 | E2 strata terpisah, E4 |
| Pengecoh | P01–P06, P08–P21 (20 dokumen) | E2 (relevansi), E3 |
| Kontrafaktual | CF-E01, CF-E06, CF-E11, CF2-E02 (nilai dan ambang) | E2 strata kontrafaktual (hafalan) |
| Perubahan tak terlihat | disegel oleh kolaborator (`review/unseen_changes/sealed/`) | E1 (H1) |
| Acuan GT1 *holdout* | 14 kasus | E0, dipakai sekali |

Tidak ada peristiwa uji yang dijalankan alur sebelum *tag* `prareg` (diperiksa dari `experiments/*/calls.jsonl`).

## 2. Parameter alur yang dibekukan

Dibekukan dengan *tag* `alur-beku` (kode `system/pph21kbs/pipeline/`, *prompt*, gerbang G1–G5, generator $S^G$,
konsensus) dan `engine-v1`; emas dikunci dengan `emas-v1` (sidik jari rantai `beb4a9ab651aef34`, hash $\Delta^\star$
dan harapan $S^E$ di `dataset/14_ruang_uji/laporan.json`).

| Parameter | Nilai |
|---|---|
| Model utama | `claude-opus-5-5`; dokumen nyata sinkron dengan *prompt caching*, pengecoh lewat Message Batches |
| *effort* relevansi / penyusunan | `medium` / `high` |
| $m$ regulasi uji | 3 |
| $m$ PKB uji | 2 |
| Kebijakan buatan, kontrafaktual, model kedua | hanya bila sisa anggaran cukup sesudah strata utama ($m = 2$); bila tidak, dicatat sebagai keterbatasan |
| Putaran perbaikan | 1 |
| *Seed* urutan kandidat | 20261027 |
| $R$ (E3) | 1 |
| $\omega$ kebijakan | 2026-10-27 |
| Anggaran LLM | USD 15 total untuk seluruh penelitian, termasuk yang sudah terpakai |

## 3. Hipotesis, ambang, dan batas yang dapat dicapai

Batas dihitung dengan `system/pph21kbs/analysis/stats.py` (Clopper–Pearson; satu sisi 95% untuk ambang).

| Hipotesis | Statistik dan keputusan | $N$ | Batas terbaik yang dapat dicapai | Ambang |
|---|---|---|---|---|
| H1 | RA perubahan tak terlihat; H1 diterima bila batas bawah satu sisi 95% ≥ $\theta_1$ | jumlah perubahan tersegel ($\geq 15$ direncanakan) | $N=15$, semua berhasil: 0,819; satu gagal: 0,721 | $\theta_1 = 0{,}70$. Bila $N < 10$, hanya estimasi dan CI |
| H2a | SER usulan atas dokumen sumber nyata yang relevan (regulasi + PKB); diterima bila batas atas satu sisi 95% ≤ $\theta_2$ | 18 | 0 salah: 0,153; 1 salah: 0,238; 2 salah: 0,310 | $\theta_2 = 0{,}25$ |
| H2b (1) | CAR usulan > CAR B3 dan > CAR B4; McNemar eksak satu sisi pada pasangan dokumen | 18 | — | $p < 0{,}05$ sesudah Holm |
| H2b (2) | Non-inferioritas SER usulan terhadap B3 dan B4: batas atas CI 95% Newcombe berpasangan dari SER$_\text{usulan}$ − SER$_\text{pembanding}$ < $\delta_S$ | 18 | — | $\delta_S = 0{,}10$ |
| H3a | OAR mode berantai (varian *abstain* tetap), diterima bila batas bawah satu sisi 95% ≥ $\theta_3$ | 33 (13 uji + 20 pengecoh) | semua: 0,913; satu gagal: 0,864; dua gagal: 0,821; tiga gagal: 0,781 | $\theta_3 = 0{,}75$ |
| H3b | kesalahan terpicu $I$ tidak melebihi batas derau dua jalan terisolasi | 13 | — | deskriptif |
| H4a | *recall* detektor dampak pada pasangan kebijakan × peristiwa berlabel positif; diterima bila batas bawah CI 95% *bootstrap* klaster per peristiwa ≥ $\theta_4$ | jumlah pasangan positif dari `docs/hasil/rq4_label.csv` | — | $\theta_4 = 0{,}70$ |
| H4b | $F_2$ detektor > $F_2$ B5(i) dan B5(ii); selisih berpasangan dengan *bootstrap* klaster, batas bawah > 0 | idem | — | Holm |

Keluarga Holm: RQ2 = {CAR vs B3, CAR vs B4, NI vs B3, NI vs B4}; RQ4 = {$F_2$ vs B5(i), $F_2$ vs B5(ii)}. Pemeriksaan
nol-cacat dan invarian (A1, A3$_\omega$) tidak masuk keluarga.

## 4. Analisis konfirmatori dan eksploratori

Konfirmatori: H1, H2a, H2b, H3a, H4a, H4b pada data uji sesuai tabel di atas.

Eksploratori (dilaporkan dengan CI, tanpa klaim): SER/CAR per lapisan dan per jenis perubahan; kebijakan buatan;
kontrafaktual dan laju hafalan (kandidat yang membawa nilai asli); peristiwa sebelum dan sesudah *cutoff* model;
*pass@1*, *pass@m*, *1@m*, η; AB3 dan AB4; laju relevansi pada pengecoh; komponen mekanis kesalahan terpicu; *drift*
akhir; biaya per dokumen; model kedua.

## 5. Kecukupan instrumen dan syarat lulus E0

- *Mutation score* terfokus-Δ per peristiwa, atas mutan yang tidak setara: ambang **0,80**. Mutan setara (tidak
  mengubah perilaku pada domain kasus mana pun, misalnya tanggal akhir sesudah tahun pajak terakhir) ditandai dengan
  alasan di `docs/hasil/mutasi.csv` sebelum E2. Peristiwa di bawah ambang ditambah kasus terarah lalu diukur ulang.
- E0 lulus bila tidak ada selisih acuan berstatus "*knowledge base* salah" yang belum diselesaikan dan ambang mutasi
  tercapai.

## 6. Protokol koreksi emas

Bila keluaran LLM atau peninjauan menyingkap kesalahan pada $\mathcal{K}^\star$ atau $\Delta^\star$: (1) catat temuan
dan buktinya (kutipan dokumen) di log; (2) perbaiki di `system/gold_src/` dengan *commit* berawalan "koreksi emas";
(3) bangun ulang emas dan harapan $S^E$; (4) nilai ulang semua kondisi dan semua jalan dengan emas baru; (5) laporkan
jumlah koreksi dan hasil sebelum/sesudah. Koreksi tidak boleh dibuat hanya pada peristiwa tempat usulan kalah.

## 6a. Temuan kalibrasi yang mengubah alur sebelum pembekuan

1. G5: subjek KLU yang berupa deskripsi himpunan tidak dapat diperiksa (D05 ditolak di semua kandidat).
2. Segmentasi PKB: judul pasal bertajuk tidak dikenali, sehingga tiga PKB hanya berisi pembuka (Koja dinilai tidak
   relevan karena teks terpotong).
3. G5: tanggal mulai sebelum cakupan $S^G$ (2013) diperiksa pada bulan pertama yang tercakup.
4. G2: tarif tertulis sebagai bilangan bulat per pangkat sepuluh (1,27% → 127/10000) dianggap berpijak.
5. Relevansi tanpa *cache*; dokumen nyata sinkron, pengecoh *batch*.

Temuan yang tidak mengubah alur: kandidat lolos gerbang tetapi salah perilaku (D05: syarat NPWP, bulan THR; Koja:
definisi upah dan komponen tahunan terlewat), sehingga SER yang tinggi pada dokumen kompleks sudah terlihat pada data
pengembangan.

## 7. Pelaksana dan rencana cadangan

Peneliti tunggal; peninjau emas dan bahan pakar adalah agen independen tanpa konteks penyusun; perubahan tak
terlihat oleh kolaborator. Bila anggaran habis sebelum semua kondisi berjalan, urutan pemangkasan (log keputusan
2026-10-27): ablasi hanya pada model utama; model kedua hanya pada usulan untuk subset; kontrafaktual dan kebijakan
buatan dengan $m$ lebih kecil; pengulangan E3 $R = 1$.

## 8. Perkiraan biaya

Terukur pada kalibrasi (`experiments/kalibrasi-1`, `kalibrasi-2`; USD harga Oktober 2026): relevansi USD 0,03–0,15;
draf pertama (menulis *cache*) USD 0,19–0,35; draf berikutnya (membaca *cache*) USD 0,07–0,21; perbaikan USD
0,06–0,10. Sebagian besar keluaran adalah penalaran (rasio karakter JSON per token keluaran 1,1–1,5).

| Strata | Dokumen | $m$ | USD per dokumen | Total USD |
|---|---|---|---|---|
| Regulasi uji (surat batas upah JP) | 4 | 3 | ~0,25 | ~1,0 |
| Regulasi uji (PMK, PP, PER) | 9 | 3 | ~0,70 | ~6,3 |
| PKB uji | 5 | 2 | ~0,80 | ~4,0 |
| Pengecoh (relevansi, *batch*) | 20 | — | ~0,04 | ~0,8 |
| Jumlah | | | | ~12,1 |

Terpakai sebelum E2: USD 2,29 (uji asap dan kalibrasi). Sisa sesudah rencana: ~USD 0,6 sebagai cadangan. Rencana
semula ($m = 5$ di semua dokumen nyata, ablasi, model kedua, kebijakan buatan, kontrafaktual) diperkirakan di atas
USD 30; selisihnya adalah keterbatasan yang dilaporkan. Dalam rupiah (kurs asumsi Rp16.500/USD): rencana ~Rp200 ribu,
seluruh anggaran Rp247.500.

## 9. Efek minimum yang dapat dideteksi

*pass@1* kalibrasi: 3/6 kandidat benar pada $S^E$ pengembangan (FR01 3/3, D05 0/3; Koja tanpa $S^E$). Simulasi McNemar
eksak satu sisi, $N = 18$, $lpha = 0{,}025$ (Holm, dua uji CAR), CAR pembanding 0,3–0,5: daya 0,15–0,16 untuk selisih
0,2; 0,41–0,42 untuk 0,3; 0,69–0,72 untuk 0,4; 0,89–0,95 untuk 0,5. Efek minimum dengan daya 80% kira-kira 0,45. H2b
(1) karena itu kurang daya untuk selisih yang realistis; hasilnya dilaporkan dengan selang Newcombe, dan kegagalan
menolak tidak dibaca sebagai bukti kesetaraan.
