"""Company instances: one system per company, each with its profile, its employees (a panel drawn from the BPS wage
cell of its sector and province, never below the provincial minimum wage), and its own stream of documents.

Assumptions (stated in the study): PTKP status uniform over the eight statuses (as in v1); a grade multiplier spreads
wages around the cell average; wages of other years follow the provincial minimum wage of that year relative to 2025
(2027: +6.5%); about 10% of employees leave and 10% join each year at a random month; THR is paid in month 4 (v1).
"""
import csv
import random
from dataclasses import dataclass, field
from datetime import date

import openpyxl

from . import DATA
from . import testspace as ts

SP_INDEX = DATA / "10_kebijakan_perusahaan" / "sintetis" / "INDEX.csv"
UMP_DIR = DATA / "04_data_publik" / "kemnaker"
YEARS = (2023, 2024, 2025, 2026)
PANEL_SIZE = 150
TURNOVER = 0.10
GRADES = ((0.85, 0.35), (1.0, 0.30), (1.3, 0.20), (1.8, 0.10), (3.0, 0.05))
SECTION = {"13": "C", "14": "C", "15": "C", "21": "C", "22": "C", "29": "C", "41": "F", "50": "H", "52": "H",
           "55": "I", "46": "G", "47": "G", "62": "J", "63": "J", "09": "B"}


@dataclass(frozen=True)
class Change:
    on: date
    workers: int | None = None
    klu: str | None = None


@dataclass(frozen=True)
class Document:
    id: str                        # document id in the workspace (13_teks)
    known_on: date                 # the day the company uploads it: issue or signing date, or the install date
    gold: str | None               # gold company update (12_emas), None while it is still to be written
    policy_from: date | None = None    # a new policy (the system names it after the document) in force from this
    #                                    day; None for an amendment of the policy already in force


@dataclass(frozen=True)
class Instance:
    id: str
    name: str
    real: bool
    klu: str
    province: str
    jkk_risk: str
    workers: int
    installed: date
    documents: tuple = ()
    changes: tuple = ()
    chain: str = ""                # the chain whose regulation drafts it uses (its own id for a real company)
    extra: dict = field(default_factory=dict, compare=False, hash=False)

    def policy_on(self, year):
        """The policy the payroll of a tax year follows: the latest policy document in force by the year's end."""
        current = None
        for d in sorted(self.documents, key=lambda d: d.policy_from or date.max):
            if d.policy_from and d.policy_from <= date(year, 12, 31):
                current = d.id
        return current

    def profile_on(self, day):
        """(KLU, workers) on a day, after the profile changes made by then."""
        klu, workers = self.klu, self.workers
        for c in self.changes:
            if c.on <= day:
                klu, workers = c.klu or klu, c.workers or workers
        return klu, workers


# Labour-intensive industries of PP 7/2025 (footwear, textiles and apparel, furniture, leather): the KLU prefixes
# whose companies with at least 50 workers get the JKK relief.
RELIEF_PREFIXES = ("13", "14", "15", "16", "31")

REAL = (
    Instance("SANSAN", "PT Sansan Saudaratex Jaya", True, "14111", "JAWA BARAT", "very_low", 1000, date(2023, 1, 1),
             (Document("PKB-SANSAN-2021", date(2023, 1, 1), "GOLD-PKB-SANSAN", date(2021, 9, 23)),), chain="SANSAN"),
    Instance("CENTEX", "PT Century Textile Industry Tbk", True, "13111", "DKI JAKARTA", "medium", 1000,
             date(2023, 1, 1), (Document("PKB-CENTEX-2021", date(2023, 1, 1), "GOLD-PKB-CENTEX-2021", date(2021, 1, 8)),
                                Document("PKB-CENTEX-2024", date(2024, 3, 27), "GOLD-PKB-CENTEX", date(2024, 3, 27))), chain="CENTEX"),
    Instance("TAEKWANG", "PT TKG Taekwang Indonesia", True, "15201", "JAWA BARAT", "low", 1000, date(2024, 1, 1),
             (Document("PKB-TAEKWANG-2024", date(2024, 1, 1), "GOLD-PKB-TKG", date(2024, 3, 1)),), chain="TAEKWANG"),
    Instance("AVCO", "PT Airfast Aviation Facilities", True, "52230", "PAPUA TENGAH", "very_high", 300,
             date(2024, 4, 1), (Document("PKB-AVCO-2024", date(2024, 4, 1), "GOLD-PKB-AVCO", date(2024, 4, 1)),), chain="AVCO"),
    Instance("WIKA", "PT Wijaya Karya (Persero) Tbk", True, "41011", "DKI JAKARTA", "high", 1000, date(2025, 3, 1),
             (Document("PKB-WIKA-2025", date(2025, 3, 1), "GOLD-PKB-WIKA", date(2025, 3, 1)),), chain="WIKA"),
)

FICTIONAL_TEST = ("SP02", "SP03", "SP04", "SP05", "SP06", "SP07", "SP08", "SP11", "SP12", "SP13")
FICTIONAL_DEV = ("SP01", "SP09", "SP10", "SP14")
FICTIONAL_PLACE = {"SP02": ("BANTEN", 400), "SP03": ("BALI", 220), "SP04": ("KALIMANTAN TIMUR", 180),
                   "SP05": ("JAWA TENGAH", 45), "SP06": ("JAWA BARAT", 120), "SP07": ("JAWA TIMUR", 300),
                   "SP08": ("DKI JAKARTA", 90), "SP11": ("SULAWESI SELATAN", 350), "SP12": ("DKI JAKARTA", 30),
                   "SP13": ("JAWA TIMUR", 160), "SP01": ("BANTEN", 150), "SP09": ("JAWA BARAT", 250),
                   "SP10": ("JAWA TIMUR", 200), "SP14": ("JAWA TENGAH", 600)}
FICTIONAL_CHANGES = {"SP05": (Change(date(2025, 1, 1), workers=60),),            # crosses 50 workers
                     "SP06": (Change(date(2026, 1, 1), klu="14111"),)}            # wholesale -> garment making
SHARED_CHAINS = {"SIM-A": FICTIONAL_TEST[:5], "SIM-B": FICTIONAL_TEST[5:]}
# A policy whose gold rules refer to facts a later regulation introduces is uploaded the day after that regulation:
# SP04 sets the taxable part of housing, a fact of PMK 66/2023 (issued 27 June 2023).
UPLOAD_AFTER = {"SP04": date(2023, 6, 28)}
# One memo amending each fictional company's policy within the window: (prospective unit id, upload day)
MEMOS = {"SP02": ("K01", date(2024, 7, 1)), "SP03": ("K02", date(2026, 1, 15)), "SP04": ("K03", date(2024, 4, 1)),
         "SP05": ("K04", date(2025, 6, 2)), "SP06": ("K05", date(2026, 3, 2)), "SP07": ("K06", date(2025, 4, 1)),
         "SP08": ("K07", date(2025, 1, 15)), "SP11": ("K08", date(2026, 2, 2)), "SP12": ("K09", date(2024, 11, 1)),
         "SP13": ("K10", date(2024, 9, 2))}


def _sp_rows():
    with open(SP_INDEX, encoding="utf-8", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def fictional(ids=FICTIONAL_TEST, jkk_risk=None):
    """Fictional companies of the synthetic policies, installed on 1 January 2023 without a policy; the policy
    document arrives on its start date. jkk_risk: id -> risk group (from the gold policy), default very_low."""
    rows, out = _sp_rows(), []
    chain_of = {i: c for c, ids_ in SHARED_CHAINS.items() for i in ids_}
    for i in ids:
        r = rows[i]
        province, workers = FICTIONAL_PLACE[i]
        start = date.fromisoformat(r["berlaku_mulai"])
        docs = [Document(i, max(start, UPLOAD_AFTER.get(i, start)), f"GOLD-{i}", start)]
        if i in MEMOS:
            memo, day = MEMOS[i]
            docs.append(Document(memo, day, memo))
        out.append(Instance(i, r["perusahaan"], False, r["klu"], province, (jkk_risk or {}).get(i, "very_low"),
                            workers, date(2023, 1, 1), tuple(docs), FICTIONAL_CHANGES.get(i, ()),
                            chain=chain_of.get(i, i)))
    return out


def relief_eligible(klu, workers):
    return workers >= 50 and klu.startswith(RELIEF_PREFIXES)


# ---------------------------------------------------------------------------------------------------- wages and panel
def _ump(year):
    """Province (upper case) -> provincial minimum wage of the year (2027: 2026 + 6.5%)."""
    if year > 2026:
        return {p: int(v * 1.065) for p, v in _ump(2026).items()}
    wb = openpyxl.load_workbook(UMP_DIR / f"kemnaker_ump_{year}.xlsx", read_only=True)
    out = {}
    for row in wb.active.iter_rows(values_only=True):
        if len(row) > 2 and isinstance(row[0], (int, float)) and row[1] and isinstance(row[2], (int, float)):
            out[str(row[1]).strip().upper()] = int(row[2] + 0.999)
    return out


_UMP = {}


def ump(year, province):
    if year not in _UMP:
        _UMP[year] = _ump(year)
    table = _UMP[year]
    return table.get(province) or table.get(province.replace("KEP.", "KEPULAUAN")) or min(table.values())


def cell_wage(province, klu):
    section = SECTION.get(klu[:2], "C")
    for p, s, v in ts.bps_wages():
        if p == province and s.split()[0].rstrip(",") == section:
            return v
    return next(v for p, s, v in ts.bps_wages() if p == province and s == "Total")


def panel(inst, years=YEARS, seed=20261115, fields=None):
    """Employee-years of the instance from its install year: case dicts in the engine's format, with
    employer.policy set to the policy in force that year, and the company's payroll fields (domains.company_fields:
    (accessor, key) -> values) varied: an employee field per employee, a company field fixed for the company, a
    monthly field per month."""
    rng = random.Random(f"{seed}-{inst.id}")
    base = cell_wage(inst.province, inst.klu)
    people, next_id, cases = [], 0, []
    for year in [y for y in years if y >= inst.installed.year]:
        if not people:
            people = [{"n": i, "grade": _grade(rng), "ptkp": rng.choice(ts.PTKP), "start": 1}
                      for i in range(PANEL_SIZE)]
            next_id = PANEL_SIZE
        else:
            people = [p for p in people if not p.get("left")]
            for p in people:
                p["start"] = 1
            joiners = [{"n": next_id + i, "grade": _grade(rng), "ptkp": rng.choice(ts.PTKP),
                        "start": rng.randint(2, 12)} for i in range(round(PANEL_SIZE * TURNOVER))]
            next_id += len(joiners)
            people += joiners
        for p in people:
            if p["start"] == 1 and rng.random() < TURNOVER:
                p["end"], p["left"] = rng.randint(1, 11), True
            else:
                p["end"] = 12
        klu, workers = inst.profile_on(date(year, 1, 1))
        scale = ump(year, inst.province) / ump(2025, inst.province)
        for p in people:
            salary = max(ump(year, inst.province), int(base * scale * p["grade"]))
            pattern = "full"
            c = ts.make_case(f"{inst.id}-{year}-{p['n']:04d}", year, salary, p["ptkp"], "gross", pattern, "thr")
            c["employment"] = {"start_month": p["start"], "end_month": p["end"]}
            c["periods"] = [q for q in c["periods"] if p["start"] <= q["month"] <= p["end"]]
            if not c["periods"]:
                continue
            c["employer"] = {"klu": klu, "jkk_risk_group": inst.jkk_risk,
                             "jkk_relief_eligible": relief_eligible(klu, workers), "policy": inst.policy_on(year)}
            _fill(c, fields or {}, p["n"], inst.id)
            c["criterion"], c["cell"] = "panel", {"instance": inst.id, "grade": p["grade"]}
            cases.append(c)
    return cases


BUCKET = {"hr": "hr", "income": "income", "benefit": "benefits"}


def _fill(case, fields, n, company):
    for j, ((accessor, key), values) in enumerate(sorted(fields.items())):
        if accessor == "employee":
            case["employee"][key] = values[(n * 7 + j) % len(values)]
        elif accessor == "employer":
            case["employer"][key] = values[sum(map(ord, company + key)) % len(values)]
        elif accessor in BUCKET:
            for q in case["periods"]:
                q.setdefault(BUCKET[accessor], {})[key] = values[(n + q["month"] + j) % len(values)]


def _grade(rng):
    r, acc = rng.random(), 0.0
    for g, w in GRADES:
        acc += w
        if r < acc:
            return g
    return GRADES[-1][0]
