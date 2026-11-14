r"""Run the acquisition pipeline on events against the gold chain before each of them (isolated mode).

    env\Scripts\python system\tools\run_event.py <RUN> <EVENT>[,<EVENT>...] [--m N] [--model main|second]
                                                [--batch] [--limit USD] [--effort high]

An event list may name groups: test (E01-E13), distractors (P..), dev (D01-D13), fictive (FR..), pkb (test PKB),
synthetic (SP..), counterfactual (CF..). The base is the gold chain up to the update before the event (fictive regulations: the chain prefix
at their date with their background; policies: the full regulation chain). Results go to
experiments/<RUN>/results/<EVENT>.json and the call log to experiments/<RUN>/calls.jsonl. With --batch every round of
LLM calls of all listed events (relevance, drafts, repairs) is sent as one Message Batch at half price; the events
run in parallel threads.
"""
import argparse
import json
import sys
import threading
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from kb_context import base_for  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.pipeline import llm  # noqa: E402
from pph21kbs.pipeline.run import Config, run_document  # noqa: E402

GROUPS = {
    "test": lambda: [e.id for e in corpus.regulation_events() if e.part == "uji"],
    "distractors": lambda: [e.id for e in corpus.regulation_events() if e.part == "pengecoh"],
    "dev": lambda: [e.id for e in corpus.regulation_events() if e.part == "pengembangan"],
    "fictive": lambda: [e.id for e in corpus.fictive_events()],
    "pkb": lambda: [e.id for e in corpus.policy_events() if e.part == "uji"],
    "synthetic": lambda: [e.id for e in corpus.policy_events() if e.part == "sintetis"],
    "counterfactual": lambda: [e.id for e in corpus.counterfactual_events()],
}


def event_ids(spec):
    out = []
    for item in spec.split(","):
        for eid in (GROUPS[item]() if item in GROUPS else [item]):
            if eid not in out:
                out.append(eid)
    return out


def summary_of(res):
    s = {k: res.get(k) for k in ("event", "status", "selected", "groups", "cost_usd")}
    s["candidates"] = [{k: c[k] for k in ("n", "passed", "passed_before_repair", "repaired", "gate_log")}
                       for c in res.get("candidates", [])]
    s["relevance"] = (res.get("relevance") or {}).get("output", {}).get("relevant")
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("events")
    ap.add_argument("--m", type=int, default=5)
    ap.add_argument("--model", choices=["main", "second"], default="main")
    ap.add_argument("--batch", action="store_true")
    ap.add_argument("--effort", default="high", help="effort of the drafts")
    ap.add_argument("--limit", type=float, default=1.0, help="USD limit of this run")
    ap.add_argument("--skip-done", action="store_true", help="skip events that already have a result")
    ap.add_argument("--no-context", action="store_true", help="ablation AB2: vocabulary only, no knowledge base records")
    args = ap.parse_args()
    chain = build_gold.build(check_only=True, side=False)
    ledger = llm.Ledger(args.run, run_limit_usd=args.limit)
    cfg = Config(m=args.m, draft_effort=args.effort, with_context=not args.no_context)
    if args.model == "second":
        client = llm.OpenAIClient(ledger)
    elif args.batch:
        client = llm.AnthropicBatchClient(ledger, log=lambda msg: print(msg, flush=True))
    else:
        client = llm.AnthropicClient(ledger)
    jobs = []
    for eid in event_ids(args.events):
        if args.skip_done and (ledger.dir / "results" / f"{eid}.json").exists():
            continue
        ev = corpus.event(eid)
        base, _ = base_for(ev, chain)
        jobs.append((ev, base))
    results = {}

    def work(ev, base):
        try:
            policies = (ev.document,) if ev.layer == "company" else ()
            if args.batch:
                with client.dispatcher.cpu():
                    results[ev.id] = run_document(ev, base, client, ledger, cfg, run_id=args.run, policies=policies)
            else:
                results[ev.id] = run_document(ev, base, client, ledger, cfg, run_id=args.run, policies=policies)
        except Exception:  # noqa: BLE001 - one event's failure must not stop the others
            results[ev.id] = {"event": ev.id, "status": "crash", "error": traceback.format_exc()[-2000:]}
        finally:
            if args.batch:
                client.dispatcher.leave()
            print(f"{ev.id}: {results[ev.id].get('status')} ({results[ev.id].get('cost_usd', 0)} USD)", flush=True)
            if results[ev.id].get("status") == "crash":
                print(results[ev.id]["error"], flush=True)

    if args.batch:
        for _ in jobs:
            client.dispatcher.enter()
        threads = [threading.Thread(target=work, args=job) for job in jobs]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    else:
        for job in jobs:
            work(*job)
    for eid, res in results.items():
        print(json.dumps(summary_of(res), ensure_ascii=False, default=str)[:3000])
    print("run spent:", ledger.spent_run(), "| total spent (all runs):", llm.spent_total())


if __name__ == "__main__":
    main()
