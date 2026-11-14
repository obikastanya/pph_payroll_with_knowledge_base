# 03_pembanding — Implementasi pembanding PPh 21 (open-source, rules-as-code, kalkulator online)

Manifest ini disusun pada 2026-10-01 untuk evaluasi proyek KBS (kalkulator PPh 21 berbasis basis pengetahuan dua lapis: regulasi pemerintah dan kebijakan perusahaan). LLM tidak dipakai dalam perhitungan apa pun di folder ini.

> **Peringatan utama.** Tidak satu pun implementasi di folder ini boleh dianggap *oracle* atau *ground truth*. Semua repo terpilih terbukti memiliki kesalahan perhitungan (lihat bagian 6, `indikasi_kesalahan`). Kebenaran harus dirujuk ke teks regulasi (PP 58/2023, PMK 168/2023 beserta contoh lampirannya, UU HPP, PMK 101/2016) di `dataset/01_regulasi/`. Baseline di sini dipakai untuk **uji diferensial**: setiap selisih harus ditelusuri ke regulasi, bukan otomatis dianggap kesalahan sistem kita.

## 1. Isi folder

| Path | Isi |
|---|---|
| `kandidat_repo.csv` | Semua kandidat yang ditemukan (35 baris): URL, bahasa, lisensi, bintang, tanggal, jumlah commit, apakah riwayat melintasi 2024, fitur (TER, gross-up, PTKP K/I, BPJS, THR/bonus, masa pajak terakhir). Tanda `(v)` berarti diverifikasi lewat pembacaan kode; `(k)` hanya indikasi pencarian kata kunci. |
| `repos/<nama>` | 7 clone penuh (bukan shallow; `git rev-parse --is-shallow-repository` = false). `core.longpaths=true` diset karena path Windows panjang. Working tree semua repo bersih (`git status` kosong); hanya `muhroyhan-pph21/node_modules/` (hasil `npm ci`, di-*gitignore*) yang ditambahkan agar tes dapat dijalankan ulang. |
| `maintenance_ter_commits.csv` | Statistik commit pengenalan/perubahan TER: hash, tanggal, file, baris +/−, baris kode non-tes, fungsi baru/diubah/dihapus (heuristik regex). |
| `mesin_rule_as_code.csv` | Perbandingan mesin rules-as-code (OpenFisca, Catala, Payroll Engine, DMN/Drools, Frappe HRMS, Odoo, Blawx, dll.). |
| `kalkulator_online.csv` | Kalkulator PPh 21 daring (kandidat uji black-box manual), dukungan fitur, robots.txt dan ToS. |

## 2. Metode pencarian (2026-10-01)

- **GitHub**: CLI `gh` tidak tersedia, jadi dipakai GitHub REST API tanpa autentikasi (`/search/repositories`). Kueri: `pph21`, `pph 21`, `pph-21`, `tarif efektif rata-rata`, `pajak penghasilan 21`, `TER pph21`, `indonesia payroll`, `payroll indonesia`, `kalkulator pajak`, `income tax indonesia`, `bpjs pph21`, `hrms indonesia`, `pajak gaji`, `l10n-indonesia`, `pph21 odoo`, `pph21 frappe`, `pph21 erpnext`. Fork `steevenz/id-payroll-calculator` diperiksa lewat API forks.
- **Packagist**: `pph21`, `pph`, `pajak`, `indonesia payroll`, `ptkp`. Hasilnya sekitar 20 paket latihan OOP pra-TER, `steevenz/id-payroll-calculator`, dan `riod94/payroll-calculator-indonesia`.
- **npm**: `pph21`, `pajak penghasilan`, `ptkp`, `bpjs`, `indonesia payroll`. Hasilnya paket `pph21` (muhroyhan) dan `payroll-calculator` (riod94/payroll-formula, repo sudah 404).
- **PyPI**: tidak ada API pencarian. Nama `pph21`, `pph-21`, `pypph21`, `pajak`, `indonesia-tax`, `indonesian-tax`, `pph21-calculator`, `payroll-indonesia`, `id-payroll`, `pajakku`, `kalkulator-pajak`, `ter-pph21`, `pph21ter`, `idtax` semuanya 404. Yang ada hanya addon Odoo `odoo14-addon-ssi-l10n-id-taxform-pph-21*`, yaitu paket open-synergy.
- **Triage**: 33 repo di-*partial clone* (`--filter=blob:none`) ke scratchpad. Riwayat dan kata kunci dipindai, lalu 7 repo dipilih dan di-clone penuh.

## 3. Repo terpilih (clone penuh di `repos/`)

| Folder | Upstream | Bahasa | Lisensi | ★ | Commit (periode) | Riwayat lintas 2024? | TER | Gross-up | PTKP K/I | BPJS | THR/bonus | Masa pajak terakhir | Dijalankan lokal? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `opnsynid-l10n-indonesia-taxform` | [open-synergy/opnsynid-l10n-indonesia-taxform](https://github.com/open-synergy/opnsynid-l10n-indonesia-taxform) (cabang 14.0) | Python/Odoo 14 | AGPL-3.0 | 0 | 587 di cabang 14.0; 806 di semua cabang (2022-03 → 2026-09) | **Ya** (90 commit pra-2024) | Mesin ada, **data tabel TER tidak dikirim** | Tidak | Kategori ada, nilai tidak ada | Tidak (input manual) | Ya (non-rutin) | Ya (`compute_pph_21_2110001`) | Tidak (butuh Odoo + dependensi OCA) |
| `pajakin` | [AsadSaleh/pajakin](https://github.com/AsadSaleh/pajakin) | TypeScript/Next.js | **tidak ada LICENSE** | 5 | 39 (2023-08 → 2026-08) | **Ya** (12 commit pra-2024) | Ya (tabel benar) | Ya (TER bulanan, closed-form) | Ya (halaman tahunan) | Parsial, ada bug | Baris input bebas | Tidak | Ya (fungsi diimpor via `tsx`) |
| `muhroyhan-pph21` | [muhroyhan/pph21](https://github.com/muhroyhan/pph21), npm `pph21` 1.0.1 | TypeScript | MIT | 0 | 25 (2026-08-06 → 08) | Tidak | Ya (+ harian) | Tidak | Ya | Helper terpisah | Via bruto bulan itu | Ya (lebih bayar diizinkan) | **Ya** (vitest 48/48 lulus) |
| `peco-id-payroll` | [Peco-lab/id-payroll](https://github.com/Peco-lab/id-payroll) | Python + TypeScript | MIT | 0 | 2 (2026-06-27) | Tidak | Ya | Tidak | Tidak | Ya (ada bug) | Via bruto | Ya (lebih bayar dipotong ke 0) | **Ya** (pytest 20/20, vitest 20/20) |
| `riod94-payroll-calculator-indonesia` | [riod94/payroll-calculator-indonesia](https://github.com/riod94/payroll-calculator-indonesia) | PHP ≥8 | ISC | 1 | 5 (2025-11-17) | Tidak (lihat garis turunan) | **Stub, tidak jalan** | Tidak (×1,2 "simplified") | Tidak | Parsial, bug | Ya (bug) | Parsial | Tidak (PHP tidak terpasang) |
| `steevenz-id-payroll-calculator` | [steevenz/id-payroll-calculator](https://github.com/steevenz/id-payroll-calculator) | PHP ^7.2 | MIT | 21 | 57 (2019) | — (leluhur pra-HPP/pra-TER dari riod94) | Tidak | Parsial (tanpa iterasi) | Tidak | Ya (bug) | Ya | Tidak | Tidak |
| `teknologi-umum-pph21` | [teknologi-umum/pph21](https://github.com/teknologi-umum/pph21) | TypeScript/Bun | MPL-2.0 | 0 | 19 (2024-01 → 2025-03) | Tidak (TER sejak commit awal) | Ya (2 baris salah) | Tidak | Tidak | Ya | Ya (1 bulan bonus) | Ya | Ya (fungsi diimpor via `tsx`) |

Alasan pemilihan:
- open-synergy dan pajakin adalah satu-satunya kandidat ber-TER yang riwayat git-nya benar-benar melintasi peralihan 2023→2024. open-synergy juga menyimpan aturan sebagai data master bertanggal, sehingga paling mirip dengan pendekatan KB proyek ini.
- muhroyhan dan peco adalah pustaka murni yang bisa dipanggil programatik untuk uji diferensial. muhroyhan punya versi konstanta per tahun pajak (2024–2026) dan tes yang mengutip contoh PMK 168.
- Pasangan steevenz → riod94 dipilih untuk studi pemeliharaan lintas-repo (fork/turunan pra-TER → klaim TER).
- teknologi-umum kecil, berlisensi permisif, dan mencakup perhitungan Desember.

Kandidat lain yang layak disebut tetapi tidak di-clone (lihat `kandidat_repo.csv`):
- `artivisi/balaka`: Java, Apache-2.0, 44★, aplikasi akuntansi besar, riwayat baru dimulai 2025-11.
- `IMOGI-ITB/Payroll-Indonesia`: Frappe, MIT, memiliki `pph21_ter_december.py`, riwayat mulai 2025-07.
- `agitnaeta/ritmehr`: Laravel, tanpa lisensi. Tabel TER disimpan di DB dan ada tes koreksi Desember.
- `OCA/l10n-indonesia`: cabang 8.0 memuat leluhur modul open-synergy.

## 4. Lokasi aturan yang di-*hard-code*

| Repo | Lokasi aturan |
|---|---|
| open-synergy | **Logika** ada di Python: metode tahunan `ssi_l10n_id_taxform_pph_21/models/res_partner.py:16-217`, TER `res_partner.py:219-246`, `models/pph_21_ter.py:28-50`, `models/pph_21_ter_line.py:38-56`, biaya jabatan `models/pph_21_biaya_jabatan.py:47-135`. **Nilai** disimpan sebagai record bertanggal (`date_start`), tetapi yang dikirim hanya data demo: `demo/pph_21_rate_demo.xml`, `demo/ptkp_demo.xml`, `demo/pph_21_biaya_jabatan_demo.xml`, `demo/pph_21_npwp_rate_modifier_demo.xml`. Data riil yang dikirim hanya kategori PTKP (`data/ptkp_category_data.xml`). Modul Coretax meng-*hard-code* Pasal 17, TER harian, pesangon, dan pensiun di Python tanpa versi tanggal: `ssi_l10n_id_taxform_coretax_bupot_pph_f113301/models/l10n_id_bukti_potong_pph_f113301_out_line.py:428-459, 552-574`. |
| pajakin | Tabel TER `app/ter-rates.ts:21-155`, pemetaan kategori `:168-184`, PTKP `app/page.tsx:20-57`, Pasal 17 `app/page.tsx:62-93`, BPJS `app/page.tsx:159-203`. |
| muhroyhan | `src/constants/ter.ts:7-155`, `article17.ts:7-13`, `ptkp.ts:7-29`, `deductions.ts:6-13`, `bpjs.ts:9-36`, `dtp.ts:12-18`, `tax-years.ts:22-65` (konfigurasi per tahun, pengali NPWP di `:32`). Ambang harian 2,5 jt dan faktor 0,5 berupa literal di `src/calculators/pegawai-tidak-tetap.ts:64,82`. |
| peco | Python: `python/src/id_payroll/ter.py:20-68`, `ptkp.py:25-34`, `pasal17.py:20-49`, `bpjs.py:16-39`, `pph21.py:36,72`. JS mencerminkan nilai yang sama di `js/src/*.ts`. |
| riod94 | `src/Constants/PphConstants.php:9-147` (Pasal 17 2021 & 2022, PTKP, JKK, kategori TER, TER harian) dan `src/DataStructures/Provisions.php:43-68` (UMP 3.940.972, plafon BPJS, tarif, biaya jabatan, `terMonthly = []`). |
| steevenz | `src/DataStructures/Provisions/State.php:36-78`, `src/Taxes/AbstractPph.php:74-87`, `src/PayrollCalculator.php:227-289`, `src/Taxes/Pph21.php:34`. |
| teknologi-umum | Semuanya di `src/tax.ts`: BPJS `:96-130`, biaya jabatan `:46`, Pasal 17 `:134-140`, PTKP `:155-174`, kategori `:182-196`, TER A/B/C `:206-338`. Salinan hasil build `src/public/client.js` ikut di-commit dan membawa bug yang sama. |

## 5. Cara pemanggilan programatik (satu pegawai, satu bulan)

Kasus acuan: tahun 2024, Januari, K/1, gaji 10.000.000; pemberi kerja menanggung JKK 0,24%, JKM 0,3%, BPJS Kes 4%; pegawai membayar JHT 2%, JP 1%, BPJS Kes 1%. Nilai acuan dihitung manual dari PP 58/2023:
- Januari: bruto 10.454.000 → TER B 1,5% → **156.810**
- Setahun: PKP 52.848.000 → **2.642.400**
- Desember: 2.642.400 − 11 × 156.810 = **917.490**

| Repo | Status | Pemanggilan | Hasil |
|---|---|---|---|
| muhroyhan | **dijalankan** | `npm ci`, lalu `node_modules/.bin/vite-node skrip.ts`. Pertama `calculateBpjs({monthlyWage:10_000_000, jkkTier:'very-low', periodDate:'2024-01-31'}, getTaxYearConfig(2024).bpjs)` untuk `taxableAddition`, lalu `calculatePPh21({employeeType:'pegawai-tetap', isFinalPeriod:false, ptkpStatus:'K1', hasNpwp:true, monthlyGrossIncome:10_454_000}, {taxYear:2024})`. Desember: `isFinalPeriod:true` plus bruto setahun, JHT/JP setahun, dan PPh yang sudah dipotong. | Jan 156.810; Des 917.490; setahun 2.642.400 (= acuan). `taxYear` default 2026, jadi tahun harus ditulis eksplisit. |
| peco | **dijalankan** | `PYTHONPATH=python/src python -c "from id_payroll import *; ..."`, memanggil `calc_monthly_tax_components(10_000_000, "K/1", bpjs_settings=BpjsSettings(jkk_rate=0.0024))`. JS: `calcMonthlyTaxComponents({grossSalary:1e7, taxStatus:'K/1', bpjsSettings:{jkkRate:0.0024}})`. | Jan **150.810** (BPJS Kes pemberi kerja tidak masuk bruto); Des 863.490; setahun 2.522.400. Hasil baru sama dengan acuan setelah input dikoreksi pemanggil. |
| pajakin | **dijalankan** (modul diimpor) | `findTerBracket(terPtkpKategori['K/1'].category, 10_454_000)` dari `app/ter-rates.ts`. Halaman tahunan hanya bisa dipakai lewat UI (logika *inline* di React). | 156.810 hanya jika pengguna memasukkan bruto lengkap. Tidak ada perhitungan Desember. |
| teknologi-umum | **dijalankan** (modul diimpor) | `calculateTax(10_000_000, 0, TaxpayerStatus.K1)` dari `src/tax.ts`. | Jan **150.000**; Des 1.000.166,34; total 2.645.042,4 (salah, lihat bagian 6). |
| open-synergy | tidak dijalankan | Pasang modul (dan dependensi OCA server-tools, ssi-mixin, opnsynid-hr-payroll), isi seluruh data master termasuk 125 baris TER, lalu panggil `partner.compute_pph_21_ter(tanggal_pemotongan, gaji, tunjangan_pph, tunjangan_lain, jumlah_penghasilan_non_rutin)`. Untuk Desember: `partner.compute_pph_21_2110001(...)`. | — |
| riod94 | tidak dijalankan (PHP tidak ada) | `composer require riod94/payroll-calculator-indonesia`; isi `$c->employee->...`, lalu `$c->getCalculation()` (contoh di `tests/Integration/PayrollCalculatorIntegrationTest.php:26-70`). README-nya rusak. | Dari pembacaan kode diperkirakan PPh bulan reguler = 0 (bug C1). |
| steevenz | tidak dijalankan | `composer require steevenz/id-payroll-calculator`; `$p->method = PayrollCalculator::GROSS_CALCULATION; $p->taxNumber = 21; ... $p->getCalculation()`. | — |

## 6. `indikasi_kesalahan` dan tes

Status bukti:
- **[V]** = terverifikasi, yaitu dibaca di kode dan, bila bisa, dibuktikan dengan menjalankan kasus.
- **[S]** = dugaan atau bergantung pada konfigurasi.

Nomor baris mengacu ke HEAD repo saat clone (2026-10-01).

### 6.1 open-synergy (opnsynid-l10n-indonesia-taxform)

Kesalahan:
- [V] **Tidak ada tabel TER yang dikirim**, baik sebagai data maupun demo. Pengguna harus mengetik 125 bracket sendiri. Ini dikonfirmasi oleh komentar tes `ssi_l10n_id_taxform_coretax_bupot_21_payslip_batch/tests/test_coretax_bupot_21.py:58`.
- [V] **Lookup TER mengabaikan versi.** `pph_21_ter.py:46` memakai `self.line_ids.search(criteria)`, padahal `search` Odoo berjalan atas seluruh model. Jika ada dua versi TER, `ensure_one` di `pph_21_ter_line.py:39` gagal. Akibatnya versioning temporal TER praktis rusak.
- [V] Model TER tidak punya `_order` (`pph_21_ter.py:11-39`), berbeda dengan empat model aturan lain. Akibatnya `find()` dengan `limit=1` bisa mengembalikan versi lama. [S] Seberapa parah bergantung pada urutan default mixin.
- [V] Batas TER `bruto >= min_income` (`pph_21_ter_line.py:47`) bersifat inklusif di bawah, sedangkan PP 58 memakai "di atas". Hasil simulasi bergantung pada cara pengguna mengisi data: jika `min_income` diisi sama dengan batas atas bracket sebelumnya, ada 43/39/40 titik batas yang tarifnya salah.
- [V] Jika bruto berada di bawah bracket pertama, `self.line_ids[line-1]` dengan `line=0` mengambil bracket tertinggi (34%) (`pph_21_ter_line.py:50-51`).
- [V] Jalur TER tidak menerapkan surcharge NPWP dan tidak membulatkan (`res_partner.py:219-246`).
- [V] Plafon biaya jabatan pegawai yang masuk di tengah tahun tidak diprorata (`pph_21_biaya_jabatan.py:104-109`, `res_partner.py:83-85`).
- [V] TER harian di atas 2,5 jt/hari menghasilkan 0% (`..._out_line.py:458-459`).
- [V] Data demo Pasal 17 memakai tarif pra-HPP dengan salah ketik ×10: batas 2.500.000.000 dan 5.000.000.000 (`demo/pph_21_rate_demo.xml:21,27,33`).
- [V] Bug "tarif TER persen dipakai sebagai pecahan → pajak 100×" sempat aktif 2026-08-28 s.d. 2026-09-03 (diperbaiki di 4ec6ee9).
- [S] PTKP diambil dari kategori partner saat ini, bukan status per 1 Januari (`res_partner.py:55,151`).
- [S] Ekspor BPMP menerapkan TER juga di bulan Desember (`hr_payslip_batch.py:101-102`).

Tes:
- Tes YAML bersifat *smoke*: `compute_pph_21_ter` dan `compute_pph_21_2110001` tidak pernah dipanggil dengan asersi hasil.
- Tes Coretax memakai tabel TER sintetis (0%/6%).
- **Tidak ada contoh resmi** DJP/PMK.

Catatan: 11 commit sejak 2026-06-19 di cabang 14.0, termasuk e65daec dan 4ec6ee9, membawa trailer `Co-Authored-By: Claude`. Artinya sebagian kode terbaru dibantu LLM. Ini relevan bila repo dipakai sebagai pembanding "buatan manusia".

### 6.2 pajakin

Yang benar:
- [V] Tabel TER A/B/C sama persis dengan PP 58 (44/40/41 baris), batas `<=` inklusif, dan pemetaan kategori benar.
- [V] Biaya jabatan dan JHT/JP tidak dikurangkan di bulan TER, sesuai aturan.

Kesalahan:
- [V] Tombol "auto" menawarkan BPJS Kes 1% pegawai sebagai pengurang (`app/page.tsx:159-172`). Seharusnya tidak dikurangkan.
- [V] Plafon JP diterapkan pada iuran, bukan pada upah: `Math.min(gaji*0.01, 10_547_000)` (`page.tsx:197`). Akibatnya JP praktis tanpa plafon.
- [V] Pengurang otomatis hanya dihitung untuk 1 bulan (`occurence:'1'`) di kalkulator tahunan (`page.tsx:167,183,198`).
- [V] Biaya jabatan tidak dihitung otomatis sejak rewrite 4f54364.
- [V] PKP tidak dibulatkan ke ribuan (`page.tsx:217`).
- [V] Tidak ada *true-up* Desember dan halaman TER tidak terhubung dengan halaman tahunan.
- [V] JKK, JKM, dan BPJS Kes pemberi kerja tidak pernah ditambahkan ke bruto.
- [S] Nilai "per bulan" = tahunan/12 menyesatkan untuk rezim 2024.

Gross-up:
- [V] Konsisten. Dari 60.000 nilai neto, tidak ada selisih terhadap iterasi titik tetap.
- [V] Hasilnya tidak dibulatkan ke rupiah.

Tes: **tidak ada**. Sumber resmi hanya disebut di komentar (`ter-rates.ts:3`).

### 6.3 muhroyhan/pph21

Yang benar:
- [V] Tabel TER A/B/C sama persis dengan PP 58 (diverifikasi programatik).
- [V] Pasal 17, PTKP, perlakuan BPJS (JKK/JKM/Kes pemberi kerja kena pajak; JHT/JP pemberi kerja tidak), tidak ada pengurang di bulan Jan–Nov, PKP dibulatkan ke ribuan, dan lebih bayar diizinkan. Semuanya sesuai.

Kesalahan:
- [V] **Lookup TER melempar error untuk bruto non-integer.** Bracket disimpan sebagai `[min,max]` integer dengan `min = max sebelumnya + 1` (`src/core/ter-lookup.ts:13-23`). Contoh nyata: gaji 5.165.487 (TK/0) menghasilkan bruto 5.400.000,1098, dan kalkulasi melempar "No TER bracket matches". Seluruh 122 probe `ub+0.5` gagal.
- [V] `maxDailyWage` DTP (500 rb) didefinisikan tetapi tidak dipakai (`dtp.ts:16`, `index.ts:93`).
- [V] Tidak ada annualisasi untuk WP baru di tengah tahun. Untuk contoh resmi PMK 168 Tuan C, Desember resmi +580.000, sedangkan library menghasilkan −2.955.000.
- [V] Tidak ada input zakat. Akibatnya Tuan A Desember 15.195.000, sedangkan resmi 14.595.000.
- [V] Tidak ada tahun 2023 (pra-TER): `getTaxYearConfig(2023)` melempar error.
- [V] Tidak ada gross-up.
- [V] DTP PMK 10/2025 tidak ada; yang ada hanya PMK 105/2025 untuk 2026.
- [S] Plafon JP 10.042.300 berlaku sejak 2024-01-01 (`bpjs.ts:27`), padahal perubahan biasanya Maret.
- [S] PTKP K/I diterapkan di pemotongan oleh pemberi kerja.
- [S] DTP Desember membuat nol pajak atas penghasilan tidak teratur.

Tes:
- vitest 8 file, **48 tes, semua lulus**.
- `test/pegawai-tetap.test.ts:4-9` mengutip **PMK 168/2023 Lampiran Tuan A dan Tuan B**. Nilainya sesuai PDF (hal. PDF 33-36), tetapi nomor halaman yang dikutip keliru.
- Tes lain berupa invarian atau nilai buatan penulis.

### 6.4 Peco-lab/id-payroll

Yang benar:
- [V] Tabel TER (Python & JS) sama persis dan tahan nilai pecahan.
- [V] PTKP, Pasal 17, dan tidak adanya pengurang di bulan Jan–Nov sudah benar.

Kesalahan:
- [V] **BPJS Kes 4% pemberi kerja tidak masuk bruto** (`python/src/id_payroll/pph21.py:134`, `js/src/pph21.ts:112`). Akibatnya Jan 150.810, seharusnya 156.810.
- [V] **JHT 2% pegawai tidak dikurangkan di Desember**. Hanya JP yang dikurangkan (`pph21.py:73`; docstring `:65-67` keliru).
- [V] **Lebih bayar dipotong ke 0**: `max(tax_annual - withheld, 0)` (`pph21.py:80`, `pph21.ts:64`). Contoh resmi Tuan B seharusnya −2.975.000, library menghasilkan 0.
- [V] Plafon biaya jabatan tetap 6 jt dan tidak diprorata (`pph21.py:72`). Untuk Tuan B: PKP 4.500.000, seharusnya 5.600.000.
- [V] Surcharge NPWP ada di bulanan tetapi tidak di Desember.
- [V] Pembulatan Python (`round`, *half-to-even*) berbeda dengan JS (`Math.round`): 13.500 vs 13.501.
- [S] `jp_cap` tetap 10.547.400 untuk semua tahun (`bpjs.py:27`).
- [S] JKK default 0,54%.
- [S] Klaim README:70 "Every number validated against the official worked examples in PMK No. 168/2023" berlebihan.

Tes:
- pytest 20/20 dan vitest 20/20 lulus.
- Hanya satu tes mengutip "Official worked example, PMK 168/2023: K/0, 10.000.000 → 200.000" tanpa nomor halaman, dan contoh itu tidak ditemukan di lampiran PMK 168.

### 6.5 teknologi-umum/pph21

Kesalahan:
- [V] **Pasal 17 memperlakukan batas kumulatif sebagai lebar bracket** (`src/tax.ts:134-149`). Pajak terlalu rendah untuk PKP > 250 jt; misalnya PKP 300 jt menghasilkan 39 jt, seharusnya 44 jt.
- [V] **TER A bracket teratas bertarif `34`, bukan `0.34`** (`tax.ts:207`).
- [V] **TER B bracket 58,5–64 jt bertarif 21%, seharusnya 20%** (`tax.ts:268`).
- [V] **Bracket TER dipilih dari penghasilan neto, bukan bruto** (`tax.ts:46-47,69`). Akibatnya biaya jabatan dan JHT/JP efektif dikurangkan di bulan Jan–Nov.
- [V] Tarif dikalikan ke `salary`, bukan bruto (`tax.ts:70`).
- [V] Basis bulan bonus tidak konsisten (`tax.ts:72-74`).
- [V] Bonus dikecualikan dari basis biaya jabatan.
- [V] PKP tidak dibulatkan.
- [V] Plafon JP 9.559.600 (nilai 2023) dipakai untuk 2024 (`tax.ts:97`).
- [V] Nilai pecahan jatuh ke bracket yang lebih rendah.

Tes: **tidak ada** (`bun test` tanpa file tes). Semua bug berasal dari commit awal 5aa9977.

### 6.6 riod94/payroll-calculator-indonesia

Kesalahan:
- [V] **TER tidak diimplementasikan.** `calculateTER()` hanya stub TODO yang kembali ke metode tahunan (`src/Taxes/Pph21.php:123-129`) dan `terMonthly = []`, padahal "TER" ada di kata kunci composer.
- [V] PPh bulan reguler selalu 0 di alur `getCalculation()`, karena `earnings->annualy->nett` tidak pernah diisi untuk pegawai tetap (`PayrollCalculator.php:393,496,570`; `Pph21.php:38-42`). Tes menutupi bug ini dengan mengisi nilai itu secara manual.
- [V] BPJS Kes 100× terlalu kecil karena dibagi 100 dua kali (`Provisions.php:51-52`, `PayrollCalculator.php:137-141`).
- [V] Surcharge NPWP menjadi 0,2%, bukan 20% (`Provisions.php:61`, `Pph21.php:62,109`).
- [V] Pengurang dikurangkan dua kali (`PayrollCalculator.php:54,126`).
- [V] Desember memakai bruto Desember ×12, tanpa biaya jabatan dan tanpa JHT/JP, dan lebih bayar dipotong ke 0 (`Pph21LastTaxPeriod.php:19-56`).
- [V] Bonus disetahunkan ×12 (`Pph21.php:89-92`).
- [V] Pesangon dan subjek lain memakai PTKP dan Pasal 17, bertentangan dengan PMK 168.
- [V] Contoh di README tidak bisa dijalankan.
- [V] Plafon JP 8.939.700 (2021) dan UMP 3.940.972 (DKI 2019) sudah usang.

Tes:
- 58 metode PHPUnit dengan asersi lemah ("> 0").
- **Tidak ada contoh resmi**.
- Cache PHPUnit yang sempat di-commit mencatat semua tes berstatus *risky*.

### 6.7 steevenz/id-payroll-calculator (2019)

Kesalahan:
- [V] Tarif "Pasal 17" berupa satu persentase datar yang dipilih dari penghasilan neto **bulanan**. Cabang 15% mustahil terpenuhi: `$m < 50000000 and $m > 250000000` (`src/Taxes/AbstractPph.php:78`).
- [V] Biaya jabatan dihitung tetapi tidak dikurangkan sebelum pajak (`PayrollCalculator.php:307-344`).
- [V] Iuran BPJS Kes, JHT, dan JP pegawai mengurangi neto kena pajak.
- [V] JKK pada plafon 100× terlalu besar (`:242`).
- [V] Pegawai tidak tetap selalu berpajak 0 (`:210`).
- [V] PKP tidak dibulatkan.

Tes: **tidak ada**. Repo ini hanya relevan sebagai leluhur untuk studi pemeliharaan.

### 6.8 Ringkasan cepat

| Repo | Tabel TER sesuai PP 58? | Kasus acuan Jan (156.810) | Desember (917.490) | Tes | Tes mengutip contoh resmi? |
|---|---|---|---|---|---|
| muhroyhan | Ya | 156.810 ✔ | 917.490 ✔ | 48 lulus | Ya (PMK 168 Tuan A/B) |
| peco | Ya | 150.810 ✘ | 863.490 ✘ | 20+20 lulus | Klaim satu contoh, tidak ditemukan di PMK 168 |
| pajakin | Ya | 156.810 hanya dengan input bruto lengkap | tidak ada | tidak ada | tidak |
| teknologi-umum | **Tidak** (A teratas, B 58,5–64 jt) | 150.000 ✘ | 1.000.166,34 ✘ | tidak ada | tidak |
| open-synergy | tidak ada data | tidak dijalankan | tidak dijalankan | smoke | tidak |
| riod94 | tidak ada tabel bulanan | (diperkirakan 0) | — | 58 lemah | tidak |
| steevenz | n/a (pra-TER) | — | — | tidak ada | tidak |

Skrip verifikasi (perbandingan tabel, menjalankan kasus) disimpan di scratchpad sesi dan tidak ikut di repo proyek. Jika ingin direproduksi, perbandingan tabel TER cukup diulang terhadap `dataset/01_regulasi/PP_58_2023.pdf` (Lampiran, hal. PDF 12-17).

## 7. Statistik pemeliharaan saat TER masuk (`maintenance_ter_commits.csv`)

| Repo | Commit | Tanggal | File | +/− (semua) | +/− (kode non-tes) | Fungsi tersentuh* | Makna |
|---|---|---|---|---|---|---|---|
| open-synergy | 5d33b69 | 2024-01-22 | 15 | +308/−5 | +163/−0 | 7 | Pengenalan TER: model `pph_21_ter`, `_ter_line`, `_ter_line_categ`, dan `ResPartner.compute_pph_21_ter`. Terjadi 21 hari setelah TER berlaku. |
| open-synergy | 406caaf | 2026-08-11 | 2 | +19/−6 | +19/−6 | 3 | Perbaikan prorata biaya jabatan |
| open-synergy | e65daec | 2026-06-19 | 17 | +699/−0 | +261/−0 | 18 | Konsumen TER pertama (ekspor BPMP Coretax), sekitar 29 bulan setelah TER |
| open-synergy | 8e89572 | 2026-08-25 | 24 | +1070/−0 | +623/−0 | 18 | Modul bupot f113301 (`_get_auto_ter_rate`) |
| open-synergy | 4ec6ee9 | 2026-09-03 | 5 | +456/−1 | +8/−1 | 4 | Perbaikan bug TER 100× |
| open-synergy | 3fdc42e | 2026-09-03 | 6 | +890/−33 | +101/−21 | 7 | TER harian, pesangon, pensiun (hard-coded) |
| pajakin | 4f54364 | 2024-04-29 | 3 | +378/−227 | +378/−203 | 4 | Rewrite 2024 (bukan TER) |
| pajakin | be3c9a6 | 2026-06-29 | 3 | +504/−0 | +504/−0 | 8 | Pengenalan TER, sekitar 30 bulan setelah berlaku. Ditambahkan *di samping* kode lama, bukan menggantikan. |
| pajakin | 0a240a6 | 2026-08-09 | 2 | +141/−9 | +141/−9 | 3 | Gross-up TER |
| teknologi-umum | 5aa9977 | 2024-01-25 | 1 | +340/−0 | +340/−0 | 8 | Commit awal sudah TER (`src/tax.ts`) |
| teknologi-umum | 9ab36fb | 2024-01-26 | 1 | +5/−1 | +5/−1 | 3 | Penyesuaian total |
| muhroyhan | 1d08bab | 2026-08-06 | 25 | +1411/−0 | +1411/−0 | 23 | Commit awal (TER + DTP 2026) |
| muhroyhan | 66964e0 | 2026-08-07 | 6 | +74/−11 | +74/−11 | 6 | Validasi tanggal |
| peco | 40176b4 | 2026-06-27 | 13 | +952/−0 | +952/−0 | 27 | Commit awal (Python + JS) |
| steevenz → riod94 | diff lintas-repo `src/` | 2019 → 2025 | 35 | +2249/−1345 | +2249/−1345 | 99 | Hanya sekitar 17% baris steevenz yang bertahan. **Kode TER yang benar-benar dieksekusi = 0 baris.** |

\*Fungsi tersentuh dihitung dengan heuristik regex (`def`/`function`/arrow-const/`class` pada baris +/− dan konteks hunk), jadi nilainya perkiraan.

Temuan untuk studi biaya pemeliharaan:
1. Pada open-synergy, yang menyimpan aturan sebagai data, pengenalan TER hanya butuh sekitar 160 baris kode logika baru plus tampilan/ACL. Namun nilai tabel tidak pernah dikirim, dan mekanisme versinya cacat untuk TER (lihat 6.1).
2. pajakin menambahkan TER sebagai fitur paralel sekitar 30 bulan terlambat. Logika metode lama tidak dihapus atau disatukan.
3. Pustaka "lahir setelah TER" (muhroyhan, peco, teknologi-umum) tidak punya riwayat transisi, sehingga hanya ukuran awal (*initial size*) yang dapat dibandingkan.
4. Belum ada repo yang menunjukkan transisi TER di dalam satu basis kode dengan riwayat tes regresi. Ini celah yang dapat ditonjolkan dalam evaluasi.

## 8. Mesin rules-as-code (`mesin_rule_as_code.csv`)

Ringkasan (bukti berupa tautan di CSV):
- **OpenFisca** (AGPL-3.0): **tidak ada paket negara Indonesia**. Pencarian di org GitHub, PyPI, dan GitHub search memberi 0 hasil. Parameter YAML bertanggal mendukung versi temporal secara native. Reform berfungsi sebagai lapisan override. Siklus memicu `CycleError` (ada opsi spiral/`max_nb_cycles` untuk rekursi lintas periode), jadi gross-up tidak didukung native.
- **Catala** (Apache-2.0): tidak ada contoh Indonesia. `catala-examples` berisi Prancis, Polandia, AS, dan NSW. Default logic berprioritas cocok untuk pola aturan umum/pengecualian. Versi hukum ditulis dengan tanggal sebagai input. Tidak ada loop atau rekursi dan siklus ditolak, sehingga gross-up harus *closed form*.
- **Payroll Engine** (MIT): lapisan regulasi base → country → industry → company dengan override native. Case value bertanda waktu (periode validitas) dan retro-kalkulasi didukung. Tidak ada regulasi Indonesia. Dokumentasi tidak menyebut gross-up/fixed point (tidak diverifikasi). Arsitekturnya paling mirip dengan proyek ini.
- **HRMQ**: **tidak teridentifikasi** lewat pencarian web. Perlu klarifikasi nama atau URL.
- Lainnya: DMN/Drools (decision table, forward-chaining, atribut `date-effective`), Frappe HRMS (Income Tax Slab `effective_from`, per company), Odoo/OCA payroll (salary rule Python), Blawx (s(CASP)), PolicyEngine (fork OpenFisca), L4/smucclaw.

## 9. Kalkulator daring (`kalkulator_online.csv`)

Lihat CSV. Prinsip yang dipakai: semua kalkulator **hanya untuk perbandingan manual** kecuali ToS-nya secara eksplisit mengizinkan otomasi. Tidak ada halaman yang di-*scrape* dan tidak ada formulir yang dikirim secara otomatis. Ringkasan per situs ada di bagian 9a.

### 9a. Ringkasan per kalkulator

CSV berisi 22 kalkulator; URL dicek pada 2026-10-01. Kolom fitur di bawah diambil dari pengamatan halaman, tanpa pengiriman formulir. Kolom "Otomasi" berisi kesimpulan konservatif dari ToS.

| Kalkulator | TER | Pra-2024 | Desember / masa terakhir | Gross-up | THR/bonus | Otomasi |
|---|---|---|---|---|---|---|
| DJP `kalkulator.pajak.go.id` (resmi) | ya | tidak | ya | ya | ya | **tidak**: ToS melarang penggunaan komersial tanpa izin; manual saja |
| Ortax `kalkulator.ortax.org` (`/ter`, `/yearly`, `/period`) | ya | **ya** (`/period`) | ya | ya | ya | **tidak**: lisensi pribadi non-komersial, ToS melarang otomasi |
| DDTCNews `news.ddtc.co.id/kalkulator` | ya | ya (pilihan tahun pajak) | ya | ya | ya | manual saja (ToS tidak jelas) |
| Pajakku | ya | tidak | ya | ya | ya | **tidak** (ToS Pasal 5.2) |
| Mekari KlikPajak | ya | tidak | tidak | ya | tidak | manual saja |
| Mekari Talenta (ID/EN) | ya | tidak | tidak | ya | tidak | manual saja |
| Gadjian (template Excel) | ya | tidak | tidak | tidak jelas | ya | **tidak**: ToS melarang scraping/robot |
| OnlinePajak | kalkulator tidak ditemukan | — | — | — | — | — |
| kalkulatorpph.com (Kledo/GajiHub) | tidak | ya (metode lama) | tidak jelas | ya | ya | manual saja |
| KalkulatorPajak.id | ya | tidak | ya | ya | ya | **tidak**: ToS melarang bot/scraper |
| KalkulatorPPh21.com | ya | tidak jelas | ya | ya | ya | **tidak**: ToS melarang scraping |
| hitungpajak.online | ya | tidak | sebagian | tidak | tidak | manual saja (tidak ada ToS) |
| StaffAny | tidak | ya (metode lama) | tidak | tidak | ya | manual saja |
| DSK Global | ya | tidak | ya | ya | ya | manual saja |
| PajakPribadiKu | ya | tidak jelas | tidak | tidak | tidak | **tidak**: ToS melarang scraping |
| KalkulasiKita.id | ya | tidak | ya | tidak | ya | **tidak**: ToS melarang scraping |
| Kalkupro | ya | tidak | tidak | tidak | tidak | manual saja |
| ScaleOcean | ya | tidak | ya | ya | ya | manual saja (tidak ada ToS) |
| LinovHR | ya | tidak | ya | ya | ya | manual saja (tidak ada ToS) |
| KlikGaji | ya | tidak | ya (klaim) | tidak jelas | tidak diverifikasi | manual saja |
| pajakin.vercel.app (OSS) | ya | ya (halaman tahunan) | sebagian | ya | ya | lebih baik jalankan kode lokal (lihat bagian 5) |
| pph21.teknologiumum.com (OSS) | — | — | — | — | — | situs mati (DNS tidak resolve); kode MPL-2.0 dijalankan lokal |

Rekomendasi untuk uji black-box **manual** (sampel kecil kasus, hasil dicatat tangan beserta tanggal akses):
- **DJP** sebagai pembanding resmi untuk 2024+.
- **Ortax**, satu-satunya yang mencakup TER, masa pajak terakhir, *dan* metode sebelum 2024.
- **DDTCNews**.
- **DSK Global / ScaleOcean / LinovHR** sebagai pembanding vendor yang mendukung TER, Desember, gross-up, dan THR.

Hasil kalkulator daring juga bukan *ground truth*. DJP sendiri menyatakan kalkulatornya hanya untuk simulasi.

## 10. Rekomendasi baseline

1. **Baseline diferensial utama: `muhroyhan/pph21`** (MIT). Pustaka ini paling benar di antara yang diuji: tabel TER tepat, perlakuan BPJS benar, ada *true-up* Desember dengan lebih bayar, konstanta diversi per tahun pajak, dan tesnya mengutip contoh PMK 168. Gunakan untuk 2024–2026. Ada empat batasan yang perlu diingat. (a) Harus dibungkus agar bruto dibulatkan ke rupiah sebelum lookup, karena bug non-integer. (b) Tidak ada 2023, gross-up, zakat, maupun annualisasi WP baru. (c) BPJS harus dijumlahkan sendiri ke bruto. (d) Hasilnya bukan oracle.
2. **Baseline diferensial kedua: `Peco-lab/id-payroll` (Python)**. Bisa dipanggil langsung dari venv proyek. Berguna justru karena bug-bugnya terdokumentasi: uji diferensial harus menghasilkan selisih yang dapat dijelaskan (BPJS Kes pemberi kerja, JHT di Desember, lebih bayar). Ini sekaligus uji sensitivitas apakah *test suite* proyek mendeteksi kesalahan tersebut.
3. **Studi pemeliharaan dan ekspresivitas: `open-synergy`** (aturan sebagai data bertanggal, riwayat 2022–2026) dan **`pajakin`** (riwayat 2023–2026, TER ditambahkan paralel). Keduanya bukan oracle. Untuk pajakin, karena tidak berlisensi, kode **tidak boleh didistribusikan ulang**; hanya metrik dan kutipan pendek yang dipakai.
4. **Contoh kesalahan untuk uji ketahanan: `teknologi-umum/pph21`**. Bug tabel TER dan Pasal 17 sangat jelas, sehingga cocok sebagai "mutant" pembanding.
5. **Pasangan steevenz → riod94** hanya untuk metrik pemeliharaan lintas-repo. Keduanya tidak dipakai sebagai baseline numerik karena perhitungannya tidak berfungsi.
6. **Untuk tahun pajak 2023 (pra-TER) tidak ada baseline OSS yang layak**. muhroyhan menolak 2023, peco tidak mendukung, dan steevenz/riod94 rusak. Gunakan contoh di PER-16/PJ/2016 (`dataset/04_data_publik/kasus_uji_resmi/`) yang disesuaikan dengan tarif HPP, kalkulator Ortax mode "Sebelum Tahun 2024" secara manual, dan studi kasus xlsx proyek (`dataset/02_studi_kasus/`).
7. **Ground truth**: contoh resmi PMK 168/2023 (29 contoh terindeks di `dataset/04_data_publik/kasus_uji_resmi/pmk168_2023_indeks_contoh.csv`) dan PER-16/PJ/2016, yang ditranskripsi di `dataset/07_kasus_uji_resmi/`, ditambah perhitungan tangan yang dapat ditelusuri.

## 11. Celah dan risiko

- **Lisensi**:
  - pajakin dan ritmehr tidak berlisensi, jadi hak cipta tetap milik penulis. Analisis untuk riset boleh, redistribusi tidak; jangan unggah folder `repos/pajakin` ke repositori publik.
  - open-synergy berlisensi AGPL-3.0. Tidak masalah selama hanya dibandingkan dan tidak dicampur ke kode proyek.
- **Repo sangat baru**: muhroyhan (2026-08) dan peco (2026-06) belum teruji komunitas (0★). Kematangannya rendah.
- **Bantuan LLM di upstream**: sebagian commit open-synergy 2026 ber-trailer `Co-Authored-By: Claude`. Ini perlu dicatat jika penelitian mengklaim baseline sepenuhnya buatan manusia.
- **Tidak dijalankan**: open-synergy (butuh Odoo), riod94, dan steevenz (PHP tidak terpasang). Temuan untuk ketiganya berasal dari pembacaan kode.
- **Fakta belum terverifikasi**:
  - Nilai plafon JP per tahun (9.559.600 / 10.042.300 / 10.547.400 / 11.086.300) dan bulan berlakunya.
  - Isi PMK 105/2025, hanya dicek sebagian oleh peninjau.
  - Dukungan gross-up di Payroll Engine.
  - Identitas "HRMQ".
- Batas *rate limit* GitHub tanpa autentikasi membatasi pencarian. Repo dengan nama tidak lazim, terutama repo privat atau GitLab, mungkin terlewat.
