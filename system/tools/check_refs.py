"""Compare the gold chain with reference cases (E0 development check; holdout cases are not used here).

    env\\Scripts\\python system\\tools\\check_refs.py gt3 [year] [omega] [--source]
    env\\Scripts\\python system\\tools\\check_refs.py gt1        # GT1 development cases (official worked examples)
    env\\Scripts\\python system\\tools\\check_refs.py gt2        # GT2 DJP calculator (monthly and annual)
    env\\Scripts\\python system\\tools\\check_refs.py all --write

By default the knowledge base is read from the knowledge graph dataset/12_emas/kb.trig; --source builds it from
system/gold_src instead (for authoring, before the graph is written). --write saves every compared observation to
docs/hasil/acuan_<ref>.csv with the reason of each known difference.
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_gold  # noqa: E402
from pph21kbs.config import REPO  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402
from pph21kbs.refs import GT1_DIR, Unsupported, compare, gt1_case, gt3_case, load_gt1_dev, load_gt3  # noqa: E402

OMEGA = date(2026, 10, 27)
OUT = REPO / "docs" / "hasil"
GT2_DIR = REPO / "dataset" / "11_acuan" / "gt2_kalkulator_djp"


def _kb(from_source=False):
    return build_gold.build(check_only=True) if from_source else build_gold.load_graph()


def _write(name, rows):
    if not rows:
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"acuan_{name}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def _key_text(k):
    return f"{k[1]}:{k[2]}" if k[0] == "period" else f"tahunan:{k[1] if not isinstance(k[1], tuple) else '|'.join(k[1])}"


def gt3(year=None, omega=OMEGA, verbose=True, kb=None, rows=None):
    kb = kb or _kb()
    ok = total = obs = bad = 0
    for d in load_gt3():
        if year and d["tahun_pajak"] != year:
            continue
        case, exp = gt3_case(d)
        r, diffs = compare(kb, case, exp, omega)
        total += 1
        obs += len(exp)
        bad += len(diffs)
        if rows is not None:
            wrong = {k for k, _, _ in diffs}
            from pph21kbs.refs import observe
            for k, v in exp.items():
                rows.append({"kasus": d["id"], "tahun": d["tahun_pajak"], "observasi": _key_text(k),
                             "engine": observe(r, k), "acuan": v, "sama": k not in wrong, "penjelasan": ""})
        if not diffs and not r.errors:
            ok += 1
        elif verbose:
            print(d["id"], d["tahun_pajak"], d["uraian"][:80])
            if r.errors:
                print("   errors", r.errors[:3])
            for k, got, want in diffs[:8]:
                print(f"   {k}: engine {got} reference {want}")
    print(f"GT3: {ok}/{total} cases equal; {obs - bad}/{obs} observations equal")
    return ok, total, obs - bad, obs


def _gt1_errata():
    """dugaan_erratum of the development transcriptions (holdout files are not opened)."""
    from pph21kbs.refs import gt1_split
    out = {}
    for name, part in gt1_split().items():
        if part == "pengembangan":
            d = json.loads((GT1_DIR / name).read_text(encoding="utf-8"))
            if d.get("dugaan_erratum"):
                out[d["id"]] = d["dugaan_erratum"]
    return out


def gt1(verbose=True, kb=None, rows=None):
    kb = kb or _kb()
    errata = _gt1_errata()
    ok = total = obs = bad = explained = 0
    skipped = []
    for c in load_gt1_dev():
        try:
            case, exp, _ = gt1_case(c)
        except Unsupported as e:
            skipped.append((c["id"], str(e)))
            continue
        r, diffs = compare(kb, case, exp, OMEGA)
        total += 1
        obs += len(exp)
        bad += len(diffs)
        note = errata.get(c["id"].replace("PP58-Penj-Ps2-1", "PP58-Penj-Ps2-1"), "")
        if diffs and note:
            explained += len(diffs)
        if rows is not None:
            wrong = {k for k, _, _ in diffs}
            from pph21kbs.refs import observe
            for k, v in exp.items():
                rows.append({"kasus": c["id"], "tahun": c["tahun_pajak"], "observasi": _key_text(k),
                             "engine": observe(r, k), "acuan": v, "sama": k not in wrong,
                             "penjelasan": f"ralat contoh resmi: {note}" if k in wrong and note else ""})
        if not diffs and not r.errors:
            ok += 1
        elif verbose:
            print(c["id"], c["tahun_pajak"], "ralat contoh resmi:" if note else "", note[:110])
            for k, got, want in diffs[:6]:
                print(f"   {k}: engine {got} reference {want}")
    print(f"GT1 dev: {ok}/{total} cases equal; {obs - bad}/{obs} observations equal; "
          f"{explained}/{bad} differences are documented errata of the official example")
    print("   outside the case model:", "; ".join(f"{i} ({why})" for i, why in skipped))
    return ok, total, obs - bad, obs


def _gt2_month_case(gid, ptkp, bruto, scheme):
    return {"case_id": gid, "tax_year": 2026, "method": "gross_up" if scheme == "Gross Up" else "gross",
            "employee": {"ptkp_status": ptkp, "sex": "M", "tax_id_valid": True},
            "employer": {"klu": None, "jkk_risk_group": "very_low", "premiums_as_billed": True, "policy": None},
            "employment": {"start_month": 1, "end_month": 12},
            "periods": [{"month": m, "income": {"base_salary": bruto}} for m in range(1, 13)]}


def gt2(verbose=True, kb=None, rows=None):
    """Monthly: PPh 21 of a non-final TER month for the gross and gross-up amounts entered in the DJP calculator.
    Annual: the A1 lines of the calculator against the KB on the GT3 case each GT2 case was taken from."""
    kb = kb or _kb()
    with open(GT2_DIR / "hasil.csv", encoding="utf-8") as f:
        monthly = list(csv.DictReader(f))
    with open(GT2_DIR / "perbandingan.csv", encoding="utf-8") as f:
        verdict = {r["gt2_id"]: r["putusan"] for r in csv.DictReader(f)}
    m_ok = m_bad = m_expl = 0
    for h in monthly:
        case = _gt2_month_case(h["gt2_id"], h["ptkp"], int(h["bruto_diisi"]), h["skema"])
        r = evaluate_case(kb, case, OMEGA)
        got, want = r.periods[1]["pph21_due"], int(h["pph21"])
        same = got == want
        m_ok += same
        m_bad += not same
        why = verdict.get(h["gt2_id"], "") if not same else ""
        m_expl += bool(why)
        if rows is not None:
            rows.append({"kasus": h["gt2_id"], "tahun": 2026, "observasi": "1:pph21_due", "engine": got, "acuan": want,
                         "sama": same, "penjelasan": why})
        if not same and verbose:
            print(f"   {h['gt2_id']} {h['skema']} {h['ptkp']} {h['bruto_diisi']}: engine {got} DJP {want}  {why[:70]}")
    print(f"GT2 monthly: {m_ok}/{m_ok + m_bad} equal; {m_expl}/{m_bad} differences adjudicated (rounding, PER-11)")
    with open(GT2_DIR / "hasil_tahunan.csv", encoding="utf-8") as f:
        annual = list(csv.DictReader(f))
    with open(GT2_DIR / "rencana_tahunan.csv", encoding="utf-8") as f:
        source = {r["gt2_id"]: r["sumber"].split()[0] for r in csv.DictReader(f)}
    gt3s = {d["id"]: d for d in load_gt3()}
    lines = {"b8": "annual_gross", "b15": "annual_net", "b16": "ptkp_amount", "b17": "taxable_income",
             "b18": "annual_pph21", "b20": "final_period_tax"}
    a_ok = a_all = 0
    for h in annual:
        case, _ = gt3_case(gt3s[source[h["gt2_id"]]])
        r = evaluate_case(kb, case, OMEGA, outputs=list(lines.values()))
        for line, fact in lines.items():
            got, want = r.year.get(fact), int(h[line])
            a_all += 1
            a_ok += got == want
            if rows is not None:
                rows.append({"kasus": h["gt2_id"], "tahun": case["tax_year"], "observasi": f"tahunan:{fact}",
                             "engine": got, "acuan": want, "sama": got == want, "penjelasan": ""})
            if got != want and verbose:
                print(f"   {h['gt2_id']} {line} {fact}: engine {got} DJP {want}")
    print(f"GT2 annual: {a_ok}/{a_all} A1 lines equal")
    return m_ok, m_ok + m_bad, a_ok, a_all


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    which = args[0] if args else "gt3"
    write = "--write" in sys.argv
    kb = _kb("--source" in sys.argv)
    if which in ("gt3", "all"):
        rows = [] if write else None
        year = int(args[1]) if which == "gt3" and len(args) > 1 else None
        omega = date.fromisoformat(args[2]) if which == "gt3" and len(args) > 2 else OMEGA
        gt3(year, omega, kb=kb, rows=rows)
        if write:
            _write("gt3", rows)
    if which in ("gt1", "all"):
        rows = [] if write else None
        gt1(kb=kb, rows=rows)
        if write:
            _write("gt1_pengembangan", rows)
    if which in ("gt2", "all"):
        rows = [] if write else None
        gt2(kb=kb, rows=rows)
        if write:
            _write("gt2", rows)
