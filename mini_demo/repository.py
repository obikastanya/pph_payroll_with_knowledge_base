"""Knowledge-base repository: versions as an append-only log of Deltas (skeleton Section V, definition of an update).

Version n is K0 (+) Delta_1 (+) ... (+) Delta_n. Nothing is edited in place. Correcting or withdrawing knowledge is
another Delta (a rule that supersedes the old one), so every earlier version, and every result computed with earlier
knowledge, can be reproduced (invariant A3_omega).
"""
import hashlib
import json
from dataclasses import dataclass, field

import kg
from evaluation import load_json


@dataclass
class Version:
    number: int
    label: str
    document: str
    delta: dict
    recorded_on: str
    author: str          # researcher, pipeline, reviewer
    note: str = ""
    graph: object = field(default=None, repr=False)
    fingerprint: str = ""

    @property
    def name(self):
        return f"v{self.number}"

    @property
    def size(self):
        return len(self.delta.get("add", [])) + len(self.delta.get("tables", []))


class Repository:
    def __init__(self):
        delta = load_json(kg.DATA / "initial_kb.json")
        self.versions = []
        self.append("K0, initial knowledge base", "K0", delta, delta["recorded_on"], "researcher", delta.get("note", ""))

    @property
    def head(self):
        return self.versions[-1]

    def append(self, label, document, delta, recorded_on, author, note=""):
        """Apply a Delta to the head and store the result as a new version. Raises kg.UpdateError if it does not apply."""
        base = self.head.graph if self.versions else kg.empty_graph()
        g = kg.apply_delta(base, delta, recorded_on)
        previous = self.head.fingerprint if self.versions else ""
        fingerprint = hashlib.sha256((previous + json.dumps(delta, sort_keys=True)).encode()).hexdigest()[:12]
        v = Version(len(self.versions), label, document, delta, recorded_on, author, note, g, fingerprint)
        self.versions.append(v)
        return v

    def diff(self, a, b):
        """What version b adds on top of version a: rules, rules it repeals, and table versions."""
        rules_a = {r["id"] for r in kg.rule_records(self.versions[a].graph)}
        rules_b = kg.rule_records(self.versions[b].graph)
        tables_a = {(t["name"], t["valid_from"]) for t in kg.table_records(self.versions[a].graph)}
        added = [r for r in rules_b if r["id"] not in rules_a]
        return {"rules": added, "superseded": sorted({i for r in added for i in r["supersedes"]}),
                "tables": [t for t in kg.table_records(self.versions[b].graph) if (t["name"], t["valid_from"]) not in tables_a]}


def demo_repository(events, gold, applied=("E1", "K1", "P1")):
    """The state the app starts in: K0 plus the events already processed and approved. E2 is left in the inbox."""
    repo = Repository()
    for e in events:
        if e["id"] in applied:
            repo.append(f"{e['id']}, {e['title']}", e["id"], gold[e["id"]], e["issued"], "reviewer",
                        "approved update (in the demo: the gold Delta)")
    return repo
