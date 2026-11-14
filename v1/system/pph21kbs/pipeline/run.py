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
from . import consensus, context, gates, inputs, prompts, review, select, sg
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
    max_tokens: int = 32000                   # per draft or repair call (AB1 formalises a whole knowledge base)
    # pipeline v2 (development; all False reproduces the frozen v1 pipeline)
    case_inputs: bool = False                 # list the case-data attributes in the context (inputs.py)
    prompt_v2: bool = False                   # modelling guidance in the draft system prompt
    g5_date_warn: bool = False                # stated effective date / subject not reflected: warning, not failure
    g5_vacuous_warn: bool = False             # element without effect on S^G: warning to the reviewer, not failure
    review: bool = False                      # self-check round with execution feedback (review.py)
    consensus_align: bool = False             # consensus compares conflict reports by fact, not by rule id
    input_gate: bool = False                  # G6: reading a case-data input that does not exist fails (repairable);
                                              # a genuinely new input goes to the reviewer instead of applying silently

    @classmethod
    def v2(cls, **kw):
        return cls(case_inputs=True, prompt_v2=True, g5_date_warn=True, g5_vacuous_warn=True, review=True,
                   consensus_align=True, input_gate=True, **kw)


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
    if cfg.input_gate:
        view_in = base.view(cfg.policy_omega if event.layer == "company" else issued)
        new = inputs.new_inputs(view_in, delta)
        if new:
            log["G6"] = ("fail: reads case-data inputs that do not exist in the payroll data: " + ", ".join(new)
                         + ". If an input listed under CASE DATA has the same meaning, use it. Otherwise keep the "
                         "provision and its new input unchanged: do not remove or simplify a provision to pass this "
                         "check; the update then goes to the reviewer, who adds the input to the payroll data")[:700]
            return False, log, kb2, None
        log["G6"] = "pass"
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
        if (cfg.g5_date_warn or cfg.g5_vacuous_warn) and not r5.passed:
            soft = [m for m in r5.messages
                    if (cfg.g5_date_warn and m.startswith(("stated effective date", "stated subject")))
                    or (cfg.g5_vacuous_warn and m.endswith("(vacuous element)"))]
            r5 = gates.GateResult("G5", len(soft) == len(r5.messages),
                                  [m for m in r5.messages if m not in soft], soft)
            log["G5_warnings"] = r5.warnings
        log["G5"] = r5.summary()
        if not r5.passed:
            return False, log, kb2, sgs
    sgs.evals = ev
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
    if cfg.case_inputs:
        ctx += "\n\n" + inputs.context_text(view)
    system_draft = prompts.SYSTEM_DRAFT_V2 if cfg.prompt_v2 else prompts.SYSTEM_DRAFT
    result = {"run": run_id, "event": event.id, "condition": "proposed", "documents": [d["id"] for d in docs],
              "selection": {s.document: {"tokens": s.tokens, "dropped": s.dropped} for s in selections},
              "candidates": [], "groups": [], "selected": None, "status": None, "delta": None, "cost_usd": 0.0}
    call_prefix = f"{run_id}-{event.id}-"           # cost = this document's calls (documents may share a ledger)
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
            return _finish(result, ledger, call_prefix, out_dir)
        # candidates
        rng = random.Random(cfg.seed + hash(event.id) % 1000)
        order = list(range(1, cfg.m + 1))
        rng.shuffle(order)
        prefix = [doc_text, ctx]
        # the m drafts are independent requests (one round; one batch with the batch client), then the repairs of
        # the candidates that failed a gate (a second round); a repair sees only its own candidate and gate messages
        cands = [Candidate(n, order.index(n)) for n in range(1, cfg.m + 1)]
        outs = client.complete_many([dict(system=system_draft, prefix=prefix,
                                          user=prompts.draft_user(event, docs, rel), schema=_schema(),
                                          schema_name="delta", effort=cfg.draft_effort, step="draft",
                                          document=event.document, event=event.id, candidate=c.n,
                                          order_seed=cfg.seed, call_id=f"{run_id}-{event.id}-cand{c.n}",
                                          max_tokens=cfg.max_tokens)
                                     for c in cands])
        for c, (_, out, _) in zip(cands, outs):
            c.llm = out
            _evaluate(c, base, event, issued, rel, cfg, docs, run_id, policies)
            c.passed_before_repair = c.passed
            c.first_gate_log = dict(c.gate_log)
            c.initial_llm, c.initial_delta = c.llm, c.delta
        for r in range(cfg.repair_rounds):
            todo = [c for c in cands if not c.passed and c.llm is not None]
            if not todo:
                break
            # same system prompt and prefix as the drafts, so the cached prefix is read, not written again
            outs = client.complete_many([dict(system=system_draft, prefix=prefix,
                                              user=prompts.repair_user(event, docs, c.llm,
                                                                       _messages(c.gate_log) or [c.error]),
                                              schema=_schema(), schema_name="delta", effort=cfg.draft_effort,
                                              step="repair", document=event.document, event=event.id,
                                              candidate=c.n, order_seed=cfg.seed,
                                              call_id=f"{run_id}-{event.id}-cand{c.n}-rep{r + 1}",
                                              max_tokens=cfg.max_tokens)
                                         for c in todo])
            for c, (_, out2, _) in zip(todo, outs):
                if out2 is not None:
                    c.llm, c.repaired = out2, True
                    _evaluate(c, base, event, issued, rel, cfg, docs, run_id, policies)
        if cfg.review:
            _review_round(cands, base, view, event, docs, rel, cfg, run_id, policies, client, system_draft, prefix)
        passing = {c.n: c._k2_sg for c in cands if c.passed}
        sel, groups, status = consensus.choose(passing, sorted(passing, key=lambda n: order.index(n)),
                                               align=cfg.consensus_align)
        result.update(groups=groups, selected=sel, status=status)
        if sel is not None:
            result["delta"] = next(c.delta for c in cands if c.n == sel)
        result["candidates"] = [{"n": c.n, "order": c.order, "passed": c.passed,
                                 "passed_before_repair": c.passed_before_repair, "repaired": c.repaired,
                                 "gate_log": c.gate_log, "first_gate_log": c.first_gate_log, "sg_size": c.sg_size,
                                 "error": c.error, "llm": c.llm, "delta": c.delta,
                                 "initial_delta": c.initial_delta if c.repaired else None,
                                 "review": getattr(c, "review_log", None)} for c in cands]
    except BudgetExceeded as e:
        result["status"] = "budget"
        result["error"] = str(e)
    return _finish(result, ledger, call_prefix, out_dir)


def _review_round(cands, base, view, event, docs, rel, cfg, run_id, policies, client, system_draft, prefix):
    """v2: each passing candidate gets one self-check call with execution feedback; a reviewed Delta replaces the
    candidate only if it passes the gates again."""
    todo = [c for c in cands if c.passed and c._k2_sg is not None]
    if not todo:
        return
    users = []
    for c in todo:
        kb2, _, _ = c._k2_sg
        sgs = c._sgs
        summary = review.effect_summary(base, kb2, sgs, sgs.evals)
        warn = list(c.gate_log.get("G5_warnings") or []) + list(c.gate_log.get("G3_warnings") or [])[:5]
        users.append(review.review_user(prompts.metadata_text(event, docs), c.llm, summary,
                                        inputs.new_inputs(view, c.delta), warn))
    outs = client.complete_many([dict(system=system_draft, prefix=prefix, user=u, schema=_schema(), schema_name="delta",
                                      effort=cfg.draft_effort, step="review", document=event.document, event=event.id,
                                      candidate=c.n, order_seed=cfg.seed, call_id=f"{run_id}-{event.id}-cand{c.n}-rev",
                                      max_tokens=cfg.max_tokens)
                                 for c, u in zip(todo, users)])
    for c, u, (_, out, _) in zip(todo, users, outs):
        before = (c.llm, c.delta, c.passed, c.gate_log, c._k2_sg, c._sgs, c.sg_size, c.error)
        c.review_log = {"prompt_tail": u[-1500:], "changed": False, "kept": True}
        if out is None or out == c.llm:
            continue
        c.llm = out
        _evaluate(c, base, event, issued_of(event), rel, cfg, docs, run_id, policies)
        if c.passed:
            c.review_log.update(changed=True, kept=True)
        else:
            c.review_log.update(changed=True, kept=False, failed=dict(c.gate_log))
            c.llm, c.delta, c.passed, c.gate_log, c._k2_sg, c._sgs, c.sg_size, c.error = before


def issued_of(event):
    return event.issued


def _evaluate(c, base, event, issued, rel, cfg, docs, run_id, policies):
    c.passed, c.gate_log, c.error, c.delta = False, {}, "", None
    c._k2_sg = None
    c._sgs = None
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
        c._sgs = sgs


def _finish(result, ledger, call_prefix, out_dir):
    result["cost_usd"] = ledger.spent_prefix(call_prefix)
    d = out_dir or ledger.dir / "results"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{result['event']}.json").write_text(json.dumps(result, ensure_ascii=False, indent=1, default=str),
                                               encoding="utf-8")
    return result
