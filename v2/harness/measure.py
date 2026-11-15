"""Measured runs. Nothing here runs without an explicit stage name and the researcher's approval of the costs.

    env\\Scripts\\python -m v2.harness.measure probe        one real call per provider (cost and model check)
    env\\Scripts\\python -m v2.harness.measure maps         document maps (gpt-5.4-mini), once per document, batch
    env\\Scripts\\python -m v2.harness.measure isolated     prospective set and real set (regulations twice), batch
    env\\Scripts\\python -m v2.harness.measure chains       the seven chains, base condition (--direct: no batch)
    env\\Scripts\\python -m v2.harness.measure sonnet       robustness: Sonnet 5.5 on the real set and 20 units
    env\\Scripts\\python -m v2.harness.measure ablation     full text instead of the map on long documents

Every stage writes under v2/work/measured/<stage>/ and skips units already scored, so a stage can resume. Each
provider has a hard spending limit (Ledger total_limit_usd).
"""
import argparse
import json
import threading

from pph21kbs import digest, documents, draft, pipeline  # noqa: E402

from . import WORK, chain, instances, isolated, prospective, units
from .batching import AnthropicBatch, Batching, OpenAIBatch, warm_up
from .replay import Recorded

MEASURED = WORK / "measured"
DRAFTER, MAPPER, ROBUST = "gpt-6.1-sol", "gpt-5.4-mini", "claude-sonnet-5-5"
LIMITS = {"openai": 95.0, "anthropic": 17.0}
SEED_UNITS = 20                    # prospective units for the Sonnet check, stratified by size


def config_measured():
    return pipeline.Config(m=3, repair_rounds=1, relevance_effort="medium", draft_effort="high", fallback="full",
                           use_stored_map=True)


def ledger(stage, provider):
    return draft.Ledger(stage, root=MEASURED / "calls", total_limit_usd=LIMITS[provider])


def client(model, stage, batch=True):
    """A batch client (half price), or a direct client with record and replay (a resumed stage re-reads answers)."""
    if model.startswith("gpt"):
        inner = draft.OpenAIClient(ledger(stage, "openai"), model=model)
        backend = OpenAIBatch(inner.api)
    else:
        inner = draft.AnthropicClient(ledger(stage, "anthropic"), model=model)
        backend = AnthropicBatch(inner.api)
    return Batching(inner, backend) if batch else Recorded(inner)


# ------------------------------------------------------------------------------------------------- stages
def all_documents():
    ids = {d for u in units.regulation_units() for d in u.event.documents}
    ids |= {d + "-UTUH" for u in units.regulation_units() if u.event.part == "distractor" for d in u.event.documents}
    for inst in list(instances.REAL) + instances.fictional():
        ids |= {d.id for d in inst.documents}
    ids |= {s["id"] for s in prospective.specs()}
    return sorted(ids)


def maps(batch=True):
    c = client(MAPPER, "maps", batch)
    todo = [d for d in all_documents() if digest.load(d, MAPPER) is None]
    titles = documents.registry()

    def work(doc):
        with c.worker():
            digest.build(doc, c, title=titles.get(doc, {}).get("title", ""), call_prefix=f"map-{doc}-")
    _threads(work, todo)
    return len(todo)


def _threads(fn, items):
    ts = [threading.Thread(target=fn, args=(x,)) for x in items]
    for t in ts:
        t.start()
    for t in ts:
        t.join()


def _done(out):
    path = out / "scores.jsonl"
    if not path.exists():
        return set()
    return {json.loads(line)["event"] for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def run_units(stage, todo, model=DRAFTER, cfg=None, batch=True):
    out = MEASURED / stage
    done = _done(out)
    todo = [u for u in todo if u.event.id not in done]
    if not todo:
        return 0
    cfg = cfg or config_measured()
    c = client(model, stage, batch)
    warm_up(todo[0].base, todo[0].expected)

    def work(u):
        with c.worker():
            isolated.run([u], c, c.ledger, cfg, f"m-{stage}", out)
    _threads(work, todo)
    return len(todo)


def isolated_stage():
    general = units.general_cases()
    pros = [prospective.unit_of(s, general) for s in prospective.specs()]
    real = units.regulation_units() + units.company_units(list(instances.REAL))
    n = run_units("isolated-prospective", pros)
    n += run_units("isolated-real-1", real)
    n += run_units("isolated-real-2", [u for u in real if u.event.part == "test"])
    return n


def chains_stage(batch=True):
    cfg = config_measured()
    c = client(DRAFTER, "chains", batch)
    out = MEASURED / "chains"
    todo = [x for x in chain.chains() if not (out / f"{x.id}.jsonl").exists()]

    def work(ch):
        with c.worker():
            chain.run(ch, lambda step: c, c.ledger, cfg, "m-chain", out)
    _threads(work, todo)
    return len(todo)


def sonnet_stage():
    general = units.general_cases()
    specs = sorted(prospective.specs(), key=lambda s: (s["size"], s["id"]))
    step = max(1, len(specs) // SEED_UNITS)
    picked = [prospective.unit_of(s, general) for s in specs[::step][:SEED_UNITS]]
    real = units.regulation_units() + units.company_units(list(instances.REAL))
    return run_units("sonnet-real", real, model=ROBUST) + run_units("sonnet-prospective", picked, model=ROBUST)


def ablation_stage():
    long_docs = [u for u in units.regulation_units() + units.company_units(list(instances.REAL))
                 if documents.full(u.event.document).tokens > digest.BUDGET_TOKENS]
    cfg = pipeline.Config(**{**config_measured().__dict__, "use_stored_map": False})
    return run_units("ablation-full-text", long_docs, cfg=cfg)


def probe():
    """One small real call per model: confirms access, the reported model version, and the price."""
    out = []
    for model in (DRAFTER, MAPPER, ROBUST):
        led = draft.Ledger("probe", root=MEASURED / "calls", total_limit_usd=1.0)
        c = draft.OpenAIClient(led, model=model) if model.startswith("gpt") else draft.AnthropicClient(led, model)
        _, parsed, entry = c.complete(system="Return JSON.", prefix=[], user="Return ok = true.",
                                      schema={"type": "object", "properties": {"ok": {"type": "boolean"}},
                                              "required": ["ok"], "additionalProperties": False},
                                      schema_name="probe", effort="low", step="probe", call_id=f"probe-{model}",
                                      max_tokens=200)
        out.append((model, entry["model_reported"], entry["cost_usd"], entry["error"], parsed))
    return out


def spent():
    total = 0.0
    for f in (MEASURED / "calls").glob("*/calls.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                total += json.loads(line).get("cost_usd") or 0.0
            except json.JSONDecodeError:
                continue
    return total


STAGES = {"probe": probe, "maps": maps, "isolated": isolated_stage, "chains": chains_stage, "sonnet": sonnet_stage,
          "ablation": ablation_stage}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=sorted(STAGES))
    ap.add_argument("--direct", action="store_true", help="chains without batch (faster, full price)")
    a = ap.parse_args()
    if a.stage == "chains":
        print(chains_stage(batch=not a.direct))
    else:
        print(STAGES[a.stage]())
    print("spent so far, all measured ledgers: USD", round(spent(), 4))
