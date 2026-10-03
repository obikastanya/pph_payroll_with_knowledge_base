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
  sisanya tidak dapat dimuat atau menghitung Karyawan A 2023–2027 (metode gross, dan gross-up mulai 2024).
- Urutan penerapan berkas tidak menentukan amandemen `parameter` dan `klasifikasi_wajib`: himpunan berkas yang sama
  selalu memberi versi yang sama, atau selalu ditolak. Urutan masih menentukan `sidik_kb`, label isian yang
  dideklarasikan ulang, dan aturan mana yang tercatat di jejak bila dua aturan seri memberi nilai sama.

## Aturan isi berkas

- **Komponen**: satu `fakta` hanya boleh dideklarasikan sekali di seluruh KB dasar dan berkas tambahan. Deklarasi
  ulang (mis. `px_lembur` dengan kategori lain) ditolak; kategori pajak diubah lewat `klasifikasi_wajib` di berkas
  lapisan regulasi. Kategori: `teratur`, `tidak_teratur`, `premi_objek`, `natura`, `iuran_pengurang`, `zakat`,
  `bukan_objek`, `tidak_diperhitungkan`. `tidak_diperhitungkan` = potongan pegawai tanpa efek pajak (cicilan koperasi,
  iuran BPJS Kesehatan pegawai): mengurangi take home pay (`px_thp`) tanpa mengubah bruto atau PPh 21.
- **Peraturan pemerintah yang memperkenalkan komponen baru** (mis. iuran wajib baru): komponen tetap milik lapisan
  perusahaan. Tulis tarif (`parameter`) dan `klasifikasi_wajib` di berkas lapisan regulasi, lalu komponen dan aturan yang
  membaca parameter itu di berkas lapisan perusahaan terpisah; begitulah JHT, JP, dan THR ditulis di KB dasar. Aturan
  yang menghasilkan fakta rupiah baru tanpa mendaftarkannya sebagai komponen dan tanpa dibaca aturan lain lolos validasi
  dengan peringatan: fakta itu "tidak ikut bruto, PPh 21, maupun take home pay".
- **Masukan**: `kunci` paling panjang 64 karakter. Kunci yang sama boleh dideklarasikan lagi hanya bila `tipe`,
  `lingkup`, `wajib`, `bawaan`, dan `pilihan` identik (`label`, `keterangan`, `sumber` boleh berbeda; deklarasi
  pertama dipakai). Nilai `rupiah` tidak boleh negatif; `bilangan` boleh. Isian tanpa `bawaan` dan tanpa nilai bawaan
  di aturan (`hr_masa('k', 0)`) tetap wajib walau dideklarasikan `wajib: false`. Isian yang punya `bawaan` dihitung
  dengan bawaan setiap kali nilainya kosong, tanpa melihat `wajib` (validasi memberi peringatan; `wajib: true` +
  `bawaan` bertentangan). Nilai yang sama untuk seluruh perusahaan sebaiknya menjadi parameter perusahaan (`px_...`,
  dibaca dengan `parameter('...')`), bukan isian per pegawai.
- **Lingkup**: aturan berlingkup `tahun` tidak boleh memanggil `hr_masa()`. Pakai `hr('kunci')` untuk isian tahunan,
  atau hitung fakta berlingkup `masa` lalu jumlahkan dengan `jumlah_masa()`. Aturan masa dievaluasi pada tanggal 1 tiap
  bulan: aturan yang mulai 15 Juli baru berlaku (dan meminta isian bulanannya) mulai Agustus.
- **Mengganti aturan**: lex specialis (konjungsi `and` terbanyak di `jika`) diputus **sebelum** lex posterior
  (`mulai` terbaru). Aturan pengganti perlu `mulai` lebih baru dan `jika` dengan konjungsi paling sedikit sama banyak
  dengan aturan lama; aturan tanpa `jika` tidak dapat mengganti aturan ber-`jika`. Aturan regulasi `wajib` selalu
  mengalahkan perusahaan. Pengganti aturan titik tetap gross-up (`tunjangan_pajak_berjalan`, `tunjangan_pajak_akhir`)
  wajib bertanda `titik_tetap: true` dengan `batas_titik_tetap`; batas iterasi diambil dari aturan pemenang.
- **Parameter**: rupiah ditulis sebagai bilangan bulat tanpa pemisah ribuan (`11500000`, bukan `"11.500"`), tarif
  sebagai teks desimal (`"0.3"`); semua versi satu parameter harus sejenis. `sampai` tidak boleh sebelum `mulai`.
  Amandemen dari semua berkas diterapkan per parameter menurut tanggal `mulai`, bukan menurut urutan berkas diterapkan
  (amandemen berlaku surut terhadap berkas lain dapat dimuat). Versi baru menutup versi lama sehari sebelum `mulai`;
  amandemen sementara (`mulai`..`sampai`) hanya berlaku di jendela itu, nilai lama berlaku lagi mulai `sampai` + 1 hari,
  dan versi baru boleh mulai tepat pada hari itu. Yang *bentrok* (ditolak, pesannya menyebut berkas lawan): dua amandemen
  dengan `mulai` yang sama, dan versi tulisan KB dasar atau berkas lain yang mulai di dalam jendela amandemen, mis. versi
  permanen yang mulai di tengah amandemen sementara padahal sesudahnya nilai lama berlaku lagi. Satu nama parameter
  dimiliki satu lapisan: parameter di `parameter.yaml` atau yang ditulis berkas lapisan regulasi mana pun tidak boleh
  diubah lapisan perusahaan; parameter buatan lapisan perusahaan boleh diamandemen lapisan perusahaan.
- **Klasifikasi wajib** (hanya lapisan regulasi): entri baru untuk jenis yang sudah ada menggantikan yang lama mulai
  tanggal `mulai`-nya, dan entri sementara mengembalikan klasifikasi lama sesudah `sampai`. Entri lama yang mulai di
  dalam rentang entri baru *bentrok*. Seperti parameter, entri diterapkan per jenis menurut tanggal `mulai`, tidak
  menurut urutan berkas. `kategori` wajib salah satu dari delapan kategori di atas.
- **DSL**: aritmetika (`+ - * /`, minus tunggal) hanya menerima angka; isian persen, desimal, atau tanggal dikonversi
  dulu dengan `persen()`, `desimal()`, atau `tanggal()`. Saat dimuat, engine menolak jumlah argumen fungsi yang salah,
  kategori literal tak dikenal di `komponen()`/`komponen_kode()`/`komponen_valas()` (sah: delapan kategori + `rapel`),
  `parameter('x')` yang tidak ada, `bulatkan('ID', ...)` yang tidak terdaftar, dan ekspresi yang terlalu panjang atau
  terlalu dalam.
