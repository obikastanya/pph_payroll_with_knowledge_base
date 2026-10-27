# GT2 — Kalkulator PPh 21 resmi DJP

Acuan independen dari otoritas pajak (RENCANA_DATASET.md, D13). Alamat: https://kalkulator.pajak.go.id/ (tab PPh 21).

## Batasan kalkulator (dicatat 2026-10-27)

- Hanya menghitung aturan yang berlaku saat diakses (rezim TER 2026); tidak ada pilihan tahun pajak.
- Formulir PPh 21 Bulanan berisi: Jenis Pemotongan (Bulanan, Final, Tidak Final, Tahunan), Kode Objek Pajak (21-100-01 Pegawai Tetap, 21-100-02 Penerima Pensiun Berkala), Skema (Gross, Gross Up), "Penghasilan yang telah dipotong PPh Pasal 21 pada masa pajak yang sama" (Ada/Tidak Ada), Penghasilan Bruto, PTKP (TK/0–K/3; tidak ada K/I), dan Kode Keamanan.
- Keluaran: DPP, Tarif, PPh 21.
- Tidak menghitung DTP, natura, atau iuran BPJS secara terpisah; yang dibandingkan adalah PPh 21 bulanan dari bruto dan PTKP.
- Setiap perhitungan meminta **kode keamanan (CAPTCHA)**. CAPTCHA diisi oleh peneliti (manusia), tidak oleh Claude.

## Protokol

1. Kasus diambil dari [rencana_kasus.csv](rencana_kasus.csv): 12 kasus dari GT3 tahun 2026 (satu bulan non-Desember per kasus) dan 6 kasus di batas lapisan TER.
2. Claude mengisi formulir persis seperti kolom rencana (jenis, kode objek, skema, PTKP, bruto), lalu menyimpan tangkapan layar formulir.
3. Peneliti mengisi kode keamanan dan menekan **Hitung**.
4. Claude mencatat waktu akses, semua angka keluaran, teks hasil apa adanya, dan tangkapan layar hasil ke [hasil.csv](hasil.csv) dan folder `bukti/`.
5. Perbandingan dengan GT3 dan KB emas dilakukan **sesudah** semua kasus tercatat, agar pencatatan tidak dipengaruhi nilai harapan.
6. Setiap selisih dicatat untuk adjudikasi di `review/adjudication/`.

## Hasil (2026-10-27, 18:54–19:09 WIB)

18 kasus dijalankan dan dicatat di [hasil.csv](hasil.csv); setiap kasus punya dua tangkapan layar di `bukti/` (formulir terisi dan hasil). Perbandingan dengan [bandingkan.py](bandingkan.py) menghasilkan [perbandingan.csv](perbandingan.csv):

| Pembanding | Kasus | Sama |
|---|---|---|
| GT3 (hitungan manual dari teks regulasi) | 10 (GT2-01 s.d. 06, 08 s.d. 10, 12) | 10 |
| Tabel TER `dataset/01_regulasi/tables/ter_bulanan.csv` (batas lapisan b dan b+1) | 6 (GT2-13 s.d. 18) | 6 |
| *Gross-up* dari tabel TER atas bruto yang diisikan | 2 (GT2-07, GT2-11) | 2 |
| **Jumlah** | **18** | **18** |

Yang terkonfirmasi oleh kalkulator resmi:
- pemetaan status PTKP ke kategori TER A, B, C;
- batas lapisan TER: tarif berubah tepat di atas batas (6.600.000 → 6.600.001 kategori C; 5.400.000 → 5.400.001 kategori A; 6.200.000 → 6.200.001 kategori B; 10.050.000 → 10.050.001 kategori A);
- *gross-up* metode TER: DPP = bruto + tunjangan pajak, dan tunjangan pajak = PPh 21.

Yang **tidak** terkonfirmasi: pembulatan ke bawah PPh bulanan (ambiguitas K1 GT3). Semua hasil kalkulator kebetulan memiliki pecahan di bawah setengah rupiah, sehingga pembulatan ke bawah dan ke terdekat memberi hasil sama.

## Catatan

- **Kesalahan perencanaan (diperbaiki dalam analisis, bukan dalam data):** GT2-07 dan GT2-11 diambil dari GT3-045 dan GT3-049 yang memakai metode "ditanggung pemberi kerja". Bruto di GT3 itu sudah termasuk pajak yang di-*gross-up*, tetapi diisikan ke mode Gross Up, sehingga pajaknya di-*gross-up* dua kali. Hasil DJP tetap sah sebagai *gross-up* atas bruto yang diisikan, jadi kedua kasus dibandingkan dengan *gross-up* independen dari tabel TER, bukan dengan GT3. Perbandingan langsung dengan GT3-045/049 memerlukan pengisian ulang dengan skema Gross atas bruto GT3.
- **GT2-11:** isian bruto sempat terbaca 2.019.260.833 (atribut *placeholder*); bruto diketik ulang dan diperiksa lewat tangkapan layar sebelum Hitung. DPP hasil (22.189.679 = 20.192.608 + 1.997.071) konsisten dengan bruto yang benar.
- **GT2-13:** klik Hitung pertama tidak memproses; klik kedua dengan kode yang sama berhasil.
- **Kolom `tarif`** sempat salah dibaca alat pencatat (titik desimal dianggap pemisah ribuan) untuk GT2-01 s.d. 13; dipulihkan dari kolom `teks_hasil` yang menyimpan teks asli kalkulator.
- Kode keamanan (CAPTCHA) diisi peneliti untuk setiap kasus.
