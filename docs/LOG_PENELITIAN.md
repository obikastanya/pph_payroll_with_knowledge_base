# Jurnal penelitian

Catatan kerja penelitian *knowledge-based system* adaptif untuk PPh 21, dari Tahap 3 (spesifikasi) sampai Tahap 20 (analisis). Setiap tahap dicatat dengan tujuan, hasil, angka penting, keputusan, penyimpangan dari rencana, berkas keluaran, dan bagian paper yang memakainya. Setiap tahap diakhiri satu *commit* git yang namanya dicatat di sini, supaya keadaan pada akhir tahap dapat dipulihkan.

Dokumen terkait:
- Rencana tahap dan log keputusan: [PANDUAN_PENELITIAN.md](../PANDUAN_PENELITIAN.md)
- Kerangka paper: [paper/draft/skeleton.tex](../paper/draft/skeleton.tex)
- Spesifikasi: [docs/spesifikasi/](spesifikasi/)
- Dataset dan statusnya: [dataset/RENCANA_DATASET.md](../dataset/RENCANA_DATASET.md)
- Indeks bahan paper (diisi bertahap): bagian **Bahan paper** di bawah dan [docs/BAHAN_PAPER.md](BAHAN_PAPER.md) setelah Tahap 20

## Status

| Tahap | Nama | Status | *Commit* |
|---|---|---|---|
| 0 | Persiapan dan keputusan terbuka | selesai (sebelum jurnal ini) | `e851c8d` dst. |
| 2 | Taksonomi dan aturan tafsir | selesai (sebelum jurnal ini) | `d2ff550`, `f9b4f08` |
| 6 | Korpus dan dataset | selesai (sebelum jurnal ini) | `02c3e01` |
| 3 | Spesifikasi representasi | selesai (v2) | `d00fe74`, lihat Tahap 4 |
| 4 | Spesifikasi akuisisi dan kontrak antarmuka | selesai (v2) | (commit Tahap 4) |
| 5 | Representasi dan *engine* | selesai | `31c3d33`, (commit Tahap 5), *tag* `representasi-v1` |
| 7 | Emas $\mathcal{K}^\star_n$, $\Delta^\star_n$ | berjalan (rantai regulasi selesai) | |
| 8 | Ruang uji dan acuan | belum | |
| 9 | Alur akuisisi | belum | |
| 10 | Pembanding, ablasi, skrip analisis | belum | |
| 11 | Kalibrasi pada data pengembangan | belum | |
| 12 | Pra-registrasi | belum | |
| 13–18 | Eksperimen E0–E5 | belum | |
| 19 | Peristiwa prospektif | dipantau (peristiwa pertama Februari 2027) | |
| 20 | Analisis dan penyajian hasil | belum | |

Tahap 1 (kajian pustaka) dan 21–24 (naskah, telaah, rilis, pengiriman) dikerjakan setelah sistem dan hasil selesai, sesuai log keputusan "Urutan kerja".

## Cara kerja yang dipakai di semua tahap

- Claude menyusun setiap materi, lalu *agent* peninjau terpisah memeriksanya terhadap teks sumber. Hasil pemeriksaan disimpan di `review/` dan materi diberi status "siap dipakai" (log keputusan "Pemeriksaan materi `review/`").
- Kode berbahasa Inggris di `system/`; dokumen berbahasa Indonesia, istilah asing dimiringkan.
- Kode lama (`engine/`, `kb/`, `ui/`, `web/`) tidak diubah; dipakai sebagai acuan kesetaraan.
- Panggilan LLM dicatat lengkap (prompt, keluaran, token, biaya) dan dibatasi anggaran USD 15.

---

## Tahap 3. Spesifikasi representasi pengetahuan

Mulai: 2026-10-27.

### Temuan saat menyusun spesifikasi

1. **P07 (PER-11/PJ/2025) ternyata peristiwa relevan.** Tafsir K1 menetapkan pembulatan PPh 21 ke rupiah terdekat mulai Masa Januari 2025 berdasarkan PER-11/PJ/2025 Pasal 129 ayat (1) huruf a dan ayat (3) (PDF hlm. 106), sedangkan tabel peristiwa mencatat dokumen itu sebagai pengecoh X1. Pasal 130 huruf a membatasi PER-2/PJ/2024 pada masa sampai Desember 2024. PMK 81/2024 (P05) hanya mengatur pembulatan keputusan dan dokumen elektronik (Pasal 33 ayat (7), PDF hlm. 34), bukan bukti potong. Koreksi: P07 dipindah menjadi peristiwa uji **E13**, jenis T9 (prosedur hitung), sifat S1 (berlaku 2025-01-01, terbit 2025-05-22). Dengan ini T9 punya contoh nyata.

### Hasil

- [docs/spesifikasi/representasi.md](spesifikasi/representasi.md): Definisi 1–3 (KB enam komponen, aturan bitemporal berversi, hasil perhitungan dan $F_\mathit{nilai}$), ontologi (ELI, OWL-Time, PROV-O, *named graph* per versi), bahasa ekspresi 27 fungsi dengan aritmetika eksak, semantik temporal dua sumbu, resolusi konflik (peringkat → `overrides` → *posterior*), bentuk kanonik, batas ekspresivitas (7 butir), Algoritma 1.
- Koreksi korpus: P07 → E13 (T9). Uji 13, pengecoh 20.

### Bahan paper

- Bagian IV: Definisi 1–3, tabel kelas/properti ontologi, gambar ontologi (versi ASCII di §5, versi gambar di Tahap 5), tabel fungsi bahasa ekspresi, resolusi konflik, batas ekspresivitas, Algoritma 1.
- Ancaman validitas: koreksi korpus P07/E13 menunjukkan klasifikasi relevansi manual bisa keliru; dicatat sebagai bukti pentingnya penilaian relevansi berkutipan.

---

## Tahap 4. Spesifikasi akuisisi dan kontrak antarmuka

Mulai dan selesai: 2026-10-27.

### Hasil

- [docs/spesifikasi/akuisisi.md](spesifikasi/akuisisi.md): Definisi 4–9 (peristiwa, pembaruan dengan penerapan ketat dan longgar, syarat adaptif A1–A4 dengan prosedur uji, adaptivitas representasional dan operasional, mode terisolasi dan berantai dengan $H_n$, terdampak (a)/(b)/(c)), alur delapan tahap, gerbang G1–G5 dengan tanggal mulai efek dan pendaratan nilai/tanggal, generator $S^G$, detektor dampak, B3/B4/AB3/AB4 dari kandidat yang sama, konfigurasi LLM dan anggaran.
- [docs/spesifikasi/format_data.md](spesifikasi/format_data.md) dan `system/schemas/`: skema $\Delta$, skema keluaran LLM datar (`delta_llm.schema.json`, mengikuti batasan keluaran terstruktur), kasus, nilai harapan, log panggilan, hasil alur.

### Tinjauan independen

Agen peninjau terpisah memeriksa ketiga dokumen terhadap kotak "Harus didefinisikan" *skeleton* IV–V, log keputusan, dan tafsir: **41 temuan (6 blokir, 19 penting, 16 kecil)**, semuanya ditanggapi dalam versi 2 ([review/specs/spesifikasi.review.md](../review/specs/spesifikasi.review.md), [tanggapan](../review/specs/spesifikasi.tanggapan.md)). Temuan blokir yang mengubah desain:
1. lapisan perusahaan harus dipasang per kebijakan dan tidak disaring ω;
2. G4/G5 gagal untuk $\Delta$ yang menutup aturan lama → **tanggal mulai efek** $s(u)$ dan pembebasan penutupan;
3. *lex posterior* harus memakai tanggal yang stabil terhadap revisi ($t_c^0$);
4. pemilihan parameter bernama sama;
5. penerapan longgar untuk mode berantai.

Keputusan baru di Log keputusan: nilai yang dinilai untuk peristiwa berlaku surut (nilai seharusnya, penyelesaian tidak dinilai; tafsir B5 untuk E13), lapisan perusahaan, spesifikasi versi 2.

### Bahan paper

- Bagian V: Definisi 4–9, tabel gerbang (G1–G5 dengan syarat yang dijaga), alur delapan tahap, generator $S^G$, definisi terdampak.
- Bagian VI: mode terisolasi/berantai, $H_n$, B3/B4 dari kandidat yang sama, anggaran.
- Diskusi: tinjauan independen spesifikasi menemukan 6 masalah blokir sebelum implementasi; contoh konkret bahwa definisi formal perlu diuji sebelum membangun (saran panduan "titik periksa dosen").

---

## Tahap 5. Representasi dan *engine* (bagian 1: inti)

Mulai: 2026-10-27. *Commit* awal `31c3d33`.

### Hasil

- `system/pph21kbs/expr/`: bahasa ekspresi (subset Python yang aman, aritmetika `Fraction`, *float* ditolak, uang wajib bulat, `round` lima mode), katalog fungsi, pemeriksaan statis, kompilasi ke *closure*, bentuk kanonik.
- `system/pph21kbs/kb/`: rekaman bitemporal (`add`/`change`/`remove` dengan *tombstone*), `KnowledgeBase.view(ω)` yang hanya menyaring lapisan regulasi, penerapan $\Delta$ ketat dan longgar, tabel ekstraksi `rows_ref` dari `dataset/13_teks/<DOK>/tabel/`.
- `system/pph21kbs/engine/evaluator.py`: evaluasi berbasis permintaan dengan memo, deteksi siklus, titik tetap terkecil untuk *gross-up* (tafsir K3), resolusi peringkat → `overrides` → *posterior* ($t_c^0$), kunci konflik stabil, jejak dan pemenang.
- `system/pph21kbs/text.py` (teks terkunci, pencarian kutipan → halaman), `system/pph21kbs/refs.py` (konversi kasus GT3 ke format kasus), `system/tools/check_refs.py`.
- Uji unit: 9 lulus (`system/tests/test_engine_core.py`).

### Temuan saat implementasi

1. **Fungsi kumulatif.** Batas tahunan natura (bingkisan Rp3 jt, olahraga Rp1,5 jt; PMK 66/2023) dihitung kumulatif sejak Juli 2023. `sum_to_date` gagal karena bulan sebelum aturan berlaku tidak punya aturan; ditambahkan `cumulative`/`cumulative_before` yang hanya menjumlah bulan dengan aturan aktif (representasi.md §6.3).
2. **Nama fakta bertabrakan dengan fungsi** (`zakat_paid`): fakta diganti `zakat_withheld`. Aturan pemeriksaan statis ditambah.
3. **Pembulatan premi BPJS tidak diatur** regulasi mana pun → tafsir **K17** (rupiah terdekat per program per pihak).
4. **Titik tetap bersarang.** *Gross-up* membaca bruto yang sedang dievaluasi; evaluasi ulang masuk ke tingkat titik tetap baru (`fp_level`) alih-alih dianggap siklus.

### Bahan paper

- Bagian IV/VII: implementasi engine (memo, titik tetap, resolusi), aritmetika eksak; batas ekspresivitas yang ditemui (fungsi kumulatif harus ditambahkan, contoh bahwa bahasa ekspresi perlu primitif temporal).

## Tahap 5. Representasi dan *engine* (bagian 2: graf, gerbang statis, kesetaraan)

Selesai: 2026-10-27.

### Hasil

- **Knowledge graph.** [system/ontology/ontology.ttl](../system/ontology/ontology.ttl) (OWL; ELI, PROV-O, OWL-Time, SKOS), `system/pph21kbs/kb/rdf.py` (KB ↔ RDF: satu *named graph* per pembaruan, graf `kb:meta` berisi dokumen, urutan pembaruan, adopsi, dan sidik jari setiap versi). Bolak-balik KB → TriG → KB menjaga sidik jari dan setiap nilai (termasuk baris tabel dan pecahan eksak). KB emas: `dataset/12_emas/kb.trig`, 11.357 *triple*, 24 graf.
- **Engine membaca graf.** `check_refs.py` dan `check_legacy.py` memuat KB dari `kb.trig`, bukan dari kode sumber emas. GraphDB 11.5 (repositori `pph21`) dimuat lewat `system/pph21kbs/kb/graphdb.py`; bolak-balik lewat GraphDB juga menjaga sidik jari.
- **G1 (SHACL).** [system/ontology/shapes.ttl](../system/ontology/shapes.ttl): 15 *shape* inti dan 12 batasan SHACL-SPARQL untuk semua butir G1.2. Validator `system/pph21kbs/kb/shacl.py` menjalankan *shape* inti dengan pyshacl dan setiap batasan SPARQL sekali atas seluruh graf (pyshacl per *focus node* butuh beberapa menit; hasilnya setara karena `$this` hanya variabel yang diikat). KB emas: 0 pelanggaran, 0,8 detik. 16 mutasi uji, satu per syarat G1, semuanya tertangkap.
- **G3 dan pemeriksa anomali.** `system/pph21kbs/static.py`: galat (siklus dependensi yang tidak melewati aturan titik tetap, siklus `overrides`, rujukan menggantung per bulan 2012–2027, nama tak dikenal) dan peringatan (potensi konflik, aturan mati, redundan, tercakup). Pengenalan kondisi eksklusif: X/¬X, perbandingan komplementer (`a > b`/`a <= b`), kesamaan dengan konstanta berbeda. KB emas pada ω 2022–2026: 0 galat; 1 peringatan "aturan mati" per versi (2022: `REG.INPUT.ZAKAT`, zakat belum menjadi pengurang sebelum PMK 168/2023; sesudah 2023: `REG.NATURA.EXCLUDED`, fakta pencatat natura yang dikecualikan). 11 uji mutasi.
- ***Test suite* resolusi konflik.** `system/tests/test_conflict_resolution.py`: 12 uji dengan pemenang hukum yang diketahui (*lex superior* empat peringkat, adopsi aturan pilihan, kebijakan harus disebut kasus, konflik *override* hanya bila nilai berbeda, *lex specialis* termasuk transitif dan tidak menaikkan peringkat, *lex posterior* menurut `valid_from` dan $t_c^0$, revisi tidak membuat aturan lebih baru, `UnresolvedConflict` dan `RedundantRules`, masa berlaku aturan masa dan tahun, batasan menyebut aturan perusahaan).
- **Kelengkapan jejak.** `system/pph21kbs/engine/trace.py`: 8.310 nilai keluaran dari 50 kasus GT3, semuanya berjejak lengkap sampai kutipan sumber (22.370 simpul jejak, 0 masalah).
- **Analisis dampak (RQ4).** [system/ontology/queries/impact_facts.rq](../system/ontology/queries/impact_facts.rq) ($F_\Delta$ dan penutup hilir lewat jalur properti `(^pph:produces/pph:reads)*`) dan `impact_policy.rq` (label a/b/c), dipanggil `system/pph21kbs/impact.py`; pembanding B5(i) `flag_all`. 3 uji.
- **Riwayat engine (E1).** `system/tools/export_engine_history.py` → [docs/hasil/riwayat_engine.csv](hasil/riwayat_engine.csv) (21 *commit*, 19 prototipe) dan [docs/hasil/fitur_engine.csv](hasil/fitur_engine.csv) (16 kemampuan engine dan regulasi pemicunya).
- **Gambar ontologi:** [docs/gambar/ontologi.tex](gambar/ontologi.tex) (TikZ) dan `ontologi.pdf`.
- **Uji:** 53 lulus (`env/Scripts/python -m pytest -q -c system/pytest.ini system/tests`).

### Validasi terhadap acuan (engine membaca graf)

| Acuan | Kasus sama | Observasi sama | Selisih |
|---|---|---|---|
| GT3 (50 kasus, 2023–2026) | 50/50 | 2107/2107 | — |
| GT1 pengembangan (32 contoh resmi; *holdout* 14 tidak dibuka) | 22/26 dibandingkan | 665/679 | 14 observasi di 4 kasus, semuanya ralat contoh resmi yang sudah dicatat transkripsi (PER-16 I.1.3 plafon biaya jabatan, I.6.2.2 selisih Rp1, PMK 10/2025 B-3 metode biaya jabatan, PMK 168 B-I.6 dasar pengali); nilai engine sama dengan hitungan koreksi di catatan transkripsi |
| GT2 kalkulator DJP, bulanan | 15/20 | — | 5 selisih Rp1: kalkulator membuang pecahan, PER-11/PJ/2025 Pasal 129 mewajibkan rupiah terdekat (putusan sebelumnya) |
| GT2 kalkulator DJP, tahunan (A1) | — | 90/90 baris | — |

6 contoh GT1 pengembangan di luar model kasus dan tidak dibandingkan: upah mingguan (2), upah harian, rapel masa lalu, mata uang asing, natura 2016 dari pemberi kerja *deemed profit*. Rincian per observasi: `docs/hasil/acuan_gt3.csv`, `acuan_gt1_pengembangan.csv`, `acuan_gt2.csv` (`check_refs.py all --write`).

### Kesetaraan dengan engine prototipe

`system/tools/check_legacy.py` menjalankan engine prototipe (`engine/` + `kb/`, *tag* `prototipe-akhir`, tidak diubah) pada kasus yang sama ([docs/hasil/kesetaraan_engine_lama.csv](hasil/kesetaraan_engine_lama.csv)):

| Kasus | Nilai | Sama | Berbeda, dengan penjelasan |
|---|---|---|---|
| GT3 | 741 | 569 | 172: putusan adjudikasi GT3 yang sudah ada (natura PMK 66/2023 54, pembulatan TER 2025–2026 menurut PER-11 114, definisi bruto masa K14 4) |
| GT1 pengembangan | 507 | 503 | 4: definisi bruto masa termasuk bonus (K14) 2, pembulatan PPh bulanan ke bawah (K2) 1, ralat contoh resmi 1 |

Tidak ada selisih yang belum dijelaskan. Engine prototipe menolak GT3-005 dan GT3-012 (*gross-up* rezim PER-16 belum dimodelkan); engine baru menghitung keduanya sama dengan GT3. Kriteria selesai Tahap 5 terpenuhi; *tag* `representasi-v1`.

### Keputusan dan penyimpangan

1. Jalur berkas ontologi dan kueri menjadi `system/ontology/` (spesifikasi menyebut `system/kb/`); akuisisi.md dan format_data.md disesuaikan.
2. GT1 dibandingkan dengan premi dan iuran sebagai masukan (`premiums_as_billed`), sesuai cara contoh resmi menyatakannya. Contoh satu masa ditempatkan dalam tahun penuh yang mengulang komponen teratur, supaya masa itu bukan masa pajak terakhir.
3. Karyawati kawin yang diberi status K/ oleh contoh resmi dianggap memiliki keterangan suami tidak berpenghasilan (tafsir K16, contoh PER-16 I.1.3).
4. "Berhak DTP" contoh PMK 72/2025 dibandingkan dengan gabungan kelayakan padat karya dan pariwisata, karena KB memisahkan keduanya per sektor.
5. *Tag* `engine-v1` (A1) ditunda ke pembekuan alur (Tahap 11): kebijakan perusahaan di Tahap 7 mungkin masih menuntut kemampuan engine.

### Bahan paper

- Bagian IV: gambar ontologi, tabel kelas dan properti, contoh *named graph* per pembaruan, kueri dampak.
- Bagian VII (E0, validitas instrumen): tabel validasi acuan dan tabel kesetaraan di atas; uji mutasi SHACL (16/16) dan G3 (11/11) sebagai bukti gerbang menangkap pelanggaran.
- Bagian VIII (keterbatasan): enam contoh resmi di luar model kasus; peringatan aturan mati yang disengaja.
- E1 (bias pandangan belakang): `fitur_engine.csv`, setiap kemampuan engine dipetakan ke peristiwa yang membutuhkannya; kedua engine ditulis setelah semua peristiwa uji terbit.

---

## Tahap 7. Emas $\mathcal{K}^\star_n$, $\Delta^\star_n$ (bagian 1: rantai regulasi)

Mulai: 2026-10-27. Dikerjakan bersamaan dengan Tahap 5 karena validasi *engine* membutuhkan KB emas.

### Hasil

- Sumber emas sebagai kode: `system/gold_src/` (satu modul per kelompok peristiwa). Setiap kutipan diverifikasi otomatis terhadap teks terkunci `dataset/13_teks/` dan halamannya diisi otomatis; kutipan yang tidak ditemukan menghentikan *build*.
- `system/tools/build_gold.py` menulis `dataset/12_emas/delta/*.json`, `rantai.csv`, `kosakata.md`.
- Rantai: **23 pembaruan** (10 latar BG-000…BG-009, 13 peristiwa GOLD-E01…E13), **230 rekaman**, sidik jari `0d0fa5b4b1905a8e`. $\mathcal{K}^\star_0$ = rekaman dengan `recorded_on` ≤ 2022-12-31.
- Teks dan tabel ekstraksi: 91 dokumen di `dataset/13_teks/` (PKB tidak di-*commit*); tabel Lampiran PP 58/2023 (TER), PMK 10/2025 (57 KLU), PMK 72/2025 (77), PMK 105/2025 (135).

### Validasi terhadap GT3 (acuan pengembangan)

| Tahun | Kasus sama | Observasi sama |
|---|---|---|
| 2023 | 12/12 | 520/520 |
| 2024 | 13/13 | 480/480 |
| 2025 (ω 2025-12-31) | 13/13 | 559/559 |
| 2026 (ω 2026-10-27) | 12/12 | 548/548 |
| Semua (ω 2026-10-27) | **50/50** | **2107/2107** |

GT1 *holdout* (14 kasus) tidak dipakai.

### Keputusan pemodelan dalam emas

1. **DTP (E06/E10/E11).** Satu aturan pengembalian mencakup PMK 10/2025 Pasal 5 ayat (5) dan PMK 72/2025 ayat (5a): yang dikembalikan ke pegawai = max(0, kelebihan − DTP masa sebelumnya). Untuk padat karya hasilnya 0 (K13), untuk pariwisata hanya bagian Oktober–November yang tidak dikembalikan. DTP tidak di-*gross-up* (Pasal 5 ayat (1)–(2)). Kriteria penghasilan tetap diuji pada bulan pertama bekerja (K5). E10 menambah fasilitas pariwisata dengan aturan yang mengalahkan aturan fasilitas dasar (`overrides`), E11 memperpanjang validitas ke 2026 dan menambah versi tabel KLU 2026.
2. **Keringanan JKK (E07/E09).** Tabel tarif keringanan terpisah dan aturan tarif bersyarat `employer('jkk_relief_eligible')`; menang atas tarif normal dengan *lex posterior*. E09 hanya mengubah `valid_until` (perpanjangan, T1).
3. **Pembulatan (E13).** Satu parameter `pph_round_mode` = `half_up` berlaku 2025-01-01, dicatat 2025-05-22 (berlaku surut, B5).
4. **E04** menutup 12 aturan PER-16 pada 2023-12-31 (pembaruan `change`), contoh penutupan yang dibebaskan dari G5.

### Bahan paper

- Bagian VI (dataset): tabel rantai emas (`dataset/12_emas/rantai.csv`), jumlah rekaman per jenis, prosedur kutipan terverifikasi otomatis.
- Bagian VII (E0, validitas instrumen): tabel validasi GT3 di atas.
- Contoh berjalan untuk paper: E10 (pariwisata) memperlihatkan pengecualian (*lex specialis*) dan nilai surut; E13 memperlihatkan perubahan parameter berlaku surut.

---

## Tahap 7. Emas (bagian 2: pengembangan, fiktif, kebijakan)

Selesai disusun: 2026-10-27. Dikerjakan paralel oleh empat *fork* (A: D01–D13; B: FR01–FR05; C: pendukung ketenagakerjaan dan SP01–SP14; D: lima PKB dan Koja), masing-masing dengan validasi sendiri; diintegrasikan dan diperiksa ulang oleh penyusun.

### Hasil

| Bagian | Modul | Isi | Validasi |
|---|---|---|---|
| Peristiwa pengembangan D01–D13 | `dev_ptkp_jkn.py`, `dev_covid.py` | PTKP 2013/2015 (berlaku surut), JKN 2014/2016, keringanan iuran 2020, DTP COVID 2020–2021 dengan tabel KLU 440/1062/1189 terekstraksi; D08, D12, D13 kosong | 11 uji hitungan tangan termasuk contoh resmi lampiran PMK 23/2020 (Tuan A, C, D) |
| Regulasi fiktif FR01–FR05 | `fr_fiktif.py` (pembaruan sisi) | TER fiktif 2020, pembulatan PKP 2021, pencabutan biaya jabatan gilir malam (dengan latar fiktif BG-FR03), komisi 2019, plafon biaya jabatan 2022 (dua dokumen) | 17/17 contoh hitung sebelum dan sesudah sama (`check_fiktif.py`) |
| Pendukung ketenagakerjaan | `bg_support.py` (BG-010) | THR minimum Permenaker 6/2016 sebagai aturan dan batasan C10 | GT1–GT3 tidak berubah |
| Kebijakan sintetis SP01–SP14 | `pol_sintetis.py` (pembaruan sisi) | aturan perusahaan per klausul; kode konflik C1–C10 sesuai INDEX; tiga kontrol negatif tanpa konflik | 37/38 contoh (sisa: SP08-3, lihat keterbatasan) (`check_policies.py`) |
| PKB nyata | `pol_pkb.py` (pembaruan sisi) | WIKA 25/2/16, CENTEX 20/2/12, AVCO 29/5/10, TKG 17/3/14, SANSAN 12/1/11, KOJA 12/2/8 klausul (formal/sebagian/tidak, alasan di catatan pembaruan) | GT5: 67/79 observasi sama, 12/12 selisih dijelaskan (`check_refs.py gt5`) |

Rantai utama: **37 pembaruan, 278 rekaman**; pembaruan sisi: **27** (7 fiktif, 20 kebijakan). Semua GT tetap: GT3 50/50 (2107/2107), GT1 pengembangan 22/26 (14 selisih = ralat contoh resmi), GT2 15/20 (5 pembulatan) dan 90/90. Uji: 71 lulus. Tabel peristiwa kebijakan: `dataset/10_kebijakan_perusahaan/peristiwa_kebijakan.csv` (20 baris).

### Gerbang terhadap emas (laju penolakan keliru)

Setiap $\Delta^\star$ diperiksa G1–G5 terhadap basisnya (`system/tools/check_gates_gold.py`, `docs/hasil/gerbang_emas.csv`). Pemeriksaan pertama menolak banyak emas; setiap penolakan dianalisis dan diputuskan apakah emasnya salah atau gerbangnya terlalu sempit:

- **Emas salah atau kurang** (diperbaiki di emas): kutipan < 20 karakter; tanggal berlaku tidak dikutip oleh unsur itu sendiri; aturan pencatat natura yang dikecualikan tanpa efek (E02); perpanjangan aturan lingkup tahun dalam tahun yang sama tanpa efek (D07, D11); pengulangan aturan wajib oleh kebijakan (AVCO JHT 2%).
- **Gerbang terlalu sempit** (spesifikasi akuisisi versi 3): angka turunan yang dinyatakan peraturan dengan kata (PTKP = diri + kawin + tanggungan; tarif keringanan 50%), angka dan tarif yang ditulis dengan kata, desimal pendek, huruf OCR dalam angka dan tahun; pola "(sampai) dengan <Bulan> <Tahun>"; galat *engine* yang sudah ada di basis; aturan A3 yang tidak berlaku bagi lapisan perusahaan; ω evaluasi kebijakan; definisi fakta; fakta milik kebijakan sebagai keluaran kebijakan; cakupan $S^G$ (kombinasi 3–4 nilai, atribut aturan pesaing, baris masa terakhir).

### Temuan dan koreksi emas

1. **K18 (DTP dan *gross-up*):** emas E06 semula menolkan tunjangan pajak juga pada metode *gross-up*; PMK 10/2025 Ps 5 ayat (1) mewajibkan DTP dibayar tunai "termasuk dalam hal ... memberikan tunjangan PPh 21". Dikoreksi; aturan gaji bersih DTP tunai pada metode ditanggung ditambahkan (E06, E11, D05). Ditemukan oleh contoh SP06 dan GT5-CENTEX.
2. **K3 butir 4:** *gross-up* dengan metode selisih PER-16 bisa tanpa titik tetap (siklus); *engine* memilih nilai terkecil yang menutup pajaknya sendiri.
3. **Perbaikan *engine*:** konflik *override* dibandingkan dengan pemenang wajib yang sebenarnya; rekaman pembaruan kebijakan tidak disaring ω.

### RQ1 (adaptivitas representasional)

- Semua peristiwa nyata (E01–E13, D01–D13) dan fiktif (FR01–FR05) dapat dinyatakan tanpa mengubah *engine*.
- Kebijakan: klausul yang tidak diformalkan dicatat per PKB beserta alasannya. Batas representasi yang ditemukan: (i) penanggungan pajak sebagian (WIKA-22-2) tidak dapat dinyatakan terhadap aturan wajib *gross-up* penuh; (ii) tidak ada iterasi per hari (lembur harian dari data kasus); (iii) tidak ada fungsi hari kalender; (iv) aturan perusahaan tidak dapat menyatakan "paling sedikit sebesar ketentuan" (kelebihan yang sah terbaca konflik C8); (v) konvensi pembulatan 2024 sebagai parameter yang dibaca aturan wajib membuat pembulatan perusahaan 2024 terbaca C9 (SP08-3); (vi) fakta lingkup tahun milik kebijakan berlaku sepanjang tahun pajak; (vii) perubahan satuan pembulatan yang tertulis sebagai literal (FR02) butuh enam versi aturan.

### Keterbatasan dan hal terbuka

- SP08-3 dan label dampak manual vs eksekusi (134/168 pasangan sepakat; sebagian besar perbedaan pada tipe (a) karena kebijakan merujuk nilai wajib secara dinamis tanpa aturan) dibahas di Tahap 8/10 sebagai validitas label.
- GT5-WIKA-03/05 memakai bulan sebelum masa berlaku PKB; dilaporkan apa adanya.
- Pembaca kedua dan Krippendorff α: berikutnya (bagian 3).

### Bahan paper

- Bagian VI: tabel korpus emas (pengembangan, uji, fiktif, kebijakan) dengan jumlah rekaman; prosedur "emas sebagai kode" dengan kutipan terverifikasi.
- Bagian VII: laju penolakan keliru gerbang atas emas sebelum dan sesudah penyesuaian; daftar penyesuaian sebagai bukti bahwa gerbang dikalibrasi pada emas pengembangan (bukan pada keluaran LLM uji).
- RQ1: daftar batas representasi di atas; klausul kebijakan yang tidak dapat diformalkan.
- Diskusi: koreksi K18 contoh bahwa contoh hitung kebijakan menguji emas regulasi (validasi silang antarlapis).

---

## Tahap 7. Emas (bagian 3: pembaca kedua dan kesepakatan)

Dikerjakan 2026-10-27/28. Dua agen peninjau independen (bukan *fork*, tanpa konteks penyusun) dengan prosedur dua tahap: (1) pengodean buta dari teks dokumen dan basis KB (`system/tools/kb_context.py`), ditulis dan tidak diubah lagi; (2) perbandingan dengan emas. Regulasi: E01–E13. Kebijakan: SP01–SP14 buta, lima PKB diperiksa tidak buta.

### Hasil

| | Regulasi E01–E13 | Kebijakan SP01–SP14 |
|---|---|---|
| Unsur emas / unit pembaca | 73 / 73 | 44 aturan / 50 baris |
| Putusan | sama 55, tafsir 18, peninjau benar 8, ragu 2 | sama 31, emas benar 8, tafsir 5, peninjau benar 1, ragu 1 |
| Kesepakatan kehadiran unsur | 82% | 91% |
| α `valid_from` (unsur tambahan, 29) | 0,79 | — |
| α `valid_until` | 1,00 | — |
| Kesepakatan nilai | 90% | 100% |
| α kode konflik (κ) | — | 0,73 (0,73) |

`docs/hasil/kesepakatan_emas.json` (`system/tools/review_agreement.py`; α Krippendorff nominal di `system/pph21kbs/analysis/agreement.py`, diuji pada contoh Krippendorff 2011, α = 0,743). α kehadiran tidak dilaporkan karena paradoks prevalensi (tidak ada satuan "keduanya tidak membuat unsur").

### Koreksi emas dari pembacaan kedua

Regulasi (8 + 2): natura bingkisan/olahraga Januari–Juni ikut batas setahun (K12.3); batas kupon makan Pasal 5 ayat (4) huruf b; natura tetap dalam uji DTP Rp10 jt (K5); syarat "tidak menerima DTP lain"; pembulatan PPh tahunan sebagian tahun sejak 2025; putusan baru tafsir_korpus B6 (penyajian DTP Desember lebih potong). Kebijakan: SP08 zakat, SP04 dipersempit ke apartemen (E02 kini memisahkan fakta natura rumah), WIKA dasar iuran hanya bila lebih sempit, AVCO kacamata dan potongan mangkir hari keenam. Masalah PKB lain dicatat sebagai keterbatasan (tanggapan: `review/gold/regulasi.tanggapan.md`, `review/gold/kebijakan.tanggapan.md`). Semua acuan tetap: GT3 50/50, GT1 22/26 (ralat resmi), GT2 15/20 + 90/90, GT5 67/79 (12 dijelaskan), contoh SP 37/38.

### Perbaikan alur dari pembacaan kedua

Konteks LLM tidak memuat aturan yang diubah kebijakan bila dokumen memakai singkatan (JKK, JP, JHT): `context.py` kini mencocokkan token id rekaman dan menyembunyikan rekaman yang berakhir lebih dari setahun sebelum tanggal dokumen.

### Ancaman validitas

Penjangkaran pada emas peristiwa sebelumnya (basis yang sama dengan LLM), E13 tidak sepenuhnya buta, tafsir K/B bersama, satuan tidak satu-satu. Semuanya dilaporkan; α dibaca sebagai kesepakatan di bawah basis dan tafsir yang sama.

### Bahan paper

- Bagian VII (keandalan $\Delta^\star$): tabel di atas, prosedur dua tahap, daftar koreksi sebagai bukti protokol koreksi emas (*skeleton* butir "Protokol koreksi emas").
- Diskusi: pembaca kedua menemukan kesalahan yang lolos semua acuan independen (GT1–GT5 tidak punya kasus yang menyentuhnya), contoh keterbatasan validasi berbasis contoh.

---

## Tahap 9. Alur akuisisi (bagian 1: komponen dan klien tiruan)

Mulai: 2026-10-27, dikerjakan sejajar dengan Tahap 7 (emas menjadi bahan kalibrasi gerbang).

### Hasil

Paket `system/pph21kbs/pipeline/`:

| Modul | Isi |
|---|---|
| `select.py` | pemilihan segmen: skor leksikal per akar panjang segmen dari leksikon KB + istilah tetap; pembuka/penutup selalu (dipotong 3.000 token), lampiran bertabel terekstraksi diganti deskripsi tabel; anggaran 14.000 token |
| `context.py` | konteks KB dari graf: kosakata, katalog fungsi, nama parameter dan tabel, rekaman relevan + tetangga satu langkah lewat SPARQL |
| `prompts.py` | prompt relevansi, penyusunan, perbaikan (contoh generik, bukan dari peristiwa uji) |
| `llm.py` | klien Anthropic (`output_config.format` JSON *schema*, `effort`, *prompt caching*), OpenAI (Responses API, *strict*), tiruan; log JSONL per panggilan, berkas *prompt* per SHA-256, penjaga anggaran USD 15 total |
| `convert.py` | keluaran datar LLM ↔ $\Delta$; bolak-balik semua emas utuh |
| `gates.py` | G1 (skema, penerapan ketat, SHACL), G2 (kutipan, pendaratan angka dan tanggal), G3 (statis), G4 (regresi, galat baru), G5 (non-vakuitas, tanggal dan subjek tercermin), tanggal mulai efek $s(u)$ |
| `sg.py` | generator $S^G$ (lihat spesifikasi versi 3) |
| `consensus.py` | pengelompokan perilaku atas gabungan $S^G$, seri → *abstain* |
| `run.py` | satu dokumen: relevansi → $m$ kandidat → gerbang → satu perbaikan → konsensus → rekaman hasil |

Tambahan: `system/pph21kbs/corpus.py` (tabel peristiwa regulasi, fiktif, kebijakan), `system/tools/kb_context.py` (tampilan yang dilihat LLM, untuk pembaca kedua). Uji klien tiruan (`system/tests/test_pipeline.py`, 7): emas sebagai keluaran diterima, pengecoh dengan kutipan sah → $\Delta$ kosong (kutipan palsu → *abstain*), kutipan palsu gagal G2 lalu diperbaiki, seri → *abstain*, penjaga anggaran, isolasi kode alur dari emas dan acuan.

### Penyimpangan

- Pemeriksaan pertama pemilihan segmen dilakukan pada beberapa dokumen uji (PMK 10/2025, PP 58/2023, PMK 168/2023, PER-11/PJ/2025, PMK 81/2024) sebelum disadari; perubahan yang dibuat bersifat umum (semua segmen bila muat, kepadatan skor, batas panjang penutup, istilah "pembulatan", "klasifikasi lapangan usaha", "insentif" yang juga ada di dokumen pengembangan D05–D11 dan FR02). Pemeriksaan selanjutnya hanya pada dokumen pengembangan. Dicatat sebagai ancaman validitas kecil (kebocoran desain), bukan penyetelan pada hasil.

### Uji dengan LLM sungguhan (kriteria selesai Tahap 9)

Jalan `dev-smoke`, peristiwa pengembangan D01 (PMK 162/2012), Claude Opus 5.5, $m = 1$ (`system/tools/run_event.py dev-smoke D01 --m 1`; log `experiments/dev-smoke/`):

1. Percobaan pertama: relevansi berhasil; penyusunan ditolak API dengan galat 400 "The compiled grammar is too large" karena skema keluaran LLM versi 1 terlalu besar. Skema diganti versi 2 (atribut khusus jenis unsur sebagai pasangan nama–nilai; format_data.md §2.3); bolak-balik 64 $\Delta^\star$ melalui bentuk baru utuh.
2. Percobaan kedua: kandidat pertama lolos G1–G4 dan gagal G5 (parameter tambahan kawin yang nilainya sama dengan tambahan tanggungan, tidak berefek); putaran perbaikan menghapusnya; hasil lolos G1–G5 dan diterapkan. LLM memilih representasi PTKP berkomponen (diri + tambahan × jumlah dari tabel status) yang berbeda bentuk dari emas (tabel PTKP lengkap) tetapi setara perilakunya. Contoh nyata mengapa konsensus dan penilaian berdasar perilaku, bukan bentuk.
3. Biaya: relevansi USD 0,012; penyusunan USD 0,144 (tulis *cache* 12.863 token, keluaran 3.950 token); perbaikan USD 0,129. Total semua jalan sejauh ini USD 0,32 dari 15.
4. Perbaikan sesudahnya: putaran perbaikan memakai *system prompt* yang sama dengan penyusunan (instruksi perbaikan dipindah ke pesan pengguna) agar awalan ber-*cache* dibaca, bukan ditulis ulang; *prompt* yang memuat teks PKB disimpan di `prompts_private/` yang tidak di-*commit*.

### Bahan paper

- Bagian V: alur delapan tahap sebagaimana diimplementasikan; skema keluaran LLM dan alasannya (batas tata bahasa keluaran terstruktur).
- Bagian VI/VII: biaya per panggilan terukur sebagai dasar perkiraan anggaran (Tahap 11).
- Contoh kualitatif: D01, representasi berbeda tetapi setara perilaku.

---

## Tahap 10. Alat analisis, penilaian, dan pembanding non-LLM

Dikerjakan 2026-10-27/28, sebelum data uji disentuh.

### Hasil

| Berkas | Isi |
|---|---|
| `system/pph21kbs/analysis/stats.py` | Clopper–Pearson (dua sisi) dan batas atas satu sisi; Newcombe (berpasangan dan tidak berpasangan, Wilson); McNemar eksak; uji non-inferioritas; Wilcoxon bertanda; *bootstrap* klaster; Holm; *pass@k* tak bias; efisiensi seleksi η; $F_\beta$ dan $F_2$ "tandai semua" |
| `system/pph21kbs/analysis/agreement.py` | α Krippendorff nominal, κ Cohen |
| `system/pph21kbs/analysis/evaluate.py` | penilaian $\hat{\Delta}$ pada $S^E$: hasil benar/salah/*abstain*, tupel salah dipecah A2, A3$_t$, A3$_\omega$, A4, galat *engine* baru |
| `system/pph21kbs/analysis/conditions.py` | kondisi pembanding dari kandidat yang sama (tanpa panggilan LLM baru): B3, B4, AB3 (tanpa G5, tanpa G4, tanpa perbaikan), AB4 (pertama lolos, konsensus, seleksi sempurna sebagai batas atas) |
| `system/tools/score_run.py` | SER/CAR/ABS per kondisi dan lapisan, pengecoh, *pass@1*, *pass@m*, *1@m*, η |
| `system/tools/run_chain.py` | E3 mode berantai: $H_n$, kesalahan baru, OAR, komponen mekanis, varian *abstain* (tetap/peninjau sempurna) |
| `system/tools/rq4_labels.py` | label eksekusi (a)/(b)/(c) pasangan kebijakan × peristiwa, detektor, B5(i), B5(ii), κ terhadap label manual |
| `system/tools/b1_maintenance.py` | B1: waktu dan ukuran perubahan kalkulator sumber terbuka saat TER |
| `system/pph21kbs/mutation.py`, `system/tools/mutation_score.py` | operator mutasi: nilai, tanggal mulai, tanggal akhir, kondisi, buang kondisi, lapisan, modalitas, cabut |

Uji `system/tests/test_analysis.py` (7): nilai acuan pustaka (Clopper–Pearson, contoh tidak berpasangan Newcombe 1998 = (0,0524; 0,3339), α Krippendorff 2011 = 0,743), sifat (monoton, simetri, rentang), McNemar dan Holm pada kasus kecil.

### B1 (pemeliharaan kalkulator hand-coded saat TER)

`docs/hasil/b1_pemeliharaan.csv`: dari dua repositori yang sudah ada sebelum PP 58/2023 (27 Desember 2023), `open-synergy` memasukkan TER 26 hari kemudian (15 berkas, 163 baris, 7 fungsi; 2 *commit* perbaikan sesudahnya) dan `pajakin` 915 hari kemudian (3 berkas, 504 baris, 8 fungsi). Tiga repositori lain lahir sudah dengan TER (340–1.411 baris). Sisi *knowledge base*: $\Delta^\star$ E03 (7 unsur baru) dan E04 (1 baru, 12 diubah), tanpa perubahan *engine*.

### Bahan paper

- Bagian VI (rencana analisis): daftar uji di atas sesuai tabel uji *skeleton*; semua alat diuji sebelum data uji dibuka.
- Bagian VII (B1): tabel di atas sebagai pembanding biaya pemeliharaan; kesimpulan hanya deskriptif (lima repositori).

---

## Tahap 11. Kalibrasi pada data pengembangan dan pembekuan

Dikerjakan 2026-10-28 00:40–01:50 WIB. Hanya peristiwa pengembangan yang pernah dikirim ke LLM: D01, D05, FR01, PKB Koja
(diperiksa dari semua `experiments/*/calls.jsonl` sebelum pembekuan).

### Jalan kalibrasi

| Jalan | Peristiwa | $m$ | Hasil | Biaya USD |
|---|---|---|---|---|
| `kalibrasi-1` | D05 (PMK 23/2020, DTP COVID) | 3 | *abstain*: ketiga kandidat ditolak G5 (subjek KLU); sesudah perbaikan gerbang ketiganya lolos tetapi salah 2–3 dari 363 tupel $S^E$ pengembangan (tanpa NPWP masih DTP; bulan THR pegawai keluar; DTP *employer-borne* bulan THR) | 0,62 |
| `kalibrasi-1` | FR01 (TER fiktif) | 3 | diterapkan; ketiga kandidat lolos dan benar pada 454 tupel (peristiwa fiktif: tidak mungkin dihafal) | 0,71 |
| `kalibrasi-1` | PKB Koja | 3 | relevansi "tidak relevan": teks yang terpilih hanya pembuka (segmentasi gagal) | 0,04 |
| `kalibrasi-2` | PKB Koja | 1 | sesudah segmentasi diperbaiki: relevan; kandidat lolos sesudah perbaikan (G2 tarif 127/10000, lalu G5 tanggal 2012) tetapi berbeda dari emas di semua kasus $S^G$ (7 unsur vs 17: definisi upah dasar memakai komponen yang tidak ada, faktor upah ditahan, pembayaran tahunan, bonus proporsional terlewat) | 0,60 |

Total LLM sampai pembekuan: USD 2,29 dari 15. Uji Batch API sebelumnya: dua *batch* dibatalkan tanpa satu permintaan pun
diproses dalam 20–33 menit (biaya nol).

### Perubahan alur dari kalibrasi (sebelum pembekuan)

1. G5 subjek KLU: hanya kode lima digit yang disebut yang diperiksa.
2. `build_texts.segment`: judul pasal bertajuk khusus PKB; Koja 1 → 137 segmen, Centex 2 → 56, Taekwang 2 → 91, AVCO
   150 → 263. Regulasi tidak berubah (pola longgar memecah "PASAL 25" di tabel).
3. G5 tanggal mulai sebelum 2013 diperiksa pada Januari 2013 (batas cakupan $S^G$).
4. G2: tarif tertulis sebagai bilangan bulat per pangkat sepuluh.
5. Relevansi tanpa *cache*; dokumen nyata sinkron (*cache* membuat draf ke-2 dan seterusnya setara harga *batch*),
   pengecoh lewat *batch*.
6. Konverter menolak draf kosong untuk dokumen yang dinilai relevan; uji `BatchDispatcher` dengan API tiruan.

### Ukuran

- *pass@1* kalibrasi 3/6 (kandidat benar pada $S^E$ pengembangan); Koja tidak punya $S^E$.
- Token: sebagian besar keluaran adalah penalaran (rasio karakter JSON per token 1,1–1,5); draf D05 3,3 ribu token
  keluaran, FR01 10 ribu, Koja 6,7 ribu.
- Daya H2b: efek minimum ~0,45 (`docs/PRAREGISTRASI.md` §9).

### Keputusan alokasi

$m = 3$ regulasi uji, $m = 2$ PKB uji, pengecoh hanya relevansi lewat *batch*; kebijakan buatan, kontrafaktual, dan
model kedua hanya dari sisa anggaran. Rinciannya di pra-registrasi §8.

### Bahan paper

- Bagian VI (kalibrasi): tabel di atas; setiap perubahan alur berasal dari data pengembangan.
- Diskusi: kandidat yang lolos semua gerbang tetapi salah perilaku sudah muncul di pengembangan (D05, Koja). Gerbang
  memeriksa konsistensi dengan dokumen dan non-vakuitas, bukan kelengkapan.
- Keterbatasan: anggaran memaksa $m$ lebih kecil dari rancangan dan menghapus ablasi serta model kedua.

---

## Tahap 8 (penutup) dan 13. Kecukupan $S^E$ dan E0, validasi instrumen

Dikerjakan 2026-10-28 01:00–02:30 WIB, sesudah pembekuan alur dan sebelum hasil E2 dinilai.

### *Mutation score* (`docs/hasil/mutasi.csv`, `mutasi_kesetaraan.csv`, `mutasi_ringkasan.json`)

| | Jumlah |
|---|---|
| Mutan (tidak *stillborn*) | 290 |
| Terbunuh $S^E$ awal | 157 (0,54 mentah) |
| Kemungkinan setara (tidak terbedakan pada $S^G$ emas dan mutan) | 116 |
| Terbedakan tetapi lolos $S^E$ → kasus terarah | 17 (E02 4, E06 8, E11 5) |
| Skor non-setara sebelum / sesudah kasus terarah | 0,90 / 1,00 (diverifikasi ulang) |

Per peristiwa sebelum penambahan: E06 0,79 dan E11 0,77 (di bawah ambang 0,80), E02 0,89, lainnya 1,00. Operator
dengan mutan setara terbanyak: modalitas (tanpa pesaing, *wajib* → *bawaan* tidak berefek), tanggal akhir dan tanggal
mulai (E04 menyatakan ulang aturan E03 yang sudah berlaku pada tanggal yang sama). Alat: `system/tools/mutation_equivalence.py`.

### GT1 *holdout* (sekali pakai; `docs/hasil/acuan_gt1_holdout.csv`)

14 berkas *holdout*: 1 tanpa transkripsi kanonik (PER16-I.5, banyak pemotong), 3 di luar model kasus (mata uang asing,
komponen belum dipetakan), 10 dibandingkan: **6/10 kasus sama, 221/235 observasi sama**. Adjudikasi selisih:

| Kasus | Selisih | Putusan |
|---|---|---|
| PMK10-B-4 (2025) | `dtp_eligible` engine benar, acuan salah | **emas salah**: kriteria DTP memakai penghasilan tetap menurut kontrak, bukan yang dibayar sesudah sanksi (Lampiran B angka 4 PMK 10/2025). Dikoreksi (lihat di bawah) |
| PER16-I.1.4 (2016) | PTKP 72 jt vs 54 jt | **pengonversi acuan**: karyawati kawin tanpa keterangan suami tidak berpenghasilan diberi sertifikat; `refs.gt1_case` kini membaca `suami_tidak_berpenghasilan_terbukti` |
| PER16-I.1.2, I.1.4 (2016) | `employee_pension_contributions` | pemetaan observasi: acuan memisah iuran pensiun dan JHT, fakta engine menjumlahkannya; pajak tidak terpengaruh. I.1.2 juga ralat dokumen (200.000 → 100.000) |
| PER16-I.1.2 | PPh 126.287 vs 126.288 | pembulatan setengah rupiah (contoh membulatkan ke atas; tafsir pembulatan PER-16 yang sama dengan GT1 pengembangan) |
| PER16-II.1.1 (2016) | PPh masa 577.083 vs 50.000 | **emas latar salah, belum dikoreksi**: pegawai pensiun Juni yang bulan kerjanya sudah diketahui disetahunkan atas 6 bulan; aturan latar hanya menangani pegawai baru. Di luar tahun uji (2023–2026), dilaporkan sebagai keterbatasan |

Sesudah koreksi: **7/10 kasus, 226/235 observasi** (`acuan_gt1_holdout_koreksi.csv`). Syarat lulus E0 untuk domain uji
terpenuhi (tidak ada selisih "emas salah" yang belum diselesaikan pada tahun 2023–2026; satu kesalahan latar 2016 tercatat).

### Koreksi emas (protokol prareg §6)

- `REG.DTP.INCOME_TEST` (E06, berlaku juga di E10/E11 lewat perubahan): `employee('contract_fixed_income')` bila
  kasus menyatakannya, selain itu penghasilan tetap bulan pertama. Sumber: kutipan Lampiran B angka 4 PMK 10/2025.
- Emas dibangun ulang (sidik jari 07765b1a51716e1e), acuan pengembangan tetap (GT3 50/50, GT1 22/26, GT2 15/20 + 90/90,
  GT5 67/79), gerbang emas E06/E10/E11 dan kontrafaktual lolos.
- $S^E$: kasus tanpa atribut kontrak tidak berubah nilainya; ditambah 2 kasus terarah per E06 dan E11 (kontrak di atas
  dan di bawah batas). Semua kondisi E2 dinilai dengan emas yang sudah dikoreksi.
- Jumlah koreksi emas sesudah pembekuan: 1 (ditambah 1 perbaikan pengonversi acuan).

### Bahan paper

- Bagian VII (keandalan instrumen): tabel mutasi dan tabel adjudikasi *holdout*; contoh nyata protokol koreksi emas
  (kesalahan yang lolos semua acuan pengembangan dan pembaca kedua, ditemukan oleh *holdout*).

---

## Tahap 15–17. E2 (akuisisi terisolasi), E3 (berantai), E4 (dampak lintas lapis)

Dijalankan 2026-10-28 01:50–03:30 WIB dengan alur beku (`alur-beku`), emas sesudah koreksi E0. Anggaran habis:
USD 15,016 dari 15 (selisih 1,6 sen dari permintaan *batch* yang selesai saat dibatalkan; tercatat di
`experiments/batal-batch/`).

### E2 (`experiments/e2-regulasi`, `e2-pkb`, `e2-pengecoh`; `docs/hasil/e2_ringkasan.json`)

| Kondisi | Regulasi (13) SER / CAR / ABS | PKB (5) SER / CAR / ABS | Gabungan (18) SER / CAR |
|---|---|---|---|
| Usulan | 3 / 8 / 2 | 0 / 0 / 5 | 3 / 8 |
| B3 (pertama lolos G1–G2) | 4 / 8 / 1 | 3 / 0 / 2 | 7 / 8 |
| B4 (mayoritas tanpa gerbang) | 3 / 9 / 1 | 0 / 0 / 5 | 3 / 9 |
| AB4 seleksi sempurna (batas atas) | 0 / 8 / 5 | 0 / 0 / 5 | 0 / 8 |

- H2a: batas atas satu sisi SER usulan 3/18 = 0,377 > θ₂ = 0,25 → **tidak diterima**.
- H2b CAR: usulan 8/18 sama dengan B3, satu di bawah B4 (McNemar satu sisi p = 0,75 terhadap B3 dan 1,0 terhadap B4; Holm 1,0) → **tidak diterima**.
- H2b non-inferioritas SER (δ_S = 0,10): terhadap B3 terpenuhi (selisih −0,222, CI Newcombe −0,428–0,004);
  terhadap B4 tidak (0, CI −0,153–0,153).
- Kesalahan senyap usulan: E02 (nilai natura bingkisan/perumahan pada bruto, 52 tupel), E07 (premi JKK keringanan
  untuk sebagian kelompok risiko, 42), E11 (natura kendaraan tidak masuk uji penghasilan tetap DTP, 2). *Abstain*:
  E04 (tidak ada kandidat lolos), E06 (tiga kandidat lolos, tiga perilaku).
- *pass@1* 0,667, *pass@m* 0,692, *1@m* 0,615 (regulasi).
- Koreksi emas E0 tidak mengubah hasil usulan mana pun (kesalahan E11 ada di kasus $S^E$ biasa).
- Pengecoh: 11 dijalankan (sisanya terhenti anggaran), positif palsu 5/11 (CI 0,17–0,77), salah diterapkan 1/11
  (P01 PP 49/2023: LLM menurunkan premi JKK di bruto karena rekomposisi JKP; tafsir_korpus A1 menyatakan Δ kosong).
  Empat keluaran *batch* yang selesai saat dibatalkan juga menilai P13, P14, P17, P21 tidak relevan (tambahan,
  tidak dipakai dalam angka utama).
- Biaya per dokumen: regulasi USD 0,12–1,87 (E04 dengan tabel TER termahal), PKB 0,47–0,90, pengecoh 0,04–0,45.

### E3 (`experiments/e3-tetap`, `e3-sempurna`)

Mode berantai dari $\mathcal{K}^\star_0$ (rekaman sampai 2022), 150 kasus $S^E$ per tahun, hasil terisolasi E2 sebagai
$\hat{\Delta}_n$ (tanpa pembangkitan ulang: anggaran habis). OAR 22/24 = 0,917 (CI 0,730–0,990; batas bawah satu sisi
0,760) → **H3a diterima** (θ₃ = 0,75). Kesalahan baru: E02 (15 tupel), P01 (264). Kesalahan bertahan sampai akhir:
579 tupel salah pada peristiwa terakhir (hampir seluruh sampel), terutama dari P01. Varian peninjau sempurna sama
persis karena E04 dan E06 hanya menyentuh tupel yang sudah salah. Komponen mekanis = kesalahan baru (tidak ada
pembangkitan ulang sehingga komponen kontekstual dan H3b tidak diukur). E09 (dan E10 pada varian tetap) diterapkan secara
longgar (Δ terisolasi tidak berlaku ketat pada $\mathcal{K}^{\mathrm{sis}}$).

### E4 (`docs/hasil/rq4_label.csv`, `rq4_ringkasan.json`)

134 pasangan, 33 positif. Detektor: presisi 0,71, *recall* 0,91 (CI 0,75–1,00), $F_2$ 0,862. B5(i) $F_2$ 0,868, B5(ii)
0,669. **H4a diterima, H4b tidak** (selisih terhadap B5(i) −0,006, CI −0,110–0,058; terhadap B5(ii) +0,193, CI
0,062–0,400). κ terhadap label manual ≈ 0 (pengertian dampak berbeda; lihat `docs/BAHAN_PAPER.md`). Evaluasi memakai
query yang sama di GraphDB karena rdflib ~10 menit per pasangan; kesetaraan diuji (`test_impact.py`).

### Bahan paper

Seluruh angka di atas dan tafsirnya ada di `docs/BAHAN_PAPER.md` bagian VI–VIII.
