# Filter rujukan naskah draf v2 (27 Oktober 2026)

## Kriteria

Kriteria diambil dari [`../../reference/README.md`](../../reference/README.md). Sebuah rujukan karya ilmiah lolos bila memenuhi ketiganya:

1. Terbit 2021 atau sesudahnya.
2. Melalui *peer review* sebagai artikel jurnal atau artikel prosiding. *Preprint*, buku, tesis, laporan teknis, situs web, dan presentasi tanpa prosiding tidak dipakai.
3. DOI terdaftar di Crossref. DOI arXiv (DataCite) tidak dihitung.

Pengecualian: standar dicatat sebagai sumber primer, seperti regulasi (PANDUAN Tahap 1).

Filter hanya diterapkan pada 43 rujukan baru dari draf v1. Ke-42 rujukan lama di `paper/latex/references.bib` sudah dinyatakan lolos kriteria yang sama oleh sesi sebelumnya dan tidak diperiksa ulang.

## Ringkasan

| Status | Jumlah |
|---|---|
| Lolos | 10 |
| Standar, dipertahankan sebagai sumber primer | 5 |
| Gugur | 27 |
| Standar yang tidak dipakai, dibuang | 1 |
| Pengganti baru yang lolos (Varshney dkk. 2022, menggantikan Geifman dan El-Yaniv 2017) | 1 |

Daftar pustaka v2 berisi 57 entri (v1: 78).

## Rincian

| Kunci | Karya | Status | Alasan gugur | Tindakan di v2 |
|---|---|---|---|---|
| veeramani2026neurosymbolic | NTOL, *Front. AI* 2026 | Lolos | – | Tetap |
| yadamsuren2026formalization | Formalisasi IRC, *AI & Law* 2026 | Lolos | – | Tetap |
| lorenzo2025translating | LLM ke Catala, NLLP 2025 | Lolos | – | Tetap |
| gupta2024forgetting | *Model editing at scale*, Findings ACL 2024 | Lolos | – | Tetap |
| gu2024harms | *Model editing harms*, EMNLP 2024 | Lolos | – | Tetap |
| li2022alphacode | AlphaCode, *Science* 2022 | Lolos | – | Tetap; kini satu-satunya sumber metrik *n@k* dan *pass@k* |
| prior2025risks | Konsolidasi undang-undang, NLLP 2025 | Lolos | – | Tetap; kini juga menopang klaim "LLM kesulitan dengan amandemen" di Bab I |
| seo2025koleg | KoLEG, Findings EMNLP 2025 | Lolos | – | Tetap |
| jurayj2026tax | LLM dan program logika, AAAI-26 | Lolos | – | Tetap |
| wu2026recode | ReCode, AAAI-26 | Lolos | – | Tetap; menggantikan CodeUpdateArena |
| varshney2022selective | Prediksi selektif, Findings ACL 2022 | Lolos (baru) | – | Menggantikan Geifman dan El-Yaniv 2017 |
| publicationsoffice2026eli | ELI | Standar | – | Tetap |
| cox2017owltime | OWL-Time, W3C 2017 | Standar | – | Tetap |
| lebo2013provo | PROV-O, W3C 2013 | Standar | – | Tetap |
| knublauch2017shacl | SHACL, W3C 2017 | Standar | – | Tetap |
| palmirani2021legalruleml | LegalRuleML, OASIS 2021 | Standar | – | Tetap |
| cox2022owltime | OWL-Time, draf 2022 | Dibuang | Tidak dipakai | – |
| goganikhiabani2025maintaining | Pemeliharaan perangkat lunak pajak dengan LLM, arXiv / IRS-TPC | **Gugur** | (2), (3): arXiv, status *review* konferensi tidak terverifikasi | Kalimat di Bab I, paragraf di Bab III, dan baris Tabel III dihapus |
| han2026autoformalization | Law&Order | Gugur | (2), (3): *preprint* | Kalimat di Bab III dan baris Tabel III dihapus |
| graus2026executable | ICAIL 2026 | Gugur sementara | (3): DOI ACM belum terbit | Kalimat di Bab III dan baris Tabel III dihapus |
| prior2026asking | ICAIL 2026 | Gugur sementara | (3): DOI ACM belum terbit | Kalimat di Bab I dan III dihapus |
| huang2026wrong | TALD-Bench | Gugur | (2), (3): *preprint* | Dihapus bersama kalimatnya |
| cymbler2026temporal | FiscalQA Pro, lokakarya ICML | Gugur | (2), (3): status arsip tidak jelas, tanpa DOI Crossref | Dihapus bersama kalimatnya |
| rodrigues2026retrieving | Poster lokakarya NeurIPS | Gugur | (2), (3) | Kalimat di Bab III dihapus |
| liu2024codeupdatearena | CodeUpdateArena | Gugur | (2), (3): *preprint* | Diganti ReCode |
| chen2021evaluating | Codex, *pass@k* | **Gugur** | (2), (3): *preprint* | Dihapus; *pass@k* kini hanya bersumber AlphaCode |
| compton1990philosophical | *Ripple-Down Rules* | Gugur | (1): 1990 | Sitasi dilepas; nama metode tetap |
| compton2021rippledown | Buku *Ripple-Down Rules* | **Gugur** | (2): buku | Sitasi dilepas; nama metode tetap |
| governatori2010changing | Abrogasi dalam *defeasible logic* | Gugur | (1): 2010 | Kalimatnya dihapus |
| geifman2017selective | Prediksi selektif, NeurIPS 2017 | Gugur | (1), (3) | Diganti Varshney dkk. 2022 |
| hevner2004design | *Design science research* | Gugur | (1): 2004 | Sitasi dilepas |
| peffers2007design | *Design science research* | Gugur | (1): 2007 | Sitasi dilepas |
| tarski1955lattice | Teorema titik tetap | Gugur | (1): 1955 | Sitasi dilepas; nama teorema tetap |
| clopper1934confidence | CI Clopper–Pearson | Gugur | (1) | Sitasi dilepas; nama metode tetap |
| newcombe1998improved | CI Newcombe | Gugur | (1) | Sitasi dilepas |
| holm1979simple | Koreksi Holm | Gugur | (1), (3) | Sitasi dilepas |
| hayes2007answering | Krippendorff's α | Gugur | (1) | Sitasi dilepas |
| cohen1960coefficient | Cohen's κ | Gugur | (1) | Sitasi dilepas |
| openfisca2026rules | Situs OpenFisca | Gugur | (2): situs web | Diganti catatan kaki URL |
| estep2024executable | Presentasi ProLaLa 2024 | Gugur | (2), (3) | Tidak dipakai di v1 |
| li2026lexkairos | LexKairos | Gugur | (2), (3) | Tidak dipakai di v1 |
| fan2026time | NLLP 2026, belum terbit | Gugur | (3) | Tidak dipakai di v1 |
| openfisca2026core | Perangkat lunak OpenFisca | Gugur | (2) | Tidak dipakai di v1 |
| shulz2019logiciel | Artikel sosiologi tentang OpenFisca | Gugur | (1) | Tidak dipakai di v1 |

## Pengecualian yang disarankan

Filter ini menurunkan mutu naskah di beberapa tempat. Pertimbangkan pengecualian berikut, diurutkan dari yang paling penting:

1. **goganikhiabani2025maintaining.** Ini gagasan yang paling dekat dengan *novelty* penelitian ini, yaitu LLM yang menerapkan perubahan dari publikasi IRS ke kode pajak versi sebelumnya. Bila tidak dikutip, penelaah dapat menganggap karya terdekat diabaikan. Klaim kebaruan v2 masih benar, karena karya itu tidak mengevaluasi pembaruan berantai, tetapi pembedanya tidak lagi tertulis.
2. **compton2021rippledown.** Ini sumber baku *Ripple-Down Rules* dan *cornerstone case*. Karya ini terbit 2021 dan ber-DOI Crossref, dan gugur hanya karena berupa buku. Tanpanya, RDR disebut tiga kali (Bab I, III, V) tanpa sitasi. Pencarian Crossref tidak menemukan sumber metode RDR berupa jurnal atau prosiding sejak 2021, hanya makalah penerapan.
3. **chen2021evaluating.** Rumus penaksir *pass@k* di Tabel XI berasal dari karya ini. AlphaCode memakai metriknya, tetapi bukan sumber rumusnya.
4. **graus2026executable, prior2026asking.** Keduanya lolos otomatis begitu prosiding ICAIL 2026 mendapat DOI ACM.
5. **Sumber metode klasik**, yaitu Clopper–Pearson, Newcombe, Holm, Cohen, Hayes–Krippendorff, Hevner dkk. (DSR), dan Tarski. Metode-metode ini kini disebut namanya tanpa sitasi. Lazimnya sumber metode tetap dikutip walaupun lama.

Bila pengecualian disetujui, entrinya tinggal disalin dari `../naskah_draf_v1/rujukan_tambahan.bib`.
