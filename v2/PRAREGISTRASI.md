# Praregistrasi: pembaruan KB PPh 21 adaptif dengan LLM, evaluasi *replay* per perusahaan

Dokumen ini dikunci dengan commit git sebelum panggilan model terukur pertama, dan diunggah ke OSF oleh peneliti. Kerangka lengkap: [research_proposal.docx](research_proposal.docx). Log keputusan: [LOG_PENELITIAN.md](LOG_PENELITIAN.md).

## 1. Pertanyaan dan hipotesis

**RQ1 (utama), ketepatan slip di satu perusahaan.**

*H1.* Pada lima perusahaan nyata (Sansan, Century Textile, Taekwang, AVCO, WIKA), masing-masing dengan rantai sendiri, dalam kondisi HR dasar:
- (a) ketepatan slip pipeline tidak lebih rendah daripada skenario kode tercepat, dengan margin 0,01: batas bawah CI 95% selisih (pipeline − kode) > −0,01;
- (b) tidak ada penjalaran sistematis.

H1 gugur bila salah satu tidak terpenuhi.

- **Ketepatan slip:** proporsi slip pegawai-bulan yang sama dengan slip acuan sampai rupiah, dinilai sebagaimana diketahui pada tanggal payroll bulan itu (tanggal 25).
- **Skenario kode tercepat:** setiap pembaruan acuan diterapkan 26 hari setelah terbit (adopsi TER tercepat pada B1); pembaruan yang diabstain pipeline juga masuk 26 hari setelah terbit.
- **Penjalaran sistematis:** peristiwa yang benar di kedua run terisolasi tetapi salah di minimal dua rantai.
- **Kesalahan dalam rantai:** pembaruan pipeline pada KB rantai berbeda hasil dengan pembaruan acuan pada KB rantai yang sama.

Analisis: *bootstrap* berklaster per peristiwa, 10.000 ulangan, pada 48 pasangan peristiwa-rantai. Daya disimulasikan dari run set pengembangan sebelum run uji; bila di bawah 0,80, H1 dilaporkan sebagai estimasi, dan keputusan itu dicatat di sini sebelum run uji.

**RQ2 (pendukung), keamanan satu pembaruan.**

*H2.* Pada set prospektif (80 unit, mode terisolasi):
- (a) batas atas satu sisi 95% SER ≤ 0,15 (Clopper–Pearson);
- (b) SER pipeline < SER B3 (McNemar eksak satu sisi, α = 0,05) dan batas bawah CI Newcombe berpasangan dari selisih CAR (pipeline − B3) ≥ −0,10;
- (c) laju abstain ≤ 0,50.

H2 gugur bila salah satu tidak terpenuhi. Set nyata (13 regulasi dan 5 PKB) harus searah: SER pipeline ≤ SER B3; seri dianggap searah.

**RQ3, dampak lintas lapis.** *H3* eksploratif: dari 142 pasangan perusahaan × peristiwa, label acuan memberi 17 pasangan terdampak, di bawah ambang 40 yang ditetapkan proposal. Recall, presisi, dan F2 detektor sistem serta dua detektor sederhana (B6) dilaporkan dengan CI *bootstrap* berklaster per peristiwa, tanpa uji.

## 2. Definisi

- **Benar (satu dokumen):** pembaruan terpilih, diterapkan ke KB dasar, menghasilkan semua nilai keluaran, laporan konflik (diselaraskan menurut fakta yang dihasilkan aturan), dan galat mesin yang sama dengan pembaruan acuan pada KB yang sama. Penilaian dilakukan untuk semua kasus uji pada dua tanggal pengetahuan: H-1 terbit dan tanggal terbit.
- **SER, CAR, abstain:** satu-satunya peringatan adalah abstain.
  - Pembaruan yang salah, termasuk yang lolos setelah ronde perbaikan atau dengan konsensus tipis, adalah *silent error*.
  - Pembaruan kosong untuk dokumen relevan adalah *silent error*.
  - Pembaruan yang tidak dapat diterapkan adalah *silent error*.
  - SER memuat semua kegagalan, termasuk bagian dokumen yang tidak terbaca.
- **Baseline dari draf yang sama:**
  - B2: draf pertama dalam urutan acak yang lolos semua *gate* setelah perbaikan;
  - B3: draf pertama yang lolos G1 dan G2 sebelum perbaikan;
  - B4: *majority vote* perilaku semua draf tanpa *gate*;
  - batas atas seleksi: benar bila ada draf lolos yang benar.
- **Kondisi HR:**
  - dasar: usulan selalu disetujui, abstain ditangani HR 26 hari setelah terbit dengan pembaruan acuan;
  - tanpa manusia: abstain tidak ditangani;
  - HR teliti: usulan salah yang kesalahannya tampak pada kasus contoh panel review ditolak dan ditangani HR.

  Kondisi tanpa manusia dan HR teliti dihitung dari draf yang sama dengan kondisi dasar.

## 3. Data (disegel sebelum run)

| Bagian | Isi |
|---|---|
| Regulasi uji | 13 peristiwa 2023–2026 (`v2/dataset/09_korpus_peristiwa/peristiwa.csv`, bagian uji) |
| Pengecoh | 20 regulasi; versi pangkas (`13_teks_pengecoh_ringkas`: pembuka, satu pasal utuh dengan istilah PPh 21 terpadat, penutup) di semua run |
| Perusahaan | 5 nyata (5 PKB, ditambah PKB Century Textile 2021–2023) dan 10 fiktif (SP02, SP03, SP04, SP05, SP06, SP07, SP08, SP11, SP12, SP13, masing-masing dengan satu memo K01–K10) |
| Set prospektif | 80 unit (`v2/dataset/15_set_prospektif/units`) |
| Set pengembangan | 13 peristiwa 2012–2022, 5 regulasi fiktif, PKB Koja, SP01, SP09, SP10, SP14 |
| Acuan | `v2/dataset/12_emas` (rantai dan pembaruan sisi) |
| Kasus | Ruang uji v1 (`v2/dataset/14_ruang_uji`), panel per perusahaan (`v2/harness/instances.py`, *seed* 20261115; setiap pegawai membawa masa kerja per bulan, bulan THR ditandai, dan kolom HR kebijakan perusahaannya), pegawai pemicu set prospektif |

SHA-256 setiap teks dan kunci jawaban dicatat di manifes saat penyegelan (`v2/dataset/MANIFEST_SEGEL.sha256`).

## 4. Sistem yang dibekukan

- **Kode:** system_final dan v2/harness pada commit yang memuat dokumen ini.
- **Penyusun:** `gpt-6.1-sol` (versi yang dilaporkan API dicatat di setiap panggilan). Model peta: `gpt-5.4-mini`.
- **Konfigurasi:**
  - `Config(m=3, repair_rounds=1, relevance_effort="medium", draft_effort="high", fallback="full", seed=20261027)`;
  - peta dokumen disimpan sekali per dokumen;
  - bagian inti tidak dipangkas;
  - pembersihan teks deterministik saat dokumen masuk.
- **Kamus data payroll:** standar (`system_final/data/kb/payroll_inputs.json`) dan per perusahaan (dibangkitkan dari kebijakan acuannya, ditambah 8 kolom HR umum).
- **Uji ketahanan:** Sonnet 5.5 dengan konfigurasi yang sama pada set nyata dan 20 unit prospektif terstratifikasi.

## 5. Aturan pelaksanaan

- *Prompt*, ambang, dan *gate* tidak diubah setelah dokumen ini dikunci. Perubahan karena galat teknis (bukan karena hasil) dicatat sebagai deviasi beserta alasannya.
- Galat API pada satu panggilan diperlakukan seperti sistem memperlakukannya: draf gagal, lalu ronde perbaikan. Panggilan tidak diulang demi hasil. Run yang terputus karena kegagalan infrastruktur dilanjutkan dari langkah terakhir yang tercatat.
- Data uji tidak dipakai untuk menyetel apa pun. Semua panggilan dicatat lengkap (prompt, keluaran, token, biaya), sehingga setiap angka dapat dihitung ulang tanpa memanggil model.
- **Anggaran:** biaya diukur pada dokumen terpanjang sebelum run. Bila perkiraan melampaui kredit, yang dipotong berturut-turut adalah ablasi teks penuh lalu B5. Jumlah unit, jumlah rantai, dan keutuhan teks tidak dikurangi; bila tetap kurang, run ditunda.

## 6. Analisis yang direncanakan

- **Statistik:** Clopper–Pearson, McNemar eksak, CI Newcombe berpasangan, dan *bootstrap* berklaster per peristiwa (H1, H3) atau per jenis perubahan (sensitivitas H2).
- **Rincian hasil:**
  - per jenis dan ukuran perubahan;
  - per perusahaan dan sektor (padat karya atau bukan);
  - per peristiwa berlaku surut atau tidak;
  - per kondisi HR;
  - jumlah dan taksiran waktu intervensi HR;
  - skenario unggah terlambat (5 peristiwa berlaku surut × 3 jeda);
  - Sonnet dibanding `gpt-6.1-sol`;
  - teks penuh dibanding peta;
- **Analisis kegagalan:** taksonomi per jenis kesalahan, kegagalan baca, kegagalan pada jebakan, dan materialitas dalam rupiah dan jumlah pegawai.
