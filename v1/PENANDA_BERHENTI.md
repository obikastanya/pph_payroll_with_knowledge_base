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

Selesai 2026-10-29. Semua eksperimen E0–E5 selesai (AB1 keadaan 2025 sengaja tidak dijalankan untuk menghemat
kredit). Paper ditulis ulang: `paper/draft/paper.tex` / `paper.pdf` (16 halaman), angka dan klaimnya diperiksa agen
independen (`review/paper/PEMERIKSAAN_ANGKA.md`, 27 temuan, semua sudah diperbaiki). Peta bahan: `docs/BAHAN_PAPER.md`.

Biaya: Claude ±USD 81,6 kumulatif; ±USD 20 kredit tersisa untuk demo (`config.BUDGET_USD` membatasi di USD 89,5);
OpenAI USD 8,1.

Untuk peneliti:
1. Daftarkan `docs/PRAREGISTRASI.md` (beserta amandemen §10) ke OSF/AsPredicted.
2. Bila ingin klaim "divalidasi pakar": pakar *payroll* manusia memeriksa perubahan tak terlihat
   (`review/unseen_changes/SEGEL.md` aturan 3), emas kebijakan buatan, dan PKB; jalankan protokol koreksi emas bila ada
   temuan.
3. Demo: kalkulator `env\Scripts\streamlit.exe run systempp\calculator_app.py` (tanpa API) dan alur akuisisi
   `system/tools/run_event.py` (memakai kredit Claude, ±USD 0,1–0,9 per dokumen).
