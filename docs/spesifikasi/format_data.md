# Format data dan kontrak antarmuka

Tahap 4 [PANDUAN_PENELITIAN.md](../../PANDUAN_PENELITIAN.md). Versi 2, 2026-10-27 (revisi atas tinjauan independen). Skema JSON yang mengikat ada di `system/schemas/`; dokumen ini menjelaskan isinya. Semua bagian sistem (alur akuisisi, emas, pembanding, skrip penilaian, aplikasi) memakai format yang sama.

## 1. Lokasi

| Isi | Lokasi |
|---|---|
| Skema JSON | `system/schemas/{delta,delta_llm,case,expected,llm_call,pipeline_result}.schema.json` |
| Ontologi dan *shape* SHACL | `system/kb/ontology.ttl`, `system/kb/shapes.ttl` |
| Kueri SPARQL bersama | `system/kb/queries/*.rq` |
| Rantai emas ($\Delta$ latar dan $\Delta^\star$) | `dataset/12_emas/delta/*.json`, urutan di `dataset/12_emas/rantai.csv` |
| Teks dokumen terkunci, segmen, tabel terekstraksi | `dataset/13_teks/<dokumen>/{teks.txt, segmen.json, tabel/*.csv, MANIFEST.sha256}` |
| Ruang uji $S^E$ dan nilai harapan | `dataset/14_ruang_uji/` (kasus JSONL, nilai harapan JSONL per peristiwa) |
| Log panggilan LLM dan hasil alur | `system/runs/<jalan>/{calls.jsonl, prompts/, results/}` |

## 2. Pembaruan $\Delta$

```json
{
  "delta_id": "GOLD-E06",
  "event_id": "E06",
  "document": {"id": "PMK-10-2025", "title": "...", "issued": "2025-02-04"},
  "relevant": true,
  "add":    [ <unsur>, ... ],
  "change": [ <unsur>, ... ],
  "remove": [ {"id": "REG.X", "recorded_on": "2025-02-04", "source": [<sumber>]} ],
  "adopts": [],
  "note": "teks bebas"
}
```

`adopts` hanya untuk dokumen kebijakan: `id` aturan regulasi `optional` yang diadopsi kebijakan itu.

**Unsur** (`kind` menentukan atribut wajib):

| `kind` | Atribut wajib | Atribut opsional |
|---|---|---|
| `rule` | `id`, `layer` (`regulation`/`company`), `modality` (`mandatory`/`default`/`optional`), `scope` (`period`/`year`), `produces`, `expression`, `valid_from`, `recorded_on`, `source`; aturan perusahaan juga `policy` | `condition`, `valid_until`, `overrides` (daftar id), `fixed_point` (`{lower, upper}`), `conflict_code` (anotasi aturan perusahaan, `C1`–`C10`), `label` |
| `parameter` | `id`, `name`, `value`, `value_type` (`money`/`exact`/`rate`/`int`/`bool`/`category`), `valid_from`, `recorded_on`, `source` | `valid_until`, `label` |
| `table` | `id`, `name`, `table_kind` (`lookup`/`bracket`/`progressive`/`set`), `valid_from`, `recorded_on`, `source`, dan salah satu: `rows` atau `rows_ref` | `valid_until`, `label` |
| `constraint` | `id`, `scope`, `assertion`, `conflict_code`, `valid_from`, `recorded_on`, `source` | `condition`, `valid_until`, `label` |
| `fact` | `id` (= nama fakta), `fact_type` (tipe representasi.md 6.2), `fact_scope` (`period`/`year`), `recorded_on`, `source` | `output` (bool, termasuk $F_\mathit{nilai}$; hanya bermakna di pembaruan latar kosakata), `label`, `label_id` (label Indonesia untuk leksikon pemilihan segmen), `unit` |

`value` untuk `exact`/`rate` ditulis sebagai teks desimal (`"0.0024"`), untuk `money`/`int` sebagai bilangan bulat. Baris tabel: `lookup` `{key, value}`; `bracket` `{key, lower, upper, value}` (`upper` = `null` untuk lapisan terakhir, `value` teks desimal); `progressive` `{lower, upper, rate}`; `set` `{key, ...atribut}`. `rows_ref` = `{"extracted_table": "PP58-2023/LAMPIRAN-A", "columns": {"key": "kategori", "lower": "batas_bawah", "upper": "batas_atas", "value": "tarif"}, "value_scale": "percent"}`.

**Konvensi id dan tanggal**: aturan `REG.`/`PRS.` sesuai lapisan, parameter `PAR.`, tabel `TAB.`, batasan `CON.`, fakta huruf kecil; `valid_from` tanggal 1 bulan, `valid_until` hari terakhir bulan (representasi.md bagian 3). `rows_ref.filter` memilih baris tabel terekstraksi yang kolomnya sama dengan nilai yang diberikan (misalnya `{"kategori": "A"}`); `value_scale` = `percent` membagi nilai dengan 100.

**Sumber** = `{"document": id, "provision": "Pasal 4 ayat (2) huruf b", "page": 5, "quote": "..."}`; `page` opsional.

Identitas dokumen: `<JENIS>-<NOMOR>-<TAHUN>` dengan tanda baca dihapus, misalnya `PMK-168-2023`, `PER-11-PJ-2025`, `PP-58-2023`, `BPJSTK-B1387-2024`, `PKB-WIKA-2025`. Konvensi masukan kasus memakai dokumen `INPUT-CONVENTION` (bukan dokumen hukum).

### 2.3 Skema keluaran LLM

Keluaran terstruktur model wajib mengikuti `system/schemas/delta_llm.schema.json`: setiap objek `additionalProperties: false`, semua atribut wajib tetapi boleh `null`, nilai parameter dan batas tabel ditulis sebagai teks, kamus diganti daftar pasangan `{name, value}`, dan `fixed_point` dipecah menjadi `fixed_point_lower`/`fixed_point_upper`. Bentuk ini mengikuti batasan keluaran terstruktur (tanpa `minLength`, `if/then`, kamus terbuka). Pengonversi deterministik (`system/pph21kbs/pipeline/convert.py`) membuang `null`, mengembalikan tipe nilai menurut `value_type`, mengisi `policy` = id dokumen untuk aturan perusahaan tanpa `policy`, lalu memvalidasi hasilnya dengan `delta.schema.json`.

## 3. Kasus

```json
{
  "case_id": "SE-E06-000123",
  "tax_year": 2025,
  "employee": {"ptkp_status": "K/1", "sex": "M", "husband_no_income_certified": false,
               "tax_id_valid": true, "subjective_start_month": null, "subjective_end_month": null},
  "employer": {"klu": "13111", "jkk_risk_group": "low", "jkk_relief_eligible": true, "policy": null},
  "method": "gross",
  "employment": {"start_month": 1, "end_month": 12},
  "periods": [
    {"month": 1,
     "income": {"base_salary": 8000000, "fixed_allowance": 500000, "overtime_pay": 0,
                "thr": 0, "bonus": 0},
     "benefits": {"housing_individual": 2500000},
     "zakat": 0,
     "hr": {}}
  ]
}
```

- `employee` dan `employer` terbuka: atribut tambahan boleh ditambahkan dan dibaca aturan lewat `employee(...)`/`employer(...)`.
- `employer.policy`: id kebijakan perusahaan (misalnya `PKB-WIKA-2025`) atau daftar id (PKB + peraturan perusahaan + adendum) yang lapisannya dipasang saat kasus dihitung; `null` = tanpa lapisan perusahaan.
- `jkk_risk_group`: nilai yang dikenal KB emas `very_low`, `low`, `medium`, `high`, `very_high` (PP 44/2015 Lampiran I); skema tidak membatasi nilai, supaya perubahan tak terlihat dapat menambah kelompok tanpa mengubah skema.
- `method`: nilai yang dikenal KB emas `gross`, `gross_up`, `employer_borne`; masuk KB lewat fakta `withholding_method` (konvensi masukan) yang dapat diganti kebijakan.
- `ptkp_status`: pola `TK/n` atau `K/n`.
- Masa kerja untuk hak ketenagakerjaan (THR, pesangon) diberikan sebagai `hr.service_months` per masa.
- `periods` hanya untuk bulan bekerja (`start_month`..`end_month`).
- `income`, `benefits`, `hr` terbuka: nama komponen baru tidak membutuhkan perubahan *engine*.

## 4. Nilai harapan dan tupel evaluasi

Satu baris JSONL per tupel (kasus, ω):

```json
{"tuple_id": "SE-E06-000123@2025-02-04", "case_id": "SE-E06-000123", "omega": "2025-02-04",
 "kb": "GOLD@E06",
 "periods": {"1": {"pph21_due": 263501, "pph21_dtp": 263501, "gross_income": 10541000, "...": 0}},
 "year": {"annual_pph21": 3161000, "...": 0},
 "conflicts": [{"source": "PRS.WIKA.DTP", "target": "REG.DTP.CASH", "fact": "dtp_paid_to_employee", "month": 1, "code": "C4"}],
 "errors": []}
```

`kb` menyebut versi KB yang menghasilkan nilai (`GOLD@<event>` untuk $\mathcal{K}^\star_n$). Nilai fakta `money` berupa bilangan bulat; `exact`/`rate` berupa teks pecahan (`"263501/1"`).

## 5. Tabel peristiwa

Sumber tetap `dataset/09_korpus_peristiwa/peristiwa.csv` (kolom dijelaskan di README korpus). Sistem membacanya lewat `system/pph21kbs/corpus.py`, yang memetakan `berkas` ke id dokumen dan `dataset/13_teks/`. Kolom yang dipakai: `id`, `bagian`, `relevan`, `dokumen`, `tanggal_terbit`, `berlaku_mulai`, `berlaku_sampai`, `jenis_perubahan`. Ukuran $|\Delta^\star|$ diisi otomatis dari rantai emas.

## 6. Log panggilan LLM

Satu baris JSONL per panggilan:

```json
{"call_id": "R1-E06-cand3", "run": "E2-main", "time": "2026-11-02T10:11:12+07:00",
 "model_requested": "claude-opus-5-5", "model_reported": "claude-opus-5-5", "provider": "anthropic",
 "effort": "high", "step": "draft|repair|relevance|b2|b5", "document": "PMK-10-2025",
 "event": "E06", "candidate": 3, "order_seed": 20261027,
 "prompt_sha256": "...", "prompt_file": "prompts/<sha>.json",
 "output_raw": "...", "stop_reason": "end_turn",
 "usage": {"input": 1200, "cache_write": 14000, "cache_read": 0, "output": 5400},
 "cost_usd": 0.1652, "batch": true, "seconds": 41.2,
 "gates": {"G1": "pass", "G2": "fail: quote 2 not in document", "G3": null, "G4": null, "G5": null}}
```

## 7. Hasil alur per dokumen

```json
{"run": "E2-main", "event": "E06", "condition": "proposed",
 "relevance": {"relevant": true, "quotes_ok": true},
 "candidates": [{"n": 1, "order": 2, "passed": true, "repaired": false, "gate_log": {}}],
 "groups": [[1, 4], [3]], "selected": 1, "status": "applied|empty|abstain",
 "delta": {...}, "sg_size": 212, "sg_overlap_se": 0, "cost_usd": 0.71}
```

## 8. Fakta keluaran ($F_\mathit{nilai}$, dibekukan)

Daftar fakta, tipe, dan lingkupnya dibuat otomatis dari rekaman `fact` di rantai emas (`dataset/12_emas/kosakata.md`, dihasilkan oleh `system/tools/vocabulary_report.py`). Fakta dengan `output = true` membentuk $F_\mathit{nilai}$ (representasi.md bagian 4).
