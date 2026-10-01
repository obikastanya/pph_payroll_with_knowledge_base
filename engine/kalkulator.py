"""API publik kalkulator PPh 21 berbasis KB (research_plan.md §6, §7).

    from engine.kalkulator import hitung, fakta
    hasil = hitung(kasus_kanonik)                       # varian tafsir default
    hasil = hitung(kasus_kanonik, {"REG-BJ-02": "b"})    # varian tafsir alternatif
    hasil = hitung(kasus_kanonik, berkas_perusahaan=["kb/perusahaan/x.yaml"])
"""
from .audit import metadata_audit, periksa_keluaran
from .inferensi import Evaluasi
from .kb import muat_kb

_KB = {}


def kb_aktif(berkas_perusahaan=()):
    kunci = tuple(str(b) for b in berkas_perusahaan)
    if kunci not in _KB:
        _KB[kunci] = muat_kb(berkas_tambahan=berkas_perusahaan)
    return _KB[kunci]


def hitung(kasus, varian=None, berkas_perusahaan=(), audit=False):
    ev = Evaluasi(kb_aktif(berkas_perusahaan), kasus, varian).jalankan()
    hasil = ev.hasil()
    if audit:
        hasil["audit"] = metadata_audit(asumsi=[f"{k}={v}" for k, v in sorted((varian or {}).items())])
    periksa_keluaran({"per_masa": hasil["per_masa"], "tahunan": hasil["tahunan"]})  # MR11
    return hasil


def fakta(hasil, nama, bulan=None):
    """Ambil nilai fakta; fakta tahunan juga dapat dibaca dari konteks satu masa (mis. ptkp)."""
    if bulan is not None or None in hasil["per_masa"]:
        m = hasil["per_masa"].get(bulan, {})
        if nama in m:
            return m[nama]
    if nama in hasil["tahunan"]:
        return hasil["tahunan"][nama]
    if bulan is None:
        ada = [m[nama] for m in hasil["per_masa"].values() if nama in m]
        if len(ada) == 1:
            return ada[0]
    return None
