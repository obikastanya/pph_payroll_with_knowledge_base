# Panduan penulisan set prospektif

Set prospektif berisi perubahan yang belum pernah terjadi tetapi wajar, ditulis dalam format dokumen nyata. Set ini menjadi data uji hipotesis H2 (keamanan satu pembaruan). Setiap unit dinilai dengan membandingkan pembaruan hasil sistem dengan kunci jawaban (`gold`) pada slip pegawai, jadi kunci jawaban harus tepat dan teksnya harus benar-benar memuat apa yang ada di kunci jawaban.

**Penulis set ini tidak pernah melihat prompt sistem** (`system_final/pph21kbs/draft.py`, bagian SYSTEM_*). Jangan membukanya.

## Struktur satu unit

`v2/dataset/15_set_prospektif/units/<ID>/`
- `teks.md`: teks dokumen dalam bahasa Indonesia, mengikuti tata letak jenisnya. Satu paragraf per baris dengan baris kosong di antaranya. Baris "Pasal N", "BAB ...", dan "LAMPIRAN" menjadi judul. Tabel ditulis dengan baris yang diawali `|`.
- `spec.json`: lihat contoh `units/R01/spec.json`. Kolomnya:
  - `id`, `layer` ("regulation" atau "company"), `instance` (unit perusahaan: SP02, SP03, …), `policy` (unit perusahaan: nama kebijakan yang dipakai pegawai, yaitu ID unit untuk kebijakan baru, atau ID SP untuk memo perubahan);
  - `change_type` (T1–T10, lihat taksonomi di bawah), `size` (jumlah elemen di `gold`), `traps` (daftar jebakan), `title`, `header` (header berulang di PDF);
  - `issued`, `effective_from`, `effective_until`, `retroactive`, `summary` (satu kalimat);
  - `gold`: pembaruan KB sesuai `system_final/spec/schemas/delta.schema.json`, dengan `delta_id` "GOLD-<ID>", `event_id` "<ID>", `document.id` "<ID>";
  - `triggers`: pegawai pemicu (lihat bawah).

## Aturan penulisan

1. **Wajar dan bergaya dokumen nyata.**
   - Regulasi: PMK, PP, PER Dirjen Pajak, Perpres, atau surat BPJS, dengan konsiderans, dasar hukum, pasal, dan penutup.
   - Kebijakan perusahaan: peraturan perusahaan, PKB, atau memo direksi.
   - Pakai nomor fiktif yang jauh dari nomor nyata, misalnya PMK 701–799/2027 atau PER-701/PJ/2027.
   - Jangan menyalin teks regulasi nyata panjang-panjang. Kalimat baku seperti konsiderans boleh mengikuti pola umum.
2. **Setiap unit memuat minimal satu jebakan**, dicatat di `traps`:
   - rujukan silang ke pasal lain;
   - pengecualian;
   - ketentuan peralihan;
   - syarat implisit (misalnya hanya pegawai tetap);
   - angka penting yang hanya ada di lampiran atau penjelasan;
   - pasal yang menyatakan ulang ketentuan lama yang tidak berubah;
   - berlaku surut;
   - nilai dalam huruf dan angka yang harus dibaca bersama.
3. **Tanggal.**
   - Unit regulasi terbit pada 2027 dan berlaku pada 2027, boleh surut ke awal 2027.
   - Basisnya adalah KB acuan akhir 2026 (seluruh rantai acuan).
   - Unit perusahaan: lihat pembagian di bawah.
4. **Kunci jawaban (`gold`).**
   - Ikuti gaya pembaruan acuan yang ada. Bacalah contoh yang relevan di `v2/dataset/12_emas/delta/`:
     - `GOLD-E05` untuk parameter;
     - `GOLD-E07` untuk tabel dan aturan bersyarat;
     - `GOLD-E06` dan `GOLD-E10` untuk fasilitas DTP dan cakupannya;
     - `GOLD-E13` untuk pembulatan;
     - `GOLD-E03` dan `GOLD-E04` untuk metode atau tabel besar;
     - `GOLD-SP*` dan `GOLD-PKB-*` untuk kebijakan perusahaan.
   - Nama fakta, parameter, dan tabel yang sudah ada harus dipakai persis. Lihat isi KB dengan:
     ```python
     import v2.harness; from datetime import date; from v2.harness import gold
     v = gold.chain().view(date(2026, 12, 31))
     [r.id for r in v.records]                               # semua rekaman
     sorted(v.params), sorted(v.tables), sorted(v.rules)     # nama parameter, tabel, aturan
     ```
   - Untuk mengganti nilai yang sudah ada, tambahkan rekaman baru dengan nama yang sama, `id` baru, dan `valid_from` baru, seperti `PAR.JP_WAGE_CAP.2024`. Untuk mengubah aturan yang sudah ada, pakai `change` dengan `id` yang sama.
   - **Setiap `quote` harus disalin kata per kata dari `teks.md`**, pendek (satu kalimat atau kurang), dan memuat angka atau syarat yang menjadi dasar elemen itu. Isi `provision` dengan pasal dan ayatnya.
   - `size` = jumlah elemen di `add` + `change` + `remove`.
   - Jangan memakai masukan data payroll yang tidak ada. Bila sebuah aturan butuh data pegawai, pakai yang sudah ada. Daftar masukan yang tersedia ada di `system_final/data/kb/payroll_inputs.json`, skema `system_final/spec/schemas/case.schema.json`, dan masukan yang sudah dibaca aturan di KB.
5. **Pegawai pemicu (`triggers`).**
   - Minimal tiga pegawai, dan minimal satu di antaranya slipnya berubah karena pembaruan ini.
   - Untuk ambang, buat pegawai tepat di bawah, di, dan di atas ambang.
   - Untuk syarat sektor, buat satu pegawai di sektor yang memenuhi dan satu yang tidak.
   - Format: `{"id": "T1", "year": 2027, "salary": 12000000, "ptkp": "TK/0", "klu": "62019", "jkk_risk": "very_low", "relief": false, "method": "gross", "start_month": 1, "end_month": 12, "income": {"bonus": 5000000}, "income_months": [12], "benefits": {}, "hr": {}, "employee": {}, "employer": {}}`. Hanya `id`, `year`, dan `salary` yang wajib.
6. **Cek sampai bersih.** Jalankan dari akar repo:
   ```
   env\Scripts\python.exe -m v2.harness.check_unit <ID> [<ID> ...]
   ```
   Perintah ini merender teks ke PDF, mengekstraknya seperti dokumen nyata, mengimpornya ke sistem, lalu memeriksa:
   - kunci jawaban bisa diterapkan (G1);
   - setiap kutipan ditemukan di teks hasil ekstraksi;
   - tidak ada masukan di luar data payroll;
   - tidak ada galat mesin;
   - slip minimal satu pegawai pemicu berubah.

   Perbaiki sampai hasilnya `OK`.

## Taksonomi jenis perubahan

| Kode | Jenis |
|---|---|
| T1 | Parameter: nilai tunggal berubah (batas upah, PTKP, persentase, plafon) |
| T2 | Tabel tarif: lapisan atau tarif berubah |
| T3 | Klasifikasi penghasilan: suatu penerimaan menjadi atau berhenti menjadi objek, teratur atau tidak teratur, pengurang atau bukan |
| T4 | Fasilitas baru dengan kriteria (misalnya DTP sektor tertentu) |
| T5 | Perubahan cakupan fasilitas atau aturan |
| T6 | Perubahan masa: perpanjangan atau pengakhiran lebih awal |
| T7 | Pergantian metode perhitungan |
| T8 | Pencabutan tanpa pengganti |
| T9 | Prosedur hitung: pembulatan, urutan, dasar pengenaan |
| T10 | Kebijakan perusahaan: komponen gaji, tunjangan, lembur, THR, bonus, pajak ditanggung perusahaan atau *gross-up*, pembagian iuran, potongan |

## Pembagian unit

Ukuran: **S** = 1 elemen, **M** = 2–10 elemen, **L** = 11 elemen atau lebih.

| Unit | Isi |
|---|---|
| R01 | contoh, sudah jadi (T1, M) |
| R02–R50 | regulasi 2027. Pembagian ukuran: S 18 unit, M 17 unit, L 14 unit. Pembagian jenis: T1 9, T2 6, T3 6, T4 7, T5 6, T6 4, T7 3, T8 3, T9 5 |
| K01–K10 | memo direksi yang mengubah kebijakan perusahaan fiktif yang sedang berlaku (lihat tabel di bawah); `policy` = ID SP-nya; ukuran S atau M |
| K11–K30 | peraturan perusahaan atau PKB baru tahun 2027 untuk perusahaan fiktif (dua per perusahaan: SP02, SP03, SP04, SP05, SP06, SP07, SP08, SP11, SP12, SP13); `policy` = ID unitnya; ukuran M atau L (sepuluh L) |

Memo (tanggal unggah = `issued`, harus persis):

| Unit | Perusahaan | Tanggal |
|---|---|---|
| K01 | SP02 | 2024-07-01 |
| K02 | SP03 | 2026-01-15 |
| K03 | SP04 | 2024-04-01 |
| K04 | SP05 | 2025-06-02 |
| K05 | SP06 | 2026-03-02 |
| K06 | SP07 | 2025-04-01 |
| K07 | SP08 | 2025-01-15 |
| K08 | SP11 | 2026-02-02 |
| K09 | SP12 | 2024-11-01 |
| K10 | SP13 | 2024-09-02 |

Kebijakan yang sedang berlaku dan teksnya:
- `v2/dataset/10_kebijakan_perusahaan/sintetis/SPxx.md` dan `SPxx.json`;
- kunci jawaban: `v2/dataset/12_emas/delta/GOLD-SPxx.json`.

Memo mengubah aturan kebijakan itu: pakai `change` dengan `id` aturan yang sama, atau `add` aturan baru dengan `policy` = ID SP.
