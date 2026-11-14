# -*- coding: utf-8 -*-
"""Write perubahan.md for U03 and U16 (texts with full TER tables).

DOKUMEN FIKTIF UNTUK PENELITIAN. Tables come from buat_contoh.py so the
text and the worked examples use exactly the same layers.
"""
from pathlib import Path

import buat_contoh  # noqa: F401  (registers U03/D and U16/* tables)
from mesin import TABLES

SEALED = Path(__file__).resolve().parents[1]


def rp(v):
    return f"{v:,}".replace(",", ".")


def pct(bp):
    return f"{bp / 100:g}".replace(".", ",") + "%"


def md_table(rows):
    out = ["| No | Penghasilan bruto bulanan | Tarif efektif |", "|---|---|---|"]
    for i, (lo, hi, bp) in enumerate(rows, 1):
        if lo == 0:
            rng = f"0 s.d. Rp{rp(hi)}"
        elif hi is None:
            rng = f"di atas Rp{rp(lo)}"
        else:
            rng = f"di atas Rp{rp(lo)} s.d. Rp{rp(hi)}"
        out.append(f"| {i} | {rng} | {pct(bp)} |")
    return "\n".join(out)


HDR = "> **DOKUMEN FIKTIF UNTUK PENELITIAN.** Dokumen ini bukan peraturan yang berlaku. Disusun sebagai materi uji perubahan tak terlihat ({id}) penelitian basis pengetahuan PPh Pasal 21 pegawai tetap. Nomor, tanggal, dan nama pejabat adalah rekaan."

MENGINGAT_PP = """Mengingat:
1. Pasal 5 ayat (2) Undang-Undang Dasar Negara Republik Indonesia Tahun 1945;
2. Undang-Undang Nomor 7 Tahun 1983 tentang Pajak Penghasilan sebagaimana telah beberapa kali diubah terakhir dengan Undang-Undang Nomor 6 Tahun 2023;
3. Peraturan Pemerintah Nomor 58 Tahun 2023 tentang Tarif Pemotongan Pajak Penghasilan Pasal 21 atas Penghasilan Sehubungan dengan Pekerjaan, Jasa, atau Kegiatan Wajib Pajak Orang Pribadi;"""

U03 = f"""# U03 — Kategori D tarif efektif bulanan

{HDR.format(id="U03")}

---

**PERATURAN PEMERINTAH REPUBLIK INDONESIA**
**NOMOR 41 TAHUN 2026**
**TENTANG**
**PERUBAHAN ATAS PERATURAN PEMERINTAH NOMOR 58 TAHUN 2023 TENTANG TARIF PEMOTONGAN PAJAK PENGHASILAN PASAL 21 ATAS PENGHASILAN SEHUBUNGAN DENGAN PEKERJAAN, JASA, ATAU KEGIATAN WAJIB PAJAK ORANG PRIBADI**

DENGAN RAHMAT TUHAN YANG MAHA ESA

PRESIDEN REPUBLIK INDONESIA,

Menimbang:
a. bahwa hasil evaluasi penerapan tarif efektif bulanan menunjukkan bahwa bagi penerima penghasilan dengan status tidak kawin tanpa tanggungan, pemotongan dengan tarif efektif bulanan kategori A menimbulkan kurang potong yang signifikan pada Masa Pajak Terakhir;
b. bahwa untuk mendekatkan jumlah pemotongan setiap Masa Pajak dengan Pajak Penghasilan yang terutang setahun, perlu dibentuk kategori tarif efektif bulanan tersendiri bagi penerima penghasilan dengan status tidak kawin tanpa tanggungan;
c. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a dan huruf b, perlu menetapkan Peraturan Pemerintah tentang Perubahan atas Peraturan Pemerintah Nomor 58 Tahun 2023;

{MENGINGAT_PP}

MEMUTUSKAN:

Menetapkan: PERATURAN PEMERINTAH TENTANG PERUBAHAN ATAS PERATURAN PEMERINTAH NOMOR 58 TAHUN 2023 TENTANG TARIF PEMOTONGAN PAJAK PENGHASILAN PASAL 21 ATAS PENGHASILAN SEHUBUNGAN DENGAN PEKERJAAN, JASA, ATAU KEGIATAN WAJIB PAJAK ORANG PRIBADI.

**Pasal I**

Beberapa ketentuan dalam Peraturan Pemerintah Nomor 58 Tahun 2023 diubah sebagai berikut:

1. Ketentuan Pasal 2 ayat (4) dan ayat (5) diubah sehingga berbunyi sebagai berikut:

> (4) Kategori tarif efektif bulanan sebagaimana dimaksud pada ayat (3) terdiri atas:
>   a. kategori A diterapkan atas penghasilan bruto bulanan yang diterima atau diperoleh penerima penghasilan dengan status Penghasilan Tidak Kena Pajak:
>      1. tidak kawin dengan jumlah tanggungan sebanyak 1 (satu) orang; atau
>      2. kawin tanpa tanggungan;
>   b. kategori B diterapkan atas penghasilan bruto bulanan yang diterima atau diperoleh penerima penghasilan dengan status Penghasilan Tidak Kena Pajak tidak kawin dengan jumlah tanggungan sebanyak 2 (dua) atau 3 (tiga) orang, atau kawin dengan jumlah tanggungan sebanyak 1 (satu) atau 2 (dua) orang;
>   c. kategori C diterapkan atas penghasilan bruto bulanan yang diterima atau diperoleh penerima penghasilan dengan status Penghasilan Tidak Kena Pajak kawin dengan jumlah tanggungan sebanyak 3 (tiga) orang; dan
>   d. kategori D diterapkan atas penghasilan bruto bulanan yang diterima atau diperoleh penerima penghasilan dengan status Penghasilan Tidak Kena Pajak tidak kawin tanpa tanggungan, termasuk penerima penghasilan yang besarnya Penghasilan Tidak Kena Pajak hanya sebesar Penghasilan Tidak Kena Pajak untuk dirinya sendiri.
>
> (5) Perincian atas tarif efektif bulanan dari masing-masing kategori sebagaimana dimaksud pada ayat (4) beserta besaran penghasilan bruto bulanan untuk masing-masing tarif dimaksud tercantum dalam Lampiran huruf A, huruf B, huruf C, dan huruf E yang merupakan bagian tidak terpisahkan dari Peraturan Pemerintah ini.

2. Di antara Lampiran huruf D dan penutup Lampiran ditambahkan 1 (satu) lampiran, yakni Lampiran huruf E, sebagaimana tercantum dalam Lampiran yang merupakan bagian tidak terpisahkan dari Peraturan Pemerintah ini.

**Pasal II**

(1) Lampiran huruf A, huruf B, huruf C, dan huruf D Peraturan Pemerintah Nomor 58 Tahun 2023 tidak berubah.

(2) Peraturan Pemerintah ini mulai berlaku pada tanggal 1 Januari 2027 dan diterapkan sejak Masa Pajak Januari 2027.

Ditetapkan di Jakarta
pada tanggal 30 Oktober 2026
PRESIDEN REPUBLIK INDONESIA,
ttd.
[NAMA FIKTIF]

Diundangkan di Jakarta
pada tanggal 2 November 2026

---

**LAMPIRAN HURUF E**
**TARIF EFEKTIF BULANAN KATEGORI D**

{md_table(TABLES["U03/D"])}

Keterangan: "di atas" berarti tidak termasuk batas bawah; "s.d." berarti termasuk batas atas.

---

## Ringkasan perubahan

- Ada kategori TER keempat, kategori D, khusus untuk status TK/0. Karyawati kawin yang PTKP-nya hanya PTKP diri sendiri juga masuk kategori D.
- Kategori A sekarang hanya untuk TK/1 dan K/0. Kategori B dan C tidak berubah.
- Tabel kategori D (Lampiran huruf E) memakai tarif yang sama dengan kategori A, tetapi setiap batas lapisan di bawah Rp100 juta digeser turun Rp400.000 (misalnya lapisan 0% hanya sampai Rp5.000.000). Batas Rp100 juta ke atas sama dengan kategori A.
- Berlaku mulai Masa Pajak Januari 2027. Perhitungan Masa Pajak Terakhir (tarif Pasal 17) tidak berubah, jadi PPh setahun tetap sama. Yang berubah adalah pembagian potongan antarbulan.
"""

U16 = f"""# U16 — Perubahan lapisan bawah tarif efektif bulanan

{HDR.format(id="U16")}

---

**PERATURAN PEMERINTAH REPUBLIK INDONESIA**
**NOMOR 47 TAHUN 2026**
**TENTANG**
**PERUBAHAN ATAS PERATURAN PEMERINTAH NOMOR 58 TAHUN 2023 TENTANG TARIF PEMOTONGAN PAJAK PENGHASILAN PASAL 21 ATAS PENGHASILAN SEHUBUNGAN DENGAN PEKERJAAN, JASA, ATAU KEGIATAN WAJIB PAJAK ORANG PRIBADI**

DENGAN RAHMAT TUHAN YANG MAHA ESA

PRESIDEN REPUBLIK INDONESIA,

Menimbang:
a. bahwa dengan kenaikan upah minimum, pemotongan Pajak Penghasilan Pasal 21 dengan tarif efektif bulanan pada lapisan penghasilan terendah menimbulkan lebih potong pada Masa Pajak Terakhir bagi pegawai berpenghasilan rendah;
b. bahwa untuk mengurangi lebih potong sebagaimana dimaksud dalam huruf a, perlu menyesuaikan lapisan penghasilan bruto bulanan terendah pada tarif efektif bulanan kategori A, kategori B, dan kategori C;
c. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a dan huruf b, perlu menetapkan Peraturan Pemerintah tentang Perubahan atas Peraturan Pemerintah Nomor 58 Tahun 2023;

{MENGINGAT_PP}

MEMUTUSKAN:

Menetapkan: PERATURAN PEMERINTAH TENTANG PERUBAHAN ATAS PERATURAN PEMERINTAH NOMOR 58 TAHUN 2023 TENTANG TARIF PEMOTONGAN PAJAK PENGHASILAN PASAL 21 ATAS PENGHASILAN SEHUBUNGAN DENGAN PEKERJAAN, JASA, ATAU KEGIATAN WAJIB PAJAK ORANG PRIBADI.

**Pasal I**

Ketentuan Lampiran huruf A, huruf B, dan huruf C Peraturan Pemerintah Nomor 58 Tahun 2023 diubah sehingga menjadi sebagaimana tercantum dalam Lampiran yang merupakan bagian tidak terpisahkan dari Peraturan Pemerintah ini.

**Pasal II**

(1) Ketentuan Pasal 2 dan Lampiran huruf D Peraturan Pemerintah Nomor 58 Tahun 2023 tidak berubah.

(2) Peraturan Pemerintah ini mulai berlaku pada tanggal 1 Januari 2027 dan diterapkan sejak Masa Pajak Januari 2027.

Ditetapkan di Jakarta
pada tanggal 16 Desember 2026
PRESIDEN REPUBLIK INDONESIA,
ttd.
[NAMA FIKTIF]

Diundangkan di Jakarta
pada tanggal 17 Desember 2026

---

**LAMPIRAN HURUF A — TARIF EFEKTIF BULANAN KATEGORI A**

{md_table(TABLES["U16/A"])}

**LAMPIRAN HURUF B — TARIF EFEKTIF BULANAN KATEGORI B**

{md_table(TABLES["U16/B"])}

**LAMPIRAN HURUF C — TARIF EFEKTIF BULANAN KATEGORI C**

{md_table(TABLES["U16/C"])}

Keterangan: "di atas" berarti tidak termasuk batas bawah; "s.d." berarti termasuk batas atas.

---

## Ringkasan perubahan

- Lapisan terbawah tabel TER A, B, dan C diubah. Lapisan 0% diperluas: kategori A sampai Rp6.000.000, kategori B sampai Rp6.850.000, kategori C sampai Rp7.350.000. Lapisan 0,25% dan 0,5% dihapus.
- Lapisan berikutnya mulai dari batas baru tersebut dengan tarif 0,75%. Lapisan di atasnya tidak berubah.
- Kategori A/B/C dan pemetaan status PTKP tetap seperti PP 58/2023. TER harian tidak berubah.
- Berlaku mulai Masa Pajak Januari 2027. Perhitungan Masa Pajak Terakhir tidak berubah, jadi PPh setahun tetap. Potongan bulanan pegawai bergaji rendah turun, dan sisanya dihitung di Masa Pajak Terakhir.
"""

(SEALED / "U03" / "perubahan.md").write_text(U03, encoding="utf-8")
(SEALED / "U16" / "perubahan.md").write_text(U16, encoding="utf-8")
print("ok")
