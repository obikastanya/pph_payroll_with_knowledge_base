"""E3 — perubahan aturan tanpa perubahan kode: bitemporal (C04) dan skenario cepat C03/C14."""
import json
from datetime import date

from eksperimen import perubahan
from eksperimen.v1 import DIR_KANONIK
from engine.kalkulator import hitung


def test_c04_dtp_berlaku_surut_knowledge_time():
    k = json.loads((DIR_KANONIK / "PMK10-B-1.json").read_text(encoding="utf-8"))
    saat_itu = hitung(k, per_tanggal_kb=date(2025, 1, 31))
    seharusnya = hitung(k, per_tanggal_kb=date(2025, 2, 5))
    assert "pph21_dtp" not in saat_itu["per_masa"][1]
    assert seharusnya["per_masa"][1]["pph21_dtp"] == 120_000
    assert hitung(k)["per_masa"] == seharusnya["per_masa"]           # tanpa per_tanggal = KB terbaru


def test_c03_batas_jp_tanpa_ubah_kode():
    h = perubahan.c03()
    assert h["impact_px_iuran_jp_pg"]["f1"] == 1.0 and h["regresi_2025"] == 0 and h["baris_kb"] == 6


def test_c14_ptkp_berversi_isolasi_temporal():
    h = perubahan.c14()
    assert h["impact_pph21_setahun"]["f1"] == 1.0 and h["regresi_2023_2026_identik"]
