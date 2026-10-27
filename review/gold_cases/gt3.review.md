# Tinjauan GT3 — 50 kasus PPh 21 dihitung manual

Berkas yang diperiksa: [dataset/11_acuan/gt3_kasus_bertingkat/](../../dataset/11_acuan/gt3_kasus_bertingkat/) (`GT3-001.json` … `GT3-050.json`, `README.md`)
Pemeriksa: pakar *payroll* (staf keuangan) · Nama: ………………………… · Tanggal: …………………

## Pengantar

Terima kasih sudah bersedia meninjau. Untuk penelitian ini saya menyusun 50 kasus PPh 21 pegawai tetap tahun pajak 2023–2026. Setiap kasus dihitung dari teks regulasi (PER-16/PJ/2016, PP 58/2023, PMK 168/2023, PMK 66/2023, PMK 10/2025 jo. PMK 72/2025, PMK 105/2025, serta PP BPJS) dan nantinya dipakai sebagai acuan untuk menilai sistem. Karena itu saya perlu tahu apakah hasilnya sama dengan cara Bapak/Ibu menghitung di pekerjaan sehari-hari.

Cara membaca:

- **Bulanan** = satu masa pajak saja (bukan Desember). **Setahun** = semua masa sampai Desember atau sampai bulan pegawai berhenti.
- 2023 memakai metode lama (disetahunkan). 2024–2026 memakai TER; Desember (atau bulan berhenti) dihitung ulang dengan tarif Pasal 17.
- Bruto sudah termasuk premi JKK, JKM, dan BPJS Kesehatan yang dibayar perusahaan. Iuran JHT 2% dan JP 1% pegawai mengurangi neto di perhitungan tahunan. Iuran JHT/JP bagian perusahaan tidak masuk bruto.
- Rincian setiap kasus (komponen gaji, asumsi, dan tiap langkah hitung beserta pasal dan halamannya) ada di `dataset/11_acuan/gt3_kasus_bertingkat/GT3-NNN.json`. Ringkasan cara hitung dan daftar ketidakpastian ada di `README.md` folder yang sama.
- Angka negatif = lebih potong.

Mohon isi kolom terakhir dengan **ya**, atau **tidak** disertai angka atau cara yang menurut Bapak/Ibu benar. Kalau tidak sempat memeriksa semua, prioritaskan kasus yang terkait pertanyaan di bagian berikutnya.

## Tabel kasus

| ID | Ringkas | Hasil utama | Setuju? (ya/tidak + koreksi) |
|---|---|---|---|
| GT3-001 | 2023 Jan TK/0 gaji+tunjangan, BPJS lengkap, metode disetahunkan | Jan: bruto Rp9.408.600; PPh 21 Rp208.408 | |
| GT3-002 | 2023 Mar K/2 lembur, JKK 1,74%, batas upah JP dan JKN | Mar: bruto Rp17.036.000; PPh 21 Rp1.077.300 | |
| GT3-003 | 2023 Apr K/1 THR, metode selisih penghasilan tidak teratur | Apr: bruto Rp24.580.800; PPh 21 Rp2.274.275 (teratur Rp474.275 + tidak teratur Rp1.800.000) | |
| GT3-004 | 2023 Mar K/3 PPh ditanggung pemberi kerja (tanpa gross-up) | Mar: bruto Rp20.588.000; PPh 21 Rp1.538.850 (ditanggung pemberi kerja) | |
| GT3-005 | 2023 Mei TK/1 gross-up tunjangan pajak | Mei: bruto Rp10.709.887; PPh 21 Rp255.887 (= tunjangan pajak) | |
| GT3-006 | 2023 Agt K/0 natura rumah (selisih di atas 2 jt) + kendaraan dikecualikan | Agt: bruto Rp15.052.900; PPh 21 Rp896.837 | |
| GT3-007 | 2023 Sep karyawati kawin (PTKP diri), masuk Juli, faktor 6 | Sep: bruto Rp10.784.000; PPh 21 Rp49.416 | |
| GT3-008 | 2023 setahun TK/0, THR, zakat, PKP tepat 60.000.000 (batas 5%/15%) | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp2.431.369; bruto setahun Rp123.060.000; PKP Rp60.000.000; PPh setahun Rp3.000.000; masa terakhir (Des) Rp568.631 | |
| GT3-009 | 2023 setahun K/1 natura mulai Juli + bingkisan > 3 jt + THR | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp13.197.625; bruto setahun Rp208.702.000; PKP Rp134.964.000; PPh setahun Rp14.244.600; masa terakhir (Des) Rp1.046.975 | |
| GT3-010 | 2023 TK/2 berhenti Agustus, perhitungan akhir di masa terakhir | 8 masa; PPh Jan–Nov/masa sebelum terakhir Rp2.333.396; bruto setahun Rp93.632.000; PKP Rp24.276.000; PPh setahun Rp1.213.800; masa terakhir (Agt) -Rp1.119.596 (lebih potong, dikembalikan ke pegawai) | |
| GT3-011 | 2023 K/0 masuk Mei, faktor 8, bonus Desember | 8 masa; PPh Jan–Nov/masa sebelum terakhir Rp1.934.850; bruto setahun Rp115.463.600; PKP Rp50.118.000; PPh setahun Rp2.505.900; masa terakhir (Des) Rp571.050 | |
| GT3-012 | 2023 setahun K/3 gross-up termasuk Desember | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp16.090.575; bruto setahun Rp240.479.700; PKP Rp157.022.000; PPh setahun Rp17.553.300; masa terakhir (Des) Rp1.462.725; tunjangan pajak Des Rp1.462.725 | |
| GT3-013 | 2024 Jan TK/0 bruto tepat 5.400.000 (batas TER A, b) | Jan: bruto Rp5.400.000; TER A 0%; PPh 21 Rp0 | |
| GT3-014 | 2024 Jan K/0 bruto 5.400.001 (batas TER A, b+1) | Jan: bruto Rp5.400.001; TER A 0,25%; PPh 21 Rp13.500 | |
| GT3-015 | 2024 Feb TK/1 bruto 5.399.999 (batas TER A, b-1) | Feb: bruto Rp5.399.999; TER A 0%; PPh 21 Rp0 | |
| GT3-016 | 2024 Apr K/1 THR digabung dalam bruto TER B | Apr: bruto Rp18.408.600; TER B 7%; PPh 21 Rp1.288.602 | |
| GT3-017 | 2024 Jun K/2 gross-up TER B | Jun: bruto Rp13.067.499; TER B 4%; PPh 21 Rp522.699 (= tunjangan pajak) | |
| GT3-018 | 2024 Jul K/3 PPh ditanggung = kenikmatan, full gross-up TER C | Jul: bruto Rp28.963.483; TER C 11%; PPh 21 Rp3.185.983 (ditanggung pemberi kerja) | |
| GT3-019 | 2024 Agt TK/0 lembur + natura rumah dan kupon makan (selisih lebih) | Agt: bruto Rp11.884.000; TER A 4%; PPh 21 Rp475.360 | |
| GT3-020 | 2024 Okt K/0 gaji tinggi, zakat tidak mengurangi TER, batas upah | Okt: bruto Rp60.804.000; TER A 20%; PPh 21 Rp12.160.800 | |
| GT3-021 | 2024 setahun K/1, THR, zakat, PKP tepat 250.000.000 | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp22.558.600; bruto setahun Rp330.995.422; PKP Rp250.000.000; PPh setahun Rp31.500.000; masa terakhir (Des) Rp8.941.400 | |
| GT3-022 | 2024 setahun TK/0 gross-up + THR | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp17.105.687; bruto setahun Rp218.838.300; PKP Rp154.042.000; PPh setahun Rp17.106.300; masa terakhir (Des) Rp613; tunjangan pajak Des Rp613 | |
| GT3-023 | 2024 TK/0 berhenti Juni, masa terakhir Juni, lebih potong | 6 masa; PPh Jan–Nov/masa sebelum terakhir Rp4.963.440; bruto setahun Rp87.268.800; PKP Rp28.235.000; PPh setahun Rp1.411.750; masa terakhir (Jun) -Rp3.551.690 (lebih potong, dikembalikan ke pegawai) | |
| GT3-024 | 2024 K/2 masuk September, 4 bulan, tanpa disetahunkan | 4 masa; PPh Jan–Nov/masa sebelum terakhir Rp5.052.320; bruto setahun Rp83.872.000; PKP Rp12.370.000; PPh setahun Rp618.500; masa terakhir (Des) -Rp4.433.820 (lebih potong, dikembalikan ke pegawai) | |
| GT3-025 | 2024 setahun K/3 PPh ditanggung (full gross-up) + THR | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp44.554.204; bruto setahun Rp396.041.250; PKP Rp310.845.000; PPh setahun Rp46.711.250; masa terakhir (Des) Rp2.157.046; PPh ditanggung Des Rp2.157.046 | |
| GT3-026 | 2025 Jan K/1 bruto tepat 11.250.000 (batas TER B, b) | Jan: bruto Rp11.250.000; TER B 2%; PPh 21 Rp225.000 | |
| GT3-027 | 2025 Jan TK/2 bruto 11.250.001 (batas TER B, b+1) | Jan: bruto Rp11.250.001; TER B 2,5%; PPh 21 Rp281.250 | |
| GT3-028 | 2025 Feb K/2 bruto 11.249.999 (batas TER B, b-1) | Feb: bruto Rp11.249.999; TER B 2%; PPh 21 Rp224.999 | |
| GT3-029 | 2025 Jan TK/0 tekstil, tetap-teratur tepat 10 jt -> DTP | Jan: bruto Rp12.019.000; TER A 4%; PPh 21 Rp480.760; DTP Rp480.760, dipotong Rp0 | |
| GT3-030 | 2025 Jan TK/0 tekstil, tetap-teratur 10,02 jt -> tidak DTP | Jan: bruto Rp10.540.038; TER A 2,5%; PPh 21 Rp263.500 | |
| GT3-031 | 2025 Mar K/0 alas kaki, THR, JKK keringanan, DTP | Mar: bruto Rp16.379.600; TER A 7%; PPh 21 Rp1.146.572; DTP Rp1.146.572, dipotong Rp0 | |
| GT3-032 | 2025 Mei K/3 industri makanan: JKK keringanan ya, DTP tidak | Mei: bruto Rp13.576.850; TER C 4%; PPh 21 Rp543.074 | |
| GT3-033 | 2025 Okt TK/1 hotel, DTP pariwisata mulai Oktober | Okt: bruto Rp7.738.800; TER A 1,5%; PPh 21 Rp116.082; DTP Rp116.082, dipotong Rp0 | |
| GT3-034 | 2025 setahun TK/0 konveksi, DTP penuh, JKK keringanan Feb-Des | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp1.774.411; bruto setahun Rp94.857.700; PKP Rp33.594.000; PPh setahun Rp1.679.700; masa terakhir (Des) -Rp94.711 (lebih potong, tidak dikembalikan karena DTP); total DTP Rp1.679.700 | |
| GT3-035 | 2025 setahun K/2, PKP 60.000.999 -> 60.000.000 (pembulatan di batas) | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp2.699.892; bruto setahun Rp136.740.999; PKP Rp60.000.000; PPh setahun Rp3.000.000; masa terakhir (Des) Rp300.108 | |
| GT3-036 | 2025 setahun K/0 furnitur, tidak DTP (>10 jt), JKK keringanan | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp5.299.509; bruto setahun Rp142.784.775; PKP Rp74.513.000; PPh setahun Rp5.176.950; masa terakhir (Des) -Rp122.559 (lebih potong, dikembalikan ke pegawai) | |
| GT3-037 | 2025 TK/1 masuk Mei, DTP bulan pertama, JKK keringanan | 8 masa; PPh Jan–Nov/masa sebelum terakhir Rp1.522.613; bruto setahun Rp82.606.200; PKP Rp17.826.000; PPh setahun Rp891.300; masa terakhir (Des) -Rp631.313 (lebih potong, tidak dikembalikan karena DTP); total DTP Rp891.300 | |
| GT3-038 | 2025 setahun K/1 gross-up + THR + zakat | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp7.954.189; bruto setahun Rp170.620.200; PKP Rp93.884.000; PPh setahun Rp8.082.600; masa terakhir (Des) Rp128.411; tunjangan pajak Des Rp128.411 | |
| GT3-039 | 2026 Jan K/3 bruto tepat 6.600.000 (batas TER C, b) | Jan: bruto Rp6.600.000; TER C 0%; PPh 21 Rp0 | |
| GT3-040 | 2026 Jan K/3 bruto 6.600.001 (batas TER C, b+1) | Jan: bruto Rp6.600.001; TER C 0,25%; PPh 21 Rp16.500 | |
| GT3-041 | 2026 Feb K/3 bruto 6.599.999 (batas TER C, b-1) | Feb: bruto Rp6.599.999; TER C 0%; PPh 21 Rp0 | |
| GT3-042 | 2026 Jan TK/0 tekstil, JKK keringanan terakhir, DTP 2026 | Jan: bruto Rp9.427.050; TER A 1,75%; PPh 21 Rp164.973; DTP Rp164.973, dipotong Rp0 | |
| GT3-043 | 2026 Mar K/1 hotel THR, DTP pariwisata 2026 | Mar: bruto Rp17.411.400; TER B 7%; PPh 21 Rp1.218.798; DTP Rp1.218.798, dipotong Rp0 | |
| GT3-044 | 2026 Apr TK/0 gross-up, batas upah JP 2026 | Apr: bruto Rp16.732.257; TER A 7%; PPh 21 Rp1.171.257 (= tunjangan pajak) | |
| GT3-045 | 2026 Jun TK/3 PPh ditanggung (full gross-up) TER B | Jun: bruto Rp17.925.161; TER B 7%; PPh 21 Rp1.254.761 (ditanggung pemberi kerja) | |
| GT3-046 | 2026 setahun K/0, PKP 500.001.000 (batas 25%/30% + 1.000) | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp83.673.680; bruto setahun Rp575.420.578; PKP Rp500.001.000; PPh setahun Rp94.000.300; masa terakhir (Des) Rp10.326.620 | |
| GT3-047 | 2026 setahun TK/0 alas kaki, DTP walau naik gaji >10 jt | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp4.582.808; bruto setahun Rp138.841.425; PKP Rp75.151.000; PPh setahun Rp5.272.650; masa terakhir (Des) Rp689.842; total DTP Rp5.272.650 | |
| GT3-048 | 2026 K/1 konveksi berhenti September, DTP, lebih potong tidak dikembalikan | 9 masa; PPh Jan–Nov/masa sebelum terakhir Rp2.280.865; bruto setahun Rp93.896.100; PKP Rp23.966.000; PPh setahun Rp1.198.300; masa terakhir (Sep) -Rp1.082.565 (lebih potong, tidak dikembalikan karena DTP); total DTP Rp1.198.300 | |
| GT3-049 | 2026 setahun K/2 PPh ditanggung (full gross-up) + THR | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp23.121.165; bruto setahun Rp276.535.800; PKP Rp197.396.000; PPh setahun Rp23.609.400; masa terakhir (Des) Rp488.235; PPh ditanggung Des Rp488.235 | |
| GT3-050 | 2026 setahun TK/0 natura + zakat, PKP 59.999.000 (batas - 1.000) | 12 masa; PPh Jan–Nov/masa sebelum terakhir Rp2.657.984; bruto setahun Rp125.879.000; PKP Rp59.999.000; PPh setahun Rp2.999.950; masa terakhir (Des) Rp341.966 | |

## Pertanyaan

1. **Pembulatan PPh TER bulanan** (GT3-014, 027, 028, 040, 042, dan 14 kasus lain). Peraturan tidak mengatur pembulatan hasil tarif TER × bruto. Saya membulatkan ke bawah ke rupiah penuh, misalnya GT3-028: 2% × Rp11.249.999 = Rp224.999,98 → Rp224.999. Bagaimana aplikasi *payroll* atau e-Bupot/Coretax yang Bapak/Ibu pakai: dibulatkan ke bawah, dibulatkan biasa (Rp225.000), atau tanpa pembulatan?
   Jawaban: …………………………………………

2. **Menghitung tunjangan pajak (*gross-up*)** (GT3-005, 012, 017, 022, 038, 044). Saya mencari tunjangan pajak T yang sama dengan PPh 21 atas (gaji + T). Karena ada pembulatan, kadang ada dua jawaban yang sama-sama benar, misalnya GT3-017: Rp522.699 atau Rp522.700; saya ambil yang terkecil. Di Desember, tunjangan pajak saya samakan dengan kekurangan PPh Desember (GT3-022: Rp613). Bagaimana praktik Bapak/Ibu: rumus langsung (PPh ÷ (1 − tarif)), iterasi, atau tunjangan tetap yang tidak harus sama dengan PPh?
   Jawaban: …………………………………………

3. **PPh ditanggung perusahaan.** Tahun 2023 (GT3-004) saya hitung tanpa *gross-up*, sesuai PER-16 Pasal 8 ayat (2) (PPh yang ditanggung = kenikmatan, bukan objek). Mulai 2024 (GT3-018, 025, 045, 049) saya hitung *full gross-up* sesuai contoh PMK 168/2023 Lampiran B I.4, sehingga angkanya sama dengan metode tunjangan pajak. Apakah ini sesuai praktik? Bagaimana perlakuan semester II 2023, setelah natura/kenikmatan menjadi objek (PMK 66/2023)?
   Jawaban: …………………………………………

4. **Kriteria DTP Rp10 juta** (GT3-029, 030). Saya hanya menghitung gaji + tunjangan tetap. Premi JKK/JKM/BPJS Kesehatan yang dibayar perusahaan, lembur, dan THR tidak saya hitung. Akibatnya GT3-029 (gaji + tunjangan tepat Rp10.000.000, bruto Rp12.019.000) tetap mendapat DTP. Apakah perusahaan Bapak/Ibu atau konsultan pajak memakai tafsiran yang sama, atau premi BPJS ikut dihitung?
   Jawaban: …………………………………………

5. **Biaya jabatan untuk pegawai yang bekerja kurang dari setahun** (GT3-037, 048). Saya memakai min(5% × bruto setahun, jumlah bulan × Rp500.000), seperti contoh PMK 168 dan PMK 105/2025. Contoh 3 PMK 10/2025 justru membatasi Rp500.000 per bulan, masing-masing bulan. Untuk GT3-048, cara pertama menghasilkan biaya jabatan Rp4.500.000 dan cara kedua Rp4.273.025. Cara mana yang dipakai di aplikasi Bapak/Ibu?
   Jawaban: …………………………………………

6. **Keringanan iuran JKK 50% untuk industri padat karya** (GT3-034, 036, 037, 042, 047, 048). Saya memakai tarif keringanan untuk iuran Februari 2025 s.d. Januari 2026 (PP 7/2025 jo. PP 36/2025), dan premi JKK yang lebih kecil itu ikut mengurangi bruto PPh 21. Di GT3-036 tarif TER bahkan turun dari 3,5% (Januari) menjadi 3% (Februari) karena hal ini. Apakah di praktik bruto PPh 21 benar-benar memakai premi yang sudah dikurangi? Apakah iuran Agustus 2025 dibayar dengan tarif keringanan, mengingat PP 36/2025 baru terbit 4 September 2025?
   Jawaban: …………………………………………

7. **Premi JKK yang direkomposisi untuk JKP.** Sebagian iuran JKK (0,14%, atau 0,12% untuk risiko sangat rendah) dialihkan BPJS ke program JKP. Saya tetap memasukkan seluruh tarif JKK nominal ke bruto (semua kasus). Apakah aplikasi Bapak/Ibu juga begitu, atau porsi JKP dikeluarkan?
   Jawaban: …………………………………………

8. **Tahun 2023: zakat dan iuran JP.** Untuk 2023 (metode PER-16) saya tidak mengurangkan zakat yang dibayar lewat perusahaan (GT3-008), karena PER-16 Pasal 10 ayat (3) tidak memuatnya. Iuran JP 1% pegawai tetap saya kurangkan. Apakah itu sesuai praktik 2023 di tempat Bapak/Ibu?
   Jawaban: …………………………………………

## Catatan lain dari peninjau

…………………………………………………………………………………………

## Keputusan

- [ ] Disetujui
- [ ] Disetujui dengan perubahan (sebutkan ID dan koreksinya di tabel atau catatan)
- [ ] Perlu revisi

Status: menunggu
