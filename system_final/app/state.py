"""Application state and data access: the knowledge base in use, what was done on top of it, the documents waiting
for review, labels and formatting, and the engine call.

The knowledge base in use is the starting knowledge base (data/kb/seed.trig) plus every update approved in the app,
in order. Approved updates, drafts, uploaded documents, saved employees and the assistant chat are kept in
workspace/state.json and workspace/chat.json; the shipped data is never changed.

Document status values (STATUSES):
    awaiting_ai       uploaded, not read by the model yet
    review            a proposed update waits for the reviewer
    uncertain         the model's drafts disagreed or none passed the checks: the reviewer formalises it
    not_relevant      the model found that the document does not change the calculation
    budget_exhausted  the spending limit stopped the model
    approved, rejected
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import date, datetime
from fractions import Fraction
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pph21kbs import config, documents, graph  # noqa: E402
from pph21kbs.documents import registry  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402

WORKSPACE = config.WORKSPACE
STATE = WORKSPACE / "state.json"
CHAT = WORKSPACE / "chat.json"
RUNS = WORKSPACE / "runs"                    # model runs of the documents read in the app
TODAY = date.today()
STATUSES = ("awaiting_ai", "review", "uncertain", "not_relevant", "budget_exhausted", "approved", "rejected")
RUN_STATUS = {"proposed": "review", "abstain": "uncertain", "empty": "not_relevant", "budget": "budget_exhausted"}


# ====================================================================================================================
# State file
# ====================================================================================================================
def _empty():
    return {"approved": [], "decided": {}, "drafts": [], "log": [], "fixed": {}, "catalog": [], "employees": {},
            "inbox": []}


def load():
    if STATE.exists():
        return {**_empty(), **json.loads(STATE.read_text(encoding="utf-8"))}
    return _empty()


def save(s):
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def log(s, text):
    s["log"].insert(0, {"when": datetime.now().strftime("%d/%m %H:%M"), "what": text})


def reset():
    """Start over: back to the starting knowledge base with nothing approved, no drafts, no documents, no saved
    employees, and no chat. The record of model calls (config.CALLS) is kept, so the spending limits still hold."""
    for p in WORKSPACE.iterdir() if WORKSPACE.exists() else ():
        if p.resolve() == config.CALLS.resolve():
            continue
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        else:
            p.unlink(missing_ok=True)
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    _SIGNATURES.clear()
    documents.clear_caches()


def pending(s=None):
    """Documents in the inbox (uploaded in the app)."""
    return (s or load())["inbox"]


def pending_by_id(s=None):
    return {p["id"]: p for p in pending(s)}


# ====================================================================================================================
# Knowledge base
# ====================================================================================================================
@st.cache_resource(show_spinner="Loading the knowledge base ...")
def base():
    """The starting knowledge base: the regulation chain shipped in data/kb/seed.trig."""
    return graph.read_trig(config.SEED_KB, "K")


def base_label():
    return fmt_date(max(u.recorded_on for u in base().updates if u.recorded_on))


@st.cache_resource(show_spinner="Applying approved updates ...", max_entries=2)
def _kb_cached(signature):
    k = base()
    for a in load()["approved"]:
        k = apply_delta(k, a["delta"])
    return k


_SIGNATURES = {}          # (mtime, size) of the state file -> signature, so the file is hashed once per save


def signature():
    """A hash of the approved updates: it changes only when the knowledge base in use changes, not when a draft, an
    employee, or a log line is saved."""
    info = STATE.stat() if STATE.exists() else None
    key = (info.st_mtime_ns, info.st_size) if info else None
    if key not in _SIGNATURES:
        approved = load()["approved"] if info else []
        _SIGNATURES.clear()
        _SIGNATURES[key] = hashlib.sha256(json.dumps(approved, sort_keys=True, default=str)
                                          .encode("utf-8")).hexdigest()[:20]
    return _SIGNATURES[key]


def kb():
    """The knowledge base in use: the starting one plus the approved updates."""
    return _kb_cached(signature())


def known_until():
    return max(u.recorded_on for u in kb().updates if u.recorded_on)


def installed_policies():
    """Company policies in the knowledge base in use: id -> title."""
    out = {}
    for a in load()["approved"]:
        for el in a["delta"].get("add", []):
            if el.get("kind") == "rule" and el.get("policy"):
                out[el["policy"]] = a["title"]
    return out


def sample_policies():
    """Sample company policies shipped in data/policies: id -> (title, Delta)."""
    out = {}
    for p in sorted(config.POLICIES.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        out[p.stem] = (d["document"].get("title") or p.stem, d)
    return out


# ====================================================================================================================
# Documents, model runs, and review decisions
# ====================================================================================================================
@st.cache_data
def _read(path, mtime):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run(pid):
    """The model run of a document in the inbox, or None."""
    p = pending_by_id().get(pid)
    if not p or not p.get("run"):
        return None
    path = WORKSPACE / p["run"]
    return _read(str(path), path.stat().st_mtime) if path.exists() else None


def status(pid, s=None):
    s = s or load()
    if pid in s["decided"]:
        return s["decided"][pid]
    if any(x["id"] == pid for x in s["drafts"]) or pid in s["fixed"]:
        return "review"
    r = run(pid)
    if r is None:
        return "awaiting_ai"
    return RUN_STATUS.get(r["status"], r["status"])


def proposal(pid, s=None):
    """The update under review: a fixed or edited version if there is one, else the model's."""
    s = s or load()
    if pid in s["fixed"]:
        return s["fixed"][pid]["delta"]
    for d in s["drafts"]:
        if d["id"] == pid:
            return d["delta"]
    r = run(pid)
    return r.get("delta") if r else None


def carried_inputs(pid, s=None):
    """Input definitions an update brings with it (new payroll inputs the calculator must ask for)."""
    s = s or load()
    for x in s["drafts"]:
        if x["id"] == pid and x.get("inputs"):
            return x["inputs"]
    return []


def approve(pid, title, delta, reviewer, note=""):
    s = load()
    s["approved"].append({"id": pid, "title": title, "delta": delta, "reviewer": reviewer, "note": note,
                          "inputs": carried_inputs(pid, s), "when": datetime.now().strftime("%d/%m/%Y %H:%M")})
    s["decided"][pid] = "approved"
    s["drafts"] = [d for d in s["drafts"] if d["id"] != pid]
    log(s, f"Approved: {title} (by {reviewer})")
    save(s)


def reject(pid, title, reason):
    s = load()
    s["decided"][pid] = "rejected"
    s["drafts"] = [d for d in s["drafts"] if d["id"] != pid]
    log(s, f"Rejected: {title}. Reason: {reason}")
    save(s)


def add_draft(pid, title, delta, origin, inputs=None):
    """A draft update for review. origin: where it comes from (a key of manage.ORIGINS: manual, upload, template,
    assistant, sample)."""
    s = load()
    s["drafts"] = [d for d in s["drafts"] if d["id"] != pid]
    s["drafts"].append({"id": pid, "title": title, "delta": delta, "origin": origin, "inputs": inputs or []})
    s["decided"].pop(pid, None)
    log(s, f"Draft sent to review: {title} ({origin})")
    save(s)


def set_fixed(pid, delta, note, by, llm=None):
    """A new version of a proposal: edited by hand, or repaired by the model (llm: the model's own output, kept for a
    further repair round)."""
    s = load()
    s["fixed"][pid] = {"delta": delta, "note": note, "by": by, "llm": llm}
    log(s, f"Proposal revised ({by}): {pid}")
    save(s)


def rollback(n):
    """Keep only the first n updates approved in the app."""
    s = load()
    removed = s["approved"][n:]
    s["approved"] = s["approved"][:n]
    for a in removed:
        s["decided"].pop(a["id"], None)
    log(s, f"Rolled back to the version before: {', '.join(a['title'] for a in removed)}")
    save(s)


def add_inbox(item):
    s = load()
    s["inbox"] = [x for x in s["inbox"] if x["id"] != item["id"]] + [item]
    s["decided"].pop(item["id"], None)
    s["fixed"].pop(item["id"], None)
    log(s, f"Document received: {item['title']}")
    save(s)


def set_run(pid, relpath, cost):
    s = load()
    for x in s["inbox"]:
        if x["id"] == pid:
            x["run"] = relpath
            x["cost_usd"] = round((x.get("cost_usd") or 0) + cost, 4)
    s["fixed"].pop(pid, None)
    s["decided"].pop(pid, None)
    log(s, f"Read by the model: {pid} (USD {cost:.3f})")
    save(s)


# ====================================================================================================================
# Company data: pay components and saved employees
# ====================================================================================================================
def add_component(name, key):
    s = load()
    s["catalog"] = [c for c in s["catalog"] if c["name"] != name] + [{"name": name, "key": key}]
    log(s, f"Pay component added: {name}")
    save(s)


def save_employee(name, entry):
    s = load()
    s["employees"][name] = entry
    log(s, f"Employee saved: {name}")
    save(s)


# ====================================================================================================================
# Assistant chat
# ====================================================================================================================
def chat_load():
    return json.loads(CHAT.read_text(encoding="utf-8")) if CHAT.exists() else []


def chat_save(msgs):
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    CHAT.write_text(json.dumps(msgs, ensure_ascii=False, indent=1), encoding="utf-8")


def chat_clear():
    CHAT.unlink(missing_ok=True)


# ====================================================================================================================
# Records of the knowledge base in use
# ====================================================================================================================
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")
MON = tuple(m[:3] for m in MONTHS)

# Topics of the knowledge-base viewer: (title, icon, one-line explanation, anchor facts). Which topic a rule, number,
# or table belongs to is decided by the knowledge graph: the topic of the nearest anchor that reads its value
# (topic_of). A new rule lands in the right topic without changing this list; when it reaches no anchor, it gets a
# topic named after the output value it leads to.
TOPICS = [
    ("Gross income", ":material/payments:", "The components added up to gross income.",
     ("gross_income", "regular_gross", "irregular_gross", "cash_income")),
    ("Benefits in kind", ":material/home_work:", "Facilities and goods from the employer that are taxable.",
     ("benefits_taxable_regular", "benefits_taxable_irregular")),
    ("Social security (BPJS)", ":material/health_and_safety:", "Contributions and premiums with their wage caps.",
     ("jkk_premium", "jkm_premium", "health_premium_employer", "jht_employee", "jp_employee",
      "employer_premiums_taxable", "employee_pension_contributions", "annual_pension_contributions",
      "health_employee")),
    ("PTKP and status", ":material/family_restroom:", "Non-taxable income (PTKP) by marital status and dependants.",
     ("ptkp_amount", "ptkp_status_effective", "subjective_months")),
    ("Monthly withholding", ":material/percent:", "How PPh 21 is computed in every period except the final one.",
     ("pph21_running",)),
    ("Year end", ":material/event_available:", "The annual recalculation in the final tax period.",
     ("annual_gross", "job_expense", "annual_deductions", "annual_net", "taxable_income", "annual_pph21",
      "withheld_before_final", "final_period_tax", "refund_to_employee")),
    ("Government-borne tax (DTP)", ":material/volunteer_activism:",
     "PPh 21 borne by the government for some employees.",
     ("pph21_dtp", "dtp_eligible", "dtp_facility")),
    ("Method and net pay", ":material/account_balance_wallet:", "Who bears the tax, and the pay the employee receives.",
     ("pph21_due", "withholding_method", "tax_allowance", "employee_tax_burden", "take_home_pay")),
    ("Employment terms", ":material/work_history:", "Labour rules that are checked, such as the minimum THR.",
     ("thr_minimum",)),
]
OTHER_TOPIC = "Other"
POLICY_TOPIC = "Company policies"
QUOTED = re.compile(r"[a-z_]+\('([a-z0-9_]+)'")       # first quoted argument of a function call


@st.cache_resource(max_entries=2)
def _facts(signature):
    return {r.id: r for r in kb().records if r.kind == "fact"}


def facts():
    return _facts(signature())


@st.cache_resource(max_entries=2)
def _params(signature):
    out = {}
    for r in kb().records:
        if r.kind == "parameter":
            out.setdefault(r.name, r)
    return out


def params():
    return _params(signature())


@st.cache_resource(max_entries=2)
def _current(signature):
    """The latest record of every id: a later version that ends or revokes an element wins over the earlier one."""
    best = {}
    for r in kb().records:
        if r.id not in best or r.seq > best[r.id].seq:
            best[r.id] = r
    return list(best.values())


def current():
    return _current(signature())


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
    """Title from the document registry, else from the knowledge base."""
    t = registry().get(doc_id, {}).get("title")
    if t:
        return t
    doc = kb().documents.get(doc_id)
    return doc.title if doc and doc.title else doc_id


def short_doc(doc_id):
    """'PMK 168/2023' from a registry title 'PMK 168/2023: ...'; otherwise the title, shortened."""
    t = doc_title(doc_id)
    if ":" in t and registry().get(doc_id):
        return t.split(":")[0]
    return t if len(t) <= 40 else t[:38] + "…"


def fact_label(name):
    """The English label of a fact or parameter, capitalised; the name itself when there is none."""
    f = facts().get(name) or params().get(name)
    if f and f.label:
        return f.label[0].upper() + f.label[1:]
    return name.replace("_", " ")


@st.cache_resource(max_entries=2)
def _names(signature):
    return {r.name for r in kb().records if r.kind in ("parameter", "table")}


def names():
    """Names of the parameters and tables of the knowledge base."""
    return _names(signature())


def _deps(r):
    exprs = [e for e in (getattr(r, "expression", None), getattr(r, "condition", None), getattr(r, "assertion", None))
             if e is not None]
    quoted = {n for e in exprs for n in QUOTED.findall(expr_text(e))}
    return {f for e in exprs for f in e.dependencies()}, quoted & names()


@st.cache_resource(max_entries=2)
def _topic_index(signature):
    """fact -> topic and parameter/table name -> topic, from the graph of every rule of the knowledge base."""
    rules = [r for r in current() if r.kind == "rule" and r.layer != "company"]
    readers, users, by_fact = {}, {}, {}
    for r in rules:
        by_fact.setdefault(r.produces, []).append(r)
        facts_read, used_names = _deps(r)
        for f in facts_read:
            readers.setdefault(f, set()).add(r.produces)
        for n in used_names:
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
    # theirs), repeated until nothing changes; at a tie, the topic of the reader earliest in the calculation.
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
            first = min((x for x in voters if votes.count(fact_topic[x]) == best), key=lambda x: (depth(x), x))
            pick = fact_topic[first]
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
        name_topic[n] = max(set(votes), key=votes.count) if votes else OTHER_TOPIC
    return fact_topic, name_topic


def topic_of(rec):
    if getattr(rec, "layer", "") == "company":
        return POLICY_TOPIC
    fact_topic, name_topic = _topic_index(signature())
    if rec.kind == "rule":
        return fact_topic.get(rec.produces, OTHER_TOPIC)
    if rec.kind in ("parameter", "table"):
        return name_topic.get(rec.name, OTHER_TOPIC)
    if rec.kind == "fact":
        return fact_topic.get(rec.id, OTHER_TOPIC)
    facts_read, _ = _deps(rec)
    votes = [fact_topic[f] for f in facts_read if f in fact_topic]
    return max(set(votes), key=votes.count) if votes else OTHER_TOPIC


def is_input_convention(rec):
    return rec.id.startswith("REG.INPUT.") or any(s.document == "INPUT-CONVENTION" for s in rec.source)


# Plain names of case-data inputs that have no fact of their own
INPUT_LABELS = {"housing_individual": "company housing", "company_vehicle": "company vehicle",
                "other_benefit": "other benefit in kind", "gift_other": "gift parcel",
                "meal_coupon_field_duty": "meal coupon for field duty", "sports_facility": "sports facility",
                "contract_fixed_income": "fixed income under the contract", "klu": "KLU",
                "tax_id_valid": "valid NPWP/NIK", "other_dtp_incentive": "receives another incentive",
                "jkk_risk_group": "JKK risk group", "ptkp_status": "PTKP status",
                "has_equity_in_employer": "shareholder of the employer",
                "avg_monthly_gross_12m": "average monthly gross over 12 months", "days_present": "days present",
                "months_of_service": "months of service", "thr_holiday": "month of the religious holiday"}


def expr_text(expr):
    return getattr(expr, "text", None) or str(expr)


def readable(expr):
    """An expression with fact names replaced by their labels, for people."""
    text = expr_text(expr)
    text = re.sub(r"param\('([a-z_0-9]+)'\)", lambda m: f"[{fact_label(m.group(1)).lower()}]", text)
    text = re.sub(r"(?:income|benefit|employee|employer|hr|case)\('([a-z_0-9]+)'\)",
                  lambda m: f"[{INPUT_LABELS.get(m.group(1), fact_label(m.group(1)).lower())}]", text)
    text = re.sub(r"(?:in_table|lookup|bracket|progressive)\('([a-z_0-9]+)'",
                  lambda m: f"table '{m.group(1).replace('_', ' ')}'", text)
    text = re.sub(r"\b([a-z][a-z_0-9]{2,})\b(?!\()", lambda m: fact_label(m.group(1)).lower()
                  if m.group(1) in facts() else m.group(1), text)
    for a, b in (("== True", "= yes"), ("!= None", "is set"), ("None", "empty")):
        text = text.replace(a, b)
    return text


# ====================================================================================================================
# Formatting and the engine call
# ====================================================================================================================
def fmt_date(x):
    """1 Jan 2026."""
    return "-" if x is None else f"{x.day} {MON[x.month - 1]} {x.year}"


def money(x):
    """Rp15,000,000 (negative: −Rp...)."""
    if x is None:
        return "-"
    x = Fraction(x)
    return ("−Rp" if x < 0 else "Rp") + f"{abs(int(x)):,}"


def pct(x):
    return "-" if x is None else f"{float(x) * 100:.2f}".rstrip("0").rstrip(".") + "%"


def fmt(fact, v):
    """A value of a fact as text, by the type the knowledge base gives the fact."""
    kind = getattr(facts().get(fact), "fact_type", "money")
    if v is None:
        return "-"
    if kind == "bool" or isinstance(v, bool):
        return "yes" if v else "no"
    if kind == "rate":
        return pct(v)
    if kind == "money":
        return money(v)
    return str(v)


def compute(case, omega=None, knowledge=None):
    """(engine result with trace, None) or (None, error text)."""
    try:
        return evaluate_case(knowledge or kb(), case, omega or TODAY, trace=True), None
    except Exception as e:  # noqa: BLE001 - shown on screen
        return None, f"{type(e).__name__}: {e}"


def value(result, fact, month=0):
    t = (result.trace or {}).get((fact, month))
    return t["value"] if t else None
