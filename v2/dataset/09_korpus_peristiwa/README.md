# 09_korpus_peristiwa — Tabel peristiwa regulasi

`peristiwa.csv`: satu baris per dokumen regulasi (13 uji 2023–2026, 20 pengecoh, 13 pengembangan) dengan tanggal terbit, masa berlaku, berlaku surut, relevansi, dan jenis perubahan. Dibaca oleh `harness/corpus.py`.

| Kolom | Arti |
|---|---|
| `bagian` | `uji`, `pengecoh`, `pengembangan` |
| `relevan` | Apakah dokumen mengubah perhitungan PPh 21 pegawai tetap; jawaban benar untuk dokumen `tidak` adalah pembaruan kosong |

`fiktif/`: teks regulasi fiktif FR01–FR05 (set pengembangan; pembaruan GOLD-FR* di `12_emas`). Tidak dipakai di run terukur.
