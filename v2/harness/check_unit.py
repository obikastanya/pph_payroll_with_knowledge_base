"""Render, import, and validate prospective units; prints the problems of each (none = usable).

    env/Scripts/python -m v2.harness.check_unit R01 K05 ...
"""
import json
import sys

from . import instances, render, workspace
from .prospective import UNITS, validate
from .units import fields_of


def check(unit_id):
    folder = UNITS / unit_id
    spec = json.loads((folder / "spec.json").read_text(encoding="utf-8"))
    if not (folder / "teks.txt").exists() or (folder / "teks.md").stat().st_mtime > (folder / "teks.txt").stat().st_mtime:
        render.render(unit_id)
    workspace.import_prospective(unit_id)
    fields = {}
    if spec["layer"] == "company":
        inst = next(i for i in instances.fictional() if i.id == spec["instance"])
        fields = fields_of(inst)
    return validate(spec, fields)


if __name__ == "__main__":
    for uid in sys.argv[1:]:
        problems = check(uid)
        print(uid, "OK" if not problems else "PROBLEMS")
        for p in problems:
            print("   -", p)
