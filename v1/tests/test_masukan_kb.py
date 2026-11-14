"""Berkas KB tambahan: deklarasi `masukan` (input baru dari pengguna), amandemen `parameter`, dan komponen baru.

Skenario: peraturan perusahaan baru memberi uang transport per hari hadir. Aturannya cukup berupa berkas KB tambahan;
engine, rumus PPh, dan rumus take home pay tidak diubah.
"""
import copy
from datetime import date

import pytest

from eksperimen.e12_tanpa_kb import BERKAS_PX
from eksperimen.e8_perusahaan_x import kasus_kar_a
from engine.kalkulator import hitung
from engine.kb import muat_kb, parameter_pada, rujukan_masukan
from engine.muat import KesalahanKB

TRANSPORT = """
lapisan: perusahaan
id: transport_2024
komponen:
  - {fakta: px_transport, jenis: tunjangan_transport, kategori: teratur, label: "Uang transport"}
masukan:
  - kunci: uang_transport_per_hari
    label: "Uang transport per hari hadir"
    tipe: rupiah
    lingkup: tahun
    wajib: false
    bawaan: 0
    sumber: "Peraturan Perusahaan 2024 Ps. 12"
aturan:
  - id: PXT-TRANSPORT-01
    sifat: opsional
    berlaku: {mulai: 2024-01-01}
    lingkup: masa
    menghasilkan: px_transport
    maka: "hr('uang_transport_per_hari') * hr_masa('hk_aktual')"
    tipe_hasil: rupiah
    sumber: "Peraturan Perusahaan 2024 Ps. 12: uang transport dibayar per hari hadir"
"""


def _tulis(tmp_path, nama, isi):
    p = tmp_path / nama
    p.write_text(isi, encoding="utf-8")
    return p


def _hitung(kasus, *tambahan):
    return hitung(kasus, berkas_perusahaan=[*BERKAS_PX, *tambahan])


def test_komponen_baru_dari_berkas_tambahan_masuk_bruto_dan_thp(tmp_path):
    berkas = _tulis(tmp_path, "transport.yaml", TRANSPORT)
    dasar = _hitung(kasus_kar_a(2024))
    kasus = kasus_kar_a(2024)
    kasus["data_hr"]["uang_transport_per_hari"] = 50_000
    h = _hitung(kasus, berkas)
    for b in range(1, 13):
        hadir = kasus["data_hr"]["per_masa"][str(b)]["hk_aktual"]
        assert h["per_masa"][b]["px_transport"] == 50_000 * hadir
        # komponen teratur baru ikut bruto & take home pay tanpa mengubah rumus PPh / THP
        assert h["per_masa"][b]["bruto"] == dasar["per_masa"][b]["bruto"] + 50_000 * hadir
        assert h["per_masa"][b]["px_penghasilan_tunai"] == dasar["per_masa"][b]["px_penghasilan_tunai"] + 50_000 * hadir
    assert h["tahunan"]["pph21_setahun"] > dasar["tahunan"]["pph21_setahun"]
    assert not [p for p in h["peringatan"] if p.get("kode") == "KONFLIK_WAJIB" and p.get("fakta") == "px_transport"]


def test_masukan_kosong_memakai_bawaan_deklarasi(tmp_path):
    berkas = _tulis(tmp_path, "transport.yaml", TRANSPORT)
    h = _hitung(kasus_kar_a(2024), berkas)
    assert all(m["px_transport"] == 0 for m in h["per_masa"].values())


def test_masukan_wajib_tanpa_bawaan_memberi_galat_berlabel(tmp_path):
    berkas = _tulis(tmp_path, "transport.yaml", TRANSPORT.replace("    wajib: false\n    bawaan: 0\n", "    wajib: true\n"))
    with pytest.raises(KesalahanKB, match=r"uang_transport_per_hari \(Uang transport per hari hadir\).*DATA_KURANG"):
        _hitung(kasus_kar_a(2024), berkas)


def test_lingkup_masukan_harus_cocok_dengan_cara_baca(tmp_path):
    salah = TRANSPORT.replace("lingkup: tahun\n    wajib", "lingkup: bulan\n    wajib")
    with pytest.raises(KesalahanKB, match="wajib dibaca dengan hr_masa"):
        muat_kb([*BERKAS_PX, _tulis(tmp_path, "t.yaml", salah)])


def test_bawaan_tidak_sesuai_tipe_ditolak(tmp_path):
    salah = TRANSPORT.replace("bawaan: 0", "bawaan: 'lima ribu'")
    with pytest.raises(KesalahanKB, match="tidak valid"):
        muat_kb([*BERKAS_PX, _tulis(tmp_path, "t.yaml", salah)])


def test_rujukan_masukan_mencakup_input_inti_dan_baru(tmp_path):
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "transport.yaml", TRANSPORT)])
    r = rujukan_masukan(kb)
    assert r["gaji_pokok"]["lingkup"] == {"tahun"}
    assert r["hk_aktual"]["lingkup"] == {"bulan"}
    assert r["uang_transport_per_hari"]["aturan"] == ["PXT-TRANSPORT-01"]
    assert kb.masukan["uang_transport_per_hari"].label == "Uang transport per hari hadir"


DPLK = """
lapisan: perusahaan
id: dplk_2024
komponen:
  - {fakta: px_iuran_dplk_pg, jenis: iuran_pensiun_dplk_pegawai, kategori: iuran_pengurang, label: "Iuran DPLK pegawai"}
masukan:
  - {kunci: iuran_dplk_bulanan, label: "Iuran DPLK pegawai per bulan", tipe: rupiah, lingkup: tahun, wajib: false, bawaan: 0}
aturan:
  - id: PXD-DPLK-01
    sifat: opsional
    berlaku: {mulai: 2024-01-01}
    lingkup: masa
    menghasilkan: px_iuran_dplk_pg
    maka: "hr('iuran_dplk_bulanan')"
    tipe_hasil: rupiah
    sumber: "Peraturan Perusahaan 2024 Ps. 20: iuran DPLK dipotong dari gaji"
"""


def test_potongan_baru_mengurangi_thp_dan_neto_tanpa_mengubah_rumus(tmp_path):
    dasar = _hitung(kasus_kar_a(2024))
    kasus = kasus_kar_a(2024)
    kasus["data_hr"]["iuran_dplk_bulanan"] = 200_000
    h = _hitung(kasus, _tulis(tmp_path, "dplk.yaml", DPLK))
    for b in range(1, 12):  # TER: iuran tidak mengubah PPh masa Jan-Nov; penghematan PPh terkumpul di Desember
        assert dasar["per_masa"][b]["px_thp"] - h["per_masa"][b]["px_thp"] == 200_000
    assert h["tahunan"]["iuran_pengurang"] == dasar["tahunan"]["iuran_pengurang"] + 12 * 200_000
    assert h["tahunan"]["pph21_setahun"] < dasar["tahunan"]["pph21_setahun"]
    # THP turun tepat sebesar iuran dikurangi PPh 21 yang ikut turun
    selisih_thp = sum(dasar["per_masa"][b]["px_thp"] - h["per_masa"][b]["px_thp"] for b in range(1, 13))
    assert selisih_thp == 12 * 200_000 - (dasar["tahunan"]["pph21_setahun"] - h["tahunan"]["pph21_setahun"])


AMANDEMEN_JP = """
lapisan: regulasi
id: jp_2026_amandemen
aturan: []
parameter:
  - nama: jp_batas_upah
    nilai: 11500000
    berlaku: {mulai: 2026-06-01}
    sumber: "Surat BPJS Ketenagakerjaan (simulasi amandemen)"
"""


def test_amandemen_parameter_menutup_versi_lama(tmp_path):
    lama = parameter_pada(muat_kb(), "jp_batas_upah", date(2026, 5, 1))
    kb = muat_kb([_tulis(tmp_path, "jp.yaml", AMANDEMEN_JP)])
    assert parameter_pada(kb, "jp_batas_upah", date(2026, 5, 31)) == lama
    assert parameter_pada(kb, "jp_batas_upah", date(2026, 6, 1)) == 11_500_000


def test_perusahaan_tidak_boleh_mengubah_parameter_regulasi(tmp_path):
    berkas = _tulis(tmp_path, "jp.yaml", AMANDEMEN_JP.replace("lapisan: regulasi", "lapisan: perusahaan"))
    with pytest.raises(KesalahanKB, match="lapisan perusahaan tidak boleh mengubahnya"):
        muat_kb([berkas])


def test_amandemen_yang_mendahului_versi_lama_ditolak(tmp_path):
    berkas = _tulis(tmp_path, "jp.yaml", AMANDEMEN_JP.replace("mulai: 2026-06-01", "mulai: 2015-01-01"))
    with pytest.raises(KesalahanKB, match="bentrok"):
        muat_kb([berkas])


def test_tanpa_berkas_tambahan_hasil_tidak_berubah():
    kasus = kasus_kar_a(2023)
    a = _hitung(copy.deepcopy(kasus))
    assert a["tahunan"]["pph21_setahun"] == 7_341_750
