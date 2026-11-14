# Setup

Panduan memasang dan menjalankan sistem penelitian KB PPh 21 di komputer baru. Diuji di Windows 11 dengan Python 3.12.4,
Docker Desktop 27.0.3 (Compose v2.28), dan Tesseract 5.5.0.

## Apa saja yang ada di repositori

| Bagian | Folder | Dipakai untuk |
|---|---|---|
| Sistem penelitian | `system/` (`pph21kbs/`, `tools/`, `ontology/`, `tests/`) | KB bitemporal dua lapis, *engine*, alur akuisisi LLM, eksperimen E0–E5 |
| Aplikasi | `system/app/` | Kalkulator, penampil KB, manajemen KB dengan AI, asisten |
| Demo | `mini_demo/mockup/` | Aplikasi yang sama dengan keadaan awal tetap dan tombol reset |
| Sistem awal | `ui/`, `web/`, `engine/`, `kb/` | Versi pertama sebelum penelitian (dijelaskan di [README.md](README.md)); tidak dipakai sistem penelitian |

## 1. Prasyarat

| Kebutuhan | Wajib? | Keterangan |
|---|---|---|
| Python 3.12 | wajib | Diuji 3.12.4. Cek `python --version` atau `py -3.12 --version` |
| Ruang disk | wajib | Beberapa GB: paket Python termasuk torch dan transformers (dipakai Docling), ditambah model Docling yang diunduh saat pertama dipakai |
| Internet | wajib | Saat instalasi paket, saat Docling pertama kali membaca PDF (unduh model), dan untuk panggilan API |
| Docker Desktop | wajib untuk GraphDB | Menjalankan GraphDB Free 11.5.1 (`graphdb/docker-compose.yml`). Docker Desktop harus sudah berjalan |
| Kunci API Anthropic dan OpenAI | wajib untuk bagian AI | Kalkulator, penampil, dan tes tetap jalan tanpa kunci; akuisisi, perbaikan, dan asisten tidak |
| Lisensi GraphDB Free | wajib untuk GraphDB | Gratis dari halaman GraphDB di graphwise.ai; dikirim lewat email sebagai kode base64 |
| Tesseract OCR + bahasa Indonesia | opsional | Untuk OCR PDF hasil pindai. Tanpa Tesseract, Docling memakai RapidOCR yang lebih lemah untuk teks Indonesia |
| Git | disarankan | Riwayat versi; beberapa alat mencatat *commit* yang dipakai |

## 2. Paket Python

Dari folder repositori, di PowerShell:

```
py -3.12 -m venv env
env\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

- `requirements.txt` berisi dependensi langsung dengan versi yang dipin.
- `requirements-lock.txt` berisi versi persis seluruh paket dari lingkungan yang sudah diuji. Pakai ini bila ingin
  lingkungan identik: `python -m pip install -r requirements-lock.txt`.
- `requirements-ekstraksi.txt` opsional, hanya untuk mengekstraksi ulang teks PDF regulasi. Hasilnya sudah tersimpan
  di `dataset/`.

## 3. Kunci API dan lisensi (`.env`)

Salin `.env.example` menjadi `.env` di root, lalu isi nilainya. `.env` tidak pernah di-*commit* dan dibaca langsung oleh
`system/pph21kbs/config.py` (tidak perlu di-*export*).

| Variabel | Isi |
|---|---|
| `CLAUDE_API_KEY` (atau `ANTHROPIC_API_KEY`) | Kunci Anthropic: model utama `claude-opus-5-5` |
| `OPENAI_API_KEY` | Kunci OpenAI: model kedua penelitian `gpt-6.1-sol` dan asisten aplikasi `gpt-5.4-mini` |
| `GRAPHDB_LICENSE` | Kode lisensi GraphDB Free (base64, satu baris) |
| `PPH21_GRAPHDB_URL`, `PPH21_GRAPHDB_REPOSITORY`, `PPH21_SECOND_MODEL` | Opsional; bawaan `http://localhost:7200`, `pph21`, `gpt-6.1-sol` |

Batas biaya API per penyedia ada di `config.BUDGET_USD`. Semua panggilan, termasuk dari aplikasi, dicatat di
`experiments/*/calls.jsonl` dan dihentikan bila batasnya tercapai.

## 4. GraphDB (Docker)

1. Jalankan Docker Desktop.
2. Pastikan `GRAPHDB_LICENSE` sudah ada di `.env`.
3. Jalankan:

   ```
   env\Scripts\python system\tools\graphdb_setup.py
   ```

   Skrip ini menulis lisensi ke `graphdb/graphdb.license`, menyalakan container `pph21-graphdb`, dan membuat
   *repository* `pph21` dengan validasi SHACL. Aman dijalankan ulang; nilai lisensi tidak pernah dicetak.
4. Workbench dan *endpoint* SPARQL ada di http://localhost:7200.

Untuk menyalakan atau mematikan container lagi: `docker compose -f graphdb/docker-compose.yml up -d` atau `... down`.
Data *repository* ada di `graphdb/home/` (tidak di-*commit*) dan bisa dibangun ulang dari KB.

## 5. Tesseract (opsional)

1. Pasang Tesseract untuk Windows (installer UB Mannheim) ke folder bawaan `C:\Program Files\Tesseract-OCR`.
2. Saat instalasi, centang bahasa **Indonesian** pada *Additional language data*. Bisa juga dengan menyalin
   `ind.traineddata` ke folder `tessdata`.
3. Cek: `"C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs` harus memuat `ind`.

Sistem mencari `tesseract` di PATH, lalu di folder bawaan itu (`system/pph21kbs/pdf_extract.py`).

## 6. Cek semuanya

```
env\Scripts\python system\tools\check_setup.py
```

Yang diperiksa: paket, kunci dan model Anthropic/OpenAI, GraphDB, dan Tesseract (Tesseract dan model asisten hanya
memberi peringatan). Pemeriksa ini hanya mendaftar model, jadi tidak memakai kredit. Hasil yang diharapkan:
`5/5 checks passed`.

## 7. Menjalankan

| Apa | Perintah | Buka |
|---|---|---|
| Aplikasi (KB emas lengkap) | `env\Scripts\streamlit run system\app\main.py` | http://localhost:8501 |
| Demo (keadaan awal tetap, reset) | `env\Scripts\streamlit run mini_demo\mockup\main.py --server.port 8503` | http://localhost:8503 |
| Sistem awal | `env\Scripts\streamlit run ui\app.py` | lihat [README.md](README.md) |

Halaman, fitur AI, dan biayanya dijelaskan di [system/app/README.md](system/app/README.md) dan
[mini_demo/mockup/README.md](mini_demo/mockup/README.md). Alat sistem penelitian (membangun KB emas, ruang uji,
eksperimen) ada di [system/README.md](system/README.md), dan langkah penelitian di
[PANDUAN_PENELITIAN.md](PANDUAN_PENELITIAN.md).

## 8. Tes

| Perintah | Isi | Waktu |
|---|---|---|
| `env\Scripts\python -m pytest system\tests -q` | Tes sistem penelitian. `test_impact.py` membandingkan dengan GraphDB dan dilewati bila GraphDB tidak berjalan | ± 2 menit |
| `env\Scripts\python -m pytest -q` | Tes sistem awal (`tests/`) | |

## 9. Masalah umum

| Gejala | Penyebab dan solusi |
|---|---|
| `GraphDB: not reachable` | Docker Desktop belum berjalan, atau container mati: jalankan `docker compose -f graphdb/docker-compose.yml up -d` |
| `GraphDB license: missing` | `GRAPHDB_LICENSE` belum ada di `.env`; isi lalu jalankan `graphdb_setup.py` |
| Membaca PDF pertama kali sangat lama | Docling mengunduh modelnya sekali; berikutnya sekitar 5 detik per halaman |
| `OCR: Tesseract ... not found` | Tesseract belum terpasang atau bahasa `ind` belum ada (bagian 5). Sistem tetap jalan dengan RapidOCR |
| Port sudah dipakai | Tambahkan `--server.port 8504` (atau port lain) |
| AI di aplikasi tidak bisa dijalankan | Kunci tidak ada, atau batas biaya aplikasi/penyedia tercapai; pesannya muncul di halaman |
