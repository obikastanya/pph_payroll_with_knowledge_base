"""Knowledge base viewer: see and understand what the system knows. Topics instead of rule ids, a picture of the
calculation, numbers over time, what changed and when, and a comparison of two dates."""
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import data as d
import demo
import explain as ex
import glossary as g
import inputs
import ui
import viewer_tech

def in_force(rec, t):
    if rec.kind == "fact" or rec.valid_from is None:
        return True
    return rec.valid_from <= t and (rec.valid_until is None or t <= rec.valid_until)


@st.cache_data
def snapshot(signature, t):
    """Records in force at t: the latest version of every id, kept when that version is in force (a later version that
    ends the validity, as a revocation does, wins over the earlier open one). Returned as seqs (cache friendly)."""
    best = {}
    for r in d.kb().records:
        if r.kind in ("rule", "parameter", "table", "constraint") and (r.id not in best or r.seq > best[r.id].seq):
            best[r.id] = r
    return {r.seq for r in best.values() if in_force(r, t)}


def records_at(t):
    seqs = snapshot(demo.signature(), t)
    return [r for r in d.kb().records if r.seq in seqs]


def _period(r):
    a = f"{d.tgl(r.valid_from)}" if r.valid_from else "-"
    return a + (f" s.d. {d.tgl(r.valid_until)}" if r.valid_until else " · masih berlaku")


def _value(r):
    if r.kind == "parameter":
        v = r.value
        if r.value_type == "rate":
            return d.pct(v)
        if r.value_type == "money":
            return d.money(v)
        return str(v)
    return None


def card(r, show_topic=False):
    src = r.source[0] if r.source else None
    where = f"{d.short_doc(src.document)} · {src.provision}" if src else "-"
    if r.kind == "rule":
        title = d.fact_label(r.produces)
        mod = {"mandatory": ("wajib", "blue"), "default": ("standar", "grey"), "optional": ("pilihan", "yellow")}.get(
            r.modality, (r.modality, "grey"))
        body = f"<b>Rumus:</b> {d.readable(r.expression)}"
        if r.condition:
            body = f"<b>Jika:</b> {d.readable(r.condition)}<br>" + body
        badge = ui.badge(mod[0], mod[1])
    elif r.kind == "parameter":
        title = (r.label_id or r.name).capitalize()
        body = f"<b>Nilai:</b> {_value(r)}"
        badge = ui.badge("angka", "green")
    elif r.kind == "table":
        title = (r.label_id or r.name).capitalize()
        body = f"<b>Tabel</b> {len(r.rows or ())} baris" + (" (dari lampiran)" if r.rows_ref else "")
        badge = ui.badge("tabel", "yellow")
    else:
        title, body, badge = (r.label_id or r.id), "Batasan yang diperiksa", ui.badge("batasan", "red")
    topic = f" · {d.topic_of(r)}" if show_topic else ""
    quote = f"<div class='quote'>“{src.quote}”</div>" if src and src.quote else ""
    old = " old" if r.valid_until and r.valid_until < d.TODAY else ""
    ui.html(f"<div class='rule{old}'>{badge}<b>{title}</b><span class='muted'>{topic}</span><br>{body}<br>"
            f"<span class='muted'>{g.term('berlaku', 'Berlaku')}: {_period(r)} · {g.term('sumber', 'Sumber')}: {where}"
            f"</span>{quote}</div>")
    return r


def tab_topics(recs, t):
    visible = [r for r in recs if not d.is_input_convention(r)]
    counts = {}
    for r in visible:
        counts[d.topic_of(r)] = counts.get(d.topic_of(r), 0) + 1
    topics = [x for x in d.TOPICS if counts.get(x[0])]
    known = {x[0] for x in topics}
    topics += [(t_, ":material/apartment:", "Aturan dari kebijakan perusahaan yang terpasang.", ())
               if t_ == "Kebijakan perusahaan" else
               (t_, ":material/category:", "Bagian knowledge base yang tidak masuk topik di atas; namanya dari nilai "
                "yang dihasilkannya.", ()) for t_ in sorted(counts) if t_ not in known]
    cols = st.columns(3)
    for i, (title, icon, expl, _) in enumerate(topics):
        with cols[i % 3].container(border=True):
            st.markdown(f"**{icon} {title}**  \n{expl}")
            st.caption(f"{counts[title]} aturan, angka, dan tabel")
    pick = st.pills("Buka topik", [x[0] for x in topics], default=topics[0][0], key="v_topic")
    if not pick:
        return
    items = sorted((r for r in visible if d.topic_of(r) == pick), key=lambda r: (r.kind != "parameter", r.kind, r.id))
    st.markdown(f"#### {pick}")
    g.md(f"<span class='muted'>Label: {ui.badge('wajib', 'blue')}{g.term('wajib', 'apa itu?')} &nbsp; "
         f"{ui.badge('standar', 'grey')}{g.term('standar', 'apa itu?')} &nbsp; {ui.badge('angka', 'green')}"
         f"{g.term('parameter', 'apa itu?')} &nbsp; {ui.badge('tabel', 'yellow')}{g.term('tabel', 'apa itu?')}</span>")
    for r in items:
        card(r)
        if r.kind == "table" and r.rows:
            with st.expander("Lihat isi tabel"):
                st.dataframe(_table_frame(r), hide_index=True, width="stretch")


def _table_frame(r):
    rows = []
    for row in r.rows:
        rows.append({k: (d.pct(v) if hasattr(v, "denominator") and v < 1 else
                         d.money(v) if hasattr(v, "denominator") else v) for k, v in row.items()})
    return pd.DataFrame(rows)


@st.cache_data
def flow(signature, t):
    """The calculation at date t as the knowledge base has it: the main steps (values the KB marks as output, and values
    whose rules read a table), and which step feeds which, through the helper values in between. Nothing here is
    written for a particular regulation: a new step, or another way of computing, comes from the rules in force."""
    rules = [r for r in d.current() if r.kind == "rule" and r.layer == "regulation" and d.in_force(r, t)]
    tables = {r.name for r in d.kb().records if r.kind == "table"}
    reads, uses_table, real = {}, set(), set()
    for r in rules:
        facts_read, names = d._deps(r)
        reads.setdefault(r.produces, set()).update(facts_read)
        if not d.is_input_convention(r):
            real.add(r.produces)
            if names & tables:
                uses_table.add(r.produces)
    outputs = {n for n, f in d.facts().items() if f.output}
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
    # values the KB computes by fixed point (gross-up) feed back into what they are computed from: those edges are
    # the loop, drawn but not used to order the steps
    fixed = {r.produces for r in rules if r.fixed_point}
    loops = {(a, b) for a, b in edges if a in fixed}
    level = {}

    def depth(f, stack=()):
        if f not in level:
            ups = [a for a, b in edges if b == f and a != "_input" and a not in stack and (a, b) not in loops]
            level[f] = 1 + max((depth(a, stack + (f,)) for a in ups), default=0)
        return level[f]
    order = sorted(main, key=lambda f: (depth(f), d.fact_label(f)))
    helpers = {b: sorted(f for f, bs in owner.items() if b in bs) for b in main}
    return order, sorted(edges), helpers, loops


def flow_dot(order, edges, pick, loops):
    out = ['digraph F { rankdir=LR; bgcolor=transparent; nodesep=.18; ranksep=.45;',
           'node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10 color="#b4b3ae" fillcolor="#ffffff"];',
           'edge [color="#8a8984" arrowsize=.6];']
    for f in order:
        out.append(f'"{f}" [label="{d.fact_label(f)}"' + (' penwidth=2.4 color="#2a78d6" fillcolor="#e8f1fc"' if f == pick
                                                           else "") + "];")
    for a, b in edges:
        if a == "_input":
            continue
        back = (a, b) in loops                              # the fixed-point loop: drawn, but not for the layout
        out.append(f'"{a}" -> "{b}"' + (' [style=dashed color="#eb6834" constraint=false]' if back else "") + ";")
    return "\n".join(out) + "}"


def tab_flow(recs, t):
    order, edges, helpers, loops = flow(demo.signature(), t)
    st.caption(f"Urutan perhitungan pada {d.tgl(t)}, digambar dari aturan yang berlaku di knowledge base: langkah utama "
               "adalah nilai yang ditandai KB sebagai hasil dan nilai yang memakai tabel. Ganti tanggal di atas untuk "
               "melihat cara hitung tahun lain.")
    default = ex.ROOT if ex.ROOT in order else order[-1]
    pick = st.selectbox("Langkah", order, index=order.index(default), key=f"v_flow_{t}",
                        format_func=lambda f: f"{d.fact_label(f)} ({f})")
    st.graphviz_chart(flow_dot(order, edges, pick, loops), width="stretch")
    st.caption("Langkah tanpa panah masuk dihitung langsung dari data pegawai dan perusahaan. Garis oranye putus-putus = "
               "perhitungan yang berputar (misalnya gross-up: tunjangan pajak ikut menaikkan bruto).")
    facts = {pick, *helpers.get(pick, [])}
    found = [r for r in recs if r.kind == "rule" and r.produces in facts and not d.is_input_convention(r)]
    st.markdown(f"**{len(found)} aturan** untuk langkah *{d.fact_label(pick)}*"
                + (f", termasuk nilai antara: {', '.join(d.fact_label(f).lower() for f in helpers[pick])}"
                   if helpers.get(pick) else "") + ":")
    for r in found:
        card(r)


def tab_numbers():
    ps = {}
    for r in d.kb().records:
        if r.kind == "parameter" and r.value_type in ("money", "rate"):
            ps.setdefault(r.name, []).append(r)
    labels = {n: (v[0].label_id or n).capitalize() for n, v in ps.items()}
    c1, c2 = st.columns([1, 2])
    with c1:
        name = st.radio("Angka", sorted(ps, key=lambda n: labels[n]), format_func=labels.get, key="v_param")
    with c2:
        vs = sorted(ps[name], key=lambda r: r.valid_from)
        money = vs[0].value_type == "money"
        x, y = [], []
        for r in vs:
            x += [r.valid_from, r.valid_until or date(2026, 12, 31)]
            y += [float(r.value) * (1 if money else 100)] * 2
        fig = go.Figure(go.Scatter(x=x, y=y, mode="lines", line_shape="hv", line=dict(color="#2a78d6", width=3)))
        fig.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="Rp" if money else "%",
                          yaxis_tickformat=",.0f" if money else ".2f", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        for r in reversed(vs):
            card(r)
    st.divider()
    tables = {}
    for r in d.kb().records:
        if r.kind == "table" and r.rows:
            tables.setdefault(r.name, []).append(r)
    c1, c2 = st.columns([1, 2])
    name = c1.selectbox("Tabel", sorted(tables), format_func=lambda n: (tables[n][0].label_id or n).capitalize(),
                        key="v_table")
    ver = c2.selectbox("Versi", sorted(tables[name], key=lambda r: r.valid_from, reverse=True), key="v_tver",
                       format_func=lambda r: f"{_period(r)} · {d.short_doc(r.source[0].document) if r.source else ''}")
    st.dataframe(_table_frame(ver), hide_index=True, width="stretch", height=300)


def tab_history():
    st.caption("Setiap pembaruan berasal dari satu dokumen. Yang terbaru di atas.")
    by_update = {}
    for r in d.kb().records:
        if r.kind != "fact":
            by_update.setdefault(r.update_id, []).append(r)
    for u in reversed(d.kb().updates):
        recs = by_update.get(u.update_id, [])
        if not recs:
            continue
        kinds = {}
        for r in recs:
            kinds[r.kind] = kinds.get(r.kind, 0) + 1
        what = ", ".join(f"{n} {dict(rule='aturan', parameter='angka', table='tabel', constraint='batasan')[k]}"
                         for k, n in kinds.items())
        with st.expander(f"{d.tgl(u.recorded_on)} · {d.doc_title(u.document)} — {what}"):
            for r in recs[:25]:
                card(r, show_topic=True)


def tab_compare():
    c1, c2 = st.columns(2)
    a = c1.date_input("Tanggal pertama", date(2023, 12, 31), key="v_a")
    b = c2.date_input("Tanggal kedua", date(2024, 1, 1), key="v_b")
    ra = {r.id: r for r in records_at(a)}
    rb = {r.id: r for r in records_at(b)}
    added = [rb[i] for i in rb if i not in ra and not d.is_input_convention(rb[i])]
    gone = [ra[i] for i in ra if i not in rb and not d.is_input_convention(ra[i])]
    changed = [(ra[i], rb[i]) for i in ra if i in rb and ra[i].seq != rb[i].seq]
    by_name_a = {r.name: r for r in ra.values() if r.kind == "parameter"}
    by_name_b = {r.name: r for r in rb.values() if r.kind == "parameter"}
    moved = [(by_name_a[n], by_name_b[n]) for n in by_name_a if n in by_name_b and by_name_a[n].value != by_name_b[n].value]
    m = st.columns(4)
    m[0].metric("Mulai berlaku", len(added))
    m[1].metric("Berhenti berlaku", len(gone))
    m[2].metric("Aturan diubah", len(changed))
    m[3].metric("Angka berubah", len(moved))
    for x, y in moved:
        ui.html(f"<div class='rule'><b>{(x.label_id or x.name).capitalize()}</b>: <span class='diff-old'>{_value(x)}</span>"
                f" → <span class='diff-new'>{_value(y)}</span> <span class='muted'>({d.short_doc(y.source[0].document)})"
                f"</span></div>")
    if added:
        st.markdown("**Mulai berlaku**")
        for r in added:
            if r.kind != "parameter" or r.name not in by_name_a:
                card(r, show_topic=True)
    if gone:
        st.markdown("**Berhenti berlaku**")
        for r in gone:
            if r.kind != "parameter" or r.name not in by_name_b:
                card(r, show_topic=True)


def tab_search(recs):
    q = st.text_input("Cari", placeholder="mis. biaya jabatan, natura, PMK 168, Pasal 17", key="v_q")
    if not q:
        st.caption("Cari di nama, rumus, pasal, kutipan, dan nama dokumen.")
        return
    ql = q.lower()
    hits = []
    for r in recs:
        hay = " ".join([r.id, getattr(r, "label_id", "") or "", getattr(r, "name", "") or "",
                        d.fact_label(getattr(r, "produces", "") or "") if getattr(r, "produces", None) else "",
                        d.expr_text(getattr(r, "expression", "") or "")]
                       + [f"{s.document} {d.doc_title(s.document)} {s.provision} {s.quote}" for s in r.source])
        if ql in hay.lower():
            hits.append(r)
    st.caption(f"{len(hits)} hasil")
    for r in hits[:40]:
        card(r, show_topic=True)


def show():
    st.session_state.page_ctx = "kb"
    st.title("Penampil knowledge base")
    mode = st.segmented_control("Tampilan", ["Isi KB", "Sistem knowledge base (teknis)"], default="Isi KB",
                                key="v_mode", label_visibility="collapsed") or "Isi KB"
    technical = mode != "Isi KB"
    if technical:
        g.md(f"Cara sistem menyimpan dan memakai pengetahuan: {g.term('knowledge graph')} {g.term('RDF')} yang "
             f"{g.term('bitemporal')} dan {g.term('dua lapis')}, {g.term('ontologi')}, pemeriksaan, versi per "
             f"{g.term('named graph')}, dan {g.term('jejak')} engine. Semua dari KB demo saat ini.")
    else:
        g.md(f"Apa yang diketahui sistem tentang PPh 21: {g.term('aturan')}, {g.term('parameter', 'angka')}, dan "
             f"{g.term('tabel')}, masing-masing dengan {g.term('berlaku', 'tanggal berlaku')} dan {g.term('sumber')} "
             "pasalnya.")
    c1, c2 = st.columns([1, 3])
    t = c1.date_input("Tampilkan yang berlaku pada", d.TODAY, key="v_t", help=g.tip("berlaku"))
    st.session_state.g_date = t
    recs = records_at(t)
    visible = [r for r in recs if not d.is_input_convention(r)]
    docs = {s.document for r in visible for s in r.source}
    with c2:
        m = st.columns(4)
        m[0].metric("Aturan", sum(r.kind == "rule" for r in visible), help=g.tip("aturan"))
        m[1].metric("Angka", sum(r.kind == "parameter" for r in visible), help=g.tip("parameter"))
        m[2].metric("Tabel", sum(r.kind == "table" for r in visible), help=g.tip("tabel"))
        m[3].metric("Dokumen sumber", len(docs), help=g.tip("sumber"))
    if technical:
        viewer_tech.show(t, recs)
        return
    tabs = st.tabs(["Peta topik", "Alur perhitungan", "Angka dari waktu ke waktu", "Riwayat perubahan",
                    "Bandingkan dua tanggal", "Cari", "Data yang dibutuhkan", "Kebijakan perusahaan"])
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


def tab_policies():
    g.md(f"{g.term('kebijakan perusahaan', 'Kebijakan perusahaan')} yang terpasang di knowledge base. Dipakai kalkulator "
         "bila dipilih. Di keadaan awal demo belum ada; setujui SP14 di Manajemen KB.")
    pols = demo.installed_policies()
    if not pols:
        st.caption("Belum ada kebijakan perusahaan terpasang.")
        return
    pick = st.selectbox("Kebijakan", list(pols), key="v_pol", format_func=lambda i: f"{i} · {pols[i]}")
    for r in d.kb().view(demo.TODAY).rules.values():
        if r.layer == "company" and r.policy == pick:
            src = r.source[0] if r.source else None
            ui.html(f"<div class='rule company'>{ui.badge('perusahaan', 'orange')}<b>{d.fact_label(r.produces)}</b><br>"
                    f"<b>Rumus:</b> {d.readable(r.expression)}<br><span class='muted'>Berlaku: {_period(r)}"
                    f"{' · ' + src.provision if src else ''}</span>"
                    + (f"<div class='quote'>“{src.quote}”</div>" if src else "") + "</div>")


def tab_inputs(t):
    g.md("Data yang ditanyakan kalkulator, langsung dari aturan yang berlaku pada tahun itu. Saat peraturan atau kebijakan "
         "perusahaan baru membaca data baru, data itu muncul di sini dan menjadi kolom di kalkulator tanpa mengubah "
         "program.")
    pols = demo.installed_policies()
    policy = st.selectbox("Dengan kebijakan perusahaan", [None] + list(pols), key="v_in_pol",
                          format_func=lambda p: "Tidak ada" if p is None else f"{p} · {pols[p]}")
    found = inputs.discover(t.year, policy)
    group = {"income": "Penghasilan per bulan", "benefit": "Natura per bulan", "hr": "Data HR per bulan",
             "zakat": "Penghasilan per bulan", "employee": "Data pegawai", "employer": "Data perusahaan",
             "case": "Data pegawai"}
    rows = [{"Data": inputs.label(k), "Kelompok": group[k.split(".")[0]],
             "Dari": "kebijakan perusahaan" if e["layer"] == "company" else "peraturan",
             "Bulan": "semua" if len(e["months"]) == 12 else f"{d.MON[e['months'][0] - 1]}–{d.MON[e['months'][-1] - 1]}",
             "Dibaca oleh": ", ".join(e["rules"][:3]) + (" ..." if len(e["rules"]) > 3 else ""),
             "Definisi": (inputs.definition(k) or {}).get("origin", "belum ada")} for k, e in found.items()]
    st.dataframe(pd.DataFrame(rows).sort_values(["Kelompok", "Data"]), hide_index=True, width="stretch")
    ui.mock("Definisi data di demo ini berupa berkas data KB (kb_ext/) yang ikut pembaruan; di sistem penuh menjadi unsur "
            "knowledge base bersama aturan yang pertama kali membacanya.")
