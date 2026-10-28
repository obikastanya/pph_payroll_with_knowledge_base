"""Survey of input fields, components and expected keys in the sealed examples."""
import json
from collections import Counter, defaultdict
from common import SEALED

inp, comp, per, year, other = Counter(), Counter(), Counter(), Counter(), defaultdict(set)
for i in range(1, 17):
    d = json.loads((SEALED / f"U{i:02d}" / "contoh.json").read_text(encoding="utf-8"))
    for c in d["contoh"]:
        for k, v in c["input"].items():
            inp[k] += 1
            if k not in ("masa",):
                other[k].add(json.dumps(v, ensure_ascii=False)[:60])
        for m in c["input"]["masa"]:
            for k in m:
                if k not in ("bulan", "komponen"):
                    other["masa." + k].add(f"U{i:02d}")
            for k in m["komponen"]:
                comp[(k)] += 1
                other["comp." + k].add(f"U{i:02d}")
        ke = c["keluaran_diharapkan"]
        for k in ke:
            if k not in ("per_masa", "setahun"):
                other["ke." + k].add(f"U{i:02d}")
        for m in ke.get("per_masa", []):
            for k in m:
                per[k] += 1
                other["per." + k].add(f"U{i:02d}")
        for k in (ke.get("setahun") or {}):
            year[k] += 1
            other["year." + k].add(f"U{i:02d}")
print("INPUT", dict(inp))
print("COMP", dict(comp))
print("PER", dict(per))
print("YEAR", dict(year))
for k, v in sorted(other.items()):
    print(k, sorted(v)[:12])
