# Referensi Penelitian

Folder ini menyimpan referensi untuk draf penelitian di `paper/latex/`. Isinya:

- `pdf/`: salinan PDF referensi yang aksesnya terbuka. Nama berkas mengikuti kunci BibTeX (`<kunci>.pdf`).
- `README.md`: indeks ini.

BibTeX yang dipakai naskah ada di `paper/latex/references.bib` (karya ilmiah) dan `paper/latex/regulasi.bib` (sumber hukum).

## Kriteria seleksi

Setiap referensi karya ilmiah harus memenuhi semua kriteria berikut:

1. **Terbit 2021 atau sesudahnya** (lima tahun terakhir, dihitung dari 2026). Tahun yang dipakai adalah tahun terbit cetak/volume menurut Crossref.
2. **Telah melalui peer review**: artikel jurnal, artikel prosiding konferensi, atau bab dalam seri prosiding (IOS Press FAIA, Springer LNCS). Preprint, tesis, laporan teknis, dan blog tidak dipakai.
3. **DOI terdaftar di Crossref**. Metadata BibTeX dibangkitkan langsung dari Crossref, bukan diketik ulang. Judul yang rusak di Crossref dikoreksi manual (lihat kepala `references.bib`).

Ke-42 referensi lolos ketiga kriteria. Bila PDF yang tersimpan adalah versi penulis (arXiv atau repositori institusi), isinya bisa berbeda tipis dari versi terbit. Kutipan di naskah tetap merujuk ke versi terbit lewat DOI.

## Ringkasan

| | Jumlah |
|---|---|
| Referensi karya ilmiah | 42 |
| Jurnal | 27 |
| Prosiding / seri prosiding | 15 |
| PDF tersimpan | 29 |
| PDF tidak tersimpan | 13 |

## Indeks karya ilmiah

Kolom "Dikutip di": Abs = abstrak, I = Pendahuluan, II = Tinjauan Pustaka, III = Metodologi.

### Rules as Code dan formalisasi hukum

| Kunci | Judul | Wadah | Tahun | Jenis | DOI | Lisensi | PDF | Dikutip di |
|---|---|---|---|---|---|---|---|---|
| `merigoux2021catala` | Catala: a programming language for the law | Proceedings of the ACM on Programming Languages | 2021 | jurnal | [10.1145/3473582](https://doi.org/10.1145/3473582) | CC-BY-4.0 | ada (versi penulis) | I, II |
| `merigoux2021mlang` | A modern compiler for the French tax code | Proceedings of the 30th ACM SIGPLAN International Conference on Compiler Construction | 2021 | prosiding | [10.1145/3446804.3446850](https://doi.org/10.1145/3446804.3446850) | arXiv | ada (versi penulis) | I, II |
| `huttner2022catala` | Catala: Moving towards the future of legal expert systems | Artificial Intelligence and Law | 2022 | jurnal | [10.1007/s10506-022-09328-5](https://doi.org/10.1007/s10506-022-09328-5) | HAL | tidak diunduh | II |
| `monat2024date` | Formalizing Date Arithmetic and Statically Detecting Ambiguities for the Law | Lecture Notes in Computer Science | 2024 | prosiding (seri buku) | [10.1007/978-3-031-57267-8_16](https://doi.org/10.1007/978-3-031-57267-8_16) | CC-BY-4.0 | ada (penerbit) | II |
| `goutagny2025cutecat` | CUTECat: Concolic Execution for Computational Law | Lecture Notes in Computer Science | 2025 | prosiding (seri buku) | [10.1007/978-3-031-91121-7_2](https://doi.org/10.1007/978-3-031-91121-7_2) | CC-BY-4.0 | ada (penerbit) | II |
| `witt2024encoding` | Encoding legislation: a methodology for enhancing technical validation, legal alignment and interdisciplinarity | Artificial Intelligence and Law | 2024 | jurnal | [10.1007/s10506-023-09350-1](https://doi.org/10.1007/s10506-023-09350-1) | CC-BY-4.0 | ada (penerbit) | II |
| `mowbray2023scaling` | Representing legislative Rules as Code: Reducing the problems of ‘scaling up’ | Computer Law & Security Review | 2023 | jurnal | [10.1016/j.clsr.2022.105772](https://doi.org/10.1016/j.clsr.2022.105772) | preprint | ada (versi penulis) | I, II |
| `mowbray2023xai` | Explainable AI (XAI) in Rules as Code (RaC): The DataLex approach | Computer Law & Security Review | 2023 | jurnal | [10.1016/j.clsr.2022.105771](https://doi.org/10.1016/j.clsr.2022.105771) | AM | ada (versi penulis) | II |
| `meessen2023arrows` | On Normative Arrows and Comparing Tax Automation Systems | Proceedings of the Nineteenth International Conference on Artificial Intelligence and Law | 2023 | prosiding | [10.1145/3594536.3595160](https://doi.org/10.1145/3594536.3595160) | CC-BY-NC-4.0 | tidak diunduh | II |
| `kowalski2022logicalenglish` | Logical English meets legal English for swaps and derivatives | Artificial Intelligence and Law | 2022 | jurnal | [10.1007/s10506-021-09295-3](https://doi.org/10.1007/s10506-021-09295-3) | CC-BY-4.0 | ada (penerbit) | I, II |

### KBS untuk pajak dan payroll

| Kunci | Judul | Wadah | Tahun | Jenis | DOI | Lisensi | PDF | Dikutip di |
|---|---|---|---|---|---|---|---|---|
| `dumancic2021payroll` | Automated Reasoning and Learning for Automated Payroll Management | Proceedings of the AAAI Conference on Artificial Intelligence | 2021 | jurnal | [10.1609/aaai.v35i17.17774](https://doi.org/10.1609/aaai.v35i17.17774) | gratis-penerbit | ada (penerbit) | I, II |
| `alhawari2026payroll` | Scrum-guided development of an intelligent payroll management system with rule-based automation and RAG chatbot support | Knowledge-Based Systems | 2026 | jurnal | [10.1016/j.knosys.2026.116301](https://doi.org/10.1016/j.knosys.2026.116301) | - | tidak diunduh | II |
| `makowski2025dmn` | Dynamic generation of Decision Model and Notation rules for tax regulations � case study from Swiss accounting offices | International Conference on Information Systems Development | 2025 | prosiding | [10.62036/isd.2025.98](https://doi.org/10.62036/isd.2025.98) | gratis-penerbit | tidak diunduh | I, II |
| `kusuma2026pph21` | Perancangan Sistem Terintegrasi untuk Otomatisasi Perhitungan PPh Pasal 21 | Jurnal Akuntansi, Perpajakan dan Auditing | 2026 | jurnal | [10.21009/japa.0701.07](https://doi.org/10.21009/japa.0701.07) | CC-BY-NC-SA-4.0 | ada (penerbit) | I, II |
| `sherra2025ter` | The, A Evaluasi Risiko Lebih Bayar PPh 21 Akibat Implementasi Tarif Efektif Rata-Rata (TER) Di CV. X | Jurnal Wahana Akuntansi | 2025 | jurnal | [10.21009/wahana.20.013](https://doi.org/10.21009/wahana.20.013) | CC-BY-NC-SA-4.0 | ada (penerbit) | II |
| `ramadhani2021grossup` | Perancangan Sistem Perhitungan Pajak Penghasilan Berbasis Web dengan Metode Gross Up | remik | 2021 | jurnal | [10.33395/remik.v6i1.11180](https://doi.org/10.33395/remik.v6i1.11180) | CC-BY-SA-4.0 | ada (penerbit) | I, II |
| `yulistyawati2022payroll` | ANALISIS DAN PERANCANGAN SISTEM INFORMASI PENGGAJIAN KARYAWAN SERTA PERHITUNGAN PPH PASAL 21 PADA CV SENI ECHO | Jurnal Teknologi Informasi dan Komputer | 2022 | jurnal | [10.36002/jutik.v8i4.2084](https://doi.org/10.36002/jutik.v8i4.2084) | CC-BY-NC-SA-4.0 | ada (penerbit) | I, II |

### Konflik norma dan penalaran temporal

| Kunci | Judul | Wadah | Tahun | Jenis | DOI | Lisensi | PDF | Dikutip di |
|---|---|---|---|---|---|---|---|---|
| `robaldo2024compliance` | Compliance checking on first-order knowledge with conflicting and compensatory norms: a comparison among currently available technologies | Artificial Intelligence and Law | 2024 | jurnal | [10.1007/s10506-023-09360-z](https://doi.org/10.1007/s10506-023-09360-z) | CC-BY-4.0 | ada (penerbit) | II |
| `moguillansky2024temporalised` | An approach to temporalised legal revision through addition of literals | Artificial Intelligence and Law | 2024 | jurnal | [10.1007/s10506-023-09363-w](https://doi.org/10.1007/s10506-023-09363-w) | CC-BY-NC-SA | tidak diunduh | II |
| `demartim2025satgraph` | An Ontology-Driven Graph RAG for Legal Norms: A Hierarchical, Temporal, and Deterministic Approach | Frontiers in Artificial Intelligence and Applications | 2025 | prosiding (seri buku) | [10.3233/FAIA251598](https://doi.org/10.3233/FAIA251598) | CC-BY | ada (versi penulis) | II |
| `kharraz2024conflicts` | On Conflicts and Satisfiability in Metric Timed Normative Logics | Frontiers in Artificial Intelligence and Applications | 2024 | prosiding (seri buku) | [10.3233/FAIA241260](https://doi.org/10.3233/FAIA241260) | CC-BY-NC-4.0 | tidak diunduh | II |
| `olivieri2025revising` | Revising non-monotonic theories with sufficient and necessary conditions: the case of Defeasible Logic | Journal of Logic and Computation | 2025 | jurnal | [10.1093/logcom/exae044](https://doi.org/10.1093/logcom/exae044) | CC-BY-4.0 | tidak diunduh | II |
| `fungwacharakorn2021debugging` | Resolving counterintuitive consequences in law using legal debugging | Artificial Intelligence and Law | 2021 | jurnal | [10.1007/s10506-021-09283-7](https://doi.org/10.1007/s10506-021-09283-7) | baca-gratis | tidak diunduh | II |
| `khoja2026consistency` | Automated consistency analysis for legal contracts | Artificial Intelligence and Law | 2026 | jurnal | [10.1007/s10506-025-09456-8](https://doi.org/10.1007/s10506-025-09456-8) | CC-BY-4.0 | ada (penerbit) | II |
| `boujelben2025anomalies` | Treating Anomalies in Rule bases associated to Ontologies | The Journal of Supercomputing | 2025 | jurnal | [10.1007/s11227-024-06688-4](https://doi.org/10.1007/s11227-024-06688-4) | - | tidak diunduh | II |

### Pengujian perangkat lunak pajak

| Kunci | Judul | Wadah | Tahun | Jenis | DOI | Lisensi | PDF | Dikutip di |
|---|---|---|---|---|---|---|---|---|
| `tizpaz2023metamorphic` | Metamorphic Testing and Debugging of Tax Preparation Software | 2023 IEEE/ACM 45th International Conference on Software Engineering: Software Engineering in Society (ICSE-SEIS) | 2023 | prosiding | [10.1109/ICSE-SEIS58686.2023.00019](https://doi.org/10.1109/ICSE-SEIS58686.2023.00019) | arXiv | ada (versi penulis) | I, II, III |
| `khiabani2026agentic` | An LLM Agentic Approach for Legal-Critical Software: A Case Study for Tax Prep Software | Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering | 2026 | prosiding | [10.1145/3744916.3764575](https://doi.org/10.1145/3744916.3764575) | CC-BY-4.0 | ada (versi penulis) | I, II |
| `srinivas2023fewshot` | On the Potential and Limitations of Few-Shot In-Context Learning to Generate Metamorphic Specifications for Tax Preparation Software | Proceedings of the Natural Legal Language Processing Workshop 2023 | 2023 | prosiding | [10.18653/v1/2023.nllp-1.23](https://doi.org/10.18653/v1/2023.nllp-1.23) | CC-BY-4.0 | ada (penerbit) | II |
| `li2025mrgeneration` | Metamorphic Relation Generation: State of the Art and Research Directions | ACM Transactions on Software Engineering and Methodology | 2025 | jurnal | [10.1145/3708521](https://doi.org/10.1145/3708521) | - | tidak diunduh | II, III |
| `goldstein2024pbt` | Property-Based Testing in Practice | Proceedings of the IEEE/ACM 46th International Conference on Software Engineering | 2024 | prosiding | [10.1145/3597503.3639581](https://doi.org/10.1145/3597503.3639581) | CC-BY-NC-4.0 | tidak diunduh | II, III |
| `ravi2025pbtpython` | An Empirical Evaluation of Property-Based Testing in Python | Proceedings of the ACM on Programming Languages | 2025 | jurnal | [10.1145/3764068](https://doi.org/10.1145/3764068) | CC-BY | tidak diunduh | II, III |
| `petrovic2022mutation` | Practical Mutation Testing at Scale: A view from Google | IEEE Transactions on Software Engineering | 2022 | jurnal | [10.1109/TSE.2021.3107634](https://doi.org/10.1109/TSE.2021.3107634) | CC-BY-4.0 | ada (penerbit) | II, III |
| `petrovic2021mutation` | Does Mutation Testing Improve Testing Practices? | 2021 IEEE/ACM 43rd International Conference on Software Engineering (ICSE) | 2021 | prosiding | [10.1109/ICSE43902.2021.00087](https://doi.org/10.1109/ICSE43902.2021.00087) | arXiv | ada (versi penulis) | II, III |

### LLM, penjelasan, dan pengawasan manusia

| Kunci | Judul | Wadah | Tahun | Jenis | DOI | Lisensi | PDF | Dikutip di |
|---|---|---|---|---|---|---|---|---|
| `blairstanek2023gpt3` | Can GPT-3 Perform Statutory Reasoning? | Proceedings of the Nineteenth International Conference on Artificial Intelligence and Law | 2023 | prosiding | [10.1145/3594536.3595163](https://doi.org/10.1145/3594536.3595163) | arXiv | ada (versi penulis) | I, II |
| `nay2024taxattorneys` | Large language models as tax attorneys: a case study in legal capabilities emergence | Philosophical Transactions of the Royal Society A: Mathematical, Physical and Engineering Sciences | 2024 | jurnal | [10.1098/rsta.2023.0159](https://doi.org/10.1098/rsta.2023.0159) | CC-BY-4.0 | ada (versi penulis) | I, II |
| `dahl2024legalfictions` | Large Legal Fictions: Profiling Legal Hallucinations in Large Language Models | Journal of Legal Analysis | 2024 | jurnal | [10.1093/jla/laae003](https://doi.org/10.1093/jla/laae003) | CC-BY-NC-4.0 | ada (versi penulis) | I, II |
| `magesh2025hallucination` | Hallucination‐Free? Assessing the Reliability of Leading
                    <scp>AI</scp>
                    Legal Research Tools | Journal of Empirical Legal Studies | 2025 | jurnal | [10.1111/jels.12413](https://doi.org/10.1111/jels.12413) | CC-BY-NC-4.0 | ada (versi penulis) | II |
| `janatian2023texttostructure` | From Text to Structure: Using Large Language Models to Support the Development of Legal Expert Systems | Frontiers in Artificial Intelligence and Applications | 2023 | prosiding (seri buku) | [10.3233/FAIA230962](https://doi.org/10.3233/FAIA230962) | CC-BY-NC-4.0 | ada (penerbit) | II |
| `zuurmond2023explanation` | Human-Centred Explanation of Rule-Based Decision-Making Systems in the Legal Domain: Demonstration | Frontiers in Artificial Intelligence and Applications | 2023 | prosiding (seri buku) | [10.3233/FAIA230992](https://doi.org/10.3233/FAIA230992) | CC-BY-NC-4.0 | ada (versi penulis) | II |
| `gorski2025xaitax` | Exploring explainable AI in the tax domain | Artificial Intelligence and Law | 2025 | jurnal | [10.1007/s10506-024-09395-w](https://doi.org/10.1007/s10506-024-09395-w) | CC-BY-4.0 | ada (penerbit) | II |
| `enqvist2023oversight` | ‘Human oversight’ in the EU artificial intelligence act: what, when and by whom? | Law, Innovation and Technology | 2023 | jurnal | [10.1080/17579961.2023.2245683](https://doi.org/10.1080/17579961.2023.2245683) | CC-BY-4.0 | tidak diunduh | II |
| `green2022oversight` | The flaws of policies requiring human oversight of government algorithms | Computer Law & Security Review | 2022 | jurnal | [10.1016/j.clsr.2022.105681](https://doi.org/10.1016/j.clsr.2022.105681) | CC-BY-4.0 | ada (versi penulis) | II |

## PDF yang tidak tersimpan

- `alhawari2026payroll`: akses tertutup (tidak ada versi akses terbuka yang ditemukan)
- `makowski2025dmn`: penerbit menolak unduhan otomatis; unduh manual dari <https://aisel.aisnet.org/cgi/viewcontent.cgi?article=1687&context=isd2014>
- `moguillansky2024temporalised`: akses tertutup (tidak ada versi akses terbuka yang ditemukan)
- `kharraz2024conflicts`: penerbit menolak unduhan otomatis; unduh manual dari <https://ebooks.iospress.nl/pdf/doi/10.3233/FAIA241260>
- `olivieri2025revising`: penerbit menolak unduhan otomatis; unduh manual dari <https://academic.oup.com/logcom/article-pdf/35/7/exae044/59029380/exae044.pdf>
- `fungwacharakorn2021debugging`: penerbit menolak unduhan otomatis; unduh manual dari <https://link.springer.com/content/pdf/10.1007/s10506-021-09283-7.pdf>
- `boujelben2025anomalies`: akses tertutup (tidak ada versi akses terbuka yang ditemukan)
- `enqvist2023oversight`: penerbit menolak unduhan otomatis; unduh manual dari <https://www.tandfonline.com/doi/pdf/10.1080/17579961.2023.2245683>
- `huttner2022catala`: penerbit menolak unduhan otomatis; unduh manual dari <https://inria.hal.science/hal-02936606/document>
- `meessen2023arrows`: penerbit menolak unduhan otomatis; unduh manual dari <https://dl.acm.org/doi/pdf/10.1145/3594536.3595160>
- `li2025mrgeneration`: akses tertutup (tidak ada versi akses terbuka yang ditemukan)
- `goldstein2024pbt`: penerbit menolak unduhan otomatis; unduh manual dari <https://dl.acm.org/doi/pdf/10.1145/3597503.3639581>
- `ravi2025pbtpython`: penerbit menolak unduhan otomatis; unduh manual dari <https://dl.acm.org/doi/pdf/10.1145/3764068>

## Sumber hukum (pengecualian)

Peraturan perundang-undangan dikutip sebagai **sumber primer domain**, bukan karya ilmiah, sehingga tidak tunduk pada kriteria lima tahun dan peer review. Dua di antaranya terbit sebelum 2021 tetapi tetap diperlukan: PER-16/PJ/2016 adalah dasar pemotongan tahun pajak 2023, dan besaran PTKP dalam PMK 101/PMK.010/2016 masih berlaku. Entri ada di `paper/latex/regulasi.bib`. PDF-nya sudah tersimpan di `dataset/01_regulasi/` beserta *checksum*-nya, sehingga tidak disalin ulang ke folder ini.

## Catatan lisensi

PDF di `pdf/` berasal dari penerbit (lisensi CC atau baca-gratis) dan versi penulis di arXiv/repositori. Tidak semua lisensinya mengizinkan redistribusi, misalnya akses "baca-gratis" atau naskah tanpa lisensi terbuka. Karena repositori ini publik, `pdf/` sebaiknya tidak di-*commit*. Simpan folder itu secara lokal dan andalkan DOI untuk rujukan.
