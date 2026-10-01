"""Registri pembulatan (research_plan.md §6.9.2).

Setiap aturan yang menghasilkan rupiah wajib merujuk satu entri registri. Mode pembulatan
didefinisikan eksplisit, termasuk untuk bilangan negatif (mis. lebih bayar masa terakhir):

    bawah                  -> floor, menuju -tak hingga
    atas                   -> ceiling, menuju +tak hingga
    menuju_nol             -> truncate
    setengah_atas          -> pecahan >= 1/2 dibulatkan menuju +tak hingga
    setengah_menjauhi_nol  -> pecahan >= 1/2 dibulatkan menjauhi nol (perilaku Excel ROUND)
    setengah_genap         -> pecahan == 1/2 ke bilangan genap (banker's; perilaku round() Python)

Catatan: ``round()`` bawaan Python adalah setengah_genap. Itulah sebabnya ``round()`` dilarang
di engine (tes ``test_kontrak_tanpa_float``) dan semua pembulatan wajib lewat modul ini.
"""
from dataclasses import dataclass
from fractions import Fraction

from .angka import PelanggaranPresisi, eksak

MODE = ("bawah", "atas", "menuju_nol", "setengah_atas", "setengah_menjauhi_nol", "setengah_genap")
STATUS = ("wajib", "tafsir", "kebijakan")
SETENGAH = Fraction(1, 2)


def bulatkan(nilai, mode, satuan=1):
    """Bulatkan ``nilai`` (int/Fraction) ke kelipatan ``satuan`` rupiah dengan ``mode``. Hasil: int."""
    if mode not in MODE:
        raise PelanggaranPresisi(f"mode pembulatan tidak dikenal: {mode!r}")
    if isinstance(satuan, bool) or not isinstance(satuan, int) or satuan <= 0:
        raise PelanggaranPresisi(f"satuan wajib int > 0: {satuan!r}")
    q = eksak(nilai) / satuan
    lantai = q.numerator // q.denominator
    sisa = q - lantai                      # 0 <= sisa < 1
    if sisa == 0:
        n = lantai
    elif mode == "bawah":
        n = lantai
    elif mode == "atas":
        n = lantai + 1
    elif mode == "menuju_nol":
        n = lantai if q >= 0 else lantai + 1
    elif mode == "setengah_atas":
        n = lantai + 1 if sisa >= SETENGAH else lantai
    elif mode == "setengah_menjauhi_nol":
        if q >= 0:
            n = lantai + 1 if sisa >= SETENGAH else lantai
        else:
            n = lantai if sisa <= SETENGAH else lantai + 1
    else:  # setengah_genap
        if sisa > SETENGAH:
            n = lantai + 1
        elif sisa < SETENGAH:
            n = lantai
        else:
            n = lantai if lantai % 2 == 0 else lantai + 1
    return n * satuan


@dataclass(frozen=True)
class EntriPembulatan:
    id: str
    titik: str
    satuan: int
    mode: str
    urutan: str
    status: str
    dasar: str
    alternatif: tuple = ()

    def validasi(self):
        if self.mode not in MODE:
            raise PelanggaranPresisi(f"{self.id}: mode {self.mode!r} tidak dikenal")
        if self.status not in STATUS:
            raise PelanggaranPresisi(f"{self.id}: status {self.status!r} tidak dikenal")
        if isinstance(self.satuan, bool) or not isinstance(self.satuan, int) or self.satuan <= 0:
            raise PelanggaranPresisi(f"{self.id}: satuan wajib int > 0")
        for m in self.alternatif:
            if m not in MODE:
                raise PelanggaranPresisi(f"{self.id}: alternatif {m!r} tidak dikenal")
        if self.mode in self.alternatif:
            raise PelanggaranPresisi(f"{self.id}: mode default tidak boleh muncul di alternatif")
        if len(set(self.alternatif)) != len(self.alternatif):
            raise PelanggaranPresisi(f"{self.id}: alternatif duplikat")
        if self.status == "wajib" and self.alternatif:
            raise PelanggaranPresisi(f"{self.id}: aturan wajib tidak boleh punya alternatif tafsir")
        if self.status == "tafsir" and not self.alternatif:
            raise PelanggaranPresisi(f"{self.id}: aturan tafsir wajib punya >= 1 alternatif")
        if not self.dasar.strip():
            raise PelanggaranPresisi(f"{self.id}: dasar (sumber/alasan) wajib diisi")


class RegistriPembulatan:
    """Kumpulan entri pembulatan; satu-satunya jalan untuk membulatkan rupiah di engine."""

    def __init__(self, entri):
        self._entri = {}
        for e in entri:
            e.validasi()
            if e.id in self._entri:
                raise PelanggaranPresisi(f"id pembulatan duplikat: {e.id}")
            self._entri[e.id] = e

    @classmethod
    def dari_data(cls, data):
        """Dari struktur hasil ``muat_yaml`` (list of dict)."""
        entri = []
        for d in data:
            entri.append(EntriPembulatan(
                id=d["id"], titik=d["titik"], satuan=d["satuan"], mode=d["mode"],
                urutan=d["urutan"], status=d["status"], dasar=d["dasar"],
                alternatif=tuple(d.get("alternatif") or ())))
        return cls(entri)

    def __contains__(self, id_):
        return id_ in self._entri

    def __iter__(self):
        return iter(self._entri.values())

    def entri(self, id_):
        try:
            return self._entri[id_]
        except KeyError:
            raise PelanggaranPresisi(f"entri pembulatan tidak terdaftar: {id_}") from None

    def terapkan(self, id_, nilai, mode=None):
        """Bulatkan dengan mode default entri, atau dengan salah satu mode alternatifnya."""
        e = self.entri(id_)
        if mode is None:
            mode = e.mode
        elif mode != e.mode and mode not in e.alternatif:
            raise PelanggaranPresisi(f"{id_}: mode {mode!r} bukan default/alternatif terdaftar")
        return bulatkan(nilai, mode, e.satuan)

    def semua_varian(self, id_, nilai):
        """Hasil untuk mode default dan setiap alternatif -> dasar 'rentang tafsir' (§6.9.6)."""
        e = self.entri(id_)
        return {m: bulatkan(nilai, m, e.satuan) for m in (e.mode, *e.alternatif)}
