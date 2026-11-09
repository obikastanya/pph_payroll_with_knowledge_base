"""The knowledge base as an RDF knowledge graph: conversion, SHACL validation, and the optional GraphDB store.

One named graph per update keeps every version. The ontology and the SHACL shapes live in spec/.
"""
import hashlib
import json
import re
import urllib.parse
import urllib.request
from datetime import date
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache

from pyshacl import validate as _validate
from rdflib import Dataset, Graph, Literal, Namespace, RDF, RDFS, XSD
from rdflib.namespace import DCTERMS, PROV, SH, SKOS

from . import config
from .expr import Expression
from .kb import (Constraint, Document, FactDef, KnowledgeBase, Parameter, Rule, Source, TableVersion, Tombstone,
                 UpdateInfo, fraction_text)


# ====================================================================================================================
# RDF conversion (one named graph per update)
# ====================================================================================================================
PPH = Namespace("https://w3id.org/pph21kbs/ontology#")
KB = Namespace("https://w3id.org/pph21kbs/kb/")
ELI = Namespace("http://data.europa.eu/eli/ontology#")
META = KB["meta"]

CLASS = {"rule": PPH.Rule, "parameter": PPH.Parameter, "table": PPH.TableVersion, "constraint": PPH.Constraint,
         "fact": PPH.FactDefinition, "tombstone": PPH.Tombstone}
KIND = {v: k for k, v in CLASS.items()}
CONCEPT = {"regulation": PPH.Regulation, "company": PPH.Company, "mandatory": PPH.Mandatory,
           "default": PPH.Default, "optional": PPH.Optional, "period": PPH.Period, "year": PPH.Year}
NAME = {v: k for k, v in CONCEPT.items()}


def _slug(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def update_iri(update_id):
    return KB[f"update/{update_id}"]


def record_iri(seq):
    return KB[f"record/{seq}"]


def fact_iri(name):
    return KB[f"fact/{name}"]


def doc_iri(doc_id):
    return KB[f"doc/{doc_id}"]


# ---------------------------------------------------------------------- typed values
def value_literal(v):
    if isinstance(v, bool):
        return Literal(v)
    if isinstance(v, int):
        return Literal(v, datatype=XSD.integer)
    if isinstance(v, Fraction):
        if v.denominator == 1:
            return Literal(v.numerator, datatype=XSD.integer)
        text = fraction_text(v)
        if "/" in text:
            return Literal(text, datatype=PPH.fraction)
        return Literal(text, datatype=XSD.decimal)
    if v is None:
        return Literal("", datatype=PPH.null)
    if isinstance(v, date):
        return Literal(v.isoformat(), datatype=XSD.date)
    return Literal(str(v))


def literal_value(lit):
    dt = lit.datatype
    if dt == PPH.null:
        return None
    if dt == XSD.boolean:
        return lit.toPython()
    if dt == XSD.integer:
        return int(str(lit))
    if dt == XSD.decimal:
        return Fraction(Decimal(str(lit)))
    if dt == PPH.fraction:
        return Fraction(str(lit))
    if dt == XSD.date:
        return date.fromisoformat(str(lit))
    return str(lit)


def _normalize(v):
    """Values inside records are Fractions only when not whole (expr.normalize)."""
    if isinstance(v, Fraction) and v.denominator == 1:
        return v.numerator
    return v


# ---------------------------------------------------------------------- writing
def _add_expression_links(g, node, expr, condition=None):
    for e in (expr, condition):
        if e is None:
            continue
        for f in sorted(e.dependencies()):
            g.add((node, PPH.reads, fact_iri(f)))
        for p in sorted(e.params):
            g.add((node, PPH.usesParameter, Literal(p)))
        for t in sorted(e.tables):
            g.add((node, PPH.usesTable, Literal(t)))


def record_triples(g, r, previous=None):
    n = record_iri(r.seq)
    g.add((n, RDF.type, CLASS[r.kind]))
    g.add((n, RDF.type, PPH.KBElement))
    g.add((n, PPH.elementId, Literal(r.id)))
    g.add((n, PPH.seq, Literal(r.seq, datatype=XSD.integer)))
    g.add((n, PPH.recordedOn, Literal(r.recorded_on.isoformat(), datatype=XSD.date)))
    g.add((n, PROV.wasGeneratedBy, update_iri(r.update_id)))
    if previous is not None:
        g.add((n, PROV.wasRevisionOf, record_iri(previous.seq)))
    if r.valid_from is not None:
        g.add((n, PPH.validFrom, Literal(r.valid_from.isoformat(), datatype=XSD.date)))
    if r.valid_until is not None:
        g.add((n, PPH.validUntil, Literal(r.valid_until.isoformat(), datatype=XSD.date)))
    if r.label:
        g.add((n, RDFS.label, Literal(r.label, lang="en")))
    if r.label_id:
        g.add((n, RDFS.label, Literal(r.label_id, lang="id")))
    for i, s in enumerate(r.source):
        q = KB[f"record/{r.seq}/source/{i}"]
        prov_node = KB[f"provision/{s.document}/{_slug(s.provision)}"]
        g.add((n, PPH.hasSource, q))
        g.add((q, RDF.type, PPH.Quote))
        g.add((q, PPH.order, Literal(i, datatype=XSD.integer)))
        g.add((q, PPH.quoteText, Literal(s.quote)))
        g.add((q, PPH.provision, prov_node))
        if s.page is not None:
            g.add((q, PPH.page, Literal(s.page, datatype=XSD.integer)))
        g.add((prov_node, RDF.type, PPH.Provision))
        g.add((prov_node, RDFS.label, Literal(s.provision)))
        g.add((prov_node, ELI.is_part_of, doc_iri(s.document)))
    if isinstance(r, Rule):
        g.add((n, PPH.layer, CONCEPT[r.layer]))
        g.add((n, PPH.modality, CONCEPT[r.modality]))
        g.add((n, PPH.scope, CONCEPT[r.scope]))
        g.add((n, PPH.produces, fact_iri(r.produces)))
        g.add((n, PPH.expression, Literal(r.expression.text)))
        if r.condition is not None:
            g.add((n, PPH.condition, Literal(r.condition.text)))
        if r.fixed_point:
            g.add((n, PPH.fixedPointLower, Literal(r.fixed_point[0].text)))
            g.add((n, PPH.fixedPointUpper, Literal(r.fixed_point[1].text)))
        for i, t in enumerate(r.overrides):
            o = KB[f"record/{r.seq}/overrides/{i}"]
            g.add((n, PPH.overridesEntry, o))
            g.add((o, PPH.order, Literal(i, datatype=XSD.integer)))
            g.add((o, PPH.targetId, Literal(t)))
            g.add((n, PPH.overrides, Literal(t)))
        if r.conflict_code:
            g.add((n, PPH.conflictCode, Literal(r.conflict_code)))
        if r.policy:
            g.add((n, PPH.policy, doc_iri(r.policy)))
        _add_expression_links(g, n, r.expression, r.condition)
    elif isinstance(r, Parameter):
        g.add((n, PPH.name, Literal(r.name)))
        g.add((n, PPH.valueType, Literal(r.value_type)))
        g.add((n, PPH.value, value_literal(r.value)))
    elif isinstance(r, TableVersion):
        g.add((n, PPH.name, Literal(r.name)))
        g.add((n, PPH.tableKind, Literal(r.table_kind)))
        if r.rows_ref:
            g.add((n, PPH.rowsRef, Literal(json.dumps(r.rows_ref, sort_keys=True, ensure_ascii=False))))
        for i, row in enumerate(r.rows):
            rn = KB[f"record/{r.seq}/row/{i}"]
            g.add((n, PPH.hasRow, rn))
            g.add((rn, RDF.type, PPH.TableRow))
            g.add((rn, PPH.order, Literal(i, datatype=XSD.integer)))
            for col, v in row.items():
                c = KB[f"record/{r.seq}/row/{i}/{col}"]
                g.add((rn, PPH.cell, c))
                g.add((c, PPH.column, Literal(col)))
                g.add((c, PPH.value, value_literal(v)))
    elif isinstance(r, Constraint):
        g.add((n, PPH.scope, CONCEPT[r.scope]))
        g.add((n, PPH.assertion, Literal(r.assertion.text)))
        g.add((n, PPH.conflictCode, Literal(r.conflict_code)))
        if r.condition is not None:
            g.add((n, PPH.condition, Literal(r.condition.text)))
        _add_expression_links(g, n, r.assertion, r.condition)
    elif isinstance(r, FactDef):
        g.add((n, PPH.factType, Literal(r.fact_type)))
        g.add((n, PPH.factScope, CONCEPT[r.fact_scope]))
        g.add((n, PPH.output, Literal(bool(r.output))))
        g.add((n, PPH.definesFact, fact_iri(r.id)))
        g.add((fact_iri(r.id), RDF.type, PPH.Fact))
        g.add((fact_iri(r.id), SKOS.prefLabel, Literal(r.id)))
        if r.unit:
            g.add((n, PPH.unit, Literal(r.unit)))
    return n


def to_dataset(kb, versions=True):
    """RDF dataset of the knowledge base: kb:meta plus one named graph per update."""
    ds = Dataset()
    ds.bind("pph", PPH)
    ds.bind("kb", KB)
    ds.bind("eli", ELI)
    ds.bind("prov", PROV)
    meta = ds.graph(META)
    for d in kb.documents.values():
        n = doc_iri(d.id)
        meta.add((n, RDF.type, PPH.LegalDocument))
        meta.add((n, DCTERMS.identifier, Literal(d.id)))
        if d.title:
            meta.add((n, DCTERMS.title, Literal(d.title)))
        if d.issued:
            meta.add((n, PPH.issued, Literal(d.issued.isoformat(), datatype=XSD.date)))
        for i, rid in enumerate(kb.adoptions.get(d.id, ())):
            a = KB[f"doc/{d.id}/adopts/{i}"]
            meta.add((n, PPH.adoptsEntry, a))
            meta.add((a, PPH.order, Literal(i, datatype=XSD.integer)))
            meta.add((a, PPH.targetId, Literal(rid)))
    for i, u in enumerate(kb.updates):
        n = update_iri(u.update_id)
        meta.add((n, RDF.type, PPH.Update))
        meta.add((n, PPH.order, Literal(i, datatype=XSD.integer)))
        meta.add((n, PPH.updateId, Literal(u.update_id)))
        meta.add((n, PPH.deltaId, Literal(u.delta_id)))
        if u.event_id:
            meta.add((n, PPH.triggeredBy, KB[f"event/{u.event_id}"]))
            meta.add((KB[f"event/{u.event_id}"], RDF.type, PPH.ChangeEvent))
            meta.add((KB[f"event/{u.event_id}"], DCTERMS.identifier, Literal(u.event_id)))
        meta.add((n, PPH.document, doc_iri(u.document)))
        if u.recorded_on:
            meta.add((n, PPH.recordedOn, Literal(u.recorded_on.isoformat(), datatype=XSD.date)))
        meta.add((n, PPH.firstSeq, Literal(u.first_seq, datatype=XSD.integer)))
        meta.add((n, PPH.lastSeq, Literal(u.last_seq, datatype=XSD.integer)))
        if u.note:
            meta.add((n, RDFS.comment, Literal(u.note)))
    if versions:
        prefix = KnowledgeBase(name=kb.name)
        for i, u in enumerate(kb.updates):
            prefix = kb.until(u.update_id)
            v = KB[f"version/{i + 1}"]
            meta.add((v, RDF.type, PPH.KBVersion))
            meta.add((v, PPH.order, Literal(i + 1, datatype=XSD.integer)))
            meta.add((v, PPH.hasMember, update_iri(u.update_id)))
            meta.add((v, PPH.fingerprint, Literal(prefix.fingerprint())))
    graphs = {u.update_id: ds.graph(update_iri(u.update_id)) for u in kb.updates}
    last = {}
    for r in kb.records:
        record_triples(graphs[r.update_id], r, last.get(r.id))
        last[r.id] = r
    return ds


def records_graph(kb):
    """All records in one graph (union of the update graphs, with metadata): input of SHACL and SPARQL checks."""
    g = Graph()
    for prefix, ns in (("pph", PPH), ("kb", KB), ("eli", ELI), ("prov", PROV)):
        g.bind(prefix, ns)
    for t in to_dataset(kb, versions=False).quads():
        g.add(t[:3])
    return g


# ---------------------------------------------------------------------- reading
def _one(g, s, p, default=None):
    return next(iter(g.objects(s, p)), default)


def _date_of(g, s, p):
    v = _one(g, s, p)
    return None if v is None else date.fromisoformat(str(v))


def _ordered(g, s, p):
    items = [(int(_one(g, o, PPH.order)), o) for o in g.objects(s, p)]
    return [o for _, o in sorted(items, key=lambda t: t[0])]


def _expr(g, s, p):
    v = _one(g, s, p)
    return None if v is None else Expression(str(v))


def _record_from_graph(g, n, update_id):
    kind = next(KIND[c] for c in g.objects(n, RDF.type) if c in KIND)
    labels = {lit.language: str(lit) for lit in g.objects(n, RDFS.label)}
    sources = []
    for q in _ordered(g, n, PPH.hasSource):
        prov_node = _one(g, q, PPH.provision)
        doc = str(_one(g, prov_node, ELI.is_part_of)).rsplit("/", 1)[1]
        page = _one(g, q, PPH.page)
        sources.append(Source(doc, str(_one(g, prov_node, RDFS.label)), str(_one(g, q, PPH.quoteText)),
                              None if page is None else int(page)))
    common = dict(kind=kind, id=str(_one(g, n, PPH.elementId)), recorded_on=_date_of(g, n, PPH.recordedOn),
                  source=tuple(sources), seq=int(_one(g, n, PPH.seq)), update_id=update_id,
                  valid_from=_date_of(g, n, PPH.validFrom), valid_until=_date_of(g, n, PPH.validUntil),
                  label=labels.get("en", ""), label_id=labels.get("id", ""))
    if kind == "rule":
        lower, upper = _expr(g, n, PPH.fixedPointLower), _expr(g, n, PPH.fixedPointUpper)
        policy = _one(g, n, PPH.policy)
        return Rule(**common, layer=NAME[_one(g, n, PPH.layer)], modality=NAME[_one(g, n, PPH.modality)],
                    scope=NAME[_one(g, n, PPH.scope)], produces=str(_one(g, n, PPH.produces)).rsplit("/", 1)[1],
                    condition=_expr(g, n, PPH.condition), expression=_expr(g, n, PPH.expression),
                    fixed_point=(lower, upper) if lower is not None else None,
                    overrides=tuple(str(_one(g, o, PPH.targetId)) for o in _ordered(g, n, PPH.overridesEntry)),
                    conflict_code=(str(_one(g, n, PPH.conflictCode)) if _one(g, n, PPH.conflictCode) else None),
                    policy=None if policy is None else str(policy).rsplit("/", 1)[1])
    if kind == "parameter":
        return Parameter(**common, name=str(_one(g, n, PPH.name)),
                         value=_normalize(literal_value(_one(g, n, PPH.value))),
                         value_type=str(_one(g, n, PPH.valueType)))
    if kind == "table":
        rows = []
        for rn in _ordered(g, n, PPH.hasRow):
            row = {}
            for c in g.objects(rn, PPH.cell):
                row[str(_one(g, c, PPH.column))] = _normalize(literal_value(_one(g, c, PPH.value)))
            rows.append(row)
        ref = _one(g, n, PPH.rowsRef)
        return TableVersion(**common, name=str(_one(g, n, PPH.name)), table_kind=str(_one(g, n, PPH.tableKind)),
                            rows=tuple(_order_row(r, str(_one(g, n, PPH.tableKind))) for r in rows),
                            rows_ref=None if ref is None else json.loads(str(ref)))
    if kind == "constraint":
        return Constraint(**common, scope=NAME[_one(g, n, PPH.scope)], condition=_expr(g, n, PPH.condition),
                          assertion=_expr(g, n, PPH.assertion), conflict_code=str(_one(g, n, PPH.conflictCode)))
    if kind == "fact":
        unit = _one(g, n, PPH.unit)
        return FactDef(**common, fact_type=str(_one(g, n, PPH.factType)), fact_scope=NAME[_one(g, n, PPH.factScope)],
                       output=bool(_one(g, n, PPH.output).toPython()), unit="" if unit is None else str(unit))
    return Tombstone(**common)


_ROW_ORDER = {"lookup": ("key", "value"), "bracket": ("key", "lower", "upper", "value"),
              "progressive": ("lower", "upper", "rate")}


def _order_row(row, kind):
    """Column order of normalised rows (kb.normalize_rows), so the canonical JSON and fingerprint match."""
    order = _ROW_ORDER.get(kind)
    if order is None:
        return row
    return {k: row[k] for k in order if k in row} | {k: v for k, v in row.items() if k not in order}


def from_dataset(ds, name="K"):
    """Rebuild a KnowledgeBase from the RDF dataset written by to_dataset (or loaded from GraphDB)."""
    meta = ds.graph(META)
    documents, adoptions = {}, {}
    for n in meta.subjects(RDF.type, PPH.LegalDocument):
        doc_id = str(_one(meta, n, DCTERMS.identifier))
        title = _one(meta, n, DCTERMS.title)
        documents[doc_id] = Document(doc_id, "" if title is None else str(title), _date_of(meta, n, PPH.issued))
        adopted = tuple(str(_one(meta, a, PPH.targetId)) for a in _ordered(meta, n, PPH.adoptsEntry))
        if adopted:
            adoptions[doc_id] = adopted
    updates = []
    for n in _ordered_subjects(meta, PPH.Update):
        ev = _one(meta, n, PPH.triggeredBy)
        note = _one(meta, n, RDFS.comment)
        updates.append(UpdateInfo(str(_one(meta, n, PPH.updateId)), str(_one(meta, n, PPH.deltaId)),
                                  None if ev is None else str(ev).rsplit("/", 1)[1],
                                  str(_one(meta, n, PPH.document)).rsplit("/", 1)[1],
                                  _date_of(meta, n, PPH.recordedOn), int(_one(meta, n, PPH.firstSeq)),
                                  int(_one(meta, n, PPH.lastSeq)), "" if note is None else str(note)))
    records = []
    for u in updates:
        g = ds.graph(update_iri(u.update_id))
        for n in g.subjects(RDF.type, PPH.KBElement):
            records.append(_record_from_graph(g, n, u.update_id))
    records.sort(key=lambda r: r.seq)
    return KnowledgeBase(records, updates, documents, name, adoptions)


def _ordered_subjects(g, cls):
    items = [(int(_one(g, s, PPH.order)), s) for s in g.subjects(RDF.type, cls)]
    return [s for _, s in sorted(items, key=lambda t: t[0])]


def write_trig(kb, path):
    to_dataset(kb).serialize(destination=str(path), format="trig")


def read_trig(path, name="K"):
    ds = Dataset()
    ds.parse(str(path), format="trig")
    return from_dataset(ds, name)


# ====================================================================================================================
# SHACL validation
# ====================================================================================================================
PREFIXES = """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
PREFIX eli: <http://data.europa.eu/eli/ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""


@lru_cache(maxsize=1)
def shapes():
    g = Graph()
    g.parse(config.SPEC / "shapes.ttl", format="turtle")
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
    g = records_graph(kb)
    for doc_id in documents or ():
        n = doc_iri(doc_id)
        g.add((n, RDF.type, PPH.LegalDocument))
        g.add((n, DCTERMS.identifier, Literal(doc_id)))
    return g


def registered_documents():
    """Ids of the documents a record may cite (the document registry)."""
    from .documents import registry
    return sorted(registry())


def validate(kb, documents=None):
    """Violations as a sorted list of (element id or node, message). Empty list means the shapes hold."""
    if documents is None:
        documents = registered_documents()
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
    eid = g.value(node, PPH.elementId)
    return str(eid) if eid is not None else str(node)


# ====================================================================================================================
# GraphDB (optional)
# ====================================================================================================================
def _endpoint(path=""):
    return f"{config.GRAPHDB_URL}/repositories/{config.GRAPHDB_REPOSITORY}{path}"


def _request(method, url, data=None, headers=None, timeout=60):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def graphdb_available():
    try:
        _request("GET", _endpoint("/size"), timeout=5)
        return True
    except OSError:
        return False


def graphdb_size():
    return int(_request("GET", _endpoint("/size")))


def graphdb_clear():
    _request("DELETE", _endpoint("/statements"))


def graphdb_upload(kb, replace=True):
    """Store the knowledge base; with replace=True the repository is cleared first."""
    if replace:
        graphdb_clear()
    data = to_dataset(kb).serialize(format="trig").encode("utf-8")
    _request("POST", _endpoint("/statements"), data, {"Content-Type": "application/x-trig"})
    return graphdb_size()


def graphdb_load(kb):
    """Replace the repository content with the ontology and the knowledge base; returns the number of statements."""
    graphdb_clear()
    _request("POST", _endpoint("/statements"), (config.SPEC / "ontology.ttl").read_bytes(),
             {"Content-Type": "text/turtle"})
    return graphdb_upload(kb, replace=False)
