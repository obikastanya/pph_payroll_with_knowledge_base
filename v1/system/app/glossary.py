"""Glossary of the terms on screen, and the hover marker for them.

term("PTKP") renders the word with a dotted underline and a small "?"; hovering shows a short, plain explanation.
tip("PTKP") is the same explanation for the help= tooltip of a widget or metric.
The lookup keys are Indonesian (other modules call them); SHOWN gives the English word shown inline for a key.
"""
import html
import re

import streamlit as st

# key: (label, explanation). Explanations are for a finance admin, not a tax lawyer: one or two sentences.
TERMS = {
    # tax calculation
    "PPh 21": ("PPh 21 (Article 21 income tax)", "Tax on salary, wages, and other pay an employee receives. The employer "
                                                 "withholds it from pay every month and pays it to the state."),
    "masa pajak": ("Tax period", "One calendar month. PPh 21 is calculated, withheld, and reported monthly."),
    "masa terakhir": ("Final tax period", "December, or the employee's last month of work if they leave mid-year. In this "
                                          "month the tax for the whole year is recalculated with the Article 17 rates."),
    "TER": ("Monthly effective rate (TER)", "A ready-made percentage for months other than the final tax period: monthly "
                                            "PPh = monthly gross income × TER rate. The table {since:ter_monthly}."),
    "kategori TER": ("TER category (A, B, C)", "The TER table that applies, set by the PTKP status. "
                                               "{groups:ter_category}."),
    "bruto": ("Gross income", "All income before any deduction: salary, allowances, overtime, THR, bonuses, taxable "
                              "in-kind benefits (natura), and insurance premiums paid by the company."),
    "biaya jabatan": ("Position cost (biaya jabatan)", "An automatic deduction of {pct:job_expense_rate} of annual gross "
                                                       "income, up to {money:job_expense_max_year} a year. No receipts needed."),
    "iuran pensiun": ("Employee pension contributions", "JHT and JP contributions the employee pays. They reduce "
                                                        "taxable income."),
    "neto": ("Net income", "Gross income minus position cost and employee pension contributions."),
    "PTKP": ("Non-taxable income threshold (PTKP)", "The part of annual income that is tax-free. It depends on marital "
                                                    "status and number of dependants on 1 January: {values:ptkp}."),
    "status PTKP": ("PTKP status", "TK = single, K = married; the number = dependants (0 to 3). The status on 1 January "
                                   "is used; a marriage or a child during the year counts only from next year."),
    "PKP": ("Taxable income (PKP)", "Annual net income minus PTKP, rounded down to the nearest thousand. This is what the "
                                    "Article 17 rates apply to."),
    "Pasal 17": ("Article 17 rates", "Progressive rates on annual taxable income (PKP): {brackets:pasal17}."),
    "PPh setahun": ("Annual PPh 21", "The tax due for the whole year: PKP × Article 17 rates."),
    "sudah dipotong": ("Already withheld", "The PPh 21 withheld in the months before the final tax period."),
    "kurang bayar": ("Under-withheld", "Annual PPh is more than what was already withheld; the difference is withheld in "
                                        "the final tax period."),
    "lebih bayar": ("Over-withheld", "What was already withheld is more than the annual PPh; the employer refunds the "
                                     "excess to the employee in the final tax period."),
    "gross": ("Gross method", "Tax is withheld from the employee's pay. Take-home pay = gross income − PPh − employee "
                              "contributions."),
    "gross-up": ("Gross-up method", "The company pays a tax allowance equal to the PPh, so the employee bears no tax. The "
                                    "allowance itself adds to gross income."),
    "ditanggung": ("Borne by the employer", "The company pays the tax without giving an allowance. The employee has no "
                                            "deduction; for the company this cost is not tax-deductible."),
    "DTP": ("Government-borne PPh 21 (DTP)", "Incentive: the state bears PPh 21 for certain employees, so the tax is paid "
                                             "out to the employee with the salary. Conditions include the business "
                                             "sector (KLU) and an income limit."),
    "KLU": ("Business sector code (KLU)", "5-digit code for the employer's line of business. It decides whether employees "
                                          "can receive the DTP incentive."),
    "NPWP": ("Valid NPWP / NIK", "Employees without a registered NPWP or NIK may be taxed at a higher rate or may not be "
                                 "eligible for the incentive."),
    "natura": ("In-kind benefits (natura)", "Pay in the form of goods or facilities (housing, vehicle, meals). Some of it is "
                                            "taxable income, some is exempt up to a limit, for example meal coupons up to "
                                            "{money:natura_meal_coupon_cap} a month."),
    "THR": ("Religious holiday allowance (THR)", "Irregular income. Added to gross income in the month it is paid, so that "
                                                 "month's TER rate can go up."),
    "bonus": ("Bonus", "Irregular income, added to gross income in the month it is paid."),
    "lembur": ("Overtime pay", "Regular income whose amount can differ from month to month."),
    "tunjangan tetap": ("Fixed allowance", "An allowance paid at a fixed amount every month (position, family, transport)."),
    "JHT": ("Old-age security (JHT)", "BPJS Ketenagakerjaan contribution. The employee's share, {pct:jht_employee_rate} of "
                                      "wages, reduces tax; the company's share is not employee income."),
    "JP": ("Pension security (JP)", "BPJS Ketenagakerjaan contribution. The employee's share, {pct:jp_employee_rate} of "
                                    "wages up to {money:jp_wage_cap} a month, reduces tax."),
    "JKK": ("Work accident insurance (JKK)", "Premium paid by the company, {range:jkk_rates} of wages depending on job "
                                             "risk. This premium adds to the employee's gross income."),
    "JKM": ("Death insurance (JKM)", "Premium of {pct:jkm_rate} of wages paid by the company; adds to the employee's "
                                     "gross income."),
    "BPJS Kesehatan": ("BPJS Kesehatan (health insurance)", "Contribution on wages up to {money:health_wage_cap} a month: "
                                                            "{pct:health_employer_rate} company (adds to gross income), "
                                                            "{pct:health_employee_rate} employee."),
    "risiko JKK": ("JKK risk group", "The level of job risk at the company, which sets the JKK premium rate."),
    "zakat": ("Zakat through the employer", "Zakat or mandatory religious donation withheld through the company; it may "
                                            "reduce net income."),
    "gaji bersih": ("Take-home pay", "What the employee receives: cash gross income minus the PPh the employee bears, "
                                     "employee contributions, and other deductions."),
    "karyawati": ("Married female employee", "A married female employee uses the single (TK) PTKP, unless there is a "
                                             "statement that her husband has no income; dependants follow the husband."),
    "bukti potong": ("Withholding slip 1721-A1", "Annual document for the employee with the year's income and PPh 21; the "
                                                 "employee uses it for the annual tax return (SPT Tahunan)."),
    # knowledge base
    "knowledge base": ("Knowledge base (KB)", "The collection of tax rules, numbers, and tables the system uses to "
                                              "calculate. Each item has an effective date and a source article."),
    "aturan": ("Rule", "One way of calculating one value, for example 'position cost = {pct:job_expense_rate} × gross "
                       "income, up to ...'."),
    "parameter": ("Number (parameter)", "One number a rule uses, for example the {pct:job_expense_rate} rate or the "
                                        "{money:job_expense_max_year} limit. When a number changes, only that number "
                                        "needs replacing."),
    "tabel": ("Table", "A list of values a rule uses, for example the PTKP table or the TER rate table."),
    "berlaku": ("Effective date", "From when (and until when) a rule applies to calculations, as the regulation sets it."),
    "dicatat": ("Recorded date", "When the rule was entered in the knowledge base. It can be after the effective date, for "
                                 "example for a regulation with retroactive effect."),
    "tanggal pengetahuan": ("Knowledge date", "Calculates 'as of that date': rules recorded after it are ignored. Useful "
                                              "for re-checking an old calculation."),
    "regulasi": ("Government regulation", "Rules from state regulations (UU, PP, PMK, PER Dirjen). Must be followed."),
    "kebijakan perusahaan": ("Company policy", "The company's own rules, for example a collective labor agreement (PKB) or "
                                               "company regulation (THR, bonus, overtime). Must not violate government "
                                               "regulation."),
    "wajib": ("Mandatory", "A rule that must be applied; it overrides a company rule if they conflict."),
    "standar": ("Default", "A fallback rule used when no other rule applies, for example how input data is read."),
    "pilihan": ("Optional", "An optional rule from a regulation that applies only if the company chooses to use it."),
    "sumber": ("Source", "The document, article, and quoted sentence where this rule is written."),
    "versi": ("KB version", "The state of the knowledge base after one update is approved. Old versions stay saved and can "
                            "be used to recalculate."),
    "pembaruan": ("Update", "A package of changes from one document: rules added, changed, or revoked."),
    "pencabutan": ("Revocation", "A rule is given an end date. It is not deleted, so old calculations can still be "
                                 "repeated."),
    "dokumen baru": ("New documents", "Regulations or company policies that were uploaded and are waiting to be read by "
                                      "the AI or reviewed."),
    "keadaan awal": ("Initial demo state", "The fixed starting point of the demo. Everything done during the demo can be "
                                           "erased with the button 'Restore initial demo state'."),
    "usulan": ("Proposed update", "A draft update the AI prepares from a document. It is not used until a person "
                                  "approves it."),
    "pemeriksaan": ("Automatic checks", "Five checks before a proposal reaches you: format, the quote is in the document, "
                                        "no conflicts, no change to past calculations, every rule makes a difference."),
    "versi usulan": ("Proposed versions", "The AI writes several proposed versions separately from the same document. When "
                                          "the versions agree, confidence is higher."),
    "kesepakatan": ("Agreement", "A proposal is chosen when most proposed versions produce the same calculation."),
    "ragu": ("System unsure", "The proposed versions disagree, so the system proposes nothing and asks a person to write "
                              "the update. Safer than guessing."),
    "dampak": ("Impact", "Company policies that read a value that changed, so they may need updating too."),
    "review": ("Review", "A person checks the proposal, then approves, fixes, or rejects it."),
    "kutipan": ("Quote", "The exact sentence from the document that a rule is based on. The system checks that this "
                         "sentence really is in the document."),
    "relevan": ("Relevant", "The document contains something that changes the PPh 21 calculation. Other documents are "
                            "ignored."),
    "asisten": ("AI assistant", "AI chat in a pop-up window that helps check proposals, fix them following your notes, and "
                                "prepare draft changes. Every change still goes through your review."),
    # technical view of the knowledge base
    "knowledge graph": ("Knowledge graph", "How the KB is stored: every rule, number, fact, and article is a node, and the "
                                           "relationships between them (produces, reads, sourced from) are edges."),
    "RDF": ("RDF", "A W3C standard for storing a graph as three-part statements (triples): subject, relationship, object."),
    "named graph": ("Named graph", "A group of triples with a name. Here one update = one named graph, so every KB version "
                                   "can be rebuilt."),
    "ontologi": ("Ontology", "The list of kinds of things in the KB (rule, number, article, update, ...) and the "
                             "relationships allowed between them. Uses the ELI (legislation), OWL-Time (time), and PROV-O "
                             "(provenance) standards."),
    "SHACL": ("SHACL", "A W3C standard for checking the shape of a graph, for example 'every rule must have a source and "
                       "an effective date'. Used as check G1."),
    "SPARQL": ("SPARQL", "A query language for RDF graphs, like SQL for tables."),
    "bitemporal": ("Bitemporal", "Every element has two times: when it is in force under the regulation, and when it was "
                                 "recorded in the KB. This lets a calculation be repeated 'as known on that date'."),
    "dua lapis": ("Two tiers", "Government rules and company rules are stored separately in the same KB; the engine "
                               "decides which one is used when both set the same value."),
    "jejak": ("Calculation trail", "The engine's record for every value: the rule used, the other values it read, the "
                                   "rules that lost, and the source article."),
    "resolusi konflik": ("Conflict resolution", "The order the engine uses to pick one rule when several apply to the same "
                                                "value: higher standing, more specific, then newer."),
    "pemeriksa statis": ("Static checker", "Checks the KB without calculating a case: rules that are never used, always "
                                           "lose, or contradict each other across tiers. Used as check G3."),
}

# The word shown inline for a key when the caller gives no text. Keys not listed here show the key itself.
SHOWN = {
    "masa pajak": "tax period", "masa terakhir": "final tax period", "kategori TER": "TER category", "bruto": "gross income",
    "biaya jabatan": "position cost", "iuran pensiun": "pension contributions", "neto": "net income",
    "Pasal 17": "Article 17", "PPh setahun": "annual PPh 21", "sudah dipotong": "already withheld",
    "kurang bayar": "under-withheld", "lebih bayar": "over-withheld", "gross": "gross method",
    "gross-up": "gross-up method", "ditanggung": "borne by the employer", "lembur": "overtime",
    "tunjangan tetap": "fixed allowance", "risiko JKK": "JKK risk group", "gaji bersih": "take-home pay",
    "karyawati": "married female employee", "bukti potong": "withholding slip", "aturan": "rule", "parameter": "number",
    "tabel": "table", "berlaku": "effective date", "dicatat": "recorded date", "tanggal pengetahuan": "knowledge date",
    "regulasi": "government regulation", "kebijakan perusahaan": "company policy", "wajib": "mandatory",
    "standar": "default", "pilihan": "optional", "sumber": "source", "versi": "version", "pembaruan": "update",
    "pencabutan": "revocation", "dokumen baru": "new documents", "keadaan awal": "initial state",
    "usulan": "proposed update", "pemeriksaan": "automatic checks", "versi usulan": "proposed versions",
    "kesepakatan": "agreement", "ragu": "unsure", "dampak": "impact", "kutipan": "quote", "relevan": "relevant",
    "asisten": "AI assistant", "ontologi": "ontology", "dua lapis": "two tiers", "jejak": "calculation trail",
    "resolusi konflik": "conflict resolution", "pemeriksa statis": "static checker",
}


CSS = """
<style>
.term { border-bottom: 1px dotted #8a8984; cursor: help; position: relative; display: inline-block; }
.term .q { font-size: .62em; vertical-align: super; color: #2a78d6; margin-left: 1px; font-weight: 600; }
[data-testid="stAppViewContainer"] { overflow-x: hidden; }
.term .tip { visibility: hidden; opacity: 0; position: absolute; z-index: 9999; left: 50%; top: 135%;
             transform: translateX(-50%); width: 250px; background: #24231f; color: #f7f7f5; padding: .55rem .7rem; border-radius: 8px;
             font-size: .82rem; font-weight: 400; line-height: 1.4; transition: opacity .12s; white-space: normal;
             box-shadow: 0 6px 18px rgba(0,0,0,.18); text-align: left; }
.term .tip b { color: #fff; display: block; margin-bottom: .15rem; }
.term:hover .tip { visibility: visible; opacity: 1; }
</style>
"""


def setup():
    st.markdown(CSS, unsafe_allow_html=True)


# Facts that have a glossary entry, so a line about the fact can carry the hover explanation. Decoration only: a fact
# that is not here (for instance one added by a new regulation) is shown with its label from the knowledge base.
FOR_FACT = {"gross_income": "bruto", "ter_rate": "TER", "ter_category": "kategori TER", "job_expense": "biaya jabatan",
            "annual_net": "neto", "ptkp_amount": "PTKP", "ptkp_status_effective": "status PTKP", "taxable_income": "PKP",
            "annual_pph21": "PPh setahun", "withheld_before_final": "sudah dipotong", "pph21_dtp": "DTP",
            "take_home_pay": "gaji bersih", "tax_allowance": "gross-up", "thr": "THR", "bonus": "bonus",
            "overtime_pay": "lembur", "fixed_allowance": "tunjangan tetap", "jkk_premium": "JKK", "jkm_premium": "JKM",
            "health_premium_employer": "BPJS Kesehatan", "jht_employee": "JHT", "jp_employee": "JP",
            "annual_pension_contributions": "iuran pensiun", "zakat_paid": "zakat"}

SLOT = re.compile(r"\{(pct|money|brackets|range|groups|values|since):([a-z_0-9]+)\}")
MISSING = "(not in the knowledge base on this date)"


def at():
    """The date the explanations speak about: set by the page (tax month in the calculator, the date chosen in the
    viewer), today otherwise."""
    import data as d
    return st.session_state.get("g_date") or d.TODAY


def _short_money(x):
    import data as d
    x = int(x)
    for unit, name in ((1_000_000_000, "billion"), (1_000_000, "million")):
        if x >= unit:
            v = x / unit
            return f"Rp{v:g} {name}"
    return d.money(x)


def _slot(m, t):
    import data as d
    kind, name = m.group(1), m.group(2)
    if kind in ("pct", "money"):
        p = d.param_at(name, t)
        return MISSING if p is None else (d.pct(p.value) if kind == "pct" else d.money(p.value))
    if kind == "since":
        versions = [r for r in d.current() if r.kind == "table" and r.name == name and r.valid_from]
        if not versions:
            return MISSING
        first = min(versions, key=lambda r: r.valid_from)
        src = d.short_doc(first.source[0].document) if first.source else ""
        if first.valid_from <= t:
            return f"has been in force since {d.tgl(first.valid_from)} ({src})"
        return f"only takes effect on {d.tgl(first.valid_from)} ({src})"
    tab = d.table_at(name, t)
    if tab is None or not tab.rows:
        return MISSING
    rows = list(tab.rows)
    if kind == "brackets":
        parts = [f"{d.pct(r['rate'])} up to {_short_money(r['upper'])}" for r in rows if r.get("upper")]
        parts += [f"{d.pct(r['rate'])} above that" for r in rows if not r.get("upper")]
        return ", ".join(parts)
    if kind == "range":
        vals = sorted(r["value"] for r in rows)
        return f"{d.pct(vals[0])} to {d.pct(vals[-1])}"
    if kind == "groups":
        groups = {}
        for r in rows:
            groups.setdefault(r["value"], []).append(r["key"])
        return ". ".join(f"{v}: {', '.join(ks)}" for v, ks in sorted(groups.items()))
    return f"{rows[0]['key']} {_short_money(rows[0]['value'])} to {rows[-1]['key']} {_short_money(rows[-1]['value'])}"


def explain(key):
    """(label, explanation) with the numbers of the knowledge base in force at the date of the page."""
    label, expl = TERMS[key]
    if "{" not in expl:
        return label, expl
    import data as d
    t = at()
    return label, SLOT.sub(lambda m: _slot(m, t), expl) + f" (per the knowledge base, in force on {d.tgl(t)})"


def term(key, text=None):
    """HTML: the word with a hover explanation. Use inside st.markdown(..., unsafe_allow_html=True)."""
    label, expl = explain(key)
    shown = html.escape(text or SHOWN.get(key, key))
    return (f'<span class="term">{shown}<span class="q">?</span>'
            f'<span class="tip"><b>{html.escape(label)}</b>{html.escape(expl)}</span></span>')


def tip(key):
    """Plain text explanation for help= of a widget or metric."""
    label, expl = explain(key)
    return f"**{label}**: {expl}"


def md(text, **kw):
    """st.markdown with HTML enabled, for lines that carry term() markers."""
    st.markdown(text, unsafe_allow_html=True, **kw)


def dictionary():
    """Searchable list of every term (sidebar)."""
    q = st.text_input("Search terms", "", placeholder="e.g. PTKP, TER, natura", key="gl_q")
    shown = [(k, v) for k, v in TERMS.items() if q.lower() in (k + SHOWN.get(k, "") + v[0] + v[1]).lower()] if q else []
    for k, _ in shown[:8]:
        label, expl = explain(k)
        st.markdown(f"**{label}**  \n{expl}")
    if q and not shown:
        st.caption("Nothing found.")
