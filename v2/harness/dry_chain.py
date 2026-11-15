"""Dry run of the chained mode with a perfect drafter (and optionally a faulty one for one event: an amount off by
Rp1.000, or a missing element), at no cost.

    env\\Scripts\\python -m v2.harness.dry_chain WIKA [--faulty E09]
"""
import argparse
import copy
import shutil
from types import SimpleNamespace

from pph21kbs import draft, pipeline  # noqa: E402

from . import WORK, chain, gold, instances, units


def expected(step):
    ev = step.event
    if not ev.gold:
        return gold.empty(ev.id, ev.document, ev.issued)
    return gold.recorded(gold.delta(ev.gold), ev.issued) if ev.layer == "company" else gold.delta(ev.gold)


def client_for(ledger, faulty=None, kind="amount"):
    def make(step):
        d = expected(step)
        if step.event.id == faulty and d.get("add"):
            d = copy.deepcopy(d)
            numeric = [e for e in d["add"] if e.get("kind") == "parameter" and isinstance(e.get("value"), int)]
            if kind == "date":                # validity one month late; the amounts stay as quoted
                first = d["add"][0]
                y, m = map(int, first["valid_from"][:7].split("-"))
                first["valid_from"] = f"{y + m // 12}-{m % 12 + 1:02d}-01"
            elif numeric:                     # a mistyped amount: the value off by Rp1.000
                numeric[0]["value"] += 1000
            else:
                d["add"] = d["add"][1:]
        return units.perfect_client(ledger, SimpleNamespace(event=step.event, expected=d))
    return make


def main(chain_id, faulty=None, kind="amount"):
    c = next(x for x in chain.chains() if x.id == chain_id)
    out = WORK / "dev" / (f"dry-chain-{chain_id}" + (f"-{faulty}-{kind}" if faulty else ""))
    shutil.rmtree(out, ignore_errors=True)
    led = draft.Ledger(f"dry-chain-{chain_id}", root=out / "calls")
    chain.run(c, client_for(led, faulty, kind), led, pipeline.Config(m=3, fallback="full"), "dry", out)
    log = chain.load(out, c)
    panels = {i.id: instances.panel(i, fields=units.fields_of(i)) for i in c.members}
    for condition in ("base", "none", "careful", "code"):
        kbs = chain.replay(c, log, condition)
        acc = chain.accuracy(c, kbs, panels)
        for inst, rows in acc.items():
            n = len(rows)
            print(f"{condition:8} {inst:9} payslips {n:6}  at payroll {sum(r['at_payroll'] for r in rows) / n:.4f}"
                  f"  at end {sum(r['at_end'] for r in rows) / n:.4f}", flush=True)
    print("statuses:", [r["status"] for r in log])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("chain")
    ap.add_argument("--faulty")
    ap.add_argument("--kind", choices=("amount", "date"), default="amount")
    a = ap.parse_args()
    main(a.chain, a.faulty, a.kind)
