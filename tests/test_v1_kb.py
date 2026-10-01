"""V1 untuk engine KB: 0 selisih tak terjelaskan pada seluruh kasus resmi kanonik (§9.1, H2a)."""
import json

import pytest

from engine.kalkulator import fakta, hitung
from eksperimen.v1 import DIR_KANONIK, jalankan, ringkas


def test_kb_stj_nol_pada_kasus_resmi():
    hasil = jalankan(hitung, fakta)
    c, stj = ringkas(hasil)
    gagal = [r for r in hasil if r["status"] in ("SELISIH", "TIDAK_DIHASILKAN")]
    assert stj == 0, gagal[:10]
    assert c["cocok"] >= 1185 and c["cocok_terkoreksi"] == 20 and c["cocok_tafsir"] == 8


@pytest.mark.parametrize("kasus_id", ["PMK168-B-I.1", "PMK10-B-3", "PER16-I.4.1", "PMK168-B-I.4"])
def test_jejak_lengkap_dan_berpasal(kasus_id):
    """Trace completeness (§11.5): setiap fakta keluaran memiliki aturan + sumber pasal."""
    kasus = json.loads((DIR_KANONIK / f"{kasus_id}.json").read_text(encoding="utf-8"))
    h = hitung(kasus)
    tercatat = {(j["fakta"], j["bulan"]) for j in h["jejak"]}
    for b, fs in h["per_masa"].items():
        for f in fs:
            assert (f, b) in tercatat, (f, b)
    for f in h["tahunan"]:
        assert (f, None) in tercatat, f
    assert all(j["sumber"].strip() for j in h["jejak"])


def test_tafsir_bj_menghasilkan_rentang_yang_tepat():
    """PMK10-B-3: varian (a) default vs (b) contoh PMK 10 -> selisih biaya jabatan tepat 200.000."""
    kasus = json.loads((DIR_KANONIK / "PMK10-B-3.json").read_text(encoding="utf-8"))
    a, b = hitung(kasus), hitung(kasus, {"REG-BJ-02": "b"})
    assert a["tahunan"]["biaya_jabatan"] == 4_750_000 and b["tahunan"]["biaya_jabatan"] == 4_550_000
    assert a["tahunan"]["pph21_setahun"] == 1_812_500 and b["tahunan"]["pph21_setahun"] == 1_822_500


def test_gross_up_titik_tetap_resmi():
    kasus = json.loads((DIR_KANONIK / "PMK168-B-I.4.json").read_text(encoding="utf-8"))
    h = hitung(kasus)
    m = h["per_masa"][8]
    assert m["tunjangan_pajak"] == m["pph21"] == 13_777_062 and m["bruto"] == 65_605_059
