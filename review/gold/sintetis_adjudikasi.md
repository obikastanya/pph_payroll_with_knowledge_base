# Adjudikasi emas dan LLM pada delapan kebijakan sintetis

Tanggal: 2026-10-29. Bahan: `dataset/13_teks/SPxx/teks.txt`, `dataset/12_emas/delta/GOLD-SPxx.json` (dari `system/gold_src/pol_sintetis.py`), *field* `delta` di `experiments/e2-sintetis/results/SPxx.json`, [representasi.md](../../docs/spesifikasi/representasi.md) bagian 6.3 dan 8. Tidak ada berkas lain yang diubah.

Cara kerja: kedua Δ dipasang pada `build_gold.load_graph()`. Setiap tupel `se_expected('SPxx')` (ω 2026-10-27) dievaluasi dengan `_obs`. Setelah itu tiap aturan emas dibuang satu per satu (ablasi) untuk melihat aturan mana yang menyebabkan beda. Penyebabnya dilacak dengan `evaluate_case(..., trace=True)`. Emas cocok dengan harapan pada semua tupel (0 beda), jadi beda dengan LLM selalu berasal dari Δ, bukan dari harapan.

Patokan: (a) teks dokumen; (b) representasi.md bagian 8, yaitu aturan perusahaan yang bertentangan dengan aturan wajib tetap dikodekan, kalah, lalu dilaporkan sebagai konflik; (c) pilihan pengodean emas nomor 4: "dipotong **dari penghasilan pekerja**" dibaca sebagai `withholding_method = 'gross'`.

## Ringkasan

| Kebijakan | Tupel beda (dari) | Penyebab beda | Putusan | Koreksi emas |
|---|---|---|---|---|
| SP02 | 50 (120) | LLM tidak menambah apa pun: `RUNNING` disetahunkan (48 tupel, konflik C5) dan `METHOD` (9 tupel) | **LLM salah** | — |
| SP03 | 49 (120) | DTP ditahan: emas `pph21_dtp := 0` (kalah, C4) vs LLM `employee_tax_burden` (menang diam-diam), 43 tupel; `METHOD` tidak dibuat LLM, 6 tupel | **LLM salah** | — |
| SP04 | 11 (120) | `METHOD` emas (10 tupel); apartemen tidak dikodekan LLM (2 tupel, C1) | **Keduanya salah** | hapus `PRS.SP04.METHOD` |
| SP07 | 14 (120) | hanya `METHOD` emas; THR sama | **Emas salah** | hapus `PRS.SP07.METHOD` |
| SP08 | 120 (120); 79 setelah id diselaraskan | LLM menambah `PRS.SP08.TAX_BURDEN_ROUND`; selebihnya hanya beda nama id | **LLM salah** | — |
| SP09 | 173 (180) | LLM tidak menambah apa pun: premi bukan bruto (173, C2), JKK 0,54% (8, C6), `METHOD` (11) | **LLM salah** | — |
| SP10 | 9 (180) | LLM tidak mengodekan JKK 0,54% (konflik C6 pada bulan keringanan JKK 2025) | **LLM salah** | — |
| SP14 | 10 (120) | hanya `METHOD` emas; THR sama | **Emas salah** | hapus `PRS.SP14.METHOD` |

## Catatan per kebijakan

### SP02
- **Klausul.** Ps. 31(2): "penghasilan bruto teratur sebulan dikalikan 12 (dua belas)"; Ps. 31(5): "berlaku selama masa berlaku Peraturan Perusahaan ini"; Ps. 31(1): "dipotong setiap bulan dari penghasilan pekerja".
- **Emas.** Metode disetahunkan ×12 dikunci untuk 2023–2024 (`PRS.SP02.RUNNING`, C5). `METHOD = 'gross'`. JKK 0,89%.
- **LLM.** `relevant: false`, dengan alasan "isinya sama dengan aturan wajib 2023".
- **Jejak.** Pada SE-2023-C022-SP02 (masuk Juli 2023), `REG.P16.RUNNING` menyetahunkan atas sisa masa kerja dan menghasilkan 287.533. Aturan perusahaan memakai ×12 dan menghasilkan 1.150.112, lalu kalah dan dilaporkan C5. Pada 2024 seluruh Januari–November berkonflik dengan TER. *Gross-up* menjadi *gross* lewat `METHOD` (SE-2023-C015-SP02).
- **Putusan.** Teks memang menyatakan ×12 tanpa pengecualian, dan Ps. 31(5) mengunci cara itu sampai 2024. Klaim LLM tidak berlaku untuk karyawan yang masuk di tengah tahun dan untuk seluruh 2024. Frasa "dari penghasilan pekerja" memenuhi pilihan pengodean 4. **LLM salah.**

### SP03
- **Klausul.** Ps. 40(3): insentif PPh 21 "diterima dan dikelola oleh Perusahaan … dan tidak dibayarkan secara perorangan kepada pekerja"; Ps. 40(1): "menjadi beban pekerja dan dipotong".
- **Emas.** `PRS.SP03.DTP_WITHHELD`: `pph21_dtp := 0` (C4). Aturan ini kalah dari `REG.DTP.RUNNING`, sehingga THP tetap memuat DTP dan konflik dilaporkan. `METHOD = 'gross'`.
- **LLM.** `PRS.SP03.DTP_RETAINED` menghasilkan `employee_tax_burden = pph21_due` bila `pph21_dtp != 0`. Pesaingnya `REG.THP.TAX_BURDEN` hanya `default`, jadi aturan ini **menang**. Akibatnya THP turun (SE-2025-O0284-SP03 bulan 10: beban 15.653 vs 0) dan tidak ada konflik yang dilaporkan, padahal catatan LLM sendiri menyebut klausul ini bertentangan dengan PMK 10/2025. `METHOD` juga tidak dibuat LLM.
- **Putusan.** Menurut bagian 8, klausul yang bertentangan dengan aturan wajib harus kalah dan dilaporkan. Kandidat LLM justru menerapkan klausul itu tanpa laporan. "Menjadi beban pekerja" secara tegas berarti *gross*. **LLM salah** (sama dengan putusan pembaca kedua di kebijakan.review.md).

### SP04
- **Klausul.** Ps. 28: fasilitas Ps. 27 "tidak diperhitungkan sebagai penghasilan pekerja dalam penghitungan Pajak Penghasilan Pasal 21"; Ps. 29(1): "PPh 21 atas penghasilan pekerja dipotong oleh Perusahaan sesuai ketentuan perpajakan yang berlaku".
- **Emas.** `PRS.SP04.BENEFITS_NOT_INCOME`: `benefit_housing_taxable := 0` (C1). `PRS.SP04.METHOD = 'gross'`.
- **LLM.** `relevant: false`, dengan alasan "regulasi wajib yang menentukan, kebijakan tidak dapat mengubahnya".
- **Jejak.** Pada SE-2023-C004-SP04, `REG.NATURA.HOUSING` (selisih di atas Rp2 juta) bernilai 1.000.000 dan aturan perusahaan kalah (C1; dilacak pada bulan 9–12). Sepuluh tupel lain berbeda hanya karena `METHOD` mengubah kasus *gross-up* atau ditanggung menjadi *gross* (SE-2023-C014-SP04 bulan 1: THP 58.873.891 vs 75.249.224).
- **Putusan.**
  - Apartemen: alasan LLM bertentangan dengan bagian 8. Kalau tidak dikodekan, konflik C1 tidak terlaporkan. Emas benar.
  - `METHOD`: Ps. 29(1) hanya menyatakan bahwa Perusahaan memotong. "Dipotong" adalah istilah pemotongan oleh pemotong pajak dan berlaku untuk semua metode. Teks tidak menyebut "beban pekerja" atau "dari penghasilan pekerja", sehingga pilihan pengodean 4 tidak terpenuhi. Metode kasus (`case('method')`) seharusnya tetap berlaku. Emas salah.
  - Hasil: **keduanya salah**.
- **Koreksi.** Hapus unsur `PRS.SP04.METHOD` (baris `p.method("gross", …)` di `_sp04`). Setelah dihapus, LLM masih berbeda pada 2 tupel (C1), sesuai putusan.
- **Batas (bukan koreksi).** Aturan apartemen menolkan seluruh rumah individual, padahal Ps. 27(2) hanya untuk jabatan Manajer ke atas di kantor pusat. Data kasus tidak punya atribut jabatan (representasi.md bagian 10 butir 6), jadi ini dicatat sebagai batas.

### SP07
- **Klausul.** Ps. 53: "THR merupakan penghasilan tidak teratur dan dipotong Pajak Penghasilan Pasal 21 pada bulan dibayarkan sesuai ketentuan perpajakan yang berlaku".
- **Emas.** `PRS.SP07.THR` dan `PRS.SP07.METHOD = 'gross'`.
- **LLM.** `PRS.SP07.THR` saja, setara dengan emas: `<= 0` vs `== 0` atas hari yang tidak negatif, dan bulan non-hari raya jatuh ke aturan regulasi yang sama.
- **Ablasi.** Emas tanpa `METHOD` sama persis dengan LLM pada 120 tupel. Ke-14 tupel yang berbeda adalah kasus *gross-up* atau ditanggung (SE-2024-C017-SP07: PPh setahun 238.472.200 vs 340.674.400).
- **Putusan.** Ps. 53 hanya mengatur bahwa THR adalah penghasilan tidak teratur dan kapan dipotong. Pasal ini tidak menyebut siapa yang menanggung pajak. **Emas salah.**
- **Koreksi.** Hapus `PRS.SP07.METHOD`.

### SP08
- **Klausul.** Ps. 18(3): "Pajak Penghasilan Pasal 21 setiap Masa Pajak dibulatkan ke atas hingga ratusan rupiah penuh".
- **Emas.** `RUNNING` dan `FINAL` dibulatkan ke atas ratusan (C9), `JOB_EXPENSE` tanpa batas, `DEDUCTIONS` ditambah JKN dan zakat, `TAXABLE` *half_up*. Semuanya kalah dan dilaporkan.
- **LLM.** Lima aturan yang sama isinya dengan nama id lain, ditambah `PRS.SP08.TAX_BURDEN_ROUND`: `employee_tax_burden = round(pph21_due − pph21_dtp, 100, 'up')`, `overrides REG.THP.TAX_BURDEN`.
- **Jejak.** Pada SE-2024-O0088-SP08 bulan 4, `pph21_due` = 163.885 (aturan wajib menang), tetapi beban pegawai menurut LLM 163.900. Akibatnya THP turun Rp15 dan tidak ada konflik yang dilaporkan.
- **Putusan.** Klausul membulatkan PPh 21, bukan potongan gaji. Teks tidak menyatakan bahwa pegawai dipotong lebih dari PPh terutang. Aturan tambahan LLM membuat efek baru yang tidak tertulis, dan efek itu menang diam-diam atas fakta `default`. **LLM salah.**
- **Catatan penilaian.** `score_kb` membandingkan kunci konflik dengan id mentah, sehingga semua 120 tupel tercatat A4 hanya karena nama (`ANNUAL_DEDUCTIONS` vs `DEDUCTIONS`, `RUNNING_ROUND` vs `RUNNING`, `FINAL_ROUND` vs `FINAL`, `TAXABLE_INCOME` vs `TAXABLE`). Representasi.md bagian 8 meminta id diselaraskan lewat bentuk kanonik lebih dulu. Setelah diselaraskan, yang tersisa 79 tupel, semuanya karena THP. Putusan tidak berubah, tetapi angka A4 SP08 di `scores.csv` terlalu besar.

### SP09
- **Klausul.** Ps. 25(2): iuran JKK, JKM, dan JKN bagian Perusahaan "bukan merupakan penghasilan pekerja, dan tidak dimasukkan dalam penghasilan bruto"; Ps. 25(1): "JKK sebesar 0,54%"; Ps. 26(1): "dipotong dari penghasilan pekerja".
- **Emas.** `PREMIUMS_NOT_GROSS := 0` (C2), `JKK_RATE` 0,0054 (C6), `METHOD = 'gross'`.
- **LLM.** `relevant: false`. Alasannya, klausul premi bertentangan dengan `REG.PREMIUMS.TAXABLE` dan "tidak dapat mengubah perhitungan".
- **Jejak.** C2 muncul pada setiap bulan (SE-2023-O0184-SP09: premi 188.921). JKK berkonflik pada Februari–Juli 2025: keringanan 0,27% vs 0,54% (SE-2025-C025-SP09).
- **Putusan.** Alasan LLM bertentangan dengan bagian 8, karena klausul yang kalah tetap harus dikodekan supaya konflik C2 terlaporkan. Tarif JKK ditulis sebagai angka tetap. "Dari penghasilan pekerja" memenuhi pilihan pengodean 4. **LLM salah.**

### SP10
- **Klausul.** Ps. 41(4): "Iuran JKK sebesar 0,54% (nol koma lima puluh empat persen) dan iuran JKM sebesar 0,30% … ditanggung Perusahaan".
- **Emas.** JHT pegawai 3%, JKN pegawai 2% dan perusahaan 3% (C7), JKK 0,0054 (C6).
- **LLM.** Tiga aturan pembagian iuran yang perilakunya sama dengan emas pada 180 tupel. Kode konflik LLM C4, bukan C7, tetapi kode tidak termasuk kunci. JKK tidak dikodekan karena dianggap "match existing rules".
- **Jejak.** Pada SE-2025-O0031-SP10 (kelompok risiko rendah, layak keringanan), `REG.BPJS.JKK_RATE.RELIEF` = 0,27%. Aturan perusahaan 0,54% kalah dan dilaporkan C6 pada bulan keringanan. Inilah satu-satunya beda (9 tupel, tanpa beda nilai).
- **Putusan.** Teks menyebut angka 0,54% tanpa merujuk "ketentuan yang berlaku". Bandingkan dengan SP14 Ps. 61(2), yang tegas mengikuti penyesuaian tarif Pemerintah. Angka itu berbeda dari tarif wajib pada masa keringanan, jadi menurut bagian 8 konfliknya harus terlaporkan. **LLM salah.** Beda ini paling tipis dari delapan kebijakan karena tidak mengubah nilai dan hanya menyangkut laporan konflik.

### SP14
- **Klausul.** Ps. 61(1): "Pajak Penghasilan Pasal 21 atas penghasilan pekerja, termasuk THR, dipotong sesuai ketentuan perpajakan yang berlaku".
- **Emas.** `PRS.SP14.THR` (1,5 kali, pegawai yang berhenti ≤ 30 hari sebelum hari raya tetap berhak) dan `PRS.SP14.METHOD = 'gross'`.
- **LLM.** THR yang setara (`15 / 10`, syarat sama). Tidak ada `METHOD`.
- **Ablasi.** Emas tanpa `METHOD` sama persis dengan LLM pada 120 tupel. Ke-10 tupel yang berbeda adalah kasus *gross-up* atau ditanggung (SE-2025-C017-SP14: PPh setahun 51.555.500 vs 69.186.000).
- **Putusan.** Kata "atas penghasilan pekerja … dipotong" tidak menyatakan siapa yang menanggung pajak, sama seperti SP04. **Emas salah.**
- **Koreksi.** Hapus `PRS.SP14.METHOD`.

## Tindak lanjut emas

1. Di `system/gold_src/pol_sintetis.py`, hapus `p.method("gross", …)` pada `_sp04`, `_sp07`, dan `_sp14` (unsur `PRS.SP04.METHOD`, `PRS.SP07.METHOD`, `PRS.SP14.METHOD`). Bangun ulang `GOLD-SP04/07/14.json` dan `dataset/14_ruang_uji/harapan/SP04|SP07|SP14.jsonl.gz`, lalu nilai ulang E2. Perkiraan dari ablasi: SP07 dan SP14 menjadi benar, SP04 tetap salah (2 tupel, C1).
2. Pembaca kedua juga menandai `METHOD` SP11 dengan alasan yang sama ("dipotong setiap bulan dengan tarif efektif bulanan"). SP11 di luar cakupan adjudikasi ini, tetapi patokan yang sama perlu diterapkan di sana.
3. Penilai: selaraskan id aturan perusahaan kandidat dengan emas sebelum membandingkan kunci konflik (representasi.md bagian 8). Saat ini A4 SP08 terlalu besar.
4. Untuk SP07 dan SP14, aturan THR emas tidak berpengaruh pada tupel uji: membuangnya tidak mengubah satu tupel pun, karena THR di data kasus sudah sama dengan THR kebijakan. Ruang uji belum dapat membedakan aturan THR yang salah.
