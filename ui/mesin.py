"""Dua mesin kalkulator untuk UI: DENGAN KB (engine + KB YAML) dan TANPA KB (kode hard-coded B2 + B1).

Keduanya menerima kasus yang sama dan mengembalikan bentuk keluaran yang sama, sehingga tampilan bisa identik.
Yang berbeda adalah mekanismenya, dan itu ditunjukkan lewat `dasar()`: KB menunjuk aturan + pasal di berkas YAML,
tanpa KB menunjuk fungsi + baris di kode Python.
"""
import inspect
import json
from pathlib import Path

import streamlit as st

from baselines.b1_hardcoded import pph21_b1 as B1
from baselines.b2_payroll_hardcoded import payroll_b2 as B2
from engine.inferensi import Ambigu, KasusTidakDidukung
from engine.kalkulator import fakta as fakta_kb
from engine.kalkulator import hitung as hitung_engine
from engine.muat import KesalahanKB
from engine.waktu import InputTidakValid
from ui import data as D

KB, TANPA_KB = "kb", "tanpa_kb"
NAMA = {KB: "Dengan knowledge base", TANPA_KB: "Tanpa knowledge base"}


def _berkas(kasus):
    return [str(D.BERKAS_PX)] if kasus.get("data_hr") else []


@st.cache_data(show_spinner=False, max_entries=256)
def _hitung(kasus_json, mesin):
    kasus = json.loads(kasus_json)
    if mesin == KB:
        h = hitung_engine(kasus, berkas_perusahaan=[Path(b) for b in _berkas(kasus)])
        rinci = [r for r in h["rincian_pasal17"] if r["bulan"] is None and r["fakta"] in ("pph21_disetahunkan", "pph21_setahun")]
        return {"per_masa": h["per_masa"], "tahunan": h["tahunan"], "jejak": h["jejak"], "peringatan": h["peringatan"],
                "rincian_p17": ({"pkp": rinci[0]["pkp"], "lapisan": rinci[0]["lapisan"]} if rinci else None)}
    h = B2.hitung(kasus)
    return {"per_masa": h["per_masa"], "tahunan": h["tahunan"], "jejak": None, "peringatan": [], "rincian_p17": h["rincian_pasal17"]}


def hitung(kasus, mesin):
    """-> (hasil, pesan_galat)."""
    try:
        return _hitung(json.dumps(kasus, sort_keys=True, ensure_ascii=False), mesin), None
    except InputTidakValid as e:
        return None, f"Isian tidak valid: {e}"
    except (KasusTidakDidukung, B1.KasusTidakDidukung) as e:
        return None, f"Kasus di luar cakupan kalkulator: {e}"
    except Ambigu as e:
        return None, f"Aturan ambigu: {e}"
    except KesalahanKB as e:
        return None, f"Data belum lengkap atau tidak sesuai: {e}"
    except (KeyError, TypeError, ValueError) as e:
        return None, f"Data belum lengkap atau tidak sesuai format ({type(e).__name__}: {e})"


@st.cache_data(show_spinner=False, max_entries=256)
def _cek_silang(kasus_json):
    from eksperimen.e12_tanpa_kb import cek_silang
    r = cek_silang(json.loads(kasus_json))
    return {"status": r["status"], "selisih": r["selisih"]}


def cek_silang(kasus):
    try:
        return _cek_silang(json.dumps(kasus, sort_keys=True, ensure_ascii=False))
    except Exception as e:  # noqa: BLE001 - galat sudah ditampilkan oleh hitung(); cek silang tidak boleh menjatuhkan UI
        return {"status": "galat", "selisih": [], "pesan": f"{type(e).__name__}: {e}"}


@st.cache_data(show_spinner=False)
def cek_resmi(kasus_id, mesin):
    """V1 untuk satu contoh resmi dengan mesin tertentu (KB: engine; tanpa KB: B1)."""
    from eksperimen.v1 import bandingkan
    k = D.muat_kanonik(kasus_id)
    if mesin == KB:
        return bandingkan(k, lambda kk, v: hitung_engine(kk, v), fakta_kb)
    return bandingkan(k, B1.hitung, B1.fakta)


# ---------------------------------------------------------------------------- dasar perhitungan per angka

_B1_TER = {"pph21": "_hitung_ter", "pph21_masa_terakhir": "_hitung_ter", "pph21_dipotong_sebelumnya": "_hitung_ter"}
_B1_P16 = {"pph21": "_hitung_per16", "pph21_masa_terakhir": "_hitung_per16", "pph21_dipotong_sebelumnya": "_hitung_per16"}
SUMBER_KODE = {
    "px_gaji": (B2, "gaji"), "px_tunjangan": (B2, "tunjangan"), "px_thr": (B2, "thr"), "px_kompensasi": (B2, "kompensasi"),
    "px_ota": (B2, "komponen_bulan"), "px_lembur": (B2, "komponen_bulan"), "px_komisi": (B2, "komponen_bulan"),
    "px_premi_jkk": (B2, "bpjs"), "px_premi_jkm": (B2, "bpjs"), "px_premi_kes": (B2, "bpjs"), "px_premi_jht_pk": (B2, "bpjs"),
    "px_premi_jp_pk": (B2, "bpjs"), "px_iuran_jht_pg": (B2, "bpjs"), "px_iuran_jp_pg": (B2, "bpjs"), "px_iuran_kes_pg": (B2, "bpjs"),
    "px_penghasilan_tunai": (B2, "hitung"), "px_thp": (B2, "hitung"),
    "bruto": (B1, "_rincian_masa"), "kategori_ter": (B1, "_hitung_ter"), "tarif_ter": (B1, "tarif_ter"),
    "pph21_dtp": (B1, "_berhak_dtp"), "tunjangan_pajak": (B1, "_grossup_ter"),
    "bruto_setahun": (B1, "_tahunan"), "biaya_jabatan": (B1, "_biaya_jabatan_setahun"), "iuran_pengurang": (B1, "_tahunan"),
    "zakat": (B1, "_tahunan"), "neto_setahun": (B1, "_tahunan"), "ptkp": (B1, "ptkp"), "pkp": (B1, "_tahunan"),
    "pph21_setahun": (B1, "pasal17"), "pph21_disetahunkan": (B1, "pasal17"), "lebih_bayar_dikembalikan": (B1, "_hitung_ter"),
    "berhak_dtp": (B1, "_berhak_dtp"), "status_ptkp_efektif": (B1, "status_efektif"),
}


@st.cache_data(show_spinner=False)
def kode_sumber(modul_nama, fungsi):
    modul = {"B1": B1, "B2": B2}[modul_nama]
    fn = getattr(modul, fungsi)
    baris, awal = inspect.getsourcelines(fn)
    path = Path(inspect.getsourcefile(fn)).relative_to(D.ROOT).as_posix()
    return {"berkas": path, "awal": awal, "akhir": awal + len(baris) - 1, "kode": "".join(baris)}


def _sumber_tanpa_kb(fakta, tahun):
    if fakta in _B1_TER and tahun is not None:
        return (B1, (_B1_TER if tahun >= 2024 else _B1_P16)[fakta])
    return SUMBER_KODE.get(fakta)


def dasar(mesin, hasil, fakta, bulan, tahun=None):
    """Penjelasan singkat sumber sebuah angka: {'pendek', 'panjang'} atau None."""
    if mesin == KB:
        for j in hasil["jejak"] or []:
            if j["fakta"] == fakta and j["bulan"] == bulan:
                lap = "Perusahaan X" if j["lapisan"] == "perusahaan" else "Regulasi"
                return {"pendek": f"{lap} · {j['aturan']}", "panjang": j["sumber"], "aturan": j["aturan"]}
        if bulan is not None:
            return dasar(mesin, hasil, fakta, None, tahun)
        return None
    s = _sumber_tanpa_kb(fakta, tahun)
    if s is None:
        return None
    modul, fn = s
    info = kode_sumber("B1" if modul is B1 else "B2", fn)
    return {"pendek": f"{Path(info['berkas']).name} · {fn}()", "panjang": f"{info['berkas']} baris {info['awal']}-{info['akhir']}",
            "fungsi": ("B1" if modul is B1 else "B2", fn)}
