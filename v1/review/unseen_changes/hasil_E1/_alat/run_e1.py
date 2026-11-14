"""E1 runner: for each change, apply KONVENSI and the change Delta (strict) to the fitting base, run SHACL (G1) and the
static checker (G3), convert every worked example, evaluate at a knowledge date after the change, and compare every
stated value.

Usage: python run_e1.py [U01 ...] [--no-shacl] [--no-konvensi]
Writes ../detail/<id>.json (per example: stated values, engine values, differences).
"""
import json
import sys
import time
from datetime import date

from common import OUT, base_at
from pph21kbs import static
from pph21kbs.kb import apply_delta, shacl
import convert
from run_eval import evaluate

U15_COMPONENTS = {"gaji_pokok": "base_salary", "tunjangan_tetap": "fixed_allowance", "premi_jkk": "jkk_premium",
                  "premi_jkm": "jkm_premium", "premi_jkn": "health_premium_employer",
                  "iuran_jht_pegawai": "jht_employee", "iuran_jp_pegawai": "jp_employee", "rapel_gaji": "back_pay",
                  "rapel_premi_jkk": "jkk_back_premium", "rapel_premi_jkm": "jkm_back_premium",
                  "rapel_premi_jkn": "health_back_premium"}
CASE = {
    "U06": {"year_extra": {"kelebihan_dtp_tidak_dikembalikan": "dtp_excess_not_refunded"}},
    "U14": {"policy": "UNSEEN-U14", "method": "gross",
            "year_extra": {"lebih_potong_menjadi_hak_perusahaan": "excess_retained_by_company"}},
    "U15": {"policy": "UNSEEN-U15", "period_extra": {"komponen_setelah_pkb": U15_COMPONENTS}},
}


def load(name):
    return json.loads((OUT / "delta" / f"{name}.json").read_text(encoding="utf-8"))


def run(uid, do_shacl=True, konvensi=True):
    t0 = time.time()
    delta = load(uid)
    issued = delta["document"]["issued"]
    out = {"id": uid, "issued": issued, "apply": None, "shacl": None, "g3_errors": [], "g3_warnings": [],
           "examples": []}
    kb = base_at(issued)
    out["base"] = kb.updates[-1].update_id
    if konvensi:
        kb = apply_delta(kb, load("KONVENSI"))
    try:
        kb2 = apply_delta(kb, delta)          # strict: validate schema, no lenient adjustments
        out["apply"] = "ok"
    except Exception as e:                    # UpdateError, jsonschema.ValidationError
        out["apply"] = f"{type(e).__name__}: {e}"
        return out
    omega = date.fromisoformat(issued)
    cfg = CASE.get(uid, {})
    policy = cfg.get("policy")
    if do_shacl:
        docs = shacl.corpus_documents() + [f"UNSEEN-{uid}", "UNSEEN-KONVENSI"]
        v = shacl.validate(kb2, docs)
        out["shacl"] = "ok" if not v else [f"{a}: {b}" for a, b in v[:30]]
    rep = static.check(kb2, omega, policies=(policy,) if policy else ())
    out["g3_errors"] = [f"{f.kind} {', '.join(f.ids)} {f.fact}: {f.detail}" for f in rep.errors]
    new_ids = {e["id"] for e in delta["add"] + delta["change"]}
    out["g3_warnings"] = [f"{f.kind} {', '.join(f.ids)} {f.fact}: {f.detail}" for f in rep.warnings
                          if set(f.ids) & new_ids]
    for ex in convert.load(uid)["contoh"]:
        case, stated = convert.to_case(ex, policy=policy, method=cfg.get("method"))
        exp = convert.expected(ex["keluaran_diharapkan"], cfg.get("period_extra"), cfg.get("year_extra"))
        try:
            r, diffs = evaluate(kb2, omega, case, exp)
            errs, warns = r.errors, r.warnings
        except Exception as e:
            diffs, errs, warns = [(("crash",), str(e), None)], [f"{type(e).__name__}: {e}"], []
        # control: the same example on the base without the change Delta
        try:
            r0, diffs0 = evaluate(kb, omega, case, exp)
            ok0 = not diffs0 and not r0.errors
        except Exception:
            ok0 = False
        out["examples"].append({"id": ex["id"], "berpengaruh": ex.get("perubahan_berpengaruh"), "n_values": len(exp),
                                "ok": not diffs and not errs, "ok_without_delta": ok0,
                                "diffs": [[list(k), a, b] for k, a, b in diffs], "errors": errs, "warnings": warns})
    out["seconds"] = round(time.time() - t0, 1)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ids = args or [f"U{i:02d}" for i in range(1, 17)]
    (OUT / "detail").mkdir(exist_ok=True)
    for uid in ids:
        res = run(uid, do_shacl="--no-shacl" not in sys.argv, konvensi="--no-konvensi" not in sys.argv)
        (OUT / "detail" / f"{uid}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str) + "\n",
                                                    encoding="utf-8")
        ok = sum(e["ok"] for e in res["examples"])
        ctrl = [(e["id"][4:], e["berpengaruh"], e["ok_without_delta"]) for e in res["examples"]]
        bad_ctrl = [c for c in ctrl if c[1] == c[2]]      # affected but passes without Delta, or unaffected but fails
        print(f"{uid}: apply={res['apply']} shacl={'ok' if res['shacl'] == 'ok' else res['shacl']} "
              f"G3err={len(res['g3_errors'])} examples {ok}/{len(res['examples'])} ({res.get('seconds')}s) "
              f"control-mismatch={bad_ctrl}")
        for e in res["g3_errors"][:5]:
            print("   G3", e)
        for e in res["g3_warnings"][:6]:
            print("   G3w", e)
        for ex in res["examples"]:
            if not ex["ok"]:
                print("   ", ex["id"], "diffs", len(ex["diffs"]), ex["diffs"][:4], ex["errors"][:2])


if __name__ == "__main__":
    main()
