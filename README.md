# KB PPh 21 — Kalkulator PPh Pasal 21 Berbasis Knowledge Base Dua Lapis

Kalkulator PPh 21 pegawai tetap (tahun pajak 2016–2026: rezim disetahunkan PER-16 dan rezim TER PMK 168/2023 + DTP 2025–2026).

- Seluruh pengetahuan pajak ada di **knowledge base** YAML/CSV. Kodenya hanya **mesin inferensi** generik.
- Kebijakan perusahaan ditaruh di **lapisan terpisah**. Konflik dengan aturan wajib terdeteksi otomatis (*lex superior*).
- Rancangan riset: [research_plan.md](research_plan.md).

## Menjalankan

```bash
env\Scripts\python.exe -m engine.cli dataset\07_kasus_uji_resmi\kanonik\PMK168-B-I.1.json --jejak
env\Scripts\python.exe -m engine.cli kasus.json --perusahaan kb\perusahaan\perusahaan_x.yaml --rentang
env\Scripts\python.exe -m engine.cli kasus.json --varian REG-BJ-02=b --json > hasil.json
```

```python
from engine.kalkulator import hitung
h = hitung(kasus)                                    # KB terbaru, varian tafsir default
h = hitung(kasus, dengan_rentang=True)               # + rentang tafsir (AMBIGU_TAFSIR)
h = hitung(kasus, berkas_perusahaan=["kb/perusahaan/perusahaan_x.yaml"])
h = hitung(kasus, per_tanggal_kb=date(2025, 1, 31))  # KB sebagaimana diketahui pada tanggal itu (bitemporal)
```

Keluaran (`dict`):
- `per_masa` dan `tahunan`: semua nilai uang berupa `int` rupiah; tarif berupa string pecahan, mis. `"3/200"`.
- `jejak`: aturan, pasal sumber, dan aturan yang ditolak beserta alasannya.
- `peringatan`: `KONFLIK_WAJIB`, `GROSSUP_GANDA`, `AMBIGU_TAFSIR`, `KLASIFIKASI_TIDAK_DIATUR`, `TRANSAKSI_TAHUN_LAIN`.
- `rentang_tafsir` (opsional).

### Format input (kasus kanonik)

Contoh lengkap ada di `dataset/07_kasus_uji_resmi/kanonik/*.json`. Ringkasnya:

```json
{"id": "...", "tahun_pajak": 2024, "cakupan": "setahun", "metode": "gross|gross_up|ditanggung_pemberi_kerja",
 "pegawai": {"status_ptkp": "K/1", "jenis_kelamin": "L", "punya_npwp": true, "bulan_masuk": null,
             "bulan_terakhir_bekerja": null, "subjektif_mulai_bulan": null, "subjektif_akhir_bulan": null,
             "periode_gaji": "bulanan", "hari_kerja_sebulan": null},
 "pemberi_kerja": {"klu": "13111", "jenis": "biasa"}, "kurs": {}, "dtp": {},
 "masa": [{"bulan": 1, "komponen": [{"kode": "gaji", "kategori": "teratur", "satuan_periode": "bulan", "nominal": 10000000}]}],
 "transaksi": [{"komponen": "thr", "kategori": "tidak_teratur", "nominal": 10000000, "periode_kerja": "2024-04",
                "tanggal_terutang": "2024-04-10", "tanggal_bayar": "2024-03-28"}],
 "data_hr": {"...": "input mentah untuk lapisan perusahaan"}}
```

- Kategori komponen: `teratur`, `tidak_teratur`, `premi_objek`, `natura`, `iuran_pengurang`, `zakat`, `rapel`.
- Nominal wajib `int ≥ 0`. Float dan pecahan **ditolak** (`InputTidakValid`).

## Struktur

| Folder | Isi |
|---|---|
| `engine/` | `ekspresi.py` (DSL aman), `kb.py` (pemuat + verifikasi statis), `inferensi.py` (graf, SCC, titik tetap Tarski, resolusi konflik, bitemporal), `kalkulator.py`, `cli.py`, kontrak presisi (`angka.py`, `pembulatan.py`, `interval.py`, `waktu.py`, `muat.py`, `audit.py`) |
| `kb/regulasi/` | `aturan_{umum,ter,per16,dtp}.yaml`, `klasifikasi.yaml`, `parameter.yaml`, `pembulatan.yaml`, `pencatatan.yaml`, `tabel_manifest.yaml` (hash SHA-256), `KODIFIKASI.md` |
| `kb/perusahaan/` | `perusahaan_x.yaml` (studi kasus), `katalog/` (kebijakan KP-xx) |
| `baselines/b1_hardcoded/` | Baseline B1 hard-coded independen (tag git `b1-frozen`) |
| `dataset/` | Regulasi (PDF + tabel double-entry), kasus resmi kanonik, pembanding, data publik, sintetis |
| `eksperimen/` | `v1.py`, `v2.py`, `ablasi.py`, `mutasi.py`, `grossup.py`, `konflik.py`, `perubahan.py`, `ekspresivitas.py`, `e8_perusahaan_x.py`, `adjudikasi.md` |
| `tests/` | ±200 tes: kontrak presisi, V1, V2, V3 metamorfik, double-entry, E3–E8 |

```bash
env\Scripts\python.exe -m pytest              # seluruh tes (±3 menit)
env\Scripts\python.exe -m eksperimen.v1 kb    # kasus resmi
env\Scripts\python.exe -m eksperimen.mutasi   # mutation testing (±15 menit)
```

## Status verifikasi (2026-10-01)

| Uji | Hasil |
|---|---|
| V1: 45 kasus resmi kanonik, 1.213 harapan (PMK 168, PP 58, PER-16, PMK 10/72/105) | **0 selisih tak terjelaskan** (1.185 cocok, 20 erratum terkoreksi, 8 tafsir); KB dan B1 identik |
| V2: differential KB vs B1, 2.201 kasus sintetis | 0 galat; seluruh selisih teradjudikasi (titik tetap gross-up ganda, `eksperimen/adjudikasi.md`) |
| V3: relasi metamorfik MR1–MR15 + properti DTP dan PPh ditanggung | lulus (Hypothesis) |
| Double-entry tabel dari gambar halaman PDF | 512 sel cocok 100%; dijalankan permanen sebagai tes |
| E4 mutation testing (52 mutan KB) | skor 100% (1 sisa mutan diubah menjadi tafsir eksplisit R16-05-N) |
| E4b deteksi konflik kebijakan (42 pemetaan berlabel) | presisi = recall = F1 = 1,0 |
| E5 ablasi | setiap fitur yang dimatikan menghasilkan contoh tandingan |
| E3 perubahan aturan (JP 2026, DTP surut, PTKP 2027, TER 2027) | 0 berkas engine berubah; impact F1 = 1,0; regresi 0 |
| E7 ekspresivitas | 17/19 entri katalog tanpa ubah kode |
| E8 Perusahaan X vs xlsx | 12 komponen payroll identik; selisih PPh hanya di temuan audit K-02/K-04/K-11 |
| E9 kinerja | ±38 ms per pegawai-tahun (gross-up dominan); ±8 ms dengan lapisan perusahaan |

## Batasan yang diketahui

- **Default tafsir belum dikalibrasi ke kalkulator resmi DJP (E10, manual).** Ini mencakup pembulatan TER × bruto, bruto pecahan, biaya jabatan, proporsi n/12, PPh bulanan PER-16, pilihan titik tetap, dan R16-05-N. Rentang tafsir selalu dapat ditampilkan (`--rentang`).
- **Di luar model:** gross-up rezim PER-16, pindah cabang multi-pemotong, penghasilan dari lebih dari satu pemberi kerja, pegawai tidak tetap/bukan pegawai/pensiunan, penilaian natura PMK 66 (nilai diinput), dan gross-up per komponen (KP-03) serta gross-up berplafon (KP-04).
- **KLU DTP** berasal dari lapisan teks (status `ekstraksi_1`); kode 96129 hanya ada di PMK 105 dan perlu dicek ke gambar halaman.
- `payroll_calculator.xlsx` memuat data pribadi, sehingga diabaikan git dan **tidak boleh dipublikasikan**.
