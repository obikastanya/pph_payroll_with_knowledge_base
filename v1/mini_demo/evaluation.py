"""Mini evaluation (skeleton Section VI): corpus, gold chain, S^E, scoring, metrics, and exact confidence bounds."""
import copy
import json
import re
from datetime import date
from decimal import Decimal
from math import comb

import acquisition
import kg
from acquisition import run_cases, safe_compute, shift_month
from reasoner import NOW, OUTPUTS


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- corpus and gold


def load_corpus():
    """Events, document texts, gold Deltas, and counterfactual variants derived automatically from their source."""
    data = load_json(kg.DATA / "corpus" / "events.json")
    events = data["events"]
    texts = {e["id"]: (kg.DATA / "corpus" / "documents" / e["document"]).read_text(encoding="utf-8") for e in events}
    gold = {e["id"]: load_json(kg.DATA / "gold" / f"{e['id']}.json") for e in events}
    counterfactuals = []
    for cf in data["counterfactuals"]:
        source = next(e for e in events if e["id"] == cf["source"])
        text, delta = texts[cf["source"]], json.dumps(gold[cf["source"]])
        for old, new in cf["replace"].items():
            text, delta = text.replace(old, new), delta.replace(old, new)
        texts[cf["id"]], gold[cf["id"]] = text, json.loads(delta)
        counterfactuals.append(dict(source, id=cf["id"], source=cf["source"], title=source["title"] + " (counterfactual)",
                                    split="counterfactual", replace=cf["replace"]))
    return events, counterfactuals, texts, gold


def initial_kb():
    delta = load_json(kg.DATA / "initial_kb.json")
    return kg.apply_delta(kg.empty_graph(), delta, delta["recorded_on"])


def gold_chain(kb0, events, gold):
    """K*_0, K*_1, ..., K*_N: the gold knowledge base before and after every event, in issue order."""
    before, after, kb = {}, {}, kb0
    for e in events:
        before[e["id"]] = kb
        kb = kg.apply_delta(kb, gold[e["id"]], e["issued"])
        after[e["id"]] = kb
    return before, after, kb


# ---------------------------------------------------------------- test space S^E

SALARIES = (5_400_000, 5_400_001, 9_999_999, 10_000_000, 10_000_001, 10_050_000, 10_050_001)
PERIODS = ((2023, 6), (2024, 6), (2024, 8), (2025, 1), (2025, 6))


def evaluation_cases():
    """S^E: boundary values of TER layer A, of Article 17 (salary 10,000,000 gives taxable income exactly 60,000,000 for
    TK/0 in 2023), and of the DTP threshold, across periods; plus cases with overtime and cases computed with past
    knowledge. The full study generates constrained 2-way combinations over all dimensions and every layer boundary."""
    cases = []
    for status in ("TK/0", "K/0"):
        for s in SALARIES:
            for year, month in PERIODS:
                cases.append(({"ptkp_status": status, "salary": s, "allowance": 0, "overtime": 0,
                               "dtp_sector": year == 2025, "year": year, "month": month}, NOW))
    for year, month in ((2023, 6), (2024, 6), (2024, 8)):
        cases.append(({"ptkp_status": "TK/0", "salary": 9_500_000, "allowance": 0, "overtime": 500_000,
                       "dtp_sector": False, "year": year, "month": month}, NOW))
    base = {"ptkp_status": "TK/0", "salary": 10_000_000, "allowance": 0, "overtime": 0}
    cases.append((dict(base, dtp_sector=True, year=2025, month=1), date(2025, 1, 31)))
    cases.append((dict(base, dtp_sector=False, year=2024, month=6), date(2023, 12, 1)))
    return cases


def score_results(g, cases):
    """Outputs and reported conflicts per tuple: the behaviour that is compared, not the shape of the rules."""
    out = {}
    for key, (values, conflicts) in run_cases(g, cases).items():
        out[key] = (("ERROR",) if "ERROR" in values else tuple(values.get(f) for f in OUTPUTS), conflicts)
    return out


def wrong_tuples(results, gold_results):
    return {k for k in gold_results if results.get(k) != gold_results[k]}


# ---------------------------------------------------------------- statistics


def _binom_cdf(k, n, p):
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def cp_upper(failures, n, alpha=0.05):
    """One-sided exact (Clopper-Pearson) upper bound of a failure rate."""
    if n == 0 or failures >= n:
        return 1.0
    lo, hi = failures / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _binom_cdf(failures, n, mid) > alpha else (lo, mid)
    return hi


def cp_lower(successes, n, alpha=0.05):
    return 0.0 if successes == 0 else 1 - cp_upper(n - successes, n, alpha)


def f_beta(precision, recall, beta=2):
    if precision + recall == 0:
        return 0.0
    return (1 + beta ** 2) * precision * recall / (beta ** 2 * precision + recall)


# ---------------------------------------------------------------- instrument adequacy


def mutants(delta):
    """Mutation operators on a gold Delta: shift the effective date, change a numeric literal, change one table rate."""
    out = []
    for i, r in enumerate(delta.get("add", [])):
        m = copy.deepcopy(delta)
        m["add"][i]["valid_from"] = shift_month(date.fromisoformat(r["valid_from"]), 1).isoformat()
        out.append((f"{r['id']}: effective date shifted by one month", m))
        numbers = re.findall(r"\d{6,}", r["expression"])
        if numbers:
            m = copy.deepcopy(delta)
            m["add"][i]["expression"] = r["expression"].replace(numbers[0], str(int(numbers[0]) * 9 // 10), 1)
            out.append((f"{r['id']}: literal {numbers[0]} changed", m))
    for i, t in enumerate(delta.get("tables", [])):
        if "extract" in t and "key" not in t["extract"]:
            m = copy.deepcopy(delta)
            rows = kg.extract_table(m["tables"][i].pop("extract"))
            row = rows[len(rows) // 4]
            row["value"] = str(Decimal(row["value"]) + Decimal("0.25"))
            m["tables"][i]["rows"] = rows
            out.append((f"table {t['name']}: rate of layer ({row['lower']}, {row['upper']}] changed", m))
    return out


def mutation_score(kb_before, delta, event, cases, gold_results):
    killed, survivors = 0, []
    for label, m in mutants(delta):
        results = score_results(kg.apply_delta(kb_before, m, event["issued"]), cases)
        if wrong_tuples(results, gold_results):
            killed += 1
        else:
            survivors.append(label)
    return killed, killed + len(survivors), survivors


# ---------------------------------------------------------------- RQ1: representational adaptability


def unseen_change_check(kb_final):
    """Apply the researcher's Delta for the unseen change U1 and reproduce the collaborator's worked examples."""
    delta = load_json(kg.DATA / "hidden" / "U1_delta_researcher.json")
    examples = load_json(kg.DATA / "hidden" / "U1_examples.json")["examples"]
    kb = kg.apply_delta(kb_final, delta, "2026-01-01")
    rows = []
    for ex in examples:
        values, _ = safe_compute(kb, ex["case"], NOW)
        rows.append((ex, {k: values.get(k) for k in ex["expected"]}))
    return rows


# ---------------------------------------------------------------- RQ2 and RQ3


def score_update(kb_before, delta, event, cases, gold_results):
    """A Delta is correct if K_(n-1) (+) Delta reproduces K*_n on every tuple of S^E (conditions A2, A3_t, A4)."""
    if delta is None:
        return False, set()
    wrong = wrong_tuples(score_results(kg.apply_delta(kb_before, delta, event["issued"]), cases), gold_results)
    return not wrong, wrong


def edit_operations(selected, final):
    """Correction effort (RQ2 diagnostic): attribute edits from the selected Delta to the final one, with elements aligned
    by id (the full study aligns by Hungarian matching). Returns (edits, operations needed to write `final` from empty)."""
    def elements(d):
        out = {("rule", r["id"]): r for r in d.get("add", [])}
        return out | {("table", t["name"], t["valid_from"]): t for t in d.get("tables", [])}

    a, b = elements(selected or {}), elements(final)
    same = lambda x, y: json.dumps(x, sort_keys=True) == json.dumps(y, sort_keys=True)  # noqa: E731
    edits = sum(not same(a.get(k, {}).get(f), b.get(k, {}).get(f))
                for k in a.keys() | b.keys() for f in a.get(k, {}).keys() | b.get(k, {}).keys())
    return edits, sum(len(e) for e in b.values())


def replay(kb0, events, texts, gold, llm, gold_before, gold_after, isolated_deltas, cases, perfect_reviewer=False):
    """Chained mode (RQ3): each event is applied to the system's own previous knowledge base.
    Abstain variants: keep the old knowledge base, or let a perfect reviewer insert the gold Delta."""
    rows, kb_sys = [], kb0
    for e in events:
        gold_prev = score_results(gold_before[e["id"]], cases)
        gold_now = score_results(gold_after[e["id"]], cases)
        inherited = wrong_tuples(score_results(kb_sys, cases), gold_prev)
        result = acquisition.run(kb_sys, e, texts[e["id"]], llm)
        if result.status == "abstain" and perfect_reviewer:
            new_kb = kg.apply_delta(kb_sys, gold[e["id"]], e["issued"])
        else:
            new_kb = result.kb
        chained_wrong = wrong_tuples(score_results(new_kb, cases), gold_now)
        isolated_wrong = isolated_deltas[e["id"]][1]
        delta_iso = isolated_deltas[e["id"]][0]
        mechanical = (wrong_tuples(score_results(kg.apply_delta(kb_sys, delta_iso, e["issued"]), cases), gold_now)
                      if delta_iso is not None else chained_wrong)
        new_errors = (chained_wrong & isolated_wrong) - inherited
        induced = chained_wrong - (isolated_wrong | inherited)
        induced_mech = mechanical - (isolated_wrong | inherited)
        rows.append({"event": e["id"], "status": result.status, "inherited": inherited, "new": new_errors,
                     "induced": induced, "induced_mechanical": induced_mech, "chained_wrong": chained_wrong,
                     "ok": not (chained_wrong - inherited),
                     "knowledge_isolation": knowledge_isolation(kb_sys, new_kb, e, cases)})
        kb_sys = new_kb
    return rows, kb_sys


def knowledge_isolation(kb_before, kb_after, event, cases):
    """Invariant A3_omega: results computed with knowledge before the issue date do not change."""
    issued = date.fromisoformat(event["issued"])
    early = [(c, w) for c, w in cases if w < issued]
    return score_results(kb_before, early) == score_results(kb_after, early), len(early)


# ---------------------------------------------------------------- RQ4: impact labels


def policy_ids(g):
    q = kg.PREFIX + "SELECT ?id ?name WHERE { ?p tax:layer tax:CompanyLayer ; tax:id ?id ; tax:produces ?f . ?f tax:name ?name }"
    return {str(r.id): str(r.name) for r in g.query(q)}


def impact_labels(kb_before, kb_after, cases):
    """Ground truth from execution: a policy is impacted if the value of its fact or its reported conflicts change."""
    labels = {}
    before = run_cases(kb_before, cases)
    after = run_cases(kb_after, cases)
    for pid, fact in policy_ids(kb_after).items():
        changed = any(before[k][0].get(fact) != after[k][0].get(fact)
                      or {c for c in before[k][1] if c[1] == pid} != {c for c in after[k][1] if c[1] == pid}
                      for k in after)
        labels[pid] = changed
    return labels
