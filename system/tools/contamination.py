r"""Data contamination analysis (skeleton: threats to validity; prareg amendment 1, exploratory).

    env\Scripts\python system\tools\contamination.py

1. Cutoff split: test events (regulation and PKB) issued before or after the training cutoff of each model
   (dataset/09_korpus_peristiwa/model_cutoff.csv).
2. Memorisation on counterfactual documents (experiments/e2-kontrafaktual): for every candidate, whether its Delta
   carries the original value of the real document (memorised), the replaced value (read), or neither, and the outcome
   of the selected update on the counterfactual S^E (experiments/e2-kontrafaktual/scores.csv, from score_run.py).
Writes docs/hasil/kontaminasi.json.
"""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))

from pph21kbs import corpus  # noqa: E402


def _number(s):
    m = re.search(r"\d{1,3}(?:\.\d{3})+", s)
    return m.group(0) if m else None


def _forms(text):
    """A value as written ("9.559.600") and as digits ("9559600"), or a date phrase as written."""
    n = _number(text)
    return {n, n.replace(".", "")} if n else {text.strip()}


def main():
    cut = {r["model"]: date.fromisoformat(r["training_cutoff"] + ("-01" if len(r["training_cutoff"]) == 7 else ""))
           for r in csv.DictReader(open(ROOT / "dataset/09_korpus_peristiwa/model_cutoff.csv", encoding="utf-8"))}
    events = [e for e in corpus.regulation_events() if e.part == "uji"] + \
             [e for e in corpus.policy_events() if e.part == "uji"]
    split = {m: {"before": [e.id for e in events if e.issued < c], "after": [e.id for e in events if e.issued >= c]}
             for m, c in cut.items()}
    out = {"cutoff": {m: c.isoformat() for m, c in cut.items()}, "split": split}
    cf_dir = ROOT / "experiments" / "e2-kontrafaktual"
    scores = {}
    if (cf_dir / "scores.csv").exists():
        scores = {r["event"]: r["outcome"] for r in csv.DictReader(open(cf_dir / "scores.csv", encoding="utf-8"))
                  if r["condition"] == "proposed"}
    rows = []
    for ev in corpus.counterfactual_events():
        path = cf_dir / "results" / f"{ev.id}.json"
        if not path.exists():
            continue
        res = json.loads(path.read_text(encoding="utf-8"))
        olds = [x for part in ev.extra["asli"].split("|") for x in _forms(part)]
        news = [x for part in ev.extra["pengganti"].split("|") for x in _forms(part)]
        cands = []
        for c in res.get("candidates", []):
            d = c.get("delta") or c.get("llm")
            if d is None:
                continue
            text = json.dumps({k: v for k, v in d.items() if k in ("add", "change", "fields")}, ensure_ascii=False)
            text = re.sub(r'"quote": "(?:[^"\\]|\\.)*"', "", text)       # values only, not the quotes
            has_old = any(o and re.search(rf"(?<![\d.]){re.escape(o)}(?![\d])", text) for o in olds)
            has_new = any(n and re.search(rf"(?<![\d.]){re.escape(n)}(?![\d])", text) for n in news)
            cands.append({"n": c["n"], "original_value": has_old, "replaced_value": has_new, "passed": c["passed"]})
        rows.append({"event": ev.id, "source": ev.extra["sumber"], "kind": ev.extra["jenis_ubahan"],
                     "status": res.get("status"), "outcome": scores.get(ev.id), "candidates": cands,
                     "memorised": sum(c["original_value"] and not c["replaced_value"] for c in cands),
                     "read": sum(c["replaced_value"] for c in cands)})
    out["counterfactual"] = rows
    out["memorisation_rate"] = (sum(r["memorised"] for r in rows) / max(1, sum(len(r["candidates"]) for r in rows)))
    (ROOT / "docs" / "hasil" / "kontaminasi.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                             encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main()
