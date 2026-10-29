# Naskah draf v3 (27 Oktober 2026): rujukan difilter dengan tiga pengecualian

Draf v3 adalah [draf v2](../naskah_draf_v2/) ditambah tiga pengecualian rujukan yang disetujui pengguna. Draf v2 sendiri adalah [draf v1](../naskah_draf_v1/) dengan rujukan yang difilter memakai kriteria di [`../../reference/README.md`](../../reference/README.md): terbit 2021+, jurnal atau prosiding ber-*peer review*, dan DOI Crossref, dengan standar sebagai sumber primer. Draf v1 dan v2 tidak diubah.

| Pengecualian | Alasan | Dipakai di |
|---|---|---|
| Gogani-Khiabani dkk. (2025), arXiv / IRS-TPC 2024 | Gagasan yang paling dekat dengan *novelty*: LLM menerapkan perubahan dari publikasi IRS ke kode pajak versi sebelumnya | Bab I, Bab III, Tabel III |
| Compton dan Kang (2021), buku *Ripple-Down Rules* | Sumber baku RDR dan *cornerstone case*; tidak ada sumber metode RDR berupa jurnal atau prosiding sejak 2021 | Bab I, III, V |
| Chen dkk. (2021), arXiv | Sumber rumus penaksir *pass@k* | Bab III, VI, Tabel XI |

Rincian semua rujukan ada di [FILTER_RUJUKAN.md](FILTER_RUJUKAN.md).

## Isi folder

| Berkas | Isi |
|---|---|
| `main.tex`, `sections/` | Sumber LaTeX |
| `rujukan_tambahan.bib` | 19 entri: 11 lolos kriteria, 3 pengecualian, 5 standar |
| `main.pdf` | 20 halaman, 60 entri daftar pustaka |
| `FILTER_RUJUKAN.md` | Hasil filter per rujukan |

## Perubahan dari v2

| Bagian | Perubahan |
|---|---|
| I Pendahuluan | Sitasi *Ripple-Down Rules* dan kalimat tentang gagasan Gogani-Khiabani dkk. dikembalikan |
| III Penelitian terkait | Paragraf Gogani-Khiabani dkk. dan barisnya di Tabel III dikembalikan. Sitasi RDR dikembalikan. *pass@k* kembali bersumber Chen dkk. dan AlphaCode |
| V Akuisisi | Sitasi RDR untuk *cornerstone case* (G4) |
| VI Metodologi evaluasi | Rumus *pass@k* di Tabel XI kini bersitasi Chen dkk. |

Law&Order, Graus, *benchmark* temporal 2026, dan sumber metode klasik tetap tidak dikutip, sama seperti v2.

Slide yang selaras dengan draf ini adalah [`progress_mingguan_draf_v2.pptx`](../../../progress_mingguan/progress_mingguan_draf_v2.pptx). Cara kompilasi dan arti penanda draf sama dengan [README v1](../naskah_draf_v1/README.md).
