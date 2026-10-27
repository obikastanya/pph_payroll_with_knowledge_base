# Segel perubahan tak terlihat

- Folder: `sealed/` (U01–U16, 16 perubahan, 100 contoh hitungan; 38 berkas)
- Disusun: 2026-10-27 oleh *agent* terpisah yang hanya membaca taksonomi perubahan (bagian 0–1) dan dataset regulasi
- SHA-256 `sealed/MANIFEST.sha256`: `df7857d6b4675784711921bf81acb3f1520723ed5a95781f3210a60054f5e5e6`
- Sebaran jenis utama: T1 2, T2 2, T3 2, T4 1, T5 1, T6 1, T7 1, T8 1, T9 3, T10 2. Sifat: S1 3, S2 8, S3 2, S4 1, S5 11, S6 3
- Ditinjau dan disegel ulang: 2026-10-27

Aturan:
1. Perancang sistem (peneliti dan Claude di sesi pengembangan) **tidak membuka** isi `sealed/` sampai representasi dibekukan (*tag* `representasi-v1`) dan pengujian RQ1 dimulai.
2. Keutuhan diperiksa dengan `env\Scripts\python system\tools\seal.py verify review\unseen_changes\sealed` dan dengan mencocokkan hash di atas.
3. Setelah dibuka, pakar memeriksa kewajaran dan contoh hitungan lewat `sealed/PANDUAN_PEMERIKSA.md`. Revisi dilakukan lewat `sealed/_alat/buat_contoh.py`, lalu folder disegel ulang dan revisinya dilaporkan.
