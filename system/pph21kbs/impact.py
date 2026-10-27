"""Static cross-layer impact detector (RQ4, akuisisi.md section 6) on the knowledge graph.

The graph has two named graphs: kb:graph/view with the effective records of K_n (+) P at omega, and kb:graph/delta
with the records the Delta created (a removed element is represented by the record it removed). The SPARQL queries
in system/ontology/queries/impact_*.rq compute F_Delta with its downstream closure and the labels (a), (b), (c) for
each policy. Baseline B5(i) ("flag every policy touching F_Delta downstream, ignoring validity") is flag_all().
"""
from functools import lru_cache

from rdflib import Dataset, URIRef

from .config import REPO
from .kb import rdf
from .kb.model import Tombstone

QUERIES = REPO / "system" / "ontology" / "queries"
VIEW = rdf.KB["graph/view"]
DELTA = rdf.KB["graph/delta"]


@lru_cache(maxsize=None)
def query_text(name):
    return (QUERIES / f"{name}.rq").read_text(encoding="utf-8")


def impact_graph(kb, update_id, omega):
    ds = Dataset()
    view, delta = ds.graph(VIEW), ds.graph(DELTA)
    for r in kb.view(omega).records:
        rdf.record_triples(view, r)
    for r in kb.records:
        if r.update_id != update_id:
            continue
        if isinstance(r, Tombstone):
            older = [x for x in kb.history(r.id) if x.seq < r.seq and not isinstance(x, Tombstone)]
            if older:
                rdf.record_triples(delta, older[-1])
            continue
        rdf.record_triples(delta, r)
    return ds


def affected_facts(ds):
    return sorted(str(row.fact).rsplit("/", 1)[1] for row in ds.query(query_text("impact_facts")))


def detect(kb, update_id, policies, omega):
    """{policy: {"kinds": set of "a"/"b"/"c", "hits": [(kind, company rule, delta element, fact)]}} for each
    policy whose rules are in kb (installed as K_n (+) P)."""
    ds = impact_graph(kb, update_id, omega)
    facts = affected_facts(ds)
    # F_Delta is passed as FILTER ... IN: rdflib ignores an inline VALUES block inside a UNION branch
    members = ", ".join(f"<{rdf.fact_iri(f)}>" for f in facts) or "<urn:pph21kbs:none>"
    q = query_text("impact_policy").replace("FILTER_AFFECTED", f"FILTER(?fact IN ({members}))")
    out = {}
    for p in policies:
        hits = []
        for row in ds.query(q, initBindings={"policy": URIRef(rdf.doc_iri(p))}):
            hits.append((str(row.kind), str(row.rule), str(row.element), str(row.fact).rsplit("/", 1)[1]))
        out[p] = {"kinds": {h[0] for h in hits}, "hits": sorted(set(hits))}
    return out


def flag_all(kb, update_id, policies, omega):
    """Baseline B5(i): a policy is flagged when any of its rules reads or produces a fact in F_Delta downstream,
    whatever the validity."""
    ds = impact_graph(kb, update_id, omega)
    facts = set(affected_facts(ds))
    view = kb.view(omega)
    out = {}
    for p in policies:
        touched = set()
        for r in view.rules.values():
            if r.layer == "company" and r.policy == p:
                deps = {r.produces}
                for e in (r.expression, r.condition):
                    if e is not None:
                        deps |= e.dependencies()
                touched |= deps & facts
        out[p] = bool(touched)
    return out
