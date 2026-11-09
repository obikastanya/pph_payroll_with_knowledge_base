"""Knowledge base viewer page: see and understand what the system knows, and how the knowledge base system works.

The content view shows topics instead of rule ids, a picture of the calculation, numbers over time, what changed and
when, a comparison of two dates, search, the data the calculator asks for, and the installed company policies. The
technical view (show_technical) shows the system itself with the knowledge base in use: architecture, the knowledge
graph, one element as RDF, the two times of every element, the version chain of named graphs, the trace of a
calculation, the ontology and the checks, SPARQL and export. The diagrams are Graphviz DOT texts built here.
"""
import io
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from rdflib import BNode, Graph, Literal, OWL, RDF, RDFS, URIRef
from rdflib.namespace import SH

import calculator
import common
import state
from manage import GATES
from pph21kbs import config, consistency, graph


# ====================================================================================================================
# Records in force at a date
# ====================================================================================================================
@st.cache_data
def snapshot(signature, t):
    """Records in force at t: the latest version of every id, kept when that version is in force (a later version that
    ends the validity, as a revocation does, wins over the earlier open one). Returned as seqs (cache friendly)."""
    best = {}
    for r in state.kb().records:
        if r.kind in ("rule", "parameter", "table", "constraint") and (r.id not in best or r.seq > best[r.id].seq):
            best[r.id] = r
    return {r.seq for r in best.values() if state.in_force(r, t)}


def records_at(t):
    seqs = snapshot(state.signature(), t)
    return [r for r in state.kb().records if r.seq in seqs]


def _chart_end(dates):
    """The right end of a time chart: one year after today or after the latest date shown, whichever is later."""
    d = max([state.TODAY, *(x for x in dates if x)])
    return d.replace(year=d.year + 1) if (d.month, d.day) != (2, 29) else date(d.year + 1, 3, 1)


def _period(r):
    a = f"{state.fmt_date(r.valid_from)}" if r.valid_from else "-"
    return a + (f" to {state.fmt_date(r.valid_until)}" if r.valid_until else " · still in force")


def _value(r):
    if r.kind == "parameter":
        v = r.value
        if r.value_type == "rate":
            return state.pct(v)
        if r.value_type == "money":
            return state.money(v)
        return str(v)
    return None


def _title(r):
    """Display name of a parameter, table, or constraint: its English label, else its name or id."""
    text = r.label or getattr(r, "name", "") or r.id
    return text[0].upper() + text[1:]


def _plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


# ====================================================================================================================
# Content view
# ====================================================================================================================
MODALITY = {"mandatory": ("mandatory", "blue"), "default": ("default", "grey"), "optional": ("optional", "yellow")}


def card(r, show_topic=False):
    src = r.source[0] if r.source else None
    where = f"{state.short_doc(src.document)} · {src.provision}" if src else "-"
    if r.kind == "rule":
        title = state.fact_label(r.produces)
        mod = MODALITY.get(r.modality, (r.modality, "grey"))
        body = f"<b>Formula:</b> {state.readable(r.expression)}"
        if r.condition:
            body = f"<b>If:</b> {state.readable(r.condition)}<br>" + body
        badge = common.badge(mod[0], mod[1])
    elif r.kind == "parameter":
        title = _title(r)
        body = f"<b>Value:</b> {_value(r)}"
        badge = common.badge("number", "green")
    elif r.kind == "table":
        title = _title(r)
        body = f"<b>Table</b> with {_plural(len(r.rows or ()), 'row')}" + (" (from the annex)" if r.rows_ref else "")
        badge = common.badge("table", "yellow")
    else:
        title, body, badge = _title(r), "A constraint that is checked", common.badge("constraint", "red")
    topic = f" · {state.topic_of(r)}" if show_topic else ""
    quote = f"<div class='quote'>“{src.quote}”</div>" if src and src.quote else ""
    old = " old" if r.valid_until and r.valid_until < state.TODAY else ""
    common.html(f"<div class='rule{old}'>{badge}<b>{title}</b><span class='muted'>{topic}</span><br>{body}<br>"
                f"<span class='muted'>{common.term('valid', 'Valid')}: {_period(r)} · "
                f"{common.term('source', 'Source')}: {where}</span>{quote}</div>")
    return r


def tab_topics(recs, t):
    visible = [r for r in recs if not state.is_input_convention(r)]
    counts = {}
    for r in visible:
        counts[state.topic_of(r)] = counts.get(state.topic_of(r), 0) + 1
    topics = [x for x in state.TOPICS if counts.get(x[0])]
    known = {x[0] for x in topics}
    topics += [(t_, ":material/apartment:", "Rules from the installed company policies.", ())
               if t_ == state.POLICY_TOPIC else
               (t_, ":material/category:", "A part of the knowledge base outside the topics above; it is named after "
                "the value it produces.", ()) for t_ in sorted(counts) if t_ not in known]
    cols = st.columns(3)
    for i, (title, icon, expl, _) in enumerate(topics):
        with cols[i % 3].container(border=True):
            st.markdown(f"**{icon} {title}**  \n{expl}")
            st.caption(f"{counts[title]} rules, numbers, and tables")
    pick = st.pills("Open a topic", [x[0] for x in topics], default=topics[0][0], key="v_topic")
    if not pick:
        return
    items = sorted((r for r in visible if state.topic_of(r) == pick),
                   key=lambda r: (r.kind != "parameter", r.kind, r.id))
    st.markdown(f"#### {pick}")
    common.md(f"<span class='muted'>Labels: {common.badge('mandatory', 'blue')}"
              f"{common.term('mandatory', 'what is it?')} &nbsp; {common.badge('default', 'grey')}"
              f"{common.term('default', 'what is it?')} &nbsp; "
              f"{common.badge('number', 'green')}{common.term('parameter', 'what is it?')} &nbsp; "
              f"{common.badge('table', 'yellow')}{common.term('table', 'what is it?')}</span>")
    for r in items:
        card(r)
        if r.kind == "table" and r.rows:
            with st.expander("Show the table"):
                st.dataframe(_table_frame(r), hide_index=True, width="stretch")


def _table_frame(r):
    rows = []
    for row in r.rows:
        rows.append({k: (state.pct(v) if hasattr(v, "denominator") and v < 1 else
                         state.money(v) if hasattr(v, "denominator") else v) for k, v in row.items()})
    return pd.DataFrame(rows)


@st.cache_data
def flow(signature, t):
    """The calculation at date t as the knowledge base has it: the main steps (values the knowledge base marks as
    output, and values whose rules read a table), and which step feeds which, through the helper values in between.
    Nothing here is written for a particular regulation: a new step, or another way of computing, comes from the rules
    in force."""
    rules = [r for r in state.current() if r.kind == "rule" and r.layer == "regulation" and state.in_force(r, t)]
    tables = {r.name for r in state.kb().records if r.kind == "table"}
    reads, uses_table, real = {}, set(), set()
    for r in rules:
        facts_read, names = state._deps(r)
        reads.setdefault(r.produces, set()).update(facts_read)
        if not state.is_input_convention(r):
            real.add(r.produces)
            if names & tables:
                uses_table.add(r.produces)
    outputs = {n for n, f in state.facts().items() if f.output}
    main = (outputs & real) | uses_table
    inputs = set(reads) - real                 # values only read from the case data
    edges, owner = set(), {}
    for b in main:
        stack, seen = list(reads.get(b, ())), set()
        while stack:
            f = stack.pop()
            if f in seen or f == b:
                continue
            seen.add(f)
            if f in main:
                edges.add((f, b))
            elif f in inputs or f not in reads:
                edges.add(("_input", b))
            else:
                owner.setdefault(f, set()).add(b)        # a helper value on the way to b
                stack.extend(reads.get(f, ()))
    # values the knowledge base computes by fixed point (gross-up) feed back into what they are computed from: those
    # edges are the loop, drawn but not used to order the steps
    fixed = {r.produces for r in rules if r.fixed_point}
    loops = {(a, b) for a, b in edges if a in fixed}
    level = {}

    def depth(f, stack=()):
        if f not in level:
            ups = [a for a, b in edges if b == f and a != "_input" and a not in stack and (a, b) not in loops]
            level[f] = 1 + max((depth(a, stack + (f,)) for a in ups), default=0)
        return level[f]
    order = sorted(main, key=lambda f: (depth(f), state.fact_label(f)))
    helpers = {b: sorted(f for f, bs in owner.items() if b in bs) for b in main}
    return order, sorted(edges), helpers, loops


def flow_dot(order, edges, pick, loops):
    out = ['digraph F { rankdir=LR; bgcolor=transparent; nodesep=.18; ranksep=.45;',
           'node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10 color="#b4b3ae" '
           'fillcolor="#ffffff"];',
           'edge [color="#8a8984" arrowsize=.6];']
    for f in order:
        out.append(f'"{f}" [label="{state.fact_label(f)}"'
                   + (' penwidth=2.4 color="#2a78d6" fillcolor="#e8f1fc"' if f == pick else "") + "];")
    for a, b in edges:
        if a == "_input":
            continue
        back = (a, b) in loops                              # the fixed-point loop: drawn, but not for the layout
        out.append(f'"{a}" -> "{b}"' + (' [style=dashed color="#eb6834" constraint=false]' if back else "") + ";")
    return "\n".join(out) + "}"


def tab_flow(recs, t):
    order, edges, helpers, loops = flow(state.signature(), t)
    st.caption(f"The order of the calculation on {state.fmt_date(t)}, drawn from the rules in force in the knowledge "
               "base: the main steps are the values the knowledge base marks as results and the values that use a "
               "table. Change the date above to see how another year is computed.")
    default = calculator.ROOT if calculator.ROOT in order else order[-1]
    pick = st.selectbox("Step", order, index=order.index(default), key=f"v_flow_{t}",
                        format_func=lambda f: f"{state.fact_label(f)} ({f})")
    st.graphviz_chart(flow_dot(order, edges, pick, loops), width="stretch")
    st.caption("Steps without an incoming arrow are computed straight from the employee and company data. Dashed "
               "orange line = a calculation that goes round in a loop (for example gross-up: the tax allowance also "
               "raises gross income).")
    facts = {pick, *helpers.get(pick, [])}
    found = [r for r in recs if r.kind == "rule" and r.produces in facts and not state.is_input_convention(r)]
    st.markdown(f"**{_plural(len(found), 'rule')}** for the step *{state.fact_label(pick)}*"
                + (f", including the values in between: "
                   f"{', '.join(state.fact_label(f).lower() for f in helpers[pick])}" if helpers.get(pick) else "")
                + ":")
    for r in found:
        card(r)


def tab_numbers():
    ps = {}
    for r in state.kb().records:
        if r.kind == "parameter" and r.value_type in ("money", "rate"):
            ps.setdefault(r.name, []).append(r)
    labels = {n: _title(v[0]) for n, v in ps.items()}
    c1, c2 = st.columns([1, 2])
    with c1:
        name = st.radio("Number", sorted(ps, key=lambda n: labels[n]), format_func=labels.get, key="v_param")
    with c2:
        vs = sorted(ps[name], key=lambda r: r.valid_from)
        money = vs[0].value_type == "money"
        x, y = [], []
        end = _chart_end(r.valid_from for r in vs)
        for r in vs:
            x += [r.valid_from, r.valid_until or end]
            y += [float(r.value) * (1 if money else 100)] * 2
        fig = go.Figure(go.Scatter(x=x, y=y, mode="lines", line_shape="hv", line=dict(color="#2a78d6", width=3)))
        fig.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="Rp" if money else "%",
                          yaxis_tickformat=",.0f" if money else ".2f", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        for r in reversed(vs):
            card(r)
    st.divider()
    tables = {}
    for r in state.kb().records:
        if r.kind == "table" and r.rows:
            tables.setdefault(r.name, []).append(r)
    c1, c2 = st.columns([1, 2])
    name = c1.selectbox("Table", sorted(tables), format_func=lambda n: _title(tables[n][0]), key="v_table")
    ver = c2.selectbox("Version", sorted(tables[name], key=lambda r: r.valid_from, reverse=True), key="v_tver",
                       format_func=lambda r: f"{_period(r)} · "
                                             f"{state.short_doc(r.source[0].document) if r.source else ''}")
    st.dataframe(_table_frame(ver), hide_index=True, width="stretch", height=300)


def tab_history():
    st.caption("Every update comes from one document. The newest is at the top.")
    by_update = {}
    for r in state.kb().records:
        if r.kind != "fact":
            by_update.setdefault(r.update_id, []).append(r)
    words = dict(rule="rule", parameter="number", table="table", constraint="constraint", tombstone="removal")
    for u in reversed(state.kb().updates):
        recs = by_update.get(u.update_id, [])
        if not recs:
            continue
        kinds = {}
        for r in recs:
            kinds[r.kind] = kinds.get(r.kind, 0) + 1
        what = ", ".join(_plural(n, words.get(k, k)) for k, n in kinds.items())
        with st.expander(f"{state.fmt_date(u.recorded_on)} · {state.doc_title(u.document)} — {what}"):
            for r in recs[:25]:
                card(r, show_topic=True)


def tab_compare():
    c1, c2 = st.columns(2)
    a = c1.date_input("First date", date(2023, 12, 31), key="v_a")
    b = c2.date_input("Second date", date(2024, 1, 1), key="v_b")
    ra = {r.id: r for r in records_at(a)}
    rb = {r.id: r for r in records_at(b)}
    added = [rb[i] for i in rb if i not in ra and not state.is_input_convention(rb[i])]
    gone = [ra[i] for i in ra if i not in rb and not state.is_input_convention(ra[i])]
    changed = [(ra[i], rb[i]) for i in ra if i in rb and ra[i].seq != rb[i].seq]
    by_name_a = {r.name: r for r in ra.values() if r.kind == "parameter"}
    by_name_b = {r.name: r for r in rb.values() if r.kind == "parameter"}
    moved = [(by_name_a[n], by_name_b[n]) for n in by_name_a
             if n in by_name_b and by_name_a[n].value != by_name_b[n].value]
    m = st.columns(4)
    m[0].metric("Came into force", len(added))
    m[1].metric("Ended", len(gone))
    m[2].metric("Rules changed", len(changed))
    m[3].metric("Numbers changed", len(moved))
    for x, y in moved:
        common.html(f"<div class='rule'><b>{_title(x)}</b>: <span class='diff-old'>{_value(x)}</span>"
                    f" → <span class='diff-new'>{_value(y)}</span> <span class='muted'>"
                    f"({state.short_doc(y.source[0].document)})</span></div>")
    if added:
        st.markdown("**Came into force**")
        for r in added:
            if r.kind != "parameter" or r.name not in by_name_a:
                card(r, show_topic=True)
    if gone:
        st.markdown("**Ended**")
        for r in gone:
            if r.kind != "parameter" or r.name not in by_name_b:
                card(r, show_topic=True)


def tab_search(recs):
    q = st.text_input("Search", placeholder="e.g. job expense, benefits in kind, PMK 168, Pasal 17", key="v_q")
    if not q:
        st.caption("Searches names, formulas, provisions, quotes, and document names.")
        return
    ql = q.lower()
    hits = []
    for r in recs:
        hay = " ".join([r.id, r.label or "", getattr(r, "label_id", "") or "", getattr(r, "name", "") or "",
                        state.fact_label(getattr(r, "produces", "") or "") if getattr(r, "produces", None) else "",
                        state.expr_text(getattr(r, "expression", "") or "")]
                       + [f"{s.document} {state.doc_title(s.document)} {s.provision} {s.quote}" for s in r.source])
        if ql in hay.lower():
            hits.append(r)
    st.caption(f"{_plural(len(hits), 'result')}")
    for r in hits[:40]:
        card(r, show_topic=True)


def tab_policies():
    common.md(f"{common.term('company policy', 'Company policies')} installed in the knowledge base. The calculator "
              "uses them when one is chosen.")
    pols = state.installed_policies()
    if not pols:
        st.caption("No company policy is installed yet.")
        return
    pick = st.selectbox("Policy", list(pols), key="v_pol", format_func=lambda i: f"{i} · {pols[i]}")
    for r in state.kb().view(state.TODAY).rules.values():
        if r.layer == "company" and r.policy == pick:
            src = r.source[0] if r.source else None
            common.html(f"<div class='rule company'>{common.badge('company', 'orange')}"
                        f"<b>{state.fact_label(r.produces)}</b><br><b>Formula:</b> {state.readable(r.expression)}<br>"
                        f"<span class='muted'>Valid: {_period(r)}{' · ' + src.provision if src else ''}</span>"
                        + (f"<div class='quote'>“{src.quote}”</div>" if src else "") + "</div>")


def tab_inputs(t):
    common.md("The data the calculator asks for, taken straight from the rules valid in that year. When a new "
              "regulation or company policy reads new data, that data appears here and becomes a field in the "
              "calculator without changing the program.")
    pols = state.installed_policies()
    policy = st.selectbox("With company policy", [None] + list(pols), key="v_in_pol",
                          format_func=lambda p: "None" if p is None else f"{p} · {pols[p]}")
    found = calculator.discover(t.year, policy)
    group = {"income": "Monthly income", "benefit": "Monthly benefits in kind", "hr": "Monthly HR data",
             "zakat": "Monthly income", "employee": "Employee data", "employer": "Company data",
             "case": "Employee data"}
    rows = [{"Data": calculator.label(k), "Group": group[k.split(".")[0]],
             "From": "company policy" if e["layer"] == "company" else "regulation",
             "Months": "all" if len(e["months"]) == 12
             else f"{state.MON[e['months'][0] - 1]}–{state.MON[e['months'][-1] - 1]}",
             "Read by": ", ".join(e["rules"][:3]) + (" ..." if len(e["rules"]) > 3 else ""),
             "Definition": (calculator.definition(k) or {}).get("origin", "none yet")} for k, e in found.items()]
    st.dataframe(pd.DataFrame(rows).sort_values(["Group", "Data"]), hide_index=True, width="stretch")
    st.caption("Data definitions (the label and explanation of each input) come with the starting knowledge base and "
               "with the approved update that first reads the data.")


# ====================================================================================================================
# Page entry point
# ====================================================================================================================
CONTENTS = "Contents"
TECHNICAL = "How the knowledge base works (technical)"


def show():
    st.session_state.page_ctx = "kb"
    st.title("Knowledge base viewer")
    mode = st.segmented_control("View", [CONTENTS, TECHNICAL], default=CONTENTS, key="v_mode",
                                label_visibility="collapsed") or CONTENTS
    technical = mode != CONTENTS
    if technical:
        common.md(f"How the system stores and uses knowledge: an {common.term('RDF')} "
                  f"{common.term('knowledge graph')} that is {common.term('bitemporal')} and has "
                  f"{common.term('two layers')}, an {common.term('ontology')}, checks, versions kept as "
                  f"{common.term('named graph', 'named graphs')}, and the {common.term('trace')} of the engine. "
                  "Everything comes from the knowledge base in use now.")
    else:
        common.md(f"What the system knows about PPh 21: {common.term('rule', 'rules')}, "
                  f"{common.term('parameter', 'numbers')}, and {common.term('table', 'tables')}, each with its "
                  f"{common.term('valid', 'validity dates')} and the {common.term('source')} provision.")
    c1, c2 = st.columns([1, 3])
    t = c1.date_input("Show what is valid on", state.TODAY, key="v_t", help=common.tip("valid"))
    st.session_state.g_date = t
    recs = records_at(t)
    visible = [r for r in recs if not state.is_input_convention(r)]
    docs = {s.document for r in visible for s in r.source}
    with c2:
        m = st.columns(4)
        m[0].metric("Rules", sum(r.kind == "rule" for r in visible), help=common.tip("rule"))
        m[1].metric("Numbers", sum(r.kind == "parameter" for r in visible), help=common.tip("parameter"))
        m[2].metric("Tables", sum(r.kind == "table" for r in visible), help=common.tip("table"))
        m[3].metric("Source documents", len(docs), help=common.tip("source"))
    if technical:
        show_technical(t, recs)
        return
    tabs = st.tabs(["Topic map", "Calculation flow", "Numbers over time", "Change history", "Compare two dates",
                    "Search", "Data needed", "Company policies"])
    with tabs[0]:
        tab_topics(recs, t)
    with tabs[1]:
        tab_flow(recs, t)
    with tabs[2]:
        tab_numbers()
    with tabs[3]:
        tab_history()
    with tabs[4]:
        tab_compare()
    with tabs[5]:
        tab_search(recs)
    with tabs[6]:
        tab_inputs(t)
    with tabs[7]:
        tab_policies()


# ====================================================================================================================
# Technical view
# ====================================================================================================================
KIND = {"rule": "rule", "parameter": "number", "table": "table", "constraint": "constraint", "fact": "fact",
        "tombstone": "removal"}
RANK = {4: "4 · mandatory (regulation)", 3: "3 · company policy", 2: "2 · optional rule adopted by the company",
        1: "1 · default"}
WHY = {"lex superior": "lower rank", "lex specialis": "beaten by a more specific rule",
       "lex posterior": "beaten by a newer rule", "redundant": "same value, not used"}
LAYER = {"regulation": "regulation", "company": "company", "case": "case data"}
LOST = "Rules that lost"
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
    "Rules that read the job expense (downstream)": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT DISTINCT ?id ?produces WHERE {
  GRAPH ?g { ?r pph:elementId ?id ; pph:reads ?f ; pph:produces ?produces .
             FILTER(STRENDS(STR(?f), "/job_expense")) }
} ORDER BY ?id""",
    "Elements recorded after they came into force (retroactive)": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
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
MANAGE = "Knowledge base management"
PARTS = [
    ("Acquisition", "Relevance, several drafts from the language model, the six automatic checks, then the drafts "
     "agree or the AI is not sure", "pph21kbs/pipeline.py, documents.py, draft.py",
     f"{MANAGE}: new documents, review"),
    (f"{GATES['G1']} (G1)", "Schema, the update applies, and the graph matches the SHACL shapes",
     "spec/shapes.ttl, pph21kbs/gates.py", "Ontology and checks tab"),
    (f"{GATES['G6']} (G6)", "Every input a rule reads exists in the payroll data", "pph21kbs/gates.py",
     f"{MANAGE}: review"),
    (f"{GATES['G2']} (G2)", "Quotes and numbers really appear in the document", "pph21kbs/gates.py",
     f"{MANAGE}: review"),
    (f"{GATES['G3']} (G3)", "Consistency checker: cycles, dead rules, rules that always lose, conflicts between "
     "layers", "pph21kbs/consistency.py", "Ontology and checks tab"),
    (f"{GATES['G4']} (G4)", "Results on generated test cases before the start date stay the same",
     "pph21kbs/gates.py", f"{MANAGE}: review, examples before and after"),
    (f"{GATES['G5']} (G5)", "Every element changes a result on the generated test cases", "pph21kbs/gates.py",
     f"{MANAGE}: review"),
    ("Knowledge base", "Bitemporal records in two layers; one update = one named graph", "pph21kbs/kb.py, graph.py",
     "Versions and named graphs tab"),
    ("Ontology", "Classes and relations; reuses ELI, OWL-Time, PROV-O", "spec/ontology.ttl",
     "Ontology and checks tab"),
    ("Engine", "Chooses a rule (rank, specificity, time), computes the gross-up fixed point, keeps the trace",
     "pph21kbs/engine.py", "Calculation trace tab, calculator"),
    ("Impact analysis", "The values that change and the company rules that read them, computed in Python; the SPARQL "
     "queries in spec/queries give the same result", "pph21kbs/pipeline.py (detect), spec/queries/",
     f"{MANAGE}: review, affected policies"),
]


@st.cache_resource(show_spinner="Building the RDF graph of the knowledge base ...")
def dataset(signature):
    return graph.to_dataset(state.kb())


@st.cache_data(show_spinner="Running the consistency checker ...")
def consistency_findings(signature, omega, policies):
    rep = consistency.check(state.kb(), omega, policies=policies)
    return [{"Level": f.severity, "Kind": f.kind, "Elements": ", ".join(f.ids), "Fact": f.fact, "Detail": f.detail}
            for f in rep.findings]


@st.cache_data(show_spinner="Checking the SHACL shapes ...")
def shacl_violations(signature):
    return [{"Element": str(e), "Message": m} for e, m in graph.validate(state.kb())]


@st.cache_data
def ontology(signature):
    return ontology_dot()


def stats(view, recs):
    """Counts for the architecture picture; recs = what is in force at the chosen date (as the numbers at the top)."""
    shown = [r for r in recs if not state.is_input_convention(r)]
    return {"reg_rules": sum(r.kind == "rule" and r.layer == "regulation" for r in shown),
            "com_rules": sum(r.kind == "rule" and r.layer == "company" for r in shown),
            "params": sum(r.kind == "parameter" for r in shown), "tables": sum(r.kind == "table" for r in shown),
            "facts": len(view.facts), "updates": len(state.kb().updates)}


def _fact_pick(view, key, default="pph21_due", label="Value shown"):
    facts = sorted({r.produces for r in view.rules.values()}, key=state.fact_label)
    return st.selectbox(label, facts, index=facts.index(default) if default in facts else 0, key=key,
                        format_func=lambda f: f"{state.fact_label(f)} ({f})")


def tab_architecture(view, t, recs):
    st.caption(f"From a document to a calculation. Numbers in the picture: the knowledge base in use now, what is in "
               f"force on {state.fmt_date(t)}.")
    st.graphviz_chart(architecture_dot(stats(view, recs)), width="stretch")
    st.dataframe(pd.DataFrame(PARTS, columns=["Part", "What it does", "Code", "Where to see it in the app"]),
                 hide_index=True, width="stretch")


def tab_graph(view, t):
    common.md(f"The part of the {common.term('knowledge graph')} around one value: the rules that produce it, the "
              "other values they read, their numbers and tables, and (when chosen) the source provisions.")
    c1, c2, c3, c4 = st.columns([1.8, 1, 1.1, 1.3])
    with c1:
        focus = _fact_pick(view, "kt_focus")
    depth = c2.slider("Depth", 1, 5, 2, key="kt_depth")
    upstream, downstream, both = "towards the sources (upstream)", "towards the users (downstream)", "both"
    way = c3.radio("Direction", (upstream, downstream, both), key="kt_way")
    with c4:
        only = st.toggle("Only what is in force", True, key="kt_only", help=common.tip("valid"))
        prov = st.toggle("Show source provisions", False, key="kt_prov", help=common.tip("source"))
        layers = st.multiselect("Layers", ["regulation", "company"], default=["regulation", "company"],
                                key="kt_layers", format_func=LAYER.get)
    dot, n = dependency_dot(view, focus, t, depth, upstream=way != downstream, downstream=way != upstream,
                            layers=tuple(layers), only_in_force=only, provenance=prov)
    st.graphviz_chart(dot, width="stretch")
    st.caption(f"{_plural(n, 'rule')}, in force on {state.fmt_date(t)}. Ellipse = value (fact), blue box = regulation "
               "rule, orange box = company rule, yellow cylinder = number or table, folder = document, note = "
               "provision. Solid line = produces, dashed = reads, dotted = uses a number or table, red = overrides.")
    st.markdown(f"**All rules for *{state.fact_label(focus)}* and how the engine chooses**")
    common.md(f"<span class='muted'>{common.term('conflict resolution', 'Order of choice')}: the highest rank wins; "
              "if equal, the more specific rule; if still equal, the one that came into force later.</span>")
    rows = [{"Rule": r.id, "Layer": LAYER.get(r.layer, r.layer), "Rank": RANK.get(r.rank, r.rank),
             "Valid": f"{state.fmt_date(r.valid_from)} – "
                      f"{state.fmt_date(r.valid_until) if r.valid_until else 'now'}",
             "Status on the date": status(r, t), "Overrides": ", ".join(r.overrides) or "-",
             "Source": f"{state.short_doc(r.source[0].document)} {r.source[0].provision}" if r.source else "-"}
            for r in sorted(view.rules_by_fact.get(focus, []), key=lambda r: (-r.rank, r.valid_from or date.min))]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def tab_rdf(view):
    kb = state.kb()
    common.md(f"Every element of the knowledge base is stored as a set of {common.term('RDF')} triples in the "
              f"{common.term('named graph')} of its update. This is the form that is stored, queried with SPARQL, "
              "and checked with SHACL.")
    ids = sorted({r.id for r in kb.records if r.kind in ("rule", "parameter", "table", "constraint")
                  and not state.is_input_convention(r)})
    label = {r.id: (state.fact_label(r.produces) if r.kind == "rule" else _title(r)) for r in kb.records
             if r.id in ids}
    first = next((r.id for r in view.rules_by_fact.get("job_expense", []) if r.id in ids), ids[0])
    c1, c2 = st.columns([2, 1.4])
    rid = c1.selectbox("Element", ids, index=ids.index(first),
                       key="kt_rid", format_func=lambda i: f"{i} · {label.get(i, '')}")
    versions = [r for r in kb.records if r.id == rid]
    i = c2.selectbox("Record (version of the element)", range(len(versions)), index=len(versions) - 1,
                     key=f"kt_rver_{rid}",
                     format_func=lambda k: f"#{versions[k].seq} · recorded {state.fmt_date(versions[k].recorded_on)}"
                                           f" · {versions[k].update_id}")
    rec, prev = versions[i], (versions[i - 1] if i else None)
    triples = record_graph(rec, prev)
    m = st.columns(4)
    m[0].metric("Triples", len(triples))
    m[1].metric("Named graph", f"…/update/{rec.update_id}")
    m[2].metric("Version of this element", f"{i + 1} of {len(versions)}")
    m[3].metric("Revision of", f"#{prev.seq}" if prev else "-")
    view_graph, view_table = st.tabs(["Graph", "Table of triples"])
    with view_graph:
        st.graphviz_chart(record_rdf_dot(triples), width="stretch")
        st.caption("Blue = resource (IRI), yellow = value (literal), grey dot = blank node. A formula is stored as "
                   "text, with a pph:reads link to every value it reads.")
    with view_table:
        rows = [{"Subject": short(s), "Predicate": short(p), "Object": short(o)} for s, p, o in triples]
        st.dataframe(pd.DataFrame(rows).sort_values(["Subject", "Predicate"]), hide_index=True, width="stretch",
                     height=380)
    with st.expander("Turtle (RDF as text)"):
        triples.bind("pph", graph.PPH)
        triples.bind("kb", graph.KB)
        triples.bind("eli", graph.ELI)
        st.code(triples.serialize(format="turtle"), language="turtle")


def tab_bitemporal(t):
    kb = state.kb()
    common.md(f"Every element has two times ({common.term('bitemporal')}): the "
              f"{common.term('valid', 'date it is valid from')} under the regulation and the "
              f"{common.term('recorded', 'date it was recorded')} in the knowledge base. A point above the diagonal "
              "line = recorded after it came into force (retroactive); below = announced in advance.")
    recs = [r for r in kb.records if r.kind in ("rule", "parameter", "table") and r.valid_from and r.recorded_on
            and not state.is_input_convention(r)]
    fig = go.Figure()
    for layer, color in (("regulation", REG), ("company", COMPANY)):
        pts = [r for r in recs if getattr(r, "layer", "regulation") == layer]
        if pts:
            fig.add_trace(go.Scatter(x=[r.valid_from for r in pts], y=[r.recorded_on for r in pts], mode="markers",
                                     name=LAYER[layer], marker=dict(color=color, size=7, opacity=.75),
                                     hovertext=[f"{r.id}<br>valid from {r.valid_from}<br>recorded {r.recorded_on}"
                                                for r in pts],
                                     hoverinfo="text"))
    lo, hi = date(2008, 1, 1), _chart_end(r.valid_from for r in recs)
    fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", line=dict(color="#b4b3ae", dash="dot"),
                             name="recorded = valid from", hoverinfo="skip"))
    fig.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), xaxis_title="Came into force",
                      yaxis_title="Recorded in the knowledge base", plot_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h"))
    c1, c2 = st.columns([2, 1])
    c1.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    retro = [r for r in recs if r.recorded_on > r.valid_from]
    with c2:
        st.metric("Dated elements", len(recs))
        st.metric("Recorded after coming into force", len(retro))
        early = [r for r in recs if r.recorded_on < r.valid_from]
        lines = [f"Latest recorded {'after' if r in retro else 'before'} coming into force: "
                 f"{state.short_doc(r.source[0].document) if r.source else r.update_id}, recorded "
                 f"{state.fmt_date(r.recorded_on)}, valid from {state.fmt_date(r.valid_from)}."
                 for r in (max(group, key=lambda r: (r.recorded_on, r.seq)) for group in (retro, early) if group)]
        st.caption(" ".join(lines) + " The calculator can compute 'with the knowledge as of a date' to repeat an old "
                   "calculation exactly as it was then.")
    st.markdown("**Timeline per value**")
    view = kb.view(state.TODAY)
    facts = sorted({r.produces for r in view.rules.values()}, key=state.fact_label)
    focus = st.multiselect("Values", facts, default=[f for f in ("ptkp_amount", "pph21_running", "pph21_dtp",
                                                                 "jp_wage", "ter_rate") if f in facts],
                           key="kt_tl", format_func=state.fact_label)
    rows = sorted([r for r in kb.records if r.kind == "rule" and r.produces in focus and r.valid_from],
                  key=lambda r: (r.produces, r.valid_from, r.seq))
    if not rows:
        return
    fig = go.Figure()
    end = _chart_end(r.valid_from for r in rows)
    for i, r in enumerate(rows):
        color = REG if r.layer == "regulation" else COMPANY
        fig.add_trace(go.Scatter(x=[r.valid_from, r.valid_until or end], y=[i, i], mode="lines",
                                 line=dict(color=color, width=9), hovertext=f"{r.id}<br>{state.fact_label(r.produces)}",
                                 hoverinfo="text", showlegend=False))
        fig.add_trace(go.Scatter(x=[r.recorded_on], y=[i], mode="markers", showlegend=False, hoverinfo="text",
                                 marker=dict(symbol="diamond", size=9, color="#3b3a37"),
                                 hovertext=f"recorded {r.recorded_on}"))
    fig.add_vline(x=t, line_color=REG, line_dash="dash")
    fig.update_layout(height=max(300, 24 * len(rows)), margin=dict(l=10, r=10, t=10, b=10),
                      yaxis=dict(tickvals=list(range(len(rows))), ticktext=[f"{r.id} #{r.seq}" for r in rows],
                                 autorange="reversed"),
                      xaxis=dict(range=[date(2012, 1, 1), end]), plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.caption("Bar = validity period, diamond = date recorded, dashed blue line = the date chosen above.")


def tab_versions():
    kb = state.kb()
    base_n = len(state.base().updates)
    common.md(f"The knowledge base is never overwritten. Every {common.term('update')} is stored as one "
              f"{common.term('named graph')}; {common.term('version')} n = the union of named graphs 1..n. Orange box "
              "= an update approved in the app.")
    st.graphviz_chart(chain_dot(kb, base_n), width="stretch")
    per = {}
    for r in kb.records:
        per.setdefault(r.update_id, {}).setdefault(r.kind, 0)
        per[r.update_id][r.kind] += 1
    rows = []
    for i, u in enumerate(kb.updates):
        c = per.get(u.update_id, {})
        rows.append({"Version": i + 1, "Update": u.update_id, "Document": state.short_doc(u.document),
                     "Recorded": u.recorded_on, "Records": sum(c.values()),
                     "Contents": ", ".join(_plural(n, KIND.get(k, k)) for k, n in c.items()),
                     "Named graph": f"kb:update/{u.update_id}",
                     "Origin": "app" if i >= base_n else "starting knowledge base"})
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
        st.dataframe(pd.DataFrame([{"Change": "only in the second version" if r in new else "only in the first version",
                                    "Record": f"#{r.seq}", "Element": r.id, "Kind": KIND.get(r.kind, r.kind),
                                    "Update": r.update_id,
                                    "Valid": f"{state.fmt_date(r.valid_from)} – "
                                             f"{state.fmt_date(r.valid_until) if r.valid_until else 'now'}"
                                    if r.valid_from else "-"} for r in new + gone]), hide_index=True, width="stretch")


def tab_trace():
    common.md(f"The {common.term('trace')} of the engine for one calculation: every value keeps the rule used, the "
              "values it read, the rules that lost, and the provision. The scenarios come from the calculator.")
    scs = calculator.scenarios()
    c1, c2, c3, c4 = st.columns([1.8, 1, 1.6, .8])
    title = c1.selectbox("Scenario", list(scs), key="kt_sc")
    case = calculator.scenario_case(scs[title])
    res, err = state.compute(case, state.TODAY)
    if err:
        st.error(err)
        return
    months = sorted(res.periods)
    choices = months + ([0] if res.year else [])
    month = c2.selectbox("Month", choices, index=choices.index(0) if 0 in choices else len(choices) - 1, key="kt_m",
                         format_func=lambda m: "Whole year" if m == 0 else state.MONTHS[m - 1])
    facts = sorted({f for (f, m) in res.trace if m == month}, key=state.fact_label)
    default = "annual_pph21" if month == 0 else "pph21_due"
    fact = c3.selectbox("Value", facts, index=facts.index(default) if default in facts else 0, key=f"kt_f{month}",
                        format_func=lambda f: f"{state.fact_label(f)} ({f})")
    depth = c4.slider("Depth", 1, 6, 3, key="kt_d")
    st.graphviz_chart(derivation_dot(res, month, fact, depth=depth), width="stretch")
    st.caption("Blue = regulation rule, orange = company rule, yellow = case data or a recorded value. Zero values "
               "are not drawn.")
    rows = []
    for (f, m), e in res.trace.items():
        src = e["source"][0] if e.get("source") else {}
        if m != month or src.get("document") == "INPUT-CONVENTION":      # data read straight from the case
            continue
        rows.append({"Value": state.fact_label(f), "Result": state.fmt(f, e["value"]), "Rule": e["rule"],
                     "Layer": LAYER.get(e["layer"], e["layer"]),
                     LOST: "; ".join(f"{i} ({WHY.get(w, w)})" for i, w in e.get("losers") or []) or "-",
                     "Source": f"{state.short_doc(src.get('document', ''))} {src.get('provision', '')}".strip() or "-"})
    lost = sum(r[LOST] != "-" for r in rows)
    st.markdown(f"**All values of this month** · {_plural(len(rows), 'value')}, {lost} of them chosen among several "
                "rules")
    only = st.toggle("Only values with rules that lost", False, key="kt_lost")
    st.dataframe(pd.DataFrame([r for r in rows if not only or r[LOST] != "-"]), hide_index=True,
                 width="stretch", height=320)


def tab_checks(t):
    sig = state.signature()
    dot, n_classes, n_props = ontology(sig)
    common.md(f"The {common.term('ontology')} of the system: {n_classes} classes and {n_props} relations. Parent "
              "classes come from the standards ELI (legislation), PROV-O (provenance), OWL-Time (time), and SKOS.")
    st.graphviz_chart(dot, width="content")
    st.caption("Triangle arrow = 'is a kind of'; dashed blue line = a relation between classes.")
    st.markdown(f"**SHACL shapes (part of the check '{GATES['G1'].lower()}', G1)**")
    st.dataframe(pd.DataFrame(shapes()), hide_index=True, width="stretch")
    st.markdown("**Checks of the knowledge base now**")
    pols = tuple(state.installed_policies())
    rows = consistency_findings(sig, t, pols)
    errors = [r for r in rows if r["Level"] == "error"]
    m = st.columns(3)
    m[0].metric("Consistency errors", len(errors), help=common.tip("consistency checker"))
    m[1].metric("Warnings", len(rows) - len(errors))
    m[2].metric("Company policies included", len(pols))
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=240)
    if st.button("Run the SHACL validation", icon=":material/rule:", key="kt_shacl", help=common.tip("SHACL")):
        v = shacl_violations(sig)
        if v:
            st.error(f"{_plural(len(v), 'violation')}")
            st.dataframe(pd.DataFrame(v), hide_index=True, width="stretch")
        else:
            st.success("All SHACL shapes hold.")


@st.cache_data
def shapes():
    """One row per SHACL node shape: target classes, checked properties, SPARQL rules, and an example message."""
    gr = graph.shapes()
    out = []
    for s in gr.subjects(RDF.type, SH.NodeShape):
        targets = ", ".join(sorted(short(c) for c in gr.objects(s, SH.targetClass)))
        paths = sorted(short(p) for prop in gr.objects(s, SH.property) for p in gr.objects(prop, SH.path))
        rules = len(list(gr.objects(s, SH.sparql)))
        msgs = [str(m) for x in list(gr.objects(s, SH.sparql)) + list(gr.objects(s, SH.property))
                for m in gr.objects(x, SH.message)]
        out.append({"Shape": short(s), "For class": targets, "Properties checked": ", ".join(paths[:6])
                    + (" …" if len(paths) > 6 else ""), "SPARQL rules": rules,
                    "Example message": msgs[0] if msgs else ""})
    return sorted(out, key=lambda r: r["Shape"])


def tab_sparql():
    common.md(f"{common.term('SPARQL')} queries straight on the graph of the knowledge base (one "
              f"{common.term('named graph')} per update, plus kb:meta).")
    preset = st.selectbox("Example query", list(PRESETS), key="kt_preset")
    q = st.text_area("Query", PRESETS[preset], height=190, key=f"kt_q_{preset}")
    if st.button("Run", icon=":material/play_arrow:", key="kt_run"):
        try:
            res = dataset(state.signature()).query(q)
            rows = [{str(v): (short(row[i]) if row[i] is not None else "") for i, v in enumerate(res.vars)}
                    for row in res]
            st.caption(f"{_plural(len(rows), 'row')}")
            st.dataframe(pd.DataFrame(rows[:1000]), hide_index=True, width="stretch")
        except Exception as e:  # noqa: BLE001 - shown to the user
            st.error(f"{type(e).__name__}: {e}")
    st.markdown("**Export**")
    st.caption("Open in Protégé (ontology) or GraphDB / Apache Jena Fuseki (graph and SPARQL).")
    c = st.columns(3)
    if c[0].button("Prepare the knowledge base as TriG", icon=":material/data_object:", key="kt_trig"):
        buf = io.BytesIO(dataset(state.signature()).serialize(format="trig").encode("utf-8"))
        st.download_button("Download kb.trig", buf.getvalue(), "kb.trig", "application/trig",
                           icon=":material/download:", key="kt_dl_trig")
    for col, name in zip(c[1:], ("ontology.ttl", "shapes.ttl")):
        col.download_button(f"Download {name}", (config.SPEC / name).read_bytes(), name, "text/turtle",
                            key=f"kt_dl_{name}", icon=":material/download:")
    st.caption(f"Knowledge base fingerprint: `{state.kb().fingerprint()[:16]}` · "
               f"{_plural(len(state.kb().records), 'record')} · {_plural(len(state.kb().updates), 'update')}")


def show_technical(t, recs):
    """The technical view: the knowledge base system itself, with the knowledge base in use."""
    view = state.kb().view(state.TODAY)
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


# ====================================================================================================================
# Diagrams (Graphviz DOT)
# ====================================================================================================================
REG, REG_FILL = "#2a78d6", "#e8f1fc"
COMPANY, COMPANY_FILL = "#eb6834", "#fdeee7"
PARAM, PARAM_FILL = "#b98900", "#fff7e0"
DOC_FILL = "#eeeeec"
IN_FORCE = "in force"


def q(text):
    """DOT string: double quotes become single quotes and a newline becomes a space; a written \\n (a backslash
    and n) stays in the text, and DOT draws it as a line break."""
    return '"' + str(text).replace('"', "'").replace("\n", " ") + '"'


def status(r, t):
    if r.valid_from and r.valid_from > t:
        return "not yet in force"
    if r.valid_until and r.valid_until < t:
        return "no longer in force"
    return IN_FORCE


def architecture_dot(stats):
    """Three rows: acquisition (top), the knowledge base (middle), what uses it (bottom)."""
    s = stats
    return f"""digraph A {{ rankdir=TB; bgcolor=transparent; nodesep=.35; ranksep=.45; newrank=true;
node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10 color="#b4b3ae" fillcolor="#ffffff"];
edge [color="#8a8984" arrowsize=.7 fontname="Helvetica" fontsize=9 fontcolor="#6b6a66"];
doc [label="New document\\nregulation · PKB · company policy\\nPDF · TXT · JSON" shape=note fillcolor="{DOC_FILL}"];
subgraph cluster_acq {{ label="1  Knowledge acquisition with a language model"; fontname="Helvetica-Bold"; fontsize=10;
  color="{REG}"; fontcolor="{REG}"; style="rounded,dashed";
  rel [label="Relevance\\n+ choice of document parts" fillcolor="{REG_FILL}"];
  cand [label="Several drafts of the update\\n(language model, structured output)" fillcolor="{REG_FILL}"];
  gates [label="Six automatic checks (G1–G6)\\nformat · inputs exist · quotes · no conflict\\n\
past results unchanged · every part has an effect"];
  cons [label="The drafts agree\\nor the AI is not sure"]; }}
rev [label="Human review\\napprove · edit · reject" fillcolor="{COMPANY_FILL}" color="{COMPANY}" penwidth=1.6];
subgraph cluster_kb {{ label="2  Knowledge base: RDF knowledge graph, bitemporal, two layers";
  fontname="Helvetica-Bold"; fontsize=10; color="{PARAM}"; fontcolor="#7a5b00"; style="rounded";
  reg [label="Regulation layer\\n{s['reg_rules']} rules" fillcolor="{REG_FILL}" color="{REG}"];
  com [label="Company layer\\n{s['com_rules']} rules" fillcolor="{COMPANY_FILL}" color="{COMPANY}"];
  par [label="{s['params']} numbers · {s['tables']} tables\\n{s['facts']} kinds of value" shape=cylinder
       fillcolor="{PARAM_FILL}" color="{PARAM}"];
  ver [label="{s['updates']} updates = {s['updates']} named graphs\\nvalid date + recorded date\\n\
source: provision + quote" shape=folder fillcolor="#f7f7f5"];
  onto [label="Ontology (ELI · OWL-Time · PROV-O)\\n+ SHACL shapes" shape=component fillcolor="#f7f7f5"]; }}
subgraph cluster_use {{ label="3  Use"; fontname="Helvetica-Bold"; fontsize=10; color="#8a8984"; style="rounded,dashed";
  eng [label="Inference engine\\nrule choice: rank > specific > newer\\nfixed point · trace to the provision"];
  calc [label="PPh 21 calculator" shape=component penwidth=2];
  imp [label="Impact analysis across layers\\n(Python, same result as the SPARQL queries)" shape=component];
  viewer [label="Knowledge base viewer" shape=component]; }}
{{ rank=same; doc; rel; cand; gates; cons; }}
{{ rank=same; reg; com; par; ver; onto; }}
{{ rank=same; eng; calc; imp; viewer; }}
doc -> rel -> cand -> gates -> cons;
gates -> cand [label="1 repair round" style=dashed constraint=false];
cons -> rev; rev -> ver [label="approved update"];
ver -> imp [label="update"]; imp -> rev [style=dashed label="impact report" constraint=false];
reg -> eng; com -> eng; par -> eng; eng -> calc; onto -> viewer [style=dotted];
reg -> com -> par -> ver -> onto [style=invis]; eng -> calc -> imp -> viewer [style=invis]; }}"""


def dependency_dot(view, focus, t, depth=2, upstream=True, downstream=False, layers=("regulation", "company"),
                   only_in_force=True, provenance=False, max_rules=40):
    """The knowledge graph around one fact (rules, facts they read, parameters, tables), optionally with provenance
    (document -> provision -> rule) and the status of every rule at date t. Returns (DOT text, number of rules)."""
    rules = [r for r in view.rules.values() if r.layer in layers and not state.is_input_convention(r)]
    if only_in_force:
        rules = [r for r in rules if status(r, t) == IN_FORCE]
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
               {g for r in chosen.values() for e in (r.expression, r.condition) if e is not None
                for g in e.dependencies()}
    for f in sorted(involved):
        fd = view.facts.get(f)
        pen = "penwidth=2.4" if f == focus else ("penwidth=1.5" if fd is not None and fd.output else "")
        out.append(f'{q("f:" + f)} [shape=ellipse style=filled fillcolor="#f7f7f5" color="#6b6a66" {pen} '
                   f'label={q(state.fact_label(f) + chr(92) + "n" + f)}];')
    params, docs = set(), {}
    for r in chosen.values():
        line, fill = (REG, REG_FILL) if r.layer == "regulation" else (COMPANY, COMPANY_FILL)
        stt = status(r, t)
        style = "rounded,filled" + ("" if stt == IN_FORCE else ",dashed")
        lab = f"{r.id}\\n{r.modality} · {r.valid_from:%Y-%m}" + (f"..{r.valid_until:%Y-%m}" if r.valid_until else "")
        if stt != IN_FORCE:
            lab += f"\\n({stt})"
        out.append(f'{q(r.id)} [shape=box style="{style}" color="{line}" '
                   f'fillcolor="{fill if stt == IN_FORCE else "#f4f4f2"}" label={q(lab)}];')
        out.append(f'{q(r.id)} -> {q("f:" + r.produces)} [color="#3b3a37" label="produces"];')
        for e in (r.expression, r.condition):
            if e is None:
                continue
            for g in e.dependencies():
                out.append(f'{q("f:" + g)} -> {q(r.id)} [style=dashed];')
            for name in set(state.QUOTED.findall(e.text)) & state.names():
                params.add(name)
                out.append(f'{q("p:" + name)} -> {q(r.id)} [style=dotted color="{PARAM}"];')
        for o in r.overrides:
            if o in chosen:
                out.append(f'{q(r.id)} -> {q(o)} [color="#c62828" fontcolor="#c62828" label="overrides"];')
        if provenance and r.source:
            s = r.source[0]
            docs.setdefault(s.document, set()).add(s.provision)
            art = f"a:{s.document}:{s.provision}"
            out.append(f'{q(art)} [shape=note style=filled fillcolor="#ffffff" color="#b4b3ae" fontsize=9 '
                       f'label={q(s.provision)}];')
            out.append(f'{q(art)} -> {q(r.id)} [style=dotted color="#b4b3ae" label="hasSource"];')
    for name in sorted(params):
        out.append(f'{q("p:" + name)} [shape=cylinder style=filled fillcolor="{PARAM_FILL}" color="{PARAM}" '
                   f'label={q(name)}];')
    for doc, arts in docs.items():
        out.append(f'{q("d:" + doc)} [shape=folder style=filled fillcolor="{DOC_FILL}" color="#8a8984" '
                   f'label={q(state.short_doc(doc))}];')
        for a in arts:
            out.append(f'{q("d:" + doc)} -> {q(f"a:{doc}:{a}")} [arrowhead=none color="#b4b3ae"];')
    out.append("}")
    return "\n".join(out), len(chosen)


SHORT = {"https://w3id.org/pph21kbs/ontology#": "pph:", "https://w3id.org/pph21kbs/kb/": "kb:",
         "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf:", "http://www.w3.org/2000/01/rdf-schema#": "rdfs:",
         "http://www.w3.org/ns/prov#": "prov:", "http://data.europa.eu/eli/ontology#": "eli:",
         "http://www.w3.org/2001/XMLSchema#": "xsd:", "http://purl.org/dc/terms/": "dcterms:",
         "http://www.w3.org/2004/02/skos/core#": "skos:", "http://www.w3.org/2006/time#": "time:",
         "http://www.w3.org/2002/07/owl#": "owl:"}


def short(term):
    """An IRI with a known namespace as prefix:name; long texts are cut."""
    s = str(term)
    for k, v in SHORT.items():
        if s.startswith(k):
            return v + s[len(k):]
    return s if len(s) < 70 else s[:67] + "…"


def record_graph(record, previous=None):
    """The RDF triples of one record (what the knowledge graph stores for it)."""
    g = Graph()
    graph.record_triples(g, record, previous)
    return g


def record_rdf_dot(g):
    out = ["digraph R {", "rankdir=LR; bgcolor=transparent; nodesep=0.18; ranksep=0.5;",
           'node [fontname="Helvetica" fontsize=9];',
           'edge [fontname="Helvetica" fontsize=8 color="#8a8984" fontcolor="#55544f"];']
    ids = {}

    def node(t):
        if t in ids:
            return ids[t]
        n = f"n{len(ids)}"
        ids[t] = n
        if isinstance(t, Literal):
            val = str(t)
            out.append(f'{n} [shape=box style="filled" fillcolor="#fff7e0" color="{PARAM}" '
                       f'label={q(val[:60] + ("…" if len(val) > 60 else ""))}];')
        elif isinstance(t, BNode):
            out.append(f'{n} [shape=circle width=.2 label="" style=filled fillcolor="#d9d8d4" color="#8a8984"];')
        else:
            out.append(f'{n} [shape=ellipse style=filled fillcolor="{REG_FILL}" color="{REG}" label={q(short(t))}];')
        return n

    for s, p, o in sorted(g, key=lambda x: (str(x[0]), str(x[1]))):
        out.append(f"{node(s)} -> {node(o)} [label={q(short(p))}];")
    out.append("}")
    return "\n".join(out)


def ontology_dot():
    """The classes and properties of the ontology (spec/ontology.ttl): (DOT text, classes, properties)."""
    g = Graph()
    g.parse(config.SPEC / "ontology.ttl")
    classes = {c for c in g.subjects(RDF.type, OWL.Class) if isinstance(c, URIRef)}
    out = ["digraph O {", "rankdir=RL; bgcolor=transparent; nodesep=0.12; ranksep=0.9;",
           'node [fontname="Helvetica" fontsize=9 shape=box style="rounded,filled" fillcolor="#ffffff" '
           'color="#8a8984"];',
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


def chain_dot(kb, base_count):
    """The chain of versions: one named graph per update; the updates approved in the app are orange."""
    ups = kb.updates
    per = {}
    for r in kb.records:
        per[r.update_id] = per.get(r.update_id, 0) + 1
    out = ["digraph C {", "rankdir=LR; bgcolor=transparent; nodesep=0.15; ranksep=0.25;",
           'node [fontname="Helvetica" fontsize=9 shape=folder style=filled fillcolor="#f7f7f5" color="#8a8984"];',
           'edge [color="#8a8984" arrowsize=.6];']
    shown = list(enumerate(ups))
    if base_count > 8:              # the starting chain is long: first two, an ellipsis, the last three
        keep = set(range(2)) | set(range(base_count - 3, len(ups)))
        shown = [(i, u) for i, u in shown if i in keep]
    prev = None
    for i, u in shown:
        in_app = i >= base_count
        fill = COMPANY_FILL if in_app else "#f7f7f5"
        lab = (f"v{i + 1}\\n{state.short_doc(u.document)}\\n{u.recorded_on or ''}\\n"
               f"{_plural(per.get(u.update_id, 0), 'record')}")
        out.append(f'u{i} [label={q(lab)} fillcolor="{fill}" color="{COMPANY if in_app else "#8a8984"}"];')
        if prev is not None:
            gap = i - prev > 1
            out.append(f'u{prev} -> u{i}' + (f' [style=dashed label="… {_plural(i - prev - 1, "update")}"]'
                                             if gap else "") + ";")
        prev = i
    out.append("}")
    return "\n".join(out)


def derivation_dot(result, month, fact, depth=3, max_nodes=22, skip_zero=True):
    """How one value of a calculation was derived, from the engine trace."""
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
        val = state.fmt(f, v)
        when = "" if m == month else (" (year)" if m == 0 else f" ({state.MON[m - 1]})")
        src = t["source"][0] if t.get("source") else {}
        lab = f"{state.fact_label(f)}{when}\\n{val}\\n{t['rule']}" + (
            f"\\n{state.short_doc(src['document'])} {src['provision']}"[:60]
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
