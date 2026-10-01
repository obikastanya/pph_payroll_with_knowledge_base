"""Model waktu tiga tanggal (research_plan.md §6.9.4).

- PMK 168/2023 Pasal 19 ayat (1): PPh 21 terutang pada saat pembayaran atau terutangnya
  penghasilan, MANA YANG TERJADI LEBIH DAHULU.
- PER-16/PJ/2016 Pasal 21 ayat (1) & (3) (rezim 2023): "pada saat dilakukan pembayaran atau
  pada saat terutangnya penghasilan"; frasa "mana yang lebih dahulu" tidak eksplisit, sehingga
  penerapan min() untuk 2023 dicatat sebagai tafsir WAKTU-P16-01.
- Parameter BPJS mengikuti periode iuran (= periode kerja), bukan masa pajak.
"""
import re
from dataclasses import dataclass
from datetime import date

from .angka import PelanggaranPresisi

_POLA_PERIODE = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")
TAFSIR_WAKTU_2023 = "WAKTU-P16-01"


class InputTidakValid(ValueError):
    """Input melanggar skema/invarian; perhitungan pegawai tersebut dihentikan (§6.9.5)."""


def periode(teks):
    """'YYYY-MM' -> (tahun, bulan)."""
    if not isinstance(teks, str):
        raise InputTidakValid(f"periode wajib string 'YYYY-MM': {teks!r}")
    m = _POLA_PERIODE.match(teks)
    if not m:
        raise InputTidakValid(f"format periode tidak valid (YYYY-MM): {teks!r}")
    return int(m.group(1)), int(m.group(2))


def tanggal(teks):
    if isinstance(teks, date):
        return teks
    if not isinstance(teks, str):
        raise InputTidakValid(f"tanggal wajib string ISO 'YYYY-MM-DD': {teks!r}")
    try:
        return date.fromisoformat(teks)
    except ValueError:
        raise InputTidakValid(f"tanggal tidak valid: {teks!r}") from None


@dataclass(frozen=True)
class TransaksiPenghasilan:
    komponen: str
    nominal: int
    periode_kerja: tuple          # (tahun, bulan)
    tanggal_terutang: date
    tanggal_bayar: object = None  # date atau None (belum dibayar)

    @classmethod
    def dari_data(cls, d):
        wajib = ("komponen", "nominal", "periode_kerja", "tanggal_terutang")
        kurang = [k for k in wajib if d.get(k) in (None, "")]
        if kurang:
            raise InputTidakValid(f"DATA_KURANG: field wajib kosong {kurang} pada {d!r}")
        nominal = d["nominal"]
        if isinstance(nominal, bool) or not isinstance(nominal, int):
            raise InputTidakValid(f"nominal wajib int rupiah: {nominal!r}")
        if nominal < 0:
            raise InputTidakValid(f"nominal negatif tidak diterima (koreksi diproses terpisah): {nominal}")
        bayar = d.get("tanggal_bayar")
        return cls(
            komponen=d["komponen"], nominal=nominal, periode_kerja=periode(d["periode_kerja"]),
            tanggal_terutang=tanggal(d["tanggal_terutang"]),
            tanggal_bayar=tanggal(bayar) if bayar not in (None, "") else None)

    @property
    def saat_terutang(self):
        """min(tanggal_bayar, tanggal_terutang) — REG-WAKTU-01."""
        if self.tanggal_bayar is None:
            return self.tanggal_terutang
        return min(self.tanggal_bayar, self.tanggal_terutang)

    @property
    def masa_pajak(self):
        """(tahun, bulan) masa pajak = bulan saat terutang."""
        s = self.saat_terutang
        return s.year, s.month

    @property
    def tahun_pajak(self):
        return self.saat_terutang.year

    @property
    def periode_iuran(self):
        """Sumbu waktu parameter BPJS (REG-WAKTU-02)."""
        return self.periode_kerja

    def tafsir_waktu(self):
        """Daftar id tafsir yang memengaruhi penentuan masa transaksi ini."""
        return [TAFSIR_WAKTU_2023] if self.tahun_pajak <= 2023 and self.tanggal_bayar is not None \
            and self.tanggal_bayar != self.tanggal_terutang else []


def pastikan_berurutan(awal, akhir, nama_awal, nama_akhir):
    if akhir < awal:
        raise InputTidakValid(f"{nama_akhir} ({akhir}) sebelum {nama_awal} ({awal})")


def pastikan_tahun_pajak(transaksi, tahun):
    """Tolak transaksi yang masa pajaknya bukan tahun yang sedang dihitung (cegah salah tahun)."""
    if transaksi.tahun_pajak != tahun:
        raise PelanggaranPresisi(
            f"transaksi {transaksi.komponen} terutang di {transaksi.masa_pajak}, bukan tahun {tahun}")
