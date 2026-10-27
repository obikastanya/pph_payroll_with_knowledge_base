# Tanggapan atas tinjauan spesifikasi Tahap 3–4

Tinjauan: [spesifikasi.review.md](spesifikasi.review.md) (peninjau independen, 41 temuan: 6 blokir, 19 penting, 16 kecil). Semua temuan diterima kecuali yang dicatat "diterima sebagian". Perubahan masuk ke spesifikasi versi 2: [representasi.md](../../docs/spesifikasi/representasi.md), [akuisisi.md](../../docs/spesifikasi/akuisisi.md), [format_data.md](../../docs/spesifikasi/format_data.md), skema di `system/schemas/`, dan *engine* (Tahap 5).

| No | Tingkat | Tanggapan | Lokasi perubahan |
|---|---|---|---|
| 1 | blokir | Aturan perusahaan diberi `policy`; hanya kebijakan yang disebut kasus yang dipasang; ω menyaring lapisan regulasi saja, kebijakan adalah masukan kasus | representasi §2, §4; *engine* |
| 2 | blokir | G4 memakai **tanggal mulai efek** per unsur ($s(u)$), dengan penutupan masa berlaku menghasilkan awal selisih interval | akuisisi §4 |
| 3 | blokir | Penutupan (hanya memendekkan masa berlaku) dibebaskan dari syarat efek G5; pendaratan tanggal hanya untuk tanggal baru/berubah dan menerima "hari sebelum tanggal yang didaratkan" | akuisisi §4 G2, G5 |
| 4 | blokir | *Lex posterior* memakai `valid_from` lalu $t_c^0$ (pencatatan rekaman pertama unsur), bukan $t_c$ rekaman terakhir | representasi §3, §8; *engine* |
| 5 | blokir | Unsur bernama sama yang berlaku bersamaan: `valid_from` terakhir, lalu $t_c^0$, lalu urutan | representasi §3; *engine* |
| 6 | blokir | Penerapan longgar $\oplus_\ell$ untuk memindahkan $\Delta$ ke basis lain (E3 mekanis, peninjau sempurna); alur tetap ketat | akuisisi §1, §2 |
| 7 | penting | Kunci stabil laporan konflik tanpa `id` regulasi; kode untuk batasan diambil dari batasan | representasi §8; *engine* |
| 8 | penting | `recorded_on` wajib sama dengan $t_\mathit{terbit}$ metadata; G4 memakai $t_\mathit{terbit}$ − 1 hari | akuisisi §4 |
| 9 | penting | G5.3 menerima pencabutan aturan mati; ablasi yang gagal dievaluasi dihitung berefek | akuisisi §4 G5 |
| 10 | penting | G3.4 menjadi peringatan; galat sebenarnya ditangkap G4 | akuisisi §4 G3 |
| 11 | penting | Keputusan dicatat di Log; tafsir_korpus B5 untuk E13 ditambahkan | Log keputusan; tafsir_korpus B5 |
| 12 | penting | Aturan tahun dipilih menurut irisan dengan tahun kerja; fakta tahun diberi masa pajak terakhir | representasi §4, §7; *engine* |
| 13 | penting | Tupel, observasi, mode berantai, $S^E_{\le n}$, $H_n$ didefinisikan | akuisisi §2 |
| 14 | penting | $F_\mathit{nilai}$ dibekukan di pembaruan latar kosakata; semua punya aturan bawaan sejak awal | representasi §4 |
| 15 | penting | Label (a) dibatasi ke fakta yang dihasilkan aturan kebijakan; (b) ke fakta yang dihasilkan/dibaca aturan kebijakan; prevalensi dilaporkan | akuisisi §6 |
| 16 | penting | RA peristiwa nyata = A1 dari riwayat *commit* + kecocokan $\mathcal{K}^\star_n$ dengan acuan independen; dinyatakan sebagai bukti konstruktif | akuisisi §2 Def. 7 |
| 17 | penting | Skema keluaran LLM datar terpisah (`delta_llm.schema.json`) + pengonversi | format_data §2.3 |
| 18 | penting | Diterima sebagian: harga dan perkiraan per kandidat dicatat; $m = 1$ untuk kontrafaktual dan kebijakan sintetis; anggaran per eksperimen ditetapkan setelah pengukuran di Tahap 11 | akuisisi §8 |
| 19 | penting | B4 memakai $m$ kandidat awal tanpa perbaikan; selisih anggaran dilaporkan | akuisisi §7 |
| 20 | penting | Fakta `withholding_method` lewat konvensi masukan (`default`), dapat diganti kebijakan; fakta bawaan `method` dihapus dari *engine* | representasi §6.3; *engine* |
| 21 | penting | Tabel peristiwa kebijakan, basis $\mathcal{K}^\star_\mathit{reg}$ lengkap, ω = 2026-10-27 | akuisisi §1 |
| 22 | penting | Hierarki peraturan tidak dipakai *engine*, dicatat sebagai keputusan dan batas; `overrides` wajib asiklik (G3) | representasi §8; akuisisi G3 |
| 23 | penting | Masa kerja lewat `hr.service_months`; contoh C8/C10 diselaraskan dengan label klausul | format_data §3 |
| 24 | penting | Penanda $S^G$ = komponen `other_regular` 7 rupiah, ikut dihitung saat mencari ambang; pemeriksaan irisan langsung | akuisisi §5 |
| 25 | penting | A1 mencakup `kb/`; skema kasus tidak membatasi enum status/metode/kelompok risiko | akuisisi §2; `case.schema.json` |
| 26 | kecil | Daftar pola tertutup pendaratan tanggal | akuisisi G2 |
| 27 | kecil | Konstanta dinormalisasi kanonik; $p/100$ dicocokkan dengan "p%"; bilangan bulat < 100 dibebaskan | akuisisi G2 |
| 28 | kecil | `C?` hanya di laporan *engine*; `conflict_code` ditambahkan ke Def. 2 sebagai anotasi | representasi §3; skema |
| 29 | kecil | Konvensi awalan id per jenis/lapisan, diperiksa G1 | representasi §3; akuisisi G1 |
| 30 | kecil | `valid_from` tanggal 1 bulan, `valid_until` hari terakhir bulan | representasi §3; akuisisi G1 |
| 31 | kecil | Label Indonesia `label_id` untuk leksikon | format_data §2; akuisisi §3.1 |
| 32 | kecil | Mengikuti no. 2 dan 8 | akuisisi G4 |
| 33 | kecil | Urutan peristiwa bertanggal sama mengikuti tabel; pengecoh ikut rangkaian E3 | akuisisi §1 |
| 34 | kecil | Penghapusan memo lintas lingkup dan evaluasi ulang di dalam iterasi dijelaskan; penyempitan dibanding prototipe dicatat di batas ekspresivitas | representasi §10, §11.4 |
| 35 | kecil | Kunci aturan dan batasan memuat `valid_from` | representasi §9 |
| 36 | kecil | Tanpa kuorum; pengelompokan atas kedua ω $S^G$; didaftarkan di pra-registrasi | akuisisi §3.6 |
| 37 | kecil | `adopts` dipindah ke tingkat dokumen kebijakan | representasi §8; format_data §2 |
| 38 | kecil | *Engine* memberi peringatan untuk komponen kasus yang tidak dibaca aturan | representasi §6.3; *engine* |
| 39 | kecil | `policy` boleh daftar; `passed_before_repair` dicatat; `step` dibatasi; `filter` dijelaskan | skema; format_data |
| 40 | kecil | *Cutoff* Opus 5.5 dan harga dicatat | akuisisi §8 |
| 41 | kecil | $S^G$ memvariasikan atribut kasus yang muncul di kondisi | akuisisi §5 |

Status: **selesai**. Spesifikasi versi 2 dipakai untuk Tahap 5 dan seterusnya.
