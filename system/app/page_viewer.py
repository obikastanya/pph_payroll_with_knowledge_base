"""Knowledge base viewer: graph around a fact, rules with their status, table versions, bitemporal timeline,
quality checks, a SPARQL console, and export."""
import io
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import state
import widgets as ui
from pph21kbs import static
from pph21kbs.kb import rdf
from pph21kbs.kb.model import Constraint, FactDef, Parameter, Rule, TableVersion

KINDS = {Rule: "aturan", Parameter: "parameter", TableVersion: "tabel", Constraint: "batasan", FactDef: "fakta"}
PRESETS = {
    "Aturan yang menghasilkan pph21_due": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT ?rule ?id ?validFrom ?validUntil WHERE {
  GRAPH ?g { ?rule pph:produces ?f ; pph:elementId ?id ; pph:validFrom ?validFrom .
             OPTIONAL { ?rule pph:validUntil ?validUntil }
             FILTER(STRENDS(STR(?f), "/pph21_due")) }
} ORDER BY ?validFrom""",
    "Aturan perusahaan dan kebijakannya": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT ?id ?policy ?fact WHERE {
  GRAPH ?g { ?r pph:policy ?policy ; pph:elementId ?id ; pph:produces ?fact }
} ORDER BY ?policy ?id""",
    "Rekaman per dokumen sumber": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
PREFIX eli: <http://data.europa.eu/eli/ontology#>
SELECT ?doc (COUNT(DISTINCT ?r) AS ?records) WHERE {
  GRAPH ?g { ?r pph:hasSource ?q . ?q pph:provision ?p . ?p eli:is_part_of ?doc }
} GROUP BY ?doc ORDER BY DESC(?records)""",
    "Fakta yang dibaca aturan TER": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT DISTINCT ?id ?reads WHERE {
  GRAPH ?g { ?r pph:elementId ?id ; pph:reads ?reads . FILTER(CONTAINS(?id, "TER")) }
} ORDER BY ?id""",
}


def _period_controls(key):
    c1, c2, c3 = st.columns([1, 1.3, 1.5])
    with c1:
        year, month = ui.period_picker(key, 2025, 3)
    with c2:
        omega = ui.knowledge_picker(key)
    with c3:
        update_id = ui.version_picker(f"{key}_v")
        policy = ui.policy_picker(f"{key}_p")
    return date(year, month, 1), omega, update_id, policy


def tab_graph(view, t, omega):
    facts = sorted({r.produces for r in view.rules.values()})
    c1, c2, c3, c4 = st.columns([1.6, 1, 1.2, 1.4])
    focus = c1.selectbox("Fokus fakta", facts, index=facts.index("pph21_due") if "pph21_due" in facts else 0,
                         key="g_focus")
    depth = c2.slider("Kedalaman", 1, 5, 2, key="g_depth")
    way = c3.radio("Arah", ("hulu", "hilir", "keduanya"), horizontal=False, key="g_way")
    with c4:
        only = st.toggle("Hanya yang berlaku", True, key="g_only")
        layers = st.multiselect("Lapis", ["regulation", "company"], default=["regulation", "company"], key="g_layers")
    dot, n = ui.dependency_dot(view, focus, depth, upstream=way != "hilir", downstream=way != "hulu",
                               layers=tuple(layers), t=t, omega=omega, only_in_force=only)
    st.graphviz_chart(dot, width="stretch")
    st.caption(f"{n} aturan ditampilkan. Elips = fakta, kotak biru = aturan regulasi, kotak oranye = aturan perusahaan, "
               "silinder = parameter/tabel; garis putus = fakta yang dibaca, garis merah = override.")


def _records_frame(view, t, omega):
    rows = []
    for r in view.records:
        kind = KINDS.get(type(r))
        if kind is None:
            continue
        rows.append({"id": r.id, "jenis": kind, "fakta": getattr(r, "produces", "") or getattr(r, "name", ""),
                     "lapis": getattr(r, "layer", ""), "modalitas": getattr(r, "modality", ""),
                     "berlaku dari": r.valid_from, "berlaku sampai": r.valid_until, "dicatat": r.recorded_on,
                     "status": ui.status(r, t, omega), "sumber": ui.sources(r), "pembaruan": r.update_id})
    return pd.DataFrame(rows)


def tab_rules(kb, view, t, omega):
    df = _records_frame(view, t, omega)
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    q = c1.text_input("Cari (id, fakta, sumber)", "", key="r_q")
    kinds = c2.multiselect("Jenis", sorted(df["jenis"].unique()), default=["aturan"], key="r_kind")
    stat = c3.multiselect("Status", sorted(df["status"].unique()), key="r_status")
    layer = c4.multiselect("Lapis", ["regulation", "company"], key="r_layer")
    sel = df
    if q:
        m = sel.apply(lambda r: q.lower() in " ".join(map(str, r.values)).lower(), axis=1)
        sel = sel[m]
    if kinds:
        sel = sel[sel["jenis"].isin(kinds)]
    if stat:
        sel = sel[sel["status"].isin(stat)]
    if layer:
        sel = sel[sel["lapis"].isin(layer)]
    st.caption(f"{len(sel)} dari {len(df)} rekaman efektif pada ω.")
    event = st.dataframe(sel, hide_index=True, width="stretch", height=330, on_select="rerun",
                         selection_mode="single-row", key="r_table")
    rows = event.selection.rows if event and event.selection else []
    if not rows:
        st.info("Pilih satu baris untuk melihat kartu detailnya.")
        return
    rid = sel.iloc[rows[0]]["id"]
    rec = next(r for r in view.records if r.id == rid)
    with st.container(border=True):
        layer_pill = ui.pill("regulasi", "reg") if getattr(rec, "layer", "regulation") == "regulation" else ui.pill("perusahaan", "com")
        st.markdown(f"#### {rid} {layer_pill}", unsafe_allow_html=True)
        if rec.label:
            st.caption(rec.label)
        c1, c2 = st.columns(2)
        with c1:
            if isinstance(rec, Rule):
                st.markdown(f"**Menghasilkan** `{rec.produces}` · {rec.modality} · lingkup {rec.scope}")
                st.code(rec.expression.text if rec.expression else "", language="python")
                if rec.condition is not None:
                    st.markdown("**Syarat**")
                    st.code(rec.condition.text, language="python")
                if rec.overrides:
                    st.markdown("**Mengalahkan (lex specialis):** " + ", ".join(rec.overrides))
            elif isinstance(rec, Parameter):
                st.markdown(f"**Parameter** `{rec.name}` = **{ui.number(rec.value)}** ({rec.value_type})")
            elif isinstance(rec, TableVersion):
                st.markdown(f"**Tabel** `{rec.name}` ({rec.table_kind}), {len(rec.rows)} baris")
                st.dataframe(ui.frame(rec.rows).head(50), hide_index=True, width="stretch")
            elif isinstance(rec, Constraint):
                st.markdown(f"**Batasan** kode {rec.conflict_code}")
                st.code(rec.assertion.text if rec.assertion else "", language="python")
            st.markdown(f"Berlaku {rec.valid_from or '-'} s.d. {rec.valid_until or 'tanpa batas'} · dicatat "
                        f"{rec.recorded_on} · pembaruan `{rec.update_id}`")
        with c2:
            st.markdown("**Sumber**")
            for s in rec.source or ():
                st.markdown(f"- {s.document} {s.provision}" + (f", hlm. {s.page}" if s.page else "") + f"  \n  *“{s.quote}”*")
            if isinstance(rec, Rule):
                readers = [r.id for r in view.rules.values()
                           if any(rec.produces in (e.dependencies() if e is not None else ()) for e in (r.expression, r.condition))]
                rivals = [r.id for r in view.rules_by_fact.get(rec.produces, []) if r.id != rec.id]
                st.markdown("**Dibaca oleh:** " + (", ".join(readers[:12]) or "-"))
                st.markdown("**Pesaing (fakta sama):** " + (", ".join(rivals) or "-"))
            hist = kb.history(rid)
            if len(hist) > 1:
                st.markdown("**Riwayat rekaman:** " + " → ".join(f"{h.update_id} ({h.recorded_on})" for h in hist))


def tab_tables(view):
    names = sorted(view.tables)
    if not names:
        st.info("Tidak ada tabel.")
        return
    name = st.selectbox("Tabel", names, index=names.index("ter_monthly") if "ter_monthly" in names else 0, key="t_name")
    versions = sorted(view.tables[name], key=lambda v: (v.valid_from or date.min))
    labels = [f"{v.id} · {v.valid_from}..{v.valid_until or ''}" for v in versions]
    i = st.selectbox("Versi", range(len(versions)), index=len(versions) - 1, format_func=lambda k: labels[k], key="t_ver")
    v = versions[i]
    rows = ui.frame(v.rows)
    st.caption(f"{v.table_kind} · {len(rows)} baris · sumber: {ui.sources(v)}")
    c1, c2 = st.columns([1, 1.3])
    c1.dataframe(rows, hide_index=True, width="stretch", height=380)
    with c2:
        if {"lower", "rate"} <= set(rows.columns):
            fig = go.Figure()
            group = "key" if "key" in rows.columns else None
            for k, sub in (rows.groupby(group) if group else [(name, rows)]):
                sub = sub.sort_values("lower")
                fig.add_trace(go.Scatter(x=[float(x) for x in sub["lower"]], y=[float(x) * 100 for x in sub["rate"]],
                                         mode="lines", line_shape="hv", name=str(k)))
            fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="batas bawah (Rp)",
                              yaxis_title="tarif (%)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Grafik tangga ditampilkan untuk tabel tarif berlapis (kolom lower dan rate).")


def tab_timeline(kb, view, t, omega):
    st.markdown("Batang = masa berlaku [mulai, akhir]; belah ketupat = tanggal dicatat (diketahui). Belah ketupat di "
                "kanan awal batang berarti aturan berlaku surut. Garis biru = periode dipilih, garis oranye = ω.")
    facts = sorted({r.produces for r in kb.records if isinstance(r, Rule)})
    focus = st.multiselect("Fakta", facts, default=[f for f in ("ptkp_amount", "pph21_running", "pph21_dtp",
                                                                   "jp_wage", "ter_rate") if f in facts], key="tl_facts")
    recs = [r for r in kb.records if isinstance(r, Rule) and r.produces in focus and r.valid_from]
    recs.sort(key=lambda r: (r.produces, r.valid_from))
    if not recs:
        return
    end = date(2027, 6, 30)
    fig = go.Figure()
    for i, r in enumerate(recs):
        color = ui.REG if r.layer == "regulation" else ui.COMPANY
        fig.add_trace(go.Scatter(x=[r.valid_from, r.valid_until or end], y=[i, i], mode="lines",
                                 line=dict(color=color, width=9), hovertext=f"{r.id}<br>{r.produces}",
                                 hoverinfo="text", showlegend=False))
        fig.add_trace(go.Scatter(x=[r.recorded_on], y=[i], mode="markers", marker=dict(symbol="diamond", size=9,
                                 color="#3b3a37"), hovertext=f"dicatat {r.recorded_on}", hoverinfo="text",
                                 showlegend=False))
    fig.add_vline(x=t, line_color=ui.REG, line_dash="dash")
    fig.add_vline(x=omega, line_color=ui.COMPANY, line_dash="dot")
    fig.update_layout(height=max(320, 22 * len(recs)), margin=dict(l=10, r=10, t=10, b=10),
                      yaxis=dict(tickvals=list(range(len(recs))), ticktext=[r.id for r in recs], autorange="reversed"),
                      xaxis=dict(range=[date(2012, 1, 1), end]))
    st.plotly_chart(fig, width="stretch")


@st.cache_data(show_spinner="Menjalankan pemeriksa statis ...")
def _static(sig, update_id, policy, omega):
    kb = state.kb_for(update_id, policy)
    rep = static.check(kb, omega, policies=(policy,) if policy else ())
    return [{"tingkat": f.severity, "jenis": f.kind, "unsur": ", ".join(f.ids), "fakta": f.fact, "keterangan": f.detail}
            for f in rep.findings]


@st.cache_data(show_spinner="Validasi SHACL (bisa memakan waktu) ...")
def _shacl(sig, update_id, policy):
    from pph21kbs.kb import shacl
    return [{"unsur": str(e), "pesan": m} for e, m in shacl.validate(state.kb_for(update_id, policy))]


def tab_quality(update_id, policy, omega):
    sig = state._signature()
    rows = _static(sig, update_id, policy, omega)
    errors = [r for r in rows if r["tingkat"] == "error"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Galat statis", len(errors))
    c2.metric("Peringatan", len(rows) - len(errors))
    c3.metric("Tanggal ω", f"{omega:%d/%m/%Y}")
    st.markdown("**Pemeriksa statis (gerbang G3):** aturan mati, aturan yang selalu kalah, konflik lintas lapis")
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=300)
    if st.button("Jalankan validasi SHACL (gerbang G1)", icon=":material/rule:"):
        v = _shacl(sig, update_id, policy)
        if v:
            st.error(f"{len(v)} pelanggaran shape")
            st.dataframe(pd.DataFrame(v), hide_index=True, width="stretch")
        else:
            st.success("Semua shape SHACL terpenuhi.")


@st.cache_resource(show_spinner="Membangun graf RDF ...")
def _dataset(sig, update_id, policy):
    return rdf.to_dataset(state.kb_for(update_id, policy))


def tab_sparql(update_id, policy):
    st.markdown("Kueri SPARQL atas *knowledge graph* (satu *named graph* per pembaruan).")
    preset = st.selectbox("Kueri contoh", list(PRESETS), key="s_preset")
    q = st.text_area("Kueri", PRESETS[preset], height=200, key=f"s_q_{preset}")
    if st.button("Jalankan", icon=":material/play_arrow:"):
        ds = _dataset(state._signature(), update_id, policy)
        try:
            res = ds.query(q)
            rows = [{str(v): (str(row[i]).rsplit("/", 1)[-1] if row[i] is not None else "") for i, v in enumerate(res.vars)}
                    for row in res]
            st.caption(f"{len(rows)} baris")
            st.dataframe(pd.DataFrame(rows[:1000]), hide_index=True, width="stretch")
        except Exception as e:  # noqa: BLE001 - shown to the user
            st.error(f"{type(e).__name__}: {e}")


def tab_export(update_id, policy):
    kb = state.kb_for(update_id, policy)
    st.markdown("Unduh *knowledge base* versi terpilih sebagai TriG (RDF), beserta ontologi dan *shapes* SHACL. "
                "Bisa dibuka di Protégé (ontologi) atau GraphDB / Apache Jena Fuseki (graf dan SPARQL).")
    if st.button("Siapkan TriG", icon=":material/data_object:"):
        buf = io.BytesIO()
        ds = _dataset(state._signature(), update_id, policy)
        buf.write(ds.serialize(format="trig").encode("utf-8"))
        st.download_button("Unduh knowledge base (.trig)", buf.getvalue(), f"kb_{update_id or 'kini'}.trig",
                           "application/trig", icon=":material/download:")
    for name in ("ontology.ttl", "shapes.ttl"):
        path = state.ROOT / "system" / "ontology" / name
        st.download_button(f"Unduh {name}", path.read_bytes(), name, "text/turtle", key=f"dl_{name}")
    st.caption(f"Sidik jari versi: `{kb.fingerprint()[:16]}` · {len(kb.records)} rekaman · {len(kb.updates)} pembaruan")


def show():
    st.title("Penampil knowledge base")
    t, omega, update_id, policy = _period_controls("v")
    kb = state.kb_for(update_id, policy)
    view = kb.view(omega)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rekaman efektif", len(view.records))
    m2.metric("Aturan", len(view.rules))
    m3.metric("Tabel", sum(len(v) for v in view.tables.values()))
    m4.metric("Pembaruan", len(kb.updates))
    tabs = st.tabs(["Graf", "Aturan", "Tabel", "Timeline", "Kualitas", "SPARQL", "Ekspor"])
    with tabs[0]:
        tab_graph(view, t, omega)
    with tabs[1]:
        tab_rules(kb, view, t, omega)
    with tabs[2]:
        tab_tables(view)
    with tabs[3]:
        tab_timeline(kb, view, t, omega)
    with tabs[4]:
        tab_quality(update_id, policy, omega)
    with tabs[5]:
        tab_sparql(update_id, policy)
    with tabs[6]:
        tab_export(update_id, policy)
