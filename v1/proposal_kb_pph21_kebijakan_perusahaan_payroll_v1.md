# Proposal Penelitian Tesis S2 Informatika

## Judul

**Judul tesis:**
**Sistem Perhitungan PPh Pasal 21 Berbasis Knowledge Base yang Dapat Disesuaikan dengan Kebijakan Penggajian Perusahaan Tanpa Mengubah Kode Program**

**Judul untuk publikasi jurnal (bahasa Inggris):**
*A Declarative Knowledge Base for Income Tax Article 21 Payroll Computation: Fixed-Point Treatment of Gross-Up under Indonesia's Average Effective Rate Scheme*

---

## Keywords

Knowledge-Based System, Knowledge Base Berlapis, Rules as Code, PPh Pasal 21, Tarif Efektif Rata-rata (TER), Gross-Up, Titik Tetap (Fixed Point), Pengujian Kesesuaian (Conformance Testing), Sistem Penggajian

---

## 1. Latar Belakang

PPh Pasal 21 adalah pajak yang paling dekat dengan kehidupan pekerja di Indonesia. Setiap bulan, pemberi kerja wajib menghitung, memotong, dan melaporkan PPh 21 untuk setiap pegawainya. Penggunaannya sangat masif: jutaan pegawai, ratusan ribu pemberi kerja, dan puluhan aplikasi payroll yang berbeda.

Perhitungan PPh 21 tidak sederhana. Satu perhitungan melibatkan banyak komponen, antara lain:

- **Aturan tarif:** tarif efektif rata-rata (TER) bulanan untuk masa Januari–November, dan tarif progresif Pasal 17 untuk masa pajak terakhir. Sejak 1 Januari 2024, skema ini diatur dalam PP 58/2023 dan PMK 168/2023.
- **Status pegawai:** PTKP berdasarkan status kawin dan jumlah tanggungan, yang menentukan kategori TER (A, B, atau C).
- **Komponen penghasilan:** gaji, tunjangan tetap, tunjangan tidak tetap, lembur, THR, bonus, dan natura.
- **Pengurang:** biaya jabatan, iuran pensiun, dan zakat melalui pemberi kerja.
- **Metode pajak:** gross atau gross-up. Sejak PMK 66/2023 tentang natura, pajak yang ditanggung perusahaan diperlakukan sama dengan tunjangan pajak, sehingga PMK 168/2023 hanya mengenal metode gross dan gross-up.
- **Insentif:** misalnya PPh 21 Ditanggung Pemerintah (DTP) untuk sektor tertentu melalui PMK 10/2025, PMK 72/2025, dan PMK 105/2025.
- **Kondisi khusus:** pegawai yang masuk atau berhenti di tengah tahun.

Di Indonesia, belum ada sistem resmi dari pemerintah untuk menghitung PPh 21. DJP Online dan Coretax hanya menyediakan platform pelaporan. Akibatnya, setiap pemberi kerja bergantung pada aplikasi payroll komersial, library, spreadsheet, atau perhitungan manual. Kesalahan hitung benar-benar terjadi di lapangan. Sebuah penelitian di dinas pemerintah daerah, misalnya, menemukan bahwa status perkawinan dan jumlah tanggungan tidak diperhitungkan dalam PTKP, sehingga PPh 21 yang dihitung lebih tinggi dari seharusnya.

Sebagian besar aplikasi perhitungan PPh 21 menanamkan aturan pajak langsung di dalam kode program. Pendekatan ini punya dua masalah:

1. **Setiap perubahan aturan membutuhkan perubahan kode.** Contoh nyatanya adalah metode gross-up. Selama ini, tunjangan pajak dihitung dengan rumus yang diturunkan manual per lapisan tarif progresif, misalnya *(PKP − 0) × 5/95* untuk lapisan pertama. Ketika TER berlaku pada 2024, rumus-rumus tersebut tidak lagi relevan dan harus diturunkan ulang serta diprogram ulang di setiap aplikasi.
2. **Konfigurasi per perusahaan terbatas pada pilihan yang sudah dikodekan pengembang.** Aplikasi payroll komersial umumnya menyediakan pilihan metode gross, gross-up, atau nett. Namun, kebijakan penggajian yang tidak disediakan sebagai pilihan tetap membutuhkan perubahan kode.

Di bidang Knowledge-Based System, pemisahan pengetahuan dari kode program adalah prinsip dasar. Pendekatan ini sudah diterapkan untuk pajak dan payroll di luar negeri, misalnya pada penelitian penalaran otomatis untuk payroll di Belgia (AAAI 2021), bahasa Catala untuk hukum pajak Prancis, serta mesin payroll open source dengan lapisan regulasi yang dapat ditumpuk dan ditimpa per penyewa. Namun, sejauh penelusuran awal, pendekatan ini belum diterapkan untuk PPh 21 Indonesia dalam publikasi ilmiah.

Selain itu, ada satu komponen PPh 21 yang belum pernah dianalisis secara formal: **gross-up di bawah skema TER**. Gross-up adalah definisi melingkar: tunjangan pajak harus sama dengan pajak yang dipotong, padahal pajak tersebut dihitung dari gaji ditambah tunjangan pajak itu sendiri. Di bawah tarif progresif, persamaan ini berperilaku baik. Di bawah TER, tarif berlaku rata untuk seluruh penghasilan bruto dan melompat di setiap batas lapisan. Analisis awal (Bagian 9.3) menunjukkan bahwa di sekitar batas lapisan, persamaan gross-up **dapat memiliki lebih dari satu solusi yang sama-sama sah**. Jika terbukti secara umum, aplikasi payroll yang berbeda bisa menghasilkan tunjangan pajak yang berbeda untuk pegawai yang sama, dan semuanya tampak benar.

Penelitian ini membangun sistem perhitungan PPh 21 berbasis knowledge base dua lapis (regulasi dan kebijakan perusahaan), merepresentasikan komponen melingkar seperti gross-up secara deklaratif dan menganalisisnya secara formal, lalu mengevaluasi manfaatnya secara empiris terhadap implementasi yang sudah ada.

---

## 2. Identifikasi Masalah

1. Perhitungan PPh 21 melibatkan banyak komponen yang saling berinteraksi, dan kombinasinya berbeda di setiap perusahaan.
2. Aturan pajak yang ditanam di kode program membuat setiap perubahan aturan atau kebijakan perusahaan membutuhkan perubahan kode, yang lambat, mahal, dan rawan kesalahan.
3. Komponen melingkar seperti gross-up saat ini ditangani dengan rumus manual yang harus diturunkan ulang setiap kali struktur tarif berubah.
4. Perilaku gross-up di bawah skema TER, terutama di sekitar batas lapisan, belum pernah dianalisis secara formal.
5. Belum ada bukti empiris tentang seberapa konsisten implementasi PPh 21 yang beredar di Indonesia terhadap aturan yang berlaku.

---

## 3. Penelitian Terkait dan Posisi Penelitian

### 3.1 Penelitian dan Sistem Internasional

| Penelitian / Sistem | Yang dilakukan | Perbedaan dengan penelitian ini |
|---|---|---|
| Dumancic dkk., *Automated Reasoning and Learning for Automated Payroll Management* (AAAI 2021) | Menerjemahkan hukum pajak Belgia ke representasi formal dalam satu knowledge base, dikompilasi ke constraint solver untuk mencari kebijakan payroll optimal; dipakai lembaga asuransi sosial | Fokus pada optimasi kebijakan payroll, bukan konfigurasi kebijakan perusahaan dan komponen melingkar; hukum Belgia |
| Liu & Liu, *Salary Management System Rule-Based Rules Engine* (2011) | Rules engine yang memisahkan logika bisnis penggajian dari aplikasi agar perubahan aturan tidak mengubah kode | Konsep pemisahan yang sama, tanpa analisis komponen melingkar dan tanpa evaluasi empiris |
| Payroll Engine (open source, MIT) | Lapisan regulasi yang dapat ditumpuk, ditimpa, dan dibagi antarpenyewa | Kerangka umum; tidak membahas PPh 21 dan gross-up di bawah TER |
| HRMQ (open source) | DSL deklaratif per yurisdiksi; negara baru ditambahkan sebagai data | Menyediakan jalan keluar kode khusus untuk ketentuan yang tidak bisa dinyatakan DSL |
| Catala dan OpenFisca | Bahasa dan platform *Rules as Code* untuk pajak dan tunjangan | Fokus pada aturan pemerintah, bukan kebijakan pemberi kerja |
| Kalkulator gross-up di AS | Menyelesaikan gross-up secara iteratif terhadap tarif progresif | Di bawah tarif progresif marginal, solusi berperilaku baik; tidak membahas tarif rata bertingkat seperti TER |

### 3.2 Penelitian di Indonesia

| Penelitian | Yang dilakukan | Perbedaan dengan penelitian ini |
|---|---|---|
| Tan & Putri (2020), sistem pakar PPh berbasis Android | Forward chaining untuk simulasi PPh 21 | Aturan dikodekan manual; tidak ada lapisan kebijakan; tanpa verifikasi formal |
| Aplikasi perhitungan PPh 21 (VB6/MS Access, 2019; mobile, 2015; Excel, program pengabdian) | Otomasi perhitungan PPh 21 | Aturan ditanam di kode atau spreadsheet |
| Penelitian akuntansi tentang gross-up setelah PP 58/2023 | Studi kasus perbandingan gross-up sebelum dan sesudah TER di satu perusahaan | Deskriptif; tidak menganalisis sifat matematis gross-up |
| Penelitian akuntansi tentang lebih bayar akibat TER | Studi kasus dan simulasi | Tidak membangun sistem |
| Studi PPh 21 di dinas pemerintah daerah | Menemukan kesalahan hitung PTKP | Bukti masalah nyata, tanpa solusi sistem |
| LexID (Universitas Indonesia, 2023) | Knowledge graph ribuan dokumen hukum Indonesia | Untuk pencarian dokumen, bukan perhitungan pajak |
| Aplikasi payroll komersial (Gadjian, Talenta, dan lainnya) | Konfigurasi gross/gross-up/nett | Tertutup; konfigurasi terbatas pada pilihan yang dikodekan |

### 3.3 Posisi Penelitian

- **Bukan kebaruan penelitian ini:** memisahkan aturan pajak dari kode, lapisan regulasi yang dapat ditimpa, dan kalkulator PPh 21. Semua ini sudah ada, dan penelitian ini **mengadopsinya** sebagai fondasi.
- **Kebaruan penelitian ini:** (1) analisis formal komponen melingkar PPh 21, terutama gross-up di bawah TER; (2) studi empiris kesesuaian, biaya pemeliharaan, dan ekspresivitas pada implementasi PPh 21 di Indonesia.

---

## 4. Rumusan Masalah

1. Bagaimana merepresentasikan aturan PPh 21 dan kebijakan penggajian perusahaan sebagai dua lapisan knowledge base yang dapat digabungkan tanpa perubahan kode program?
2. Bagaimana merepresentasikan komponen melingkar PPh 21 (gross-up gaji, THR, bonus, dan natura yang ditanggung) secara deklaratif, dan dalam kondisi apa solusinya ada, tunggal, atau ganda di bawah skema TER?
3. Seberapa konsisten implementasi PPh 21 yang beredar dibandingkan dengan knowledge base yang tervalidasi, dan pada kondisi apa ketidaksesuaian terjadi?
4. Seberapa besar pengurangan biaya pemeliharaan dan peningkatan ekspresivitas yang diberikan knowledge base dibandingkan aturan yang ditanam di kode?

---

## 5. Tujuan Penelitian

1. Membangun knowledge base PPh 21 dua lapis (regulasi dan kebijakan perusahaan) beserta mesin perhitungan yang tidak perlu diubah ketika aturan atau kebijakan berubah.
2. Merumuskan komponen melingkar PPh 21 sebagai persamaan titik tetap, lalu mengkarakterisasi secara formal keberadaan dan ketunggalan solusinya di bawah TER untuk setiap kategori dan lapisan.
3. Mengusulkan aturan penyelesaian yang konsisten untuk kasus dengan solusi ganda.
4. Mengukur tingkat kesesuaian implementasi PPh 21 yang tersedia publik terhadap knowledge base.
5. Mengukur biaya pemeliharaan dan ekspresivitas knowledge base dibandingkan implementasi berbasis kode.
6. Menghasilkan aplikasi perhitungan PPh 21 yang menampilkan rincian aturan dan pasal yang dikenakan.

---

## 6. Manfaat Penelitian

### Manfaat Akademik

- Analisis formal pertama (sejauh penelusuran) tentang gross-up di bawah skema tarif efektif rata-rata bertingkat.
- Metode representasi deklaratif untuk komponen melingkar dalam sistem pajak berbasis knowledge base.
- Studi empiris kesesuaian implementasi PPh 21 di Indonesia.
- Knowledge base PPh 21 dan kasus uji yang dirilis terbuka.

### Manfaat Praktis

- **Pengembang payroll:** satu mesin perhitungan untuk banyak perusahaan; perubahan aturan cukup mengubah knowledge base.
- **HR dan pemberi kerja:** kebijakan penggajian bisa diatur tanpa pengembang, dan hasil perhitungan disertai rincian pasal.
- **Pegawai:** potongan di slip gaji dapat dijelaskan dan diperiksa.
- **Pembuat kebijakan:** masukan tentang potensi ambiguitas gross-up di bawah TER.

### Batas Manfaat

Sistem ini adalah prototipe penelitian, bukan alat konsultasi pajak resmi.

---

## 7. Novelty

### 7.1 Yang Bukan Novelty

- Pemisahan aturan pajak atau payroll dari kode program (AAAI 2021, rules engine 2011, Payroll Engine, HRMQ, Catala, OpenFisca).
- Lapisan regulasi yang dapat ditumpuk dan ditimpa per penyewa (Payroll Engine).
- Penyelesaian gross-up secara iteratif (kalkulator gross-up di AS).
- Kalkulator dan sistem pakar PPh 21 (banyak penelitian di Indonesia).

### 7.2 Novelty Penelitian Ini

1. **Analisis formal komponen melingkar di bawah TER.** Karakterisasi lengkap kapan persamaan gross-up memiliki solusi tunggal atau ganda, untuk setiap kategori TER dan setiap batas lapisan, disertai aturan penyelesaian yang konsisten.
2. **Representasi deklaratif komponen melingkar** sebagai definisi, sehingga perubahan struktur tarif tidak membutuhkan penurunan ulang rumus.
3. **Studi empiris di Indonesia:** kesesuaian implementasi PPh 21 yang beredar, biaya pemeliharaan saat TER berlaku, dan ekspresivitas kebijakan penggajian.
4. **Penerapan knowledge base dua lapis pada PPh 21**, termasuk pemeriksaan apakah mesin payroll berlapis yang sudah ada dapat menyatakan gross-up di bawah TER tanpa kode khusus.

### 7.3 Penilaian Jujur

- **Kekuatan novelty: sedang, dengan potensi naik** jika analisis gross-up (poin 1) menghasilkan temuan yang jelas dan studi kesesuaian (poin 3) menemukan ketidaksesuaian nyata.
- Gagasan knowledge base untuk payroll **bukan** kontribusi baru dan tidak diklaim sebagai kontribusi.
- Klaim "belum ada" pada poin 1 dan 3 berdasarkan penelusuran awal, dan wajib dikonfirmasi melalui tinjauan pustaka sistematis.

---

## 8. Batasan Ruang Lingkup

1. **Jenis pajak:** hanya PPh Pasal 21.
2. **Subjek:** pegawai tetap, termasuk yang masuk atau berhenti di tengah tahun. Pegawai tidak tetap, bukan pegawai, dan pensiunan tidak dibahas.
3. **Perhitungan:** pemotongan bulanan (TER) dan masa pajak terakhir (Pasal 17).
4. **Komponen penghasilan:** gaji, tunjangan tetap dan tidak tetap, THR, bonus, natura sederhana, iuran pensiun, dan biaya jabatan.
5. **Metode pajak:** gross dan gross-up.
6. **Insentif:** PPh 21 DTP sesuai PMK 10/2025, PMK 72/2025, dan PMK 105/2025.
7. **Periode regulasi:** tahun pajak 2024 sampai versi terbaru saat penelitian. PER-16/PJ/2016 dipakai sebagai pembanding historis.
8. **Tidak dibahas:** PPh selain Pasal 21, perlakuan tanpa NPWP/NIK, penghasilan dari lebih dari satu pemberi kerja, perjanjian pajak internasional, dan penggunaan LLM.
9. **Data:** tidak memakai data pajak riil pegawai. Kasus uji dibuat berdasarkan contoh resmi dan dibangkitkan secara sintetis.
10. **Implementasi yang diuji:** hanya yang tersedia publik (library open source dan kalkulator online), sesuai ketentuan layanannya.

---

## 9. Landasan Konsep

### 9.1 Knowledge Base Dua Lapis

- **Lapisan regulasi** memuat aturan yang berlaku untuk semua pemberi kerja: tabel TER, PTKP, tarif Pasal 17, biaya jabatan, aturan masa pajak terakhir, dan DTP. Setiap aturan menyimpan masa berlaku dan pasal sumbernya.
- **Lapisan kebijakan perusahaan** memuat konfigurasi setiap pemberi kerja: metode gross atau gross-up, daftar komponen penghasilan, jadwal THR dan bonus, dan perlakuan natura.
- **Mesin perhitungan** menggabungkan keduanya dan tidak pernah diubah ketika aturan atau kebijakan berubah.

### 9.2 Gross-Up sebagai Persamaan Titik Tetap

Misalkan:
- *B* = penghasilan bruto sebelum tunjangan pajak,
- *T* = tunjangan pajak,
- *r(x)* = tarif TER untuk penghasilan bruto *x*.

Definisi gross-up: tunjangan pajak sama dengan pajak yang dipotong atas penghasilan bruto setelah ditambah tunjangan tersebut:

> *T = r(B + T) × (B + T)*

Dengan *x = B + T*, syaratnya menjadi:

> *x − r(x) × x = B*, atau *g(x) = B* dengan *g(x) = x × (1 − r(x))*

Artinya, mencari gross-up sama dengan mencari penghasilan bruto *x* yang menghasilkan penghasilan bersih tepat sebesar *B*.

- Di dalam satu lapisan TER, *r* konstan, sehingga *g* naik secara linear dan solusinya adalah *x = B / (1 − r)*, **asalkan** *x* memang jatuh di lapisan tersebut.
- Di setiap batas lapisan, *r* melompat naik, sehingga *g* **turun mendadak**. Akibatnya, untuk nilai *B* di sekitar batas lapisan, persamaan bisa dipenuhi oleh dua nilai *x*: satu tepat sebelum batas dan satu tepat sesudah batas.

### 9.3 Contoh Awal (Hipotesis yang Akan Dibuktikan)

Menggunakan TER kategori A (PP 58/2023): lapisan di atas Rp13,75 juta sampai Rp15,1 juta bertarif 6%, dan lapisan di atas Rp15,1 juta sampai Rp16,95 juta bertarif 7%. Tabel ini harus diverifikasi ulang dengan lampiran resmi.

Seorang pegawai TK/0 dengan metode gross-up, di mana penghasilan bersih yang dijanjikan *B* = Rp14.100.000:

| Kemungkinan | Penghasilan bruto *x* | Lapisan dan tarif | Tunjangan pajak = PPh 21 | Penghasilan bersih |
|---|---|---|---|---|
| Solusi 1 | Rp15.000.000 (= 14.100.000 / 0,94) | Rp13,75–15,1 juta → 6% | Rp900.000 | Rp14.100.000 |
| Solusi 2 | Rp15.161.290 (= 14.100.000 / 0,93) | Rp15,1–16,95 juta → 7% | Rp1.061.290 | Rp14.100.000 |

Kedua solusi sama-sama memenuhi definisi gross-up dan menghasilkan penghasilan bersih yang sama. Namun, biaya perusahaan dan PPh 21 yang disetor berbeda sekitar **Rp161.290 per bulan**. Lebar pita nilai *B* yang memiliki dua solusi di batas ini kira-kira Rp15,1 juta × 1% ≈ Rp151.000.

**Hipotesis penelitian:**
- **H1:** di bawah TER, persamaan gross-up bulanan selalu memiliki setidaknya satu solusi, tetapi memiliki solusi ganda di pita tertentu di sekitar setiap batas lapisan.
- **H2:** implementasi yang berbeda memilih solusi yang berbeda di pita tersebut, sehingga terjadi ketidaksesuaian antaraplikasi.
- **H3:** pada masa pajak terakhir, yang memakai tarif progresif Pasal 17, gross-up selalu memiliki solusi tunggal.

Ketiga hipotesis akan dibuktikan atau dibantah secara formal dan empiris. Pembulatan rupiah dan aturan pembulatan resmi juga akan diperhitungkan, karena dapat mengubah hasil. Perlu dicek juga apakah PMK 168/2023 atau publikasi DJP menetapkan prosedur tertentu untuk menentukan tunjangan pajak. Jika ya, pertanyaannya bergeser menjadi apakah prosedur resmi tersebut konsisten dan tunggal.

---

## 10. Rancangan Sistem

### 10.1 Arsitektur

```
┌────────────────────────────┐   ┌──────────────────────────────┐
│ Lapisan Regulasi (YAML)    │   │ Lapisan Kebijakan Perusahaan │
│ TER, PTKP, Pasal 17, DTP,  │   │ (YAML per perusahaan)        │
│ biaya jabatan, masa berlaku│   │ metode, komponen, THR/bonus  │
│ + pasal sumber             │   │                              │
└─────────────┬──────────────┘   └───────────────┬──────────────┘
              └──────────────┬───────────────────┘
                             ▼
              ┌──────────────────────────────┐
              │ Mesin Perhitungan (Python)   │
              │ - pemilihan aturan berlaku   │
              │ - penyelesai titik tetap     │
              │ - jejak aturan & pasal       │
              └──────────────┬───────────────┘
                             ▼
      ┌─────────────────────────────────────────────┐
      │ Hasil PPh 21 + rincian aturan dan pasal     │
      │ Aplikasi web (kalkulator & konfigurasi)     │
      └─────────────────────────────────────────────┘

      Analisis formal (Z3): keberadaan & ketunggalan solusi,
      konsistensi konfigurasi kebijakan
```

### 10.2 Contoh Isi Lapisan Regulasi

```yaml
aturan: ter_bulanan
sumber: PP 58/2023, Lampiran
berlaku:
  mulai: 2024-01-01
kategori: A
status_ptkp: [TK/0, TK/1, K/0]
lapisan:
  - {batas_atas: 5400000,  tarif: 0.0}
  - {batas_atas: 5650000,  tarif: 0.0025}
  # ... dan seterusnya sesuai lampiran
```

### 10.3 Contoh Isi Lapisan Kebijakan Perusahaan

```yaml
perusahaan: PT Contoh
metode_pph21: gross_up
komponen:
  - kode: gaji_pokok
    jenis: teratur
  - kode: tunjangan_transport
    jenis: teratur
  - kode: thr
    jenis: tidak_teratur
    bulan_bayar: 3
  - kode: tunjangan_pph
    definisi: "pph21_masa_ini"     # definisi melingkar
aturan_penyelesaian_gross_up: solusi_terkecil   # dipakai bila solusi ganda
```

Mesin perhitungan membaca kedua file ini. Menambah perusahaan baru atau mengubah aturan cukup dengan mengubah file, tanpa mengubah kode.

---

## 11. Dataset yang Digunakan

### A. Sumber Pengetahuan (Regulasi)

| No | Dataset | Isi | Sumber | Format | Akses | Kegunaan |
|---|---|---|---|---|---|---|
| 1 | UU PPh s.t.d.t.d. UU HPP | Pasal 17, Pasal 21, PTKP | JDIH Kemenkeu, peraturan.bpk.go.id | PDF | Publik | Lapisan regulasi |
| 2 | PMK 101/PMK.010/2016 | Besaran PTKP | JDIH Kemenkeu | PDF | Publik | Lapisan regulasi |
| 3 | PP 58/2023 | Tabel TER kategori A, B, C | JDIH Kemenkeu | PDF | Publik | Lapisan regulasi |
| 4 | PMK 168/2023 | Tata cara pemotongan, metode gross dan gross-up, masa pajak terakhir | JDIH Kemenkeu | PDF | Publik | Lapisan regulasi dan contoh resmi |
| 5 | PMK 66/2023 | Perlakuan natura dan kenikmatan | JDIH Kemenkeu | PDF | Publik | Lapisan regulasi |
| 6 | PMK 10/2025, PMK 72/2025, PMK 105/2025 | Insentif PPh 21 DTP | JDIH Kemenkeu | PDF | Publik | Lapisan regulasi |
| 7 | PER-16/PJ/2016 | Metode sebelum TER, termasuk rumus gross-up lama | pajak.go.id | PDF | Publik | Pembanding historis |

### B. Kasus Uji Resmi

| No | Dataset | Isi | Sumber | Ukuran | Kegunaan |
|---|---|---|---|---|---|
| 8 | Contoh di lampiran PMK 168/2023 | Contoh perhitungan resmi, termasuk gross-up | JDIH Kemenkeu | Puluhan contoh | Validasi knowledge base |
| 9 | Publikasi DJP | Contoh perhitungan TER dan gross-up | pajak.go.id | Puluhan contoh | Validasi tambahan |

### C. Implementasi yang Diuji

| No | Dataset | Isi | Sumber | Ukuran | Kegunaan |
|---|---|---|---|---|---|
| 10 | Library open source PPh 21 | Kode dan riwayat git (misalnya komponen PHP penghitung gaji dan forks-nya) | GitHub, Packagist | 3–5 library | Uji kesesuaian dan biaya pemeliharaan |
| 11 | Kalkulator PPh 21 online | Kalkulator publik dari penyedia jasa aplikasi perpajakan dan vendor payroll | Situs publik | 3–5 kalkulator | Uji kesesuaian (black-box) |
| 12 | Mesin payroll berlapis | Payroll Engine, HRMQ | GitHub | 1–2 sistem | Pembanding ekspresivitas |

### D. Data yang Dibangun dalam Penelitian

| No | Dataset | Isi | Cara Membuat | Target Ukuran | Kegunaan |
|---|---|---|---|---|---|
| 13 | Knowledge base PPh 21 | Lapisan regulasi, tervalidasi | Kodifikasi manual, divalidasi ahli pajak | Ratusan item aturan | Acuan kebenaran |
| 14 | Katalog kebijakan penggajian | 10–20 variasi kebijakan | Disusun dari PMK 168/2023, PMK 66/2023, dan dokumentasi publik vendor | 10–20 konfigurasi | Uji ekspresivitas |
| 15 | Kasus uji sintetis | Profil pegawai 12 bulan: status PTKP, komponen gaji, THR, bonus, metode, bulan mulai kerja | Program pembangkit, difokuskan pada titik rawan (batas lapisan TER, pita gross-up ganda, masuk tengah tahun) | 10.000–100.000 kasus | Uji kesesuaian |
| 16 | Peta solusi gross-up | Pita solusi tunggal/ganda per kategori TER dan batas lapisan | Hasil analisis formal | 3 kategori × seluruh batas lapisan | Luaran K2 |

---

## 12. Metode Penelitian (Per Tahap)

### Tahap 1 – Tinjauan Pustaka Sistematis (Bulan 1–2)
- Menelusuri penelitian knowledge base untuk pajak dan payroll, Rules as Code, mesin payroll berlapis, dan analisis gross-up.
- Menelusuri penelitian Indonesia di Garuda, SINTA, dan Google Scholar dengan kata kunci "sistem pakar PPh 21", "knowledge base pajak", "rule engine penggajian", "gross up TER", dan "aplikasi payroll PPh 21".
- Mengonfirmasi atau merevisi klaim novelty.
- **Luaran:** tabel pembeda penelitian terkait.

### Tahap 2 – Pengumpulan dan Kodifikasi Regulasi (Bulan 2–3)
- Mengumpulkan regulasi no. 1–7 dan mengecek status berlakunya.
- Memecah setiap pasal menjadi kondisi, akibat, pengecualian, parameter, masa berlaku, dan pasal sumber.
- Mencatat keputusan interpretasi (misalnya pembulatan) sebagai daftar asumsi.
- **Luaran:** tabel kodifikasi dan daftar asumsi.

### Tahap 3 – Knowledge Base Lapisan Regulasi (Bulan 3–4)
- Menyusun lapisan regulasi dalam YAML sesuai skema.
- Memvalidasi terhadap seluruh contoh resmi (target 100% cocok).
- Meminta minimal satu ahli pajak memeriksa knowledge base dan daftar asumsi.
- **Luaran:** lapisan regulasi tervalidasi.

### Tahap 4 – Lapisan Kebijakan Perusahaan dan Mesin Perhitungan (Bulan 5–6)
- Merancang skema lapisan kebijakan perusahaan.
- Membangun mesin perhitungan Python yang menggabungkan kedua lapisan, memilih aturan berlaku berdasarkan tanggal, dan mencatat jejak aturan serta pasal.
- Membangun penyelesai titik tetap umum untuk komponen melingkar.
- Membangun aplikasi web sederhana untuk kalkulator dan konfigurasi.
- **Luaran:** sistem perhitungan yang berjalan.

### Tahap 5 – Analisis Formal Komponen Melingkar (Bulan 7–8)
- Merumuskan setiap komponen melingkar sebagai persamaan titik tetap: gross-up gaji bulanan, gross-up pada bulan THR atau bonus, natura yang ditanggung, dan gross-up pada masa pajak terakhir.
- Membuktikan secara analitis dan memverifikasi dengan Z3:
  - kapan solusi ada;
  - kapan solusi tunggal;
  - di pita mana solusi ganda muncul, untuk setiap kategori TER dan batas lapisan.
- Memperhitungkan pembulatan rupiah.
- Menguji hipotesis H1 dan H3.
- Mengusulkan aturan penyelesaian untuk solusi ganda (misalnya solusi dengan tunjangan terkecil) dan menganalisis konsekuensinya.
- **Luaran:** peta solusi gross-up (dataset no. 16) dan aturan penyelesaian.

### Tahap 6 – Studi Kesesuaian (Bulan 9)
- Membangkitkan kasus uji yang difokuskan pada titik rawan.
- Menjalankan kasus uji pada setiap implementasi (no. 10 dan 11) dan membandingkan hasilnya dengan knowledge base.
- Mengelompokkan ketidaksesuaian berdasarkan penyebab (batas lapisan, gross-up, THR, masuk tengah tahun, pembulatan).
- Menguji hipotesis H2.
- Melaporkan temuan kepada pengembang terkait sebelum dipublikasikan.
- **Luaran:** laporan kesesuaian.

### Tahap 7 – Biaya Pemeliharaan dan Ekspresivitas (Bulan 10)
- **Biaya pemeliharaan:** dari riwayat git library open source, mengukur perubahan kode saat TER berlaku (jumlah file, baris, dan fungsi yang berubah), lalu membandingkannya dengan jumlah entri knowledge base yang perlu diubah.
- **Ekspresivitas:** mencoba menyatakan 10–20 kebijakan penggajian (dataset no. 14) dalam sistem ini, dalam mesin payroll berlapis yang sudah ada, dan dalam pilihan konfigurasi aplikasi komersial (berdasarkan dokumentasi publik). Hitung berapa yang bisa dinyatakan tanpa kode.
- Menguji secara khusus apakah gross-up di bawah TER bisa dinyatakan tanpa kode khusus di mesin payroll berlapis.
- **Luaran:** tabel perbandingan biaya pemeliharaan dan ekspresivitas.

### Tahap 8 – Penulisan dan Rilis Artefak (Bulan 11–12)
- Menulis tesis dan artikel jurnal.
- Merilis knowledge base, katalog kebijakan, kasus uji, dan peta solusi gross-up secara terbuka.
- **Luaran:** tesis, artikel, dan repositori.

---

## 13. Rancangan Evaluasi dan Metrik

| Aspek | Metrik | Target / Keterangan |
|---|---|---|
| Kebenaran knowledge base | Kecocokan dengan contoh resmi | 100% |
| Analisis gross-up | Jumlah dan lebar pita solusi ganda per kategori dan batas lapisan; status H1 dan H3 | Terbukti atau terbantah secara formal |
| Kesesuaian implementasi | Persentase kasus uji yang berbeda dari knowledge base, per implementasi dan per jenis kondisi; besar selisih | Dilaporkan apa adanya |
| Hipotesis H2 | Apakah implementasi berbeda memilih solusi gross-up yang berbeda di pita ganda | Terbukti atau terbantah |
| Biaya pemeliharaan | Baris/file kode yang berubah vs entri knowledge base yang berubah saat TER berlaku | Perbandingan kuantitatif |
| Ekspresivitas | Jumlah kebijakan yang dapat dinyatakan tanpa kode | Dibandingkan dengan mesin berlapis dan aplikasi komersial |
| Kinerja | Waktu perhitungan per pegawai dan per 10.000 pegawai | Wajar untuk payroll bulanan |

---

## 14. Teknologi

| Komponen | Teknologi | Lisensi |
|---|---|---|
| Mesin perhitungan | Python | PSF |
| Knowledge base | YAML/JSON dengan skema tetap, disimpan di Git | – |
| Analisis formal | Z3 (`z3-solver`) | MIT |
| Kasus uji | pytest | MIT |
| Aplikasi | FastAPI dan Streamlit | MIT / Apache 2.0 |

Z3 hanya dipakai untuk analisis titik tetap dan pemeriksaan konsistensi konfigurasi. Perhitungan harian dilakukan mesin Python biasa.

---

## 15. Jadwal Penelitian

| Bulan | Kegiatan |
|---|---|
| 1–2 | Tinjauan pustaka sistematis |
| 2–3 | Pengumpulan dan kodifikasi regulasi |
| 3–4 | Knowledge base lapisan regulasi dan validasi |
| 5–6 | Lapisan kebijakan perusahaan, mesin perhitungan, dan aplikasi |
| 7–8 | Analisis formal komponen melingkar |
| 9 | Studi kesesuaian |
| 10 | Biaya pemeliharaan dan ekspresivitas |
| 11–12 | Penulisan tesis, artikel, dan rilis artefak |

---

## 16. Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Penafsiran aturan keliru | Acuan kebenaran salah | Validasi ahli pajak; daftar asumsi terdokumentasi |
| PMK 168/2023 ternyata menetapkan prosedur gross-up tertentu | Pertanyaan K2 berubah | Analisis bergeser ke apakah prosedur resmi konsisten dan tunggal; tetap menjadi kontribusi |
| Pembulatan menghilangkan pita solusi ganda | H1 sebagian terbantah | Tetap dilaporkan sebagai hasil formal yang sah |
| Implementasi yang diuji sedikit atau sulit diakses | Studi kesesuaian lemah | Prioritaskan library open source; kalkulator online sesuai ketentuan layanan |
| Semua implementasi ternyata sesuai | Temuan K3 kurang menarik | Tetap bernilai sebagai acuan tervalidasi; perkuat dengan biaya pemeliharaan dan ekspresivitas |
| Aturan berubah di tengah penelitian | Knowledge base harus diperbarui | Justru menjadi demonstrasi pembaruan tanpa perubahan kode |
| Cakupan melebar | Waktu habis | Cakupan dikunci pada Bagian 8 |

---

## 17. Luaran dan Target Publikasi

| Luaran | Target | Peluang (penilaian jujur) |
|---|---|---|
| Tesis S2 | – | Layak |
| Artikel utama: knowledge base dua lapis + analisis gross-up di bawah TER + kesesuaian | SINTA 1, lalu Scopus Q2 | SINTA 1 realistis; Q2 mungkin jika H1/H2 terbukti dengan jelas |
| Artikel kedua (opsional): studi kesesuaian aplikasi payroll PPh 21 | SINTA 2 | Realistis jika data cukup kaya |
| Repositori terbuka: knowledge base, kasus uji, peta solusi gross-up | GitHub/Zenodo | – |

---

## 18. Referensi Awal

1. Dumancic, S., Meert, W., Goethals, S., Stuyckens, T., Huygen, J., & Denies, K. (2021). *Automated Reasoning and Learning for Automated Payroll Management.* Proceedings of the AAAI Conference on Artificial Intelligence, 35(17), 15107–15116.
2. Liu, Y., & Liu, B. (2011). *The Preliminary Investigation of Salary Management System Rule-Based Rules Engine.* SciTePress.
3. Payroll Engine. *Open-source payroll automation framework* (lisensi MIT). payrollengine.org.
4. Conduction. *HRMQ Payroll Engine documentation.*
5. Merigoux, D., Chataing, N., & Protzenko, J. *Catala: A Programming Language for the Law.*
6. OpenFisca. *Open-source rules as code engine.*
7. Holzenberger, N., Blair-Stanek, A., & Van Durme, B. (2020). *A Dataset for Statutory Reasoning in Tax Law Entailment and Question Answering.*
8. Muninggar, N. S., & Krisnadhi, A. A. (2023). *LexID: The Metadata and Semantic Knowledge Graph Construction of Indonesian Legal Document.* Jurnal Ilmu Komputer dan Informasi, 16(1), 15–46.
9. Tan, J., & Putri, A. D. (2020). *Sistem Pakar Perhitungan Pajak Penghasilan Berbasis Android.* COMASIE, 3(1), 38–43.
10. Sari, D. M., Darmawiguna, I. G. M., & Arthana, I. K. R. (2015). *Sistem Informasi Perhitungan Pajak PPh 21 Berbasis Mobile.* KARMAPATI, 4(5).
11. *Perancangan Aplikasi Perhitungan Pajak Tahunan PPh Pasal 21* (2019). Journal of Information Technology and Accounting, 2(1).
12. *Perancangan Aplikasi Perhitungan PPh Pasal 21 berbasis Microsoft Excel.* Jurnal IBIK.
13. Studi penerapan metode gross-up PPh 21 sebelum dan sesudah PP 58/2023. Jurnal COSTING.
14. *Evaluasi Risiko Lebih Bayar PPh 21 Akibat Implementasi Tarif Efektif Rata-Rata.* Jurnal Wahana Akuntansi, UNJ.
15. Studi perhitungan PPh 21 di Dinas Pemberdayaan Masyarakat dan Desa Kabupaten Kudus. Jurnal Ekono Insentif.
16. Studi sistem informasi akuntansi penggajian dan penerapan TER di PT Putra Dumas Lestari. Jurnal Mankeu, 14(2), 2025.
17. de Moura, L., & Bjørner, N. (2008). *Z3: An Efficient SMT Solver.* TACAS 2008.
18. Regulasi: UU PPh s.t.d.t.d. UU HPP; PMK 101/PMK.010/2016; PER-16/PJ/2016; PP 58/2023; PMK 168/2023; PMK 66/2023; PMK 10/2025; PMK 72/2025; PMK 105/2025.

> Catatan: detail penulis, halaman, dan DOI untuk beberapa referensi (terutama no. 11–16) harus dilengkapi pada Tahap 1.
