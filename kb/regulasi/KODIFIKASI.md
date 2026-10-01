# Kodifikasi Regulasi PPh 21 Pegawai Tetap (WP1b)

Dokumen ini adalah **spesifikasi bersama** untuk baseline B1 (`baselines/b1_hardcoded/`) dan KB (`kb/regulasi/*.yaml`). Setiap aturan dikodifikasi dari teks pasal, lalu dicek terhadap contoh resmi (`dataset/07_kasus_uji_resmi/`).

**Sifat aturan:**
- **W** (wajib): tidak boleh ditimpa perusahaan.
- **D** (default): boleh ditimpa perusahaan.
- **T** (tafsir): tidak diatur tegas; memiliki varian dan rentang tafsir (research_plan §6.9.6).

**Sumbu waktu:** `MP` = masa pajak (saat terutang); `PI` = periode iuran.

Semua uang dalam rupiah `int`. Nilai antara bersifat eksak, dan pembulatan dilakukan hanya di titik registri (`kb/regulasi/pembulatan.yaml`).

---

## A. Lintas rezim

| ID | Sifat | Berlaku | Kondisi → Akibat | Sumber | Bukti V1 |
|---|---|---|---|---|---|
| REG-PTKP-01 | W | 2016-01-01 – | PTKP = 54 jt (diri) + 4,5 jt bila kawin + 4,5 jt × tanggungan (maks 3) | PMK 101/2016 Ps. 1 | semua kasus |
| REG-PTKP-02 | W | 2016 – | Status PTKP = keadaan awal tahun kalender; pegawai baru datang dan menetap di Indonesia: awal bulan bagian tahun | PMK 168 Ps. 9(4)-(5); PER-16 Ps. 11(5)-(6) | — |
| REG-PTKP-03 | W | 2016 – | Karyawati kawin: PTKP diri saja; jika ada keterangan kecamatan bahwa suami tidak berpenghasilan: diri + kawin + tanggungan. Karyawati tidak kawin: diri + tanggungan | PMK 168 Ps. 9(2)-(3); PER-16 Ps. 11(3)-(4) | PER16-I.1.3, I.1.4 |
| REG-P17-01 | W | versi tabel (`tarif_pasal17.csv`): pra-HPP 2009–2021; HPP 2022– | PPh setahun = tarif progresif × PKP (lapisan (a, b]) | UU 36/2008 Ps. 17; UU HPP | 25/25 (tests/test_interval.py) |
| REG-PKP-01 | W | 2016 – | PKP = neto − PTKP, min 0; dibulatkan ke bawah ribuan (BULAT-PKP-01) | PMK 168 Ps. 8(4); PER-16 Ps. 14(8) | 3 kasus |
| REG-BJ-01 | W | 2016 – | Biaya jabatan = 5% × bruto; plafon Rp500.000 × bulan / Rp6.000.000 setahun | PMK 168 Ps. 10(2); PER-16 Ps. 10(3)a | semua |
| REG-BJ-02 | **T** | 2016 – | Plafon untuk masa kerja n < 12 bulan: **(a, default)** 5% × bruto n bulan, plafon n × 500.000; **(b)** plafon per bulan, Σ min(5% × bruto_m, 500.000) | PMK 168 Ps. 10(2). (a): PMK168-B-I.2.x, PMK105-B-3, PER16-II.1.1, I.6.2.2. (b): PMK10-B-3 | 6 vs 1 |
| REG-PENG-01 | W | 2016 – | Iuran pensiun/JHT/JP yang **dibayar pegawai** = pengurang neto | PMK 168 Ps. 10(1)b; PER-16 Ps. 10(3)b | — |
| REG-PENG-02 | W | 2024 – | Zakat/sumbangan keagamaan wajib melalui pemberi kerja = pengurang neto | PMK 168 Ps. 10(1)c | PMK168-B-I.1, B-I.2.1.2 |
| REG-PENG-02-P16 | W | 2016–2023 | Zakat **bukan** pengurang dalam pemotongan (dikurangkan sendiri di SPT) | PER-16 Ps. 10(3) | — |
| REG-OBJ-01 | W | 2016 – | Bruto mencakup gaji, tunjangan, lembur, bonus, THR, premi JKK/JKM/JKN dan asuransi yang dibayar pemberi kerja | PMK 168 Ps. 5(3); PER-16 Ps. 1 angka 15–16 | semua |
| REG-OBJ-02 | W | 2016 – | Iuran pensiun/JHT/JP yang dibayar **pemberi kerja** bukan objek | PMK 168 Ps. 7c | PMK168-B-I.1 |
| REG-OBJ-03 | W | 2016–2023 | Lembur = penghasilan **teratur** | PER-16 Ps. 1 angka 15 | PER16-I.1.3, I.1.4 |
| REG-NAT-01 | W | 2016-01-01 – 2023-06-30 | Natura objek PPh 21 hanya bila pemberi kerja bukan WP/deemed profit/final (dan kenikmatan tertentu) | PER-16 (contoh I.10) | PER16-I.10 |
| REG-NAT-02 | W | 2023-07-01 – | Natura/kenikmatan objek PPh 21 kecuali jenis yang dikecualikan PMK 66/2023 | PMK 66/2023 Ps. 27 (berlaku 1-7-2023); PMK 168 Ps. 5(2), 7b | PMK168-B-I.6 |
| REG-DITANGGUNG-01 | W | 2016–2023-06-30 | PPh ditanggung pemberi kerja **bukan** penghasilan pegawai; pajak dihitung atas bruto tanpa gross-up | PER-16 (contoh I.8) | PER16-I.8 |
| REG-DITANGGUNG-02 | W | 2024 – | PPh ditanggung pemberi kerja = kenikmatan (objek) → dihitung *full gross-up* | PMK 168 Lampiran B I.4 | PMK168-B-I.4 |
| REG-DITANGGUNG-T | **T** | 2023-07-01 – 2023-12-31 | Peralihan: PMK 66 berlaku, prosedur masih PER-16 → varian (a) bukan objek; (b) gross-up | — | — |
| REG-TUNJPAJAK-01 | W | 2016 – | Tunjangan pajak berjumlah tetap = penghasilan biasa (masuk bruto) | PER-16 I.9; PMK 168 B I.5 | PER16-I.9, PMK168-B-I.5 |
| REG-VALAS-01 | W | 2016 – | Penghasilan valas dikonversi dengan kurs Menteri Keuangan yang berlaku saat bayar/terutang (mana lebih dahulu) | PMK 168 Ps. 5(4) | PER16-I.7, PMK168-B-I.3 |
| REG-WAKTU-01 | W | 2024 – | Masa pajak = bulan saat terutang = min(tanggal bayar, tanggal terutang) | PMK 168 Ps. 19(1) | — |
| REG-WAKTU-01-P16 | W/T | 2016–2023 | Saat terutang = saat pembayaran atau terutangnya; frasa "mana yang lebih dahulu" tidak eksplisit (WAKTU-P16-01) | PER-16 Ps. 21(1),(3) | — |
| REG-NPWP-01 | W | 2016–2023 | Tanpa NPWP: PPh × 120% | UU PPh Ps. 21(5a); PER-16 Ps. 20 | PER16-I.1.1 |
| REG-NPWP-02 | W | 2024 – | Tidak diterapkan (PMK 168 tidak mengatur; NIK sebagai NPWP) → di luar lingkup | `pembulatan_dan_lainnya.csv` | — |

## B. Masa pajak terakhir dan bagian tahun pajak (kedua rezim)

| ID | Sifat | Kondisi → Akibat | Sumber | Bukti V1 |
|---|---|---|---|---|
| REG-MT-01 | W | Masa pajak terakhir = Desember; atau bulan **terakhir bekerja** bila berhenti bekerja/pensiun sebelum Desember | PMK 168 Lamp. B I.2; PER-16 Ps. 14 | PMK168-B-I.2.2.1 (Agustus), C-I.1.4a (Mei) |
| REG-MT-02 | W | PPh masa terakhir = PPh setahun (atau bagian tahun) − Σ PPh masa sebelumnya; boleh negatif (lebih potong dikembalikan, kecuali bagian DTP) | PMK 168 Ps. 15(1)b, Lamp. B I.2 angka 7–8 | 9 kasus lebih potong |
| REG-MT-03 | W | Pegawai yang **kewajiban subjektifnya sudah ada sejak awal tahun** tetapi mulai/berhenti bekerja di tengah tahun: dihitung atas penghasilan selama bekerja, **tidak disetahunkan** | PMK 168 Lamp. B I.2 angka 6a | PMK168-B-I.2.1.1, I.2.2.1, I.2.2.2a |
| REG-MT-04 | W | Kewajiban subjektif baru dimulai setelah Januari / berakhir sebelum Desember (mis. WNA datang/pergi): neto **disetahunkan × 12/n**, PPh **× n/12** (BULAT-PROPORSI-01) | PMK 168 Ps. 15(3), Lamp. B I.2 angka 6c; PER-16 | PMK168-B-I.2.1.2, I.2.2.3; PER16-I.6.1.2, I.6.2.2 |

## C. Rezim TER (berlaku 2024-01-01 –)

| ID | Sifat | Kondisi → Akibat | Sumber | Bukti V1 |
|---|---|---|---|---|
| R24-01 | W | Kategori TER dari status PTKP: A = {TK/0, TK/1, K/0}; B = {TK/2, TK/3, K/1, K/2}; C = {K/3} | PP 58/2023 Ps. 2(4) | 170 entri |
| R24-02 | W | Masa selain terakhir: PPh = TER(kategori, bruto masa) × bruto masa (BULAT-TER-01); bruto pecahan dibulatkan dulu (BULAT-BRUTO-01) | PMK 168 Ps. 15(1)a | 169/170 (+1 erratum) |
| R24-03 | W | Bruto masa = seluruh penghasilan masa (teratur + tidak teratur + premi objek + natura objek + tunjangan pajak). Iuran pegawai & zakat **tidak** dikurangkan | PMK 168 Ps. 8(2)a; Lamp. B I.1 | PMK168-B-I.5 |
| R24-04 | W | Masa terakhir: neto setahun = bruto setahun − biaya jabatan − iuran pegawai − zakat | PMK 168 Lamp. B I.2 angka 5a | 16 kasus |
| R24-05 | W | Gross-up (metode `gross_up` atau REG-DITANGGUNG-02): T = PPh_int(B + T), titik tetap terkecil; peringatan bila solusi ganda | PMK 168 Lamp. B I.4 | PMK168-B-I.4 |
| R24-DTP-01 | W | 2025: DTP bila KLU termasuk 4 sektor padat karya (masa Jan–Des) atau pariwisata (masa Okt–Des, PMK 72/2025); 2026: 5 sektor (PMK 105/2025). Syarat pegawai tetap: penghasilan **tetap & teratur menurut kontrak** pada Januari (atau bulan pertama bekerja) ≤ Rp10.000.000; NPWP/NIK terintegrasi; tidak menerima DTP lain | PMK 10/2025 Ps. 4(2); PMK 72/2025; PMK 105/2025 Ps. 4(2) | 10 kasus (+PMK10-B-4 tidak berhak) |
| R24-DTP-02 | W | PPh DTP masa = PPh terutang masa (seluruhnya, termasuk atas bonus) di masa fasilitas; DTP dibayar tunai dan bukan penghasilan | PMK 10/2025 Ps. 5 | idem |
| R24-DTP-03 | W | Lebih potong masa terakhir: tidak dikembalikan sepanjang berasal dari DTP. Pariwisata 2025 (PMK 72): yang dikembalikan = max(0, lebih potong − DTP masa Okt–Nov) | PMK 10/2025 Ps. 5(5); PMK 72/2025 Ps. 5(5a); PMK 168 Lamp. B I.2 angka 8 | PMK10-B-3, PMK105-B-3, PMK72-B-7, B-8 |

## D. Rezim disetahunkan (PER-16/PJ/2016; dipakai tahun pajak 2016–2023)

> Catatan berlaku: PER-16/PJ/2016 mulai berlaku 29-09-2016 (Ps. 29). Contohnya memakai Januari–Agustus 2016 dengan metode yang sama dengan pendahulunya. KB memakai rezim ini untuk 2016-01-01 s.d. 2023-12-31 dan tabel Pasal 17 sesuai versinya (asumsi A-01).

| ID | Sifat | Kondisi → Akibat | Sumber | Bukti V1 |
|---|---|---|---|---|
| R16-01 | W | Bruto teratur sebulan = penghasilan teratur + premi objek (+ natura objek, tunjangan pajak tetap) | PER-16 Ps. 1 angka 15; contoh I.1.x | 10 kasus |
| R16-02 | W | Neto sebulan = bruto teratur − biaya jabatan bulanan (5%, maks 500.000) − iuran pegawai | PER-16 Ps. 10(3) | idem |
| R16-03 | W | Neto disetahunkan = neto sebulan × N; N = 12; atau **N = jumlah bulan bekerja tersisa** bagi pegawai masuk tengah tahun (subjektif sudah ada); atau bulan bekerja yang sudah pasti (pensiun yang sudah diketahui sejak awal tahun) | PER-16 Ps. 14; contoh I.6.1.1 (N=4), II.1.1 (N=6) | 3 kasus |
| R16-04 | W | PPh masa (teratur) = PPh(PKP) ÷ N (BULAT-P16-01) | contoh I.1.x | 12 kasus |
| R16-05 | W | Penghasilan tidak teratur: PPh = PPh(bruto teratur × 12 + tidak teratur − pengurang setahun − PTKP) − PPh(bruto teratur × 12 − pengurang setahun − PTKP); biaya jabatan dihitung atas bruto setahun masing-masing dengan plafon 6 jt | PER-16 Ps. 14(3)–(4); contoh I.4.1, I.4.2, I.6.2.2 | 3 kasus |
| R16-06 | W | Gaji mingguan/harian pegawai tetap: bruto sebulan = 4 × mingguan / hari kerja × harian; PPh periode = PPh sebulan ÷ 4 / ÷ hari kerja (BULAT-P16-01) | contoh I.2.1–I.2.3 | 3 kasus |
| R16-07 | W | Rapel kenaikan gaji berlaku surut: PPh rapel = Σ (PPh bulanan dengan gaji baru − PPh yang telah dipotong) untuk masa yang dirapel | contoh I.3 | 1 kasus |
| R16-08 | W | Masa terakhir: perhitungan setahun aktual (tidak disetahunkan, kecuali REG-MT-04) dengan biaya jabatan maks n × 500.000 | contoh I.12.1, I.6.2.1, II.1.1 | 3 kasus |

## E. Di luar model engine v1 (dilaporkan, tidak diklaim)

- PER16-I.5 (pindah tugas antarcabang dengan pemotong berbeda dalam satu tahun): butuh model multi-pemotong.
- PMK168-B-I.2.2.2b, C-I.1.3b (penghasilan dari pemberi kerja sebelumnya/lain digabung): di luar lingkup §4.3.
- Pegawai tidak tetap, bukan pegawai, pensiunan: di luar lingkup.

## F. Daftar asumsi interpretasi

| ID | Asumsi | Alasan |
|---|---|---|
| A-01 | Metode disetahunkan PER-16 dipakai untuk tahun pajak 2016–2023 | Contoh resmi PER-16 bertahun 2016; metode identik dengan pendahulunya |
| A-02 | REG-BJ-02 varian (a) sebagai default | 6 contoh resmi (PMK 168, PMK 105, PER-16) vs 1 (PMK 10) |
| A-03 | BULAT-TER-01, BULAT-BRUTO-01, BULAT-BJ-01, BULAT-PROPORSI-01 = `bawah`; BULAT-P16-01 = `setengah_menjauhi_nol` (default sementara) | Konsisten dengan seluruh contoh resmi kecuali PER16-I.1.4 (bukti tafsir); kalibrasi E10 |
| A-04 | Masa pajak terakhir bagi pegawai yang berhenti = bulan terakhir ada penghasilan | Contoh PMK168-B-I.2.2.1 (berhenti 1 September → Agustus) dan C-I.1.4a |
