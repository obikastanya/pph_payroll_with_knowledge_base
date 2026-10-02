"""Evaluator ekspresi aman untuk DSL aturan (research_plan.md §6.2 prinsip (a)).

Subset Python yang diizinkan: aritmetika (+ - * /, pembagian menghasilkan Fraction eksak),
perbandingan, and/or/not, `x if c else y`, `in`, literal int/str/bool/None dan tuple/list
literal, nama fakta, akses atribut input (mis. `pegawai.status_ptkp`), serta pemanggilan
fungsi yang terdaftar. Float literal, atribut privat, lambda, comprehension, subscript, dan
pemanggilan sembarang ditolak SAAT PARSE (verifikasi statis), bukan saat runtime.
"""
import ast
from fractions import Fraction

from .angka import PelanggaranPresisi


class KesalahanEkspresi(ValueError):
    pass


_OP_BIN = {ast.Add, ast.Sub, ast.Mult, ast.Div}
_OP_CMP = {ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn}


class Ekspresi:
    """Ekspresi yang sudah diparse dan divalidasi; menyimpan nama fakta & fungsi yang dirujuk."""

    def __init__(self, teks, fungsi_dikenal):
        if not isinstance(teks, str):
            raise KesalahanEkspresi(f"ekspresi wajib string: {teks!r}")
        self.teks = teks
        try:
            self.pohon = ast.parse(teks.strip(), mode="eval")
        except SyntaxError as e:
            raise KesalahanEkspresi(f"sintaks tidak valid: {teks!r} ({e.msg})") from None
        self.nama = set()
        self.fungsi = set()
        self.argumen_fakta = set()   # nama fakta yang dirujuk lewat argumen string (mis. jumlah_masa('pph21'))
        self._fungsi_dikenal = fungsi_dikenal
        self._validasi(self.pohon.body)

    def _validasi(self, n):
        if isinstance(n, ast.Constant):
            if isinstance(n.value, float):
                raise PelanggaranPresisi(f"float literal di ekspresi {self.teks!r}; pakai persen('5') / tarif('0.05')")
            if not isinstance(n.value, (int, str, bool, type(None))):
                raise KesalahanEkspresi(f"literal tidak didukung: {n.value!r}")
        elif isinstance(n, ast.Name):
            self.nama.add(n.id)
        elif isinstance(n, ast.Attribute):
            if n.attr.startswith("_"):
                raise KesalahanEkspresi(f"atribut privat ditolak: {n.attr}")
            if not isinstance(n.value, (ast.Name, ast.Attribute)):
                raise KesalahanEkspresi("atribut hanya boleh pada nama input")
            self._validasi(n.value)
        elif isinstance(n, ast.BinOp):
            if type(n.op) not in _OP_BIN:
                raise KesalahanEkspresi(f"operator tidak diizinkan: {type(n.op).__name__}")
            self._validasi(n.left)
            self._validasi(n.right)
        elif isinstance(n, ast.UnaryOp):
            if not isinstance(n.op, (ast.Not, ast.USub)):
                raise KesalahanEkspresi(f"operator unary tidak diizinkan: {type(n.op).__name__}")
            self._validasi(n.operand)
        elif isinstance(n, ast.BoolOp):
            for v in n.values:
                self._validasi(v)
        elif isinstance(n, ast.Compare):
            for op in n.ops:
                if type(op) not in _OP_CMP:
                    raise KesalahanEkspresi(f"perbandingan tidak diizinkan: {type(op).__name__}")
            self._validasi(n.left)
            for c in n.comparators:
                self._validasi(c)
        elif isinstance(n, ast.IfExp):
            self._validasi(n.test)
            self._validasi(n.body)
            self._validasi(n.orelse)
        elif isinstance(n, (ast.Tuple, ast.List)):
            for e in n.elts:
                self._validasi(e)
        elif isinstance(n, ast.Call):
            if not isinstance(n.func, ast.Name):
                raise KesalahanEkspresi("hanya fungsi terdaftar yang boleh dipanggil")
            if n.func.id not in self._fungsi_dikenal:
                raise KesalahanEkspresi(f"fungsi tidak terdaftar: {n.func.id}")
            if n.keywords:
                raise KesalahanEkspresi("argumen bernama tidak didukung")
            self.fungsi.add(n.func.id)
            for a in n.args:
                self._validasi(a)
            meta = self._fungsi_dikenal[n.func.id]
            if getattr(meta, "argumen_fakta", False) and n.args and isinstance(n.args[0], ast.Constant):
                self.argumen_fakta.add(n.args[0].value)
        else:
            raise KesalahanEkspresi(f"konstruksi tidak diizinkan: {type(n).__name__} di {self.teks!r}")

    def dependensi(self):
        """Nama fakta yang dibutuhkan (langsung + lewat argumen fungsi agregasi)."""
        return {n for n in self.nama} | self.argumen_fakta

    def panggilan_literal(self, nama_fungsi):
        """[(fungsi, kunci, jumlah_argumen)] untuk pemanggilan nama_fungsi('kunci', ...) dengan kunci literal string.
        Dipakai untuk mengetahui data input apa yang diminta aturan (mis. hr('gaji_pokok'))."""
        hasil = []
        for n in ast.walk(self.pohon):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in nama_fungsi and n.args
                    and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)):
                hasil.append((n.func.id, n.args[0].value, len(n.args)))
        return hasil

    def evaluasi(self, konteks):
        return _eval(self.pohon.body, konteks)


def _eval(n, k):
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.Name):
        return k.nilai(n.id)
    if isinstance(n, ast.Attribute):
        jalur = []
        while isinstance(n, ast.Attribute):
            jalur.append(n.attr)
            n = n.value
        jalur.append(n.id)
        return k.input(".".join(reversed(jalur)))
    if isinstance(n, ast.BinOp):
        a, b = _eval(n.left, k), _eval(n.right, k)
        for v in (a, b):
            if isinstance(v, (float, bool)) or v is None:
                raise PelanggaranPresisi(f"operand aritmetika tidak valid: {v!r}")
        if isinstance(n.op, ast.Add):
            return a + b
        if isinstance(n.op, ast.Sub):
            return a - b
        if isinstance(n.op, ast.Mult):
            return a * b
        if b == 0:
            raise KesalahanEkspresi("pembagian dengan nol")
        return Fraction(a) / Fraction(b)
    if isinstance(n, ast.UnaryOp):
        v = _eval(n.operand, k)
        return (not v) if isinstance(n.op, ast.Not) else -v
    if isinstance(n, ast.BoolOp):
        if isinstance(n.op, ast.And):
            hasil = True
            for v in n.values:
                hasil = _eval(v, k)
                if not hasil:
                    return hasil
            return hasil
        hasil = False
        for v in n.values:
            hasil = _eval(v, k)
            if hasil:
                return hasil
        return hasil
    if isinstance(n, ast.Compare):
        kiri = _eval(n.left, k)
        for op, kanan_n in zip(n.ops, n.comparators):
            kanan = _eval(kanan_n, k)
            ok = {ast.Eq: lambda: kiri == kanan, ast.NotEq: lambda: kiri != kanan,
                  ast.Lt: lambda: kiri < kanan, ast.LtE: lambda: kiri <= kanan,
                  ast.Gt: lambda: kiri > kanan, ast.GtE: lambda: kiri >= kanan,
                  ast.In: lambda: kiri in kanan, ast.NotIn: lambda: kiri not in kanan}[type(op)]()
            if not ok:
                return False
            kiri = kanan
        return True
    if isinstance(n, ast.IfExp):
        return _eval(n.body, k) if _eval(n.test, k) else _eval(n.orelse, k)
    if isinstance(n, (ast.Tuple, ast.List)):
        return tuple(_eval(e, k) for e in n.elts)
    if isinstance(n, ast.Call):
        return k.panggil(n.func.id, [_eval(a, k) for a in n.args])
    raise KesalahanEkspresi(f"konstruksi tidak diizinkan: {type(n).__name__}")


def jumlah_konjungsi(ekspresi):
    """Spesifisitas (lex specialis): jumlah konjungsi tingkat atas pada kondisi `jika`."""
    if ekspresi is None:
        return 0
    b = ekspresi.pohon.body
    if isinstance(b, ast.BoolOp) and isinstance(b.op, ast.And):
        return len(b.values)
    return 1
