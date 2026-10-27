# Spesifikasi representasi pengetahuan dan *inference engine*

Tahap 3 [PANDUAN_PENELITIAN.md](../../PANDUAN_PENELITIAN.md); *skeleton* Bagian IV (Representasi pengetahuan dan *inference engine*). Versi 2, 2026-10-27: revisi atas tinjauan independen [review/specs/spesifikasi.review.md](../../review/specs/spesifikasi.review.md); tanggapan per temuan di [review/specs/spesifikasi.tanggapan.md](../../review/specs/spesifikasi.tanggapan.md) dan ringkasan perubahan di bagian 14.

Dokumen ini menetapkan bentuk *knowledge base* (KB), arti hasil perhitungan, ontologi, bahasa ekspresi, semantik waktu, resolusi konflik, bentuk kanonik, batas ekspresivitas, dan algoritma inferensi. Implementasinya di `system/pph21kbs/` (Tahap 5). Semua nama di dalam KB berbahasa Inggris; penjelasan berbahasa Indonesia.

Daftar keputusan sebelumnya yang dipakai di sini (Log keputusan, PANDUAN): representasi *legal knowledge graph* RDF/OWL + SHACL + SPARQL dengan aturan yang dijalankan *engine*; ω dan $t_c$ = tanggal terbit dokumen; rekaman aturan berversi dengan operasi *add*, *change*, *remove*; *lex specialis* berupa relasi eksplisit antaraturan; cakupan *engine* setahun penuh; GraphDB sebagai *triple store* dengan satu *named graph* per versi. Aturan tafsir perhitungan K1–K16 ([tafsir_perhitungan.md](tafsir_perhitungan.md)) dan semantik berlaku surut B0–B4 ([tafsir_korpus.md](tafsir_korpus.md)) adalah isi KB emas, bukan bagian representasi.

---

## 1. Model pengetahuan

Pengetahuan dibagi dua.

1. **Pengetahuan struktural** disimpan sebagai *knowledge graph*: dokumen hukum dan pasalnya, aturan, parameter, tabel, konsep (fakta, jenis penghasilan, jenis natura), kebijakan perusahaan, versi KB, dan relasi di antaranya (bersumber, menghasilkan, membaca, mengungguli, mengubah, mencabut, berkonflik).
2. **Pengetahuan komputasional** berupa ekspresi perhitungan yang disimpan sebagai atribut *literal* pada *node* aturan, dan dijalankan oleh *inference engine*.

Alasan pembagian:
- Relasi antarunsur (dari mana sebuah aturan berasal, fakta apa yang dibacanya, kebijakan mana yang bergantung padanya, aturan mana yang diganti) adalah pertanyaan graf. SPARQL menjawabnya tanpa menjalankan perhitungan, dan ini yang dipakai analisis dampak lintas lapis (RQ4), gerbang G3, dan pemeriksa anomali.
- Aritmetika pajak membutuhkan ketepatan rupiah, pecahan eksak, pembulatan bertitik, dan iterasi titik tetap (*gross-up*). Hal ini tidak praktis diungkapkan sebagai *triple* atau dalam aturan SWRL/SHACL-AF. Ekspresi dalam bahasa kecil yang diverifikasi statis (bagian 6) memberi ketepatan itu dan tetap dapat dibaca serta disunting LLM.
- Dengan pembagian ini, perubahan regulasi hanya menyentuh data graf (A1: kode *engine* tidak berubah).

---

## 2. *Knowledge base*

**Definisi 1 (*Knowledge base*).** $\mathcal{K} = \langle \mathcal{O}, \mathcal{R}, \mathcal{P}, \mathcal{T}, \mathcal{C}, \mathcal{D} \rangle$:
- $\mathcal{O}$ ontologi: kelas, properti, dan individu konsep (fakta, jenis penghasilan, jenis natura, kategori);
- $\mathcal{R}$ himpunan rekaman aturan (Definisi 2);
- $\mathcal{P}$ himpunan rekaman parameter berversi;
- $\mathcal{T}$ himpunan rekaman versi tabel;
- $\mathcal{C}$ himpunan rekaman batasan (*constraint*) wajib;
- $\mathcal{D}$ dokumen sumber dan pasalnya, beserta provenans pembaruan.

Setiap unsur $\mathcal{R}$, $\mathcal{P}$, $\mathcal{T}$, $\mathcal{C}$ berada pada lapisan $\ell \in \{\mathit{reg}, \mathit{prs}\}$ (regulasi, perusahaan). Parameter, tabel, dan batasan hanya ada di lapisan regulasi pada versi ini; kebijakan perusahaan menyatakan nilainya sendiri lewat aturan.

**Lapisan perusahaan per kebijakan.** Setiap aturan perusahaan milik tepat satu kebijakan (`policy` = id dokumen kebijakan, misalnya `PKB-WIKA-2025`). $\mathcal{K} = \mathcal{K}_\mathit{reg} \oplus \bigcup_j P_j$, dan untuk kasus $x$ hanya lapisan $P(x)$ yang dipasang, yaitu kebijakan yang disebut di data kasus (`employer.policy`, satu id atau daftar id). Kebijakan juga dapat mengadopsi aturan regulasi `optional` (`adopts` di tingkat dokumen kebijakan).

**Rekaman dan identitas.** Unsur KB punya identitas logis (`id`, misalnya `REG.PTKP.AMOUNT`) dan satu atau lebih **rekaman**. Rekaman tidak pernah disunting di tempat. Operasi pembaruan menambah rekaman baru:
- *add*: rekaman pertama untuk `id` baru;
- *change*: rekaman baru untuk `id` yang sudah ada, menggantikan rekaman sebelumnya sejak tanggal pencatatannya;
- *remove*: rekaman nisan (*tombstone*) untuk `id`, yang menghapus unsur itu sejak tanggal pencatatannya.

Rekaman yang berlaku untuk `id` pada tanggal pengetahuan ω adalah rekaman dengan tanggal pencatatan $t_c \le \omega$ terbesar; bila beberapa rekaman punya $t_c$ sama, yang terakhir diterapkan (urutan penerapan dicatat). Bila rekaman itu nisan, unsur tidak ada pada ω. Inilah yang membuat $\mathcal{K}$ bitemporal dan menjamin A3$_\omega$: rekaman yang dicatat pada $t_\mathit{terbit}$ tidak terlihat oleh pertanyaan dengan $\omega < t_\mathit{terbit}$.

**ω menyaring lapisan regulasi saja.** Lapisan perusahaan $P(x)$ adalah masukan kasus: kebijakan yang berlaku bagi pegawai itu, dalam versi yang dicatat. Rekamannya dipilih menurut masa berlaku, tidak menurut ω. Dengan begitu pertanyaan "bagaimana kebijakan ini berinteraksi dengan regulasi sebagaimana diketahui pada ω" terdefinisi walaupun dokumen kebijakan terbit sesudah ω (misalnya PKB AVCO 2024 terhadap E03 yang terbit Desember 2023).

Pencabutan hukum biasa (aturan lama tidak berlaku lagi mulai suatu masa) bukan *remove*, melainkan *change* yang mengisi `valid_until`. Dengan begitu hasil masa lampau tetap dihitung dengan aturan lama (A3$_t$). *Remove* dipakai untuk unsur yang dianggap tidak pernah benar sejak ω tertentu, misalnya aturan pembantu yang tidak dibutuhkan lagi.

---

## 3. Aturan, parameter, tabel, batasan

**Definisi 2 (Aturan).** Rekaman aturan
$$r = \langle \mathit{id}, \ell, \sigma, \kappa, [t_s, t_e], t_c, \varphi, f \coloneqq e, \mathit{fp}, \mathit{ov}, \mathit{src} \rangle$$

| Simbol | Nama di KB | Arti |
|---|---|---|
| $\mathit{id}$ | `id` | identitas logis, huruf besar dipisah titik: `<lapisan>.<topik>.<nama>`, misalnya `REG.TER.RATE`, `PRS.WIKA.THR` |
| $\ell$ | `layer` | `regulation` atau `company` |
| $\sigma$ | `modality` | `mandatory` (wajib), `default` (boleh diganti kebijakan perusahaan), `optional` (berlaku hanya bila diadopsi kebijakan perusahaan) |
| $\kappa$ | `scope` | `period` (dievaluasi per masa/bulan) atau `year` (sekali per tahun pajak) |
| $[t_s, t_e]$ | `valid_from`, `valid_until` | masa berlaku hukum, tanggal; `valid_until` kosong = tidak terbatas |
| $t_c$ | `recorded_on` | tanggal pencatatan = tanggal terbit dokumen sumber |
| $\varphi$ | `condition` | ekspresi boolean; kosong = selalu |
| $f$ | `produces` | nama fakta yang dihasilkan |
| $e$ | `expression` | ekspresi nilai fakta |
| $\mathit{fp}$ | `fixed_point` | opsional: `{lower, upper}`, ekspresi batas titik tetap (bagian 11.4) |
| $\mathit{ov}$ | `overrides` | daftar `id` aturan yang dikalahkan aturan ini (*lex specialis*, bagian 8) |
| $\mathit{src}$ | `source` | `{document, provision, quote}`: dokumen, pasal/ayat/huruf/halaman, dan kutipan teks pendukung |
| $\pi$ | `policy` | khusus aturan perusahaan: id dokumen kebijakan pemiliknya |
| $\kappa_c$ | `conflict_code` | khusus aturan perusahaan, anotasi opsional: jenis konflik C1–C10 bila aturan ini dikalahkan aturan wajib (untuk laporan; tidak dipakai saat membandingkan laporan) |

Atribut tambahan yang tidak memengaruhi hasil: `label` (uraian singkat), `note`.

**Konvensi identitas dan tanggal.** `id` aturan berawalan `REG.` atau `PRS.` sesuai lapisan; parameter `PAR.`, tabel `TAB.`, batasan `CON.`; `id` fakta = nama fakta (huruf kecil). `valid_from` selalu tanggal 1 sebuah bulan dan `valid_until` selalu hari terakhir sebuah bulan, karena masa pajak dan bulan iuran adalah satuan waktu terkecil; G1 menolak tanggal lain.

**Identitas tahun berlaku.** Untuk resolusi konflik dibutuhkan tanggal yang tidak berubah ketika rekaman direvisi: $t_c^0(\mathit{id})$, tanggal pencatatan rekaman **pertama** unsur itu.

**Parameter.** $p = \langle \mathit{id}, \mathit{name}, v, [t_s, t_e], t_c, \mathit{src} \rangle$. Nilai $v$ berupa bilangan bulat (rupiah atau hitungan), pecahan eksak yang ditulis sebagai teks desimal (`"0.0024"`), boolean, atau teks (misalnya mode pembulatan `"half_up"`). Satu nama parameter bisa punya banyak unsur dengan masa berlaku berbeda (misalnya `jp_wage_cap`, satu unsur per tahun). Bila beberapa unsur bernama sama berlaku pada tanggal evaluasi, yang dipakai adalah unsur dengan `valid_from` paling akhir, lalu $t_c^0$ paling akhir, lalu urutan penerapan; jadi nilai baru tidak perlu menutup nilai lama. Aturan yang sama berlaku untuk versi tabel.

**Versi tabel.** $\tau = \langle \mathit{id}, \mathit{name}, \mathit{kind}, [t_s, t_e], t_c, \mathit{rows}, \mathit{src} \rangle$ dengan `kind`:
- `lookup`: baris `{key, value}`, misalnya PTKP per status, kategori TER per status;
- `bracket`: baris `{key, lower, upper, value}` untuk interval $(\mathit{lower}, \mathit{upper}]$ per kunci, misalnya tarif TER per kategori;
- `progressive`: baris `{lower, upper, rate}`, misalnya lapisan Pasal 17;
- `set`: baris `{key}` (dengan atribut tambahan bebas), misalnya daftar KLU penerima DTP.

**Batasan.** $c = \langle \mathit{id}, \ell=\mathit{reg}, \sigma=\mathit{mandatory}, \kappa, [t_s, t_e], t_c, \varphi, \psi, \mathit{code}, \mathit{src} \rangle$. Bila kondisi $\varphi$ benar dan pernyataan $\psi$ salah pada suatu konteks, batasan dilanggar dan dilaporkan sebagai konflik berkode `code` (taksonomi C1–C10). Batasan dipakai untuk ketentuan wajib yang tidak berbentuk "fakta ini bernilai ini", misalnya THR paling sedikit satu bulan upah (C10) atau dasar upah iuran tidak boleh lebih sempit dari gaji pokok + tunjangan tetap (C8).

---

## 4. Hasil perhitungan

**Definisi 3 (Hasil perhitungan).** $\mathit{hasil}(\mathcal{K}, x, t, \omega)$ adalah nilai fakta keluaran untuk kasus $x$ pada masa pajak $t$, dihitung dengan $\mathcal{K}_\mathit{reg}$ sebagaimana diketahui pada tanggal ω ditambah lapisan kebijakan $P(x)$. Dalam implementasi, *engine* menghitung satu kasus untuk seluruh tahun pajaknya sekaligus, dan $\mathit{hasil}$ untuk masa $t$ adalah proyeksi ke masa itu. Fakta lingkup tahun dihitung di masa pajak terakhir dan diberi masa itu sebagai $t$ (dipakai untuk membagi A2 dan A3$_t$). Selain nilai, *engine* mengeluarkan **laporan konflik** $\mathit{konflik}(\mathcal{K}, x, \omega)$ dan **jejak** setiap fakta sampai sumber hukum.

**Kasus.** $x$ adalah satu pegawai tetap pada satu pemberi kerja untuk satu tahun pajak: data pegawai (status PTKP awal tahun, jenis kelamin, keterangan suami tidak berpenghasilan, NPWP/NIK, awal/akhir kewajiban subjektif), data pemberi kerja (KLU, kelompok risiko JKK, kelayakan keringanan iuran), metode (`gross`, `gross_up`, `employer_borne`), bulan masuk dan keluar, dan per masa: komponen penghasilan, natura menurut jenis, zakat lewat pemberi kerja, serta data SDM (jam lembur, hari kerja, dan sebagainya) bila kebijakan perusahaan menghitungnya. Format JSON di [format_data.md](format_data.md).

**Masa.** $t$ = (tahun pajak, bulan). Masa pajak terakhir adalah Desember, atau bulan terakhir bekerja bila pegawai berhenti sebelum Desember (PMK 168/2023 Lampiran B I.2).

**Fakta keluaran yang dinilai** ($F_\mathit{nilai}$):

| Fakta | Lingkup | Arti |
|---|---|---|
| `pph21_due` | masa | **fakta utama**: PPh 21 terutang masa itu (masa terakhir: PPh setahun dikurangi PPh masa sebelumnya; boleh negatif) |
| `pph21_dtp` | masa | bagian PPh 21 yang ditanggung pemerintah |
| `gross_income` | masa | penghasilan bruto masa (seluruh penghasilan teratur dan tidak teratur yang menjadi objek, termasuk premi objek, natura objek, dan tunjangan pajak; tafsir K14) |
| `tax_allowance` | masa | tunjangan pajak (*gross-up*) atau PPh yang ditanggung pemberi kerja |
| `take_home_pay` | masa | penghasilan tunai dikurangi iuran pegawai, potongan perusahaan, dan PPh yang ditanggung pegawai |
| `jkk_premium`, `jkm_premium`, `health_premium_employer` | masa | premi yang dibayar pemberi kerja dan masuk bruto |
| `jht_employee`, `jp_employee` | masa | iuran pegawai yang menjadi pengurang |
| `annual_gross`, `job_expense`, `annual_deductions`, `annual_net`, `ptkp_amount`, `taxable_income`, `annual_pph21` | tahun | perhitungan masa pajak terakhir |
| `refund_to_employee` | tahun | kelebihan potong yang dikembalikan kepada pegawai |

Fakta komponen yang dapat ditetapkan kebijakan perusahaan (misalnya `thr`, `overtime_pay`, `base_salary`) juga termasuk $F_\mathit{nilai}$.

**$F_\mathit{nilai}$ dibekukan.** Daftar fakta yang dinilai ditetapkan di $\mathcal{K}^\star_0$ (pembaruan latar kosakata) dan dibekukan bersama penilai sebelum eksperimen. Semua fakta $F_\mathit{nilai}$ punya aturan bawaan sejak awal rentang (misalnya `pph21_dtp` = 0 sebelum ada fasilitas DTP), sehingga pembaruan hanya mengubah nilainya. Fakta baru yang ditambahkan pembaruan (oleh peneliti atau LLM) adalah fakta antara dan tidak dinilai, kecuali untuk perubahan tak terlihat yang dinilai dengan contoh hitungan penulisnya. Daftar dihasilkan dari rantai emas sebagai `dataset/12_emas/kosakata.md`.

**Mekanisme penyelesaian berlaku surut tidak dinilai.** Sesuai B0, nilai yang dihitung untuk masa $t$ dengan ω ≥ $t_\mathit{terbit}$ adalah *nilai seharusnya*; perhitungan masa pajak terakhir memakai jumlah nilai seharusnya. Entri penyelesaian (misalnya pembayaran tunai DTP Januari pada penggajian Februari) dicatat di jejak sebagai catatan, bukan fakta yang dinilai.

---

## 5. Ontologi

**Ruang nama.** `pph:` = `https://w3id.org/pph21kbs/ontology#` (kelas dan properti), `kb:` = `https://w3id.org/pph21kbs/kb/` (individu). IRI dicadangkan; pendaftaran w3id dilakukan saat rilis artefak (Tahap 23). Standar yang dipakai ulang: ELI (`eli:`), OWL-Time (`time:`), PROV-O (`prov:`), Dublin Core (`dcterms:`), SHACL (`sh:`).

**Kelas.**

| Kelas | Induk | Arti |
|---|---|---|
| `pph:LegalDocument` | `eli:LegalResource` | dokumen hukum (UU, PP, PMK, PER, surat BPJS, PKB, peraturan perusahaan) |
| `pph:Provision` | `eli:LegalResourceSubdivision` | pasal, ayat, huruf, angka, atau bagian lampiran |
| `pph:Quote` | `prov:Entity` | kutipan teks dari satu pasal |
| `pph:KBElement` | `prov:Entity` | induk abstrak rekaman KB |
| `pph:Rule` | `pph:KBElement` | rekaman aturan |
| `pph:Parameter` | `pph:KBElement` | rekaman parameter |
| `pph:TableVersion`, `pph:TableRow` | `pph:KBElement` | versi tabel dan barisnya |
| `pph:Constraint` | `pph:KBElement` | rekaman batasan wajib |
| `pph:Tombstone` | `pph:KBElement` | rekaman *remove* |
| `pph:Fact` | `skos:Concept` | konsep fakta: nama, tipe, lingkup, keluaran atau antara |
| `pph:InputFact` | `pph:Fact` | fakta dari data kasus |
| `pph:IncomeKind`, `pph:BenefitKind` | `skos:Concept` | jenis penghasilan dan jenis natura |
| `pph:Layer`, `pph:Modality`, `pph:Scope` | `skos:Concept` | individu `pph:Regulation`, `pph:Company`, `pph:Mandatory`, `pph:Default`, `pph:Optional`, `pph:Period`, `pph:Year` |
| `pph:CompanyPolicy` | `pph:LegalDocument` | dokumen kebijakan perusahaan |
| `pph:ChangeEvent` | `prov:Activity` | peristiwa perubahan $\epsilon$ |
| `pph:Update` | `prov:Activity` | penerapan satu $\Delta$ (oleh peneliti, LLM, atau peninjau) |
| `pph:KBVersion` | `prov:Entity` | versi KB $\mathcal{K}_n$; satu *named graph* |
| `pph:ValidityInterval` | `time:ProperInterval` | masa berlaku (lihat penyelarasan di bawah) |

**Properti utama.**

| Properti | Domain → Jangkauan | Arti |
|---|---|---|
| `pph:elementId` | KBElement → string | identitas logis |
| `pph:layer`, `pph:modality`, `pph:scope` | Rule → konsep | Definisi 2 |
| `pph:validFrom`, `pph:validUntil`, `pph:recordedOn` | KBElement → `xsd:date` | waktu |
| `pph:produces` | Rule → Fact | fakta yang dihasilkan |
| `pph:reads` | Rule/Constraint → Fact | fakta yang dibaca ekspresi atau kondisi (diturunkan otomatis dari ekspresi) |
| `pph:usesParameter`, `pph:usesTable` | Rule → string | parameter dan tabel yang dirujuk (diturunkan) |
| `pph:condition`, `pph:expression`, `pph:assertion` | → string | ekspresi |
| `pph:fixedPointLower`, `pph:fixedPointUpper` | Rule → string | batas titik tetap |
| `pph:overrides` | Rule → Rule-id | *lex specialis* eksplisit |
| `pph:adopts` | Rule(company) → Rule-id | adopsi aturan `optional` |
| `pph:conflictCode` | Constraint → string | kode C1–C10 |
| `pph:hasSource` | KBElement → Quote | sumber |
| `pph:quoteText`, `pph:provision` | Quote → string, Provision | kutipan dan pasal |
| `eli:is_part_of` | Provision → LegalDocument | pasal bagian dari dokumen |
| `eli:date_document`, `eli:date_publication`, `eli:first_date_entry_in_force` | LegalDocument → `xsd:date` | ditetapkan, diundangkan, mulai berlaku |
| `pph:issued` | LegalDocument → `xsd:date` | $t_\mathit{terbit}$ |
| `prov:wasGeneratedBy` | KBElement → Update | pembaruan yang membuat rekaman |
| `prov:wasRevisionOf` | KBElement → KBElement | rekaman sebelumnya untuk `id` yang sama |
| `pph:triggeredBy` | Update → ChangeEvent | peristiwa pemicu |
| `pph:hasMember` | KBVersion → Update | pembaruan penyusun versi |
| `pph:conflictsWith` | Rule(company) → Rule/Constraint | konflik yang terdeteksi statis (diturunkan, untuk RQ4) |

**Penyelarasan OWL-Time dan PROV-O.** `pph:validFrom`/`pph:validUntil` adalah bentuk ringkas dari `time:hasBeginning`/`time:hasEnd` sebuah `pph:ValidityInterval`; pengekspor dapat menuliskan bentuk panjang. `pph:recordedOn` setara dengan `prov:generatedAtTime` pada tanggal hukum (bukan waktu sistem); waktu persetujuan peninjau disimpan terpisah di `pph:Update` sebagai `prov:endedAtTime` (Log keputusan "Makna ω dan $t_c$").

**Versi dan *named graph*.** Setiap $\Delta$ yang diterapkan disimpan sebagai satu *named graph* `kb:update/<id>`. Versi $\mathcal{K}_n$ disimpan sebagai *named graph* snapshot `kb:version/<n>` (gabungan semua rekaman sampai pembaruan ke-$n$) dan dideskripsikan di graf metadata `kb:meta` (`pph:hasMember`, urutan, sidik jari SHA-256 atas serialisasi kanonik). Di GraphDB, snapshot dipakai untuk kueri dan validasi SHACL; di git, sumber kebenaran adalah berkas $\Delta$ JSON dan hasil serialisasinya.

**Gambar ontologi.**

```
                 eli:LegalResource
                        ▲
  pph:CompanyPolicy ─▶ pph:LegalDocument ◀─eli:is_part_of── pph:Provision ◀─pph:provision── pph:Quote
                                                                                               ▲
                                                                                    pph:hasSource
  pph:ChangeEvent ◀─pph:triggeredBy── pph:Update ◀─prov:wasGeneratedBy── pph:KBElement ────────┘
                                         ▲                 ▲  ├── pph:Rule ──pph:produces──▶ pph:Fact ◀── pph:InputFact
                         pph:hasMember   │                 │  │      │  └─pph:reads────────▶ pph:Fact
                     pph:KBVersion ──────┘                 │  │      └─pph:overrides / pph:adopts ─▶ pph:Rule
                                                           │  ├── pph:Parameter
                                       prov:wasRevisionOf ─┘  ├── pph:TableVersion ──▶ pph:TableRow
                                                              ├── pph:Constraint ──pph:reads──▶ pph:Fact
                                                              └── pph:Tombstone
  atribut waktu setiap KBElement: pph:validFrom, pph:validUntil (≈ time:ProperInterval), pph:recordedOn (≈ prov:generatedAtTime)
  atribut aturan: pph:layer ∈ {Regulation, Company}, pph:modality ∈ {Mandatory, Default, Optional}, pph:scope ∈ {Period, Year}
```

Versi gambar untuk paper dibuat dari berkas ontologi di Tahap 5 (`docs/gambar/ontologi.*`).

**Batasan SHACL (G1).** Daftar lengkap di [akuisisi.md](akuisisi.md) bagian G1. Ringkasnya: setiap rekaman punya tepat satu `elementId`, `recordedOn`, `validFrom`; `validUntil` ≥ `validFrom`; aturan punya tepat satu `layer`, `modality`, `scope`, `produces`, `expression`; aturan perusahaan tidak boleh `mandatory`; setiap rekaman punya minimal satu sumber dengan kutipan tak kosong dan pasal yang menjadi bagian dari dokumen; `produces` merujuk `pph:Fact` yang dikenal; tabel `bracket` punya `lower` < `upper`.

---

## 6. Bahasa ekspresi

### 6.1 Sintaks

Subset ekspresi Python (satu ekspresi, tanpa pernyataan):
- literal: bilangan bulat, teks, `True`, `False`, `None`, tuple;
- operator: `+ - * /`, `-x`, `== != < <= > >=`, `in`, `not in`, `and`, `or`, `not`, `a if c else b`;
- nama fakta (huruf kecil dan garis bawah);
- pemanggilan fungsi terdaftar (bagian 6.3) dengan argumen posisional.

Ditolak saat *parse* (verifikasi statis): literal pecahan biner (`0.05`), atribut, *subscript*, *lambda*, *comprehension*, argumen bernama, fungsi tak terdaftar, dan nama fakta yang tidak dikenal di kosakata. Pecahan ditulis sebagai pembagian (`5 / 100`) atau `dec("0.0024")`.

### 6.2 Tipe dan aritmetika

| Tipe | Nilai | Catatan |
|---|---|---|
| `money` | bilangan bulat rupiah | nilai akhir fakta bertipe `money` wajib bulat; pecahan → kesalahan "pembulatan tidak dinyatakan" |
| `exact` | pecahan eksak (rasional) | nilai antara, misalnya neto disetahunkan |
| `rate` | pecahan eksak | tarif |
| `int` | bilangan bulat | bulan, hitungan |
| `bool` | benar/salah | |
| `category` | teks | status PTKP, kategori TER, KLU, metode |
| `date` | tanggal | hanya dari data kasus |

Semua aritmetika eksak. Pembagian menghasilkan pecahan. Pembulatan hanya terjadi lewat `round(...)` (atau fungsi yang secara eksplisit membulatkan), sehingga titik pembulatan selalu terlihat di aturan dan dapat diubah oleh pembaruan (jenis T9). Operan aritmetika boolean, teks, dan `None` ditolak saat evaluasi.

### 6.3 Fungsi

| Fungsi | Lingkup | Arti |
|---|---|---|
| `min(a, b, ...)`, `max(a, b, ...)`, `abs(a)` | semua | |
| `round(x, unit, mode)` | semua | bulatkan $x$ ke kelipatan `unit`; `mode` ∈ `down` (ke −∞), `up` (ke +∞), `truncate` (ke nol), `half_up` (0,5 menjauhi nol), `half_even` |
| `dec(teks)` | semua | pecahan eksak dari teks desimal |
| `param(nama)` | semua | nilai parameter yang berlaku pada tanggal evaluasi (bagian 7) |
| `lookup(tabel, kunci)` | semua | nilai tabel `lookup` |
| `bracket(tabel, kunci, jumlah)` | semua | nilai baris tabel `bracket` dengan `lower < jumlah ≤ upper` untuk kunci itu |
| `progressive(tabel, jumlah)` | semua | pajak progresif: Σ tarif × bagian jumlah di tiap lapisan (eksak) |
| `in_table(tabel, kunci)` | semua | apakah kunci ada di tabel `set` |
| `table_attr(tabel, kunci, atribut)` | semua | atribut baris tabel `set` |
| `startswith(teks, awalan)` | semua | |
| `income(nama)` | masa | komponen penghasilan masa ini dari data kasus (0 bila tidak ada) |
| `benefit(jenis)` | masa | nilai natura jenis itu masa ini (0 bila tidak ada) |
| `hr(nama)` | masa | data SDM masa ini (0 bila tidak ada) |
| `employee(atribut)`, `employer(atribut)`, `case(atribut)` | semua | data kasus |
| `sum_periods(fakta)` | tahun | Σ fakta atas semua masa kerja tahun itu |
| `sum_periods_before_final(fakta)` | tahun | Σ fakta atas masa selain masa terakhir |
| `sum_to_date(fakta)` | masa | Σ fakta dari masa kerja pertama sampai masa ini |
| `sum_before(fakta)` | masa | Σ fakta dari masa kerja pertama sampai sebelum masa ini |
| `cumulative(fakta)` | masa | Σ fakta dari masa kerja pertama sampai masa ini, hanya atas masa yang punya aturan aktif untuk fakta itu (untuk batas kumulatif setahun atas fakta yang baru berlaku di tengah tahun) |
| `cumulative_before(fakta)` | masa | seperti `cumulative`, untuk masa sebelum masa ini |
| `value_in(fakta, bulan)` | semua | nilai fakta lingkup masa pada bulan tertentu |
| `year_value(fakta)` | masa | nilai fakta lingkup tahun dari dalam aturan masa |
| `defined(fakta)` | semua | apakah ada aturan aktif yang menghasilkan fakta itu |
| `value_or(fakta, cadangan)` | semua | nilai fakta, atau cadangan bila tidak ada aturan aktif |

Fakta konteks bawaan (selalu tersedia): `month`, `tax_year`, `is_final_period`, `first_month` (bulan kerja pertama tahun itu), `final_month`, `months_employed` (jumlah masa kerja tahun itu). Fakta lingkup tahun dapat dibaca langsung dari aturan masa dengan namanya; `year_value` hanya untuk keterbacaan.

**Konvensi masukan.** Data kasus masuk ke KB lewat aturan regulasi `default` bersumber dokumen `INPUT-CONVENTION`, misalnya `base_salary := income("base_salary")` dan `withholding_method := case("method")`. Karena `default`, kebijakan perusahaan dapat menggantinya (misalnya PKB yang menetapkan PPh ditanggung perusahaan, atau menghitung lembur dari jam kerja). Metode pemotongan sengaja tidak menjadi fakta bawaan *engine* agar dapat diatur kebijakan. *Engine* memberi peringatan untuk komponen data kasus (`income`, `benefits`, `hr`) yang tidak dibaca aturan mana pun, supaya penghasilan baru yang belum dikenal KB tidak hilang diam-diam.

### 6.4 Verifikasi statis

Saat sebuah rekaman masuk (G1/G3) dan saat KB dimuat: ekspresi di-*parse*; nama fakta, fungsi, parameter, dan tabel diperiksa terhadap kosakata dan KB; aritmetika fungsi dicocokkan; tipe dasar diturunkan dari tipe fakta, dan ketidakcocokan yang pasti (misalnya `bool + money`) ditolak. Pemeriksaan ini juga membatasi keluaran LLM: kandidat yang memakai fungsi atau fakta di luar kosakata tertolak di G1/G3.

---

## 7. Semantik temporal

Ada dua sumbu waktu.

1. **Waktu berlaku** (*valid time*) $[t_s, t_e]$: masa hukum yang dicakup ketentuan. Sumbu ini dibandingkan dengan **tanggal evaluasi** $d$:
   - aturan lingkup masa: $d$ = tanggal 1 bulan masa itu; rekaman berlaku bila $t_s \le d \le t_e$;
   - aturan lingkup tahun: rekaman berlaku bila $[t_s, t_e]$ beririsan dengan rentang kerja tahun itu (tanggal 1 bulan kerja pertama sampai hari terakhir masa pajak terakhir). Dengan ini fasilitas sementara yang berakhir sebelum Desember (misalnya DTP April–September 2020) tetap punya aturan perhitungan akhir tahunnya. Bila beberapa rekaman untuk fakta yang sama beririsan, resolusi konflik memilih (bagian 8, *posterior* menurut `valid_from`);
   - `param`, `lookup`, `bracket`, `progressive`, `in_table` dalam konteks masa memakai $d$ masa itu; dalam konteks tahun memakai irisan yang sama seperti aturan tahun, dengan pilihan `valid_from` paling akhir (bagian 3).
   Bulan iuran BPJS disamakan dengan bulan upah, sehingga batas upah JP yang berlaku "mulai iuran Maret" dibaca pada masa Maret.
2. **Waktu pengetahuan** $t_c$: tanggal terbit dokumen. Pertanyaan pada ω hanya melihat rekaman dengan $t_c \le \omega$ (bagian 2).

**Pemilihan.** Untuk konteks dengan tanggal evaluasi $d$ dan pengetahuan ω, himpunan kandidat untuk fakta $f$ adalah
$$\mathcal{R}_f(d, \omega) = \{ r \in \mathrm{rekaman\_berlaku}(\mathcal{K}, \omega) : r.\mathit{produces} = f,\ r.\kappa = \kappa(\mathrm{konteks}),\ t_s \le d \le t_e \}.$$
Aturan **aktif** adalah kandidat yang kondisinya benar. Parameter dan tabel dipilih dengan cara yang sama berdasarkan nama.

**Berlaku surut.** Untuk $t_s < t_c$, pertanyaan dengan $\omega < t_c$ melihat keadaan lama dan pertanyaan dengan $\omega \ge t_c$ melihat *nilai seharusnya* (B0). Perhitungan masa pajak terakhir dengan ω ≥ $t_c$ menjumlahkan nilai seharusnya semua masa.

**Konsekuensi untuk A3.** Rekaman baru dengan $t_s$ tertentu hanya dapat mengubah hasil masa $t \ge t_s$, kecuali lewat fakta lingkup tahun dan agregat yang membaca masa sesudah $t_s$; G4 memeriksa masa sebelum **tanggal mulai efek** pembaruan (akuisisi.md bagian 4), bukan sebelum $t_c$, sesuai A3$_t$.

---

## 8. Resolusi konflik

Bila lebih dari satu aturan aktif untuk fakta yang sama pada konteks yang sama, *engine* menentukan pemenang tunggal dengan urutan berikut.

1. ***Lex superior*** (peringkat). Peringkat aturan:
   - 4: regulasi `mandatory`;
   - 3: perusahaan (semua `modality`);
   - 2: regulasi `optional` yang diadopsi oleh kebijakan $P(x)$ (`adopts` di tingkat dokumen kebijakan); aturan `optional` yang tidak diadopsi tidak pernah aktif;
   - 1: regulasi `default`.
   Hanya aturan berperingkat tertinggi yang lanjut. Bila sebuah aturan perusahaan aktif kalah dari aturan regulasi `mandatory` untuk fakta yang sama **dan nilainya berbeda**, *engine* mencatat konflik (A4); kodenya diambil dari anotasi `conflict_code` aturan perusahaan bila ada, atau `C?` bila tidak.
   Hierarki peraturan (UU > PP > PMK > PER) tidak dipakai *engine*: semua aturan regulasi `mandatory` berperingkat sama, dan pertentangan antartingkat harus dinyatakan dengan `overrides` di pembaruan. Ini keputusan desain (KB menyimpan ketentuan yang sudah diharmonisasi, bukan menalar keabsahan peraturan) dan dicatat sebagai batas.
2. ***Lex specialis*** (relasi eksplisit). Di antara aturan sisa, aturan $a$ mengalahkan $b$ bila $b$ ada dalam penutup transitif `overrides` milik $a$. Aturan yang dikalahkan aturan sisa lain disingkirkan. Ukuran "lebih spesifik" tidak dihitung dari sintaks kondisi (Log keputusan "*Lex specialis*"). Relasi `overrides` harus asiklik (G3).
3. ***Lex posterior***. Di antara aturan sisa, yang `valid_from`-nya paling akhir menang; bila sama, yang $t_c^0$-nya (tanggal pencatatan rekaman pertama unsur) paling akhir. Tanggal pencatatan rekaman terakhir tidak dipakai, supaya revisi metadata aturan lama (misalnya penutupan masa berlaku) tidak membuatnya "lebih baru" dan menang kembali untuk masa lampau.
4. **Tidak ada pemenang tunggal.** Bila masih lebih dari satu aturan dan nilai ekspresinya berbeda, fakta itu dinyatakan **tidak terdefinisi** dengan kesalahan `UnresolvedConflict` yang menyebut semua aturan yang tersisa. Bila nilainya sama, salah satunya dipakai dan peringatan `RedundantRules` dicatat. Kasus yang menghasilkan kesalahan dinilai salah pada semua fakta yang bergantung pada fakta itu.

**Batasan.** Setelah semua fakta dihitung, setiap batasan yang berlaku pada konteks itu dievaluasi; pelanggaran dicatat sebagai konflik.

**Laporan konflik** $\mathit{konflik}(\mathcal{K}, x, \omega)$ berisi entri dengan atribut jenis (`override` atau `constraint`), aturan perusahaan yang terlibat, aturan atau batasan regulasi yang terlibat, fakta, masa, dan kode. Untuk membandingkan dua laporan (A4, konsensus, label (c)), yang dipakai adalah **kunci stabil** yang tidak bergantung pada nama unsur regulasi pilihan penyusun $\Delta$:
- `override`: (jenis, `id` aturan perusahaan, fakta, masa);
- `constraint`: (jenis, himpunan `id` aturan perusahaan yang menghasilkan fakta yang dibaca batasan, masa, kode batasan).
Aturan perusahaan berasal dari emas kebijakan, sehingga `id`-nya stabil pada eksperimen regulasi; pada eksperimen kebijakan, `id` aturan perusahaan kandidat diselaraskan dengan emas lewat bentuk kanonik (bagian 9) sebelum dibandingkan.

---

## 9. Bentuk kanonik unsur

Dipakai untuk mencocokkan unsur kandidat dengan unsur emas pada metrik diagnostik (kebenaran per unsur, upaya koreksi) dan untuk mendeteksi aturan redundan. Kebenaran utama tetap diukur dari perilaku (A2), bukan dari bentuk.

1. **Ekspresi kanonik**: AST dicetak ulang dengan spasi tetap; operan operator komutatif (`+`, `*`, `and`, `or`, `==`, `min`, `max`) diurutkan leksikografis; konstanta dilipat (`5 / 100` → `1/20`); `dec("0.05")` → `1/20`; perbandingan dinormalisasi ke `<`/`<=` dengan menukar sisi; kondisi kosong → `True`.
2. **Kunci unsur**:
   - aturan: (`layer`, `produces`, `scope`, kondisi kanonik, `valid_from`);
   - parameter: (`name`, `valid_from`);
   - tabel: (`name`, `valid_from`);
   - batasan: (`code`, asersi kanonik, `valid_from`).
3. **Atribut yang dibandingkan** setelah kunci cocok: `modality`, `valid_from`, `valid_until`, `recorded_on`, ekspresi kanonik, `overrides`, nilai, baris tabel (sebagai himpunan), dokumen sumber dan pasal.
4. **Penyelarasan** kandidat dengan emas: pencocokan bipartit (*Hungarian*) dengan biaya = jumlah atribut berbeda, kunci tidak cocok = biaya maksimum. Operasi sunting = jumlah atribut yang harus diubah ditambah unsur yang harus ditambah atau dihapus.

---

## 10. Batas ekspresivitas

Yang sengaja **tidak** dapat dinyatakan tanpa mengubah *engine* (pelanggaran A1 bila dibutuhkan):
1. hubungan antarpegawai atau antar-pemberi kerja (misalnya penghasilan dari pemberi kerja lain, pindah cabang dengan pemotong berbeda);
2. perhitungan lintas tahun pajak (misalnya rapel tahun lalu, kompensasi lebih bayar ke tahun berikutnya);
3. satuan masa selain bulan (gaji harian/mingguan dinyatakan sebagai komponen bulanan di data kasus);
4. iterasi selain titik tetap terkecil satu fakta (persamaan simultan beberapa fakta). Ini penyempitan dibanding prototipe, yang mendukung iterasi Kleene atas komponen terhubung kuat beranggota banyak; seluruh *gross-up* di korpus cukup dengan satu fakta titik tetap per konteks;
5. kewajiban prosedural tanpa angka (tenggat setor/lapor, bentuk bukti potong, sanksi administrasi);
6. pertimbangan yang tidak dapat ditentukan dari data kasus (misalnya "kenikmatan yang tidak dapat dimanfaatkan secara khusus oleh pegawai" tanpa atribut yang menyatakannya); untuk hal ini data kasus harus memuat atributnya;
7. kurs valas (komponen valas dinyatakan dalam rupiah di data kasus).

Penambahan fungsi baru ke bahasa ekspresi adalah perubahan *engine*. Penambahan fakta, jenis penghasilan, jenis natura, parameter, tabel, atau atribut data kasus **bukan** perubahan *engine*, karena kosakata berada di KB dan data kasus bersifat terbuka (`income`, `benefit`, `hr`, `employee`, `employer` menerima nama baru).

---

## 11. Algoritma inferensi

### 11.1 Ringkasan

```
Algoritma 1. Inferensi untuk satu pegawai dan satu tahun pajak
Masukan : K, kasus x, tanggal pengetahuan ω
 1  R_ω ← rekaman berlaku pada ω (rekaman terakhir per id dengan t_c ≤ ω, tanpa nisan)
 2  verifikasi statis R_ω (sekali per versi; hasil di-cache)
 3  M ← masa kerja x pada tahun pajak; m_akhir ← masa pajak terakhir
 4  untuk setiap fakta keluaran f dan setiap konteks c (masa m ∈ M, atau tahun):
 5      nilai(f, c)                                   ▷ evaluasi berdasarkan permintaan
 6  untuk setiap batasan yang berlaku: catat pelanggaran
 7  keluarkan nilai F_nilai, laporan konflik, jejak

fungsi nilai(f, c):
 a  bila (f, c) sudah dihitung: kembalikan memo
 b  bila (f, c) ada di tumpukan evaluasi: bila aturan pemiliknya titik tetap, kembalikan nilai iterasi saat ini;
    selain itu galat CircularDefinition
 c  kandidat ← R_f(d(c), ω); aktif ← {r : φ_r(c) benar}
 d  bila aktif kosong: bila f fakta masukan/konteks → nilai dari data kasus; selain itu galat MissingRule
 e  r* ← resolusi(aktif)                                ▷ bagian 8; catat konflik
 f  v ← e_{r*}(c), atau titik tetap terkecil bila r* bertanda fixed_point (11.4)
 g  periksa tipe v; simpan memo dan jejak (r*, sumber, fakta yang dibaca, nilai)
```

Evaluasi berdasarkan permintaan dengan memo setara dengan menelusuri graf dependensi fakta secara topologis: fakta dievaluasi sesudah semua fakta yang dibacanya. Graf dependensi statis (fakta → fakta lewat `pph:reads`/`pph:produces`) tetap dibangun untuk G3 dan pemeriksa anomali, termasuk deteksi siklus.

### 11.2 Konteks dan lingkup

Konteks masa membaca fakta masa pada bulan yang sama dan fakta tahun. Konteks tahun membaca fakta tahun dan agregat fakta masa (`sum_periods`, `value_in`). Dengan begitu fakta masa dapat bergantung pada fakta tahun (misalnya kategori TER dari status PTKP awal tahun, kelayakan DTP dari penghasilan Januari) dan sebaliknya, selama tidak ada siklus.

### 11.3 Pembulatan dan ketepatan

Seluruh nilai antara eksak. Fakta bertipe `money` harus bernilai bulat; aturan yang menghasilkan pecahan untuk fakta `money` gagal dengan galat yang menyebut aturannya. Titik dan mode pembulatan dinyatakan di ekspresi lewat `round(...)` dengan mode dari parameter (misalnya `param("pph_round_mode")`), sehingga perubahan pembulatan (K1, E13) adalah pembaruan data.

Semantik mode untuk bilangan negatif: `down` ke −∞, `up` ke +∞, `truncate` ke nol, `half_up` menjauhi nol pada 0,5, `half_even` ke genap.

### 11.4 Titik tetap

Aturan bertanda `fixed_point` dengan batas `lower` dan `upper` menghitung titik tetap terkecil $T = e(T)$ dengan iterasi $T_0 = \mathit{lower}$, $T_{k+1} = e(T_k)$ sampai $T_{k+1} = T_k$ (tafsir K3: titik tetap terkecil, iterasi dari 0). Selama iterasi, pembacaan fakta itu di dalam ekspresinya sendiri (langsung atau lewat fakta lain) mengembalikan $T_k$, dan memo fakta yang bergantung padanya dihapus setiap putaran. Bila $T_k$ keluar dari $[\mathit{lower}, \mathit{upper}]$ atau tidak konvergen dalam 200 putaran, *engine* gagal dengan `FixedPointError`. Fungsi PPh atas bruto monoton tidak turun, sehingga iterasi dari batas bawah konvergen ke titik tetap terkecil (Tarski); monotonisitas tidak diperiksa saat *runtime*, tetapi kegagalannya muncul sebagai `FixedPointError` atau nilai yang berbeda dari acuan.

Fakta yang sedang dievaluasi di luar iterasi (misalnya `gross_income` masa itu ketika `tax_allowance` sedang diiterasi) boleh dievaluasi ulang di dalam iterasi, karena ketergantungannya pada fakta titik tetap dipenuhi oleh nilai iterasi; siklus lain tetap `CircularDefinition`. Memo yang dibuat selama satu putaran dihapus bila putaran itu belum konvergen, termasuk memo fakta lingkup tahun (siklus Desember: tunjangan pajak masa terakhir ↔ PPh setahun).

### 11.5 Jejak penjelasan

Untuk setiap fakta yang dihitung: aturan pemenang (`id`, rekaman, lapisan, sifat), aturan yang kalah dan alasannya (peringkat, *specialis*, *posterior*), sumber (dokumen, pasal, kutipan), fakta yang dibaca beserta nilainya, parameter dan versi tabel yang dipakai, dan nilai. **Kelengkapan jejak** (diagnostik RQ1) = proporsi fakta keluaran yang rantai jejaknya sampai ke kutipan sumber pada setiap langkah.

---

## 12. Perbandingan dengan prototipe lama

Prototipe `engine/` + `kb/` (YAML) tetap menjadi acuan kesetaraan di Tahap 5. Perbedaan yang disengaja:

| Hal | Prototipe | Representasi baru | Alasan |
|---|---|---|---|
| Penyimpanan | YAML/CSV di git | *knowledge graph* RDF (rdflib, GraphDB), $\Delta$ JSON | keputusan representasi final |
| Kosakata | bahasa Indonesia | bahasa Inggris | Log keputusan "Code in English" |
| *Lex specialis* | jumlah konjungsi kondisi | relasi `overrides` eksplisit | Log keputusan "*Lex specialis*" |
| Versi | `berlaku` + `dicatat` per aturan | rekaman berversi dengan *add/change/remove* dan nisan | Log keputusan "Pencabutan dan perubahan aturan" |
| Varian tafsir | aturan bersifat `tafsir` dengan varian | satu tafsir per hal, ditetapkan di `tafsir_perhitungan.md` | KB emas harus satu |
| Pembulatan | registri terpisah, mode tetap | `round()` di ekspresi dengan mode dari parameter berversi | K1 berubah menurut waktu (E13) |
| Iuran BPJS | masukan kasus | dihitung dari dasar upah dan parameter | agar peristiwa batas upah JP dan keringanan JKK berpengaruh |
| Natura | seluruh nilai menjadi objek | pengecualian dan batas PMK 66/2023 per jenis | adjudikasi diferensial GT3 |
| Konflik ketenagakerjaan | tidak ada | batasan wajib (C8, C10) | A4 dan RQ4 |
| Sumbu waktu iuran | `PI` terpisah | bulan iuran = bulan upah | penyederhanaan; batas upah JP dibaca pada masanya |

Daftar perubahan ini adalah masukan Tahap 5.

---

## 13. Pemenuhan kotak "Harus didefinisikan" *skeleton* Bagian IV

| Butir *skeleton* | Bagian |
|---|---|
| Definisi *knowledge base* (lapisan) | 2 |
| Definisi aturan | 3 |
| Definisi hasil perhitungan dan fakta keluaran | 4 |
| Kelas, relasi, standar yang dipakai ulang; gambar ontologi | 5 |
| Fungsi bahasa ekspresi dan sistem tipe; pembatas keluaran LLM | 6 |
| Semantik temporal $[t_s, t_e]$, $t_c$, sumbu waktu | 7 |
| Relasi superioritas, ukuran *lex specialis*, perilaku tanpa pemenang | 8 |
| Bentuk kanonik unsur | 9 |
| Batas ekspresivitas | 10 |
| Algoritma inferensi, aritmetika eksak, pembulatan, definisi melingkar, jejak | 11 |

---

## 14. Riwayat revisi

| Versi | Tanggal | Perubahan |
|---|---|---|
| 1 | 2026-10-27 | Draf pertama |
| 2 | 2026-10-27 | Tanggapan atas tinjauan independen (41 temuan): lapisan perusahaan per kebijakan dan tidak disaring ω; *lex posterior* menurut `valid_from` dan $t_c^0$; pemilihan parameter/tabel bernama sama; aturan tahun dipilih menurut irisan dengan tahun kerja; fakta tahun diberi masa pajak terakhir; $F_\mathit{nilai}$ dibekukan; kunci stabil laporan konflik; konvensi masukan termasuk `withholding_method`; konvensi id dan tanggal batas bulan; kunci kanonik memuat `valid_from`; hierarki peraturan tidak dipakai; penyempitan titik tetap dicatat |
