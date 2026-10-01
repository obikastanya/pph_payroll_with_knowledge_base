"""Tabel bertingkat dengan semantik interval eksplisit (research_plan.md §6.9.3).

Bunyi regulasi "di atas a sampai dengan b" = interval (a, b]. Lapisan pertama = [0, b].
Domain lookup adalah int rupiah: bruto pecahan wajib dibulatkan dulu (BULAT-BRUTO-01),
sehingga lookup menolak Fraction alih-alih diam-diam memilih lapisan.
"""
from dataclasses import dataclass
from fractions import Fraction

from .angka import PelanggaranPresisi


@dataclass(frozen=True)
class Lapisan:
    bawah: int            # eksklusif, kecuali lapisan pertama (bawah = 0, inklusif)
    atas: object          # int inklusif, atau None = tak terbatas
    tarif: Fraction

    def memuat(self, x):
        di_atas_bawah = x >= 0 if self.bawah == 0 else x > self.bawah
        return di_atas_bawah and (self.atas is None or x <= self.atas)

    def __str__(self):
        kiri = "[" if self.bawah == 0 else "("
        kanan = "∞)" if self.atas is None else f"{self.atas}]"
        return f"{kiri}{self.bawah}, {kanan} -> {self.tarif}"


class TabelBertingkat:
    """Tabel lapisan yang divalidasi: mulai dari 0, bersambung tanpa celah/tumpang tindih, berakhir di ∞."""

    def __init__(self, nama, lapisan):
        self.nama = nama
        self.lapisan = tuple(lapisan)
        self._validasi()

    def _validasi(self):
        L = self.lapisan
        if not L:
            raise PelanggaranPresisi(f"{self.nama}: tabel kosong")
        for i, l in enumerate(L):
            for v in (l.bawah, l.atas):
                if v is not None and (isinstance(v, bool) or not isinstance(v, int)):
                    raise PelanggaranPresisi(f"{self.nama}: batas lapisan {i + 1} bukan int: {v!r}")
            if not isinstance(l.tarif, Fraction):
                raise PelanggaranPresisi(f"{self.nama}: tarif lapisan {i + 1} bukan Fraction")
            if l.tarif < 0 or l.tarif >= 1:
                raise PelanggaranPresisi(f"{self.nama}: tarif lapisan {i + 1} di luar [0, 1): {l.tarif}")
            if l.atas is not None and l.atas <= l.bawah:
                raise PelanggaranPresisi(f"{self.nama}: lapisan {i + 1} kosong/terbalik")
        if L[0].bawah != 0:
            raise PelanggaranPresisi(f"{self.nama}: lapisan pertama tidak mulai dari 0")
        for i in range(1, len(L)):
            if L[i - 1].atas is None:
                raise PelanggaranPresisi(f"{self.nama}: lapisan tak terbatas bukan yang terakhir")
            if L[i].bawah != L[i - 1].atas:
                jenis = "celah" if L[i].bawah > L[i - 1].atas else "tumpang tindih"
                raise PelanggaranPresisi(
                    f"{self.nama}: {jenis} antara lapisan {i} (atas {L[i - 1].atas}) "
                    f"dan {i + 1} (bawah {L[i].bawah})")
        if L[-1].atas is not None:
            raise PelanggaranPresisi(f"{self.nama}: lapisan terakhir harus tak terbatas")

    def monoton(self):
        """True bila tarif tidak pernah turun saat lapisan naik."""
        return all(a.tarif <= b.tarif for a, b in zip(self.lapisan, self.lapisan[1:]))

    def cari(self, x):
        if isinstance(x, bool) or not isinstance(x, int):
            raise PelanggaranPresisi(
                f"{self.nama}: lookup wajib int rupiah, diterima {type(x).__name__} {x!r} "
                f"(bulatkan dulu sesuai BULAT-BRUTO-01)")
        if x < 0:
            raise PelanggaranPresisi(f"{self.nama}: nilai negatif {x}")
        for l in self.lapisan:
            if l.memuat(x):
                return l
        raise PelanggaranPresisi(f"{self.nama}: {x} tidak tercakup")  # tidak terjangkau bila valid

    def batas(self):
        """Semua batas atas berhingga (titik uji b-1, b, b+1)."""
        return [l.atas for l in self.lapisan if l.atas is not None]


def tabel_ter(baris, kategori):
    """Bangun tabel TER bulanan satu kategori dari hasil ``muat_tabel('ter_bulanan')``."""
    pilih = sorted((b for b in baris if b["kategori"] == kategori), key=lambda b: int(b["urutan"]))
    if not pilih:
        raise PelanggaranPresisi(f"kategori TER {kategori!r} tidak ditemukan")
    return TabelBertingkat(
        f"TER-{kategori}",
        [Lapisan(b["batas_bawah"], b["batas_atas"], b["tarif_desimal"]) for b in pilih])


def tabel_pasal17(baris, rezim="UU HPP"):
    """Bangun tabel tarif Pasal 17 dari hasil ``muat_tabel('tarif_pasal17')``."""
    pilih = sorted((b for b in baris if b["rezim"] == rezim), key=lambda b: int(b["lapisan"]))
    if not pilih:
        raise PelanggaranPresisi(f"rezim Pasal 17 {rezim!r} tidak ditemukan")
    return TabelBertingkat(
        f"Pasal17-{rezim}",
        [Lapisan(b["pkp_batas_bawah"], b["pkp_batas_atas"], b["tarif_persen"]) for b in pilih])


def pajak_progresif(tabel, pkp):
    """Pajak progresif eksak (Fraction) atas pkp int: Σ tarif_i × bagian pkp di lapisan i."""
    if isinstance(pkp, bool) or not isinstance(pkp, int) or pkp < 0:
        raise PelanggaranPresisi(f"PKP wajib int >= 0: {pkp!r}")
    total = Fraction(0)
    for l in tabel.lapisan:
        if pkp <= l.bawah:
            break
        atas = pkp if l.atas is None else min(pkp, l.atas)
        total += (atas - l.bawah) * l.tarif
    return total
