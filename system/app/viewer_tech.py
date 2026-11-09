"""Technical view of the KB viewer: the knowledge base system itself (the novelty of the research), with the real KB of
the demo. Architecture, the knowledge graph, one element as RDF, the two times of every element, the version chain of
named graphs, the trace of a calculation, the ontology and the checks, SPARQL and export."""
import io
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import data as d
import employee as emp
import glossary as g
import kbviz as kv
import store

KIND = {"rule": "rule", "parameter": "number", "table": "table", "constraint": "check", "fact": "value",
        "tombstone": "revoked"}
RANK = {4: "4 · mandatory (government)", 3: "3 · company policy", 2: "2 · optional, adopted by the company",
        1: "1 · default"}
WHY = {"lex superior": "lower rank", "lex specialis": "beaten by a more specific rule",
       "lex posterior": "beaten by a newer rule", "redundant": "same value, not used"}
PRESETS = {
    "Rules that produce the monthly PPh 21, with their validity": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT ?id ?validFrom ?validUntil ?graph WHERE {
  GRAPH ?graph { ?rule pph:produces ?f ; pph:elementId ?id ; pph:validFrom ?validFrom .
                 OPTIONAL { ?rule pph:validUntil ?validUntil }
                 FILTER(STRENDS(STR(?f), "/pph21_due")) }
} ORDER BY ?validFrom""",
    "Number of elements per source document": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
PREFIX eli: <http://data.europa.eu/eli/ontology#>
SELECT ?doc (COUNT(DISTINCT ?r) AS ?elements) WHERE {
  GRAPH ?g { ?r pph:hasSource ?q . ?q pph:provision ?p . ?p eli:is_part_of ?doc }
} GROUP BY ?doc ORDER BY DESC(?elements)""",
    "Rules that read the position cost (downstream)": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT DISTINCT ?id ?produces WHERE {
  GRAPH ?g { ?r pph:elementId ?id ; pph:reads ?f ; pph:produces ?produces .
             FILTER(STRENDS(STR(?f), "/job_expense")) }
} ORDER BY ?id""",
    "Elements recorded after their effective date (retroactive)": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT ?id ?validFrom ?recordedOn WHERE {
  GRAPH ?g { ?r pph:elementId ?id ; pph:validFrom ?validFrom ; pph:recordedOn ?recordedOn .
             FILTER(?recordedOn > ?validFrom) }
} ORDER BY DESC(?recordedOn)""",
    "Company rules and their policies": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT ?id ?policy ?fact WHERE {
  GRAPH ?g { ?r pph:policy ?policy ; pph:elementId ?id ; pph:produces ?fact }
} ORDER BY ?policy ?id""",
}
TABS = ["System architecture", "Knowledge graph", "One element as RDF", "Two times (bitemporal)",
        "Versions and named graphs", "Calculation trace", "Ontology and checks", "SPARQL and export"]


@st.cache_resource(show_spinner="Building the RDF graph from the knowledge base ...")
def dataset(signature):
    from pph21kbs.kb import rdf
    return rdf.to_dataset(d.kb())


@st.cache_data(show_spinner="Running the static checker ...")
def static_findings(signature, omega, policies):
    from pph21kbs import static
    rep = static.check(d.kb(), omega, policies=policies)
    return [{"Severity": f.severity, "Type": f.kind, "Element": ", ".join(f.ids), "Value": f.fact, "Detail": f.detail}
            for f in rep.findings]


@st.cache_data(show_spinner="Validating SHACL ...")
def shacl_violations(signature):
    from pph21kbs.kb import shacl
    return [{"Element": str(e), "Message": m} for e, m in shacl.validate(d.kb())]


@st.cache_data
def ontology(signature):
    return kv.ontology_dot()


def stats(view, recs):
    """Counts for the architecture picture; recs = what is in force at the chosen date (as the numbers at the top)."""
    shown = [r for r in recs if not d.is_input_convention(r)]
    return {"reg_rules": sum(r.kind == "rule" and r.layer == "regulation" for r in shown),
            "com_rules": sum(r.kind == "rule" and r.layer == "company" for r in shown),
            "params": sum(r.kind == "parameter" for r in shown), "tables": sum(r.kind == "table" for r in shown),
            "facts": len(view.facts), "updates": len(d.kb().updates)}


def _fact_pick(view, key, default="pph21_due", label="Value to look at"):
    facts = sorted({r.produces for r in view.rules.values()}, key=d.fact_label)
    return st.selectbox(label, facts, index=facts.index(default) if default in facts else 0, key=key,
                        format_func=lambda f: f"{d.fact_label(f)} ({f})")


# ---------------------------------------------------------------- tabs
def tab_architecture(view, t, recs):
    st.caption(f"From document to calculation. The numbers in the picture come from the KB in use now, as in force on {d.tgl(t)}.")
    st.graphviz_chart(kv.architecture_dot(stats(view, recs)), width="stretch")
    rows = [
        ("Acquisition", "Relevance, m proposed versions from the LLM, gates G1–G5, agreement or system unsure",
         "system/pph21kbs/pipeline/ (run, select, consensus)", "New documents, Review"),
        ("Gate G1", "Graph shape matches the SHACL shapes", "system/ontology/shapes.ttl", "Ontology and checks tab"),
        ("Gate G2", "The quote really exists in the document", "system/pph21kbs/pipeline/gates.py", "Review"),
        ("Gate G3", "Static checker: dead rules, rules that always lose, conflicts between levels",
         "system/pph21kbs/static.py", "Ontology and checks tab"),
        ("Gates G4–G5", "Regression on test cases and non-vacuity (the update really changes a calculation)",
         "system/pph21kbs/pipeline/gates.py", "Review: before/after example"),
        ("Knowledge base", "Bitemporal, two-level records; one update = one named graph",
         "system/pph21kbs/kb/ (store, rdf, delta)", "Versions and named graphs tab"),
        ("Ontology", "Classes and relations; uses ELI, OWL-Time, PROV-O", "system/ontology/ontology.ttl",
         "Ontology and checks tab"),
        ("Engine", "Chooses rules (rank, specificity, time), computes the gross-up fixed point, keeps a trace",
         "system/pph21kbs/engine/evaluator.py", "Calculation trace tab, Calculator"),
        ("Impact analysis", "SPARQL queries: which values changed, which company rules read them",
         "system/pph21kbs/impact.py, system/ontology/queries/", "Review: affected policies"),
    ]
    st.dataframe(pd.DataFrame(rows, columns=["Part", "What it does", "Code", "Seen in the app"]), hide_index=True,
                 width="stretch")


def tab_graph(view, t):
    g.md(f"The part of the {g.term('knowledge graph')} around one value: the rules that produce it, the other values "
         "they read, their numbers and tables, and (if chosen) the source articles.")
    c1, c2, c3, c4 = st.columns([1.8, 1, 1.1, 1.3])
    with c1:
        focus = _fact_pick(view, "kt_focus")
    depth = c2.slider("Depth", 1, 5, 2, key="kt_depth")
    way = c3.radio("Direction", ("to sources (upstream)", "to users (downstream)", "both"), key="kt_way")
    with c4:
        only = st.toggle("Only what is in force", True, key="kt_only", help=g.tip("berlaku"))
        prov = st.toggle("Show source articles", False, key="kt_prov", help=g.tip("sumber"))
        layers = st.multiselect("Level", ["regulation", "company"], default=["regulation", "company"], key="kt_layers",
                                format_func={"regulation": "government", "company": "company"}.get)
    dot, n = kv.dependency_dot(view, focus, t, depth, upstream=way != "to users (downstream)",
                               downstream=way != "to sources (upstream)", layers=tuple(layers), only_in_force=only,
                               provenance=prov)
    st.graphviz_chart(dot, width="stretch")
    st.caption(f"{n} rule{'' if n == 1 else 's'}, in force on {d.tgl(t)}. Ellipse = value (fact), blue box = government rule, "
               "orange box = company rule, yellow cylinder = number/table, folder = document, note = article. Thick line = "
               "produces, dashed = reads, dotted = uses a number/table, red = overrides.")
    st.markdown(f"**All rules for *{d.fact_label(focus)}* and how the engine chooses between them**")
    g.md(f"<span class='muted'>{g.term('resolusi konflik', 'Order of choice')}: the highest rank wins; if equal, "
         "the more specific one; if still equal, the one that took effect later.</span>")
    rows = [{"Rule": r.id, "Level": "company" if r.layer == "company" else "government",
             "Rank": RANK.get(r.rank, r.rank), "Effective": f"{d.tgl(r.valid_from)} – {d.tgl(r.valid_until) if r.valid_until else 'now'}",
             "Status on the date": kv.status(r, t), "Overrides": ", ".join(r.overrides) or "-",
             "Source": f"{d.short_doc(r.source[0].document)} {r.source[0].provision}" if r.source else "-"}
            for r in sorted(view.rules_by_fact.get(focus, []), key=lambda r: (-r.rank, r.valid_from or date.min))]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def tab_rdf(view):
    kb = d.kb()
    g.md(f"Every KB element is stored as a set of {g.term('RDF')} triples in the {g.term('named graph')} of its update. "
         "This is the form that is actually stored, queried with SPARQL, and checked with SHACL.")
    ids = sorted({r.id for r in kb.records if r.kind in ("rule", "parameter", "table", "constraint")
                  and not d.is_input_convention(r)})
    label = {r.id: (d.fact_label(r.produces) if r.kind == "rule" else (d.label_of(r) or getattr(r, "name", ""))) for r in kb.records
             if r.id in ids}
    first = next((r.id for r in view.rules_by_fact.get("job_expense", []) if r.id in ids), ids[0])
    c1, c2 = st.columns([2, 1.4])
    rid = c1.selectbox("Element", ids, index=ids.index(first),
                       key="kt_rid", format_func=lambda i: f"{i} · {label.get(i, '')}")
    versions = [r for r in kb.records if r.id == rid]
    i = c2.selectbox("Record (version of the element)", range(len(versions)), index=len(versions) - 1, key=f"kt_rver_{rid}",
                     format_func=lambda k: f"#{versions[k].seq} · recorded {d.tgl(versions[k].recorded_on)} · "
                                           f"{versions[k].update_id}")
    rec, prev = versions[i], (versions[i - 1] if i else None)
    graph = kv.record_graph(rec, prev)
    from pph21kbs.kb import rdf
    m = st.columns(4)
    m[0].metric("Triple", len(graph))
    m[1].metric("Named graph", f"…/update/{rec.update_id}")
    m[2].metric("Version of this element", f"{i + 1} of {len(versions)}")
    m[3].metric("Revision of", f"#{prev.seq}" if prev else "-")
    view_graph, view_table = st.tabs(["Graph", "Triple table"])
    with view_graph:
        st.graphviz_chart(kv.record_rdf_dot(graph), width="stretch")
        st.caption("Blue = resource (IRI), yellow = value (literal), grey circle = unnamed node. The formula is stored "
                   "as text plus a pph:reads relation to every value it reads.")
    with view_table:
        rows = [{"Subject": kv.short(s), "Predicate": kv.short(p), "Object": kv.short(o)} for s, p, o in graph]
        st.dataframe(pd.DataFrame(rows).sort_values(["Subject", "Predicate"]), hide_index=True, width="stretch", height=380)
    with st.expander("Turtle (RDF text)"):
        graph.bind("pph", rdf.PPH)
        graph.bind("kb", rdf.KB)
        graph.bind("eli", rdf.ELI)
        st.code(graph.serialize(format="turtle"), language="turtle")


def tab_bitemporal(t):
    kb = d.kb()
    g.md(f"Every element has two times ({g.term('bitemporal')}): the {g.term('berlaku', 'effective date')} set by the "
         f"regulation and the {g.term('dicatat', 'recorded date')} in the KB. A point below the diagonal line was recorded "
         "after it took effect (retroactive); above it was announced in advance.")
    recs = [r for r in kb.records if r.kind in ("rule", "parameter", "table") and r.valid_from and r.recorded_on
            and not d.is_input_convention(r)]
    fig = go.Figure()
    for layer, color, name in (("regulation", kv.REG, "government"), ("company", kv.COMPANY, "company")):
        pts = [r for r in recs if getattr(r, "layer", "regulation") == layer]
        if pts:
            fig.add_trace(go.Scatter(x=[r.valid_from for r in pts], y=[r.recorded_on for r in pts], mode="markers",
                                     name=name, marker=dict(color=color, size=7, opacity=.75),
                                     hovertext=[f"{r.id}<br>effective {r.valid_from}<br>recorded {r.recorded_on}" for r in pts],
                                     hoverinfo="text"))
    lo, hi = date(2008, 1, 1), date(2027, 6, 30)
    fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", line=dict(color="#b4b3ae", dash="dot"),
                             name="recorded = effective", hoverinfo="skip"))
    fig.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), xaxis_title="Effective from",
                      yaxis_title="Recorded in the KB", plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h"))
    c1, c2 = st.columns([2, 1])
    c1.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    retro = [r for r in recs if r.recorded_on > r.valid_from]
    with c2:
        st.metric("Elements with dates", len(recs))
        st.metric("Recorded after effective date", len(retro))
        early = [r for r in recs if r.recorded_on < r.valid_from]
        lines = [f"Latest recorded {'after' if r in retro else 'before'} its effective date: "
                 f"{d.short_doc(r.source[0].document) if r.source else r.update_id}, recorded {d.tgl(r.recorded_on)} "
                 f"to take effect {d.tgl(r.valid_from)}."
                 for r in (max(group, key=lambda r: (r.recorded_on, r.seq)) for group in (retro, early) if group)]
        st.caption(" ".join(lines) + " The calculator can calculate 'with the knowledge as of a date' to repeat an "
                   "old calculation exactly as it was.")
    st.markdown("**Timeline per value**")
    view = kb.view(d.TODAY)
    facts = sorted({r.produces for r in view.rules.values()}, key=d.fact_label)
    focus = st.multiselect("Value", facts, default=[f for f in ("ptkp_amount", "pph21_running", "pph21_dtp", "jp_wage",
                                                               "ter_rate") if f in facts],
                           key="kt_tl", format_func=d.fact_label)
    rows = sorted([r for r in kb.records if r.kind == "rule" and r.produces in focus and r.valid_from],
                  key=lambda r: (r.produces, r.valid_from, r.seq))
    if not rows:
        return
    fig = go.Figure()
    end = date(2027, 6, 30)
    for i, r in enumerate(rows):
        color = kv.REG if r.layer == "regulation" else kv.COMPANY
        fig.add_trace(go.Scatter(x=[r.valid_from, r.valid_until or end], y=[i, i], mode="lines", line=dict(color=color, width=9),
                                 hovertext=f"{r.id}<br>{d.fact_label(r.produces)}", hoverinfo="text", showlegend=False))
        fig.add_trace(go.Scatter(x=[r.recorded_on], y=[i], mode="markers", showlegend=False, hoverinfo="text",
                                 marker=dict(symbol="diamond", size=9, color="#3b3a37"), hovertext=f"recorded {r.recorded_on}"))
    fig.add_vline(x=t, line_color=kv.REG, line_dash="dash")
    fig.update_layout(height=max(300, 24 * len(rows)), margin=dict(l=10, r=10, t=10, b=10),
                      yaxis=dict(tickvals=list(range(len(rows))), ticktext=[f"{r.id} #{r.seq}" for r in rows],
                                 autorange="reversed"),
                      xaxis=dict(range=[date(2012, 1, 1), end]), plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.caption("Bar = period in force, diamond = recorded date, dashed blue line = the date chosen above.")


def tab_versions():
    kb = d.kb()
    base_n = len(store.base().updates)
    g.md(f"The KB is never overwritten. Each {g.term('pembaruan', 'update')} is stored as one {g.term('named graph')}; "
         f"{g.term('versi', 'version')} n = named graphs 1..n combined. Orange box = an update approved in the app.")
    st.graphviz_chart(kv.chain_dot(kb, base_n), width="stretch")
    per = {}
    for r in kb.records:
        per.setdefault(r.update_id, {}).setdefault(r.kind, 0)
        per[r.update_id][r.kind] += 1
    rows = []
    for i, u in enumerate(kb.updates):
        c = per.get(u.update_id, {})
        rows.append({"Version": i + 1, "Update": u.update_id, "Document": d.short_doc(u.document),
                     "Recorded": u.recorded_on, "Records": sum(c.values()),
                     "Contents": ", ".join(f"{n} {KIND.get(k, k)}" for k, n in c.items()),
                     "Named graph": f"kb:update/{u.update_id}", "Origin": "app" if i >= base_n else "initial KB"})
    st.dataframe(pd.DataFrame(rows[::-1]), hide_index=True, width="stretch", height=320)
    st.markdown("**Compare two versions**")
    c1, c2 = st.columns(2)
    a = c1.number_input("First version", 1, len(kb.updates), max(1, len(kb.updates) - 1), key="kt_va")
    b = c2.number_input("Second version", 1, len(kb.updates), len(kb.updates), key="kt_vb")
    ka, kb2 = kb.until(kb.updates[a - 1].update_id), kb.until(kb.updates[b - 1].update_id)
    sa, sb = {r.seq for r in ka.records}, {r.seq for r in kb2.records}
    new = [r for r in kb2.records if r.seq not in sa]
    gone = [r for r in ka.records if r.seq not in sb]
    m = st.columns(3)
    m[0].metric("Records in the first version", len(ka.records))
    m[1].metric("Records in the second version", len(kb2.records))
    m[2].metric("Fingerprint of the second version", kb2.fingerprint()[:12])
    if new or gone:
        st.dataframe(pd.DataFrame([{"Change": "only in the second version" if r in new else "only in the first version", "Record": f"#{r.seq}",
                                    "Element": r.id, "Type": KIND.get(r.kind, r.kind), "Update": r.update_id,
                                    "Effective": f"{d.tgl(r.valid_from)} – {d.tgl(r.valid_until) if r.valid_until else 'now'}"
                                    if r.valid_from else "-"} for r in new + gone]), hide_index=True, width="stretch")


def tab_trace():
    g.md(f"The engine {g.term('jejak', 'trace')} of one calculation: every value keeps the rule that was used, the values "
         "it read, the rules that lost, and the article. The scenarios come from the calculator.")
    scs = emp.scenarios()
    c1, c2, c3, c4 = st.columns([1.8, 1, 1.6, .8])
    title = c1.selectbox("Scenario", list(scs), key="kt_sc")
    case = emp.scenario_case(scs[title])
    res, err = d.compute(case, d.TODAY)
    if err:
        st.error(err)
        return
    months = sorted(res.periods)
    choices = months + ([0] if res.year else [])
    month = c2.selectbox("Month", choices, index=choices.index(0) if 0 in choices else len(choices) - 1, key="kt_m",
                         format_func=lambda m: "Full year" if m == 0 else d.MONTHS[m - 1])
    facts = sorted({f for (f, m) in res.trace if m == month}, key=d.fact_label)
    default = "annual_pph21" if month == 0 else "pph21_due"
    fact = c3.selectbox("Value", facts, index=facts.index(default) if default in facts else 0, key=f"kt_f{month}",
                        format_func=lambda f: f"{d.fact_label(f)} ({f})")
    depth = c4.slider("Depth", 1, 6, 3, key="kt_d")
    st.graphviz_chart(kv.derivation_dot(res, month, fact, depth=depth), width="stretch")
    st.caption("Blue = government rule, orange = company rule, yellow = case data or recorded value. Zero values "
               "are not drawn.")
    rows = []
    for (f, m), e in res.trace.items():
        src = e["source"][0] if e.get("source") else {}
        if m != month or src.get("document") == "INPUT-CONVENTION":      # data read straight from the case
            continue
        rows.append({"Value": d.fact_label(f), "Result": kv.fmt(f, e["value"]), "Rule": e["rule"],
                     "Level": {"regulation": "government", "company": "company", "case": "case data"}.get(e["layer"], e["layer"]),
                     "Rules not chosen": "; ".join(f"{i} ({WHY.get(w, w)})" for i, w in e.get("losers") or []) or "-",
                     "Source": f"{d.short_doc(src.get('document', ''))} {src.get('provision', '')}".strip() or "-"})
    lost = sum(r["Rules not chosen"] != "-" for r in rows)
    st.markdown(f"**All values this month** · {len(rows)} value{'' if len(rows) == 1 else 's'}, {lost} of them chosen from several rules")
    only = st.toggle("Only values that have rules not chosen", False, key="kt_lost")
    st.dataframe(pd.DataFrame([r for r in rows if not only or r["Rules not chosen"] != "-"]), hide_index=True,
                 width="stretch", height=320)


def tab_checks(t):
    sig = store.signature()
    dot, n_classes, n_props = ontology(sig)
    g.md(f"The system's {g.term('ontologi', 'ontology')}: {n_classes} classes and {n_props} relations. Parent classes come from the "
         "ELI (legislation), PROV-O (provenance), OWL-Time (time), and SKOS standards.")
    st.graphviz_chart(dot, width="content")
    st.caption("Triangle arrow = 'is a kind of'; dashed blue line = relation between classes.")
    st.markdown("**SHACL shapes (gate G1)**")
    st.dataframe(pd.DataFrame(shapes()), hide_index=True, width="stretch")
    st.markdown("**Checks of the current KB**")
    pols = tuple(store.installed_policies())
    rows = static_findings(sig, t, pols)
    errors = [r for r in rows if r["Severity"] == "error"]
    m = st.columns(3)
    m[0].metric("Static checker errors", len(errors), help=g.tip("pemeriksa statis"))
    m[1].metric("Warnings", len(rows) - len(errors))
    m[2].metric("Company policies checked too", len(pols))
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=240)
    if st.button("Run SHACL validation", icon=":material/rule:", key="kt_shacl", help=g.tip("SHACL")):
        v = shacl_violations(sig)
        if v:
            st.error(f"{len(v)} violation{'' if len(v) == 1 else 's'}")
            st.dataframe(pd.DataFrame(v), hide_index=True, width="stretch")
        else:
            st.success("All SHACL shapes are satisfied.")


@st.cache_data
def shapes():
    from rdflib import Graph, Namespace, RDF
    sh = Namespace("http://www.w3.org/ns/shacl#")
    gr = Graph()
    gr.parse(kv.ROOT / "system" / "ontology" / "shapes.ttl")
    out = []
    for s in gr.subjects(RDF.type, sh.NodeShape):
        targets = ", ".join(sorted(kv.short(c) for c in gr.objects(s, sh.targetClass)))
        paths = sorted(kv.short(p) for prop in gr.objects(s, sh.property) for p in gr.objects(prop, sh.path))
        rules = len(list(gr.objects(s, sh.sparql)))
        msgs = [str(m) for x in list(gr.objects(s, sh.sparql)) + list(gr.objects(s, sh.property))
                for m in gr.objects(x, sh.message)]
        out.append({"Shape": kv.short(s), "For class": targets, "Properties checked": ", ".join(paths[:6])
                    + (" …" if len(paths) > 6 else ""), "SPARQL rules": rules, "Example message": msgs[0] if msgs else ""})
    return sorted(out, key=lambda r: r["Shape"])


def tab_sparql():
    g.md(f"{g.term('SPARQL')} queries run directly on the KB graph (one {g.term('named graph')} per update, plus kb:meta).")
    preset = st.selectbox("Example query", list(PRESETS), key="kt_preset")
    q = st.text_area("Query", PRESETS[preset], height=190, key=f"kt_q_{preset}")
    if st.button("Run", icon=":material/play_arrow:", key="kt_run"):
        try:
            res = dataset(store.signature()).query(q)
            rows = [{str(v): (kv.short(row[i]) if row[i] is not None else "") for i, v in enumerate(res.vars)}
                    for row in res]
            st.caption(f"{len(rows)} row{'' if len(rows) == 1 else 's'}")
            st.dataframe(pd.DataFrame(rows[:1000]), hide_index=True, width="stretch")
        except Exception as e:  # noqa: BLE001 - shown to the user
            st.error(f"{type(e).__name__}: {e}")
    st.markdown("**Export**")
    st.caption("Open in Protégé (ontology) or GraphDB / Apache Jena Fuseki (graph and SPARQL).")
    c = st.columns(3)
    if c[0].button("Prepare KB as TriG", icon=":material/data_object:", key="kt_trig"):
        buf = io.BytesIO(dataset(store.signature()).serialize(format="trig").encode("utf-8"))
        st.download_button("Download kb.trig", buf.getvalue(), "kb.trig", "application/trig",
                           icon=":material/download:", key="kt_dl_trig")
    for col, name in zip(c[1:], ("ontology.ttl", "shapes.ttl")):
        col.download_button(f"Download {name}", (kv.ROOT / "system" / "ontology" / name).read_bytes(), name, "text/turtle",
                            key=f"kt_dl_{name}", icon=":material/download:")
    st.caption(f"KB fingerprint: `{d.kb().fingerprint()[:16]}` · {len(d.kb().records)} records · "
               f"{len(d.kb().updates)} updates")


def show(t, recs):
    view = d.kb().view(d.TODAY)
    tabs = st.tabs(TABS)
    with tabs[0]:
        tab_architecture(view, t, recs)
    with tabs[1]:
        tab_graph(view, t)
    with tabs[2]:
        tab_rdf(view)
    with tabs[3]:
        tab_bitemporal(t)
    with tabs[4]:
        tab_versions()
    with tabs[5]:
        tab_trace()
    with tabs[6]:
        tab_checks(t)
    with tabs[7]:
        tab_sparql()
