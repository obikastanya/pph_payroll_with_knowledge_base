# Jurnal penelitian

Catatan kerja penelitian *knowledge-based system* adaptif untuk PPh 21, dari Tahap 3 (spesifikasi) sampai Tahap 20 (analisis). Setiap tahap dicatat dengan tujuan, hasil, angka penting, keputusan, penyimpangan dari rencana, berkas keluaran, dan bagian paper yang memakainya. Setiap tahap diakhiri satu *commit* git yang namanya dicatat di sini, supaya keadaan pada akhir tahap dapat dipulihkan.

Dokumen terkait:
- Rencana tahap dan log keputusan: [PANDUAN_PENELITIAN.md](../PANDUAN_PENELITIAN.md)
- Kerangka paper: [paper/draft/skeleton.tex](../paper/draft/skeleton.tex)
- Spesifikasi: [docs/spesifikasi/](spesifikasi/)
- Dataset dan statusnya: [dataset/RENCANA_DATASET.md](../dataset/RENCANA_DATASET.md)
- Indeks bahan paper (diisi bertahap): bagian **Bahan paper** di bawah dan [docs/BAHAN_PAPER.md](BAHAN_PAPER.md) setelah Tahap 20

## Status

| Tahap | Nama | Status | *Commit* |
|---|---|---|---|
| 0 | Persiapan dan keputusan terbuka | selesai (sebelum jurnal ini) | `e851c8d` dst. |
| 2 | Taksonomi dan aturan tafsir | selesai (sebelum jurnal ini) | `d2ff550`, `f9b4f08` |
| 6 | Korpus dan dataset | selesai (sebelum jurnal ini) | `02c3e01` |
| 3 | Spesifikasi representasi | selesai (v2) | `d00fe74`, lihat Tahap 4 |
| 4 | Spesifikasi akuisisi dan kontrak antarmuka | selesai (v2) | (commit Tahap 4) |
| 5 | Representasi dan *engine* | berjalan | |
| 7 | Emas $\mathcal{K}^\star_n$, $\Delta^\star_n$ | belum | |
| 8 | Ruang uji dan acuan | belum | |
| 9 | Alur akuisisi | belum | |
| 10 | Pembanding, ablasi, skrip analisis | belum | |
| 11 | Kalibrasi pada data pengembangan | belum | |
| 12 | Pra-registrasi | belum | |
| 13–18 | Eksperimen E0–E5 | belum | |
| 19 | Peristiwa prospektif | dipantau (peristiwa pertama Februari 2027) | |
| 20 | Analisis dan penyajian hasil | belum | |

Tahap 1 (kajian pustaka) dan 21–24 (naskah, telaah, rilis, pengiriman) dikerjakan setelah sistem dan hasil selesai, sesuai log keputusan "Urutan kerja".

## Cara kerja yang dipakai di semua tahap

- Claude menyusun setiap materi, lalu *agent* peninjau terpisah memeriksanya terhadap teks sumber. Hasil pemeriksaan disimpan di `review/` dan materi diberi status "siap dipakai" (log keputusan "Pemeriksaan materi `review/`").
- Kode berbahasa Inggris di `system/`; dokumen berbahasa Indonesia, istilah asing dimiringkan.
- Kode lama (`engine/`, `kb/`, `ui/`, `web/`) tidak diubah; dipakai sebagai acuan kesetaraan.
- Panggilan LLM dicatat lengkap (prompt, keluaran, token, biaya) dan dibatasi anggaran USD 15.

---

## Tahap 3. Spesifikasi representasi pengetahuan

Mulai: 2026-10-27.

### Temuan saat menyusun spesifikasi

1. **P07 (PER-11/PJ/2025) ternyata peristiwa relevan.** Tafsir K1 menetapkan pembulatan PPh 21 ke rupiah terdekat mulai Masa Januari 2025 berdasarkan PER-11/PJ/2025 Pasal 129 ayat (1) huruf a dan ayat (3) (PDF hlm. 106), sedangkan tabel peristiwa mencatat dokumen itu sebagai pengecoh X1. Pasal 130 huruf a membatasi PER-2/PJ/2024 pada masa sampai Desember 2024. PMK 81/2024 (P05) hanya mengatur pembulatan keputusan dan dokumen elektronik (Pasal 33 ayat (7), PDF hlm. 34), bukan bukti potong. Koreksi: P07 dipindah menjadi peristiwa uji **E13**, jenis T9 (prosedur hitung), sifat S1 (berlaku 2025-01-01, terbit 2025-05-22). Dengan ini T9 punya contoh nyata.

### Hasil

- [docs/spesifikasi/representasi.md](spesifikasi/representasi.md): Definisi 1–3 (KB enam komponen, aturan bitemporal berversi, hasil perhitungan dan $F_\mathit{nilai}$), ontologi (ELI, OWL-Time, PROV-O, *named graph* per versi), bahasa ekspresi 27 fungsi dengan aritmetika eksak, semantik temporal dua sumbu, resolusi konflik (peringkat → `overrides` → *posterior*), bentuk kanonik, batas ekspresivitas (7 butir), Algoritma 1.
- Koreksi korpus: P07 → E13 (T9). Uji 13, pengecoh 20.

### Bahan paper

- Bagian IV: Definisi 1–3, tabel kelas/properti ontologi, gambar ontologi (versi ASCII di §5, versi gambar di Tahap 5), tabel fungsi bahasa ekspresi, resolusi konflik, batas ekspresivitas, Algoritma 1.
- Ancaman validitas: koreksi korpus P07/E13 menunjukkan klasifikasi relevansi manual bisa keliru; dicatat sebagai bukti pentingnya penilaian relevansi berkutipan.

---

## Tahap 4. Spesifikasi akuisisi dan kontrak antarmuka

Mulai dan selesai: 2026-10-27.

### Hasil

- [docs/spesifikasi/akuisisi.md](spesifikasi/akuisisi.md): Definisi 4–9 (peristiwa, pembaruan dengan penerapan ketat dan longgar, syarat adaptif A1–A4 dengan prosedur uji, adaptivitas representasional dan operasional, mode terisolasi dan berantai dengan $H_n$, terdampak (a)/(b)/(c)), alur delapan tahap, gerbang G1–G5 dengan tanggal mulai efek dan pendaratan nilai/tanggal, generator $S^G$, detektor dampak, B3/B4/AB3/AB4 dari kandidat yang sama, konfigurasi LLM dan anggaran.
- [docs/spesifikasi/format_data.md](spesifikasi/format_data.md) dan `system/schemas/`: skema $\Delta$, skema keluaran LLM datar (`delta_llm.schema.json`, mengikuti batasan keluaran terstruktur), kasus, nilai harapan, log panggilan, hasil alur.

### Tinjauan independen

Agen peninjau terpisah memeriksa ketiga dokumen terhadap kotak "Harus didefinisikan" *skeleton* IV–V, log keputusan, dan tafsir: **41 temuan (6 blokir, 19 penting, 16 kecil)**, semuanya ditanggapi dalam versi 2 ([review/specs/spesifikasi.review.md](../review/specs/spesifikasi.review.md), [tanggapan](../review/specs/spesifikasi.tanggapan.md)). Temuan blokir yang mengubah desain:
1. lapisan perusahaan harus dipasang per kebijakan dan tidak disaring ω;
2. G4/G5 gagal untuk $\Delta$ yang menutup aturan lama → **tanggal mulai efek** $s(u)$ dan pembebasan penutupan;
3. *lex posterior* harus memakai tanggal yang stabil terhadap revisi ($t_c^0$);
4. pemilihan parameter bernama sama;
5. penerapan longgar untuk mode berantai.

Keputusan baru di Log keputusan: nilai yang dinilai untuk peristiwa berlaku surut (nilai seharusnya, penyelesaian tidak dinilai; tafsir B5 untuk E13), lapisan perusahaan, spesifikasi versi 2.

### Bahan paper

- Bagian V: Definisi 4–9, tabel gerbang (G1–G5 dengan syarat yang dijaga), alur delapan tahap, generator $S^G$, definisi terdampak.
- Bagian VI: mode terisolasi/berantai, $H_n$, B3/B4 dari kandidat yang sama, anggaran.
- Diskusi: tinjauan independen spesifikasi menemukan 6 masalah blokir sebelum implementasi; contoh konkret bahwa definisi formal perlu diuji sebelum membangun (saran panduan "titik periksa dosen").
