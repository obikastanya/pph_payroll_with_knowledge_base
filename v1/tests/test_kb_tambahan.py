"""Kontrak berkas KB tambahan: penolakan deklarasi berbahaya dan semantik amandemen berversi waktu.

E1 komponen ganda, E2 kontrak masukan, E3 amandemen parameter, E4 klasifikasi wajib & take home pay,
E5 pengerasan ekspresi, E6 alias YAML, E7 batas titik tetap, E8 parameter perusahaan. Setiap tes menulis berkas
tambahan ke tmp_path, persis seperti aplikasi web menyimpan berkas yang disetujui di kb/tambahan/.
Ketidakbergantungan amandemen pada urutan berkas dimuat diuji di tests/test_urutan_amandemen.py.
"""
import json
import sys
from datetime import date
from fractions import Fraction

import pytest

from eksperimen.e12_tanpa_kb import BERKAS_PX
from eksperimen.e8_perusahaan_x import kasus_kar_a
from engine.angka import PelanggaranPresisi
from engine.ekspresi import Ekspresi, KesalahanEkspresi
from engine.inferensi import Evaluasi
from engine.kalkulator import hitung
from engine.kb import FUNGSI, KATEGORI_KOMPONEN, KlasifikasiWajib, muat_kb, nilai_masukan, parameter_pada
from engine.muat import ROOT, KesalahanKB, muat_yaml
from engine.pembulatan import bulatkan


def _tulis(tmp_path, nama, isi):
    p = tmp_path / nama
    p.write_text(isi, encoding="utf-8")
    return p


def _komponen_baru(fakta, kategori, jenis, kunci, id_aturan, tambahan_masukan=""):
    return f"""
lapisan: perusahaan
komponen:
  - {{fakta: {fakta}, jenis: {jenis}, kategori: {kategori}}}
masukan:
  - {{kunci: {kunci}, label: "Nilai {kunci}", tipe: rupiah, lingkup: tahun, wajib: false, bawaan: 0{tambahan_masukan}}}
aturan:
  - id: {id_aturan}
    sifat: opsional
    berlaku: {{mulai: 2016-01-01}}
    lingkup: masa
    menghasilkan: {fakta}
    maka: "hr('{kunci}')"
    tipe_hasil: rupiah
    sumber: "uji berkas tambahan"
"""


# ------------------------------------------------------------------------------------------- E1 komponen ganda

def test_komponen_sama_di_dua_berkas_tambahan_ditolak(tmp_path):
    a = _tulis(tmp_path, "transport_a.yaml", _komponen_baru("px_transport", "teratur", "tunjangan_transport", "transport_a", "UJI-TRA-01"))
    b = _tulis(tmp_path, "transport_b.yaml", _komponen_baru("px_transport", "teratur", "tunjangan_transport", "transport_b", "UJI-TRB-01"))
    with pytest.raises(KesalahanKB, match=r"transport_b\.yaml: komponen px_transport sudah dideklarasikan di transport_a\.yaml; "
                                          r"deklarasi ulang tidak diizinkan"):
        muat_kb([*BERKAS_PX, a, b])


def test_berkas_tambahan_tidak_boleh_mendeklarasikan_ulang_komponen_dasar(tmp_path):
    # tanpa penolakan, px_lembur terhitung dua kali di bruto, PPh 21, dan take home pay
    p = _tulis(tmp_path, "lembur.yaml", "lapisan: perusahaan\naturan: []\nkomponen:\n"
                                        "  - {fakta: px_lembur, jenis: lembur, kategori: teratur}\n")
    with pytest.raises(KesalahanKB, match=r"lembur\.yaml: komponen px_lembur sudah dideklarasikan di perusahaan_x\.yaml.*"
                                          r"kategori komponen yang sudah ada tidak dapat diubah"):
        muat_kb([*BERKAS_PX, p])


def test_komponen_ganda_dalam_satu_berkas_ditolak(tmp_path):
    isi = _komponen_baru("px_transport", "teratur", "tunjangan_transport", "transport", "UJI-TRA-01").replace(
        "komponen:\n", "komponen:\n  - {fakta: px_transport, jenis: tunjangan_transport, kategori: teratur}\n")
    with pytest.raises(KesalahanKB, match="komponen px_transport sudah dideklarasikan"):
        muat_kb([*BERKAS_PX, _tulis(tmp_path, "t.yaml", isi)])


def test_berkas_yang_sama_dimuat_dua_kali_ditolak_sebagai_id_aturan_duplikat(tmp_path):
    isi = _komponen_baru("px_transport", "teratur", "tunjangan_transport", "transport", "UJI-TRA-01")
    a, b = _tulis(tmp_path, "a.yaml", isi), _tulis(tmp_path, "b.yaml", isi)
    with pytest.raises(KesalahanKB, match=r"b\.yaml: id aturan duplikat: UJI-TRA-01 sudah ada di a\.yaml"):
        muat_kb([*BERKAS_PX, a, b])


def test_kb_dasar_tetap_termuat_tanpa_komponen_ganda():
    kb = muat_kb(BERKAS_PX)
    fakta = [k.fakta for k in kb.komponen]
    assert len(fakta) == len(set(fakta)) == 15


def test_komponen_di_berkas_regulasi_ditolak_dengan_jalan_keluar(tmp_path):
    # peraturan pemerintah yang memperkenalkan komponen gaji baru: pesan menunjukkan cara memecah berkasnya
    isi = _komponen_baru("px_transport", "teratur", "tunjangan_transport", "transport", "UJI-TRA-01").replace(
        "lapisan: perusahaan", "lapisan: regulasi")
    with pytest.raises(KesalahanKB) as galat:
        muat_kb([*BERKAS_PX, _tulis(tmp_path, "pp.yaml", isi)])
    assert str(galat.value) == (
        "pp.yaml: pemetaan komponen hanya boleh di lapisan perusahaan; untuk peraturan pemerintah, tulis tarif dan "
        "klasifikasi_wajib di berkas lapisan regulasi, lalu komponen dan aturannya di berkas perusahaan terpisah")


# ------------------------------------------------------------------------------------------- E2 kontrak masukan

MASUKAN_A = """
lapisan: perusahaan
masukan:
  - {kunci: uang_makan, label: "Uang makan", tipe: rupiah, lingkup: tahun, wajib: false, bawaan: 0, sumber: "PP 2024"}
aturan:
  - {id: UJI-MAKAN-A, sifat: opsional, berlaku: {mulai: 2016-01-01}, lingkup: masa, menghasilkan: _uji_makan_a,
     maka: "hr('uang_makan')", tipe_hasil: rupiah, sumber: "uji"}
"""


def test_deklarasi_ulang_masukan_identik_diizinkan(tmp_path):
    a = _tulis(tmp_path, "a.yaml", MASUKAN_A)
    b = _tulis(tmp_path, "b.yaml", MASUKAN_A.replace("UJI-MAKAN-A", "UJI-MAKAN-B").replace("_uji_makan_a", "_uji_makan_b")
               .replace('label: "Uang makan"', 'label: "Uang makan harian", keterangan: "teks lain"')
               .replace('sumber: "PP 2024"', 'sumber: "PP 2025"'))
    kb = muat_kb([*BERKAS_PX, a, b])
    assert kb.masukan["uang_makan"].label == "Uang makan" and kb.masukan["uang_makan"].berkas == "a.yaml"


@pytest.mark.parametrize("ubah, atribut", [
    ("bawaan: 0", "bawaan: 5000"),
    ("wajib: false", "wajib: true"),
    ("tipe: rupiah", "tipe: bilangan"),
])
def test_deklarasi_ulang_masukan_berbeda_ditolak(tmp_path, ubah, atribut):
    a = _tulis(tmp_path, "a.yaml", MASUKAN_A)
    b = _tulis(tmp_path, "b.yaml", MASUKAN_A.replace("UJI-MAKAN-A", "UJI-MAKAN-B").replace("_uji_makan_a", "_uji_makan_b")
               .replace(ubah, atribut))
    nama = atribut.split(":")[0]
    with pytest.raises(KesalahanKB, match=rf"b\.yaml: masukan uang_makan sudah dideklarasikan di a\.yaml dengan atribut "
                                          rf"berbeda: {nama} "):
        muat_kb([*BERKAS_PX, a, b])


def test_aturan_tahunan_yang_memanggil_hr_masa_ditolak(tmp_path):
    isi = """
lapisan: perusahaan
aturan:
  - {id: UJI-TAHUN-01, sifat: opsional, berlaku: {mulai: 2016-01-01}, lingkup: tahun, menghasilkan: _uji_tahunan,
     maka: "hr_masa('lembur', 0)", tipe_hasil: rupiah, sumber: "uji"}
"""
    with pytest.raises(KesalahanKB, match=r"UJI-TAHUN-01: aturan berlingkup tahun tidak boleh memanggil hr_masa\(\).*hr\('kunci'\)"):
        muat_kb([*BERKAS_PX, _tulis(tmp_path, "t.yaml", isi)])


def test_masukan_rupiah_negatif_ditolak_bilangan_tidak(tmp_path):
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "a.yaml", MASUKAN_A)])
    m = kb.masukan["uang_makan"]
    with pytest.raises(KesalahanKB, match="tidak boleh negatif"):
        nilai_masukan(m, -1, "data_hr")
    assert nilai_masukan(m, 0, "data_hr") == 0
    bilangan = type(m)(**{**m.__dict__, "tipe": "bilangan"})
    assert nilai_masukan(bilangan, -3, "data_hr") == -3
    with pytest.raises(KesalahanKB, match="tidak boleh negatif"):
        muat_kb([*BERKAS_PX, _tulis(tmp_path, "b.yaml", MASUKAN_A.replace("bawaan: 0", "bawaan: -5"))])
    kasus = kasus_kar_a(2024)
    kasus["data_hr"]["uang_makan"] = -100_000
    with pytest.raises(KesalahanKB, match="uang_makan.*tidak boleh negatif"):
        hitung(kasus, kb=kb)


def test_kunci_masukan_maksimal_64_karakter(tmp_path):
    def isi(kunci):
        return MASUKAN_A.replace("uang_makan", kunci)
    muat_kb([*BERKAS_PX, _tulis(tmp_path, "ok.yaml", isi("k" * 64))])
    with pytest.raises(KesalahanKB, match="too long"):
        muat_kb([*BERKAS_PX, _tulis(tmp_path, "panjang.yaml", isi("k" * 65))])


# ------------------------------------------------------------------------------------------- E3 amandemen parameter

def _parameter(lapisan, nama, nilai, mulai, sampai=None):
    berlaku = f"{{mulai: {mulai}" + (f", sampai: {sampai}}}" if sampai else "}")
    return f"""
lapisan: {lapisan}
aturan: []
parameter:
  - nama: {nama}
    nilai: {nilai}
    berlaku: {berlaku}
    sumber: "uji amandemen"
"""


def test_amandemen_sementara_tidak_memutus_versi_lama(tmp_path):
    # keringanan iuran JKM Juli-Desember 2025; sesudahnya tarif lama berlaku lagi (dulu: "0 versi berlaku" di 2026)
    p = _tulis(tmp_path, "jkm.yaml", _parameter("regulasi", "jkm_pk_persen", '"0.1"', "2025-07-01", "2025-12-31"))
    kb = muat_kb([*BERKAS_PX, p])
    assert parameter_pada(kb, "jkm_pk_persen", date(2025, 6, 30)) == Fraction(3, 10)
    assert parameter_pada(kb, "jkm_pk_persen", date(2025, 7, 1)) == Fraction(1, 10)
    assert parameter_pada(kb, "jkm_pk_persen", date(2026, 1, 1)) == Fraction(3, 10)
    versi = kb.parameter["jkm_pk_persen"]
    assert [v[0] for v in versi] == sorted(v[0] for v in versi)
    assert versi[-1][1] is None and "berlaku lagi setelah 2025-12-31" in versi[-1][3]
    h25 = hitung(kasus_kar_a(2025), kb=kb)
    h26 = hitung(kasus_kar_a(2026), kb=kb)
    dasar26 = hitung(kasus_kar_a(2026), berkas_perusahaan=BERKAS_PX)
    assert [m["px_premi_jkm"] for m in h26["per_masa"].values()] == [m["px_premi_jkm"] for m in dasar26["per_masa"].values()]
    assert h26["per_masa"][12]["px_premi_jkm"] > 0
    for b, tarif_jkm in ((6, Fraction(3, 1000)), (8, Fraction(1, 1000))):
        m = h25["per_masa"][b]
        assert m["px_premi_jkm"] == bulatkan(tarif_jkm * m["px_gaji_berlaku"], "setengah_menjauhi_nol") > 0


def test_amandemen_sementara_menyambung_versi_berakhir_dan_menyisakan_versi_berikutnya(tmp_path):
    p = _tulis(tmp_path, "jp.yaml", _parameter("regulasi", "jp_batas_upah", 12000000, "2025-07-01", "2025-09-30"))
    kb = muat_kb([p])
    assert parameter_pada(kb, "jp_batas_upah", date(2025, 6, 1)) == 10_547_400
    assert parameter_pada(kb, "jp_batas_upah", date(2025, 8, 1)) == 12_000_000
    assert parameter_pada(kb, "jp_batas_upah", date(2025, 10, 1)) == 10_547_400
    assert parameter_pada(kb, "jp_batas_upah", date(2026, 2, 28)) == 10_547_400
    assert parameter_pada(kb, "jp_batas_upah", date(2026, 3, 1)) == 11_086_300


def test_amandemen_dengan_sampai_sebelum_mulai_ditolak(tmp_path):
    p = _tulis(tmp_path, "jkm.yaml", _parameter("regulasi", "jkm_pk_persen", '"0.1"', "2025-07-01", "2025-06-30"))
    with pytest.raises(KesalahanKB, match="masa berlaku terbalik"):
        muat_kb([p])


@pytest.mark.parametrize("nama, nilai", [("jp_batas_upah", '"11.500"'), ("jkm_pk_persen", "1")])
def test_jenis_nilai_amandemen_wajib_sama_dengan_versi_lama(tmp_path, nama, nilai):
    # "11.500" (maksudnya 11.500.000) terbaca sebagai tarif 23/2, bukan rupiah
    p = _tulis(tmp_path, "p.yaml", _parameter("regulasi", nama, nilai, "2026-06-01"))
    with pytest.raises(KesalahanKB, match=r"Rupiah ditulis sebagai bilangan bulat tanpa pemisah ribuan.*teks desimal"):
        muat_kb([p])


def test_perusahaan_boleh_mengamandemen_parameter_buatannya_sendiri(tmp_path):
    a = _tulis(tmp_path, "a.yaml", _parameter("perusahaan", "px_uang_makan_harian", 25000, "2024-01-01"))
    b = _tulis(tmp_path, "b.yaml", _parameter("perusahaan", "px_uang_makan_harian", 30000, "2025-01-01"))
    kb = muat_kb([*BERKAS_PX, a, b])
    assert parameter_pada(kb, "px_uang_makan_harian", date(2024, 12, 31)) == 25_000
    assert parameter_pada(kb, "px_uang_makan_harian", date(2025, 1, 1)) == 30_000


def test_perusahaan_tetap_tidak_boleh_mengamandemen_parameter_regulasi(tmp_path):
    for i, (nama, nilai) in enumerate([("jkm_pk_persen", '"0.1"'), ("jp_batas_upah", 12000000)]):
        p = _tulis(tmp_path, f"p{i}.yaml", _parameter("perusahaan", nama, nilai, "2026-06-01"))
        with pytest.raises(KesalahanKB, match="lapisan perusahaan tidak boleh mengubahnya"):
            muat_kb([*BERKAS_PX, p])
    # parameter baru dari berkas regulasi tambahan juga milik regulasi
    reg = _tulis(tmp_path, "reg.yaml", _parameter("regulasi", "batas_baru", 1000, "2026-01-01"))
    prsh = _tulis(tmp_path, "prsh.yaml", _parameter("perusahaan", "batas_baru", 2000, "2026-06-01"))
    with pytest.raises(KesalahanKB, match="lapisan perusahaan tidak boleh mengubahnya"):
        muat_kb([reg, prsh])


# ------------------------------------------------------------------------------------------- E4 klasifikasi & THP

KLASIFIKASI_JKN = """
lapisan: regulasi
aturan: []
klasifikasi_wajib:
  - {jenis: iuran_jkn_pegawai, kategori: iuran_pengurang, berlaku: {mulai: 2026-01-01}, sumber: "simulasi amandemen"}
"""


def test_reklasifikasi_jkn_menutup_entri_lama_dan_thp_tidak_terpotong_dua_kali(tmp_path):
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "jkn.yaml", KLASIFIKASI_JKN)])
    jkn = [w for w in kb.klasifikasi if w.jenis == "iuran_jkn_pegawai"]
    assert [(w.kategori, w.mulai, w.sampai) for w in jkn] == [
        ("tidak_diperhitungkan", date(2016, 1, 1), date(2025, 12, 31)), ("iuran_pengurang", date(2026, 1, 1), None)]
    dasar = hitung(kasus_kar_a(2026), berkas_perusahaan=BERKAS_PX)
    h = hitung(kasus_kar_a(2026), kb=kb)
    kes = sum(h["per_masa"][b]["px_iuran_kes_pg"] for b in range(1, 13))
    assert kes > 0
    assert h["tahunan"]["iuran_pengurang"] == dasar["tahunan"]["iuran_pengurang"] + kes
    for b in range(1, 13):
        # THP hanya bergeser sebesar perubahan PPh 21 (iuran kini mengurangi neto), bukan dipotong iuran JKN dua kali
        assert h["per_masa"][b]["px_thp"] + h["per_masa"][b]["pph21"] == dasar["per_masa"][b]["px_thp"] + dasar["per_masa"][b]["pph21"]
    for b in range(1, 12):   # TER Jan-Nov tidak dipengaruhi iuran pengurang
        assert h["per_masa"][b]["px_thp"] == dasar["per_masa"][b]["px_thp"]
    # 2025 tetap memakai klasifikasi lama
    h25 = hitung(kasus_kar_a(2025), kb=kb)
    assert h25["tahunan"]["iuran_pengurang"] == hitung(kasus_kar_a(2025), berkas_perusahaan=BERKAS_PX)["tahunan"]["iuran_pengurang"]


def test_klasifikasi_yang_mendahului_entri_lama_bentrok(tmp_path):
    p = _tulis(tmp_path, "k.yaml", KLASIFIKASI_JKN.replace("2026-01-01", "2016-01-01"))
    with pytest.raises(KesalahanKB, match="klasifikasi wajib iuran_jkn_pegawai mulai 2016-01-01 bentrok"):
        muat_kb([p])


def test_klasifikasi_sementara_berlaku_lagi_setelah_berakhir(tmp_path):
    p = _tulis(tmp_path, "k.yaml", KLASIFIKASI_JKN.replace("{mulai: 2026-01-01}", "{mulai: 2026-01-01, sampai: 2026-06-30}"))
    kb = muat_kb([p])
    jkn = [(w.kategori, w.mulai, w.sampai) for w in kb.klasifikasi if w.jenis == "iuran_jkn_pegawai"]
    assert jkn[-1] == ("tidak_diperhitungkan", date(2026, 7, 1), None)


def test_kategori_efektif_memilih_entri_yang_mulai_terakhir():
    kb = muat_kb(BERKAS_PX)
    # entri yang tidak dipotong (mis. disisipkan langsung) tetap diselesaikan dengan lex posterior
    kb.klasifikasi.append(KlasifikasiWajib("iuran_jkn_pegawai", "iuran_pengurang", date(2026, 1, 1), None, "uji"))
    h = hitung(kasus_kar_a(2026), kb=kb)
    assert any(p["kode"] == "KONFLIK_WAJIB" and p.get("fakta") == "px_iuran_kes_pg" and p["kategori_wajib"] == "iuran_pengurang"
               for p in h["peringatan"])


def test_potongan_koperasi_tidak_diperhitungkan_mengurangi_thp_saja(tmp_path):
    p = _tulis(tmp_path, "koperasi.yaml", _komponen_baru("px_koperasi", "tidak_diperhitungkan", "cicilan_koperasi",
                                                          "cicilan_koperasi_bulanan", "UJI-KOP-01"))
    dasar = hitung(kasus_kar_a(2024), berkas_perusahaan=BERKAS_PX)
    kasus = kasus_kar_a(2024)
    kasus["data_hr"]["cicilan_koperasi_bulanan"] = 150_000
    h = hitung(kasus, kb=muat_kb([*BERKAS_PX, p]))
    for b in range(1, 13):
        assert h["per_masa"][b]["px_koperasi"] == 150_000
        assert dasar["per_masa"][b]["px_thp"] - h["per_masa"][b]["px_thp"] == 150_000
        assert h["per_masa"][b]["bruto"] == dasar["per_masa"][b]["bruto"]
        assert h["per_masa"][b]["pph21"] == dasar["per_masa"][b]["pph21"]
    assert h["tahunan"]["pph21_setahun"] == dasar["tahunan"]["pph21_setahun"]


def test_kategori_klasifikasi_salah_ketik_ditolak(tmp_path):
    p = _tulis(tmp_path, "k.yaml", KLASIFIKASI_JKN.replace("kategori: iuran_pengurang", "kategori: tidak teratur"))
    with pytest.raises(KesalahanKB, match="klasifikasi_wajib/0/kategori"):
        muat_kb([p])


def test_enum_kategori_skema_sama_dengan_engine():
    skema = json.loads((ROOT / "kb" / "skema" / "aturan.schema.json").read_text(encoding="utf-8"))
    for bagian in ("komponen", "klasifikasi_wajib"):
        assert tuple(skema["properties"][bagian]["items"]["properties"]["kategori"]["enum"]) == KATEGORI_KOMPONEN


# ------------------------------------------------------------------------------------------- E5 ekspresi

class _Konteks:
    def __init__(self, **nilai):
        self._nilai = nilai

    def nilai(self, nama):
        return self._nilai[nama]


@pytest.mark.parametrize("operand", ["10", ("a", "b"), [1], date(2026, 1, 1)])
def test_aritmetika_hanya_untuk_int_dan_pecahan(operand):
    for teks in ("x * 3", "3 + x", "x - 1", "x / 2", "-x"):
        with pytest.raises(PelanggaranPresisi, match="operand aritmetika tidak valid"):
            Ekspresi(teks, FUNGSI).evaluasi(_Konteks(x=operand))


def test_teks_di_aritmetika_menyarankan_konversi():
    # dulu "10" * 3 = "101010" (pengulangan string) dan diam-diam menghasilkan nominal absurd
    with pytest.raises(PelanggaranPresisi, match=r"persen\(\.\.\.\), desimal\(\.\.\.\) atau tanggal\(\.\.\.\)"):
        Ekspresi("x * 3", FUNGSI).evaluasi(_Konteks(x="10"))


def test_aritmetika_sah_dan_perbandingan_teks_tetap_jalan():
    k = _Konteks(x=Fraction(1, 3), s="K/1", n=7)
    assert Ekspresi("x * 3 + n - -1", FUNGSI).evaluasi(k) == 9
    assert Ekspresi("s == 'K/1' and s != 'TK/0' and s in ('K/1', 'K/2')", FUNGSI).evaluasi(k) is True


def test_masukan_persen_tanpa_persen_ditolak_saat_hitung(tmp_path):
    isi = """
lapisan: perusahaan
komponen:
  - {fakta: px_bonus_uji, jenis: bonus, kategori: tidak_teratur}
masukan:
  - {kunci: bonus_persen, label: "Bonus (persen gaji)", tipe: persen, lingkup: tahun, wajib: false, bawaan: "10"}
aturan:
  - {id: UJI-BONUS-01, sifat: opsional, berlaku: {mulai: 2016-01-01}, lingkup: masa, menghasilkan: px_bonus_uji,
     maka: "hr('bonus_persen') * hr('gaji_pokok')", tipe_hasil: rupiah, sumber: "uji"}
"""
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "bonus.yaml", isi)])
    with pytest.raises(PelanggaranPresisi, match=r"'10' \(str\).*persen\("):
        hitung(kasus_kar_a(2024), kb=kb)


EKSPRESI_DALAM = {   # RecursionError di validasi / di konstruksi AST, MemoryError "parser stack overflow"
    "jumlah_20000": "1" + "+1" * 20000, "minus_200000": "-" * 200000 + "1",
    "if_5000": "1 if 1 else " * 5000 + "1",
}


@pytest.mark.parametrize("nama", sorted(EKSPRESI_DALAM))
def test_ekspresi_terlalu_dalam_ditolak_saat_parse(nama):
    with pytest.raises(KesalahanEkspresi, match="ekspresi terlalu panjang atau terlalu dalam"):
        Ekspresi(EKSPRESI_DALAM[nama], FUNGSI)


def test_ekspresi_terlalu_dalam_ditolak_saat_evaluasi():
    e = Ekspresi("1" + "+1" * 400, FUNGSI)
    kedalaman, f = 0, sys._getframe()
    while f is not None:
        kedalaman, f = kedalaman + 1, f.f_back
    lama = sys.getrecursionlimit()
    sys.setrecursionlimit(kedalaman + 100)
    try:
        with pytest.raises(KesalahanEkspresi, match="ekspresi terlalu panjang atau terlalu dalam"):
            e.evaluasi(_Konteks())
    finally:
        sys.setrecursionlimit(lama)


ATURAN_ARGUMEN = """
lapisan: perusahaan
aturan:
  - {id: UJI-ARG-01, sifat: opsional, berlaku: {mulai: 2016-01-01}, lingkup: masa, menghasilkan: _uji_arg,
     maka: "MAKA", tipe_hasil: bilangan, sumber: "uji"}
"""


@pytest.mark.parametrize("maka, pesan", [
    ("komponen('teratur_x')", r"komponen\('teratur_x'\): kategori komponen tidak dikenal"),
    ("komponen('tidak teratur', 'bulan')", "kategori komponen tidak dikenal"),
    ("komponen_kode('iuran', 'jht')", r"komponen_kode\('iuran'\): kategori komponen tidak dikenal"),
    ("komponen_valas('valas')", "kategori komponen tidak dikenal"),
    ("parameter('jkm_persen')", r"parameter\('jkm_persen'\) tidak dikenal"),
    ("bulatkan('BULAT-TIDAK-ADA', 10)", r"bulatkan\('BULAT-TIDAK-ADA', \.\.\.\): entri pembulatan tidak terdaftar"),
    ("hr()", r"hr\(\) menerima 1 argumen, diberi 0"),
    ("bulatkan('BULAT-PKP-01')", r"bulatkan\(\) menerima 2 argumen, diberi 1"),
    ("hr_masa('a', 0, 1)", r"hr_masa\(\) menerima 1\.\.2 argumen, diberi 3"),
    ("min()", r"min\(\) menerima minimal 1 argumen"),
])
def test_argumen_fungsi_yang_pasti_salah_ditolak_saat_muat(tmp_path, maka, pesan):
    p = _tulis(tmp_path, "arg.yaml", ATURAN_ARGUMEN.replace("MAKA", maka.replace('"', "'")))
    with pytest.raises(KesalahanKB, match=pesan):
        muat_kb([*BERKAS_PX, p])


@pytest.mark.parametrize("maka", ["komponen('rapel', 'bulan')", "komponen('tidak_diperhitungkan')", "parameter('jkm_pk_persen') * 0",
                                  "bulatkan('BULAT-PKP-01', 10)", "min(1, 2, 3) + max(4)", "komponen_kode('iuran_pengurang', 'apa_saja')"])
def test_argumen_sah_tetap_diterima(tmp_path, maka):
    muat_kb([*BERKAS_PX, _tulis(tmp_path, "arg.yaml", ATURAN_ARGUMEN.replace("MAKA", maka))])


# ------------------------------------------------------------------------------------------- E6 alias YAML

@pytest.mark.parametrize("isi", [
    "a: &x [1, 2]\nb: *x\n",
    "a: &x 1\nb: 2\n",
    "a: &a [\"lol\",\"lol\",\"lol\",\"lol\",\"lol\",\"lol\",\"lol\",\"lol\",\"lol\"]\nb: &b [*a,*a,*a,*a,*a,*a,*a,*a,*a]\n"
    "c: &c [*b,*b,*b,*b,*b,*b,*b,*b,*b]\nd: &d [*c,*c,*c,*c,*c,*c,*c,*c,*c]\ne: [*d,*d,*d,*d,*d,*d,*d,*d,*d]\n",
])
def test_alias_dan_anchor_yaml_ditolak(tmp_path, isi):
    with pytest.raises(KesalahanKB, match="alias/anchor YAML tidak diizinkan"):
        muat_yaml(_tulis(tmp_path, "alias.yaml", isi))


def test_berkas_tambahan_dengan_alias_ditolak_saat_muat_kb(tmp_path):
    isi = _komponen_baru("px_transport", "teratur", "tunjangan_transport", "transport", "UJI-TRA-01").replace(
        "berlaku: {mulai: 2016-01-01}", "berlaku: &b {mulai: 2016-01-01}")
    with pytest.raises(KesalahanKB, match="alias/anchor YAML tidak diizinkan"):
        muat_kb([*BERKAS_PX, _tulis(tmp_path, "t.yaml", isi)])


# ------------------------------------------------------------------------------------------- E7 batas titik tetap

TITIK_TETAP_2026 = """
lapisan: regulasi
aturan:
  - id: UJI-TT-01
    sifat: wajib
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: tunjangan_pajak_berjalan
    jika: "gross_up and not masa_terakhir"
    maka: "tunjangan_pajak_berjalan"
    tipe_hasil: rupiah
    titik_tetap: true
    batas_titik_tetap: {bawah: "1000", atas: "2000"}
    sumber: "uji batas titik tetap"
"""


def _kasus_gross_up(tahun):
    kasus = kasus_kar_a(tahun)
    kasus["metode"] = "gross_up"
    return kasus


def test_batas_titik_tetap_diambil_dari_aturan_pemenang(tmp_path):
    # UJI-TT-01 mengalahkan R24-05a mulai 2026 (jika sama, mulai lebih baru: lex posterior). maka-nya mengembalikan fakta
    # itu sendiri, jadi setiap nilai adalah titik tetap: solusi terkecil & terbesar = batas yang dipakai iterasi.
    # Dulu batasnya tetap milik R24-05a (0 .. _bruto_dasar) walaupun nilainya dihitung UJI-TT-01.
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "tt.yaml", TITIK_TETAP_2026)])
    h = hitung(_kasus_gross_up(2026), kb=kb)
    ganda = {p["bulan"]: (p["terkecil"], p["terbesar"]) for p in h["peringatan"]
             if p["kode"] == "GROSSUP_GANDA" and p["fakta"] == "tunjangan_pajak_berjalan"}
    assert ganda == {b: (1000, 2000) for b in range(1, 12)}
    assert [h["per_masa"][b]["tunjangan_pajak_berjalan"] for b in range(1, 12)] == [1000] * 11
    assert {j["aturan"] for j in h["jejak"] if j["fakta"] == "tunjangan_pajak_berjalan"} == {"UJI-TT-01"}
    # sebelum aturan baru berlaku, hasilnya sama persis dengan KB dasar
    assert hitung(_kasus_gross_up(2025), kb=kb) == hitung(_kasus_gross_up(2025), berkas_perusahaan=BERKAS_PX)


def test_pemilik_batas_titik_tetap_ditentukan_tanpa_efek_samping(tmp_path, monkeypatch):
    # aturan perusahaan untuk fakta gross-up kalah lex superior; peringatan KONFLIK_WAJIB-nya ditulis saat nilai
    # dihitung, bukan saat pemilik batas ditentukan (yang juga tidak boleh mengevaluasi `maka`)
    isi = """
lapisan: perusahaan
aturan:
  - {id: UJI-TT-PRSH, sifat: opsional, berlaku: {mulai: 2016-01-01}, lingkup: masa, menghasilkan: tunjangan_pajak_berjalan,
     maka: "0", tipe_hasil: rupiah, sumber: "uji"}
"""
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "prsh.yaml", isi)])
    ev = Evaluasi(kb, _kasus_gross_up(2026)).jalankan()
    assert any(p["kode"] == "KONFLIK_WAJIB" and p.get("ditolak") == ["UJI-TT-PRSH"] for p in ev.peringatan)
    n_peringatan = len(ev.peringatan)
    monkeypatch.setattr(ev, "_nilai_aturan", lambda a, b: pytest.fail(f"maka {a.id} dievaluasi"))
    assert ev._aturan_titik("tunjangan_pajak_berjalan", 1).id == "R24-05a"
    assert ev._aturan_titik("tunjangan_pajak_berjalan", 12) is None   # hanya aturan perusahaan (bukan titik_tetap) menyala
    assert len(ev.peringatan) == n_peringatan
    # ablasi A3: perusahaan selalu menang, sama seperti saat nilai dihitung -> pemenang bukan titik_tetap, tanpa batas
    a3 = Evaluasi(kb, _kasus_gross_up(2026), ablasi=("A3_tanpa_resolusi_konflik",)).jalankan()
    assert a3._aturan_titik("tunjangan_pajak_berjalan", 1) is None
    assert a3.hasil()["per_masa"][1]["tunjangan_pajak_berjalan"] == 0


@pytest.mark.parametrize("lapisan, sifat", [("perusahaan", "opsional"), ("regulasi", "wajib")])
def test_jika_yang_membaca_anggota_siklus_tidak_dinilai_saat_menentukan_batas(tmp_path, lapisan, sifat):
    # pph21_berjalan ada di dalam siklus gross-up dan belum bernilai (None) sebelum iterasi dimulai; `jika` ini dulu
    # ikut dinilai saat pemilik batas ditentukan -> TypeError. Aturannya tidak pernah menyala, jadi hasil = KB dasar.
    isi = f"""
lapisan: {lapisan}
aturan:
  - id: UJI-BATAS
    sifat: {sifat}
    berlaku: {{mulai: 2024-01-01}}
    lingkup: masa
    menghasilkan: tunjangan_pajak_berjalan
    jika: "gross_up and not masa_terakhir and pph21_berjalan > 100000000"
    maka: "100000000"
    tipe_hasil: rupiah
    sumber: "uji batas tunjangan pajak"
"""
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "batas.yaml", isi)])
    for tahun in (2024, 2026):
        assert hitung(_kasus_gross_up(tahun), kb=kb) == hitung(_kasus_gross_up(tahun), berkas_perusahaan=BERKAS_PX)


def test_pengganti_aturan_titik_tetap_tanpa_tanda_titik_tetap_ditolak_dengan_pesan_jelas(tmp_path):
    # UJI-GANTI menang atas R24-05a (lex posterior) dan maka-nya tetap bersiklus, tetapi tanpa titik_tetap tidak ada
    # batas iterasi. Dulu pesannya "tidak monoton", padahal fungsinya monoton: yang kurang adalah tanda dan batasnya.
    isi = """
lapisan: regulasi
aturan:
  - id: UJI-GANTI
    sifat: wajib
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: tunjangan_pajak_berjalan
    jika: "gross_up and not masa_terakhir"
    maka: "pph21_berjalan"
    tipe_hasil: rupiah
    sumber: "uji pengganti R24-05a tanpa titik_tetap"
"""
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "ganti.yaml", isi)])
    with pytest.raises(KesalahanKB, match=r"UJI-GANTI menggantikan R24-05a pada fakta titik tetap tunjangan_pajak_berjalan\[1\]"
                                          r" tetapi tidak bertanda titik_tetap/batas_titik_tetap"):
        hitung(_kasus_gross_up(2026), kb=kb)
    # sebelum aturan pengganti berlaku, dan untuk metode selain gross-up, tidak ada yang berubah
    assert hitung(_kasus_gross_up(2025), kb=kb) == hitung(_kasus_gross_up(2025), berkas_perusahaan=BERKAS_PX)
    assert hitung(kasus_kar_a(2026), kb=kb) == hitung(kasus_kar_a(2026), berkas_perusahaan=BERKAS_PX)


# ------------------------------------------------------------------------------------------- E8 parameter perusahaan

TRANSPORT_PARAMETER = """
lapisan: perusahaan
komponen:
  - {fakta: px_transport, jenis: tunjangan_transport, kategori: teratur}
parameter:
  - {nama: px_transport_per_hari, nilai: 50000, berlaku: {mulai: 2016-01-01}, sumber: "Peraturan Perusahaan Ps. 12"}
aturan:
  - id: UJI-TRA-01
    sifat: opsional
    berlaku: {mulai: 2016-01-01}
    lingkup: masa
    menghasilkan: px_transport
    maka: "parameter('px_transport_per_hari') * hr_masa('hk_aktual')"
    tipe_hasil: rupiah
    sumber: "uji parameter perusahaan"
"""


def _hadir(kasus, bulan):
    return kasus["data_hr"]["per_masa"][str(bulan)]["hk_aktual"]


def test_parameter_perusahaan_dipakai_aturan_komponen(tmp_path):
    # nilai yang sama untuk seluruh perusahaan = parameter perusahaan, bukan masukan per pegawai
    kasus = kasus_kar_a(2024)
    h = hitung(kasus, kb=muat_kb([*BERKAS_PX, _tulis(tmp_path, "transport.yaml", TRANSPORT_PARAMETER)]))
    for b in range(1, 13):
        assert h["per_masa"][b]["px_transport"] == 50_000 * _hadir(kasus, b) > 0


def test_amandemen_parameter_perusahaan_berlaku_mulai_tanggalnya_di_kedua_urutan_muat(tmp_path):
    a = _tulis(tmp_path, "transport.yaml", TRANSPORT_PARAMETER)
    b = _tulis(tmp_path, "transport_juli.yaml", _parameter("perusahaan", "px_transport_per_hari", 60000, "2024-07-01"))
    kasus = kasus_kar_a(2024)
    for urutan in ([a, b], [b, a]):
        h = hitung(kasus, kb=muat_kb([*BERKAS_PX, *urutan]))
        for bulan in range(1, 13):
            per_hari = 50_000 if bulan < 7 else 60_000
            assert h["per_masa"][bulan]["px_transport"] == per_hari * _hadir(kasus, bulan)


def test_berkas_yang_hanya_berisi_parameter_tetap_menulis_aturan_kosong(tmp_path):
    isi = _parameter("perusahaan", "px_transport_per_hari", 50000, "2016-01-01")
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "p.yaml", isi)])
    assert parameter_pada(kb, "px_transport_per_hari", date(2024, 1, 1)) == 50_000
    # skema mewajibkan kunci `aturan` walaupun berkas tidak membawa aturan
    assert "aturan: []\n" in isi
    with pytest.raises(KesalahanKB, match="'aturan' is a required property"):
        muat_kb([*BERKAS_PX, _tulis(tmp_path, "tanpa_aturan.yaml", isi.replace("aturan: []\n", ""))])
