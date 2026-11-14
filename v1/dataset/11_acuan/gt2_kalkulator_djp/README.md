# GT2 — Kalkulator PPh 21 resmi DJP

Acuan independen dari otoritas pajak (RENCANA_DATASET.md, D13). Alamat: https://kalkulator.pajak.go.id/ (tab PPh 21).

## Batasan kalkulator (dicatat 2026-10-27)

- Hanya menghitung aturan yang berlaku saat diakses (rezim TER 2026); tidak ada pilihan tahun pajak.
- Formulir PPh 21 Bulanan berisi: Jenis Pemotongan (Bulanan, Final, Tidak Final, Tahunan), Kode Objek Pajak (21-100-01 Pegawai Tetap, 21-100-02 Penerima Pensiun Berkala), Skema (Gross, Gross Up), "Penghasilan yang telah dipotong PPh Pasal 21 pada masa pajak yang sama" (Ada/Tidak Ada), Penghasilan Bruto, PTKP (TK/0–K/3; tidak ada K/I), dan Kode Keamanan.
- Keluaran: DPP, Tarif, PPh 21.
- Tidak menghitung DTP, natura, atau iuran BPJS secara terpisah; yang dibandingkan adalah PPh 21 bulanan dari bruto dan PTKP.
- Setiap perhitungan bulanan meminta **kode keamanan (CAPTCHA)**. CAPTCHA diisi oleh peneliti (manusia), tidak oleh Claude.
- Formulir **PPh 21 Tahunan (A1/A2)** berbentuk bukti potong A1: isian baris 1–7 (bruto per jenis), 9 (biaya jabatan), 10 (iuran pensiun/JHT), 11 (zakat), 14 (neto masa sebelumnya), 19 (PPh yang telah dipotong), PTKP, Setahun/Disetahunkan, dan masa awal–akhir. Baris 8, 12, 13, 15–18, dan 20 dihitung langsung tanpa CAPTCHA.
- **Biaya jabatan tidak dihitung kalkulator.** Baris 9 adalah isian dan tidak dibatasi plafon: biaya jabatan 4.193.600 untuk masa September–Desember (di atas plafon 4 × 500.000) diterima tanpa peringatan dan langsung menurunkan PKP (`bukti/GT2-24_uji_plafon_biaya_jabatan.jpg`). Plafon biaya jabatan (tafsir K6) tidak dapat diuji dengan GT2.

## Protokol

1. Kasus bulanan diambil dari [rencana_kasus.csv](rencana_kasus.csv): 12 kasus dari GT3 tahun 2026 (satu bulan non-Desember per kasus), 6 kasus di batas lapisan TER, dan 2 kasus ulang (GT2-19, GT2-20). Kasus tahunan diambil dari [rencana_tahunan.csv](rencana_tahunan.csv): 15 kasus GT3 berstrata tahunan 2024–2026, masa pajak terakhir.
2. Claude mengisi formulir persis seperti kolom rencana (jenis, kode objek, skema, PTKP, bruto), lalu menyimpan tangkapan layar formulir.
3. Peneliti mengisi kode keamanan dan menekan **Hitung**.
4. Claude mencatat waktu akses, semua angka keluaran, teks hasil apa adanya, dan tangkapan layar hasil ke [hasil.csv](hasil.csv) dan folder `bukti/`.
5. Perbandingan dengan GT3 dan KB emas dilakukan **sesudah** semua kasus tercatat, agar pencatatan tidak dipengaruhi nilai harapan.
6. Setiap selisih dicatat untuk adjudikasi di `review/adjudication/`.

## Hasil bulanan (2026-10-27, 18:54–19:09 WIB; GT2-19 dan GT2-20 20:42 WIB)

20 kasus dijalankan dan dicatat di [hasil.csv](hasil.csv); setiap kasus punya dua tangkapan layar di `bukti/` (formulir terisi dan hasil). Perbandingan dengan [bandingkan.py](bandingkan.py) menghasilkan [perbandingan.csv](perbandingan.csv). Acuan memakai aturan pembulatan yang ditetapkan di [tafsir_perhitungan.md](../../../docs/spesifikasi/tafsir_perhitungan.md) (K1).

| Pembanding | Kasus | Sama | Beda |
|---|---|---|---|
| GT3 (hitungan dari teks regulasi) | 12 (GT2-01 s.d. 06, 08 s.d. 10, 12, 19, 20) | 8 | 4 (GT2-06, 09, 10, 20: Rp1) |
| Tabel TER (batas lapisan b dan b+1) | 6 (GT2-13 s.d. 18) | 6 | 0 |
| *Gross-up* dari tabel TER atas bruto yang diisikan | 2 (GT2-07, 11) | 1 | 1 (GT2-07: Rp1) |
| **Jumlah** | **20** | **15** | **5** |

Terkonfirmasi oleh kalkulator resmi di semua 20 kasus:
- pemetaan status PTKP ke kategori TER A, B, C;
- tarif lapisan TER, termasuk tepat di batas lapisan (6.600.000/6.600.001 kategori C; 5.400.000/5.400.001 dan 10.050.000/10.050.001 kategori A; 6.200.000/6.200.001 kategori B);
- mekanisme *gross-up* TER: DPP = bruto + tunjangan pajak, dan tunjangan pajak = PPh 21.

**Pembulatan berbeda.** Kalkulator DJP membuang pecahan rupiah, termasuk pecahan tepat 0,5: GT2-09 9.950.775 × 2% = 199.015,5 ditampilkan 199.015; GT2-10 9.411.300 × 1,5% = 141.169,5 ditampilkan 141.169; GT2-20 20.192.609 × 8% = 1.615.408,72 ditampilkan 1.615.408. PER-11/PJ/2025 Pasal 129 ayat (1) huruf a dan ayat (3) (PDF hlm. 106) mewajibkan PPh pada bukti pemotongan PPh 21 dibulatkan ke rupiah penuh: kurang dari 0,50 ke bawah, 0,50 atau lebih ke atas. Acuan mengikuti peraturan, sehingga kelima selisih Rp1 diberi putusan "pembulatan" di `perbandingan.csv`. Untuk pembulatan, kalkulator DJP bukan acuan.

## Hasil tahunan (2026-10-27, 20:16–20:33 WIB)

15 kasus dicatat di [hasil_tahunan.csv](hasil_tahunan.csv) dengan [catat_tahunan.py](catat_tahunan.py); setiap kasus punya dua tangkapan layar (`bukti/GT2-xx_atas.jpg` identitas dan bruto, `bukti/GT2-xx_bawah.jpg` pengurang sampai PPh terutang). Pencatat menolak kasus yang isiannya tidak sama dengan rencana. Perbandingan dengan [bandingkan_tahunan.py](bandingkan_tahunan.py) menghasilkan [perbandingan_tahunan.csv](perbandingan_tahunan.csv).

| Fakta yang dihitung kalkulator | Sama dengan GT3 |
|---|---|
| bruto setahun, neto, PTKP, PKP, PPh Pasal 17 setahun, PPh masa terakhir | **90/90** (15 kasus × 6) |

Terkonfirmasi: pembulatan PKP ke bawah ke ribuan; lapisan Pasal 17 UU HPP termasuk PKP tepat di atas batas Rp500 juta (GT2-31, 500.001.000 → 94.000.300); lebih bayar di masa terakhir (nilai negatif, 7 kasus); masa kerja tidak penuh setahun (GT2-23 Januari–Juni, GT2-24 September–Desember, GT2-29 Mei–Desember, GT2-33 Januari–September) dihitung tanpa disetahunkan; zakat sebagai pengurang; tunjangan PPh (*gross-up* dan ditanggung) di baris 2; natura objek di baris 6. Yang tidak teruji GT2 tahunan: biaya jabatan (isian, lihat Batasan), pemilahan natura dan DTP (nilai disalin dari GT3).

## Catatan

- **Kesalahan perencanaan (diperbaiki dalam analisis, bukan dalam data):** GT2-07 dan GT2-11 diambil dari GT3-045 dan GT3-049 yang memakai metode "ditanggung pemberi kerja". Bruto di GT3 itu sudah termasuk pajak yang di-*gross-up*, tetapi diisikan ke mode Gross Up, sehingga pajaknya di-*gross-up* dua kali. Hasil DJP tetap sah sebagai *gross-up* atas bruto yang diisikan, jadi kedua kasus dibandingkan dengan *gross-up* independen dari tabel TER, bukan dengan GT3. Pengisian ulang dengan skema Gross atas bruto GT3 dilakukan sebagai GT2-19 (GT3-045 bulan 6: sama) dan GT2-20 (GT3-049 bulan 1: selisih Rp1 pembulatan).
- **GT2-11:** isian bruto sempat terbaca 2.019.260.833 (atribut *placeholder*); bruto diketik ulang dan diperiksa lewat tangkapan layar sebelum Hitung. DPP hasil (22.189.679 = 20.192.608 + 1.997.071) konsisten dengan bruto yang benar.
- **GT2-13, GT2-19, GT2-20:** klik Hitung pertama tidak memproses; klik kedua dengan kode yang sama berhasil.
- **GT2-22:** pengisian pertama tidak dicatat karena nilai baru tersambung ke nilai kasus sebelumnya (kolom berformat tidak terkosongkan); sejak itu setiap kolom dikosongkan dengan Ctrl+A, Delete sebelum diketik, dan pencatat memeriksa isian terhadap rencana.
- **Kolom `tarif`** sempat salah dibaca alat pencatat (titik desimal dianggap pemisah ribuan) untuk GT2-01 s.d. 13; dipulihkan dari kolom `teks_hasil` yang menyimpan teks asli kalkulator.
- Kode keamanan (CAPTCHA) diisi peneliti untuk setiap kasus bulanan. Formulir tahunan tidak meminta CAPTCHA.
