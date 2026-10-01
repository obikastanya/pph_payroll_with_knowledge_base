# dataset/ — Manifest Induk

Rincian dan status setiap aset ada di `research_plan.md` §8. Setiap subfolder memiliki README sendiri.

| Folder | Isi singkat | README |
|---|---|---|
| `01_regulasi/` | 33 PDF regulasi resmi (pajak, DTP, BPJS) + OCR PER-16 + `tables/` (TER, PTKP, Pasal 17, biaya jabatan, BPJS berversi, pembulatan) | [01_regulasi/README.md](01_regulasi/README.md) |
| `02_studi_kasus/` | Studi kasus Perusahaan X (dari xlsx, teranonimkan) | [02_studi_kasus/README.md](02_studi_kasus/README.md) |
| `03_pembanding/` | 7 repo OSS PPh 21 + survei mesin rules-as-code + 22 kalkulator online; semuanya **bukan oracle** | [03_pembanding/README.md](03_pembanding/README.md) |
| `04_data_publik/` | BPS (upah, status kawin, rumah tangga), Kemnaker UMP 2018–2026, sekunder | [04_data_publik/README.md](04_data_publik/README.md) |
| `05_katalog_kebijakan/` | 20 variasi kebijakan penggajian untuk uji ekspresivitas | `katalog_kebijakan.yaml` |
| `06_kasus_uji_sintetis/` | Pembangkit kasus (strata S1–S6) + 2.600 profil awal | `bangkitkan_kasus.py` (docstring) |
| `07_kasus_uji_resmi/` | **Gold standard**: 46 contoh resmi dalam lingkup (PMK 168, PP 58, PER-16, PMK DTP), diverifikasi dua pass | [07_kasus_uji_resmi/README.md](07_kasus_uji_resmi/README.md) |

Aturan pakai:
1. Hanya `07_kasus_uji_resmi/` (dengan protokol erratum) dan teks regulasi yang menjadi acuan kebenaran.
2. `03_pembanding/repos/pajakin` tidak berlisensi, sehingga dilarang didistribusikan ulang.
3. `payroll_calculator.xlsx` di root proyek memuat data pribadi, sehingga dilarang dipublikasikan.
