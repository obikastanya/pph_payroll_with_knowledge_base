"""Gate G1 item 2: SHACL validation of K' (system/ontology/shapes.ttl, akuisisi.md section 4).

The data graph holds every record of the knowledge base (all versions, rdf.records_graph) and the documents known to
the corpus registry, so that a provision must belong to a document of dataset/13_teks/dokumen.csv.

pyshacl evaluates SHACL-SPARQL constraints once per focus node, which takes minutes on the gold graph. The validator
therefore runs the core shapes with pyshacl and evaluates each sh:sparql constraint once over the whole graph with
$this as an ordinary variable, keeping only results whose $this is a target of the shape. For SELECT constraints
whose only free pre-bound variable is $this this gives the same results as SHACL-SPARQL.
"""
import re
from functools import lru_cache

from pyshacl import validate as _validate
from rdflib import RDF, Graph, Literal
from rdflib.namespace import DCTERMS, SH

from ..config import REPO
from . import rdf

ONTOLOGY_DIR = REPO / "system" / "ontology"
PREFIXES = """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
PREFIX eli: <http://data.europa.eu/eli/ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""


@lru_cache(maxsize=1)
def shapes():
    g = Graph()
    g.parse(ONTOLOGY_DIR / "shapes.ttl", format="turtle")
    return g


@lru_cache(maxsize=1)
def _split():
    """(core shapes graph without sh:sparql, list of (target classes, message, query))."""
    full = shapes()
    core = Graph()
    sparql = []
    skip = set()
    for shape in full.subjects(RDF.type, SH.NodeShape):
        targets = list(full.objects(shape, SH.targetClass))
        for c in full.objects(shape, SH.sparql):
            skip.add(c)
            query = str(full.value(c, SH.select))
            msg = str(full.value(c, SH.message))
            sparql.append((targets, msg, re.sub(r"\$this\b", "?this", query)))
    for s, p, o in full:
        if p == SH.sparql or s in skip:
            continue
        core.add((s, p, o))
    return core, sparql


def data_graph(kb, documents=None):
    g = rdf.records_graph(kb)
    for doc_id in documents or ():
        n = rdf.doc_iri(doc_id)
        g.add((n, RDF.type, rdf.PPH.LegalDocument))
        g.add((n, DCTERMS.identifier, Literal(doc_id)))
    return g


def corpus_documents():
    from ..text import registry
    return sorted(registry())


def validate(kb, documents=None):
    """Violations as a sorted list of (element id or node, message). Empty list means the shapes hold."""
    if documents is None:
        documents = corpus_documents()
    g = data_graph(kb, documents)
    core, sparql = _split()
    out = set()
    conforms, report, _ = _validate(g, shacl_graph=core, inference="none", allow_warnings=True)
    if not conforms:
        for res in report.subjects(RDF.type, SH.ValidationResult):
            focus = report.value(res, SH.focusNode)
            msg = str(report.value(res, SH.resultMessage) or report.value(res, SH.sourceConstraintComponent))
            out.add((_name(g, focus), msg))
    for targets, msg, query in sparql:
        for row in g.query(PREFIXES + query):
            focus = row.this
            if any((focus, RDF.type, t) in g for t in targets):
                out.add((_name(g, focus), msg))
    return sorted(out)


def _name(g, node):
    eid = g.value(node, rdf.PPH.elementId)
    return str(eid) if eid is not None else str(node)
