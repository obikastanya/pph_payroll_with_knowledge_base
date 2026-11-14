# Entri jurnal penggunaan AI, 27 Oktober 2026 (siap tempel ke journal.md)

Berkas ini sengaja dibuat terpisah karena permintaan pengguna adalah tidak mengubah berkas yang sudah ada. Salin isinya ke [`journal.md`](../../../journal.md) bila disetujui.

---

### 27 Oktober 2026 — Draf paper v1 dan slide progres mingguan

| Butir | Keterangan |
|---|---|
| Asisten AI | Claude Code (ekstensi VS Code), model Claude Opus 5.5 (`claude-opus-5-5`), ditambah satu sub-agen dari model yang sama untuk memverifikasi metadata rujukan |
| Permintaan pengguna | "paper draft latex + pdf (bab 1, 2, 3) + draft (abstract, bab 4, dst)"; "ppt progress mingguan (perubahan konsep berdasarkan feedback and revision + progress paper draft)"; "jangan nimpa file ya, buatkan versi draftnya kita saja" |
| Hasil | `paper/draft/naskah_draf_v1/` (LaTeX, PDF 21 halaman, README, `.bib` tambahan berisi 43 rujukan terverifikasi); `progress_mingguan/progress_mingguan_draf_v1.pptx` dan `.pdf` (13 slide) |
| Berkas lama yang diubah | Tidak ada. Semua hasil berupa berkas baru. `journal.md`, `skeleton.tex`, `paper/latex/`, dan kedua `.bib` lama tidak disentuh |

| Yang dilakukan AI | Catatan |
|---|---|
| Membaca `skeleton.tex`, `PANDUAN_PENELITIAN.md`, dan catatan revisi versi `origin/main` (`b2aec05`) lewat `git show` ke folder sementara | Cabang lokal tertinggal 2 *commit* dari `origin/main`; tidak dilakukan `git pull` |
| Menulis Bagian I–III lengkap, Bagian IV–VI sebagai prosa dengan keputusan terbuka ditandai, dan abstrak serta Bagian VII–IX sebagai kerangka | Tidak ada angka hasil eksperimen yang dikarang; semua tempat hasil ditandai isian |
| Mencocokkan setiap angka yang dikutip dengan sumbernya di repositori | Daftar sumber ada di `README.md` folder draf |
| Menggambar empat diagram TikZ (ikhtisar sistem, ontologi, alur akuisisi, rantai kepercayaan) dan satu contoh Turtle/SHACL/SPARQL | Nama kelas dan properti di contoh RDF masih usulan |
| Membangun 13 slide dengan `python-pptx`, mengekspornya ke PDF lewat PowerPoint, dan memeriksa tampilannya slide demi slide | Gaya mengikuti slide progres sebelumnya |
| Mengompilasi LaTeX dengan Tectonic 0.17.0 yang sudah ada di komputer dari sesi lain | Unduhan Tectonic baru ditolak pengaman mode otomatis |
| Sub-agen memverifikasi metadata rujukan baru lewat Crossref, doi.org, ACL Anthology, arXiv, W3C, dan OASIS (126 panggilan alat, ±48 menit) | 43 entri; enam di antaranya diperiksa ulang oleh sesi utama. Satu entri dibuang karena duplikat dengan `khiabani2026agentic` di `references.bib` |
| Sub-agen menemukan karya yang tidak ada di daftar awal tetapi relevan dengan *novelty*: Gogani-Khiabani dkk. (2025), Prior dkk. (2025), KoLEG, Jurayj dkk. (2026), ReCode, dan Rodrigues dkk. (2026) | Gogani-Khiabani dkk. adalah gagasan terdekat dan kini dikutip serta dibedakan di Bagian I dan III |

**Usulan AI di draf yang perlu ditinjau peneliti**

1. Sifat aturan *tafsir* sebagai sifat keempat di Definisi 2 (skeleton hanya menyebut wajib, *default*, opsional).
2. Kunci leksikografis $\kappa$ untuk resolusi konflik, mengikuti urutan di prototipe.
3. SHACL dengan dua tingkat: `sh:Violation` menolak pembaruan, `sh:Warning` mencatat konflik kebijakan dengan aturan wajib.
4. Jenis perubahan tambahan "kondisi atau cakupan" (contoh PMK 72/2025).
5. Kandidat korpus tambahan K1: PP 7/2025 dan PP 36/2025 (keringanan iuran JKK).
6. Aturan bila dua kelompok konsensus sama besar: *abstain*.
7. Pertanyaan lingkup *gross-up* pada rezim disetahunkan (ditandai keputusan terbuka).

**Belum diverifikasi manusia**

1. Seluruh isi draf, terutama klaim domain di Bagian II dan definisi di Bagian IV–V.
2. Karya 2025–2026 di Bagian III baru diperiksa dari metadata dan abstrak, belum dari naskah lengkap. Klaim *novelty* perlu dicek ulang terhadap naskah lengkap Gogani-Khiabani dkk. (2025), Law&Order (2026), dan NTOL (2026).
3. Pernyataan pengungkapan penggunaan AI di akhir naskah, yang harus disesuaikan dengan kebijakan penerbit tujuan.
