# Mockup v3: demo sistem PPh 21 berbasis knowledge base

Implementasi tampilan dari penelitian, disusun menurut `mini_demo/user_design.txt`, untuk memperlihatkan cara kerja
sistem, cara mengelola knowledge base (manual atau dibantu AI), dan cara kalkulator memakainya.

```
env\Scripts\streamlit run mini_demo\mockup\main.py --server.port 8503
```

Lalu buka http://localhost:8503. Tidak butuh kunci API dan tidak memakai kredit.

## Keadaan awal demo dan reset

- **Knowledge base:** knowledge base emas penelitian sampai pembaruan batas upah JP 2025 (dicatat 27 Februari 2025),
  tanpa kebijakan perusahaan.
- **Delapan dokumen menunggu** di Manajemen KB, masing-masing dengan hasil kerja AI asli dari penelitian
  (`experiments/*/results`):
  - PER-11/PJ/2025, PP 36/2025, PMK 72/2025, dan batas upah JP 2026: usulan AI benar;
  - PMK 105/2025: usulan AI **salah**;
  - kebijakan SP14: THR dari masa kerja;
  - PKB WIKA: sistem ragu;
  - PMK 81/2024: tidak relevan.
- **Penyimpanan:** semua yang dilakukan selama demo disimpan di `mini_demo/mockup/workspace/` (tidak di-commit):
  pembaruan yang disetujui, draf, suntingan, unggahan, dan chat.
- **Reset:** tombol **Kembalikan ke keadaan awal demo** (Beranda dan sidebar) menghapus folder itu.

## Yang nyata dan yang simulasi

| Bagian | Status |
|---|---|
| Hitungan kalkulator, contoh sebelum/sesudah, cek KB, dampak ke kebijakan perusahaan | nyata: engine dan KB penelitian |
| Usulan AI dan log pemeriksaannya | nyata: hasil jalan penelitian (claude-opus-5-5) |
| Setujui, tolak, sunting, kembalikan versi, draf dari formulir dan asisten | nyata: pembaruan Δ divalidasi dan diterapkan dengan kode penelitian, di ruang kerja demo |
| "Minta AI perbaiki" dan "Minta AI mengerjakan ulang" | simulasi: hasilnya jawaban acuan penelitian (diberi label) |
| Menjalankan AI pada dokumen unggahan PDF/TXT | belum dijalankan di demo (tombol nonaktif) |
| Jawaban asisten | pencocokan maksud atas KB nyata; pemeriksaan kutipan, draf, dan angka nyata; tanpa API |

## Halaman

**Beranda**
- Ringkasan sistem, alur sistem, serta menu dan fitur utamanya.
- Keadaan KB.
- Langkah demo, dengan tanda selesai otomatis.
- Tombol reset.

**Kalkulator PPh 21**
- Profil pegawai bawaan yang bisa diubah, dan pilihan "hitung sampai bulan".
- Tabel rincian dari bulan pertama sampai bulan itu; semua sel bisa diubah, termasuk kolom "PPh sudah dipotong".
- Hasil sampai bulan itu. Hitung ulang setahun hanya muncul di masa terakhir (Desember atau bulan keluar).
- 14 skenario umum.
- **Kolom dibentuk dari KB:** data yang dibaca aturan yang berlaku tahun itu (`inputs.py`). Setelah SP14 disetujui,
  kolom *Bulan hari raya*, *Masa kerja*, dan *Hari sejak berhenti sebelum hari raya* muncul sendiri.

**Penampil knowledge base**, dengan dua tampilan sejajar di bagian atas halaman:
- **Isi KB:**
  - peta topik, alur perhitungan, angka dari waktu ke waktu, riwayat, bandingkan dua tanggal, cari;
  - **Data yang dibutuhkan:** input yang dibaca aturan, beserta aturan mana yang membacanya;
  - kebijakan perusahaan.
- **Sistem knowledge base (teknis):** sistem KB itu sendiri, langsung dari KB demo (`viewer_tech.py`, `kbviz.py`):
  - **Arsitektur sistem:** dari dokumen sampai hitungan, dengan jumlah unsur dari KB saat ini;
  - **Knowledge graph:** graf di sekitar satu nilai (hulu/hilir, lapis, pasal sumber), dan semua aturan untuk nilai
    itu beserta urutan pilih engine;
  - **Satu unsur sebagai RDF:** triple satu rekaman di named graph pembaruannya (graf, tabel, Turtle);
  - **Dua waktu (bitemporal):** tanggal berlaku vs tanggal dicatat, serta garis waktu per nilai;
  - **Versi dan named graph:** rantai pembaruan, isi tiap pembaruan, dan perbandingan dua versi;
  - **Jejak perhitungan:** jejak engine untuk satu skenario kalkulator, termasuk aturan yang kalah dan alasannya;
  - **Ontologi dan pemeriksaan:** kelas dan hubungan, shapes SHACL (G1), pemeriksa statis (G3), dan validasi SHACL;
  - **SPARQL dan ekspor:** kueri contoh, unduh TriG, ontologi, dan shapes.

**Manajemen knowledge base**
- **Dokumen baru:** pekerjaan AI per langkah (relevansi, versi usulan, pemeriksaan, kesepakatan) dan catatan untuk
  presenter.
- **Review:**
  - kartu perubahan, dengan aturan lama untuk nilai yang sama sebagai pembanding;
  - pemeriksaan;
  - semua skenario sebelum dan sesudah;
  - kebijakan perusahaan yang terdampak;
  - tombol Setujui, Sunting, Minta AI perbaiki, Tolak.
- **Tambah, ubah, cabut:** minta AI dengan kalimat biasa, atau isi formulir.
- **Kebijakan perusahaan:** dari contoh aturan.
- **Cek KB** dan **Riwayat versi** (kembali ke versi sebelumnya).

**Asisten AI**
- Tombol mengambang di semua halaman yang membuka jendela pop-up.
- Chat tersimpan sesudah ditutup dan dimuat ulang, dan bisa dihapus.
- Pilihan model, dengan bawaan gpt-5.4-mini.
- Menjelaskan dan memeriksa usulan, memperbaiki sesuai catatan, membuat draf, dan menjelaskan hasil kalkulator.
- Tidak pernah menyetujui apa pun.

**Hasil penelitian:** empat pertanyaan dalam bahasa biasa.

## Skrip demo (± 10 menit)

1. **Kalkulator:** skenario *DTP padat karya 2026*. Hasilnya belum ada DTP, karena KB demo diketahui sampai
   Februari 2025.
2. **Manajemen KB → Review PMK 105/2025.** Bandingkan kartu *Penghasilan bruto tetap dan teratur* dan *Penghasilan
   tetap bulan pertama* dengan aturan 2025 di bawahnya: AI menghilangkan rumah dan mobil dinas serta penghasilan
   menurut kontrak. Lalu *Minta AI perbaiki*, periksa contoh sebelum/sesudah (2025 sama, 2026 berubah), dan setujui.
3. **Kalkulator:** skenario yang sama. DTP muncul, lengkap dengan pasal PMK 105/2025.
4. **Setujui SP14**, lalu buka skenario *THR menurut kebijakan perusahaan*. Kolom data HR muncul, dan THR dihitung
   dari masa kerja.
5. **Setujui PER-11/PJ/2025**, lalu di kalkulator bandingkan "hitung dengan pengetahuan per tanggal" sebelum dan
   sesudah tanggal dicatatnya.
6. **PKB WIKA:** tanyakan ke asisten kenapa sistem ragu, lalu minta AI mengerjakan ulang.
7. **Asisten:** "Batas upah JP 2027 menjadi Rp11.600.000" → review → setujui.
8. **Kembalikan ke keadaan awal demo.**

## Tampilan yang mengikuti knowledge base

Tidak ada langkah hitung PPh 21 yang ditulis di program tampilan. Kalau KB berubah, bagian-bagian ini ikut berubah:

- **Kartu hasil kalkulator** (`explain.py`): disusun dari rumus aturan yang menang di jejak engine. Rinciannya bisa
  berupa bruto × tarif, penyetahunan, atau cara hitung baru. Kolom tabel hasil dan angka ringkasan adalah nilai yang
  ditandai KB sebagai hasil (`output`).
- **Kamus istilah:** angka dan tanggal diambil dari parameter dan tabel KB yang berlaku pada bulan di kalkulator atau
  tanggal di penampil.
- **Topik di penampil:** nama topik adalah panduan baca. Isinya ditentukan graf: sebuah nilai masuk ke topik tempat
  nilai itu dipakai.
- **Alur perhitungan:** digambar dari aturan yang berlaku pada tanggal yang dipilih.
- **Daftar KLU, judul dokumen, label input tanpa definisi:** dari aturan dan isi KB.
- **Review:** gerbang G1–G5 penelitian (`pipeline.run.check`, termasuk S^G) bisa dijalankan pada KB demo. Hasil
  pemeriksaan saat AI menyusun usulan diberi label sebagai hasil jalan penelitian.

Diuji dengan perubahan dari penelitian sendiri: peraturan fiktif FR01 (cara hitung baru), FR04 (komponen baru), FR05
(angka berubah), serta E10, E11, E12, dan SP14 dari daftar tunggu demo.

Yang masih ditulis tangan:
- **Penjelasan istilah dan nama topik:** kalimatnya ditulis tangan, angkanya dari KB.
- **Tautan nilai ke kamus** (`glossary.FOR_FACT`).
- **Definisi data input** (`kb_ext/`).
- **Nilai yang dijelaskan kalkulator:** `pph21_due`.

## Yang berbeda dari sistem penelitian

- **Bulan penutup dan PPh yang sudah dipotong:** sudah ditangani engine (`engine-v2`). Kalkulator mengirim bulan
  sampai bulan perhitungan saja, dan isian "PPh sudah dipotong" dikirim sebagai nilai tercatat. Bila perusahaan
  menanggung pajaknya (gross-up, ditanggung, atau karena kebijakan perusahaan), tunjangan pajak bulan itu ikut
  dicatat. Verifikasi dan evaluasinya ada di `docs/LOG_PENELITIAN.md`.
- **Definisi data (label dan penjelasan input)** ada di berkas data KB demo (`kb_ext/`), ikut pembaruan yang membawanya.
  Di sistem penuh menjadi unsur KB; Cek KB sudah menampilkan data tanpa definisi.
- **Perbaikan dengan catatan manusia:** belum ada di alur penelitian. Rencananya memakai putaran perbaikan yang sudah
  ada (`repair_user`), dan hasilnya dicatat terpisah dari E2.
