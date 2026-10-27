# Spesifikasi akuisisi pengetahuan, adaptivitas, dan dampak lintas lapis

Tahap 4 [PANDUAN_PENELITIAN.md](../../PANDUAN_PENELITIAN.md); *skeleton* Bagian V. Versi 2, 2026-10-27: revisi atas tinjauan independen ([review/specs/spesifikasi.review.md](../../review/specs/spesifikasi.review.md), tanggapan di [spesifikasi.tanggapan.md](../../review/specs/spesifikasi.tanggapan.md)). Bergantung pada [representasi.md](representasi.md) (Definisi 1–3). Format data dan skema JSON di [format_data.md](format_data.md).

---

## 1. Peristiwa perubahan dan pembaruan

**Definisi 4 (Peristiwa perubahan).** $\epsilon = \langle d, t_\mathit{terbit}, t_\mathit{berlaku}, \tau, \ell, b \rangle$: dokumen sumber, tanggal terbit (tanggal diundangkan bila ada, selain itu tanggal ditetapkan), tanggal mulai berlaku hukum (awal masa pajak atau bulan iuran pertama yang dicakup), jenis perubahan menurut [taksonomi.md](taksonomi.md), lapisan (regulasi atau kebijakan perusahaan), dan bagian data (pengembangan, uji, prospektif, kontrafaktual, pengecoh, tak terlihat). $\epsilon$ berlaku surut bila $t_\mathit{berlaku} < t_\mathit{terbit}$.

- **Rangkaian regulasi** $\epsilon_1, \dots, \epsilon_N$: peristiwa regulasi (relevan dan pengecoh) diurutkan menurut $t_\mathit{terbit}$, lalu menurut urutan baris tabel peristiwa (`dataset/09_korpus_peristiwa/peristiwa.csv`; misalnya E03 sebelum E04, E07 sebelum P06 yang terbit pada hari sama). Pengecoh ikut rangkaian E3: $\hat{\Delta}$ tak kosong pada pengecoh diterapkan dan dapat menimbulkan kesalahan, sama seperti dalam operasi.
- **Peristiwa kebijakan**: setiap dokumen kebijakan perusahaan adalah satu peristiwa lapisan perusahaan, dicatat di `dataset/10_kebijakan_perusahaan/peristiwa_kebijakan.csv` (id, dokumen, tanggal dokumen, masa berlaku, bagian: uji untuk 5 PKB nyata, sintetis untuk SP01–SP14, pengembangan untuk PKB TPK Koja). Peristiwa kebijakan tidak masuk rangkaian regulasi (Log keputusan "Cakupan kebijakan perusahaan").

**Definisi 5 (Pembaruan).** $\Delta = \langle \Delta^{+}, \Delta^{\sim}, \Delta^{-} \rangle$ berisi unsur yang ditambah, diubah, dan dicabut. Penerapan ketat $\mathcal{K}' = \mathcal{K} \oplus \Delta$:
- setiap unsur $u \in \Delta^{+}$ menjadi rekaman pertama untuk `id`-nya; `id` yang sudah ada → $\Delta$ ditolak;
- setiap unsur $u \in \Delta^{\sim}$ menjadi rekaman baru untuk `id` yang sudah ada, dengan `prov:wasRevisionOf` ke rekaman sebelumnya; `id` yang tidak ada → ditolak;
- setiap `id` $\in \Delta^{-}$ mendapat rekaman nisan;
- semua rekaman dicatat dengan `prov:wasGeneratedBy` ke `pph:Update` baru yang `pph:triggeredBy` peristiwanya; dokumen dan pasal yang dikutip ditambahkan ke $\mathcal{D}$.

**Penerapan longgar** $\mathcal{K} \oplus_\ell \Delta$ dipakai hanya untuk memindahkan $\Delta$ ke basis yang bukan basis penyusunannya (komponen mekanis kesalahan terpicu, varian *abstain* dengan peninjau sempurna di E3): *change* untuk `id` yang tidak ada diperlakukan sebagai *add*, *add* untuk `id` yang ada sebagai *change*, *remove* untuk `id` yang tidak ada diabaikan. Setiap penyesuaian dicatat. Alur akuisisi selalu memakai penerapan ketat.

$\Delta$ kosong adalah jawaban benar untuk pengecoh. Pembaruan emas memenuhi $\mathcal{K}^\star_n = \mathcal{K}^\star_{n-1} \oplus \Delta^\star_n$.

**Rantai emas tunggal.** Emas regulasi disimpan sebagai satu rangkaian pembaruan: pembaruan latar (dokumen yang bukan peristiwa korpus, misalnya UU PPh, PMK 101/2016, PER-16/PJ/2016, PP 44–46/2015) dan pembaruan peristiwa ($\Delta^\star_n$). Karena KB bitemporal, keadaan sebelum peristiwa $n$, $\mathcal{K}^\star_{<n}$, adalah semua rekaman emas yang diterapkan sebelum $\Delta^\star_n$; keadaan awal rentang uji, $\mathcal{K}^\star_0$, adalah semua rekaman dengan $t_c \le$ 2022-12-31. Peristiwa pengembangan (2012–2022) tercakup di rantai yang sama. Rentang uji 2023–2026 tidak berisi pembaruan latar (kelengkapan korpus, tafsir_korpus A9). Untuk rentang pengembangan, sebagian pembaruan latar memakai dokumen terbitan lebih akhir sebagai sumber kutipan (misalnya metode disetahunkan dikutip dari PER-16/PJ/2016 untuk tahun 2013–2015 karena PER-31/PJ/2012 tidak tersedia); ini penyederhanaan yang hanya memengaruhi data pengembangan dan dicatat di rantai emas.

**Emas kebijakan.** Untuk setiap kebijakan $P_j$, $\Delta^\star(P_j)$ berisi aturan perusahaan milik kebijakan itu (dan `adopts` bila ada). Basis akuisisi kebijakan adalah $\mathcal{K}^\star_\mathit{reg}$ lengkap (semua peristiwa regulasi, ω = 2026-10-27) tanpa lapisan perusahaan.

---

## 2. Syarat adaptif dan prosedur ujinya

**Satuan evaluasi.** *Tupel* $\tau = (x, \omega)$ adalah satu kasus (satu pegawai, satu tahun pajak) yang dihitung sekali dengan satu tanggal pengetahuan. *Observasi* $o = (x, t, f)$ adalah satu nilai fakta $f \in F_\mathit{nilai}$ pada masa $t$ dari tupel itu; fakta lingkup tahun memakai masa pajak terakhir sebagai $t$. Laporan konflik tupel dibandingkan dengan kunci stabil (representasi.md bagian 8).

**Definisi 6 (Syarat adaptif).** Untuk $\mathcal{K}' = \mathcal{K} \oplus \Delta$, basis $\mathcal{K}$, peristiwa $\epsilon$, dan himpunan tupel $S$:
- **(A1) Invariansi kode.** Kode *engine* tidak berubah.
- **(A2) Kesesuaian.** $\mathit{hasil}(\mathcal{K}', x, t, \omega) = \mathit{hasil}(\mathcal{K}^\star, x, t, \omega)$ untuk observasi dengan $t \ge t_\mathit{berlaku}$ dari tupel dengan $\omega \ge t_\mathit{terbit}$.
- **(A3$_t$) Isolasi masa.** $\mathit{hasil}(\mathcal{K}', x, t, \omega) = \mathit{hasil}(\mathcal{K}, x, t, \omega)$ untuk observasi dengan $t < t_\mathit{berlaku}$, semua ω.
- **(A3$_\omega$) Isolasi pengetahuan.** $\mathit{hasil}(\mathcal{K}', x, t, \omega) = \mathit{hasil}(\mathcal{K}, x, t, \omega)$ untuk $\omega < t_\mathit{terbit}$ dan semua $t$.
- **(A4) Konsistensi lintas lapis.** $\mathit{konflik}(\mathcal{K}', x, \omega) = \mathit{konflik}(\mathcal{K}^\star, x, \omega)$ (kunci stabil) untuk tupel yang kasusnya memuat kebijakan perusahaan.

Nilai sama berarti sama persis; fakta yang gagal dihitung (galat *engine*) berbeda dari nilai apa pun.

**Prosedur uji otomatis.**

| Syarat | Prosedur | Pelanggaran dihitung sebagai |
|---|---|---|
| A1 | SHA-256 atas paket `system/pph21kbs/engine/`, `system/pph21kbs/expr/`, dan `system/pph21kbs/kb/` (semantik rekaman dan penerapan) dihitung di awal setiap jalan dan dibandingkan dengan manifes yang dibekukan pada *tag* `engine-v1`. Riwayat *commit* ketiga folder diekspor dan dipetakan ke regulasi pemicu | jumlah berkas berbeda; harus 0 |
| A2 | Untuk setiap tupel $S^E$ peristiwa $n$ (ω = $t_\mathit{terbit}$): bandingkan observasi $t \ge t_\mathit{berlaku}$ dari $\mathcal{K}'$ dan $\mathcal{K}^\star_n$ | observasi berbeda |
| A3$_t$ | Tupel yang sama: bandingkan observasi $t < t_\mathit{berlaku}$ dari $\mathcal{K}'$ dan basis $\mathcal{K}$ | idem |
| A3$_\omega$ | Invarian: semua rekaman $\Delta$ harus punya `recorded_on` = $t_\mathit{terbit}$ dokumen (diperiksa statis di G2). Diperiksa juga secara eksekusi pada sampel $S^E$ dengan ω = $t_\mathit{terbit}$ − 1 hari | rekaman/observasi; harus 0 |
| A4 | Tupel $S^E$ yang memuat kebijakan: bandingkan laporan konflik $\mathcal{K}'$ dan $\mathcal{K}^\star_n$ | entri yang hilang atau palsu |

Karena $\mathcal{K}'$ dan $\mathcal{K}^\star_n$ tidak memuat rekaman sesudah peristiwa $n$, satu nilai ω = $t_\mathit{terbit}$ cukup.

**Definisi 7 (Adaptivitas representasional).** Representasi adaptif terhadap $\epsilon$ bila ada $\Delta$ dalam bahasa representasi yang memenuhi A1–A4. Untuk peristiwa nyata, keberadaan $\Delta^\star$ adalah bukti konstruktif, dan bagian yang tidak tautologis adalah: (i) tidak ada perubahan *engine* yang dipicu peristiwa itu (A1, dari riwayat *commit*), dan (ii) $\mathcal{K}^\star_n$ cocok dengan acuan independen GT1–GT5 pada sel yang dipengaruhi peristiwa itu. Untuk perubahan tak terlihat, $\Delta$ disusun peneliti dan dinilai dengan contoh hitungan penulisnya (RA). Untuk dokumen kebijakan, $\Delta^\star(P_j)$ dinilai dengan GT5.

**Definisi 8 (Adaptivitas operasional).** Sistem adaptif secara operasional terhadap $\epsilon$ bila $\hat{\Delta}$ yang dipilih alur memenuhi A2, A3$_t$, dan A4 pada seluruh $S^E$ peristiwa itu, dengan A1 dan A3$_\omega$ sebagai invarian. Satu observasi salah sudah membuat $\hat{\Delta}$ salah.

**Mode evaluasi.**
- *Terisolasi* (RQ2): $\hat{\Delta}_n$ diterapkan pada $\mathcal{K}^\star_{n-1}$; dinilai pada $S^E_n$.
- *Berantai* (RQ3): $\mathcal{K}^\mathrm{sis}_n = \mathcal{K}^\mathrm{sis}_{n-1} \oplus \hat{\Delta}_n$, dengan $\hat{\Delta}_n$ dibangkitkan dari konteks $\mathcal{K}^\mathrm{sis}_{n-1}$. $S^E_{\le n} = \bigcup_{k \le n} S^E_k$, dievaluasi dengan ω = $t_\mathit{terbit}(\epsilon_n)$. Observasi yang sudah salah sebelum peristiwa $n$ adalah $H_n = \{o \in S^E_{\le n} : \mathit{hasil}(\mathcal{K}^\mathrm{sis}_{n-1}, o, \omega^-_n) \ne \mathit{hasil}(\mathcal{K}^\star_{n-1}, o, \omega^-_n)\}$ dengan $\omega^-_n = t_\mathit{terbit}(\epsilon_n) - 1$ hari. Kesalahan baru pada peristiwa $n$ = observasi salah di $\mathcal{K}^\mathrm{sis}_n$ yang tidak ada di $H_n$. OAR = proporsi peristiwa tanpa kesalahan baru. Komponen mekanis kesalahan terpicu memakai $\mathcal{K}^\mathrm{sis}_{n-1} \oplus_\ell \hat{\Delta}^\mathrm{iso}_n$.

**Semantik berlaku surut.** Ditetapkan di [tafsir_korpus.md](tafsir_korpus.md) B0–B5 dan dicatat di Log keputusan: untuk ω ≥ $t_\mathit{terbit}$ setiap masa bernilai *nilai seharusnya*, perhitungan masa pajak terakhir menjumlahkan nilai seharusnya, dan mekanisme penyelesaian tunai dicatat di jejak tetapi tidak dinilai. Ini penyimpangan sadar dari bunyi *skeleton* ("nilai sebagaimana seharusnya ... mengikuti mekanisme itu"): entri penyelesaian bergantung pada apa yang benar-benar dipotong pada tanggal penggajian, yang bukan masukan kasus.

---

## 3. Alur akuisisi

Delapan tahap, dijalankan untuk satu dokumen.

### 3.1 Pemotongan dokumen

Teks diambil sekali per dokumen (pdfplumber; HTML: pengurai HTML; dokumen pindai: OCR yang tersimpan), diperiksa sekali, lalu dikunci beserta SHA-256-nya di `dataset/13_teks/` (Log keputusan "Pengambilan teks PDF"). Teks dipotong menjadi **segmen**: pembuka, setiap pasal (`Pasal N`; pada dokumen perubahan, setiap angka "Pasal I angka k"), penutup (tanggal ditetapkan, diundangkan, mulai berlaku), dan setiap bagian lampiran. Tabel lampiran diekstraksi sekali oleh alat ekstraksi tabel, diperiksa, dan disimpan sebagai **tabel terekstraksi** dengan id (misalnya `PP-58-2023/LAMPIRAN-A`). LLM merujuk tabel dengan id, pemetaan kolom, dan penyaring baris, tidak menyalin barisnya.

**Pemilihan segmen.** Segmen diberi skor leksikal dari leksikon domain: label berbahasa Indonesia (`label_id`) setiap fakta, parameter, dan tabel di KB, ditambah daftar istilah pajak umum yang tetap ("Pasal 21", "pegawai tetap", "penghasilan bruto", "tarif", "dibulatkan", "iuran", "upah", "ditanggung pemerintah", "masa pajak"). Segmen diurutkan menurut skor dan diambil sampai anggaran masukan (bawaan 14.000 token), selalu ditambah pembuka dan penutup. Leksikon dan anggaran ditetapkan pada data pengembangan dan dibekukan di Tahap 11. Pembaruan terlewat karena pasal tidak terpilih dilaporkan sebagai jenis kesalahan tersendiri.

### 3.2 Penilaian relevansi berkutipan

Satu panggilan LLM (*effort* `medium`) menerima metadata dokumen (jenis, nomor, judul, $t_\mathit{terbit}$ dari intake) dan segmen terpilih. Keluaran terstruktur: `relevant`, `layer`, alasan, `quotes`, `effective_from` dan `effective_until` (beserta kutipan), dan `subjects` (sektor, KLU, kelompok pegawai, beserta kutipan). Bila `relevant = false` dan kutipannya lolos G2, alur menerapkan $\Delta$ kosong. Bila `relevant = false` tetapi kutipan gagal G2, alur *abstain*.

### 3.3 Konteks dari graf

Dari basis $\mathcal{K}$ dengan kueri SPARQL: (1) kosakata lengkap (fakta beserta tipe, lingkup, label Inggris dan Indonesia; katalog fungsi); (2) rekaman yang relevan: aturan, parameter, dan tabel yang label Indonesianya cocok dengan leksikon segmen terpilih, ditambah aturan yang menghasilkan atau membaca fakta-fakta itu (satu langkah ke hulu dan hilir), ditambah aturan fakta keluaran utama; (3) atribut setiap rekaman: `id`, lapisan, sifat, lingkup, masa berlaku, kondisi, ekspresi, `overrides`, dokumen dan pasal sumber. Ablasi AB2 hanya memberi bagian (1).

### 3.4 Penyusunan $m$ kandidat

$m = 5$ panggilan independen, *effort* `high`, awalan bersama di-*cache* (instruksi sistem, skema keluaran, segmen dokumen, tabel terekstraksi, konteks KB). Instruksi menetapkan: `valid_from` = tanggal 1 masa/bulan iuran pertama yang dicakup, `valid_until` = hari terakhir masa/bulan terakhir, `recorded_on` = $t_\mathit{terbit}$ dari metadata, kutipan wajib per unsur, ketentuan lama ditutup dengan *change* yang mengisi `valid_until` (bukan *remove*). Keluaran mengikuti **skema keluaran LLM** yang datar dan kompatibel dengan keluaran terstruktur (format_data.md §2.3), lalu divalidasi lagi dengan skema $\Delta$ lengkap. Urutan kandidat diacak dengan *seed* yang dicatat.

### 3.5 Gerbang dan putaran perbaikan

Setiap kandidat melewati G1–G5 berurutan (bagian 4). Kandidat yang gagal mendapat **satu** putaran perbaikan berisi kandidat semula dan pesan gerbang; hasilnya diperiksa ulang G1–G5. Status lolos sebelum perbaikan dicatat terpisah (dibutuhkan pass@k).

### 3.6 Pemilihan konsensus

Kandidat yang lolos dikelompokkan menurut **perilaku**: dua kandidat sekelompok bila observasi $F_\mathit{nilai}$ dan laporan konfliknya (kunci stabil) sama pada seluruh $S^G_\cup$, gabungan $S^G$ semua kandidat yang lolos, untuk kedua nilai ω $S^G$. Kelompok terbesar menang, termasuk kelompok berukuran 1 bila hanya satu kandidat lolos (tidak ada kuorum minimum). Wakilnya adalah anggota pertama menurut urutan acak. Seri antara dua kelompok terbesar → *abstain*; tidak ada kandidat lolos → *abstain*. Aturan ini didaftarkan di pra-registrasi.

### 3.7 Peninjauan manusia

Dalam operasi, peninjau menerima $\hat{\Delta}$, laporan dampak (bagian 6), dan perbedaan hasil $S^G$. Dalam eksperimen E2–E4 tahap ini dilewati (batas bawah kinerja); upaya peninjau diperkirakan lewat operasi sunting dari $\hat{\Delta}$ ke $\Delta^\star$.

### 3.8 Penerapan

$\hat{\Delta}$ diterapkan sebagai `pph:Update` baru dan versi KB baru, dengan provenans model, *prompt*, dan jalan eksperimen.

---

## 4. Gerbang verifikasi

**Tanggal mulai efek.** Untuk setiap unsur $u$ di $\Delta$, $s(u)$ = tanggal pertama di mana rekaman yang berlaku untuk `id`-nya dapat berbeda antara $\mathcal{K}$ dan $\mathcal{K}'$:
- *add*: `valid_from`;
- *change* yang mengubah isi (ekspresi, kondisi, nilai, baris, sifat, lingkup, `overrides`): min(`valid_from` lama, `valid_from` baru);
- *change* yang hanya mengubah masa berlaku: awal selisih simetris kedua interval (misalnya penutupan 2023-12-31 → 2024-01-01);
- *remove*: `valid_from` rekaman lama.

Tanggal mulai efek pembaruan $s(\Delta) = \min_u s(u)$.

### G1 — struktur

1. Keluaran valid terhadap skema keluaran LLM, lalu terhadap skema $\Delta$ lengkap ([format_data.md](format_data.md) §2).
2. $\mathcal{K}' = \mathcal{K} \oplus \Delta$ valid terhadap *shape* SHACL (`system/ontology/shapes.ttl`; validator `system/pph21kbs/kb/shacl.py`):
   - setiap `pph:KBElement` punya tepat satu `pph:elementId`, `pph:recordedOn`; unsur bermasa berlaku punya tepat satu `pph:validFrom` (tanggal 1 bulan) dan paling banyak satu `pph:validUntil` (hari terakhir bulan, ≥ `validFrom`);
   - `id` berawalan sesuai jenis dan lapisan (`REG.`/`PRS.`/`PAR.`/`TAB.`/`CON.`; fakta huruf kecil);
   - `pph:Rule`: tepat satu `layer`, `modality`, `scope`, `produces`, `expression`; paling banyak satu `condition`; lingkup aturan sama dengan lingkup fakta yang dihasilkan; aturan `Company` tidak boleh `Mandatory` dan wajib punya `policy`; `overrides` merujuk `elementId` yang ada;
   - `pph:Parameter`: tepat satu `name` dan satu nilai bertipe sesuai `value_type`;
   - `pph:TableVersion`: tepat satu `name`, `kind`; minimal satu baris; baris `bracket` punya `lower` < `upper` (atau `upper` kosong); baris `progressive` punya `rate`;
   - `pph:Constraint`: tepat satu `assertion`; `conflictCode` sesuai `C([1-9]|10)` (`C?` hanya ada di laporan *engine*);
   - setiap rekaman punya minimal satu sumber dengan kutipan tak kosong dan pasal yang `eli:is_part_of` dokumen yang dikenal;
   - `produces` merujuk `pph:Fact` di kosakata.
3. Operasi konsisten dengan $\mathcal{K}$ (penerapan ketat).

### G2 — kutipan, nilai, dan tanggal

1. **Kutipan.** Kutipan dan teks dokumen dinormalisasi sama (huruf kecil; spasi dan baris baru dirapatkan; pemenggalan akhir baris disambung; tanda kutip dan tanda hubung diseragamkan; spasi di sekitar tanda baca dalam bilangan dihapus). Kutipan ≥ 20 karakter dan harus *substring* teks dokumen.
2. **Pendaratan nilai.** Konstanta di ekspresi, kondisi, nilai parameter, dan baris tabel tertulis dinormalisasi ke bentuk kanonik. Setiap bilangan bulat ≥ 100 dan setiap pecahan harus muncul di kutipan unsur itu dalam salah satu bentuk penulisan Indonesia: `9.559.600`, `9.559.600,00`, `Rp9.559.600`, `Rp 9.559.600,00`; pecahan $p/100$ sebagai `p%`, `p %`, `p persen` (dengan koma desimal, misalnya `0,24%`); pecahan lain sebagai desimal berkoma. Bilangan bulat < 100 (bulan, faktor, satuan pembulatan kecil) dibebaskan, demikian juga 1.000 sebagai satuan pembulatan dan bilangan yang sama dengan konstanta di rekaman lama yang diubah. Baris dari tabel terekstraksi tidak perlu didaratkan.
3. **Pendaratan tanggal** (perluasan G2, Log keputusan). Hanya tanggal yang baru atau berubah pada rekaman yang diperiksa. Tanggal $d$ didaratkan bila kutipan unsur memuat salah satu pola tertutup:
   - tanggal lengkap ("1 Juli 2023");
   - "Masa Pajak <Bulan> <Tahun>", "bulan <Bulan> <Tahun>", "Iuran JKK bulan <Bulan> <Tahun>", atau "<Bulan> <Tahun>" → tanggal 1 bulan itu (`valid_from`) atau hari terakhirnya (`valid_until`);
   - "Tahun Pajak <Tahun>", "Tahun Anggaran <Tahun>" → 1 Januari (`valid_from`) atau 31 Desember (`valid_until`);
   - nama bulan tanpa tahun bila tahunnya ada di kutipan lain unsur yang sama;
   - `valid_until` boleh hari sebelum tanggal yang didaratkan pada unsur lain di $\Delta$ yang sama (penutupan ketentuan lama oleh ketentuan baru);
   - "berlaku pada tanggal diundangkan/ditetapkan" → $t_\mathit{terbit}$ (dibulatkan ke tanggal 1 bulan itu atau bulan berikutnya sesuai kutipan).
   `recorded_on` setiap rekaman harus **sama dengan** $t_\mathit{terbit}$ dari metadata dokumen.

### G3 — konsistensi statis

1. Semua ekspresi lolos verifikasi statis (representasi.md 6.4).
2. Graf dependensi $\mathcal{K}'$ asiklik kecuali siklus yang melewati aturan `fixed_point`; relasi `overrides` asiklik.
3. Tidak ada rujukan menggantung: setiap fakta yang dibaca punya penghasil yang berlaku, atau berupa fakta bawaan, untuk setiap bulan dalam masa berlaku pembacanya (dibatasi ke 2012–2027).
4. Peringatan (tidak menggagalkan): pasangan aturan berperingkat sama untuk fakta sama dengan masa berlaku tumpang tindih tanpa `overrides` dan `valid_from` sama (potensi `UnresolvedConflict`; galat sebenarnya ditangkap G4 saat eksekusi); aturan mati; aturan redundan; aturan tercakup.

### G4 — regresi dan eksekusi pada $S^G$

Untuk setiap tupel $S^G$:
1. observasi dengan masa $t < s(\Delta)$: $\mathit{hasil}(\mathcal{K}', \cdot) = \mathit{hasil}(\mathcal{K}, \cdot)$ pada ω = $t_\mathit{terbit}$ (A3$_t$);
2. dengan ω = $t_\mathit{terbit}$ − 1 hari: semua observasi sama (A3$_\omega$);
3. evaluasi $\mathcal{K}'$ pada ω = $t_\mathit{terbit}$ tidak menghasilkan galat *engine* pada observasi mana pun.

### G5 — non-vakuitas (hanya untuk $\Delta$ tidak kosong)

1. Setiap unsur $u$ yang ditambah atau diubah isinya harus **berefek**: ada tupel $S^G$ dengan observasi $t \ge s(u)$ yang hasil $F_\mathit{nilai}$ atau laporan konfliknya berbeda antara $\mathcal{K}'$ dan $\mathcal{K}' \ominus u$ ($u$ dikembalikan: *add* dihapus, *change* dipulihkan ke rekaman sebelumnya). Bila $\mathcal{K}' \ominus u$ gagal dievaluasi karena unsur lain bergantung pada $u$, itu dihitung berefek. Efek berupa laporan konflik saja diterima.
2. *Change* yang hanya memendekkan masa berlaku (penutupan) dibebaskan dari syarat efek, asalkan masa berlaku baru tidak berakhir sebelum $s(\Delta)$ − 1 hari.
3. Setiap `id` di $\Delta^{-}$ harus pernah menyala di $\mathcal{K}$ pada suatu tupel $S^G$, atau merupakan aturan mati di $\mathcal{K}$ (pencabutan aturan pembantu bersifat opsional, Log keputusan).
4. **Tanggal tercermin.** Bila penilaian relevansi menyebut `effective_from`, harus ada tupel $S^G$ pada bulan itu yang hasilnya berubah dari $\mathcal{K}$ ke $\mathcal{K}'$.
5. **Subjek tercermin.** Bila penilaian relevansi menyebut subjek, harus ada tupel $S^G$ dengan subjek itu yang hasilnya berubah.

**Syarat pembekuan.** Setiap gerbang harus meloloskan $\Delta^\star$ semua peristiwa pengembangan yang relevan (laju penolakan keliru nol) sebelum dibekukan di Tahap 11.

---

## 5. Generator $S^G$

$S^G$ dibangkitkan untuk satu kandidat dari $\mathcal{K} \oplus \hat{\Delta}$ dan hasil penilaian relevansi, tanpa membaca emas atau $S^E$.

1. **Waktu.** Tahun yang dicakup unsur (dari $s(u)$ sampai `valid_until` atau tahun berikutnya), dibatasi ke 2013–2027. Bulan: $s(u)$, bulan sebelumnya, Desember, dan `effective_from`.
2. **Ambang.** Konstanta pembanding di kondisi dan ekspresi unsur, nilai parameter yang dirujuk, dan batas tabel. Untuk ambang $b$ pada fakta turunan upah atau bruto, generator mencari gaji pokok sehingga nilai fakta jatuh di $b - 1$, $b$, $b + 1$ (pencarian biner dengan menjalankan $\mathcal{K} \oplus \hat{\Delta}$).
3. **Atribut kasus di kondisi.** Setiap atribut `employee(...)`, `employer(...)`, `case(...)`, dan `hr(...)` yang muncul di kondisi atau ekspresi unsur divariasikan: boolean → keduanya; kategori/teks → setiap literal pembanding ditambah satu nilai lain; bilangan → ambang seperti butir 2. Status PTKP: literal yang muncul atau kedelapan status. KLU: setiap kunci tabel `set` yang ditambah/diubah ditambah satu KLU di luar tabel. Metode: ketiga nilai.
4. **Pola kerja.** Setahun penuh; masuk pada bulan $s(u)$; berhenti sebulan sesudah $s(u)$.
5. **Komponen.** Gaji pokok + tunjangan tetap; varian dengan THR dan bonus di bulan $s(u)$; natura untuk setiap jenis yang dirujuk unsur; zakat.
6. **Ukuran.** Kombinasi dengan cakupan 2-arah atas dimensi di atas, maksimal 300 kasus per kandidat; ω ∈ {$t_\mathit{terbit}$ − 1 hari, $t_\mathit{terbit}$}.
7. **Keterpisahan dari $S^E$.** Setiap kasus $S^G$ memuat komponen penanda `income.other_regular` = 7 rupiah (ikut dihitung saat mencari ambang), dan $S^E$ tidak pernah memakai komponen itu. Keterpisahan juga diperiksa langsung atas kunci kanonik tupel. Irisan harus kosong.

---

## 6. Analisis dampak lintas lapis (RQ4)

**Definisi 9 (Terdampak).** Kebijakan $P$ terdampak oleh peristiwa $\epsilon_n$ bila, pada tupel $S^E$ yang memuat $P$, dengan ω = $t_\mathit{terbit}$:
- **(a)** nilai fakta yang **dihasilkan aturan $P$** berubah untuk minimal satu observasi $t \ge t_\mathit{berlaku}$, antara $\mathcal{K}^\star_{n-1} \oplus P$ dan $\mathcal{K}^\star_n \oplus P$;
- **(b)** aturan pemenang suatu fakta yang dihasilkan atau dibaca aturan $P$ berubah untuk minimal satu observasi (dari jejak);
- **(c)** muncul entri konflik baru yang melibatkan $P$.

Definisi (a) dibatasi ke fakta milik $P$; perubahan PPh pegawai karena peristiwa regulasi saja bukan dampak pada kebijakan. Label (a) dan (b) diturunkan dari eksekusi; label (c) dari laporan konflik eksekusi dan dibandingkan dengan label manual yang sudah ada (klausul PKB dan kebijakan sintetis) dengan Cohen's κ. Pasangan positif bila (a) ∨ (b) ∨ (c); *recall* dan $F_2$ dihitung atas gabungan ini, dan per jenis sebagai diagnostik. Prevalensi positif dilaporkan untuk menafsirkan pembanding "tandai semua".

**Detektor (usulan).** Statis pada graf $\mathcal{K}_n \oplus P$ dengan masukan $\Delta$ ($\Delta^\star$ atau $\hat{\Delta}$):
1. $F_\Delta$ = fakta yang dihasilkan unsur $\Delta$, ditambah fakta yang dihasilkan aturan yang memakai parameter atau tabel di $\Delta$;
2. penutup hilir $F^\downarrow_\Delta$ lewat `pph:reads`;
3. aturan $P$ yang membaca fakta di $F^\downarrow_\Delta$ dengan masa berlaku beririsan dengan masa berlaku unsur $\Delta$ → (a);
4. aturan $P$ yang menghasilkan fakta yang juga dihasilkan aturan di $\Delta$ dengan masa berlaku beririsan → (b), dan bila aturan $\Delta$ itu `mandatory` → (c);
5. batasan di $\Delta$ yang membaca fakta yang dihasilkan aturan $P$ → (c).
Kueri SPARQL di `system/ontology/queries/impact_*.rq` (pemanggil `system/pph21kbs/impact.py`).

**Pembanding B5.** (i) tandai semua kebijakan yang menyentuh fakta mana pun di $F^\downarrow_\Delta$ tanpa memeriksa masa berlaku; (ii) penelusuran dependensi datar tanpa graf (pemindaian teks ekspresi); (iii) penilaian LLM (*effort* `low`).

---

## 7. Pembanding yang memakai kandidat yang sama

- **B3**: kandidat pertama (urutan acak) yang lolos G1–G2, tanpa perbaikan.
- **B4**: suara terbanyak menurut perilaku atas $m$ kandidat **awal** (sebelum perbaikan), tanpa gerbang. B4 memakai $m$ panggilan, lebih sedikit daripada usulan ($m(1 + \bar{r})$); selisih anggaran dilaporkan eksplisit. Kandidat hasil perbaikan tidak dipakai B4 karena perbaikannya memakai umpan balik gerbang.
- **AB3** (tanpa G5, tanpa G4, tanpa perbaikan) dan **AB4** (pertama lolos, konsensus, pilihan sempurna) dihitung ulang dari kandidat dan log gerbang yang sama.

---

## 8. Konfigurasi LLM, pencatatan, dan anggaran

| Hal | Nilai |
|---|---|
| Model utama | `claude-opus-5-5` (*cutoff* Juni 2026, `dataset/09_korpus_peristiwa/model_cutoff.csv`), *adaptive thinking* (tidak dapat dimatikan), `output_config.effort` = `high` untuk penyusunan dan perbaikan, `medium` untuk relevansi, `low` untuk B5(iii) |
| Model kedua | `gpt-6.1-sol` (*cutoff* 30 April 2026), `reasoning.effort` = `high`; hanya usulan dan B3 pada dokumen nyata |
| Sampling | tidak dapat diatur pada kedua model; keragaman kandidat dari sampling bawaan |
| Format keluaran | keluaran terstruktur dengan skema keluaran LLM (format_data.md §2.3) |
| *Fallback* model | tidak dipakai; penolakan model dicatat sebagai kegagalan kandidat |
| Penghematan | *prompt caching* untuk awalan bersama; Batch API (potongan 50%) untuk jalan eksperimen; $m = 5$ hanya pada dokumen nyata; kontrafaktual dan kebijakan sintetis $m = 1$ (strata diagnostik); kandidat dipakai ulang untuk B3, B4, AB3, AB4; AB1 dan AB2 pada subset dokumen; E3 dengan $R = 1$ dan pembangkitan ulang hanya bila $\mathcal{K}^\mathrm{sis}_{n-1} \ne \mathcal{K}^\star_{n-1}$ |
| Harga (Okt 2026) | Opus 5.5: USD 4 / 20 per 1 juta token masukan/keluaran, baca *cache* USD 0,20, tulis *cache* 1,25×; GPT-6.1 Sol: USD 2 / 10 |
| Anggaran | USD 15 total. Perkiraan per kandidat (masukan ±16.000 token sebagian dari *cache*, keluaran termasuk *thinking* ±6.000 token): ±USD 0,07–0,10 dengan Batch. Rincian per eksperimen ditetapkan setelah pengukuran pada data pengembangan (Tahap 11) dan dikunci di pra-registrasi; pencatat menghentikan jalan bila biaya kumulatif melewati batas per eksperimen |

Setiap panggilan dicatat (JSONL, format_data.md §6): waktu, model diminta dan dilaporkan API, *effort*, langkah, dokumen, kandidat, SHA-256 *prompt*, isi *prompt* (berkas terpisah), keluaran mentah, `stop_reason`, token masuk/keluar/*cache*, biaya, durasi, dan hasil setiap gerbang. Semua analisis dapat diulang dari log tanpa memanggil LLM lagi.

---

## 9. Nilai yang ditetapkan di sini

| Hal | Nilai | Dasar |
|---|---|---|
| $m$ | 5 (dokumen nyata) | Log keputusan |
| Putaran perbaikan | 1 | Log keputusan |
| Seri konsensus | *abstain* | Log keputusan |
| Kuorum | tidak ada (kelompok terbesar ≥ 1) | bagian 3.6 |
| $R$ (pengulangan E3) | 1 | Log keputusan "Anggaran API" |
| Anggaran masukan segmen | 14.000 token (ditinjau di Tahap 11) | bagian 3.1 |
| Batas $S^G$ | 300 kasus per kandidat | bagian 5 |

---

## 10. Pemenuhan kotak "Harus didefinisikan" *skeleton* Bagian V

| Butir *skeleton* | Bagian |
|---|---|
| Definisi peristiwa, pembaruan, syarat adaptif, adaptivitas representasional dan operasional | 1–2 |
| Prosedur uji otomatis A1–A4 | 2 |
| Semantik berlaku surut menurut mekanisme hukum | 2 (dan tafsir_korpus B0–B5) |
| Daftar *constraint* G1 | 4 (G1) |
| Cara G2 mencocokkan kutipan | 4 (G2) |
| Cara membangkitkan $S^G$; $S^G \cap S^E = \varnothing$ | 5 |
| $m$, batas perbaikan | 9 |
| Cara mengelompokkan kandidat | 3.6 |
| Syarat pembekuan G5 | 4 |
| Arti *terdampak* (a), (b), (c) | 6 |
| Konfigurasi LLM yang dicatat | 8 |
| Tabel lampiran: alat ekstraksi | 3.1 |

## 11. Riwayat revisi

| Versi | Tanggal | Perubahan |
|---|---|---|
| 1 | 2026-10-27 | Draf pertama |
| 2 | 2026-10-27 | Tanggapan atas tinjauan independen: peristiwa kebijakan dan basisnya; penerapan longgar untuk mode berantai; satuan tupel/observasi, mode berantai, $H_n$; tanggal mulai efek untuk G4/G5; penutupan dibebaskan dari G5; `recorded_on` = $t_\mathit{terbit}$; pola tertutup pendaratan tanggal dan nilai; G3.4 menjadi peringatan; definisi (a) dibatasi ke fakta milik kebijakan; RA peristiwa nyata diukur dengan acuan independen; skema keluaran LLM terpisah; B4 dari kandidat awal; penanda $S^G$; variasi atribut kasus di $S^G$; A1 mencakup paket `kb/`; anggaran dan harga dicatat |
