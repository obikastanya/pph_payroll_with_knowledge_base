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

Checkpoint akhir 03:45 WIB 2026-10-28. Penelitian berhenti pada titik ini karena anggaran LLM habis (USD 15,016 dari 15),
bukan karena batas waktu.

Selesai (lihat `docs/BAHAN_PAPER.md` untuk peta lengkap):
- Tahap 3–13: spesifikasi, emas, gerbang, $S^E$ + *mutation score* (non-setara 1,00), alat analisis, kalibrasi,
  pembekuan (`alur-beku`, `engine-v1`), pra-registrasi (`prareg`), `emas-v1`, E0 (*holdout* GT1 + satu koreksi emas).
- E2: 13 regulasi ($m = 3$), 5 PKB ($m = 2$), 11 dari 20 pengecoh. H2a tidak diterima; H2b CAR tidak diterima;
  non-inferioritas SER terhadap B3 terpenuhi, terhadap B4 tidak.
- E3: OAR 22/24 (H3a diterima, $N = 24$); kesalahan P01 bertahan sampai akhir rantai.
- E4: H4a diterima, H4b tidak.
- Angka diperiksa ulang oleh agen peninjau independen; temuan sudah diperbaiki.

Belum dan perlu keputusan peneliti:
1. E1 (H1): buka `review/unseen_changes/sealed/` (Claude tidak membukanya), cocokkan hash, susun Δ, hitung RA.
2. Daftarkan `docs/PRAREGISTRASI.md` ke OSF/AsPredicted (stempel waktu pihak ketiga).
3. Anggaran tambahan bila ingin: 9 pengecoh tersisa, kebijakan buatan dan kontrafaktual di E2, model kedua (E5),
   pembangkitan ulang E3 (komponen kontekstual, H3b), ablasi AB1/AB2/AB5.
4. Kesalahan emas latar 2016 (PER16-II.1.1, pegawai pensiun yang bulan kerjanya diketahui): perbaikannya menyentuh
   daftar aturan P16 yang diakhiri E03/E04 dan FR01; putuskan apakah dikoreksi.
5. Celah detektor dampak (kebijakan *menghasilkan* fakta di $F_\Delta$ tanpa aturan Δ yang sama) untuk versi berikutnya.
6. Menulis ulang paper dari `docs/BAHAN_PAPER.md` dan `docs/LOG_PENELITIAN.md`.
