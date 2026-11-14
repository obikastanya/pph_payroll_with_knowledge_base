"""Set up GraphDB for the system: license file, container, and the pph21 repository with SHACL validation.

    env\\Scripts\\python system\\tools\\graphdb_setup.py

1. License. The Graphwise email gives the free license as a base64 code. Put it in .env as GRAPHDB_LICENSE (one line;
   GRAPH_LISENCE is also accepted). It is decoded to the binary graphdb/graphdb.license that GraphDB reads.
2. Container. Starts graphdb/docker-compose.yml (Docker Desktop must be running).
3. Repository. Creates `pph21` if missing: SHACL validation on (it cannot be switched on later), no inference
   (ruleset "empty", so queries see exactly the stored triples), context index on (one named graph per version).
   SHACL's sh:class follows rdfs:subClassOf only for triples in the repository, so the ontology must be loaded with
   the data (the system's store does this).

Re-running is safe: every step is skipped when it is already done. The license value is never printed.
"""
import base64
import binascii
import re
import subprocess
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pph21kbs import config  # noqa: E402

FOLDER = config.REPO / "graphdb"
LICENSE = FOLDER / "graphdb.license"
SETTINGS = {"isShacl": "true", "ruleset": "empty", "enableContextIndex": "true"}
ENV_KEY = re.compile(r"^\s*(export\s+)?[A-Z_][A-Z0-9_]*\s*=")


def write_license():
    if LICENSE.is_file():
        print(f"license: {LICENSE.name} exists")
        return True
    code = config.secret("GRAPHDB_LICENSE", "GRAPH_LISENCE")
    if not code:
        print("license: put the code from the Graphwise email in .env as GRAPHDB_LICENSE")
        return False
    lines = config.ENV_FILE.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.split("=", 1)[0].strip() in ("GRAPHDB_LICENSE", "GRAPH_LISENCE"))
    parts = [code]
    for line in lines[start + 1:]:          # a code pasted over several lines continues until the next KEY=
        if not line.strip() or ENV_KEY.match(line):
            break
        parts.append(line.strip())
    try:
        LICENSE.write_bytes(base64.b64decode("".join("".join(parts).split()), validate=True))
    except binascii.Error:
        print("license: the code in .env is not valid base64")
        return False
    print(f"license: written to {LICENSE} ({LICENSE.stat().st_size} bytes)")
    return True


def start_container():
    subprocess.run(["docker", "compose", "-f", str(FOLDER / "docker-compose.yml"), "up", "-d"], check=True)
    for _ in range(60):
        try:
            httpx.get(f"{config.GRAPHDB_URL}/rest/repositories", timeout=3).raise_for_status()
            break
        except httpx.HTTPError:
            time.sleep(2)
    lic = httpx.get(f"{config.GRAPHDB_URL}/rest/graphdb-settings/license", timeout=10).json()
    print(f"graphdb: running at {config.GRAPHDB_URL}; license valid: {lic.get('valid')} ({lic.get('product')})")
    return bool(lic.get("valid"))


def create_repository():
    base = config.GRAPHDB_URL
    if any(r["id"] == config.GRAPHDB_REPOSITORY for r in httpx.get(f"{base}/rest/repositories").json()):
        print(f"repository: {config.GRAPHDB_REPOSITORY} exists")
        return True
    cfg = httpx.get(f"{base}/rest/repositories/default-config/graphdb").json()
    for k, v in SETTINGS.items():
        cfg["params"][k]["value"] = v
    title = "PPh 21 knowledge base (one named graph per version)"
    cfg["params"]["title"]["value"] = title
    cfg.update(id=config.GRAPHDB_REPOSITORY, title=title, type="graphdb")
    r = httpx.post(f"{base}/rest/repositories", json=cfg, timeout=60)
    print(f"repository: create {config.GRAPHDB_REPOSITORY} -> HTTP {r.status_code}")
    return r.status_code < 300


def main():
    return 0 if write_license() and start_container() and create_repository() else 1


if __name__ == "__main__":
    sys.exit(main())
