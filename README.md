# KB PPh 21: Kalkulator Payroll PPh Pasal 21 Berbasis Knowledge Base Dua Lapis

Kalkulator gaji, BPJS, THR, dan PPh 21 untuk pegawai tetap. Cakupan tahun pajaknya 2016–2026: rezim disetahunkan PER-16 sampai 2023, lalu rezim TER (PMK 168/2023) ditambah fasilitas DTP 2025–2026.

- **Pengetahuan ada di knowledge base.** Semua aturan pajak pemerintah dan kebijakan perusahaan disimpan di berkas YAML/CSV di `kb/` dan `dataset/01_regulasi/tables/`. Kodenya hanya **mesin inferensi** generik.
- **Dua lapisan.** Kebijakan perusahaan berada di lapisan terpisah. Konflik dengan aturan wajib terdeteksi otomatis, dan aturan pemerintah yang menang (*lex superior*).
- **Pembanding tanpa KB.** Tersedia kalkulator payroll "biasa" yang aturannya ditanam di kode (`baselines/`), dan hasilnya harus identik dengan versi KB.
- **Dua antarmuka.** Ada demo Streamlit (`ui/`) untuk riset dan presentasi, serta aplikasi web Laravel (`web/`) untuk admin finance. Keduanya memakai engine yang sama.
- **Aturan baru tanpa mengubah kode.** Peraturan baru masuk sebagai berkas KB tambahan, termasuk isian baru yang dimintanya dari pengguna. Rancangannya dapat disusun LLM dari PDF peraturan, lalu divalidasi engine dan disetujui manusia (§2.6).
- **Rancangan riset** ada di [research_plan.md](research_plan.md), dan riwayat pengerjaan bersama AI di [journal.md](journal.md).

---

## 1. Setup

### Prasyarat

| Kebutuhan | Keterangan |
|---|---|
| **Python 3.12** | Diuji dengan Python 3.12.4. Cek dengan `python --version`; di Windows bisa juga `py -3.12 --version` |
| Koneksi internet | Hanya saat instalasi paket pertama kali (±500 MB, terutama Streamlit, pandas, pyarrow) |
| Git | Opsional. Dipakai untuk mencatat versi KB (commit) di metadata audit; tanpa git, versi KB tertulis `tidak-diketahui` (akhiran `+belum-dikomit` = ada perubahan di `kb/` atau `engine/` yang belum di-commit) |
| Sistem operasi | Diuji di Windows 11 (PowerShell). Perintah untuk macOS/Linux disertakan |

### Langkah instalasi (Windows PowerShell)

Jalankan dari folder project (`kb_payroll`):

```powershell
# 1. buat lingkungan virtual bernama env (sekali saja)
python -m venv env            # atau: py -3.12 -m venv env

# 2. aktifkan (setiap membuka terminal baru)
env\Scripts\Activate.ps1      # Command Prompt: env\Scripts\activate.bat

# 3. pasang paket
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Kalau langkah 2 memunculkan *"running scripts is disabled on this system"*, jalankan sekali perintah berikut, lalu ulangi langkah 2:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**macOS / Linux:**

```bash
python3.12 -m venv env
source env/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Berkas requirements

| Berkas | Isi | Kapan dipakai |
|---|---|---|
| `requirements.txt` | Dependensi langsung, versinya dipin: PyYAML, jsonschema, pytest, hypothesis, streamlit, plotly, pandas, openpyxl, openai dan anthropic (hanya untuk asisten KB, §2.6) | **Default**, cukup untuk menjalankan kalkulator, UI, tes, dan eksperimen |
| `requirements-lock.txt` | Versi persis seluruh paket, termasuk dependensi turunan, dari lingkungan yang sudah diuji | Bila ingin lingkungan yang identik byte-per-byte |
| `requirements-ekstraksi.txt` | pdfplumber, pypdf, pypdfium2 | Opsional; hanya untuk mengekstraksi ulang teks/tabel dari PDF regulasi. Hasil ekstraksinya sudah tersimpan di `dataset/` |

### Cek instalasi

```powershell
python -m engine.cli dataset\07_kasus_uji_resmi\kanonik\PMK168-B-I.1.json
```

Baris `pph21_setahun` harus menunjukkan **64.715.000**, sama dengan contoh di Lampiran PMK 168/2023 B-I.1. Untuk pengujian lengkap:

```powershell
python -m pytest -q
```

Hasil yang diharapkan: semua tes lulus, dan 8 dilewati (*skipped*: gross-up rezim 2023, yang memang di luar model). Waktunya beberapa menit, karena tes UI menelusuri semua data di kedua kalkulator.

### Berkas yang sengaja tidak ada di repositori

| Berkas | Alasan | Apakah dibutuhkan? |
|---|---|---|
| `payroll_calculator.xlsx` | Spreadsheet kantor yang memuat data pribadi; diabaikan git dan **tidak boleh dipublikasikan** | Tidak. Data Karyawan A yang dianonimkan sudah diekstrak ke `dataset/02_studi_kasus/` |
| `dataset/03_pembanding/repos/` | Clone repo pembanding pihak ketiga; salah satunya tidak berlisensi sehingga tidak boleh didistribusikan | Tidak. Daftar URL-nya ada di `dataset/03_pembanding/kandidat_repo.csv` bila ingin di-clone ulang |
| `env/` | Lingkungan virtual lokal | Dibuat lewat langkah instalasi di atas |

---

## 2. Menjalankan

Semua perintah di bawah dijalankan dari folder project dengan venv **aktif**. Tanpa mengaktifkan venv, ganti `python` dengan `env\Scripts\python.exe` dan `streamlit` dengan `env\Scripts\streamlit.exe`.

### 2.1 Aplikasi demo (UI)

```powershell
streamlit run ui\app.py
```

Buka **http://localhost:8501** (biasanya terbuka otomatis). Tekan **Ctrl + C** di terminal untuk menghentikan. Port lain: `streamlit run ui\app.py --server.port 8502`. Tema dan ukuran huruf untuk proyektor diatur di `.streamlit/config.toml`. Untuk presentasi, tekan **F11** (layar penuh) dan atur zoom dengan **Ctrl + / Ctrl −**.

**Tab Kalkulator** punya dua sub-tab dengan tampilan identik dan mekanisme berbeda:

| Sub-tab | Mekanisme | Kolom "Dasar" per angka menunjuk ke |
|---|---|---|
| **Dengan KB** | Engine membaca aturan regulasi dan kebijakan Perusahaan X dari berkas KB; konflik kebijakan terdeteksi | aturan dan pasalnya |
| **Tanpa KB** | Kalkulator payroll biasa: kebijakan Perusahaan X ditanam di `baselines/b2_payroll_hardcoded/`, pajaknya oleh `baselines/b1_hardcoded/` | fungsi dan baris kodenya |

- **Panel kiri: isian admin finance.** Defaultnya diambil dari dataset:
  - Karyawan A dari xlsx kantor (dianonimkan);
  - 8 pegawai sintetis berbasis UMP Kemnaker dan upah BPS;
  - 45 contoh resmi regulasi dalam mode "komponen gaji sudah jadi".

  Edit hanya tersimpan di layar dan tidak pernah menulis ke dataset. Tidak ada konfigurasi sistem di layar: tafsir, versi KB, dan kategori pajak tidak bisa dipilih.
- **Panel kanan: hasil.**
  - Cek silang dengan kalkulator satunya.
  - Pencocokan dengan contoh resmi, selama isian belum diubah.
  - Slip gaji per bulan sampai take home pay.
  - Perhitungan setahun gaya 1721-A1, termasuk rincian Pasal 17 per lapisan.
  - Tabel dan grafik 12 bulan.
  - Penjelasan cara mesin menghitung.

**Tab Knowledge Base** berisi:
- alur perhitungan;
- kartu per topik untuk aturan pemerintah dan kebijakan Perusahaan X, dengan penjelasan, nilai yang berlaku per tahun, dan pasal;
- tabel konflik klasifikasi komponen;
- katalog kebijakan lain (KP-xx);
- bukti kebenaran (V1 dan E12);
- rincian teknis aturan.

Demo ini dibekukan sebagai peraga inti yang terverifikasi: ia hanya memuat KB dasar (regulasi + Perusahaan X). Berkas KB tambahan dan isian baru yang dimintanya (§2.6) hanya tersedia di aplikasi web. Memuatnya di demo akan menyesatkan: kalkulator pembanding tanpa KB tidak mengenal aturan tambahan, sehingga lencana "identik sampai rupiah" tetap muncul walau hasilnya berbeda.

### 2.2 Baris perintah (CLI)

```powershell
python -m engine.cli dataset\07_kasus_uji_resmi\kanonik\PMK168-B-I.1.json --jejak          # + jejak aturan & pasal
python -m engine.cli kasus.json --perusahaan kb\perusahaan\perusahaan_x.yaml --rentang     # + lapisan perusahaan & rentang tafsir
python -m engine.cli kasus.json --varian REG-BJ-02=b --json > hasil.json                   # varian tafsir, keluaran JSON
```

### 2.3 API Python

```python
from datetime import date
from engine.kalkulator import hitung
h = hitung(kasus)                                    # KB terbaru, varian tafsir default
h = hitung(kasus, dengan_rentang=True)               # + rentang tafsir (AMBIGU_TAFSIR)
h = hitung(kasus, berkas_perusahaan=["kb/perusahaan/perusahaan_x.yaml"])
h = hitung(kasus, per_tanggal_kb=date(2025, 1, 31))  # KB sebagaimana diketahui pada tanggal itu (bitemporal)

from baselines.b2_payroll_hardcoded.payroll_b2 import hitung as hitung_tanpa_kb
h2 = hitung_tanpa_kb(kasus)                          # kalkulator tanpa KB (format keluaran sama)
```

Keluaran (`dict`):
- `per_masa` dan `tahunan`: semua nilai uang berupa `int` rupiah; tarif berupa string pecahan, mis. `"3/200"`.
- `jejak`: aturan, pasal sumber, serta aturan yang ditolak beserta alasannya.
- `peringatan`: `KONFLIK_WAJIB`, `GROSSUP_GANDA`, `AMBIGU_TAFSIR`, `KLASIFIKASI_TIDAK_DIATUR`, `TRANSAKSI_TAHUN_LAIN`.
- `rincian_pasal17`: pajak per lapisan tarif.
- `rentang_tafsir`: opsional.

### 2.4 Tes dan eksperimen

| Perintah | Isi |
|---|---|
| `python -m pytest -q` | Seluruh tes: kontrak presisi, V1–V3, double-entry, E3–E8, E12, UI |
| `python -m pytest tests\test_ui.py -q` | Tes UI saja (AppTest Streamlit) |
| `python -m eksperimen.v1 kb` | V1: kalkulator KB vs 45 contoh resmi (`b1` untuk baseline B1) |
| `python -m eksperimen.v2` | V2: differential KB vs B1 pada kasus sintetis |
| `python -m eksperimen.e12_tanpa_kb` | E12: kalkulator dengan KB vs tanpa KB |
| `python -m eksperimen.e8_perusahaan_x` | E8: Perusahaan X vs xlsx (`--tahun 2024` untuk rezim TER) |
| `python -m eksperimen.perubahan` | E3: skenario perubahan aturan |
| `python -m eksperimen.ablasi` / `grossup` / `konflik` / `ekspresivitas` | E5 / E6 / E4b / E7 |
| `python -m eksperimen.mutasi` | E4: mutation testing (±15 menit) |
| `python dataset\08_pegawai_sintetis\bangkitkan.py` | Bangkitkan ulang data pegawai sintetis dari data publik |

### 2.5 Aplikasi web (Laravel)

`web/` berisi aplikasi Laravel multi-pengguna untuk admin finance. Isinya data pegawai, data HR per tahun pajak, proses payroll (per pegawai atau satu tahun sekaligus), slip gaji, perhitungan setahun gaya 1721-A1, rekap, dan riwayat perhitungan.

Aplikasi ini **tidak menghitung pajak sendiri**. Ia menyusun kasus kanonik dari database, lalu memanggil engine lewat jembatan JSON:

```powershell
'{"perintah": "info"}' | python -m jembatan      # satu permintaan JSON di stdin, satu jawaban JSON di stdout
```

Aplikasi web tidak menyalin rumus dari `engine/` atau `kb/`, jadi angkanya mewarisi bukti verifikasi di §5. Untuk 9 pegawai contoh, kasus yang disusun dari database identik dengan dataset, dan cek silang E12 identik. Setup dan cara pakai ada di [web/README.md](web/README.md).

### 2.6 Aturan baru tanpa mengubah kode: berkas KB tambahan dan asisten KB

Peraturan baru (pemerintah atau perusahaan) masuk sebagai **berkas KB tambahan**, bukan sebagai perubahan rumus. Satu berkas (format `kb/skema/aturan.schema.json`) dapat berisi:

| Bagian | Fungsi |
|---|---|
| `aturan` | Aturan baru, atau pengganti aturan lama untuk fakta yang sama (lihat *Mengganti aturan* di bawah) |
| `komponen` | Komponen gaji baru beserta kategori pajak dan labelnya (hanya lapisan perusahaan). Bruto, PPh 21, dan take home pay menjumlahkan komponen per kategori, sehingga komponen baru langsung ikut dihitung |
| `masukan` | **Isian baru yang diminta dari pengguna** (kunci, label, tipe, lingkup tahun/bulan, wajib, bawaan). Dibaca aturan lewat `hr('kunci')` / `hr_masa('kunci')`; aplikasi web membangun form-nya dari deklarasi ini |
| `parameter` | Amandemen nilai berversi (mis. batas upah JP): versi baru menutup versi lama sehari sebelum `mulai`; amandemen sementara (`sampai` terisi) mengembalikan nilai lama mulai `sampai` + 1 hari |
| `klasifikasi_wajib` | Kategori wajib suatu jenis komponen (hanya lapisan regulasi), berversi dengan semantik yang sama seperti `parameter` |
| `pembulatan` | Entri registri pembulatan |

Kategori komponen: `teratur`, `tidak_teratur`, `premi_objek`, `natura`, `iuran_pengurang`, `zakat`, `bukan_objek`, `tidak_diperhitungkan`. Take home pay Perusahaan X (`px_thp`) = penghasilan tunai (teratur + tidak teratur) + tunjangan pajak − iuran pengurang − zakat − **semua komponen `tidak_diperhitungkan`** − PPh 21 + PPh 21 DTP. Jadi `tidak_diperhitungkan` berarti potongan dari pegawai tanpa efek pajak (iuran BPJS Kesehatan pegawai, cicilan koperasi, ...): mengurangi take home pay tanpa mengubah bruto atau PPh 21.

**Mengganti aturan.** Bila beberapa aturan untuk fakta yang sama menyala bersamaan, urutannya: aturan regulasi `wajib` mengalahkan perusahaan (lex superior); aturan perusahaan mengalahkan regulasi `default`/`opsional`; lalu **lex specialis** (lebih banyak konjungsi `and` di `jika` menang) **sebelum** lex posterior (`mulai` lebih baru menang); terakhir `prioritas`. Aturan pengganti karena itu perlu `mulai` lebih baru **dan** `jika` dengan konjungsi paling sedikit sama banyak dengan aturan lama; aturan tanpa `jika` tidak dapat mengganti aturan ber-`jika`. Pengganti aturan titik tetap gross-up (`tunjangan_pajak_berjalan`, `tunjangan_pajak_akhir`) wajib bertanda `titik_tetap: true` dengan `batas_titik_tetap`: batas iterasi diambil dari aturan yang menang resolusi konflik, dan pengganti tanpa tanda itu ditolak saat pegawai gross-up dihitung.

**Urutan berkas tidak menentukan hasil.** Amandemen `parameter` dan `klasifikasi_wajib` dari semua berkas tambahan dikumpulkan dulu, lalu diterapkan per nama menurut tanggal `mulai` (research_plan §6.4: masa berlaku yang menentukan, bukan urutan penerapan). Versi baru menutup versi lama sehari sebelum `mulai`-nya. Amandemen sementara mengembalikan nilai lama mulai `sampai` + 1 hari dan boleh langsung disusul versi baru yang mulai tepat pada hari itu. Amandemen yang berlaku surut terhadap berkas tambahan lain dapat dimuat. Himpunan berkas yang sama selalu memberi KB yang sama, atau selalu ditolak, apa pun urutan penerapannya.

**Yang ditolak saat memuat** (`KesalahanKB`, di jembatan jenis `kesalahan_kb`):

- Komponen (`fakta`) yang sudah dideklarasikan, di KB dasar maupun berkas lain (mis. `px_lembur`). Kategori komponen yang ada tidak dapat diubah lewat deklarasi ulang; perlakuan pajaknya diubah lewat `klasifikasi_wajib` di berkas lapisan regulasi. Id aturan ganda juga ditolak; pesannya menyebut kedua berkas.
- Deklarasi ulang `masukan` yang `tipe`, `lingkup`, `wajib`, `bawaan`, atau `pilihan`-nya berbeda (yang identik boleh; deklarasi pertama dipakai). `kunci` paling panjang 64 karakter. Nilai bertipe `rupiah` tidak boleh negatif (bawaan maupun data HR); `bilangan` boleh.
- Aturan berlingkup `tahun` yang memanggil `hr_masa()`: pakai `hr('kunci')`, atau hitung fakta berlingkup masa lalu jumlahkan dengan `jumlah_masa()`.
- Amandemen `parameter`: `sampai` sebelum `mulai`; jenis nilai berbeda dari versi yang ada (rupiah ditulis bilangan bulat tanpa pemisah ribuan, mis. `11500000`; tarif sebagai teks desimal, mis. `"0.3"`); dua amandemen untuk parameter yang sama dengan `mulai` yang sama; versi yang ditulis KB dasar atau berkas lain mulai di dalam rentang [`mulai`, `sampai`] (*bentrok*; pesannya menyebut berkas lawan), mis. versi permanen yang mulai di tengah amandemen sementara padahal sesudah amandemen itu nilai lama berlaku lagi. Satu nama parameter dimiliki satu lapisan: parameter yang ada di `parameter.yaml` atau ditulis berkas lapisan regulasi mana pun tidak boleh diubah lapisan perusahaan; parameter buatan lapisan perusahaan boleh diamandemen lapisan perusahaan.
- `klasifikasi_wajib`: aturan versi dan bentroknya sama dengan parameter; `kategori` di luar delapan kategori di atas. `komponen` di berkas lapisan regulasi (pesannya menunjuk jalan keluar: tarif dan `klasifikasi_wajib` di berkas regulasi, komponen dan aturannya di berkas perusahaan terpisah).
- DSL: kategori literal tak dikenal di `komponen()`/`komponen_kode()`/`komponen_valas()` (sah: delapan kategori + `rapel`), `parameter('x')` yang tidak ada di KB, `bulatkan('ID', ...)` yang tidak terdaftar, jumlah argumen fungsi yang salah, dan ekspresi yang terlalu panjang atau terlalu dalam.
- Anchor/alias YAML (`&nama` / `*nama`) di berkas KB mana pun.

Saat menghitung, aritmetika (`+ - * /`, minus tunggal) hanya menerima angka: masukan bertipe persen, desimal, atau tanggal wajib dikonversi dulu dengan `persen()`, `desimal()`, atau `tanggal()`; selain itu `PelanggaranPresisi` (di jembatan `data_tidak_sesuai`).

Tabel terverifikasi (TER, tarif Pasal 17, PTKP, KLU DTP) **tidak** dapat diubah lewat berkas tambahan; jalurnya tetap double-entry + `tabel_manifest.yaml`.

`asisten_kb/` menyusun **rancangan** berkas itu dari PDF peraturan (maks. 20 MB) dengan LLM (keluaran terstruktur). Model bawaannya `gpt-5.6-sol` lewat OpenAI Responses API (`OPENAI_API_KEY`); model `claude-...` memakai Anthropic (`ANTHROPIC_API_KEY`). Paket ini sengaja di luar `engine/`: engine tetap bebas LLM (research_plan §4.3), dan LLM tidak pernah menghitung pajak. Lapisan berkas selalu mengikuti pilihan unggah; bila LLM menilai lain, pilihannya disimpan di `usulan.lapisan_llm` dan dicatat di `catatan_peninjau`. Rupiah berpemisah ribuan di rancangan (`500.000`, `1,500,000`) diubah menjadi bilangan bulat; bentuk lain dibiarkan agar ditolak engine. Rancangan baru berlaku setelah dua gerbang:

1. **Validasi engine** (`asisten_kb/rancangan.py`, tidak pernah melempar galat; galat Python tak terduga muncul sebagai `galat` beserta jenis dan id aturannya): skema, verifikasi statis KB, kewajiban mendeklarasikan setiap isian baru, dan simulasi sebelum/sesudah pada dua pegawai contoh (Karyawan A setahun penuh dan pegawai masuk 1 Juli). Tahun simulasi diturunkan dari rancangan: tiap entri dari max(2023, tahun mulai) s.d. min(2030, max(2026, tahun mulai + 1)) dalam masa berlakunya, ditambah tahun sesudah `sampai` (s.d. 2031), paling banyak 8 tahun. Hasilnya juga memuat `perubahan` (aturan, parameter, dan klasifikasi yang sudah ada yang diubah rancangan) dan `belum_teruji` (aturan rancangan yang tidak pernah terpilih di simulasi, beserta alasannya). Flag `wajib` isian adalah perilaku engine yang efektif: isian tanpa `bawaan` dan tanpa nilai bawaan di aturan (`hr_masa('k', 0)`) tetap wajib walau dideklarasikan `wajib: false`. Simulasi juga menghitung Karyawan A dengan metode gross-up di tahun yang didukung KB dasar (2024 ke atas): hasilnya tidak masuk tabel dampak, tetapi galatnya menggagalkan validasi dan jejaknya ikut dihitung sebagai cakupan uji (aturan titik tetap tidak pernah menyala pada pegawai bermetode gross). Peringatan yang tidak menggagalkan: fakta rupiah baru yang bukan komponen dan tidak dibaca aturan mana pun ("tidak ikut bruto, PPh 21, maupun take home pay"), dan isian yang punya `bawaan` (pegawai yang belum diisi dihitung dengan bawaan; `wajib: true` + `bawaan` bertentangan).
2. **Persetujuan manusia** di aplikasi web (menu Basis pengetahuan), dengan kutipan dan halaman PDF untuk tiap aturan.

```powershell
# validasi rancangan tanpa LLM; berkas_tambahan = berkas yang sudah aktif (harus di bawah kb/tambahan/); "lapisan" opsional
'{"perintah": "validasi", "yaml": "...", "lapisan": "perusahaan", "berkas_tambahan": []}' | python -m jembatan
# PDF -> rancangan (butuh OPENAI_API_KEY; "model" opsional, bawaan gpt-5.6-sol)
'{"perintah": "usulkan", "pdf": "C:\\dok\\peraturan.pdf", "lapisan": "perusahaan"}' | python -m jembatan
# KB dasar + berkas tambahan dapat dimuat dan menghitung Karyawan A 2023-2027? -> {"periksa": {"ok", "galat", "tahun"}}
'{"perintah": "periksa", "berkas_tambahan": ["kb/tambahan/0001_x.yaml"]}' | python -m jembatan
```

`periksa` mengisi nilai contoh untuk setiap isian tambahan dan menghitung Karyawan A dengan metode gross serta, di tahun yang didukung KB dasar (2024 ke atas), gross-up; aplikasi web memakainya sebelum menonaktifkan berkas dan di halaman Mesin.

Yang sudah diuji: konversi dan validasi rancangan, isian baru, amandemen parameter, aturan penolakan di atas (`tests/test_kb_tambahan.py`), serta alur web dari ujung ke ujung dengan engine sungguhan (`tests/test_asisten_kb.py`, `tests/test_masukan_kb.py`, `web/tests/`). Tes memakai klien LLM tiruan. **Mutu ekstraksi LLM terhadap dokumen nyata belum dievaluasi**, jadi tinjauan manusia adalah bagian wajib dari alur, bukan formalitas.

---

## 3. Format input (kasus kanonik)

Contoh lengkap ada di `dataset/07_kasus_uji_resmi/kanonik/*.json` (komponen sudah jadi) dan `dataset/08_pegawai_sintetis/pegawai_sintetis.json` (data HR). Ringkasnya:

```json
{"id": "...", "tahun_pajak": 2024, "cakupan": "setahun", "metode": "gross|gross_up|ditanggung_pemberi_kerja",
 "pegawai": {"status_ptkp": "K/1", "jenis_kelamin": "L", "punya_npwp": true, "bulan_masuk": null,
             "bulan_terakhir_bekerja": null, "subjektif_mulai_bulan": null, "subjektif_akhir_bulan": null,
             "periode_gaji": "bulanan", "hari_kerja_sebulan": null},
 "pemberi_kerja": {"klu": "13111", "jenis": "biasa"}, "kurs": {}, "dtp": {},
 "masa": [{"bulan": 1, "komponen": [{"kode": "gaji", "kategori": "teratur", "satuan_periode": "bulan", "nominal": 10000000}]}],
 "transaksi": [{"komponen": "thr", "kategori": "tidak_teratur", "nominal": 10000000, "periode_kerja": "2024-04",
                "tanggal_terutang": "2024-04-10", "tanggal_bayar": "2024-03-28"}],
 "data_hr": {"...": "input mentah untuk lapisan perusahaan"}}
```

- Kategori komponen: `teratur`, `tidak_teratur`, `premi_objek`, `natura`, `iuran_pengurang`, `zakat`, `rapel`.
- Nominal wajib `int ≥ 0`. Float dan pecahan **ditolak** (`InputTidakValid`).

## 4. Struktur

| Folder | Isi |
|---|---|
| `engine/` | `ekspresi.py` (DSL aman), `kb.py` (pemuat + verifikasi statis), `inferensi.py` (graf, SCC, titik tetap Tarski, resolusi konflik, bitemporal), `kalkulator.py`, `cli.py`, kontrak presisi (`angka.py`, `pembulatan.py`, `interval.py`, `waktu.py`, `muat.py`, `audit.py`) |
| `kb/regulasi/` | `aturan_{umum,ter,per16,dtp}.yaml`, `klasifikasi.yaml`, `parameter.yaml`, `pembulatan.yaml`, `pencatatan.yaml`, `tabel_manifest.yaml` (hash SHA-256), `KODIFIKASI.md` |
| `kb/perusahaan/` | `perusahaan_x.yaml` (studi kasus), `katalog/` (kebijakan KP-xx) |
| `kb/tambahan/` | Berkas KB tambahan yang diterapkan lewat aplikasi web (data runtime, tidak ikut git; database aplikasi adalah sumber kebenarannya dan berkas aktif ditulis ulang dari sana; lihat §2.6) |
| `asisten_kb/` | PDF peraturan → rancangan berkas KB lewat LLM: `konteks.py` (prompt + inventaris KB), `skema.py` (keluaran terstruktur), `llm.py` (klien LLM: OpenAI bawaan, Anthropic opsional), `rancangan.py` (YAML + validasi + simulasi). Engine tidak mengimpor paket ini |
| `baselines/b1_hardcoded/` | Baseline B1: pajak hard-coded, independen dari KB (tag git `b1-frozen`) |
| `baselines/b2_payroll_hardcoded/` | Kalkulator payroll tanpa KB: kebijakan Perusahaan X di kode + B1 untuk pajak |
| `dataset/` | `01_regulasi` (PDF + tabel double-entry), `02_studi_kasus` (Perusahaan X), `03_pembanding`, `04_data_publik` (BPS, Kemnaker), `05_katalog_kebijakan`, `06_kasus_uji_sintetis`, `07_kasus_uji_resmi` (kanonik), `08_pegawai_sintetis` |
| `ui/` | Demo Streamlit: `app.py`, `kalkulator.py` (isian), `hasil.py` (slip & perhitungan setahun), `mesin.py` (adapter KB / tanpa KB), `tab_kb.py`, `data.py` (dataset, konversi isian, format eksak) |
| `eksperimen/` | `v1.py`, `v2.py`, `ablasi.py`, `mutasi.py`, `grossup.py`, `konflik.py`, `perubahan.py`, `ekspresivitas.py`, `e8_perusahaan_x.py`, `e12_tanpa_kb.py`, `adjudikasi.md`, `hasil/` |
| `tests/` | Kontrak presisi, V1, V2, V3 metamorfik, double-entry, E3–E8, E12, UI, jembatan |
| `jembatan/` | Protokol JSON stdin/stdout ke engine untuk aplikasi web (`python -m jembatan`): `hitung`, `contoh`, `info`, `masukan`, `usulkan`, `validasi`, `periksa`; tanpa pengetahuan pajak |
| `web/` | Aplikasi web Laravel (admin finance): pegawai, data HR, proses payroll, slip, rekap, basis pengetahuan. Lihat [web/README.md](web/README.md) |

## 5. Status verifikasi (2026-10-01)

| Uji | Hasil |
|---|---|
| V1: 45 kasus resmi kanonik, 1.213 harapan (PMK 168, PP 58, PER-16, PMK 10/72/105) | **0 selisih tak terjelaskan** (1.185 cocok, 20 erratum terkoreksi, 8 tafsir); KB dan B1 identik |
| V2: differential KB vs B1, 2.201 kasus sintetis | 0 galat; seluruh selisih teradjudikasi (titik tetap gross-up ganda, `eksperimen/adjudikasi.md`) |
| V3: relasi metamorfik MR1–MR15 + properti DTP dan PPh ditanggung | Lulus (Hypothesis) |
| Double-entry tabel dari gambar halaman PDF | 512 sel cocok 100%; dijalankan permanen sebagai tes |
| E4: mutation testing (52 mutan KB) | Skor 100% (1 sisa mutan diubah menjadi tafsir eksplisit R16-05-N) |
| E4b: deteksi konflik kebijakan (42 pemetaan berlabel) | Presisi = recall = F1 = 1,0 |
| E5: ablasi | Setiap fitur yang dimatikan menghasilkan contoh tandingan |
| E3: perubahan aturan (JP 2026, DTP surut, PTKP 2027, TER 2027) | 0 berkas engine berubah; impact F1 = 1,0; regresi 0 |
| E7: ekspresivitas | 17/19 entri katalog tanpa ubah kode |
| E8: Perusahaan X vs xlsx | 12 komponen payroll identik; selisih PPh hanya di temuan audit K-02/K-04/K-11 |
| E12: kalkulator dengan KB vs tanpa KB (Karyawan A 2023–2026, 8 pegawai sintetis, 36 variasi isian, 45 contoh resmi) | Identik sampai rupiah; satu-satunya selisih adalah titik tetap gross-up ganda yang dilaporkan KB (A-02) |
| E9: kinerja | ±38 ms per pegawai-tahun (gross-up dominan); ±8 ms dengan lapisan perusahaan |

## 6. Batasan yang diketahui

- **Default tafsir belum dikalibrasi ke kalkulator resmi DJP** (E10, manual). Ini mencakup pembulatan TER × bruto, bruto pecahan, biaya jabatan, proporsi n/12, PPh bulanan PER-16, pilihan titik tetap, dan R16-05-N. Rentang tafsir selalu dapat ditampilkan (`--rentang`).
- **Di luar model:**
  - gross-up rezim PER-16;
  - pindah cabang multi-pemotong;
  - penghasilan dari lebih dari satu pemberi kerja;
  - pegawai tidak tetap, bukan pegawai, dan pensiunan;
  - penilaian natura PMK 66 (nilainya diinput);
  - gross-up per komponen (KP-03) dan gross-up berplafon (KP-04).
- **Asisten KB (LLM) berada di luar inti terverifikasi.** Validasi engine memeriksa bentuk dan konsistensi rancangan, bukan kesesuaiannya dengan isi dokumen; itu tugas peninjau. Cek silang E12 dilewati untuk perhitungan yang memakai berkas KB tambahan, karena kalkulator pembanding tanpa KB tidak mengenal aturan baru. Simulasi validasi hanya memakai dua pegawai contoh turunan Karyawan A, jadi aturan yang tidak pernah terpilih di sana dilaporkan sebagai `belum_teruji`, bukan dibuktikan benar.
- **KLU DTP** berasal dari lapisan teks (status `ekstraksi_1`). Kode 96129 hanya ada di PMK 105 dan perlu dicek ke gambar halaman.
- **KLU Perusahaan X tidak diketahui** karena datanya dianonimkan. Akibatnya fasilitas DTP hanya terlihat pada contoh resmi PMK 10/72/105.

## 7. Masalah umum

| Gejala | Penyebab / solusi |
|---|---|
| `python` tidak dikenali, atau versinya bukan 3.12 | Pasang Python 3.12 dari python.org (centang *Add to PATH*), atau pakai `py -3.12 -m venv env` |
| `running scripts is disabled` saat aktivasi | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, atau aktifkan lewat Command Prompt: `env\Scripts\activate.bat` |
| `ModuleNotFoundError: No module named 'engine'` | Jalankan dari folder project (folder yang berisi `engine/`), dengan bentuk `python -m ...` |
| `streamlit` tidak dikenali | Venv belum aktif; aktifkan, atau pakai `env\Scripts\streamlit.exe run ui\app.py` |
| `Port 8501 is already in use` | Server lama masih jalan; hentikan dengan Ctrl + C di terminalnya, atau pakai `--server.port 8502` |
| Tampilan tidak berubah setelah kode diedit | Hentikan server (Ctrl + C), lalu jalankan lagi |
| `KesalahanKB: hash tabel '...' tidak cocok` | Tabel di `dataset/01_regulasi/tables/` berubah tanpa memperbarui `kb/regulasi/tabel_manifest.yaml`. Ini disengaja: tabel tidak boleh berubah diam-diam |
