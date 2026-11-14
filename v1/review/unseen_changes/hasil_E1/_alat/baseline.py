"""Check case conversion: base KB (no change Delta; optionally the convention Delta) vs keluaran_menurut_aturan_2026.

Usage: python baseline.py [--konvensi]
"""
import json
import sys
from datetime import date

from common import base_at, OUT
from pph21kbs.kb import apply_delta
import convert
from run_eval import evaluate

conv = "--konvensi" in sys.argv
kb = base_at("2026-10-28")
if conv:
    kb = apply_delta(kb, json.loads((OUT / "delta" / "KONVENSI.json").read_text(encoding="utf-8")))
omega = date(2026, 12, 31)
tot = bad = 0
for i in range(1, 17):
    uid = f"U{i:02d}"
    for ex in convert.load(uid)["contoh"]:
        case, stated = convert.to_case(ex, method="gross" if ex["input"]["metode"] != "gross" else None)
        exp = convert.expected(ex["keluaran_menurut_aturan_2026"])
        r, diffs = evaluate(kb, omega, case, exp)
        tot += 1
        if diffs or r.errors:
            bad += 1
            print(ex["id"], "DIFF", len(diffs), diffs[:4], r.errors[:2])
print("total", tot, "with differences", bad)
