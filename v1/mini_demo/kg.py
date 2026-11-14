"""Mini knowledge graph (skeleton Section IV).

Structural knowledge is stored as RDF: documents, articles, rules, facts, and versioned tables. Computational
knowledge (the expressions) is stored as literals on rule nodes and executed by reasoner.py.
A Delta update (JSON in data/gold/ and data/mock_llm/) is applied with apply_delta().
"""
import csv
import re
from pathlib import Path

from pyshacl import validate
from rdflib import RDF, BNode, Graph, Literal, Namespace
from rdflib.namespace import XSD

REPO = Path(__file__).resolve().parents[1]
DATA = Path(__file__).resolve().parent / "data"
TAX = Namespace("https://w3id.org/pph21/ontology#")
KB = Namespace("https://w3id.org/pph21/kb#")
LAYERS = {"regulation": TAX.RegulationLayer, "company": TAX.CompanyLayer}
DOCUMENT_TYPES = {"regulation": TAX.Regulation, "company": TAX.CompanyPolicy}
PREFIX = "PREFIX tax: <https://w3id.org/pph21/ontology#>\n"


class UpdateError(ValueError):
    pass


def _slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-")


def empty_graph():
    g = Graph()
    g.bind("tax", TAX)
    g.bind("kb", KB)
    return g


def copy_graph(g):
    h = empty_graph()
    for t in g:
        h.add(t)
    return h


def extract_table(spec):
    """Deterministic table-extraction tool: reads rows from a dataset CSV instead of letting the LLM copy them."""
    rows = []
    with open(REPO / spec["file"], encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if any(r.get(k) != v for k, v in spec.get("filter", {}).items()):
                continue
            value = (r.get(spec["value"]) or "").strip()
            if not value:
                continue
            row = {"value": spec.get("prefix", "") + value}
            if "key" in spec:
                row["key"] = r[spec["key"]]
                row["value"] = spec.get("override", {}).get(row["key"], row["value"])
            else:
                row["lower"] = int(r[spec["lower"]])
                row["upper"] = int(r[spec["upper"]]) if r[spec["upper"]].strip() else None
            rows.append(row)
    return rows


def _source(g, source, layer):
    doc = KB["doc-" + _slug(source["document"])]
    article = KB["article-" + _slug(source["document"] + " " + source["article"])]
    g.add((doc, RDF.type, DOCUMENT_TYPES.get(layer, TAX.Document)))
    g.add((doc, TAX.label, Literal(source["document"])))
    g.add((article, RDF.type, TAX.Article))
    g.add((article, TAX.label, Literal(f"{source['document']} {source['article']}")))
    g.add((article, TAX.partOf, doc))
    return article


def _fact(g, name):
    n = KB["fact-" + name]
    g.add((n, RDF.type, TAX.Fact))
    g.add((n, TAX.name, Literal(name)))
    return n


def apply_delta(g, delta, recorded_on):
    """K' = K (+) Delta. Returns a new graph; the old graph is left untouched."""
    import reasoner

    if delta.get("change") or delta.get("remove"):
        raise UpdateError("the mini demo only supports 'add' and 'tables'; repeal is expressed with 'supersedes'")
    h = copy_graph(g)
    for r in delta.get("add", []):
        n = KB[_slug(r["id"])]
        if (n, RDF.type, TAX.Rule) in h:
            raise UpdateError(f"rule {r['id']} already exists")
        h.add((n, RDF.type, TAX.Rule))
        h.add((n, TAX.id, Literal(r["id"])))
        h.add((n, TAX.layer, LAYERS.get(r.get("layer"), Literal(str(r.get("layer"))))))
        h.add((n, TAX.modality, Literal(r.get("modality", ""))))
        h.add((n, TAX.validFrom, Literal(r["valid_from"], datatype=XSD.date)))
        if r.get("valid_until"):
            h.add((n, TAX.validUntil, Literal(r["valid_until"], datatype=XSD.date)))
        h.add((n, TAX.recordedOn, Literal(r.get("recorded_on", recorded_on), datatype=XSD.date)))
        h.add((n, TAX.produces, _fact(h, r["produces"])))
        if r.get("condition"):
            h.add((n, TAX.condition, Literal(r["condition"])))
        h.add((n, TAX.expression, Literal(r["expression"])))
        for old in r.get("supersedes", []):
            h.add((n, TAX.supersedes, KB[_slug(old)]))
        if r.get("source"):
            h.add((n, TAX.hasSource, _source(h, r["source"], r.get("layer"))))
            if r["source"].get("quote"):
                h.add((n, TAX.quote, Literal(r["source"]["quote"])))
        try:
            read = reasoner.dependencies(r.get("condition"), r["expression"])
        except Exception as e:
            raise UpdateError(f"invalid expression in rule {r['id']}: {e}") from None
        for f in read:
            h.add((n, TAX.reads, _fact(h, f)))
    for t in delta.get("tables", []):
        n = KB[f"table-{_slug(t['name'])}-{t['valid_from']}"]
        h.add((n, RDF.type, TAX.Table))
        h.add((n, TAX.name, Literal(t["name"])))
        h.add((n, TAX.validFrom, Literal(t["valid_from"], datatype=XSD.date)))
        h.add((n, TAX.recordedOn, Literal(t.get("recorded_on", recorded_on), datatype=XSD.date)))
        if t.get("source"):
            h.add((n, TAX.hasSource, _source(h, t["source"], "regulation")))
        for i, row in enumerate(t.get("rows") or extract_table(t["extract"])):
            b = BNode()
            h.add((n, TAX.row, b))
            h.add((b, TAX.order, Literal(i)))
            for column in ("key", "lower", "upper", "value"):
                if row.get(column) is not None:
                    h.add((b, TAX[column], Literal(str(row[column]))))
    return h


def shacl_check(g):
    """Gate G1: the graph conforms to the SHACL shapes."""
    shapes = Graph().parse(DATA / "shapes.ttl")
    ontology = Graph().parse(DATA / "ontology.ttl")
    conforms, _, text = validate(g, shacl_graph=shapes, ont_graph=ontology, inference="rdfs")
    return conforms, text


def _values(ids):
    return ", ".join(f'"{i}"' for i in ids) or '""'


def impacted_policies(g, changed_rules):
    """Cross-layer impact analysis (RQ4). A company policy is impacted if it reads, directly or through a chain of rules,
    a fact produced by a changed rule, or if it produces the same fact as a changed mandatory rule."""
    q_reads = PREFIX + f"""
    SELECT DISTINCT ?pid WHERE {{
      ?p tax:layer tax:CompanyLayer ; tax:id ?pid ; tax:reads ?f .
      ?f (^tax:produces/tax:reads)* ?g .
      ?r tax:produces ?g ; tax:id ?rid .
      FILTER(?rid IN ({_values(changed_rules)}))
    }}"""
    q_conflict = PREFIX + f"""
    SELECT DISTINCT ?pid WHERE {{
      ?p tax:layer tax:CompanyLayer ; tax:id ?pid ; tax:produces ?f .
      ?r tax:layer tax:RegulationLayer ; tax:modality "mandatory" ; tax:produces ?f ; tax:id ?rid .
      FILTER(?rid IN ({_values(changed_rules)}) || ?pid IN ({_values(changed_rules)}))
    }}"""
    return {str(row.pid) for q in (q_reads, q_conflict) for row in g.query(q)}


def static_conflicts(g):
    """(mandatory rule, company policy, fact) triples that produce the same fact. Reported by gate G3 (condition A4)."""
    q = PREFIX + """
    SELECT ?rid ?pid ?name WHERE {
      ?r tax:layer tax:RegulationLayer ; tax:modality "mandatory" ; tax:produces ?f ; tax:id ?rid .
      ?p tax:layer tax:CompanyLayer ; tax:produces ?f ; tax:id ?pid .
      ?f tax:name ?name .
    }"""
    return sorted((str(row.rid), str(row.pid), str(row.name)) for row in g.query(q))


def _date(literal):
    return literal.toPython() if literal is not None else None


def _source_labels(g, node):
    article = g.value(node, TAX.hasSource)
    if article is None:
        return "", ""
    return str(g.value(g.value(article, TAX.partOf), TAX.label)), str(g.value(article, TAX.label))


def rule_records(g):
    """Every rule node as a plain record, for viewers and reports."""
    out = []
    for n in g.subjects(RDF.type, TAX.Rule):
        v = lambda p: g.value(n, p)  # noqa: E731
        document, article = _source_labels(g, n)
        out.append({"id": str(v(TAX.id)), "layer": "regulation" if v(TAX.layer) == TAX.RegulationLayer else "company",
                    "modality": str(v(TAX.modality)), "valid_from": _date(v(TAX.validFrom)),
                    "valid_until": _date(v(TAX.validUntil)), "recorded_on": _date(v(TAX.recordedOn)),
                    "produces": str(g.value(v(TAX.produces), TAX.name)),
                    "condition": str(v(TAX.condition)) if v(TAX.condition) else None,
                    "expression": str(v(TAX.expression)),
                    "reads": sorted(str(g.value(f, TAX.name)) for f in g.objects(n, TAX.reads)),
                    "supersedes": sorted(str(g.value(x, TAX.id)) for x in g.objects(n, TAX.supersedes)),
                    "document": document, "article": article, "quote": str(v(TAX.quote)) if v(TAX.quote) else None})
    return sorted(out, key=lambda r: (r["valid_from"], r["layer"], r["id"]))


def table_records(g):
    """Every table version as a plain record, rows in order."""
    out = []
    for n in g.subjects(RDF.type, TAX.Table):
        rows = sorted(((int(g.value(b, TAX.order)), {k: str(g.value(b, TAX[k])) for k in ("key", "lower", "upper", "value")
                                                        if g.value(b, TAX[k]) is not None})
                       for b in g.objects(n, TAX.row)), key=lambda x: x[0])
        document, article = _source_labels(g, n)
        out.append({"name": str(g.value(n, TAX.name)), "valid_from": _date(g.value(n, TAX.validFrom)),
                    "recorded_on": _date(g.value(n, TAX.recordedOn)), "document": document, "article": article,
                    "rows": [r for _, r in rows]})
    return sorted(out, key=lambda t: (t["name"], t["valid_from"]))


def known_rules(g):
    """Context for the LLM: existing rule ids and the facts they produce."""
    q = PREFIX + "SELECT ?id ?name WHERE { ?r tax:id ?id ; tax:produces ?f . ?f tax:name ?name }"
    return sorted((str(row.id), str(row.name)) for row in g.query(q))


def save(g, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(path), format="turtle")
