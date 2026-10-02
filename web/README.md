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

Prasyarat: PHP ≥ 8.3 (ekstensi `pdo_sqlite`, `mbstring`, `openssl`, `fileinfo`), Composer, Node.js ≥ 20, dan **venv Python repositori induk sudah terpasang** (README induk §1).

```powershell
cd web
composer install
copy .env.example .env          # macOS/Linux: cp .env.example .env
php artisan key:generate
php artisan migrate --seed      # admin demo + 9 pegawai contoh dari dataset (lewat engine)
npm install
npm run build
php artisan serve               # http://localhost:8000
```

Masuk dengan `admin@example.com` / `password`, lalu ganti kata sandinya:

```powershell
php artisan payroll:pengguna admin@example.com "Admin Finance"   # buat pengguna / ganti kata sandi
```

Cek koneksi ke engine di menu **Mesin**: halaman itu menampilkan versi engine, commit KB, dan status verifikasi tabel parameter.

### Konfigurasi (`web/.env`)

| Variabel | Bawaan | Isi |
|---|---|---|
| `PAYROLL_ROOT` | folder induk `web/` | Repositori induk (berisi `engine/`, `kb/`, `jembatan/`) |
| `PAYROLL_PYTHON` | `<root>\env\Scripts\python.exe` (Windows), `<root>/env/bin/python` | Interpreter venv induk |
| `PAYROLL_TIMEOUT` | `300` | Batas waktu satu panggilan engine, dalam detik |
| `PAYROLL_KLU` | kosong | KLU pemberi kerja. Menentukan fasilitas PPh 21 DTP 2025–2026; kosong = tidak diterapkan |

## Alur kerja

1. **Pegawai**: tambah pegawai (tanggal masuk dan berhenti menentukan bulan yang dihitung).
2. **Tambah tahun**: isi data HR satu tahun pajak. Isinya status PTKP, metode (gross / gross-up / ditanggung), gaji dan kenaikan, tunjangan tetap/prorata, THR, BPJS, serta kehadiran dan penghasilan variabel per bulan. Isian awal dilanjutkan dari tahun sebelumnya.
3. **Hitung** (per pegawai) atau **Hitung semua** di halaman Rekap. Satu tahun dikirim ke engine dalam satu panggilan, sehingga KB cukup dimuat sekali.
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
- Persen disimpan sebagai teks desimal, lalu dikonversi eksak (`app/Support/Desimal.php`).
- Setiap bulan dalam masa kerja wajib berisi hari kerja dan hadir, dan hadir tidak boleh melebihi hari kerja.
- Kenaikan gaji di tengah bulan wajib dipecah ke hari sebelum/sesudah, dengan jumlah yang sama dengan hari bulan itu. Tanpa aturan ini, gaji bulan tersebut akan menjadi 0 diam-diam.

## Tes

```powershell
php artisan test                       # semua tes (integrasi engine dilewati bila venv induk tidak ada)
php vendor/bin/phpunit --group mesin   # hanya integrasi nyata dengan engine Python
```

`tests/Feature/IntegrasiMesinTest.php` memeriksa jaminan utama aplikasi ini. Untuk kesembilan pegawai contoh, kasus yang disusun dari database **identik** dengan kasus di dataset. Hasil hitung lewat web juga sama persis dengan engine yang dipanggil langsung (Karyawan A 2023: PPh 21 setahun Rp7.341.750, cek silang identik). Tes lainnya memakai engine palsu (`Process::fake`). Di sisi Python, protokol jembatan diuji di `tests/test_jembatan.py` induk.

## Struktur

| Lokasi | Isi |
|---|---|
| `app/Payroll/MesinPajak.php` | Klien jembatan: menjalankan `python -m jembatan` di repositori induk |
| `app/Payroll/PenyusunKasus.php` | Database → kasus kanonik `data_hr` (padanan `ui/kalkulator.py::form_hr`) |
| `app/Payroll/Penghitung.php` | Hitung satu/banyak pegawai dalam satu panggilan, catat riwayat, deteksi data berubah |
| `app/Payroll/TampilanHasil.php` | Menata keluaran engine untuk slip / 1721-A1 / jejak (padanan `ui/hasil.py`) |
| `app/Payroll/ImporContoh.php` | Kasus kanonik → database (pegawai contoh dari dataset) |
| `app/Http/Requests/PayrollTahunRequest.php` | Validasi data HR tahunan |
| `database/migrations/` | `pegawai`, `payroll_tahun`, `payroll_bulan`, `perhitungan` |

## Batasan

- Lapisan perusahaan tetap **Perusahaan X** (`kb/perusahaan/perusahaan_x.yaml`), karena isian data HR mengikuti struktur kebijakan itu. Perusahaan lain perlu berkas KB sendiri, dan formnya perlu disesuaikan.
- Tahun pajak yang dibuka adalah 2023–2026, rentang yang sudah diuji E12. Gross-up 2023 (rezim PER-16) di luar model engine dan akan ditolak dengan pesan jelas.
- Mode "komponen gaji sudah jadi" (contoh resmi regulasi) tetap ada di demo Streamlit induk, tidak di aplikasi ini.
- Perhitungan berjalan sinkron di request. Untuk ratusan pegawai, pindahkan "Hitung semua" ke queue Laravel.
- Prototipe penelitian, bukan alat konsultasi pajak resmi. Default tafsir belum dikalibrasi ke kalkulator DJP (README induk §6).
