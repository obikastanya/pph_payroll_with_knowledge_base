"""Knowledge base viewer: see and understand what the system knows. Topics instead of rule ids, a picture of the
calculation, numbers over time, what changed and when, and a comparison of two dates."""
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import data as d
import glossary as g
import ui

FLOW = {  # step of the picture -> facts whose rules explain it
    "Komponen penghasilan": ("base_salary", "fixed_allowance", "overtime_pay", "thr", "bonus", "other_regular_income"),
    "Natura dan premi": ("benefits_taxable_regular", "benefits_taxable_irregular", "benefit_housing_taxable",
                         "employer_premiums_taxable", "jkk_premium", "jkm_premium", "health_premium_employer"),
    "Bruto sebulan": ("regular_gross", "irregular_gross", "gross_income"),
    "Tarif TER": ("ter_category", "ter_rate"),
    "PPh 21 masa": ("pph21_running", "pph21_due"),
    "Bruto setahun": ("annual_gross",),
    "Biaya jabatan dan iuran": ("job_expense", "employee_pension_contributions", "annual_pension_contributions",
                                "annual_deductions", "jht_employee", "jp_employee"),
    "PTKP": ("ptkp_status_effective", "ptkp_amount"),
    "PKP dan Pasal 17": ("annual_net", "taxable_income", "annual_pph21"),
    "Masa terakhir": ("withheld_before_final", "final_period_tax", "refund_to_employee"),
    "Insentif DTP": ("dtp_eligible", "dtp_facility", "pph21_dtp"),
    "Gaji bersih": ("withholding_method", "tax_allowance", "employee_tax_burden", "take_home_pay"),
}

FLOW_DOT = """digraph F { rankdir=LR; bgcolor=transparent; nodesep=.25; ranksep=.35;
node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=11 color="#b4b3ae" fillcolor="#ffffff"];
edge [color="#8a8984" arrowsize=.7 fontname="Helvetica" fontsize=9 fontcolor="#6b6a66"];
inc [label="Komponen penghasilan\\ngaji, tunjangan, lembur,\\nTHR, bonus" fillcolor="#f7f7f5"];
nat [label="Natura dan premi\\nyang dibayar perusahaan" fillcolor="#f7f7f5"];
gross [label="Bruto sebulan"];
ter [label="Tarif TER\\n(kategori dari PTKP)" fillcolor="#e8f1fc" color="#2a78d6"];
pm [label="PPh 21 masa\\nJan–Nov" penwidth=2 color="#2a78d6"];
ag [label="Bruto setahun"]; dj [label="− Biaya jabatan\\n− iuran pensiun"]; pt [label="− PTKP"];
pkp [label="PKP × Pasal 17\\n= PPh setahun" fillcolor="#fdeee7" color="#eb6834"];
fin [label="Masa terakhir\\n= PPh setahun − sudah dipotong" penwidth=2 color="#eb6834"];
dtp [label="Insentif DTP" style="rounded,dashed"]; thp [label="Gaji bersih" penwidth=2];
inc -> gross; nat -> gross; gross -> ter -> pm; gross -> ag [label="dijumlah"];
ag -> dj -> pt -> pkp -> fin; pm -> fin [label="sudah dipotong" style=dashed];
pm -> dtp [style=dashed]; pm -> thp; fin -> thp; }"""


def in_force(rec, t):
    if rec.kind == "fact" or rec.valid_from is None:
        return True
    return rec.valid_from <= t and (rec.valid_until is None or t <= rec.valid_until)


@st.cache_data
def snapshot(t):
    """Records in force at t: the latest version of every id. Returned as ids (cache friendly)."""
    best = {}
    for r in d.kb().records:
        if r.kind in ("rule", "parameter", "table", "constraint") and in_force(r, t):
            if r.id not in best or r.seq > best[r.id][1]:
                best[r.id] = (r.id, r.seq)
    return {seq for _, seq in best.values()}


def records_at(t):
    seqs = snapshot(t)
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


def tab_flow(recs):
    st.caption("Gambaran urutan perhitungan PPh 21 pegawai tetap. Pilih satu langkah untuk melihat aturan di baliknya.")
    st.graphviz_chart(FLOW_DOT, width="stretch")
    pick = st.segmented_control("Langkah", list(FLOW), default="Tarif TER", key="v_flow")
    if pick:
        found = [r for r in recs if r.kind == "rule" and r.produces in FLOW[pick] and not d.is_input_convention(r)]
        st.markdown(f"**{len(found)} aturan** untuk langkah *{pick}* pada tanggal yang dipilih:")
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
    st.title("Penampil knowledge base")
    g.md(f"Apa yang diketahui sistem tentang PPh 21: {g.term('aturan')}, {g.term('parameter', 'angka')}, dan "
         f"{g.term('tabel')}, masing-masing dengan {g.term('berlaku', 'tanggal berlaku')} dan {g.term('sumber')} pasalnya.")
    c1, c2 = st.columns([1, 3])
    t = c1.date_input("Tampilkan yang berlaku pada", d.TODAY, key="v_t", help=g.tip("berlaku"))
    recs = records_at(t)
    visible = [r for r in recs if not d.is_input_convention(r)]
    docs = {s.document for r in visible for s in r.source}
    with c2:
        m = st.columns(4)
        m[0].metric("Aturan", sum(r.kind == "rule" for r in visible), help=g.tip("aturan"))
        m[1].metric("Angka", sum(r.kind == "parameter" for r in visible), help=g.tip("parameter"))
        m[2].metric("Tabel", sum(r.kind == "table" for r in visible), help=g.tip("tabel"))
        m[3].metric("Dokumen sumber", len(docs), help=g.tip("sumber"))
    tabs = st.tabs(["Peta topik", "Alur perhitungan", "Angka dari waktu ke waktu", "Riwayat perubahan",
                    "Bandingkan dua tanggal", "Cari", "Kebijakan perusahaan"])
    with tabs[0]:
        tab_topics(recs, t)
    with tabs[1]:
        tab_flow(recs)
    with tabs[2]:
        tab_numbers()
    with tabs[3]:
        tab_history()
    with tabs[4]:
        tab_compare()
    with tabs[5]:
        tab_search(recs)
    with tabs[6]:
        tab_policies()
    ui.mock("Tampilan untuk ahli (graf lengkap, SPARQL, ekspor TriG) tetap ada di aplikasi sistem, di menu 'Mode audit'.")


@st.cache_resource
def _policies():
    import build_gold
    return [(u.doc.id, u.to_json()) for u in build_gold.collect_side() if u.kind == "policy"]


def tab_policies():
    g.md(f"{g.term('kebijakan perusahaan', 'Kebijakan perusahaan')} yang tersimpan: aturan perusahaan tentang THR, bonus, "
         "lembur, dan tunjangan. Dipakai bila dipilih di kalkulator.")
    pols = _policies()
    pick = st.selectbox("Kebijakan", [p[0] for p in pols], key="v_pol",
                        format_func=lambda i: f"{i} · {d.doc_title(i)}")
    j = dict(pols)[pick]
    for el in j.get("add", []):
        if el.get("kind") != "rule":
            continue
        src = (el.get("source") or [{}])[0]
        ui.html(f"<div class='rule company'>{ui.badge('perusahaan', 'orange')}<b>{d.fact_label(el['produces'])}</b><br>"
                f"<b>Rumus:</b> {d.readable(el['expression'])}<br><span class='muted'>Berlaku: {el.get('valid_from')}"
                f"{' s.d. ' + el['valid_until'] if el.get('valid_until') else ''} · {src.get('provision', '')}</span>"
                f"<div class='quote'>“{src.get('quote', '')}”</div></div>")
