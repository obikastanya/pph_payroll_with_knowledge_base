"""Chained mode: one company system receives its documents in order and updates its own knowledge base.

The base condition runs the model: an applied proposal is approved as is; an abstention is handled by HR, who writes
the gold update HR_DAYS after the document was issued. The other conditions reuse the same results without new model
calls: "none" leaves an abstention unhandled; "careful" also has HR reject a wrong proposal whose error shows on the
review examples (the generated cases of the selected draft) and write the gold update instead. The "code" scenario
applies every gold update HR_DAYS after issue, as the fastest open-source calculator adopted TER (B1).
"""
import copy
import json
from dataclasses import dataclass, field
from datetime import date, timedelta

from pph21kbs import gates, pipeline  # noqa: E402
from pph21kbs.kb import UpdateError, apply_delta  # noqa: E402

from . import corpus, gold, instances, score
from .isolated import as_pipeline_event, set_dictionary
from .units import company_event, fields_of

HR_DAYS = 26
WINDOW_END = date(2026, 12, 31)


@dataclass
class Step:
    event: object
    instance: str | None           # the company of a company document; None for a regulation document
    result: dict = field(default_factory=dict)


@dataclass
class Chain:
    id: str
    members: tuple                 # instances served
    start: date
    steps: list = field(default_factory=list)


def stream(members, start):
    """Regulation documents issued on or after `start` and the members' company documents, in date order (on the
    same day, company documents first: they are installed before anything else)."""
    out = [(e.issued, 1, Step(e, None)) for e in corpus.test_stream() if e.issued >= start]
    for inst in members:
        for doc in inst.documents:
            if doc.known_on >= start:
                out.append((doc.known_on, 0, Step(company_event(inst, doc), inst.id)))
    return [s for _, _, s in sorted(out, key=lambda t: (t[0], t[1], t[2].event.id))]


def chains():
    """The seven independent chains: one per real company, two shared by the fictional companies (simulation)."""
    out = [Chain(i.id, (i,), i.installed) for i in instances.REAL]
    fict = {i.id: i for i in instances.fictional()}
    out += [Chain(cid, tuple(fict[x] for x in ids), date(2023, 1, 1))
            for cid, ids in instances.SHARED_CHAINS.items()]
    return out


# ---------------------------------------------------------------------------------------------- applying updates
def shifted(update, days):
    d = copy.deepcopy(update)
    for op in ("add", "change", "remove"):
        for rec in d.get(op, []):
            if rec.get("recorded_on"):
                rec["recorded_on"] = (date.fromisoformat(rec["recorded_on"]) + timedelta(days=days)).isoformat()
    return d


def lenient(kb, update, update_id):
    """Apply an update written for another base: an add of a live id becomes a change, a change or removal of an
    absent id becomes an add or is skipped. Used only to replay updates across conditions."""
    try:
        return apply_delta(kb, update, update_id=update_id)
    except (UpdateError, ValueError, KeyError):
        live = {r.id for r in kb.records if r.kind != "tombstone"}
        d = copy.deepcopy(update)
        adds = [r for r in d.get("add", []) if r["id"] not in live]
        changes = [r for r in d.get("change", []) if r["id"] in live] + [r for r in d.get("add", [])
                                                                           if r["id"] in live]
        adds += [r for r in d.get("change", []) if r["id"] not in live]
        d["add"], d["change"] = adds, changes
        d["remove"] = [r for r in d.get("remove", []) if r["id"] in live]
        return apply_delta(kb, d, update_id=update_id, validate=False)


# ---------------------------------------------------------------------------------------------- running a chain
def run(chain, client_for, ledger, cfg, run_id, out_dir, digester=None):
    """Run the base condition of one chain with the model. client_for(step) gives the client of a step (one client
    for all steps in a measured run; a perfect or faulty drafter in a dry run). Writes out_dir/<chain>.jsonl."""
    reg = gold.chain().known_on(chain.start)
    kbs = {i.id: reg for i in chain.members}
    fields = {i.id: fields_of(i) for i in chain.members}
    shared = len(chain.members) > 1
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / f"{chain.id}.jsonl"
    log_path.unlink(missing_ok=True)
    for k, step in enumerate(stream(chain.members, chain.start)):
        ev = step.event
        if step.instance is None:
            set_dictionary(None if shared else fields[chain.members[0].id])
            base = reg if shared else kbs[chain.members[0].id]
            ucfg, policies = cfg, ()
        else:
            set_dictionary(fields[step.instance])
            base = kbs[step.instance]
            ucfg = pipeline.Config(**{**cfg.__dict__, "policy_omega": ev.issued})
            policies = (ev.document,)
        result = pipeline.run_document(as_pipeline_event(ev), base, client_for(step), ledger, ucfg,
                                       run_id=f"{run_id}-{chain.id}-{k:02d}", out_dir=out_dir / "results" / chain.id,
                                       policies=policies, digester=digester)
        step.result = result
        update, how = _decision(ev, result)
        if update is not None:
            targets = list(kbs) if step.instance is None else [step.instance]
            for t in targets:
                kbs[t] = lenient(kbs[t], update, f"{ev.id}-{how}")
            if step.instance is None and shared:
                reg = lenient(reg, update, f"{ev.id}-{how}")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"k": k, "event": ev.id, "instance": step.instance, "status": result.get("status"),
                                "how": how, "delta": score.delta_of(result, ev),
                                "cost_usd": result.get("cost_usd")}, ensure_ascii=False, default=str) + "\n")
    set_dictionary(None)
    return kbs


def _decision(ev, result, condition="base"):
    """(update to apply or None, how): the system's update, HR's gold update, or nothing."""
    d = score.delta_of(result, ev)
    if d is not None:
        return d, "system"
    if condition != "none" and ev.gold:
        return shifted(gold.delta(ev.gold), HR_DAYS), "hr"
    return None, "none"


def load(out_dir, chain):
    return [json.loads(line) for line in (out_dir / f"{chain.id}.jsonl").read_text(encoding="utf-8").splitlines()]


# ---------------------------------------------------------------------------------------------- conditions and scoring
def replay(chain, log, condition):
    """The members' final knowledge bases under a condition, from the logged base-condition results."""
    reg = gold.chain().known_on(chain.start)
    kbs = {i.id: reg for i in chain.members}
    events = {s.event.id: s.event for s in stream(chain.members, chain.start)}
    for row in log:
        ev = events[row["event"]]
        targets = list(kbs) if row["instance"] is None else [row["instance"]]
        if condition == "code":
            update, how = (shifted(gold.delta(ev.gold), HR_DAYS) if ev.gold else None), "code"
        else:
            update, how = (row["delta"], "system") if row["delta"] is not None else (None, "none")
            if update is None and condition != "none" and ev.gold:
                update, how = shifted(gold.delta(ev.gold), HR_DAYS), "hr"
            if condition == "careful" and how == "system" and ev.gold is not None:
                for t in targets:
                    if _caught(kbs[t], update, ev):
                        update, how = shifted(gold.delta(ev.gold), HR_DAYS), "hr-rejected"
                        break
        if update is not None:
            for t in targets:
                kbs[t] = lenient(kbs[t], update, f"{ev.id}-{how}")
    return kbs


def _caught(base, update, ev):
    """HR sees the error: on the review examples of the proposal, its results differ from the gold update's."""
    try:
        kb2 = apply_delta(base, update, update_id="REVIEW")
        starts, s_d = gates.effect_start(base, update)
        sgs = gates.generate(base, kb2, update, s_d, ev.issued, None, 20261027, starts=starts,
                             omega=ev.issued if ev.layer == "company" else None)
        want = score.Behaviour(lenient(base, gold.delta(ev.gold), "REVIEW-GOLD"))
        return score.compare(score.Behaviour(kb2), want, sgs.cases, sgs.omegas).outcome != "correct"
    except Exception:  # noqa: BLE001 - an update that cannot even be shown is rejected
        return True


def gold_final(inst):
    kb = gold.chain()
    for doc in sorted(inst.documents, key=lambda d: d.known_on):
        if doc.gold and gold.exists(doc.gold):
            kb = gold.apply(kb, gold.delta(doc.gold))
    return kb


def accuracy(chain, kbs, panels):
    """Payslip rows per member, from its install month: score.payslips of its final knowledge base against its
    gold."""
    out = {}
    for i in chain.members:
        rows = score.payslips(kbs[i.id], gold_final(i), panels[i.id], WINDOW_END)
        out[i.id] = [r for r in rows if (r["year"], r["month"]) >= (i.installed.year, i.installed.month)]
    return out
