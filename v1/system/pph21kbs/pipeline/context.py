"""Knowledge-base context for the LLM (akuisisi.md 3.3), from the graph of the base knowledge base.

(1) vocabulary: every fact with type, scope, output flag, English and Indonesian label, and the function catalogue;
(2) relevant records: records whose Indonesian or English label occurs in the selected segments (seeds), the rules
    that produce or read the facts of the seeds (one step up and down, SPARQL over the view graph), and the rules of
    the main output facts;
(3) for each record: id, layer, modality, scope, validity, condition, expression, overrides, source document and
    provision.
AB2 (ablation) uses part (1) only.
"""
import json
import re
from datetime import timedelta
from fractions import Fraction

from rdflib import Graph

from ..expr.functions import CONTEXT_FACTS, FUNCTIONS
from ..kb import rdf
from ..kb.model import FactDef, Parameter, Rule, TableVersion
from ..kb.serialize import fraction_text, record_to_json
from ..text import normalize

MAIN_OUTPUTS = ("pph21_due", "gross_income", "annual_pph21", "taxable_income", "pph21_dtp")
NEIGHBOURS = """
PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT DISTINCT ?id WHERE {
  VALUES ?f { %s }
  { ?r pph:produces ?f } UNION { ?r pph:reads ?f }
  ?r pph:elementId ?id .
}"""


def vocabulary_text(view):
    lines = ["FACTS (name | type | scope | output | label | label_id):"]
    for f in sorted(view.facts.values(), key=lambda f: (f.fact_scope, f.id)):
        lines.append(f"{f.id} | {f.fact_type} | {f.fact_scope} | {'output' if f.output else '-'} | {f.label} | "
                     f"{f.label_id}")
    lines.append("")
    lines.append("BUILT-IN CONTEXT FACTS (no rule produces them): " + ", ".join(
        f"{k} ({t}, {s})" for k, (t, s) in sorted(CONTEXT_FACTS.items())))
    lines.append("")
    lines.append("FUNCTIONS (name(arity): meaning):")
    for spec in sorted(FUNCTIONS.values(), key=lambda s: s.name):
        arity = str(spec.min_args) if spec.min_args == spec.max_args else f"{spec.min_args}..{spec.max_args or 'n'}"
        lines.append(f"{spec.name}({arity}) [{spec.scope}]: {spec.doc}")
    names = sorted({p.name for p in view.records if isinstance(p, Parameter)})
    tables = sorted({t.name for t in view.records if isinstance(t, TableVersion)})
    lines.append("")
    lines.append("PARAMETER NAMES: " + ", ".join(names))
    lines.append("TABLE NAMES: " + ", ".join(tables))
    return "\n".join(lines)


def _record_line(r):
    d = record_to_json(r, with_source=False)
    d.pop("recorded_on", None)
    if isinstance(r, TableVersion):
        rows = d.pop("rows", None)
        if rows is not None:
            rows = [{k: (fraction_text(v) if isinstance(v, Fraction) else v) for k, v in row.items()}
                    for row in r.rows]
            d["rows"] = rows[:12] + ([f"... {len(rows) - 12} more rows"] if len(rows) > 12 else [])
    if r.source:
        d["source"] = f"{r.source[0].document} {r.source[0].provision}"
    d["first_recorded"] = None
    return d


GENERIC_ID_TOKENS = {"reg", "prs", "par", "tab", "con", "input", "default", "billed"}


def _id_tokens(record_id):
    """Abbreviations in an element id (REG.BPJS.JKK_RATE -> bpjs, jkk, rate), used to match documents that write
    JKK, JP, JHT instead of the full labels."""
    parts = re.split(r"[._]", record_id.lower())
    return {p for p in parts if p.isalpha() and len(p) >= 2 and p not in GENERIC_ID_TOKENS}


def relevant_records(view, segment_text, limit=220):
    text = normalize(segment_text)
    words = set(re.findall(r"[a-z]{2,}", text))
    oldest = view.omega - timedelta(days=365)
    current = [r for r in view.records if r.valid_until is None or r.valid_until >= oldest]
    seeds = []
    for r in current:
        labels = [normalize(x) for x in (getattr(r, "label_id", ""), getattr(r, "label", "")) if x]
        if any(len(lab) >= 5 and lab in text for lab in labels):
            seeds.append(r)
        elif not isinstance(r, FactDef) and (_id_tokens(r.id) & words) - {"rate", "wage", "cap", "year", "month",
                                                                           "amount", "status", "value", "final",
                                                                           "running", "gross", "net", "tax"}:
            seeds.append(r)
    facts = set()
    for r in seeds:
        if isinstance(r, Rule):
            facts.add(r.produces)
        elif isinstance(r, FactDef):
            facts.add(r.id)
        elif isinstance(r, (Parameter, TableVersion)):
            for rule in view.rules.values():
                e = rule.expression
                if r.name in (e.params | e.tables):
                    facts.add(rule.produces)
    facts |= set(MAIN_OUTPUTS)
    ids = {r.id for r in seeds}
    if facts:
        g = Graph()
        for r in view.records:
            if isinstance(r, Rule):
                rdf.record_triples(g, r)
        values = " ".join(f"<{rdf.fact_iri(f)}>" for f in sorted(facts))
        ids |= {str(row.id) for row in g.query(NEIGHBOURS % values)}
    chosen = [r for r in current if r.id in ids and not isinstance(r, FactDef)]
    chosen.sort(key=lambda r: (r.kind, r.id))
    return chosen[:limit]


def context_text(view, segment_text, records=True):
    parts = [vocabulary_text(view)]
    if records:
        recs = relevant_records(view, segment_text)
        parts.append(f"RELEVANT RECORDS OF THE KNOWLEDGE BASE ({len(recs)}; effective records at the knowledge "
                     "date; change an element by repeating its id in change, close it by setting valid_until):")
        for r in recs:
            first = view.first_recorded.get(r.id)
            d = _record_line(r)
            d["first_recorded"] = first.isoformat() if first else None
            parts.append(json.dumps(d, ensure_ascii=False))
    return "\n".join(parts)
