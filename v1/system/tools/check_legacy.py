"""Equivalence check of the new engine against the prototype engine (Tahap 5, "Periksa kesetaraan").

    env\\Scripts\\python system\\tools\\check_legacy.py [--write]

The prototype (engine/ + kb/, frozen at tag prototipe-akhir) is run unchanged on the same cases: GT3 (all 50) and the
GT1 development cases (holdout never opened). Each value the prototype reports is compared with the new engine reading
the gold knowledge graph. A difference is explained when the GT3 adjudication (dataset/11_acuan/diferensial_gt3.csv,
column putusan) or the GT1 transcription (dugaan_erratum) already decided it, or when the new engine equals the
reference and the prototype does not. --write saves the rows to docs/hasil/kesetaraan_engine_lama.csv.
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))
sys.path.insert(0, str(ROOT / "dataset" / "11_acuan"))

import build_gold  # noqa: E402
from diferensial_gt3_engine_lama import kanonik as gt3_kanonik  # noqa: E402
from engine.kalkulator import hitung  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402
from pph21kbs.refs import GT1_DIR, Unsupported, gt1_case, gt3_case, load_gt1_dev, load_gt3  # noqa: E402

OMEGA = date(2026, 10, 27)
PERIOD = {"bruto": "gross_income", "pph21": "pph21_due", "pph21_dtp": "pph21_dtp"}
YEAR = {"pkp": "taxable_income", "pph21_setahun": "annual_pph21", "pph21_masa_terakhir": "final_period_tax"}
OUTPUTS = sorted(set(PERIOD.values()) | set(YEAR.values()))


def _irregular(case):
    return {p["month"]: sum(v for k, v in (p.get("income") or {}).items() if k in ("thr", "bonus", "other_irregular"))
            for p in case["periods"]}


def _rows_for(source, case_id, legacy, new, reference, verdicts, case):
    rows = []
    irregular = _irregular(case)
    for m, got in sorted(legacy["per_masa"].items()):
        for k, f in PERIOD.items():
            if k not in got and k != "pph21_dtp":
                continue
            old = got.get(k, 0)
            nv = (new.periods.get(m) or {}).get(f)
            ref = reference.get(("period", m, f))
            why = verdicts.get((case_id, str(m), k), "") or _known(k, old, nv, irregular.get(m, 0), case)
            rows.append(_row(source, case_id, m, k, old, nv, ref, why))
    for k, f in YEAR.items():
        if k not in legacy["tahunan"]:
            continue
        old, nv = legacy["tahunan"][k], new.year.get(f)
        ref = reference.get(("year", f))
        rows.append(_row(source, case_id, "tahunan", k, old, nv, ref, verdicts.get((case_id, "tahunan", k), "")))
    return rows


def _known(fact, old, new, irregular, case):
    """Differences of a kind the GT3 adjudication already decided, recognised by their shape."""
    if old is None or new is None or old == new:
        return ""
    if fact == "bruto" and irregular and new - old == irregular:
        return "definisi bruto masa termasuk penghasilan tidak teratur (tafsir K14)"
    if fact == "pph21" and abs(new - old) == 1 and case["tax_year"] < 2024:
        return "PPh setahun dibagi bulan dibulatkan ke bawah (tafsir K2)"
    return ""


def _row(source, case_id, month, fact, old, new, ref, verdict):
    same = old == new
    if same:
        why = ""
    elif verdict:
        why = verdict
    elif ref is not None and new == ref:
        why = "engine baru sama dengan acuan"
    else:
        why = "BELUM DIJELASKAN"
    return {"sumber": source, "kasus": case_id, "bulan": month, "fakta": fact, "engine_lama": old, "engine_baru": new,
            "acuan": "" if ref is None else ref, "sama": same, "penjelasan": why}


def gt3_rows(kb):
    verdicts = {}
    with open(ROOT / "dataset" / "11_acuan" / "diferensial_gt3.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["putusan"]:
                verdicts[(r["id"], r["bulan"], r["fakta"])] = f"putusan GT3: {r['putusan']}"
    rows, refused = [], []
    for d in load_gt3():
        case, expected = gt3_case(d)
        new = evaluate_case(kb, case, OMEGA, outputs=OUTPUTS)
        try:
            legacy = hitung(gt3_kanonik(d))
        except Exception as e:  # noqa: BLE001 - a refusal of the prototype is reported
            refused.append((d["id"], f"{type(e).__name__}: {e}"[:120]))
            continue
        # GT3 states only some months; the prototype reports every month. Compare the months GT3 states.
        months = {k[1] for k in expected if k[0] == "period"}
        legacy = {"per_masa": {m: v for m, v in legacy["per_masa"].items() if m in months},
                  "tahunan": legacy["tahunan"] if d["expected"].get("tahunan") else {}}
        ref = dict(expected)
        t = d["expected"].get("tahunan") or {}
        if t.get("pph21_masa_terakhir") is not None:
            ref[("year", "final_period_tax")] = t["pph21_masa_terakhir"]
        rows += _rows_for("GT3", d["id"], legacy, new, ref, verdicts, case)
    return rows, refused


def gt1_rows(kb):
    rows, refused, skipped = [], [], []
    for c in load_gt1_dev():
        src = GT1_DIR / (c["id"].replace("-", "_", 1).replace("PP58_Penj-Ps2-1", "PP58_Penj_Ps2_1") + ".json")
        note = ""
        if src.exists():
            note = json.loads(src.read_text(encoding="utf-8")).get("dugaan_erratum") or ""
        try:
            case, expected, _ = gt1_case(c)
        except Unsupported as e:
            skipped.append((c["id"], str(e)))
            continue
        new = evaluate_case(kb, case, OMEGA, outputs=OUTPUTS)
        try:
            legacy = hitung(c)
        except Exception as e:  # noqa: BLE001
            refused.append((c["id"], f"{type(e).__name__}: {e}"[:120]))
            continue
        stated = {m["bulan"] for m in c["masa"]}
        legacy = {"per_masa": {m: v for m, v in legacy["per_masa"].items() if m in stated},
                  "tahunan": legacy["tahunan"] if c["cakupan"] == "setahun" else {}}
        verdicts = {}
        if note:
            for m in list(stated) + ["tahunan"]:
                for k in list(PERIOD) + list(YEAR):
                    verdicts[(c["id"], str(m), k)] = f"ralat contoh resmi ({note[:60]})"
        rows += _rows_for("GT1", c["id"], legacy, new, expected, verdicts, case)
    return rows, refused, skipped


def main(write=False):
    kb = build_gold.load_graph()
    r3, ref3 = gt3_rows(kb)
    r1, ref1, skip1 = gt1_rows(kb)
    rows = r3 + r1
    for name, part in (("GT3", r3), ("GT1 dev", r1)):
        same = sum(r["sama"] for r in part)
        print(f"{name}: {len(part)} nilai, {same} sama dengan engine lama, {len(part) - same} berbeda")
        groups = {}
        for r in part:
            if not r["sama"]:
                groups.setdefault(r["penjelasan"].split(" (")[0], set()).add(r["kasus"])
        for why, cases in sorted(groups.items()):
            n = sum(1 for r in part if not r["sama"] and r["penjelasan"].split(" (")[0] == why)
            print(f"   {n:4d}  {why}: {', '.join(sorted(cases))}")
    print("engine lama menolak:", ref3 + ref1)
    print("di luar model kasus baru (tidak dibandingkan):", skip1)
    if write:
        out = ROOT / "docs" / "hasil" / "kesetaraan_engine_lama.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print("ditulis", out.relative_to(ROOT))


if __name__ == "__main__":
    main("--write" in sys.argv)
