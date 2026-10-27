# Taksonomi perubahan, konflik, dan kesalahan LLM

Draf Tahap 2, 2026-10-27. Taksonomi ini dipakai untuk menyusun korpus, membuat materi sintetis (perubahan tak terlihat, konflik buatan, regulasi fiktif), dan melaporkan hasil per jenis. Taksonomi kesalahan LLM ditetapkan **sebelum** ada keluaran LLM, sesuai *skeleton* Bagian VIII.

## 0. Lingkup

- **Subjek:** pegawai tetap pada pemberi kerja swasta atau BUMN di Indonesia, termasuk yang masuk atau keluar di tengah tahun. Di luar lingkup: pegawai tidak tetap, bukan pegawai, pensiunan, ASN, peserta magang, PPh 26, pegawai di IKN, dan wajib pajak tanpa NIK atau NPWP valid.
- **Tahun pajak:** 2023–2026 untuk data uji; sebelum 2023 untuk data pengembangan.
- **Perhitungan:** PPh 21 bulanan masa Januari–November, perhitungan ulang di masa pajak terakhir, metode *gross*, *gross-up*, dan ditanggung pemberi kerja, penghasilan teratur dan tidak teratur, iuran dan premi BPJS yang masuk bruto atau menjadi pengurang, natura, zakat lewat pemberi kerja, dan fasilitas DTP.
- **Lapisan perusahaan:** komponen penghasilan, prorata, THR, bonus, lembur, perlakuan pajak (siapa menanggung), pembagian iuran, potongan.

## 1. Jenis perubahan

Setiap peristiwa diberi satu **jenis utama** dan nol atau lebih **sifat**.

### 1.1 Jenis utama

| Kode | Jenis | Contoh di korpus | Bentuk Δ yang diharapkan |
|---|---|---|---|
| T1 | Parameter: nilai tunggal berubah (batas upah, PTKP, persentase, plafon) | E01, E05, E08, E12 (batas upah JP); D01, D03 (PTKP) | versi baru tabel atau parameter |
| T2 | Tabel tarif: lapisan atau tarif berubah atau dibentuk | E03 (TER) | tabel berversi baru |
| T3 | Klasifikasi penghasilan: suatu penerimaan menjadi atau berhenti menjadi objek, teratur atau tidak teratur, pengurang atau bukan | E02 (natura) | aturan klasifikasi baru |
| T4 | Fasilitas baru: insentif atau pengecualian dengan kriteria | E06, E11 (DTP); D05, D10 | aturan baru dengan kondisi |
| T5 | Perubahan cakupan: kriteria fasilitas atau aturan diperluas atau dipersempit | E10 (sektor pariwisata); D06 | aturan baru menggantikan kondisi lama |
| T6 | Perubahan masa: perpanjangan atau pengakhiran lebih awal | E09; D07, D11 | rekaman berversi atau aturan pengganti |
| T7 | Pergantian metode perhitungan | E03 + E04 (TER) | sekumpulan aturan baru dan pencabutan aturan lama |
| T8 | Pencabutan tanpa pengganti | D13 (DTP COVID berakhir) | `remove` atau pencabutan |
| T9 | Perubahan prosedur hitung: pembulatan, urutan, dasar pengenaan | (belum ada di korpus nyata) | aturan baru atau registri pembulatan |
| T10 | Perubahan kebijakan perusahaan | K1 di mini demo; dokumen PKB | aturan lapisan perusahaan |

### 1.2 Sifat tambahan

| Kode | Sifat | Contoh |
|---|---|---|
| S1 | Berlaku surut ($t_{berlaku} < t_{terbit}$) | E06, E07, E09, E10; D03, D06, D07, D09, D10 |
| S2 | Bersyarat: berlaku hanya untuk sektor, KLU, kriteria penghasilan, atau tanggal tertentu | E06, E07, E09, E10, E11 |
| S3 | Sementara: punya `berlaku_sampai` | E06, E07, E09–E11 |
| S4 | Terdiri dari beberapa dokumen | E03 + E04 |
| S5 | Mengubah dokumen lain ("perubahan atas ...") | E10, E09 |
| S6 | Bergantung tabel lampiran | E03 |

### 1.3 Pengecoh

| Kode | Jenis pengecoh | Contoh |
|---|---|---|
| X1 | Administrasi atau pelaporan | P02, P05, P07, P19, P21 |
| X2 | Subjek di luar lingkup (ASN, magang, IKN, bukan penerima upah) | P03, P08, P14, P18 |
| X3 | Mengubah iuran atau upah tanpa mengubah PPh 21 | P01, P06, P10 |
| X4 | Menyatakan ulang ketentuan tanpa perubahan nilai | P04, D08, D12 |
| X5 | Mengganti dasar hukum tanpa mengubah rumus | P15, P20 |

## 2. Jenis konflik kebijakan perusahaan dengan aturan wajib

Konflik terjadi bila kebijakan perusahaan menetapkan fakta yang juga ditetapkan aturan wajib, dengan nilai atau syarat berbeda. **Pilihan yang memang diserahkan ke perusahaan bukan konflik**, misalnya metode *gross*, *gross-up*, atau ditanggung perusahaan; besaran tunjangan; rumus prorata THR yang tidak di bawah minimum.

| Kode | Jenis konflik | Contoh | Sumber |
|---|---|---|---|
| C1 | Klasifikasi penghasilan menyimpang (teratur/tidak teratur, objek/bukan objek) | lembur diperlakukan sebagai tidak teratur | Perusahaan X (prototipe); K1 mini demo |
| C2 | Komponen bruto dihilangkan | premi JKK/JKM yang dibayar pemberi kerja tidak dimasukkan bruto | sintetis |
| C3 | Pengurang tidak sah atau melebihi plafon | biaya jabatan tanpa plafon; iuran yang bukan pengurang dikurangkan | sintetis |
| C4 | Fasilitas pemerintah tidak diteruskan ke pegawai | insentif pajak pemerintah tidak diberikan kepada pegawai | **PKB WIKA 2025–2026 Ps. 22 ayat (3)** vs PMK 10/2025 Ps. 5 ayat (1); laten karena WIKA bukan sektor padat karya |
| C5 | Tarif atau metode menyimpang | memakai metode disetahunkan setelah 2024 | sintetis |
| C6 | Parameter usang | PTKP K/I keliru; batas upah JP tahun lalu | Perusahaan X (prototipe) |
| C7 | Pembagian iuran BPJS menyimpang | porsi pegawai melebihi ketentuan | sintetis |
| C8 | Batas upah atau plafon iuran diabaikan | iuran JP dihitung dari seluruh upah | sintetis |
| C9 | Pembulatan menyimpang | PKP tidak dibulatkan ke ribuan | sintetis |
| C10 | Hak minimum dilanggar | THR di bawah ketentuan untuk masa kerja ≥ 12 bulan | sintetis; ketenagakerjaan, di luar PPh 21 tetapi tercatat |

**Status konflik:**
- **aktif:** kebijakan menghasilkan nilai yang dilarang pada kasus yang ada;
- **laten:** konflik hanya muncul bila syarat terpenuhi, misalnya sektor DTP;
- **terpicu perubahan:** kebijakan tadinya sah, tetapi menjadi berkonflik setelah regulasi berubah. Inilah yang diukur RQ4.

## 3. Jenis kesalahan LLM

Dipakai untuk melabeli kandidat Δ yang salah. Satu kandidat bisa punya beberapa label.

| Kode | Kesalahan | Gerbang yang diharapkan menangkap |
|---|---|---|
| L1 | Nilai salah (angka, persentase, batas) | G4/G5 bila berdampak; G2 bila kutipan tidak memuat nilai |
| L2 | Masa berlaku salah (`valid_from`, `valid_until`) | G2 dengan *date grounding* |
| L3 | Tanggal pengetahuan salah (`recorded_on` dimundurkan) | G4 (ω sebelum terbit) |
| L4 | Kondisi atau cakupan salah (sektor, kriteria, subjek) | G5 sebagian; sering lolos |
| L5 | Pengecualian terlewat | sering lolos |
| L6 | Pencabutan terlewat (aturan lama tetap menyala) | G5, perilaku pada $S^G$ |
| L7 | Lapisan atau sifat salah (wajib/*default*/opsional, regulasi/perusahaan) | G3 |
| L8 | Kutipan karangan atau tidak mendukung unsur | G2 |
| L9 | Perubahan pada pengecoh (pembaruan tidak kosong untuk dokumen tidak relevan) | penilaian relevansi berkutipan |
| L10 | Nilai hafalan (nilai asli dipakai pada dokumen kontrafaktual) | G2 |
| L11 | Unsur tanpa efek (vakum) | G5 |
| L12 | Ekspresi tidak sah atau fakta tidak dikenal | G1, G3 |

## 4. Pemetaan korpus

Pemetaan per peristiwa ada di kolom `jenis_perubahan` di [peristiwa.csv](../../dataset/09_korpus_peristiwa/peristiwa.csv). Jenis yang belum punya contoh nyata di rentang uji, yaitu T8 dan T9, ditutup oleh perubahan tak terlihat (RQ1) dan data pengembangan.
