r"""Ablation AB5, RQ2 part (skeleton: plain schema validation versus graph shape constraints).

    env\Scripts\python system\tools\ab5_shacl.py [RUN ...]

Every candidate Delta of the given runs has already passed or failed G1 = JSON schema + strict application + SHACL.
This counts, from the stored gate logs, the drafts and final candidates that G1 rejected only through SHACL (schema
and application passed), lists the violated shapes, and whether a rejected draft passed after its repair round. A
candidate rejected only by SHACL is what plain schema validation would have let through. Writes
docs/hasil/ab5_shacl.json.
"""
import glob
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ("e2-regulasi", "e2-pkb", "e2-pengecoh", "e2-regulasi-ulang", "e2-regulasi-m5", "e2-pkb-m5",
           "e2-kontrafaktual", "e2-sintetis", "e2-ab2-regulasi", "e2-ab2-pkb", "e2-model2-regulasi", "e2-model2-pkb")


def main():
    runs = sys.argv[1:] or DEFAULT
    counts, shapes, cases = Counter(), Counter(), []
    for run in runs:
        for p in sorted(glob.glob(str(ROOT / "experiments" / run / "results" / "*.json"))):
            r = json.loads(Path(p).read_text(encoding="utf-8"))
            for c in r.get("candidates", []):
                first = (c.get("first_gate_log") or {}).get("G1", "")
                final = (c.get("gate_log") or {}).get("G1", "")
                if first:
                    counts["drafts"] += 1
                if "SHACL" in first:
                    counts["drafts_rejected_by_shacl"] += 1
                    for part in first.split(";"):
                        if "SHACL" in part:
                            shapes[part.split(":", 2)[-1].strip()[:80]] += 1
                    cases.append({"run": run, "event": r["event"], "candidate": c["n"],
                                  "passed_after_repair": c.get("passed"), "message": first[:200]})
                if "SHACL" in final:
                    counts["final_rejected_by_shacl"] += 1
    out = {"runs": list(runs), "counts": dict(counts), "shapes": dict(shapes), "cases": cases}
    path = ROOT / "docs" / "hasil" / "ab5_shacl.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("counts", "shapes")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
