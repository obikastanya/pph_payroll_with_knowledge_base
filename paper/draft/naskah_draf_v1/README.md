# Naskah draf v1 (27 Oktober 2026)

Draf penelitian *Knowledge-Based System Adaptif untuk Perhitungan PPh 21 dengan Akuisisi Pengetahuan Berbantuan LLM dari Regulasi dan Kebijakan Perusahaan*.

Draf ini disusun dari [`../skeleton.tex`](../skeleton.tex) versi `origin/main` (commit `b2aec05`, yang sudah memuat pengujian kebijakan perusahaan) dan [`../../../feedback_and_revision/revision_27_10_26.md`](../../../feedback_and_revision/revision_27_10_26.md). Semua berkas di folder ini baru. Skeleton, draf lama di [`../../latex/`](../../latex/), dan kedua berkas `.bib` lama tidak diubah. Bibliografi lama dipakai lewat path relatif.

## Isi folder

| Berkas | Isi |
|---|---|
| `main.tex` | Berkas induk (IEEEtran *journal*, A4), preambul mengikuti skeleton |
| `sections/00_abstrak.tex` sampai `sections/09_kesimpulan.tex` | Satu berkas per bagian |
| `rujukan_tambahan.bib` | Rujukan baru yang metadatanya sudah diverifikasi (lihat bagian Rujukan) |
| `main.pdf` | Hasil kompilasi |

## Status per bagian

| Bagian | Status | Bab (bila memakai pembagian skripsi) |
|---|---|---|
| Abstrak | Kerangka. Kalimat hasil dan implikasi menunggu E1–E4 | – |
| I Pendahuluan | Lengkap | Bab 1 |
| II Latar belakang dan rumusan masalah | Lengkap | Bab 1 |
| III Penelitian terkait | Lengkap. Karya 2025–2026 baru dibaca dari abstrak | Bab 2 |
| IV Representasi pengetahuan dan *inference engine* | Prosa, dengan keputusan terbuka | Bab 3 |
| V Akuisisi pengetahuan inkremental berbantuan LLM | Prosa, dengan keputusan terbuka | Bab 3 |
| VI Metodologi evaluasi | Prosa, dengan keputusan terbuka | Bab 3 |
| VII Hasil | Kerangka, tabel kosong, gambar pengganti | Bab 4 |
| VIII Pembahasan | Kerangka. Ancaman validitas dan keterbatasan sudah ditulis | Bab 4 |
| IX Kesimpulan | Kerangka | Bab 5 |

Tidak ada angka hasil eksperimen yang dikarang. Semua tempat hasil ditandai sebagai isian.

## Penanda draf

| Penanda | Arti |
|---|---|
| Kotak ungu "Status" | Keadaan sebenarnya: bagian mana yang baru rancangan dan bagian mana yang sudah ada di prototipe |
| Kotak oranye "Keputusan terbuka" | Pilihan yang belum diambil peneliti |
| Kotak hijau "Harus didefinisikan" | Definisi yang masih harus ditetapkan sebelum membangun |
| Kotak abu "Catatan draf" | Catatan penyusunan |
| Teks abu `[...]` | Angka atau teks yang menunggu hasil |
| Teks merah `[rujukan: ...]` | Rujukan yang belum ada di bibliografi |

Semua penanda hilang bila `\rancangantrue` di `main.tex` diganti `\rancanganfalse`.

## Kompilasi

Dari folder ini:

```
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

atau `tectonic -X compile main.tex`. Path bibliografi `../../latex/references` dan `../../latex/regulasi` mengandaikan struktur folder repositori tidak berubah.

## Sumber angka yang dikutip di draf

| Angka di draf | Sumber di repositori |
|---|---|
| 254 sel rumus berisi konstanta regulasi; lembur dicatat tidak teratur | `dataset/02_studi_kasus/README.md` |
| Tujuh pustaka dan aplikasi *open source*, semuanya memuat kesalahan terverifikasi; TER ditambahkan sekitar 30 bulan setelah berlaku | `dataset/03_pembanding/README.md` bagian 6 dan 7 |
| 45 contoh resmi, 1.213 nilai harapan, 1.185 cocok, 20 erratum, 8 tafsir | `README.md` bagian 5 |
| 52 mutan pada *knowledge base* | `README.md` bagian 5 |
| PTKP, biaya jabatan, tarif Pasal 17, lapisan TER 44/40/41, DTP 2025–2026, batas upah JP, PMK 66/2023 | `dataset/01_regulasi/README.md` |
| 33 fungsi bawaan ekspresi, 6 mode pembulatan | `engine/kb.py` (`FUNGSI`), `engine/pembulatan.py` (`MODE`) |
| Klasifikasi lembur dan sumber pasalnya | `kb/regulasi/klasifikasi.yaml`, `kb/perusahaan/perusahaan_x.yaml` |
| Ruang uji 48 dan 366 titik, 2.995 kasus; batas RA 0,69 dan 0,82; batas SER 0,26 dan 59 dokumen | Dihitung ulang dari rumus di skeleton dan catatan revisi |

## Rujukan baru (`rujukan_tambahan.bib`)

Berisi 43 entri ditambah satu entri kontrol IEEEtran (lebih dari enam penulis ditulis "et al."). Metadata setiap entri diverifikasi terhadap Crossref, doi.org, ACL Anthology, arXiv, W3C, OASIS, atau Publications Office EU. Sumbernya dicatat di baris `% verified:` di atas setiap entri. Enam entri diperiksa ulang secara acak: NTOL, Yadamsuren dkk., Law&Order, Gogani-Khiabani dkk. (2025), Prior dkk. (2025), dan Tarski (1955). Naskah lengkap karya-karya ini **belum dibaca**. Isi yang dikutip di draf berasal dari abstrak.

Hasil pengecekan *novelty* (tingkat abstrak):

- Karya terdekat adalah **Gogani-Khiabani dkk. (2025)**, yang mengusulkan LLM untuk mengekstraksi perubahan kode dari publikasi IRS dan menerapkannya pada versi perangkat lunak pajak sebelumnya. Abstraknya berupa kajian tantangan teknis, tanpa evaluasi berantai. Karya ini sekarang dikutip dan dibedakan di Bagian I dan III.
- *Pipeline* teknis terdekat adalah **Law&Order (2026, preprint)**, yaitu sintesis LLM ditambah verifikasi per sel dan perbaikan berulang, dengan hasil 100% pada 51 SPT. Karya ini memformalkan, tetapi tidak memperbarui secara inkremental.
- Tidak ada karya yang diperiksa yang mengevaluasi pembaruan berulang atas basis aturan yang dieksekusi, perambatan kesalahan antarpembaruan, atau lapisan kebijakan pemberi kerja. Klaim inti tetap berdiri, tetapi harus dicek ulang dari naskah lengkap (PANDUAN Tahap 1).
- Bukti pendukung baru untuk RQ3 dan prinsip "nilai dari perilaku, bukan kemiripan": Prior dkk. (NLLP 2025). Kemiripan teks konsolidasi undang-undang dengan LLM mencapai 93–99%, tetapi kecocokan persisnya hanya 50,3% untuk satu langkah dan 20,51% untuk amandemen berantai.

Rujukan yang tidak memenuhi kriteria lama di [`../../reference/README.md`](../../reference/README.md), yaitu terbit 2021 ke atas, ber-*peer review*, dan ber-DOI:

- *Preprint* atau belum ber-*peer review*: Law&Order, Huang dkk. 2026, Gogani-Khiabani dkk. 2025, CodeUpdateArena, Chen dkk. 2021, Cymbler dkk. 2026, dan Rodrigues dkk. 2026 (poster lokakarya).
- Terbit sebelum 2021: Compton dan Jansen 1990, Governatori dan Rotolo 2010, Geifman dan El-Yaniv 2017, Hevner dkk. 2004, Peffers dkk. 2007, Tarski 1955, serta rujukan statistik (Clopper–Pearson, Newcombe, Holm, Cohen, Hayes–Krippendorff).
- Standar dan situs: ELI, OWL-Time, PROV-O, SHACL, LegalRuleML, dan OpenFisca. Menurut PANDUAN Tahap 1, standar dicatat sebagai sumber primer.

Apakah semua ini boleh dikutip adalah keputusan terbuka (skeleton, keputusan no. 2). Dua entri ICAIL 2026 (Graus, Prior dkk. 2026) belum punya DOI ACM; lengkapi saat prosiding terbit.

## Yang belum selesai

1. Pembacaan naskah lengkap karya terdekat, lalu pengecekan ulang Tabel III (PANDUAN Tahap 1).
2. Keputusan tentang kriteria rujukan (lihat bagian sebelumnya).
3. Semua isian hasil di abstrak dan Bagian VII–IX.
4. Keputusan terbuka. Daftarnya ada di halaman terakhir PDF.
5. Pernyataan pengungkapan penggunaan AI, yang perlu disesuaikan dengan kebijakan penerbit tujuan.
