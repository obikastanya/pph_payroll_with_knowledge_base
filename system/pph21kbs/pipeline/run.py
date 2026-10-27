"""The acquisition pipeline for one document (akuisisi.md 3): selection, relevance, m candidates, gates G1-G5 with one
repair round, behavioural consensus, result.

run_document() never reads the gold, S^E, or expected values (checked by test_pipeline_isolation). Everything it
does is written to experiments/<run>/: the call log, prompts, candidate Deltas, gate logs, and the result record
(format_data.md 7), so that B3/B4/AB3/AB4 can be recomputed from the same candidates without calling the LLM again.
"""
import json
import random
from dataclasses import dataclass, field
from datetime import date

from ..kb import apply_delta
from ..text import registry
from . import consensus, context, gates, prompts, select, sg
from .convert import ConversionError, to_delta
from .llm import BudgetExceeded

DELTA_LLM_SCHEMA = None


def _schema():
    global DELTA_LLM_SCHEMA
    if DELTA_LLM_SCHEMA is None:
        from ..kb.delta import schema
        DELTA_LLM_SCHEMA = schema("delta_llm")
    return DELTA_LLM_SCHEMA


@dataclass
class Config:
    m: int = 5
    repair_rounds: int = 1
    seed: int = 20261027
    relevance_effort: str = "medium"
    draft_effort: str = "high"
    with_context: bool = True          # False = ablation AB2 (vocabulary only)
    gates: tuple = ("G1", "G2", "G3", "G4", "G5")
    budget_tokens: int = select.TOKEN_BUDGET
    policy_omega: date = date(2026, 10, 27)   # knowledge date of the regulation chain policies are acquired against


@dataclass
class Candidate:
    n: int
    order: int
    llm: dict | None = None
    delta: dict | None = None
    passed: bool = False
    passed_before_repair: bool = False
    repaired: bool = False
    gate_log: dict = field(default_factory=dict)
    first_gate_log: dict = field(default_factory=dict)
    initial_llm: dict | None = None        # output before repair (B4 votes over the initial candidates)
    initial_delta: dict | None = None
    sg_size: int = 0
    error: str = ""


def documents_of(event):
    reg = registry()
    return [{"id": d, "title": reg[d]["title"], "issued": reg[d]["issued"]} for d in event.documents]


def relevance_quotes_ok(rel, event):
    for q in rel.get("quotes") or []:
        if not any(gates.find_quote(d, q["quote"]) for d in event.documents) or len(q["quote"]) < gates.MIN_QUOTE:
            return False
    return bool(rel.get("quotes"))


def check(base, delta, event, issued, relevance, cfg, policies=()):
    """Run the gates in order; stop at the first failure. Returns (passed, log, K', S^G)."""
    log = {}
    r1, kb2 = gates.g1(base, delta)
    log["G1"] = r1.summary()
    if not r1.passed:
        return False, log, None, None
    if "G2" in cfg.gates:
        r2 = gates.g2(base, delta, list(event.documents), issued)
        log["G2"] = r2.summary()
        if not r2.passed:
            return False, log, kb2, None
    if "G3" in cfg.gates:
        r3 = gates.g3(kb2, cfg.policy_omega if event.layer == "company" else issued, policies)
        log["G3"] = r3.summary()
        log["G3_warnings"] = r3.warnings[:20]
        if not r3.passed:
            return False, log, kb2, None
    starts, s_d = gates.effect_start(base, delta)
    company = event.layer == "company"
    sgs = sg.generate(base, kb2, delta, s_d, issued, relevance, cfg.seed, starts=starts,
                      omega=cfg.policy_omega if company else None)
    extra = [e["id"] for e in delta["add"] if e["kind"] == "fact"] if company else []
    ev = gates.Evaluations(sgs.cases, extra)
    if "G4" in cfg.gates:
        r4 = gates.g4(base, kb2, sgs, ev, s_d, company=company)
        log["G4"] = r4.summary()
        if not r4.passed:
            return False, log, kb2, sgs
    if "G5" in cfg.gates:
        r5 = gates.g5(base, kb2, delta, sgs, ev, starts, relevance)
        log["G5"] = r5.summary()
        if not r5.passed:
            return False, log, kb2, sgs
    return True, log, kb2, sgs


def _messages(log):
    return [f"{g}: {v[6:]}" for g, v in log.items() if isinstance(v, str) and v.startswith("fail")]


def run_document(event, base, client, ledger, cfg=None, run_id="dev", out_dir=None, policies=()):
    """Acquire one document against base (K). Returns the result record."""
    cfg = cfg or Config()
    docs = documents_of(event)
    issued = event.issued
    view = base.view(issued)
    selections = [select.select(d["id"], view, cfg.budget_tokens) for d in docs]
    doc_text = "\n\n".join(select.render(s) for s in selections)
    ctx = context.context_text(view, doc_text, records=cfg.with_context)
    result = {"run": run_id, "event": event.id, "condition": "proposed", "documents": [d["id"] for d in docs],
              "selection": {s.document: {"tokens": s.tokens, "dropped": s.dropped} for s in selections},
              "candidates": [], "groups": [], "selected": None, "status": None, "delta": None, "cost_usd": 0.0}
    spent0 = ledger.spent_run()
    try:
        # relevance
        _, rel, entry = client.complete(system=prompts.SYSTEM_RELEVANCE, prefix=[doc_text],
                                        user=prompts.relevance_user(event, docs), schema=prompts.RELEVANCE_SCHEMA,
                                        schema_name="relevance", effort=cfg.relevance_effort, step="relevance",
                                        document=event.document, event=event.id, call_id=f"{run_id}-{event.id}-rel")
        rel = rel or {}
        result["relevance"] = {"output": rel, "quotes_ok": relevance_quotes_ok(rel, event) if rel else False}
        if rel and rel.get("relevant") is False:
            if result["relevance"]["quotes_ok"]:
                result["status"] = "empty"
                result["delta"] = {"delta_id": f"{run_id}-{event.id}", "event_id": event.id, "document": docs[0],
                                   "relevant": False, "add": [], "change": [], "remove": [], "note": rel.get("reason", "")}
            else:
                result["status"] = "abstain"
            return _finish(result, ledger, spent0, out_dir)
        # candidates
        rng = random.Random(cfg.seed + hash(event.id) % 1000)
        order = list(range(1, cfg.m + 1))
        rng.shuffle(order)
        prefix = [doc_text, ctx]
        cands = []
        for n in range(1, cfg.m + 1):
            c = Candidate(n, order.index(n))
            _, out, entry = client.complete(system=prompts.SYSTEM_DRAFT, prefix=prefix,
                                            user=prompts.draft_user(event, docs, rel), schema=_schema(),
                                            schema_name="delta", effort=cfg.draft_effort, step="draft",
                                            document=event.document, event=event.id, candidate=n,
                                            order_seed=cfg.seed, call_id=f"{run_id}-{event.id}-cand{n}")
            c.llm = out
            _evaluate(c, base, event, issued, rel, cfg, docs, run_id, policies)
            c.passed_before_repair = c.passed
            c.first_gate_log = dict(c.gate_log)
            c.initial_llm, c.initial_delta = c.llm, c.delta
            for r in range(cfg.repair_rounds if not c.passed and c.llm is not None else 0):
                msgs = _messages(c.gate_log) or [c.error]
                # same system prompt and prefix as the drafts, so the cached prefix is read, not written again
                _, out2, _ = client.complete(system=prompts.SYSTEM_DRAFT,
                                             prefix=prefix, user=prompts.repair_user(event, docs, c.llm, msgs),
                                             schema=_schema(), schema_name="delta", effort=cfg.draft_effort,
                                             step="repair", document=event.document, event=event.id, candidate=n,
                                             order_seed=cfg.seed, call_id=f"{run_id}-{event.id}-cand{n}-rep{r + 1}")
                if out2 is not None:
                    c.llm, c.repaired = out2, True
                    _evaluate(c, base, event, issued, rel, cfg, docs, run_id, policies)
            cands.append(c)
        passing = {c.n: c._k2_sg for c in cands if c.passed}
        sel, groups, status = consensus.choose(passing, sorted(passing, key=lambda n: order.index(n)))
        result.update(groups=groups, selected=sel, status=status)
        if sel is not None:
            result["delta"] = next(c.delta for c in cands if c.n == sel)
        result["candidates"] = [{"n": c.n, "order": c.order, "passed": c.passed,
                                 "passed_before_repair": c.passed_before_repair, "repaired": c.repaired,
                                 "gate_log": c.gate_log, "first_gate_log": c.first_gate_log, "sg_size": c.sg_size,
                                 "error": c.error, "llm": c.llm, "delta": c.delta,
                                 "initial_delta": c.initial_delta if c.repaired else None} for c in cands]
    except BudgetExceeded as e:
        result["status"] = "budget"
        result["error"] = str(e)
    return _finish(result, ledger, spent0, out_dir)


def _evaluate(c, base, event, issued, rel, cfg, docs, run_id, policies):
    c.passed, c.gate_log, c.error, c.delta = False, {}, "", None
    c._k2_sg = None
    if c.llm is None:
        c.error = "no parsable output"
        c.gate_log = {"G1": "fail: no parsable output"}
        return
    try:
        c.delta = to_delta(c.llm, f"{run_id}-{event.id}-cand{c.n}", event.id, docs[0])
    except ConversionError as e:
        c.error = str(e)
        c.gate_log = {"G1": f"fail: {e}"}
        return
    ok, log, kb2, sgs = check(base, c.delta, event, issued, rel, cfg, policies)
    c.passed, c.gate_log = ok, log
    c.sg_size = len(sgs.cases) if sgs else 0
    if ok:
        c._k2_sg = (kb2, sgs.cases, sgs.omegas)


def _finish(result, ledger, spent0, out_dir):
    result["cost_usd"] = round(ledger.spent_run() - spent0, 6)
    d = out_dir or ledger.dir / "results"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{result['event']}.json").write_text(json.dumps(result, ensure_ascii=False, indent=1, default=str),
                                               encoding="utf-8")
    return result
