# -*- coding: utf-8 -*-
"""Independent arithmetic check of every contoh.json (does not import mesin.py).

For every worked example:
1. every step with "ekspresi" is re-evaluated and compared with "hasil";
2. every table lookup is redone from tables/ter_bulanan.csv or from the
   change's own table ("tabel_perubahan") and compared;
3. every number of 4+ digits in an expression must come from the input, an
   earlier step result, or a declared constant (traceability);
4. every numeric output must be bound to a step whose result equals it.
The verdict is written back as "cek_aritmetika" ("cocok" or a list of issues).
Usage: python cek_aritmetika.py [--tulis]
"""
import csv
import json
import re
import sys
from pathlib import Path

SEALED = Path(__file__).resolve().parents[1]
ROOT = SEALED.parents[2]
TD = ROOT / "dataset" / "01_regulasi" / "tables"


def base_tables():
    t = {}
    with open(TD / "ter_bulanan.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t.setdefault("PP58/" + r["kategori"], []).append(
                (int(r["batas_bawah"]), int(r["batas_atas"]) if r["batas_atas"] else None,
                 round(float(r["tarif_persen"]) * 100)))
    return t


def constants():
    c = set()
    with open(TD / "ptkp.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            c.add(int(r["ptkp_setahun"]))
    with open(TD / "tarif_pasal17.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            c.add(int(r["pkp_batas_bawah"]))
            if r["pkp_batas_atas"]:
                c.add(int(r["pkp_batas_atas"]))
    c |= {1000, 10000, 100000, 99999, 500000, 6000000, 12000000, 11086300, 10547400}
    c |= set(range(1900, 2101))  # years in age computation
    return c


CHANGE_CONST = {
    "U01": {60000000, 5400000}, "U02": {750000}, "U04": {200000}, "U05": {400000},
    "U06": {9000000}, "U07": {10000000},
}

BASE = base_tables()
CONST = constants()


def lookup(tab, base, tables):
    for lo, hi, bp in tables[tab]:
        if (base > lo or lo == 0) and (hi is None or base <= hi):
            return bp
    return None


def ints_in(obj, acc):
    if isinstance(obj, bool):
        return acc
    if isinstance(obj, int):
        acc.add(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            ints_in(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            ints_in(v, acc)
    return acc


def leaves(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, obj


def check_example(uid, ex, tables):
    issues = []
    known = ints_in(ex["input"], set()) | CONST | CHANGE_CONST.get(uid, set())
    results = {}
    for s in ex["langkah"]:
        if "ekspresi" in s:
            try:
                v = eval(s["ekspresi"], {"__builtins__": {}}, {"min": min, "max": max})
            except Exception as e:  # noqa: BLE001
                issues.append(f"langkah {s['no']}: ekspresi gagal dievaluasi ({e})")
                continue
            if v != s["hasil"]:
                issues.append(f"langkah {s['no']}: {s['ekspresi']} = {v}, tercatat {s['hasil']}")
            for lit in re.findall(r"\d+", s["ekspresi"]):
                n = int(lit)
                if n >= 1000 and n not in known:
                    issues.append(f"langkah {s['no']}: angka {n} tidak berasal dari input, langkah sebelumnya, atau konstanta")
            known.add(s["hasil"])
            known.add(abs(s["hasil"]))
            results[s["no"]] = s["hasil"]
        elif "tabel" in s:
            bp = lookup(s["tabel"], s["nilai"], tables)
            if bp != s["tarif_basis_poin"]:
                issues.append(f"langkah {s['no']}: tabel {s['tabel']} untuk {s['nilai']} = {bp} bp, tercatat {s['tarif_basis_poin']}")
            if s["nilai"] not in known:
                issues.append(f"langkah {s['no']}: nilai {s['nilai']} untuk tabel tidak berasal dari langkah sebelumnya")
            known.add(s["tarif_basis_poin"])
            results[s["no"]] = s["tarif_basis_poin"]
    bound = {}
    for s in ex["langkah"]:
        for p in s.get("keluaran", []):
            bound[p] = s["no"]
    for path, v in leaves(ex["keluaran_diharapkan"]):
        if not isinstance(v, int) or isinstance(v, bool) or path.endswith(".bulan"):
            continue
        if ".komponen_setelah_pkb." in path:
            if v not in known:
                issues.append(f"{path}: {v} tidak ditemukan pada input maupun langkah")
            continue
        if path in bound:
            if results.get(bound[path]) != v:
                issues.append(f"{path}: {v} berbeda dengan hasil langkah {bound[path]} ({results.get(bound[path])})")
        elif not (v == 0 and path.endswith("pph21_dtp")):
            issues.append(f"{path}: {v} tidak terikat ke langkah mana pun")
    # internal consistency: dipotong = pph21 - dtp
    for i, r in enumerate(ex["keluaran_diharapkan"]["per_masa"]):
        if r["pph21"] >= 0 and r["pph21_dipotong"] != r["pph21"] - r.get("pph21_dtp", 0):
            issues.append(f"per_masa[{i}]: pph21_dipotong != pph21 - pph21_dtp")
    return issues


def main():
    write = "--tulis" in sys.argv
    total, bad = 0, 0
    report = {}
    for d in sorted(SEALED.glob("U[0-9][0-9]")):
        f = d / "contoh.json"
        doc = json.loads(f.read_text(encoding="utf-8"))
        tables = dict(BASE)
        for k, rows in doc.get("tabel_perubahan", {}).items():
            tables[k] = [tuple(r) for r in rows]
        n_bad = 0
        for ex in doc["contoh"]:
            total += 1
            iss = check_example(doc["id"], ex, tables)
            ex["cek_aritmetika"] = "cocok" if not iss else iss
            if iss:
                bad += 1
                n_bad += 1
                print(ex["id"], iss[:5])
        report[doc["id"]] = (len(doc["contoh"]), n_bad)
        if write:
            f.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"contoh": total, "tidak_cocok": bad, "per_perubahan": report}))


if __name__ == "__main__":
    main()
