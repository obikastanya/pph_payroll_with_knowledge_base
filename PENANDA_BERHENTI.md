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

Checkpoint 2026-10-29. Semua eksperimen E0–E5 selesai (kecuali AB1 keadaan 2025, dihentikan untuk menghemat kredit).
Ringkasan putusan dan peta bahan: `docs/BAHAN_PAPER.md`; log: `docs/LOG_PENELITIAN.md` bagian "Lanjutan 2026-10-28/29".
Biaya: Claude ±USD 81,6 kumulatif (±USD 20 kredit disisakan untuk demo; batas di `config.BUDGET_USD` USD 89,5), OpenAI
USD 8,1.

Sisa pekerjaan:
1. Menulis ulang paper dari `docs/BAHAN_PAPER.md` (sedang dikerjakan).
2. Untuk peneliti: daftarkan `docs/PRAREGISTRASI.md` ke OSF/AsPredicted; pakar manusia memeriksa perubahan tak
   terlihat (`review/unseen_changes/SEGEL.md` aturan 3) dan emas kebijakan buatan bila ingin klaim "divalidasi pakar".
