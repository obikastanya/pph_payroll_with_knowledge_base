"""Dry run of the isolated mode with a perfect drafter (the gold update as model output), at no cost. Every unit must
come out correct; anything else is a defect of the harness, the gates, or the gold, to be explained before any
measured run.

    env\\Scripts\\python -m v2.harness.dry_run [unit ids ...]
"""
import collections
import shutil
import sys

from pph21kbs import draft, pipeline  # noqa: E402

from . import WORK, instances, isolated, prospective, units


def all_units():
    return units.regulation_units() + units.company_units(list(instances.REAL) + instances.fictional())


def prospective_units():
    fields = {i.id: units.fields_of(i) for i in instances.fictional()}
    out = []
    for spec in prospective.specs():
        u = prospective.unit_of(spec, units.general_cases())
        if spec["layer"] == "company":
            u.extra["fields"] = fields[spec["instance"]]
        out.append(u)
    return out


def main(only=(), pros=False):
    out = WORK / "dev" / ("dry-perfect-prospective" if pros else "dry-perfect")
    shutil.rmtree(out, ignore_errors=True)
    cfg = pipeline.Config(m=3, fallback="full")
    todo = [u for u in (prospective_units() if pros else all_units()) if not only or u.event.id in only]
    counts = collections.Counter()
    for u in todo:
        led = draft.Ledger(f"dry-{u.event.id}", root=out / "calls")
        row = isolated.run([u], units.perfect_client(led, u), led, cfg, "dry", out)[0]
        counts[row["outcome"]] += 1
        print(f"{u.event.id:20} {row['status']:9} {row['outcome']:13} B2 {row['B2']:13} B3 {row['B3']:13} "
              f"B4 {row['B4']:13} cases {len(u.cases):5} {row['note']}", flush=True)
    print(dict(counts))


if __name__ == "__main__":
    args = sys.argv[1:]
    main([a for a in args if a != "--prospective"], pros="--prospective" in args)
