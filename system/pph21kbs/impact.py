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
    if isinstance(ds, _Remote):
        return sorted(r["fact"].rsplit("/", 1)[1] for r in ds.select(query_text("impact_facts")))
    return sorted(str(row.fact).rsplit("/", 1)[1] for row in ds.query(query_text("impact_facts")))


class _Remote:
    """The impact graph loaded into GraphDB (graphs view and delta of the repository, replaced on each load): the
    same SPARQL queries, evaluated by GraphDB instead of rdflib's in-memory engine (property paths over the whole
    view are slow there). Used by the RQ4 evaluation, where the detector runs for every policy x event pair."""

    def __init__(self, ds):
        from .kb import graphdb
        self.db = graphdb
        for g in (VIEW, DELTA):
            graphdb._request("DELETE", graphdb._endpoint(f"/statements?context=<{g}>".replace("<", "%3C")
                                                         .replace(">", "%3E")))
        data = ds.serialize(format="trig").encode("utf-8")
        graphdb._request("POST", graphdb._endpoint("/statements"), data, {"Content-Type": "application/x-trig"},
                         timeout=300)

    def select(self, query):
        return self.db.select(query)


def _graph(kb, update_id, omega, remote):
    ds = impact_graph(kb, update_id, omega)
    return _Remote(ds) if remote else ds


def detect(kb, update_id, policies, omega, remote=False, query="impact_policy"):
    """{policy: {"kinds": set of "a"/"b"/"c", "hits": [(kind, company rule, delta element, fact)]}} for each
    policy whose rules are in kb (installed as K_n (+) P). remote=True evaluates the queries in GraphDB."""
    ds = _graph(kb, update_id, omega, remote)
    facts = affected_facts(ds)
    # F_Delta is passed as FILTER ... IN: rdflib ignores an inline VALUES block inside a UNION branch
    members = ", ".join(f"<{rdf.fact_iri(f)}>" for f in facts) or "<urn:pph21kbs:none>"
    q = query_text(query).replace("FILTER_AFFECTED", f"FILTER(?fact IN ({members}))")
    out = {}
    for p in policies:
        hits = []
        if remote:
            rows = ds.select(q.replace("?r pph:policy ?policy ;", f"?r pph:policy <{rdf.doc_iri(p)}> ;"))
            hits += [(r["kind"], r["rule"], r["element"], r["fact"].rsplit("/", 1)[1]) for r in rows]
        else:
            for row in ds.query(q, initBindings={"policy": URIRef(rdf.doc_iri(p))}):
                hits.append((str(row.kind), str(row.rule), str(row.element), str(row.fact).rsplit("/", 1)[1]))
        out[p] = {"kinds": {h[0] for h in hits}, "hits": sorted(set(hits))}
    return out


def flag_all(kb, update_id, policies, omega, remote=False, facts=None):
    """Baseline B5(i): a policy is flagged when any of its rules reads or produces a fact in F_Delta downstream,
    whatever the validity. facts: F_Delta already computed (skips the query)."""
    if facts is None:
        facts = affected_facts(_graph(kb, update_id, omega, remote))
    facts = set(facts)
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
