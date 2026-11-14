# Log Adjudikasi V2 (research_plan.md §9.2)

Setiap kelas selisih antar-sistem diputuskan berdasarkan pasal, bukan voting. Status: **TERJELASKAN** berarti setiap kasus dalam kelas sudah diverifikasi otomatis (`tests/test_v2_differential.py`).

Kasus: 2.201 profil sintetis (`dataset/06_kasus_uji_sintetis/kasus_sintetis.jsonl`, seed 42; S8 dan gross-up PER-16 dikecualikan, lihat di bawah). Sistem: KB (engine + `kb/regulasi`) vs B1 (`baselines/b1_hardcoded`, tag `b1-frozen`).

## A-01 — Representasi keluaran (bukan selisih nilai)

| Fakta | Gejala | Putusan |
|---|---|---|
| `pph21_dtp` | B1 menulis 0 untuk pemberi kerja tanpa KLU; KB tidak menghasilkan fakta (None) | Tidak ada nilai pajak yang berbeda. KB hanya menghasilkan fakta DTP bila KLU tersedia (aturan DTP-04*). **TERJELASKAN** |
| `lebih_bayar_dikembalikan` | KB juga menghasilkan untuk rezim PER-16; B1 hanya untuk rezim TER | KB benar menerapkan REG-MT-LB0 (PMK 168 Ps. 21(1); prinsip yang sama di PER-16). Tidak memengaruhi PPh. **TERJELASKAN** |

## A-02 — Gross-up masa pajak terakhir memiliki lebih dari satu titik tetap integer (25 kasus)

- **Gejala.** KB dan B1 berbeda pada `tunjangan_pajak` bulan terakhir sebesar Rp150 atau Rp250, beserta seluruh fakta tahunan turunannya.
- **Verifikasi.** Untuk setiap kasus, nilai KB maupun nilai B1 disubstitusikan ke persamaan T = PPh_setahun(A + T) − PPh_dipotong. **Keduanya memenuhi persamaan secara persis**, sehingga keduanya titik tetap yang sah.
- **Penyebab.** PKP dibulatkan ke bawah ribuan (PMK 168 Ps. 8(4)), sehingga f(T) berupa fungsi tangga dengan lompatan tarif marginal × Rp1.000 (Rp50/150/250/300/350). Fungsi tangga monoton bisa memotong garis T = f(T) lebih dari sekali.
- **Konsekuensi penelitian.** H5c ("masa pajak terakhir Pasal 17 selalu bersolusi tunggal") **terbantah di domain integer**. Pada data sintetis, 154 dari 998 kasus gross-up memiliki solusi ganda di bulan terakhir.
- **Putusan.** Regulasi tidak menetapkan solusi mana yang dipakai, sehingga ini tafsir `TITIK-TETAP-PILIH`.
  - KB menghitung titik tetap **terkecil dan terbesar** (Knaster–Tarski, iterasi dari batas bawah/atas), memberi peringatan `GROSSUP_GANDA`, dan memilih secara deterministik (default `terkecil`).
  - B1 memilih berdasarkan jalur iterasinya: 129 kasus = terkecil, 25 kasus = terbesar.
  - Selisih V2 = 25 kasus tersebut. **TERJELASKAN** (bukan bug; ketidaktunggalan regulasi).

## Pengecualian dari V2

| Kelompok | Alasan | Diuji di |
|---|---|---|
| S8 (sumbu waktu) | B1 dibekukan sebelum model transaksi bertanggal ada | E11 + MR14 |
| Gross-up tahun ≤ 2023 | Di luar model v1 (KODIFIKASI.md bagian E); kedua sistem menolak eksplisit | — |

## Perbaikan yang dipicu V2 (sebelum adjudikasi akhir)

1. **Kontrak input diperketat.** Nominal komponen wajib `int ≥ 0`; engine melempar `InputTidakValid` untuk pecahan atau float (§6.9.5). Prorata S7 kini dibulatkan oleh kebijakan perusahaan sebelum menjadi input.
2. **Penyelesai titik tetap diganti** dari "iterasi dari 0" (bergantung jalur) menjadi titik tetap terkecil dan terbesar dengan pengaman monotonisitas. Gross-up bulanan dan gross-up akhir tahun dipisah menjadi dua SCC, agar setiap fungsi monoton terhadap satu variabel.
