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

**Sesi lanjutan, 2–4 Oktober 2026** (ditulis 4 Oktober):

| Butir | Keterangan |
|---|---|
| Asisten AI | Claude Code (ekstensi VS Code), model Claude Opus 5.5 (`claude-opus-5-5`). Untuk audit, telaah, dan perbaikan dipakai juga sub-agen dari model yang sama (workflow multi-agen) |
| Pengguna | Akun git `mahathirmuh`; commit berzona +08:00. Sesi 1 Oktober di atas tercatat atas nama `obikast` (commit berzona +07:00). Riwayat git tidak menunjukkan apakah kedua akun milik orang yang sama |
| Tanggal | 2–4 Oktober 2026, satu sesi panjang dengan beberapa kali pemadatan konteks |
| LLM di dalam produk | Hanya di `asisten_kb/`, dan bukan asisten AI yang menulis kode. Bawaannya `gpt-5.6-sol` lewat API OpenAI; model `claude-…` lewat API Anthropic juga didukung, dan versi pertama (`f377592`) memakainya sebagai bawaan. Terhadap API sungguhan, pada 2 Oktober: beberapa panggilan kecil untuk memeriksa kunci dan akses model, dan satu kali alur penuh yang berbayar |
| Hasil | `web/`, `jembatan/`, `asisten_kb/`, `kb/tambahan/`, perubahan `engine/` dan `kb/`, tes, dan Adendum A di `research_plan.md`; 20 commit (`4b8d87a` s.d. `47af9a8`) sebelum entri ini ditulis, semuanya sudah di-*push* |
| Catatan untuk tabel di atas | Sesi 1 Oktober berakhir dengan 13 commit (s.d. `5630897`), yang kini juga sudah di-*push* |

## Batas peran AI

- **AI dipakai sebagai asisten riset dan pemrograman, bukan sebagai komponen sistem.** Kalkulator tidak memakai LLM sama sekali, juga tidak sebagai baseline (keputusan pengguna, jawaban no. 7). Semua angka pajak dihitung oleh mesin inferensi deterministik dari KB YAML/CSV.
- **Kebenaran ditetapkan oleh teks regulasi, bukan oleh AI.** Setiap aturan di KB mencantumkan pasal sumbernya. Setiap selisih diputuskan dengan merujuk ke pasal (`eksperimen/adjudikasi.md`). Hasil AI diperlakukan sebagai klaim yang harus lolos uji, bukan sebagai kebenaran.
- **Keputusan ruang lingkup diambil pengguna.** AI mengajukan pilihan beserta rekomendasi, dan pengguna yang memilih (lihat bagian *Keputusan pengguna*).
- **Data pribadi.** `payroll_calculator.xlsx` memuat sheet tersembunyi berisi nama, NIK, dan NPWP. AI hanya membaca sheet kalkulator dan sheet parameter. File ini diabaikan git dan tidak dipublikasikan. Studi kasus memakai nama anonim "Perusahaan X".
- **Sejak 2 Oktober 2026 ada LLM di repositori, tetapi di luar kalkulator.** `asisten_kb/` memakai LLM untuk menyusun *rancangan* berkas KB dari PDF peraturan. Engine tetap tidak memakai LLM, dan semua angka pajak tetap dihitung mesin inferensi. Rancangan baru berlaku setelah validasi engine dan persetujuan manusia. Ini bertentangan dengan bunyi D6 dan §4.3 rencana yang dikunci; batasnya dicatat di Adendum A `research_plan.md`.

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

## Kronologi lanjutan: 2–4 Oktober 2026

Bagian ini **direkonstruksi pada 4 Oktober 2026** dari riwayat git dan catatan sesi; tidak ditulis saat kejadian seperti kronologi 1 Oktober. Waktu adalah stempel commit dalam zona +08:00, bukan WIB. Prompt pengguna dikutip apa adanya; kredensial dan path lokal tidak dikutip. Kutipan prompt, rincian panggilan API, angka audit, dan jumlah agen berasal dari catatan sesi dan tidak punya artefak di repositori. Sejak sesi ini commit dibuat atas nama akun git pengguna tanpa baris atribusi AI (keputusan no. 13), sehingga jurnal inilah catatan keterlibatan AI.

### 2 Oktober, sebelum 14.10 — Mempelajari proyek

| Permintaan pengguna | Yang dilakukan AI |
|---|---|
| "pelajari project ini" | Membaca rencana riset, engine, KB, baseline, eksperimen, dan UI, lalu merangkumnya |
| "coba install requirements" | Membuat venv `env` (Python 3.12) dan memasang `requirements.txt` |
| "ini method ml nya menggunakan apa ? diskusi disini" dan "berarti gak bisa dijadikan paper ya ini ?" | Diskusi tanpa perubahan kode: sistem ini berbasis aturan dan mesin inferensi, bukan *machine learning*; dibahas juga peluang publikasinya |

### 2 Oktober 14.10–15.09 — Aplikasi web Laravel

> "tolong buatkan dengan framework laravel, apakah bisa ? diskusi disini dahulu"

**Usulan AI:** arsitektur hibrida. Laravel mengurus antarmuka, pengguna, dan database. Engine Python tetap satu-satunya penghitung dan dipanggil lewat jembatan JSON (`python -m jembatan`), sehingga logika pajak tidak ditulis ulang di PHP. Pengguna menjawab: **"ikuti rekomendasimu"**.

| Waktu | Commit | Isi | Permintaan pengguna |
|---|---|---|---|
| 14.10 | `4b8d87a` | Aplikasi web untuk admin finance dan jembatan JSON ke engine | Lihat kutipan di atas |
| 14.16 | `8aae359` | Port bawaan 8100 | "eh ini laravelnya jalan di port berapa ? baiknya di ubah deh, kalau default 8000, ini sudah dipakai" |
| 14.53 | `4272b9c` | Struktur modul dan gaya tampilan mengikuti proyek templat milik pengguna | Pengguna menunjuk proyek templatnya sebagai acuan gaya dan bentuk |
| 15.03 | `378a802` | Halaman login mengikuti templat yang sama | Pengguna meminta halaman login mengikuti templat itu dan mempersilakan AI mencari gambarnya |
| 15.09 | `e489573` | Indikator carousel berupa garis yang terisi | "sepertinya jangan kelihatan bentuk gambar gini, baiknya kek bentuk - tapi berisi gitu, jadi nampak bagus carouselnya, atau rekomendasimu deh" |

Di tengah pekerjaan, pengguna menambahkan: *"auto commit & push setiap selesai action, pastikan authornya bukan claude"*.

### 2 Oktober 16.07–16.48 — Berkas KB tambahan dan asisten KB (LLM)

> "Buat sekarang itu yang perlu ditambahin yakni 2: Upload pdf peraturan pemerintah/perusahaan -> llm parsing -> masuk knowledge base. Karena alasan pake knowledge base ini kan biar kalo ada rules baru, gak perlu update rumus di kode. Kendala nya, kalau trnyata peraturan baru itu butuh input value dari user, jadi panel kb itu juga harus support extra input kalau kb nya minta extra input."

**Rancangan AI.** LLM ditempatkan di luar `engine/` dan hanya menyusun *rancangan*: PDF → LLM (keluaran terstruktur) → berkas YAML → validasi engine (skema, verifikasi statis, simulasi) → persetujuan manusia di aplikasi web → `kb/tambahan/`. Engine tidak memanggil LLM, dan LLM tidak menghitung pajak.

Permintaan ini bertentangan dengan bunyi D6 dan §4.3 rencana yang dikunci. Tidak tercatat bahwa pertentangan itu dibahas dengan pengguna pada 2 Oktober; README dan docstring `asisten_kb/` saat itu malah mengutip §4.3 sebagai dasar "engine tetap bebas LLM". Pertentangannya baru dicatat pada 4 Oktober (Adendum A.2).

**Yang dibangun AI:**

| Bagian | Isi |
|---|---|
| `engine/`, `kb/skema/` | Perluasan DSL: `masukan` (isian baru yang diminta dari pengguna), amandemen `parameter` berversi, label komponen |
| `asisten_kb/` | Prompt dan inventaris KB (`konteks.py`), skema keluaran (`skema.py`), klien LLM (`llm.py`), konversi dan validasi rancangan (`rancangan.py`) |
| `jembatan/` | Perintah `masukan`, `usulkan`, dan `validasi` |
| `web/` | Menu Basis pengetahuan (unggah PDF, antrean, halaman tinjau, terapkan atau tolak) dan isian tambahan dinamis di form data HR |

Versi pertama memakai Claude lewat API Anthropic sebagai model bawaan. Pengguna lalu menetapkan modelnya:

> "llm nya nanti menggunakan model gpt-5.6"

| Waktu | Commit | Isi |
|---|---|---|
| 16.07 | `f377592`, `fb3864e` | Berkas KB tambahan, asisten KB (bawaan Claude), menu Basis pengetahuan |
| 16.15 | `49e2b9a` | Model bawaan `gpt-5.6` lewat OpenAI Responses API; jalur Anthropic tetap ada untuk model `claude-…` |
| 16.48 | `e40b97d` | Model bawaan `gpt-5.6-sol`; penanganan jawaban yang terpotong |

**Uji dengan API sungguhan.** Pengguna mengisi kunci API di `web/.env` (*"sudah ku input apikey nya, coba cek .env nya"*, lalu *"sudah, cek lagi"*). AI memeriksa keabsahan kunci dan akses model dengan beberapa panggilan kecil yang keluarannya dibatasi, tanpa menampilkan isi kunci: kunci pertama ditolak API, kunci pengganti diterima, dan alias `gpt-5.6` ditolak untuk proyek API pengguna sehingga bawaan diganti `gpt-5.6-sol`. Panggilan kecil itu juga yang memperlihatkan galat pada jawaban terpotong.

Setelah pengguna menyetujui satu panggilan berbayar (*"mau . . ikuti rekomendasimu"*), AI menjalankan alur penuh satu kali dengan PDF sintetis satu halaman berisi peraturan fiktif (uang transport, uang makan, bonus kinerja): 99 detik, 8.588 token masuk dan 6.532 token keluar. Rancangannya lolos validasi, dan hasil hitung di slip sesuai dengan isi peraturan fiktif itu menurut pemeriksaan AI sendiri. PDF dan keluarannya tidak disimpan di repositori, sehingga tidak dapat diperiksa ulang. **Ini uji asap (*smoke test*: memastikan alurnya hidup), bukan evaluasi mutu.**

### 2 Oktober 21.09 — PostgreSQL

Pengguna memberi nama database, host, dan sandi (tidak dikutip). AI memindahkan aplikasi web dari SQLite ke PostgreSQL lokal dan menyalin datanya; itu terjadi di luar repositori. Sandi hanya ada di `web/.env`, yang tidak ikut git. Commit `adc016c` hanya memuat penyesuaian pencarian yang peka huruf besar-kecil di PostgreSQL dan dokumentasinya.

### 3 Oktober — Audit menyeluruh dan perbaikan

> "ada lagi ?"

AI menjalankan audit multi-agen atas 65 berkas kode yang berubah sejak 2 Oktober: 71 temuan mentah, sekitar 30 akar masalah. Cacat kunci direproduksi dengan eksperimen sebelum diperbaiki. Workflow audit pertama terhenti karena batas pemakaian (217 agen gagal), lalu dilanjutkan dengan paket yang lebih kecil. Pengguna menjawab: **"lanjut"**.

| Waktu | Commit | Isi |
|---|---|---|
| 10.08 | `fe63736` | Engine: deklarasi ganda ditolak, amandemen berversi, ekspresi bertipe, pemuat YAML menolak anchor dan alias |
| 10.08 | `6265699` | Asisten dan jembatan: validasi tidak pernah melempar, simulasi mengikuti masa berlaku, penanda perubahan, perintah `periksa` |
| 10.08 | `b6db904` | Web: galat 500, antrean, sinkron berkas KB, rahasia tidak diwariskan ke proses Python, pengaman tes |
| 10.08 | `dbc9791` | README diselaraskan |
| 10.29 | `c835cce` | Jembatan dan audit: berkas KB tambahan hanya dari `kb/tambahan/`, versi KB dihitung sekali per proses, tes kontrak |
| 11.21 | `f28f7f3` | Web: Hitung semua per batch, pengaman angka per baris, isian yang ditolak PostgreSQL |

### 3–4 Oktober — Rekomendasi, Paket 1, dan dokumen riset

> "rekomendasikan"

AI menelaah sembilan butir keputusan yang tersisa dengan workflow 10 agen yang hanya membaca (7 analis, 2 peninjau, 1 pengkritik), lalu mengusulkan tiga paket pekerjaan dan lima pertanyaan. Sebelum engine disentuh lagi, AI menjalankan dua belas kali jalan dari sepuluh modul eksperimen pada commit `5630897` (keadaan 1 Oktober) dan `f28f7f3`: keluarannya identik byte demi byte.

Pengguna menjawab: **"ikuti rekomendasimu"**, lalu **"lanjut"**.

| Waktu | Commit | Isi |
|---|---|---|
| 4 Okt 07.31 | `b3e6986` | Engine: batas titik tetap dari aturan pemenang; amandemen parameter dan klasifikasi tidak bergantung urutan berkas |
| 4 Okt 07.31 | `7f208b2` | Asisten: simulasi metode gross-up, peringatan aturan tanpa efek dan isian yang punya nilai bawaan |
| 4 Okt 07.31 | `9cf61fb` | Web: zona waktu dari `APP_TIMEZONE`, kunci Hitung semua, perintah `payroll:hitung` |
| 4 Okt 07.31 | `47af9a8` | Dokumentasi |

Paket 1 dikerjakan workflow 9 agen: tiga pelaksana dengan berkas terpisah, tiga peninjau yang mencoba mematahkan hasilnya, dan tiga agen perbaikan. Peninjau engine menemukan dua regresi pada perbaikan batas titik tetap buatan AI; keduanya diperbaiki sebelum commit. Keluaran kedua belas jalan eksperimen sesudah Paket 1 tetap identik dengan sebelumnya.

Sesudah itu AI menulis entri jurnal ini dan Adendum A di `research_plan.md` (Paket 2). Sebelum di-commit, drafnya diperiksa tiga agen terhadap repositori dan riwayat git; temuan mereka (antara lain daftar commit yang tidak lengkap, asal keputusan D6 yang ditulis terlalu kuat, dan klaim "tanpa perubahan kode" yang berlebihan) diperbaiki lebih dulu.

### 4 Oktober — Paket 3, bagian pertama: field `menggantikan`

Sesuai keputusan no. 20, AI mengerjakan pencabutan tegas aturan: aturan baru menyebut `menggantikan: [ID]`, dan selama ia berlaku menurut tanggalnya aturan yang disebut keluar dari kandidat sebelum resolusi konflik. Dikerjakan workflow 7 agen: pelaksana engine dan pelaksana tampilan web sejajar; lalu peninjau engine sejajar dengan pelaksana asisten; lalu perbaikan engine, peninjau asisten dan web, dan perbaikan asisten.

| Waktu | Commit | Isi |
|---|---|---|
| 4 Okt 10.44 | `0d0bb3b` | Engine dan skema: field `menggantikan`, pemeriksaan saat muat, penyaringan saat evaluasi, kunci jejak `digantikan` |
| 4 Okt 10.44 | `b5739a5` | Asisten: skema usulan, galat fakta yang hilang, peringatan, prompt |
| 4 Okt 10.44 | `56bb943` | Web: tab jejak menampilkan aturan yang dicabut |

Agen peninjau menemukan lima cacat sebelum commit, dan semuanya diperbaiki:

- Engine: aturan titik tetap yang dicabut aturan lain dianggap tergeser oleh pemenang mana pun, sehingga KB yang sah ditolak dengan pesan yang menuduh aturan yang salah.
- Engine: penanda titik tetap aturan yang dicabut setahun penuh masih mengesahkan siklus, tidak setara dengan menutup `sampai`.
- Validasi: pengganti ber-`jika` yang menyempit di luar pegawai contoh lolos tanpa tanda. Kini diberi peringatan; galat tetap hanya bila terlihat pada pegawai contoh.
- Validasi: pengganti yang lebih sempit atas aturan dari rancangan yang sama tidak terdeteksi.
- Validasi: pada rantai pencabutan, galat dituduhkan ke aturan yang salah.

Sesudah perubahan ini keluaran dua belas jalan eksperimen tetap identik dengan sebelumnya; tes: 668 lulus dan 8 dilewati (Python), 101 lulus (web). Prompt asisten ikut berubah (cara mengganti aturan, peraturan pemerintah yang memperkenalkan komponen, nilai seperusahaan sebagai parameter) dan **belum dijalankan terhadap LLM sungguhan**: itu butuh izin pengguna untuk satu panggilan berbayar. Bagian kedua Paket 3 (arsip isi berkas KB per sidik dan log peristiwa) menunggu jawaban pengguna tentang status data di database.

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

**Keputusan pada sesi 2–4 Oktober** (akun git `mahathirmuh`):

| No. | Pokok | Keputusan pengguna |
|---|---|---|
| 12 | Aplikasi web | Laravel, dengan arsitektur hibrida usulan AI: engine Python tetap satu-satunya penghitung ("ikuti rekomendasimu") |
| 13 | Commit | "auto commit & push setiap selesai action, pastikan authornya bukan claude" |
| 14 | Port aplikasi | Bukan 8000; dipakai 8100 |
| 15 | Tampilan | Mengikuti proyek templat milik pengguna |
| 16 | Fitur PDF → LLM → KB, termasuk isian tambahan | Diminta pengguna (kutipan di kronologi 2 Oktober 16.07) |
| 17 | Model LLM | "gpt-5.6" (OpenAI). Model bawaan menjadi `gpt-5.6-sol` karena aliasnya ditolak proyek API pengguna |
| 18 | Uji alur penuh dengan API berbayar | Disetujui satu kali |
| 19 | Database aplikasi web | PostgreSQL lokal |
| 20 | Urutan pekerjaan sisa audit | "ikuti rekomendasimu": tiga paket usulan AI, termasuk Adendum A tanpa menyunting isi rencana terkunci, dan rencana field `menggantikan` (belum dikerjakan, Adendum A.7) dengan perilaku standar usulan AI |

Keputusan no. 16–17 menambahkan LLM ke repositori. Itu bertentangan dengan bunyi D6 dan §4.3 rencana yang dikunci; keputusan pengguna yang tercatat pada sesi pertama (no. 7) hanya menolak LLM sebagai baseline. Batasnya dicatat di Adendum A.2. Belum dijawab pengguna per 4 Oktober: zona waktu aplikasi (`APP_TIMEZONE`), dan apakah data di PostgreSQL masih data uji.

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

**Sesi 2–4 Oktober.** Semuanya sudah diperbaiki, kecuali baris terakhir yang hanya dicatat.

| Kesalahan | Asal | Koreksi |
|---|---|---|
| Kunci API pertama ditolak; alias model `gpt-5.6` ditolak untuk proyek API | Konfigurasi | Kunci diganti pengguna; model bawaan menjadi `gpt-5.6-sol` |
| Jawaban LLM yang terpotong memicu galat di pembantu stream SDK | Kode AI (2 Okt) | Peristiwa stream dibaca sendiri; jawaban terpotong menjadi pesan yang jelas |
| Komponen yang dideklarasikan ulang di berkas KB tambahan terhitung dua kali di bruto, PPh 21, dan take home pay | Kode AI (2 Okt) | Deklarasi ganda ditolak saat muat |
| Amandemen parameter yang bersifat sementara (ber-`sampai`) membuat semua perhitungan sesudah `sampai` gagal; nilai `"11.500"` terbaca sebagai pecahan 11,5 (23/2), bukan sebagai rupiah | Kode AI (2 Okt) | Nilai lama berlaku lagi sesudah `sampai`; jenis nilai harus sama dengan versi lama |
| Validasi rancangan bisa melempar galat dan membuang keluaran LLM yang sudah dibayar | Kode AI (2 Okt) | Validasi tidak pernah melempar |
| `retry_after` antrean 90 detik, lebih pendek dari job LLM, sehingga job bisa dijalankan dan dibayar dua kali | Konfigurasi bawaan kerangka yang tidak disesuaikan AI (2 Okt) | 1080 detik |
| Tes PHP dapat mengosongkan database aplikasi bila konfigurasi ter-cache | Konfigurasi bawaan kerangka yang tidak disesuaikan AI (2 Okt); berisiko sejak PostgreSQL dipakai | Lingkungan tes dipaksa ke SQLite in-memory, dan `TestCase` menolak database lain |
| Proses Python mewarisi kunci API dan sandi database dari lingkungan PHP | Kode AI (2 Okt) | Rahasia dihapus dari lingkungan proses anak |
| Hitung semua mengirim seluruh pegawai dalam satu panggilan engine | Kode AI (2 Okt) | Per batch 50 pegawai |
| Workflow audit pertama terhenti karena batas pemakaian | Proses AI | Dipecah menjadi paket kecil |
| Amandemen sementara yang langsung disusul versi baru pada `sampai` + 1 hari ditolak | Kode AI (3 Okt) | Diperbaiki 4 Oktober |
| Batas iterasi titik tetap diambil dari aturan pertama menurut urutan muat, bukan aturan pemenang | Engine sejak 1 Oktober; baru berdampak dengan berkas KB tambahan | Diambil dari pemenang resolusi konflik |
| Perbaikan batas titik tetap menimbulkan dua regresi (galat pada gross-up; pesan menyesatkan) | Kode AI (4 Okt) | Ditemukan agen peninjau dan diperbaiki sebelum commit |
| Simulasi validasi hanya memakai metode gross, sehingga rancangan yang merusak gross-up lolos | Kode AI (2 Okt; `periksa` 3 Okt) | Simulasi dan `periksa` ikut menghitung gross-up |
| Versi pertama field `menggantikan` punya lima cacat (dua di engine, tiga di validasi asisten) | Kode AI (4 Okt) | Ditemukan agen peninjau dan diperbaiki sebelum commit |
| README dan docstring `asisten_kb/__init__.py` mengutip §4.3 sebagai dasar "engine tetap bebas LLM", padahal §4.3 menaruh LLM dalam bentuk apa pun di luar lingkup | Tulisan AI (2 Okt) | Diluruskan 4 Oktober; lihat Adendum A.2 |
| `eksperimen/hasil/mutasi.json` yang tersimpan tertinggal dari skripnya (label satu mutan) | Sejak 1 Oktober | Dibuat ulang 4 Oktober; status mutan dan skor tidak berubah |
| Urutan resolusi konflik, ukuran spesifisitas, dan saat `AMBIGU` muncul di engine berbeda dari §6.3 rencana | Sejak 1 Oktober | Belum diubah; dicatat di Adendum A.5 |

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

**Diperiksa ulang 4 Oktober 2026** (pohon kerja yang menjadi commit `47af9a8`):

| Uji | Hasil |
|---|---|
| Dua belas kali jalan dari sepuluh modul eksperimen (V1 KB dan B1, V2, E12, E8 2023 dan 2024, E3, ablasi, gross-up, konflik, ekspresivitas, mutasi) | Keluaran identik byte demi byte dengan jalankan ulang pada commit `5630897` (keadaan 1 Oktober) dan `f28f7f3`. Keluaran itu tidak disimpan di repositori |
| Berkas hasil yang tersimpan | `mutasi.json` dibuat ulang (label satu mutan tertinggal sejak 1 Oktober); tiga berkas lain sama dengan keluaran jalankan ulang |
| Tes Python | 583 lulus, 8 dilewati (383 pada 1 Oktober; 200 tes baru berasal dari sesi 2–4 Oktober) |
| Tes aplikasi web (PHP, SQLite in-memory) | 99 lulus |
| E9: kinerja | Tidak diulang |
| Sesudah field `menggantikan` (`0d0bb3b`, `b5739a5`, `56bb943`) | Keluaran kedua belas jalan eksperimen tetap identik; tes Python 668 lulus dan 8 dilewati; tes web 101 lulus |

## Belum diverifikasi manusia

Butir-butir ini sengaja tidak diselesaikan oleh AI dan memerlukan tindakan pengguna:

1. **Kalibrasi ke kalkulator DJP (E10).** Kalkulatornya memakai CAPTCHA, jadi harus dikerjakan manual. Sampai dikalibrasi, default tafsir pembulatan masih asumsi, dan sistem menampilkan rentang tafsirnya.
2. **Pembaca kedua untuk daftar asumsi A-01..A-04** di `kb/regulasi/KODIFIKASI.md`. Semua kodifikasi dan adjudikasi dibuat oleh pasangan pengguna–AI yang sama, sehingga oracle-nya belum independen penuh.
3. **KLU 96129.** Kode ini hanya ada di PMK 105/2025 dan baru diekstraksi dari lapisan teks. Perlu dicek ke gambar halaman.
4. **Label uji F1 konflik** dibuat sendiri, bukan oleh pihak independen.
5. **Review kode** oleh pengguna sebelum dipakai di luar konteks tugas.
6. **Mutu ekstraksi asisten KB (LLM) pada dokumen nyata.** Baru ada satu uji asap dengan PDF sintetis satu halaman. Dokumen panjang, hasil pindai, dan regulasi pemerintah yang sebenarnya belum pernah dicoba.
7. **Review kode `web/`, `jembatan/`, dan `asisten_kb/`** oleh pengguna. Kode aplikasinya ditulis AI pada 2–4 Oktober, di atas kerangka Laravel, pustaka pihak ketiga, dan aset tampilan dari proyek templat pengguna.
8. **Perilaku di PostgreSQL yang tidak tercakup tes.** Tes memakai SQLite in-memory dan cache array. Kunci Hitung semua dan perilaku transaksi di PostgreSQL hanya dapat diperiksa lewat uji manual.
9. **Keputusan yang masih terbuka:** zona waktu aplikasi, dan status data di database (uji atau bukan).
10. **Dua akun git.** Sesi 1 Oktober tercatat atas nama `obikast`, sesi 2–4 Oktober atas nama `mahathirmuh`. Jurnal ini tidak mengetahui apakah kedua akun milik orang yang sama. Asisten KB berbasis LLM (keputusan no. 16–17) bertentangan dengan bunyi D6 dan §4.3 rencana yang dikunci pada sesi pertama. Batasnya dicatat di Adendum A, dan perlu diketahui semua pihak yang terlibat dalam tugas ini.
11. **Prompt asisten sesudah 4 Oktober.** Prompt berubah bersama field `menggantikan` dan belum dijalankan terhadap LLM sungguhan; tesnya memakai klien tiruan.

### Lanjutan — Membersihkan kode lama, setup, dan requirements

| Permintaan pengguna | Yang dilakukan AI |
|---|---|
| "bisakah kamu hapus sisa kode dari versi sebelumnya yang tidak dipakai" | Menghapus fungsi dan konstanta UI versi lama yang tidak lagi dirujuk: `ganti_tahun`, `berkas_perusahaan_tersedia`, `PERINGATAN`, `SATUAN`, `BULAN_DARI_NAMA`, beserta import yang tidak terpakai. Pengecekan memakai pyflakes, yang dipasang sementara lalu dicopot, ditambah pemindai rujukan |
| "buat atau perbarui readme tentang cara setup dan menjalankan project ini, update requirements.txt" | `requirements.txt` disusun ulang menjadi dependensi langsung yang dipin. `requirements-lock.txt` berisi versi persis seluruh paket, tanpa playwright yang hanya alat screenshot AI. `requirements-ekstraksi.txt` berisi alat ekstraksi PDF yang opsional. README ditulis ulang: prasyarat, instalasi (Windows/macOS/Linux), cek instalasi, berkas yang sengaja tidak ada di repo, cara menjalankan UI/CLI/API/tes/eksperimen, dan masalah umum |

**Verifikasi:** sebuah venv baru dibuat dari nol dan hanya dipasang dari `requirements.txt`. Seluruh tes lulus di sana (383 lulus, 8 dilewati), jadi berkas itu memang cukup untuk menjalankan project.
