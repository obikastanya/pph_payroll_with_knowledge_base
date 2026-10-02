"""Panggilan Claude: PDF peraturan -> rancangan berkas KB (keluaran terstruktur sesuai asisten_kb/skema.py)."""
import base64
import json

from .skema import SKEMA_USULAN

MODEL_BAWAAN = "claude-opus-5-5"
BATAS_PDF = 30 * 1024 * 1024   # batas permintaan API 32 MB (base64 menambah ~33%)


class GagalLLM(RuntimeError):
    """LLM tidak menghasilkan rancangan yang dapat dipakai (kredensial, jaringan, penolakan, keluaran terpotong)."""


def minta_usulan(pdf, sistem, instruksi, model=MODEL_BAWAAN, klien=None):
    """-> (usulan: dict sesuai SKEMA_USULAN, info: dict model/pemakaian token). `klien` dapat diganti (tes)."""
    if len(pdf) > BATAS_PDF:
        raise GagalLLM(f"PDF terlalu besar ({len(pdf) // (1024 * 1024)} MB; maksimal 30 MB)")
    import anthropic  # di sini, bukan di atas: jembatan & tes tetap jalan tanpa paket ini selama LLM tidak dipanggil
    try:
        klien = klien or anthropic.Anthropic()
        with klien.beta.messages.stream(
            model=model,
            max_tokens=64000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            thinking={"type": "adaptive"},
            output_config={"effort": "high", "format": {"type": "json_schema", "schema": SKEMA_USULAN}},
            # prompt sistem stabil (aturan main + inventaris KB) -> di-cache antar dokumen
            system=[{"type": "text", "text": sistem, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf",
                                                "data": base64.standard_b64encode(pdf).decode("ascii")}},
                {"type": "text", "text": instruksi},
            ]}],
        ) as stream:
            pesan = stream.get_final_message()
    except anthropic.AuthenticationError:
        raise GagalLLM("kunci API Anthropic tidak valid atau belum diatur (ANTHROPIC_API_KEY)") from None
    except anthropic.PermissionDeniedError as e:
        raise GagalLLM(f"akses ke model ditolak: {e.message}") from None
    except anthropic.RateLimitError:
        raise GagalLLM("batas pemakaian API tercapai; coba lagi beberapa saat lagi") from None
    except anthropic.BadRequestError as e:
        raise GagalLLM(f"permintaan ditolak API: {e.message}") from None
    except anthropic.APIStatusError as e:
        raise GagalLLM(f"galat server API ({e.status_code}); coba lagi nanti") from None
    except anthropic.APIConnectionError:
        raise GagalLLM("tidak dapat terhubung ke API Anthropic (periksa koneksi internet/proxy)") from None

    if pesan.stop_reason == "refusal":
        raise GagalLLM("model menolak memproses dokumen ini")
    if pesan.stop_reason == "max_tokens":
        raise GagalLLM("keluaran model terpotong (dokumen terlalu panjang); pecah PDF menjadi bagian yang lebih kecil")
    teks = next((b.text for b in pesan.content if b.type == "text"), None)
    if not teks:
        raise GagalLLM("model tidak mengembalikan rancangan")
    try:
        usulan = json.loads(teks)
    except json.JSONDecodeError as e:
        raise GagalLLM(f"keluaran model bukan JSON yang sah: {e}") from None
    u = pesan.usage
    info = {"model": pesan.model, "token_masuk": u.input_tokens, "token_keluar": u.output_tokens,
            "token_cache_baca": getattr(u, "cache_read_input_tokens", 0) or 0,
            "token_cache_tulis": getattr(u, "cache_creation_input_tokens", 0) or 0}
    return usulan, info
