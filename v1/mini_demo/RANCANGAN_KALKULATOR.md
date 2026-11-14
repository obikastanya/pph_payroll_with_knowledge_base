# Rancangan kalkulator PPh 21 (v4)

Disusun dari draf → evaluasi agen independen (sudut pandang admin payroll dan pemeriksa KB adaptif) → perbaikan.
Belum diterapkan.

## 1. Masalah yang diselesaikan

Admin ingin mencoba angka satu pegawai dengan bebas: mengetik gaji, menambah komponen gaji perusahaannya, mengubah
bulan-bulan sebelumnya, lalu melihat pajaknya sampai bulan itu. Sementara itu, data yang dibutuhkan aturan pajak
**berubah dari waktu ke waktu**:
- peraturan baru menambah data, misalnya natura sejak Juli 2023 atau penghasilan menurut kontrak untuk syarat DTP
  2025;
- kebijakan perusahaan menambah data HR (PKB AVCO membaca 37 data);
- sebagian data berhenti dipakai.

Kalkulator harus memenuhi kebutuhan admin **tanpa** menyimpan daftar data atau aturan pajak di program.

## 2. Keputusan utama

1. **Satu tabel isian sebagai satu-satunya sumber angka.**
   - Baris = bulan, dari bulan mulai sampai "hitung sampai bulan". Kolom = komponen gaji perusahaan + data lain yang
     dibutuhkan aturan.
   - Tidak ada daftar "gaji tetap" atau "kejadian" yang terpisah. Alat bantu ("isi sampai Desember", "isi mulai bulan
     ini") hanya menulis angka biasa ke sel.
   - Kenaikan gaji 10 April = ketik nilai April (yang sudah diprorata menurut perhitungan admin), lalu isi Mei sampai
     Desember dengan gaji baru.
2. **Angka dicatat di bulan dibayarnya.**
   - Judul kolom menyebut "dibayar bulan ini". Tidak ada kolom tanggal bayar.
   - Aturan "masa pajak = bulan bayar atau terutang" adalah aturan pajak, jadi milik KB, bukan pilihan di layar.
3. **Definisi data adalah bagian KB.**
   - Setiap data yang dibaca aturan punya definisi: label, penjelasan, tipe, pilihan, satuan, batas, nilai bawaan,
     kelompok, urutan tampil, berlaku sejak/sampai, dan "menggantikan".
   - Definisi ikut dalam pembaruan yang pertama kali membaca data itu, ikut versi, dan bisa dicabut.
   - **Tidak ada daftar definisi di kode aplikasi.**
   - Bila sebuah data dibaca aturan tetapi belum punya definisi, kolomnya tetap muncul dengan nama teknis dan tanda
     "definisi belum ada". Tipenya ditebak dari cara aturan memakainya: dibandingkan dengan teks → pilihan berisi teks
     itu; dibandingkan dengan 1 → ya/tidak; dipakai berhitung → angka. Cek KB ikut melaporkannya.
4. **Tidak ada logika pajak atau kebijakan di aplikasi.**
   - Prorata, masa kerja, dan "THR dibayar bulan ini" bukan dihitung aplikasi.
   - Admin mengetik angka sebenarnya. Kalau kebijakan perusahaan yang menghitung (misalnya THR = 1,5 × upah × masa
     kerja/12), selnya diisi hasil engine dan tidak bisa diketik; admin mengubah data HR yang dibacanya.
   - Turunan otomatis dari tanggal (masa kerja dari tanggal masuk) baru bisa setelah engine menerima tanggal dan KB
     punya aturan turunan. Ini perubahan penelitian, dicatat di bagian 8. Sampai saat itu, masa kerja diisi sebagai
     angka dengan alat bantu "naik 1 tiap bulan".
5. **Komponen perusahaan dipetakan ke jenis data KB oleh admin**, sekali, di katalog komponen. Katalog milik
   perusahaan, bukan KB.
   - Pilihan jenisnya diambil dari definisi data yang berlaku: label sifat, misalnya "Upah lembur", "Tunjangan tetap
     bulanan", "Mobil dinas", "Insentif atau kompensasi sekali-sekali".
   - Jujur: sebagian jenis di KB memang berupa golongan pajak ("penghasilan tidak teratur lain"). Penjelasannya harus
     memberi contoh dalam kata sehari-hari.
6. **Skenario mengisi form yang sedang dibuka** (sesuai user_design.txt).
   - Bila ada perubahan yang belum disimpan, muncul pertanyaan dulu.
   - Skenario disimpan dalam nama komponen perusahaan, bukan kunci KB, sehingga tetap berlaku saat KB berubah.
7. **Tidak menghitung gaji bersih.** Gaji bersih memerlukan potongan payroll (pinjaman, iuran pegawai), bukan aturan
   pajak. Fokusnya PPh 21 dan DTP.
8. **Kata sehari-hari.**
   - "Masa pajak terakhir" ditulis "bulan penutup (Desember atau bulan keluar)".
   - "Tanggal pengetahuan" ditulis "Aturan per tanggal".
   - Semua istilah sulit diberi catatan saat kursor diarahkan; untuk kolom isian, catatannya dari definisi data di KB.

## 3. Layar

```
┌ Bilah atas ───────────────────────────────────────────────────────────────────────┐
│ Pegawai: [Rina ▾] [Simpan ●] [Simpan sebagai…]   Skenario: [pilih ▾]               │
│ Tahun [2025 ▾]  Hitung sampai [Mei ▾]   Aturan per [hari ini ▾] ⓘ                   │
│ ⚑ 2 data baru dibutuhkan sejak 1 Jan 2025 karena kebijakan SP14  [lihat]           │
│ ⚑ Hasil Januari 2026 berubah sejak terakhir disimpan karena PMK 105/2025 [bandingkan]│
└───────────────────────────────────────────────────────────────────────────────────┘
┌ Pegawai (bisa dilipat) ───────────────────────────────────────────────────────────┐
│ Nama · Status PTKP per 1 Jan ⓘ · Jenis kelamin (+ keterangan suami) · Cara bayar   │
│ pajak · Mulai bekerja · Keluar (kosong = masih bekerja) · NIK/NPWP terdaftar       │
│ ▸ Data lain yang dibutuhkan aturan tahun ini (dari KB): pemegang saham, …          │
│ Perusahaan: Bidang usaha (KLU) · Risiko pekerjaan · Kebijakan perusahaan [▾]       │
└───────────────────────────────────────────────────────────────────────────────────┘
┌ Rincian per bulan (lebar penuh) ──────────────────── [+ Komponen] [+ Data lain ▾] ┐
│ Bulan │ Gaji pokok ✎ │ Tunj. jabatan ✎ │ Lembur ✎ │ THR ⚙ SP14 │ Masa kerja ✎ │ PPh sudah dipotong ✎ │
│ Jan   │ 10.000.000   │ 1.500.000       │ 0        │ (dihitung) │ 7            │ (sama dgn sistem)    │
│ …                                                                                  │
│ Tiap sel: ketik langsung; menu sel: "isi sampai Desember", "isi mulai bulan ini", │
│ "naik 1 tiap bulan" (untuk bilangan). Sel arsir = tidak dibutuhkan aturan bulan    │
│ itu (nilai lama tetap tampil, tidak dihitung, diberi peringatan).                  │
└───────────────────────────────────────────────────────────────────────────────────┘
┌ Hasil ────────────────────────────────────────────────────────────────────────────┐
│ PPh Mei · Total s.d. Mei · DTP s.d. Mei                                            │
│ Kartu Mei: bruto (rincian per komponen perusahaan) × tarif TER kategori B = PPh;   │
│   cara lama untuk 2023; DTP; satu kalimat penjelasan; ▸ Kenapa? (aturan + pasal +   │
│   data yang dibaca + komponen asalnya)                                              │
│ Kartu bulan penutup (hanya Desember atau bulan keluar): hitung ulang setahun …      │
│ Tabel per bulan: bruto · tarif · PPh · DTP · sudah dipotong · selisih               │
│ Peringatan: data dibutuhkan tapi kosong · data diisi tapi tidak dipakai (alasan) ·  │
│   komponen terpetakan ke data yang dicabut (MEMBLOKIR hasil) · di luar cakupan      │
└───────────────────────────────────────────────────────────────────────────────────┘
```

Layar lebar menaruh Hasil di kanan tabel. Layar sempit menumpuknya.

### 3.1 Menambah komponen ("+ Komponen")

Formulir kecil:
- nama, misalnya "Tunjangan komunikasi";
- "Apa ini?": pilihan dari definisi data KB yang berlaku untuk tahun itu, dengan label sifat dan contoh;
- nilai awal dan "mulai bulan" (alat bantu isi).

Hasilnya kolom baru dengan nama itu, dan komponen tersimpan di katalog perusahaan. Bila jenis yang dipilih
bertentangan dengan sifat yang ditulis (misalnya nama mengandung "lembur" tetapi dipilih "sekali-sekali"), sistem
memberi peringatan, bukan larangan.

### 3.2 Kolom yang dihitung kebijakan

Kalau kebijakan perusahaan yang dipilih punya aturan yang menghasilkan nilai untuk jenis data sebuah komponen
(misalnya aturan SP14 menghasilkan THR), sel komponen itu menampilkan hasil engine dengan ikon ⚙ dan tidak bisa
diketik. Ini **dibaca dari KB setiap kali**, tidak disimpan di katalog. Data HR yang dibaca aturan itu (misalnya "THR
dibayar bulan ini", "masa kerja") menjadi kolom yang bisa diketik.

### 3.3 Menyimpan

- Satu pegawai yang sedang dibuka. Tanda ● muncul bila ada perubahan yang belum disimpan.
- **Simpan** menyimpan ke ruang kerja demo, bersama hasil terakhir dan versi KB-nya.
- **Simpan sebagai…** membuat pegawai lain.
- Demo punya beberapa pegawai bawaan. Semuanya kembali seperti semula saat reset demo.

## 4. Kesadaran terhadap KB adaptif

| Perubahan KB | Yang terjadi di kalkulator |
|---|---|
| Pembaruan menambah data baru (aturan + definisinya) | Kolom atau field muncul **sendiri** untuk bulan-bulan sejak tanggal berlakunya. Pegawai tersimpan diberi tanda "data baru dibutuhkan sejak …"; nilai bawaan dipakai sampai diisi, dan itu disebut di peringatan. Kode aplikasi tidak berubah. |
| Data baru berupa pilihan teks (mis. alasan berhenti: resign/PHK) | Muncul sebagai daftar pilihan dengan opsi dari definisinya (atau dari teks yang dibandingkan aturan bila definisi belum ada). |
| Data hanya berlaku sebagian tahun (mis. kebijakan mulai Juli) | Sel bulan sebelum Juli diarsir: "tidak dibutuhkan bulan ini". |
| Data dicabut | Kolom diarsir "tidak dipakai sejak …". Nilai lama tetap tersimpan dan tampil, tetapi tidak dihitung. |
| Jenis data yang dipetakan komponen dicabut atau dipecah (definisi baru "menggantikan" yang lama) | **Peringatan yang memblokir hasil:** "Komponen 'Insentif OTA' dipetakan ke data yang tidak dipakai lagi sejak …; pilih jenis baru". Penghasilan tidak boleh hilang diam-diam dari bruto. |
| Kebijakan perusahaan dipasang/dilepas | Kolom ⚙ berubah antara bisa diketik dan dihitung; data HR-nya muncul atau hilang; isian lama tidak dihapus. |
| Aturan diubah atau angka (parameter) berubah | Hasil pegawai tersimpan dibandingkan dengan hasil terakhir: "Hasil Januari 2026 berubah karena PMK 105/2025", dengan angka sebelum/sesudah. |
| "Aturan per tanggal" dimundurkan | Kolom, pilihan, dan hasil mengikuti KB pada tanggal itu. Kolom yang belum ada saat itu hilang, nilainya tetap tersimpan. Ini memperlihatkan aturan yang berlaku surut. |
| Pilihan tetap (status PTKP, cara bayar pajak, risiko JKK, daftar tahun) | Diambil dari KB: definisi bertipe pilihan, kunci tabel (tarif JKK), dan rentang tahun yang punya aturan. Tidak ada daftar tetap di kode. KLU diketik 5 digit; sistem memberi tahu apakah kode itu ada di tabel DTP tahun itu menurut KB. |

## 5. Skenario umum

Skenario = isian lengkap (profil, perusahaan, komponen perusahaan, angka per bulan, bulan hitung), disimpan dengan
nama komponen perusahaan.
- **Memilih skenario mengisi form yang sedang dibuka**; ada konfirmasi bila ada perubahan belum disimpan.
- Bila skenario membutuhkan data atau kebijakan yang belum ada di KB, form tetap terisi. Kolom yang belum dikenal KB
  ditandai, dengan penjelasan "aktif setelah <dokumen> disetujui".
- **Daftar:**
  - pegawai biasa; Desember hitung setahun; THR dan bonus; masuk tengah tahun;
  - keluar tengah tahun (lebih bayar); gaji naik di tengah bulan; lembur berubah; cuti tanpa upah;
  - gross-up; karyawati kawin; mobil dinas pemegang saham; tahun 2023 (cara lama);
  - DTP padat karya 2026; THR menurut kebijakan perusahaan; PPh bulan lalu berbeda;
  - insentif dengan nama perusahaan (komponen baru).
- Skenario yang sama juga menjadi contoh uji sebelum/sesudah di Review Manajemen KB.

## 6. Bulan penutup dan hal yang ditolak

- **Bulan penutup** adalah Desember, atau bulan keluar untuk pegawai yang berhenti di tengah tahun.
  - Ini sedikit lebih luas dari "hitung setahun khusus Desember" di user_design.txt, karena memang begitu aturannya.
  - Pegawai yang mulai atau berhenti menjadi wajib pajak di Indonesia di tengah tahun (datang dari atau pindah ke luar
    negeri, meninggal) dihitung lain (disetahunkan). Datanya diminta KB lewat "Data lain".
- **Ditolak dengan pesan jelas:**
  - pegawai tidak tetap atau harian;
  - pindahan dari pemberi kerja lain di tahun yang sama (butuh bukti potong pemberi kerja sebelumnya);
  - kembali bekerja di tahun yang sama;
  - pembayaran sesudah keluar, pesangon, pensiunan, pegawai asing (PPh 26), valuta asing.
- **Status PTKP ditetapkan per 1 Januari.** Field ini diberi catatan; perubahan karena menikah atau punya anak baru
  berlaku tahun depan.

## 7. Uji penerimaan (dicoba sebagai admin di browser sebelum dilaporkan)

1. Pegawai baru dengan gaji dan satu tunjangan: hasil pertama muncul dengan **paling banyak 3 isian**.
2. Ganti gaji pokok 10 jt → 12 jt untuk semua bulan: satu ketik + "isi sampai Desember".
3. Gaji naik April: ketik April dan "isi mulai bulan ini"; hasil berubah mulai April saja.
4. "+ Komponen: Tunjangan komunikasi 500.000 mulai Juni": kolom baru, bruto naik mulai Juni, tersimpan di katalog.
5. THR diketik di Maret: masuk Maret.
6. Setujui SP14: kolom THR menjadi ⚙ dan data HR "THR dibayar bulan ini" serta "masa kerja" muncul. **Kode aplikasi
   tidak berubah.** Lepas kebijakan: kolom THR bisa diketik lagi, tanpa kehilangan isian.
7. Setujui pembaruan yang membaca data pilihan teks baru: daftar pilihan muncul dengan opsi dari KB.
8. Cabut jenis data yang dipetakan komponen: peringatan memblokir, angka tidak hilang diam-diam.
9. "Aturan per tanggal" sebelum SP14 disetujui: kolom kebijakan hilang, nilai tetap, hasil dihitung ulang.
10. Setujui PMK 105/2025, buka pegawai tersimpan: tanda "hasil Januari 2026 berubah", dengan angka sebelum/sesudah.
11. Pilih skenario saat ada perubahan belum disimpan: ditanya dulu.
12. Sel yang tidak dibutuhkan bulan itu tetapi berisi nilai lama: ditampilkan, tidak dihitung, diberi peringatan.
13. Desember: kartu hitung setahun. Keluar Agustus: Agustus menjadi bulan penutup, dengan lebih bayar.
14. Pemeriksaan kode: aplikasi kalkulator tidak berisi angka pajak, nama kunci data KB, atau daftar pilihan tetap di
    luar berkas data (definisi KB, katalog, skenario).
15. Semua angka bertitik ribuan; sel yang bisa diketik bertanda ✎ dan bisa diedit dengan satu klik.

## 8. Perubahan pada sistem penelitian yang dibutuhkan

| Perubahan | Wajib untuk | Catatan |
|---|---|---|
| Definisi data sebagai unsur KB (jenis unsur baru di Δ, SHACL, pemeriksaan "data dibaca tanpa definisi" → peringatan) | 3, 7, uji 6–9 | Di mockup: disimpan sebagai berkas data KB demo yang ikut pembaruan (bukan kode). Definisi untuk dokumen tersimpan ditulis terpisah, karena hasil AI penelitian belum memuatnya; di sistem penuh AI menyusunnya bersama usulan. |
| Engine: bulan penutup = Desember atau bulan keluar | hasil sampai bulan tertentu | **Selesai** (`engine-v2`, hasil penelitian identik). |
| Engine: PPh sudah dipotong sebagai data | kolom "PPh sudah dipotong" | **Selesai** (`periods[].recorded`); untuk gross-up/ditanggung, tunjangan pajak bulan itu ikut dicatat. |
| Engine: peringatan "data dibutuhkan tetapi kosong" | peringatan hasil | **Selesai** (`Result.missing_inputs`). |
| Engine menerima tanggal + aturan turunan di KB (masa kerja dari tanggal masuk, hari kerja) | isian lebih sedikit | Bisa ditunda; sementara diisi sebagai angka. |
| Prorata sebagai aturan kebijakan perusahaan (membaca hari kerja) | gaji berubah di tengah bulan | Bisa ditunda; sementara admin mengetik angka sebenarnya. |

## 9. Yang sengaja tidak dibuat

Daftar penghasilan tetap dan daftar kejadian yang terpisah, formulir per bulan sebagai pengganti tabel, kolom tanggal
bayar, gaji bersih, dan manajemen banyak pegawai di luar Simpan/Simpan sebagai. Alasannya: semua itu menambah sumber
angka kedua, atau di luar PPh 21.
