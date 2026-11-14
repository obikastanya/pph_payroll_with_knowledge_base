"""Search a locked document text: page, line, and context for a regular expression.

    env\\Scripts\\python system\\tools\\grep_text.py DOC-ID "regex" [context_lines] [max_hits]
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pph21kbs.text import pages  # noqa: E402


def main(doc, pattern, context=2, max_hits=12):
    rx = re.compile(pattern, re.I)
    hits = 0
    for n, text in pages(doc):
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if rx.search(line):
                lo, hi = max(0, i - context), min(len(lines), i + context + 1)
                print(f"--- {doc} hlm. {n}, baris {i + 1}")
                print("\n".join(lines[lo:hi]))
                hits += 1
                if hits >= max_hits:
                    return


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args[0], args[1], int(args[2]) if len(args) > 2 else 2, int(args[3]) if len(args) > 3 else 12)
