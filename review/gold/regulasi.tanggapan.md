# Tanggapan atas pembacaan kedua emas regulasi E01–E13

Tinjauan: [regulasi.review.md](regulasi.review.md), pengodean buta [regulasi.koding.csv](regulasi.koding.csv), perbandingan [regulasi.banding.csv](regulasi.banding.csv). Kesepakatan: [docs/hasil/kesepakatan_emas.json](../../docs/hasil/kesepakatan_emas.json). Ditanggapi 2026-10-28 oleh penyusun emas.

## Temuan "peninjau benar" (8) dan "ragu" (2)

| Temuan | Putusan | Perubahan |
|---|---|---|
| E02 `REG.NATURA.GIFT_VALUE`, `SPORTS_VALUE`, `IRREGULAR`: bingkisan dan fasilitas olahraga Januari–Juni tidak ikut menghabiskan batas setahun | **Diterima.** Bertentangan dengan Lampiran A angka 2 dan 5 ("dalam jangka waktu 1 Tahun Pajak") dan tafsir K12 butir 3 | Aturan nilai mulai 2023-01-01 (dikutip Pasal 23 ayat (4) "Januari 2023 sampai dengan Masa Pajak Juni 2023"); aturan objek tetap mulai Juli; `cumulative` kini menjumlah sejak Januari |
| E02 `REG.NATURA.REGULAR`: batas kupon tetap Rp2 jt | **Diterima.** Pasal 5 ayat (4) huruf b: nilai pengeluaran makanan di tempat kerja bila lebih dari Rp2 jt | Batas = max(Rp2 jt, `employer('workplace_meal_value')`); masukan kasus baru, tanpa nilai = Rp2 jt |
| E06/E11 `REG.DTP.FIXED_INCOME`: natura tetap tidak dihitung | **Diterima** (K5; PMK 10 Ps 4 ayat (4), PMK 105 Ps 4 ayat (5)) | + `benefit('housing_individual')` + `benefit('company_vehicle')` (natura bulanan yang tetap). Gaji kontraktual vs dibayar: `base_salary` di model kasus adalah gaji kontraktual; potongan kehadiran adalah `company_deductions`, jadi tidak diubah |
| E06/E11 `REG.DTP.ELIGIBLE` (dan E10 pariwisata): syarat "tidak menerima insentif PPh 21 DTP lainnya" tidak ada | **Diterima** (Pasal 4 ayat (2) huruf c) | `and employee('other_dtp_incentive') != True` dengan kutipan |
| E10 DTP Desember negatif bagi pegawai pariwisata (contoh 7 menulis "-") | **Ragu → diputuskan.** Contoh 3 PMK 10/2025 menyajikan DTP Desember negatif (277.500) untuk lebih potong yang berasal dari DTP; contoh 7 menyajikan "-" dengan total DTP 240.000. Keduanya menggambarkan perlakuan yang sama (lebih potong yang berasal dari DTP tidak dikembalikan, Pasal 5 ayat (5)/(5a)) dengan penyajian berbeda. Emas mengikuti contoh 3 agar satu konvensi berlaku untuk semua penerima DTP | Tidak ada; dicatat sebagai tafsir_korpus B6 |
| E13 `REG.YEAR.PPH.PART_YEAR` tetap dibulatkan ke bawah sejak 2025 | **Diterima.** PER-11 Pasal 129 ayat (1) mencakup PPh di bukti pemotongan, termasuk tahunan | Aturan latar membaca `param('pph_round_mode')` (sebelum 2025 = *truncate*, sama dengan ke bawah untuk nilai positif), sehingga E13 berlaku juga bagi pegawai sebagian tahun |

Semua perubahan diperiksa ulang: GT3 50/50 (2107/2107), GT1 pengembangan 22/26 (14 ralat contoh resmi), GT2 15/20 + 90/90, GT5 67/79 (12 selisih dijelaskan), kebijakan sintetis 37/38; gerbang G1–G5 atas emas dijalankan ulang (`docs/hasil/gerbang_emas.csv`).

## Kekhawatiran prosedur

1. **Penjangkaran pada emas peristiwa sebelumnya.** Basis setiap peristiwa memuat emas peristiwa sebelumnya, sehingga nama dan pola dari E04 dan seterusnya dapat ikut tertiru. Ini sifat rancangan (basis $\mathcal{K}^\star_{n-1}$ memang yang dilihat LLM), tetapi menaikkan kesepakatan representasional. Dilaporkan sebagai batas: α mengukur kesepakatan di bawah basis yang sama.
2. **E13 tidak buta** (pembaca melihat parameter E13 di basis E09 karena urutan terbit). α kehadiran juga dihitung tanpa E13 (`alpha_presence_without_E13`).
3. **Konteks pembaca lebih luas daripada konteks LLM** (pembaca membuat daftar semua rekaman). Dicatat.
4. **Tafsir bersama (K-, B-).** Kesepakatan diukur di bawah putusan tafsir yang sama, bukan pembacaan hukum yang sepenuhnya independen. Dicatat di paper.
5. **Satuan tidak satu-satu.** α kehadiran tidak bermakna di data ini: setiap baris adalah unsur yang dibuat salah satu penyusun, tidak ada baris "keduanya tidak membuat unsur", sehingga terjadi paradoks prevalensi (α ≈ −0,09 dengan kesepakatan 82%). Yang dilaporkan: kesepakatan kehadiran (persen), α `valid_from` pada unsur tambahan (0,79; unsur *change* dikecualikan karena emas mempertahankan `valid_from` asli unsur sedangkan pembaca menulis awal perubahan), α `valid_until` (1,0), dan kesepakatan nilai (90%).
