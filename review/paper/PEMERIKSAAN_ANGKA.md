# Pemeriksaan angka dan klaim `paper/draft/paper.tex`

Pemeriksa: agen independen, 2026-10-29. Tidak ada berkas lain yang diubah. Tidak ada panggilan API LLM.
Angka dihitung ulang dari berkas mentah dengan `env\Scripts\python` dan `system/pph21kbs/analysis/stats.py`
(`clopper_pearson`, `upper_bound`, `newcombe_paired`). Nomor baris merujuk ke `paper/draft/paper.tex` (821 baris).

## Ringkasan

| Tingkat | Jumlah |
|---|---|
| A. Angka, satuan, atau fakta salah | 6 |
| B. Klaim berlebihan | 7 |
| C. Catatan (*caveat*) yang hilang | 9 |
| D. Kata-kata minor | 5 |

**Putusan hipotesis: kedelapan putusan sesuai ambang pra-registrasi** (rincian di bagian E). Catatan untuk H3a: putusan
"diterima" mengikuti aturannya, tetapi penetapan rantai transplantasi sebagai analisis terdaftar adalah tafsiran (B7).

Yang **cocok persis** dengan berkas hasil (tidak dirinci lagi di bawah):
- Abstrak dan kesimpulan: 16/16 (0,829), SER 3/18 (batas atas 0,377), CAR 8/18 (CI 0,215–0,692), OAR 31/33 (0,821)
  dan 23/33 (0,540), *recall* 0,91 (0,75–1,00).
- Tabel korpus: semua |Δ*| (rantai.csv, sisi.csv), hasil E2 per peristiwa, baris P, PKB, SP, dan CF. Rantai 37 pembaruan,
  282 rekaman, 27 pembaruan sisi. Tujuh peristiwa terbit pada 2025.
- Tabel E2: ke-12 baris (SER, CAR, ABS, cakupan, risiko selektif) cocok dengan `e2-*/scores.csv`. McNemar p = 0,75 dan 1,0,
  NI B3 [−0,428; 0,004], NI B4 [−0,153; 0,153]. *pass@1* 0,667, *pass@m* 0,692, *1@m* 0,615, η = −2,0. Positif palsu
  7/20 (CI 0,154–0,592). Kontrafaktual 1/1/2, hafalan 0/6. Kebijakan buatan 5/6/3, B3 salah 7, B4 salah 2. Jalan kedua
  8/2/3. m = 5 (E02 → *abstain*, Taekwang → salah). Model kedua 7/2/4 dan PKB Sansan. Biaya per dokumen.
- Tabel E1: ketiga varian dan CP-nya (16/16 [0,794; 1,000] 0,829; 15/16 [0,698; 0,998] 0,736; 8/16 [0,247; 0,753] 0,279),
  100 contoh.
- Tabel E3: OAR, CI, batas bawah, OAR regulasi 12/13 dan 5/13, daftar peristiwa dengan kesalahan baru, interim 22/24
  (0,760), H3b 29 lawan 0 pada E03, E09, E10, E11. Satuannya salah (A1).
- Tabel RQ4: semua presisi, *recall*, F2, CI, selisih F2, κ = −0,018, pola abc 16 / a 7 / ac 7 / b 3, tiga pasangan terlewat.
- Validasi instrumen: GT3 50/50 dan 2.107/2.107, GT1 22/26 (14 selisih), GT2 15/20 (lima selisih Rp1) dan 90/90,
  GT5 67/79, *holdout* 6/10 221/235 → 8/10 232/235. Mutasi 290/157/116, 0,90, E06 0,79, E11 0,77, 17 kasus terarah.
  Kutipan 23/28 (0,631–0,939). AB5 7/319. AB1 1 dari 6 kandidat, 150/150. B2 76/100 (0,664–0,840), 97/100, USD 0,068.
  B1 26 dan 915 hari. $S^E$ 2.398 kasus (45/42/45/43 kombinatorial, 3-arah 0,62–0,64).
- Semua 52 kunci `\cite` ada di `paper/latex/references.bib` atau `regulasi.bib`. `paper.log` tidak mencatat rujukan
  tak terdefinisi.
- Tiga rujukan baru diperiksa ke Crossref dan cocok (judul, tahun, wadah, halaman):
  `gupta2024editing` (Findings of ACL 2024, 15202–15232), `li2022alphacode` (Science 378(6624), 1092–1097, 2022),
  `xin2021abstention` (ACL-IJCNLP 2021 Vol. 1, 1040–1051).

## A. Angka, satuan, atau fakta salah

**A1. Satuan E3 bukan tupel, melainkan kasus (pegawai-tahun).** Baris 580–581 (definisi), 718, 734–736, 741, 812.
- Naskah: "15 tupel", "264 tupel", "579 dari 600 tupel", "93 dari 600", "29 tupel kesalahan terpicu".
- Seharusnya: `system/tools/run_chain.py` `wrong_set()` mengembalikan himpunan `case_id`, satu per kasus yang punya
  observasi salah. Kolom `cases` di `experiments/e3-*/chain.csv` (300/450/600) adalah jumlah kasus sampel rantai
  (150 per tahun). Jadi 579 dari 600 **kasus**, dan 29 **kasus** kesalahan terpicu. Di E2, `wrong_tuples` memang tupel
  (misalnya E02 52 dari 1.256), sehingga naskah memakai satu kata untuk dua satuan berbeda. `docs/BAHAN_PAPER.md` membawa
  kesalahan yang sama. Perbaiki istilahnya, atau ubah definisi OAR dan $I_n$ menjadi per kasus.

**A2. Tabel E3, baris 736: "Kesalahan terpicu — tidak diukur" untuk rantai transplantasi.**
- Seharusnya: `experiments/e3-tetap/chain_summary.json` mencatat `triggered_total: 0` dan `mechanical_total: 279`
  (E02 15 + P01 264). Batas derau tidak dihitung karena `--iso2` tidak diberikan. Lebih tepat ditulis "0, komponen mekanis;
  batas derau tidak dihitung". Angka ini juga relevan bagi pembahasan: komponen mekanis kesalahan terpicu pada rantai
  transplantasi nol. Pada rantai pembangkitan ulang kolom `mechanical` tidak nol (E11 135, E13 89, E10 2), dan ini tidak
  dilaporkan.

**A3. Baris 513: "Δ* [kebijakan] disusun dan diperiksa dengan cara yang sama seperti dokumen regulasi".**
- Seharusnya: `docs/LOG_PENELITIAN.md` Tahap 7 menyatakan "Kebijakan: SP01–SP14 buta, lima PKB diperiksa tidak buta".
  Lima PKB nyata tidak mendapat pengodean ulang buta seperti E01–E13.

**A4. Baris 785: "Nilai tambah graf pada RQ4 dalam data ini terbatas pada presisi."**
- Seharusnya: menurut `docs/hasil/rq4_ringkasan.json`, terhadap pembanding tanpa graf B5(ii), detektor justru menang pada
  *recall* (0,91 lawan 0,64) dan F2 (+0,193, CI 0,062–0,400), tetapi **kalah** pada presisi (0,71 lawan 0,84). Keunggulan
  presisi (0,71 lawan 0,57) hanya ada terhadap B5(i), dan B5(i) sendiri memakai penutup hilir $F_\Delta$ di graf.
  Kalimat ini membalik arah temuan.

**A5. Baris 402: penulis perubahan tak terlihat "hanya membaca taksonomi perubahan".**
- Seharusnya: `review/unseen_changes/SEGEL.md` menyebut agen itu membaca "taksonomi perubahan (bagian 0–1) dan dataset
  regulasi".

**A6. Baris 647: "Pembacaan kedua menghasilkan delapan koreksi emas regulasi."**
- Berkas: `kesepakatan_emas.json` mencatat 8 putusan `peninjau_benar`, tetapi `LOG_PENELITIAN.md` Tahap 7 menulis
  "Regulasi (8 + 2)". Pastikan apakah koreksinya 8 atau 10, lalu samakan.

## B. Klaim berlebihan

**B1. Keunggulan SER atas B3.** Baris 781 ("Gerbang dan konsensus menekan pembaruan salah dibanding pemilihan pertama"),
812 ("keunggulannya atas pembanding hanya berupa SER yang lebih rendah daripada B3"), juga 712 dan 158 BAHAN.
- Selisih berpasangan −0,222 punya CI Newcombe [−0,428; 0,004], jadi nol masih termasuk. Pasangan sumbang 0 lawan 4,
  sehingga McNemar eksak satu sisi p = 0,0625. Yang terbukti hanya non-inferioritas, bukan SER yang lebih rendah. Tulis
  "secara titik lebih rendah (3 lawan 7), tetapi selisihnya belum bermakna".
- Baris 812, "aman terhadap pemilihan naif": B4 (suara terbanyak tanpa gerbang, juga naif) punya SER yang sama (3/18) dan
  CAR lebih tinggi (9/18). Klaim ini hanya berlaku terhadap B3.

**B2. "Kesalahan memang merambat" (baris 783) dan "Pada rangkaian nyata, kesalahan merambat" (baris 812).**
- Dasarnya satu rantai pembangkitan ulang (R = 1). Batas derau berasal dari hanya dua jalan terisolasi, dan pra-registrasi
  §3 menetapkan H3b sebagai deskriptif.
- Dari 29 unit terpicu, 26 ada di E10 (2) dan E11 (24). Di kedua peristiwa itu rantai *abstain*, sehingga KB tidak
  diperbarui (`e3-bangkit-ulang/chain.csv`). Itu kegagalan memperbarui dalam konteks berantai, bukan pembaruan salah yang
  menjalar. Sisanya E03 (1) dan E09 (2).
- Usul: "kesalahan terpicu teramati di atas batas derau pada satu rantai, sebagian besar akibat *abstain*".

**B3. Peran konteks KB dan formalisasi dari nol.** Baris 772 ("Konteks KB berperan besar") dan 791 ("jauh lebih mudah
daripada formalisasi dari nol").
- AB2 lawan usulan berbeda dua dokumen pada SER (5 lawan 3) dan dua pada CAR (6 lawan 8). Pasangan sumbang SER 2 lawan 4
  (McNemar dua sisi p ≈ 0,69), CAR 2 lawan 0 (p = 0,5). Analisisnya eksploratori dan ditambahkan lewat amandemen.
- AB1 hanya dua keadaan dan enam kandidat. Keadaan 2024 direkonstruksi dari log jalan yang terhenti
  (`experiments/e2-ab1/ab1_2024_dari_log.json`: "run stopped before the result record"). Masukannya juga berbeda
  (seluruh dokumen yang berlaku, 15 dokumen untuk 2023), sehingga efek konteks KB tercampur dengan ukuran tugas.
  Perlunak menjadi "petunjuk".

**B4. Selisih varian tanpa konvensi disebut murni asumsi dasar.** Baris 655 ("Semua selisih ... berasal dari pembulatan")
dan 779 ("bukan kegagalan menyatakan perubahan").
- `hasil_E1/_review/TINJAUAN.md` §4.4 dan `RINGKASAN.md` §7 butir 9: Δ U14 tidak menyatakan sendiri pembulatan ke bawah
  tunjangan pajak yang diwajibkan teks U14. U14 lolos hanya berkat Δ konvensi global. Sebagian kegagalan U14 di varian
  8/16 berasal dari Δ yang tidak lengkap. Catatan ini juga perlu disebut untuk hasil utama 16/16.

**B5. Baris 812: "Representasinya terbukti cukup ekspresif."**
- Hasilnya bergantung pada Δ konvensi (8/16 tanpa konvensi). Perubahannya ditulis agen, satu pelaksana menyusun Δ, dan
  pemeriksaan pakar yang diminta SEGEL.md aturan 3 belum dilakukan. "Terbukti" terlalu kuat. Usul: "mendukung bahwa
  representasi cukup ekspresif untuk 16 perubahan ini".

**B6. Abstrak, baris 66: "Evaluasinya terdaftar sebelum eksperimen dan mencakup ... ablasi, dan model kedua".**
- Sembilan pengecoh sisa, rantai pembangkitan ulang, jalan kedua, AB1, AB2, AB5, m = 5, model kedua, B2, kontaminasi, dan
  label kutipan dijalankan lewat amandemen 1 sesudah hasil awal terlihat (PRAREGISTRASI §10, tidak buta). Abstrak tidak
  menyebutnya. Abstrak juga tidak menyebut bahwa emas dan perubahan tak terlihat hanya ditinjau agen AI.

**B7. H3a pada rantai transplantasi disebut "analisis yang ditetapkan ... dalam amandemen 1".** Baris 630 dan 718.
- §10 hanya menulis "H3a diuji pada N = 33 sesuai §3", dan §3 menulis "OAR mode berantai (varian *abstain* tetap)".
  Kata "transplantasi" tidak ada. Penetapan itu tafsiran, walaupun didukung oleh jalan interim N = 24 yang memakai
  transplantasi sebelum amandemen.
- Definisi adaptivitas operasional naskah sendiri (baris 312, 518) cocok dengan rantai pembangkitan ulang.
- Pada rantai transplantasi, 579 dari 600 kasus sudah salah ($H_n$) sejak P05, sehingga 31/33 sebagian besar
  mencerminkan *masking*. Naskah membahasnya, tetapi "diterima" sebaiknya selalu disertai "tidak kokoh" (abstrak sudah,
  baris 718 belum).

## C. Catatan yang hilang

**C1. Status "tidak buta" tidak ditandai di tempat hasil dilaporkan.** Penandaan hanya ada di baris 390 dan 797. Tabel E2
(baris 680–706) mencampur kondisi terdaftar dengan AB2, m = 5, dan model kedua (amandemen) tanpa tanda. Kolom
"Pembangkitan ulang" di Tabel E3 tidak ditandai amandemen. Paragraf "Jalan kedua dan m = 5" (710), "Model kedua" (712),
B2 (745), Ablasi (772), kontaminasi dan kutipan (714, 647), detektor v2 (761, hanya "eksploratori"), dan penyelarasan
kunci konflik (643, 708) juga tanpa tanda. Butir 6 permintaan pemeriksaan hanya terpenuhi sebagian.

**C2. Koreksi emas kebijakan buatan sesudah keluaran terlihat.** Baris 643 dan 714. Pada *commit* `a57ea18` hasil usulan
adalah benar 3, salah 8, *abstain* 3. Sesudah koreksi SP04/07/11/14 menjadi benar 5, salah 6, *abstain* 3. Kedua
perubahan (SP07, SP14 dari salah menjadi benar-tak-teruji) menguntungkan usulan. PRAREGISTRASI §6 butir 5 mewajibkan
hasil sebelum/sesudah dilaporkan, dan naskah tidak melaporkannya. Tabel korpus (baris 495) menulis "5 B" tanpa catatan
"2 tidak teruji".

**C3. RQ4 didominasi kebijakan buatan.** Menurut `rq4_label.csv`, 99 dari 134 pasangan dan 27 dari 33 positif berasal
dari kebijakan buatan SP01–SP14. Hanya 6 positif dari PKB nyata. Hal ini tidak disebut di baris 748 maupun di ancaman
validitas.

**C4. Kesepakatan kehadiran unsur emas.** Baris 647 hanya menyebut persentase (82%, 91%). Di `kesepakatan_emas.json`,
α kehadiran −0,09 untuk regulasi dan 0,46 untuk kebijakan. Log menyatakan α tidak dilaporkan karena paradoks prevalensi.
Alasan itu perlu disebut, beserta fakta bahwa peninjau menerima konteks KB (`kb_context.py`), sehingga "buta" hanya
berarti buta terhadap emas.

**C5. Gerbang disesuaikan pada emas uji.** Baris 649 menyebut semua Δ* uji lolos G1–G5 dan penyesuaian gerbang "dibuat
atas emas". `LOG_PENELITIAN.md` "Gerbang terhadap emas" menunjukkan gerbang dilonggarkan untuk emas termasuk peristiwa
uji (misalnya tarif keringanan 50% PP 7/2025, E07). Padahal baris 373 menyebut syarat pembekuan hanya atas emas
pengembangan. Ini kebocoran desain dari emas uji ke gerbang, dan belum ada di baris 797.

**C6. Pemeriksaan invarian A1/A3ω tidak dilaporkan sebagai hasil.** Pemeriksaan ini terdaftar di Tabel lacak baris 567,
tetapi Tabel putusan dan subbagian hasil tidak memuat angkanya. Berkas mendukung nol pelanggaran: kolom `a3w` = 0 di
semua `e2-*/scores.csv`, dan A1 dibuktikan lewat `git diff engine-v1` kosong di RINGKASAN E1.

**C7. Holm untuk non-inferioritas.** Menurut PRAREGISTRASI §3, uji NI termasuk keluarga Holm RQ2. Naskah memakai CI 95%
tanpa penyesuaian. Hitung ulang: pada α/4 batas atas NI terhadap B3 0,064, dan pada α/2 0,036. Keduanya < 0,10, jadi
putusan tidak berubah, tetapi penyesuaian ini perlu disebut di baris 629/678.

**C8. Kesalahan terpicu pada pengecoh dihilangkan.** `e3-bangkit-ulang/chain_summary.json` mencatat `triggered_total` 57.
Angka 29 hanya mencakup 13 peristiwa regulasi yang punya batas derau. P06 (4) dan P15 (24) juga terpicu. Baris 741 perlu
menyebut pembatasan ini.

**C9. Konvensi pembulatan.** Kalkulator resmi DJP (GT2, baris 639) membuang pecahan, sama dengan konvensi contoh E1.
Pembulatan ke rupiah terdekat (tafsir K1) adalah bacaan proyek atas PER-11/PJ/2025. Hasil utama E1 bergantung pada
penyelarasan terhadap konvensi yang sama dengan alat resmi itu. Hubungan ini sebaiknya disebut di baris 655/779.

## D. Kata-kata minor

- **D1.** Baris 741, "keduanya identik pada sampel rantai". Hasil kedua jalan terisolasi berbeda pada E02 (salah lawan
  *abstain*, `e2-regulasi` lawan `e2-regulasi-ulang`). Yang identik adalah himpunan kasus salahnya pada sampel rantai
  (`run_chain.py`: |E_iso1 xor E_iso2| = 0). Perjelas.
- **D2.** Baris 606, 796, 814, "bahan pakar". Frasa ini dapat terbaca sebagai bahan buatan pakar. Usul: "bahan untuk
  peninjauan pakar".
- **D3.** Baris 498, D/FR "2013–2022" berbeda dengan baris 395 "2012–2022" (D01 terbit 2012-10-22). Kolomnya "Berlaku",
  jadi mungkin benar, tetapi sebaiknya diseragamkan.
- **D4.** Baris 79/743. B1 bertumpu pada dua repositori. Kalimat motivasi "setiap perubahan regulasi menuntut pemrograman
  ulang" sebaiknya menyebut bahwa ini ilustrasi n = 2.
- **D5.** Baris 390, "Anggaran itu habis sesudah strata utama E2, E3, dan E4". E4 tidak memakai LLM (masukannya Δ*).
  Tulis "E2 dan E3".

## E. Putusan hipotesis terhadap ambang

| H | Ambang (PRAREGISTRASI §3) | Nilai hitung ulang | Putusan naskah | Sesuai |
|---|---|---|---|---|
| H1 | batas bawah satu sisi ≥ 0,70, N ≥ 10 | 0,829 (N = 16) | diterima | ya |
| H2a | batas atas satu sisi ≤ 0,25 | 0,377 | tidak diterima | ya |
| H2b CAR | McNemar satu sisi, Holm p < 0,05 | p = 0,75 dan 1,0; Holm 1 | tidak diterima | ya |
| H2b NI | batas atas CI selisih < 0,10 | B3 0,004 (Holm α/4: 0,064); B4 0,153 | B3 ya, B4 tidak | ya |
| H3a | batas bawah satu sisi ≥ 0,75 | transplantasi 0,821; pembangkitan ulang 0,540 | diterima pada analisis terdaftar, tidak kokoh | ya, lihat B7 |
| H3b | I ≤ batas derau | 29 > 0 | tidak didukung | ya |
| H4a | batas bawah CI *bootstrap* klaster ≥ 0,70 | 0,75 | diterima | ya |
| H4b | selisih F2 > 0 terhadap kedua B5 | B5(i) −0,006 (CI −0,110–0,058) | tidak diterima | ya |

## F. Validasi manusia

Naskah tidak mengklaim validasi oleh pakar manusia. Baris 402, 433, 606, 647, 796, dan 798 menyatakan dengan jelas bahwa
emas, perubahan tak terlihat, dan bahan pakar hanya ditinjau agen AI independen, dan baris 814 menjadikan validasi oleh
praktisi pajak manusia sebagai penelitian lanjutan. Kekurangannya hanya di abstrak (B6) dan pada frasa "bahan pakar" (D2).
