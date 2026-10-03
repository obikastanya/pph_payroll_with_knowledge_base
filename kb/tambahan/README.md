# kb/tambahan — berkas KB yang diterapkan lewat aplikasi web

Folder ini diisi aplikasi web (menu **Basis pengetahuan**): setiap peraturan baru yang rancangannya disetujui admin
ditulis ke sini sebagai satu berkas YAML, lalu ikut dimuat engine (`berkas_tambahan` di protokol `jembatan/`).

- Format berkas sama dengan berkas KB lain (`kb/skema/aturan.schema.json`): `aturan`, `komponen` (hanya lapisan
  perusahaan), `masukan` (isian baru yang diminta dari pengguna), `parameter` (amandemen nilai berversi), `pembulatan`,
  `klasifikasi_wajib` (hanya lapisan regulasi). Anchor/alias YAML (`&nama` / `*nama`) tidak diizinkan.
- Berkas di sini **tidak** ikut versi git (`.gitignore`): isinya data runtime tiap instalasi. Database aplikasi
  (tabel `kb_usulan`) adalah sumber kebenarannya: berkas aktif yang hilang atau berbeda isinya ditulis ulang dari
  database, jadi folder ini tidak perlu dicadangkan terpisah. Setiap perhitungan menyimpan sidik berkas aktif
  (`sidik_kb`).
- Tabel terverifikasi (TER, tarif Pasal 17, PTKP, KLU DTP) tidak dapat diubah dari sini; perubahan tabel tetap lewat
  jalur double-entry di `kb/regulasi/` + `tabel_manifest.yaml`.
- Rancangan berkas disusun LLM (`asisten_kb/`, PDF maks. 20 MB), tetapi engine tidak memakai LLM: berkas baru berlaku
  hanya setelah lolos validasi engine (skema, verifikasi statis, simulasi) dan disetujui manusia. Rupiah berpemisah
  ribuan di rancangan LLM (`500.000`, `1,500,000`) diubah menjadi bilangan bulat; status pembulatan `tafsir` tidak
  ditawarkan ke LLM.
- Sebelum berkas dinonaktifkan, engine menjalankan `periksa` pada berkas yang tersisa; penonaktifan ditolak bila KB
  sisanya tidak dapat dimuat atau menghitung Karyawan A 2023–2027.

## Aturan isi berkas

- **Komponen**: satu `fakta` hanya boleh dideklarasikan sekali di seluruh KB dasar dan berkas tambahan. Deklarasi
  ulang (mis. `px_lembur` dengan kategori lain) ditolak; kategori pajak diubah lewat `klasifikasi_wajib` di berkas
  lapisan regulasi. Kategori: `teratur`, `tidak_teratur`, `premi_objek`, `natura`, `iuran_pengurang`, `zakat`,
  `bukan_objek`, `tidak_diperhitungkan`. `tidak_diperhitungkan` = potongan pegawai tanpa efek pajak (cicilan koperasi,
  iuran BPJS Kesehatan pegawai): mengurangi take home pay (`px_thp`) tanpa mengubah bruto atau PPh 21.
- **Masukan**: `kunci` paling panjang 64 karakter. Kunci yang sama boleh dideklarasikan lagi hanya bila `tipe`,
  `lingkup`, `wajib`, `bawaan`, dan `pilihan` identik (`label`, `keterangan`, `sumber` boleh berbeda; deklarasi
  pertama dipakai). Nilai `rupiah` tidak boleh negatif; `bilangan` boleh. Isian tanpa `bawaan` dan tanpa nilai bawaan
  di aturan (`hr_masa('k', 0)`) tetap wajib walau dideklarasikan `wajib: false`.
- **Lingkup**: aturan berlingkup `tahun` tidak boleh memanggil `hr_masa()`. Pakai `hr('kunci')` untuk isian tahunan,
  atau hitung fakta berlingkup `masa` lalu jumlahkan dengan `jumlah_masa()`. Aturan masa dievaluasi pada tanggal 1 tiap
  bulan: aturan yang mulai 15 Juli baru berlaku (dan meminta isian bulanannya) mulai Agustus.
- **Mengganti aturan**: lex specialis (konjungsi `and` terbanyak di `jika`) diputus **sebelum** lex posterior
  (`mulai` terbaru). Aturan pengganti perlu `mulai` lebih baru dan `jika` dengan konjungsi paling sedikit sama banyak
  dengan aturan lama; aturan tanpa `jika` tidak dapat mengganti aturan ber-`jika`. Aturan regulasi `wajib` selalu
  mengalahkan perusahaan.
- **Parameter**: rupiah ditulis sebagai bilangan bulat tanpa pemisah ribuan (`11500000`, bukan `"11.500"`), tarif
  sebagai teks desimal (`"0.3"`); semua versi satu parameter harus sejenis. `sampai` tidak boleh sebelum `mulai`. Versi
  baru menutup versi lama sehari sebelum `mulai`; amandemen sementara (`mulai`..`sampai`) hanya berlaku di jendela itu,
  dan nilai lama berlaku lagi mulai `sampai` + 1 hari. Versi yang sudah ada dan mulai di dalam jendela itu *bentrok*
  (ditolak); versi yang mulai sesudahnya dipertahankan. Lapisan perusahaan boleh mengamandemen parameter buatan lapisan
  perusahaan, tetapi tidak pernah parameter regulasi.
- **Klasifikasi wajib** (hanya lapisan regulasi): entri baru untuk jenis yang sudah ada menggantikan yang lama mulai
  tanggal `mulai`-nya, dan entri sementara mengembalikan klasifikasi lama sesudah `sampai`. Entri lama yang mulai di
  dalam rentang entri baru *bentrok*. `kategori` wajib salah satu dari delapan kategori di atas.
- **DSL**: aritmetika (`+ - * /`, minus tunggal) hanya menerima angka; isian persen, desimal, atau tanggal dikonversi
  dulu dengan `persen()`, `desimal()`, atau `tanggal()`. Saat dimuat, engine menolak jumlah argumen fungsi yang salah,
  kategori literal tak dikenal di `komponen()`/`komponen_kode()`/`komponen_valas()` (sah: delapan kategori + `rapel`),
  `parameter('x')` yang tidak ada, `bulatkan('ID', ...)` yang tidak terdaftar, dan ekspresi yang terlalu panjang atau
  terlalu dalam.
