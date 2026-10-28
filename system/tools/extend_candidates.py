r"""Sensitivity to m (prareg amendment 1): add candidates to finished results, then choose again by consensus.

    env\Scripts\python system\tools\extend_candidates.py <RUN> <EVENT>[,<EVENT>|group...] --to-m 5 [--limit USD]

For every event, experiments/<RUN>/results/<EVENT>.json is read; candidates n = m+1 .. to-m are drafted with the same
system prompt, prefix (document selection and knowledge base context recomputed from the same base) and relevance
output as the originals, gated with one repair round, and the consensus is taken over the original and the new
candidates (the original candidates are gated again, without LLM calls, to rebuild their behaviour on S^G). New
candidates come after the originals in the tie order. The result goes to experiments/<RUN>-m<to-m>/results/<EVENT>.json
with every candidate; the original run is not touched. Calls are logged under the new run.
"""
import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from kb_context import base_for  # noqa: E402
from run_event import event_ids  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.pipeline import consensus, context, llm, prompts, select  # noqa: E402
from pph21kbs.pipeline.run import Candidate, Config, _evaluate, _finish, _messages, _schema, documents_of  # noqa: E402


def extend(res, ev, base, client, ledger, cfg, run_id, out_dir, policies, to_m):
    docs = documents_of(ev)
    issued = ev.issued
    view = base.view(issued)
    selections = [select.select(d["id"], view, cfg.budget_tokens) for d in docs]
    doc_text = "\n\n".join(select.render(s) for s in selections)
    ctx = context.context_text(view, doc_text, records=cfg.with_context)
    prefix = [doc_text, ctx]
    rel = (res.get("relevance") or {}).get("output") or {}
    out = copy.deepcopy(res)
    out["run"] = run_id
    out["extended_from"] = res.get("run")
    if res.get("status") in ("empty", "budget", "crash") or not res.get("candidates"):
        return _finish(out, ledger, f"{run_id}-{ev.id}-", out_dir)       # nothing drafted in the original
    old = res["candidates"]
    m0 = len(old)
    cands = []
    for c in old:                                  # rebuild behaviour of the original candidates (no LLM)
        k = Candidate(c["n"], c["order"])
        k.llm, k.repaired = c["llm"], c["repaired"]
        k.initial_delta = c.get("initial_delta")
        _evaluate(k, base, ev, issued, rel, cfg, docs, res.get("run"), policies)
        k.passed_before_repair, k.first_gate_log = c["passed_before_repair"], c["first_gate_log"]
        cands.append(k)
    new = [Candidate(n, m0 + i) for i, n in enumerate(range(m0 + 1, to_m + 1))]
    outs = client.complete_many([dict(system=prompts.SYSTEM_DRAFT, prefix=prefix,
                                      user=prompts.draft_user(ev, docs, rel), schema=_schema(), schema_name="delta",
                                      effort=cfg.draft_effort, step="draft", document=ev.document, event=ev.id,
                                      candidate=c.n, order_seed=cfg.seed, call_id=f"{run_id}-{ev.id}-cand{c.n}")
                                 for c in new])
    for c, (_, o, _) in zip(new, outs):
        c.llm = o
        _evaluate(c, base, ev, issued, rel, cfg, docs, run_id, policies)
        c.passed_before_repair, c.first_gate_log = c.passed, dict(c.gate_log)
        c.initial_llm, c.initial_delta = c.llm, c.delta
    todo = [c for c in new if not c.passed and c.llm is not None]
    if todo:
        outs = client.complete_many([dict(system=prompts.SYSTEM_DRAFT, prefix=prefix,
                                          user=prompts.repair_user(ev, docs, c.llm, _messages(c.gate_log) or [c.error]),
                                          schema=_schema(), schema_name="delta", effort=cfg.draft_effort, step="repair",
                                          document=ev.document, event=ev.id, candidate=c.n, order_seed=cfg.seed,
                                          call_id=f"{run_id}-{ev.id}-cand{c.n}-rep1") for c in todo])
        for c, (_, o2, _) in zip(todo, outs):
            if o2 is not None:
                c.llm, c.repaired = o2, True
                _evaluate(c, base, ev, issued, rel, cfg, docs, run_id, policies)
    allc = cands + new
    order = [c.n for c in sorted(allc, key=lambda c: c.order)]
    passing = {c.n: c._k2_sg for c in allc if c.passed}
    sel, groups, status = consensus.choose(passing, [n for n in order if n in passing])
    out.update(groups=groups, selected=sel, status=status,
               delta=next((c.delta for c in allc if c.n == sel), None) if sel is not None else None)
    out["candidates"] = [{"n": c.n, "order": c.order, "passed": c.passed, "passed_before_repair": c.passed_before_repair,
                          "repaired": c.repaired, "gate_log": c.gate_log, "first_gate_log": c.first_gate_log,
                          "sg_size": c.sg_size, "error": c.error, "llm": c.llm, "delta": c.delta,
                          "initial_delta": c.initial_delta if c.repaired else None} for c in allc]
    return _finish(out, ledger, f"{run_id}-{ev.id}-", out_dir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("events")
    ap.add_argument("--to-m", type=int, default=5)
    ap.add_argument("--limit", type=float, default=10.0)
    args = ap.parse_args()
    new_run = f"{args.run}-m{args.to_m}"
    chain = build_gold.build(check_only=True, side=False)
    ledger = llm.Ledger(new_run, run_limit_usd=args.limit)
    client = llm.AnthropicClient(ledger)
    for eid in event_ids(args.events):
        path = ROOT / "experiments" / args.run / "results" / f"{eid}.json"
        if not path.exists():
            continue
        res = json.loads(path.read_text(encoding="utf-8"))
        ev = corpus.event(eid)
        base, _ = base_for(ev, chain)
        policies = (ev.document,) if ev.layer == "company" else ()
        out = extend(res, ev, base, client, ledger, Config(), new_run, ledger.dir / "results", policies, args.to_m)
        print(f"{eid}: {res.get('status')} -> {out.get('status')} ({out.get('cost_usd')} USD)", flush=True)
    print("run spent:", ledger.spent_run(), "| anthropic total:", llm.spent_total(provider="anthropic"))


if __name__ == "__main__":
    main()
