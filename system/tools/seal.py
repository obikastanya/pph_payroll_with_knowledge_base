"""Seal and verify research materials with SHA-256 manifests (decision log: unseen changes, locked gold Deltas).

    env\\Scripts\\python system\\tools\\seal.py seal   review/unseen_changes/sealed
    env\\Scripts\\python system\\tools\\seal.py verify review/unseen_changes/sealed

`seal` writes MANIFEST.sha256 next to the files; commit the manifest (and tag the commit) before the event it guards,
for example before the representation is frozen. `verify` fails if any file was added, removed, or changed since.
"""
import hashlib
import sys
from pathlib import Path

MANIFEST = "MANIFEST.sha256"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(folder):
    return sorted(p for p in folder.rglob("*") if p.is_file() and p.name != MANIFEST)


def seal(folder):
    lines = [f"{digest(p)}  {p.relative_to(folder).as_posix()}" for p in files(folder)]
    (folder / MANIFEST).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sealed {len(lines)} files in {folder / MANIFEST}")
    return 0


def verify(folder):
    manifest = folder / MANIFEST
    if not manifest.exists():
        print(f"no manifest in {folder}")
        return 1
    expected = dict(reversed(line.split("  ", 1)) for line in manifest.read_text(encoding="utf-8").splitlines() if line)
    actual = {p.relative_to(folder).as_posix(): digest(p) for p in files(folder)}
    problems = [f"changed: {f}" for f in expected if f in actual and actual[f] != expected[f]]
    problems += [f"missing: {f}" for f in expected if f not in actual]
    problems += [f"added:   {f}" for f in actual if f not in expected]
    print("\n".join(problems) or f"intact: {len(expected)} files match {manifest}")
    return 1 if problems else 0


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("seal", "verify"):
        print(__doc__)
        sys.exit(2)
    sys.exit({"seal": seal, "verify": verify}[sys.argv[1]](Path(sys.argv[2])))
