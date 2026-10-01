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


FAKTA_RENTANG_MASA = ("pph21", "pph21_dtp", "tunjangan_pajak", "bruto")
FAKTA_RENTANG_TAHUN = ("pph21_setahun", "pph21_masa_terakhir", "lebih_bayar_dikembalikan", "pkp", "biaya_jabatan")


def titik_tafsir(kb):
    """Semua titik tafsir di KB: {id: [varian alternatif]} (registri pembulatan, grup aturan, titik tetap)."""
    titik = {e.id: list(e.alternatif) for e in kb.registri if e.status == "tafsir"}
    for a in kb.aturan:
        if a.tafsir and not a.varian_default:
            titik.setdefault(a.tafsir, [])
            if a.varian not in titik[a.tafsir]:
                titik[a.tafsir].append(a.varian)
    titik["TITIK-TETAP-PILIH"] = ["terbesar"]
    return titik


def rentang_tafsir(kasus, hasil_default, varian=None, berkas_perusahaan=(), kb=None):
    """§6.9.6: hitung ulang setiap varian alternatif (satu per satu) dan laporkan selisih angka keluaran."""
    kb = kb or kb_aktif(berkas_perusahaan)
    dasar = dict(varian or {})
    rentang = []
    for tid, alternatif in titik_tafsir(kb).items():
        if tid in dasar:
            continue
        for v in alternatif:
            h = Evaluasi(kb, kasus, dict(dasar, **{tid: v})).jalankan().hasil()
            for b, m in hasil_default["per_masa"].items():
                for f in FAKTA_RENTANG_MASA:
                    a, c = m.get(f), h["per_masa"].get(b, {}).get(f)
                    if isinstance(a, int) and isinstance(c, int) and a != c:
                        rentang.append({"tafsir": tid, "varian": v, "fakta": f, "bulan": b, "default": a,
                                        "alternatif": c, "selisih": c - a})
            for f in FAKTA_RENTANG_TAHUN:
                a, c = hasil_default["tahunan"].get(f), h["tahunan"].get(f)
                if isinstance(a, int) and isinstance(c, int) and a != c:
                    rentang.append({"tafsir": tid, "varian": v, "fakta": f, "bulan": None, "default": a,
                                    "alternatif": c, "selisih": c - a})
    return rentang


def hitung(kasus, varian=None, berkas_perusahaan=(), audit=False, ablasi=(), kb=None, dengan_rentang=False):
    kb_pakai = kb or kb_aktif(berkas_perusahaan)
    ev = Evaluasi(kb_pakai, kasus, varian, ablasi=ablasi).jalankan()
    hasil = ev.hasil()
    if audit:
        hasil["audit"] = metadata_audit(asumsi=[f"{k}={v}" for k, v in sorted((varian or {}).items())])
    if dengan_rentang:
        hasil["rentang_tafsir"] = rentang_tafsir(kasus, hasil, varian, kb=kb_pakai)
        for tid in sorted({r["tafsir"] for r in hasil["rentang_tafsir"]}):
            hasil["peringatan"].append({"kode": "AMBIGU_TAFSIR", "tafsir": tid,
                                        "selisih_maks": max(abs(r["selisih"]) for r in hasil["rentang_tafsir"] if r["tafsir"] == tid)})
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
