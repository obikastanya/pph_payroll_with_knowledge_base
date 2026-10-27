"""Knowledge-base viewer: the graph, rules, tables, a bitemporal timeline, quality checks, SPARQL, and export."""
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import kg
import reasoner
import state
import widgets as ui

PRESETS = {
    "Rules with layer, modality, and source": """SELECT ?id ?layer ?modality ?fact ?article WHERE {
  ?r a tax:Rule ; tax:id ?id ; tax:layer ?layer ; tax:modality ?modality ; tax:produces/tax:name ?fact ;
     tax:hasSource/tax:label ?article .
} ORDER BY ?layer ?id""",
    "Company policies that depend on PPh 21 (impact path)": """SELECT DISTINCT ?policy ?via WHERE {
  ?p tax:layer tax:CompanyLayer ; tax:id ?policy ; tax:reads ?f .
  ?f (^tax:produces/tax:reads)* ?g .
  ?g tax:name ?via .
  FILTER(?via IN ("pph21", "pph21_withheld"))
}""",
    "Conflicts between mandatory rules and company policies": """SELECT ?rule ?policy ?fact WHERE {
  ?r tax:layer tax:RegulationLayer ; tax:modality "mandatory" ; tax:produces ?f ; tax:id ?rule .
  ?p tax:layer tax:CompanyLayer ; tax:produces ?f ; tax:id ?policy .
  ?f tax:name ?fact .
}""",
    "Repeal chain (supersedes)": """SELECT ?new ?old ?from WHERE {
  ?n tax:supersedes ?o ; tax:id ?new ; tax:validFrom ?from . ?o tax:id ?old .
}""",
    "Documents and how many rules cite them": """SELECT ?document (COUNT(?r) AS ?rules) WHERE {
  ?r tax:hasSource/tax:partOf/tax:label ?document .
} GROUP BY ?document ORDER BY DESC(?rules)""",
}


def _controls():
    c1, c2, c3 = st.columns([2.2, 1.4, 1.6])
    with c1:
        name, g = state.version_picker("Knowledge base", "v_version")
    with c2:
        year, month = ui.period_picker("v", (2024, 8))
    with c3:
        w = ui.knowledge_picker("v")
    return name, g, date(year, month, 1), w


def tab_graph(g, t, w):
    c1, c2, c3 = st.columns([1.4, 1, 1.2])
    mode = c1.radio("View", ("Data flow", "Provenance", "Full"), horizontal=True, key="v_view")
    only = c2.toggle("Only rules in force", False, key="v_only")
    layers = c3.multiselect("Layers", ("regulation", "company"), default=("regulation", "company"), key="v_layers")
    st.graphviz_chart(ui.kb_dot(g, t, w, mode, only, tuple(layers)), width="stretch")
    st.caption("Blue: regulation layer. Orange: company layer. Dashed box: not in force, not yet known, or superseded in "
               "the chosen period. Ellipse: fact (bold = output fact). Cylinder: table. Red: supersedes / conflict.")
    ui.where("Ontology figure and the two-layer representation (skeleton Section IV, K1).")


def tab_rules(g, t, w, repo):
    records = kg.rule_records(g)
    _, _, superseded = reasoner.select(g, t, w)
    df = pd.DataFrame([{"id": r["id"], "status": ui.rule_status(r, t, w, superseded), "layer": r["layer"],
                        "modality": r["modality"], "produces": r["produces"], "valid from": r["valid_from"],
                        "valid until": r["valid_until"], "recorded on": r["recorded_on"], "condition": r["condition"] or "",
                        "expression": r["expression"], "source": r["article"]} for r in records])
    st.dataframe(df, hide_index=True, width="stretch")
    rid = st.selectbox("Rule detail", [r["id"] for r in records], key="v_rule")
    r = next(x for x in records if x["id"] == rid)
    readers = [x["id"] for x in records if r["produces"] in x["reads"]]
    rivals = [x["id"] for x in records if x["produces"] == r["produces"] and x["id"] != rid]
    added_in = next((v for v in repo.versions if rid in {x["id"] for x in kg.rule_records(v.graph)}), None)
    c1, c2 = st.columns(2)
    with c1, st.container(border=True):
        st.markdown(f"#### {rid}")
        st.markdown(f"**{r['layer']} · {r['modality']}** · produces `{r['produces']}`")
        st.markdown(f"Valid **{r['valid_from']}** to **{r['valid_until'] or 'open'}** · recorded on **{r['recorded_on']}**")
        if r["condition"]:
            st.code(f"if {r['condition']}", language="python")
        st.code(f"{r['produces']} := {r['expression']}", language="python")
        if r["supersedes"]:
            st.markdown(f"Repeals: {', '.join(r['supersedes'])}")
    with c2, st.container(border=True):
        st.markdown(f"**Source:** {r['article']}")
        st.markdown(f"> {r['quote']}" if r["quote"] else "_No quote. Rules of K0 were written by the researcher; gate G2 "
                                                          "requires quotes only from LLM updates._")
        st.markdown(f"**Reads:** {', '.join(r['reads']) or '-'}")
        st.markdown(f"**Read by:** {', '.join(readers) or '-'}")
        st.markdown(f"**Same fact as:** {', '.join(rivals) or '-'}")
        if added_in:
            st.markdown(f"**Entered in:** {added_in.name} · {added_in.label} · by {added_in.author}")


def tab_tables(g):
    tables = kg.table_records(g)
    labels = [f"{t['name']} from {t['valid_from']}" for t in tables]
    i = st.selectbox("Table version", range(len(tables)), format_func=lambda k: labels[k], key="v_table")
    t = tables[i]
    st.caption(f"{t['article']} · recorded on {t['recorded_on']} · {len(t['rows'])} rows")
    rows = pd.DataFrame(t["rows"])
    c1, c2 = st.columns([1, 1.4])
    c1.dataframe(rows, hide_index=True, width="stretch", height=360)
    if "lower" in rows:
        x = rows["lower"].astype(int)
        fig = go.Figure(go.Scatter(x=x, y=rows["value"].astype(float), mode="lines", line_shape="hv", name="rate"))
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="lower bound (Rp)",
                          yaxis_title="rate (%)")
        c2.plotly_chart(fig, width="stretch")
    ui.where("Tables are read by the deterministic extraction tool, not typed by the LLM (open decision in Section V).")


def tab_timeline(g, t, w):
    records = kg.rule_records(g)
    end = date(2026, 12, 31)
    fig = go.Figure()
    for r in reversed(records):
        color = ui.REG if r["layer"] == "regulation" else ui.COMPANY
        stop = r["valid_until"] or end
        fig.add_trace(go.Bar(y=[r["id"]], x=[(pd.Timestamp(stop) - pd.Timestamp(r["valid_from"])).total_seconds() * 1000],
                             base=[pd.Timestamp(r["valid_from"])], orientation="h", marker_color=color, opacity=0.75,
                             showlegend=False, hovertext=f"valid {r['valid_from']} to {r['valid_until'] or 'open'}"))
        fig.add_trace(go.Scatter(y=[r["id"]], x=[pd.Timestamp(r["recorded_on"])], mode="markers", showlegend=False,
                                 marker=dict(symbol="diamond", size=10, color="#0b0b0b"),
                                 hovertext=f"recorded on {r['recorded_on']}"))
    fig.add_vline(x=pd.Timestamp(t).timestamp() * 1000, line_color="#c62828", annotation_text="period t")
    if w != reasoner.NOW:
        fig.add_vline(x=pd.Timestamp(w).timestamp() * 1000, line_dash="dot", line_color="#0b0b0b", annotation_text="ω")
    fig.update_layout(height=60 + 28 * len(records), margin=dict(l=10, r=10, t=30, b=10), barmode="overlay",
                      xaxis=dict(type="date", range=["2015-07-01", "2027-01-01"]))
    st.plotly_chart(fig, width="stretch")
    st.caption("Bars: valid time [t_s, t_e]. Diamonds: knowledge time t_c (recorded on). A diamond to the right of the bar's "
               "start is a retroactive rule; a rule counts only when t is inside the bar and ω is right of the diamond.")
    ui.where("Temporal semantics, conditions A3_t and A3_ω (skeleton Sections IV and V).")


def tab_checks(g, t, w):
    conforms, report = kg.shacl_check(g)
    c1, c2, c3 = st.columns(3)
    c1.metric("SHACL (gate G1)", "conforms" if conforms else "violations")
    found = reasoner.anomalies(g, t, w)
    c2.metric("Anomalies in this period", sum(k in ("dangling", "unused") for k, _, _ in found))
    c3.metric("Reported conflicts (A4)", sum(k == "conflict" for k, _, _ in found))
    if not conforms:
        st.code(report)
    st.dataframe(pd.DataFrame(found, columns=["kind", "rule", "detail"]), hide_index=True, width="stretch")
    st.caption("dangling: reads a fact nobody produces (error). unused: produces a fact nobody reads (dead rule). "
               "overridden / conflict: always loses to a higher-ranked rule. superseded: repealed.")
    ui.mockup("The full checker also finds redundant and subsumed rules, and its counts per version feed the RQ3 "
              "diagnostic 'knowledge-base anomalies'.")


def tab_sparql(g):
    preset = st.selectbox("Preset query", list(PRESETS), key="v_preset")
    query = st.text_area("SPARQL", PRESETS[preset], height=170, key=f"v_q_{preset}")
    try:
        rows = g.query(kg.PREFIX + query)
        df = pd.DataFrame([[str(x) for x in row] for row in rows], columns=[str(v) for v in rows.vars])
        st.dataframe(df, hide_index=True, width="stretch")
    except Exception as e:  # noqa: BLE001 - show query errors to the user
        st.error(str(e))
    ui.where("Impact analysis (RQ4) and ablation AB5 (graph query vs flat dependency scan) run on queries like these.")


def tab_export(name, g):
    st.download_button("Download Turtle (.ttl)", g.serialize(format="turtle"), "knowledge_base.ttl", "text/turtle")
    st.download_button("Download ontology", (kg.DATA / "ontology.ttl").read_text(encoding="utf-8"), "ontology.ttl", "text/turtle")
    st.download_button("Download SHACL shapes", (kg.DATA / "shapes.ttl").read_text(encoding="utf-8"), "shapes.ttl", "text/turtle")
    st.markdown(f"{len(g):,} triples in **{name}**.")
    ui.mockup("External viewers: open the Turtle file in Protégé (ontology and classes) or load it into GraphDB or Apache "
              "Jena Fuseki (graph browser and SPARQL endpoint). The full system serves every version from a triple store "
              "with a named graph per version.")
    with st.expander("Turtle preview"):
        st.code(g.serialize(format="turtle")[:6000], language="turtle")


def show():
    st.title("Knowledge base viewer")
    st.markdown("The knowledge graph as the engine sees it in a given period and with a given knowledge date.")
    repo = state.repo()
    name, g, t, w = _controls()
    tabs = st.tabs([":material/hub: Graph", ":material/rule: Rules", ":material/table: Tables", ":material/date_range: Timeline",
                    ":material/verified: Quality checks", ":material/terminal: SPARQL", ":material/download: Export"])
    with tabs[0]:
        tab_graph(g, t, w)
    with tabs[1]:
        tab_rules(g, t, w, repo)
    with tabs[2]:
        tab_tables(g)
    with tabs[3]:
        tab_timeline(g, t, w)
    with tabs[4]:
        tab_checks(g, t, w)
    with tabs[5]:
        tab_sparql(g)
    with tabs[6]:
        tab_export(name, g)
