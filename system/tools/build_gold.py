"""Build the gold chain dataset/12_emas from system/gold_src (akuisisi.md section 1).

    env\\Scripts\\python system\\tools\\build_gold.py            # build, validate, write
    env\\Scripts\\python system\\tools\\build_gold.py --check    # build and validate only

Updates are applied in chain order (recorded_on, then module order). Every Delta is validated against the JSON schema,
applied strictly, and its quotes are checked against dataset/13_teks. Output: dataset/12_emas/delta/<id>.json,
dataset/12_emas/rantai.csv, dataset/12_emas/kosakata.md, the knowledge graph dataset/12_emas/kb.trig (one named graph
per update, read back by the engine through pph21kbs.kb.rdf), and the fingerprint of the final knowledge base.
"""
import csv
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))

from pph21kbs.kb import apply_delta, empty_kb, rdf  # noqa: E402

MODULES = ["bg_base", "bg_2015_2022", "ev_jp", "ev_natura", "ev_ter", "ev_dtp", "ev_jkk", "ev_rounding"]
OUT = ROOT / "dataset" / "12_emas"


def collect():
    updates = []
    for i, name in enumerate(MODULES):
        try:
            mod = importlib.import_module(f"gold_src.{name}")
        except ModuleNotFoundError as e:
            if e.name == f"gold_src.{name}":
                continue
            raise
        for j, u in enumerate(mod.UPDATES):
            updates.append((u.recorded_on or u.doc.issued, i, j, u))
    updates.sort(key=lambda t: t[:3])
    return [t[3] for t in updates]


def build(check_only=False):
    updates = collect()
    kb = empty_kb("K*")
    rows = []
    for u in updates:
        d = u.to_json()
        kb = apply_delta(kb, d)
        n_add, n_change, n_remove = len(d["add"]), len(d["change"]), len(d["remove"])
        rows.append({"seq": len(rows) + 1, "update_id": u.delta_id, "kind": u.kind, "event_id": u.event_id or "",
                     "document": u.doc.id, "recorded_on": u.recorded_on or u.doc.issued, "add": n_add,
                     "change": n_change, "remove": n_remove, "file": f"delta/{u.delta_id}.json"})
        if not check_only:
            (OUT / "delta").mkdir(parents=True, exist_ok=True)
            (OUT / "delta" / f"{u.delta_id}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                                                              encoding="utf-8")
    if not check_only:
        with open(OUT / "rantai.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        write_vocabulary(kb)
        rdf.write_trig(kb, OUT / "kb.trig")
    print(f"{len(rows)} updates, {len(kb.records)} records, fingerprint {kb.fingerprint()[:16]}")
    return kb


def load_graph():
    """The gold knowledge base read from the knowledge graph written by build()."""
    return rdf.read_trig(OUT / "kb.trig", "K*")


def write_vocabulary(kb):
    from datetime import date
    view = kb.view(date(2099, 12, 31))
    lines = ["# Kosakata KB emas", "", "Dihasilkan oleh `system/tools/build_gold.py`. Fakta bertanda keluaran membentuk "
             "$F_\\mathit{nilai}$ (dibekukan, representasi.md bagian 4).", "",
             "| Fakta | Tipe | Lingkup | Keluaran | Label | Label Indonesia |", "|---|---|---|---|---|---|"]
    for f in sorted(view.facts.values(), key=lambda f: (not f.output, f.fact_scope, f.id)):
        lines.append(f"| `{f.id}` | {f.fact_type} | {f.fact_scope} | {'ya' if f.output else ''} | {f.label} | {f.label_id} |")
    (OUT / "kosakata.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build("--check" in sys.argv)
