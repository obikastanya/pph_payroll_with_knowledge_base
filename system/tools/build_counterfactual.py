"""Counterfactual documents (PANDUAN Tahap 6, "dokumen kontrafaktual"; skeleton: memorisation rate).

    env\\Scripts\\python system\\tools\\build_counterfactual.py [CF-E01,CF-E06,...] [--no-gates]

For each selected row of dataset/09_korpus_peristiwa/kontrafaktual_spesifikasi.csv of kind nilai or ambang (value or
threshold; date variants are not built): every occurrence of the original value in the locked text of the source
document is replaced (the number of replacements must equal the column kemunculan, else the row is skipped), and
the result is locked as document <CF id> in dataset/13_teks/<CF id>/ (text, segments, extracted tables, manifest)
and registered in dataset/13_teks/dokumen.csv (role counterfactual). The counterfactual gold Delta*_CF is derived
from the source gold Delta* by the same substitution (number as written and as digits, number words, document id) and
written to dataset/12_emas/kontrafaktual/GOLD-<CF id>.json; it must apply to the source's base and pass G1-G5 against
the counterfactual text. Expected values on S^E (K_{n-1} (+) Delta*_CF, the source event's years) go to
dataset/14_ruang_uji/harapan/<CF id>.jsonl.gz, and the event to dataset/09_korpus_peristiwa/kontrafaktual/INDEX.csv
with the original and replaced values (memorisation: a candidate carrying the original value).
"""
import csv
import hashlib
import json
import random
import re
import shutil
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
import build_se  # noqa: E402
from kb_context import base_for  # noqa: E402
from pph21kbs import corpus, testspace, text  # noqa: E402

SPEC = ROOT / "dataset" / "09_korpus_peristiwa" / "kontrafaktual_spesifikasi.csv"
INDEX = ROOT / "dataset" / "09_korpus_peristiwa" / "kontrafaktual" / "INDEX.csv"
GOLD_DIR = ROOT / "dataset" / "12_emas" / "kontrafaktual"
DEFAULT = ("CF-E01", "CF-E06", "CF-E11", "CF2-E02")
# number words written after an amount, "Rp10.000.000,00 (sepuluh juta rupiah)", changed with it
WORDS = {"10.000.000": "sepuluh juta", "11.000.000": "sebelas juta", "12.000.000": "dua belas juta",
         "3.000.000": "tiga juta", "4.000.000": "empat juta"}


def _flex(s):
    """Regex of a literal that tolerates any whitespace (line breaks in the extracted text) between words."""
    return r"\s+".join(re.escape(w) for w in s.split())


def _swap_text(t, olds, news):
    for o, n in zip(olds, news):
        t = re.sub(_flex(o), n, t)
        on, nn = _number(o), _number(n)
        if on in WORDS and nn in WORDS and WORDS[on] not in o.lower():
            t = re.sub(rf"({re.escape(nn)}[^()]{{0,12}}\(\s*){_flex(WORDS[on])}", rf"\g<1>{WORDS[nn]}", t, flags=re.I)
    return t


def _number(s):
    m = re.search(r"\d{1,3}(?:\.\d{3})+", s)
    return m.group(0) if m else None


def _sub_number(s, old, new):
    """Replace a number written with thousand dots, or as plain digits, not inside a longer number."""
    for o, n in ((old, new), (old.replace(".", ""), new.replace(".", ""))):
        s = re.sub(rf"(?<![\d.]){re.escape(o)}(?![\d])(?!\.\d)", n, s)
    return s


def build_one(row, chain, check_gates=True):
    cf, src = row["id"], corpus.event(row["sumber"])
    doc = src.document
    olds = [x.strip() for x in row["asli"].split("|")]
    news = [x.strip() for x in row["pengganti"].split("|")]
    want = [int(x) for x in re.findall(r"\d+", row["kemunculan"])]
    raw = (text.TEXT_DIR / doc / "teks.txt").read_text(encoding="utf-8")
    counts = [len(re.findall(_flex(o), raw)) for o in olds]
    if counts != want:
        return {"id": cf, "status": f"skipped: occurrences {counts} != specification {want}"}
    raw = _swap_text(raw, olds, news)
    out = text.TEXT_DIR / cf
    out.mkdir(parents=True, exist_ok=True)
    (out / "teks.txt").write_text(raw, encoding="utf-8")
    segs = json.loads((text.TEXT_DIR / doc / "segmen.json").read_text(encoding="utf-8"))
    for s in segs:
        s["text"] = _swap_text(s["text"], olds, news)
    (out / "segmen.json").write_text(json.dumps(segs, ensure_ascii=False, indent=1), encoding="utf-8")
    if (text.TEXT_DIR / doc / "tabel").exists():
        shutil.copytree(text.TEXT_DIR / doc / "tabel", out / "tabel", dirs_exist_ok=True)
    sha = hashlib.sha256((out / "teks.txt").read_bytes()).hexdigest()
    (out / "MANIFEST.sha256").write_text(f"{sha}  teks.txt\n{sha}  turunan:{doc} ({row['jenis_ubahan']})\n",
                                         encoding="utf-8")
    # gold
    gold = json.loads(json.dumps(next(u for u in build_gold.collect() if u.event_id == src.id).to_json()))
    kept = []                                   # quotes of other documents (earlier regulations) stay as they are
    for e in gold["add"] + gold["change"] + gold["remove"]:
        for q in e.get("source") or []:
            if q.get("document") != doc and q.get("quote"):
                kept.append(q["quote"])
                q["quote"] = f"__KEEP_{len(kept) - 1}__"
    s = json.dumps(gold, ensure_ascii=False)
    for o, n in zip(olds, news):
        on, nn = _number(o), _number(n)
        if on and nn:
            s = _sub_number(s, on, nn)
            if on in WORDS and nn in WORDS:
                s = re.sub(WORDS[on], WORDS[nn], s, flags=re.I)
    s = s.replace(f'"{doc}"', f'"{cf}"')
    d = json.loads(s)
    for e in d["add"] + d["change"] + d["remove"]:
        for q in e.get("source") or []:
            m = re.fullmatch(r"__KEEP_(\d+)__", q.get("quote") or "")
            if m:
                q["quote"] = kept[int(m.group(1))]
    d.update(delta_id=f"GOLD-{cf}", event_id=cf)
    d["document"]["id"] = cf
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    (GOLD_DIR / f"GOLD-{cf}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return {"id": cf, "status": "built", "source": src.id, "document": cf, "source_document": doc,
            "kind": row["jenis_ubahan"], "original": row["asli"], "replacement": row["pengganti"],
            "occurrences": sum(want), "delta": d}


def register(rows):
    reg = text.TEXT_DIR / "dokumen.csv"
    lines = list(csv.DictReader(open(reg, encoding="utf-8", newline="")))
    fields = list(lines[0])
    keep = [r for r in lines if r["role"] != "counterfactual"]
    for r in rows:
        src = text.registry()[r["source_document"]]
        title = src["title"]
        for o, n in zip(r["original"].split("|"), r["replacement"].split("|")):
            title = title.replace(o.strip(), n.strip())
        keep.append({"id": r["id"], "event": r["id"], "role": "counterfactual", "issued": src["issued"],
                     "title": title, "files": f"turunan:{r['source_document']}"})
    with open(reg, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fields, lineterminator="\n")
        w.writeheader()
        w.writerows(keep)
    text.registry.cache_clear()
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, ["id", "sumber", "dokumen", "jenis_ubahan", "asli", "pengganti", "kemunculan"],
                           lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({"id": r["id"], "sumber": r["source"], "dokumen": r["id"], "jenis_ubahan": r["kind"],
                        "asli": r["original"], "pengganti": r["replacement"], "kemunculan": r["occurrences"]})
    corpus.counterfactual_events.cache_clear()


def main():
    ids = [a for a in sys.argv[1:] if not a.startswith("--")]
    ids = ids[0].split(",") if ids else list(DEFAULT)
    spec = {r["id"]: r for r in csv.DictReader(open(SPEC, encoding="utf-8", newline=""))}
    chain = build_gold.build(check_only=True, side=False)
    built = []
    for cf in ids:
        r = spec[cf]
        if r["jenis_ubahan"] not in ("nilai", "ambang"):
            print(f"{cf}: skipped (kind {r['jenis_ubahan']}; only value and threshold variants are built)")
            continue
        res = build_one(r, chain)
        print(f"{cf}: {res['status']}")
        if res["status"] == "built":
            built.append(res)
    register(built)
    from pph21kbs.pipeline.run import Config, check
    cases = {}
    for c in build_se.load_cases():
        cases.setdefault(c["tax_year"], []).append(c)
    rep_path = build_se.OUT / "laporan.json"
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    for r in built:
        ev = corpus.event(r["id"])
        base, _ = base_for(ev, chain)
        if "--no-gates" not in sys.argv:
            ok, log, kb2, _ = check(base, r["delta"], ev, ev.issued, None, Config())
            print(f"{r['id']}: gold gates {'pass' if ok else 'FAIL'} "
                  + "; ".join(f"{g}={v[:200]}" for g, v in log.items() if str(v).startswith("fail")))
        from pph21kbs.kb import apply_delta
        kb = apply_delta(base, r["delta"])
        rng = random.Random(f"{ev.id}-omega")
        rows = []
        years = testspace.event_years(ev)
        for y in years:
            for c in cases.get(y, []):
                rows.append(build_se.observations(kb, c, ev.issued))
                if rng.random() < 0.2:
                    rows.append(build_se.observations(kb, c, ev.issued - timedelta(days=1)))
        rep["events"][ev.id] = {"sha256": build_se.write_gz(build_se.OUT / "harapan" / f"{ev.id}.jsonl.gz", rows),
                                "tuples": len(rows), "years": years}
        print(f"{ev.id}: {len(rows)} expected tuples")
    rep_path.write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
