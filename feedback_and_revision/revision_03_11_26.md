# Revisi 3 November 2026

Telaah `paper/draft/paper.tex` terhadap [PANDUAN_PENELITIAN.md](../PANDUAN_PENELITIAN.md) Tahap 21, 22, dan 24 serta Lampiran B, sesudah naskah dipindah ke templat konferensi IEEE. Berkas ini mengikuti format [revision_27_10_26.md](revision_27_10_26.md).

Telaah ini dikerjakan asisten AI atas permintaan peneliti. Telaah oleh dosen pembimbing (Tahap 22) belum dilakukan.

Sesudah telaah ini peneliti menilai 20 halaman terlalu panjang, sehingga ada dua versi:

| Berkas | Isi | Panjang |
|---|---|---|
| `paper/draft/paper.tex` | Naskah kirim, bahasa Indonesia | 8 halaman, 5 tabel, 3 gambar, 32 rujukan |
| `paper/draft/paper_en.tex` | Naskah kirim, bahasa Inggris | 8 halaman, isi sama dengan `paper.tex` |
| `paper/draft/paper_lengkap.tex` | Versi lengkap bahasa Indonesia, dirujuk dari bagian Ketersediaan data | 20 halaman, 14 tabel, 6 gambar, 67 rujukan |

Target 8 halaman ditetapkan asisten, mengikuti panjang draf v1–v8 dan batas yang lazim di konferensi IEEE. Batas konferensi sasaran belum diketahui. Kecuali disebut lain, angka di bawah berlaku untuk naskah 8 halaman.

Kesamaan kedua bahasa diperiksa skrip. Dari 583 angka, selisihnya hanya dua hal yang disengaja: "15" ditulis "Fifteen" di awal kalimat, dan label K1–K4 menjadi (1)–(4). Sitasi, label, urutan rujukan, dan jumlah baris tabel sama. Skrip ini tidak memeriksa makna, jadi terjemahan masih perlu dibaca penulis.

## 1. Format

Kedua naskah memakai templat konferensi IEEE yang diberikan peneliti: `\documentclass[conference]{IEEEtran}`, US Letter, tanpa mengubah margin, kolom, atau huruf.

| Butir templat | Keadaan naskah |
|---|---|
| Blok penulis | `\IEEEauthorblockN` dan `\IEEEauthorblockA`, urutan kiri ke kanan |
| Pendanaan | Tidak ada, sehingga `\thanks` dihapus dan `\IEEEoverridecommandlockouts` dinonaktifkan |
| Abstrak | 233 kata, satu paragraf, tanpa simbol, rumus, atau rujukan |
| Kata kunci | 7, urut abjad |
| *Drop cap* | Dihapus, karena templat konferensi tidak memakainya |
| Singkatan | Didefinisikan pada pemakaian pertama di teks, termasuk PPh, PKB, BPJS, JP, JKK, DJP, RDF, OWL, SHACL, ELI, DMN, SER, CAR, OAR, RA, dan CI |
| Label gambar | 8 pt Times pada semua gambar. Ontologi dibuat ulang di `paper/draft/gambar_ontologi.tex`, karena labelnya semula sekitar 5 pt dan bukan Times. `ontologi.pdf` tidak dipakai lagi |
| Catatan tabel | Huruf, bukan tanda belati |
| Algoritma | Hanya di versi lengkap, dengan paket `algorithmic` sesuai templat dan kata kunci Indonesia |
| Rujukan | Hanya kata pertama dan nama diri berhuruf kapital (28 judul diubah); enam penulis atau lebih memakai *et al.* |
| Teks arahan templat | Tidak ada yang tersisa |
| `hyperref` | Dilepas, karena tidak ada di templat |

Dua penyimpangan disengaja pada versi Indonesia. Keterangan gambar tetap "Gambar", bukan "Fig.", dan singkatan LLM dan PPh 21 tetap ada di judul, karena judul sudah ditetapkan di revisi 27 Oktober. Versi Inggris memakai "Fig.", "Index Terms", dan judul bagian berhuruf kapital seperti contoh templat, serta aturan templat untuk bahasa Inggris, misalnya *data* jamak dan awalan *non* tanpa tanda hubung. Judul Inggris diambil dari revisi 27 Oktober.

## 2. Daftar periksa Lampiran B

| Butir | Status | Bukti |
|---|---|---|
| Judul, abstrak, pendahuluan, kesimpulan memakai angka yang sama | Lulus | Skrip membandingkan semua angka abstrak dengan Hasil dan Kesimpulan. Abstrak semula menulis 0,22–0,69, kini 0,215–0,692 |
| Setiap RQ dijawab dengan putusan eksplisit | Lulus | Tabel putusan di Hasil; putusan ditambahkan di awal setiap paragraf Pembahasan |
| Setiap kontribusi punya bukti | Sebagian | K1–K3 lulus. K4 bertumpu pada repositori publik, belum pada arsip ber-DOI |
| Metrik utama dengan selang kepercayaan | Lulus | Kesalahan terpicu deskriptif sesuai rencana ($R = 1$) |
| Hipotesis yang terbantah dilaporkan | Lulus | Naskah memakai "tidak diterima", bukan "terbantah", karena pada H2a dan H2b data tidak membantah hipotesis, hanya tidak cukup mendukungnya |
| Analisis di luar pra-registrasi berlabel eksploratori | Lulus | Tanda amandemen 1 di tabel dan paragraf |
| Hasil per jenis dan per lapisan | Lulus | Tabel korpus, bagian RQ2, dan Gambar 3 |
| Peristiwa prospektif dilaporkan terpisah | Lulus | Belum ada sampai 3 November 2026, menurut penelusuran berita. JDIH belum diperiksa langsung |
| Peran yang tidak terisi dilaporkan | Lulus | Paragraf Instrumen dan Ancaman validitas |
| Enam jenis ancaman validitas | Lulus | Semua ada |
| Tidak ada "makalah" atau "oracle" | Lulus | Skrip: 0 |
| Istilah asing miring | Lulus | Satu perbaikan: *dataset* |
| Sitasi ada di bibliografi, DOI benar | Lulus | 32 sitasi, bagian dari 67 sitasi yang diperiksa ke Crossref. Tidak ada pemberitahuan retraksi. Dua preprint memakai DOI arXiv |
| Tabel dan gambar dirujuk | Lulus | Semua dirujuk sebelum muncul |
| Melewati *skill* unslop | Lulus | Pass dijalankan, perubahannya terbatas pada kalimat yang melanggar |
| Tautan pra-registrasi dan DOI arsip | **Belum** | Belum ada pendaftaran pihak ketiga maupun DOI. Naskah memakai *commit* publik sebagai gantinya |

## 3. Tanggapan akhir atas feedback dosen

| No. | Feedback | Jawaban sekarang |
|---|---|---|
| 1 | Representasi final | *Knowledge graph* RDF/OWL bitemporal dua lapis, divalidasi SHACL, dengan ekspresi perhitungan dijalankan *engine* (Bagian IV) |
| 2 | Kontribusi | K1–K4 di Pendahuluan. Kebaruannya pembaruan berulang pada basis aturan hukum yang dieksekusi, bukan pola LLM ke aturan |
| 3 | *Ground truth* semua level pajak | Kelima tarif Pasal 17 teruji. TER **belum semua**: 107 dari 122 batas teruji, dan tarif 30–34% tidak muncul di kasus mana pun. Lihat bagian 4 |
| 4 | Matriks evaluasi | RA, SER, CAR, OAR, kesalahan terpicu, *recall*, dan $F_2$. Tabel diagnostik dan tabel analisis statistik ada di versi lengkap |
| 5 | Bukti perubahan regulasi dapat langsung diterapkan | *Regulation replay* 33 peristiwa, kini juga sebagai Gambar 3. Hasilnya tidak kokoh: 31/33 pada rantai transplantasi, 23/33 pada rantai pembangkitan ulang |

## 4. Ralat yang ditemukan saat telaah

1. **Cakupan batas TER.** Naskah menulis setiap batas diuji. Dari `dataset/14_ruang_uji/kasus.jsonl.gz`, yang teruji 107 dari 122 (A 38, B 34, C 35). Lima batas teratas tiap kategori tidak tercapai karena `testspace._bisect` berhenti di gaji Rp400 juta. Bruto bulanan tertinggi di $S^E$ tahun TER sekitar Rp428 juta, sedangkan tarif 30% mulai Rp454 juta. $S^E$ tidak diubah karena sudah dibekukan. Hal ini kini tertulis di Ruang uji, Keterbatasan, dan Penelitian lanjutan.
2. **Batas Pasal 17.** Naskah menulis $b-1$, $b$, $b+1$. Yang dipakai $b-1000$, $b$, $b+1000$, pada lima nilai PKP termasuk Rp50 juta dari tabel lama.
3. **Kronologi kasus uji.** Naskah menulis kasus uji dikunci sebelum peristiwa uji pertama. Kasus utama memang terkunci di `c5983ff` (hash sama), tetapi analisis mutan dan 17 kasus terarah masuk di `d9c2886`, 42 menit sesudah panggilan E2 pertama, padahal prareg §5 memintanya sebelum E2. Keduanya diturunkan dari emas saja dan masuk sebelum penilaian E2 pertama (`a03edfd`). Baris Log keputusan 2026-10-28 keliru soal ini dan sudah diralat dengan baris baru.
4. ***Seed*.** *Seed* 20261027 tidak mengunci urutan kandidat, karena `pipeline/run.py` memakai `hash(event.id)` yang berubah antarproses. Urutan tersimpan di hasil, sehingga penilaian tetap dapat diulang. Hal ini tertulis di bagian Reproduksibilitas versi lengkap, dan naskah 8 halaman tidak lagi menyebut *seed*.
5. **Klaim kebaruan.** "Membangun dari nol" terlalu mutlak, karena Gogani-Khiabani dkk. memperbarui kode pajak satu langkah. Naskah kini menulis "umumnya", dan klaim tiga hal dipersempit ke basis aturan hukum yang dieksekusi.
6. **Karya terdekat.** Penelitian Terkait semula tidak memuat NTOL, formalisasi IRC, dan LLM ke Catala. Kini enam karya terdekat masuk Tabel posisi berdasarkan teks lengkap, dengan dua di antaranya dari versi arXiv.
7. **Gambar dan tabel *skeleton*.** Bidang risiko–cakupan, *regulation replay*, tabel metrik diagnostik, dan tabel analisis statistik belum ada. Keempatnya ada di versi lengkap, dan naskah 8 halaman memuat *regulation replay*. Gambar dibangkitkan `system/tools/paper_figures.py` dari log.
8. **Pengungkapan AI dan ketersediaan data.** Keduanya hilang dari `paper.tex`, dan kini ada di bagian akhir.

Penelusuran pembanding oleh agen terpisah tidak menemukan karya yang membantah klaim kebaruan. Penelusuran itu sebagian besar berdasarkan judul dan abstrak, dan ICAIL 2026 hanya terlihat lewat arXiv.

## 5. Yang masih harus dikerjakan manusia

| Butir | Pemilik | Catatan |
|---|---|---|
| Tentukan konferensi sasaran, lalu batas halaman dan bahasanya | Peneliti | Kedua naskah 8 halaman, dengan ruang tersisa sekitar setengah halaman |
| Baca terjemahan Inggris dan judul peraturan terjemahannya | Kedua penulis | Terjemahan disusun AI, dan judul peraturan di daftar pustaka Inggris bukan terjemahan resmi |
| Dorong *tag* ke remote | Obi | `prareg`, `alur-beku`, `engine-v1`, `emas-v1`, `prareg-amandemen-1`, dan lainnya tidak ada di remote maupun di salinan ini. Naskah menyebut nama *tag*, jadi pembaca belum dapat memeriksanya |
| Daftarkan pra-registrasi ke OSF atau AsPredicted | Peneliti | Sesudah eksperimen, pendaftaran hanya berfungsi sebagai arsip, dan harus diungkapkan begitu |
| Arsipkan ke Zenodo untuk DOI (Tahap 23) | Peneliti | Tambahkan DOI ke bagian Ketersediaan data |
| Baca dan setujui Ucapan terima kasih | Kedua penulis | Pernyataan penggunaan AI dan tanggung jawab isi adalah pernyataan penulis |
| Tambahkan nama dosen atau pendanaan bila ada | Peneliti | Tidak dicantumkan karena tidak diketahui |
| Telaah dosen pembimbing (Tahap 22) | Dosen | Berkas ini bahan awalnya |
| Periksa kompilasi dengan pdfLaTeX | Peneliti | PDF dibuat dengan Tectonic (XeTeX), karena pdfLaTeX tidak tersedia di mesin ini |

Berkas sumber versi Indonesia: `paper/draft/paper.tex`, `gambar_replay.tex`, `gambar_ontologi.tex`, `rujukan_tambahan.bib`, serta `paper/latex/references.bib` dan `regulasi.bib`. Versi Inggris memakai `paper_en.tex`, `gambar_replay_en.tex`, `gambar_ontologi.tex`, `rujukan_tambahan.bib`, `rujukan_en.bib`, dan `references.bib`. Semuanya perlu ikut bila naskah dikirim atau dipindah ke Overleaf. Versi lengkap juga memakai `gambar_rq2.tex`.

## 6. Yang dipangkas dari naskah 8 halaman

Semua yang dipangkas tetap ada di `paper_lengkap.tex`. Bagian Ketersediaan data menyatakan versi lengkap ada di repositori, jadi berkas itu harus di-*commit* dan didorong sebelum naskah dikirim.

| Dipangkas | Yang tersisa di naskah 8 halaman |
|---|---|
| Rumusan subbagian panjang | Paragraf ber-*lead-in* tebal |
| Definisi 1–8 | Empat definisi, termasuk syarat A1–A4 |
| Algoritma inferensi | Satu kalimat tentang cara kerja *engine* |
| Gambar ikhtisar dan alur | Satu gambar gabungan |
| Gambar rantai kepercayaan dan risiko–cakupan | Paragraf Instrumen dan Tabel kondisi E2 |
| Tabel gerbang, pembanding, keterlacakan, diagnostik, statistik, varian E1, E3, dan RQ4 | Dilipat ke teks dan Tabel hipotesis |
| 35 rujukan yang tidak lagi dikutip | 32 rujukan |

Ketiga hal yang kemungkinan ditanyakan dosen dipertahankan sebagai gambar atau tabel: ontologi (feedback no. 1), ruang uji (no. 3), dan *regulation replay* (no. 5). Catatan yang membatasi klaim juga dipertahankan, yaitu *masking*, status amandemen, emas yang hanya ditinjau AI, kronologi kasus terarah, cakupan TER, dan kebocoran desain gerbang.

## Status

Tahap 21 selesai. Tahap 22 selesai untuk telaah mandiri, belum untuk telaah dosen. Tahap 23 belum dimulai. Tahap 24 selesai untuk pernyataan AI dan ketersediaan data tanpa DOI. Cabang IEEE Access tidak dikerjakan, karena format yang dipilih adalah templat konferensi.
