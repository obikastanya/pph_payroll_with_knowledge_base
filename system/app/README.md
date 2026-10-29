# Aplikasi KBS PPh 21

Aplikasi di atas sistem penelitian: *knowledge base* emas (`dataset/12_emas`), *engine* `system/pph21kbs`, alur akuisisi
LLM, dan hasil eksperimen. Pengganti *mockup* `mini_demo/` dengan data dan mesin yang sesungguhnya.

```
env\Scripts\streamlit run system\app\main.py
```

Buka http://localhost:8501. Tidak butuh kunci API, kecuali "Jalankan LLM sekarang" di Manajemen KB (memakai kredit Claude).

| Halaman | Isi |
|---|---|
| Beranda | alur sistem, ringkasan KB |
| Kalkulator PPh 21 | slip gaji dengan diagram derivasi dan jejak sampai pasal; bandingkan versi dan tanggal pengetahuan; satu pegawai 2023–2026 (hari ini vs saat itu); *payroll* massal dengan CSV |
| Penampil KB | graf fakta–aturan, aturan dengan status dan kartu detail, versi tabel dengan grafik tarif, *timeline* bitemporal, pemeriksa statis dan SHACL, konsol SPARQL, ekspor TriG |
| Manajemen KB | kotak masuk (korpus, atau unggah PDF ber-lapisan teks / .txt), alur akuisisi langkah demi langkah (putar ulang jalan tersimpan atau langsung dengan LLM), dampak lintas lapis, *review* dan persetujuan, Δ manual, editor kebijakan perusahaan, riwayat versi dan *diff* |
| Hasil penelitian | putusan hipotesis, E2, E3, E4 |

Pembaruan yang disetujui disimpan sebagai berkas Δ di `system/app/workspace/updates/` (tidak di-*commit*) dan diterapkan di
atas KB emas; KB emas penelitian tidak pernah diubah. "Kosongkan ruang kerja" di Riwayat versi mengembalikan ke KB emas.
`system/app/calculator_app.py` adalah kalkulator versi pertama (satu halaman).
