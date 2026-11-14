"""Model tiga tanggal (research_plan.md §6.9.4) — strata S8."""
from datetime import date

import pytest

from engine.angka import PelanggaranPresisi
from engine.waktu import (TAFSIR_WAKTU_2023, InputTidakValid, TransaksiPenghasilan,
                          pastikan_berurutan, pastikan_tahun_pajak)


def _t(**ubah):
    d = dict(komponen="gaji_pokok", nominal=10_000_000, periode_kerja="2024-12",
             tanggal_terutang="2024-12-31", tanggal_bayar="2025-01-03")
    d.update(ubah)
    return TransaksiPenghasilan.dari_data(d)


def test_gaji_desember_dibayar_januari_tetap_masa_desember():
    t = _t()
    assert t.saat_terutang == date(2024, 12, 31)
    assert t.masa_pajak == (2024, 12) and t.tahun_pajak == 2024
    assert t.periode_iuran == (2024, 12)


def test_thr_dibayar_sebelum_lebaran_masuk_masa_pembayaran():
    t = _t(komponen="thr", periode_kerja="2024-04", tanggal_terutang="2024-04-01", tanggal_bayar="2024-03-28")
    assert t.masa_pajak == (2024, 3)


def test_rapel_lintas_tahun_masuk_tahun_terutang():
    t = _t(komponen="rapel", periode_kerja="2023-11", tanggal_terutang="2024-01-15", tanggal_bayar="2024-01-25")
    assert t.masa_pajak == (2024, 1)
    assert t.periode_iuran == (2023, 11)  # parameter BPJS tetap mengikuti periode kerja


def test_belum_dibayar_memakai_tanggal_terutang():
    assert _t(tanggal_bayar=None).masa_pajak == (2024, 12)


def test_mr14_geser_tanggal_bayar_dalam_bulan_yang_sama_tidak_mengubah_masa():
    a = _t(komponen="thr", tanggal_terutang="2024-04-10", tanggal_bayar="2024-04-02")
    b = _t(komponen="thr", tanggal_terutang="2024-04-10", tanggal_bayar="2024-04-09")
    c = _t(komponen="thr", tanggal_terutang="2024-04-10", tanggal_bayar="2024-03-31")
    assert a.masa_pajak == b.masa_pajak == (2024, 4)
    assert c.masa_pajak == (2024, 3)


def test_tafsir_waktu_2023_ditandai():
    t = _t(periode_kerja="2023-04", tanggal_terutang="2023-04-01", tanggal_bayar="2023-02-28")
    assert t.masa_pajak == (2023, 2)              # kasus K-11 (THR xlsx ditransfer 28-02-2023)
    assert t.tafsir_waktu() == [TAFSIR_WAKTU_2023]
    assert _t().tafsir_waktu() == []              # 2024: PMK 168 Ps. 19(1) eksplisit


@pytest.mark.parametrize("ubah,pesan", [
    (dict(nominal=1.5), "int rupiah"), (dict(nominal=True), "int rupiah"), (dict(nominal=-1), "negatif"),
    (dict(nominal=None), "DATA_KURANG"), (dict(tanggal_terutang=""), "DATA_KURANG"),
    (dict(periode_kerja="2024-13"), "periode"), (dict(periode_kerja="12-2024"), "periode"),
    (dict(tanggal_bayar="2024-02-30"), "tanggal tidak valid"),
])
def test_input_tidak_valid_menghentikan(ubah, pesan):
    with pytest.raises(InputTidakValid, match=pesan):
        _t(**ubah)


def test_invarian_urutan_tanggal():
    with pytest.raises(InputTidakValid):
        pastikan_berurutan(date(2024, 5, 1), date(2024, 4, 30), "tanggal_masuk", "tanggal_keluar")
    pastikan_berurutan(date(2024, 5, 1), date(2024, 5, 1), "tanggal_masuk", "tanggal_keluar")


def test_transaksi_tahun_lain_ditolak():
    with pytest.raises(PelanggaranPresisi):
        pastikan_tahun_pajak(_t(tanggal_terutang="2025-01-02", tanggal_bayar=None), 2024)
