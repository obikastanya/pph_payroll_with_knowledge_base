"""Prompt untuk LLM: aturan main DSL KB + inventaris KB yang sedang berlaku (dibangkitkan dari KB, bukan ditulis
tangan, agar nama fakta/parameter/pembulatan yang dirujuk LLM memang ada)."""
from datetime import date
from fractions import Fraction

from engine.kb import FAKTA_DASAR_MASA, FAKTA_DASAR_TAHUN
from jembatan.kontrak import KUNCI_INTI_BULAN, KUNCI_INTI_TAHUN

ATURAN_MAIN = """\
Anda menyusun knowledge base (KB) untuk kalkulator payroll dan PPh Pasal 21 pegawai tetap di Indonesia. Dari dokumen
peraturan yang dilampirkan (peraturan pemerintah atau peraturan perusahaan), tuliskan bagian yang memengaruhi
perhitungan payroll/BPJS/PPh 21 sebagai rancangan SATU berkas KB dalam DSL di bawah. Rancangan Anda divalidasi otomatis
oleh engine, disimulasikan pada pegawai contoh, lalu ditinjau manusia sebelum berlaku. Jangan mengarang angka, tarif,
tanggal, atau syarat yang tidak tertulis di dokumen; bila dokumen tidak jelas, tulis tafsir Anda di catatan_peninjau.

## Cara engine menghitung
- Fakta adalah nilai bernama per masa (bulan) atau per tahun. Setiap aturan menghasilkan SATU fakta (`menghasilkan`)
  untuk `lingkup` masa atau tahun, berlaku dalam rentang tanggal `mulai`..`sampai` (kosong = tanpa batas).
- Dua lapisan. `regulasi` = peraturan pemerintah; `perusahaan` = kebijakan pemberi kerja. Bila beberapa aturan
  menghasilkan fakta yang sama: aturan regulasi bersifat `wajib` mengalahkan aturan perusahaan (lex superior); aturan
  perusahaan mengalahkan regulasi `default`/`opsional`; berikutnya lex specialis (lebih banyak konjungsi `and` di
  `jika`), lex posterior (`mulai` lebih baru), lalu `prioritas`. Untuk MENGGANTI aturan lama, tulis aturan baru untuk
  fakta yang sama dengan `mulai` = tanggal berlakunya peraturan (lex posterior); jangan menulis ulang aturan lain.
- Komponen gaji perusahaan dideklarasikan di `komponen` (fakta, jenis, kategori, label) dan dihasilkan oleh aturan
  lingkup masa bertipe rupiah. Kategori menentukan perlakuan pajak: teratur, tidak_teratur, premi_objek (premi asuransi
  dibayar perusahaan, objek pajak), natura, iuran_pengurang (iuran pensiun/JHT/JP pegawai), zakat, bukan_objek,
  tidak_diperhitungkan. Aturan regulasi sudah menjumlahkan SEMUA komponen per kategori (komponen('teratur'), dst.),
  dan take home pay sudah = komponen teratur + tidak_teratur - komponen iuran_pengurang - komponen zakat - PPh 21.
  Jadi komponen baru cukup dideklarasikan; JANGAN menulis ulang rumus bruto, biaya jabatan, PPh 21, BPJS, atau take
  home pay.
- Klasifikasi wajib (lapisan regulasi saja): `klasifikasi_wajib` menetapkan kategori pajak suatu `jenis` komponen yang
  wajib diikuti perusahaan.
- Parameter adalah nilai skalar berversi waktu (tarif BPJS, batas upah, biaya jabatan, ...). Untuk mengubah nilai
  parameter yang sudah ada (lapisan regulasi), tulis entri `parameter` dengan nama yang sama dan `mulai` = tanggal
  berlaku; versi lama otomatis berakhir sehari sebelumnya. jenis_nilai `rupiah` = bilangan bulat (nilai "12000000");
  `pecahan` = teks desimal (persen ditulis sebagai angka persennya, mis. "3.7" untuk 3,7% bila parameter lama juga
  persen; lihat nilai saat ini di inventaris agar satuannya sama). Lapisan perusahaan hanya boleh menambah parameter BARU.

## Input dari pengguna (masukan)
- Data yang harus diisi admin HR dibaca dengan hr('kunci') (sekali per tahun pajak) atau hr_masa('kunci') (per bulan).
  Kunci inti yang SUDAH tersedia di aplikasi tercantum di inventaris. Setiap kunci BARU WAJIB dideklarasikan di
  `masukan`: kunci snake_case, label Indonesia yang jelas bagi admin, tipe, lingkup (tahun untuk hr, bulan untuk
  hr_masa), wajib, bawaan ("" bila tidak ada), pilihan (untuk tipe pilihan), keterangan singkat, sumber (pasal).
- Tipe dan cara membacanya di ekspresi: rupiah/bilangan -> bilangan bulat, langsung dipakai; persen -> teks angka
  persen, baca dengan persen(hr('kunci')); desimal -> teks desimal, baca dengan desimal(hr('kunci'));
  tanggal -> teks ISO, baca dengan tanggal(hr('kunci')); pilihan -> teks, bandingkan hr('kunci') == 'nilai';
  ya_tidak -> True/False.
- Beri `bawaan` bila peraturan menetapkan nilai umum (mis. "0" bila komponen tidak selalu ada), agar data lama tetap
  bisa dihitung.

## DSL ekspresi (`jika`, `maka`)
Subset Python: + - * / (pembagian eksak menghasilkan pecahan), perbandingan, and/or/not, `a if kondisi else b`,
`x in ('A', 'B')`, literal bilangan bulat, teks, True/False/None, dan nama fakta. TIDAK ada float literal (tulis
persen('5') atau desimal('0.05')), subscript, lambda, argumen bernama, atau fungsi di luar daftar ini:
- min(a, b, ...), max(...), abs(x)
- persen('5') -> 5/100; desimal('0.24') -> 24/100 (argumen teks)
- parameter('nama') -> nilai parameter yang berlaku pada masa itu
- bulatkan('ID-PEMBULATAN', x) -> pembulatan sesuai registri
- komponen('kategori') -> jumlah komponen kategori itu pada masa ini
- atau('fakta', bawaan) -> nilai fakta bila ada pada masa itu, selain itu bawaan
- nilai_masa('fakta', bulan), jumlah_masa('fakta') (jumlah setahun), jumlah_masa_selain_terakhir('fakta')
- hr('kunci'), hr_masa('kunci'), hr_masa('kunci', bawaan)
- tanggal('2026-01-01'), tanggal_masa() (tanggal 1 masa ini), tambah_hari(t, n), geser_bulan(t, n), selisih_hari(a, b),
  selisih_bulan(a, b), bulan_dari(t), hari_dari(t), tahun_dari(t)
- kawin(status_ptkp), ptkp(status), tolak('alasan') (menolak kasus di luar cakupan)
Nama `bulan` = nomor bulan masa (1-12) dan `tahun_pajak` tersedia. Fakta lingkup masa boleh membaca fakta lingkup tahun.

## Ketentuan hasil
- Aturan bertipe rupiah HARUS menghasilkan bilangan bulat. Bila ada persen/pembagian, isi `pembulatan` dengan id
  dari registri (inventaris) atau deklarasikan entri baru di `pembulatan` (id HURUF-HURUF, mis. PPT-BULAT;
  status `kebijakan` untuk perusahaan, `wajib` atau `tafsir` untuk regulasi; urutan per_komponen atau sekali).
- id aturan: HURUF/ANGKA dipisah tanda hubung, unik, dengan awalan khas berkas ini (mis. PPT-TRANSPORT-01).
  Fakta baru: snake_case; untuk lapisan perusahaan awali dengan px_ (mis. px_transport).
- sifat: regulasi yang mengikat = wajib; nilai bawaan pemerintah yang boleh diganti perusahaan = default;
  kebijakan perusahaan = opsional.
- Tanggal ISO YYYY-MM-DD. `sumber` wajib mengutip pasal/ayat/bab dokumen.
- `rujukan`: untuk setiap aturan, masukan, dan parameter, satu entri berisi bagian (id/kunci/nama), halaman PDF
  (1 = halaman pertama), dan kutipan pendek kalimat dokumen yang menjadi dasarnya.
- Tabel TER, tarif Pasal 17, PTKP, dan daftar KLU DTP adalah tabel terverifikasi (double-entry) dan TIDAK dapat
  diubah lewat berkas ini. Bila dokumen mengubahnya, jelaskan di `alasan`/`catatan_peninjau`.
- Bila dokumen tidak memuat ketentuan yang memengaruhi perhitungan, atau tidak dapat dinyatakan dengan DSL ini,
  set dapat_dikodifikasi = false, jelaskan di `alasan`, dan biarkan daftar aturan kosong.
- `ringkasan`: 2-4 kalimat isi dokumen yang relevan. `keterangan`: satu kalimat judul berkas.
"""

CONTOH = """\
## Contoh rancangan (peraturan perusahaan: uang transport per hari hadir mulai 1 Juli 2026)
komponen: [{fakta: px_transport, jenis: tunjangan_transport, kategori: teratur, label: Uang transport}]
masukan: [{kunci: uang_transport_per_hari, label: Uang transport per hari hadir, tipe: rupiah, lingkup: tahun,
          wajib: false, bawaan: "0", pilihan: [], keterangan: Nominal per hari kerja yang dihadiri, sumber: PP Ps. 12}]
aturan: [{id: PPT-TRANSPORT-01, sifat: opsional, mulai: 2026-07-01, sampai: "", lingkup: masa,
         menghasilkan: px_transport, jika: "", maka: "hr('uang_transport_per_hari') * hr_masa('hk_aktual')",
         tipe_hasil: rupiah, pembulatan: "", sumber: "Peraturan Perusahaan 2026 Ps. 12 ayat (1)", catatan: ""}]
(Untuk masa sebelum 1 Juli 2026 fakta px_transport tidak dihasilkan, sehingga tidak ikut dijumlah.)
"""


def _potong(teks, n=110):
    teks = " ".join(str(teks).split())
    return teks if len(teks) <= n else teks[: n - 1] + "…"


def _teks_nilai(v):
    """Pecahan -> teks desimal bila berhingga (37/10 -> '3.7'), agar satuan parameter mudah dibaca LLM."""
    if isinstance(v, Fraction) and v.denominator != 1:
        for k in range(1, 13):
            if (v * 10 ** k).denominator == 1:
                return _desimal(v, k)
    return str(v)


def _desimal(v, k):
    n = v * 10 ** k
    s = str(abs(n.numerator)).rjust(k + 1, "0")
    return ("-" if v < 0 else "") + s[:-k] + "." + s[-k:]


def inventaris(kb):
    """Ringkasan KB yang sedang berlaku, dalam teks ringkas untuk prompt (stabil, agar prompt dapat di-cache)."""
    baris = ["## Inventaris KB yang sedang berlaku"]
    baris.append("### Fakta dasar dari data kasus (bukan hasil aturan)")
    baris.append(", ".join(sorted(FAKTA_DASAR_TAHUN | FAKTA_DASAR_MASA)))

    baris.append("### Fakta yang dihasilkan aturan (nama | lingkup | tipe | lapisan | sumber aturan terbaru)")
    per_fakta = {}
    for a in kb.aturan:
        per_fakta.setdefault(a.menghasilkan, []).append(a)
    for fakta in sorted(per_fakta):
        if fakta.startswith("_"):
            continue
        ats = sorted(per_fakta[fakta], key=lambda a: a.mulai)
        a = ats[-1]
        lapisan = "/".join(sorted({x.lapisan for x in ats}))
        baris.append(f"- {fakta} | {a.lingkup} | {a.tipe_hasil} | {lapisan} | {_potong(a.sumber)}")

    baris.append("### Komponen gaji perusahaan (fakta | jenis | kategori)")
    baris += [f"- {k.fakta} | {k.jenis} | {k.kategori}" for k in kb.komponen]
    baris.append("### Klasifikasi wajib regulasi (jenis -> kategori)")
    baris += [f"- {k.jenis} -> {k.kategori} ({_potong(k.sumber, 70)})" for k in kb.klasifikasi]

    baris.append("### Registri pembulatan (id | titik | mode | satuan)")
    baris += [f"- {e.id} | {_potong(e.titik, 70)} | {e.mode} | {e.satuan}" for e in kb.registri]

    baris.append("### Parameter (nama = nilai versi terbaru, berlaku mulai)")
    for nama in sorted(kb.parameter):
        mulai, _sampai, nilai, sumber = sorted(kb.parameter[nama], key=lambda v: v[0])[-1]
        baris.append(f"- {nama} = {_teks_nilai(nilai)} (mulai {mulai}; {_potong(sumber, 60)})")

    baris.append("### Masukan inti yang sudah tersedia di aplikasi")
    baris.append("hr(): " + ", ".join(sorted(KUNCI_INTI_TAHUN)))
    baris.append("hr_masa(): " + ", ".join(sorted(KUNCI_INTI_BULAN)))
    if kb.masukan:
        baris.append("### Masukan tambahan yang sudah dideklarasikan berkas KB lain")
        baris += [f"- {m.kunci} | {m.label} | {m.tipe} | {m.lingkup}" for m in kb.masukan.values()]
    return "\n".join(baris)


def prompt_sistem(kb):
    return "\n\n".join([ATURAN_MAIN, CONTOH, inventaris(kb)])


def instruksi(lapisan, catatan, hari_ini=None):
    hari_ini = hari_ini or date.today()
    teks = (f"Dokumen terlampir adalah peraturan untuk lapisan **{lapisan}**. Susun rancangan berkas KB sesuai aturan "
            "main di atas. Gunakan lapisan tersebut kecuali isi dokumen jelas menunjukkan lapisan lain (jelaskan di "
            f"catatan_peninjau). Tanggal hari ini: {hari_ini.isoformat()}.")
    if catatan:
        teks += f"\n\nCatatan dari admin yang mengunggah:\n{catatan}"
    return teks
