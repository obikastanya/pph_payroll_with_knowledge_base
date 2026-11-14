"""Pencabutan eksplisit antar-aturan: `menggantikan: [ID, ...]` (research_plan.md §6.4, §6.7).

Selama aturan pengganti berlaku menurut tanggal, aturan yang disebutnya keluar dari kandidat faktanya SEBELUM resolusi
konflik. Itulah yang dicapai KB dasar dengan mengisi `sampai` pada aturan lama; berkas KB tambahan tidak dapat mengubah
aturan yang sudah ada, dan tanpa field ini aturan baru hanya dapat "mengganti" dengan cara mengalahkan (aturan tanpa
`jika` tidak pernah mengalahkan aturan ber-`jika`). Seperti tests/test_kb_tambahan.py, setiap tes menulis berkas tambahan
ke tmp_path, persis seperti aplikasi web menyimpan berkas yang disetujui di kb/tambahan/.

M1 skema & model data, M2 penolakan saat muat, M3 pengganti permanen/sementara/knowledge time, M4 aturan yang digantikan
tidak dinilai, M5 berantai, M6 titik tetap, M7 graf per tahun, M8 masa berlaku efektif, M9 field tidak dipakai.
"""
import hashlib
import itertools
import json
from datetime import date

import pytest

from eksperimen.e12_tanpa_kb import BERKAS_PX
from eksperimen.e8_perusahaan_x import kasus_kar_a
from engine.inferensi import Evaluasi, KasusTidakDidukung
from engine.kalkulator import hitung
from engine.kb import masa_berlaku_efektif, muat_kb
from engine.muat import KesalahanKB

THP_LAMA = ("PX-THP-01", "PX-THP-02")   # seluruh aturan KB dasar yang menghasilkan px_thp (keduanya ber-`jika`)
KUNCI_JEJAK = ["fakta", "bulan", "nilai", "aturan", "lapisan", "sifat", "sumber", "ditolak", "alasan"]


def _tulis(tmp_path, nama, isi):
    p = tmp_path / nama
    p.write_text(isi, encoding="utf-8")
    return p


def _aturan(id_aturan, menghasilkan, maka, mulai="2026-01-01", sampai=None, menggantikan=(), jika=None, sifat="opsional",
            lingkup="masa", tipe="rupiah", tambahan=()):
    baris = [f"  - id: {id_aturan}", f"    sifat: {sifat}",
             f"    berlaku: {{mulai: {mulai}" + (f", sampai: {sampai}}}" if sampai else "}"),
             f"    lingkup: {lingkup}", f"    menghasilkan: {menghasilkan}"]
    if menggantikan:
        baris.append(f"    menggantikan: [{', '.join(menggantikan)}]")
    if jika:
        baris.append(f'    jika: "{jika}"')
    baris += [f'    maka: "{maka}"', f"    tipe_hasil: {tipe}", *(f"    {t}" for t in tambahan),
              '    sumber: "uji menggantikan"']
    return "\n".join(baris) + "\n"


def _berkas(*aturan, lapisan="perusahaan"):
    return f"lapisan: {lapisan}\naturan:\n" + "".join(aturan)


def _thp_baru(**kw):
    """Aturan perusahaan tanpa `jika` untuk px_thp; daftar `menggantikan` sengaja ditulis terbalik (jejak mengurutkannya)."""
    kw.setdefault("menggantikan", THP_LAMA[::-1])
    return _berkas(_aturan("UJI-THP-BARU", "px_thp", "px_penghasilan_tunai - pph21", **kw))


def _kasus(tahun, metode="gross"):
    kasus = kasus_kar_a(tahun)
    kasus["metode"] = metode
    return kasus


def _dasar(tahun, metode="gross", **kw):
    return hitung(_kasus(tahun, metode), berkas_perusahaan=BERKAS_PX, **kw)


def _jejak(h, fakta):
    return {j["bulan"]: j for j in h["jejak"] if j["fakta"] == fakta}


def _selain(h, fakta):
    """Hasil tanpa satu fakta: untuk memeriksa bahwa penggantian tidak menyentuh fakta lain."""
    return {"per_masa": {b: {f: v for f, v in m.items() if f != fakta} for b, m in h["per_masa"].items()},
            "tahunan": h["tahunan"], "jejak": [j for j in h["jejak"] if j["fakta"] != fakta],
            "peringatan": h["peringatan"], "titik_tetap": h["titik_tetap"]}


DIGANTIKAN_THP = [{"aturan": "PX-THP-01", "oleh": "UJI-THP-BARU"}, {"aturan": "PX-THP-02", "oleh": "UJI-THP-BARU"}]


# ------------------------------------------------------------------------------------------- M1 skema & model data

def test_field_menggantikan_terbaca_sebagai_tuple_id(tmp_path):
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "ganti.yaml", _thp_baru())])
    per_id = {a.id: a for a in kb.aturan}
    assert per_id["UJI-THP-BARU"].menggantikan == ("PX-THP-02", "PX-THP-01")
    assert all(a.menggantikan == () for a in kb.aturan if a.id != "UJI-THP-BARU")


@pytest.mark.parametrize("nilai, pesan", [
    ("[]", "should be non-empty|is too short"),
    ("[PX-THP-01, PX-THP-01]", "non-unique"),
    ('[""]', "should be non-empty|is too short"),
    ("PX-THP-01", "is not of type 'array'"),
    ("[1]", "is not of type 'string'"),
])
def test_bentuk_menggantikan_yang_salah_ditolak_skema(tmp_path, nilai, pesan):
    isi = _thp_baru().replace("menggantikan: [PX-THP-02, PX-THP-01]", f"menggantikan: {nilai}")
    with pytest.raises(KesalahanKB, match=rf"aturan\.schema\.json: .*({pesan}).*\(di aturan/0/menggantikan"):
        muat_kb([*BERKAS_PX, _tulis(tmp_path, "ganti.yaml", isi)])


# ------------------------------------------------------------------------------------------- M2 penolakan saat muat

TAFSIR = ("tafsir: UJI-TAFSIR", "varian: a", "varian_default: true")
TOLAK = {
    # nama: (lapisan berkas, aturan pengganti, pesan lengkap)
    "id_tidak_ada": ("perusahaan", _aturan("UJI-X", "px_thp", "0", menggantikan=["PX-THP-99"]),
                     "ganti.yaml: aturan UJI-X menggantikan PX-THP-99, tetapi tidak ada aturan ber-id PX-THP-99 di KB dasar "
                     "maupun di berkas tambahan yang dimuat"),
    "diri_sendiri": ("perusahaan", _aturan("UJI-X", "px_thp", "0", menggantikan=["PX-THP-01", "UJI-X"]),
                     "ganti.yaml: aturan UJI-X tidak boleh menggantikan dirinya sendiri"),
    "fakta_berbeda": ("perusahaan", _aturan("UJI-X", "px_thp", "0", menggantikan=["PX-THP-00"]),
                      "ganti.yaml: aturan UJI-X tidak dapat menggantikan PX-THP-00 (perusahaan_x.yaml): keduanya menghasilkan "
                      "fakta berbeda (px_thp vs px_penghasilan_tunai)"),
    "lingkup_berbeda": ("perusahaan", _aturan("UJI-X", "px_thp", "0", menggantikan=["PX-THP-01"], lingkup="tahun"),
                        "ganti.yaml: aturan UJI-X tidak dapat menggantikan PX-THP-01 (perusahaan_x.yaml): lingkupnya berbeda "
                        "(tahun vs masa)"),
    "regulasi_menggantikan_perusahaan": (
        "regulasi", _aturan("UJI-X", "px_thp", "0", menggantikan=["PX-THP-01"], sifat="wajib"),
        "ganti.yaml: aturan UJI-X tidak dapat menggantikan PX-THP-01 (perusahaan_x.yaml): lapisannya berbeda (regulasi vs "
        "perusahaan); `menggantikan` hanya berlaku di dalam satu lapisan, urutan antar-lapisan diatur lex superior / "
        "override sah"),
    "perusahaan_menggantikan_regulasi": (
        "perusahaan", _aturan("UJI-X", "tunjangan_pajak_berjalan", "0", menggantikan=["R24-05a"]),
        "ganti.yaml: aturan UJI-X tidak dapat menggantikan R24-05a (aturan_ter.yaml): lapisannya berbeda (perusahaan vs "
        "regulasi); `menggantikan` hanya berlaku di dalam satu lapisan, urutan antar-lapisan diatur lex superior / "
        "override sah"),
    "pengganti_tafsir": (
        "regulasi", _aturan("UJI-X", "tunjangan_pajak_berjalan", "0", menggantikan=["R24-05a"], sifat="tafsir",
                            tambahan=TAFSIR),
        "ganti.yaml: aturan UJI-X tidak dapat menggantikan R24-05a (aturan_ter.yaml): UJI-X adalah aturan tafsir; aturan "
        "tafsir dipilih lewat varian, bukan dicabut lewat `menggantikan`"),
    "yang_digantikan_tafsir": (
        "regulasi", _aturan("UJI-X", "biaya_jabatan", "0", menggantikan=["REG-BJ-02a"], sifat="wajib", lingkup="tahun"),
        "ganti.yaml: aturan UJI-X tidak dapat menggantikan REG-BJ-02a (aturan_umum.yaml): REG-BJ-02a adalah aturan tafsir; "
        "aturan tafsir dipilih lewat varian, bukan dicabut lewat `menggantikan`"),
    "mulai_sama": ("perusahaan", _aturan("UJI-X", "px_thp", "0", mulai="2016-01-01", menggantikan=["PX-THP-01"]),
                   "ganti.yaml: aturan UJI-X tidak dapat menggantikan PX-THP-01 (perusahaan_x.yaml): UJI-X mulai berlaku "
                   "2016-01-01, tidak lebih baru daripada PX-THP-01 (2016-01-01); aturan pengganti wajib mulai berlaku "
                   "sesudah aturan yang digantikannya"),
    "mulai_lebih_awal": ("perusahaan", _aturan("UJI-X", "px_thp", "0", mulai="2015-06-01", menggantikan=["PX-THP-01"]),
                         "ganti.yaml: aturan UJI-X tidak dapat menggantikan PX-THP-01 (perusahaan_x.yaml): UJI-X mulai "
                         "berlaku 2015-06-01, tidak lebih baru daripada PX-THP-01 (2016-01-01); aturan pengganti wajib mulai "
                         "berlaku sesudah aturan yang digantikannya"),
    "yang_digantikan_sudah_berakhir": (
        "perusahaan", _aturan("UJI-X", "px_dtp_tunai", "0", mulai="2027-01-01", menggantikan=["PX-THP-DTP1"]),
        "ganti.yaml: aturan UJI-X tidak dapat menggantikan PX-THP-DTP1 (perusahaan_x.yaml): PX-THP-DTP1 sudah berakhir "
        "2026-12-31, sebelum UJI-X mulai berlaku (2027-01-01), sehingga tidak ada yang digantikan"),
}


@pytest.mark.parametrize("nama", sorted(TOLAK))
def test_menggantikan_yang_tidak_sah_ditolak_saat_muat(tmp_path, nama):
    lapisan, aturan, pesan = TOLAK[nama]
    with pytest.raises(KesalahanKB) as galat:
        muat_kb([*BERKAS_PX, _tulis(tmp_path, "ganti.yaml", _berkas(aturan, lapisan=lapisan))])
    assert str(galat.value) == pesan


def test_aturan_lama_yang_berakhir_tepat_pada_mulai_pengganti_masih_boleh_digantikan(tmp_path):
    # PX-THP-DTP1 berlaku s.d. 2026-12-31: pada hari itu ia masih berlaku, jadi masih ada yang digantikan
    isi = _berkas(_aturan("UJI-X", "px_dtp_tunai", "0", mulai="2026-12-31", menggantikan=["PX-THP-DTP1"]))
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "ganti.yaml", isi)])
    assert masa_berlaku_efektif(kb)["PX-THP-DTP1"] == (date(2025, 1, 1), date(2026, 12, 30))


TRANSPORT_LAMA = """
lapisan: perusahaan
komponen:
  - {fakta: px_transport, jenis: tunjangan_transport, kategori: teratur}
aturan:
""" + _aturan("UJI-TRA-01", "px_transport", "hr('kunci_x')", mulai="2016-01-01", jika="hr('kunci_x') > 0")


def _transport_baru(mulai="2026-01-01", **kw):
    return _berkas(_aturan("UJI-TRA-02", "px_transport", "250000", mulai=mulai, menggantikan=["UJI-TRA-01"], **kw))


def test_pengganti_dan_yang_digantikan_di_dua_berkas_tambahan_tidak_bergantung_urutan_muat(tmp_path):
    lama = _tulis(tmp_path, "lama.yaml", TRANSPORT_LAMA)
    baru = _tulis(tmp_path, "baru.yaml", _transport_baru("2026-07-01"))
    kasus = {t: kasus_kar_a(t) for t in (2025, 2026, 2027)}
    for k in kasus.values():
        k["data_hr"]["kunci_x"] = 100_000
    hasil = []
    for urutan in itertools.permutations([lama, baru]):   # di urutan (baru, lama) pengganti terbaca lebih dulu
        kb = muat_kb([*BERKAS_PX, *urutan])
        hasil.append({t: hitung(k, kb=kb) for t, k in kasus.items()})
    assert hasil[0] == hasil[1]
    assert [hasil[0][2026]["per_masa"][b]["px_transport"] for b in range(1, 13)] == [100_000] * 6 + [250_000] * 6
    # penolakan pun sama di kedua urutan, dengan pesan yang sama
    surut = _tulis(tmp_path, "surut.yaml", _transport_baru("2016-01-01"))
    pesan = []
    for urutan in itertools.permutations([lama, surut]):
        with pytest.raises(KesalahanKB) as galat:
            muat_kb([*BERKAS_PX, *urutan])
        pesan.append(str(galat.value))
    assert pesan[0] == pesan[1] and pesan[0].startswith("surut.yaml: aturan UJI-TRA-02 tidak dapat menggantikan UJI-TRA-01 "
                                                        "(lama.yaml): UJI-TRA-02 mulai berlaku 2016-01-01")
    # berkas pengganti tanpa berkas aturan lamanya (mis. berkas lama dinonaktifkan) tidak termuat
    with pytest.raises(KesalahanKB, match=r"baru\.yaml: aturan UJI-TRA-02 menggantikan UJI-TRA-01, tetapi tidak ada aturan"):
        muat_kb([*BERKAS_PX, baru])


# ------------------------------------------------------------------------------------------- M3 permanen/sementara

def test_tanpa_menggantikan_aturan_tanpa_jika_selalu_kalah_lex_specialis(tmp_path):
    # keadaan sebelum field ini ada: aturan baru tanpa `jika` tidak pernah menang atas PX-THP-01 (1 konjungsi)
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp.yaml", _thp_baru(menggantikan=()))])
    h = hitung(_kasus(2026), kb=kb)
    for b, j in _jejak(h, "px_thp").items():
        assert (j["aturan"], j["ditolak"], j["alasan"]) == ("PX-THP-01", ["UJI-THP-BARU"], ["lex_specialis"])
        assert list(j) == KUNCI_JEJAK
    assert _selain(h, "px_thp") == _selain(_dasar(2026), "px_thp")


def test_aturan_tanpa_jika_menggantikan_aturan_dasar_px_thp_sepanjang_2026(tmp_path):
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp.yaml", _thp_baru())])
    h, dasar = hitung(_kasus(2026), kb=kb), _dasar(2026)
    jejak = _jejak(h, "px_thp")
    assert sorted(jejak) == list(range(1, 13))
    for b, j in jejak.items():
        m = h["per_masa"][b]
        assert j["aturan"] == "UJI-THP-BARU" and m["px_thp"] == j["nilai"] == m["px_penghasilan_tunai"] - m["pph21"]
        # aturan yang digantikan tidak pernah menyala, jadi bukan "ditolak": ia dicatat di "digantikan", urut id
        assert (j["ditolak"], j["alasan"], j["digantikan"]) == ([], [], DIGANTIKAN_THP)
        assert list(j) == KUNCI_JEJAK + ["digantikan"]
    assert h["per_masa"][12]["px_thp"] != dasar["per_masa"][12]["px_thp"]   # aturan baru memang menghitung lain
    # fakta lain tidak tersentuh, dan jejaknya tidak mendapat kunci baru
    assert _selain(h, "px_thp") == _selain(dasar, "px_thp")
    assert not any("digantikan" in j for j in h["jejak"] if j["fakta"] != "px_thp")
    # tahun berikutnya: pengganti permanen tetap berlaku
    h27 = hitung(_kasus(2027), kb=kb)
    assert {j["aturan"] for j in _jejak(h27, "px_thp").values()} == {"UJI-THP-BARU"}
    assert all(j["digantikan"] == DIGANTIKAN_THP for j in _jejak(h27, "px_thp").values())


def test_isolasi_temporal_sebelum_pengganti_berlaku_hasil_sama_dengan_kb_dasar(tmp_path):
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp.yaml", _thp_baru())])
    for tahun, metode in ((2023, "gross"), (2024, "gross"), (2025, "gross"), (2024, "gross_up"), (2025, "gross_up"),
                          (2025, "ditanggung_pemberi_kerja")):
        assert hitung(_kasus(tahun, metode), kb=kb) == _dasar(tahun, metode), (tahun, metode)


def test_pengganti_berlaku_menurut_tanggal_walaupun_kalah_resolusi_konflik(tmp_path):
    # UJI-THP-BARU hanya menyebut PX-THP-01. Pada metode ditanggung pemberi kerja PX-THP-02 (1 konjungsi) tetap kandidat
    # dan mengalahkannya (lex specialis); PX-THP-01 tetap tercatat digantikan karena penggantinya berlaku menurut tanggal.
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp.yaml", _thp_baru(menggantikan=["PX-THP-01"]))])
    h = hitung(_kasus(2026, "ditanggung_pemberi_kerja"), kb=kb)
    dasar = _dasar(2026, "ditanggung_pemberi_kerja")
    for b, j in _jejak(h, "px_thp").items():
        assert (j["aturan"], j["ditolak"], j["alasan"]) == ("PX-THP-02", ["UJI-THP-BARU"], ["lex_specialis"])
        assert j["digantikan"] == [{"aturan": "PX-THP-01", "oleh": "UJI-THP-BARU"}]
    assert h["per_masa"] == dasar["per_masa"] and h["tahunan"] == dasar["tahunan"]
    # metode gross: PX-THP-02 tidak menyala, PX-THP-01 digantikan -> aturan baru satu-satunya yang menyala
    assert {j["aturan"] for j in _jejak(hitung(_kasus(2026), kb=kb), "px_thp").values()} == {"UJI-THP-BARU"}


def test_pengganti_sementara_aturan_lama_berlaku_lagi_mulai_juli(tmp_path):
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp.yaml", _thp_baru(sampai="2026-06-30"))])
    h, dasar = hitung(_kasus(2026), kb=kb), _dasar(2026)
    jejak = _jejak(h, "px_thp")
    for b in range(1, 7):
        assert jejak[b]["aturan"] == "UJI-THP-BARU" and jejak[b]["digantikan"] == DIGANTIKAN_THP
    for b in range(7, 13):
        # pengganti sudah berakhir: bukan kandidat (tidak "ditolak") dan tidak ada lagi yang digantikan
        assert jejak[b] == _jejak(dasar, "px_thp")[b] and jejak[b]["aturan"] == "PX-THP-01" and "digantikan" not in jejak[b]
        assert h["per_masa"][b]["px_thp"] == dasar["per_masa"][b]["px_thp"]
    assert _selain(h, "px_thp") == _selain(dasar, "px_thp")
    assert hitung(_kasus(2027), kb=kb) == _dasar(2027) and hitung(_kasus(2025), kb=kb) == _dasar(2025)


def test_pengganti_mulai_tengah_bulan_baru_menggantikan_pada_masa_berikutnya(tmp_path):
    # aturan masa dinilai pada tanggal 1 tiap bulan: pengganti yang mulai 15 Juli menggantikan mulai masa Agustus
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp.yaml", _thp_baru(mulai="2026-07-15"))])
    jejak = _jejak(hitung(_kasus(2026), kb=kb), "px_thp")
    assert [jejak[b]["aturan"] for b in range(1, 13)] == ["PX-THP-01"] * 7 + ["UJI-THP-BARU"] * 5
    assert ["digantikan" in jejak[b] for b in range(1, 13)] == [False] * 7 + [True] * 5


def test_aturan_lama_yang_sudah_berakhir_sendiri_tidak_dicatat_digantikan(tmp_path):
    # PX-THP-DTP1 berlaku 2025-01-01..2026-12-31. Di 2027 ia memang sudah berakhir: bukan "digantikan", walaupun
    # penggantinya masih berlaku (dan di sana kalah lex posterior dari PX-THP-DTP2 yang mulai 2027)
    isi = _berkas(_aturan("UJI-DTP-P", "px_dtp_tunai", "0", mulai="2026-07-01", menggantikan=["PX-THP-DTP1"]))
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "dtp.yaml", isi)])
    j26 = _jejak(hitung(_kasus(2026), kb=kb), "px_dtp_tunai")
    assert [j26[b]["aturan"] for b in range(1, 13)] == ["PX-THP-DTP1"] * 6 + ["UJI-DTP-P"] * 6
    assert all(j26[b]["digantikan"] == [{"aturan": "PX-THP-DTP1", "oleh": "UJI-DTP-P"}] for b in range(7, 13))
    for j in _jejak(hitung(_kasus(2027), kb=kb), "px_dtp_tunai").values():
        assert (j["aturan"], j["ditolak"], j["alasan"]) == ("PX-THP-DTP2", ["UJI-DTP-P"], ["lex_posterior"])
        assert "digantikan" not in j


def test_fakta_lingkup_tahun_dinilai_pada_masa_terakhir_sehingga_pengganti_tengah_tahun_berlaku_setahun(tmp_path):
    # fakta tahunan dinilai sekali, pada tanggal 1 masa terakhir (Desember), sama seperti aturan berversi waktu lainnya
    def bulan_thr(mulai):
        isi = _berkas(_aturan("UJI-THR-BULAN", "px_bulan_thr", "6", mulai=mulai, menggantikan=["PX-THR-00"], lingkup="tahun",
                              tipe="bilangan"))
        h = hitung(_kasus(2026), kb=muat_kb([*BERKAS_PX, _tulis(tmp_path, f"thr_{mulai}.yaml", isi)]))
        (j,) = [j for j in h["jejak"] if j["fakta"] == "px_bulan_thr"]
        return h["tahunan"]["px_bulan_thr"], j["aturan"], j.get("digantikan")
    assert bulan_thr("2026-07-01") == (6, "UJI-THR-BULAN", [{"aturan": "PX-THR-00", "oleh": "UJI-THR-BULAN"}])
    assert bulan_thr("2026-12-02") == (_dasar(2026)["tahunan"]["px_bulan_thr"], "PX-THR-00", None)


def test_knowledge_time_pengganti_yang_belum_dicatat_belum_menggantikan(tmp_path):
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp.yaml", _thp_baru(tambahan=("dicatat: 2026-03-01",)))])
    # KB sebagaimana diketahui 1 Februari 2026: aturan pengganti belum dikenal, aturan lama yang berlaku
    saat_itu = hitung(_kasus(2026), kb=kb, per_tanggal_kb=date(2026, 2, 1))
    assert saat_itu == _dasar(2026, per_tanggal_kb=date(2026, 2, 1)) == _dasar(2026)
    assert {j["aturan"] for j in _jejak(saat_itu, "px_thp").values()} == {"PX-THP-01"}
    # sejak dicatat (dan tanpa per_tanggal_kb = KB terbaru): aturan baru menggantikan sepanjang 2026 (berlaku surut)
    for kw in ({}, {"per_tanggal_kb": date(2026, 3, 1)}):
        h = hitung(_kasus(2026), kb=kb, **kw)
        assert {j["aturan"] for j in _jejak(h, "px_thp").values()} == {"UJI-THP-BARU"}
        assert all(j["digantikan"] == DIGANTIKAN_THP for j in _jejak(h, "px_thp").values())


def test_ablasi_tanpa_versi_waktu_tidak_menerapkan_pencabutan(tmp_path):
    # A1 mengabaikan seluruh logika tanggal, termasuk "selama pengganti berlaku": resolusi konflik biasa
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp.yaml", _thp_baru())])
    h = hitung(_kasus(2026), kb=kb, ablasi=("A1_tanpa_versi_waktu",))
    for j in _jejak(h, "px_thp").values():
        assert (j["aturan"], j["ditolak"], j["alasan"]) == ("PX-THP-01", ["UJI-THP-BARU"], ["lex_specialis"])
    assert not any("digantikan" in j for j in h["jejak"])


# ------------------------------------------------------------------------------------------- M4 tidak dinilai

def test_aturan_yang_digantikan_tidak_dinilai_sehingga_isiannya_tidak_lagi_diminta(tmp_path):
    # UJI-TRA-01 membaca hr('kunci_x') di `jika` dan `maka`, tanpa nilai bawaan: tanpa kunci_x = DATA_KURANG
    lama = _tulis(tmp_path, "lama.yaml", TRANSPORT_LAMA)
    kb = muat_kb([*BERKAS_PX, lama, _tulis(tmp_path, "baru.yaml", _transport_baru())])
    assert "kunci_x" not in kasus_kar_a(2026)["data_hr"]
    with pytest.raises(KesalahanKB, match=r"data_hr\.kunci_x tidak tersedia \(DATA_KURANG\)"):
        hitung(kasus_kar_a(2025), kb=kb)
    for tahun in (2026, 2027):
        h = hitung(kasus_kar_a(tahun), kb=kb)
        assert [h["per_masa"][b]["px_transport"] for b in range(1, 13)] == [250_000] * 12
        assert all(j["digantikan"] == [{"aturan": "UJI-TRA-01", "oleh": "UJI-TRA-02"}]
                   for j in _jejak(h, "px_transport").values())


def test_pengganti_mulai_tengah_tahun_aturan_lama_masih_dinilai_sebelum_itu(tmp_path):
    lama = _tulis(tmp_path, "lama.yaml", TRANSPORT_LAMA)
    kb = muat_kb([*BERKAS_PX, lama, _tulis(tmp_path, "baru.yaml", _transport_baru("2026-07-01"))])
    with pytest.raises(KesalahanKB, match=r"data_hr\.kunci_x tidak tersedia \(DATA_KURANG\)"):
        hitung(kasus_kar_a(2026), kb=kb)   # Januari-Juni masih dihitung aturan lama
    kasus = kasus_kar_a(2026)
    kasus["data_hr"]["kunci_x"] = 100_000
    h = hitung(kasus, kb=kb)
    assert [h["per_masa"][b]["px_transport"] for b in range(1, 13)] == [100_000] * 6 + [250_000] * 6
    assert [j["aturan"] for j in _jejak(h, "px_transport").values()] == ["UJI-TRA-01"] * 6 + ["UJI-TRA-02"] * 6
    assert hitung(kasus_kar_a(2027), kb=kb)["per_masa"][1]["px_transport"] == 250_000


def test_pengganti_ber_jika_lebih_sempit_fakta_tidak_dihasilkan_dan_tidak_ditebak(tmp_path):
    # pengganti berlaku menurut tanggal walaupun `jika`-nya tidak terpenuhi: aturan lama tetap keluar, tidak ada
    # aturan lain yang menyala, fakta tidak dihasilkan (validasi asisten yang melaporkannya sebagai galat)
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp.yaml", _thp_baru(jika="bulan >= 4"))])
    h = hitung(_kasus(2026), kb=kb)
    assert ["px_thp" in h["per_masa"][b] for b in range(1, 13)] == [False] * 3 + [True] * 9
    assert sorted(_jejak(h, "px_thp")) == list(range(4, 13))
    assert _selain(h, "px_thp") == _selain(_dasar(2026), "px_thp")


# ------------------------------------------------------------------------------------------- M5 berantai

def _rantai_thp():
    """Z -> X -> Y: X menggantikan aturan dasar mulai Januari 2026, Z menggantikan X mulai Juli 2026."""
    return _berkas(_aturan("UJI-THP-X", "px_thp", "px_penghasilan_tunai - pph21", menggantikan=THP_LAMA),
                   _aturan("UJI-THP-Z", "px_thp", "px_penghasilan_tunai", mulai="2026-07-01", menggantikan=["UJI-THP-X"],
                           jika="bulan != 9"))


def test_rantai_aturan_lama_tetap_keluar_walaupun_penggantinya_sendiri_digantikan(tmp_path):
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "rantai.yaml", _rantai_thp())])
    oleh_x = [{"aturan": "PX-THP-01", "oleh": "UJI-THP-X"}, {"aturan": "PX-THP-02", "oleh": "UJI-THP-X"}]
    oleh_z = oleh_x + [{"aturan": "UJI-THP-X", "oleh": "UJI-THP-Z"}]
    h = hitung(_kasus(2026), kb=kb)
    jejak = _jejak(h, "px_thp")
    for b in range(1, 7):
        assert (jejak[b]["aturan"], jejak[b]["digantikan"]) == ("UJI-THP-X", oleh_x)
    for b in (7, 8, 10, 11, 12):
        assert (jejak[b]["aturan"], jejak[b]["ditolak"], jejak[b]["digantikan"]) == ("UJI-THP-Z", [], oleh_z)
        assert h["per_masa"][b]["px_thp"] == h["per_masa"][b]["px_penghasilan_tunai"]
    # September: `jika` Z tidak terpenuhi, tetapi X (digantikan Z) dan aturan dasar (digantikan X) tidak hidup kembali
    assert 9 not in jejak and "px_thp" not in h["per_masa"][9]
    h27 = hitung(_kasus(2027), kb=kb)
    assert {b: j["aturan"] for b, j in _jejak(h27, "px_thp").items()} == {b: "UJI-THP-Z" for b in range(1, 13) if b != 9}
    assert all(j["digantikan"] == oleh_z for j in _jejak(h27, "px_thp").values())
    assert hitung(_kasus(2025), kb=kb) == _dasar(2025)


def test_dua_pengganti_berlaku_bersamaan_jejak_mencatat_yang_mulai_paling_akhir(tmp_path):
    # keduanya menyebut PX-THP-01 dan PX-THP-02; di antara keduanya sendiri berlaku resolusi konflik biasa (lex posterior)
    isi = _berkas(_aturan("UJI-THP-A", "px_thp", "px_penghasilan_tunai - pph21", menggantikan=THP_LAMA),
                  _aturan("UJI-THP-B", "px_thp", "px_penghasilan_tunai", mulai="2026-07-01", menggantikan=THP_LAMA))
    jejak = _jejak(hitung(_kasus(2026), kb=muat_kb([*BERKAS_PX, _tulis(tmp_path, "dua.yaml", isi)])), "px_thp")
    assert (jejak[6]["aturan"], jejak[6]["ditolak"]) == ("UJI-THP-A", [])
    assert {d["oleh"] for d in jejak[6]["digantikan"]} == {"UJI-THP-A"}
    assert (jejak[7]["aturan"], jejak[7]["ditolak"], jejak[7]["alasan"]) == ("UJI-THP-B", ["UJI-THP-A"], ["lex_posterior"])
    assert jejak[7]["digantikan"] == [{"aturan": "PX-THP-01", "oleh": "UJI-THP-B"},
                                      {"aturan": "PX-THP-02", "oleh": "UJI-THP-B"}]


# ------------------------------------------------------------------------------------------- M6 titik tetap

def _titik_tetap(jika, maka="tunjangan_pajak_berjalan", mulai="2026-01-01", titik=True):
    """Pengganti R24-05a (jika: gross_up and not masa_terakhir; batas 0 .. _bruto_dasar). Dengan maka = fakta itu sendiri
    setiap nilai adalah titik tetap, sehingga solusi terkecil & terbesar = batas yang dipakai iterasi (trik yang sama
    dengan test_batas_titik_tetap_diambil_dari_aturan_pemenang di tests/test_kb_tambahan.py)."""
    tambahan = ("titik_tetap: true", 'batas_titik_tetap: {bawah: "1000", atas: "2000"}') if titik else ()
    return _berkas(_aturan("UJI-TT-02", "tunjangan_pajak_berjalan", maka, mulai=mulai, menggantikan=["R24-05a"], jika=jika,
                           sifat="wajib", tambahan=tambahan), lapisan="regulasi")


def _ganda(h):
    return {p["bulan"]: (p["terkecil"], p["terbesar"]) for p in h["peringatan"]
            if p["kode"] == "GROSSUP_GANDA" and p["fakta"] == "tunjangan_pajak_berjalan"}


def test_pengganti_titik_tetap_yang_menyebut_r24_05a_memakai_batasnya_sendiri(tmp_path):
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "tt.yaml", _titik_tetap("gross_up and not masa_terakhir"))])
    h = hitung(_kasus(2026, "gross_up"), kb=kb)
    assert _ganda(h) == {b: (1000, 2000) for b in range(1, 12)}
    assert [h["per_masa"][b]["tunjangan_pajak_berjalan"] for b in range(1, 12)] == [1000] * 11
    jejak = _jejak(h, "tunjangan_pajak_berjalan")
    assert sorted(jejak) == list(range(1, 12))
    for j in jejak.values():
        assert (j["aturan"], j["ditolak"], j["digantikan"]) == ("UJI-TT-02", [], [{"aturan": "R24-05a", "oleh": "UJI-TT-02"}])
    # sebelum pengganti berlaku, dan untuk metode selain gross-up, tidak ada yang berubah
    assert hitung(_kasus(2025, "gross_up"), kb=kb) == _dasar(2025, "gross_up")
    assert hitung(_kasus(2026), kb=kb) == _dasar(2026)


def test_pengganti_titik_tetap_yang_lebih_umum_dari_r24_05a_kini_mungkin(tmp_path):
    # tanpa "not masa_terakhir" (1 konjungsi < 2): dulu kalah lex specialis dari R24-05a di masa 1-11. Kini R24-05a
    # dicabut, sehingga aturan baru menghitung kedua belas masa dengan batasnya sendiri.
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "tt.yaml", _titik_tetap("gross_up"))])
    h = hitung(_kasus(2026, "gross_up"), kb=kb)
    assert _ganda(h) == {b: (1000, 2000) for b in range(1, 13)}
    assert [h["per_masa"][b]["tunjangan_pajak_berjalan"] for b in range(1, 13)] == [1000] * 12
    assert {j["aturan"] for j in _jejak(h, "tunjangan_pajak_berjalan").values()} == {"UJI-TT-02"}
    # pembanding: aturan yang sama tanpa `menggantikan` kalah di masa 1-11 dan hanya menghitung masa terakhir
    tanpa = _titik_tetap("gross_up").replace("    menggantikan: [R24-05a]\n", "")
    h_tanpa = hitung(_kasus(2026, "gross_up"), kb=muat_kb([*BERKAS_PX, _tulis(tmp_path, "tanpa.yaml", tanpa)]))
    assert [j["aturan"] for j in _jejak(h_tanpa, "tunjangan_pajak_berjalan").values()] == ["R24-05a"] * 11 + ["UJI-TT-02"]


def test_pengganti_titik_tetap_mulai_tengah_tahun_batas_berganti_per_masa(tmp_path):
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "tt.yaml", _titik_tetap("gross_up", mulai="2026-07-01"))])
    h, dasar = hitung(_kasus(2026, "gross_up"), kb=kb), _dasar(2026, "gross_up")
    for b in range(1, 7):   # Januari-Juni: R24-05a dengan batasnya sendiri, nilai sama dengan KB dasar
        assert h["per_masa"][b]["tunjangan_pajak_berjalan"] == dasar["per_masa"][b]["tunjangan_pajak_berjalan"]
        assert _ganda(h).get(b) == _ganda(dasar).get(b)
    assert {b: v for b, v in _ganda(h).items() if b >= 7} == {b: (1000, 2000) for b in range(7, 13)}
    assert [j["aturan"] for j in _jejak(h, "tunjangan_pajak_berjalan").values()] == ["R24-05a"] * 6 + ["UJI-TT-02"] * 6


def test_pengganti_r24_05a_tanpa_tanda_titik_tetap_ditolak_dengan_pesan_jelas(tmp_path):
    # maka-nya tetap bersiklus (pph21_berjalan) tetapi tanpa batas iterasi. Pada tahun peralihan (mulai 1 Juli) galat
    # muncul di instance pertama yang dimenangkan pengganti: pesan yang sama dengan pengganti lewat lex posterior,
    # walaupun R24-05a kini bukan kandidat lagi; metode selain gross-up tidak tersentuh.
    isi = _titik_tetap("gross_up", maka="pph21_berjalan", mulai="2026-07-01", titik=False)
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "tt.yaml", isi)])
    with pytest.raises(KesalahanKB, match=r"UJI-TT-02 menggantikan R24-05a pada fakta titik tetap tunjangan_pajak_berjalan"
                                          r"\[7\] tetapi tidak bertanda titik_tetap/batas_titik_tetap; tambahkan"):
        hitung(_kasus(2026, "gross_up"), kb=kb)
    assert hitung(_kasus(2026), kb=kb) == _dasar(2026)
    assert hitung(_kasus(2025, "gross_up"), kb=kb) == _dasar(2025, "gross_up")


PESAN_SIKLUS_R24_05A = (
    "UJI-TT-02 menggantikan R24-05a pada fakta titik tetap tunjangan_pajak_berjalan tetapi tidak bertanda"
    " titik_tetap/batas_titik_tetap, sehingga siklus ['bruto_berjalan', 'pph21_berjalan', 'tarif_ter',"
    " 'tunjangan_pajak_berjalan'] tidak punya titik tetap di tahun {tahun}; tambahkan keduanya pada UJI-TT-02")


@pytest.mark.parametrize("mulai, tahun", [("2026-01-01", 2026), ("2026-01-01", 2027), ("2026-07-01", 2027)])
def test_penanda_titik_tetap_aturan_yang_dicabut_sepanjang_tahun_tidak_mengesahkan_siklus(tmp_path, mulai, tahun):
    # setara dengan mengisi `sampai` pada R24-05a: siklusnya tidak lagi punya aturan titik_tetap yang hidup, jadi tahun
    # itu ditolak untuk semua metode (graf dibangun sebelum `jika` dinilai), dengan pesan yang menyebut penggantinya
    isi = _titik_tetap("gross_up", maka="pph21_berjalan", mulai=mulai, titik=False)
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "tt.yaml", isi)])
    for metode in ("gross", "gross_up"):
        with pytest.raises(KesalahanKB) as galat:
            hitung(_kasus(tahun, metode), kb=kb)
        assert str(galat.value) == PESAN_SIKLUS_R24_05A.format(tahun=tahun)
    assert hitung(_kasus(2025, "gross_up"), kb=kb) == _dasar(2025, "gross_up")
    # knowledge time: sebelum pengganti dicatat, R24-05a belum dicabut dan siklusnya masih sah
    kb_dicatat = muat_kb([*BERKAS_PX, _tulis(tmp_path, "dicatat.yaml",
                                              isi.replace("    sumber:", "    dicatat: 2027-06-01\n    sumber:"))])
    assert (hitung(_kasus(tahun, "gross_up"), kb=kb_dicatat, per_tanggal_kb=date(2025, 12, 1))
            == _dasar(tahun, "gross_up", per_tanggal_kb=date(2025, 12, 1)))


def _siklus_f(lama_sampai=None, menggantikan=(), titik_baru=False):
    """uji_f = uji_g (titik tetap 0..100) dan uji_g = atau('uji_f', 0); aturan baru 2026 membaca uji_g di `jika`-nya."""
    tt = ("titik_tetap: true", 'batas_titik_tetap: {bawah: "0", atas: "100"}')
    return _berkas(
        _aturan("UJI-F-01", "uji_f", "uji_g", mulai="2016-01-01", sampai=lama_sampai, tipe="bilangan", tambahan=tt),
        _aturan("UJI-G-01", "uji_g", "atau('uji_f', 0)", mulai="2016-01-01", tipe="bilangan"),
        _aturan("UJI-F-02", "uji_f", "10", menggantikan=menggantikan, jika="atau('uji_g', 0) > 5", tipe="bilangan",
                tambahan=("prioritas: 1", *(tt if titik_baru else ()))),
        _aturan("UJI-F-03", "uji_f", "0", tipe="bilangan"))


def test_siklus_yang_aturan_titik_tetapnya_dicabut_ditolak_seperti_bila_aturan_itu_diberi_sampai(tmp_path):
    # dulu penanda titik_tetap UJI-F-01 yang sudah dicabut masih mengesahkan siklus: uji_f = 0 tanpa peringatan,
    # padahal 10 juga titik tetap dan iterasi berangkat tanpa batas
    cara_sampai = muat_kb([*BERKAS_PX, _tulis(tmp_path, "sampai.yaml", _siklus_f(lama_sampai="2025-12-31"))])
    with pytest.raises(KesalahanKB, match=r"^siklus tanpa titik_tetap: \['uji_f', 'uji_g'\]$"):
        hitung(_kasus(2026), kb=cara_sampai)
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "ganti.yaml", _siklus_f(menggantikan=["UJI-F-01"]))])
    with pytest.raises(KesalahanKB) as galat:
        hitung(_kasus(2026), kb=kb)
    assert str(galat.value) == (
        "UJI-F-02 menggantikan UJI-F-01 pada fakta titik tetap uji_f tetapi tidak bertanda titik_tetap/batas_titik_tetap,"
        " sehingga siklus ['uji_f', 'uji_g'] tidak punya titik tetap di tahun 2026; tambahkan keduanya pada UJI-F-02")
    # tahun sebelumnya tidak tersentuh di kedua cara
    h25 = hitung(_kasus(2025), kb=kb)
    assert h25 == hitung(_kasus(2025), kb=cara_sampai)
    assert {p["bulan"]: (p["terkecil"], p["terbesar"]) for p in h25["peringatan"]
            if p["kode"] == "GROSSUP_GANDA" and p["fakta"] == "uji_f"} == {b: (0, 100) for b in range(1, 13)}
    # pengganti yang bertanda titik_tetap mengesahkan siklus lagi, sama seperti pada cara `sampai`
    for nama, isi in (("tanda.yaml", _siklus_f(menggantikan=["UJI-F-01"], titik_baru=True)),
                      ("tanda_sampai.yaml", _siklus_f(lama_sampai="2025-12-31", titik_baru=True))):
        h = hitung(_kasus(2026), kb=muat_kb([*BERKAS_PX, _tulis(tmp_path, nama, isi)]))
        assert [h["per_masa"][b]["uji_f"] for b in range(1, 13)] == [0] * 12
        assert _jejak(h, "uji_f")[1].get("digantikan") == ([{"aturan": "UJI-F-01", "oleh": "UJI-F-02"}]
                                                          if nama == "tanda.yaml" else None)


def _tt_akhir(menggantikan=("R24-05a",), mulai="2026-01-01", titik=True):
    """UJI-TT-AKHIR: aturan masa terakhir tanpa tanda titik_tetap yang maka-nya membaca anggota siklus; UJI-TT-02:
    pengganti R24-05a dengan `jika`, rumus, dan batas yang sama."""
    tt = ("titik_tetap: true", 'batas_titik_tetap: {bawah: "0", atas: "_bruto_dasar"}') if titik else ()
    return _berkas(
        _aturan("UJI-TT-AKHIR", "tunjangan_pajak_berjalan", "nilai_masa('tunjangan_pajak_berjalan', 11)", mulai="2024-01-01",
                jika="gross_up and masa_terakhir", sifat="wajib"),
        _aturan("UJI-TT-02", "tunjangan_pajak_berjalan", "pph21_berjalan", mulai=mulai, menggantikan=menggantikan,
                jika="gross_up and not masa_terakhir", sifat="wajib", tambahan=tt), lapisan="regulasi")


def test_aturan_titik_tetap_yang_dicabut_aturan_lain_tidak_dianggap_tergeser_oleh_pemenang(tmp_path):
    # masa 12 dimenangkan UJI-TT-AKHIR, yang tidak menyebut R24-05a (dan R24-05a memang tidak menyala di masa terakhir):
    # dulu KB sah ini ditolak dengan "UJI-TT-AKHIR menggantikan R24-05a ... [12]"
    def nilai(isi, nama):
        return hitung(_kasus(2026, "gross_up"), kb=muat_kb([*BERKAS_PX, _tulis(tmp_path, nama, isi)]))
    h, tanpa = nilai(_tt_akhir(), "ganti.yaml"), nilai(_tt_akhir(menggantikan=()), "tanpa.yaml")   # tanpa: lex posterior
    for kunci in ("per_masa", "tahunan", "peringatan", "titik_tetap"):
        assert h[kunci] == tanpa[kunci]
    jejak = _jejak(h, "tunjangan_pajak_berjalan")
    assert [jejak[b]["aturan"] for b in range(1, 13)] == ["UJI-TT-02"] * 11 + ["UJI-TT-AKHIR"]
    assert jejak[12]["digantikan"] == [{"aturan": "R24-05a", "oleh": "UJI-TT-02"}] and jejak[12]["ditolak"] == []
    assert h["per_masa"][12]["tunjangan_pajak_berjalan"] == h["per_masa"][11]["tunjangan_pajak_berjalan"] > 0
    # pemenang yang sendiri menyebut R24-05a tetap ditolak bila tidak bertanda titik_tetap, dan pesannya menyebut pemenang
    # itu (pengganti mulai 1 Juli, supaya penanda R24-05a masih mengesahkan siklus tahun 2026)
    isi = _tt_akhir(mulai="2026-07-01", titik=False)
    with pytest.raises(KesalahanKB, match=r"^UJI-TT-02 menggantikan R24-05a pada fakta titik tetap tunjangan_pajak_berjalan"
                                          r"\[7\] tetapi tidak bertanda"):
        hitung(_kasus(2026, "gross_up"), kb=muat_kb([*BERKAS_PX, _tulis(tmp_path, "tengah.yaml", isi)]))


def test_pengganti_r24_05a_yang_tidak_bersiklus_dihitung_langsung(tmp_path):
    # maka konstan: tidak ada lagi siklus pada tunjangan_pajak_berjalan, jadi tidak perlu titik_tetap maupun batas
    isi = _titik_tetap("gross_up and not masa_terakhir", maka="0", titik=False)
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "tt.yaml", isi)])
    h = hitung(_kasus(2026, "gross_up"), kb=kb)
    assert [h["per_masa"][b]["tunjangan_pajak_berjalan"] for b in range(1, 12)] == [0] * 11
    assert _ganda(h) == {} and {t["anggota"][0] for t in h["titik_tetap"]} == {"tunjangan_pajak_akhir"}


# ------------------------------------------------------------------------------------------- M7 graf per tahun

BALIK_ARAH = _berkas(
    _aturan("UJI-A-01", "uji_a", "uji_b + 1", mulai="2016-01-01", tipe="bilangan"),
    _aturan("UJI-B-01", "uji_b", "5", mulai="2016-01-01", tipe="bilangan"),
    _aturan("UJI-A-02", "uji_a", "7", mulai="MULAI", menggantikan=["UJI-A-01"], tipe="bilangan"),
    _aturan("UJI-B-02", "uji_b", "uji_a * 2", mulai="MULAI", menggantikan=["UJI-B-01"], tipe="bilangan",
            tambahan=("dicatat: 2026-03-01",)))


def test_aturan_yang_dicabut_sepanjang_tahun_tidak_ikut_graf_dependensi(tmp_path):
    # aturan lama: uji_a membaca uji_b; aturan baru: uji_b membaca uji_a. Bila dependensi aturan lama masih dihitung,
    # tahun 2026 menjadi "siklus tanpa titik_tetap" padahal aturan lama tidak pernah dinilai lagi.
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "balik.yaml", BALIK_ARAH.replace("MULAI", "2026-01-01"))])
    h25, h26 = hitung(_kasus(2025), kb=kb), hitung(_kasus(2026), kb=kb)
    assert [(h25["per_masa"][b]["uji_a"], h25["per_masa"][b]["uji_b"]) for b in range(1, 13)] == [(6, 5)] * 12
    assert [(h26["per_masa"][b]["uji_a"], h26["per_masa"][b]["uji_b"]) for b in range(1, 13)] == [(7, 14)] * 12
    assert _selain(_selain(h26, "uji_a"), "uji_b") == _selain(_dasar(2026), "uji_a")   # fakta lain tidak tersentuh
    # knowledge time: sebelum UJI-B-02 dicatat, uji_b masih dihitung aturan lama (uji_a sudah aturan baru)
    lama = hitung(_kasus(2026), kb=kb, per_tanggal_kb=date(2026, 2, 1))
    assert (lama["per_masa"][1]["uji_a"], lama["per_masa"][1]["uji_b"]) == (7, 5)


def test_pencabutan_di_tengah_tahun_tetap_memakai_graf_kedua_aturan(tmp_path):
    # batas yang disengaja: pada tahun peralihan kedua arah dependensi masih ada di graf, sehingga pembalikan arah di
    # tengah tahun ditolak (tidak ditebak); tahun berikutnya, saat aturan lama dicabut sepanjang tahun, dapat dihitung
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "balik.yaml", BALIK_ARAH.replace("MULAI", "2026-07-01"))])
    with pytest.raises(KesalahanKB, match=r"siklus tanpa titik_tetap: \['uji_a', 'uji_b'\]"):
        hitung(_kasus(2026), kb=kb)
    h27 = hitung(_kasus(2027), kb=kb)
    assert (h27["per_masa"][1]["uji_a"], h27["per_masa"][1]["uji_b"]) == (7, 14)


def test_graf_evaluasi_tidak_berubah_bila_tidak_ada_yang_dicabut_sepanjang_tahun(tmp_path):
    dasar = Evaluasi(muat_kb(BERKAS_PX), _kasus(2026, "gross_up"))
    for isi in (_thp_baru(mulai="2026-07-01"), _thp_baru(sampai="2026-12-31")):   # tengah tahun; sementara
        ev = Evaluasi(muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp.yaml", isi)]), _kasus(2026, "gross_up"))
        assert ev.tepi == dasar.tepi and ev.urutan == dasar.urutan
    # pengganti permanen sejak awal tahun: px_thp hanya bergantung pada yang dibaca aturan baru
    ev = Evaluasi(muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp.yaml", _thp_baru())]), _kasus(2026, "gross_up"))
    assert ev.tepi["px_thp"] == {"px_penghasilan_tunai", "pph21"} < dasar.tepi["px_thp"]
    assert {f: d for f, d in ev.tepi.items() if f != "px_thp"} == {f: d for f, d in dasar.tepi.items() if f != "px_thp"}


# ------------------------------------------------------------------------------------------- M8 masa berlaku efektif

def test_masa_berlaku_efektif_kb_dasar_sama_dengan_masa_berlaku_aturan():
    kb = muat_kb(BERKAS_PX)
    assert masa_berlaku_efektif(kb) == {a.id: (a.mulai, a.sampai) for a in kb.aturan}


def test_masa_berlaku_efektif_dipendekkan_pengganti_permanen_saja(tmp_path):
    permanen = masa_berlaku_efektif(muat_kb([*BERKAS_PX, _tulis(tmp_path, "p.yaml", _thp_baru())]))
    assert permanen["PX-THP-01"] == permanen["PX-THP-02"] == (date(2016, 1, 1), date(2025, 12, 31))
    assert permanen["UJI-THP-BARU"] == (date(2026, 1, 1), None)
    assert permanen["PX-THP-00"] == (date(2016, 1, 1), None)   # aturan yang tidak disebut tidak tersentuh
    # pengganti sementara: aturan lama berlaku lagi sesudahnya, jadi masa berlakunya tidak dipendekkan
    sementara = masa_berlaku_efektif(muat_kb([*BERKAS_PX, _tulis(tmp_path, "s.yaml", _thp_baru(sampai="2026-06-30"))]))
    assert sementara["PX-THP-01"] == (date(2016, 1, 1), None)
    assert sementara["UJI-THP-BARU"] == (date(2026, 1, 1), date(2026, 6, 30))


def test_masa_berlaku_efektif_memakai_pengganti_permanen_paling_awal(tmp_path):
    isi = _berkas(
        _aturan("UJI-THP-S", "px_thp", "0", mulai="2025-01-01", sampai="2025-03-31", menggantikan=["PX-THP-01"]),
        _aturan("UJI-THP-P2", "px_thp", "0", mulai="2027-01-01", menggantikan=["PX-THP-01"]),
        _aturan("UJI-THP-P1", "px_thp", "0", mulai="2026-07-01", menggantikan=["PX-THP-01"]),
        # aturan lama yang punya `sampai` sendiri (PX-THP-DTP1: 2026-12-31) juga dipendekkan
        _aturan("UJI-DTP-P", "px_dtp_tunai", "0", mulai="2026-07-01", menggantikan=["PX-THP-DTP1"]),
        _aturan("UJI-GU-S", "px_tunjangan_pajak_tunai", "0", mulai="2027-01-01", sampai="2027-12-31",
                menggantikan=["PX-THP-GU1"]))
    efektif = masa_berlaku_efektif(muat_kb([*BERKAS_PX, _tulis(tmp_path, "e.yaml", isi)]))
    assert efektif["PX-THP-01"] == (date(2016, 1, 1), date(2026, 6, 30))
    assert efektif["PX-THP-DTP1"] == (date(2025, 1, 1), date(2026, 6, 30))
    assert efektif["PX-THP-DTP0"] == (date(2016, 1, 1), date(2024, 12, 31))
    assert efektif["PX-THP-GU1"] == (date(2024, 1, 1), None)
    # berantai: tiap aturan dipendekkan oleh penggantinya sendiri (masa berlaku menurut tanggal, bukan masa efektif)
    rantai = masa_berlaku_efektif(muat_kb([*BERKAS_PX, _tulis(tmp_path, "rantai.yaml", _rantai_thp())]))
    assert rantai["PX-THP-01"] == (date(2016, 1, 1), date(2025, 12, 31))
    assert rantai["UJI-THP-X"] == (date(2026, 1, 1), date(2026, 6, 30)) and rantai["UJI-THP-Z"] == (date(2026, 7, 1), None)


# ------------------------------------------------------------------------------------------- M9 field tidak dipakai

# Sidik sha256 hasil lengkap (per_masa, tahunan, peringatan, titik_tetap, jejak; urutan kunci dipertahankan) Karyawan A
# dari pohon SEBELUM field `menggantikan` ada (commit 4df7554). KB dasar tidak memakai field itu, jadi keluarannya harus
# identik sampai ke byte. Bila KB dasar atau engine sengaja diubah sehingga hasil Karyawan A berubah, sidik ini
# diperbarui bersama perubahan itu: _sidik(tahun, metode, dengan_px) mencetak nilai barunya.
BAGIAN_HASIL = ("per_masa", "tahunan", "peringatan", "titik_tetap", "jejak")
SIDIK_SEBELUM = {
    (2023, "gross", True): "6e6618d8c6425c5335132c4a1da4aa06b2a539b39871000c241059561540b2ba",
    (2024, "gross", True): "d077cb8e7ad687daee115f2d3775b7e6d0f52876014dfd533e9e847f6c7b579a",
    (2025, "gross", True): "0bdaf815363f05bd691366d9041a46c18b4e4615b376e0079b5b675787ab7077",
    (2026, "gross", True): "0bdaf815363f05bd691366d9041a46c18b4e4615b376e0079b5b675787ab7077",
    (2027, "gross", True): "e871ffacc61c6ed855554ef94db565d630ea80728d744b0567951e9a9692a896",
    (2023, "gross_up", True): "4d4531abde21701722b6704d797fff3ad48661b1bedd676b4fe73ab7f2d3361d",
    (2024, "gross_up", True): "4907b6f6f21d57c109d4c3a4ee54375e5f8d1aa86d2a5b8a25d393761239af6c",
    (2025, "gross_up", True): "b357fdf81ecd6cafae7ea658960a3c199d106e8e5cb4c54d7dd61d772f76f4ac",
    (2026, "gross_up", True): "b357fdf81ecd6cafae7ea658960a3c199d106e8e5cb4c54d7dd61d772f76f4ac",
    (2027, "gross_up", True): "f519cebdf1576fcd66298cc4d0cb30a67c318533a5f7c9b5eff1ee0f3fc688d1",
    (2023, "gross", False): "e5eb49941cc06dc7982d3e3a58c37165eeda56faa32b01dde0172b1144709ebf",
    (2024, "gross", False): "04e57912a29c3bebf0c50fe7aa8b09fdfeddf34c27d5ec8ae343ac241d1a3ca5",
    (2025, "gross", False): "2e503a5a0048f1fad4d87a112de315a4b08e3fe0e8f98800d9722b92b381aedc",
    (2026, "gross", False): "2e503a5a0048f1fad4d87a112de315a4b08e3fe0e8f98800d9722b92b381aedc",
    (2027, "gross", False): "04e57912a29c3bebf0c50fe7aa8b09fdfeddf34c27d5ec8ae343ac241d1a3ca5",
    (2023, "gross_up", False): "4d4531abde21701722b6704d797fff3ad48661b1bedd676b4fe73ab7f2d3361d",
    (2024, "gross_up", False): "214df09d77e75e2b6d3a41361b7b01298d2deaeb83344609816c969b1e959925",
    (2025, "gross_up", False): "35cb9839d07eb8224cec58ba29874c209a2ce5da93663a15e539cd45dc9534a2",
    (2026, "gross_up", False): "35cb9839d07eb8224cec58ba29874c209a2ce5da93663a15e539cd45dc9534a2",
    (2027, "gross_up", False): "214df09d77e75e2b6d3a41361b7b01298d2deaeb83344609816c969b1e959925",
}


def _sidik(tahun, metode, dengan_px):
    try:
        h = hitung(_kasus(tahun, metode), berkas_perusahaan=BERKAS_PX if dengan_px else ())
        teks = json.dumps({k: h[k] for k in BAGIAN_HASIL}, ensure_ascii=False, default=str)
    except KasusTidakDidukung as e:   # gross-up rezim PER-16 (2023) ditolak KB: pesannya yang dibandingkan
        teks = f"{type(e).__name__}: {e}"
    return hashlib.sha256(teks.encode("utf-8")).hexdigest()


@pytest.mark.parametrize("tahun, metode, dengan_px", sorted(SIDIK_SEBELUM))
def test_tanpa_field_menggantikan_hasil_lengkap_identik_dengan_sebelum_perubahan(tahun, metode, dengan_px):
    assert _sidik(tahun, metode, dengan_px) == SIDIK_SEBELUM[(tahun, metode, dengan_px)]


def test_tanpa_field_menggantikan_jejak_tidak_mendapat_kunci_baru():
    assert len(SIDIK_SEBELUM) == 20
    for tahun, metode in ((2023, "gross"), (2026, "gross"), (2026, "gross_up")):
        h = _dasar(tahun, metode)
        assert h["jejak"] and all(list(j) == KUNCI_JEJAK for j in h["jejak"])
