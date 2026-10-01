"""E8 — lapisan perusahaan Perusahaan X vs xlsx v8 (B0): komponen payroll identik; selisih pajak terjelaskan."""
import pytest

from eksperimen.e8_perusahaan_x import BERKAS_PX, bandingkan, kasus_kar_a, keluaran_xlsx
from engine.kalkulator import hitung

KOMPONEN_IDENTIK = ["px_gaji", "px_tunjangan", "px_premi_jkm", "px_premi_jkk", "px_premi_jht_pk", "px_premi_jp_pk",
                    "px_iuran_jp_pg", "px_iuran_jht_pg", "px_kompensasi", "px_ota", "px_lembur", "px_komisi"]


@pytest.fixture(scope="module")
def e8():
    return hitung(kasus_kar_a(2023), berkas_perusahaan=BERKAS_PX), keluaran_xlsx()


def test_komponen_payroll_identik_dengan_xlsx(e8):
    h, xl = e8
    beda = [r for r in bandingkan(h, xl) if r["fakta"] in KOMPONEN_IDENTIK and not r["sama"]]
    assert beda == []


def test_konflik_lembur_terdeteksi(e8):
    h, _ = e8
    k = [p for p in h["peringatan"] if p["kode"] == "KONFLIK_WAJIB"]
    assert len(k) == 1 and k[0]["fakta"] == "px_lembur" and k[0]["kategori_wajib"] == "teratur"


def test_selisih_hanya_di_lokasi_temuan_audit(e8):
    """K-04 (BPJS Kes Desember), K-11 (THR Februari) adalah satu-satunya selisih komponen."""
    h, xl = e8
    beda = {(r["fakta"], r["bulan"]) for r in bandingkan(h, xl) if not r["sama"] and r["fakta"].startswith("px_")}
    assert beda == {("px_premi_kes", 12), ("px_iuran_kes_pg", 12), ("px_thr", 2), ("px_thr", 4)}


def test_selisih_pph_setahun_dijelaskan_k04(e8):
    """PPh setahun KB - xlsx = 15% x (PKP selisih) dan PKP selisih = premi BPJS Kes Desember (dibulatkan ribuan)."""
    h, xl = e8
    t = h["tahunan"]
    assert t["pkp"] - 88_570_000 == 375_000                      # xlsx PKP setahun (Q28)
    assert t["pph21_setahun"] - xl["pph21_setahun"]["setahun"] == 56_250
    assert h["per_masa"][12]["px_premi_kes"] == 375_152


@pytest.mark.parametrize("tahun", [2024, 2025, 2026])
def test_rezim_ter_tanpa_perubahan_kode(tahun):
    """Pegawai & kebijakan sama, rezim berbeda: PPh setahun sama (TER hanya mengubah distribusi bulanan)."""
    h23 = hitung(kasus_kar_a(2023), berkas_perusahaan=BERKAS_PX)
    h = hitung(kasus_kar_a(tahun), berkas_perusahaan=BERKAS_PX)
    assert h["tahunan"]["pph21_setahun"] == h23["tahunan"]["pph21_setahun"]
    assert sum(m["pph21"] for m in h["per_masa"].values()) == h["tahunan"]["pph21_setahun"]
    assert "tarif_ter" in h["per_masa"][1] and "tarif_ter" not in h23["per_masa"][1]
