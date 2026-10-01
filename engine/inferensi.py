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
from .kb import FAKTA_DASAR_MASA, FAKTA_DASAR_TAHUN, FUNGSI, FUNGSI_KOMPONEN, KesalahanKB, parameter_pada
from .pembulatan import bulatkan as _bulatkan

BATAS_ITERASI = 10_000

# Saklar ablasi E5 (research_plan.md §12.1). HANYA untuk eksperimen; default kosong.
ABLASI_SAH = {
    "A1_tanpa_versi_waktu",       # abaikan masa berlaku: aturan & tabel versi terbaru selalu dipakai
    "A3_tanpa_resolusi_konflik",  # perusahaan selalu menang; klasifikasi wajib diabaikan
    "A4_iterasi_naif",            # titik tetap: satu iterasi dari 0 (bergantung jalur), tanpa deteksi ganda
    "A5_pembulatan_naif",         # registri diabaikan: semua pembulatan = setengah_genap (perilaku round())
    "A9_tanpa_tiga_tanggal",      # masa transaksi = periode kerja (bukan saat terutang)
}


class KasusTidakDidukung(ValueError):
    pass


class Ambigu(KesalahanKB):
    pass


def _normal(v):
    if isinstance(v, Fraction) and v.denominator == 1:
        return int(v)
    return v


class Evaluasi:
    def __init__(self, kb, kasus, varian=None, ablasi=(), per_tanggal_kb=None):
        self.per_tanggal_kb = per_tanggal_kb   # knowledge time: KB sebagaimana diketahui pada tanggal ini
        self.ablasi = set(ablasi)
        if self.ablasi - ABLASI_SAH:
            raise KesalahanKB(f"saklar ablasi tidak dikenal: {sorted(self.ablasi - ABLASI_SAH)}")
        self.kb = kb
        self.kasus = kasus
        self.varian = dict(varian or {})
        self.tahun = kasus["tahun_pajak"]
        self.peringatan = []
        self._konflik = set()
        kasus = self.kasus = _terapkan_transaksi(kasus, self.peringatan, "A9_tanpa_tiga_tanggal" in self.ablasi)
        self.masa = sorted(kasus["masa"], key=lambda m: (m["bulan"] is None, m["bulan"] or 0))
        self.bulan = [m["bulan"] for m in self.masa]
        self.komp = {m["bulan"]: m["komponen"] for m in self.masa}
        _validasi_input(kasus)
        self.dasar_tahun = self._fakta_dasar()
        self.nilai_tahun = {}
        self.nilai_masa = {b: {} for b in self.bulan}
        self.iterasi_titik_tetap = []
        self.rincian_p17 = {}
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
        if "A1_tanpa_versi_waktu" in getattr(self, "ablasi", ()):
            return date(9999, 12, 1)
        return date(self.tahun, bulan or self.dasar_tahun["bulan_terakhir"] or 12, 1)

    # ------------------------------------------------------------------ seleksi aturan & graf
    def _pilih_aturan(self):
        terpilih = []
        for a in self.kb.aturan:
            if "A1_tanpa_versi_waktu" in self.ablasi:
                if a.sampai is not None:   # hanya versi yang masih berlaku 'sekarang' yang tersisa
                    continue
            elif not a.berlaku_di_tahun(self.tahun):
                continue
            if self.per_tanggal_kb is not None and a.dicatat is not None and a.dicatat > self.per_tanggal_kb:
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
        komp_prsh = {k.fakta for k in self.kb.komponen if k.fakta in per_fakta}
        tepi = {}
        for f, ats in per_fakta.items():
            dep = set()
            for a in ats:
                deps = set(a.dependensi())
                if a.maka.fungsi & FUNGSI_KOMPONEN or (a.jika is not None and a.jika.fungsi & FUNGSI_KOMPONEN):
                    deps |= komp_prsh - {f}
                for n in deps:
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
        """Titik tetap terkecil & terbesar (Knaster-Tarski) lewat iterasi Kleene dari batas bawah/atas.

        Bila keduanya berbeda -> peringatan GROSSUP_GANDA; solusi dipilih deterministik menurut tafsir
        TITIK-TETAP-PILIH (default 'terkecil'). Hasil tidak bergantung pada jalur iterasi.
        """
        urut = _urut_dalam_scc(anggota, self.tepi, set(titik))
        instance = [(f, b) for f in titik for b in self._instance(f)]
        batas = {}
        for f, b in instance:
            a = self._aturan_titik(f, b)
            if a is None:
                batas[(f, b)] = None
                continue
            ctx = Konteks(self, b, a)
            bawah, atas = _normal(a.batas_bawah.evaluasi(ctx)), _normal(a.batas_atas.evaluasi(ctx))
            if bawah > atas:
                raise KesalahanKB(f"{a.id}: batas titik tetap terbalik ({bawah} > {atas})")
            batas[(f, b)] = (bawah, atas)
        if "A4_iterasi_naif" in self.ablasi:
            self._iterasi_kleene(anggota, titik, urut, {i: (None if v is None else 0) for i, v in batas.items()}, naik=None)
            return
        solusi = {}
        for arah in ("terkecil", "terbesar"):
            awal = {i: (None if v is None else (v[0] if arah == "terkecil" else v[1])) for i, v in batas.items()}
            solusi[arah] = self._iterasi_kleene(anggota, titik, urut, awal, naik=(arah == "terkecil"))
        pilih = self.varian.get("TITIK-TETAP-PILIH", "terkecil")
        if pilih not in solusi:
            raise KesalahanKB(f"varian TITIK-TETAP-PILIH tidak dikenal: {pilih}")
        for i in instance:
            if solusi["terkecil"][i] != solusi["terbesar"][i]:
                self.peringatan.append({"kode": "GROSSUP_GANDA", "fakta": i[0], "bulan": i[1],
                                        "terkecil": solusi["terkecil"][i], "terbesar": solusi["terbesar"][i],
                                        "dipilih": pilih})
        self._iterasi_kleene(anggota, titik, urut, solusi[pilih], naik=None)

    def _aturan_titik(self, f, b):
        tgl = self._tanggal(b)
        for a in self.per_fakta[f]:
            if a.titik_tetap and a.berlaku_pada(tgl) and (a.jika is None or a.jika.evaluasi(Konteks(self, b, a))):
                return a
        return None

    def _iterasi_kleene(self, anggota, titik, urut, awal, naik):
        for (f, b), v in awal.items():
            self._simpan(f, b, (v, None))
        for i in range(BATAS_ITERASI):
            for f in urut:
                self._hitung_fakta(f)
            berubah = False
            for f in titik:
                for b in self._instance(f):
                    lama = self.nilai_fakta(f, b)
                    self._simpan(f, b, self._evaluasi_instance(f, b))
                    baru = self.nilai_fakta(f, b)
                    if baru != lama:
                        berubah = True
                        if naik is not None and lama is not None and baru is not None and (baru < lama) == naik:
                            raise KesalahanKB(f"fungsi titik tetap {f}[{b}] tidak monoton (iterasi {'naik' if naik else 'turun'}:"
                                              f" {lama} -> {baru}); asumsi Knaster-Tarski dilanggar")
            if not berubah:
                self.iterasi_titik_tetap.append({"anggota": sorted(titik), "iterasi": i + 1,
                                                 "arah": {True: "dari_bawah", False: "dari_atas", None: "konfirmasi"}[naik]})
                return {(f, b): self.nilai_fakta(f, b) for f in titik for b in self._instance(f)}
        raise KesalahanKB(f"titik tetap tidak konvergen dalam {BATAS_ITERASI} iterasi: {sorted(anggota)}")

    def _evaluasi_instance(self, fakta, b):
        tgl = self._tanggal(b)
        kandidat = [a for a in self.per_fakta[fakta] if "A1_tanpa_versi_waktu" in self.ablasi or a.berlaku_pada(tgl)]
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
            if "A5_pembulatan_naif" in self.ablasi:
                v = _bulatkan(v, "setengah_genap", 1)
            else:
                v = self.kb.registri.terapkan(a.pembulatan, v, mode=self.varian.get(a.pembulatan))
        if a.tipe_hasil == "rupiah":
            if isinstance(v, bool) or not isinstance(v, int):
                raise PelanggaranPresisi(f"{a.id}: hasil rupiah bukan int ({v!r}); tambahkan pembulatan dari registri")
        return v

    def _resolusi(self, fakta, b, menyala):
        reg_wajib = [a for a in menyala if a.lapisan == "regulasi" and a.sifat in ("wajib", "tafsir")]
        prsh = [a for a in menyala if a.lapisan == "perusahaan"]
        reg_lain = [a for a in menyala if a.lapisan == "regulasi" and a.sifat not in ("wajib", "tafsir")]
        ditolak, alasan = [], []
        if "A3_tanpa_resolusi_konflik" in self.ablasi and prsh:
            grup = prsh
        elif reg_wajib and prsh:
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
        rincian = [{"fakta": f, "bulan": b, "pkp": pkp, "rezim": rezim,
                    "lapisan": [{"bawah": lo, "atas": hi, "tarif": str(t), "dasar": dasar,
                                 "pajak": pj.numerator if pj.denominator == 1 else str(pj)}
                                for lo, hi, t, dasar, pj in rinci]}
                   for (f, b), (pkp, rezim, rinci) in sorted(self.rincian_p17.items(), key=lambda kv: (kv[0][1] is None, kv[0][1] or 0, kv[0][0]))]
        return {"per_masa": per, "tahunan": tahun, "jejak": jejak, "peringatan": self.peringatan,
                "titik_tetap": self.iterasi_titik_tetap, "varian": dict(self.varian), "rincian_pasal17": rincian}


def _terapkan_transaksi(kasus, peringatan, tanpa_tiga_tanggal=False):
    """REG-WAKTU-01 (§6.9.4): transaksi bertanggal -> masa pajak = bulan saat terutang.

    Transaksi yang terutang di tahun lain dikeluarkan (peringatan TRANSAKSI_TAHUN_LAIN); transaksi
    di bulan tanpa masa kerja menjadi galat input (tidak ditebak).
    """
    import copy
    from .waktu import InputTidakValid, TransaksiPenghasilan
    daftar = kasus.get("transaksi") or []
    if not daftar:
        return kasus
    k = copy.deepcopy(kasus)
    masa = {m["bulan"]: m for m in k["masa"]}
    for d in daftar:
        t = TransaksiPenghasilan.dari_data(d)
        tahun, bulan = t.periode_kerja if tanpa_tiga_tanggal else t.masa_pajak
        if tahun != k["tahun_pajak"]:
            peringatan.append({"kode": "TRANSAKSI_TAHUN_LAIN", "komponen": t.komponen, "masa_pajak": f"{tahun}-{bulan:02d}",
                               "aturan": "REG-WAKTU-01", "tafsir": t.tafsir_waktu()})
            continue
        if bulan not in masa:
            raise InputTidakValid(f"{k['id']}: transaksi {t.komponen} terutang {tahun}-{bulan:02d} di luar masa kerja")
        masa[bulan]["komponen"].append({"kode": d["komponen"], "kategori": d["kategori"], "satuan_periode": "bulan",
                                        "nominal": t.nominal, "asal": "transaksi", "saat_terutang": t.saat_terutang.isoformat()})
        if t.tafsir_waktu():
            peringatan.append({"kode": "AMBIGU_TAFSIR", "aturan": "WAKTU-P16-01", "komponen": t.komponen})
    return k


def _validasi_input(kasus):
    """Kontrak input (§6.9.5): nominal komponen int >= 0, kategori dikenal; DATA_KURANG menghentikan."""
    from .waktu import InputTidakValid
    kategori_sah = {"teratur", "tidak_teratur", "premi_objek", "natura", "iuran_pengurang", "zakat", "rapel"}

    def tanpa_float(obj, jalur):
        if isinstance(obj, float):
            raise InputTidakValid(f"{kasus['id']}: float di input {jalur} ({obj!r}); pakai int rupiah atau string desimal")
        if isinstance(obj, dict):
            for kk, vv in obj.items():
                tanpa_float(vv, f"{jalur}.{kk}")
        elif isinstance(obj, list):
            for i, vv in enumerate(obj):
                tanpa_float(vv, f"{jalur}[{i}]")
    tanpa_float(kasus.get("data_hr") or {}, "data_hr")
    tanpa_float(kasus.get("dtp") or {}, "dtp")
    for m in kasus["masa"]:
        for k in m["komponen"]:
            if k.get("kategori") not in kategori_sah:
                raise InputTidakValid(f"{kasus['id']}: kategori komponen tidak dikenal {k.get('kategori')!r}")
            n = k["valas"]["jumlah"] if "valas" in k else k.get("nominal")
            if isinstance(n, bool) or not isinstance(n, int) or n < 0:
                raise InputTidakValid(f"{kasus['id']}: nominal {k.get('kode')} bulan {m['bulan']} wajib int >= 0, diterima {n!r}")


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
            if "A5_pembulatan_naif" in ev.ablasi:
                return _bulatkan(args[1], "setengah_genap", 1)
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
            total, rezim, rinci = _pasal17(ev, args[0], self._tgl(), dengan_rincian=True)
            ev.rincian_p17[(self.aturan.menghasilkan, self.b)] = (args[0], rezim, rinci)   # fasilitas penjelasan
            return total
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
        if fn in ("hr", "hr_masa"):
            return _hr(ev, self.b, fn, args)
        if fn == "desimal":
            from .angka import tarif
            return tarif(args[0])
        if fn in ("tanggal", "tanggal_masa", "tambah_hari", "geser_bulan", "selisih_hari", "selisih_bulan",
                  "bulan_dari", "hari_dari", "tahun_dari"):
            return _fungsi_tanggal(ev, self.b, fn, args)
        raise KesalahanKB(f"fungsi tidak dikenal: {fn}")


# ---------------------------------------------------------------------- fungsi tabel

def _mulai_ptkp(r):
    teks = (r.get("berlaku_mulai") or r.get("berlaku") or "2016-01-01")[:10]
    return date.fromisoformat(teks)


def _ptkp(ev, status):
    """PTKP berversi: baris dengan tanggal mulai berlaku terbaru <= awal tahun pajak (PMK 168 Ps. 9(4))."""
    awal = date(9999, 1, 1) if "A1_tanpa_versi_waktu" in ev.ablasi else date(ev.tahun, 1, 1)
    kandidat = [r for r in ev.kb.tabel["ptkp"] if r["status"] == status and _mulai_ptkp(r) <= awal]
    if not kandidat:
        raise KesalahanKB(f"status PTKP tidak dikenal/berlaku: {status} ({ev.tahun})")
    return max(kandidat, key=_mulai_ptkp)["ptkp_setahun"]


def _kategori_ter(ev, status):
    for r in ev.kb.tabel["ptkp"]:
        if r["status"] == status and r["kategori_ter"] in ("A", "B", "C"):
            return r["kategori_ter"]
    raise KesalahanKB(f"status {status} tidak dipetakan ke kategori TER (PP 58/2023 Ps. 2(4))")


def _tarif_ter(ev, kategori, bruto, tgl):
    from .interval import tabel_ter
    if not hasattr(ev, "_cache_ter"):
        ev._cache_ter = {}
    versi = sorted({r["berlaku_mulai"] for r in ev.kb.tabel["ter_bulanan"] if date.fromisoformat(r["berlaku_mulai"]) <= tgl})
    if not versi:
        raise KesalahanKB(f"tidak ada tabel TER yang berlaku pada {tgl}")
    baris = [r for r in ev.kb.tabel["ter_bulanan"] if r["berlaku_mulai"] == versi[-1]]  # hanya versi terbaru
    kunci = (kategori, versi[-1])
    if kunci not in ev._cache_ter:
        ev._cache_ter[kunci] = tabel_ter(baris, kategori)
    return ev._cache_ter[kunci].cari(bruto).tarif


def _pasal17(ev, pkp, tgl, dengan_rincian=False):
    from .interval import pajak_progresif, rincian_progresif, tabel_pasal17
    if "A1_tanpa_versi_waktu" in ev.ablasi:
        tgl = date(9999, 12, 1)
    for rezim in ("UU HPP", "UU 36/2008 (pra-HPP)"):
        b = [r for r in ev.kb.tabel["tarif_pasal17"] if r["rezim"] == rezim]
        mulai = date.fromisoformat(b[0]["berlaku_mulai"])
        sampai = b[0]["berlaku_sampai"] and date.fromisoformat(b[0]["berlaku_sampai"])
        if mulai <= tgl and (not sampai or tgl <= sampai):
            tabel = tabel_pasal17(ev.kb.tabel["tarif_pasal17"], rezim)
            if dengan_rincian:
                return pajak_progresif(tabel, pkp), rezim, rincian_progresif(tabel, pkp)
            return pajak_progresif(tabel, pkp)
    raise KesalahanKB(f"tidak ada tarif Pasal 17 yang berlaku pada {tgl}")


def kategori_efektif(ev, kp, b):
    """Lex superior: klasifikasi wajib regulasi mengalahkan pemetaan kategori perusahaan."""
    if "A3_tanpa_resolusi_konflik" in ev.ablasi:
        return kp.kategori
    tgl = ev._tanggal(b)
    wajib = [w for w in ev.kb.klasifikasi if w.jenis == kp.jenis and w.mulai <= tgl and (w.sampai is None or tgl <= w.sampai)]
    if wajib and wajib[0].kategori != kp.kategori:
        kunci = ("KONFLIK_WAJIB", kp.fakta)
        if kunci not in ev._konflik:
            ev._konflik.add(kunci)
            ev.peringatan.append({"kode": "KONFLIK_WAJIB", "fakta": kp.fakta, "jenis": kp.jenis,
                                  "kategori_perusahaan": kp.kategori, "kategori_wajib": wajib[0].kategori,
                                  "sumber": wajib[0].sumber, "berkas": kp.berkas})
        return wajib[0].kategori
    if not wajib:
        kunci = ("KLASIFIKASI_TIDAK_DIATUR", kp.fakta)
        if kunci not in ev._konflik:
            ev._konflik.add(kunci)
            ev.peringatan.append({"kode": "KLASIFIKASI_TIDAK_DIATUR", "fakta": kp.fakta, "jenis": kp.jenis,
                                  "kategori_perusahaan": kp.kategori,
                                  "catatan": "regulasi tidak memuat klasifikasi wajib untuk jenis ini; kategori perusahaan dipakai (tafsir)"})
    return kp.kategori


def _komponen(ev, b, fn, args):
    kategori = args[0]
    total = 0
    if fn != "komponen_valas" and (len(args) < 2 or fn == "komponen_kode" or args[1] == "bulan"):
        for kp in ev.kb.komponen:
            if kp.fakta not in ev.per_fakta or kategori_efektif(ev, kp, b) != kategori:
                continue
            if fn == "komponen_kode" and args[1] not in kp.fakta and args[1] not in kp.jenis:
                continue
            v = ev.nilai_masa.get(b, {}).get(kp.fakta)
            total += 0 if v is None else v
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


def _hr(ev, b, fn, args):
    data = ev.kasus.get("data_hr") or {}
    if fn == "hr":
        if args[0] not in data:
            raise KesalahanKB(f"data_hr.{args[0]} tidak tersedia (DATA_KURANG)")
        return data[args[0]]
    per = (data.get("per_masa") or {}).get(str(b)) or {}
    if args[0] not in per:
        if len(args) > 1:
            return args[1]
        raise KesalahanKB(f"data_hr.per_masa[{b}].{args[0]} tidak tersedia (DATA_KURANG)")
    return per[args[0]]


def _fungsi_tanggal(ev, b, fn, args):
    import calendar
    from datetime import timedelta
    if fn == "tanggal":
        return args[0] if isinstance(args[0], date) else date.fromisoformat(args[0])
    if fn == "tanggal_masa":
        return date(ev.tahun, b, 1)
    if fn == "tambah_hari":
        return args[0] + timedelta(days=args[1])
    if fn == "geser_bulan":  # setara EDATE: tanggal sama, dipangkas ke akhir bulan bila perlu
        t, n = args
        m = t.month - 1 + n
        y, m = t.year + m // 12, m % 12 + 1
        return date(y, m, min(t.day, calendar.monthrange(y, m)[1]))
    if fn == "selisih_hari":
        return (args[1] - args[0]).days
    if fn == "selisih_bulan":  # setara DATEDIF(a, b, "M")
        a, c = args
        n = (c.year - a.year) * 12 + (c.month - a.month)
        return n - 1 if c.day < a.day else n
    if fn == "bulan_dari":
        return args[0].month
    if fn == "hari_dari":
        return args[0].day
    return args[0].year


def _klu(ev, klu, tahun, bulan):
    if not klu:
        return False
    for r in ev.kb.tabel["klu_dtp"]:
        if r["klu"] != klu or int(r["masa_mulai"][:4]) != tahun:
            continue
        if ev.per_tanggal_kb is not None:
            reg = r["regulasi"].split(" Lampiran")[0]
            if reg not in ev.kb.pencatatan:
                raise KesalahanKB(f"tanggal pencatatan {reg} tidak diketahui (kb/regulasi/pencatatan.yaml)")
            if ev.kb.pencatatan[reg] > ev.per_tanggal_kb:
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
