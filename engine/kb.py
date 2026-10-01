"""Pemuat & verifikator statis knowledge base aturan (research_plan.md §6.2, §6.6).

Satu KB = kumpulan berkas aturan YAML (lapisan regulasi + opsional lapisan perusahaan),
registri pembulatan, parameter berversi, dan tabel bertingkat (lewat manifest berhash).
"""
from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction
from pathlib import Path

from .angka import PelanggaranPresisi, rupiah, tarif
from .ekspresi import Ekspresi, jumlah_konjungsi
from .muat import ROOT, KesalahanKB, muat_registri_pembulatan, muat_tabel, muat_yaml, validasi_skema

DIR_REGULASI = ROOT / "kb" / "regulasi"
BERKAS_ATURAN_REGULASI = ["aturan_umum.yaml", "aturan_ter.yaml", "aturan_per16.yaml", "aturan_dtp.yaml", "klasifikasi.yaml"]


@dataclass(frozen=True)
class MetaFungsi:
    argumen_fakta: bool = False   # argumen pertama (string) adalah nama fakta -> dependensi


# Fungsi yang boleh dipakai di DSL. Implementasinya ada di engine/inferensi.py.
FUNGSI = {
    "min": MetaFungsi(), "max": MetaFungsi(), "abs": MetaFungsi(),
    "persen": MetaFungsi(), "parameter": MetaFungsi(), "bulatkan": MetaFungsi(),
    "ptkp": MetaFungsi(), "kategori_ter": MetaFungsi(), "kawin": MetaFungsi(),
    "tarif_ter": MetaFungsi(), "pasal17": MetaFungsi(),
    "komponen": MetaFungsi(), "komponen_kode": MetaFungsi(), "komponen_valas": MetaFungsi(),
    "dtp_sektor_tahun": MetaFungsi(), "dtp_masa_fasilitas": MetaFungsi(),
    "atau": MetaFungsi(argumen_fakta=True), "nilai_masa": MetaFungsi(argumen_fakta=True),
    "jumlah_masa": MetaFungsi(argumen_fakta=True),
    "jumlah_masa_selain_terakhir": MetaFungsi(argumen_fakta=True),
    "tolak": MetaFungsi(),
    # data HR mentah (lapisan perusahaan) & tanggal
    "hr": MetaFungsi(), "hr_masa": MetaFungsi(), "desimal": MetaFungsi(),
    "tanggal": MetaFungsi(), "tanggal_masa": MetaFungsi(), "tambah_hari": MetaFungsi(), "geser_bulan": MetaFungsi(),
    "selisih_hari": MetaFungsi(), "selisih_bulan": MetaFungsi(), "bulan_dari": MetaFungsi(), "hari_dari": MetaFungsi(),
    "tahun_dari": MetaFungsi(),
}
FUNGSI_KOMPONEN = {"komponen", "komponen_kode", "komponen_valas"}

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
            sumbu_waktu=d.get("sumbu_waktu", "masa_pajak"), berkas=berkas)
    except (KesalahanKB, PelanggaranPresisi, ValueError) as e:
        raise KesalahanKB(f"{berkas}: aturan {d.get('id')}: {e}") from None


@dataclass(frozen=True)
class KomponenPerusahaan:
    fakta: str
    jenis: str
    kategori: str
    berkas: str


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

    def aturan_untuk(self, fakta):
        return [a for a in self.aturan if a.menghasilkan == fakta]


def _muat_parameter(path):
    data = muat_yaml(path)
    hasil = {}
    for p in data["parameter"]:
        nilai = p["nilai"]
        if isinstance(nilai, str):
            nilai = tarif(nilai)
        else:
            nilai = rupiah(nilai)
        hasil.setdefault(p["nama"], []).append((_tanggal(p["berlaku"]["mulai"]), _tanggal(p["berlaku"].get("sampai")),
                                                 nilai, p["sumber"]))
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
    berkas = [dreg / b for b in (berkas_regulasi or BERKAS_ATURAN_REGULASI)] + [Path(b) for b in berkas_tambahan]
    aturan, komponen, klasifikasi = [], [], []
    registri = muat_registri_pembulatan(dreg / "pembulatan.yaml")
    for p in berkas:
        data = _iso(muat_yaml(p))
        validasi_skema(data, "aturan.schema.json")
        lapisan = data["lapisan"]
        for d in data["aturan"]:
            aturan.append(_bangun_aturan(d, lapisan, p.name))
        if data.get("komponen"):
            if lapisan != "perusahaan":
                raise KesalahanKB(f"{p.name}: pemetaan komponen hanya boleh di lapisan perusahaan")
            komponen += [KomponenPerusahaan(k["fakta"], k["jenis"], k["kategori"], p.name) for k in data["komponen"]]
        if data.get("klasifikasi_wajib"):
            if lapisan != "regulasi":
                raise KesalahanKB(f"{p.name}: klasifikasi wajib hanya boleh di lapisan regulasi")
            klasifikasi += [KlasifikasiWajib(k["jenis"], k["kategori"], _tanggal(k["berlaku"]["mulai"]),
                                             _tanggal(k["berlaku"].get("sampai")), k["sumber"]) for k in data["klasifikasi_wajib"]]
        if data.get("pembulatan"):
            registri.tambah(data["pembulatan"], lapisan)
    tabel = {n: muat_tabel(n, dreg / "tabel_manifest.yaml") for n in ("ter_bulanan", "tarif_pasal17", "ptkp", "klu_dtp")}
    kb = KnowledgeBase(aturan=aturan, registri=registri,
                       parameter=_muat_parameter(dreg / "parameter.yaml"), tabel=tabel,
                       berkas=[p.name for p in berkas], komponen=komponen, klasifikasi=klasifikasi)
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
