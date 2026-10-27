# Lembar pemeriksaan materi

Semua materi penelitian disusun oleh Claude, lalu diperiksa oleh *agent* peninjau terpisah terhadap teks sumber (PDF regulasi, PKB, contoh resmi). Folder ini menyimpan lembar pemeriksaan itu: pertanyaan, jawaban beserta pasal dan halaman, serta koreksi yang sudah diterapkan ke dataset. Materi berstatus `siap dipakai` dipakai di eksperimen E0–E5.

## Cara memeriksa ulang

1. Buka subfolder sesuai peran Anda (tabel di bawah).
2. Setiap berkas punya pasangan `*.review.md` berisi pertanyaan, misalnya "Apakah tanggal berlakunya benar?" atau "Apakah hasil hitungan ini sama dengan hitungan Anda?", beserta jawaban yang sudah dipakai.
3. Bila Anda tidak setuju dengan suatu jawaban, tulis koreksi dan sumbernya di bawah jawaban itu, lalu ubah status berkas di tabel di bawah menjadi `perlu revisi`.
4. Claude merevisi dataset sesuai koreksi, lalu status kembali menjadi `siap dipakai`.

## Isi folder

| Subfolder | Isi | Peran pemeriksa | Yang diperiksa |
|---|---|---|---|
| `corpus/` | Tabel peristiwa perubahan (relevansi, tanggal terbit dan berlaku, pengecoh) dan regulasi fiktif | pakar *payroll* | Kelengkapan, relevansi, dan tanggal sesuai praktik |
| `gold_delta/` | Δ emas: kunci jawaban perubahan KB untuk setiap regulasi dan kebijakan (disusun di Tahap 7) | pakar *payroll* | Isi aturan, tanggal berlaku, dan kutipan pasal sesuai teks dokumen |
| `gold_cases/` | 50 kasus pegawai bertingkat (GT3) beserta langkah hitungnya | pakar *payroll* | Hasil hitungan sama dengan hitungan manual |
| `adjudication/` | Selisih antara acuan dan pembanding beserta putusan mana yang benar | pakar *payroll* | Putusan adjudikasi |
| `impact_labels/` | Label kebijakan perusahaan yang terdampak setiap perubahan regulasi (RQ4; label a dan b disusun di Tahap 17) | pakar *payroll* | Label dibuat ulang secara terpisah, lalu dibandingkan |
| `company_policies/` | Klausul PKB nyata dan label konfliknya, contoh hitung kebijakan (GT5), kebijakan dan konflik sintetis | pakar *payroll* | Klausul dibaca benar, label konflik tepat, contoh hitungannya benar |
| `unseen_changes/` | Perubahan tak terlihat beserta contoh hitungannya, disegel dengan manifes hash (`system/tools/seal.py`) | teman peneliti dan pakar *payroll* | Perubahan masuk akal secara hukum dan contoh hitungannya benar. Dibuka setelah desain dibekukan |

## Status

| Berkas | Status | Tanggal | Aturan tafsir yang dipakai |
|---|---|---|---|
| [corpus/peristiwa.review.md](corpus/peristiwa.review.md) | siap dipakai | 2026-10-27 | [tafsir_korpus.md](../docs/spesifikasi/tafsir_korpus.md) |
| [corpus/fiktif.review.md](corpus/fiktif.review.md) | siap dipakai | 2026-10-27 | [tafsir_korpus.md](../docs/spesifikasi/tafsir_korpus.md) |
| [gold_cases/gt3.review.md](gold_cases/gt3.review.md) | siap dipakai | 2026-10-27 | [tafsir_perhitungan.md](../docs/spesifikasi/tafsir_perhitungan.md) |
| [adjudication/gt3_engine_lama.review.md](adjudication/gt3_engine_lama.review.md) | siap dipakai | 2026-10-27 | [tafsir_perhitungan.md](../docs/spesifikasi/tafsir_perhitungan.md) |
| [company_policies/klausul.review.md](company_policies/klausul.review.md) | siap dipakai | 2026-10-27 | README klausul |
| [company_policies/gt5.review.md](company_policies/gt5.review.md) | siap dipakai | 2026-10-27 | README GT5, bagian Putusan tafsir |
| [company_policies/sintetis.review.md](company_policies/sintetis.review.md) | siap dipakai | 2026-10-27 | [tafsir_perhitungan.md](../docs/spesifikasi/tafsir_perhitungan.md) |
| [unseen_changes/SEGEL.md](unseen_changes/SEGEL.md) | siap dipakai, tersegel sampai pengujian RQ1 | 2026-10-27 | — |

## Catatan independensi

Materi di sini disusun oleh model dari keluarga yang sama dengan model yang diuji (Claude), sehingga kesalahan keduanya bisa searah. Ada tiga pengaman. Pertama, setiap materi diperiksa oleh *agent* peninjau yang terpisah dari penyusunnya, terhadap teks sumber, dengan hitungan ulang memakai program sendiri. Kedua, KB emas juga dicek terhadap acuan yang tidak disusun Claude, yaitu contoh resmi di regulasi (GT1), kalkulator DJP (GT2), dan implementasi pihak ketiga (GT4). Ketiga, aturan tafsir yang dipakai ditulis eksplisit di `docs/spesifikasi/` sehingga dapat diuji ulang.

Perubahan tak terlihat disusun oleh *agent* terpisah yang hanya membaca taksonomi perubahan, tanpa membaca spesifikasi representasi. Hasilnya langsung disegel (manifes hash di-*commit*) sebelum representasi dibekukan, dan Claude tidak membukanya sampai saat pengujian RQ1.
