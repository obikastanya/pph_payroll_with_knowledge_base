# dataset/ — Manifest Induk

Pemetaan setiap kebutuhan dataset penelitian (D01–D26) ke asal dan statusnya ada di [RENCANA_DATASET.md](RENCANA_DATASET.md). Setiap subfolder memiliki README sendiri.

| Folder | Isi singkat | README |
|---|---|---|
| `01_regulasi/` | 37 PDF regulasi resmi (pajak, DTP, BPJS) + OCR PER-16 + `tables/` (TER, PTKP, Pasal 17, biaya jabatan, BPJS berversi, pembulatan); `pengecoh/` (12 PDF) dan `pengembangan/` (13 PDF) dengan `manifest_tambahan.csv` | [01_regulasi/README.md](01_regulasi/README.md) |
| `02_studi_kasus/` | Studi kasus Perusahaan X (dari xlsx, teranonimkan) | [02_studi_kasus/README.md](02_studi_kasus/README.md) |
| `03_pembanding/` | 7 repo OSS PPh 21 + survei mesin rules-as-code + 22 kalkulator online (GT4, B1); hanya untuk uji diferensial | [03_pembanding/README.md](03_pembanding/README.md) |
| `04_data_publik/` | BPS (upah, status kawin, rumah tangga), Kemnaker UMP 2018–2026, sekunder | [04_data_publik/README.md](04_data_publik/README.md) |
| `05_katalog_kebijakan/` | 20 variasi kebijakan penggajian untuk uji ekspresivitas | `katalog_kebijakan.yaml` |
| `06_kasus_uji_sintetis/` | Pembangkit kasus (strata S1–S8) + 2.600 profil | `bangkitkan_kasus.py` (docstring) |
| `07_kasus_uji_resmi/` | GT1: 46 contoh resmi dalam lingkup (PMK 168, PP 58, PER-16, PMK DTP); 32 pengembangan, 14 *holdout* disegel | [07_kasus_uji_resmi/README.md](07_kasus_uji_resmi/README.md) |
| `08_pegawai_sintetis/` | 8 pegawai sintetis berbasis UMP | [08_pegawai_sintetis/README.md](08_pegawai_sintetis/README.md) |
| `09_korpus_peristiwa/` | Korpus untuk alur akuisisi: 12 peristiwa uji, 21 pengecoh, 13 peristiwa pengembangan, 5 regulasi fiktif; spesifikasi 21 kontrafaktual; *cutoff* model; pantauan peristiwa prospektif | [09_korpus_peristiwa/README.md](09_korpus_peristiwa/README.md) |
| `10_kebijakan_perusahaan/` | 5 PKB nyata untuk uji + 1 untuk pengembangan (salinan lokal, hanya manifes yang di-commit), 201 klausul terekstrak, 14 kebijakan sintetis dengan label konflik dan dampak | `kandidat.csv`, [klausul/README.md](10_kebijakan_perusahaan/klausul/README.md), [sintetis/README.md](10_kebijakan_perusahaan/sintetis/README.md) |
| `11_acuan/` | Acuan kebenaran: GT2 kalkulator DJP, GT3 kasus bertingkat, GT5 contoh kebijakan, uji diferensial GT3, kasus B2 | [11_acuan/README.md](11_acuan/README.md) |

Skrip: [unduh_dataset.py](unduh_dataset.py) mengunduh ulang dokumen tambahan dan menulis manifesnya (URL, tanggal akses, ukuran, SHA-256).

Aturan pakai:
1. Acuan kebenaran: teks regulasi, contoh resmi (`07_kasus_uji_resmi/`, *holdout* hanya untuk E0), kalkulator DJP (GT2), dan acuan di `11_acuan/`. Implementasi pihak ketiga (`03_pembanding/`) hanya untuk uji diferensial.
2. Kasus *holdout* di `07_kasus_uji_resmi/` dan perubahan tak terlihat di `review/unseen_changes/sealed/` tidak dibuka selama sistem dikembangkan.
3. `03_pembanding/repos/pajakin` tidak berlisensi, sehingga dilarang didistribusikan ulang. Salinan PKB di `10_kebijakan_perusahaan/dokumen/` tidak di-commit.
4. `payroll_calculator.xlsx` di root proyek memuat data pribadi, sehingga dilarang dipublikasikan.
