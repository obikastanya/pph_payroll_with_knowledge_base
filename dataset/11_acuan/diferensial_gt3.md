# Uji diferensial GT3 terhadap engine prototipe lama

Dijalankan 2026-10-27 dengan [diferensial_gt3_engine_lama.py](diferensial_gt3_engine_lama.py); hasil lengkap di [diferensial_gt3.csv](diferensial_gt3.csv).

Engine lama (`engine/` + `kb/`) dibangun sebelum GT3 dan sudah lolos 46 contoh resmi. Penyusun GT3 tidak membaca kode engine. Jadi kecocokan keduanya adalah bukti yang saling independen, dan selisihnya menunjukkan titik yang perlu diadjudikasi.

## Ringkasan

Angka di tabel ini adalah hasil run awal, sebelum GT3 dikoreksi. Status sesudah putusan ada di bagian Putusan.

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

## Putusan

Diadjudikasi 2026-10-27 dari teks regulasi dan contoh resmi (rincian: [review/adjudication/gt3_engine_lama.review.md](../../review/adjudication/gt3_engine_lama.review.md); aturan tafsir: [docs/spesifikasi/tafsir_perhitungan.md](../../docs/spesifikasi/tafsir_perhitungan.md)). Kolom `putusan` di [diferensial_gt3.csv](diferensial_gt3.csv) diisi untuk setiap baris yang berbeda.

| Kelompok | Putusan | Dasar |
|---|---|---|
| Natura (GT3-006, 009 Jul–Des dan tahunan, 019, 050) — 46 baris | `gt3_benar`. Hanya selisih di atas batas pengecualian yang menjadi bruto; kendaraan dinas untuk pegawai tanpa penyertaan modal dengan rata-rata bruto ≤ Rp100 juta/bulan dikecualikan; natura Januari–Juni 2023 tidak dipotong | PMK 66/2023 Pasal 5 ayat (4)–(5), Pasal 7 ayat (4), Pasal 23 ayat (4), Lampiran A angka 2, 7, 8 (PDF hlm. 6–8, 18, 21–22); tafsir K12 |
| Bruto bulan THR 2023 (GT3-003, 008, 009, 010 bulan 4) — 4 baris | `definisi_berbeda`. PPh sama; engine lama melaporkan bruto teratur saja. Arti yang ditetapkan: bruto masa = seluruh penghasilan masa itu, teratur + tidak teratur (seperti GT3) | PER-16/PJ/2016 Pasal 10 ayat (1), PDF hlm. 10; tafsir K14 |
| Pembulatan PPh bulanan 2023 (GT3-007, 010) — 8 baris | `gt3_benar`. PPh setahun ÷ 12 (atau ÷ faktor) dibulatkan ke bawah | contoh resmi PER-16 Lampiran I.6.2.2 (5/12 × 17.500.000 = 7.291.666), PDF hlm. 43–45; tafsir K2 |
| Kasus tidak didukung engine lama (GT3-005, 012) — 2 baris | `gt3_benar`. Engine lama tidak menghasilkan angka; nilai GT3 sudah dihitung ulang independen | — |
| Pembulatan TER 2025–2026 (GT3-028, 030, 034, 036, 037, 038, 044, 047, 048, 049) — 114 baris | `tafsir`. Selisih baru setelah koreksi GT3: mulai Masa Januari 2025 PPh dibulatkan ke rupiah terdekat (0,50 ke atas), engine lama membulatkan ke bawah. Nilai engine lama di baris ini sama dengan nilai GT3 sebelum koreksi | PER-11/PJ/2025 Pasal 129 ayat (1) huruf a dan ayat (3), PDF hlm. 106; tafsir K1 |

Status setelah putusan: dari 743 baris, 569 sama dan 174 berbeda (20 kasus). Kolom `gt3` di CSV sudah memakai nilai GT3 setelah koreksi; kolom `engine_lama` tidak berubah. Tidak ada baris yang diputus `engine_lama_benar`.

Akibat untuk sistem baru:
1. Pengecualian dan batas natura PMK 66/2023 wajib dimodelkan (kesalahan engine lama).
2. Fakta "bruto" masa metode lama memakai arti K14; bruto teratur disimpan sebagai rincian.
3. Registri pembulatan memakai K1 (berganti antara Masa Desember 2024 dan Januari 2025) dan K2.
