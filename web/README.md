# Aplikasi web payroll (Laravel)

Aplikasi multi-pengguna untuk admin finance: data pegawai, data HR per tahun pajak, proses payroll, slip gaji, dan rekap PPh 21.

**Aplikasi ini tidak menghitung pajak sendiri.** Setiap angka dihitung oleh engine knowledge base di repositori induk (`engine/` + `kb/`), dipanggil lewat jembatan JSON (`jembatan/`). Karena tidak ada rumus yang disalin ke PHP, angka yang tampil di aplikasi ini mewarisi bukti verifikasi engine (V1–V3, E3–E12; lihat README induk §5).

**Aturan baru tidak mengubah kode.** Di menu **Basis pengetahuan**, admin mengunggah PDF peraturan, LLM menyusun rancangan berkas KB, engine memvalidasi dan menyimulasikannya, lalu admin meninjau dan menerapkannya. Bila aturan baru membutuhkan data baru, isiannya muncul otomatis di form data HR.

```text
Laravel (web/)                                   repositori induk
 ├─ pegawai, data HR per tahun, kehadiran        │
 ├─ PenyusunKasus: database -> kasus kanonik ──► python -m jembatan  (stdin: JSON, stdout: JSON)
 │                                               │   └─ engine.kalkulator.hitung + lapisan Perusahaan X
 │                                               │   └─ cek silang: kalkulator tanpa KB (B2 + B1), E12
 ├─ Perhitungan: hasil engine apa adanya ◄───────┘
 ├─ slip gaji, perhitungan setahun (1721-A1), rekap, CSV
 │
 └─ Basis pengetahuan: PDF peraturan ──(antrean)──► python -m jembatan  {"perintah": "usulkan"}
      rancangan + validasi + simulasi ◄──────────────    └─ asisten_kb: LLM menyusun rancangan, engine memvalidasi
      admin meninjau -> Terapkan ─────────────────────► kb/tambahan/NNNN_nama.yaml (ikut dimuat di setiap hitung)
```

## Setup

Prasyarat: PHP ≥ 8.3 (ekstensi `pdo_sqlite`, `mbstring`, `openssl`, `fileinfo`), Composer, dan **venv Python repositori induk sudah terpasang** (README induk §1). Node.js tidak diperlukan: aset tampilan sudah jadi di `public/assets/`. Untuk unggah PDF peraturan (maks. 20 MB), naikkan `upload_max_filesize` dan `post_max_size` di `php.ini` menjadi minimal `32M`, lalu jalankan ulang `php artisan serve`; bawaan PHP (2M/8M) menolak sebagian besar PDF.

```powershell
cd web
composer install
copy .env.example .env          # macOS/Linux: cp .env.example .env
php artisan key:generate
php artisan migrate --seed      # admin demo + 9 pegawai contoh dari dataset (lewat engine)
php artisan serve               # http://localhost:8100 (SERVER_PORT di .env)
```

Ikon memakai Tabler Icons dari CDN jsDelivr, sama seperti Base-Apps-Merdeka, jadi butuh internet. Hal lain berjalan lokal.

Masuk dengan `admin@example.com` / `password`, lalu ganti kata sandinya:

```powershell
php artisan payroll:pengguna admin@example.com "Admin Finance"   # buat pengguna / ganti kata sandi
```

Cek koneksi ke engine di menu **Mesin**: halaman itu menampilkan versi engine, commit KB, dan status verifikasi tabel parameter.

### Database

Bawaannya SQLite (`database/database.sqlite`), tanpa pengaturan apa pun. Untuk **PostgreSQL**, aktifkan ekstensi PHP `pdo_pgsql`, buat databasenya, lalu isi `web/.env`:

```ini
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=its_pph21
DB_USERNAME=postgres
DB_PASSWORD="..."        # apit dengan tanda kutip bila berisi simbol
```

```powershell
php artisan migrate --seed      # tabel + admin demo + 9 pegawai contoh
```

Kode aplikasi tidak bergantung pada salah satu database, dan pencarian tidak peka huruf besar/kecil di keduanya. Tes memakai SQLite dalam memori secara bawaan dan dilindungi agar tidak pernah menyentuh database aplikasi (lihat [Tes](#tes)).

Database adalah sumber kebenaran berkas KB tambahan: setiap kali daftar berkas aktif dibaca, berkas di `kb/tambahan/` yang hilang atau berbeda isinya ditulis ulang dari database (dicatat sebagai peringatan di log). Setelah clone baru atau pemulihan database, folder itu tidak perlu dicadangkan terpisah.

### Konfigurasi (`web/.env`)

| Variabel | Bawaan | Isi |
|---|---|---|
| `SERVER_PORT` | `8100` | Port `php artisan serve`; samakan dengan `APP_URL`. Port 8000 sengaja dihindari karena sering dipakai aplikasi lain |
| `PAYROLL_ROOT` | folder induk `web/` | Repositori induk (berisi `engine/`, `kb/`, `jembatan/`) |
| `PAYROLL_PYTHON` | `<root>\env\Scripts\python.exe` (Windows), `<root>/env/bin/python` | Interpreter venv induk |
| `PAYROLL_TIMEOUT` | `300` | Batas waktu satu panggilan engine, dalam detik |
| `PAYROLL_KLU` | kosong | KLU pemberi kerja. Menentukan fasilitas PPh 21 DTP 2025–2026; kosong = tidak diterapkan |
| `PAYROLL_LLM_MODEL` | `gpt-5.6-sol` | Model yang membaca PDF. Penyedia mengikuti namanya: `gpt-...` = OpenAI, `claude-...` = Anthropic. Tulis nama lengkap yang diizinkan untuk proyek API Anda: alias `gpt-5.6` bisa ditolak (403) walau `gpt-5.6-sol` diizinkan. `gpt-5.6-terra` dan `gpt-5.6-luna` lebih murah |
| `OPENAI_API_KEY` | kosong | Kunci API untuk model OpenAI (bawaan). Tanpa kunci, unggahan PDF gagal dengan pesan jelas; fitur lain tetap berjalan |
| `ANTHROPIC_API_KEY` | kosong | Hanya bila `PAYROLL_LLM_MODEL` diisi model `claude-...` |
| `PAYROLL_LLM_TIMEOUT` | `900` | Batas waktu membaca satu dokumen, dalam detik |
| `DB_QUEUE_RETRY_AFTER` | `1080` | Detik sebelum job antrean yang belum selesai dianggap hilang dan diambil ulang. Wajib lebih besar dari `PAYROLL_LLM_TIMEOUT` + 60; bila lebih kecil, pekerja lain mengambil ulang job LLM yang masih berjalan dan menandainya gagal |

Membaca PDF berjalan di antrean Laravel (`QUEUE_CONNECTION=database`). Jalankan pekerjanya di terminal terpisah:

```powershell
php artisan queue:listen --timeout=960
```

Di Windows, pakai `queue:listen`: batas waktu `queue:work` bergantung pada ekstensi `pcntl` yang tidak ada di Windows, sedangkan `queue:listen` menjalankan setiap job sebagai proses terpisah dengan batas waktu. Di macOS/Linux `queue:work --timeout=960` juga dapat dipakai. Setelah mengubah `.env`, hentikan pekerja (Ctrl + C) lalu jalankan lagi.

Kunci API tidak pernah ditulis ke repositori (`.env` ada di `.gitignore`). Proses Python jembatan tidak mewarisi `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DB_PASSWORD`, `DB_URL`, `APP_KEY`, `MAIL_PASSWORD`, `REDIS_PASSWORD`, dan `AWS_SECRET_ACCESS_KEY`; hanya perintah `usulkan` yang menerima satu kunci LLM sesuai model terpilih. Kegagalan jembatan dicatat di log (perintah, kode keluar, durasi, akhir stderr) tanpa isi permintaan.

## Alur kerja

1. **Pegawai**: tambah pegawai (tanggal masuk dan berhenti menentukan bulan yang dihitung).
2. **Tambah tahun**: isi data HR satu tahun pajak. Isinya status PTKP, metode (gross / gross-up / ditanggung), gaji dan kenaikan, tunjangan tetap/prorata, THR, BPJS, serta kehadiran dan penghasilan variabel per bulan. Isian awal dilanjutkan dari tahun sebelumnya; isian tambahan tahunan dari KB diisi dari tahun terakhir pegawai yang memilikinya (hanya kunci yang masih diminta KB aktif), isian tambahan per bulan tidak dibawa.
3. **Hitung** (per pegawai) atau **Hitung semua** di halaman Dashboard. Satu tahun dikirim ke engine dalam satu panggilan, sehingga KB cukup dimuat sekali.
4. **Hasil**:
   - slip gaji per bulan; setiap angka menunjuk aturan KB dan pasalnya;
   - perhitungan setahun gaya 1721-A1 dengan rincian Pasal 17;
   - tabel 12 bulan;
   - jejak inferensi lengkap;
   - peringatan konflik kebijakan;
   - cek silang dengan kalkulator tanpa KB;
   - cetak slip dan unduh CSV.

Slip (layar dan cetak memakai baris yang sama) mengelompokkan komponen dari berkas KB tambahan menurut kategori efektifnya: bila regulasi mewajibkan kategori lain (`KONFLIK_WAJIB`), slip mengikuti kategori wajib seperti engine. Kategori `tidak_diperhitungkan` (potongan pegawai tanpa efek pajak, mis. cicilan koperasi) tampil di **Potongan** karena take home pay menguranginya; `bukan_objek` tampil di bagian terpisah *Lainnya (bukan objek pajak, tidak dibayar tunai)* sesudah take home pay. Peringatan konflik tingkat aturan tampil sekali sebagai *Aturan X untuk (komponen) tidak dipakai karena aturan wajib Y berlaku.*

CSV payroll per pegawai berisi kolom `bulan` lalu kolom tetap (`px_gaji` ... `px_thp`) dengan urutan selalu sama; komponen dari berkas KB tambahan ditambahkan di akhir menurut urutan deklarasi. Nama unduhan mengganti karakter selain `A-Z a-z 0-9 . _ -` dengan `-` (nomor induk `001/HR/2023` → `payroll_001-HR-2023_2024.csv`).

Setiap perhitungan disimpan sebagai riwayat baru, tanpa menimpa yang lama. Yang tersimpan adalah kasus yang dikirim, keluaran engine, versi KB, sidik berkas KB tambahan, dan siapa yang menghitung. Bila data HR atau berkas KB tambahan berubah sesudah dihitung, aplikasi menandainya usang (*data HR berubah* / *aturan KB berubah*); kartu Dashboard menghitung hasil usang sebagai perlu dihitung ulang, dan slip cetak menampilkan spanduk *Hasil usang* serta sidik berkas KB tambahan di kakinya. CSV rekap Dashboard: kolom `status` berisi `berhasil`, `usang (data)`, `usang (aturan KB)`, `galat`, atau `belum`, disusul kolom `sidik_kb` dan `pesan` (pesan galat).

### Aturan baru (menu Basis pengetahuan)

1. **Unggah** PDF peraturan (maks. 20 MB; form menampilkan batas efektif, yaitu yang terkecil dari 20 MB dan `upload_max_filesize`/`post_max_size` PHP), pilih jenisnya (peraturan perusahaan atau pemerintah), dan beri catatan bila perlu. Unggahan yang melebihi `post_max_size` kembali ke form dengan pesan, bukan halaman galat 413/419.
2. **LLM menyusun rancangan** berkas KB di antrean. Halaman usulan diperbarui otomatis. Selama masih *antre*, unggahan dapat **dibatalkan**. Bila menunggu lama, halaman mengingatkan untuk menjalankan pekerja antrean. Usulan yang terlalu lama *dibaca LLM* (lebih dari `PAYROLL_LLM_TIMEOUT` + 120 detik, mis. karena pekerja berhenti) ditandai gagal saat halamannya dibuka; setelah itu dapat **Baca ulang** atau dihapus. Kegagalan job menampilkan alasan yang jelas (pekerja berhenti atau job diambil ulang, batas waktu terlampaui).
3. **Tinjau**. Halaman usulan menampilkan:
   - ringkasan dokumen dan hal yang menurut LLM perlu diperiksa; lencana peringatan bila lapisan yang tertulis di YAML berbeda dari pilihan unggah (lapisan berkas selalu mengikuti pilihan unggah, pilihan LLM dicatat untuk peninjau);
   - hasil validasi engine (skema, verifikasi statis KB, simulasi). *Lolos* menjadi kuning bila masih ada peringatan atau aturan belum teruji;
   - kartu *Yang diubah rancangan ini*: aturan, parameter, dan klasifikasi yang sudah ada yang berubah, serta *Aturan belum teruji* (tidak pernah terpilih di simulasi, dengan alasannya);
   - isian baru yang akan diminta di form data HR;
   - setiap aturan dengan rumus, pasal, kutipan, dan halaman PDF-nya;
   - simulasi dampak (bruto, PPh 21, take home pay sebelum/sesudah) pada dua pegawai contoh, Karyawan A dan pegawai masuk Juli, untuk tahun-tahun yang diturunkan dari masa berlaku rancangan;
   - berkas YAML yang boleh diubah; setiap simpan divalidasi ulang dengan lapisan pilihan unggah.
4. **Terapkan** (hanya bila lolos validasi; konfirmasinya menyebut berapa hal yang sudah ada di KB yang berubah), **Tolak**, atau **Baca ulang**. Berkas yang diterapkan ditulis ke `kb/tambahan/` dan dapat dinonaktifkan kapan saja. Sebelum menonaktifkan, engine menjalankan `periksa` pada berkas aktif yang tersisa (memuat KB dan menghitung Karyawan A 2023–2027); bila gagal, penonaktifan ditolak dengan kutipan galat engine. Halaman **Mesin** juga melaporkan hasil `periksa` setiap kali ada berkas tambahan aktif.
5. **Isi data baru**. Bila berkas mendeklarasikan `masukan`, form data HR menampilkan bagian *Isian tambahan dari knowledge base*: isian tahunan dan isian per bulan, hanya untuk tahun dan bulan saat aturannya berlaku. Engine mengevaluasi aturan pada tanggal 1 tiap bulan, jadi aturan yang mulai 15 Juli baru meminta isian bulanannya mulai Agustus; isian tahunan diminta di tahun Y bila aturannya mulai paling lambat 1 Desember Y dan berakhir paling cepat 1 Januari Y. Tipenya rupiah, bilangan, persen, desimal, tanggal, pilihan, atau ya/tidak. Komponen gaji baru tampil di slip dan CSV dengan label dari berkas KB.

LLM hanya mengusulkan. Ia tidak menghitung pajak, tidak dapat mengubah tabel TER/PTKP/Pasal 17, dan rancangannya tidak pernah berlaku tanpa persetujuan admin. Validasi engine memeriksa bentuk dan konsistensi, **bukan** kesesuaian dengan isi dokumen; mencocokkan aturan dengan kutipan PDF adalah tugas peninjau.

## Validasi isian

Validasinya mencegah angka salah yang lolos diam-diam:

- Nominal wajib rupiah bulat; float dan sen ditolak.
- Persen disimpan sebagai teks desimal, lalu dikonversi eksak (`app/Helpers/Desimal.php`).
- Setiap bulan dalam masa kerja wajib berisi hari kerja dan hadir, dan hadir tidak boleh melebihi hari kerja.
- Kenaikan gaji di tengah bulan wajib dipecah ke hari sebelum/sesudah, dengan jumlah yang sama dengan hari bulan itu. Tanpa aturan ini, gaji bulan tersebut akan menjadi 0 diam-diam.
- Isian tambahan dari KB divalidasi menurut tipe di deklarasinya. Isian wajib tanpa nilai bawaan harus diisi (pilihan dan ya/tidak yang wajib juga ditandai wajib di browser); engine juga menolak nilai bertipe salah dengan pesan yang menyebut label isiannya. Isian bertipe rupiah tidak boleh negatif (`min="0"` di form, ditolak saat simpan dan oleh engine); bertipe bilangan boleh negatif.

## Tes

```powershell
php artisan test                       # semua tes (integrasi engine dilewati bila venv induk tidak ada)
php vendor/bin/phpunit --group mesin   # hanya integrasi nyata dengan engine Python
```

Tes tidak pernah menyentuh database aplikasi. `phpunit.xml` memaksa (`force="true"`) SQLite `:memory:` beserta cache, sesi, antrean, mail, dan broadcast palsu, sehingga nilai dari `.env` atau shell tidak dapat mengalihkannya. Selain itu `TestCase` menghentikan setiap tes sebelum migrasi bila koneksinya bukan SQLite `:memory:` (mis. karena konfigurasi ter-cache; jalankan `php artisan config:clear`). Uji opsional di PostgreSQL memakai database **terpisah**: buat `its_pph21_uji`, lalu jalankan `php artisan test --configuration=phpunit.pgsql.xml` (nama pengguna dan sandi diambil dari `.env`). Pengaman hanya mengizinkan database berakhiran `_uji` dengan `PAYROLL_UJI_PGSQL=1`, yang diset oleh berkas konfigurasi itu.

`tests/Feature/IntegrasiMesinTest.php` memeriksa jaminan utama aplikasi ini. Untuk kesembilan pegawai contoh, kasus yang disusun dari database **identik** dengan kasus di dataset. Hasil hitung lewat web juga sama persis dengan engine yang dipanggil langsung (Karyawan A 2023: PPh 21 setahun Rp7.341.750, cek silang identik). Tes lainnya memakai engine palsu (`Process::fake`). Di sisi Python, protokol jembatan diuji di `tests/test_jembatan.py` induk.

Fitur aturan baru diuji di tiga tempat:

- `IntegrasiMesinTest` (engine sungguhan, tanpa LLM): rancangan salah ditolak; rancangan benar diterapkan; isian baru muncul di form; hasilnya masuk bruto, PPh 21, dan take home pay; setelah dinonaktifkan angka kembali ke Rp7.341.750 dan cek silang kembali identik.
- `BasisPengetahuanTest`: unggah (batas ukuran), antrean, status, usulan macet, pembatalan, tinjau (termasuk bentuk hasil validasi yang rusak), terapkan/tolak/nonaktifkan (dengan `periksa`)/hapus, pemulihan berkas dari database, rahasia yang tidak diwariskan ke jembatan, dan pengaman database uji.
- `MasukanKbTest`: form dinamis, validasi per tipe, isian per bulan (aturan mulai di tengah bulan), isian tahunan dibawa ke tahun baru, kolom CSV, sidik KB, kunci cache skema, dan penanda hasil usang.

Panggilan LLM sungguhan tidak ada di tes; klien LLM tiruan diuji di `tests/test_asisten_kb.py` induk.

## Struktur

Struktur dan gaya tampilan mengikuti **Base-Apps-Merdeka**.

### Module

Setiap fitur adalah module di `modules/{Nama}/`. Isinya:

- `Http/Controllers` dan `Http/Requests`;
- `Repositories/{Nama}Interface.php` + `{Nama}Repository.php`, di-bind otomatis;
- `Providers/{Nama}ServiceProvider.php`, yang memuat routes dan views dengan namespace `{Nama}::`;
- `Resources/views` dan `Routes/web`.

`App\Providers\ModuleServiceProvider` mendaftarkan semua provider module secara otomatis. Module baru dibuat dengan:

```powershell
php artisan make:module Laporan    # kerangka lengkap + route laporan.index; tambahkan ke config/menu.php
```

| Module | Isi |
|---|---|
| `Dashboard` | Rekap payroll per tahun: kartu ringkasan, tabel AJAX, hitung semua (satu panggilan engine), ekspor CSV |
| `Pegawai` | Daftar pegawai (tabel AJAX: cari, filter, urut, paginasi), tambah/ubah lewat modal, halaman detail per tahun pajak |
| `Payroll` | Form data HR tahunan, hasil (slip, 1721-A1, 12 bulan + grafik, jejak aturan), cetak slip, riwayat. `Services/` berisi klien engine |
| `BasisPengetahuan` | Unggah PDF peraturan, antrean LLM (`Jobs/ProsesUsulanKb`), halaman tinjau, terapkan/tolak/nonaktifkan (`Services/PenerapanKb`) |
| `Mesin` | Status engine: konfigurasi jembatan, versi engine, commit KB, verifikasi tabel parameter, berkas KB tambahan aktif dan hasil `periksa`-nya |

| Lokasi | Isi |
|---|---|
| `modules/Payroll/Services/MesinPajak.php` | Klien jembatan: menjalankan `python -m jembatan` di repositori induk (`hitung`, `masukan`, `usulkan`, `validasi`, `periksa`, ...) tanpa variabel rahasia (`RAHASIA`) |
| `modules/Payroll/Services/KbTambahan.php` | Berkas KB tambahan yang aktif, sidik isinya, tulis/hapus berkas di `kb/tambahan/`, tulis ulang berkas aktif yang hilang/berbeda dari database |
| `modules/Payroll/Services/SkemaMasukan.php` | Isian tambahan yang diminta KB aktif untuk form data HR (dari engine, di-cache per sidik berkas tambahan **dan** sidik KB dasar: `kb/regulasi`, `kb/perusahaan`, `jembatan/kontrak.py`, `asisten_kb/rancangan.py`; perubahan di sana terbaca tanpa `cache:clear`) |
| `modules/Payroll/Services/PenyusunKasus.php` | Database → kasus kanonik `data_hr` (padanan `ui/kalkulator.py::form_hr`), termasuk isian tambahan |
| `modules/Payroll/Services/Penghitung.php` | Hitung satu/banyak pegawai dalam satu panggilan, catat riwayat, deteksi data atau KB berubah |
| `modules/Payroll/Services/TampilanHasil.php` | Menata keluaran engine untuk slip / 1721-A1 / jejak (padanan `ui/hasil.py`); komponen baru dari KB tampil dengan labelnya |
| `modules/Payroll/Services/ImporContoh.php` | Kasus kanonik → database (pegawai contoh dari dataset) |
| `app/Models/Payroll/` | `Pegawai`, `PayrollTahun`, `PayrollBulan`, `PayrollMasukan`, `Perhitungan` |
| `app/Models/Kb/` | `UsulanKb` (dokumen, rancangan, hasil validasi, status) |
| `app/Helpers/` | `Desimal` (persen eksak tanpa float), `Format` (rupiah, tarif, bulan) |
| `database/migrations/` | `pegawai`, `payroll_tahun`, `payroll_bulan`, `perhitungan`, `payroll_masukan`, `kb_usulan` |

### Tampilan

| Lokasi | Isi |
|---|---|
| `resources/views/main/` | Layout `main.index`: sidebar vertikal yang bisa diciutkan, navbar dengan `@section('page-title')`, breadcrumb dari `$menuItems`, footer, notifikasi SweetAlert dari session `success`/`error`/`warning` |
| `resources/views/main/components/js/` | jQuery, `renderTableWithFeatures` (tabel AJAX + paginasi + urut, dengan escaping HTML), `showError`, konfirmasi form `data-konfirmasi` |
| `resources/views/components/global/` | `x-global.btn-detail`, `x-global.summary-card`, `x-global.cek-silang` |
| `config/menu.php` | Item sidebar (section, title, ikon Tabler, route). Base-Apps-Merdeka menyimpan menu di tabel `menu` dengan role; di sini cukup satu peran |
| `public/assets/` | Tabler 1.0.0-beta19 (MIT), `custom.css`/`constant.css` (token `mdka-*`, disalin dari Base-Apps-Merdeka), font Inter (OFL), jQuery, ApexCharts, SweetAlert2 |

Halaman login (`resources/views/auth/`) mengikuti template login Base-Apps-Merdeka:

- latar foto yang digelapkan;
- kartu dengan carousel foto ber-thumbnail di kiri;
- panel kanan berisi merek, form, dan tombol "Panduan masuk" yang membuka modal;
- galat login dan notifikasi keluar lewat SweetAlert.

Bagian SSO Google/Microsoft tidak ditiru karena aplikasi ini tidak memakai SSO. Foto login berlisensi **CC0** dari StockSnap/rawpixel (dicari lewat Openverse); kreditnya ada di `public/assets/img/bg-auth/KREDIT.md`.

Logo, foto, dan nama Merdeka sengaja **tidak** disalin karena repositori ini publik. Merek aplikasi memakai ikon Tabler. Di `custom.css` ada satu perbaikan dibanding aslinya: baris `/////!SECTION` (komentar `//` tidak sah di CSS) membuat aturan `.mdka-nav-btn` dibuang browser. Baris itu kini menjadi `/* !SECTION */`.

## Batasan

- Lapisan perusahaan dasar tetap **Perusahaan X** (`kb/perusahaan/perusahaan_x.yaml`), dan isian inti form data HR mengikuti struktur kebijakan itu. Berkas KB tambahan menambah atau mengganti aturan di atasnya; mengganti kebijakan dasar seluruhnya masih perlu berkas KB sendiri dan penyesuaian isian inti.
- **Mutu rancangan LLM terhadap dokumen nyata belum dievaluasi.** Yang diuji adalah alur dan validasinya (dengan klien LLM tiruan dan engine sungguhan). Anggap setiap rancangan sebagai draf yang wajib dicocokkan dengan dokumen.
- Perhitungan yang memakai berkas KB tambahan tidak punya cek silang: kalkulator pembanding tanpa KB tidak mengenal aturan baru, jadi statusnya *dilewati*.
- Take home pay otomatis mengikuti komponen baru berkategori teratur, tidak teratur, iuran pengurang, zakat, dan `tidak_diperhitungkan` (potongan non-pajak, mis. cicilan koperasi). Berkas tambahan tidak dapat mendeklarasikan ulang komponen Perusahaan X (`px_*`); pakai fakta baru, atau ubah perlakuan pajaknya lewat `klasifikasi_wajib` di berkas regulasi.
- Tahun pajak yang dibuka adalah 2023–2026, rentang yang sudah diuji E12. Gross-up 2023 (rezim PER-16) di luar model engine dan akan ditolak dengan pesan jelas.
- Mode "komponen gaji sudah jadi" (contoh resmi regulasi) tetap ada di demo Streamlit induk, tidak di aplikasi ini.
- Perhitungan berjalan sinkron di request. Untuk ratusan pegawai, pindahkan "Hitung semua" ke queue Laravel.
- Prototipe penelitian, bukan alat konsultasi pajak resmi. Default tafsir belum dikalibrasi ke kalkulator DJP (README induk §6).
