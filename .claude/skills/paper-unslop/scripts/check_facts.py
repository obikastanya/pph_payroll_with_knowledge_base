"""Meaning-lock check: compares the facts of two versions of a paper (LaTeX or plain text).

    python check_facts.py original.tex revised.tex

Extracts numbers, citation keys, cross-reference labels, inline math, italic terms (\\en, \\emph, \\textit) and the
words that change a claim's strength (hanya, semua, selalu, tidak, ...), then prints what disappeared or appeared.
Exit code 1 when anything differs, so every difference is either fixed or reported as intended.
"""
import re
import sys
from collections import Counter

STRENGTH = r"\b(hanya|semua|seluruh|selalu|tidak pernah|tidak|bukan|belum|tanpa|pasti|terbukti|setiap|paling|" \
           r"sebagian|mungkin|dapat|only|all|always|never|not|no|every|most|may|might|proved?)\b"


def strip_comments(t):
    return re.sub(r"(?<!\\)%[^\n]*", "", t)


def facts(text):
    t = strip_comments(text)
    out = {}
    out["sitasi"] = Counter(k.strip() for g in re.findall(r"\\cite\w*\{([^}]*)\}", t) for k in g.split(","))
    out["rujukan"] = Counter(re.findall(r"\\(?:ref|eqref|autoref|cref)\{([^}]*)\}", t))
    out["label"] = Counter(re.findall(r"\\label\{([^}]*)\}", t))
    out["matematika"] = Counter(m.strip() for m in re.findall(r"\$([^$]+)\$", t))
    out["istilah miring"] = Counter(m.strip().lower() for m in re.findall(r"\\(?:en|emph|textit)\{([^{}]*)\}", t))
    plain = re.sub(r"\$[^$]*\$", " ", t)
    plain = re.sub(r"\\(cite\w*|ref|eqref|label|autoref|cref|includegraphics|usepackage|documentclass)(\[[^\]]*\])?\{[^}]*\}", " ", plain)
    plain = re.sub(r"\\[a-zA-Z]+", " ", plain)
    out["angka"] = Counter(re.findall(r"(?<![\w])[-−+]?\d+(?:[.,]\d+)*(?:\s?%)?", plain))
    out["kata kekuatan klaim"] = Counter(w.lower() for w in re.findall(STRENGTH, plain, flags=re.I))
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    a = facts(open(sys.argv[1], encoding="utf-8", errors="replace").read())
    b = facts(open(sys.argv[2], encoding="utf-8", errors="replace").read())
    differs = False
    for kind in a:
        lost, gained = a[kind] - b[kind], b[kind] - a[kind]
        if not lost and not gained:
            print(f"{kind}: sama ({sum(a[kind].values())})")
            continue
        differs = True
        print(f"{kind}: BERBEDA")
        if lost:
            print("    hilang:  " + ", ".join(f"{k} x{n}" if n > 1 else k for k, n in sorted(lost.items())))
        if gained:
            print("    muncul:  " + ", ".join(f"{k} x{n}" if n > 1 else k for k, n in sorted(gained.items())))
    commas = [len(re.findall(r",(?!\d)", re.sub(r"\$[^$]*\$", " ", strip_comments(open(f, encoding="utf-8", errors="replace").read()))))
              for f in sys.argv[1:3]]
    note = " (K7: perbaikan tidak boleh menambah koma; periksa kalimat yang berubah)" if commas[1] > commas[0] else ""
    print(f"koma di luar angka dan matematika: {commas[0]} -> {commas[1]}{note}")
    if differs:
        print("\nSetiap selisih harus diperbaiki atau dilaporkan sebagai perubahan yang disengaja. "
              "Kata kekuatan klaim yang bergeser wajib dibaca ulang di kalimatnya.")
    return 1 if differs else 0


if __name__ == "__main__":
    sys.exit(main())
