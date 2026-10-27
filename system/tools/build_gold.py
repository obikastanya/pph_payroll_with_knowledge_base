"""Build the gold chain dataset/12_emas from system/gold_src (akuisisi.md section 1).

    env\\Scripts\\python system\\tools\\build_gold.py            # build, validate, write
    env\\Scripts\\python system\\tools\\build_gold.py --check    # build and validate only

Main chain: UPDATES of every module (background, test events, development events), applied in chain order
(recorded_on, then module order). Every Delta is validated against the JSON schema, applied strictly, and its quotes
are checked against dataset/13_teks. Side updates: SIDE_UPDATES of a module are not part of the chain. A fictive
regulation (kind "event", development only) is applied to the chain prefix known at its issue date; a company policy
(kind "policy") is installed on the final chain, and on any K*_n by the experiments (RQ4).

Output: dataset/12_emas/delta/<id>.json for every update, rantai.csv (main chain), sisi.csv (side updates and the
prefix each was validated on), kosakata.md, the knowledge graph kb.trig (one named graph per update, read back by the
engine through pph21kbs.kb.rdf), and the fingerprint of the final knowledge base.
"""
import csv
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))

from pph21kbs.kb import apply_delta, empty_kb, rdf  # noqa: E402

MODULES = ["bg_base", "bg_2015_2022", "bg_support", "dev_ptkp_jkn", "dev_covid", "ev_jp", "ev_natura", "ev_ter", "ev_dtp",
           "ev_jkk", "ev_rounding", "fr_fiktif", "pol_sintetis", "pol_pkb"]
OUT = ROOT / "dataset" / "12_emas"


def _modules():
    for i, name in enumerate(MODULES):
        try:
            yield i, importlib.import_module(f"gold_src.{name}")
        except ModuleNotFoundError as e:
            if e.name == f"gold_src.{name}":
                continue
            raise


def collect():
    updates = []
    for i, mod in _modules():
        for j, u in enumerate(mod.UPDATES):
            updates.append((u.recorded_on or u.doc.issued, i, j, u))
    updates.sort(key=lambda t: t[:3])
    return [t[3] for t in updates]


def collect_side():
    return [u for _, mod in _modules() for u in getattr(mod, "SIDE_UPDATES", [])]


def _write_delta(d):
    (OUT / "delta").mkdir(parents=True, exist_ok=True)
    (OUT / "delta" / f"{d['delta_id']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                                                        encoding="utf-8")


def prefix_at(kb, date_text):
    """The chain prefix whose updates were recorded on or before the date (the knowledge base an update of that
    date would be acquired against)."""
    last = None
    for u in kb.updates:
        if u.recorded_on is not None and u.recorded_on.isoformat() <= date_text:
            last = u.update_id
    return kb.until(last) if last else empty_kb(kb.name)


def apply_side(kb, u):
    """(base update id, K' = base (+) side update). Policies go on the given chain, fictive regulations on its
    prefix at their issue date."""
    d = u.to_json()
    base = kb if u.kind == "policy" else prefix_at(kb, u.recorded_on or u.doc.issued)
    # a side update may name other side updates it is applied on top of (base_side), e.g. a fictive background
    for sid in getattr(u, "base_side", ()):
        base = apply_delta(base, side_update(sid).to_json())
    base_id = base.updates[-1].update_id if base.updates else ""
    return base_id, apply_delta(base, d)


def build(check_only=False, side=True):
    updates = collect()
    kb = empty_kb("K*")
    rows = []
    for u in updates:
        d = u.to_json()
        kb = apply_delta(kb, d)
        rows.append({"seq": len(rows) + 1, "update_id": u.delta_id, "kind": u.kind, "event_id": u.event_id or "",
                     "document": u.doc.id, "recorded_on": u.recorded_on or u.doc.issued, "add": len(d["add"]),
                     "change": len(d["change"]), "remove": len(d["remove"]), "file": f"delta/{u.delta_id}.json"})
        if not check_only:
            _write_delta(d)
    side_rows = []
    if side:
        for u in collect_side():
            base_id, _ = apply_side(kb, u)
            d = u.to_json()
            side_rows.append({"update_id": u.delta_id, "kind": u.kind, "event_id": u.event_id or "",
                              "document": u.doc.id, "recorded_on": u.recorded_on or u.doc.issued, "base": base_id,
                              "add": len(d["add"]), "change": len(d["change"]), "remove": len(d["remove"]),
                              "file": f"delta/{u.delta_id}.json"})
            if not check_only:
                _write_delta(d)
    if not check_only:
        _write_csv(OUT / "rantai.csv", rows)
        if side_rows:
            _write_csv(OUT / "sisi.csv", side_rows)
        write_vocabulary(kb)
        rdf.write_trig(kb, OUT / "kb.trig")
    print(f"{len(rows)} updates, {len(kb.records)} records, fingerprint {kb.fingerprint()[:16]}"
          + (f"; {len(side_rows)} side updates valid" if side_rows else ""))
    return kb


def _write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def load_graph():
    """The gold knowledge base read from the knowledge graph written by build()."""
    return rdf.read_trig(OUT / "kb.trig", "K*")


def side_update(update_id):
    for u in collect_side():
        if u.delta_id == update_id:
            return u
    raise KeyError(update_id)


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
