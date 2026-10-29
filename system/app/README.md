# Aplikasi KBS PPh 21

Aplikasi di atas sistem penelitian: *knowledge base* emas (`dataset/12_emas`), *engine* `system/pph21kbs`, alur akuisisi
LLM, dan hasil eksperimen.

```
env\Scripts\streamlit run system\app\main.py
```

Lalu buka http://localhost:8501. Demo dengan keadaan awal tetap dan tombol reset menjalankan program yang sama dari
`mini_demo/mockup/main.py` (lihat README di sana).

## Dua mode, satu program

| | Sistem (`system/app/main.py`) | Demo (`mini_demo/mockup/main.py`) |
|---|---|---|
| KB awal | KB emas lengkap | KB emas sampai 27 Februari 2025 |
| Dokumen menunggu | dokumen yang diunggah | delapan dokumen penelitian dengan hasil AI tersimpan, ditambah unggahan |
| Ruang kerja | `system/app/workspace/` | `mini_demo/mockup/workspace/` |
| Reset | tidak ada (kembali ke versi lama lewat Riwayat versi) | ada |

Keduanya tidak di-*commit*. Pembaruan yang disetujui disimpan di `state.json` dan diterapkan di atas KB emas. KB emas
penelitian tidak pernah diubah.

## Halaman

- **Beranda:** ringkasan, alur sistem, menu, keadaan KB, dan langkah demo (mode demo saja).
- **Kalkulator PPh 21:**
  - satu pegawai, satu tabel per bulan, 16 skenario umum;
  - kolom data dibentuk dari aturan yang berlaku;
  - kartu hasil disusun dari jejak engine (`explain.py`);
  - hitung ulang setahun di bulan penutup.
- **Penampil knowledge base:**
  - *Isi KB:* topik dari graf, alur dari aturan yang berlaku, angka dari waktu ke waktu, riwayat, perbandingan tanggal,
    pencarian, data yang dibutuhkan, kebijakan perusahaan;
  - *Sistem knowledge base (teknis):* arsitektur, knowledge graph, RDF satu unsur, bitemporal, versi per named graph,
    jejak perhitungan, ontologi dan SHACL, SPARQL dan ekspor TriG.
- **Manajemen knowledge base:**
  - *Dokumen baru:* unggah PDF/TXT/JSON (PDF diekstrak dengan Docling dan OCR), lalu AI membaca dengan alur penelitian;
  - *Review:* pemeriksaan pada KB sekarang, gerbang G1–G5 penelitian, contoh sebelum/sesudah, dampak ke kebijakan
    perusahaan, setujui/sunting/perbaiki dengan AI/tolak;
  - tab *Tambah/ubah/cabut*, *Kebijakan perusahaan*, *Cek KB*, dan *Riwayat versi*.
- **Asisten AI:** jendela pop-up di semua halaman. Riwayat obrolan tersimpan dan bisa dihapus.
- **Hasil penelitian:** empat pertanyaan dalam bahasa biasa.

## AI dan biaya (`ai.py`)

| Bagian | Model | Biaya |
|---|---|---|
| Membaca dokumen unggahan | Claude (`claude-opus-5-5`), alur penelitian `run_document`: relevansi, 1 atau 3 versi usulan, G1–G5, satu putaran perbaikan, kesepakatan | ± USD 0,1–0,9 per dokumen |
| Minta AI perbaiki | Claude, satu putaran perbaikan penelitian (`prompts.repair_user`) dengan catatan reviewer, lalu G1–G5 | ± USD 0,3 (uji: USD 0,29) |
| Asisten | `gpt-5.4-mini` (bawaan) atau `gpt-6.1-sol`; atau tanpa AI | ± USD 0,002 per pertanyaan |

- **Asisten:**
  - menjawab dari konteks KB dan memilih paling banyak satu tindakan, yang dijalankan kode aplikasi (draf masuk Review);
  - tidak pernah menyetujui apa pun;
  - perbaikan yang memakai kredit Claude hanya diisikan ke Review; Anda yang menekan tombolnya;
  - nama pegawai tidak dikirim ke model.
- **Pencatatan biaya:**
  - setiap panggilan dicatat buku biaya penelitian di `experiments/app-*/calls.jsonl` (tidak di-*commit*);
  - batas total per penyedia di `config.BUDGET_USD` berlaku juga untuk aplikasi;
  - batas aplikasi per jenis pekerjaan ada di `ai.LIMITS`: akuisisi USD 4, perbaikan USD 1,5, asisten USD 1.
- **Di mode demo:** dokumen penelitian tetap memakai hasil AI tersimpan. Untuk dokumen itu, perbaikan bisa memakai AI
  sungguhan atau jawaban acuan penelitian (simulasi, gratis, diberi label).
- **Hasil perbaikan oleh reviewer** dicatat terpisah dan tidak termasuk hasil penelitian.

## Yang belum

- **Definisi data input** (label, penjelasan, pilihan) ada di `kb_ext/`, belum menjadi unsur KB.
- **Dokumen draf** dari formulir atau asisten tidak terdaftar, jadi gerbang G1 menolaknya sampai dokumennya diunggah.
- **Penyimpanan:** berkas JSON per ruang kerja, tanpa login dan tanpa banyak pengguna.
- **Fitur aplikasi lama yang belum dipindahkan** (masih ada di riwayat git):
  - payroll massal dari CSV;
  - putar ulang hasil AI untuk seluruh dokumen korpus penelitian (sekarang hanya delapan dokumen demo).
- `system/app/calculator_app.py` adalah kalkulator versi pertama (satu halaman), tidak dipakai aplikasi ini.
