# Jurnal penelitian

Catatan kerja penelitian *knowledge-based system* adaptif untuk PPh 21, dari Tahap 3 (spesifikasi) sampai Tahap 20 (analisis). Setiap tahap dicatat dengan tujuan, hasil, angka penting, keputusan, penyimpangan dari rencana, berkas keluaran, dan bagian paper yang memakainya. Setiap tahap diakhiri satu *commit* git yang namanya dicatat di sini, supaya keadaan pada akhir tahap dapat dipulihkan.

Dokumen terkait:
- Rencana tahap dan log keputusan: [PANDUAN_PENELITIAN.md](../PANDUAN_PENELITIAN.md)
- Kerangka paper: [paper/draft/skeleton.tex](../paper/draft/skeleton.tex)
- Spesifikasi: [docs/spesifikasi/](spesifikasi/)
- Dataset dan statusnya: [dataset/RENCANA_DATASET.md](../dataset/RENCANA_DATASET.md)
- Indeks bahan paper (diisi bertahap): bagian **Bahan paper** di bawah dan [docs/BAHAN_PAPER.md](BAHAN_PAPER.md) setelah Tahap 20

## Status

| Tahap | Nama | Status | *Commit* |
|---|---|---|---|
| 0 | Persiapan dan keputusan terbuka | selesai (sebelum jurnal ini) | `e851c8d` dst. |
| 2 | Taksonomi dan aturan tafsir | selesai (sebelum jurnal ini) | `d2ff550`, `f9b4f08` |
| 6 | Korpus dan dataset | selesai (sebelum jurnal ini) | `02c3e01` |
| 3 | Spesifikasi representasi | berjalan | |
| 4 | Spesifikasi akuisisi dan kontrak antarmuka | belum | |
| 5 | Representasi dan *engine* | belum | |
| 7 | Emas $\mathcal{K}^\star_n$, $\Delta^\star_n$ | belum | |
| 8 | Ruang uji dan acuan | belum | |
| 9 | Alur akuisisi | belum | |
| 10 | Pembanding, ablasi, skrip analisis | belum | |
| 11 | Kalibrasi pada data pengembangan | belum | |
| 12 | Pra-registrasi | belum | |
| 13–18 | Eksperimen E0–E5 | belum | |
| 19 | Peristiwa prospektif | dipantau (peristiwa pertama Februari 2027) | |
| 20 | Analisis dan penyajian hasil | belum | |

Tahap 1 (kajian pustaka) dan 21–24 (naskah, telaah, rilis, pengiriman) dikerjakan setelah sistem dan hasil selesai, sesuai log keputusan "Urutan kerja".

## Cara kerja yang dipakai di semua tahap

- Claude menyusun setiap materi, lalu *agent* peninjau terpisah memeriksanya terhadap teks sumber. Hasil pemeriksaan disimpan di `review/` dan materi diberi status "siap dipakai" (log keputusan "Pemeriksaan materi `review/`").
- Kode berbahasa Inggris di `system/`; dokumen berbahasa Indonesia, istilah asing dimiringkan.
- Kode lama (`engine/`, `kb/`, `ui/`, `web/`) tidak diubah; dipakai sebagai acuan kesetaraan.
- Panggilan LLM dicatat lengkap (prompt, keluaran, token, biaya) dan dibatasi anggaran USD 15.

---

## Tahap 3. Spesifikasi representasi pengetahuan

Mulai: 2026-10-27.

### Temuan saat menyusun spesifikasi

1. **P07 (PER-11/PJ/2025) ternyata peristiwa relevan.** Tafsir K1 menetapkan pembulatan PPh 21 ke rupiah terdekat mulai Masa Januari 2025 berdasarkan PER-11/PJ/2025 Pasal 129 ayat (1) huruf a dan ayat (3) (PDF hlm. 106), sedangkan tabel peristiwa mencatat dokumen itu sebagai pengecoh X1. Pasal 130 huruf a membatasi PER-2/PJ/2024 pada masa sampai Desember 2024. PMK 81/2024 (P05) hanya mengatur pembulatan keputusan dan dokumen elektronik (Pasal 33 ayat (7), PDF hlm. 34), bukan bukti potong. Koreksi: P07 dipindah menjadi peristiwa uji **E13**, jenis T9 (prosedur hitung), sifat S1 (berlaku 2025-01-01, terbit 2025-05-22). Dengan ini T9 punya contoh nyata.
