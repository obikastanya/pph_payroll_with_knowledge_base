"""Seal the test data before the measured runs: SHA-256 of every text the system reads and every gold update, in
v2/dataset/MANIFEST_SEGEL.sha256. `--check` verifies the files against the manifest.

    env\\Scripts\\python -m v2.tools.seal [--check]
"""
import hashlib
import sys

import v2.harness  # noqa: F401
from v2.harness import DATA

MANIFEST = DATA / "MANIFEST_SEGEL.sha256"
PATTERNS = ("12_emas/kb.trig", "12_emas/delta/*.json", "12_emas/rantai.csv", "12_emas/sisi.csv",
            "13_teks/*/teks.txt", "13_teks_pengecoh_ringkas/*/teks.txt", "14_ruang_uji/*.jsonl.gz",
            "15_set_prospektif/units/*/spec.json", "15_set_prospektif/units/*/teks.txt",
            "15_set_prospektif/units/*/dokumen.pdf", "09_korpus_peristiwa/peristiwa.csv",
            "10_kebijakan_perusahaan/peristiwa_kebijakan.csv")


def files():
    out = []
    for pattern in PATTERNS:
        out += sorted(DATA.glob(pattern))
    return out


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal():
    lines = [f"{digest(p)}  {p.relative_to(DATA).as_posix()}" for p in files()]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def check():
    want = dict(reversed(line.split("  ", 1)) for line in MANIFEST.read_text(encoding="utf-8").splitlines())
    have = {p.relative_to(DATA).as_posix(): digest(p) for p in files()}
    changed = sorted(k for k in want if have.get(k) != want[k])
    added = sorted(k for k in have if k not in want)
    return changed, added


if __name__ == "__main__":
    if "--check" in sys.argv:
        changed, added = check()
        print("changed:", changed or "none", "| not sealed:", added or "none")
    else:
        print("sealed", seal(), "files in", MANIFEST)
