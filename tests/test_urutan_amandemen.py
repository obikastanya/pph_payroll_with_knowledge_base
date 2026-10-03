"""Amandemen parameter & klasifikasi wajib tidak bergantung urutan berkas dimuat (research_plan.md §6.4).

Yang menentukan adalah masa berlaku tiap entri, bukan urutan penerapannya: muat_kb mengumpulkan entri semua berkas,
lalu menerapkannya per nama parameter / per jenis menurut tanggal mulai. Setiap permutasi berkas_tambahan memberi
kb.parameter dan kb.klasifikasi yang sama, atau semuanya ditolak. Versi KB dasar (kb/regulasi) tetap versi yang
sudah ada: amandemen yang rentangnya memuat tanggal mulai versi dasar ditolak, tidak ditebak.
"""
import itertools
from datetime import date
from fractions import Fraction

import pytest

from engine.kb import muat_kb, parameter_pada
from engine.muat import KesalahanKB

JKM = "jkm_pk_persen"       # KB dasar: "0.3" mulai 2015-07-01, tanpa batas akhir
JP = "jp_batas_upah"        # KB dasar: lima versi; 10.547.400 (2025-03-01..2026-02-28) lalu 11.086.300 mulai 2026-03-01
JKN = "iuran_jkn_pegawai"   # KB dasar: tidak_diperhitungkan mulai 2016-01-01, tanpa batas akhir


def _berlaku(mulai, sampai):
    return f"{{mulai: {mulai}" + (f", sampai: {sampai}}}" if sampai else "}")


def _berkas(tmp_path, nama, lapisan="regulasi", parameter=(), klasifikasi=()):
    """parameter: [(nama, nilai, mulai, sampai)]; klasifikasi: [(jenis, kategori, mulai, sampai)]."""
    baris = [f"lapisan: {lapisan}", "aturan: []"]
    if parameter:
        baris.append("parameter:")
        baris += [f'  - {{nama: {n}, nilai: {v}, berlaku: {_berlaku(m, s)}, sumber: "uji {nama}"}}' for n, v, m, s in parameter]
    if klasifikasi:
        baris.append("klasifikasi_wajib:")
        baris += [f'  - {{jenis: {j}, kategori: {k}, berlaku: {_berlaku(m, s)}, sumber: "uji {nama}"}}'
                  for j, k, m, s in klasifikasi]
    p = tmp_path / nama
    p.write_text("\n".join(baris) + "\n", encoding="utf-8")
    return p


def _setiap_urutan(berkas):
    """Hasil muat_kb untuk setiap permutasi berkas: KnowledgeBase atau KesalahanKB."""
    hasil = []
    for urutan in itertools.permutations(berkas):
        try:
            hasil.append(muat_kb(list(urutan)))
        except KesalahanKB as e:
            hasil.append(e)
    return hasil


def _kb_di_setiap_urutan(berkas):
    """KB yang sama dari setiap permutasi (gagal bila ada permutasi yang ditolak atau hasilnya berbeda)."""
    hasil = _setiap_urutan(berkas)
    for h in hasil:
        assert not isinstance(h, KesalahanKB), h
        assert h.parameter == hasil[0].parameter and list(h.parameter) == list(hasil[0].parameter)
        assert h.klasifikasi == hasil[0].klasifikasi
    return hasil[0]


def _galat_di_setiap_urutan(berkas, cocok):
    """Pesan galat tiap permutasi (gagal bila ada permutasi yang termuat atau pesannya tidak memuat pola)."""
    hasil = _setiap_urutan(berkas)
    for h in hasil:
        assert isinstance(h, KesalahanKB), "termuat di salah satu urutan"
        assert cocok in str(h), h
    return [str(h) for h in hasil]


def _versi(kb, nama):
    return [v[:3] for v in kb.parameter[nama]]


def _klasifikasi(kb, jenis):
    return [(w.kategori, w.mulai, w.sampai) for w in kb.klasifikasi if w.jenis == jenis]


# ------------------------------------------------------------------------------------------- semua permutasi

HIMPUNAN = {
    # nama himpunan: (termuat?, {berkas: (lapisan, parameter, klasifikasi)})
    "tiga_versi_permanen": (True, {
        "a.yaml": ("regulasi", [(JKM, '"0.1"', "2025-01-01", None)], []),
        "b.yaml": ("regulasi", [(JKM, '"0.2"', "2025-07-01", None)], []),
        "c.yaml": ("regulasi", [(JKM, '"0.4"', "2026-01-01", None)], [])}),
    "sementara_bersarang_lalu_penerus": (True, {
        "a.yaml": ("regulasi", [(JKM, '"0.1"', "2025-01-01", "2025-12-31")], []),
        "b.yaml": ("regulasi", [(JKM, '"0.2"', "2025-04-01", "2025-06-30")], []),
        "c.yaml": ("regulasi", [(JKM, '"0.4"', "2026-01-01", None)], [])}),
    "rupiah_di_antara_versi_dasar": (True, {
        "a.yaml": ("regulasi", [(JP, 12000000, "2025-07-01", "2025-09-30")], []),
        "b.yaml": ("regulasi", [(JP, 12500000, "2026-06-01", None)], [])}),
    "parameter_dan_klasifikasi_bersilang": (True, {
        "a.yaml": ("regulasi", [("uji_x", 100, "2025-01-01", None)], [(JKN, "iuran_pengurang", "2027-01-01", None)]),
        "b.yaml": ("regulasi", [("uji_x", 200, "2026-01-01", None)], [(JKN, "bukan_objek", "2026-01-01", None)]),
        "c.yaml": ("perusahaan", [("px_uji", 300, "2024-01-01", "2024-12-31")], [])}),
    "jenis_baru_dari_dua_berkas": (True, {
        "a.yaml": ("regulasi", [], [("uji_jenis_b", "teratur", "2026-01-01", None)]),
        "b.yaml": ("regulasi", [], [("uji_jenis_a", "natura", "2025-01-01", None),
                                    ("uji_jenis_b", "tidak_teratur", "2027-01-01", None)])}),
    "mulai_sama": (False, {
        "a.yaml": ("regulasi", [(JKM, '"0.1"', "2025-01-01", None)], []),
        "b.yaml": ("regulasi", [(JKM, '"0.2"', "2025-01-01", "2025-06-30")], []),
        "c.yaml": ("regulasi", [(JKM, '"0.4"', "2026-01-01", None)], [])}),
    "permanen_di_dalam_jendela_sementara": (False, {
        "a.yaml": ("regulasi", [(JKM, '"0.1"', "2025-01-01", "2025-06-30")], []),
        "b.yaml": ("regulasi", [(JKM, '"0.2"', "2025-04-01", None)], []),
        "c.yaml": ("regulasi", [(JKM, '"0.4"', "2027-01-01", None)], [])}),
    "sementara_bersilang": (False, {
        "a.yaml": ("regulasi", [(JKM, '"0.1"', "2025-01-01", "2025-06-30")], []),
        "b.yaml": ("regulasi", [(JKM, '"0.2"', "2025-04-01", "2025-09-30")], [])}),
    "mendahului_versi_dasar": (False, {
        "a.yaml": ("regulasi", [(JKM, '"0.1"', "2014-01-01", None)], []),
        "b.yaml": ("regulasi", [(JKM, '"0.2"', "2026-01-01", None)], [])}),
    "perusahaan_mengubah_parameter_regulasi": (False, {
        "a.yaml": ("perusahaan", [("uji_batas", 2000, "2027-01-01", None)], []),
        "b.yaml": ("regulasi", [("uji_batas", 1000, "2026-01-01", None)], []),
        "c.yaml": ("perusahaan", [("px_uji", 300, "2024-01-01", None)], [])}),
}


@pytest.mark.parametrize("nama", sorted(HIMPUNAN))
def test_setiap_permutasi_memberi_kb_yang_sama_atau_semuanya_ditolak(tmp_path, nama):
    termuat, isi = HIMPUNAN[nama]
    berkas = [_berkas(tmp_path, n, *b) for n, b in isi.items()]
    if not termuat:
        hasil = _setiap_urutan(berkas)
        assert len(hasil) in (2, 6) and [isinstance(h, KesalahanKB) for h in hasil] == [True] * len(hasil)
        return
    kb = _kb_di_setiap_urutan(berkas)
    diamandemen = {p[0] for _, parameter, _ in isi.values() for p in parameter}
    for n, versi in muat_kb().parameter.items():   # parameter yang tidak diamandemen tidak tersentuh
        if n not in diamandemen:
            assert kb.parameter[n] == versi


def test_potongan_sementara_bersarang_tersusun_menurut_masa_berlaku(tmp_path):
    _, isi = HIMPUNAN["sementara_bersarang_lalu_penerus"]
    kb = _kb_di_setiap_urutan([_berkas(tmp_path, n, *b) for n, b in isi.items()])
    assert _versi(kb, JKM) == [
        (date(2015, 7, 1), date(2024, 12, 31), Fraction(3, 10)), (date(2025, 1, 1), date(2025, 3, 31), Fraction(1, 10)),
        (date(2025, 4, 1), date(2025, 6, 30), Fraction(2, 10)), (date(2025, 7, 1), date(2025, 12, 31), Fraction(1, 10)),
        (date(2026, 1, 1), None, Fraction(4, 10))]
    assert "berlaku lagi setelah 2025-06-30" in kb.parameter[JKM][3][3]


# ------------------------------------------------------------------------------------------- parameter

def test_dua_versi_permanen_termuat_di_kedua_urutan(tmp_path):
    # dulu urutan (b, a) ditolak: versi a "mendahului" versi b yang sudah diterapkan
    a = _berkas(tmp_path, "a.yaml", parameter=[(JKM, '"0.1"', "2025-01-01", None)])
    b = _berkas(tmp_path, "b.yaml", parameter=[(JKM, '"0.2"', "2025-07-01", None)])
    kb = _kb_di_setiap_urutan([a, b])
    for tgl, nilai in ((date(2024, 12, 31), Fraction(3, 10)), (date(2025, 1, 1), Fraction(1, 10)),
                       (date(2025, 6, 30), Fraction(1, 10)), (date(2025, 7, 1), Fraction(2, 10)),
                       (date(2030, 1, 1), Fraction(2, 10))):
        assert parameter_pada(kb, JKM, tgl) == nilai


def test_amandemen_bersilang_antara_dua_berkas_termuat(tmp_path):
    # dulu tidak termuat di urutan mana pun: x menuntut p sebelum q, y menuntut q sebelum p
    p = _berkas(tmp_path, "p.yaml", parameter=[("uji_x", 100, "2025-01-01", None), ("uji_y", 10, "2027-01-01", None)])
    q = _berkas(tmp_path, "q.yaml", parameter=[("uji_x", 200, "2026-01-01", None), ("uji_y", 20, "2026-01-01", None)])
    kb = _kb_di_setiap_urutan([p, q])
    assert _versi(kb, "uji_x") == [(date(2025, 1, 1), date(2025, 12, 31), 100), (date(2026, 1, 1), None, 200)]
    assert _versi(kb, "uji_y") == [(date(2026, 1, 1), date(2026, 12, 31), 20), (date(2027, 1, 1), None, 10)]


def test_amandemen_sementara_disusul_versi_baru_termuat_di_kedua_urutan(tmp_path):
    # dulu urutan kronologis ditolak: potongan "berlaku lagi" 2025-04-01 buatan pemuat dianggap versi tulisan berkas
    sementara = _berkas(tmp_path, "sementara.yaml", parameter=[(JKM, '"0.1"', "2025-01-01", "2025-03-31")])
    baru = _berkas(tmp_path, "baru.yaml", parameter=[(JKM, '"0.2"', "2025-04-01", None)])
    kb = _kb_di_setiap_urutan([sementara, baru])
    assert _versi(kb, JKM) == [(date(2015, 7, 1), date(2024, 12, 31), Fraction(3, 10)),
                               (date(2025, 1, 1), date(2025, 3, 31), Fraction(1, 10)), (date(2025, 4, 1), None, Fraction(2, 10))]
    assert not any("berlaku lagi" in v[3] for v in kb.parameter[JKM])


def test_dua_amandemen_sementara_berurutan_mengembalikan_nilai_lama_sesudahnya(tmp_path):
    a = _berkas(tmp_path, "a.yaml", parameter=[(JKM, '"0.1"', "2025-01-01", "2025-03-31")])
    b = _berkas(tmp_path, "b.yaml", parameter=[(JKM, '"0.2"', "2025-04-01", "2025-06-30")])
    kb = _kb_di_setiap_urutan([a, b])
    assert _versi(kb, JKM)[1:] == [(date(2025, 1, 1), date(2025, 3, 31), Fraction(1, 10)),
                                   (date(2025, 4, 1), date(2025, 6, 30), Fraction(2, 10)), (date(2025, 7, 1), None, Fraction(3, 10))]
    sumber = kb.parameter[JKM][-1][3]
    assert "berlaku lagi setelah 2025-06-30" in sumber and "2025-03-31" not in sumber


def test_mulai_sama_ditolak_dan_pesan_menyebut_kedua_berkas(tmp_path):
    a = _berkas(tmp_path, "a.yaml", parameter=[(JKM, '"0.1"', "2025-01-01", None)])
    b = _berkas(tmp_path, "b.yaml", parameter=[(JKM, '"0.2"', "2025-01-01", "2025-06-30")])
    pesan = _galat_di_setiap_urutan([a, b], "bentrok dengan versi yang berlaku mulai 2025-01-01")
    # berkas yang dimuat belakangan yang ditolak; berkas lawannya disebut di dalam kurung
    assert pesan == ["b.yaml: parameter jkm_pk_persen mulai 2025-01-01 bentrok dengan versi yang berlaku mulai 2025-01-01 (a.yaml)",
                     "a.yaml: parameter jkm_pk_persen mulai 2025-01-01 bentrok dengan versi yang berlaku mulai 2025-01-01 (b.yaml)"]
    ganda = _berkas(tmp_path, "ganda.yaml", parameter=[("uji_x", 100, "2025-01-01", None), ("uji_x", 200, "2025-01-01", None)])
    with pytest.raises(KesalahanKB, match=r"ganda\.yaml: parameter uji_x mulai 2025-01-01 bentrok .* \(ganda\.yaml\)"):
        muat_kb([ganda])


def test_amandemen_permanen_di_dalam_jendela_sementara_ditolak_di_kedua_urutan(tmp_path):
    # sesudah 2025-06-30 nilai lama berlaku lagi atau versi permanen berlanjut? tidak ditebak
    sementara = _berkas(tmp_path, "sementara.yaml", parameter=[(JKM, '"0.1"', "2025-01-01", "2025-06-30")])
    permanen = _berkas(tmp_path, "permanen.yaml", parameter=[(JKM, '"0.2"', "2025-04-01", None)])
    pesan = _galat_di_setiap_urutan([sementara, permanen], "permanen.yaml: parameter jkm_pk_persen mulai 2025-04-01 bentrok")
    assert set(pesan) == {"permanen.yaml: parameter jkm_pk_persen mulai 2025-04-01 bentrok dengan versi yang berlaku mulai "
                          "2025-07-01 (parameter.yaml, berlaku lagi setelah amandemen sementara sementara.yaml)"}


def test_versi_permanen_di_tengah_amandemen_sementara_parameter_baru_menutupnya_lebih_awal(tmp_path):
    # parameter tanpa versi lama: tidak ada yang "berlaku lagi" sesudah amandemen sementara, jadi tidak ada yang ditebak
    sementara = _berkas(tmp_path, "sementara.yaml", parameter=[("uji_baru", 100, "2025-01-01", "2025-06-30")])
    permanen = _berkas(tmp_path, "permanen.yaml", parameter=[("uji_baru", 200, "2025-04-01", None)])
    kb = _kb_di_setiap_urutan([sementara, permanen])
    assert _versi(kb, "uji_baru") == [(date(2025, 1, 1), date(2025, 3, 31), 100), (date(2025, 4, 1), None, 200)]


def test_urutan_kunci_parameter_baru_tidak_bergantung_urutan_berkas(tmp_path):
    reg = _berkas(tmp_path, "reg.yaml", parameter=[("uji_reg", 100, "2026-01-01", None)])
    prsh = _berkas(tmp_path, "prsh.yaml", lapisan="perusahaan", parameter=[("px_baru", 200, "2025-01-01", None)])
    kb = _kb_di_setiap_urutan([reg, prsh])
    assert list(kb.parameter)[-2:] == ["px_baru", "uji_reg"]   # parameter baru menurut abjad, sesudah parameter dasar


def test_amandemen_yang_memuat_mulai_versi_dasar_tetap_bentrok(tmp_path):
    lain = _berkas(tmp_path, "lain.yaml", parameter=[(JKM, '"0.2"', "2027-01-01", None)])
    surut = _berkas(tmp_path, "surut.yaml", parameter=[(JKM, '"0.1"', "2014-01-01", None)])
    _galat_di_setiap_urutan([surut, lain], "surut.yaml: parameter jkm_pk_persen mulai 2014-01-01 bentrok dengan versi yang "
                                           "berlaku mulai 2015-07-01 (parameter.yaml)")
    jendela = _berkas(tmp_path, "jendela.yaml", parameter=[(JP, 12000000, "2026-01-01", "2026-06-30")])
    _galat_di_setiap_urutan([jendela, lain], "jendela.yaml: parameter jp_batas_upah mulai 2026-01-01 bentrok dengan versi "
                                             "yang berlaku mulai 2026-03-01 (parameter.yaml)")
    # jendela surut yang berakhir sebelum versi dasar pertama tidak bentrok
    awal = _berkas(tmp_path, "awal.yaml", parameter=[(JKM, '"0.1"', "2014-01-01", "2015-06-30")])
    kb = _kb_di_setiap_urutan([awal, lain])
    assert parameter_pada(kb, JKM, date(2014, 6, 1)) == Fraction(1, 10)
    assert parameter_pada(kb, JKM, date(2015, 7, 1)) == Fraction(3, 10)


def test_perusahaan_tidak_boleh_mengubah_parameter_regulasi_di_urutan_mana_pun(tmp_path):
    # termasuk bila berkas regulasi tambahan dimuat SESUDAH berkas perusahaan (dulu urutan itu lolos)
    reg = _berkas(tmp_path, "reg.yaml", parameter=[("uji_batas", 1000, "2026-01-01", None)])
    prsh = _berkas(tmp_path, "prsh.yaml", "perusahaan", parameter=[("uji_batas", 2000, "2025-01-01", None)])
    pesan = _galat_di_setiap_urutan([prsh, reg], "lapisan perusahaan tidak boleh mengubahnya")
    assert set(pesan) == {"prsh.yaml: parameter uji_batas milik lapisan regulasi (reg.yaml); lapisan perusahaan tidak boleh "
                          "mengubahnya"}
    dasar = _berkas(tmp_path, "dasar.yaml", "perusahaan", parameter=[(JKM, '"0.1"', "2026-01-01", None)])
    with pytest.raises(KesalahanKB, match=r"dasar\.yaml: parameter jkm_pk_persen milik lapisan regulasi \(parameter\.yaml\); "
                                          r"lapisan perusahaan tidak boleh mengubahnya"):
        muat_kb([dasar])


def test_parameter_buatan_perusahaan_boleh_diamandemen_perusahaan_di_kedua_urutan(tmp_path):
    a = _berkas(tmp_path, "a.yaml", "perusahaan", parameter=[("px_uang_makan_harian", 25000, "2024-01-01", None)])
    b = _berkas(tmp_path, "b.yaml", "perusahaan", parameter=[("px_uang_makan_harian", 30000, "2025-01-01", None)])
    kb = _kb_di_setiap_urutan([a, b])
    assert _versi(kb, "px_uang_makan_harian") == [(date(2024, 1, 1), date(2024, 12, 31), 25_000), (date(2025, 1, 1), None, 30_000)]


# ------------------------------------------------------------------------------------------- klasifikasi wajib

def test_klasifikasi_wajib_dari_dua_berkas_tidak_bergantung_urutan(tmp_path):
    a = _berkas(tmp_path, "a.yaml", klasifikasi=[(JKN, "iuran_pengurang", "2026-01-01", None)])
    b = _berkas(tmp_path, "b.yaml", klasifikasi=[(JKN, "bukan_objek", "2027-01-01", None)])
    kb = _kb_di_setiap_urutan([a, b])
    assert _klasifikasi(kb, JKN) == [("tidak_diperhitungkan", date(2016, 1, 1), date(2025, 12, 31)),
                                     ("iuran_pengurang", date(2026, 1, 1), date(2026, 12, 31)),
                                     ("bukan_objek", date(2027, 1, 1), None)]
    # jenis lain tidak tersentuh dan tetap pada urutan KB dasar
    dasar = muat_kb()
    assert [w for w in kb.klasifikasi if w.jenis != JKN] == [w for w in dasar.klasifikasi if w.jenis != JKN]
    assert list(dict.fromkeys(w.jenis for w in kb.klasifikasi)) == [w.jenis for w in dasar.klasifikasi]


def test_klasifikasi_sementara_disusul_entri_baru_termuat_di_kedua_urutan(tmp_path):
    sementara = _berkas(tmp_path, "sementara.yaml", klasifikasi=[(JKN, "iuran_pengurang", "2026-01-01", "2026-06-30")])
    baru = _berkas(tmp_path, "baru.yaml", klasifikasi=[(JKN, "bukan_objek", "2026-07-01", None)])
    kb = _kb_di_setiap_urutan([sementara, baru])
    assert _klasifikasi(kb, JKN) == [("tidak_diperhitungkan", date(2016, 1, 1), date(2025, 12, 31)),
                                     ("iuran_pengurang", date(2026, 1, 1), date(2026, 6, 30)),
                                     ("bukan_objek", date(2026, 7, 1), None)]


def test_klasifikasi_bentrok_ditolak_di_kedua_urutan_dan_menyebut_berkas_lawan(tmp_path):
    a = _berkas(tmp_path, "a.yaml", klasifikasi=[(JKN, "iuran_pengurang", "2026-01-01", None)])
    b = _berkas(tmp_path, "b.yaml", klasifikasi=[(JKN, "bukan_objek", "2026-01-01", None)])
    pesan = _galat_di_setiap_urutan([a, b], "klasifikasi wajib iuran_jkn_pegawai mulai 2026-01-01 bentrok dengan versi yang "
                                            "berlaku mulai 2026-01-01")
    assert pesan[0].startswith("b.yaml: ") and pesan[0].endswith(" (a.yaml)")
    assert pesan[1].startswith("a.yaml: ") and pesan[1].endswith(" (b.yaml)")
    # entri KB dasar tetap versi yang sudah ada: entri surut yang rentangnya memuat tanggal mulainya ditolak
    surut = _berkas(tmp_path, "surut.yaml", klasifikasi=[(JKN, "iuran_pengurang", "2014-01-01", None)])
    _galat_di_setiap_urutan([surut, a], "surut.yaml: klasifikasi wajib iuran_jkn_pegawai mulai 2014-01-01 bentrok dengan versi "
                                        "yang berlaku mulai 2016-01-01 (klasifikasi.yaml)")
