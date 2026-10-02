"""Panggilan LLM: PDF peraturan -> rancangan berkas KB (keluaran terstruktur sesuai asisten_kb/skema.py).

Penyedia dipilih dari nama model: `gpt-...` (bawaan, OpenAI Responses API) atau `claude-...` (Anthropic Messages API).
Keduanya menerima PDF apa adanya dan dipaksa menjawab dengan JSON yang cocok dengan SKEMA_USULAN.
"""
import base64
import json

from .skema import SKEMA_USULAN

MODEL_BAWAAN = "gpt-5.6-sol"
BATAS_PDF = 30 * 1024 * 1024   # batas permintaan API 32 MB (base64 menambah ~33%)
BATAS_KELUARAN = 64000         # token keluaran, termasuk penalaran
KUNCI_API = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}   # variabel lingkungan per penyedia


class GagalLLM(RuntimeError):
    """LLM tidak menghasilkan rancangan yang dapat dipakai (kredensial, jaringan, penolakan, keluaran terpotong)."""


def penyedia(model):
    return "anthropic" if model.startswith("claude") else "openai"


def minta_usulan(pdf, sistem, instruksi, model=MODEL_BAWAAN, klien=None):
    """-> (usulan: dict sesuai SKEMA_USULAN, info: dict model/pemakaian token). `klien` dapat diganti (tes)."""
    if len(pdf) > BATAS_PDF:
        raise GagalLLM(f"PDF terlalu besar ({len(pdf) // (1024 * 1024)} MB; maksimal 30 MB)")
    panggil = _lewat_claude if penyedia(model) == "anthropic" else _lewat_openai
    teks, info = panggil(base64.standard_b64encode(pdf).decode("ascii"), sistem, instruksi, model, klien)
    if not teks:
        raise GagalLLM("model tidak mengembalikan rancangan")
    try:
        usulan = json.loads(teks)
    except json.JSONDecodeError as e:
        raise GagalLLM(f"keluaran model bukan JSON yang sah: {e}") from None
    return usulan, info


def _galat_api(modul, e, model):
    """Galat SDK (openai / anthropic punya hierarki kelas yang sama) -> GagalLLM berbahasa pengguna."""
    kunci = KUNCI_API[penyedia(model)]
    if isinstance(e, modul.AuthenticationError):
        return GagalLLM(f"kunci API tidak valid atau belum diatur ({kunci})")
    if isinstance(e, modul.PermissionDeniedError):
        return GagalLLM(f"akses ke model ditolak: {e.message}")
    if isinstance(e, modul.NotFoundError):
        return GagalLLM(f"model '{model}' tidak ditemukan atau tidak tersedia untuk kunci API ini (periksa PAYROLL_LLM_MODEL)")
    if isinstance(e, modul.RateLimitError):
        return GagalLLM("batas pemakaian atau kuota API tercapai; coba lagi beberapa saat lagi")
    if isinstance(e, modul.BadRequestError):
        return GagalLLM(f"permintaan ditolak API: {e.message}")
    if isinstance(e, modul.APIStatusError):
        return GagalLLM(f"galat server API ({e.status_code}); coba lagi nanti")
    if isinstance(e, modul.APIConnectionError):
        return GagalLLM("tidak dapat terhubung ke API LLM (periksa koneksi internet/proxy)")
    return GagalLLM(f"klien LLM gagal: {e}")


def _lewat_openai(pdf_b64, sistem, instruksi, model, klien):
    import openai  # di sini, bukan di atas: jembatan & tes tetap jalan tanpa paket ini selama LLM tidak dipanggil
    try:
        klien = klien or openai.OpenAI()
        with klien.responses.stream(
            model=model,
            # instruksi stabil (aturan main + inventaris KB) di depan -> prefiksnya di-cache otomatis antar dokumen
            instructions=sistem,
            prompt_cache_key="asisten-kb",
            input=[{"role": "user", "content": [
                {"type": "input_file", "filename": "peraturan.pdf", "file_data": f"data:application/pdf;base64,{pdf_b64}"},
                {"type": "input_text", "text": instruksi},
            ]}],
            text={"format": {"type": "json_schema", "name": "usulan_kb", "strict": True, "schema": SKEMA_USULAN}},
            reasoning={"effort": "high"},
            max_output_tokens=BATAS_KELUARAN,
            store=False,   # dokumen peraturan perusahaan tidak disimpan di sisi penyedia
        ) as stream:
            # baca event terminal sendiri: stream.get_final_response() hanya menerima response.completed dan melempar
            # RuntimeError untuk jawaban terpotong/gagal, padahal keduanya perlu pesan yang jelas bagi pengguna
            r = None
            for ev in stream:
                if ev.type in ("response.completed", "response.incomplete", "response.failed"):
                    r = ev.response
                elif ev.type == "error":
                    raise GagalLLM(f"API mengirim galat di tengah jawaban: {getattr(ev, 'message', '')}")
    except openai.OpenAIError as e:
        raise _galat_api(openai, e, model) from None
    if r is None:
        raise GagalLLM("aliran jawaban terputus sebelum selesai; coba lagi")

    alasan = getattr(r.incomplete_details, "reason", None)
    if r.status == "incomplete" and alasan == "max_output_tokens":
        raise GagalLLM("keluaran model terpotong (dokumen terlalu panjang); pecah PDF menjadi bagian yang lebih kecil")
    if r.status == "incomplete" and alasan == "content_filter":
        raise GagalLLM("model menolak memproses dokumen ini")
    if r.status != "completed":
        raise GagalLLM(f"model tidak menyelesaikan jawaban (status {r.status}{f': {r.error.message}' if r.error else ''})")
    for butir in r.output:
        for isi in getattr(butir, "content", None) or []:
            if isi.type == "refusal":
                raise GagalLLM("model menolak memproses dokumen ini")
    u = r.usage
    rinci = getattr(u, "input_tokens_details", None)
    return r.output_text, {"model": r.model, "token_masuk": u.input_tokens, "token_keluar": u.output_tokens,
                           "token_cache_baca": getattr(rinci, "cached_tokens", 0) or 0,
                           "token_cache_tulis": getattr(rinci, "cache_write_tokens", 0) or 0}


def _lewat_claude(pdf_b64, sistem, instruksi, model, klien):
    import anthropic
    try:
        klien = klien or anthropic.Anthropic()
        with klien.beta.messages.stream(
            model=model,
            max_tokens=BATAS_KELUARAN,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            thinking={"type": "adaptive"},
            output_config={"effort": "high", "format": {"type": "json_schema", "schema": SKEMA_USULAN}},
            # prompt sistem stabil (aturan main + inventaris KB) -> di-cache antar dokumen
            system=[{"type": "text", "text": sistem, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
                {"type": "text", "text": instruksi},
            ]}],
        ) as stream:
            pesan = stream.get_final_message()
    except anthropic.AnthropicError as e:
        raise _galat_api(anthropic, e, model) from None

    if pesan.stop_reason == "refusal":
        raise GagalLLM("model menolak memproses dokumen ini")
    if pesan.stop_reason == "max_tokens":
        raise GagalLLM("keluaran model terpotong (dokumen terlalu panjang); pecah PDF menjadi bagian yang lebih kecil")
    u = pesan.usage
    return next((b.text for b in pesan.content if b.type == "text"), None), {
        "model": pesan.model, "token_masuk": u.input_tokens, "token_keluar": u.output_tokens,
        "token_cache_baca": getattr(u, "cache_read_input_tokens", 0) or 0,
        "token_cache_tulis": getattr(u, "cache_creation_input_tokens", 0) or 0}
