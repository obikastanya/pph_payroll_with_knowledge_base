"""Labels in plain Indonesian, formatting, the topic map of the knowledge base, and the engine call.

The knowledge base is the demo's current one (store.kb(): the initial state plus what was approved during the demo).
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

import store  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402
from pph21kbs.text import registry  # noqa: E402

TODAY = date.today()
MONTHS = ("Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober",
          "November", "Desember")
MON = tuple(m[:3] for m in MONTHS)

# Topics of the viewer: (title, icon, one-line explanation, anchor facts). The titles are a reading guide; which topic
# a rule, number, or table belongs to is decided by the knowledge graph: the topic of the nearest anchor that reads
# its value (topic_of). A new rule lands in the right topic without changing this list; when it reaches no anchor, it
# gets a topic named after the output value it leads to.
TOPICS = [
    ("Penghasilan bruto", ":material/payments:", "Komponen apa saja yang dijumlahkan menjadi penghasilan bruto.",
     ("gross_income", "regular_gross", "irregular_gross", "cash_income")),
    ("Natura dan fasilitas", ":material/home_work:", "Fasilitas dan barang dari perusahaan yang ikut kena pajak.",
     ("benefits_taxable_regular", "benefits_taxable_irregular")),
    ("BPJS dan iuran", ":material/health_and_safety:", "Iuran dan premi jaminan sosial beserta batas upahnya.",
     ("jkk_premium", "jkm_premium", "health_premium_employer", "jht_employee", "jp_employee", "employer_premiums_taxable",
      "employee_pension_contributions", "annual_pension_contributions", "health_employee")),
    ("PTKP dan status", ":material/family_restroom:", "Penghasilan bebas pajak menurut status kawin dan tanggungan.",
     ("ptkp_amount", "ptkp_status_effective", "subjective_months")),
    ("PPh bulan biasa", ":material/percent:", "Cara menghitung PPh 21 bulan selain masa pajak terakhir.",
     ("pph21_running",)),
    ("Akhir tahun", ":material/event_available:", "Hitung ulang setahun di masa pajak terakhir.",
     ("annual_gross", "job_expense", "annual_deductions", "annual_net", "taxable_income", "annual_pph21",
      "withheld_before_final", "final_period_tax", "refund_to_employee")),
    ("Insentif DTP", ":material/volunteer_activism:", "PPh 21 yang ditanggung pemerintah untuk pegawai tertentu.",
     ("pph21_dtp", "dtp_eligible", "dtp_facility")),
    ("Metode dan gaji bersih", ":material/account_balance_wallet:", "Siapa menanggung pajak, dan gaji yang diterima.",
     ("pph21_due", "withholding_method", "tax_allowance", "employee_tax_burden", "take_home_pay")),
    ("Ketenagakerjaan", ":material/work_history:", "Ketentuan ketenagakerjaan yang diperiksa, misalnya THR minimum.",
     ("thr_minimum",)),
]
QUOTED = re.compile(r"[a-z_]+\('([a-z0-9_]+)'")       # first quoted argument of a function call


def kb():
    return store.kb()


@st.cache_resource
def _facts(signature):
    return {r.id: r for r in kb().records if r.kind == "fact"}


def facts():
    return _facts(store.signature())


@st.cache_resource
def _params(signature):
    out = {}
    for r in kb().records:
        if r.kind == "parameter":
            out.setdefault(r.name, r)
    return out


def params():
    return _params(store.signature())


@st.cache_resource
def _current(signature):
    """The latest record of every id: a later version that ends or revokes an element wins over the earlier one."""
    best = {}
    for r in kb().records:
        if r.id not in best or r.seq > best[r.id].seq:
            best[r.id] = r
    return list(best.values())


def current():
    return _current(store.signature())


def in_force(r, t):
    return r.valid_from is None or (r.valid_from <= t and (r.valid_until is None or t <= r.valid_until))


def _named_at(kind, name, t):
    found = [r for r in current() if r.kind == kind and r.name == name and in_force(r, t)]
    return max(found, key=lambda r: (r.valid_from, r.seq)) if found else None     # the newer one wins, as in the engine


def param_at(name, t):
    """The parameter record in force at t, or None."""
    return _named_at("parameter", name, t)


def table_at(name, t):
    """The table version in force at t, or None."""
    return _named_at("table", name, t)


def doc_title(doc_id):
    """Title from the document registry of the research, else from the knowledge base (documents added later)."""
    t = registry().get(doc_id, {}).get("title")
    if t:
        return t
    doc = kb().documents.get(doc_id)
    return (doc.title if doc and doc.title else doc_id)


def short_doc(doc_id):
    """'PMK 168/2023' from the registry title; for a document added later its own title, shortened."""
    if registry().get(doc_id, {}).get("title"):
        t = doc_title(doc_id)
        return t.split(":")[0] if ":" in t else doc_id
    t = doc_title(doc_id)
    return t if len(t) <= 40 else t[:38] + "…"


def fact_label(name):
    f = facts().get(name)
    if f and f.label_id:
        return f.label_id[0].upper() + f.label_id[1:]
    p = params().get(name)
    if p and p.label_id:
        return p.label_id[0].upper() + p.label_id[1:]
    return name.replace("_", " ")


@st.cache_resource
def _names(signature):
    return {r.name for r in kb().records if r.kind in ("parameter", "table")}


def names():
    """Names of the parameters and tables of the knowledge base."""
    return _names(store.signature())


def _deps(r):
    exprs = [e for e in (getattr(r, "expression", None), getattr(r, "condition", None), getattr(r, "assertion", None))
             if e is not None]
    return {f for e in exprs for f in e.dependencies()}, {n for e in exprs for n in QUOTED.findall(expr_text(e))} & names()


@st.cache_resource
def _topic_index(signature):
    """fact -> topic and parameter/table name -> topic, from the graph of every rule of the knowledge base."""
    rules = [r for r in current() if r.kind == "rule" and r.layer != "company"]      # input conventions link too
    readers, users, by_fact = {}, {}, {}
    for r in rules:
        by_fact.setdefault(r.produces, []).append(r)
        facts_read, names = _deps(r)
        for f in facts_read:
            readers.setdefault(f, set()).add(r.produces)
        for n in names:
            users.setdefault(n, []).append((r.produces, in_force(r, TODAY)))
    anchor = {f: title for title, _, _, fs in TOPICS for f in fs}
    outputs = {n for n, f in facts().items() if f.output}

    level = {}

    def depth(f, stack=()):
        """Position in the order of calculation: 1 + the deepest value its rules read."""
        if f not in level:
            ds = [g for r in by_fact.get(f, ()) for g in _deps(r)[0] if g not in stack]
            level[f] = 1 + max((depth(g, stack + (f,)) for g in ds), default=0)
        return level[f]
    # A value belongs where it is used: it takes the topic most of the values that read it have (anchors keep
    # theirs), repeated until nothing changes; at a tie, the topic of the reader earliest in the calculation. A new
    # rule therefore joins the topic of what it feeds, whatever its name.
    fact_topic = dict(anchor)
    neighbours = set(readers) | {r.produces for r in rules}
    for _ in range(40):
        changed = False
        for f in sorted(neighbours):
            if f in anchor:
                continue
            voters = [x for x in readers.get(f, ()) if x in fact_topic]
            if not voters:
                continue
            votes = [fact_topic[x] for x in voters]
            best = max(votes.count(v) for v in set(votes))
            pick = fact_topic[min((x for x in voters if votes.count(fact_topic[x]) == best), key=lambda x: (depth(x), x))]
            if fact_topic.get(f) != pick:
                fact_topic[f], changed = pick, True
        if not changed:
            break
    for f in neighbours:                      # a part of the graph no topic reaches: named by the output it leads to
        if f not in fact_topic:
            seen, frontier, named = {f}, [f], None
            while frontier and named is None:
                named = next((x for x in frontier if x in outputs and x != f), None)
                frontier = [y for x in frontier for y in sorted(readers.get(x, ())) if not (y in seen or seen.add(y))]
            fact_topic[f] = fact_label(named or f)
    name_topic = {}
    for n, fs in users.items():         # a number or table belongs where it is used now (else where it was used)
        now = [f for f, live in fs if live] or [f for f, _ in fs]
        votes = [fact_topic[f] for f in now if f in fact_topic]
        name_topic[n] = max(set(votes), key=votes.count) if votes else "Lainnya"
    return fact_topic, name_topic


def topic_of(rec):
    if getattr(rec, "layer", "") == "company":
        return "Kebijakan perusahaan"
    fact_topic, name_topic = _topic_index(store.signature())
    if rec.kind == "rule":
        return fact_topic.get(rec.produces, "Lainnya")
    if rec.kind in ("parameter", "table"):
        return name_topic.get(rec.name, "Lainnya")
    if rec.kind == "fact":
        return fact_topic.get(rec.id, "Lainnya")
    facts_read, _ = _deps(rec)
    votes = [fact_topic[f] for f in facts_read if f in fact_topic]
    return max(set(votes), key=votes.count) if votes else "Lainnya"


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


def fmt(fact, v):
    """A value of a fact as text, by the type the knowledge base gives the fact."""
    kind = getattr(facts().get(fact), "fact_type", "money")
    if v is None:
        return "-"
    if kind == "bool" or isinstance(v, bool):
        return "ya" if v else "tidak"
    if kind == "rate":
        return pct(v)
    if kind == "money":
        return money(v)
    return str(v)


def compute(case, omega=None, knowledge=None):
    try:
        return evaluate_case(knowledge or kb(), case, omega or TODAY, trace=True), None
    except Exception as e:  # noqa: BLE001 - shown on screen
        return None, f"{type(e).__name__}: {e}"


def value(result, fact, month=0):
    t = (result.trace or {}).get((fact, month))
    return t["value"] if t else None
