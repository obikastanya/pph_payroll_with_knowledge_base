"""Technical pictures of the knowledge base system (Graphviz DOT), for the technical view of the KB viewer.

- architecture_dot: the parts of the system and how a document becomes knowledge and a tax result;
- dependency_dot: the knowledge graph around one fact (rules, facts they read, parameters, tables), optionally with
  provenance (document -> article -> rule) and status at a date;
- record_rdf_dot: one element of the knowledge base as RDF triples (what is stored in the graph);
- ontology_dot: the classes and properties of the ontology (system/ontology/ontology.ttl);
- chain_dot: the chain of versions (one named graph per update);
- derivation_dot: how one value of a calculation was derived (from the engine trace).
"""
import re
from pathlib import Path

import data as d

REG, REG_FILL = "#2a78d6", "#e8f1fc"
COMPANY, COMPANY_FILL = "#eb6834", "#fdeee7"
PARAM, PARAM_FILL = "#b98900", "#fff7e0"
DOC_FILL = "#eeeeec"
ROOT = Path(__file__).resolve().parents[2]


def q(text):
    """DOT string; a written \\n inside the text stays a line break."""
    return '"' + str(text).replace('"', "'").replace("\n", " ") + '"'


fmt = d.fmt


def status(r, t):
    if r.valid_from and r.valid_from > t:
        return "belum berlaku"
    if r.valid_until and r.valid_until < t:
        return "tidak berlaku lagi"
    return "berlaku"


# ---------------------------------------------------------------- architecture
def architecture_dot(stats):
    """Three rows: acquisition (top), the knowledge base (middle), what uses it (bottom)."""
    s = stats
    return f"""digraph A {{ rankdir=TB; bgcolor=transparent; nodesep=.35; ranksep=.45; newrank=true;
node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10 color="#b4b3ae" fillcolor="#ffffff"];
edge [color="#8a8984" arrowsize=.7 fontname="Helvetica" fontsize=9 fontcolor="#6b6a66"];
doc [label="Dokumen baru\\nperaturan · PKB · kebijakan\\nPDF · TXT · JSON" shape=note fillcolor="{DOC_FILL}"];
subgraph cluster_acq {{ label="1  Akuisisi pengetahuan berbantuan LLM"; fontname="Helvetica-Bold"; fontsize=10;
  color="{REG}"; fontcolor="{REG}"; style="rounded,dashed";
  rel [label="Relevansi\\n+ pilih bagian dokumen" fillcolor="{REG_FILL}"];
  cand [label="m versi usulan Δ\\n(LLM, keluaran terstruktur)" fillcolor="{REG_FILL}"];
  gates [label="Gerbang G1–G5\\nSHACL · kutipan · statis\\nregresi · non-vakuitas"];
  cons [label="Kesepakatan perilaku\\natau ragu (abstain)"]; }}
rev [label="Review manusia\\nsetujui · sunting · tolak" fillcolor="{COMPANY_FILL}" color="{COMPANY}" penwidth=1.6];
subgraph cluster_kb {{ label="2  Knowledge base: knowledge graph RDF, bitemporal, dua lapis"; fontname="Helvetica-Bold";
  fontsize=10; color="{PARAM}"; fontcolor="#7a5b00"; style="rounded";
  reg [label="Lapis negara\\n{s['reg_rules']} aturan" fillcolor="{REG_FILL}" color="{REG}"];
  com [label="Lapis perusahaan\\n{s['com_rules']} aturan" fillcolor="{COMPANY_FILL}" color="{COMPANY}"];
  par [label="{s['params']} angka · {s['tables']} tabel\\n{s['facts']} jenis nilai" shape=cylinder fillcolor="{PARAM_FILL}" color="{PARAM}"];
  ver [label="{s['updates']} pembaruan = {s['updates']} named graph\\ntanggal berlaku + tanggal dicatat\\nsumber: pasal + kutipan" shape=folder fillcolor="#f7f7f5"];
  onto [label="Ontologi (ELI · OWL-Time · PROV-O)\\n+ shapes SHACL" shape=component fillcolor="#f7f7f5"]; }}
subgraph cluster_use {{ label="3  Pemakaian"; fontname="Helvetica-Bold"; fontsize=10; color="#8a8984"; style="rounded,dashed";
  eng [label="Inference engine\\npilih aturan: kedudukan > khusus > baru\\ntitik tetap · jejak sampai pasal"];
  calc [label="Kalkulator PPh 21" shape=component penwidth=2];
  imp [label="Analisis dampak\\n(SPARQL lintas lapis)" shape=component];
  viewer [label="Penampil KB" shape=component]; }}
{{ rank=same; doc; rel; cand; gates; cons; }}
{{ rank=same; reg; com; par; ver; onto; }}
{{ rank=same; eng; calc; imp; viewer; }}
doc -> rel -> cand -> gates -> cons;
gates -> cand [label="1× perbaikan" style=dashed constraint=false];
cons -> rev; rev -> ver [label="Δ disetujui"];
ver -> imp [label="Δ"]; imp -> rev [style=dashed label="laporan dampak" constraint=false];
reg -> eng; com -> eng; par -> eng; eng -> calc; onto -> viewer [style=dotted];
reg -> com -> par -> ver -> onto [style=invis]; eng -> calc -> imp -> viewer [style=invis]; }}"""


# ---------------------------------------------------------------- knowledge graph around a fact
def dependency_dot(view, focus, t, depth=2, upstream=True, downstream=False, layers=("regulation", "company"),
                   only_in_force=True, provenance=False, max_rules=40):
    rules = [r for r in view.rules.values() if r.layer in layers and not d.is_input_convention(r)]
    if only_in_force:
        rules = [r for r in rules if status(r, t) == "berlaku"]
    by_fact, readers = {}, {}
    for r in rules:
        by_fact.setdefault(r.produces, []).append(r)
        for e in (r.expression, r.condition):
            for f in (e.dependencies() if e is not None else ()):
                readers.setdefault(f, []).append(r)
    chosen, facts, frontier = {}, {focus}, [(focus, 0)]
    while frontier and len(chosen) < max_rules:
        f, dd = frontier.pop(0)
        if dd >= depth:
            continue
        nxt = ([(r, "up") for r in by_fact.get(f, [])] if upstream else []) + \
              ([(r, "down") for r in readers.get(f, [])] if downstream else [])
        for r, way in nxt:
            if r.id in chosen:
                continue
            chosen[r.id] = r
            new = ([g for e in (r.expression, r.condition) if e is not None for g in e.dependencies()]
                   if way == "up" else [r.produces])
            for g in new:
                if g not in facts:
                    facts.add(g)
                    frontier.append((g, dd + 1))
    out = ["digraph K {", "rankdir=LR; bgcolor=transparent; nodesep=0.22; ranksep=0.55;",
           'node [fontname="Helvetica" fontsize=10];', 'edge [fontname="Helvetica" fontsize=8 color="#8a8984"];']
    involved = {r.produces for r in chosen.values()} | {focus} | \
               {g for r in chosen.values() for e in (r.expression, r.condition) if e is not None for g in e.dependencies()}
    for f in sorted(involved):
        fd = view.facts.get(f)
        pen = "penwidth=2.4" if f == focus else ("penwidth=1.5" if fd is not None and fd.output else "")
        out.append(f'{q("f:" + f)} [shape=ellipse style=filled fillcolor="#f7f7f5" color="#6b6a66" {pen} '
                   f'label={q(d.fact_label(f) + chr(92) + "n" + f)}];')
    params, docs = set(), {}
    for r in chosen.values():
        line, fill = (REG, REG_FILL) if r.layer == "regulation" else (COMPANY, COMPANY_FILL)
        stt = status(r, t)
        style = "rounded,filled" + ("" if stt == "berlaku" else ",dashed")
        lab = f"{r.id}\\n{r.modality} · {r.valid_from:%Y-%m}" + (f"..{r.valid_until:%Y-%m}" if r.valid_until else "")
        if stt != "berlaku":
            lab += f"\\n({stt})"
        out.append(f'{q(r.id)} [shape=box style="{style}" color="{line}" fillcolor="{fill if stt == "berlaku" else "#f4f4f2"}" '
                   f'label={q(lab)}];')
        out.append(f'{q(r.id)} -> {q("f:" + r.produces)} [color="#3b3a37" label="produces"];')
        for e in (r.expression, r.condition):
            if e is None:
                continue
            for g in e.dependencies():
                out.append(f'{q("f:" + g)} -> {q(r.id)} [style=dashed];')
            for name in set(d.QUOTED.findall(e.text)) & d.names():
                params.add(name)
                out.append(f'{q("p:" + name)} -> {q(r.id)} [style=dotted color="{PARAM}"];')
        for o in r.overrides:
            if o in chosen:
                out.append(f'{q(r.id)} -> {q(o)} [color="#c62828" fontcolor="#c62828" label="override"];')
        if provenance and r.source:
            s = r.source[0]
            docs.setdefault(s.document, set()).add(s.provision)
            art = f"a:{s.document}:{s.provision}"
            out.append(f'{q(art)} [shape=note style=filled fillcolor="#ffffff" color="#b4b3ae" fontsize=9 label={q(s.provision)}];')
            out.append(f'{q(art)} -> {q(r.id)} [style=dotted color="#b4b3ae" label="hasSource"];')
    for name in sorted(params):
        out.append(f'{q("p:" + name)} [shape=cylinder style=filled fillcolor="{PARAM_FILL}" color="{PARAM}" label={q(name)}];')
    for doc, arts in docs.items():
        out.append(f'{q("d:" + doc)} [shape=folder style=filled fillcolor="{DOC_FILL}" color="#8a8984" label={q(d.short_doc(doc))}];')
        for a in arts:
            out.append(f'{q("d:" + doc)} -> {q(f"a:{doc}:{a}")} [arrowhead=none color="#b4b3ae"];')
    out.append("}")
    return "\n".join(out), len(chosen)


# ---------------------------------------------------------------- one element as RDF
SHORT = {"https://w3id.org/pph21kbs/ontology#": "pph:", "https://w3id.org/pph21kbs/kb/": "kb:",
         "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf:", "http://www.w3.org/2000/01/rdf-schema#": "rdfs:",
         "http://www.w3.org/ns/prov#": "prov:", "http://data.europa.eu/eli/ontology#": "eli:",
         "http://www.w3.org/2001/XMLSchema#": "xsd:", "http://purl.org/dc/terms/": "dcterms:",
         "http://www.w3.org/2004/02/skos/core#": "skos:", "http://www.w3.org/2006/time#": "time:",
         "http://www.w3.org/2002/07/owl#": "owl:"}


def short(term):
    s = str(term)
    for k, v in SHORT.items():
        if s.startswith(k):
            return v + s[len(k):]
    return s if len(s) < 70 else s[:67] + "…"


def record_graph(record, previous=None):
    from rdflib import Graph
    from pph21kbs.kb import rdf
    g = Graph()
    rdf.record_triples(g, record, previous)
    return g


def record_rdf_dot(g):
    from rdflib import BNode, Literal
    out = ["digraph R {", "rankdir=LR; bgcolor=transparent; nodesep=0.18; ranksep=0.5;",
           'node [fontname="Helvetica" fontsize=9];', 'edge [fontname="Helvetica" fontsize=8 color="#8a8984" fontcolor="#55544f"];']
    ids = {}

    def node(t):
        if t in ids:
            return ids[t]
        n = f"n{len(ids)}"
        ids[t] = n
        if isinstance(t, Literal):
            val = str(t)
            out.append(f'{n} [shape=box style="filled" fillcolor="#fff7e0" color="{PARAM}" label={q(val[:60] + ("…" if len(val) > 60 else ""))}];')
        elif isinstance(t, BNode):
            out.append(f'{n} [shape=circle width=.2 label="" style=filled fillcolor="#d9d8d4" color="#8a8984"];')
        else:
            out.append(f'{n} [shape=ellipse style=filled fillcolor="{REG_FILL}" color="{REG}" label={q(short(t))}];')
        return n

    for s, p, o in sorted(g, key=lambda x: (str(x[0]), str(x[1]))):
        out.append(f"{node(s)} -> {node(o)} [label={q(short(p))}];")
    out.append("}")
    return "\n".join(out)


# ---------------------------------------------------------------- ontology
def ontology_dot():
    from rdflib import Graph, OWL, RDF, RDFS
    g = Graph()
    g.parse(ROOT / "system" / "ontology" / "ontology.ttl")
    from rdflib import URIRef
    classes = {c for c in g.subjects(RDF.type, OWL.Class) if isinstance(c, URIRef)}
    out = ["digraph O {", "rankdir=RL; bgcolor=transparent; nodesep=0.12; ranksep=0.9;",
           'node [fontname="Helvetica" fontsize=9 shape=box style="rounded,filled" fillcolor="#ffffff" color="#8a8984"];',
           'edge [fontname="Helvetica" fontsize=8 color="#8a8984" fontcolor="#55544f"];']
    for c in sorted(classes, key=str):
        out.append(f'{q(short(c))} [fillcolor="{REG_FILL}" color="{REG}"];')
    for c in classes:
        for sup in g.objects(c, RDFS.subClassOf):
            if isinstance(sup, URIRef):
                out.append(f'{q(short(c))} -> {q(short(sup))} [arrowhead=empty color="#b4b3ae"];')
    for p in g.subjects(RDF.type, OWL.ObjectProperty):
        for dom in g.objects(p, RDFS.domain):
            for rng in g.objects(p, RDFS.range):
                if isinstance(dom, URIRef) and isinstance(rng, URIRef):
                    out.append(f'{q(short(dom))} -> {q(short(rng))} [label={q(short(p))} style=dashed '
                               f'color="{REG}" fontcolor="{REG}" constraint=false];')
    out.append("}")
    n_props = len(set(g.subjects(RDF.type, OWL.ObjectProperty))) + len(set(g.subjects(RDF.type, OWL.DatatypeProperty)))
    return "\n".join(out), len(classes), n_props


# ---------------------------------------------------------------- chain of versions
def chain_dot(kb, base_count):
    ups = kb.updates
    per = {}
    for r in kb.records:
        per[r.update_id] = per.get(r.update_id, 0) + 1
    out = ["digraph C {", "rankdir=LR; bgcolor=transparent; nodesep=0.15; ranksep=0.25;",
           'node [fontname="Helvetica" fontsize=9 shape=folder style=filled fillcolor="#f7f7f5" color="#8a8984"];',
           'edge [color="#8a8984" arrowsize=.6];']
    shown = list(enumerate(ups))
    if base_count > 8:              # the initial chain is long: first two, an ellipsis, the last three
        keep = set(range(2)) | set(range(base_count - 3, len(ups)))
        shown = [(i, u) for i, u in shown if i in keep]
    prev = None
    for i, u in shown:
        demo_made = i >= base_count
        fill = COMPANY_FILL if demo_made else "#f7f7f5"
        lab = f"v{i + 1}\\n{d.short_doc(u.document)}\\n{u.recorded_on or ''}\\n{per.get(u.update_id, 0)} rekaman"
        out.append(f'u{i} [label={q(lab)} fillcolor="{fill}" color="{COMPANY if demo_made else "#8a8984"}"];')
        if prev is not None:
            gap = i - prev > 1
            out.append(f'u{prev} -> u{i}' + (f' [style=dashed label="… {i - prev - 1} pembaruan"]' if gap else "") + ";")
        prev = i
    out.append("}")
    return "\n".join(out)


# ---------------------------------------------------------------- derivation of one value
def derivation_dot(result, month, fact, depth=3, max_nodes=22, skip_zero=True):
    trace = result.trace or {}

    def entry(f, m):
        return trace.get((f, m)) or trace.get((f, 0))

    def visible(f, m):
        t = entry(f, m)
        return t is not None and not (skip_zero and t["value"] in (0, None, "", False) and (f, m) != (fact, month))

    out = ["digraph D {", "rankdir=RL; bgcolor=transparent; nodesep=0.22; ranksep=0.45;",
           'node [fontname="Helvetica" fontsize=10 shape=box style="rounded,filled" margin="0.1,0.05"];',
           'edge [color="#8a8984" arrowsize=0.7];']
    seen, frontier = set(), [((fact, month), 0)]
    while frontier and len(seen) < max_nodes:
        (f, m), dd = frontier.pop(0)
        t = entry(f, m)
        if t is None or (f, m) in seen:
            continue
        seen.add((f, m))
        if t["layer"] == "company":
            line, fill = COMPANY, COMPANY_FILL
        elif t["layer"] == "case":
            line, fill = PARAM, PARAM_FILL
        else:
            line, fill = REG, REG_FILL
        v = t["value"]
        val = fmt(f, v)
        when = "" if m == month else (" (setahun)" if m == 0 else f" ({d.MON[m - 1]})")
        src = t["source"][0] if t.get("source") else {}
        lab = f"{d.fact_label(f)}{when}\\n{val}\\n{t['rule']}" + (f"\\n{d.short_doc(src['document'])} {src['provision']}"[:60]
                                                                if src.get("document") not in (None, "CASE", "INPUT-CONVENTION") else "")
        pen = " penwidth=2.4" if (f, m) == (fact, month) else ""
        out.append(f'{q(f"{f}@{m}")} [color="{line}" fillcolor="{fill}"{pen} label={q(lab)}];')
        if dd >= depth:
            continue
        for dep in t.get("reads") or []:
            df, dm = dep if isinstance(dep, (list, tuple)) else (dep, m)
            if visible(df, dm) and len(seen) + len(frontier) < max_nodes * 2:
                out.append(f'{q(f"{df}@{dm}")} -> {q(f"{f}@{m}")};')
                frontier.append(((df, dm), dd + 1))
    out.append("}")
    nodes = {f"{f}@{m}" for f, m in seen}
    return "\n".join(x for x in out if "->" not in x or all(n.strip('" ;') in nodes for n in x.split("->")))
