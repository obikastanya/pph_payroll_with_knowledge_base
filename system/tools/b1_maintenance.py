"""Baseline B1: how hand-coded open-source PPh 21 calculators followed the switch to TER (PP 58/2023, PMK 168/2023).

    env\\Scripts\\python system\\tools\\b1_maintenance.py

Reads dataset/03_pembanding/maintenance_ter_commits.csv (commit statistics collected from the cloned repositories)
and writes docs/hasil/b1_pemeliharaan.csv: per repository the days from the issue date of PP 58/2023 (2023-12-27) to
the commit that introduced TER, code lines and functions changed, and the number of later fix commits. The knowledge
base side of the comparison is the size of the gold updates E03 + E04 with no engine change (A1).
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))

ISSUED = date(2023, 12, 27)          # PP 58/2023 (E03); PMK 168/2023 (E04) followed on 2023-12-29


def main():
    rows = list(csv.DictReader(open(ROOT / "dataset/03_pembanding/maintenance_ter_commits.csv", encoding="utf-8")))
    out = []
    for repo in sorted({r["repo"] for r in rows}):
        rs = [r for r in rows if r["repo"] == repo]
        intro = [r for r in rs if r["kategori"] in ("TER_intro", "initial_with_TER")]
        fixes = [r for r in rs if r["kategori"] in ("TER_fix", "rule_fix")]
        follow = [r for r in rs if "followup" in r["kategori"] or "consumer" in r["kategori"]]
        if not intro:
            continue
        i = intro[0]
        d = date.fromisoformat(i["tanggal"])
        out.append({"repo": repo, "introduced": i["tanggal"], "kind": i["kategori"],
                    "days_after_issue": (d - ISSUED).days if i["kategori"] == "TER_intro" else "",
                    "files": i["jumlah_file"], "code_lines_added": i["baris_kode_tambah"],
                    "code_lines_removed": i["baris_kode_hapus"], "functions_touched": i["jumlah_fungsi_tersentuh"],
                    "fix_commits": len(fixes), "followup_commits": len(follow),
                    "fix_dates": ";".join(r["tanggal"] for r in fixes)})
    kb = {}
    for name in ("GOLD-E03", "GOLD-E04"):
        d = json.loads((ROOT / "dataset/12_emas/delta" / f"{name}.json").read_text(encoding="utf-8"))
        kb[name] = {"add": len(d["add"]), "change": len(d["change"]), "remove": len(d["remove"])}
    path = ROOT / "docs" / "hasil" / "b1_pemeliharaan.csv"
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print(json.dumps({"repositories": out, "knowledge_base_updates": kb, "engine_changes": 0}, indent=1))


if __name__ == "__main__":
    main()
