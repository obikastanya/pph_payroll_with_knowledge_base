# Aplikasi web payroll (Laravel)

Aplikasi multi-pengguna untuk admin finance: data pegawai, data HR per tahun pajak, proses payroll, slip gaji, dan rekap PPh 21.

**Aplikasi ini tidak menghitung pajak sendiri.** Setiap angka dihitung oleh engine knowledge base di repositori induk (`engine/` + `kb/`), dipanggil lewat jembatan JSON (`jembatan/`). Karena engine dan KB tidak diubah, angka yang tampil di aplikasi ini mewarisi bukti verifikasi engine (V1–V3, E3–E12; lihat README induk §5).

```text
Laravel (web/)                                   repositori induk
 ├─ pegawai, data HR per tahun, kehadiran        │
 ├─ PenyusunKasus: database -> kasus kanonik ──► python -m jembatan  (stdin: JSON, stdout: JSON)
 │                                               │   └─ engine.kalkulator.hitung + lapisan Perusahaan X
 │                                               │   └─ cek silang: kalkulator tanpa KB (B2 + B1), E12
 ├─ Perhitungan: hasil engine apa adanya ◄───────┘
 └─ slip gaji, perhitungan setahun (1721-A1), rekap, CSV
```

## Setup

Prasyarat: PHP ≥ 8.3 (ekstensi `pdo_sqlite`, `mbstring`, `openssl`, `fileinfo`), Composer, dan **venv Python repositori induk sudah terpasang** (README induk §1). Node.js tidak diperlukan: aset tampilan sudah jadi di `public/assets/`.

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

### Konfigurasi (`web/.env`)

| Variabel | Bawaan | Isi |
|---|---|---|
| `SERVER_PORT` | `8100` | Port `php artisan serve`; samakan dengan `APP_URL`. Port 8000 sengaja dihindari karena sering dipakai aplikasi lain |
| `PAYROLL_ROOT` | folder induk `web/` | Repositori induk (berisi `engine/`, `kb/`, `jembatan/`) |
| `PAYROLL_PYTHON` | `<root>\env\Scripts\python.exe` (Windows), `<root>/env/bin/python` | Interpreter venv induk |
| `PAYROLL_TIMEOUT` | `300` | Batas waktu satu panggilan engine, dalam detik |
| `PAYROLL_KLU` | kosong | KLU pemberi kerja. Menentukan fasilitas PPh 21 DTP 2025–2026; kosong = tidak diterapkan |

## Alur kerja

1. **Pegawai**: tambah pegawai (tanggal masuk dan berhenti menentukan bulan yang dihitung).
2. **Tambah tahun**: isi data HR satu tahun pajak. Isinya status PTKP, metode (gross / gross-up / ditanggung), gaji dan kenaikan, tunjangan tetap/prorata, THR, BPJS, serta kehadiran dan penghasilan variabel per bulan. Isian awal dilanjutkan dari tahun sebelumnya.
3. **Hitung** (per pegawai) atau **Hitung semua** di halaman Dashboard. Satu tahun dikirim ke engine dalam satu panggilan, sehingga KB cukup dimuat sekali.
4. **Hasil**:
   - slip gaji per bulan; setiap angka menunjuk aturan KB dan pasalnya;
   - perhitungan setahun gaya 1721-A1 dengan rincian Pasal 17;
   - tabel 12 bulan;
   - jejak inferensi lengkap;
   - peringatan konflik kebijakan;
   - cek silang dengan kalkulator tanpa KB;
   - cetak slip dan unduh CSV.

Setiap perhitungan disimpan sebagai riwayat baru, tanpa menimpa yang lama. Yang tersimpan adalah kasus yang dikirim, keluaran engine, versi KB, dan siapa yang menghitung. Bila data HR diubah sesudah dihitung, aplikasi menandainya *data berubah, hitung ulang*.

## Validasi isian

Validasinya mencegah angka salah yang lolos diam-diam:

- Nominal wajib rupiah bulat; float dan sen ditolak.
- Persen disimpan sebagai teks desimal, lalu dikonversi eksak (`app/Helpers/Desimal.php`).
- Setiap bulan dalam masa kerja wajib berisi hari kerja dan hadir, dan hadir tidak boleh melebihi hari kerja.
- Kenaikan gaji di tengah bulan wajib dipecah ke hari sebelum/sesudah, dengan jumlah yang sama dengan hari bulan itu. Tanpa aturan ini, gaji bulan tersebut akan menjadi 0 diam-diam.

## Tes

```powershell
php artisan test                       # semua tes (integrasi engine dilewati bila venv induk tidak ada)
php vendor/bin/phpunit --group mesin   # hanya integrasi nyata dengan engine Python
```

`tests/Feature/IntegrasiMesinTest.php` memeriksa jaminan utama aplikasi ini. Untuk kesembilan pegawai contoh, kasus yang disusun dari database **identik** dengan kasus di dataset. Hasil hitung lewat web juga sama persis dengan engine yang dipanggil langsung (Karyawan A 2023: PPh 21 setahun Rp7.341.750, cek silang identik). Tes lainnya memakai engine palsu (`Process::fake`). Di sisi Python, protokol jembatan diuji di `tests/test_jembatan.py` induk.

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
| `Mesin` | Status engine: konfigurasi jembatan, versi engine, commit KB, verifikasi tabel parameter |

| Lokasi | Isi |
|---|---|
| `modules/Payroll/Services/MesinPajak.php` | Klien jembatan: menjalankan `python -m jembatan` di repositori induk |
| `modules/Payroll/Services/PenyusunKasus.php` | Database → kasus kanonik `data_hr` (padanan `ui/kalkulator.py::form_hr`) |
| `modules/Payroll/Services/Penghitung.php` | Hitung satu/banyak pegawai dalam satu panggilan, catat riwayat, deteksi data berubah |
| `modules/Payroll/Services/TampilanHasil.php` | Menata keluaran engine untuk slip / 1721-A1 / jejak (padanan `ui/hasil.py`) |
| `modules/Payroll/Services/ImporContoh.php` | Kasus kanonik → database (pegawai contoh dari dataset) |
| `app/Models/Payroll/` | `Pegawai`, `PayrollTahun`, `PayrollBulan`, `Perhitungan` |
| `app/Helpers/` | `Desimal` (persen eksak tanpa float), `Format` (rupiah, tarif, bulan) |
| `database/migrations/` | `pegawai`, `payroll_tahun`, `payroll_bulan`, `perhitungan` |

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

- Lapisan perusahaan tetap **Perusahaan X** (`kb/perusahaan/perusahaan_x.yaml`), karena isian data HR mengikuti struktur kebijakan itu. Perusahaan lain perlu berkas KB sendiri, dan formnya perlu disesuaikan.
- Tahun pajak yang dibuka adalah 2023–2026, rentang yang sudah diuji E12. Gross-up 2023 (rezim PER-16) di luar model engine dan akan ditolak dengan pesan jelas.
- Mode "komponen gaji sudah jadi" (contoh resmi regulasi) tetap ada di demo Streamlit induk, tidak di aplikasi ini.
- Perhitungan berjalan sinkron di request. Untuk ratusan pegawai, pindahkan "Hitung semua" ke queue Laravel.
- Prototipe penelitian, bukan alat konsultasi pajak resmi. Default tafsir belum dikalibrasi ke kalkulator DJP (README induk §6).
