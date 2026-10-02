"""Asisten KB: usulan LLM -> berkas KB YAML -> validasi engine, dan perintah jembatan untuk aplikasi web.

Tidak ada panggilan API sungguhan: klien Claude diganti tiruan yang mengembalikan usulan terstruktur.
"""
import copy
import json
from types import SimpleNamespace

import pytest

import jembatan.__main__ as J
from asisten_kb.konteks import prompt_sistem
from asisten_kb.rancangan import ke_berkas, ke_yaml, validasi
from asisten_kb.skema import SKEMA_USULAN
from eksperimen.e12_tanpa_kb import BERKAS_PX
from engine.kb import muat_kb

ATURAN = {"id": "PPT-TRANSPORT-01", "sifat": "opsional", "mulai": "2026-07-01", "sampai": "", "lingkup": "masa",
          "menghasilkan": "px_transport", "jika": "", "maka": "hr('uang_transport_per_hari') * hr_masa('hk_aktual')",
          "tipe_hasil": "rupiah", "pembulatan": "", "sumber": "Peraturan Perusahaan 2026 Ps. 12 ayat (1)", "catatan": ""}
USULAN = {
    "ringkasan": "Uang transport per hari hadir mulai Juli 2026.", "dapat_dikodifikasi": True, "alasan": "",
    "lapisan": "perusahaan", "id_berkas": "transport_2026", "keterangan": "Peraturan Perusahaan 2026: uang transport",
    "komponen": [{"fakta": "px_transport", "jenis": "tunjangan_transport", "kategori": "teratur", "label": "Uang transport"}],
    "masukan": [{"kunci": "uang_transport_per_hari", "label": "Uang transport per hari hadir", "tipe": "rupiah",
                 "lingkup": "tahun", "wajib": False, "bawaan": "0", "pilihan": [], "keterangan": "Per hari kerja hadir",
                 "sumber": "PP 2026 Ps. 12"}],
    "parameter": [], "pembulatan": [], "aturan": [ATURAN], "klasifikasi_wajib": [],
    "rujukan": [{"bagian": "PPT-TRANSPORT-01", "halaman": 3, "kutipan": "uang transport dibayarkan per hari hadir"}],
    "catatan_peninjau": [],
}


def _usulan(**ubah):
    u = copy.deepcopy(USULAN)
    u.update(ubah)
    return u


class KlienTiruan:
    """Meniru anthropic.Anthropic().beta.messages.stream(...).get_final_message()."""

    def __init__(self, usulan, stop_reason="end_turn"):
        self.usulan, self.stop_reason, self.permintaan = usulan, stop_reason, None
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))

    def _stream(self, **kw):
        self.permintaan = kw
        pesan = SimpleNamespace(
            stop_reason=self.stop_reason, model=kw["model"],
            content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=json.dumps(self.usulan))],
            usage=SimpleNamespace(input_tokens=1000, output_tokens=200, cache_read_input_tokens=0, cache_creation_input_tokens=900))
        return _Konteks(pesan)


class _Konteks:
    def __init__(self, pesan):
        self.pesan = pesan

    def __enter__(self):
        return SimpleNamespace(get_final_message=lambda: self.pesan)

    def __exit__(self, *a):
        return False


@pytest.fixture
def pdf(tmp_path):
    p = tmp_path / "peraturan.pdf"
    p.write_bytes(b"%PDF-1.4\n% tiruan\n")
    return p


@pytest.fixture
def dir_kb(tmp_path, monkeypatch):
    """Berkas KB tambahan di direktori sementara (jembatan hanya menerima berkas di bawah DIR_KB)."""
    monkeypatch.setattr(J, "DIR_KB", tmp_path.resolve())
    return tmp_path


def test_rancangan_menjadi_berkas_kb_yang_lolos_validasi_dan_simulasi():
    y = ke_yaml(ke_berkas(USULAN), "PP 2026", "claude-opus-5-5")
    assert "mulai: 2026-07-01" in y and "WAJIB ditinjau" in y
    v = validasi(y, nama_berkas="transport_2026.yaml")
    assert v["ok"], v["galat"]
    assert v["isi"]["aturan"][0]["berlaku"] == {"mulai": "2026-07-01"} and v["ringkasan"]["aturan"] == 1
    [m] = v["masukan"]
    assert (m["kunci"], m["tipe"], m["lingkup"], m["wajib"], m["dideklarasikan"]) == ("uang_transport_per_hari", "rupiah", "tahun", False, True)
    [d] = v["dampak"]  # hanya tahun yang tersentuh rancangan
    assert d["tahun"] == 2026 and d["nilai_contoh"] == {"uang_transport_per_hari": 100_000}
    assert d["fakta_baru"]["px_transport"] > 0
    assert d["sesudah"]["bruto_setahun"] - d["sebelum"]["bruto_setahun"] == d["fakta_baru"]["px_transport"]
    assert d["sesudah"]["thp_setahun"] > d["sebelum"]["thp_setahun"]


def test_masukan_baru_tanpa_deklarasi_ditolak():
    u = _usulan(masukan=[], aturan=[dict(ATURAN, maka="hr('uang_makan') * hr_masa('hk_aktual')")])
    v = validasi(ke_yaml(ke_berkas(u)))
    assert not v["ok"] and any("uang_makan" in g and "belum dideklarasikan" in g for g in v["galat"])


@pytest.mark.parametrize("ubah, pesan", [
    ({"maka": "__import__('os').system('dir')"}, "ditolak verifikasi KB"),
    ({"maka": "hr('uang_transport_per_hari') * 1.5"}, "ditolak verifikasi KB"),
    ({"pembulatan": "TIDAK-ADA"}, "tidak terdaftar"),
    ({"menghasilkan": "bruto", "lingkup": "tahun"}, "ditolak verifikasi KB"),
])
def test_rancangan_tidak_sah_ditolak_engine(ubah, pesan):
    v = validasi(ke_yaml(ke_berkas(_usulan(aturan=[dict(ATURAN, **ubah)]))))
    assert not v["ok"] and any(pesan in g for g in v["galat"]), v["galat"]


def test_yaml_rusak_atau_kosong_ditolak():
    assert "YAML tidak dapat dibaca" in validasi("lapisan: [")["galat"][0]
    assert "kunci duplikat" in validasi("lapisan: perusahaan\nlapisan: regulasi\n")["galat"][0]
    assert "float literal" in validasi("lapisan: perusahaan\nnilai: 1.5\n")["galat"][0]
    assert "tidak berisi aturan" in validasi("lapisan: perusahaan\nid: x\naturan: []\n")["galat"][0]


def test_prompt_sistem_memuat_inventaris_kb_aktif():
    teks = prompt_sistem(muat_kb(BERKAS_PX))
    for kata in ("px_thp", "jp_batas_upah", "hk_aktual", "komponen('teratur')"):
        assert kata in teks
    assert len(teks) < 60_000


def test_usulkan_lewat_jembatan_dengan_klien_tiruan(pdf):
    klien = KlienTiruan(USULAN)
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf), "lapisan": "perusahaan", "catatan": "berlaku Juli"}, klien)
    assert jawab["ok"] and jawab["validasi"]["ok"], jawab
    assert jawab["yaml"].startswith("# Rancangan berkas KB") and jawab["info"]["token_cache_tulis"] == 900
    kw = klien.permintaan
    assert kw["model"] == "claude-opus-5-5" and kw["thinking"] == {"type": "adaptive"}
    assert kw["output_config"]["format"] == {"type": "json_schema", "schema": SKEMA_USULAN}
    assert kw["system"][0]["cache_control"] == {"type": "ephemeral"}
    dok, teks = kw["messages"][0]["content"]
    assert dok["type"] == "document" and dok["source"]["media_type"] == "application/pdf"
    assert "perusahaan" in teks["text"] and "berlaku Juli" in teks["text"]


def test_dokumen_tidak_dapat_dikodifikasi_tidak_menghasilkan_yaml(pdf):
    u = _usulan(dapat_dikodifikasi=False, alasan="hanya mengubah tabel TER", aturan=[], masukan=[], komponen=[])
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf)}, KlienTiruan(u))
    assert jawab["ok"] and jawab["yaml"] == "" and jawab["validasi"] is None
    assert jawab["usulan"]["alasan"] == "hanya mengubah tabel TER"


def test_penolakan_model_dan_kunci_api_kosong(pdf, monkeypatch):
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf)}, KlienTiruan(USULAN, stop_reason="refusal"))
    assert jawab == {"ok": False, "jenis": "gagal_llm", "pesan": "model menolak memproses dokumen ini"}
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf)})
    assert jawab["jenis"] == "permintaan_tidak_valid" and "ANTHROPIC_API_KEY" in jawab["pesan"]


def test_berkas_tambahan_di_luar_kb_ditolak(tmp_path):
    luar = tmp_path / "x.yaml"
    luar.write_text("lapisan: perusahaan\n", encoding="utf-8")
    for b in (str(luar), "../engine/kb.py", "kb/perusahaan/../../README.md"):
        jawab = J.jalankan({"perintah": "hitung", "kasus": [], "berkas_tambahan": [b]})
        assert jawab["jenis"] == "permintaan_tidak_valid", b


def test_hitung_dan_masukan_dengan_berkas_tambahan(dir_kb):
    from eksperimen.e8_perusahaan_x import kasus_kar_a
    berkas = dir_kb / "transport_2026.yaml"
    berkas.write_text(ke_yaml(ke_berkas(USULAN)), encoding="utf-8")

    m = J.jalankan({"perintah": "masukan", "berkas_tambahan": [str(berkas)]})
    assert m["ok"] and [x["kunci"] for x in m["masukan"]] == ["uang_transport_per_hari"]
    assert (m["masukan"][0]["mulai"], m["masukan"][0]["sampai"]) == ("2026-07-01", None)
    assert {"fakta": "px_transport", "jenis": "tunjangan_transport", "kategori": "teratur", "label": "Uang transport",
            "berkas": "transport_2026.yaml"} in m["komponen"]
    assert all(x["fakta"].startswith("px_") for x in m["komponen"])

    kasus = kasus_kar_a(2026)
    kasus["data_hr"]["uang_transport_per_hari"] = 25_000
    jawab = J.jalankan({"perintah": "hitung", "kasus": [kasus], "cek_silang": True, "berkas_tambahan": [str(berkas)]})
    [r] = jawab["hasil"]
    assert r["ok"] and r["cek_silang"]["status"] == "dilewati" and len(jawab["sidik_kb"]) == 16
    assert r["hasil"]["per_masa"][7]["px_transport"] == 25_000 * kasus["data_hr"]["per_masa"]["7"]["hk_aktual"]
    assert "px_transport" not in r["hasil"]["per_masa"][6]
    assert {"fakta": "px_transport", "jenis": "tunjangan_transport", "kategori": "teratur", "label": "Uang transport",
            "berkas": "transport_2026.yaml"} in r["hasil"]["komponen"]

    kasus["data_hr"]["uang_transport_per_hari"] = "25000"  # tipe salah -> galat berlabel, bukan TypeError
    [r] = J.jalankan({"perintah": "hitung", "kasus": [kasus], "berkas_tambahan": [str(berkas)]})["hasil"]
    assert not r["ok"] and r["jenis"] == "kesalahan_kb" and "uang_transport_per_hari" in r["pesan"]

    tanpa = J.jalankan({"perintah": "hitung", "kasus": [kasus_kar_a(2026)]})
    assert tanpa["sidik_kb"] == "" and "px_transport" not in tanpa["hasil"][0]["hasil"]["per_masa"][7]


def test_validasi_lewat_jembatan_mempertimbangkan_berkas_aktif(dir_kb):
    berkas = dir_kb / "transport_2026.yaml"
    berkas.write_text(ke_yaml(ke_berkas(USULAN)), encoding="utf-8")
    # berkas kedua dengan id aturan yang sama -> bentrok dengan KB aktif
    jawab = J.jalankan({"perintah": "validasi", "yaml": ke_yaml(ke_berkas(USULAN)), "nama": "lagi.yaml",
                        "berkas_tambahan": [str(berkas)]})
    assert jawab["ok"] and not jawab["validasi"]["ok"]
    assert any("duplikat" in g for g in jawab["validasi"]["galat"])
