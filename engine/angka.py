"""Kontrak aritmetika (research_plan.md §6.9.1, AR-1..AR-3).

- Nilai uang final: ``int`` rupiah (bukan ``bool``, bukan ``float``).
- Nilai antara yang belum dibulatkan: ``Fraction`` eksak.
- Tarif/persentase: ``Fraction`` yang dibaca dari STRING desimal, tidak pernah dari float.
"""
import re
from decimal import Decimal
from fractions import Fraction

_POLA_DESIMAL = re.compile(r"^-?\d+(\.\d+)?$")
_POLA_BULAT = re.compile(r"^-?\d+$")


class PelanggaranPresisi(ValueError):
    """Nilai melanggar kontrak presisi (float, tipe salah, atau format tidak eksak)."""


def tarif(teks):
    """String desimal (mis. ``"0.0025"``) -> ``Fraction`` eksak.

    Menolak float, karena ``float`` tidak dapat menyimpan mis. 0,29 secara persis.
    """
    if not isinstance(teks, str):
        raise PelanggaranPresisi(f"tarif wajib string desimal, diterima {type(teks).__name__}: {teks!r}")
    s = teks.strip()
    if not _POLA_DESIMAL.match(s):
        raise PelanggaranPresisi(f"format tarif tidak valid: {teks!r}")
    return Fraction(s)


def persen(teks):
    """String persen (mis. ``"1.5"`` berarti 1,5%) -> ``Fraction`` eksak (3/200)."""
    return tarif(teks) / 100


def rupiah(nilai):
    """Terima ``int`` atau string bilangan bulat -> ``int`` rupiah. Menolak float/bool/pecahan."""
    if isinstance(nilai, bool):
        raise PelanggaranPresisi(f"bool bukan rupiah: {nilai!r}")
    if isinstance(nilai, int):
        return nilai
    if isinstance(nilai, str) and _POLA_BULAT.match(nilai.strip()):
        return int(nilai.strip())
    raise PelanggaranPresisi(f"rupiah wajib bilangan bulat, diterima {type(nilai).__name__}: {nilai!r}")


def eksak(nilai):
    """``int``/``Fraction``/``Decimal`` -> ``Fraction``. Menolak float dan bool."""
    if isinstance(nilai, bool) or isinstance(nilai, float):
        raise PelanggaranPresisi(f"nilai tidak eksak: {nilai!r}")
    if isinstance(nilai, (int, Fraction)):
        return Fraction(nilai)
    if isinstance(nilai, Decimal):
        return Fraction(nilai)
    raise PelanggaranPresisi(f"tipe tidak didukung: {type(nilai).__name__}")


def pastikan_rupiah(nilai, nama="nilai"):
    """Asersi keluaran (MR11): nilai uang final wajib ``int`` dan bukan ``bool``."""
    if isinstance(nilai, bool) or not isinstance(nilai, int):
        raise PelanggaranPresisi(f"{nama} wajib int rupiah, ditemukan {type(nilai).__name__}: {nilai!r}")
    return nilai
