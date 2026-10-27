# Penanda berhenti

Dibuat 2026-10-28 00:36 WIB atas permintaan peneliti (besok berangkat perjalanan).

**Batas waktu: 2026-10-28 07:00 WIB.** Bila penelitian belum selesai sampai batas itu, pekerjaan dihentikan pada
*checkpoint* terdekat:

1. Tidak memulai langkah panjang baru (jalan LLM, *build* S^E, pemeriksaan gerbang penuh) yang tidak dapat selesai
   sebelum 07:00. Langkah yang dimulai sesudah 06:15 hanya langkah pendek (dokumentasi, *commit*).
2. Batch LLM yang sedang berjalan ditunggu bila diperkirakan selesai sebelum 07:00; bila tidak, hasilnya diambil
   kemudian dari ID batch yang tercatat di `experiments/<RUN>/calls.jsonl` (biaya tidak hilang).
3. Semua pekerjaan di-*commit*, `docs/LOG_PENELITIAN.md` diperbarui, dan bagian "Status saat berhenti" di bawah diisi:
   tahap terakhir yang selesai, yang sedang berjalan, dan langkah berikutnya.

## Status saat berhenti

Checkpoint 02:30 WIB (diperbarui setiap *commit*).

Selesai: Tahap 3–13 (emas, gerbang, $S^E$ + mutasi, alat analisis, kalibrasi, pembekuan `alur-beku`/`engine-v1`,
pra-registrasi `prareg`, `emas-v1`, E0 *holdout* + satu koreksi emas), E2 dijalankan untuk 13 regulasi ($m = 3$) dan 5 PKB
($m = 2$). Anggaran LLM terpakai ~USD 12,6 dari 15.

Sedang berjalan: penilaian E2 regulasi, pengecoh E2 (sinkron), label RQ4 (GraphDB).

Belum: E3 (`run_chain.py` dengan `--iso e2-regulasi,e2-pengecoh`), ringkasan RQ4, E1 (perubahan tersegel: harus dibuka
oleh peneliti/kolaborator, Claude tidak membukanya), E5 (model kedua: tidak ada sisa anggaran), `docs/BAHAN_PAPER.md`.
Pendaftaran OSF dokumen `docs/PRAREGISTRASI.md` dilakukan peneliti.
