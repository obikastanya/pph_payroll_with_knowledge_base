"""Exploratory, after the freeze (not preregistered): a completeness gate G7 replayed on the recorded drafts.

G7: a draft for a document the system judged relevant must change at least one observed value or conflict on its own
review examples (the cases the gates generate from the draft), at either knowledge date. A draft whose update leaves
every example as the base computes it (for instance an update that only declares facts and adds no rule that uses
them) fails G7. G5 skips facts and reports a rule without effect only as a warning, so such a draft passed G1-G6.

Replay: the drafts that passed G1-G6 in the recorded run are checked against G7; the consensus is chosen again among
the drafts that pass (pipeline.choose, same random order). A draft that fails G7 gets no repair here (a repair would
need a new model call), so the replay is conservative: it can only turn a selection into another passing draft or an
abstention. No model calls.

    env\\Scripts\\python -m v2.harness.posthoc_gate dev          the development set first (rule checked there)
    env\\Scripts\\python -m v2.harness.posthoc_gate isolated     prospective set and real set
    env\\Scripts\\python -m v2.harness.posthoc_gate chains       rewritten chain logs (v2/work/posthoc_g7/chains)
"""
import argparse
import json
from collections import Counter
from dataclasses import replace

from pph21kbs import gates, pipeline  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402

from . import WORK, chain, gold, instances, score, units
from .isolated import as_pipeline_event, set_dictionary
from .measure import MEASURED, config_measured, dev_units, prospective_units

OUT = WORK / "posthoc_g7"


def review(base, delta, event, relevance, cfg):
    """(K', cases, omegas, extra) of a draft, generated as pipeline.check generates them."""
    company = event.layer == "company"
    kb2 = apply_delta(base, delta, update_id="G7")
    starts, s_d = gates.effect_start(base, delta)
    sgs = gates.generate(base, kb2, delta, s_d, event.issued, relevance, cfg.seed, starts=starts,
                         omega=cfg.policy_omega if company else None)
    extra = [e["id"] for e in delta["add"] if e["kind"] == "fact"] if company else []
    return kb2, sgs.cases, sgs.omegas, extra


def has_effect(base, kb2, cases, omegas, extra):
    for case in cases:
        for w in omegas:
            o1, c1, e1, _ = gates.observe(kb2, case, w, extra)
            o0, c0, e0, _ = gates.observe(base, case, w, extra)
            if sorted(map(str, c1)) != sorted(map(str, c0)) or bool(e1) != bool(e0):
                return True
            if any(o1.get(k) != o0.get(k) for k in set(o1) | set(o0)):
                return True
    return False


def regate(result, base, event, cfg):
    """(new status, new selected delta, per-draft G7 verdicts, whether the decision changed) for a recorded result."""
    if result.get("status") != "proposed":
        return result.get("status"), result.get("delta"), {}, False
    rel = (result.get("relevance") or {}).get("output")
    order_of = {d["n"]: d["order"] for d in result["drafts"]}
    passing, verdict = {}, {}
    for d in result["drafts"]:
        if not d.get("passed"):
            continue
        try:
            kb2, cases, omegas, extra = review(base, d["delta"], event, rel, cfg)
        except Exception as e:  # noqa: BLE001 - the recorded run passed it; keep it, note why it could not be rechecked
            verdict[d["n"]] = f"recheck failed: {e}"[:160]
            continue
        ok = bool(cases) and has_effect(base, kb2, cases, omegas, extra)
        verdict[d["n"]] = "pass" if ok else ("fail: no review example" if not cases else "fail: no effect")
        if ok:
            passing[d["n"]] = (kb2, cases, omegas)
    if all(not v.startswith("fail") for v in verdict.values()):
        return "proposed", result["delta"], verdict, False
    sel, _, status = pipeline.choose(passing, sorted(passing, key=lambda n: order_of[n]))
    delta = next(d["delta"] for d in result["drafts"] if d["n"] == sel) if sel is not None else None
    return status, delta, verdict, status != "proposed" or sel != result.get("selected")


def _cfg(u_event):
    cfg = config_measured()
    return replace(cfg, policy_omega=u_event.issued) if u_event.layer == "company" else cfg


# ------------------------------------------------------------------------------------------------------- isolated
def isolated_stage(stage, pool):
    """Re-gated outcome of every unit of a stage; units of the stage missing from the pool are skipped."""
    path = MEASURED / stage / "scores.jsonl"
    rows = {json.loads(x)["event"]: json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()}
    out = {}
    for eid, row in rows.items():
        u = pool.get(eid)
        if u is None:
            continue
        res = json.loads((MEASURED / stage / "results" / f"{eid}.json").read_text(encoding="utf-8"))
        set_dictionary(u.extra.get("fields"))
        status, delta, verdict, changed = regate(res, u.base, as_pipeline_event(u.event), _cfg(u.event))
        new = row["outcome"]
        if changed:
            if status == "proposed":
                want = score.Behaviour(gold.apply(u.base, u.expected, update_id="GOLD"))
                new = score.score_delta(u.base, delta, want, u.cases, gold.omegas(u.event)).outcome
            else:
                new = "abstain"
        out[eid] = {"before": row["outcome"], "after": new, "status_after": status, "g7": verdict,
                    "changed": changed}
    set_dictionary(None)
    return out


def summary(rows):
    before, after = Counter(r["before"] for r in rows.values()), Counter(r["after"] for r in rows.values())
    flips = Counter((r["before"], r["after"]) for r in rows.values() if r["before"] != r["after"])
    flagged = [k for k, r in rows.items() if any(str(v).startswith("fail") for v in r["g7"].values())]
    return {"n": len(rows), "before": dict(before), "after": dict(after),
            "flips": {f"{a}->{b}": n for (a, b), n in flips.items()}, "drafts_failing_g7_in": flagged}


def dev():
    pool = {u.event.id: u for u in dev_units()}
    stages = sorted(p.name for p in MEASURED.glob("dev-*") if (p / "scores.jsonl").exists())
    return {st: (lambda r: {"summary": summary(r), "units": r})(isolated_stage(st, pool)) for st in stages}


def isolated():
    from . import instances as ins
    pros = {u.event.id: u for u in prospective_units()}
    real = {u.event.id: u for u in units.regulation_units() + units.company_units(list(ins.REAL))}
    out = {}
    for st, pool in (("isolated-prospective", pros), ("isolated-real-1", real), ("isolated-real-2", real)):
        r = isolated_stage(st, pool)
        out[st] = {"summary": summary(r), "units": r}
    return out


# ------------------------------------------------------------------------------------------------------- chains
def chain_logs(ids=None):
    """Rewrite each chain log with the re-gated decisions. The base of a step is the one the recorded run used (the
    recorded decisions up to that step), since the drafts were written against it."""
    src, dst = MEASURED / "chains", OUT / "chains"
    dst.mkdir(parents=True, exist_ok=True)
    report = {}
    for c in chain.chains():
        if ids and c.id not in ids or not (src / f"{c.id}.jsonl").exists():
            continue
        log = chain.load(src, c)
        reg = gold.chain().known_on(c.start)
        kbs = {i.id: reg for i in c.members}
        fields = {i.id: units.fields_of(i) for i in c.members}
        shared = len(c.members) > 1
        events = {s.event.id: s.event for s in chain.stream(c.members, c.start)}
        new_log, changes = [], []
        for row in log:
            ev = events[row["event"]]
            if row["instance"] is None:
                set_dictionary(None if shared else fields[c.members[0].id])
                base = reg if shared else kbs[c.members[0].id]
                cfg = config_measured()
            else:
                set_dictionary(fields[row["instance"]])
                base = kbs[row["instance"]]
                cfg = replace(config_measured(), policy_omega=ev.issued)
            res_path = src / "results" / c.id / f"{ev.id}.json"
            res = json.loads(res_path.read_text(encoding="utf-8")) if res_path.exists() else None
            new = dict(row)
            if res is not None and res.get("status") == "proposed":
                status, delta, verdict, changed = regate(res, base, as_pipeline_event(ev), cfg)
                if changed:
                    new.update(status=status, delta=delta, how="system" if delta is not None else "none",
                               g7=verdict)
                    changes.append({"event": ev.id, "status": status, "g7": verdict})
            new_log.append(new)
            # the recorded decision (not the re-gated one) builds the base of the next step
            update, how = chain._decision(ev, res) if res is not None else (row["delta"], row["how"])
            if update is not None:
                targets = list(kbs) if row["instance"] is None else [row["instance"]]
                for t in targets:
                    kbs[t] = chain.lenient(kbs[t], update, f"{ev.id}-{how}")
                if row["instance"] is None and shared:
                    reg = chain.lenient(reg, update, f"{ev.id}-{how}")
        set_dictionary(None)
        with open(dst / f"{c.id}.jsonl", "w", encoding="utf-8") as f:
            for r in new_log:
                f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
        report[c.id] = changes
        print(c.id, changes, flush=True)
    return report


def save(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(obj, indent=1, default=str, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("dev", "isolated", "chains"))
    ap.add_argument("--chain", action="append")
    a = ap.parse_args()
    if a.what == "dev":
        r = dev()
        save("dev", r)
        for st, v in r.items():
            print(st, json.dumps(v["summary"]))
    elif a.what == "isolated":
        r = isolated()
        save("isolated", r)
        for st, v in r.items():
            print(st, json.dumps(v["summary"]))
    else:
        save("chain_changes", chain_logs(a.chain))
