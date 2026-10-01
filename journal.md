# Jurnal Riwayat Penggunaan AI — Proyek KB PPh 21

Catatan kronologis kolaborasi dengan asisten AI dalam proyek *Kalkulator PPh Pasal 21 Berbasis Knowledge Base Dua Lapis Berversi Waktu*. Isinya: apa yang diminta, apa yang dikerjakan AI, keputusan apa yang diambil dan oleh siapa, kesalahan yang ditemukan, serta hal yang masih harus diverifikasi manusia.

## Identitas sesi

| Butir | Keterangan |
|---|---|
| Asisten AI | Claude Code (ekstensi VS Code), model Claude Opus 5.5 (`claude-opus-5-5`) |
| Pengguna | obikast (mahasiswa S2 Informatika, mata kuliah KBS) |
| Tanggal | 1 Oktober 2026, ±11.14–16.50 WIB, satu sesi dengan dua kali pemadatan konteks |
| Pemakaian tool oleh AI | 314 panggilan: Bash 144, Edit 78, Write 62, Read 14, Agent 4, AskUserQuestion 3, lainnya 9 |
| Hasil | `research_plan.md`, `dataset/`, `engine/`, `kb/`, `baselines/`, `eksperimen/`, `tests/`, `README.md`, `ui/` (demo Streamlit), 10 commit lokal (belum di-*push*; UI belum di-commit) |

## Batas peran AI

- **AI dipakai sebagai asisten riset dan pemrograman, bukan sebagai komponen sistem.** Kalkulator tidak memakai LLM sama sekali, juga tidak sebagai baseline (keputusan pengguna, jawaban no. 7). Semua angka pajak dihitung oleh mesin inferensi deterministik dari KB YAML/CSV.
- **Kebenaran ditetapkan oleh teks regulasi, bukan oleh AI.** Setiap aturan di KB mencantumkan pasal sumbernya. Setiap selisih diputuskan dengan merujuk ke pasal (`eksperimen/adjudikasi.md`). Hasil AI diperlakukan sebagai klaim yang harus lolos uji, bukan sebagai kebenaran.
- **Keputusan ruang lingkup diambil pengguna.** AI mengajukan pilihan beserta rekomendasi, dan pengguna yang memilih (lihat bagian *Keputusan pengguna*).
- **Data pribadi.** `payroll_calculator.xlsx` memuat sheet tersembunyi berisi nama, NIK, dan NPWP. AI hanya membaca sheet kalkulator dan sheet parameter. File ini diabaikan git dan tidak dipublikasikan. Studi kasus memakai nama anonim "Perusahaan X".

---

## Kronologi

Waktu dalam WIB, dibulatkan ke menit. Prompt pengguna dikutip apa adanya.

### 11.14 — Permintaan awal

> "Saya ingin melakukan penelitian untuk membuat sistem perhitungan pph21 menggunakan sistem knowledge base yang mengakomodir baik regulasi pemerintah maupun internal perusahaan. [...] Anggap dirimu sebagai researcher, buat ini research plan yang sangat detail (research plan.md). [...] Sebelum kamu mulai research, ada yang ingin kamu tanyakan?"

**Yang dikerjakan AI:**
- Membaca proposal lama.
- Membedah sheet *Calculator PPh21 v8* dan sheet parameter di xlsx.

**Temuan awal:**
- xlsx memakai rezim 2023 (PER-16, disetahunkan), bukan TER.
- xlsx sudah berisi kebijakan perusahaan nyata: prorata hari kerja, kenaikan gaji tengah bulan, dan perlakuan premi BPJS.
- Ada dugaan bug pada PTKP K/I/0.
- Tidak ada gross-up di xlsx.

AI lalu menyusun 11 pertanyaan klarifikasi.

### 11.18 — "berikan dalam bentuk pertanyaan agar saya langsung jawab perpoint"

AI mengajukan pertanyaan dalam tiga putaran (AskUserQuestion). Jawabannya dirangkum di bagian *Keputusan pengguna*.

### 11.18–13.07 — Menyusun rencana riset dan mengumpulkan data

**Yang dikerjakan AI:**
- **Regulasi.** Mengunduh 33 PDF regulasi, lalu mengekstraksi tabel PTKP, Pasal 17, TER bulanan/harian, BPJS, dan KLU DTP lengkap dengan pasal dan halaman.
- **Contoh resmi.** Mengumpulkan 46 contoh perhitungan dari lampiran PMK 168/2023, PP 58/2023, PER-16/PJ/2016, dan PMK 10, 72, 105/2025.
- **Pembanding.** Mensurvei 7 repo open source dan kalkulator online. Hasilnya, ketujuh library punya kesalahan terverifikasi, dan hanya 1 dari 4 yang bisa dijalankan memberi angka benar pada kasus acuan.
- **Data publik.** Mengambil data BPS dan Kemnaker.
- **Data sintetis.** Menulis generator kasus sintetis strata S1–S8.
- **Rencana.** Menulis `research_plan.md` (±850 baris).

**Temuan:** contoh resmi pun bisa salah. Ada salah cetak di PMK 168, PMK 105, dan PER-16. Contoh PMK 10/2025 dan PMK 105/2025 juga berbeda tafsir soal plafon biaya jabatan.

### Arahan pengguna: "Hati hati terhadap modul kalkulator yang sudah ada, takutnya perhitungannya salah"

Dampaknya: semua pembanding (xlsx, library, kalkulator online) ditempatkan sebagai *sistem yang diuji*, bukan oracle.

### 13.34 — "bagaimana cara tahu bahwa perhitungan pajak nya sudah benar? apa pembandingnya?"

AI menjelaskan piramida oracle tanpa SME. Kriterianya: cocok sampai rupiah terakhir. Pembanding hanya berfungsi memancing selisih.

| Lapis | Sumber kebenaran |
|---|---|
| V1 | Contoh resmi |
| V2 | Differential testing yang diadjudikasi ke pasal |
| V3 | Relasi metamorfik |
| V4 | Z3 |

### 13.37 — "analisa dan evaluasi research plan kita [...] selisih 1 rupiah pun dapat menjadi masalah"

AI melakukan audit kritis dan menemukan 16 celah. Lima celah kritis:

1. **Tidak ada kontrak aritmetika.** Uji AI pada grid tarif TER menunjukkan float menghasilkan **700 selisih Rp1**, misalnya 0,29 × 3.000 = 869,999…. PyYAML juga membaca `0.29` sebagai float.
2. **Aturan pembulatan tidak ditetapkan.** Hanya 1 dari 170 contoh TER resmi yang menghasilkan pecahan, jadi pembulatan nyaris tak teruji.
3. **Sumbu waktu tidak didefinisikan.** Menurut PMK 168 Ps. 19, masa pajak ditentukan saat terutang.
4. **Target akurasi masih bertoleransi** (≥ 99,9%, MAE).
5. **Koreksi Desember bisa menutupi galat bulanan.**

### 14.07 — "Perbaiki"

**Yang dikerjakan AI:**
- Rencana diperbarui menjadi ±1.090 baris.
- §6.9 Kontrak Presisi Numerik & Waktu: uang bertipe `int`, tarif berupa pecahan dari string, float dilarang, registri pembulatan, interval (a, b], model tiga tanggal, dan validasi input ketat.
- Hierarki otoritas dan rentang tafsir.
- Tingkat bukti BK-1..4 per aturan.
- Double-entry tabel.
- Kriteria lulus menjadi **0 selisih tak terjelaskan**.
- Eksperimen baru E10/E11 dan ablasi A8/A9.

### 14.44 — "xlsx itu bukan patokan kebenaran, cuma referensi, bisa salah. apakah kita sudah siap untuk memulai research nya?"

AI mengonfirmasi bahwa xlsx tidak dipakai sebagai kebenaran. Ada tiga prasyarat:

1. Inisialisasi git dengan `.gitignore` yang mengecualikan xlsx, repo tanpa lisensi, dan `env/`.
2. Pembaca kedua untuk daftar asumsi.
3. Akses manual ke kalkulator DJP.

### 14.55 — "silahkan mulai" → WP1a kontrak presisi

Di tengah pekerjaan, pengguna menambahkan: *"gitnya silahkan initiate"*.

**Yang dibangun AI:** `engine/angka.py`, `pembulatan.py`, `muat.py`, `interval.py`, `waktu.py`, `audit.py`, beserta 135 tes.

**Hasil uji:**

| Uji | Hasil |
|---|---|
| TER bulanan | 169/170 cocok. Satu-satunya selisih jatuh di salah cetak PMK168-B-I.6 yang sudah dikonfirmasi |
| Pasal 17 | 25/25 cocok |

**Temuan:**
- Ada titik pembulatan ke-9 (proporsi n/12).
- Ada dua jebakan YAML: kunci ganda saling menimpa, dan `1.0e+3` dibaca sebagai float.
- AI sempat salah menamai mode pembulatan Excel `ROUND` untuk bilangan negatif, lalu memperbaikinya.

**Commit** `f04210b` (15.39).

### 15.38 — "lanjutkan dan lakukan perbaikan sampai research menghasilkan perhitungan pajak [...] benar sesuai dengan perhitungan pajak di dunia nyata."

Di tengah pekerjaan, pengguna menambahkan: *"untuk saat ini, fokus sampai pada program (code/model) dulu, tidak perlu menulis paper nya."*

AI mengerjakan paket kerja berikut berurutan.

| Waktu | Commit | Isi |
|---|---|---|
| 15.54 | `4807a4b` (tag `b1-frozen`) | Kodifikasi regulasi (`KODIFIKASI.md`), 45 kasus resmi kanonik (1.213 harapan, 20 erratum, 8 tafsir), baseline B1 *hard-coded*. B1 dibekukan **sebelum** KB ditulis agar menjadi implementasi independen |
| 16.06 | `ffcc469` | KB deklaratif rezim PER-16 dan TER, engine inferensi (*forward chaining*, Tarjan SCC), dan double-entry 512 sel tabel dari gambar halaman PDF |
| 16.15 | `2e982f9` | V2 differential KB vs B1 pada 2.201 kasus, dan solver titik tetap Tarski (terkecil/terbesar) |
| 16.19 | `9225626` | V3 metamorfik MR1–MR15 (Hypothesis) dan transaksi bertanggal |
| 16.26 | `7aa77d0` | Lapisan perusahaan dan E8 Perusahaan X vs xlsx |
| 16.40 | `431aae3` | Mutation testing (52 mutan, skor 100%), ablasi, peta gross-up integer, F1 deteksi konflik, CLI, dan rentang tafsir |
| 16.43 | `d0d5d2f` | E3 skenario perubahan aturan, bitemporal (*knowledge time*), dan PTKP berversi |
| 16.47 | `d0ce48d` | E7 ekspresivitas: katalog kebijakan, 17/19 tanpa ubah kode |
| 16.48 | `e4ba4a7` | README program |

AI menyampaikan ringkasan status akhir. Hasilnya ada di bagian *Hasil akhir*.

### 16.50 — "tulis journal.md untuk project ini." → "ini jurnal history ai ya, bukan paper"

Dokumen ini. Versi pertama ditulis di sini, lalu ditambah entri berikut.

### 19.32–19.42 — Tanya-jawab tentang program (tanpa perubahan kode)

| Pertanyaan pengguna | Isi jawaban AI |
|---|---|
| "apa saja yang sudah kita buat sejauh ini?" | Inventaris: rencana riset, data, program, dokumentasi |
| "kalau pemerintah mengeluarkan aturan baru, atau perusahaan mengeluarkan aturan baru, apa yang harus saya lakukan?" | Prosedur menurut jenis perubahan: parameter (tutup versi lama dengan `sampai`), tabel (tambah baris, perbarui hash manifest, double-entry), aturan baru, regulasi berlaku surut (`pencatatan.yaml`), dan kebijakan perusahaan. Setelah itu jalankan pytest dan V1 |
| "jelaskan seperti apa program dengan kb yang kamu buat? cara kerja nya bagaimana" | Arsitektur KB + mesin inferensi dan tujuh langkah inferensi, dengan contoh keluaran asli PMK168-B-I.1 |
| "apakah saya bisa memilih peraturan yang ingin dipakai untuk hitung?" | Yang bisa dipilih: tahun, tafsir (`--varian`), kebijakan perusahaan, versi KB per tanggal, dan KB alternatif. Yang sengaja tidak bisa: mematikan aturan wajib |
| "adakah file yang saya bisa jalankan untuk melihat demo perhitungan pajaknya?" | Perintah CLI untuk enam skenario. Semuanya dijalankan dulu oleh AI sebelum disarankan |

### 19.58–20.14 — Merancang UI demo

> "Bisakah program ini dibuat ada UI nya? [...] ada beberapa tab [...] 2 panel kanan kiri. kiri inputan, kanan hasilnya. Buat menarik. Bagaimana menurutmu, ada ide lebih baik?"

**Usulan AI:**
- **Teknologi.** Streamlit, karena UI bisa memanggil `hitung()` langsung sehingga logika pajak tidak ditulis ulang.
- **Ide tambahan:**
  - badge "cocok dengan contoh resmi";
  - tab Bandingkan;
  - tab Knowledge Base;
  - "Kenapa angka ini?".

Pengguna menolak form pertanyaan pertama dan bertanya dulu soal interaktivitas: *"apakah bisa interactive seperti user ubah value, lalu hasil langsung berubah?"* AI menjelaskan kapan hasil diperbarui untuk tiap jenis input dan berapa kecepatan engine.

Pengguna lalu meminta *"coba jelaskan ke saya apa yang ingin kamu bangun, biar kita saling paham"*. AI menulis rancangan berisi tata letak, daftar tab, dan aturan main. Aturan mainnya antara lain: tidak ada logika pajak di UI, dan badge kebenaran hanya tampil selama input belum diubah.

**Jawaban form pengguna:**

| Pertanyaan | Jawaban |
|---|---|
| Untuk siapa | Demo dan presentasi penelitian |
| Tampilan | Proyektor, tema terang |
| Fitur | Cek vs contoh resmi, Bandingkan, tab Knowledge Base, simpan/muat kasus |
| Urutan pengerjaan | Langsung semua |

### 20.14–21.10 — Membangun UI (`ui/`)

**Yang dibangun AI:**

| Berkas | Isi |
|---|---|
| `ui/data.py` | Konversi kasus kanonik ↔ tabel isian, format rupiah/persen eksak, preset dari dataset uji |
| `ui/hasil.py` | Panel hasil |
| `ui/tab_kasus.py` | Tab TER, Gross-up, DTP, dan PER-16 |
| `ui/tab_perusahaan.py` | Tab Perusahaan X: data HR mentah, KB dua lapis, perbandingan dengan xlsx beserta penjelasan K-02/K-04/K-11 |
| `ui/tab_bandingkan.py` | Lima skenario perbandingan |
| `ui/tab_kb.py` | Penjelajah aturan, graf ketergantungan, tabel, dan parameter |
| `.streamlit/config.toml` | Tema |
| `tests/test_ui.py` | 59 tes |

**Keputusan teknis AI:**
- **Badge cocok dihitung ulang langsung.** Badge "cocok dengan contoh resmi" memakai protokol V1 (`eksperimen.v1.bandingkan`) pada hasil engine. Angkanya tidak disalin ke UI.
- **Input default dijamin sama dengan dataset.** Tes memastikan konversi isian → kasus tidak mengubah input untuk ke-45 kasus resmi.
- **Kasus sintetis diberi label jelas.** Untuk skenario "titik tetap ganda" dibuat satu kasus sintetis: gross-up setahun dengan gaji Rp10,1 jt. Engine sendiri yang menemukan bahwa di gaji ini tunjangan pajak bulanannya punya dua jawaban sah, Rp232.480 dan Rp258.974. Kasus ini ditandai "bukan contoh resmi" dan tidak diberi badge kebenaran.
- **Kode UI juga bebas float.** UI tidak boleh memanggil `float()`/`round()`, dan ini dijaga oleh pemindai AST di tes. Tampilan persen memakai `Fraction`, dan nilai yang tidak berhingga ditandai "≈".

**Kesalahan yang ditemukan lewat AppTest dan screenshot headless Chromium, lalu diperbaiki:**

| Kesalahan | Asal | Koreksi |
|---|---|---|
| Opsi jenis kelamin tidak memuat nilai `tidak_disebutkan` dari kasus PER-16 | Kode AI | Opsi mengikuti nilai di kasus |
| Tombol "Perluas ke setahun" tanpa key unik sehingga bentrok antar-tab | Kode AI | Key per tab |
| `PRESET_TAB` merujuk `SINTETIS` sebelum didefinisikan | Kode AI | Daftar literal |
| Nilai metrik terpotong ("Rp64.7…") di layar proyektor | Tampilan | Maksimal tiga kartu per baris dan teks tidak dipotong |
| Tabel per masa memakai scroll, legenda grafik menimpa judul | Tampilan | Tinggi tabel mengikuti isi, legenda di kanan atas |
| f-string terpotong baris saat penyuntingan otomatis | Kode AI | Diperbaiki, tertangkap oleh pytest |
| Tes membaca metrik lewat label yang dipakai di beberapa tab | Tes AI | Tes membaca metrik pertama (tab TER) |

**Paket baru:** `streamlit` 1.64 dan `plotly` 7.1 di venv `env`, dicatat di `requirements.txt`. `playwright` juga dipasang, tetapi hanya untuk screenshot verifikasi AI dan tidak menjadi dependensi aplikasi.

### 21.30–21.32 — Cara menjalankan UI

Pengguna bertanya cara menjalankan UI, dengan dan tanpa awalan `env\Scripts\`. AI menjelaskan dua cara: mengaktifkan venv lalu `streamlit run ui\app.py`, atau memakai Python global. Cara kedua tidak disarankan.

### 21.37–22.13 — Pengguna meluruskan arah UI

> "bisa jelaskan apa yang kamu buat ini? sedikit berbeda dari gambaran saya"

> "Yang saya bayangkan adalah sebuah kalkulator dimana kiri adalah inputan data diambil dari dataset (default) dan bisa diedit oleh user [...] kanan adalah perhitungan pajaknya, lengkap dengan detail dan pasal yang dikenakan. lalu ada 1 tab untuk melihat knowledge base [...] Inputan yang ada ini adalah inputan nilai dari manusia, anggaplah admin finance, bukan konfigurasi sistem. Payroll calculator ini harus benar dan berperilaku seperti payroll calculator sungguhan. [...] sebelum ubah, beritahu dulu seperti apa rancanganmu"

> "Mari kita fokus ke 2 tab dulu: 1. Tab kalkulator (With and Without KB) [...] Ada 2 jenis payroll calculator, 1 tanpa KB, 1 dengan KB, identik. Tapi mekanisme nya berbeda. Input Ini harus benar dan sesuai kondisi nyata, tidak boleh mengarang dari kasus yang tidak pernah ada. [...] 2. Tab knowledge base [...] buat mudah dipahami."

**Penilaian ulang atas rancangan sebelumnya:** UI versi pertama terlalu dekat dengan alat riset. Ada pilihan tafsir, berkas kebijakan, kategori pajak, dan tab per rezim, sementara isiannya meniru struktur dokumen PMK. Ada juga satu kasus sintetis gross-up yang dibuat AI sendiri. Kasus ini dibuang karena melanggar arahan "tidak boleh mengarang dari kasus yang tidak pernah ada".

**Keputusan pengguna lewat form:**

| Pertanyaan | Jawaban |
|---|---|
| Bentuk dua kalkulator | Dua sub-tab terpisah |
| Isi kalkulator tanpa KB | Pajak + kebijakan perusahaan |
| Data default | Karyawan A + contoh resmi + data sintetis berbasis data publik |
| Kebijakan yang dipakai | Kebijakan "Perusahaan X + katalog". Form lanjutan memperjelas bahwa katalog hanya ditampilkan di tab KB |
| Contoh resmi | Mode "komponen sudah jadi" |
| Dasar data sintetis | UMP + upah BPS |
| Tanda cek silang | Ya |

AI menyampaikan rancangan final. Pengguna menjawab: **"ya, terapkan"**.

### 22.13–22.45 — Membangun kalkulator dengan/tanpa KB

**Yang dibangun AI:**

| Bagian | Isi |
|---|---|
| `baselines/b2_payroll_hardcoded/payroll_b2.py` | Kalkulator payroll **tanpa KB**. Kebijakan Perusahaan X (prorata, kenaikan gaji tengah bulan, tunjangan, BPJS, THR, kompensasi, THP) dan konstanta BPJS ditanam di kode. Pajaknya memakai B1, yang tidak diubah karena sudah dibekukan. B2 tidak mengimpor engine dan tidak membaca berkas KB; ini diuji dengan pemindai AST |
| `kb/perusahaan/perusahaan_x.yaml` | Aturan THP ditambahkan, supaya take home pay keluar dari mesin dan bukan dihitung di UI |
| `engine/interval.py`, `engine/inferensi.py` | Keluaran `rincian_pasal17` (pajak per lapisan) untuk fasilitas penjelasan. Nilai PPh tidak berubah |
| `dataset/08_pegawai_sintetis/` | 8 pegawai sintetis. Gaji pokoknya **dibaca dari sel** UMP Kemnaker 2023–2026 dan upah rata-rata BPS Sakernas, dan sumbernya dicatat per pegawai |
| `eksperimen/e12_tanpa_kb.py` | Modul cek silang KB vs tanpa KB, berikut klasifikasi selisih yang sah |
| UI | Disusun ulang menjadi dua tab: Kalkulator (sub-tab Dengan KB dan Tanpa KB) dan Knowledge Base. Isinya: `ui/kalkulator.py`, `hasil.py`, `mesin.py`, `tab_kb.py`, `data.py`. Tab lama dihapus |
| Tes | `tests/test_b2_payroll.py` dan `tests/test_ui.py` ditulis ulang |

**Temuan dan koreksi selama pengerjaan:**

| Temuan | Asal | Penanganan |
|---|---|---|
| Aturan THP merujuk `pph21_dtp` dan `tunjangan_pajak` di tahun yang tidak memiliki fakta itu, sehingga engine menolak KB | KB AI | Engine sengaja tidak dilonggarkan, karena pemeriksaan statis ini berguna. Aturan THP dipecah per masa berlaku DTP dan gross-up secara eksplisit |
| B2 vs KB berbeda pada representasi: tarif `Fraction` vs string, DTP 0 vs tidak ada | Kode AI | Representasi B2 disamakan |
| 16 dari 192 variasi gross-up/ditanggung berbeda Rp250 di masa terakhir | Bukan bug | Diverifikasi: KB melaporkan `GROSSUP_GANDA` dengan titik terkecil −1.159.683 dan terbesar −1.159.433, dan nilai B1 sama persis dengan yang terbesar. Ini fenomena A-02 yang sudah diadjudikasi. Tes hanya menerima selisih ini bila terjelaskan |
| Tanggal Idul Fitri 2026 mula-mula ditebak 20 Maret | Ingatan AI | Diverifikasi lewat web: SKB 3 Menteri menetapkan 21 Maret 2026. Keempat tanggal (2023–2026) sekarang memakai URL sumber |
| Nomor SKB 2023–2025 sempat ditulis dari ingatan | Ingatan AI | Dihapus. Hanya rujukan yang diverifikasi yang dipakai |
| ID elemen Streamlit ganda antar-sub-tab, dan pilihan bulan slip tertinggal dari data sebelumnya | Kode AI | Key unik per mesin, data, dan daftar bulan |

**Hasil verifikasi:**
- KB dan tanpa KB identik sampai rupiah untuk Karyawan A 2023–2026, 8 pegawai sintetis, dan seluruh variasi isian dengan metode gross.
- Ke-45 contoh resmi cocok sampai rupiah di **kedua** mesin. Ini diuji di UI lewat AppTest untuk setiap contoh.

---

## Keputusan pengguna

Keputusan diambil pengguna. AI hanya menyiapkan opsi dan rekomendasi.

| No. | Pertanyaan AI | Jawaban pengguna |
|---|---|---|
| 1 | Skala riset | Tugas KBS saja |
| 2 | Tahun pajak | Semua (2023–2026), untuk mengevaluasi pengaruh perubahan KB |
| 3 | Izin memakai xlsx | Boleh, dianonimkan |
| 4 | Data payroll riil | Tidak ada; pakai dataset Indonesia yang relevan |
| 5 | SME untuk validasi | Tidak ada; pengguna meminta alternatif. Disetujui validasi berlapis: contoh resmi, differential, metamorfik, dan Z3 |
| 6 | Metrik evaluasi | Diserahkan ke AI untuk dipilih yang tepat secara ilmiah |
| 7 | LLM sebagai baseline | **Tidak.** Alasan pengguna: "llm bisa halusinasi dan tidak teliti" |
| 8 | Formalisme KB | YAML DSL + *forward chaining* |
| 9 | Fokus novelty | KB dua lapis + versi waktu |
| 10 | Timeline | Diabaikan |
| 11 | Izin unduh dan instalasi | Ya, instalasi di venv `env` |

**Arahan lanjutan pengguna yang mengubah arah kerja:**
- Kalkulator yang sudah ada bisa salah.
- Selisih Rp1 pun masalah.
- xlsx hanya referensi.
- Fokus pada program, bukan paper.

---

## Kesalahan dan koreksi selama pengerjaan

Kesalahan berikut dibuat atau ditemukan selama sesi. Semuanya sudah diperbaiki dan dikunci dengan tes.

| Kesalahan | Asal | Koreksi |
|---|---|---|
| Generator dan B1 sempat memakai floor float | Kode AI | Diganti seluruhnya dengan `Fraction` |
| Strata S2 menaruh gaji, bukan bruto, di batas lapisan TER, dan ujung pita gross-up meleset Rp1 | Kode AI | BPJS dinonaktifkan di strata itu, dan pita (lo, hi] diverifikasi ulang |
| Contoh DSL di rencana merujuk pasal yang salah | Tulisan AI | Diganti menjadi Pasal 15(1)a |
| Mode pembulatan Excel `ROUND` bilangan negatif salah dinamai | Tulisan AI | Mode `setengah_menjauhi_nol` |
| B1: kondisi `bulan None == terakhir None` bernilai benar | Kode AI | Diperbaiki **sebelum** B1 dibekukan |
| KB dan B1 berbeda Rp150–250 di 25 kasus gross-up | Bukan bug. Keduanya titik tetap yang sah, dan hasilnya bergantung urutan iterasi | Solver Tarski terkecil/terbesar dan peringatan `GROSSUP_GANDA`. Hipotesis H5c gugur: 154 dari 998 kasus punya titik tetap Desember ganda |
| Nilai `350000.0` dari xlsx masuk sebagai float | Data | Ditolak di pintu masuk (`InputTidakValid`) |
| Variabel tertimpa di `muat_kb` | Kode AI | Diganti nama |
| Mutation testing menemukan celah yang lolos dari semua uji: tabel yang tak tersentuh V1, batas BPJS Kes, tumpang tindih versi Pasal 17, kondisi ditanggung, dan asumsi n/12 | Celah uji | Ditutup dengan double-entry permanen, pemeriksaan statis, properti baru, dan tafsir eksplisit R16-05-N |
| 20 angka di contoh resmi salah cetak | Dokumen resmi | Dicatat sebagai ERRATUM dengan nilai koreksi dan alasan per pasal |

---

## Hasil akhir

| Uji | Hasil |
|---|---|
| V1: 45 kasus resmi, 1.213 angka | 0 selisih tak terjelaskan (1.185 cocok, 20 erratum, 8 tafsir); KB = B1 |
| V2: 2.201 kasus sintetis | 0 galat; semua selisih teradjudikasi |
| V3: MR1–MR15 | Lulus |
| Double-entry tabel | 512 sel cocok 100% |
| Mutation testing | 52 mutan, skor 100% |
| Deteksi konflik kebijakan | F1 = 1,0 (42 pemetaan berlabel buatan sendiri) |
| E3: perubahan aturan | 0 berkas engine berubah; impact F1 = 1,0; regresi 0 |
| E7: ekspresivitas | 17/19 kebijakan tanpa ubah kode |
| E8: Perusahaan X | 12 komponen identik dengan xlsx; selisih PPh Rp56.250 karena xlsx menghilangkan premi BPJS Kes Desember (temuan K-04) |
| E9: kinerja | ±38 ms per pegawai-tahun |

## Belum diverifikasi manusia

Butir-butir ini sengaja tidak diselesaikan oleh AI dan memerlukan tindakan pengguna:

1. **Kalibrasi ke kalkulator DJP (E10).** Kalkulatornya memakai CAPTCHA, jadi harus dikerjakan manual. Sampai dikalibrasi, default tafsir pembulatan masih asumsi, dan sistem menampilkan rentang tafsirnya.
2. **Pembaca kedua untuk daftar asumsi A-01..A-04** di `kb/regulasi/KODIFIKASI.md`. Semua kodifikasi dan adjudikasi dibuat oleh pasangan pengguna–AI yang sama, sehingga oracle-nya belum independen penuh.
3. **KLU 96129.** Kode ini hanya ada di PMK 105/2025 dan baru diekstraksi dari lapisan teks. Perlu dicek ke gambar halaman.
4. **Label uji F1 konflik** dibuat sendiri, bukan oleh pihak independen.
5. **Review kode** oleh pengguna sebelum dipakai di luar konteks tugas.

### Lanjutan — Membersihkan kode lama, setup, dan requirements

| Permintaan pengguna | Yang dilakukan AI |
|---|---|
| "bisakah kamu hapus sisa kode dari versi sebelumnya yang tidak dipakai" | Menghapus fungsi dan konstanta UI versi lama yang tidak lagi dirujuk: `ganti_tahun`, `berkas_perusahaan_tersedia`, `PERINGATAN`, `SATUAN`, `BULAN_DARI_NAMA`, beserta import yang tidak terpakai. Pengecekan memakai pyflakes, yang dipasang sementara lalu dicopot, ditambah pemindai rujukan |
| "buat atau perbarui readme tentang cara setup dan menjalankan project ini, update requirements.txt" | `requirements.txt` disusun ulang menjadi dependensi langsung yang dipin. `requirements-lock.txt` berisi versi persis seluruh paket, tanpa playwright yang hanya alat screenshot AI. `requirements-ekstraksi.txt` berisi alat ekstraksi PDF yang opsional. README ditulis ulang: prasyarat, instalasi (Windows/macOS/Linux), cek instalasi, berkas yang sengaja tidak ada di repo, cara menjalankan UI/CLI/API/tes/eksperimen, dan masalah umum |

**Verifikasi:** sebuah venv baru dibuat dari nol dan hanya dipasang dari `requirements.txt`. Seluruh tes lulus di sana (383 lulus, 8 dilewati), jadi berkas itu memang cukup untuk menjalankan project.
