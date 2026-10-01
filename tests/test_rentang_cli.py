"""Rentang tafsir (§6.9.6) dan CLI."""
import json

from eksperimen.v1 import DIR_KANONIK
from engine import cli
from engine.kalkulator import hitung


def _k(nama):
    return json.loads((DIR_KANONIK / f"{nama}.json").read_text(encoding="utf-8"))


def test_rentang_tafsir_bj_pmk10():
    h = hitung(_k("PMK10-B-3"), dengan_rentang=True)
    r = {(x["tafsir"], x["fakta"]): x for x in h["rentang_tafsir"]}
    assert r[("REG-BJ-02", "pph21_setahun")]["selisih"] == 10_000
    assert r[("REG-BJ-02", "biaya_jabatan")]["selisih"] == -200_000
    assert any(p["kode"] == "AMBIGU_TAFSIR" and p["tafsir"] == "REG-BJ-02" for p in h["peringatan"])


def test_kasus_tanpa_ambiguitas_rentang_kosong():
    h = hitung(_k("PP58-Penj-Ps2-1"), dengan_rentang=True)
    assert h["rentang_tafsir"] == []


def test_rentang_gross_up_ganda_terlihat():
    h = hitung(_k("PMK168-B-I.4"), dengan_rentang=True)
    assert all(x["tafsir"] != "BULAT-TER-01" or x["selisih"] for x in h["rentang_tafsir"])


def test_cli_berjalan(capsys):
    cli.main([str(DIR_KANONIK / "PMK168-B-I.1.json"), "--jejak"])
    keluar = capsys.readouterr().out
    assert "14.595.000" in keluar and "REG-MT-02" in keluar and "PMK 168/2023" in keluar
