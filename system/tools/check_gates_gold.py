"""Gates G1-G5 on every gold Delta (akuisisi.md 4, freezing condition: no false rejection of a gold Delta).

    env\\Scripts\\python system\\tools\\check_gates_gold.py [--write] [ids...]

Each event Delta of the main chain is checked against the chain before it (omega = its issue date); a fictive
regulation against the chain prefix at its issue date; a company policy against the full regulation chain
(omega = 2026-10-27). Background updates are not acquired and are not gated. --write saves
docs/hasil/gerbang_emas.csv.
"""
import csv
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402
from pph21kbs.pipeline.run import Config, check  # noqa: E402
from pph21kbs.text import registry  # noqa: E402


def _event(u):
    try:
        return corpus.event(u.event_id or u.doc.id)
    except KeyError:
        return None


def main(write=False, only=()):
    chain = build_gold.build(check_only=True)
    cfg = Config()
    rows = []
    jobs = []
    ids = [x.update_id for x in chain.updates]
    for u in build_gold.collect():
        if u.kind == "event":
            i = ids.index(u.delta_id)
            jobs.append((u, chain.until(ids[i - 1])))
    for u in build_gold.collect_side():
        if u.kind == "background":          # not acquired, not gated (e.g. the fictive background of FR03)
            continue
        if u.kind == "policy":
            jobs.append((u, chain))
        else:
            base = build_gold.prefix_at(chain, u.recorded_on or u.doc.issued)
            for sid in getattr(u, "base_side", ()):
                base = apply_delta(base, build_gold.side_update(sid).to_json())
            jobs.append((u, base))
    for u, base in jobs:
        if only and u.delta_id not in only:
            continue
        ev = _event(u)
        if ev is None:
            continue
        d = u.to_json()
        issued = date.fromisoformat(u.recorded_on or registry()[u.doc.id]["issued"])
        if ev.layer == "company":
            from dataclasses import replace
            ev = replace(ev, issued=issued)
        t = time.time()
        if not (d["add"] or d["change"] or d["remove"]):
            ok, log = True, {"G1-G5": "empty Delta (relevance only)"}
        else:
            ok, log, _, sgs = check(base, d, ev, issued, None, cfg, policies=(u.doc.id,) if u.kind == "policy" else ())
        row = {"update": u.delta_id, "event": ev.id, "kind": u.kind, "passed": ok,
               "seconds": round(time.time() - t, 1)}
        for g in ("G1", "G2", "G3", "G4", "G5"):
            row[g] = log.get(g, "")
        rows.append(row)
        print(f"{u.delta_id:18s} {'pass' if ok else 'FAIL'} {row['seconds']:6.1f}s "
              + " ".join(f"{g}={v[:60]}" for g, v in log.items() if g.startswith("G") and not str(v).startswith("pass")),
              flush=True)
    n_ok = sum(r["passed"] for r in rows)
    print(f"{n_ok}/{len(rows)} gold Deltas pass all gates")
    if write:
        out = ROOT / "docs" / "hasil" / "gerbang_emas.csv"
        with open(out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print("written", out.relative_to(ROOT))


if __name__ == "__main__":
    main("--write" in sys.argv, [a for a in sys.argv[1:] if not a.startswith("--")])
