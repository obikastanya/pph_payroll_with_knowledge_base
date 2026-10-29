"""Technical view of the KB viewer: the knowledge base system itself (the novelty of the research), with the real KB of
the demo. Architecture, the knowledge graph, one element as RDF, the two times of every element, the version chain of
named graphs, the trace of a calculation, the ontology and the checks, SPARQL and export."""
import io
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import data as d
import demo
import employee as emp
import glossary as g
import kbviz as kv

KIND = {"rule": "aturan", "parameter": "angka", "table": "tabel", "constraint": "batasan", "fact": "fakta",
        "tombstone": "hapus"}
RANK = {4: "4 · wajib (negara)", 3: "3 · kebijakan perusahaan", 2: "2 · pilihan yang dipakai perusahaan", 1: "1 · standar"}
WHY = {"lex superior": "kedudukan lebih rendah", "lex specialis": "kalah oleh aturan yang lebih khusus",
       "lex posterior": "kalah oleh aturan yang lebih baru", "redundant": "nilainya sama, tidak dipakai"}
PRESETS = {
    "Aturan yang menghasilkan PPh 21 sebulan, dengan masa berlakunya": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT ?id ?validFrom ?validUntil ?graph WHERE {
  GRAPH ?graph { ?rule pph:produces ?f ; pph:elementId ?id ; pph:validFrom ?validFrom .
                 OPTIONAL { ?rule pph:validUntil ?validUntil }
                 FILTER(STRENDS(STR(?f), "/pph21_due")) }
} ORDER BY ?validFrom""",
    "Jumlah unsur per dokumen sumber": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
PREFIX eli: <http://data.europa.eu/eli/ontology#>
SELECT ?doc (COUNT(DISTINCT ?r) AS ?unsur) WHERE {
  GRAPH ?g { ?r pph:hasSource ?q . ?q pph:provision ?p . ?p eli:is_part_of ?doc }
} GROUP BY ?doc ORDER BY DESC(?unsur)""",
    "Aturan yang membaca biaya jabatan (hilir)": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT DISTINCT ?id ?produces WHERE {
  GRAPH ?g { ?r pph:elementId ?id ; pph:reads ?f ; pph:produces ?produces .
             FILTER(STRENDS(STR(?f), "/job_expense")) }
} ORDER BY ?id""",
    "Unsur yang dicatat sesudah tanggal berlakunya (retroaktif)": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT ?id ?validFrom ?recordedOn WHERE {
  GRAPH ?g { ?r pph:elementId ?id ; pph:validFrom ?validFrom ; pph:recordedOn ?recordedOn .
             FILTER(?recordedOn > ?validFrom) }
} ORDER BY DESC(?recordedOn)""",
    "Aturan perusahaan dan kebijakannya": """PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT ?id ?policy ?fact WHERE {
  GRAPH ?g { ?r pph:policy ?policy ; pph:elementId ?id ; pph:produces ?fact }
} ORDER BY ?policy ?id""",
}
TABS = ["Arsitektur sistem", "Knowledge graph", "Satu unsur sebagai RDF", "Dua waktu (bitemporal)",
        "Versi dan named graph", "Jejak perhitungan", "Ontologi dan pemeriksaan", "SPARQL dan ekspor"]


@st.cache_resource(show_spinner="Menyusun graf RDF dari knowledge base ...")
def dataset(signature):
    from pph21kbs.kb import rdf
    return rdf.to_dataset(d.kb())


@st.cache_data(show_spinner="Menjalankan pemeriksa statis ...")
def static_findings(signature, omega, policies):
    from pph21kbs import static
    rep = static.check(d.kb(), omega, policies=policies)
    return [{"Tingkat": f.severity, "Jenis": f.kind, "Unsur": ", ".join(f.ids), "Fakta": f.fact, "Keterangan": f.detail}
            for f in rep.findings]


@st.cache_data(show_spinner="Validasi SHACL ...")
def shacl_violations(signature):
    from pph21kbs.kb import shacl
    return [{"Unsur": str(e), "Pesan": m} for e, m in shacl.validate(d.kb())]


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


def _fact_pick(view, key, default="pph21_due", label="Nilai yang dilihat"):
    facts = sorted({r.produces for r in view.rules.values()}, key=d.fact_label)
    return st.selectbox(label, facts, index=facts.index(default) if default in facts else 0, key=key,
                        format_func=lambda f: f"{d.fact_label(f)} ({f})")


# ---------------------------------------------------------------- tabs
def tab_architecture(view, t, recs):
    st.caption(f"Dari dokumen sampai hitungan. Angka di gambar: KB demo saat ini, yang berlaku pada {d.tgl(t)}.")
    st.graphviz_chart(kv.architecture_dot(stats(view, recs)), width="stretch")
    rows = [
        ("Akuisisi", "Relevansi, m versi usulan dari LLM, gerbang G1–G5, kesepakatan atau ragu",
         "system/pph21kbs/pipeline/ (run, select, consensus)", "Dokumen baru, Review"),
        ("Gerbang G1", "Bentuk graf sesuai shapes SHACL", "system/ontology/shapes.ttl", "tab Ontologi dan pemeriksaan"),
        ("Gerbang G2", "Kutipan benar-benar ada di dokumen", "system/pph21kbs/pipeline/gates.py", "Review"),
        ("Gerbang G3", "Pemeriksa statis: aturan mati, selalu kalah, konflik antarlapis", "system/pph21kbs/static.py",
         "tab Ontologi dan pemeriksaan"),
        ("Gerbang G4–G5", "Regresi kasus uji dan non-vakuitas (Δ benar-benar mengubah hitungan)",
         "system/pph21kbs/pipeline/gates.py", "Review: contoh sebelum/sesudah"),
        ("Knowledge base", "Rekaman bitemporal dua lapis; satu pembaruan = satu named graph",
         "system/pph21kbs/kb/ (store, rdf, delta)", "tab Versi dan named graph"),
        ("Ontologi", "Kelas dan hubungan; memakai ELI, OWL-Time, PROV-O", "system/ontology/ontology.ttl",
         "tab Ontologi dan pemeriksaan"),
        ("Engine", "Pilih aturan (kedudukan, kekhususan, waktu), hitung titik tetap gross-up, simpan jejak",
         "system/pph21kbs/engine/evaluator.py", "tab Jejak perhitungan, Kalkulator"),
        ("Analisis dampak", "Kueri SPARQL: nilai yang berubah, aturan perusahaan yang membacanya",
         "system/pph21kbs/impact.py, system/ontology/queries/", "Review: kebijakan yang terdampak"),
    ]
    st.dataframe(pd.DataFrame(rows, columns=["Bagian", "Tugasnya", "Kode", "Terlihat di demo"]), hide_index=True,
                 width="stretch")


def tab_graph(view, t):
    g.md(f"Bagian {g.term('knowledge graph')} di sekitar satu nilai: aturan yang menghasilkannya, nilai lain yang "
         "dibacanya, angka dan tabelnya, dan (bila dipilih) pasal sumbernya.")
    c1, c2, c3, c4 = st.columns([1.8, 1, 1.1, 1.3])
    with c1:
        focus = _fact_pick(view, "kt_focus")
    depth = c2.slider("Kedalaman", 1, 5, 2, key="kt_depth")
    way = c3.radio("Arah", ("ke asal (hulu)", "ke pemakai (hilir)", "keduanya"), key="kt_way")
    with c4:
        only = st.toggle("Hanya yang berlaku", True, key="kt_only", help=g.tip("berlaku"))
        prov = st.toggle("Tampilkan pasal sumber", False, key="kt_prov", help=g.tip("sumber"))
        layers = st.multiselect("Lapis", ["regulation", "company"], default=["regulation", "company"], key="kt_layers",
                                format_func={"regulation": "negara", "company": "perusahaan"}.get)
    dot, n = kv.dependency_dot(view, focus, t, depth, upstream=way != "ke pemakai (hilir)",
                               downstream=way != "ke asal (hulu)", layers=tuple(layers), only_in_force=only,
                               provenance=prov)
    st.graphviz_chart(dot, width="stretch")
    st.caption(f"{n} aturan, berlaku pada {d.tgl(t)}. Elips = nilai (fakta), kotak biru = aturan negara, kotak oranye = "
               "aturan perusahaan, silinder kuning = angka/tabel, map = dokumen, catatan = pasal. Garis tebal = "
               "menghasilkan, putus-putus = membaca, titik-titik = memakai angka/tabel, merah = mengesampingkan.")
    st.markdown(f"**Semua aturan untuk *{d.fact_label(focus)}* dan cara engine memilihnya**")
    g.md(f"<span class='muted'>{g.term('resolusi konflik', 'Urutan pilih')}: kedudukan tertinggi menang; bila sama, "
         "yang lebih khusus; bila masih sama, yang mulai berlaku lebih baru.</span>")
    rows = [{"Aturan": r.id, "Lapis": "perusahaan" if r.layer == "company" else "negara",
             "Kedudukan": RANK.get(r.rank, r.rank), "Berlaku": f"{d.tgl(r.valid_from)} – {d.tgl(r.valid_until) if r.valid_until else 'kini'}",
             "Status pada tanggal": kv.status(r, t), "Mengesampingkan": ", ".join(r.overrides) or "-",
             "Sumber": f"{d.short_doc(r.source[0].document)} {r.source[0].provision}" if r.source else "-"}
            for r in sorted(view.rules_by_fact.get(focus, []), key=lambda r: (-r.rank, r.valid_from or date.min))]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def tab_rdf(view):
    kb = d.kb()
    g.md(f"Setiap unsur KB disimpan sebagai sekumpulan triple {g.term('RDF')} di {g.term('named graph')} pembaruannya. "
         "Inilah bentuk asli yang disimpan, ditanyai dengan SPARQL, dan diperiksa SHACL.")
    ids = sorted({r.id for r in kb.records if r.kind in ("rule", "parameter", "table", "constraint")
                  and not d.is_input_convention(r)})
    label = {r.id: (d.fact_label(r.produces) if r.kind == "rule" else (r.label_id or getattr(r, "name", ""))) for r in kb.records
             if r.id in ids}
    first = next((r.id for r in view.rules_by_fact.get("job_expense", []) if r.id in ids), ids[0])
    c1, c2 = st.columns([2, 1.4])
    rid = c1.selectbox("Unsur", ids, index=ids.index(first),
                       key="kt_rid", format_func=lambda i: f"{i} · {label.get(i, '')}")
    versions = [r for r in kb.records if r.id == rid]
    i = c2.selectbox("Rekaman (versi unsur)", range(len(versions)), index=len(versions) - 1, key=f"kt_rver_{rid}",
                     format_func=lambda k: f"#{versions[k].seq} · dicatat {d.tgl(versions[k].recorded_on)} · "
                                           f"{versions[k].update_id}")
    rec, prev = versions[i], (versions[i - 1] if i else None)
    graph = kv.record_graph(rec, prev)
    from pph21kbs.kb import rdf
    m = st.columns(4)
    m[0].metric("Triple", len(graph))
    m[1].metric("Named graph", f"…/update/{rec.update_id}")
    m[2].metric("Versi unsur ini", f"{i + 1} dari {len(versions)}")
    m[3].metric("Revisi dari", f"#{prev.seq}" if prev else "-")
    view_graph, view_table = st.tabs(["Graf", "Tabel triple"])
    with view_graph:
        st.graphviz_chart(kv.record_rdf_dot(graph), width="stretch")
        st.caption("Biru = sumber daya (IRI), kuning = nilai (literal), bulatan abu = simpul tanpa nama. Rumus disimpan "
                   "sebagai teks dan hubungan pph:reads ke setiap nilai yang dibacanya.")
    with view_table:
        rows = [{"Subjek": kv.short(s), "Predikat": kv.short(p), "Objek": kv.short(o)} for s, p, o in graph]
        st.dataframe(pd.DataFrame(rows).sort_values(["Subjek", "Predikat"]), hide_index=True, width="stretch", height=380)
    with st.expander("Turtle (teks RDF)"):
        graph.bind("pph", rdf.PPH)
        graph.bind("kb", rdf.KB)
        graph.bind("eli", rdf.ELI)
        st.code(graph.serialize(format="turtle"), language="turtle")


def tab_bitemporal(t):
    kb = d.kb()
    g.md(f"Setiap unsur punya dua waktu ({g.term('bitemporal')}): {g.term('berlaku', 'tanggal berlaku')} menurut "
         f"peraturan dan {g.term('dicatat', 'tanggal dicatat')} ke KB. Titik di bawah garis diagonal = dicatat sesudah "
         "mulai berlaku (retroaktif); di atas = diumumkan lebih dulu.")
    recs = [r for r in kb.records if r.kind in ("rule", "parameter", "table") and r.valid_from and r.recorded_on
            and not d.is_input_convention(r)]
    fig = go.Figure()
    for layer, color, name in (("regulation", kv.REG, "negara"), ("company", kv.COMPANY, "perusahaan")):
        pts = [r for r in recs if getattr(r, "layer", "regulation") == layer]
        if pts:
            fig.add_trace(go.Scatter(x=[r.valid_from for r in pts], y=[r.recorded_on for r in pts], mode="markers",
                                     name=name, marker=dict(color=color, size=7, opacity=.75),
                                     hovertext=[f"{r.id}<br>berlaku {r.valid_from}<br>dicatat {r.recorded_on}" for r in pts],
                                     hoverinfo="text"))
    lo, hi = date(2008, 1, 1), date(2027, 6, 30)
    fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", line=dict(color="#b4b3ae", dash="dot"),
                             name="dicatat = berlaku", hoverinfo="skip"))
    fig.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), xaxis_title="Mulai berlaku",
                      yaxis_title="Dicatat ke KB", plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h"))
    c1, c2 = st.columns([2, 1])
    c1.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    retro = [r for r in recs if r.recorded_on > r.valid_from]
    with c2:
        st.metric("Unsur bertanggal", len(recs))
        st.metric("Dicatat sesudah berlaku", len(retro))
        early = [r for r in recs if r.recorded_on < r.valid_from]
        lines = [f"Terbaru dicatat {'sesudah' if r in retro else 'sebelum'} berlaku: "
                 f"{d.short_doc(r.source[0].document) if r.source else r.update_id}, dicatat {d.tgl(r.recorded_on)} "
                 f"untuk berlaku {d.tgl(r.valid_from)}."
                 for r in (max(group, key=lambda r: (r.recorded_on, r.seq)) for group in (retro, early) if group)]
        st.caption(" ".join(lines) + " Kalkulator bisa menghitung 'dengan pengetahuan per tanggal' untuk mengulang "
                   "hitungan lama persis seperti dulu.")
    st.markdown("**Garis waktu per nilai**")
    view = kb.view(d.TODAY)
    facts = sorted({r.produces for r in view.rules.values()}, key=d.fact_label)
    focus = st.multiselect("Nilai", facts, default=[f for f in ("ptkp_amount", "pph21_running", "pph21_dtp", "jp_wage",
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
                                 marker=dict(symbol="diamond", size=9, color="#3b3a37"), hovertext=f"dicatat {r.recorded_on}"))
    fig.add_vline(x=t, line_color=kv.REG, line_dash="dash")
    fig.update_layout(height=max(300, 24 * len(rows)), margin=dict(l=10, r=10, t=10, b=10),
                      yaxis=dict(tickvals=list(range(len(rows))), ticktext=[f"{r.id} #{r.seq}" for r in rows],
                                 autorange="reversed"),
                      xaxis=dict(range=[date(2012, 1, 1), end]), plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.caption("Batang = masa berlaku, belah ketupat = tanggal dicatat, garis putus biru = tanggal yang dipilih di atas.")


def tab_versions():
    kb = d.kb()
    base_n = len(demo.base().updates)
    g.md(f"KB tidak pernah ditimpa. Setiap {g.term('pembaruan')} disimpan sebagai satu {g.term('named graph')}; "
         f"{g.term('versi')} ke-n = gabungan named graph 1..n. Kotak oranye = pembaruan yang disetujui selama demo.")
    st.graphviz_chart(kv.chain_dot(kb, base_n), width="stretch")
    per = {}
    for r in kb.records:
        per.setdefault(r.update_id, {}).setdefault(r.kind, 0)
        per[r.update_id][r.kind] += 1
    rows = []
    for i, u in enumerate(kb.updates):
        c = per.get(u.update_id, {})
        rows.append({"Versi": i + 1, "Pembaruan": u.update_id, "Dokumen": d.short_doc(u.document),
                     "Dicatat": u.recorded_on, "Rekaman": sum(c.values()),
                     "Isi": ", ".join(f"{n} {KIND.get(k, k)}" for k, n in c.items()),
                     "Named graph": f"kb:update/{u.update_id}", "Asal": "demo" if i >= base_n else "KB awal"})
    st.dataframe(pd.DataFrame(rows[::-1]), hide_index=True, width="stretch", height=320)
    st.markdown("**Bandingkan dua versi**")
    c1, c2 = st.columns(2)
    a = c1.number_input("Versi pertama", 1, len(kb.updates), max(1, len(kb.updates) - 1), key="kt_va")
    b = c2.number_input("Versi kedua", 1, len(kb.updates), len(kb.updates), key="kt_vb")
    ka, kb2 = kb.until(kb.updates[a - 1].update_id), kb.until(kb.updates[b - 1].update_id)
    sa, sb = {r.seq for r in ka.records}, {r.seq for r in kb2.records}
    new = [r for r in kb2.records if r.seq not in sa]
    gone = [r for r in ka.records if r.seq not in sb]
    m = st.columns(3)
    m[0].metric("Rekaman di versi pertama", len(ka.records))
    m[1].metric("Rekaman di versi kedua", len(kb2.records))
    m[2].metric("Sidik jari versi kedua", kb2.fingerprint()[:12])
    if new or gone:
        st.dataframe(pd.DataFrame([{"Perubahan": "hanya di versi kedua" if r in new else "hanya di versi pertama", "Rekaman": f"#{r.seq}",
                                    "Unsur": r.id, "Jenis": KIND.get(r.kind, r.kind), "Pembaruan": r.update_id,
                                    "Berlaku": f"{d.tgl(r.valid_from)} – {d.tgl(r.valid_until) if r.valid_until else 'kini'}"
                                    if r.valid_from else "-"} for r in new + gone]), hide_index=True, width="stretch")


def tab_trace():
    g.md(f"{g.term('jejak', 'Jejak')} engine untuk satu hitungan: setiap nilai menyimpan aturan yang dipakai, nilai yang "
         "dibacanya, aturan yang kalah, dan pasalnya. Skenario diambil dari kalkulator.")
    scs = emp.scenarios()
    c1, c2, c3, c4 = st.columns([1.8, 1, 1.6, .8])
    title = c1.selectbox("Skenario", list(scs), key="kt_sc")
    case = emp.scenario_case(scs[title])
    res, err = d.compute(case, d.TODAY)
    if err:
        st.error(err)
        return
    months = sorted(res.periods)
    choices = months + ([0] if res.year else [])
    month = c2.selectbox("Bulan", choices, index=choices.index(0) if 0 in choices else len(choices) - 1, key="kt_m",
                         format_func=lambda m: "Setahun" if m == 0 else d.MONTHS[m - 1])
    facts = sorted({f for (f, m) in res.trace if m == month}, key=d.fact_label)
    default = "annual_pph21" if month == 0 else "pph21_due"
    fact = c3.selectbox("Nilai", facts, index=facts.index(default) if default in facts else 0, key=f"kt_f{month}",
                        format_func=lambda f: f"{d.fact_label(f)} ({f})")
    depth = c4.slider("Kedalaman", 1, 6, 3, key="kt_d")
    st.graphviz_chart(kv.derivation_dot(res, month, fact, depth=depth), width="stretch")
    st.caption("Biru = aturan negara, oranye = aturan perusahaan, kuning = data kasus atau nilai tercatat. Nilai nol "
               "tidak digambar.")
    rows = []
    for (f, m), e in res.trace.items():
        src = e["source"][0] if e.get("source") else {}
        if m != month or src.get("document") == "INPUT-CONVENTION":      # data read straight from the case
            continue
        rows.append({"Nilai": d.fact_label(f), "Hasil": kv.fmt(f, e["value"]), "Aturan": e["rule"],
                     "Lapis": {"regulation": "negara", "company": "perusahaan", "case": "data kasus"}.get(e["layer"], e["layer"]),
                     "Aturan yang kalah": "; ".join(f"{i} ({WHY.get(w, w)})" for i, w in e.get("losers") or []) or "-",
                     "Sumber": f"{d.short_doc(src.get('document', ''))} {src.get('provision', '')}".strip() or "-"})
    lost = sum(r["Aturan yang kalah"] != "-" for r in rows)
    st.markdown(f"**Semua nilai bulan ini** · {len(rows)} nilai, {lost} di antaranya dipilih dari beberapa aturan")
    only = st.toggle("Hanya nilai yang punya aturan kalah", False, key="kt_lost")
    st.dataframe(pd.DataFrame([r for r in rows if not only or r["Aturan yang kalah"] != "-"]), hide_index=True,
                 width="stretch", height=320)


def tab_checks(t):
    sig = demo.signature()
    dot, n_classes, n_props = ontology(sig)
    g.md(f"{g.term('ontologi', 'Ontologi')} sistem: {n_classes} kelas dan {n_props} hubungan. Kelas induk dari standar "
         "ELI (peraturan), PROV-O (asal-usul), OWL-Time (waktu), dan SKOS.")
    st.graphviz_chart(dot, width="content")
    st.caption("Panah segitiga = 'adalah jenis dari'; garis biru putus-putus = hubungan antar kelas.")
    st.markdown("**Shapes SHACL (gerbang G1)**")
    st.dataframe(pd.DataFrame(shapes()), hide_index=True, width="stretch")
    st.markdown("**Pemeriksaan KB demo saat ini**")
    pols = tuple(demo.installed_policies())
    rows = static_findings(sig, t, pols)
    errors = [r for r in rows if r["Tingkat"] == "error"]
    m = st.columns(3)
    m[0].metric("Galat pemeriksa statis", len(errors), help=g.tip("pemeriksa statis"))
    m[1].metric("Peringatan", len(rows) - len(errors))
    m[2].metric("Kebijakan perusahaan ikut diperiksa", len(pols))
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=240)
    if st.button("Jalankan validasi SHACL", icon=":material/rule:", key="kt_shacl", help=g.tip("SHACL")):
        v = shacl_violations(sig)
        if v:
            st.error(f"{len(v)} pelanggaran")
            st.dataframe(pd.DataFrame(v), hide_index=True, width="stretch")
        else:
            st.success("Semua shape SHACL terpenuhi.")


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
        out.append({"Shape": kv.short(s), "Untuk kelas": targets, "Properti diperiksa": ", ".join(paths[:6])
                    + (" …" if len(paths) > 6 else ""), "Aturan SPARQL": rules, "Contoh pesan": msgs[0] if msgs else ""})
    return sorted(out, key=lambda r: r["Shape"])


def tab_sparql():
    g.md(f"Kueri {g.term('SPARQL')} langsung atas graf KB demo ({g.term('named graph')} per pembaruan, plus kb:meta).")
    preset = st.selectbox("Kueri contoh", list(PRESETS), key="kt_preset")
    q = st.text_area("Kueri", PRESETS[preset], height=190, key=f"kt_q_{preset}")
    if st.button("Jalankan", icon=":material/play_arrow:", key="kt_run"):
        try:
            res = dataset(demo.signature()).query(q)
            rows = [{str(v): (kv.short(row[i]) if row[i] is not None else "") for i, v in enumerate(res.vars)}
                    for row in res]
            st.caption(f"{len(rows)} baris")
            st.dataframe(pd.DataFrame(rows[:1000]), hide_index=True, width="stretch")
        except Exception as e:  # noqa: BLE001 - shown to the user
            st.error(f"{type(e).__name__}: {e}")
    st.markdown("**Ekspor**")
    st.caption("Buka di Protégé (ontologi) atau GraphDB / Apache Jena Fuseki (graf dan SPARQL).")
    c = st.columns(3)
    if c[0].button("Siapkan TriG KB demo", icon=":material/data_object:", key="kt_trig"):
        buf = io.BytesIO(dataset(demo.signature()).serialize(format="trig").encode("utf-8"))
        st.download_button("Unduh kb_demo.trig", buf.getvalue(), "kb_demo.trig", "application/trig",
                           icon=":material/download:", key="kt_dl_trig")
    for col, name in zip(c[1:], ("ontology.ttl", "shapes.ttl")):
        col.download_button(f"Unduh {name}", (kv.ROOT / "system" / "ontology" / name).read_bytes(), name, "text/turtle",
                            key=f"kt_dl_{name}", icon=":material/download:")
    st.caption(f"Sidik jari KB demo: `{d.kb().fingerprint()[:16]}` · {len(d.kb().records)} rekaman · "
               f"{len(d.kb().updates)} pembaruan")


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
