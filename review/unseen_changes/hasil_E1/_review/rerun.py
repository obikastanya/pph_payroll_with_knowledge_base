r"""Independent re-run of E1 using the executor's own scripts in ../_alat, writing only into this folder.

Variants: main (KONVENSI.json), no_premium (percobaan/KONVENSI_v1.json = only pph_round_mode), none (no convention).
Usage (from repo root): env\Scripts\python review\unseen_changes\hasil_E1\_review\rerun.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALAT = HERE.parent / "_alat"
sys.path.insert(0, str(ALAT))

import run_e1  # noqa: E402
from pph21kbs.analysis.stats import clopper_pearson, upper_bound  # noqa: E402

orig_load = run_e1.load
VARIANTS = {"utama": ("KONVENSI", True), "tanpa_premi": ("KONVENSI_v1", True), "tanpa_konvensi": (None, False)}


def make_load(konv):
    def load(name):
        if name == "KONVENSI" and konv == "KONVENSI_v1":
            return json.loads((ALAT / "percobaan" / "KONVENSI_v1.json").read_text(encoding="utf-8"))
        return orig_load(name)
    return load


def main():
    summary = {}
    for var, (konv, use) in VARIANTS.items():
        run_e1.load = make_load(konv)
        outdir = HERE / var
        outdir.mkdir(exist_ok=True)
        k, n_ex, n_ok, fails = 0, 0, 0, {}
        for i in range(1, 17):
            uid = f"U{i:02d}"
            res = run_e1.run(uid, do_shacl=True, konvensi=use)
            (outdir / f"{uid}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str) + "\n",
                                                encoding="utf-8")
            ok = sum(e["ok"] for e in res["examples"])
            tot = len(res["examples"])
            succ = res["apply"] == "ok" and res["shacl"] == "ok" and not res["g3_errors"] and ok == tot
            k += succ
            n_ex += tot
            n_ok += ok
            if not succ:
                fails[uid] = {"apply": res["apply"], "shacl": res["shacl"] if res["shacl"] != "ok" else "ok",
                              "g3": res["g3_errors"][:3],
                              "bad": [(e["id"], e["diffs"][:3]) for e in res["examples"] if not e["ok"]]}
            print(var, uid, "ok" if succ else "FAIL", f"{ok}/{tot}", flush=True)
        lo, hi = clopper_pearson(k, 16)
        lb = 1 - upper_bound(16 - k, 16)
        summary[var] = {"RA": f"{k}/16", "CP95": [round(lo, 4), round(hi, 4)], "lower_one_sided": round(lb, 4),
                        "H1": lb >= 0.70, "examples": f"{n_ok}/{n_ex}", "failures": fails}
        print(var, summary[var]["RA"], summary[var]["CP95"], summary[var]["lower_one_sided"], flush=True)
    (HERE / "rerun_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, default=str) + "\n",
                                             encoding="utf-8")


if __name__ == "__main__":
    main()
