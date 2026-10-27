r"""Run the acquisition pipeline on one event against the gold chain before it (isolated mode).

    env\Scripts\python system\tools\run_event.py <RUN> <EVENT> [--m N] [--model main|second] [--mock-gold]

The base is the gold chain up to the update before the event (policies: the full regulation chain). Results go to
experiments/<RUN>/results/<EVENT>.json and the call log to experiments/<RUN>/calls.jsonl. --mock-gold feeds the gold
Delta through the mock client (dry run without API cost).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from kb_context import base_for  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.pipeline import llm  # noqa: E402
from pph21kbs.pipeline.run import Config, run_document  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("event")
    ap.add_argument("--m", type=int, default=5)
    ap.add_argument("--model", choices=["main", "second"], default="main")
    ap.add_argument("--limit", type=float, default=1.0, help="USD limit of this run")
    args = ap.parse_args()
    ev = corpus.event(args.event)
    chain = build_gold.build(check_only=True, side=False)
    base, _ = base_for(ev, chain)
    ledger = llm.Ledger(args.run, run_limit_usd=args.limit)
    client = llm.AnthropicClient(ledger) if args.model == "main" else llm.OpenAIClient(ledger)
    policies = (ev.document,) if ev.layer == "company" else ()
    res = run_document(ev, base, client, ledger, Config(m=args.m), run_id=args.run, policies=policies)
    summary = {k: res.get(k) for k in ("event", "status", "selected", "groups", "cost_usd")}
    summary["candidates"] = [{k: c[k] for k in ("n", "passed", "passed_before_repair", "repaired", "gate_log")}
                             for c in res.get("candidates", [])]
    summary["relevance"] = (res.get("relevance") or {}).get("output", {}).get("relevant")
    print(json.dumps(summary, ensure_ascii=False, indent=1, default=str))
    print("total spent so far (all runs):", llm.spent_total())


if __name__ == "__main__":
    main()
