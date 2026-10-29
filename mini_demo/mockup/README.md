# Demo sistem PPh 21 berbasis knowledge base

Peluncur demo untuk aplikasi `system/app` (lihat README di sana untuk halaman, AI, dan biaya). Programnya sama; demo
menambahkan keadaan awal yang tetap dan tombol reset, supaya bisa diulang dari awal.

```
env\Scripts\streamlit run mini_demo\mockup\main.py --server.port 8503
```

Lalu buka http://localhost:8503.

## Keadaan awal demo dan reset

- **Knowledge base:** KB emas penelitian sampai pembaruan batas upah JP 2025 (dicatat 27 Februari 2025), tanpa kebijakan
  perusahaan.
- **Delapan dokumen menunggu** di Manajemen KB, masing-masing dengan hasil kerja AI asli dari penelitian
  (`experiments/*/results`):
  - PER-11/PJ/2025, PP 36/2025, PMK 72/2025, dan batas upah JP 2026: usulan AI benar;
  - PMK 105/2025: usulan AI **salah**;
  - kebijakan SP14: THR dari masa kerja;
  - PKB WIKA: sistem ragu;
  - PMK 81/2024: tidak relevan.
- **Penyimpanan:** semua yang dilakukan selama demo disimpan di `mini_demo/mockup/workspace/` (tidak di-commit).
- **Reset:** tombol **Kembalikan ke keadaan awal demo** (Beranda dan sidebar) menghapus folder itu. Biaya API yang
  sudah terpakai tidak kembali.

## Yang memakai kredit API di demo

| Bagian | Di demo |
|---|---|
| Usulan AI untuk delapan dokumen penelitian | hasil tersimpan, tanpa API |
| Dokumen yang diunggah saat demo | AI sungguhan (Claude), ± USD 0,1–0,9 |
| Minta AI perbaiki | pilihan: AI sungguhan (± USD 0,3) atau jawaban acuan penelitian (gratis, diberi label simulasi) |
| Minta AI mengerjakan ulang (dokumen ragu) | jawaban acuan penelitian (gratis, diberi label simulasi) |
| Asisten | gpt-5.4-mini (± USD 0,002 per pertanyaan), atau "Tanpa AI" |

## Skrip demo (± 10 menit)

1. **Kalkulator:** skenario *DTP padat karya 2026*. Hasilnya belum ada DTP, karena KB demo diketahui sampai
   Februari 2025.
2. **Manajemen KB → Review PMK 105/2025:**
   - bandingkan kartu *Penghasilan bruto tetap dan teratur* dan *Penghasilan tetap bulan pertama* dengan aturan 2025
     di bawahnya: AI menghilangkan rumah dan mobil dinas serta penghasilan menurut kontrak;
   - lalu *Minta AI perbaiki* dengan catatan itu;
   - periksa contoh sebelum/sesudah (2025 sama, 2026 berubah), lalu setujui.

   Uji dengan AI sungguhan (USD 0,29): AI memperbaiki yang diminta, tetapi menambah "natura lain" dan membatasi
   penghasilan kontrak ke pegawai yang mulai setelah Januari. Keduanya lolos G1–G5, jadi ini contoh baik bahwa review
   manusia tetap perlu.
3. **Kalkulator:** skenario yang sama. DTP muncul, lengkap dengan pasal PMK 105/2025.
4. **Setujui SP14**, lalu buka skenario *THR menurut kebijakan perusahaan*. Kolom data HR muncul, dan THR dihitung
   dari masa kerja.
5. **Setujui PER-11/PJ/2025**, lalu di kalkulator bandingkan "hitung dengan pengetahuan per tanggal" sebelum dan
   sesudah tanggal dicatatnya.
6. **PKB WIKA:** tanyakan ke asisten kenapa sistem ragu, lalu minta AI mengerjakan ulang.
7. **Asisten:** "Batas upah JP 2027 menjadi Rp11.600.000" → review → setujui.
8. **Penampil KB → Sistem knowledge base (teknis):** knowledge graph, RDF, versi per named graph, dan jejak perhitungan
   dari pembaruan yang baru disetujui.
9. **Kembalikan ke keadaan awal demo.**
