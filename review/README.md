# Antrean tinjauan manusia

Semua materi penelitian disusun lebih dulu oleh Claude. Folder ini menampung materi yang **wajib diperiksa manusia** (teman peneliti atau pakar *payroll*) sebelum dipakai untuk menilai sistem. Materi yang belum disetujui tidak boleh dipakai di eksperimen E0–E5.

## Cara memeriksa

1. Buka subfolder sesuai peran Anda (tabel di bawah).
2. Setiap berkas punya pasangan `*.review.md` berisi pertanyaan yang harus dijawab, misalnya "Apakah tanggal berlakunya benar?" atau "Apakah hasil hitungan ini sama dengan hitungan Anda?".
3. Tulis jawaban dan koreksi langsung di berkas `*.review.md` itu, lalu ubah statusnya di tabel status di bawah: `menunggu` → `disetujui` atau `perlu revisi`.
4. Claude merevisi materi yang berstatus `perlu revisi`, lalu statusnya kembali ke `menunggu`.

## Isi folder

| Subfolder | Isi | Diperiksa oleh | Yang diperiksa |
|---|---|---|---|
| `corpus/` | Tabel peristiwa perubahan: relevansi, tanggal terbit dan berlaku, pengecoh | pakar *payroll* | Kelengkapan, relevansi, dan tanggal sesuai praktik |
| `gold_delta/` | Δ emas: kunci jawaban perubahan KB untuk setiap regulasi dan kebijakan | pakar *payroll* | Isi aturan, tanggal berlaku, dan kutipan pasal sesuai teks dokumen |
| `gold_cases/` | Sekitar 50 kasus pegawai bertingkat beserta hasil hitungan KB emas | pakar *payroll* | Hasil hitungan sama dengan hitungan manual |
| `adjudication/` | Selisih antara KB emas dan acuan (contoh resmi, kalkulator pihak ketiga) beserta keputusan siapa yang salah | pakar *payroll* | Keputusan adjudikasi, diperiksa tanpa melihat keputusan Claude lebih dulu |
| `impact_labels/` | Label kebijakan perusahaan yang terdampak setiap perubahan regulasi (RQ4) | pakar *payroll* | Label dibuat ulang secara terpisah, lalu dibandingkan |
| `company_policies/` | Kebijakan perusahaan buatan dan konflik buatan, beserta contoh hitungannya (GT5) | pakar *payroll* | Kebijakan masuk akal dan contoh hitungannya benar |
| `unseen_changes/` | Perubahan tak terlihat beserta contoh hitungannya, disegel dengan manifes hash (`system/tools/seal.py`) | teman peneliti dan pakar *payroll* | Perubahan masuk akal secara hukum dan contoh hitungannya benar. Dibuka setelah desain dibekukan |

## Status

| Berkas | Peran | Status | Tanggal |
|---|---|---|---|
| [corpus/peristiwa.review.md](corpus/peristiwa.review.md) | pakar *payroll* | menunggu | 2026-10-27 |
| [gold_cases/gt3.review.md](gold_cases/gt3.review.md) | pakar *payroll* | menunggu | 2026-10-27 |
| [unseen_changes/SEGEL.md](unseen_changes/SEGEL.md) | teman peneliti dan pakar *payroll* | tersegel, dibuka saat RQ1 | 2026-10-27 |

## Catatan independensi

Materi di sini disusun oleh model dari keluarga yang sama dengan model yang diuji (Claude). Kesalahan keduanya bisa searah, sehingga kecocokan antara keduanya terlihat lebih tinggi dari seharusnya. Karena itu tinjauan manusia di folder ini **wajib**, bukan pelengkap, dan KB emas juga dicek terhadap acuan yang tidak disusun Claude: contoh resmi di regulasi dan kalkulator pihak ketiga.

Perubahan tak terlihat disusun oleh *agent* terpisah yang hanya membaca taksonomi perubahan, tanpa membaca spesifikasi representasi. Hasilnya langsung disegel (manifes hash di-*commit*) sebelum representasi dibekukan, dan Claude tidak membukanya sampai saat pengujian RQ1.
