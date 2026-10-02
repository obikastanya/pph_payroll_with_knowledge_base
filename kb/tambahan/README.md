# kb/tambahan — berkas KB yang diterapkan lewat aplikasi web

Folder ini diisi aplikasi web (menu **Basis pengetahuan**): setiap peraturan baru yang rancangannya disetujui admin
ditulis ke sini sebagai satu berkas YAML, lalu ikut dimuat engine (`berkas_tambahan` di protokol `jembatan/`).

- Format berkas sama dengan berkas KB lain (`kb/skema/aturan.schema.json`): `aturan`, `komponen`, `masukan` (isian baru
  yang diminta dari pengguna), `parameter` (amandemen nilai berversi), `pembulatan`, `klasifikasi_wajib`.
- Berkas di sini **tidak** ikut versi git (`.gitignore`): isinya data runtime tiap instalasi. Berkas mana yang aktif
  dicatat di database aplikasi (tabel `kb_usulan`), dan setiap perhitungan menyimpan sidik berkas aktif (`sidik_kb`).
- Tabel terverifikasi (TER, tarif Pasal 17, PTKP, KLU DTP) tidak dapat diubah dari sini; perubahan tabel tetap lewat
  jalur double-entry di `kb/regulasi/` + `tabel_manifest.yaml`.
- Rancangan berkas disusun LLM (`asisten_kb/`), tetapi engine tidak memakai LLM: berkas baru berlaku hanya setelah
  lolos validasi engine (skema, verifikasi statis, simulasi) dan disetujui manusia.
