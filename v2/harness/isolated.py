"""Isolated mode: every document is applied to the gold knowledge base just before it, and scored with the
baselines computed from the same drafts.

    B2  first draft (in the random order) that passes every gate, repair included; no consensus, no abstention
    B3  first draft that passes the schema and quote checks (G1, G2) before repair
    B4  majority vote over the behaviour of all drafts, without gates (Gogani-Khiabani et al.)
    top perfect selection: correct when any passing draft is correct
"""
import json
from dataclasses import dataclass, field, replace

from pph21kbs import config, gates, pipeline  # noqa: E402

from . import domains, gold, score


@dataclass
class Unit:
    event: object                  # corpus.Event (or a prospective unit with the same fields)
    base: object                   # knowledge base the document is applied to
    expected: dict                 # gold update
    cases: list
    policies: tuple = ()
    extra: dict = field(default_factory=dict)


def as_pipeline_event(ev):
    return pipeline.Event(ev.id, tuple(ev.documents), ev.issued, layer=ev.layer, title=ev.title)


def _initial(d):
    return d["initial_delta"] if d.get("repaired") and d.get("initial_delta") else d["delta"]


def _passes(log, gates_):
    return all(str(log.get(g, "")).startswith("pass") for g in gates_)


def _behaviour_inputs(base, delta, ev, relevance, cfg):
    kb2 = gold.apply(base, delta, update_id="B4")
    starts, s_d = gates.effect_start(base, delta)
    sgs = gates.generate(base, kb2, delta, s_d, ev.issued, relevance, cfg.seed, starts=starts,
                         omega=cfg.policy_omega if ev.layer == "company" else None)
    return kb2, sgs.cases, sgs.omegas


def majority_without_gates(unit, result, cfg):
    drafts = sorted(result.get("drafts", []), key=lambda d: d["order"])
    rel = (result.get("relevance") or {}).get("output")
    inputs = {}
    for d in drafts:
        delta = _initial(d)
        if delta is None:
            continue
        try:
            inputs[d["n"]] = _behaviour_inputs(unit.base, delta, unit.event, rel, cfg)
        except Exception:  # noqa: BLE001 - a draft that cannot be applied takes no part in the vote
            continue
    sel, _, status = pipeline.choose(inputs, [d["n"] for d in drafts if d["n"] in inputs])
    return next(_initial(d) for d in drafts if d["n"] == sel) if status == "proposed" else None


def score_result(unit, result, cfg):
    ev = unit.event
    expected = score.Behaviour(gold.apply(unit.base, unit.expected, update_id="GOLD"))
    ws = gold.omegas(ev)

    def judge(delta):
        return score.score_delta(unit.base, delta, expected, unit.cases, ws)

    main = judge(score.delta_of(result, ev))
    drafts = sorted(result.get("drafts", []), key=lambda d: d["order"])
    by_draft = {d["n"]: judge(d["delta"]).outcome for d in drafts if d.get("passed")}
    b3 = next((_initial(d) for d in drafts if _initial(d) is not None and _passes(d["first_gate_log"], ("G1", "G2"))),
              None)
    b2 = next((d["delta"] for d in drafts if d.get("passed")), None)
    if result.get("status") == "empty":
        b2 = b3 = b4 = score.delta_of(result, ev)
    else:
        b4 = majority_without_gates(unit, result, cfg) if drafts else None
    return {"event": ev.id, "status": result.get("status"), "outcome": main.outcome, "tuples": main.tuples,
            "wrong_tuples": main.wrong_tuples, "wrong_cases": main.wrong_cases, "note": main.note,
            "B2": judge(b2).outcome, "B3": judge(b3).outcome, "B4": judge(b4).outcome,
            "top": "correct" if "correct" in by_draft.values() else ("abstain" if not by_draft else "silent_error"),
            "drafts": by_draft, "cost_usd": result.get("cost_usd"), "selection": result.get("selection"),
            "relevant": (result.get("relevance") or {}).get("output", {}).get("relevant") if result.get("relevance")
            else None}


def set_dictionary(fields):
    """The company's payroll data dictionary in the workspace, or none (the standard dictionary only)."""
    path = config.PAYROLL_INPUTS
    if fields:
        path.parent.mkdir(parents=True, exist_ok=True)
        domains.write_dictionary(path, fields)
    else:
        path.unlink(missing_ok=True)


def run(units, client, ledger, cfg, run_id, out_dir, digester=None):
    """Run and score every unit; one JSON line per unit in out_dir/scores.jsonl (results in out_dir/results)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for u in units:
        set_dictionary(u.extra.get("fields"))
        ucfg = replace(cfg, policy_omega=u.event.issued) if u.event.layer == "company" else cfg
        result = pipeline.run_document(as_pipeline_event(u.event), u.base, client, ledger, ucfg, run_id=run_id,
                                       out_dir=out_dir / "results", policies=u.policies, digester=digester)
        row = score_result(u, result, ucfg)
        rows.append(row)
        with open(out_dir / "scores.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    return rows
