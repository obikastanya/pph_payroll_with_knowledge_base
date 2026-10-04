"""Pemuat & verifikator statis knowledge base aturan (research_plan.md §6.2, §6.6).

Satu KB = kumpulan berkas aturan YAML (lapisan regulasi + opsional lapisan perusahaan),
registri pembulatan, parameter berversi, dan tabel bertingkat (lewat manifest berhash).
"""
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path

from .angka import PelanggaranPresisi, rupiah, tarif
from .ekspresi import Ekspresi, jumlah_konjungsi
from .muat import ROOT, KesalahanKB, muat_registri_pembulatan, muat_tabel, muat_yaml, validasi_skema

DIR_REGULASI = ROOT / "kb" / "regulasi"
BERKAS_ATURAN_REGULASI = ["aturan_umum.yaml", "aturan_ter.yaml", "aturan_per16.yaml", "aturan_dtp.yaml", "klasifikasi.yaml",
                          "pencatatan.yaml"]


@dataclass(frozen=True)
class MetaFungsi:
    argumen_fakta: bool = False   # argumen pertama (string) adalah nama fakta -> dependensi
    arg_min: int = 0              # jumlah argumen diperiksa saat parse, bukan baru gagal saat menghitung
    arg_maks: object = None       # None = tidak dibatasi


def _ar(n_min, n_maks="sama", fakta=False):
    return MetaFungsi(argumen_fakta=fakta, arg_min=n_min, arg_maks=n_min if n_maks == "sama" else n_maks)


# Fungsi yang boleh dipakai di DSL beserta jumlah argumennya. Implementasinya ada di engine/inferensi.py.
FUNGSI = {
    "min": _ar(1, None), "max": _ar(1, None), "abs": _ar(1),
    "persen": _ar(1), "parameter": _ar(1), "bulatkan": _ar(2),
    "ptkp": _ar(1), "kategori_ter": _ar(1), "kawin": _ar(1),
    "tarif_ter": _ar(2), "pasal17": _ar(1),
    # komponen(kategori[, satuan_periode]); komponen_kode(kategori, potongan_kode); komponen_valas(kategori)
    "komponen": _ar(1, 2), "komponen_kode": _ar(2), "komponen_valas": _ar(1),
    "dtp_sektor_tahun": _ar(2), "dtp_masa_fasilitas": _ar(3),
    "atau": _ar(2, fakta=True), "nilai_masa": _ar(2, fakta=True),
    "jumlah_masa": _ar(1, fakta=True),
    "jumlah_masa_selain_terakhir": _ar(1, fakta=True),
    "tolak": _ar(1),
    # data HR mentah (lapisan perusahaan) & tanggal
    "hr": _ar(1), "hr_masa": _ar(1, 2), "desimal": _ar(1),
    "tanggal": _ar(1), "tanggal_masa": _ar(0), "tambah_hari": _ar(2), "geser_bulan": _ar(2),
    "selisih_hari": _ar(2), "selisih_bulan": _ar(2), "bulan_dari": _ar(1), "hari_dari": _ar(1),
    "tahun_dari": _ar(1),
}
FUNGSI_KOMPONEN = {"komponen", "komponen_kode", "komponen_valas"}

# Kategori pajak komponen (sama dengan enum `kategori` di kb/skema/aturan.schema.json). 'rapel' hanya ada pada
# komponen input kasus, tetapi sah sebagai argumen pertama komponen().
KATEGORI_KOMPONEN = ("teratur", "tidak_teratur", "premi_objek", "natura", "iuran_pengurang", "zakat", "bukan_objek",
                     "tidak_diperhitungkan")
KATEGORI_INPUT = ("rapel",)

# Fakta dasar yang disediakan engine dari input kasus (bukan hasil aturan).
FAKTA_DASAR_TAHUN = {
    "tahun_pajak", "metode", "cakupan", "status_ptkp_input", "jenis_kelamin", "suami_tidak_berpenghasilan",
    "punya_npwp", "subjektif_mulai", "subjektif_akhir", "bulan_masuk", "bulan_kerja_diketahui",
    "periode_gaji", "hari_kerja_sebulan", "klu", "jenis_pemberi_kerja", "penghasilan_tetap_kontrak",
    "rapel_n_bulan", "rapel_dipotong_per_bulan", "n_bulan_kerja", "bulan_pertama", "bulan_terakhir",
}
FAKTA_DASAR_MASA = {"bulan", "masa_terakhir"}


def _tanggal(teks):
    if teks is None:
        return None
    return date.fromisoformat(str(teks))


@dataclass
class Aturan:
    id: str
    lapisan: str
    sifat: str
    mulai: date
    sampai: object
    lingkup: str
    menghasilkan: str
    maka: Ekspresi
    jika: object
    tipe_hasil: str
    sumber: str
    tafsir: object = None
    varian: object = None
    varian_default: bool = False
    pembulatan: object = None
    titik_tetap: bool = False
    batas_bawah: object = None
    batas_atas: object = None
    prioritas: int = 0
    sumbu_waktu: str = "masa_pajak"
    berkas: str = ""
    dicatat: object = None   # knowledge time (None = sejak awal KB)
    menggantikan: tuple = ()   # id aturan yang dicabut selama aturan ini berlaku menurut tanggal (pencabutan eksplisit)

    @property
    def spesifisitas(self):
        return jumlah_konjungsi(self.jika)

    def berlaku_pada(self, tgl):
        return self.mulai <= tgl and (self.sampai is None or tgl <= self.sampai)

    def berlaku_di_tahun(self, tahun):
        return self.mulai <= date(tahun, 12, 31) and (self.sampai is None or self.sampai >= date(tahun, 1, 1))

    def dependensi(self):
        d = self.maka.dependensi()
        if self.jika is not None:
            d |= self.jika.dependensi()
        for b in (self.batas_bawah, self.batas_atas):
            if b is not None:
                d |= b.dependensi()
        return d


def _bangun_aturan(d, lapisan, berkas):
    try:
        return Aturan(
            id=d["id"], lapisan=lapisan, sifat=d["sifat"], mulai=_tanggal(d["berlaku"]["mulai"]),
            sampai=_tanggal(d["berlaku"].get("sampai")), lingkup=d["lingkup"], menghasilkan=d["menghasilkan"],
            maka=Ekspresi(d["maka"], FUNGSI), jika=Ekspresi(d["jika"], FUNGSI) if d.get("jika") else None,
            tipe_hasil=d["tipe_hasil"], sumber=d["sumber"], tafsir=d.get("tafsir"), varian=d.get("varian"),
            varian_default=d.get("varian_default", False), pembulatan=d.get("pembulatan"),
            titik_tetap=d.get("titik_tetap", False), prioritas=d.get("prioritas", 0),
            batas_bawah=Ekspresi(d["batas_titik_tetap"]["bawah"], FUNGSI) if d.get("batas_titik_tetap") else None,
            batas_atas=Ekspresi(d["batas_titik_tetap"]["atas"], FUNGSI) if d.get("batas_titik_tetap") else None,
            sumbu_waktu=d.get("sumbu_waktu", "masa_pajak"), berkas=berkas, dicatat=_tanggal(d.get("dicatat")),
            menggantikan=tuple(d.get("menggantikan") or ()))
    except (KesalahanKB, PelanggaranPresisi, ValueError) as e:
        raise KesalahanKB(f"{berkas}: aturan {d.get('id')}: {e}") from None


@dataclass(frozen=True)
class KomponenPerusahaan:
    fakta: str
    jenis: str
    kategori: str
    berkas: str
    label: object = None


TIPE_MASUKAN = ("rupiah", "bilangan", "persen", "desimal", "tanggal", "pilihan", "ya_tidak")


@dataclass(frozen=True)
class Masukan:
    """Data input yang diminta aturan dari pengguna (dibaca lewat hr('kunci') / hr_masa('kunci')).

    Nilai di data_hr: rupiah/bilangan = int; persen = teks desimal angka persen ("10" = 10%, baca dengan
    persen(hr(...))); desimal = teks desimal ("0.24", baca dengan desimal(hr(...))); tanggal = teks ISO
    (baca dengan tanggal(hr(...))); pilihan = salah satu teks di `pilihan`; ya_tidak = bool.
    """
    kunci: str
    label: str
    tipe: str
    lingkup: str          # tahun -> hr('kunci'); bulan -> hr_masa('kunci')
    wajib: bool
    bawaan: object
    pilihan: tuple
    keterangan: str
    sumber: str
    berkas: str


def nilai_masukan(m, v, tempat):
    """Validasi & normalisasi satu nilai masukan sesuai tipenya (tanpa float). None tetap None."""
    if v is None:
        return None
    try:
        if m.tipe in ("rupiah", "bilangan"):
            if isinstance(v, bool) or not isinstance(v, int):
                raise ValueError("harus bilangan bulat")
            if m.tipe == "rupiah" and v < 0:
                raise ValueError("tidak boleh negatif")
            return rupiah(v) if m.tipe == "rupiah" else v
        if m.tipe in ("persen", "desimal"):
            if not isinstance(v, str):
                raise ValueError("harus teks desimal, mis. '10' atau '0.24'")
            tarif(v)
            return v
        if m.tipe == "tanggal":
            return date.fromisoformat(str(v)).isoformat()
        if m.tipe == "pilihan":
            if v not in m.pilihan:
                raise ValueError(f"harus salah satu dari {list(m.pilihan)}")
            return v
        if m.tipe == "ya_tidak":
            if not isinstance(v, bool):
                raise ValueError("harus true/false")
            return v
    except (ValueError, PelanggaranPresisi) as e:
        raise KesalahanKB(f"{tempat}: masukan '{m.kunci}' ({m.tipe}) tidak valid: {v!r} ({e})") from None
    raise KesalahanKB(f"{tempat}: tipe masukan tidak dikenal {m.tipe!r}")


def _bangun_masukan(d, berkas):
    m = Masukan(kunci=d["kunci"], label=d["label"], tipe=d["tipe"], lingkup=d["lingkup"], wajib=d.get("wajib", True),
                bawaan=None, pilihan=tuple(d.get("pilihan") or ()), keterangan=d.get("keterangan", ""),
                sumber=d.get("sumber", ""), berkas=berkas)
    if m.tipe == "pilihan" and not m.pilihan:
        raise KesalahanKB(f"{berkas}: masukan {m.kunci} bertipe pilihan wajib punya daftar 'pilihan'")
    bawaan = nilai_masukan(m, d.get("bawaan"), berkas)
    return Masukan(**{**m.__dict__, "bawaan": bawaan})


# Atribut yang menentukan arti nilai masukan; deklarasi ulang hanya sah bila semuanya sama (label, keterangan, sumber
# boleh berbeda karena hanya teks tampilan).
KONTRAK_MASUKAN = ("tipe", "lingkup", "wajib", "bawaan", "pilihan")


def _tambah_masukan(masukan, m):
    ada = masukan.get(m.kunci)
    if ada is None:
        masukan[m.kunci] = m
        return
    beda = [f"{a} ({getattr(ada, a)!r} vs {getattr(m, a)!r})" for a in KONTRAK_MASUKAN
            if getattr(ada, a) != getattr(m, a) or type(getattr(ada, a)) is not type(getattr(m, a))]
    if beda:
        raise KesalahanKB(f"{m.berkas}: masukan {m.kunci} sudah dideklarasikan di {ada.berkas} dengan atribut berbeda: "
                          f"{'; '.join(beda)}; deklarasi ulang hanya boleh bila tipe, lingkup, wajib, bawaan dan pilihan sama")
    # deklarasi identik: deklarasi pertama dipertahankan


@dataclass(frozen=True)
class KlasifikasiWajib:
    jenis: str
    kategori: str
    mulai: date
    sampai: object
    sumber: str


@dataclass
class KnowledgeBase:
    aturan: list
    registri: object
    parameter: dict
    tabel: dict
    berkas: list = field(default_factory=list)
    komponen: list = field(default_factory=list)
    klasifikasi: list = field(default_factory=list)
    pencatatan: dict = field(default_factory=dict)
    masukan: dict = field(default_factory=dict)

    def aturan_untuk(self, fakta):
        return [a for a in self.aturan if a.menghasilkan == fakta]


def _nilai_parameter(nilai):
    return tarif(nilai) if isinstance(nilai, str) else rupiah(nilai)


def _muat_parameter(path):
    data = muat_yaml(path)
    hasil = {}
    for p in data["parameter"]:
        hasil.setdefault(p["nama"], []).append((_tanggal(p["berlaku"]["mulai"]), _tanggal(p["berlaku"].get("sampai")),
                                                 _nilai_parameter(p["nilai"]), p["sumber"]))
    return hasil


def _sisipkan_versi(lama, mulai, sampai, apa, berkas):
    """Semantik amandemen berversi waktu (parameter & klasifikasi wajib). lama: [(mulai, sampai, isi, asal, lanjutan)]
    dengan asal = berkas yang menulis versi itu dan lanjutan = () untuk versi yang ditulis berkas. Potongan yang
    "berlaku lagi" (buatan pemuat, bukan tulisan berkas) mencatat di lanjutan amandemen sementara yang membuatnya:
    ((tanggal akhir, berkas), ...).

    Versi baru [M, S] menutup versi lama yang masih berlaku pada M (sampai = M - 1 hari); versi lama yang mulai di
    dalam [M, S] berarti bentrok. Amandemen sementara (S terisi) tidak memotong versi lama selamanya: bila versi lama
    semula berlaku melewati S, ia berlaku lagi mulai S + 1 hari sampai tanggal akhirnya semula.
    Potongan "berlaku lagi" yang mulai tepat pada M digantikan versi baru (sisanya, bila melewati S, berlaku lagi mulai
    S + 1 hari): tanpa ini amandemen sementara yang langsung disusul versi baru tertolak. Potongan yang mulai sesudah M
    di dalam [M, S] tetap bentrok. Akibatnya versi permanen yang mulai di tengah amandemen sementara ditolak hanya
    bila ada versi lama yang berlaku lagi sesudah amandemen itu; tanpa versi lama (parameter baru), versi permanen itu
    menutup amandemen sementara lebih awal.
    Hasil: lama setelah disisipi, bentuknya sama dengan lama dan belum memuat versi baru itu sendiri."""
    if sampai is not None and sampai < mulai:
        raise KesalahanKB(f"{berkas}: {apa}: masa berlaku terbalik (sampai {sampai} sebelum mulai {mulai})")
    hasil = []
    for m, s, isi, asal, lanjutan in lama:
        melewati = sampai is not None and (s is None or s > sampai)
        if m >= mulai and (sampai is None or m <= sampai):
            if not lanjutan or m != mulai:
                if lanjutan:
                    asal = f"{asal}, berlaku lagi setelah amandemen sementara {lanjutan[-1][1]}"
                raise KesalahanKB(f"{berkas}: {apa} mulai {mulai} bentrok dengan versi yang berlaku mulai {m} ({asal})")
            if melewati:
                hasil.append((sampai + timedelta(days=1), s, isi, asal, lanjutan[:-1] + ((sampai, berkas),)))
            continue
        if m > mulai or (s is not None and s < mulai):   # tidak beririsan dengan versi baru
            hasil.append((m, s, isi, asal, lanjutan))
            continue
        hasil.append((m, mulai - timedelta(days=1), isi, asal, lanjutan))
        if melewati:
            hasil.append((sampai + timedelta(days=1), s, isi, asal, lanjutan + ((sampai, berkas),)))
    return hasil


def _sumber_versi(sumber, lanjutan):
    return sumber + "".join(f" (berlaku lagi setelah {s})" for s, _ in lanjutan)


def _jenis_nilai(v):
    return "rupiah (bilangan bulat)" if isinstance(v, int) else "tarif (teks desimal)"


def _amandemen_parameter(param, entri, berkas_dasar="parameter.yaml"):
    """Parameter dari berkas aturan, dengan semantik versi _sisipkan_versi. entri: [(p, lapisan, berkas, tambahan)]
    dari SEMUA berkas, diterapkan per nama parameter: entri berkas dasar lebih dulu (bersama parameter.yaml, itulah
    versi yang sudah ada), lalu entri berkas_tambahan menurut tanggal mulai, bukan menurut urutan berkas dimuat. Yang
    menentukan adalah masa berlaku (§6.4), sehingga hasilnya sama untuk setiap urutan berkas_tambahan.
    Kepemilikan lapisan juga tidak bergantung urutan: parameter milik regulasi bila ada di parameter.yaml atau ditulis
    berkas lapisan regulasi mana pun. Lapisan perusahaan tidak boleh mengubahnya (lex superior), tetapi boleh
    mengamandemen parameter yang hanya dibuat lapisan perusahaan."""
    milik_regulasi = {nama: berkas_dasar for nama in param}
    for p, lapisan, berkas, _ in entri:
        if lapisan == "regulasi":
            milik_regulasi.setdefault(p["nama"], berkas)
    per_nama = {}
    for p, lapisan, berkas, tambahan in entri:
        nama = p["nama"]
        if lapisan != "regulasi" and nama in milik_regulasi:
            raise KesalahanKB(f"{berkas}: parameter {nama} milik lapisan regulasi ({milik_regulasi[nama]}); "
                              "lapisan perusahaan tidak boleh mengubahnya")
        per_nama.setdefault(nama, []).append((tambahan, _tanggal(p["berlaku"]["mulai"]),
                                              _tanggal(p["berlaku"].get("sampai")), p, berkas))
    for nama, daftar in sorted(per_nama.items()):   # urutan kunci parameter baru pun tidak bergantung urutan berkas
        versi = [(m, s, (v, src), berkas_dasar, ()) for m, s, v, src in param.get(nama, [])]
        # pengurutan stabil: dari dua entri yang mulai pada tanggal sama (bentrok), yang dimuat belakangan yang ditolak
        for _, mulai, sampai, p, berkas in sorted(daftar, key=lambda e: e[:2]):
            try:
                nilai = _nilai_parameter(p["nilai"])
            except (ValueError, PelanggaranPresisi) as e:
                raise KesalahanKB(f"{berkas}: parameter {nama}: {e}") from None
            if versi and type(versi[0][2][0]) is not type(nilai):
                # mis. "11.500" (maksudnya 11.500.000) terbaca sebagai tarif 23/2 untuk parameter rupiah jp_batas_upah
                raise KesalahanKB(
                    f"{berkas}: parameter {nama}: nilai {p['nilai']!r} terbaca sebagai {_jenis_nilai(nilai)}, padahal "
                    f"versi yang ada bernilai {_jenis_nilai(versi[0][2][0])}. Rupiah ditulis sebagai bilangan bulat tanpa "
                    f"pemisah ribuan (mis. 11500000); tarif/persen ditulis sebagai teks desimal (mis. \"0.3\")")
            versi = _sisipkan_versi(versi, mulai, sampai, f"parameter {nama}", berkas)
            versi.append((mulai, sampai, (nilai, f"{p['sumber']} [{berkas}]"), berkas, ()))
            versi.sort(key=lambda x: x[0])   # bentrok dilaporkan terhadap versi yang mulai paling awal
        param[nama] = [(m, s, v, _sumber_versi(src, lanjutan)) for m, s, (v, src), _, lanjutan in versi]


def _amandemen_klasifikasi(entri):
    """Klasifikasi wajib berversi waktu, semantik sama dengan parameter: entri baru untuk jenis J menutup entri J yang
    masih berlaku pada tanggal mulainya (tanpa ini entri baru tidak pernah terpakai karena kalah urutan).
    entri: [(k, berkas, tambahan)] dari semua berkas, diterapkan per jenis seperti parameter: entri berkas dasar lebih
    dulu, lalu entri berkas_tambahan menurut tanggal mulai. Urutan daftar hasil juga tidak bergantung urutan
    berkas_tambahan: jenis dari berkas dasar menurut urutan muat, lalu jenis yang hanya ada di berkas tambahan menurut
    abjad; di dalam satu jenis menurut tanggal mulai."""
    per_jenis = {}
    for k, berkas, tambahan in entri:
        w = KlasifikasiWajib(k["jenis"], k["kategori"], _tanggal(k["berlaku"]["mulai"]),
                             _tanggal(k["berlaku"].get("sampai")), k["sumber"])
        per_jenis.setdefault(w.jenis, []).append((tambahan, w, berkas))
    urutan = list(dict.fromkeys(k["jenis"] for k, _, tambahan in entri if not tambahan))
    urutan += sorted(set(per_jenis) - set(urutan))
    klasifikasi = []
    for jenis in urutan:
        versi = []
        for _, baru, berkas in sorted(per_jenis[jenis], key=lambda e: (e[0], e[1].mulai)):
            versi = _sisipkan_versi(versi, baru.mulai, baru.sampai, f"klasifikasi wajib {jenis}", berkas)
            versi.append((baru.mulai, baru.sampai, baru, berkas, ()))
            versi.sort(key=lambda x: x[0])
        klasifikasi += [replace(w, mulai=m, sampai=s, sumber=_sumber_versi(w.sumber, lanjutan))
                        for m, s, w, _, lanjutan in versi]
    return klasifikasi


def rujukan_masukan(kb):
    """{kunci: {'lingkup': 'tahun'|'bulan', 'aturan': [id...], 'bawaan_di_aturan': bool}} dari hr()/hr_masa() di aturan."""
    hasil = {}
    for a in kb.aturan:
        for ek in [a.maka, a.jika, a.batas_bawah, a.batas_atas]:
            if ek is None:
                continue
            for fn, kunci, n_arg in ek.panggilan_literal({"hr", "hr_masa"}):
                r = hasil.setdefault(kunci, {"lingkup": set(), "aturan": [], "bawaan_di_aturan": True})
                r["lingkup"].add("tahun" if fn == "hr" else "bulan")
                if a.id not in r["aturan"]:
                    r["aturan"].append(a.id)
                r["bawaan_di_aturan"] = r["bawaan_di_aturan"] and fn == "hr_masa" and n_arg > 1
    return hasil


def _iso(obj):
    """Tanggal YAML (datetime.date) -> string ISO agar dapat divalidasi JSON Schema."""
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _iso(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_iso(v) for v in obj]
    return obj


def muat_kb(berkas_tambahan=(), berkas_regulasi=None, dir_regulasi=None):
    """dir_regulasi: direktori lapisan regulasi alternatif (dipakai mutation testing E4)."""
    dreg = Path(dir_regulasi or DIR_REGULASI)
    berkas_dasar = [dreg / b for b in (berkas_regulasi or BERKAS_ATURAN_REGULASI)]
    berkas = berkas_dasar + [Path(b) for b in berkas_tambahan]
    aturan, komponen, pencatatan, masukan = [], [], {}, {}
    registri = muat_registri_pembulatan(dreg / "pembulatan.yaml")
    parameter = _muat_parameter(dreg / "parameter.yaml")
    # amandemen dikumpulkan dulu dan baru diterapkan setelah semua berkas terbaca: hasilnya ditentukan masa berlaku
    # tiap entri, bukan urutan berkas dimuat
    entri_parameter, entri_klasifikasi = [], []
    asal_komponen = {}                                    # fakta -> berkas yang mendeklarasikannya
    for i, p in enumerate(berkas):
        data = _iso(muat_yaml(p))
        validasi_skema(data, "aturan.schema.json")
        lapisan, tambahan = data["lapisan"], i >= len(berkas_dasar)
        for d in data["aturan"]:
            a = _bangun_aturan(d, lapisan, p.name)
            ganda = next((x for x in aturan if x.id == a.id), None)
            if ganda is not None:   # diperiksa per berkas agar pesan menyebut kedua berkas
                raise KesalahanKB(f"{p.name}: id aturan duplikat: {a.id} sudah ada di {ganda.berkas}")
            aturan.append(a)
        if data.get("komponen"):
            if lapisan != "perusahaan":
                raise KesalahanKB(f"{p.name}: pemetaan komponen hanya boleh di lapisan perusahaan; untuk peraturan "
                                  "pemerintah, tulis tarif dan klasifikasi_wajib di berkas lapisan regulasi, lalu komponen "
                                  "dan aturannya di berkas perusahaan terpisah")
            for k in data["komponen"]:
                # _komponen() menjumlah per entri: deklarasi ganda = komponen terhitung dua kali di bruto, PPh & THP
                if k["fakta"] in asal_komponen:
                    raise KesalahanKB(f"{p.name}: komponen {k['fakta']} sudah dideklarasikan di {asal_komponen[k['fakta']]}; "
                                      "deklarasi ulang tidak diizinkan (kategori komponen yang sudah ada tidak dapat diubah "
                                      "lewat berkas tambahan)")
                asal_komponen[k["fakta"]] = p.name
                komponen.append(KomponenPerusahaan(k["fakta"], k["jenis"], k["kategori"], p.name, k.get("label")))
        for d in data.get("masukan") or []:
            _tambah_masukan(masukan, _bangun_masukan(d, p.name))
        entri_parameter += [(e, lapisan, p.name, tambahan) for e in data.get("parameter") or []]
        if data.get("klasifikasi_wajib"):
            if lapisan != "regulasi":
                raise KesalahanKB(f"{p.name}: klasifikasi wajib hanya boleh di lapisan regulasi")
            entri_klasifikasi += [(k, p.name, tambahan) for k in data["klasifikasi_wajib"]]
        if data.get("pembulatan"):
            registri.tambah(data["pembulatan"], lapisan)
        for c in data.get("pencatatan") or []:
            pencatatan[c["regulasi"]] = _tanggal(c["dicatat"])
    _amandemen_parameter(parameter, entri_parameter)
    klasifikasi = _amandemen_klasifikasi(entri_klasifikasi)
    tabel = {n: muat_tabel(n, dreg / "tabel_manifest.yaml") for n in ("ter_bulanan", "tarif_pasal17", "ptkp", "klu_dtp")}
    kb = KnowledgeBase(aturan=aturan, registri=registri, parameter=parameter, tabel=tabel,
                       berkas=[p.name for p in berkas], komponen=komponen, klasifikasi=klasifikasi,
                       pencatatan=pencatatan, masukan=masukan)
    verifikasi_statis(kb)
    return kb


def _verifikasi_versi_tabel(kb):
    """§6.6: versi tabel tidak boleh tumpang tindih; setiap versi TER per kategori harus tabel bertingkat sah."""
    from .interval import tabel_ter
    rezim = {}
    for r in kb.tabel["tarif_pasal17"]:
        rezim.setdefault(r["rezim"], (_tanggal(r["berlaku_mulai"]), _tanggal(r["berlaku_sampai"] or None)))
    daftar = sorted(rezim.items(), key=lambda kv: kv[1][0])
    for (n1, (m1, s1)), (n2, (m2, s2)) in zip(daftar, daftar[1:]):
        if s1 is None or s1 >= m2:
            raise KesalahanKB(f"tabel Pasal 17: versi '{n1}' dan '{n2}' berlaku bersamaan (tumpang tindih masa berlaku)")
    for mulai in {r["berlaku_mulai"] for r in kb.tabel["ter_bulanan"]}:
        versi = [r for r in kb.tabel["ter_bulanan"] if r["berlaku_mulai"] == mulai]
        for k in sorted({r["kategori"] for r in versi}):
            tabel_ter(versi, k)   # melempar bila celah / tumpang tindih / tidak berakhir di tak hingga


def _verifikasi_argumen_literal(kb, a, ekspresi):
    """Argumen literal yang pasti salah ditolak saat muat, bukan saat menghitung (untuk komponen(): kategori salah
    ketik diam-diam menjumlah 0). Hanya argumen pertama, yang maknanya pasti, yang diperiksa."""
    kategori = KATEGORI_KOMPONEN + KATEGORI_INPUT
    for e in ekspresi:
        for fn, arg, _ in e.panggilan_literal(FUNGSI_KOMPONEN | {"parameter", "bulatkan"}):
            if fn in FUNGSI_KOMPONEN and arg not in kategori:
                raise KesalahanKB(f"{a.id}: {fn}('{arg}'): kategori komponen tidak dikenal (pilihan: {', '.join(kategori)})")
            if fn == "parameter" and arg not in kb.parameter:
                raise KesalahanKB(f"{a.id}: parameter('{arg}') tidak dikenal (tidak ada di kb/regulasi/parameter.yaml "
                                  "maupun berkas tambahan)")
            if fn == "bulatkan" and arg not in kb.registri:
                raise KesalahanKB(f"{a.id}: bulatkan('{arg}', ...): entri pembulatan tidak terdaftar di registri")


def _verifikasi_menggantikan(kb):
    """`menggantikan: [ID, ...]` = pencabutan eksplisit: selama aturan pengganti berlaku menurut tanggal, aturan yang
    disebutnya keluar dari kandidat faktanya sebelum resolusi konflik (engine/inferensi.py). Itulah yang dicapai KB
    dasar dengan mengisi `sampai` pada aturan lama; berkas tambahan tidak dapat mengubah aturan yang sudah ada.

    Diperiksa setelah SEMUA berkas termuat dan menurut id aturan, sehingga hasil maupun pesannya tidak bergantung urutan
    berkas. Pengganti wajib mulai sesudah aturan yang digantikannya, jadi tidak mungkin ada siklus."""
    per_id = {a.id: a for a in kb.aturan}
    for x in sorted((a for a in kb.aturan if a.menggantikan), key=lambda a: a.id):
        for id_lama in x.menggantikan:
            if id_lama == x.id:
                raise KesalahanKB(f"{x.berkas}: aturan {x.id} tidak boleh menggantikan dirinya sendiri")
            t = per_id.get(id_lama)
            if t is None:
                raise KesalahanKB(f"{x.berkas}: aturan {x.id} menggantikan {id_lama}, tetapi tidak ada aturan ber-id {id_lama} "
                                  "di KB dasar maupun di berkas tambahan yang dimuat")
            awal = f"{x.berkas}: aturan {x.id} tidak dapat menggantikan {t.id} ({t.berkas}): "
            if x.menghasilkan != t.menghasilkan:
                raise KesalahanKB(f"{awal}keduanya menghasilkan fakta berbeda ({x.menghasilkan} vs {t.menghasilkan})")
            if x.lingkup != t.lingkup:
                raise KesalahanKB(f"{awal}lingkupnya berbeda ({x.lingkup} vs {t.lingkup})")
            if x.lapisan != t.lapisan:
                raise KesalahanKB(f"{awal}lapisannya berbeda ({x.lapisan} vs {t.lapisan}); `menggantikan` hanya berlaku di "
                                  "dalam satu lapisan, urutan antar-lapisan diatur lex superior / override sah")
            for a in (x, t):
                if a.sifat == "tafsir" or a.tafsir:
                    raise KesalahanKB(f"{awal}{a.id} adalah aturan tafsir; aturan tafsir dipilih lewat varian, bukan "
                                      "dicabut lewat `menggantikan`")
            if x.mulai <= t.mulai:
                raise KesalahanKB(f"{awal}{x.id} mulai berlaku {x.mulai}, tidak lebih baru daripada {t.id} ({t.mulai}); "
                                  "aturan pengganti wajib mulai berlaku sesudah aturan yang digantikannya")
            if t.sampai is not None and t.sampai < x.mulai:
                raise KesalahanKB(f"{awal}{t.id} sudah berakhir {t.sampai}, sebelum {x.id} mulai berlaku ({x.mulai}), "
                                  "sehingga tidak ada yang digantikan")


def verifikasi_statis(kb):
    """Pemeriksaan yang tidak bergantung kasus (§6.6). Pemeriksaan per-tahun ada di inferensi.graf()."""
    _verifikasi_versi_tabel(kb)
    ids = [a.id for a in kb.aturan]
    duplikat = {i for i in ids if ids.count(i) > 1}
    if duplikat:
        raise KesalahanKB(f"id aturan duplikat: {sorted(duplikat)}")
    per_fakta = {}
    for a in kb.aturan:
        per_fakta.setdefault(a.menghasilkan, []).append(a)
        if a.tipe_hasil == "rupiah" and a.pembulatan and a.pembulatan not in kb.registri:
            raise KesalahanKB(f"{a.id}: pembulatan {a.pembulatan} tidak terdaftar di registri")
        if a.sifat == "tafsir" and (not a.tafsir or not a.varian):
            raise KesalahanKB(f"{a.id}: aturan tafsir wajib punya 'tafsir' dan 'varian'")
        if a.titik_tetap and (a.batas_bawah is None or a.batas_atas is None):
            raise KesalahanKB(f"{a.id}: aturan titik_tetap wajib punya batas_titik_tetap (bawah/atas) agar Tarski berlaku")
        if a.sampai is not None and a.sampai < a.mulai:
            raise KesalahanKB(f"{a.id}: masa berlaku terbalik")
    _verifikasi_menggantikan(kb)
    for k in kb.komponen:
        if k.fakta not in per_fakta:
            raise KesalahanKB(f"komponen perusahaan {k.fakta} tidak dihasilkan aturan mana pun")
        if per_fakta[k.fakta][0].lingkup != "masa" or per_fakta[k.fakta][0].tipe_hasil != "rupiah":
            raise KesalahanKB(f"komponen perusahaan {k.fakta} wajib fakta masa bertipe rupiah")
    for fakta, daftar in per_fakta.items():
        lingkup = {a.lingkup for a in daftar}
        if len(lingkup) > 1:
            raise KesalahanKB(f"fakta {fakta} dihasilkan dengan lingkup berbeda: {lingkup}")
        tipe = {a.tipe_hasil for a in daftar}
        if len(tipe) > 1:
            raise KesalahanKB(f"fakta {fakta} dihasilkan dengan tipe berbeda: {tipe}")
        if fakta in FAKTA_DASAR_TAHUN | FAKTA_DASAR_MASA:
            raise KesalahanKB(f"fakta dasar {fakta} tidak boleh dihasilkan aturan")
    for a in kb.aturan:
        ekspresi = [e for e in (a.maka, a.jika, a.batas_bawah, a.batas_atas) if e is not None]
        if a.lingkup == "tahun" and any("hr_masa" in e.fungsi for e in ekspresi):
            raise KesalahanKB(f"{a.id}: aturan berlingkup tahun tidak boleh memanggil hr_masa() (tidak ada masa yang "
                              "dibaca, sehingga nilainya selalu bawaan); pakai hr('kunci') untuk masukan tahunan, atau "
                              "hitung fakta berlingkup masa lalu jumlahkan dengan jumlah_masa()")
        _verifikasi_argumen_literal(kb, a, ekspresi)
    for kunci, r in rujukan_masukan(kb).items():
        m = kb.masukan.get(kunci)
        if m is not None and r["lingkup"] != {m.lingkup}:
            cara = "hr()" if m.lingkup == "tahun" else "hr_masa()"
            raise KesalahanKB(f"masukan {kunci} berlingkup {m.lingkup} wajib dibaca dengan {cara} (aturan {r['aturan']})")
    grup = {}
    for a in kb.aturan:
        if a.tafsir:
            grup.setdefault(a.tafsir, []).append(a)
    for t, ats in grup.items():
        default = {a.varian for a in ats if a.varian_default}
        if len(default) != 1:
            raise KesalahanKB(f"tafsir {t}: wajib tepat satu varian default di seluruh KB (ditemukan {sorted(default)})")
        tidak_konsisten = [a.id for a in ats if a.varian in default and not a.varian_default]
        if tidak_konsisten:
            raise KesalahanKB(f"tafsir {t}: aturan varian default tidak bertanda varian_default: {tidak_konsisten}")
    return True


def parameter_pada(kb, nama, tgl):
    if nama not in kb.parameter:
        raise KesalahanKB(f"parameter tidak dikenal: {nama}")
    cocok = [v for mulai, sampai, v, _ in kb.parameter[nama] if mulai <= tgl and (sampai is None or tgl <= sampai)]
    if len(cocok) != 1:
        raise KesalahanKB(f"parameter {nama} pada {tgl}: {len(cocok)} versi berlaku (harus tepat 1)")
    return cocok[0]


def masa_berlaku_efektif(kb):
    """{id aturan: (mulai, sampai_efektif)}: masa berlaku tiap aturan setelah pencabutan eksplisit (`menggantikan`).

    sampai_efektif = `sampai` aturan itu sendiri, dipendekkan menjadi sehari sebelum `mulai` aturan pengganti PERMANEN
    (tanpa `sampai`) paling awal yang menyebutnya. Pengganti sementara tidak memendekkannya: sesudah pengganti itu
    berakhir, aturan lama berlaku lagi. Dihitung dari seluruh KB (tanpa knowledge time); dipakai mis. agar isian yang
    hanya dibaca aturan yang sudah dicabut permanen tidak lagi diminta."""
    hasil = {a.id: (a.mulai, a.sampai) for a in kb.aturan}
    for x in kb.aturan:
        if x.sampai is not None:
            continue
        akhir = x.mulai - timedelta(days=1)
        for id_lama in x.menggantikan:
            mulai, sampai = hasil[id_lama]
            if sampai is None or akhir < sampai:
                hasil[id_lama] = (mulai, akhir)
    return hasil
