"""Engine development history for E1 (hindsight bias, PANDUAN Tahap 5): every commit that changed an engine, and the
regulation that motivated each engine capability.

    env\\Scripts\\python system\\tools\\export_engine_history.py

Writes docs/hasil/riwayat_engine.csv (one row per commit touching the prototype engine/ and kb/ or the new
system/pph21kbs/{engine,expr,kb}) and docs/hasil/fitur_engine.csv (capability, where it is implemented, the regulation
and event that motivated it, and the first commit that contains it). The point for E1: both engines were written in
2026, after every test event had been issued, so each capability is mapped to the event whose Delta needs it.
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "hasil"
LEGACY = ["engine", "kb"]
NEW = ["system/pph21kbs/engine", "system/pph21kbs/expr", "system/pph21kbs/kb"]
REG = re.compile(r"\b(PMK|PP|PER|UU|Perpres|PERPRES)[ -]?\d+[A-Z/.\-0-9]*", re.I)

# capability, file and pattern that implements it, motivating provision, event
FEATURES = [
    ("exact rational arithmetic, floats rejected", "system/pph21kbs/expr/numbers.py", "def decimal_value",
     "all tariffs (e.g. PP 58/2023 Lampiran, 0,25%)", "E03"),
    ("named rounding modes round(x, unit, mode)", "system/pph21kbs/expr/numbers.py", "half_even",
     "PER-16/PJ/2016 (truncate), PER-11/PJ/2025 Pasal 129 (half up)", "E13"),
    ("versioned parameters by valid and knowledge time", "system/pph21kbs/kb/store.py", "def effective",
     "BPJS JP wage cap letters (yearly), PER-11/PJ/2025 retroactive", "E01,E05,E08,E12,E13"),
    ("bracket tables with category key", "system/pph21kbs/expr/functions.py", '"bracket"',
     "PP 58/2023 Lampiran A-C (TER)", "E03"),
    ("progressive tables", "system/pph21kbs/expr/functions.py", '"progressive"', "UU 7/2021 Pasal 17", "-"),
    ("set tables and in_table", "system/pph21kbs/expr/functions.py", '"in_table"',
     "PMK 10/2025, 72/2025, 105/2025 Lampiran A (KLU)", "E06,E10,E11"),
    ("extracted tables (rows_ref)", "system/pph21kbs/kb/delta.py", "def default_table_resolver",
     "PMK 10/2025 Lampiran A (57 KLU), PP 58/2023 Lampiran", "E03,E06"),
    ("least fixed point for tax allowance", "system/pph21kbs/engine/evaluator.py", "def _fixed_point",
     "PMK 168/2023 Pasal 5 (tunjangan PPh), PMK 66/2023 (PPh ditanggung sebagai natura)", "E02,E04"),
    ("cumulative sums over months with an active rule", "system/pph21kbs/engine/evaluator.py", '"cumulative"',
     "PMK 66/2023 Lampiran A (annual caps from July 2023)", "E02"),
    ("year rules valid on the employment span", "system/pph21kbs/engine/evaluator.py", "def _valid",
     "PMK 72/2025 Pasal 4A (tourism Oct-Dec 2025)", "E10"),
    ("optional reads value_or/defined", "system/pph21kbs/expr/functions.py", '"value_or"',
     "PMK 72/2025 Pasal 4A, 5 ayat (5a)", "E10"),
    ("explicit overrides (lex specialis)", "system/pph21kbs/engine/evaluator.py", "lex specialis",
     "PMK 72/2025 (tourism facility), PMK 10/2025 Pasal 5 ayat (5)", "E06,E10"),
    ("lex posterior by valid_from and first recording", "system/pph21kbs/engine/evaluator.py", "lex posterior",
     "PP 58/2023 replacing PER-16 method", "E03,E04"),
    ("company layer per policy, mandatory beats company", "system/pph21kbs/engine/evaluator.py",
     "def _record_override", "PKB and company regulations against UU 13/2003, PP 36/2021", "policies"),
    ("constraints with conflict codes", "system/pph21kbs/engine/evaluator.py", "def check_constraints",
     "minimum wage and BPJS obligations (C8, C10)", "policies"),
    ("tombstones and closing validity", "system/pph21kbs/kb/delta.py", "Tombstone(",
     "PMK 168/2023 Pasal 24 revoking PMK 252/2008", "E04"),
]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                          check=True).stdout


def commits(paths):
    out = []
    for line in git("log", "--format=%H%x09%ad%x09%s", "--date=short", "--", *paths).splitlines():
        h, d, s = line.split("\t", 2)
        files = [f for f in git("show", "--name-only", "--format=", h).splitlines()
                 if any(f.startswith(p + "/") for p in paths)]
        out.append({"commit": h[:7], "tanggal": d, "pesan": s, "berkas_engine": len(files),
                    "regulasi_disebut": "; ".join(sorted({m.group(0) for m in REG.finditer(s)}))})
    return out


def first_commit(path, pattern):
    lines = git("log", "--reverse", "--format=%h %ad", "--date=short", "-S", pattern, "--", path).splitlines()
    return lines[0] if lines else "belum di-commit"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [dict(r, engine="prototipe") for r in commits(LEGACY)] + [dict(r, engine="baru") for r in commits(NEW)]
    with open(OUT / "riwayat_engine.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, ["engine", "commit", "tanggal", "berkas_engine", "regulasi_disebut", "pesan"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    feats = []
    for name, path, pattern, reg, event in FEATURES:
        if pattern not in (ROOT / path).read_text(encoding="utf-8"):
            sys.exit(f"pattern {pattern!r} not found in {path}: update FEATURES")
        feats.append({"kemampuan": name, "berkas": path, "regulasi_pemicu": reg, "peristiwa": event,
                      "commit_pertama": first_commit(path, pattern)})
    with open(OUT / "fitur_engine.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(feats[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(feats)
    print(f"{len(rows)} commits ({sum(r['engine'] == 'prototipe' for r in rows)} prototype), {len(feats)} capabilities")


if __name__ == "__main__":
    main()
