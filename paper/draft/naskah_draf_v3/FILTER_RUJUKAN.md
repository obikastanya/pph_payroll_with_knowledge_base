# Filter rujukan naskah draf v3 (27 Oktober 2026)

## Kriteria

Kriteria diambil dari [`../../reference/README.md`](../../reference/README.md). Sebuah rujukan karya ilmiah lolos bila memenuhi ketiganya:

1. Terbit 2021 atau sesudahnya.
2. Melalui *peer review* sebagai artikel jurnal atau artikel prosiding. *Preprint*, buku, tesis, laporan teknis, situs web, dan presentasi tanpa prosiding tidak dipakai.
3. DOI terdaftar di Crossref. DOI arXiv (DataCite) tidak dihitung.

Pengecualian: standar dicatat sebagai sumber primer, seperti regulasi (PANDUAN Tahap 1).

Draf v3 memakai filter yang sama dengan v2, ditambah tiga pengecualian yang disetujui pengguna pada 27 Oktober 2026. Filter hanya diterapkan pada 43 rujukan baru dari draf v1. Ke-42 rujukan lama di `paper/latex/references.bib` sudah dinyatakan lolos kriteria yang sama oleh sesi sebelumnya dan tidak diperiksa ulang.

## Ringkasan

| Status | Jumlah |
|---|---|
| Lolos | 10 |
| Standar, dipertahankan sebagai sumber primer | 5 |
| Pengecualian yang disetujui (tidak memenuhi kriteria, tetap dikutip) | 3 |
| Gugur | 24 |
| Standar yang tidak dipakai, dibuang | 1 |
| Pengganti baru yang lolos (Varshney dkk. 2022, menggantikan Geifman dan El-Yaniv 2017) | 1 |

Daftar pustaka v3 berisi 60 entri (v1: 78, v2: 57).

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
| goganikhiabani2025maintaining | Pemeliharaan perangkat lunak pajak dengan LLM, arXiv / IRS-TPC | **Pengecualian** | (2), (3): arXiv, status *review* konferensi tidak terverifikasi | Tetap dikutip di Bab I, Bab III, dan Tabel III sebagai gagasan terdekat |
| han2026autoformalization | Law&Order | Gugur | (2), (3): *preprint* | Kalimat di Bab III dan baris Tabel III dihapus |
| graus2026executable | ICAIL 2026 | Gugur sementara | (3): DOI ACM belum terbit | Kalimat di Bab III dan baris Tabel III dihapus |
| prior2026asking | ICAIL 2026 | Gugur sementara | (3): DOI ACM belum terbit | Kalimat di Bab I dan III dihapus |
| huang2026wrong | TALD-Bench | Gugur | (2), (3): *preprint* | Dihapus bersama kalimatnya |
| cymbler2026temporal | FiscalQA Pro, lokakarya ICML | Gugur | (2), (3): status arsip tidak jelas, tanpa DOI Crossref | Dihapus bersama kalimatnya |
| rodrigues2026retrieving | Poster lokakarya NeurIPS | Gugur | (2), (3) | Kalimat di Bab III dihapus |
| liu2024codeupdatearena | CodeUpdateArena | Gugur | (2), (3): *preprint* | Diganti ReCode |
| chen2021evaluating | Codex, *pass@k* | **Pengecualian** | (2), (3): *preprint* | Tetap dikutip untuk *pass@k* (Bab III, VI) dan rumus penaksirnya (Tabel XI) |
| compton1990philosophical | *Ripple-Down Rules* | Gugur | (1): 1990 | Sitasi dilepas; nama metode tetap |
| compton2021rippledown | Buku *Ripple-Down Rules* | **Pengecualian** | (2): buku | Tetap dikutip untuk *Ripple-Down Rules* dan *cornerstone case* (Bab I, III, V) |
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

## Pengecualian di v3

Tiga pengecualian berikut disetujui pengguna pada 27 Oktober 2026 dan dipakai di v3:

1. **goganikhiabani2025maintaining.** Gagasan yang paling dekat dengan *novelty*. Karya ini dikutip agar pembeda penelitian ini tertulis eksplisit.
2. **compton2021rippledown.** Sumber baku *Ripple-Down Rules* dan *cornerstone case*. Terbit 2021 dan ber-DOI Crossref, tetapi berupa buku.
3. **chen2021evaluating.** Sumber rumus penaksir *pass@k* di Tabel XI.

Yang masih dapat dipertimbangkan kemudian:

- **graus2026executable, prior2026asking.** Keduanya lolos otomatis begitu prosiding ICAIL 2026 mendapat DOI ACM.
- **Sumber metode klasik**, yaitu Clopper–Pearson, Newcombe, Holm, Cohen, Hayes–Krippendorff, Hevner dkk. (DSR), dan Tarski. Di v3 metode-metode ini masih disebut namanya tanpa sitasi.

Entri yang ingin dipulihkan tinggal disalin dari `../naskah_draf_v1/rujukan_tambahan.bib`. Jangan menulis tanda `@` di baris komentar berkas `.bib`, karena BibTeX membacanya sebagai awal entri.
