r"""Ablation AB1 (skeleton: formalisation from scratch at selected legal states; descriptive case study, RQ2/RQ3).

    env\Scripts\python system\tools\ab1_scratch.py <RUN> [--states 2023-03-01,2024-06-01,2025-06-01] [--m 3]
                                                   [--limit USD] [--score-only]

For each legal state, the knowledge base starts with the fact vocabulary in force at that date only (no rules,
parameters, tables or constraints: without the shared fact names the result could not be compared on S^E). The input
is every document cited by a gold record in force at that date (the pipeline's segment selection, 4,000 tokens per
document), the model and gates are those of the proposed pipeline, and the output is one Delta holding the whole
knowledge base. Scored against the gold chain known at that date:
  A2 at the state   wrong tuples on S^E cases of the state's tax year at omega = the state date;
  history loss      wrong tuples on cases of the previous tax year at the same omega (the bitemporal chain keeps the
                    old rules; a knowledge base built from the documents in force does not).
Writes experiments/<RUN>/results/<STATE>.json and ab1_ringkasan.json.
"""
import argparse
import json
import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from pph21kbs.analysis.evaluate import _obs, se_cases  # noqa: E402
from pph21kbs.corpus import Event  # noqa: E402
from pph21kbs.kb import KnowledgeBase, apply_delta  # noqa: E402
from pph21kbs.kb.delta import UpdateError  # noqa: E402
from pph21kbs.kb.serialize import record_to_json  # noqa: E402
from pph21kbs.pipeline import llm  # noqa: E402
from pph21kbs.pipeline.run import Config, run_document  # noqa: E402
from pph21kbs.text import TEXT_DIR  # noqa: E402


def gold_at(chain, state):
    return build_gold.prefix_at(chain, state.isoformat())


def documents_at(kb, state):
    view = kb.view(state)
    docs = set()
    for r in view.records:
        if (r.valid_from is None or r.valid_from <= state) and (r.valid_until is None or r.valid_until >= state):
            for s in getattr(r, "source", None) or []:
                d = s.get("document") if isinstance(s, dict) else getattr(s, "document", None)
                if d and (TEXT_DIR / d / "segmen.json").exists():
                    docs.add(d)
    return tuple(sorted(docs))


def vocabulary_base(kb, state):
    facts = [record_to_json(f) for f in kb.view(state).facts.values()]
    delta = {"delta_id": f"AB1-VOCAB-{state}", "document": {"id": "AB1-VOCAB", "issued": state.isoformat()},
             "relevant": True, "add": facts, "change": [], "remove": [], "note": "fact vocabulary only"}
    return apply_delta(KnowledgeBase(name="AB1"), delta)


def wrong(kb, gold, cases, omega):
    bad = 0
    for c in cases:
        want = _obs(gold, c, omega)
        try:
            got = _obs(kb, c, omega)
        except Exception:  # noqa: BLE001 - an engine failure is a wrong tuple
            bad += 1
            continue
        if (got[0], got[1]) != (want[0], want[1]):
            bad += 1
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--states", default="2023-03-01,2024-06-01,2025-06-01")
    ap.add_argument("--m", type=int, default=3)
    ap.add_argument("--limit", type=float, default=25.0)
    ap.add_argument("--sample", type=int, default=150)
    ap.add_argument("--score-only", action="store_true")
    args = ap.parse_args()
    out = ROOT / "experiments" / args.run
    chain = build_gold.load_graph()
    ledger = llm.Ledger(args.run, run_limit_usd=args.limit)
    client = None
    test_cases, dev_cases = se_cases(), se_cases(dev=True)
    summary = {}
    for s in args.states.split(","):
        state = date.fromisoformat(s)
        sid = f"AB1-{state.isoformat()}"
        gold = gold_at(chain, state)
        base = vocabulary_base(gold, state)
        docs = documents_at(gold, state)
        ev = Event(sid, "ab1", True, docs, state, None, None, "", "regulation",
                   f"Formalisasi dari nol, keadaan hukum {state}")
        path = out / "results" / f"{sid}.json"
        if args.score_only or path.exists():
            res = json.loads(path.read_text(encoding="utf-8"))
        else:
            if client is None:
                client = llm.AnthropicClient(ledger)
            res = run_document(ev, base, client, ledger, Config(m=args.m, budget_tokens=4000, max_tokens=64000),
                               run_id=args.run)
        row = {"documents": len(docs), "status": res.get("status"), "cost_usd": res.get("cost_usd"),
               "candidates_passed": sum(c["passed"] for c in res.get("candidates", []))}
        kb = base
        if res.get("delta"):
            try:
                kb = apply_delta(base, res["delta"])
            except (UpdateError, ValueError, KeyError) as e:
                row["apply_error"] = str(e)[:200]
        row["elements"] = len(res["delta"]["add"]) if res.get("delta") else 0
        rng = random.Random(sid)
        for label, year in (("state_year", state.year), ("previous_year", state.year - 1)):
            pool = [c for c in list(test_cases.values()) + list(dev_cases.values()) if c["tax_year"] == year
                    and c.get("criterion") in ("combinatorial", "operational", "boundary_ter", "boundary_p17")]
            cases = rng.sample(sorted(pool, key=lambda c: c["case_id"]), min(args.sample, len(pool)))
            row[label] = {"year": year, "cases": len(cases), "wrong": wrong(kb, gold, cases, state)}
        summary[sid] = row
        print(sid, json.dumps(row, default=str), flush=True)
    (out / "ab1_ringkasan.json").write_text(json.dumps(summary, indent=1, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
