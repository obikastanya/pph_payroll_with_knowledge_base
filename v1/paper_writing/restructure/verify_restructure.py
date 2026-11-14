"""Check that every sentence of the pre-restructure manuscript survives in main.tex or supplementary.tex.

Prints the old sentences that are not found verbatim (after whitespace normalization).
Run from the repository root:  python paper_writing/restructure/verify_restructure.py
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
old = subprocess.run(["git", "show", "b4bf5e6:paper_final/main.tex"], cwd=ROOT, capture_output=True,
                     text=True, encoding="utf8", check=True).stdout
new = (ROOT / "paper_final" / "main.tex").read_text(encoding="utf8")
new += "\n" + (ROOT / "paper_final" / "supplementary.tex").read_text(encoding="utf8")


STRUCT = [r"\\begin\{[a-zA-Z*]+\}(\[[^\]]*\])?(\{[^}]*\})?", r"\\end\{[a-zA-Z*]+\}",
          r"\\(sub)?section\*?\{[^}]*\}", r"\\label\{[^}]*\}", r"\\centering", r"\\footnotesize",
          r"\\scriptsize", r"\\setlength\{[^}]*\}\{[^}]*\}", r"\\resizebox\{[^}]*\}\{!\}\{%?",
          r"\\includegraphics\[[^\]]*\]\{[^}]*\}", r"\\(PAR|IEEEPAR)start\{(.)\}\{([^}]*)\}", r"%"]


def norm(s):
    s = re.sub(r"\\(PAR|IEEEPAR)start\{(.)\}\{([^}]*)\}", r"\2\3", s)
    for pat in STRUCT:
        s = re.sub(pat, " ", s)
    return re.sub(r"\s+", " ", s).strip()


old_body = old[old.index("\\begin{abstract}"):old.index("\\bibliographystyle")]
new_n = norm(new)
# sentences: split after ". " followed by an upper-case letter or a backslash command
parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", norm(old_body))
missing = []
for p in parts:
    p = p.strip()
    if len(p) < 25 or p.startswith("\\begin{tabular}") or p.startswith("\\toprule"):
        continue
    if p not in new_n:
        missing.append(p)
print(f"{len(parts)} sentence-like units checked, {len(missing)} not found verbatim:\n")
for m in missing:
    print("-", m[:220])
    print()
