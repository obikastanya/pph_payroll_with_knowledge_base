"""Interval (a, b] dan tabel bertingkat (research_plan.md §6.9.3), diuji terhadap contoh resmi (V1)."""
import glob
from fractions import Fraction
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from engine.angka import PelanggaranPresisi
from engine.interval import Lapisan, TabelBertingkat, pajak_progresif, tabel_pasal17, tabel_ter
from engine.muat import muat_json_eksak, muat_registri_pembulatan, muat_tabel

ROOT = Path(__file__).resolve().parents[1]
JUMLAH_LAPISAN = {"A": 44, "B": 40, "C": 41}
# Erratum contoh resmi yang sudah terkonfirmasi dari gambar halaman (research_plan.md §9.1).
# Protokol: selisih HARUS muncul tepat di sini, tidak di tempat lain.
ERRATUM_TER = {("PMK168-B-I.6", 1)}


@pytest.fixture(scope="module")
def ter():
    baris = muat_tabel("ter_bulanan")
    return {k: tabel_ter(baris, k) for k in "ABC"}


@pytest.fixture(scope="module")
def p17():
    baris = muat_tabel("tarif_pasal17")
    return {"hpp": tabel_pasal17(baris, "UU HPP"), "lama": tabel_pasal17(baris, "UU 36/2008 (pra-HPP)")}


def test_tabel_ter_valid_dan_monoton(ter):
    for k, t in ter.items():
        assert len(t.lapisan) == JUMLAH_LAPISAN[k]
        assert t.monoton()


def test_setiap_batas_ter_b_min1_b_b_plus1(ter):
    """Semua 122 batas berhingga: b-1 dan b di lapisan i, b+1 di lapisan i+1."""
    n = 0
    for t in ter.values():
        for i, l in enumerate(t.lapisan[:-1]):
            b = l.atas
            assert t.cari(b) is l
            if b - 1 > l.bawah or l.bawah == 0:
                assert t.cari(b - 1) is l
            assert t.cari(b + 1) is t.lapisan[i + 1]
            n += 1
    assert n == 43 + 39 + 40


def test_contoh_proposal_batas_15_1_juta(ter):
    assert ter["A"].cari(15_100_000).tarif == Fraction(6, 100)
    assert ter["A"].cari(15_100_001).tarif == Fraction(7, 100)
    assert ter["A"].cari(0).tarif == 0 and ter["A"].cari(5_400_000).tarif == 0
    assert ter["A"].cari(5_400_001).tarif == Fraction(25, 10_000)


@pytest.mark.parametrize("x", [Fraction(5_400_001, 1) / 2, 5_400_000.0, True, -1, "5400000"])
def test_lookup_menolak_non_int_dan_negatif(ter, x):
    with pytest.raises(PelanggaranPresisi):
        ter["A"].cari(x)


def _l(bawah, atas, t="0.05"):
    return Lapisan(bawah, atas, Fraction(t))


@pytest.mark.parametrize("lapisan,pesan", [
    ([_l(0, 100), _l(101, None)], "celah"),
    ([_l(0, 100), _l(99, None)], "tumpang tindih"),
    ([_l(1, 100), _l(100, None)], "mulai dari 0"),
    ([_l(0, 100), _l(100, 200)], "tak terbatas"),
    ([_l(0, 100), _l(100, None, "1")], r"di luar \[0, 1\)"),
    ([Lapisan(0, 100.0, Fraction(0)), _l(100, None)], "bukan int"),
])
def test_tabel_cacat_ditolak(lapisan, pesan):
    with pytest.raises(PelanggaranPresisi, match=pesan):
        TabelBertingkat("uji", lapisan)


def _entri_ter_resmi():
    for f in sorted(glob.glob(str(ROOT / "dataset/07_kasus_uji_resmi/*.json"))):
        d = muat_json_eksak(f)
        if not isinstance(d, dict) or not d.get("dalam_lingkup", False):
            continue
        for m in (d.get("expected") or {}).get("per_masa") or []:
            if all(m.get(k) is not None for k in ("bruto", "kategori_ter", "tarif_ter", "pph21")):
                yield d["id"], m["bulan"], m


def test_v1_ter_bulanan_resmi(ter):
    """V1: 170 perhitungan TER bulanan resmi. Tarif dari lookup harus sama; PPh harus sama
    kecuali TEPAT di lokasi erratum terkonfirmasi."""
    reg = muat_registri_pembulatan()
    entri = list(_entri_ter_resmi())
    assert len(entri) == 170
    selisih = set()
    for id_, bulan, m in entri:
        lap = ter[m["kategori_ter"]].cari(m["bruto"])
        assert lap.tarif == m["tarif_ter"], (id_, bulan)
        for mode, hasil in reg.semua_varian("BULAT-TER-01", lap.tarif * m["bruto"]).items():
            if hasil != m["pph21"]:
                selisih.add((id_, bulan))
    assert selisih == ERRATUM_TER


def test_kasus_acuan_k1_10_juta(ter):
    """Kasus acuan (bukan V1; perhitungan tangan di dataset/03_pembanding/README.md §5):
    K/1, gaji 10.000.000 + JKK 0,24% + JKM 0,3% + BPJS Kes 4% = bruto 10.454.000 -> TER B 1,5%."""
    lap = ter["B"].cari(10_454_000)
    assert lap.tarif == Fraction(15, 1000)
    assert lap.tarif * 10_454_000 == 156_810


def test_pasal17_nilai_dasar(p17):
    t = p17["hpp"]
    assert pajak_progresif(t, 60_000_000) == 3_000_000
    # 60jt x 5% + 190jt x 15% + 50jt x 25% = 44 jt (teknologi-umum/pph21 menghasilkan 39 jt; README §6.5)
    assert pajak_progresif(t, 300_000_000) == 44_000_000
    assert pajak_progresif(t, 0) == 0


@given(k=st.integers(0, 10**7))
def test_pasal17_atas_pkp_ribuan_selalu_bulat(p17, k):
    """Dasar BULAT-P17-01: PKP kelipatan Rp1.000 x tarif 5/15/25/30/35% selalu rupiah bulat."""
    assert pajak_progresif(p17["hpp"], k * 1000).denominator == 1


def _pasangan_pasal17_resmi():
    for f in sorted(glob.glob(str(ROOT / "dataset/07_kasus_uji_resmi/*.json"))):
        d = muat_json_eksak(f)
        if isinstance(d, dict):
            t = (d.get("expected") or {}).get("tahunan") or {}
            if "pkp" in t and "pph21_setahun" in t:
                yield d, t


def test_v1_pasal17_resmi(p17):
    """V1: 25 perhitungan setahun resmi. PER-16 (contoh 2016) memakai tarif pra-HPP.

    Bagian tahun pajak: Pasal 17 atas neto disetahunkan, lalu diproporsikan n/12 (PMK 168 Ps. 15(3)).
    """
    reg = muat_registri_pembulatan()
    pasangan = list(_pasangan_pasal17_resmi())
    assert len(pasangan) == 25
    proporsional = 0
    for d, t in pasangan:
        tabel = p17["lama"] if d["rezim"].startswith("PER16") else p17["hpp"]
        pph = pajak_progresif(tabel, t["pkp"])
        if "faktor_proporsi" in t:
            proporsional += 1
            assert pph == t["pph21_disetahunkan"], d["id"]
            pembilang, penyebut = (int(x) for x in t["faktor_proporsi"].split("/"))
            pph = reg.terapkan("BULAT-PROPORSI-01", pph * Fraction(pembilang, penyebut))
        assert pph == t["pph21_setahun"], d["id"]
    assert proporsional == 2
