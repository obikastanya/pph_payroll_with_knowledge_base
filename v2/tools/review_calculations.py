"""One workbook for the tax expert: the reference PPh 21 calculations used to validate the gold KB, one sheet per
calculation criterion, one row per employee (or employee-month), with a verification status and a note.

    Petunjuk               what to check and how to fill the status
    PPh bulanan TER        monthly withholding with the effective rate (2024 onwards), including the DTP incentive
    PPh bulanan 2023       monthly withholding with the old annualisation method (January-December 2023)
    Gross-up               monthly withholding when the employer pays the tax (tax allowance or tax borne)
    Masa Pajak Terakhir    the year-end recalculation with the Article 17 rates
    Kebijakan PKB          amounts set by the five real collective agreements, and the PPh 21 they lead to

    env\\Scripts\\python -m v2.tools.review_calculations
"""
import json

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

import v2.harness  # noqa: F401
from v2.harness import DATA

SOURCE = DATA / "11_acuan"
OUT = v2.harness.V2 / "review_pakar" / "uji_perhitungan_pph21.xlsx"

FONT = "Arial"
HEAD_FILL = PatternFill("solid", fgColor="DDEBF7")
RESULT_FILL = PatternFill("solid", fgColor="E2EFDA")
FILL_IN = PatternFill("solid", fgColor="FFFF00")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
MONTHS = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober",
          "November", "Desember"]
RP, PCT = "#,##0", "0.00%"

NATURA = {"natura_rumah_individual": "rumah dinas individual", "kendaraan_dinas": "kendaraan dinas",
          "bingkisan_non_hari_raya": "bingkisan (bukan hari raya)", "kupon_makan_dinas_luar": "kupon makan dinas luar"}
GT5_CRITERION = {
    "GT5-AVCO-02": "THR", "GT5-CENTEX-02": "THR", "GT5-SANSAN-01": "THR", "GT5-TKG-01": "THR", "GT5-WIKA-01": "THR",
    "GT5-AVCO-01": "Lembur", "GT5-CENTEX-01": "Lembur", "GT5-TKG-02": "Lembur",
    "GT5-AVCO-04": "Potongan dan tunjangan kehadiran", "GT5-CENTEX-04": "Potongan dan tunjangan kehadiran",
    "GT5-SANSAN-02": "Potongan dan tunjangan kehadiran", "GT5-TKG-04": "Potongan dan tunjangan kehadiran",
    "GT5-TKG-03": "Upah pegawai baru (prorata)",
    "GT5-AVCO-03": "Tunjangan neto dan PPh ditanggung", "GT5-CENTEX-03": "Bonus", "GT5-WIKA-02": "Bonus dan PPh ditanggung",
    "GT5-WIKA-03": "Uang cuti dan PPh ditanggung", "GT5-WIKA-05": "Insentif DTP", "GT5-SANSAN-03": "Masa Pajak Terakhir",
    "GT5-WIKA-04": "Berhenti kerja", "GT5-SANSAN-04": "Berhenti kerja",
}


def rupiah(v):
    return f"Rp{v:,.0f}".replace(",", ".")


def text_of(v):
    if isinstance(v, dict):
        return "; ".join(f"{k.replace('_', ' ')}: {text_of(x)}" for k, x in v.items())
    if isinstance(v, list):
        return "; ".join(text_of(x) for x in v)
    if isinstance(v, bool):
        return "ya" if v else "tidak"
    return "" if v is None else str(v)


# ---------------------------------------------------------------------------------------------------- writing
class Table:
    """One sheet: a header row, then one row per employee; the last two columns are filled by the expert."""

    def __init__(self, wb, title, columns, intro):
        """columns: [(header, width, format, kind)] with kind in {"data", "result"}."""
        self.ws = wb.create_sheet(title)
        self.columns = columns + [("Status verifikasi (pass/failed)", 14, None, "fill"), ("Catatan", 40, None, "fill")]
        self.ws.cell(1, 1, intro).font = Font(name=FONT, size=10, italic=True)
        self.ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(self.columns))
        self.ws.row_dimensions[1].height = 30
        self.ws.cell(1, 1).alignment = Alignment(wrap_text=True, vertical="top")
        for i, (head, width, _, kind) in enumerate(self.columns, 1):
            c = self.ws.cell(2, i, head)
            c.font = Font(name=FONT, size=10, bold=True)
            c.fill = FILL_IN if kind == "fill" else RESULT_FILL if kind == "result" else HEAD_FILL
            c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
            c.border = BOX
            self.ws.column_dimensions[get_column_letter(i)].width = width
        self.ws.row_dimensions[2].height = 45
        self.row = 3
        self.status = DataValidation(type="list", formula1='"pass,failed"', allow_blank=True)
        self.ws.add_data_validation(self.status)

    def add(self, values, note=None):
        for i, ((_, _, fmt, kind), v) in enumerate(zip(self.columns, list(values) + [None, None]), 1):
            c = self.ws.cell(self.row, i, v)
            c.font = Font(name=FONT, size=10)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = BOX
            if fmt and isinstance(v, (int, float)) and not isinstance(v, bool):
                c.number_format = fmt
            if kind == "fill":
                c.fill = FILL_IN
        if note:
            self.ws.cell(self.row, 1).comment = Comment(note[:30000], "penelitian", width=420, height=260)
        self.status.add(f"{get_column_letter(len(self.columns) - 1)}{self.row}")
        self.row += 1

    def finish(self):
        self.ws.freeze_panes = "C3"
        self.ws.auto_filter.ref = f"A2:{get_column_letter(len(self.columns))}{self.row - 1}"


# ---------------------------------------------------------------------------------------------------- GT3
def gt3_cases():
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted((SOURCE / "gt3_kasus_bertingkat").glob("GT3-*.json"))]


def kind_of(m):
    if m.get("keterangan"):
        return "year_end"
    if "tunjangan_pajak" in m or "pph21_ditanggung_pemberi_kerja" in m:
        return "gross_up"
    if "rincian_metode_lama" in m:
        return "old"
    return "ter"


def note_of(d):
    """Hover note on the case code: the scenario and its assumptions."""
    return d["uraian"] + "\n\nAsumsi:\n" + "\n".join(f"{i}. {a}" for i, a in enumerate(d["asumsi"], 1))


def employee(d):
    inp = d["input"]
    return inp["status_ptkp"] + (" (karyawati, suami berpenghasilan)" if inp.get("karyawati_kawin_suami_berpenghasilan")
                                 else "")


def sector(d):
    s = d["input"]["sektor"]
    return f"KLU {s['klu']}, risiko JKK {s['kelompok_risiko_jkk']}" + (", padat karya" if s.get("padat_karya_pp7_2025") else "")


def component(k, m):
    return m["komponen"].get(k, 0) or 0


def natura(m):
    items = [(NATURA[k], v) for k, v in m["komponen"].items() if k in NATURA and v]
    return sum(v for _, v in items), "; ".join(f"{n} {rupiah(v)}" for n, v in items)


def income_columns(m):
    """The month's pay components the expert needs to rebuild the gross: salary, allowance, overtime, THR/bonus,
    employer premiums that are taxable, benefits in kind (total; the items in the next column)."""
    total, items = natura(m)
    return [component("gaji", m), component("tunjangan_tetap", m), component("lembur", m),
            component("thr", m) + component("bonus", m), component("premi_jkk", m), component("premi_jkm", m),
            component("premi_bpjs_kesehatan_pemberi_kerja", m), total or None, items or None]


INCOME_HEADS = [("Gaji (Rp)", 13, RP, "data"), ("Tunjangan tetap (Rp)", 12, RP, "data"), ("Lembur (Rp)", 12, RP, "data"),
                ("THR / bonus (Rp)", 12, RP, "data"), ("Premi JKK dibayar pemberi kerja (Rp)", 12, RP, "data"),
                ("Premi JKM dibayar pemberi kerja (Rp)", 12, RP, "data"),
                ("Premi BPJS Kesehatan dibayar pemberi kerja (Rp)", 13, RP, "data"),
                ("Natura / kenikmatan (Rp)", 12, RP, "data"), ("Rincian natura", 24, None, "data")]
CASE_HEADS = [("Kode kasus", 10, None, "data"), ("Masa pajak", 13, None, "data"), ("Status PTKP", 11, None, "data"),
              ("Pemberi kerja", 20, None, "data")]


def months_of(d):
    inputs = {m["bulan"]: m for m in d["input"]["masa"]}
    for m in d["expected"]["per_masa"]:
        yield inputs[m["bulan"]], m


def period(d, month):
    return f"{MONTHS[month - 1]} {d['tahun_pajak']}"


def ter_sheet(wb, cases):
    t = Table(wb, "PPh bulanan TER", CASE_HEADS + INCOME_HEADS + [
        ("Penghasilan bruto (Rp)", 14, RP, "result"), ("Kategori TER", 9, None, "result"), ("Tarif TER", 9, PCT, "result"),
        ("PPh 21 terutang (Rp)", 13, RP, "result"), ("Berhak insentif DTP", 10, None, "result"),
        ("PPh 21 DTP (Rp)", 12, RP, "result"), ("PPh 21 dipotong dari pegawai (Rp)", 13, RP, "result")],
        "PPh 21 bulanan dengan tarif efektif (TER) pada masa selain Masa Pajak Terakhir, 2024–2026, termasuk "
        "insentif PPh 21 DTP 2025–2026. Kolom hijau adalah hasil yang diperiksa. Arahkan kursor ke kode kasus untuk "
        "melihat skenario dan asumsinya.")
    for d in cases:
        for i, m in months_of(d):
            if kind_of(m) != "ter":
                continue
            dtp = d["expected"].get("berhak_dtp")
            t.add([d["id"], period(d, m["bulan"]), employee(d), sector(d)] + income_columns(i) +
                  [m["bruto"], m["kategori_ter"], m["tarif_ter"], m["pph21"],
                   "" if dtp is None else text_of(dtp), m["pph21_dtp"], m["pph21_dipotong"]], note_of(d))
    t.finish()
    return t.row - 3


def old_sheet(wb, cases):
    t = Table(wb, "PPh bulanan 2023", CASE_HEADS + INCOME_HEADS + [
        ("Iuran JHT + JP pegawai (Rp)", 12, RP, "data"), ("Penghasilan bruto (Rp)", 14, RP, "result"),
        ("Faktor pengali disetahunkan", 10, None, "result"), ("Neto disetahunkan (Rp)", 14, RP, "result"),
        ("PKP disetahunkan (Rp)", 14, RP, "result"), ("PPh setahun atas penghasilan teratur (Rp)", 14, RP, "result"),
        ("PPh 21 terutang bulan ini (Rp)", 13, RP, "result")],
        "PPh 21 bulanan 2023 dengan metode lama (PER-16/PJ/2016): penghasilan teratur disetahunkan, dikenai tarif "
        "Pasal 17, lalu dibagi 12. Kolom hijau adalah hasil yang diperiksa.")
    for d in cases:
        for i, m in months_of(d):
            if kind_of(m) != "old":
                continue
            r = m["rincian_metode_lama"]
            t.add([d["id"], period(d, m["bulan"]), employee(d), sector(d)] + income_columns(i) +
                  [component("iuran_jht_pegawai", i) + component("iuran_jp_pegawai", i), m["bruto"], r["faktor_pengali"],
                   r["neto_disetahunkan"], r["pkp_teratur"], r["pph_setahun_teratur"], m["pph21"]], note_of(d))
    t.finish()
    return t.row - 3


def gross_up_sheet(wb, cases):
    t = Table(wb, "Gross-up", CASE_HEADS + INCOME_HEADS + [
        ("Metode", 14, None, "data"), ("Tunjangan pajak (Rp)", 13, RP, "result"),
        ("PPh 21 ditanggung pemberi kerja (Rp)", 13, RP, "result"), ("Penghasilan bruto (Rp)", 14, RP, "result"),
        ("Kategori TER", 9, None, "result"), ("Tarif TER", 9, PCT, "result"), ("PPh 21 terutang (Rp)", 13, RP, "result"),
        ("PPh 21 dipotong dari pegawai (Rp)", 13, RP, "result")],
        "PPh 21 bulanan bila pemberi kerja menanggung pajaknya: tunjangan pajak (gross-up) atau PPh ditanggung. "
        "Tahun 2023 memakai metode lama (tanpa kategori TER). Kolom hijau adalah hasil yang diperiksa.")
    for d in cases:
        for i, m in months_of(d):
            if kind_of(m) != "gross_up":
                continue
            t.add([d["id"], period(d, m["bulan"]), employee(d), sector(d)] + income_columns(i) +
                  [d["input"]["metode"].replace("_", "-"), m.get("tunjangan_pajak"), m.get("pph21_ditanggung_pemberi_kerja"),
                   m["bruto"], m["kategori_ter"], m["tarif_ter"], m["pph21"], m["pph21_dipotong"]], note_of(d))
    t.finish()
    return t.row - 3


def year_end_sheet(wb, cases):
    t = Table(wb, "Masa Pajak Terakhir", [
        ("Kode kasus", 10, None, "data"), ("Tahun pajak", 8, None, "data"), ("Status PTKP", 11, None, "data"),
        ("Pemberi kerja", 20, None, "data"), ("Metode", 10, None, "data"), ("Bulan bekerja", 9, None, "data"),
        ("Bruto masa sebelumnya (Rp)", 14, RP, "data"), ("Bruto Masa Pajak Terakhir (Rp)", 14, RP, "data"),
        ("Bruto setahun (Rp)", 14, RP, "result"), ("Biaya jabatan (Rp)", 12, RP, "result"),
        ("Iuran JHT + JP pegawai setahun (Rp)", 13, RP, "result"), ("Zakat setahun (Rp)", 11, RP, "result"),
        ("Neto setahun (Rp)", 14, RP, "result"), ("PTKP (Rp)", 12, RP, "result"), ("PKP (Rp)", 14, RP, "result"),
        ("PPh per lapisan tarif Pasal 17", 26, None, "result"), ("PPh 21 setahun (Rp)", 13, RP, "result"),
        ("PPh 21 dipotong masa sebelumnya (Rp)", 13, RP, "result"), ("PPh 21 Masa Pajak Terakhir (Rp)", 13, RP, "result"),
        ("PPh 21 DTP setahun (Rp)", 12, RP, "result"), ("Kelebihan potong dikembalikan (Rp)", 12, RP, "result")],
        "Perhitungan Masa Pajak Terakhir (Desember atau bulan berhenti) dengan tarif Pasal 17. Rincian bulan-bulan "
        "sebelumnya untuk kasus yang sama ada di sheet PPh bulanan dengan kode kasus yang sama. Kolom hijau adalah "
        "hasil yang diperiksa.")
    for d in cases:
        y = d["expected"].get("tahunan")
        if not y:
            continue
        per = d["expected"]["per_masa"]
        last = next(m for m in per if m["bulan"] == y["bulan_masa_terakhir"])
        layers = "; ".join(f"{x['tarif']:.0%} × {rupiah(x['dasar'])} = {rupiah(x['pph'])}" for x in y["pph21_lapisan"])
        t.add([d["id"], str(d["tahun_pajak"]), employee(d), sector(d), d["input"]["metode"].replace("_", "-"),
               y["jumlah_bulan"], sum(m["bruto"] for m in per if m is not last), last["bruto"], y["bruto_setahun"],
               y["biaya_jabatan"], y["iuran_jht_jp_pegawai"], y["zakat"], y["neto_setahun"], y["ptkp"], y["pkp"], layers,
               y["pph21_setahun"], y["pph21_dipotong_sebelumnya"], y["pph21_masa_terakhir"], y["pph21_dtp_setahun"],
               y["kelebihan_dikembalikan_ke_pegawai"]], note_of(d))
    t.finish()
    return t.row - 3


# ---------------------------------------------------------------------------------------------------- GT5
def gt5_examples():
    out = []
    for f in sorted((SOURCE / "gt5_contoh_kebijakan").glob("PKB_*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        for e in doc["contoh"]:
            out.append(dict(e, dokumen=doc["dokumen"].replace("_", " ")))
    return out


def split_expected(e):
    """Expected values into gross, PPh 21, take-home, and the policy amounts (labelled)."""
    notes = e.get("nilai_harapan_keterangan") or {}
    gross = take = None
    pph, policy = [], []
    for k, v in e["nilai_harapan"].items():
        name = notes.get(k, k.replace("_", " "))
        if k.startswith("bruto") and gross is None:
            gross = v
        elif k.startswith(("pph_", "pph21_")):
            pph.append(f"{name}: {rupiah(v)}")
        elif k == "take_home":
            take = v
        else:
            policy.append(f"{name}: {rupiah(v) if isinstance(v, (int, float)) else v}")
    return gross, pph, take, policy


def gt5_note(e):
    lines = [e["menguji"], "", "Asumsi:"] + [f"{i}. {a}" for i, a in enumerate(e["asumsi"], 1)]
    lines += ["", "Langkah hitung:"] + [f"{x['no']}. {x['uraian']}: {x.get('ekspresi') or ''} = {x['hasil']}"
                                         for x in e["langkah"]]
    decisions = e.get("putusan") or []
    for i, q in enumerate(e.get("ambiguitas") or []):
        lines += ["", f"Pertanyaan tafsir: {q}", f"Putusan: {decisions[i] if i < len(decisions) else '-'}"]
    return "\n".join(lines)


def policy_sheet(wb, examples):
    t = Table(wb, "Kebijakan PKB", [
        ("Kode contoh", 15, None, "data"), ("PKB", 18, None, "data"), ("Kriteria", 18, None, "data"),
        ("Masa pajak", 10, None, "data"), ("Data pegawai dan masukan", 40, None, "data"),
        ("Klausul PKB", 18, None, "data"), ("Nilai yang ditentukan kebijakan", 40, None, "result"),
        ("Penghasilan bruto masa (Rp)", 14, RP, "result"), ("PPh 21", 34, None, "result"),
        ("Uang diterima pegawai (Rp)", 14, RP, "result")],
        "Nilai yang ditentukan oleh klausul lima PKB nyata (THR, lembur, potongan, bonus, uang pisah, dan lainnya) "
        "serta PPh 21 yang timbul. Arahkan kursor ke kode contoh untuk melihat asumsi, langkah hitung, dan putusan "
        "tafsirnya. Kolom hijau adalah hasil yang diperiksa.")
    for e in sorted(examples, key=lambda e: (GT5_CRITERION.get(e["id"], "~"), e["id"])):
        gross, pph, take, policy = split_expected(e)
        inputs = {k: v for k, v in e["masukan"].items() if k != "masa_pajak"}
        t.add([e["id"], e["dokumen"], GT5_CRITERION.get(e["id"], ""), e["masukan"].get("masa_pajak", str(e["tahun_pajak"])),
               "\n".join(f"{k.replace('_', ' ')}: {text_of(v)}" for k, v in inputs.items()), ", ".join(e["klausul"]),
               "\n".join(policy), gross, "\n".join(pph) or None, take], gt5_note(e))
    t.finish()
    return t.row - 3


# ---------------------------------------------------------------------------------------------------- workbook
def instructions(ws, counts):
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 110
    rows = [
        ("Tujuan", "Memeriksa apakah PPh 21 yang dipakai penelitian sebagai jawaban benar memang benar."),
        ("Isi", "Setiap sheet memuat satu kriteria perhitungan. Setiap baris adalah satu pegawai pada satu masa pajak: "
                "data pegawai, gaji dan komponen lainnya, lalu hasil hitung (kolom hijau)."),
        ("Cara memeriksa", "Periksa kolom hijau pada setiap baris. Isi kolom kuning: Status verifikasi = pass bila "
                           "benar, failed bila salah; tulis nilai yang benar dan alasannya di Catatan."),
        ("Skenario dan asumsi", "Arahkan kursor ke kode kasus (sel bertanda segitiga merah) untuk melihat skenario, "
                                "asumsi, dan untuk sheet Kebijakan PKB juga langkah hitungnya."),
        ("Asumsi umum", "Pegawai tetap, Wajib Pajak dalam negeri, satu pemberi kerja, NPWP/NIK valid. Iuran JHT dan JP "
                        "yang dibayar pemberi kerja bukan objek PPh 21 sehingga tidak ditampilkan. Iuran JHT/JP pegawai "
                        "mengurangi penghasilan neto setahun. Nilai dalam rupiah; tarif dalam persen."),
        ("Contoh pengisian", "(Ilustrasi format) Status = failed; Catatan = \"PPh 21 seharusnya Rp149.857 karena ...\""),
    ]
    rows += [(f"Sheet: {name}", f"{n} baris") for name, n in counts]
    c = ws.cell(1, 1, "Uji perhitungan PPh 21: lembar verifikasi pakar")
    c.font = Font(name=FONT, size=12, bold=True)
    for r, (k, v) in enumerate(rows, 3):
        a, b = ws.cell(r, 1, k), ws.cell(r, 2, v)
        a.font, b.font = Font(name=FONT, size=10, bold=True), Font(name=FONT, size=10)
        for x in (a, b):
            x.alignment = Alignment(wrap_text=True, vertical="top")
            x.border = BOX
        if k == "Cara memeriksa":
            b.fill = FILL_IN


def build():
    wb = Workbook()
    wb.active.title = "Petunjuk"
    cases = gt3_cases()
    counts = [("PPh bulanan TER", ter_sheet(wb, cases)), ("PPh bulanan 2023", old_sheet(wb, cases)),
              ("Gross-up", gross_up_sheet(wb, cases)), ("Masa Pajak Terakhir", year_end_sheet(wb, cases)),
              ("Kebijakan PKB", policy_sheet(wb, gt5_examples()))]
    instructions(wb["Petunjuk"], counts)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    return counts


if __name__ == "__main__":
    print(build(), "→", OUT)
