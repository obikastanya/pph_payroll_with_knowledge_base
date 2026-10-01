"""Mesin inferensi (research_plan.md §6.3–§6.7).

Evaluasi data-driven (forward chaining terstratifikasi):
  1. aturan yang berlaku di tahun pajak dan varian tafsir aktif dipilih;
  2. graf dependensi antar-fakta dibangun dari ekspresi `jika`/`maka`;
  3. komponen terhubung kuat (SCC) diurutkan topologis; SCC bersiklus WAJIB memuat aturan
     `titik_tetap: true` -> diselesaikan dengan iterasi Kleene dari 0 (titik tetap terkecil);
  4. setiap instance fakta (per masa atau per tahun) dipilih aturannya lewat resolusi konflik:
     lex superior (regulasi wajib > perusahaan) -> override sah (perusahaan > regulasi default)
     -> lex specialis (konjungsi terbanyak) -> lex posterior (mulai berlaku terakhir)
     -> prioritas eksplisit; sisa seri dengan nilai berbeda = AMBIGU (galat);
  5. setiap nilai dicatat bersama aturan, sumber pasal, dan aturan yang ditolak (jejak).
"""
from datetime import date
from fractions import Fraction

from .angka import PelanggaranPresisi
from .kb import FAKTA_DASAR_MASA, FAKTA_DASAR_TAHUN, FUNGSI, KesalahanKB, parameter_pada
from .pembulatan import bulatkan as _bulatkan

BATAS_ITERASI = 10_000


class KasusTidakDidukung(ValueError):
    pass


class Ambigu(KesalahanKB):
    pass


def _normal(v):
    if isinstance(v, Fraction) and v.denominator == 1:
        return int(v)
    return v


class Evaluasi:
    def __init__(self, kb, kasus, varian=None):
        self.kb = kb
        self.kasus = kasus
        self.varian = dict(varian or {})
        self.tahun = kasus["tahun_pajak"]
        self.masa = sorted(kasus["masa"], key=lambda m: (m["bulan"] is None, m["bulan"] or 0))
        self.bulan = [m["bulan"] for m in self.masa]
        self.komp = {m["bulan"]: m["komponen"] for m in self.masa}
        self.dasar_tahun = self._fakta_dasar()
        self.nilai_tahun = {}
        self.nilai_masa = {b: {} for b in self.bulan}
        self.peringatan = []
        self.iterasi_titik_tetap = []
        self.aturan = self._pilih_aturan()
        self.urutan = self._urutan_evaluasi()

    # ------------------------------------------------------------------ fakta dasar
    def _fakta_dasar(self):
        k, p = self.kasus, self.kasus["pegawai"]
        cakupan = k["cakupan"]
        rapel = (k.get("riwayat") or {}).get("rapel") or {}
        terakhir = (p.get("bulan_terakhir_bekerja") or 12) if cakupan == "setahun" else None
        return {
            "tahun_pajak": self.tahun, "metode": k["metode"], "cakupan": cakupan,
            "status_ptkp_input": p["status_ptkp"], "jenis_kelamin": p.get("jenis_kelamin"),
            "suami_tidak_berpenghasilan": bool(p.get("suami_tidak_berpenghasilan_terbukti", False)),
            "punya_npwp": p.get("punya_npwp", True), "subjektif_mulai": p.get("subjektif_mulai_bulan"),
            "subjektif_akhir": p.get("subjektif_akhir_bulan"), "bulan_masuk": p.get("bulan_masuk"),
            "bulan_kerja_diketahui": p.get("bulan_kerja_diketahui"), "periode_gaji": p.get("periode_gaji", "bulanan"),
            "hari_kerja_sebulan": p.get("hari_kerja_sebulan"), "klu": k["pemberi_kerja"].get("klu"),
            "jenis_pemberi_kerja": k["pemberi_kerja"].get("jenis", "biasa"),
            "penghasilan_tetap_kontrak": (k.get("dtp") or {}).get("penghasilan_tetap_teratur_kontrak_januari"),
            "rapel_n_bulan": len(rapel["bulan"]) if rapel else None,
            "rapel_dipotong_per_bulan": rapel.get("pph21_dipotong_per_bulan") if rapel else None,
            "n_bulan_kerja": len([b for b in self.bulan if b is not None]) or 1,
            "bulan_pertama": self.bulan[0] if self.bulan else None, "bulan_terakhir": terakhir,
        }

    def _tanggal(self, bulan):
        return date(self.tahun, bulan or self.dasar_tahun["bulan_terakhir"] or 12, 1)

    # ------------------------------------------------------------------ seleksi aturan & graf
    def _pilih_aturan(self):
        terpilih = []
        for a in self.kb.aturan:
            if not a.berlaku_di_tahun(self.tahun):
                continue
            if a.tafsir:
                v = self.varian.get(a.tafsir)
                if (v is None and not a.varian_default) or (v is not None and v != a.varian):
                    continue
            terpilih.append(a)
        return terpilih

    def _urutan_evaluasi(self):
        per_fakta = {}
        for a in self.aturan:
            per_fakta.setdefault(a.menghasilkan, []).append(a)
        self.per_fakta = per_fakta
        self.lingkup = {f: ats[0].lingkup for f, ats in per_fakta.items()}
        dasar = FAKTA_DASAR_TAHUN | FAKTA_DASAR_MASA
        tepi = {}
        for f, ats in per_fakta.items():
            dep = set()
            for a in ats:
                for n in a.dependensi():
                    if n in dasar:
                        continue
                    if n not in per_fakta:
                        raise KesalahanKB(f"{a.id}: fakta '{n}' tidak dihasilkan aturan mana pun di tahun {self.tahun}")
                    dep.add(n)
            tepi[f] = dep
        self.tepi = tepi
        scc = _tarjan(tepi)
        urutan = []
        for komponen in scc:  # Tarjan menghasilkan urutan topologis terbalik dari dependensi -> sudah benar
            bersiklus = len(komponen) > 1 or any(f in tepi[f] for f in komponen)
            if bersiklus:
                titik = [f for f in komponen if any(a.titik_tetap for a in per_fakta[f])]
                if not titik:
                    raise KesalahanKB(f"siklus tanpa titik_tetap: {sorted(komponen)}")
                urutan.append(("scc", sorted(komponen), titik))
            else:
                urutan.append(("fakta", komponen[0]))
        return urutan

    # ------------------------------------------------------------------ akses nilai
    def nilai_fakta(self, nama, bulan):
        if nama in FAKTA_DASAR_TAHUN:
            return self.dasar_tahun[nama]
        if nama == "bulan":
            return bulan
        if nama == "masa_terakhir":
            return bulan is not None and bulan == self.dasar_tahun["bulan_terakhir"]
        if self.lingkup.get(nama) == "masa":
            if bulan is None and None not in self.nilai_masa:
                raise KesalahanKB(f"fakta masa '{nama}' dirujuk dari lingkup tahun; pakai jumlah_masa/nilai_masa")
            return self.nilai_masa.get(bulan, {}).get(nama)
        return self.nilai_tahun.get(nama)

    # ------------------------------------------------------------------ evaluasi
    def jalankan(self):
        for langkah in self.urutan:
            if langkah[0] == "fakta":
                self._hitung_fakta(langkah[1])
            else:
                self._selesaikan_scc(langkah[1], langkah[2])
        return self

    def _instance(self, fakta):
        return self.bulan if self.lingkup[fakta] == "masa" else [None]

    def _hitung_fakta(self, fakta):
        for b in self._instance(fakta):
            self._simpan(fakta, b, self._evaluasi_instance(fakta, b))

    def _simpan(self, fakta, b, hasil):
        nilai, catatan = hasil
        if self.lingkup[fakta] == "masa":
            self.nilai_masa[b][fakta] = nilai
        else:
            self.nilai_tahun[fakta] = nilai
        if catatan is not None:
            self._jejak[(fakta, b)] = catatan

    @property
    def _jejak(self):
        if not hasattr(self, "_jejak_map"):
            self._jejak_map = {}
        return self._jejak_map

    def _selesaikan_scc(self, anggota, titik):
        """Iterasi Kleene: nilai awal titik tetap = 0, ulang sampai seluruh anggota stabil."""
        for f in titik:
            for b in self._instance(f):
                self._simpan(f, b, (0, None))
        urut = _urut_dalam_scc(anggota, self.tepi, set(titik))
        sebelumnya = None
        for i in range(BATAS_ITERASI):
            for f in urut:
                self._hitung_fakta(f)
            for f in titik:
                self._hitung_fakta(f)
            sekarang = tuple((f, b, self.nilai_fakta(f, b)) for f in sorted(anggota) for b in self._instance(f))
            if sekarang == sebelumnya:
                self.peringatan.append({"kode": "TITIK_TETAP", "anggota": sorted(anggota), "iterasi": i + 1}) \
                    if i > 1 else None
                return
            sebelumnya = sekarang
        raise KesalahanKB(f"titik tetap tidak konvergen dalam {BATAS_ITERASI} iterasi: {sorted(anggota)}")

    def _evaluasi_instance(self, fakta, b):
        tgl = self._tanggal(b)
        kandidat = [a for a in self.per_fakta[fakta] if a.berlaku_pada(tgl)]
        menyala = []
        for a in kandidat:
            if a.jika is None or a.jika.evaluasi(Konteks(self, b, a)):
                menyala.append(a)
        if not menyala:
            return None, None
        pilihan, ditolak, alasan = self._resolusi(fakta, b, menyala)
        nilai = self._nilai_aturan(pilihan, b)
        catatan = {"fakta": fakta, "bulan": b, "nilai": nilai, "aturan": pilihan.id, "lapisan": pilihan.lapisan,
                   "sifat": pilihan.sifat, "sumber": pilihan.sumber, "ditolak": ditolak, "alasan": alasan}
        return nilai, catatan

    def _nilai_aturan(self, a, b):
        v = _normal(a.maka.evaluasi(Konteks(self, b, a)))
        if a.pembulatan:
            mode = self.varian.get(a.pembulatan)
            v = self.kb.registri.terapkan(a.pembulatan, v, mode=mode)
        if a.tipe_hasil == "rupiah":
            if isinstance(v, bool) or not isinstance(v, int):
                raise PelanggaranPresisi(f"{a.id}: hasil rupiah bukan int ({v!r}); tambahkan pembulatan dari registri")
        return v

    def _resolusi(self, fakta, b, menyala):
        reg_wajib = [a for a in menyala if a.lapisan == "regulasi" and a.sifat in ("wajib", "tafsir")]
        prsh = [a for a in menyala if a.lapisan == "perusahaan"]
        reg_lain = [a for a in menyala if a.lapisan == "regulasi" and a.sifat not in ("wajib", "tafsir")]
        ditolak, alasan = [], []
        if reg_wajib and prsh:
            ditolak += [a.id for a in prsh]
            alasan.append("lex_superior")
            self.peringatan.append({"kode": "KONFLIK_WAJIB", "fakta": fakta, "bulan": b,
                                    "ditolak": [a.id for a in prsh], "pemenang": [a.id for a in reg_wajib]})
            grup = reg_wajib
        elif reg_wajib:
            grup = reg_wajib
        elif prsh:
            if reg_lain:
                ditolak += [a.id for a in reg_lain]
                alasan.append("override_sah")
            grup = prsh
        else:
            grup = reg_lain
        for kunci, nama in ((lambda a: a.spesifisitas, "lex_specialis"), (lambda a: a.mulai, "lex_posterior"),
                            (lambda a: a.prioritas, "prioritas")):
            if len(grup) == 1:
                break
            terbaik = max(kunci(a) for a in grup)
            kalah = [a for a in grup if kunci(a) != terbaik]
            if kalah:
                ditolak += [a.id for a in kalah]
                alasan.append(nama)
                grup = [a for a in grup if kunci(a) == terbaik]
        if len(grup) > 1:
            nilai = {repr(self._nilai_aturan(a, b)) for a in grup}
            if len(nilai) > 1:
                raise Ambigu(f"AMBIGU: fakta {fakta}[{b}] -> {[a.id for a in grup]} memberi nilai berbeda {nilai}")
        return grup[0], ditolak, alasan

    def hasil(self):
        per = {}
        for b in self.bulan:
            per[b] = {f: _keluaran(v) for f, v in self.nilai_masa[b].items() if v is not None and not f.startswith("_")}
        tahun = {f: _keluaran(v) for f, v in self.nilai_tahun.items() if v is not None and not f.startswith("_")}
        jejak = [self._jejak[k] for k in sorted(self._jejak, key=lambda k: (k[1] is None, k[1] or 0, k[0]))]
        return {"per_masa": per, "tahunan": tahun, "jejak": jejak, "peringatan": self.peringatan,
                "titik_tetap": self.iterasi_titik_tetap, "varian": dict(self.varian)}


def _keluaran(v):
    if isinstance(v, Fraction):
        return str(v)          # tarif & nilai eksak non-bulat: string pecahan (bukan float)
    return v


class Konteks:
    """Konteks evaluasi satu instance fakta: menyelesaikan nama dan fungsi DSL."""

    def __init__(self, ev, bulan, aturan):
        self.ev, self.b, self.aturan = ev, bulan, aturan

    def nilai(self, nama):
        return self.ev.nilai_fakta(nama, self.b)

    def input(self, jalur):
        raise KesalahanKB(f"akses atribut input tidak didukung: {jalur}")

    def _tgl(self):
        return self.ev._tanggal(self.b)

    def panggil(self, fn, args):
        ev = self.ev
        if fn == "min":
            return min(args)
        if fn == "max":
            return max(args)
        if fn == "abs":
            return abs(args[0])
        if fn == "persen":
            from .angka import persen
            return persen(args[0])
        if fn == "parameter":
            return parameter_pada(ev.kb, args[0], self._tgl())
        if fn == "bulatkan":
            return ev.kb.registri.terapkan(args[0], args[1], mode=ev.varian.get(args[0]))
        if fn == "kawin":
            return str(args[0]).startswith("K/")
        if fn == "ptkp":
            return _ptkp(ev, args[0])
        if fn == "kategori_ter":
            return _kategori_ter(ev, args[0])
        if fn == "tarif_ter":
            return _tarif_ter(ev, args[0], args[1], self._tgl())
        if fn == "pasal17":
            return _pasal17(ev, args[0], self._tgl())
        if fn in ("komponen", "komponen_kode", "komponen_valas"):
            return _komponen(ev, self.b, fn, args)
        if fn == "dtp_sektor_tahun":
            return _klu(ev, args[0], args[1], None)
        if fn == "dtp_masa_fasilitas":
            return _klu(ev, args[0], args[1], args[2])
        if fn == "atau":
            v = ev.nilai_fakta(args[0], self.b)
            return args[1] if v is None else v
        if fn == "nilai_masa":
            return ev.nilai_masa.get(args[1], {}).get(args[0])
        if fn in ("jumlah_masa", "jumlah_masa_selain_terakhir"):
            terakhir = ev.dasar_tahun["bulan_terakhir"]
            total = 0
            for b in ev.bulan:
                if fn == "jumlah_masa_selain_terakhir" and terakhir is not None and b == terakhir:
                    continue
                v = ev.nilai_masa[b].get(args[0])
                total += 0 if v is None else v
            return total
        if fn == "tolak":
            raise KasusTidakDidukung(f"{self.aturan.id}: {args[0]}")
        raise KesalahanKB(f"fungsi tidak dikenal: {fn}")


# ---------------------------------------------------------------------- fungsi tabel

def _ptkp(ev, status):
    for r in ev.kb.tabel["ptkp"]:
        if r["status"] == status:
            return r["ptkp_setahun"]
    raise KesalahanKB(f"status PTKP tidak dikenal: {status}")


def _kategori_ter(ev, status):
    for r in ev.kb.tabel["ptkp"]:
        if r["status"] == status and r["kategori_ter"] in ("A", "B", "C"):
            return r["kategori_ter"]
    raise KesalahanKB(f"status {status} tidak dipetakan ke kategori TER (PP 58/2023 Ps. 2(4))")


def _tarif_ter(ev, kategori, bruto, tgl):
    from .interval import tabel_ter
    if not hasattr(ev, "_cache_ter"):
        ev._cache_ter = {}
    baris = [r for r in ev.kb.tabel["ter_bulanan"] if date.fromisoformat(r["berlaku_mulai"]) <= tgl]
    kunci = (kategori, len(baris))
    if kunci not in ev._cache_ter:
        ev._cache_ter[kunci] = tabel_ter(baris, kategori)
    return ev._cache_ter[kunci].cari(bruto).tarif


def _pasal17(ev, pkp, tgl):
    from .interval import pajak_progresif, tabel_pasal17
    for rezim in ("UU HPP", "UU 36/2008 (pra-HPP)"):
        b = [r for r in ev.kb.tabel["tarif_pasal17"] if r["rezim"] == rezim]
        mulai = date.fromisoformat(b[0]["berlaku_mulai"])
        sampai = b[0]["berlaku_sampai"] and date.fromisoformat(b[0]["berlaku_sampai"])
        if mulai <= tgl and (not sampai or tgl <= sampai):
            return pajak_progresif(tabel_pasal17(ev.kb.tabel["tarif_pasal17"], rezim), pkp)
    raise KesalahanKB(f"tidak ada tarif Pasal 17 yang berlaku pada {tgl}")


def _komponen(ev, b, fn, args):
    kategori = args[0]
    total = 0
    for k in ev.komp.get(b, []):
        if k["kategori"] != kategori:
            continue
        if fn == "komponen_valas":
            if "valas" in k:
                total += k["valas"]["jumlah"] * ev.kasus["kurs"][k["valas"]["mata_uang"]]
            continue
        if "valas" in k:
            continue
        if fn == "komponen" and k.get("satuan_periode", "bulan") == (args[1] if len(args) > 1 else "bulan"):
            total += k["nominal"]
        elif fn == "komponen_kode" and args[1] in k["kode"]:
            total += k["nominal"]
    return total


def _klu(ev, klu, tahun, bulan):
    if not klu:
        return False
    for r in ev.kb.tabel["klu_dtp"]:
        if r["klu"] != klu or int(r["masa_mulai"][:4]) != tahun:
            continue
        if bulan is None or int(r["masa_mulai"][5:7]) <= bulan <= int(r["masa_akhir"][5:7]):
            return True
    return False


# ---------------------------------------------------------------------- graf

def _tarjan(tepi):
    indeks, rendah, tumpukan, di_tumpukan, hasil = {}, {}, [], set(), []
    counter = [0]

    def kunjungi(v):
        indeks[v] = rendah[v] = counter[0]
        counter[0] += 1
        tumpukan.append(v)
        di_tumpukan.add(v)
        for w in sorted(tepi.get(v, ())):
            if w not in indeks:
                kunjungi(w)
                rendah[v] = min(rendah[v], rendah[w])
            elif w in di_tumpukan:
                rendah[v] = min(rendah[v], indeks[w])
        if rendah[v] == indeks[v]:
            komp = []
            while True:
                w = tumpukan.pop()
                di_tumpukan.discard(w)
                komp.append(w)
                if w == v:
                    break
            hasil.append(komp)

    import sys
    sys.setrecursionlimit(max(10_000, sys.getrecursionlimit()))
    for v in sorted(tepi):
        if v not in indeks:
            kunjungi(v)
    return hasil


def _urut_dalam_scc(anggota, tepi, titik):
    """Urutan topologis anggota SCC setelah tepi menuju variabel titik tetap diputus."""
    sisa = set(anggota) - titik
    urut, selesai = [], set(titik)
    while sisa:
        siap = sorted(f for f in sisa if all(d in selesai or d not in anggota for d in tepi[f]))
        if not siap:
            raise KesalahanKB(f"SCC {sorted(anggota)} masih bersiklus setelah titik tetap {sorted(titik)} diputus")
        for f in siap:
            urut.append(f)
            selesai.add(f)
            sisa.discard(f)
    return urut
