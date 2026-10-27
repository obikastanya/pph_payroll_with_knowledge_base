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

(diisi pada *checkpoint* terakhir)
