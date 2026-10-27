"""Independent arithmetic check of GT5 JSON files.

Re-evaluates every step expression with exact Decimal arithmetic, re-looks up every TER rate
from ter_bulanan.csv, and checks that nilai_harapan values equal the step results.
Usage: python check_gt5.py <repo_root> <gt5_dir>
"""
import csv
import glob
import json
import os
import re
import sys
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP

root, gdir = sys.argv[1], sys.argv[2]

rows = list(csv.DictReader(open(os.path.join(root, "dataset/01_regulasi/tables/ter_bulanan.csv"), encoding="utf-8")))


def rate(cat, bruto):
    for r in rows:
        if r["kategori"] != cat:
            continue
        lo = Decimal(r["batas_bawah"])
        hi = Decimal(r["batas_atas"]) if r["batas_atas"] else None
        if (lo == 0 and bruto <= hi) or (bruto > lo and (hi is None or bruto <= hi)):
            return Decimal(r["tarif_persen"])
    return None


ns = {
    "Dec": Decimal,
    "floor": lambda x: x.to_integral_value(rounding=ROUND_FLOOR),
    "rnd": lambda x: x.quantize(Decimal(1), rounding=ROUND_HALF_UP),
    "floor1000": lambda x: (x / 1000).to_integral_value(rounding=ROUND_FLOOR) * 1000,
    "min": min, "max": max,
}

steps = fails = examples = 0
for path in sorted(glob.glob(os.path.join(gdir, "*.json"))):
    data = json.load(open(path, encoding="utf-8"))
    for ex in data["contoh"]:
        examples += 1
        results = {}
        for st in ex["langkah"]:
            steps += 1
            expr = re.sub(r"(?<![\w.])(\d+(?:\.\d+)?)", r"Dec('\1')", st["ekspresi"])
            val = eval(expr, ns)
            results[st["kunci"]] = val
            if abs(val - Decimal(str(st["hasil"]))) > Decimal("0.005"):
                fails += 1
                print("MISMATCH", ex["id"], st["kunci"], val, st["hasil"])
            if "ter" in st:
                r = rate(st["ter"]["kategori"], Decimal(str(st["ter"]["bruto"])))
                if r != Decimal(str(st["ter"]["tarif_persen"])):
                    fails += 1
                    print("TER MISMATCH", ex["id"], st["kunci"], r, st["ter"])
        for k, v in ex["nilai_harapan"].items():
            if abs(results[k] - Decimal(str(v))) > Decimal("0.005"):
                fails += 1
                print("HARAPAN MISMATCH", ex["id"], k)
print(f"{examples} contoh, {steps} langkah dicek, {fails} selisih")
