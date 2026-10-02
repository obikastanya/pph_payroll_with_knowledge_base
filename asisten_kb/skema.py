"""Skema keluaran terstruktur LLM (structured outputs). Semua properti wajib; isian kosong = "" atau [] agar
skema tetap sederhana dan pasti valid. Konversi ke berkas KB YAML ada di asisten_kb/rancangan.py."""

KATEGORI_KOMPONEN = ["teratur", "tidak_teratur", "premi_objek", "natura", "iuran_pengurang", "zakat", "bukan_objek",
                     "tidak_diperhitungkan"]
MODE_PEMBULATAN = ["bawah", "atas", "menuju_nol", "setengah_atas", "setengah_menjauhi_nol", "setengah_genap"]


def _obj(properti):
    return {"type": "object", "properties": properti, "required": list(properti), "additionalProperties": False}


_S = {"type": "string"}
_DAFTAR_S = {"type": "array", "items": {"type": "string"}}

SKEMA_USULAN = _obj({
    "ringkasan": _S,
    "dapat_dikodifikasi": {"type": "boolean"},
    "alasan": _S,
    "lapisan": {"type": "string", "enum": ["regulasi", "perusahaan"]},
    "id_berkas": _S,
    "keterangan": _S,
    "komponen": {"type": "array", "items": _obj({
        "fakta": _S, "jenis": _S, "kategori": {"type": "string", "enum": KATEGORI_KOMPONEN}, "label": _S})},
    "masukan": {"type": "array", "items": _obj({
        "kunci": _S, "label": _S,
        "tipe": {"type": "string", "enum": ["rupiah", "bilangan", "persen", "desimal", "tanggal", "pilihan", "ya_tidak"]},
        "lingkup": {"type": "string", "enum": ["tahun", "bulan"]},
        "wajib": {"type": "boolean"}, "bawaan": _S, "pilihan": _DAFTAR_S, "keterangan": _S, "sumber": _S})},
    "parameter": {"type": "array", "items": _obj({
        "nama": _S, "nilai": _S, "jenis_nilai": {"type": "string", "enum": ["rupiah", "pecahan"]},
        "mulai": _S, "sampai": _S, "sumber": _S})},
    "pembulatan": {"type": "array", "items": _obj({
        "id": _S, "titik": _S, "satuan": {"type": "integer"}, "mode": {"type": "string", "enum": MODE_PEMBULATAN},
        "urutan": {"type": "string", "enum": ["per_komponen", "sekali"]},
        "status": {"type": "string", "enum": ["wajib", "tafsir", "kebijakan"]}, "dasar": _S})},
    "aturan": {"type": "array", "items": _obj({
        "id": _S, "sifat": {"type": "string", "enum": ["wajib", "default", "opsional"]},
        "mulai": _S, "sampai": _S, "lingkup": {"type": "string", "enum": ["masa", "tahun"]},
        "menghasilkan": _S, "jika": _S, "maka": _S,
        "tipe_hasil": {"type": "string", "enum": ["rupiah", "tarif", "kategori", "bool", "bilangan", "eksak"]},
        "pembulatan": _S, "sumber": _S, "catatan": _S})},
    "klasifikasi_wajib": {"type": "array", "items": _obj({
        "jenis": _S, "kategori": {"type": "string", "enum": KATEGORI_KOMPONEN}, "mulai": _S, "sampai": _S, "sumber": _S})},
    "rujukan": {"type": "array", "items": _obj({"bagian": _S, "halaman": {"type": "integer"}, "kutipan": _S})},
    "catatan_peninjau": _DAFTAR_S,
})
