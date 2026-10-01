"""CLI kalkulator PPh 21 berbasis KB.

    env\\Scripts\\python.exe -m engine.cli kasus.json
    env\\Scripts\\python.exe -m engine.cli kasus.json --perusahaan kb/perusahaan/perusahaan_x.yaml --rentang --jejak
    env\\Scripts\\python.exe -m engine.cli kasus.json --varian REG-BJ-02=b --json > hasil.json

Format input: kasus kanonik (lihat dataset/07_kasus_uji_resmi/kanonik/*.json); boleh memuat `data_hr` (lapisan
perusahaan) dan `transaksi` (tanggal bayar/terutang, REG-WAKTU-01).
"""
import argparse
import json
import sys

from .kalkulator import hitung


def _rp(v):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "ya" if v else "tidak"
    if isinstance(v, int):
        s = f"{abs(v):,}".replace(",", ".")
        return f"({s})" if v < 0 else s
    return str(v)


def cetak(h, jejak=False):
    print("PPh 21 per masa")
    print(f"{'masa':>4} {'bruto':>15} {'kategori':>8} {'tarif':>8} {'PPh 21':>14} {'DTP':>12} {'tunj. pajak':>12}")
    for b in sorted(h["per_masa"], key=lambda x: (x is None, x or 0)):
        m = h["per_masa"][b]
        print(f"{str(b):>4} {_rp(m.get('bruto')):>15} {str(m.get('kategori_ter', '-')):>8} {str(m.get('tarif_ter', '-')):>8} "
              f"{_rp(m.get('pph21')):>14} {_rp(m.get('pph21_dtp')):>12} {_rp(m.get('tunjangan_pajak')):>12}")
    t = h["tahunan"]
    if t:
        print("\nPerhitungan setahun / masa pajak terakhir")
        for k in ("bruto_setahun", "biaya_jabatan", "iuran_pengurang", "zakat", "neto_setahun", "neto_disetahunkan", "ptkp",
                  "pkp", "pph21_disetahunkan", "pph21_setahun", "pph21_dipotong_sebelumnya", "pph21_masa_terakhir",
                  "lebih_bayar_dikembalikan", "berhak_dtp"):
            if k in t:
                print(f"  {k:28} {_rp(t[k]):>16}")
    if h["peringatan"]:
        print("\nPeringatan")
        for p in h["peringatan"]:
            print("  -", json.dumps(p, ensure_ascii=False, default=str))
    if h.get("rentang_tafsir"):
        print("\nRentang tafsir (varian alternatif -> selisih terhadap default)")
        for r in h["rentang_tafsir"]:
            print(f"  {r['tafsir']}={r['varian']}: {r['fakta']}[{r['bulan']}] {_rp(r['default'])} -> {_rp(r['alternatif'])}"
                  f" (selisih {_rp(r['selisih'])})")
    if jejak:
        print("\nJejak aturan")
        for j in h["jejak"]:
            print(f"  {j['fakta']}[{j['bulan']}] = {_rp(j['nilai']) if isinstance(j['nilai'], int) else j['nilai']}"
                  f" <- {j['aturan']} ({j['lapisan']}/{j['sifat']}) | {j['sumber']}"
                  + (f" | ditolak: {j['ditolak']} [{', '.join(j['alasan'])}]" if j["ditolak"] else ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kasus")
    ap.add_argument("--perusahaan", action="append", default=[], help="berkas lapisan kebijakan perusahaan (YAML)")
    ap.add_argument("--varian", action="append", default=[], help="pilih varian tafsir, mis. REG-BJ-02=b")
    ap.add_argument("--rentang", action="store_true", help="hitung rentang tafsir")
    ap.add_argument("--jejak", action="store_true", help="tampilkan jejak aturan & pasal")
    ap.add_argument("--json", action="store_true", help="keluaran JSON lengkap")
    a = ap.parse_args(argv)
    with open(a.kasus, encoding="utf-8") as f:
        kasus = json.load(f)
    varian = dict(v.split("=", 1) for v in a.varian)
    h = hitung(kasus, varian, berkas_perusahaan=a.perusahaan, audit=True, dengan_rentang=a.rentang)
    if a.json:
        json.dump(h, sys.stdout, indent=1, ensure_ascii=False, default=str)
    else:
        cetak(h, a.jejak)


if __name__ == "__main__":
    main()
