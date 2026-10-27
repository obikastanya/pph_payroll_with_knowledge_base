# Uji diferensial GT3 terhadap engine prototipe lama

Dijalankan 2026-10-27 dengan [diferensial_gt3_engine_lama.py](diferensial_gt3_engine_lama.py); hasil lengkap di [diferensial_gt3.csv](diferensial_gt3.csv).

Engine lama (`engine/` + `kb/`) dibangun sebelum GT3 dan sudah lolos 46 contoh resmi. Penyusun GT3 tidak membaca kode engine. Jadi kecocokan keduanya adalah bukti yang saling independen, dan selisihnya menunjukkan titik yang perlu diadjudikasi.

## Ringkasan

| | Jumlah |
|---|---|
| Nilai yang dibandingkan (bruto, PPh 21, DTP per masa; PKP dan PPh setahun) | 743 |
| Sama persis | **683 (91,9%)** |
| Berbeda | 60, di 8 kasus |
| Kasus yang sama sepenuhnya | 40 dari 50 |
| Kasus yang tidak didukung engine lama | 2 (GT3-005, GT3-012: *gross-up* rezim 2023 belum dimodelkan) |

Dua selisih awal ternyata kesalahan konverter, bukan kesalahan GT3, dan sudah diperbaiki sebelum angka di atas:
- **GT3-048:** karyawati kawin K/1 dengan suami tidak berpenghasilan. Konverter belum meneruskan keterangan suami, sehingga engine memakai TK (kategori A, bukan B).
- **GT3-029:** kriteria DTP Rp10 juta. Konverter menandai lembur sebagai "teratur", sehingga engine ikut menjumlahkannya ke penghasilan tetap.

## Selisih yang tersisa dan dugaan penyebabnya

| Kelompok | Kasus | Selisih | Dugaan | Yang lebih mungkin benar |
|---|---|---|---|---|
| Natura (PMK 66/2023) | GT3-006, 009, 019, 050 | bruto dan PPh 21 bulan bernatura; PKP dan PPh setahun | Engine lama memakai seluruh nilai natura sebagai objek; ambang dan pengecualian PMK 66/2023 (rumah, kendaraan dinas, kupon makan dinas luar) belum dimodelkan. GT3 menerapkannya | GT3, menunggu konfirmasi pakar |
| Definisi "bruto" masa 2023 | GT3-003, 008, 009, 010 | bruto bulan THR 2023 berbeda tepat sebesar THR; PPh 21 sama | Engine lama melaporkan bruto teratur pada metode lama; GT3 melaporkan bruto termasuk penghasilan tidak teratur | bukan kesalahan; perbedaan definisi fakta keluaran (perlu ditetapkan di Tahap 3) |
| Pembulatan PPh bulanan 2023 | GT3-007, 010 | Rp1 per bulan | GT3 membulatkan ke bawah PPh setahun ÷ 12; engine lama membulatkan berbeda. PER-16 tidak mengatur tegas (ambiguitas K2 di README GT3) | perlu keputusan |

## Tindak lanjut

1. Pakar mengadjudikasi ketiga kelompok lewat [review/adjudication/gt3_engine_lama.review.md](../../review/adjudication/gt3_engine_lama.review.md).
2. Definisi fakta "bruto" untuk metode lama ditetapkan di spesifikasi representasi (Tahap 3).
3. Aturan pembulatan PPh bulanan 2023 dan TER dicatat di registri pembulatan sistem baru, dengan sumber hasil adjudikasi.
4. Hasil adjudikasi dicatat di kolom tambahan `putusan` di `diferensial_gt3.csv`.
