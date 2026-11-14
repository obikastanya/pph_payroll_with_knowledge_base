"""LLM-assisted incremental knowledge acquisition (skeleton Section V, acquisition pipeline figure).

Steps: relevance judgement with a quote, context from the graph, m candidates, gates G1-G5 with a repair round,
behavioural-consensus selection or abstain, then an impact report for the reviewer.
The pipeline never reads S^E or any gold Delta.
"""
import re
from dataclasses import dataclass, field
from datetime import date, timedelta

import kg
from reasoner import NOW, OUTPUTS, ReasoningError, compute, dependencies

M_CANDIDATES = 3
MAX_REPAIR_ROUNDS = 1
GATES = ("G1", "G2", "G3", "G4", "G5")
GATE_STATUSES = ("TK/1", "K/1", "K/3")


def _norm(text):
    return " ".join(text.split())


def quote_found(quote, text):
    return bool(quote) and _norm(quote) in _norm(text)


def _date(s):
    return date.fromisoformat(s)


def shift_month(d, n):
    m = d.month - 1 + n
    return date(d.year + m // 12, m % 12 + 1, 1)


def segment(text):
    """Step 1: cut a document into citable units (articles). The full system also handles PDF layout and annexes."""
    parts = re.split(r"\n\s*\n", text.strip())
    out = []
    for p in parts:
        m = re.match(r"((?:Pasal|Lampiran)[^:]*):\s*(.*)", p, re.S)
        out.append((m.group(1), _norm(m.group(2))) if m else ("Preamble", _norm(p)))
    return out


def effective_date(delta):
    dates = [r["valid_from"] for r in delta.get("add", [])] + [t["valid_from"] for t in delta.get("tables", [])]
    return min(map(_date, dates)) if dates else None


def case_key(case, knowledge_date):
    return tuple(sorted(case.items())) + (("knowledge_date", knowledge_date.isoformat()),)


def safe_compute(g, case, knowledge_date):
    try:
        r = compute(g, case, knowledge_date)
        return r.values, r.conflicts
    except (ReasoningError, ValueError, TypeError) as e:
        return {"ERROR": str(e)}, frozenset()


def run_cases(g, cases):
    return {case_key(c, w): safe_compute(g, c, w) for c, w in cases}


def _numbers(delta):
    """Numbers mentioned by a candidate: literals in expressions and explicit table bounds."""
    numbers = set()
    for r in delta.get("add", []):
        for text in (r.get("condition"), r.get("expression")):
            numbers |= {int(x) for x in re.findall(r"\d{6,}", text or "")}
    for t in delta.get("tables", []):
        for row in t.get("rows", []):
            numbers |= {v for v in (row.get("lower"), row.get("upper")) if v}
    return numbers


def gate_cases(candidates, event):
    """S^G, generated automatically: cases around the numbers and dates the candidates mention, before and after the
    effective date, with current knowledge and with knowledge as of the day before the document was issued."""
    salaries = {6_000_007, 8_000_013}
    for d in candidates:
        for x in _numbers(d):
            salaries |= {x - 13, x - 7, x + 7, x + 13}
    salaries = sorted(s for s in salaries if 0 < s <= 30_000_000)
    months = set()
    for d in candidates:
        start = effective_date(d)
        if start:
            months |= {shift_month(start, -1), start, shift_month(start, 2)}
    knowledge = (NOW, _date(event["issued"]) - timedelta(days=1))
    cases = []
    for i, s in enumerate(salaries):
        for j, t in enumerate(sorted(months)):
            case = {"ptkp_status": GATE_STATUSES[(i + j) % 3], "salary": s, "allowance": 0,
                    "overtime": 700_000 * ((i + j) % 2), "dtp_sector": (i + j) % 2 == 0, "year": t.year, "month": t.month}
            cases.extend((case, w) for w in knowledge)
    return cases


@dataclass
class Check:
    number: int
    delta: dict
    gates: dict = field(default_factory=dict)
    kb: object = None
    signature: tuple = None
    new_conflicts: list = field(default_factory=list)
    required: tuple = GATES

    @property
    def passed(self):
        """Passed every required gate. All gates are still evaluated, so ablations can report what each one would catch."""
        return self.kb is not None and all(self.gates.get(g) == "pass" for g in self.required)


def check_candidate(kb_old, delta, event, text, cases, old_results, number, required=GATES):
    c = Check(number, delta, required=required)
    try:
        c.kb = kg.apply_delta(kb_old, delta, event["issued"])
    except kg.UpdateError as e:
        c.gates["G1"] = f"fail: {e}"
        return c
    conforms, _ = kg.shacl_check(c.kb)
    c.gates["G1"] = "pass" if conforms else "fail: graph does not conform to the SHACL shapes"

    sources = [x.get("source", {}) for x in delta.get("add", []) + delta.get("tables", [])]
    missing = [s.get("quote") for s in sources if not quote_found(s.get("quote"), text)]
    c.gates["G2"] = "pass" if not missing else f"fail: quote not found in document: {missing[0]!r}"

    produced = {str(o) for o in c.kb.objects(None, kg.TAX.name)}
    unknown = [f for r in delta.get("add", []) for f in dependencies(r.get("condition"), r["expression"]) if f not in produced]
    c.gates["G3"] = "pass" if not unknown else f"fail: unknown facts {unknown}"
    before = set(kg.static_conflicts(kb_old))
    c.new_conflicts = [x for x in kg.static_conflicts(c.kb) if x not in before]
    c.gates["G3 report"] = (f"conflict with a mandatory rule, reported (A4): {c.new_conflicts}" if c.new_conflicts
                            else "no new conflict")

    new_results = run_cases(c.kb, cases)
    start = effective_date(delta)
    earlier = [case_key(k, w) for k, w in cases
               if date(k["year"], k["month"], 1) < start or w < _date(event["issued"])]
    changed = [x for x in earlier if new_results[x] != old_results[x]]
    c.gates["G4"] = "pass" if not changed else f"fail: {len(changed)} results before the effective date changed"

    no_effect = []
    for r in delta.get("add", []):
        without = dict(delta, add=[x for x in delta["add"] if x is not r])
        try:
            results_without = run_cases(kg.apply_delta(kb_old, without, event["issued"]), cases)
        except kg.UpdateError:
            continue
        has_effect = any(new_results[x] != results_without[x] for x in new_results)
        reported = any(r["id"] in x for x in c.new_conflicts)
        if not (has_effect or reported):
            no_effect.append(r["id"])
    c.gates["G5"] = "pass" if not no_effect else f"fail: rules without effect {no_effect}"

    c.signature = tuple((tuple(v.get(f) for f in OUTPUTS) if "ERROR" not in v else ("ERROR",), conf)
                        for v, conf in (new_results[x] for x in sorted(new_results)))
    return c


@dataclass
class PipelineResult:
    document: str
    status: str                 # "applied", "empty", or "abstain"
    kb: object
    delta: dict = None
    relevance: dict = None
    candidates: list = field(default_factory=list)
    checks: list = field(default_factory=list)
    selected: int = None
    impacted: list = field(default_factory=list)
    reason: str = ""
    gate_cases: list = field(default_factory=list)
    groups: list = field(default_factory=list)   # candidate numbers grouped by identical behaviour on S^G


def run(kb, event, text, llm, m=M_CANDIDATES, gates=GATES, selection="consensus"):
    """One acquisition step for one document. No human reviewer: the selected candidate is applied directly.
    gates and selection define the condition: the proposed method uses every gate and behavioural consensus;
    B3 is m=1 with G1-G2 and 'first'; B4 is m candidates, no gates, and a majority vote ('consensus' over all)."""
    doc_id = event["id"]
    relevance = llm.judge_relevance(doc_id, text)
    if not quote_found(relevance.get("quote"), text):
        return PipelineResult(doc_id, "abstain", kb, relevance=relevance, reason="relevance quote not found in document")
    if not relevance["relevant"]:
        return PipelineResult(doc_id, "empty", kb, delta={"add": [], "tables": []}, relevance=relevance,
                              reason="judged not relevant")

    candidates = llm.draft_candidates(doc_id, text, kg.known_rules(kb), m)
    cases = gate_cases(candidates, event)
    old_results = run_cases(kb, cases)
    checks = []
    for i, d in enumerate(candidates, 1):
        c = check_candidate(kb, d, event, text, cases, old_results, i, gates)
        for _ in range(MAX_REPAIR_ROUNDS if gates else 0):
            if c.passed:
                break
            repaired = llm.repair(doc_id, d, c.gates)
            if repaired is None:
                c.gates["repair"] = "no repair offered by the LLM"
                break
            c = check_candidate(kb, repaired, event, text, cases, old_results, i, gates)
        checks.append(c)

    result = PipelineResult(doc_id, "abstain", kb, relevance=relevance, candidates=candidates, checks=checks,
                            gate_cases=cases)
    passed = [c for c in checks if c.passed]
    if not passed:
        result.reason = "no candidate passed every gate"
        return result
    groups = {}
    for c in passed:
        groups.setdefault(c.signature, []).append(c)
    result.groups = [[c.number for c in grp] for grp in groups.values()]
    if selection == "first":
        chosen = passed[0]
        result.reason = f"first of {len(passed)} passing candidates"
    else:
        largest = max(groups.values(), key=len)
        chosen = largest[0]
        result.reason = f"consensus of {len(largest)} out of {len(passed)} passing candidates"
    result.status, result.kb, result.delta, result.selected = "applied", chosen.kb, chosen.delta, chosen.number
    result.impacted = sorted(kg.impacted_policies(chosen.kb, [r["id"] for r in chosen.delta.get("add", [])]))
    return result
