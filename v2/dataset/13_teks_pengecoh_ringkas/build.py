"""Short versions of the 20 distractor documents: the opening, ONE core part, and the closing.

The frozen texts in dataset/13_teks/ are not changed. For each distractor (role "distractor" in
dataset/13_teks/dokumen.csv) this script writes dataset/13_teks_pengecoh_ringkas/<ID>/teks.txt and meta.json.

Rule (mechanical, the same for every distractor):
1. Opening: the opening segment (title, number, considerations), cut at OPENING_CAP characters.
2. One core part: the whole article (annexes are left out) of MIN_PART to PART_CAP characters with the highest
   density of PPh 21 and wage terms (matches per square root of length, as the pipeline's own text selection scores
   segments) and at least one match. A whole article keeps its legal context, and it is the part most likely to look
   relevant, so the relevance test stays meaningful. Articles shorter than MIN_PART (such as "this regulation comes
   into force on ...") are not candidates. Only when no article qualifies is the beginning of the densest article
   used, cut at a paragraph break.
3. Closing: the first closing segment ("Ditetapkan di ..."), with the dates of enactment and entry into force, cut at
   CLOSING_CAP characters.

    python v2/dataset/13_teks_pengecoh_ringkas/build.py
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "system_final"))
from pph21kbs.documents import FIXED_TERMS, normalize, segment  # noqa: E402

SOURCE = HERE.parent / "13_teks"
OPENING_CAP, PART_CAP, CLOSING_CAP, MIN_PART = 3_000, 12_000, 2_000, 500
TERMS = sorted(set(FIXED_TERMS) | {"pph 21", "pegawai", "karyawan", "pekerja", "gaji", "penghasilan", "upah"})


def score(text):
    t = normalize(text)
    hits = sum(len(re.findall(re.escape(term), t)) for term in TERMS)
    return hits / max(1, len(t)) ** 0.5, hits


def cap(text, n):
    return text if len(text) <= n else text[:text.rfind("\n", 0, n) if text.rfind("\n", 0, n) > n // 2 else n]


def core_part(segs, full):
    """(label, text) of the core part, by the rule in the module docstring."""
    articles = [s for s in segs if s["kind"] == "article"] or [{"id": "text", "text": full}]
    whole = [s for s in articles if MIN_PART <= len(s["text"]) <= PART_CAP and score(s["text"])[1] > 0]
    if whole:
        best = max(whole, key=lambda s: score(s["text"])[0])
        return best["id"], best["text"]
    best = max(articles, key=lambda s: score(s["text"])[0])
    text = cap(best["text"], PART_CAP)
    return (best["id"] + (f" [0:{len(text)}]" if len(text) < len(best["text"]) else "")), text


def build(doc_id):
    src = SOURCE / doc_id / "teks.txt"
    full = src.read_text(encoding="utf-8")
    segs = segment(full)
    opening = next((s for s in segs if s["kind"] == "opening"), None)
    closing = next((s for s in segs if s["kind"] == "closing"), None)
    best_id, best_text = core_part(segs, full)
    parts = [("opening", cap(opening["text"], OPENING_CAP)) if opening else None, (best_id, best_text),
             ("closing", cap(closing["text"], CLOSING_CAP)) if closing else None]
    parts = [p for p in parts if p and p[1].strip()]
    text = "\n\n".join(p[1].strip() for p in parts) + "\n"
    out = HERE / doc_id
    out.mkdir(exist_ok=True)
    (out / "teks.txt").write_text(text, encoding="utf-8")
    dens, hits = score(best_text)
    meta = {"id": doc_id, "source": f"v2/dataset/13_teks/{doc_id}/teks.txt",
            "source_sha256": hashlib.sha256(full.encode("utf-8")).hexdigest(), "source_chars": len(full),
            "chars": len(text), "parts": [p[0] for p in parts], "core_part": best_id, "core_term_hits": hits,
            "core_density": round(dens, 4), "rule": {"opening_cap": OPENING_CAP, "part_cap": PART_CAP,
                                                      "min_part": MIN_PART, "core": "whole article",
                                                      "closing_cap": CLOSING_CAP, "annexes": "left out"}}
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


def main():
    rows = [r for r in csv.DictReader(open(SOURCE / "dokumen.csv", encoding="utf-8")) if r["role"] == "distractor"]
    metas = [build(r["id"]) for r in rows]
    (HERE / "ringkasan.csv").write_text(
        "id,source_chars,chars,share,core_part,core_term_hits\n"
        + "".join(f"{m['id']},{m['source_chars']},{m['chars']},{m['chars'] / m['source_chars']:.3f},"
                  f"\"{m['core_part']}\",{m['core_term_hits']}\n" for m in metas), encoding="utf-8")
    for m in metas:
        print(f"{m['id']:20} {m['source_chars']:>10,} -> {m['chars']:>7,} ({m['chars'] / m['source_chars']:6.1%})"
              f"  core: {m['core_part'][:40]:40} hits {m['core_term_hits']}")
    tot0, tot1 = sum(m["source_chars"] for m in metas), sum(m["chars"] for m in metas)
    print(f"TOTAL {len(metas)}: {tot0:,} -> {tot1:,} chars ({tot1 / tot0:.1%})")


if __name__ == "__main__":
    main()
