# Entri jurnal penggunaan AI, 27 Oktober 2026, lanjutan (siap tempel ke journal.md)

Lanjutan dari [`../naskah_draf_v1/CATATAN_AI.md`](../naskah_draf_v1/CATATAN_AI.md). Berkas ini sengaja terpisah karena pengguna meminta berkas yang sudah ada tidak diubah.

---

### 27 Oktober 2026 — Draf paper v2: filter rujukan

| Butir | Keterangan |
|---|---|
| Asisten AI | Claude Code (ekstensi VS Code), model Claude Opus 5.5 (`claude-opus-5-5`) |
| Permintaan pengguna | "coba filter rujukannya deh" |
| Tafsiran AI | Menerapkan kriteria yang sudah tertulis di `paper/reference/README.md` (2021+, *peer review*, DOI Crossref), dengan standar sebagai sumber primer sesuai PANDUAN Tahap 1 |
| Hasil | `paper/draft/naskah_draf_v2/` (salinan v1 dengan rujukan difilter, PDF 20 halaman, `FILTER_RUJUKAN.md`) |
| Berkas lama yang diubah | Tidak ada. Draf v1 tetap utuh; *checksum*-nya dicek sebelum dan sesudah pekerjaan |

| Yang dilakukan AI | Catatan |
|---|---|
| Menilai 43 rujukan baru v1 terhadap tiga kriteria | 10 lolos, 5 standar dipertahankan, 27 gugur, 1 standar tidak terpakai |
| Mencari pengganti yang lolos untuk rujukan metode yang gugur, lewat Crossref dan ACL Anthology | Prediksi selektif: Varshney dkk. (Findings ACL 2022), diverifikasi. *Ripple-Down Rules*: tidak ada sumber metode berupa jurnal atau prosiding sejak 2021, hanya makalah penerapan |
| Menulis ulang kalimat yang kehilangan sitasi, menghapus klaim yang tidak lagi tertopang, dan mengurangi Tabel III | Rincian per bagian ada di `README.md` v2 |
| Mengompilasi v2 dengan Tectonic | 57 entri pustaka, tanpa sitasi tak terdefinisi |

**Belum diverifikasi manusia**

1. Keputusan pengecualian. Filter yang ketat menghapus Gogani-Khiabani dkk. (2025), padahal karya itu gagasan yang paling dekat dengan *novelty*.
2. AlphaCode sebagai sumber *pass@k* dan *n@k* sudah dicek ke naskah versi arXiv (2203.07814): keduanya didefinisikan di sana ("If there is no filtering, then n = k and the metric is pass@k"). Namun rumus penaksir *pass@k* di Tabel XI berasal dari Chen dkk. (2021), yang gugur filter.
