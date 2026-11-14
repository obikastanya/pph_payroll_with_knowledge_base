# Naskah draf v2 (27 Oktober 2026): rujukan difilter

Draf v2 sama dengan [draf v1](../naskah_draf_v1/), kecuali rujukannya sudah difilter dengan kriteria di [`../../reference/README.md`](../../reference/README.md):

- terbit 2021 ke atas;
- jurnal atau prosiding ber-*peer review*;
- DOI terdaftar di Crossref.

Standar dipertahankan sebagai sumber primer (PANDUAN Tahap 1). Draf v1 tidak diubah, jadi keduanya dapat dibandingkan.

Rincian setiap rujukan yang gugur, alasannya, dan pengecualian yang disarankan ada di [FILTER_RUJUKAN.md](FILTER_RUJUKAN.md).

## Isi folder

| Berkas | Isi |
|---|---|
| `main.tex`, `sections/` | Sumber LaTeX, salinan v1 dengan perubahan di bawah |
| `rujukan_tambahan.bib` | 16 entri: 11 lolos kriteria (termasuk pengganti baru Varshney dkk. 2022) dan 5 standar |
| `main.pdf` | Hasil kompilasi: 20 halaman, 57 entri daftar pustaka (v1: 21 halaman, 78 entri) |
| `FILTER_RUJUKAN.md` | Hasil filter per rujukan |

## Perubahan teks dari v1

| Bagian | Perubahan |
|---|---|
| I Pendahuluan | Kelemahan LLM terhadap amandemen kini hanya ditopang Prior dkk. (2025). Law&Order dan Gogani-Khiabani dkk. dihapus. Sitasi *Ripple-Down Rules* dilepas |
| III Penelitian terkait | Kalimat Graus, Law&Order, Gogani-Khiabani dkk., Governatori dan Rotolo, *benchmark* temporal 2026, dan Rodrigues dkk. dihapus. CodeUpdateArena diganti ReCode. Geifman dan El-Yaniv diganti Varshney dkk. OpenFisca menjadi catatan kaki URL. Tabel III tinggal 6 karya |
| IV Representasi | Sitasi Tarski dilepas; nama teorema Knaster–Tarski tetap |
| VI Metodologi evaluasi | Sitasi *design science research* dan sumber statistik (Clopper–Pearson, Newcombe, Holm, Cohen, Krippendorff) dilepas; nama metodenya tetap. *pass@k* dan *n@k* kini hanya bersumber AlphaCode |

Bagian II, V, VII, VIII, IX, dan abstrak tidak berubah.

## Perlu diputuskan

Filter yang ketat menghapus karya yang paling dekat dengan *novelty* (Gogani-Khiabani dkk. 2025) dan membuat beberapa metode tidak bersitasi. Usulan pengecualian ada di bagian akhir `FILTER_RUJUKAN.md`.

[Slide progres](../../../progress_mingguan/progress_mingguan_draf_v1.pptx) slide 5 masih menyebut Law&Order dan Gogani-Khiabani dkk. Bila v2 yang dipakai, slide itu perlu disesuaikan.

Cara kompilasi dan arti penanda draf sama dengan [README v1](../naskah_draf_v1/README.md).
