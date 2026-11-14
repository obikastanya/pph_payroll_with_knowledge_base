r"""Development runs of the acquisition pipeline with blind Claude Code subagents in place of the API (no API cost).

    env\Scripts\python system\tools\run_subagent.py <RUN> <EVENT>[,<EVENT>...] --exchange DIR [--m N]

Same isolated mode and event groups as run_event.py. Every LLM call becomes <DIR>/<call_id>.req.md plus a schema
file; the run waits for <DIR>/<call_id>.resp.json, written by a subagent that is given only those two files. The
events run in parallel threads, so each round (relevance, drafts, repairs) of all events is pending at the same time.
Results are for designing the pipeline only; reported results come from the API runs.
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
from run_event import event_ids, summary_of  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("events")
    ap.add_argument("--exchange", required=True)
    ap.add_argument("--m", type=int, default=3)
    ap.add_argument("--skip-done", action="store_true")
    ap.add_argument("--v2", action="store_true", help="pipeline v2: case inputs, guidance, G5 date warning, self-check")
    ap.add_argument("--no-review", action="store_true", help="v2 without the self-check round")
    args = ap.parse_args()
    chain = build_gold.build(check_only=True, side=False)
    ledger = llm.Ledger(args.run)
    client = llm.FileClient(ledger, args.exchange)
    cfg = Config.v2(m=args.m) if args.v2 else Config(m=args.m)
    if args.no_review:
        cfg.review = False
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
            with client.hold():
                results[ev.id] = run_document(ev, base, client, ledger, cfg, run_id=args.run, policies=policies)
        except Exception:  # noqa: BLE001
            results[ev.id] = {"event": ev.id, "status": "crash", "error": traceback.format_exc()[-2000:]}
        print(f"DONE {ev.id}: {results[ev.id].get('status')}", flush=True)
        if results[ev.id].get("status") == "crash":
            print(results[ev.id]["error"], flush=True)

    threads = [threading.Thread(target=work, args=job) for job in jobs]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for res in results.values():
        print(json.dumps(summary_of(res), ensure_ascii=False, default=str)[:3000], flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
