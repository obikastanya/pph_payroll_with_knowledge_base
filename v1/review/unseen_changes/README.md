# Perubahan tak terlihat (RQ1)

Bahan uji adaptivitas representasi: perubahan regulasi fiktif yang masuk akal, disertai contoh hitungan, yang tidak dilihat perancang sistem sampai pengujian. Sistem dinilai berhasil pada satu perubahan bila perubahan itu dapat dinyatakan sebagai Δ tanpa mengubah kode *engine*, dan seluruh contoh hitungannya tereproduksi.

| Berkas | Isi |
|---|---|
| `sealed/` | 16 perubahan (U01–U16), masing-masing `perubahan.md` dan `contoh.json`; `INDEX.csv`, panduan pemeriksaan, alat pembangkit contoh, dan `MANIFEST.sha256` |
| [SEGEL.md](SEGEL.md) | hash manifes, sebaran jenis perubahan, dan aturan buka segel |

## Aturan

1. Isi `sealed/` tidak dibuka selama representasi dan *engine* dikembangkan. Segel dibuka setelah *tag* `representasi-v1`, saat pengujian E1.
2. Keutuhan diperiksa sebelum dibuka:
   ```
   env\Scripts\python system\tools\seal.py verify review\unseen_changes\sealed
   ```
   dan SHA-256 `sealed/MANIFEST.sha256` dicocokkan dengan [SEGEL.md](SEGEL.md).
3. Saat pengujian, setiap perubahan dikerjakan dalam batas waktu yang ditetapkan di pra-registrasi. Hasilnya (berhasil atau tidak, Δ yang ditulis, contoh yang gagal, waktu kerja) dicatat per perubahan.
4. Revisi isi setelah segel dibuka dilakukan lewat `sealed/_alat/`, lalu folder disegel ulang dan revisinya dilaporkan.
