"""Experiments E0-E4 as data (skeleton Section VI). run_demo.py prints them; the app draws them."""
import hashlib
import json
from dataclasses import dataclass
from datetime import date
from math import comb

import acquisition
import evaluation as ev
import kg
from reasoner import NOW

HERE = kg.DATA.parent
ENGINE_FILES = [HERE / "reasoner.py"] + [kg.REPO / "engine" / f for f in ("ekspresi.py", "angka.py", "pembulatan.py")]

# Conditions of E2 that the mock can run (skeleton table of baselines and ablations).
CONDITIONS = {
    "Proposed": dict(m=3, gates=acquisition.GATES, selection="consensus"),
    "B3 one candidate, G1-G2": dict(m=1, gates=("G1", "G2"), selection="first"),
    "B4 majority vote, no gates": dict(m=3, gates=(), selection="consensus"),
    "AB3 without G5": dict(m=3, gates=("G1", "G2", "G3", "G4"), selection="consensus"),
    "AB3 without G4": dict(m=3, gates=("G1", "G2", "G3", "G5"), selection="consensus"),
    "AB4 first passing": dict(m=3, gates=acquisition.GATES, selection="first"),
}


def engine_hash():
    return hashlib.sha256(b"".join(p.read_bytes() for p in ENGINE_FILES)).hexdigest()[:12]


@dataclass
class Study:
    kb0: object
    events: list
    counterfactuals: list
    texts: dict
    gold: dict
    gold_before: dict
    gold_after: dict
    kb_gold: object
    cases: list

    def event(self, doc_id):
        return next(e for e in self.events + self.counterfactuals if e["id"] == doc_id)


def prepare():
    kb0 = ev.initial_kb()
    events, counterfactuals, texts, gold = ev.load_corpus()
    before, after, kb_gold = ev.gold_chain(kb0, events, gold)
    for cf in counterfactuals:
        before[cf["id"]] = before[cf["source"]]
        after[cf["id"]] = kg.apply_delta(before[cf["id"]], gold[cf["id"]], cf["issued"])
    return Study(kb0, events, counterfactuals, texts, gold, before, after, kb_gold, ev.evaluation_cases())


# ---------------------------------------------------------------- E0


def e0(s):
    refs = []
    for ref in ev.load_json(kg.DATA / "reference" / "references.json")["references"]:
        w = date.fromisoformat(ref["knowledge_date"]) if "knowledge_date" in ref else NOW
        values, _ = acquisition.safe_compute(s.kb_gold, ref["case"], w)
        got = {k: values.get(k) for k in ref["expected"]}
        refs.append(dict(ref, got=got, match=got == ref["expected"]))
    mutation = {}
    for e in s.events:
        if s.gold[e["id"]]["add"] or s.gold[e["id"]]["tables"]:
            gold_results = ev.score_results(s.gold_after[e["id"]], s.cases)
            mutation[e["id"]] = ev.mutation_score(s.gold_before[e["id"]], s.gold[e["id"]], e, s.cases, gold_results)
    passed = all(r["match"] for r in refs) and all(k == n for k, n, _ in mutation.values())
    return {"references": refs, "mutation": mutation, "passed": passed}


# ---------------------------------------------------------------- E1


def e1(s):
    real = [(e["id"], e["layer"], kg.shacl_check(s.gold_after[e["id"]])[0]) for e in s.events if e["relevant"]]
    unseen = ev.unseen_change_check(s.kb_gold)
    ok = all(got == ex["expected"] for ex, got in unseen)
    return {"real": real, "unseen": unseen, "ra": (int(ok), 1, ev.cp_lower(int(ok), 1))}


# ---------------------------------------------------------------- E2


def pass_at(j, m, c):
    return 1 - comb(m - c, j) / comb(m, j) if m >= j else None


def e2(s, llm, condition="Proposed"):
    """Isolated mode: every document is applied to the gold knowledge base before it."""
    opts = CONDITIONS[condition]
    rows, isolated = [], {}
    for e in s.events + s.counterfactuals:
        kb_before = s.gold_before[e["id"]]
        gold_results = ev.score_results(s.gold_after[e["id"]], s.cases)
        res = acquisition.run(kb_before, e, s.texts[e["id"]], llm, **opts)
        correct, wrong = (ev.score_update(kb_before, res.delta, e, s.cases, gold_results)
                          if res.status in ("applied", "empty") else (False, set()))
        outcome = "abstain" if res.status == "abstain" else ("correct-applied" if correct else "wrong-applied")
        cand = [ev.score_update(kb_before, c.delta, e, s.cases, gold_results)[0] for c in res.checks]
        row = {"document": e["id"], "split": e["split"], "layer": e["layer"], "change_type": e["change_type"],
               "relevant": e["relevant"], "status": res.status, "outcome": outcome, "wrong_tuples": len(wrong),
               "m": len(res.checks), "c": sum(cand), "candidate_correct": cand, "selected": res.selected,
               "reason": res.reason, "gates": [c.gates for c in res.checks], "groups": res.groups, "result": res}
        if e["split"] == "counterfactual":
            orig = [v for v in e["replace"] if v.isdigit()][0]
            row["memorised"] = (sum(orig in json.dumps(c) for c in res.candidates), len(res.candidates), orig)
        rows.append(row)
        isolated[e["id"]] = (res.delta, wrong)
    real = [r for r in rows if r["relevant"] and r["split"] == "test"]
    n = len(real)
    ser = sum(r["outcome"] == "wrong-applied" for r in real)
    car = sum(r["outcome"] == "correct-applied" for r in real)
    distractors = [r for r in rows if not r["relevant"]]
    return {"condition": condition, "rows": rows, "isolated": isolated, "n": n, "ser": ser, "car": car,
            "abs": n - ser - car, "ser_upper": ev.cp_upper(ser, n), "car_lower": ev.cp_lower(car, n),
            "distractor_fp": sum(r["outcome"] != "correct-applied" for r in distractors), "n_distractors": len(distractors),
            "missed": sum(r["status"] == "empty" for r in real)}


def gate_confusion(result):
    """Per gate, with a wrong candidate as the positive class: leakage FN/(TP+FN) and false rejection FP/(FP+TN)."""
    table = {}
    for gate in acquisition.GATES:
        tp = fn = fp = tn = 0
        for row in result["rows"]:
            if not row["relevant"]:
                continue
            for gates, correct in zip(row["gates"], row["candidate_correct"]):
                rejected = gates.get(gate, "pass") != "pass"
                tp += rejected and not correct
                fn += (not rejected) and not correct
                fp += rejected and correct
                tn += (not rejected) and correct
        table[gate] = {"TP": tp, "FN": fn, "FP": fp, "TN": tn,
                       "leakage": fn / (tp + fn) if tp + fn else None,
                       "false_rejection": fp / (fp + tn) if fp + tn else None}
    return table


# ---------------------------------------------------------------- E3


def e3(s, llm, isolated, perfect_reviewer=False):
    rows, kb_sys = ev.replay(s.kb0, s.events, s.texts, s.gold, llm, s.gold_before, s.gold_after, isolated, s.cases,
                             perfect_reviewer=perfect_reviewer)
    return {"rows": rows, "kb_sys": kb_sys, "oar": sum(r["ok"] for r in rows), "n": len(rows),
            "drift": len(rows[-1]["chained_wrong"]), "n_cases": len(s.cases)}


# ---------------------------------------------------------------- E4


def e4(s):
    pairs = []
    for e in [e for e in s.events if e["layer"] == "regulation"]:
        labels = ev.impact_labels(s.gold_before[e["id"]], s.gold_after[e["id"]], s.cases)
        flagged = kg.impacted_policies(s.gold_after[e["id"]], [r["id"] for r in s.gold[e["id"]]["add"]])
        pairs += [{"policy": pid, "event": e["id"], "label": label, "flagged": pid in flagged}
                  for pid, label in labels.items()]
    tp = sum(p["label"] and p["flagged"] for p in pairs)
    fp = sum(p["flagged"] and not p["label"] for p in pairs)
    fn = sum(p["label"] and not p["flagged"] for p in pairs)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    prevalence = sum(p["label"] for p in pairs) / len(pairs) if pairs else 0.0
    return {"pairs": pairs, "precision": precision, "recall": recall, "recall_lower": ev.cp_lower(tp, tp + fn),
            "f2": ev.f_beta(precision, recall), "flag_all_f2": 5 * prevalence / (4 * prevalence + 1), "prevalence": prevalence}
