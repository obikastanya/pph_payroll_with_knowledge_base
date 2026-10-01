"""V3 — relasi metamorfik & properti (research_plan.md §9.3, MR1-MR15) pada engine KB."""
import copy
from fractions import Fraction

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from engine.kalkulator import hitung

STATUS = ["TK/0", "TK/1", "TK/2", "TK/3", "K/0", "K/1", "K/2", "K/3"]
CFG = settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])


def _kasus(tahun, status, gaji, bonus_bulan=None, bonus=0, iuran=0, zakat=0, masuk=1, keluar=12, metode="gross",
           tunjangan=0):
    masa = []
    for b in range(masuk, keluar + 1):
        k = [{"kode": "gaji", "kategori": "teratur", "satuan_periode": "bulan", "nominal": gaji}]
        if tunjangan:
            k.append({"kode": "tunjangan", "kategori": "teratur", "satuan_periode": "bulan", "nominal": tunjangan})
        if bonus_bulan == b and bonus:
            k.append({"kode": "bonus", "kategori": "tidak_teratur", "satuan_periode": "bulan", "nominal": bonus})
        if iuran:
            k.append({"kode": "iuran_pensiun_pegawai", "kategori": "iuran_pengurang", "satuan_periode": "bulan", "nominal": iuran})
        if zakat:
            k.append({"kode": "zakat", "kategori": "zakat", "satuan_periode": "bulan", "nominal": zakat})
        masa.append({"bulan": b, "komponen": k})
    return {"id": "MR", "tahun_pajak": tahun, "cakupan": "setahun", "metode": metode, "kurs": {}, "dtp": {},
            "pegawai": {"status_ptkp": status, "jenis_kelamin": "L", "punya_npwp": True, "subjektif_mulai_bulan": None,
                        "subjektif_akhir_bulan": None, "bulan_masuk": masuk if masuk > 1 else None,
                        "bulan_terakhir_bekerja": keluar if keluar < 12 else None, "periode_gaji": "bulanan",
                        "hari_kerja_sebulan": None},
            "pemberi_kerja": {"klu": None, "jenis": "biasa"}, "masa": masa, "harapan": []}


tahun_s = st.sampled_from([2023, 2024, 2025, 2026])
gaji_s = st.integers(0, 150_000_000)
status_s = st.sampled_from(STATUS)


@CFG
@given(tahun=tahun_s, status=status_s, gaji=gaji_s, tambah=st.integers(1, 20_000_000), bulan=st.integers(1, 11))
def test_mr1_bruto_naik_pph_tidak_turun(tahun, status, gaji, tambah, bulan):
    a = hitung(_kasus(tahun, status, gaji))
    k = _kasus(tahun, status, gaji)
    k["masa"][bulan - 1]["komponen"].append({"kode": "lembur", "kategori": "teratur", "satuan_periode": "bulan", "nominal": tambah})
    b = hitung(k)
    assert b["per_masa"][bulan]["pph21"] >= a["per_masa"][bulan]["pph21"]
    assert b["tahunan"]["pph21_setahun"] >= a["tahunan"]["pph21_setahun"]


@CFG
@given(tahun=tahun_s, gaji=gaji_s, n=st.integers(0, 2), kawin=st.booleans())
def test_mr2_tanggungan_bertambah_pph_setahun_tidak_naik(tahun, gaji, n, kawin):
    p = "K" if kawin else "TK"
    a = hitung(_kasus(tahun, f"{p}/{n}", gaji))["tahunan"]["pph21_setahun"]
    b = hitung(_kasus(tahun, f"{p}/{n + 1}", gaji))["tahunan"]["pph21_setahun"]
    assert b <= a


@CFG
@given(tahun=tahun_s, status=status_s, gaji=gaji_s, bonus=st.integers(0, 300_000_000), bb=st.integers(1, 12),
       iuran=st.integers(0, 500_000), masuk=st.integers(1, 6), keluar=st.integers(7, 12))
def test_mr3_mr12_buku_besar(tahun, status, gaji, bonus, bb, iuran, masuk, keluar):
    """Sum PPh semua masa = PPh setahun; bruto & neto setahun merekonsiliasi komponen."""
    assume(masuk <= bb <= keluar or bonus == 0)
    h = hitung(_kasus(tahun, status, gaji, bb, bonus, iuran, 0, masuk, keluar))
    t = h["tahunan"]
    assert sum(m["pph21"] for m in h["per_masa"].values()) == t["pph21_setahun"]
    assert t["bruto_setahun"] == sum(m["bruto_total_masa"] for m in h["per_masa"].values())
    assert t["neto_setahun"] == t["bruto_setahun"] - t["biaya_jabatan"] - t["iuran_pengurang"] - t["zakat"]
    assert t["pkp"] % 1000 == 0 and t["pkp"] >= 0


@CFG
@given(tahun=st.sampled_from([2024, 2025, 2026]), status=status_s, gaji=st.integers(1_000_000, 100_000_000))
def test_mr4_gross_up_tunjangan_sama_dengan_pph(tahun, status, gaji):
    h = hitung(_kasus(tahun, status, gaji, metode="gross_up"))
    for b, m in h["per_masa"].items():
        assert m["tunjangan_pajak"] == m["pph21"], b
    assert h["tahunan"]["tunjangan_pajak_akhir"] == h["tahunan"]["pph21_masa_terakhir"]


@CFG
@given(tahun=st.sampled_from([2024, 2025, 2026]), status=status_s, gaji=gaji_s, bonus=st.integers(1, 300_000_000),
       b1=st.integers(1, 11), b2=st.integers(1, 11))
def test_mr5_pindah_bulan_bonus_total_setahun_tetap(tahun, status, gaji, bonus, b1, b2):
    a = hitung(_kasus(tahun, status, gaji, b1, bonus))["tahunan"]["pph21_setahun"]
    b = hitung(_kasus(tahun, status, gaji, b2, bonus))["tahunan"]["pph21_setahun"]
    assert a == b


@CFG
@given(tahun=tahun_s, status=status_s, gaji=gaji_s, tunj=st.integers(2, 20_000_000), potong=st.integers(1, 100))
def test_mr6_memecah_komponen_tidak_mengubah_hasil(tahun, status, gaji, tunj, potong):
    a = hitung(_kasus(tahun, status, gaji, tunjangan=tunj))
    k = _kasus(tahun, status, gaji)
    bagian = tunj * potong // 101
    for m in k["masa"]:
        m["komponen"] += [{"kode": "tunjangan_a", "kategori": "teratur", "satuan_periode": "bulan", "nominal": bagian},
                          {"kode": "tunjangan_b", "kategori": "teratur", "satuan_periode": "bulan", "nominal": tunj - bagian}]
    b = hitung(k)
    assert a["per_masa"] == b["per_masa"] and a["tahunan"] == b["tahunan"]


def test_mr7_aturan_di_luar_masa_berlaku_tidak_mengubah_hasil(tmp_path):
    """Isolasi temporal: menambah aturan perusahaan yang berlaku 2030 tidak mengubah output 2023-2026."""
    p = tmp_path / "masa_depan.yaml"
    p.write_text('''lapisan: perusahaan
aturan:
  - id: PX-UJI-2030
    sifat: opsional
    berlaku: {mulai: 2030-01-01}
    lingkup: tahun
    menghasilkan: ptkp
    maka: "0"
    tipe_hasil: rupiah
    sumber: "uji isolasi temporal"
''', encoding="utf-8")
    for tahun in (2023, 2024, 2025, 2026):
        k = _kasus(tahun, "K/1", 25_000_000, 6, 40_000_000, 100_000)
        a, b = hitung(k), hitung(k, berkas_perusahaan=[p])
        assert a["per_masa"] == b["per_masa"] and a["tahunan"] == b["tahunan"], tahun


@CFG
@given(status=status_s, gaji=gaji_s)
def test_mr9_kategori_ter_hanya_bergantung_status(status, gaji):
    h = hitung(_kasus(2024, status, gaji))
    kat = {m.get("kategori_ter") for b, m in h["per_masa"].items() if b != 12}
    assert kat == {{"TK/0": "A", "TK/1": "A", "K/0": "A", "K/3": "C"}.get(status, "B")}


@CFG
@given(tahun=tahun_s, status=status_s, gaji=st.integers(0, 4_000_000))
def test_mr10_neto_di_bawah_ptkp_pajak_nol(tahun, status, gaji):
    h = hitung(_kasus(tahun, status, gaji))
    if h["tahunan"]["neto_setahun"] <= h["tahunan"]["ptkp"]:
        assert h["tahunan"]["pph21_setahun"] == 0


@CFG
@given(tahun=st.sampled_from([2024, 2025, 2026]), status=status_s, gaji=gaji_s, bonus=st.integers(0, 50_000_000))
def test_mr13_isolasi_pembulatan(tahun, status, gaji, bonus):
    """Mengganti mode BULAT-TER-01 hanya boleh memengaruhi fakta turunan pph21_berjalan."""
    k = _kasus(tahun, status, gaji, 3, bonus)
    a, b = hitung(k), hitung(k, {"BULAT-TER-01": "setengah_menjauhi_nol"})
    for f in ("bruto_setahun", "biaya_jabatan", "neto_setahun", "ptkp", "pkp", "pph21_setahun"):
        assert a["tahunan"][f] == b["tahunan"][f], f


@CFG
@given(tahun=tahun_s, status=status_s, gaji=gaji_s, tunj=st.integers(0, 10_000_000), bonus=st.integers(0, 50_000_000))
def test_mr15_urutan_komponen_tidak_berpengaruh(tahun, status, gaji, tunj, bonus):
    k = _kasus(tahun, status, gaji, 5, bonus, 100_000, 0, 1, 12, "gross", tunj)
    k2 = copy.deepcopy(k)
    for m in k2["masa"]:
        m["komponen"].reverse()
    a, b = hitung(k), hitung(k2)
    assert a["per_masa"] == b["per_masa"] and a["tahunan"] == b["tahunan"]


def test_mr14_sumbu_waktu_transaksi():
    """THR dibayar 28-03 untuk Lebaran April -> masa Maret; geser dalam bulan yang sama tidak berpengaruh;
    gaji Desember dibayar Januari tetap masa Desember; rapel terutang tahun berikut dikeluarkan."""
    def dengan(transaksi):
        k = _kasus(2024, "TK/0", 10_000_000)
        k["transaksi"] = transaksi
        return hitung(k)
    thr = lambda bayar: {"komponen": "thr", "kategori": "tidak_teratur", "nominal": 10_000_000, "periode_kerja": "2024-04",
                         "tanggal_terutang": "2024-04-10", "tanggal_bayar": bayar}
    a, b, c = dengan([thr("2024-03-28")]), dengan([thr("2024-03-02")]), dengan([thr("2024-04-05")])
    assert a["per_masa"] == b["per_masa"]
    assert a["per_masa"][3]["bruto"] == 20_000_000 and c["per_masa"][4]["bruto"] == 20_000_000
    assert a["tahunan"]["pph21_setahun"] == c["tahunan"]["pph21_setahun"]
    rapel = {"komponen": "rapel", "kategori": "tidak_teratur", "nominal": 3_000_000, "periode_kerja": "2024-11",
             "tanggal_terutang": "2025-01-15", "tanggal_bayar": "2025-01-25"}
    d = dengan([rapel])
    assert any(p["kode"] == "TRANSAKSI_TAHUN_LAIN" for p in d["peringatan"])
    assert d["tahunan"]["bruto_setahun"] == 120_000_000


@CFG
@given(status=status_s, gaji=st.integers(1_000_000, 80_000_000), bonus=st.integers(0, 40_000_000))
def test_ditanggung_pemberi_kerja_setara_gross_up_sejak_2024(status, gaji, bonus):
    """REG-DITANGGUNG-02 (PMK 168 Lamp. B I.4): PPh ditanggung pemberi kerja = kenikmatan -> full gross-up."""
    a = hitung(_kasus(2024, status, gaji, 6, bonus, metode="gross_up"))
    b = hitung(_kasus(2024, status, gaji, 6, bonus, metode="ditanggung_pemberi_kerja"))
    assert a["per_masa"] == b["per_masa"] and a["tahunan"] == b["tahunan"]


@CFG
@given(tahun=st.sampled_from([2025, 2026]), klu=st.sampled_from(["13111", "55110", "14111", "79121"]),
       gaji=st.integers(0, 15_000_000), status=status_s)
def test_dtp_terdefinisi_setiap_masa(tahun, klu, gaji, status):
    """Bila KLU tersedia, pph21_dtp terdefinisi di SETIAP masa (termasuk masa terakhir dengan PPh = 0)."""
    k = _kasus(tahun, status, gaji)
    k["pemberi_kerja"]["klu"] = klu
    h = hitung(k)
    for b, m in h["per_masa"].items():
        assert "pph21_dtp" in m, b
        assert 0 <= m["pph21_dtp"] <= m["pph21"] or m["pph21"] < 0, (b, m["pph21_dtp"], m["pph21"])
