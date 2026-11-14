"""Knowledge base as an append-only sequence of records, and its view at a knowledge date (representasi.md 2, 7).

KnowledgeBase objects are immutable: apply() returns a new KnowledgeBase that shares the old records. A View is the
set of effective records at knowledge date omega, indexed for the engine. Views are cached per (kb, omega).
"""
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date

from .model import Constraint, FactDef, Parameter, Rule, TableVersion, Tombstone


class UpdateError(ValueError):
    """A Delta cannot be applied to the knowledge base (wrong operation for an id, kind mismatch, ...)."""


@dataclass(frozen=True)
class UpdateInfo:
    update_id: str
    delta_id: str
    event_id: str | None
    document: str
    recorded_on: date | None
    first_seq: int
    last_seq: int
    note: str = ""


class KnowledgeBase:
    def __init__(self, records=(), updates=(), documents=None, name="K", adoptions=None):
        self.records = tuple(records)
        self.updates = tuple(updates)
        self.documents = dict(documents or {})
        self.adoptions = dict(adoptions or {})     # policy document id -> ids of optional rules it adopts
        self.name = name
        self._views = {}
        self._by_id = None

    # ------------------------------------------------------------------ basics
    @property
    def next_seq(self):
        return self.records[-1].seq + 1 if self.records else 1

    def history(self, element_id):
        """All records of one element id in application order."""
        if self._by_id is None:
            by_id = defaultdict(list)
            for r in self.records:
                by_id[r.id].append(r)
            self._by_id = by_id
        return self._by_id.get(element_id, [])

    def effective(self, element_id, omega):
        """The effective record of an id at knowledge date omega, or None (absent or removed)."""
        best = None
        for r in self.history(element_id):
            if r.recorded_on <= omega and (best is None or r.key > best.key):
                best = r
        if best is None or isinstance(best, Tombstone):
            return None
        return best

    def extended(self, new_records, update, documents=None, adoptions=None):
        docs = dict(self.documents)
        docs.update(documents or {})
        adopt = dict(self.adoptions)
        adopt.update(adoptions or {})
        return KnowledgeBase(self.records + tuple(new_records), self.updates + (update,), docs, self.name, adopt)

    def first_recorded(self, element_id):
        """t_c^0: recording date of the first record of an element (stable under later revisions)."""
        h = self.history(element_id)
        return h[0].recorded_on if h else None

    def until(self, update_id):
        """Prefix of the knowledge base up to and including the named update."""
        for i, u in enumerate(self.updates):
            if u.update_id == update_id:
                keep = {x.update_id for x in self.updates[: i + 1]}
                recs = [r for r in self.records if r.update_id in keep]
                return KnowledgeBase(recs, self.updates[: i + 1], self.documents, self.name, self.adoptions)
        raise KeyError(update_id)

    def view(self, omega):
        v = self._views.get(omega)
        if v is None:
            v = View(self, omega)
            self._views[omega] = v
        return v

    def fingerprint(self):
        """SHA-256 over the canonical serialisation of all records (stable across runs)."""
        import hashlib
        import json
        from .serialize import record_to_json
        h = hashlib.sha256()
        for r in self.records:
            h.update(json.dumps(record_to_json(r), sort_keys=True, ensure_ascii=False).encode("utf-8"))
        return h.hexdigest()


class View:
    """Effective records at knowledge date omega, indexed by what the engine asks for.

    omega filters the regulation layer only. Company-layer records belong to a policy that the case states, so the
    latest record of each company element is used whatever omega is (representasi.md section 2)."""

    def __init__(self, kb, omega):
        self.kb = kb
        self.omega = omega
        # every record of a policy update (one that contains company rules) belongs to the company layer, including
        # the facts and parameters the policy defines for its own rules
        policy_updates = {r.update_id for r in kb.records if getattr(r, "layer", None) == "company"}
        latest = {}
        for r in kb.records:
            company = (getattr(r, "layer", None) == "company" or r.id.startswith("PRS.")
                       or r.update_id in policy_updates)
            if company or r.recorded_on <= omega:
                prev = latest.get(r.id)
                if prev is None or r.key > prev.key:
                    latest[r.id] = r
        self.records = [r for r in latest.values() if not isinstance(r, Tombstone)]
        self.records.sort(key=lambda r: r.seq)
        self.rules_by_fact = defaultdict(list)
        self.params = defaultdict(list)
        self.tables = defaultdict(list)
        self.constraints = []
        self.facts = {}
        self.rules = {}
        self.first_recorded = {}
        for r in self.records:
            self.first_recorded[r.id] = kb.first_recorded(r.id)
            if isinstance(r, Rule):
                self.rules_by_fact[r.produces].append(r)
                self.rules[r.id] = r
            elif isinstance(r, Parameter):
                self.params[r.name].append(r)
            elif isinstance(r, TableVersion):
                self.tables[r.name].append(r)
            elif isinstance(r, Constraint):
                self.constraints.append(r)
            elif isinstance(r, FactDef):
                self.facts[r.id] = r
        self._override_closure = {}

    def overrides_closure(self, rule_id):
        """Transitive closure of the overrides relation from one rule (lex specialis)."""
        out = self._override_closure.get(rule_id)
        if out is None:
            out, stack = set(), [rule_id]
            while stack:
                r = self.rules.get(stack.pop())
                if r is None:
                    continue
                for t in r.overrides:
                    if t not in out:
                        out.add(t)
                        stack.append(t)
            self._override_closure[rule_id] = out
        return out

    def output_facts(self, scope):
        return [f for f in self.facts.values() if f.output and f.fact_scope == scope]
