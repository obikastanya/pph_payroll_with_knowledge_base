"""Kontrak data HR antara aplikasi web dan engine (jembatan/kontrak.py).

Kunci inti punya isian khusus di form web; kunci lain yang dibaca aturan KB lewat hr()/hr_masa() tampil sebagai "masukan
tambahan". Bila KB Perusahaan X mulai membaca kunci baru atau kunci inti berganti nama, tes ini gagal lebih dulu, alih-alih
kunci itu diam-diam tampil ganda di form atau tidak pernah terisi.
"""
import json
import re

from eksperimen.e8_perusahaan_x import kasus_kar_a
from eksperimen.e12_tanpa_kb import BERKAS_PX
from engine.kalkulator import kb_aktif
from engine.kb import rujukan_masukan
from engine.muat import ROOT
from jembatan.kontrak import KUNCI_INTI_BULAN, KUNCI_INTI_TAHUN, TIPE_INTI

SKEMA = json.loads((ROOT / "kb" / "skema" / "aturan.schema.json").read_text(encoding="utf-8"))
TIPE_MASUKAN = set(SKEMA["properties"]["masukan"]["items"]["properties"]["tipe"]["enum"])


def test_kunci_inti_sama_dengan_kunci_yang_dibaca_kb_perusahaan_x():
    rujukan = rujukan_masukan(kb_aktif(BERKAS_PX))
    assert {k for k, r in rujukan.items() if "tahun" in r["lingkup"]} == KUNCI_INTI_TAHUN
    assert {k for k, r in rujukan.items() if "bulan" in r["lingkup"]} == KUNCI_INTI_BULAN
    assert not KUNCI_INTI_TAHUN & KUNCI_INTI_BULAN


def test_data_hr_contoh_hanya_memakai_kunci_inti():
    hr = kasus_kar_a(2023)["data_hr"]
    assert set(hr) - {"per_masa"} == KUNCI_INTI_TAHUN
    assert sorted(hr["per_masa"], key=int) == [str(b) for b in range(1, 13)]
    assert set().union(*(set(m) for m in hr["per_masa"].values())) <= KUNCI_INTI_BULAN


def test_tipe_inti_lengkap_dan_cara_bacanya_dipakai_kb():
    assert set(TIPE_INTI) == KUNCI_INTI_TAHUN | KUNCI_INTI_BULAN
    kb = kb_aktif(BERKAS_PX)
    teks = re.sub(r"\s+", "", " ".join(e.teks for a in kb.aturan for e in (a.maka, a.jika, a.batas_bawah, a.batas_atas)
                                       if e is not None))
    for kunci, (tipe, baca, arti) in TIPE_INTI.items():
        assert tipe in TIPE_MASUKAN and arti, kunci
        # prompt asisten KB mengajarkan cara baca ini; harus sama dengan cara KB Perusahaan X membacanya
        assert re.sub(r"\s+", "", baca) in teks, (kunci, baca)
