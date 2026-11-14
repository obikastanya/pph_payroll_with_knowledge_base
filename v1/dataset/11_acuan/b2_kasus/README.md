# b2_kasus — Kasus untuk pembanding B2 (LLM menghitung PPh 21 langsung)

Disusun 2026-10-27 (RENCANA_DATASET.md, D24). Dipakai di E5: LLM diberi dokumen regulasi dan data pegawai, lalu diminta menghitung PPh 21 tanpa *knowledge base*.

- `kasus.jsonl`: 100 profil pegawai-tahun, 25 per tahun pajak 2023–2026, diambil acak (`random.Random(20261027)`) dari strata `S1_acak` di [06_kasus_uji_sintetis](../../06_kasus_uji_sintetis/). Formatnya sama dengan berkas sumbernya.
- Nilai harapan belum ada. Nilai itu dihitung dari KB emas setelah Tahap 7, lalu divalidasi terhadap acuan.
- Jumlah kasus yang benar-benar dijalankan menyesuaikan anggaran API (Log keputusan: USD 15). Bila dipangkas, ambil 10 pertama per tahun sesuai urutan berkas.

Keterbatasan: distribusi strata S1 belum dikalibrasi ke data upah BPS (research_plan.md §8.2), sehingga "operasional" di sini berarti acak dari generator, bukan sampel populasi. Kalibrasi dilakukan bersama generator $S^E$ di Tahap 8.
