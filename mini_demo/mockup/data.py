"""Labels in plain Indonesian, formatting, the topic map of the knowledge base, and the engine call.

The knowledge base is the demo's current one (demo.kb(): the initial state plus what was approved during the demo).
"""
import re
import sys
from datetime import date
from fractions import Fraction
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "system", ROOT / "system" / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import demo  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402
from pph21kbs.text import registry  # noqa: E402

TODAY = date.today()
MONTHS = ("Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober",
          "November", "Desember")
MON = tuple(m[:3] for m in MONTHS)
STATUSES = ("TK/0", "TK/1", "TK/2", "TK/3", "K/0", "K/1", "K/2", "K/3")
METHODS = {"gross": "Gross: dipotong dari gaji", "gross_up": "Gross-up: diberi tunjangan pajak",
           "employer_borne": "Ditanggung perusahaan"}
METHOD_TERM = {"gross": "gross", "gross_up": "gross-up", "employer_borne": "ditanggung"}
JKK = {"very_low": "Sangat rendah (0,24%)", "low": "Rendah (0,54%)", "medium": "Sedang (0,89%)",
       "high": "Tinggi (1,27%)", "very_high": "Sangat tinggi (1,74%)"}
KLU = {"": "Tidak diisi", "62019": "62019 · Aktivitas pemrograman", "47111": "47111 · Perdagangan eceran",
       "13921": "13921 · Tekstil rumah tangga (padat karya)", "14111": "14111 · Pakaian jadi (padat karya)",
       "55110": "55110 · Hotel bintang (pariwisata)"}

# Topics of the viewer: (title, icon, one-line explanation, facts or parameter/table names that belong to it)
TOPICS = [
    ("Penghasilan bruto", ":material/payments:", "Komponen apa saja yang dijumlahkan menjadi penghasilan bruto.",
     ("base_salary", "fixed_allowance", "overtime_pay", "thr", "bonus", "gross_income", "regular_gross",
      "irregular_gross", "cash_income", "other_regular_income", "other_irregular_income", "tax_allowance")),
    ("Natura dan fasilitas", ":material/home_work:", "Fasilitas dan barang dari perusahaan yang ikut kena pajak.",
     ("benefit_", "benefits_", "natura_")),
    ("BPJS dan iuran", ":material/health_and_safety:", "Iuran JHT, JP, JKK, JKM, dan BPJS Kesehatan beserta batas upahnya.",
     ("jht", "jp_", "jkk", "jkm", "health", "bpjs", "employer_premiums_taxable", "pension")),
    ("PTKP dan status", ":material/family_restroom:", "Penghasilan bebas pajak menurut status kawin dan tanggungan.",
     ("ptkp", "subjective")),
    ("Tarif bulanan (TER)", ":material/percent:", "Tarif Januari sampai November: bruto sebulan × tarif TER.",
     ("ter_", "pph21_running", "pph_regular_month", "pph_irregular_month", "job_expense_month", "net_regular_month",
      "taxable_regular_annualized", "taxable_with", "taxable_without", "pph_regular_annual")),
    ("Akhir tahun (Pasal 17)", ":material/event_available:", "Hitung ulang setahun di masa pajak terakhir.",
     ("annual_", "job_expense", "taxable_income", "final_period_tax", "withheld_before_final", "refund_to_employee",
      "annualization", "pasal17", "pph_round")),
    ("Insentif DTP", ":material/volunteer_activism:", "PPh 21 yang ditanggung pemerintah untuk sektor tertentu.",
     ("dtp", "covid")),
    ("Metode dan gaji bersih", ":material/account_balance_wallet:", "Gross, gross-up, ditanggung, zakat, gaji bersih.",
     ("withholding_method", "employee_tax_burden", "take_home_pay", "pph21_due", "company_deductions", "zakat")),
    ("Ketenagakerjaan", ":material/work_history:", "THR minimum dan ketentuan ketenagakerjaan lain.",
     ("thr_minimum", "CON.")),
]


def kb():
    return demo.kb()


@st.cache_resource
def _facts(signature):
    return {r.id: r for r in kb().records if r.kind == "fact"}


def facts():
    return _facts(demo.signature())


@st.cache_resource
def _params(signature):
    out = {}
    for r in kb().records:
        if r.kind == "parameter":
            out.setdefault(r.name, r)
    return out


def params():
    return _params(demo.signature())


def doc_title(doc_id):
    return registry().get(doc_id, {}).get("title", doc_id)


def short_doc(doc_id):
    """'PMK 168/2023' from the registry title, or the id."""
    t = doc_title(doc_id)
    return t.split(":")[0] if ":" in t else doc_id


def fact_label(name):
    f = facts().get(name)
    if f and f.label_id:
        return f.label_id[0].upper() + f.label_id[1:]
    p = params().get(name)
    if p and p.label_id:
        return p.label_id[0].upper() + p.label_id[1:]
    return name.replace("_", " ")


def topic_of(rec):
    if getattr(rec, "layer", "") == "company":
        return "Kebijakan perusahaan"
    key = getattr(rec, "produces", None) or getattr(rec, "name", None) or rec.id
    for title, _, _, keys in TOPICS:
        if any(key.startswith(k) or k in key or rec.id.startswith(k) for k in keys):
            return title
    return "Lainnya"


def is_input_convention(rec):
    return rec.id.startswith("REG.INPUT.") or any(s.document == "INPUT-CONVENTION" for s in rec.source)


INPUT_LABELS = {"housing_individual": "rumah dinas", "company_vehicle": "mobil dinas", "other_benefit": "natura lain",
                "gift_other": "bingkisan", "meal_coupon_field_duty": "kupon makan dinas luar", "sports_facility":
                "fasilitas olahraga", "contract_fixed_income": "penghasilan tetap menurut kontrak", "klu": "KLU",
                "tax_id_valid": "NPWP/NIK valid", "other_dtp_incentive": "menerima insentif lain",
                "jkk_risk_group": "risiko JKK", "ptkp_status": "status PTKP", "has_equity_in_employer": "pemegang saham",
                "avg_monthly_gross_12m": "rata-rata bruto 12 bulan", "days_present": "hari hadir",
                "months_of_service": "masa kerja (bulan)", "thr_holiday": "bulan hari raya"}


def expr_text(expr):
    return getattr(expr, "text", None) or str(expr)


def readable(expr):
    """An expression with fact names replaced by their labels, for people."""
    text = expr_text(expr)
    text = re.sub(r"param\('([a-z_0-9]+)'\)", lambda m: f"[{fact_label(m.group(1)).lower()}]", text)
    text = re.sub(r"(?:income|benefit|employee|employer|hr|case)\('([a-z_0-9]+)'\)",
                  lambda m: f"[{INPUT_LABELS.get(m.group(1), fact_label(m.group(1)).lower())}]", text)
    text = re.sub(r"(?:in_table|lookup|bracket|progressive)\('([a-z_0-9]+)'",
                  lambda m: f"tabel '{m.group(1).replace('_', ' ')}'", text)
    text = re.sub(r"\b([a-z][a-z_0-9]{2,})\b(?!\()", lambda m: fact_label(m.group(1)).lower()
                  if m.group(1) in facts() else m.group(1), text)
    for a, b in ((" and ", " dan "), (" or ", " atau "), (" if ", " jika "), (" else ", " selain itu "),
                 ("max(", "maks("), ("min(", "min("), ("== True", "= ya"), ("!= None", "terisi"), ("None", "kosong")):
        text = text.replace(a, b)
    return text


def tgl(x):
    """1 Jan 2026, with Indonesian month abbreviations."""
    names = ("Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des")
    return "-" if x is None else f"{x.day} {names[x.month - 1]} {x.year}"


def money(x):
    if x is None:
        return "-"
    x = Fraction(x)
    s = f"{abs(int(x)):,}".replace(",", ".")
    return ("−Rp" if x < 0 else "Rp") + s


def pct(x):
    return "-" if x is None else f"{float(x) * 100:.2f}".rstrip("0").rstrip(",.").replace(".", ",") + "%"


def compute(case, omega=None, knowledge=None):
    try:
        return evaluate_case(knowledge or kb(), case, omega or TODAY, trace=True), None
    except Exception as e:  # noqa: BLE001 - shown on screen
        return None, f"{type(e).__name__}: {e}"


def value(result, fact, month=0):
    t = (result.trace or {}).get((fact, month))
    return t["value"] if t else None
