"""Asisten KB: usulan LLM -> berkas KB YAML -> validasi engine, dan perintah jembatan untuk aplikasi web.

Tidak ada panggilan API sungguhan: klien Claude diganti tiruan yang mengembalikan usulan terstruktur.
"""
import copy
import json
import re
from types import SimpleNamespace

import pytest

import jembatan.__main__ as J
from asisten_kb.konteks import prompt_sistem
from asisten_kb.rancangan import ke_berkas, ke_yaml, validasi
from asisten_kb.skema import SKEMA_USULAN
from eksperimen.e12_tanpa_kb import BERKAS_PX
from engine.kb import muat_kb

ATURAN = {"id": "PPT-TRANSPORT-01", "sifat": "opsional", "mulai": "2026-07-01", "sampai": "", "lingkup": "masa",
          "menghasilkan": "px_transport", "menggantikan": [], "jika": "",
          "maka": "hr('uang_transport_per_hari') * hr_masa('hk_aktual')",
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
    """Meniru kedua SDK: openai.OpenAI().responses.stream(...).get_final_response() dan
    anthropic.Anthropic().beta.messages.stream(...).get_final_message()."""

    def __init__(self, usulan, status="completed", alasan=None, menolak=False, stop_reason="end_turn"):
        self.usulan, self.status, self.alasan, self.menolak, self.stop_reason = usulan, status, alasan, menolak, stop_reason
        self.permintaan = None
        self.responses = SimpleNamespace(stream=self._openai)
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._claude))

    def _openai(self, **kw):
        self.permintaan = kw
        teks = json.dumps(self.usulan)
        isi = SimpleNamespace(type="refusal", refusal="tidak bisa") if self.menolak else SimpleNamespace(type="output_text", text=teks)
        r = SimpleNamespace(
            status=self.status, incomplete_details=SimpleNamespace(reason=self.alasan) if self.alasan else None, error=None,
            model=kw["model"], output_text="" if self.menolak else teks,
            output=[SimpleNamespace(type="reasoning"), SimpleNamespace(type="message", content=[isi])],
            usage=SimpleNamespace(input_tokens=1000, output_tokens=200,
                                  input_tokens_details=SimpleNamespace(cached_tokens=800, cache_write_tokens=0)))
        # aliran event seperti SDK: delta, lalu satu event terminal (completed / incomplete / failed) yang membawa respons
        return _Konteks([SimpleNamespace(type="response.output_text.delta", delta=teks[:5]),
                         SimpleNamespace(type=f"response.{self.status}", response=r)])

    def _claude(self, **kw):
        self.permintaan = kw
        pesan = SimpleNamespace(
            stop_reason=self.stop_reason, model=kw["model"],
            content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=json.dumps(self.usulan))],
            usage=SimpleNamespace(input_tokens=1000, output_tokens=200, cache_read_input_tokens=0, cache_creation_input_tokens=900))
        return _Konteks(SimpleNamespace(get_final_message=lambda: pesan))


class _Konteks:
    def __init__(self, stream):
        self.stream = stream

    def __enter__(self):
        return self.stream

    def __exit__(self, *a):
        return False


@pytest.fixture
def pdf(tmp_path):
    p = tmp_path / "peraturan.pdf"
    p.write_bytes(b"%PDF-1.4\n% tiruan\n")
    return p


@pytest.fixture
def dir_kb(tmp_path, monkeypatch):
    """Berkas KB tambahan di direktori sementara (jembatan hanya menerima berkas di bawah DIR_TAMBAHAN)."""
    monkeypatch.setattr(J, "DIR_TAMBAHAN", tmp_path.resolve())
    return tmp_path


def test_rancangan_menjadi_berkas_kb_yang_lolos_validasi_dan_simulasi():
    y = ke_yaml(ke_berkas(USULAN), "PP 2026", "claude-opus-5-5")
    assert "mulai: 2026-07-01" in y and "WAJIB ditinjau" in y
    v = validasi(y, nama_berkas="transport_2026.yaml")
    assert v["ok"], v["galat"]
    assert v["isi"]["aturan"][0]["berlaku"] == {"mulai": "2026-07-01"} and v["ringkasan"]["aturan"] == 1
    [m] = v["masukan"]
    assert (m["kunci"], m["tipe"], m["lingkup"], m["wajib"], m["dideklarasikan"]) == ("uang_transport_per_hari", "rupiah", "tahun", False, True)
    # mulai Juli 2026: tahun mulai + tahun penuh pertamanya, untuk Karyawan A dan pegawai yang masuk Juli
    assert [(d["pegawai"], d["tahun"]) for d in v["dampak"]] == [
        ("Karyawan A (contoh)", 2026), ("Pegawai masuk Juli (contoh)", 2026),
        ("Karyawan A (contoh)", 2027), ("Pegawai masuk Juli (contoh)", 2027)]
    for d in v["dampak"]:
        assert d["nilai_contoh"] == {"uang_transport_per_hari": 100_000}
        assert d["fakta_baru"]["px_transport"] > 0
        assert d["sesudah"]["bruto_setahun"] - d["sebelum"]["bruto_setahun"] == d["fakta_baru"]["px_transport"]
        assert d["sesudah"]["thp_setahun"] > d["sebelum"]["thp_setahun"]
    a26, _, a27, _ = v["dampak"]
    assert a27["fakta_baru"]["px_transport"] > a26["fakta_baru"]["px_transport"]   # 2026 hanya Juli-Desember
    assert v["perubahan"] == [] and v["belum_teruji"] == []
    [p] = v["peringatan"]   # satu-satunya peringatan: masukan dengan bawaan 0 (A2); px_transport komponen -> bukan A1
    assert p.startswith("masukan 'uang_transport_per_hari' punya bawaan 0:")


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
    assert jawab["yaml"].startswith("# Rancangan berkas KB") and "(gpt-5.6-sol)" in jawab["yaml"]
    assert jawab["info"] == {"model": "gpt-5.6-sol", "token_masuk": 1000, "token_keluar": 200, "token_cache_baca": 800, "token_cache_tulis": 0}
    kw = klien.permintaan   # bawaan: OpenAI Responses API
    assert kw["model"] == "gpt-5.6-sol" and kw["reasoning"] == {"effort": "high"} and kw["store"] is False
    assert kw["text"]["format"] == {"type": "json_schema", "name": "usulan_kb", "strict": True, "schema": SKEMA_USULAN}
    assert "komponen('teratur')" in kw["instructions"]
    dok, teks = kw["input"][0]["content"]
    assert dok["type"] == "input_file" and dok["file_data"].startswith("data:application/pdf;base64,JVBERi0xLjQ")
    assert teks["type"] == "input_text" and "perusahaan" in teks["text"] and "berlaku Juli" in teks["text"]


def test_model_claude_memakai_api_anthropic(pdf):
    klien = KlienTiruan(USULAN)
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf), "model": "claude-opus-5-5"}, klien)
    assert jawab["ok"] and jawab["validasi"]["ok"] and jawab["info"]["token_cache_tulis"] == 900
    kw = klien.permintaan
    assert kw["model"] == "claude-opus-5-5" and kw["thinking"] == {"type": "adaptive"}
    assert kw["output_config"]["format"] == {"type": "json_schema", "schema": SKEMA_USULAN}
    assert kw["system"][0]["cache_control"] == {"type": "ephemeral"}
    dok, _ = kw["messages"][0]["content"]
    assert dok["type"] == "document" and dok["source"]["media_type"] == "application/pdf"


def test_dokumen_tidak_dapat_dikodifikasi_tidak_menghasilkan_yaml(pdf):
    u = _usulan(dapat_dikodifikasi=False, alasan="hanya mengubah tabel TER", aturan=[], masukan=[], komponen=[])
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf)}, KlienTiruan(u))
    assert jawab["ok"] and jawab["yaml"] == "" and jawab["validasi"] is None
    assert jawab["usulan"]["alasan"] == "hanya mengubah tabel TER"


def test_penolakan_model_dan_kunci_api_kosong(pdf, monkeypatch):
    menolak = {"ok": False, "jenis": "gagal_llm", "pesan": "model menolak memproses dokumen ini"}
    assert J.jalankan({"perintah": "usulkan", "pdf": str(pdf)}, KlienTiruan(USULAN, menolak=True)) == menolak
    assert J.jalankan({"perintah": "usulkan", "pdf": str(pdf)}, KlienTiruan(USULAN, status="incomplete", alasan="content_filter")) == menolak
    assert J.jalankan({"perintah": "usulkan", "pdf": str(pdf), "model": "claude-opus-5-5"}, KlienTiruan(USULAN, stop_reason="refusal")) == menolak
    terpotong = J.jalankan({"perintah": "usulkan", "pdf": str(pdf)}, KlienTiruan(USULAN, status="incomplete", alasan="max_output_tokens"))
    assert terpotong["jenis"] == "gagal_llm" and "terpotong" in terpotong["pesan"]
    gagal = J.jalankan({"perintah": "usulkan", "pdf": str(pdf)}, KlienTiruan(USULAN, status="failed"))
    assert gagal["jenis"] == "gagal_llm" and "status failed" in gagal["pesan"]
    putus = SimpleNamespace(responses=SimpleNamespace(stream=lambda **kw: _Konteks([SimpleNamespace(type="response.created")])))
    assert "terputus" in J.jalankan({"perintah": "usulkan", "pdf": str(pdf)}, putus)["pesan"]

    for kunci in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(kunci, raising=False)
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf)})
    assert jawab["jenis"] == "permintaan_tidak_valid" and "OPENAI_API_KEY" in jawab["pesan"]
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf), "model": "claude-opus-5-5"})
    assert jawab["jenis"] == "permintaan_tidak_valid" and "ANTHROPIC_API_KEY" in jawab["pesan"]


def test_galat_sdk_dipetakan_ke_pesan_pengguna(pdf, monkeypatch):
    import anthropic
    import openai

    from asisten_kb.llm import GagalLLM, _galat_api, minta_usulan

    nama = ("AuthenticationError", "PermissionDeniedError", "NotFoundError", "RateLimitError", "BadRequestError", "APIStatusError",
            "APIConnectionError")
    for sdk in (openai, anthropic):   # kedua SDK harus punya kelas galat yang dipetakan
        assert all(isinstance(getattr(sdk, n), type) for n in nama)

    def galat(kelas, **atribut):   # instans tanpa HTTP sungguhan: yang diuji pemetaannya, bukan SDK
        e = kelas.__new__(kelas)
        e.__dict__.update(atribut)
        return e

    kasus = [(openai.AuthenticationError, {}, "gpt-5.6-sol", r"kunci API tidak valid atau belum diatur \(OPENAI_API_KEY\)"),
             (anthropic.AuthenticationError, {}, "claude-opus-5-5", r"\(ANTHROPIC_API_KEY\)"),
             (openai.NotFoundError, {}, "gpt-5.6-sol", "model 'gpt-5.6-sol' tidak ditemukan"),
             (openai.RateLimitError, {}, "gpt-5.6-sol", "kuota"),
             (openai.BadRequestError, {"message": "file terlalu besar"}, "gpt-5.6-sol", "permintaan ditolak API: file terlalu besar"),
             (openai.InternalServerError, {"status_code": 503}, "gpt-5.6-sol", r"galat server API \(503\)"),
             (openai.APIConnectionError, {}, "gpt-5.6-sol", "tidak dapat terhubung")]
    for kelas, atribut, model, pesan in kasus:
        sdk = anthropic if model.startswith("claude") else openai
        assert re.search(pesan, str(_galat_api(sdk, galat(kelas, **atribut), model))), kelas.__name__
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(GagalLLM, match="klien LLM gagal"):   # klien asli tanpa kunci: galat SDK, bukan traceback
        minta_usulan(pdf.read_bytes(), "sistem", "instruksi")


def test_berkas_tambahan_di_luar_kb_ditolak(tmp_path):
    luar = tmp_path / "x.yaml"
    luar.write_text("lapisan: perusahaan\n", encoding="utf-8")
    # KB dasar (kb/regulasi, kb/perusahaan) juga ditolak: dimuat dua kali bila dikirim sebagai berkas tambahan
    for b in (str(luar), "../engine/kb.py", "kb/perusahaan/../../README.md", "kb/regulasi/aturan_umum.yaml",
              "kb/perusahaan/perusahaan_x.yaml", "kb/tambahan/../regulasi/parameter.yaml"):
        jawab = J.jalankan({"perintah": "hitung", "kasus": [], "berkas_tambahan": [b]})
        assert jawab["jenis"] == "permintaan_tidak_valid", b
    for daftar in ("kb/tambahan/x.yaml", [5], {"b": "kb/tambahan/x.yaml"}):
        jawab = J.jalankan({"perintah": "masukan", "berkas_tambahan": daftar})
        assert jawab == {"ok": False, "jenis": "permintaan_tidak_valid",
                         "pesan": "berkas_tambahan harus daftar path berkas (teks)"}, daftar


def test_path_unc_ditolak_tanpa_menyentuh_jaringan(monkeypatch):
    def jangan(*_):
        raise AssertionError("resolve() atas path UNC menghubungi server berbagi berkas")
    monkeypatch.setattr(J.Path, "resolve", jangan)
    for b in ("\\\\server\\berbagi\\x.yaml", "//server/berbagi/x.yaml", "\\/server/berbagi/x.yaml"):
        jawab = J.jalankan({"perintah": "hitung", "kasus": [], "berkas_tambahan": [b]})
        assert jawab["jenis"] == "permintaan_tidak_valid" and "kb/tambahan/" in jawab["pesan"], b


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


# ------------------------------------------------------------------------------------------- R1: validasi tidak melempar

def _tulis(direktori, nama, isi):
    p = direktori / nama
    p.write_text(isi, encoding="utf-8")
    return p


TGL = """
lapisan: perusahaan
id: uji_tgl
masukan:
  - {kunci: tanggal_sk, label: Tanggal SK, tipe: tanggal, lingkup: tahun, wajib: true}
aturan:
  - id: PPU-TGL-01
    sifat: opsional
    berlaku: {mulai: 2026-01-01}
    lingkup: tahun
    menghasilkan: px_bulan_sk
    maka: "bulan_dari(hr('tanggal_sk'))"
    tipe_hasil: bilangan
    sumber: uji
"""
OVERFLOW = (TGL.replace("bulan_dari(hr('tanggal_sk'))", "tahun_dari(tambah_hari(tanggal_masa(), 100000000))")
            .replace("lingkup: tahun\n    menghasilkan", "lingkup: masa\n    menghasilkan"))


@pytest.mark.parametrize("teks, pesan, termuat", [
    (TGL, "simulasi Karyawan A 2026 gagal (aturan PPU-TGL-01): AttributeError", True),   # tanggal() terlupa
    (OVERFLOW, "simulasi Karyawan A 2026 gagal (aturan PPU-TGL-01): OverflowError", True),
    (TGL.replace("mulai: 2026-01-01", "mulai: 2026-02-30"), "YAML tidak dapat dibaca: ValueError", False),
    ("lapisan: perusahaan\naturan: 5\n", "ditolak verifikasi KB", False),
    ("lapisan: perusahaan\naturan:\n  - 5\n", "ditolak verifikasi KB", False),
])
def test_galat_tak_terduga_menjadi_galat_validasi(teks, pesan, termuat):
    v = validasi(teks)
    assert not v["ok"] and any(pesan in g for g in v["galat"]), v["galat"]
    # KB tidak termuat -> isi kosong, agar halaman tinjau tidak menyusun tabel dari struktur rusak
    assert bool(v["isi"]) == termuat


def test_isi_hanya_terisi_bila_kb_termuat():
    v = validasi("lapisan: perusahaan\naturan: 5\n")
    assert v["isi"] == {} and v["ringkasan"]["aturan"] == 0 and v["ringkasan"]["lapisan"] == "perusahaan"
    assert validasi(TGL)["isi"]["aturan"][0]["id"] == "PPU-TGL-01"


def test_galat_internal_tidak_melempar(monkeypatch):
    import asisten_kb.rancangan as R

    def rusak(*a, **k):
        raise IndexError("list index out of range")
    monkeypatch.setattr(R, "muat_kb", rusak)
    v = validasi(ke_yaml(ke_berkas(USULAN)))
    assert not v["ok"] and v["isi"] == {} and "IndexError" in v["galat"][0]
    monkeypatch.undo()
    monkeypatch.setattr(R, "_simulasi", rusak)
    v = validasi(ke_yaml(ke_berkas(USULAN)))
    assert not v["ok"] and v["galat"] == ["galat internal validasi: IndexError: list index out of range"]


def test_usulkan_tetap_mengembalikan_usulan_bila_validasi_gagal(pdf):
    u = _usulan(aturan=[dict(ATURAN, maka="hr('uang_transport_per_hari') * 'a'")])
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf)}, KlienTiruan(u))
    assert jawab["ok"] and not jawab["validasi"]["ok"] and jawab["yaml"] and jawab["usulan"]["id_berkas"] == "transport_2026"
    assert jawab["info"]["model"] == "gpt-5.6-sol"
    assert any("PelanggaranPresisi" in g and "PPT-TRANSPORT-01" in g for g in jawab["validasi"]["galat"])

    rusak = _usulan(aturan=[{k: v for k, v in ATURAN.items() if k != "maka"}])   # di luar skema keluaran
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf)}, KlienTiruan(rusak))
    assert jawab["ok"] and jawab["yaml"] == "" and jawab["usulan"]["aturan"] and jawab["info"]
    assert "usulan tidak dapat diubah menjadi berkas KB: KeyError" in jawab["validasi"]["galat"][0]
    assert jawab["validasi"]["perubahan"] == [] and jawab["validasi"]["belum_teruji"] == []


# ------------------------------------------------------------------------------------------- R2: nilai contoh semua masukan

KINERJA = """
lapisan: perusahaan
id: kinerja
komponen:
  - {fakta: px_bonus_kinerja, jenis: bonus_kinerja, kategori: tidak_teratur, label: Bonus kinerja}
masukan:
  - {kunci: kinerja_sangat_baik, label: Kinerja sangat baik, tipe: ya_tidak, lingkup: tahun, wajib: true}
aturan:
  - id: PPK-KINERJA-01
    sifat: opsional
    berlaku: {mulai: 2024-01-01}
    lingkup: masa
    menghasilkan: px_bonus_kinerja
    jika: "bulan == 12"
    maka: "hr('gaji_pokok') if hr('kinerja_sangat_baik') else 0"
    tipe_hasil: rupiah
    sumber: uji
"""
TRANSPORT_WAJIB = _usulan(masukan=[dict(USULAN["masukan"][0], wajib=True, bawaan="")])
MAKAN = """
lapisan: perusahaan
id: makan
komponen:
  - {fakta: px_makan, jenis: tunjangan_makan, kategori: teratur, label: Uang makan}
aturan:
  - id: PPM-MAKAN-01
    sifat: opsional
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: px_makan
    maka: "hr('uang_transport_per_hari') + 1000"
    tipe_hasil: rupiah
    sumber: uji
"""


def test_masukan_wajib_berkas_aktif_diberi_nilai_contoh(tmp_path):
    from asisten_kb.rancangan import periksa_kb
    kinerja = _tulis(tmp_path, "kinerja.yaml", KINERJA)
    transport = _tulis(tmp_path, "transport.yaml", ke_yaml(ke_berkas(TRANSPORT_WAJIB)))
    # dua berkas dengan masukan wajib tanpa bawaan dapat aktif bersama
    assert periksa_kb([kinerja, transport]) == {"ok": True, "galat": [], "tahun": [2023, 2024, 2025, 2026, 2027]}
    v = validasi(MAKAN, [kinerja, transport], "makan.yaml")
    assert v["ok"], v["galat"]
    assert v["dampak"]
    for d in v["dampak"]:
        # nilai contoh hanya masukan baru milik rancangan; nilai bersama identik sebelum & sesudah -> selisih = komponen baru
        assert d["nilai_contoh"] == {}
        assert d["sesudah"]["bruto_setahun"] - d["sebelum"]["bruto_setahun"] == d["fakta_baru"]["px_makan"] > 0


def test_kb_aktif_yang_tidak_dapat_dihitung_bukan_galat_rancangan(tmp_path):
    v = validasi(ke_yaml(ke_berkas(USULAN)), [_tulis(tmp_path, "tgl.yaml", TGL)], "transport.yaml")
    assert not v["ok"] and v["galat"]
    assert all(g.startswith("KB aktif tidak dapat dihitung: ") for g in v["galat"]), v["galat"]
    assert "PPU-TGL-01" in v["galat"][0]


# ------------------------------------------------------------------------------------------- R3: tahun & cakupan simulasi

@pytest.mark.parametrize("berlaku, tahun", [
    ({"mulai": "2016-01-01"}, [2023, 2024, 2025, 2026]),
    ({"mulai": "2024-03-01"}, [2024, 2025, 2026]),
    ({"mulai": "2026-07-01"}, [2026, 2027]),
    ({"mulai": "2027-01-01"}, [2027, 2028]),
    ({"mulai": "2030-01-01"}, [2030]),
    ({"mulai": "2027-01-01", "sampai": "2027-06-30"}, [2027, 2028]),
    ({"mulai": "2016-01-01", "sampai": "2023-12-31"}, [2023, 2024]),
    ({"mulai": "2030-01-01", "sampai": "2030-12-31"}, [2030, 2031]),
    ({"mulai": "2035-01-01"}, []),
])
def test_tahun_simulasi_mengikuti_masa_berlaku(berlaku, tahun):
    from asisten_kb.rancangan import tahun_simulasi
    assert tahun_simulasi({"aturan": [{"berlaku": berlaku}]}) == tahun


def test_tahun_simulasi_dibatasi_delapan_dengan_tahun_awal_didahulukan():
    from asisten_kb.rancangan import tahun_simulasi
    data = {"aturan": [{"berlaku": {"mulai": "2016-01-01"}}, {"berlaku": {"mulai": "2028-01-01", "sampai": "2028-12-31"}}],
            "parameter": [{"berlaku": {"mulai": "2030-01-01", "sampai": "2030-06-30"}}],
            "klasifikasi_wajib": [{"berlaku": {"mulai": "2027-01-01"}}]}
    # 2026 (tahun lanjutan aturan lama) yang dikorbankan, bukan tahun pertama atau tahun sesudah `sampai`
    assert tahun_simulasi(data) == [2023, 2024, 2025, 2027, 2028, 2029, 2030, 2031]


@pytest.mark.parametrize("maka, pesan", [
    ("hr('uang_transport_per_hari') * 'a'", "simulasi Karyawan A 2027 gagal (aturan PPT-TRANSPORT-01): PelanggaranPresisi"),
    ("hr('uang_transport_per_hari') * faktor_tidak_ada", "faktor_tidak_ada' tidak dihasilkan aturan mana pun di tahun 2027"),
])
def test_rancangan_mulai_2027_disimulasikan_di_2027(maka, pesan):
    v = validasi(ke_yaml(ke_berkas(_usulan(aturan=[dict(ATURAN, mulai="2027-01-01", maka=maka)]))))
    assert not v["ok"] and any(pesan in g for g in v["galat"]), v["galat"]


def test_rancangan_di_luar_jangkauan_simulasi():
    v = validasi(ke_yaml(ke_berkas(_usulan(aturan=[dict(ATURAN, mulai="2035-01-01")]))))
    assert v["ok"] and v["dampak"] == []
    assert v["belum_teruji"] == [{"aturan": "PPT-TRANSPORT-01", "alasan": "masa berlaku di luar jangkauan simulasi"}]
    assert any("di luar jangkauan simulasi (2023-2031)" in p for p in v["peringatan"])


def test_pegawai_masuk_juli_dapat_dihitung_setiap_tahun():
    from asisten_kb.rancangan import kasus_masuk_juli
    from engine.kalkulator import hitung
    kb = muat_kb(BERKAS_PX)
    for tahun in range(2023, 2032):
        h = hitung(kasus_masuk_juli(tahun), kb=kb)
        assert list(h["per_masa"]) == [7, 8, 9, 10, 11, 12] and h["tahunan"]["bruto_setahun"] > 0
        assert all("px_thr" not in m for m in h["per_masa"].values())   # THR (April) jatuh sebelum masuk


BRUTO = """
lapisan: perusahaan
id: bruto
aturan:
  - id: PPB-BRUTO-01
    sifat: opsional
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: bruto
    maka: "0"
    tipe_hasil: rupiah
    sumber: uji
  - id: PPB-NOL-01
    sifat: opsional
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: px_tidak_pernah
    jika: "bulan == 13"
    maka: "1"
    tipe_hasil: bilangan
    sumber: uji
  - id: PPB-JULI-01
    sifat: opsional
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: px_pegawai_baru
    jika: "bulan_masuk == 7"
    maka: "1"
    tipe_hasil: bilangan
    sumber: uji
"""


def test_aturan_yang_tidak_pernah_terpilih_dilaporkan_belum_teruji():
    v = validasi(BRUTO)
    assert v["ok"], v["galat"]   # belum teruji = peringatan, bukan galat
    [kalah, mati] = v["belum_teruji"]   # PPB-JULI-01 hanya menyala untuk pegawai yang masuk Juli -> teruji
    assert kalah["aturan"] == "PPB-BRUTO-01" and kalah["alasan"].startswith("kalah dari R24-03") and "(lex_superior)" in kalah["alasan"]
    assert mati == {"aturan": "PPB-NOL-01", "alasan": "tidak pernah menyala pada simulasi (syarat atau masa berlaku tidak terpenuhi)"}
    assert any(p.startswith("aturan PPB-NOL-01 belum teruji: tidak pernah menyala") for p in v["peringatan"])
    juli = {d["pegawai"]: d["fakta_baru"]["px_pegawai_baru"] for d in v["dampak"] if d["tahun"] == 2026}
    assert juli == {"Karyawan A (contoh)": None, "Pegawai masuk Juli (contoh)": 6}
    # R4: perusahaan menulis fakta yang hanya dihasilkan regulasi
    assert any("PPB-BRUTO-01 menulis fakta 'bruto'" in p and "lex superior" in p for p in v["peringatan"])
    [ubah] = v["perubahan"]
    assert ubah["jenis"] == "aturan" and "R24-03b (regulasi/wajib)" in ubah["teks"]
    assert "dipakai di 0 masa, kalah di 36 masa" in ubah["teks"]   # 2026-2027 x (12 + 6 masa)


LEMBUR_DESEMBER = """
lapisan: perusahaan
id: lembur_desember
aturan:
  - id: PPL-LEMBUR-12
    sifat: opsional
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: px_lembur
    jika: "bulan == 12"
    maka: "500000"
    tipe_hasil: rupiah
    sumber: uji
"""


def test_fakta_baru_hanya_nilai_dari_aturan_rancangan():
    v = validasi(LEMBUR_DESEMBER)
    assert v["ok"], v["galat"]
    assert all(d["fakta_baru"] == {"px_lembur": 500_000} for d in v["dampak"])   # bukan lembur setahun dari PX-LEMBUR-01
    assert v["perubahan"] == [{"jenis": "aturan", "teks": (
        "PPL-LEMBUR-12 menghasilkan 'px_lembur' yang sudah dihasilkan PX-LEMBUR-01 (perusahaan/opsional); "
        "pada simulasi dipakai di 4 masa, kalah di 0 masa")}]


# ------------------------------------------------------------------------------------------- R4: perubahan

JP_SEMENTARA = """
lapisan: regulasi
id: jp_2027
aturan: []
parameter:
  - {nama: jp_batas_upah, nilai: 11500000, berlaku: {mulai: 2027-01-01, sampai: 2027-06-30}, sumber: uji}
klasifikasi_wajib:
  - {jenis: lembur, kategori: tidak_teratur, berlaku: {mulai: 2027-01-01}, sumber: uji}
  - {jenis: insentif_ota, kategori: teratur, berlaku: {mulai: 2027-01-01}, sumber: uji}
"""


def test_perubahan_parameter_dan_klasifikasi():
    v = validasi(JP_SEMENTARA)
    assert v["ok"], v["galat"]
    assert sorted({d["tahun"] for d in v["dampak"]}) == [2027, 2028]
    assert v["perubahan"] == [
        {"jenis": "parameter", "teks": "parameter jp_batas_upah: 11.086.300 -> 11.500.000 mulai 2027-01-01 sampai "
                                       "2027-06-30; setelah 2027-06-30 kembali 11.086.300"},
        {"jenis": "klasifikasi", "teks": "klasifikasi wajib lembur: teratur -> tidak_teratur mulai 2027-01-01 (tanpa batas akhir)"},
        {"jenis": "klasifikasi", "teks": "klasifikasi wajib baru insentif_ota -> teratur mulai 2027-01-01 (tanpa batas "
                                         "akhir); komponen perusahaan yang terkena: px_ota (tidak_teratur)"}]


def test_regulasi_rancangan_yang_mengalahkan_aturan_perusahaan_diperingatkan():
    teks = (LEMBUR_DESEMBER.replace("lapisan: perusahaan", "lapisan: regulasi").replace("sifat: opsional", "sifat: wajib")
            .replace('jika: "bulan == 12"\n    ', "").replace('maka: "500000"', "maka: \"hr_masa('lembur', 0)\""))
    v = validasi(teks)
    assert v["ok"], v["galat"]
    assert any("aturan regulasi rancangan PPL-LEMBUR-12 mengalahkan aturan perusahaan PX-LEMBUR-01 pada 'px_lembur'" in p
               for p in v["peringatan"]), v["peringatan"]
    assert "dipakai di 36 masa, kalah di 0 masa" in v["perubahan"][0]["teks"]


# ------------------------------------------------------------------------------------------- R5: lapisan pilihan unggah

def test_lapisan_unggah_dipaksakan_dan_pilihan_llm_disimpan(pdf):
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf), "lapisan": "regulasi"}, KlienTiruan(USULAN))
    u = jawab["usulan"]
    assert (u["lapisan"], u["lapisan_llm"]) == ("regulasi", "perusahaan")
    assert u["catatan_peninjau"][-1] == ("LLM menilai dokumen ini lapisan perusahaan; berkas dibuat sebagai lapisan regulasi "
                                         "sesuai pilihan unggahan")
    assert "lapisan: regulasi" in jawab["yaml"] and jawab["validasi"]["ringkasan"]["lapisan"] == "regulasi"
    assert any("komponen hanya boleh di lapisan perusahaan" in g for g in jawab["validasi"]["galat"])

    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf), "lapisan": "perusahaan"}, KlienTiruan(USULAN))
    assert jawab["usulan"]["lapisan_llm"] == "perusahaan" and jawab["usulan"]["catatan_peninjau"] == []


def test_validasi_jembatan_memperingatkan_lapisan_berbeda():
    y = ke_yaml(ke_berkas(USULAN))
    v = J.jalankan({"perintah": "validasi", "yaml": y, "lapisan": "regulasi"})["validasi"]
    assert "lapisan berkas 'perusahaan' berbeda dengan lapisan yang dipilih saat unggah 'regulasi'" in v["peringatan"]
    sama = J.jalankan({"perintah": "validasi", "yaml": y, "lapisan": "perusahaan"})["validasi"]
    assert sama["ok"] and not any("lapisan berkas" in p for p in sama["peringatan"])
    assert J.jalankan({"perintah": "validasi", "yaml": y, "lapisan": "pusat"})["jenis"] == "permintaan_tidak_valid"


# ------------------------------------------------------------------------------------------- R6: isi prompt

def test_prompt_memuat_aturan_main_yang_akurat():
    from asisten_kb.konteks import ATURAN_MAIN, instruksi
    teks = prompt_sistem(muat_kb(BERKAS_PX))
    assert len(teks) < 60_000
    for kata in ("`mulai` WAJIB diisi", "!= None", "selisih_hari(a, b) = jumlah hari dari a ke b",
                 "jumlah bulan penuh dari a ke b", "tanggal 1 setiap bulan", "(3) lex specialis: lebih banyak konjungsi",
                 # mengganti aturan: pencabutan eksplisit, bukan lagi dengan memenangkan lex specialis
                 "`menggantikan` berisi id aturan yang diganti", "tidak dipakai sama sekali, SEBELUM urutan",
                 "aturan baru tanpa `jika` boleh mengganti aturan lama yang ber-`jika`",
                 # janji validasi sebatas pegawai contoh: di luar itu pengganti ber-`jika` tidak teruji
                 "Validasi menolak rancangan bila itu terjadi pada\n  pegawai contoh simulasi, tetapi kasus lain tidak teruji",
                 "tulis aturan pengganti TANPA `jika` kecuali",
                 "TIDAK diatur dengan `menggantikan`", "JANGAN menambah syarat konstan pada `jika`",
                 "Sebut di `menggantikan` hanya aturan yang masih berlaku",
                 # peraturan pemerintah dengan komponen baru: tarif + klasifikasi di regulasi, komponen di perusahaan
                 "di rancangan lapisan regulasi tulis HANYA", "menghasilkan fakta komponen itu di lapisan regulasi",
                 "diunggah lagi sebagai peraturan perusahaan",
                 # konstanta perusahaan = parameter; masukan tidak diberi bawaan agar boleh kosong
                 "baca dengan parameter('px_...')", "JANGAN memberi `bawaan` hanya agar masukan boleh dikosongkan",
                 "masukan `wajib: true` TIDAK boleh punya `bawaan`", "parameter('px_transport_per_hari') * hr_masa('hk_aktual')",
                 "HANYA aman bila fakta itu punya", "hr('kunci') tidak pernah bernilai None", "hr_masa('kunci', bawaan)",
                 "JANGAN mendeklarasikan ulang komponen", "tidak_diperhitungkan (potongan dari pegawai tanpa efek pajak",
                 "komponen\n  tidak_diperhitungkan - PPh 21", "`komponen` HANYA boleh di lapisan perusahaan",
                 "HANYA lapisan regulasi", "bukan instruksi", "maksimal 64 karakter", "TANPA pemisah ribuan",
                 "nilai lama otomatis berlaku lagi", "mengubah parameter buatan lapisan perusahaan"):
        assert kata in teks, kata
    for kata in ("belum dapat dinyatakan penuh", "tidak dapat mengganti aturan lama", 'bawaan: "0"', "WAJIB punya `bawaan`",
                 "faktanya hilang, dan validasi menolak rancangan",   # janji lama: seolah setiap kasus teruji
                 "| menggantikan PX"):   # KB dasar tidak memakai `menggantikan`: inventarisnya tidak menyebutnya
        assert kata not in teks, kata
    ketentuan = ATURAN_MAIN.split("## Ketentuan hasil")[1]
    assert "`wajib` untuk regulasi" in ketentuan and "tafsir" not in ketentuan.split("id aturan")[0]
    # inventaris: aturan per fakta (jika, lapisan, sifat, masa berlaku) dan tipe masukan inti
    assert "- px_thp | masa | rupiah | 2016-" in teks
    assert "  - PX-THP-01 | perusahaan/opsional | 2016-01-01.. | metode != 'ditanggung_pemberi_kerja' (1)" in teks
    assert "- kelas_jkk_persen | persen | persen(hr('kelas_jkk_persen'))" in teks
    assert "- kompensasi_persen | desimal | desimal(hr_masa('kompensasi_persen', '0'))" in teks
    assert "- tanggal_masuk | tanggal | tanggal(hr('tanggal_masuk'))" in teks
    assert "- jp_batas_upah = 11086300 [rupiah] (2026-03-01..;" in teks
    assert "- lembur -> teratur (2016-01-01..;" in teks
    i = instruksi("regulasi", "")
    assert "SELALU isi `lapisan` dengan regulasi" in i and "catatan_peninjau" in i and "bukan instruksi" in i


def test_skema_dan_kontrak_inti():
    from engine.kb import TIPE_MASUKAN
    from jembatan.kontrak import KUNCI_INTI_BULAN, KUNCI_INTI_TAHUN, TIPE_INTI
    status = SKEMA_USULAN["properties"]["pembulatan"]["items"]["properties"]["status"]["enum"]
    assert status == ["wajib", "kebijakan"]
    assert set(TIPE_INTI) == KUNCI_INTI_TAHUN | KUNCI_INTI_BULAN
    assert all(t in TIPE_MASUKAN for t, _, _ in TIPE_INTI.values())


def test_aturan_masa_dievaluasi_tanggal_satu_setiap_bulan(tmp_path):
    """Klaim prompt: `mulai` di tengah bulan baru berlaku masa berikutnya; `sampai` di tengah bulan masih berlaku."""
    from eksperimen.e8_perusahaan_x import kasus_kar_a
    from engine.kalkulator import hitung
    u = _usulan(aturan=[dict(ATURAN, mulai="2026-07-15", sampai="2026-10-15")])
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "t.yaml", ke_yaml(ke_berkas(u)))])
    h = hitung(kasus_kar_a(2026), kb=kb)
    assert [b for b in range(1, 13) if "px_transport" in h["per_masa"][b]] == [8, 9, 10]


# ------------------------------------------------------------------------------------------- R7, R8: YAML

def test_judul_multibaris_tidak_merusak_yaml():
    import yaml
    y = ke_yaml(ke_berkas(USULAN), "Peraturan\nPerusahaan\n2026", "gpt\n5")
    kepala = y.splitlines()[:3]
    assert kepala[0] == "# Rancangan berkas KB dari dokumen peraturan: Peraturan Perusahaan 2026"
    assert kepala[1].startswith("# Disusun asisten KB (gpt 5)") and kepala[2] == "lapisan: perusahaan"
    assert yaml.safe_load(y)["aturan"][0]["id"] == "PPT-TRANSPORT-01"


@pytest.mark.parametrize("nilai, hasil", [
    ("12000000", 12_000_000), ("500.000", 500_000), ("12.000.000", 12_000_000), ("1,500,000", 1_500_000),
    ("-1.000", -1000), (" 750000 ", 750_000),
    ("11.5", "11.5"), ("0.300", "0.300"), ("1.500,50", "1.500,50"), ("12.00.000", "12.00.000"), ("Rp 5.000", "Rp 5.000"),
])
def test_nilai_rupiah_dengan_pemisah_ribuan(nilai, hasil):
    u = _usulan(parameter=[{"nama": "px_uang_saku", "nilai": nilai, "jenis_nilai": "rupiah", "mulai": "2026-01-01",
                            "sampai": "", "sumber": "uji"}],
                masukan=[dict(USULAN["masukan"][0], bawaan=nilai)])
    b = ke_berkas(u)
    assert b["parameter"][0]["nilai"] == hasil and type(b["parameter"][0]["nilai"]) is type(hasil)
    assert b["masukan"][0]["bawaan"] == (hasil.strip() if isinstance(hasil, str) else hasil)


def test_rupiah_yang_bukan_bilangan_bulat_ditolak_engine():
    u = _usulan(parameter=[{"nama": "jp_batas_upah", "nilai": "11.5", "jenis_nilai": "rupiah", "mulai": "2027-01-01",
                            "sampai": "", "sumber": "uji"}], lapisan="regulasi", komponen=[], masukan=[], aturan=[])
    v = validasi(ke_yaml(ke_berkas(u)))
    assert not v["ok"] and any("terbaca sebagai tarif" in g for g in v["galat"]), v["galat"]


# ------------------------------------------------------------------------------------------- R10: wajib efektif

WAJIB = """
lapisan: perusahaan
id: wajib
masukan:
  - {kunci: tanpa_bawaan, label: A, tipe: rupiah, lingkup: tahun, wajib: false}
  - {kunci: dengan_bawaan, label: B, tipe: rupiah, lingkup: tahun, wajib: true, bawaan: 0}
  - {kunci: bawaan_di_aturan, label: C, tipe: rupiah, lingkup: bulan, wajib: true}
  - {kunci: tidak_dibaca, label: D, tipe: rupiah, lingkup: tahun, wajib: false}
komponen:
  - {fakta: px_wajib, jenis: tunjangan_uji, kategori: teratur, label: Uji}
aturan:
  - id: PPW-WAJIB-01
    sifat: opsional
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: px_wajib
    maka: "hr('tanpa_bawaan') + hr('dengan_bawaan') + hr_masa('bawaan_di_aturan', 0)"
    tipe_hasil: rupiah
    sumber: uji
"""


def test_wajib_mengikuti_perilaku_engine(tmp_path):
    from asisten_kb.rancangan import masukan_tambahan
    kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, "wajib.yaml", WAJIB)])
    wajib = {m["kunci"]: m["wajib"] for m in masukan_tambahan(kb)}
    assert wajib == {"tanpa_bawaan": True, "dengan_bawaan": False, "bawaan_di_aturan": False, "tidak_dibaca": False}
    v = validasi(WAJIB)
    assert v["ok"], v["galat"]
    [p] = [p for p in v["peringatan"] if "dideklarasikan wajib: false" in p]
    assert p.startswith("masukan 'tanpa_bawaan' dideklarasikan wajib: false tetapi tanpa bawaan")


# ------------------------------------------------------------------------------------------- A1: fakta tanpa efek

TAPERA = """
lapisan: regulasi
id: tapera
aturan:
  - id: R-TAPERA-01
    sifat: wajib
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: iuran_tapera_pegawai
    maka: "250000"
    tipe_hasil: rupiah
    sumber: uji
"""
ATURAN_TAPERA = """  - id: R-TAPERA-02
    sifat: wajib
    berlaku: {mulai: 2026-01-01}
    lingkup: LINGKUP
    menghasilkan: FAKTA
    maka: "MAKA"
    tipe_hasil: TIPE
    sumber: uji
"""


def _tanpa_efek(v):
    return [p for p in v["peringatan"] if "tidak ikut bruto, PPh 21, maupun take home pay" in p]


def _tapera_dengan(fakta, maka, lingkup="masa", tipe="rupiah"):
    return TAPERA + (ATURAN_TAPERA.replace("LINGKUP", lingkup).replace("FAKTA", fakta).replace("MAKA", maka)
                     .replace("TIPE", tipe))


def test_fakta_rupiah_baru_tanpa_efek_diperingatkan():
    v = validasi(TAPERA)
    assert v["ok"], v["galat"]   # peringatan, bukan galat
    assert _tanpa_efek(v) == [
        "aturan R-TAPERA-01 menghasilkan fakta baru 'iuran_tapera_pegawai' yang bukan komponen dan tidak dibaca aturan "
        "mana pun, sehingga tidak ikut bruto, PPh 21, maupun take home pay; tulis tarif dan klasifikasi_wajib di berkas "
        "lapisan regulasi, lalu komponen dan aturannya di berkas perusahaan terpisah"]
    for d in v["dampak"]:   # lubang yang diperingatkan: fakta muncul, angka lain identik
        assert d["fakta_baru"]["iuran_tapera_pegawai"] > 0 and d["sesudah"] == d["sebelum"]

    # lapisan perusahaan: dua aturan untuk satu fakta -> satu peringatan, jalan keluarnya mendaftarkan komponen
    teks = (_tapera_dengan("px_tapera", "100000").replace("menghasilkan: iuran_tapera_pegawai", "menghasilkan: px_tapera")
            .replace("lapisan: regulasi", "lapisan: perusahaan").replace("sifat: wajib", "sifat: opsional"))
    [p] = _tanpa_efek(validasi(teks))
    assert p.startswith("aturan R-TAPERA-01, R-TAPERA-02 menghasilkan fakta baru 'px_tapera'")
    assert p.endswith("; daftarkan di komponen berkas ini")


@pytest.mark.parametrize("teks", [
    ke_yaml(ke_berkas(USULAN)),                                                  # dideklarasikan sebagai komponen
    TAPERA.replace("iuran_tapera_pegawai", "_bantu_tapera"),                      # fakta bantu
    TAPERA.replace("lingkup: masa", "lingkup: tahun"),                            # fakta tahunan
    TAPERA.replace("tipe_hasil: rupiah", "tipe_hasil: bilangan"),                 # bukan rupiah
    _tapera_dengan("_dasar_tapera", "iuran_tapera_pegawai * 2"),                  # dibaca aturan lain lewat nama
    _tapera_dengan("_tapera_setahun", "jumlah_masa('iuran_tapera_pegawai')", "tahun"),   # ... lewat argumen fungsi
    _tapera_dengan("_tapera_aman", "atau('iuran_tapera_pegawai', 0)"),
    LEMBUR_DESEMBER,                                                             # fakta yang sudah ada di KB aktif
])
def test_fakta_tanpa_efek_tidak_salah_tuduh(teks):
    v = validasi(teks)
    assert v["ok"], v["galat"]
    assert _tanpa_efek(v) == []


# ------------------------------------------------------------------------------------------- A2: masukan dengan bawaan

def test_masukan_dengan_bawaan_diperingatkan():
    v = validasi(WAJIB)
    assert v["ok"], v["galat"]
    bawaan = [p for p in v["peringatan"] if "bawaan 0" in p]
    assert bawaan == [
        "masukan 'dengan_bawaan' dideklarasikan wajib: true tetapi punya bawaan 0; keduanya bertentangan: engine memakai "
        "bawaan bila nilainya kosong, sehingga pegawai yang belum diisi dihitung dengan 0 tanpa galat; hapus 'bawaan' "
        "bila nilainya memang wajib diisi, atau tulis wajib: false"]
    # masukan tanpa bawaan (wajib atau tidak) tidak diperingatkan soal bawaan
    assert not any("punya bawaan" in p for p in validasi(ke_yaml(ke_berkas(TRANSPORT_WAJIB)))["peringatan"])

    # wajib tidak ditulis (bawaan skema) atau wajib: false -> peringatan nilai diam-diam + saran parameter perusahaan
    for wajib in ("", ", wajib: false"):
        teks = WAJIB.replace(", wajib: true, bawaan: 0", wajib + ", bawaan: 25000")
        [p] = [p for p in validasi(teks)["peringatan"] if "punya bawaan" in p]
        assert p == ("masukan 'dengan_bawaan' punya bawaan 25.000: pegawai yang nilainya kosong dihitung dengan 25.000 "
                     "tanpa tanda apa pun; nilai yang sama untuk seluruh perusahaan lebih tepat menjadi parameter "
                     "perusahaan (parameter px_... di berkas lapisan perusahaan, dibaca dengan parameter('...')), bukan "
                     "masukan per pegawai")


def test_bawaan_deklarasi_yang_kalah_oleh_bawaan_di_aturan():
    # engine/inferensi.py _hr: hr_masa('k', 0) mengembalikan 0 sebelum melihat bawaan deklarasi
    teks = WAJIB.replace("lingkup: bulan, wajib: true}", "lingkup: bulan, bawaan: 5000}")
    v = validasi(teks)
    assert v["ok"], v["galat"]
    [p] = [p for p in v["peringatan"] if "'bawaan_di_aturan'" in p]
    assert p == ("masukan 'bawaan_di_aturan' punya bawaan 5.000, tetapi bawaan itu tidak pernah dipakai: aturan yang "
                 "membacanya (PPW-WAJIB-01) memberi bawaan sendiri lewat hr_masa('bawaan_di_aturan', ...), dan engine "
                 "mendahulukan bawaan di aturan; pegawai yang nilainya kosong dihitung dengan bawaan di aturan tanpa "
                 "tanda apa pun; hapus 'bawaan' di deklarasi, atau hapus bawaan di aturan bila 5.000 yang dimaksud")
    assert "dihitung dengan 5.000" not in p
    # wajib: true yang ditulis tidak mengubahnya: angka deklarasi tetap bukan angka yang dipakai engine
    [p] = [p for p in validasi(teks.replace("bulan, bawaan: 5000}", "bulan, wajib: true, bawaan: 5000}"))["peringatan"]
           if "'bawaan_di_aturan'" in p]
    assert "tidak pernah dipakai" in p and "dihitung dengan 5.000" not in p
    # satu pembaca tanpa bawaan di aturan -> bawaan deklarasi dipakai di sana: peringatan biasa
    [p] = [p for p in validasi(teks.replace("hr_masa('bawaan_di_aturan', 0)", "hr_masa('bawaan_di_aturan')"))["peringatan"]
           if "'bawaan_di_aturan'" in p]
    assert p.startswith("masukan 'bawaan_di_aturan' punya bawaan 5.000: pegawai yang nilainya kosong dihitung dengan 5.000")


def test_bawaan_bilangan_ditulis_tanpa_pemisah_ribuan():
    teks = WAJIB.replace("{kunci: tidak_dibaca, label: D, tipe: rupiah, lingkup: tahun, wajib: false}",
                         "{kunci: tidak_dibaca, label: D, tipe: bilangan, lingkup: tahun, wajib: false, bawaan: 2026}")
    [p] = [p for p in validasi(teks)["peringatan"] if "'tidak_dibaca'" in p]
    assert p.startswith("masukan 'tidak_dibaca' punya bawaan 2026: ")   # dulu "2.026", seperti nominal rupiah


# ------------------------------------------------------------------------------------------- simulasi metode gross-up

GANTI_TUNJANGAN = """
lapisan: regulasi
id: ganti_tunjangan
aturan:
  - id: PPG-GANTI-01
    sifat: wajib
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: tunjangan_pajak_berjalan
    jika: "gross_up and not masa_terakhir"
    maka: "pph21_berjalan"
    tipe_hasil: rupiah
    sumber: uji
"""
GANTI_TUNJANGAN_SAH = GANTI_TUNJANGAN.replace(
    '    tipe_hasil: rupiah\n', '    tipe_hasil: rupiah\n    titik_tetap: true\n'
                                '    batas_titik_tetap: {bawah: "0", atas: "_bruto_dasar"}\n')


def test_simulasi_gross_up_menangkap_pengganti_aturan_titik_tetap_tanpa_tanda():
    # pegawai contoh bermetode gross: tanpa simulasi gross-up rancangan ini lolos, lalu setiap pegawai gross-up gagal
    v = validasi(GANTI_TUNJANGAN)
    assert not v["ok"]
    assert v["galat"] == [
        f"simulasi Karyawan A {t} metode gross-up gagal: KesalahanKB: PPG-GANTI-01 menggantikan R24-05a pada fakta titik "
        "tetap tunjangan_pajak_berjalan[1] tetapi tidak bertanda titik_tetap/batas_titik_tetap; tambahkan keduanya pada "
        "PPG-GANTI-01" for t in (2026, 2027)]
    # simulasi metode gross tetap berjalan; gross-up tidak menambah baris tabel dampak
    assert [(d["pegawai"], d["tahun"]) for d in v["dampak"]] == [
        ("Karyawan A (contoh)", 2026), ("Pegawai masuk Juli (contoh)", 2026),
        ("Karyawan A (contoh)", 2027), ("Pegawai masuk Juli (contoh)", 2027)]


def test_pengganti_aturan_titik_tetap_teruji_lewat_simulasi_gross_up():
    v = validasi(GANTI_TUNJANGAN_SAH)
    assert v["ok"], v["galat"]
    assert v["belum_teruji"] == []   # dulu "tidak pernah menyala": hanya metode gross yang disimulasikan
    assert v["perubahan"] == [{"jenis": "aturan", "teks": (
        "PPG-GANTI-01 menghasilkan 'tunjangan_pajak_berjalan' yang sudah dihasilkan R24-05a (regulasi/wajib); pada "
        "simulasi metode gross-up dipakai di 22 masa, kalah di 0 masa")}]


def test_periksa_kb_ikut_memeriksa_metode_gross_up(tmp_path):
    from asisten_kb.rancangan import periksa_kb

    assert periksa_kb([_tulis(tmp_path, "sah.yaml", GANTI_TUNJANGAN_SAH)]) == {"ok": True, "galat": [],
                                                                               "tahun": [2023, 2024, 2025, 2026, 2027]}
    p = periksa_kb([_tulis(tmp_path, "rusak.yaml", GANTI_TUNJANGAN)])
    assert not p["ok"]
    assert [g.split(":")[0] for g in p["galat"]] == ["Karyawan A 2026 metode gross-up tidak dapat dihitung",
                                                       "Karyawan A 2027 metode gross-up tidak dapat dihitung"]
    assert all("PPG-GANTI-01 menggantikan R24-05a" in g for g in p["galat"])


JKM_BERVERSI = """
lapisan: regulasi
id: jkm
aturan: []
parameter:
  - {nama: jkm_pk_persen, nilai: "0.2", berlaku: {mulai: 2026-01-01}, sumber: uji}
"""


def test_perubahan_menyebut_akhir_efektif_amandemen_berlaku_surut(tmp_path):
    # amandemen berlaku surut kini termuat: versi aktif yang mulai lebih baru menutupnya, dan peninjau harus tahu
    aktif = _tulis(tmp_path, "jkm_2026.yaml", JKM_BERVERSI)
    surut = JKM_BERVERSI.replace('"0.2"', '"0.1"').replace("2026-01-01", "2025-01-01")
    v = validasi(surut, [aktif], "jkm_2025.yaml")
    assert v["ok"], v["galat"]
    assert v["perubahan"] == [{"jenis": "parameter", "teks": (
        "parameter jkm_pk_persen: 0.3 -> 0.1 mulai 2025-01-01 (tanpa batas akhir); efektif hanya sampai 2025-12-31: versi "
        "yang mulai 2026-01-01 sudah ada (0.2)")}]
    # amandemen sementara yang langsung disusul versi aktif: sesudahnya bukan "kembali" ke nilai lama
    sementara = surut.replace("{mulai: 2025-01-01}", "{mulai: 2025-01-01, sampai: 2025-12-31}")
    [ubah] = validasi(sementara, [aktif], "jkm_2025.yaml")["perubahan"]
    assert ubah["teks"] == ("parameter jkm_pk_persen: 0.3 -> 0.1 mulai 2025-01-01 sampai 2025-12-31; setelah 2025-12-31 "
                            "berlaku 0.2 (versi lain yang sudah ada)")


# ------------------------------------------------------------------------------------------- R11: LLM

def test_batas_pdf_413_dan_runtimeerror_stream(pdf):
    import anthropic
    import openai

    from asisten_kb.llm import BATAS_PDF, GagalLLM, _galat_api, minta_usulan

    assert BATAS_PDF == 20 * 1024 * 1024
    with pytest.raises(GagalLLM, match="maksimal 20 MB"):
        minta_usulan(b"%" * (BATAS_PDF + 1), "s", "i", klien=KlienTiruan(USULAN))
    for sdk, model in ((openai, "gpt-5.6-sol"), (anthropic, "claude-opus-5-5")):
        e = sdk.APIStatusError.__new__(sdk.APIStatusError)
        e.__dict__.update(status_code=413, message="request too large")
        assert str(_galat_api(sdk, e, model)) == "PDF terlalu besar untuk API; pecah dokumen menjadi bagian yang lebih kecil"

    class AliranRusak:
        def __iter__(self):
            raise RuntimeError("Expected to have received `response.created` before `response.output_text.delta`")
    klien = SimpleNamespace(responses=SimpleNamespace(stream=lambda **kw: _Konteks(AliranRusak())))
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf)}, klien)
    assert jawab["jenis"] == "gagal_llm" and jawab["pesan"].startswith("aliran jawaban API gagal: Expected")


# ------------------------------------------------------------------------------------------- menggantikan (pencabutan eksplisit)

THP_BARU = """
lapisan: perusahaan
id: thp_baru
aturan:
  - id: UJI-THP-BARU
    sifat: opsional
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: px_thp
    menggantikan: [PX-THP-01, PX-THP-02]
    maka: "px_penghasilan_tunai - pph21"
    tipe_hasil: rupiah
    sumber: uji
"""
THP_TANPA_FIELD = THP_BARU.replace("    menggantikan: [PX-THP-01, PX-THP-02]\n", "")


def _dengan_jika(teks, jika):
    return teks.replace("    maka:", f'    jika: "{jika}"\n    maka:')


def test_skema_usulan_dan_konversi_menggantikan(pdf):
    properti = SKEMA_USULAN["properties"]["aturan"]["items"]
    assert properti["properties"]["menggantikan"]["type"] == "array"
    assert properti["properties"]["menggantikan"]["items"] == {"type": "string"}
    assert "menggantikan" in properti["required"] and set(properti["required"]) == set(ATURAN)   # skema ketat: semua wajib
    # daftar kosong (atau field tidak ada) tidak ditulis: skema KB menolak `menggantikan: []`
    assert "menggantikan" not in ke_berkas(USULAN)["aturan"][0]
    assert "menggantikan" not in ke_berkas(_usulan(aturan=[{k: v for k, v in ATURAN.items() if k != "menggantikan"}]))["aturan"][0]
    assert "menggantikan" not in ke_berkas(_usulan(aturan=[dict(ATURAN, menggantikan=["", " "])]))["aturan"][0]
    thp = dict(ATURAN, id="UJI-THP-BARU", mulai="2026-01-01", menghasilkan="px_thp", maka="px_penghasilan_tunai - pph21",
               menggantikan=["PX-THP-01", " PX-THP-02 ", "PX-THP-01"])
    u = _usulan(aturan=[thp], komponen=[], masukan=[])
    e = ke_berkas(u)["aturan"][0]
    assert e["menggantikan"] == ["PX-THP-01", "PX-THP-02"]
    assert list(e)[:6] == ["id", "sifat", "berlaku", "lingkup", "menghasilkan", "menggantikan"]
    # dari keluaran LLM (tiruan) sampai berkas KB yang lolos validasi engine
    jawab = J.jalankan({"perintah": "usulkan", "pdf": str(pdf), "lapisan": "perusahaan"}, KlienTiruan(u))
    assert jawab["ok"] and jawab["validasi"]["ok"], jawab["validasi"]["galat"]
    assert "  menggantikan:\n  - PX-THP-01\n  - PX-THP-02\n" in jawab["yaml"]
    assert jawab["validasi"]["isi"]["aturan"][0]["menggantikan"] == ["PX-THP-01", "PX-THP-02"]


@pytest.mark.parametrize("berlaku, teks", [
    ("{mulai: 2026-01-01}", "mulai 2026-01-01; pada simulasi dipakai di 36 masa"),   # 2026-2027 x (12 + 6 masa)
    ("{mulai: 2026-03-01, sampai: 2026-08-31}",
     "mulai 2026-03-01 sampai 2026-08-31; sesudahnya aturan lama berlaku lagi; pada simulasi dipakai di 8 masa"),
])
def test_perubahan_menyebut_aturan_yang_digantikan(berlaku, teks):
    v = validasi(THP_BARU.replace("{mulai: 2026-01-01}", berlaku))
    assert v["ok"], v["galat"]
    # satu entri saja: aturan yang digantikan bukan pesaing lagi, jadi tidak dilaporkan ulang sebagai "sudah dihasilkan"
    assert v["perubahan"] == [{"jenis": "aturan", "teks": f"UJI-THP-BARU menggantikan PX-THP-01, PX-THP-02 (fakta 'px_thp') {teks}"}]
    assert v["peringatan"] == [] and v["belum_teruji"] == []   # aturan tanpa `jika` mengganti dua aturan ber-`jika`
    assert v["dampak"][0]["fakta_baru"]["px_thp"] > 0
    assert all(d["sesudah"]["pph21_setahun"] == d["sebelum"]["pph21_setahun"] for d in v["dampak"])   # hanya THP yang berubah


def test_penggantian_sebagian_melaporkan_pesaing_yang_tersisa():
    v = validasi(THP_BARU.replace("[PX-THP-01, PX-THP-02]", "[PX-THP-02]"))
    assert v["ok"], v["galat"]
    assert [u["teks"] for u in v["perubahan"]] == [
        "UJI-THP-BARU menggantikan PX-THP-02 (fakta 'px_thp') mulai 2026-01-01; pada simulasi dipakai di 0 masa",
        "UJI-THP-BARU menghasilkan 'px_thp' yang sudah dihasilkan PX-THP-01 (perusahaan/opsional); pada simulasi dipakai di "
        "0 masa, kalah di 36 masa (dikalahkan PX-THP-01)"]
    assert ("aturan UJI-THP-BARU kalah di 36 masa dari PX-THP-01 (lex_specialis); bila UJI-THP-BARU dimaksudkan mengganti "
            "PX-THP-01, tulis menggantikan: [PX-THP-01]") in v["peringatan"]


def test_fakta_yang_hilang_karena_pengganti_lebih_sempit_adalah_galat():
    v = validasi(_dengan_jika(THP_BARU, "bulan != 12"))
    assert not v["ok"]
    assert v["galat"] == [
        "aturan UJI-THP-BARU menggantikan PX-THP-01, PX-THP-02 tetapi tidak mencakup semua kasusnya: fakta 'px_thp' yang "
        "sebelumnya bernilai tidak lagi dihasilkan di 6 masa simulasi, mis. Karyawan A 2026 bulan 12; perluas atau hapus "
        "`jika` UJI-THP-BARU, atau tambahkan aturan untuk kasus yang tidak tercakup"]
    # pengganti sementara: masa di luar rentangnya dilayani aturan lama lagi, bukan fakta yang hilang
    sementara = _dengan_jika(THP_BARU, "bulan != 12").replace("{mulai: 2026-01-01}", "{mulai: 2026-03-01, sampai: 2026-08-31}")
    assert validasi(sementara)["galat"] == []
    # pengganti sementara yang sempit DI DALAM rentangnya: hanya masa di dalam rentang (Juni-Agustus) yang dihitung hilang
    sempit = _dengan_jika(THP_BARU, "bulan < 6").replace("{mulai: 2026-01-01}", "{mulai: 2026-03-01, sampai: 2026-08-31}")
    assert validasi(sempit)["galat"] == [
        "aturan UJI-THP-BARU menggantikan PX-THP-01, PX-THP-02 tetapi tidak mencakup semua kasusnya: fakta 'px_thp' yang "
        "sebelumnya bernilai tidak lagi dihasilkan di 8 masa simulasi, mis. Karyawan A 2026 bulan 6; perluas atau hapus "
        "`jika` UJI-THP-BARU, atau tambahkan aturan untuk kasus yang tidak tercakup"]


def test_pengganti_ber_jika_yang_lolos_simulasi_tetap_diperingatkan(tmp_path):
    # pegawai contoh bermetode gross dan gross-up: pegawai bermetode ditanggung pemberi kerja kehilangan px_thp tanpa terlihat
    v = validasi(_dengan_jika(THP_BARU, "metode != 'ditanggung_pemberi_kerja'"))
    assert v["ok"], v["galat"]
    assert v["peringatan"] == [
        "aturan UJI-THP-BARU menggantikan PX-THP-01, PX-THP-02 tetapi ber-`jika`: pada kasus di luar `jika` itu fakta "
        "'px_thp' tidak lagi dihasilkan. Simulasi hanya menguji pegawai contoh (metode gross dan gross-up), jadi kasus lain "
        "yang dicakup PX-THP-01, PX-THP-02 (mis. metode pajak atau status pegawai lain) tidak teruji; pastikan `jika` "
        "UJI-THP-BARU mencakup semuanya, atau hapus `jika` itu"]
    from eksperimen.e8_perusahaan_x import kasus_kar_a
    from engine.kalkulator import hitung
    dtp = dict(kasus_kar_a(2026), metode="ditanggung_pemberi_kerja")   # bukti bahwa peringatan itu bukan dugaan kosong
    sempit = _tulis(tmp_path, "thp_sempit.yaml", _dengan_jika(THP_BARU, "metode != 'ditanggung_pemberi_kerja'"))
    assert "px_thp" in hitung(copy.deepcopy(dtp), kb=muat_kb(BERKAS_PX))["per_masa"][1]
    assert "px_thp" not in hitung(copy.deepcopy(dtp), kb=muat_kb([*BERKAS_PX, sempit]))["per_masa"][1]
    # sudah menjadi galat (terlihat pada pegawai contoh): tidak diperingatkan dua kali
    assert validasi(_dengan_jika(THP_BARU, "bulan != 12"))["peringatan"] == []
    # ada aturan tanpa `jika` yang tidak dicabut untuk fakta yang sama: faktanya tidak dapat hilang
    aman = _dengan_jika(THP_BARU, "bulan != 12") + ATURAN_SISA
    v = validasi(aman)
    assert v["ok"], v["galat"]
    assert not any("ber-`jika`" in p for p in v["peringatan"])


ATURAN_SISA = """  - id: UJI-THP-SISA
    sifat: opsional
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: px_thp
    maka: "px_penghasilan_tunai"
    tipe_hasil: rupiah
    sumber: uji
"""


def test_rantai_pengganti_galat_hanya_pada_pengganti_yang_menyempit():
    # E (tanpa `jika`) mencabut aturan KB aktif, Z (ber-`jika`) mencabut E: Desember 2027 hilang karena Z, bukan E
    rantai = THP_BARU.replace("UJI-THP-BARU", "E-THP-01") + _dengan_jika(
        ATURAN_SISA.replace("UJI-THP-SISA", "Z-THP-01").replace("2026-01-01", "2027-01-01")
        .replace("    maka:", "    menggantikan: [E-THP-01]\n    maka:"), "bulan != 12")
    v = validasi(rantai)
    assert v["galat"] == [
        "aturan Z-THP-01 menggantikan E-THP-01 tetapi tidak mencakup semua kasusnya: fakta 'px_thp' yang sebelumnya "
        "bernilai tidak lagi dihasilkan di 6 masa simulasi, mis. Karyawan A 2027 bulan 12; perluas atau hapus `jika` "
        "Z-THP-01, atau tambahkan aturan untuk kasus yang tidak tercakup"]
    assert not any("E-THP-01 menggantikan" in t for t in v["galat"] + v["peringatan"])


def test_pengganti_lebih_sempit_atas_aturan_rancangan_sendiri_adalah_galat():
    # px_uji_isian belum ada di KB aktif: pembandingnya rancangan yang sama tanpa pencabutan di dalamnya
    sempit = ISIAN_DIGANTI.replace("    menggantikan: [UJI-ISIAN-01]\n", '    menggantikan: [UJI-ISIAN-01]\n    jika: "bulan != 12"\n')
    v = validasi(sempit)
    assert v["galat"] == [
        "aturan UJI-ISIAN-02 menggantikan UJI-ISIAN-01 tetapi tidak mencakup semua kasusnya: fakta 'px_uji_isian' yang "
        "dihasilkan aturan yang digantikannya (dari rancangan ini juga) tidak lagi dihasilkan di 4 masa simulasi, mis. "
        "Karyawan A 2027 bulan 12; perluas atau hapus `jika` UJI-ISIAN-02, atau tambahkan aturan untuk kasus yang tidak "
        "tercakup"]
    v = validasi(ISIAN_DIGANTI)   # pengganti tanpa `jika`: tidak ada yang hilang
    assert v["ok"] and v["peringatan"] == [], v


def test_fakta_hilang_yang_dibaca_aturan_lain_diberi_keterangan():
    # px_penghasilan_tunai dibaca PX-THP-01/02: simulasi gagal lebih dulu, dan pesan engine tidak menyebut aturan pengganti
    teks = _dengan_jika(THP_BARU.replace("px_thp", "px_penghasilan_tunai").replace("[PX-THP-01, PX-THP-02]", "[PX-THP-00]")
                        .replace("px_penghasilan_tunai - pph21", "komponen('teratur')"), "bulan != 12")
    v = validasi(teks)
    assert not v["ok"] and all(g.startswith("simulasi ") for g in v["galat"])
    [p] = [p for p in v["peringatan"] if p.startswith("kemungkinan penyebab simulasi gagal")]
    assert "aturan UJI-THP-BARU menggantikan PX-THP-00 tetapi ber-`jika`" in p
    assert "fakta 'px_penghasilan_tunai' tidak lagi dihasilkan, padahal dibaca PX-THP-01, PX-THP-02" in p


def test_aturan_yang_kalah_tanpa_menggantikan_diperingatkan():
    v = validasi(THP_TANPA_FIELD)
    assert v["ok"], v["galat"]
    assert [p for p in v["peringatan"] if "tulis menggantikan" in p] == [
        "aturan UJI-THP-BARU kalah di 36 masa dari PX-THP-01 (lex_specialis); bila UJI-THP-BARU dimaksudkan mengganti "
        "PX-THP-01, tulis menggantikan: [PX-THP-01]"]
    assert "(dikalahkan PX-THP-01)" in v["perubahan"][0]["teks"] and len(v["perubahan"]) == 1
    # kalah antar-lapisan (lex superior) tidak dapat diatasi dengan `menggantikan`: tidak disarankan
    assert not any("tulis menggantikan" in p for p in validasi(BRUTO)["peringatan"])


def test_syarat_konstan_di_jika_diperingatkan():
    # dua konjungsi mengalahkan PX-THP-01 (satu konjungsi) tanpa menguji apa pun lebih banyak
    v = validasi(_dengan_jika(THP_TANPA_FIELD, "metode != 'ditanggung_pemberi_kerja' and True and 1 == 1"))
    assert v["ok"], v["galat"]
    assert v["peringatan"] == [
        "aturan UJI-THP-BARU: `jika` memuat syarat konstan (True, 1 == 1) yang tidak menguji apa pun; jumlah konjungsi `and` "
        "menentukan lex specialis, sehingga syarat itu hanya menaikkan peringkat aturan; hapus syarat itu, dan bila "
        "UJI-THP-BARU dimaksudkan mengganti aturan lain tulis menggantikan: [id aturan itu]"]
    assert "dipakai di 36 masa, kalah di 0 masa" in v["perubahan"][0]["teks"]
    # syarat sungguhan (nama fakta, pemanggilan fungsi) dan konstanta di dalam `or` bukan konjungsi konstan
    for jika in ("bulan != 12 and metode != 'x'", "hr_masa('hk_aktual') > 0 and (bulan == 1 or True)"):
        assert not any("syarat konstan" in p for p in validasi(_dengan_jika(THP_TANPA_FIELD, jika))["peringatan"]), jika
    # konstanta yang selalu salah bukan soal peringkat: aturannya tidak pernah menyala
    [p] = [p for p in validasi(_dengan_jika(THP_TANPA_FIELD, "False and bulan > 0"))["peringatan"] if "syarat konstan" in p]
    assert p == ("aturan UJI-THP-BARU: `jika` memuat syarat konstan (False) yang selalu salah, sehingga aturan ini tidak "
                 "akan pernah menyala; hapus syarat itu")


ISIAN_DIGANTI = """
lapisan: perusahaan
id: isian_diganti
komponen:
  - {fakta: px_uji_isian, jenis: tunjangan_uji, kategori: teratur, label: Uji}
masukan:
  - {kunci: uang_lama, label: Uang lama, tipe: rupiah, lingkup: tahun, wajib: true}
  - {kunci: uang_baru, label: Uang baru, tipe: rupiah, lingkup: tahun, wajib: true}
aturan:
  - id: UJI-ISIAN-01
    sifat: opsional
    berlaku: {mulai: 2026-01-01}
    lingkup: masa
    menghasilkan: px_uji_isian
    jika: "bulan >= 1"
    maka: "hr('uang_lama')"
    tipe_hasil: rupiah
    sumber: uji
  - id: UJI-ISIAN-02
    sifat: opsional
    berlaku: {mulai: 2027-01-01}
    lingkup: masa
    menghasilkan: px_uji_isian
    menggantikan: [UJI-ISIAN-01]
    maka: "hr('uang_baru')"
    tipe_hasil: rupiah
    sumber: uji
"""


def test_isian_aturan_yang_dicabut_permanen_tidak_lagi_diminta(tmp_path):
    from asisten_kb.rancangan import masukan_tambahan

    def rentang(teks, nama):
        kb = muat_kb([*BERKAS_PX, _tulis(tmp_path, nama, teks)])
        return {m["kunci"]: (m["mulai"], m["sampai"]) for m in masukan_tambahan(kb)}

    assert rentang(ISIAN_DIGANTI, "permanen.yaml") == {"uang_lama": ("2026-01-01", "2026-12-31"),
                                                       "uang_baru": ("2027-01-01", None)}
    # pengganti sementara: aturan lama berlaku lagi sesudahnya, jadi isiannya tetap diminta tanpa batas akhir
    sementara = ISIAN_DIGANTI.replace("{mulai: 2027-01-01}", "{mulai: 2027-01-01, sampai: 2027-06-30}")
    assert rentang(sementara, "sementara.yaml") == {"uang_lama": ("2026-01-01", None),
                                                    "uang_baru": ("2027-01-01", "2027-06-30")}
    # tanpa field: rentang = masa berlaku aturan itu sendiri, seperti sebelumnya
    tanpa = ISIAN_DIGANTI.replace("    menggantikan: [UJI-ISIAN-01]\n", "")
    assert rentang(tanpa, "tanpa.yaml") == {"uang_lama": ("2026-01-01", None), "uang_baru": ("2027-01-01", None)}
    v = validasi(ISIAN_DIGANTI)   # 2027: uang_lama tidak dibaca lagi, aturan baru dipakai di setiap masa
    assert v["ok"], v["galat"]
    assert {m["kunci"]: m["sampai"] for m in v["masukan"]} == {"uang_lama": "2026-12-31", "uang_baru": None}


def test_inventaris_prompt_menyebut_aturan_yang_digantikan(tmp_path):
    teks = prompt_sistem(muat_kb([*BERKAS_PX, _tulis(tmp_path, "thp_baru.yaml", THP_BARU)]))
    assert "  - UJI-THP-BARU | perusahaan/opsional | 2026-01-01.. | - (0) | menggantikan PX-THP-01, PX-THP-02" in teks
    assert "  - PX-THP-01 | perusahaan/opsional | 2016-01-01.. | metode != 'ditanggung_pemberi_kerja' (1)\n" in teks


def test_contoh_di_prompt_lolos_validasi_tanpa_peringatan():
    """Contoh rancangan di prompt (konstanta perusahaan sebagai parameter, tanpa masukan ber-bawaan) memang sah."""
    from asisten_kb.konteks import CONTOH
    assert "parameter: [{nama: px_transport_per_hari" in CONTOH and "masukan: []" in CONTOH
    u = _usulan(masukan=[], aturan=[dict(ATURAN, maka="parameter('px_transport_per_hari') * hr_masa('hk_aktual')")],
                parameter=[{"nama": "px_transport_per_hari", "nilai": "25000", "jenis_nilai": "rupiah", "mulai": "2026-07-01",
                            "sampai": "", "sumber": "Peraturan Perusahaan 2026 Ps. 12 ayat (1)"}])
    v = validasi(ke_yaml(ke_berkas(u)))
    assert v["ok"], v["galat"]
    assert v["peringatan"] == [] and v["masukan"] == []
    assert all(d["fakta_baru"]["px_transport"] > 0 for d in v["dampak"])
