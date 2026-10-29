"""Knowledge base management: inbox (PDF, TXT, JSON), review with approve / fix / reject, add a number or a rule,
change or revoke a rule, company policies, health of the knowledge base, version history, and the assistant.

Simulated in the session. The proposals in the inbox are real gold updates of the research (PMK 105/2025, the
2026 JP wage cap), so the change cards, the checks, and the before/after example are computed, not drawn.
"""
import json
from datetime import date, timedelta

import pandas as pd
import streamlit as st

import data as d
import glossary as g
import ui
from assistant import panel as assistant_panel

STEPS = ("Baca teks", "Cek relevansi", "Susun usulan", "Pemeriksaan otomatis", "Cek kesepakatan", "Review Anda")
CHECKS = (("Format dan struktur benar", "Bentuk usulan sesuai format knowledge base (G1)."),
          ("Kutipan, angka, dan tanggal ada di dokumen", "Setiap aturan menunjuk kalimat yang benar-benar ada di "
                                                         "dokumen, dan angkanya sama (G2)."),
          ("Tidak bertabrakan dengan aturan lain", "Tidak ada dua aturan wajib yang menghitung nilai yang sama pada "
                                                    "waktu yang sama (G3)."),
          ("Hitungan masa lalu tidak berubah", "Kasus sebelum tanggal berlaku dihitung ulang dan hasilnya tetap (G4)."),
          ("Setiap aturan berpengaruh", "Setiap bagian usulan mengubah paling tidak satu hasil (G5)."))
EXAMPLES = {  # event -> example employee for the before/after card
    "E11": ("Dewi, TK/0, tekstil rumah tangga (KLU 13921), gaji Rp6.500.000", 2026, "TK/0", "13921", 6_500_000),
    "E12": ("Budi, TK/0, gaji Rp12.000.000 (di atas batas upah JP)", 2026, "TK/0", "", 12_000_000),
}


@st.cache_resource
def _gold(event):
    import build_gold
    for u in build_gold.collect():
        if u.event_id == event:
            return u.to_json()
    return None


def _update_ids(event):
    ups = d.kb().updates
    for i, u in enumerate(ups):
        if u.event_id == event:
            return ups[i - 1].update_id, u.update_id
    return None, None


def _seed():
    s = st.session_state
    if "mg_inbox" in s:
        return
    s.mg_inbox = [
        {"id": "E11", "doc": "PMK-105-2025", "status": "review", "steps": 5, "received": date(2025, 12, 30)},
        {"id": "E12", "doc": "BPJSTK-JP-2026", "status": "review", "steps": 5, "received": date(2026, 2, 20)},
        {"id": "PKB-WIKA-2025", "doc": "PKB-WIKA-2025", "status": "abstain", "steps": 4, "received": date(2025, 3, 3)},
        {"id": "PMK-28-2024", "doc": "PMK-28-2024", "status": "irrelevant", "steps": 1, "received": date(2024, 3, 12)},
    ]
    s.mg_log = []          # approvals, rejections, manual changes of this session
    s.mg_drafts = []       # drafts from the forms and the assistant, waiting for review


STATUS = {"review": ("Siap direview", "blue"), "abstain": ("Sistem ragu", "yellow"),
          "irrelevant": ("Tidak relevan", "grey"), "reading": ("Sedang dibaca", "grey"),
          "approved": ("Disetujui", "green"), "rejected": ("Ditolak", "red")}


def _flow_for(item):
    out = []
    for i, label in enumerate(STEPS):
        if item["status"] == "irrelevant" and i == 1:
            out.append((label + ": tidak relevan", "skip"))
        elif item["status"] == "abstain" and i == 4:
            out.append((label + ": versi usulan tidak sepakat", "skip"))
        elif i < item["steps"]:
            out.append((label, "done"))
        elif i == item["steps"] and item["status"] in ("review", "reading"):
            out.append((label, "now"))
        elif item["status"] in ("approved", "rejected") and i == 5:
            out.append((STATUS[item["status"]][0], "done" if item["status"] == "approved" else "fail"))
        else:
            out.append((label, "todo"))
    return out


# ---------------------------------------------------------------- inbox
def tab_inbox():
    s = st.session_state
    with st.container(border=True):
        c1, c2 = st.columns([2, 1])
        with c1:
            up = st.file_uploader("Unggah dokumen baru: PDF, TXT, atau JSON", type=["pdf", "txt", "json"], key="mg_up",
                                  help="PDF dan TXT dibaca AI lalu diusulkan menjadi pembaruan. JSON adalah pembaruan "
                                       "yang sudah jadi, langsung diperiksa lalu masuk review.")
        with c2:
            kind = st.radio("Isi dokumen", ("Peraturan negara", "Kebijakan perusahaan"), key="mg_kind",
                            help=g.tip("regulasi") + "\n\n" + g.tip("kebijakan perusahaan"))
            issued = st.date_input("Tanggal terbit", d.TODAY, key="mg_issued")
        if up and st.button("Masukkan ke kotak masuk", type="primary", icon=":material/inbox:"):
            if up.name.lower().endswith(".json"):
                try:
                    delta = json.loads(up.getvalue())
                    ok = isinstance(delta, dict) and any(k in delta for k in ("add", "change", "remove"))
                except ValueError:
                    ok = False
                s.mg_inbox.insert(0, {"id": up.name, "doc": up.name, "status": "review" if ok else "rejected",
                                      "steps": 4 if ok else 0, "received": d.TODAY, "json": ok})
                (st.success if ok else st.error)("JSON dibaca sebagai pembaruan." if ok else
                                                 "JSON tidak berbentuk pembaruan (butuh add / change / remove).")
            else:
                s.mg_inbox.insert(0, {"id": up.name, "doc": up.name, "status": "reading", "steps": 1,
                                      "received": d.TODAY, "layer": kind})
                st.success("Masuk ke kotak masuk. Teks dibaca per halaman, termasuk hasil pindaian dan tabel.")
    ui.mock("Di sistem penuh tombol ini menjalankan alur akuisisi (± USD 0,1–1,9 per dokumen) di latar belakang dan "
            "memberi notifikasi saat usulan siap.")
    for item in s.mg_inbox:
        label, colour = STATUS[item["status"]]
        title = d.doc_title(item["doc"]) if item["doc"] in d.registry() else item["doc"]
        with st.container(border=True):
            ui.html(f"{ui.badge(label, colour)}<b>{title}</b><br><span class='muted'>Diterima "
                    f"{d.tgl(item['received'])} · {item['id']}</span>")
            ui.flow(_flow_for(item))
            if item["status"] == "review":
                if st.button("Buka review", key=f"open_{item['id']}", icon=":material/rate_review:"):
                    s.mg_open = item["id"]
                    st.toast("Buka tab Review di atas.")
            elif item["status"] == "abstain":
                g.md(f"Dua {g.term('versi usulan')} dari AI lolos pemeriksaan tetapi hasil hitungnya berbeda, jadi sistem "
                     f"{g.term('ragu')} dan tidak menebak. Dokumen perusahaan (PKB) memang paling sulit: "
                     "di penelitian, tidak ada PKB yang berhasil diusulkan benar oleh AI. Tulis aturannya di tab "
                     "**Kebijakan perusahaan** atau minta bantuan asisten.")
            elif item["status"] == "irrelevant":
                g.md(f"AI menilai dokumen ini tidak {g.term('relevan')} untuk PPh 21 pegawai tetap (mis. hanya mengatur "
                     "wilayah atau pajak lain). Tidak ada yang berubah.")
                st.button("Tetap proses dokumen ini", key=f"force_{item['id']}", icon=":material/replay:")
            elif item["status"] == "reading":
                if st.button("Lanjutkan (simulasi)", key=f"go_{item['id']}"):
                    item["steps"], item["status"] = 5, "review"
                    st.rerun()


# ---------------------------------------------------------------- review
def _prev_version(rec_id, before_kb):
    found = [r for r in before_kb.records if r.id == rec_id]
    return max(found, key=lambda r: r.seq) if found else None


def _el_card(el, change, before_kb):
    kind = el.get("kind")
    src = (el.get("source") or [{}])[0]
    quote = f"<div class='quote'>“{src.get('quote', '')}” · {src.get('provision', '')} hlm. {src.get('page', '-')} ✓</div>"
    iso = lambda x: d.tgl(date.fromisoformat(str(x))) if x else "-"  # noqa: E731
    period = f"berlaku {iso(el.get('valid_from'))}" + (f" s.d. {iso(el['valid_until'])}" if el.get("valid_until") else "")
    if kind == "parameter":
        title = (el.get("label_id") or el.get("name", "")).capitalize()
        old = _prev_version(el["id"], before_kb) if change else None
        prev = [r for r in before_kb.records if r.kind == "parameter" and r.name == el.get("name")]
        old = old or (max(prev, key=lambda r: r.valid_from) if prev else None)
        val = el.get("value")
        new = d.money(int(val)) if el.get("value_type") == "money" else str(val)
        oldv = (d.money(old.value) if old and old.value_type == "money" else str(old.value)) if old else None
        body = (f"<span class='diff-old'>{oldv}</span> → " if oldv else "") + f"<span class='diff-new'>{new}</span>"
        what = "Angka diperbarui" if oldv else "Angka baru"
    elif kind == "rule":
        title = d.fact_label(el["produces"])
        old = _prev_version(el["id"], before_kb) if change else None
        body = f"<b>Rumus:</b> {d.readable(el['expression'])}"
        if el.get("condition"):
            body = f"<b>Jika:</b> {d.readable(el['condition'])}<br>" + body
        if old and d.expr_text(old.expression) == el["expression"] and str(old.valid_until) != str(el.get("valid_until")):
            what = "Masa berlaku diubah"
            body += (f"<br><span class='diff-old'>s.d. {d.tgl(old.valid_until) if old.valid_until else 'tanpa batas'}</span> → "
                     f"<span class='diff-new'>s.d. {iso(el.get('valid_until')) if el.get('valid_until') else 'tanpa batas'}</span>")
        elif old:
            what = "Aturan diubah"
            body = f"<span class='diff-old'>{d.readable(old.expression)}</span><br>" + body
        else:
            what = "Aturan baru"
    elif kind == "table":
        title, what = (el.get("label_id") or el.get("name", "")).capitalize(), "Tabel " + ("diubah" if change else "baru")
        body = f"{len(el.get('rows') or [])} baris" + (" dari lampiran" if el.get("rows_ref") else "")
    elif kind == "fact":
        title, what, body = (el.get("label_id") or el["id"]).capitalize(), "Istilah baru", el.get("label", "")
    else:
        title, what, body = el.get("id", ""), kind, ""
    ui.html(f"<div class='rule'>{ui.badge(what, 'green' if 'baru' in what else 'blue')}<b>{title}</b> "
            f"<span class='muted'>· {period if kind != 'fact' else ''}</span><br>{body}{quote}</div>")


def _example(event, before, after):
    ex = EXAMPLES.get(event)
    if not ex:
        return
    label, year, ptkp, klu, salary = ex
    case = {"case_id": "contoh", "tax_year": year, "method": "gross",
            "employee": {"ptkp_status": ptkp, "tax_id_valid": True},
            "employer": {"klu": klu or None, "jkk_risk_group": "low"},
            "employment": {"start_month": 1, "end_month": 12},
            "periods": [{"month": m, "income": {"base_salary": salary}} for m in range(1, 13)]}
    from pph21kbs.engine import evaluate_case
    rows = []
    for name, kb in (("Sebelum", d.kb().until(before)), ("Sesudah", d.kb().until(after))):
        r = evaluate_case(kb, case, d.TODAY)
        p = r.periods[1]
        rows.append({"": name, "PPh 21 Januari": d.money(p.get("pph21_due")), "DTP Januari": d.money(p.get("pph21_dtp")),
                     "Iuran JP pegawai": d.money(p.get("jp_employee")), "Gaji bersih Januari": d.money(p.get("take_home_pay")),
                     "PPh setahun": d.money(r.year.get("annual_pph21"))})
    st.markdown(f"**Contoh dampak** · {label}, tahun {year}")
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def tab_review():
    s = st.session_state
    items = [i for i in s.mg_inbox if i["status"] == "review"]
    drafts = s.mg_drafts
    if not items and not drafts:
        st.success("Tidak ada yang menunggu review.")
        return
    options = [i["id"] for i in items] + [f"draf:{k}" for k in range(len(drafts))]
    names = {i["id"]: (d.doc_title(i["doc"]) if i["doc"] in d.registry() else i["doc"]) for i in items}
    names.update({f"draf:{k}": f"Draf: {x['title']}" for k, x in enumerate(drafts)})
    default = options.index(s.get("mg_open")) if s.get("mg_open") in options else 0
    pick = st.selectbox("Yang direview", options, index=default, format_func=names.get, key="mg_pick")
    if pick.startswith("draf:"):
        _review_draft(int(pick.split(":")[1]))
        return
    item = next(i for i in items if i["id"] == pick)
    delta = _gold(item["id"]) if not item.get("json") else None
    if delta is None:
        st.info("Pembaruan dari JSON atau dokumen unggahan: tampilannya sama seperti contoh PMK 105/2025.")
        ui.mock("Isi usulan unggahan disimulasikan.")
        return
    before, after = _update_ids(item["id"])
    before_kb = d.kb().until(before)
    n_add, n_chg, n_rm = len(delta["add"]), len(delta["change"]), len(delta["remove"])
    ui.flow(_flow_for(item))
    g.md(f"**{names[pick]}**  \nAI mengusulkan {n_add} tambahan, {n_chg} perubahan, dan {n_rm} pencabutan. "
         f"Semua {g.term('pemeriksaan', 'pemeriksaan otomatis')} lulus dan sebagian besar {g.term('versi usulan')} "
         f"{g.term('kesepakatan', 'sepakat')}.")
    ui.mock("Isi usulan di mockup ini diambil dari pembaruan emas penelitian, supaya kartu dan contoh dampaknya nyata.")
    left, right = st.columns([1.6, 1], gap="large")
    with left:
        st.markdown("**Perubahan yang diusulkan**")
        for el in delta["change"]:
            _el_card(el, True, before_kb)
        for el in delta["add"]:
            _el_card(el, False, before_kb)
        for el in delta["remove"]:
            ui.html(f"<div class='rule old'>{ui.badge('Dicabut', 'red')}<b>{el}</b></div>")
    with right:
        st.markdown("**Pemeriksaan otomatis**")
        for name, expl in CHECKS:
            st.markdown(f":material/check_circle: {name}", help=expl)
        st.markdown("**Kebijakan perusahaan yang mungkin terdampak**")
        g.md(f"<span class='muted'>{g.term('dampak', 'Apa ini?')}</span>")
        st.markdown("- SP04 · tunjangan pajak membaca *PPh 21 terutang*\n- SP11 · gross-up membaca *PPh 21 terutang*")
        ui.mock("Daftar dampak memakai detektor penelitian (RQ4); di sini contoh.")
    _example(item["id"], before, after)
    st.divider()
    c1, c2, c3 = st.columns(3)
    note = st.text_input("Catatan review (opsional)", key=f"mg_note_{pick}")
    if c1.button("Setujui dan terapkan", type="primary", icon=":material/check:", width="stretch", key=f"ok_{pick}"):
        item["status"] = "approved"
        s.mg_log.insert(0, {"when": d.TODAY, "what": f"Disetujui: {names[pick]}", "note": note})
        st.rerun()
    if c2.button("Perbaiki dulu", icon=":material/edit:", width="stretch", key=f"fix_{pick}"):
        s[f"mg_fixing_{pick}"] = True
    if c3.button("Tolak", icon=":material/close:", width="stretch", key=f"no_{pick}"):
        item["status"] = "rejected"
        s.mg_log.insert(0, {"when": d.TODAY, "what": f"Ditolak: {names[pick]}", "note": note})
        st.rerun()
    if s.get(f"mg_fixing_{pick}"):
        st.markdown("**Perbaiki usulan**: ubah sel lalu jalankan pemeriksaan lagi.")
        rows = [{"Unsur": el.get("id"), "Jenis": el.get("kind"), "Nilai / rumus": str(el.get("value", el.get("expression", ""))),
                 "Berlaku mulai": el.get("valid_from"), "Berlaku sampai": el.get("valid_until")}
                for el in delta["change"] + delta["add"] if el.get("kind") != "fact"]
        st.data_editor(pd.DataFrame(rows), hide_index=True, width="stretch", key=f"mg_edit_{pick}", disabled=["Unsur", "Jenis"])
        if st.button("Periksa ulang dan bandingkan hasil", icon=":material/fact_check:"):
            st.success("Pemeriksaan lulus. Contoh dampak dihitung ulang.")
            ui.mock("Pemeriksaan ulang disimulasikan.")


def _review_draft(k):
    s = st.session_state
    dr = s.mg_drafts[k]
    st.markdown(f"**{dr['title']}**")
    g.md(dr["html"])
    for name, expl in CHECKS:
        st.markdown(f":material/check_circle: {name}", help=expl)
    c1, c2 = st.columns(2)
    if c1.button("Setujui", type="primary", icon=":material/check:", key=f"dok_{k}", width="stretch"):
        s.mg_log.insert(0, {"when": d.TODAY, "what": "Disetujui: " + dr["title"], "note": ""})
        s.mg_drafts.pop(k)
        st.rerun()
    if c2.button("Buang draf", icon=":material/delete:", key=f"dno_{k}", width="stretch"):
        s.mg_drafts.pop(k)
        st.rerun()


# ---------------------------------------------------------------- add
def _source_inputs(key):
    c1, c2 = st.columns([1, 1])
    doc = c1.text_input("Dokumen dasar", placeholder="mis. PMK 168/2023", key=f"{key}_doc")
    prov = c2.text_input("Pasal", placeholder="mis. Pasal 2 ayat (1)", key=f"{key}_prov")
    quote = st.text_area("Kutipan kalimat dari dokumen", key=f"{key}_quote", height=68, help=g.tip("kutipan"))
    return doc, prov, quote


def tab_add():
    s = st.session_state
    what = st.segmented_control("Apa yang ingin ditambahkan?", ["Angka baru", "Aturan baru", "Tabel baru"],
                                default="Angka baru", key="mg_add_kind")
    if what == "Angka baru":
        g.md(f"Paling sering terjadi: peraturan hanya mengganti satu {g.term('parameter', 'angka')} (batas upah, tarif, "
             "plafon). Pilih angkanya, isi nilai baru dan tanggal berlaku; nilai lama otomatis berakhir sehari sebelumnya.")
        ps = d.params()
        name = st.selectbox("Angka", sorted(ps, key=lambda n: d.fact_label(n)), format_func=d.fact_label, key="mg_p")
        cur = max((r for r in d.kb().records if r.kind == "parameter" and r.name == name), key=lambda r: r.valid_from)
        curv = d.money(cur.value) if cur.value_type == "money" else (d.pct(cur.value) if cur.value_type == "rate"
                                                                     else str(cur.value))
        st.caption(f"Nilai sekarang: **{curv}**, berlaku sejak {d.tgl(cur.valid_from)} "
                   f"({d.short_doc(cur.source[0].document) if cur.source else '-'})")
        c1, c2 = st.columns(2)
        new = c1.text_input("Nilai baru", key="mg_pv", placeholder="mis. 11.086.300 atau 1%")
        start = c2.date_input("Berlaku mulai", date(d.TODAY.year + 1, 1, 1), key="mg_pf")
        doc, prov, quote = _source_inputs("mg_ps")
        if new:
            sentence = (f"<b>{d.fact_label(name)}</b>: <span class='diff-old'>{curv}</span> → "
                        f"<span class='diff-new'>{new}</span> mulai {d.tgl(start)}; nilai lama berlaku sampai "
                        f"{d.tgl(start - timedelta(days=1))}. Sumber: {doc or '?'} {prov}.")
            ui.html(f"<div class='rule'>{sentence}</div>")
            if st.button("Kirim ke review", type="primary", icon=":material/send:", key="mg_p_send"):
                s.mg_drafts.append({"title": f"{d.fact_label(name)} → {new}", "html": sentence})
                st.success("Masuk ke tab Review.")
    elif what == "Aturan baru":
        facts = sorted(d.facts(), key=d.fact_label)
        c1, c2 = st.columns(2)
        produces = c1.selectbox("Nilai yang dihitung", facts, format_func=d.fact_label, key="mg_r_f",
                                help="Aturan selalu menghitung satu nilai.")
        layer = c2.radio("Berlaku untuk", ("Peraturan negara", "Kebijakan perusahaan"), horizontal=True, key="mg_r_l",
                         help=g.tip("regulasi") + "\n\n" + g.tip("kebijakan perusahaan"))
        cond = st.text_input("Berlaku jika (opsional)", key="mg_r_c", placeholder="mis. gross_income > 10000000")
        expr = st.text_input("Rumus", key="mg_r_e", placeholder="mis. min(gross_income * 5 / 100, 500000)")
        with st.expander("Nama nilai yang bisa dipakai di rumus"):
            st.dataframe(pd.DataFrame([{"Nama": f, "Arti": d.fact_label(f)} for f in facts]), hide_index=True,
                         height=220, width="stretch")
        c1, c2 = st.columns(2)
        start = c1.date_input("Berlaku mulai", date(d.TODAY.year + 1, 1, 1), key="mg_r_s")
        end = c2.date_input("Berlaku sampai (kosongkan bila tanpa batas)", None, key="mg_r_u")
        doc, prov, quote = _source_inputs("mg_rs")
        if expr:
            sentence = (f"<b>{d.fact_label(produces)}</b> = {d.readable(expr)}"
                        + (f" <i>jika {d.readable(cond)}</i>" if cond else "")
                        + f"<br><span class='muted'>{layer} · berlaku {d.tgl(start)}"
                          f"{' s.d. ' + d.tgl(end) if end else ''} · {doc} {prov}</span>")
            ui.html(f"<div class='rule{' company' if layer != 'Peraturan negara' else ''}'>{sentence}</div>")
            st.caption("Asisten bisa menuliskan rumus dari kalimat biasa, mis. \"biaya jabatan 5% paling banyak 600 ribu "
                       "sebulan\".")
            if st.button("Kirim ke review", type="primary", icon=":material/send:", key="mg_r_send"):
                s.mg_drafts.append({"title": f"Aturan baru: {d.fact_label(produces)}", "html": sentence})
                st.success("Masuk ke tab Review.")
    else:
        st.caption("Tabel (mis. tarif TER atau PTKP) biasanya terlalu panjang untuk diketik: unggah CSV atau minta AI "
                   "mengambilnya dari lampiran PDF.")
        st.file_uploader("CSV tabel", type="csv", key="mg_t_up")
        ui.mock("Pratinjau tabel dan pembandingan dengan versi lama.")


# ---------------------------------------------------------------- change or revoke
def tab_change():
    s = st.session_state
    action = st.segmented_control("Tindakan", ["Ubah aturan", "Cabut aturan"], default="Cabut aturan", key="mg_ch_act")
    rules = {}
    for r in d.kb().view(d.TODAY).rules.values():
        if not d.is_input_convention(r):
            rules[r.id] = r
    preset = s.pop("mg_revoke_target", None)
    ids = sorted(rules, key=lambda i: d.fact_label(rules[i].produces))
    idx = ids.index(preset) if preset in ids else 0
    rid = st.selectbox("Aturan", ids, index=idx, key="mg_ch_rule",
                       format_func=lambda i: f"{d.fact_label(rules[i].produces)} · {d.short_doc(rules[i].source[0].document)}"
                       f" {rules[i].source[0].provision}" if rules[i].source else i)
    r = rules[rid]
    src = r.source[0] if r.source else None
    ui.html(f"<div class='rule'><b>{d.fact_label(r.produces)}</b><br><b>Rumus:</b> {d.readable(r.expression)}<br>"
            f"<span class='muted'>Berlaku {d.tgl(r.valid_from)}{' s.d. ' + d.tgl(r.valid_until) if r.valid_until else ''}"
            f" · {d.short_doc(src.document) if src else ''} {src.provision if src else ''}</span></div>")
    if action == "Cabut aturan":
        g.md(f"{g.term('pencabutan', 'Mencabut')} berarti memberi tanggal akhir berlaku. Aturannya tidak dihapus, jadi "
             "perhitungan bulan-bulan sebelumnya tetap sama.")
        end = st.date_input("Tidak berlaku lagi sesudah", date(d.TODAY.year, 12, 31), key="mg_ch_end")
        users = sorted({x.id for x in rules.values() if r.produces in d.expr_text(x.expression) + d.expr_text(x.condition or "")})
        others = [x for x in d.kb().records if x.kind == "rule" and x.produces == r.produces and x.id != r.id
                  and (x.valid_until is None or x.valid_until > end)]
        if not others:
            st.warning(f"Sesudah {d.tgl(end)} tidak ada aturan lain yang menghitung *{d.fact_label(r.produces)}*. "
                       f"{len(users)} aturan lain memakai nilai ini, jadi perhitungan sesudah tanggal itu akan gagal. "
                       "Tambahkan aturan pengganti, atau pastikan peraturan memang menghapusnya.",
                       icon=":material/warning:")
        else:
            st.info(f"Sesudah tanggal itu *{d.fact_label(r.produces)}* dihitung oleh {len(others)} aturan lain.",
                    icon=":material/info:")
        doc, prov, quote = _source_inputs("mg_cs")
        if st.button("Kirim pencabutan ke review", type="primary", icon=":material/send:"):
            s.mg_drafts.append({"title": f"Cabut: {d.fact_label(r.produces)} sesudah {d.tgl(end)}",
                                "html": f"<div class='rule old'>{ui.badge('Dicabut', 'red')}<b>{d.fact_label(r.produces)}"
                                        f"</b> berlaku sampai {d.tgl(end)}. Dasar: {doc} {prov}.</div>"})
            st.success("Masuk ke tab Review.")
    else:
        g.md("Mengubah aturan membuat **versi baru** mulai tanggal tertentu; versi lama tetap dipakai untuk bulan-bulan "
             "sebelumnya.")
        expr = st.text_input("Rumus baru", d.expr_text(r.expression), key="mg_ch_expr")
        start = st.date_input("Berlaku mulai", date(d.TODAY.year + 1, 1, 1), key="mg_ch_start")
        doc, prov, quote = _source_inputs("mg_cu")
        if expr != d.expr_text(r.expression):
            ui.html(f"<div class='rule'><span class='diff-old'>{d.readable(r.expression)}</span><br>"
                    f"<span class='diff-new'>{d.readable(expr)}</span><br><span class='muted'>mulai {d.tgl(start)}</span></div>")
            if st.button("Kirim perubahan ke review", type="primary", icon=":material/send:"):
                s.mg_drafts.append({"title": f"Ubah: {d.fact_label(r.produces)}",
                                    "html": f"<div class='rule'>{d.readable(expr)} mulai {d.tgl(start)}</div>"})
                st.success("Masuk ke tab Review.")


# ---------------------------------------------------------------- company policy
TEMPLATES = {
    "THR": ("thr", "THR = {n} × gaji pokok, dibayar bulan {m}", ("Kelipatan gaji", 1.0), "Bulan dibayar"),
    "Bonus tahunan": ("bonus", "Bonus = {n} × gaji pokok, dibayar bulan {m}", ("Kelipatan gaji", 1.0), "Bulan dibayar"),
    "Uang makan dan transport": ("other_regular_income", "Rp{n} × hari hadir", ("Rupiah per hari", 60000.0), None),
    "Tunjangan pajak (gross-up)": ("tax_allowance", "Perusahaan menanggung PPh 21 lewat tunjangan pajak", None, None),
}


def tab_policy():
    s = st.session_state
    g.md(f"Aturan {g.term('kebijakan perusahaan', 'perusahaan sendiri')}: dari PKB atau peraturan perusahaan. Mulai dari "
         "contoh, lalu sesuaikan. Aturan perusahaan tidak boleh bertentangan dengan regulasi; sistem memeriksanya.")
    c1, c2 = st.columns(2)
    company = c1.text_input("Nama perusahaan / kebijakan", "PT Contoh Sejahtera · PP 2026", key="mg_pol_name")
    tpl = c2.selectbox("Contoh aturan", list(TEMPLATES), key="mg_pol_tpl")
    fact, text, num, month_label = TEMPLATES[tpl]
    n = st.number_input(num[0], value=num[1], key=f"mg_pol_n_{tpl}") if num else None
    m = st.selectbox(month_label, range(1, 13), index=2, format_func=lambda x: d.MONTHS[x - 1],
                     key=f"mg_pol_m_{tpl}") if month_label else None
    c1, c2 = st.columns(2)
    start = c1.date_input("Berlaku mulai", date(d.TODAY.year, 1, 1), key="mg_pol_s")
    c2.date_input("Berlaku sampai", date(d.TODAY.year + 1, 12, 31), key="mg_pol_u")
    _source_inputs("mg_pol_src")
    sentence = text.format(n=f"{n:g}" if n is not None else "", m=d.MONTHS[m - 1] if m else "")
    ui.html(f"<div class='rule company'>{ui.badge('perusahaan', 'orange')}<b>{d.fact_label(fact)}</b>: {sentence}"
            f"<br><span class='muted'>{company} · mulai {d.tgl(start)}</span></div>")
    if st.button("Kirim ke review", type="primary", icon=":material/send:", key="mg_pol_send"):
        s.mg_drafts.append({"title": f"{company}: {tpl}", "html": f"<div class='rule company'>{sentence}</div>"})
        st.success("Masuk ke tab Review.")


# ---------------------------------------------------------------- health
@st.cache_data
def _health(today):
    out = []
    by_name = {}
    for r in d.kb().records:
        if r.kind == "parameter":
            by_name.setdefault(r.name, []).append(r)
    for name, vs in by_name.items():
        years = sorted({v.valid_from.year for v in vs})
        if len(years) >= 3 and years[-1] - years[-2] == 1 and years[-1] <= today.year:
            out.append(("warn", f"{d.fact_label(name)} biasanya berganti tiap tahun; nilai {today.year + 1} belum ada.",
                        f"Terakhir: {d.short_doc(vs[-1].source[0].document)}"))
    ending = {}
    for r in d.kb().view(today).rules.values():
        if r.valid_until and today <= r.valid_until <= today + timedelta(days=120):
            ending.setdefault((r.valid_until, d.topic_of(r)), []).append(r)
    for (until, topic), rs in sorted(ending.items()):
        docs = sorted({d.short_doc(r.source[0].document) for r in rs if r.source})
        out.append(("info", f"{topic}: {len(rs)} aturan berakhir {d.tgl(until)}.",
                    f"Dasar: {', '.join(docs)}. Bila diperpanjang, unggah peraturan barunya ke kotak masuk."))
    from pph21kbs import static
    for f in static.check(d.kb(), today).findings[:10]:
        out.append(("error" if f.severity == "error" else "warn", f"{f.kind}: {f.detail}", ", ".join(f.ids)))
    return out


def tab_health():
    g.md("Pemeriksaan rutin atas isi knowledge base, supaya Anda tahu lebih dulu sebelum perhitungan salah.")
    items = _health(d.TODAY)
    seen = set()
    for level, title, detail in items:
        if title in seen:
            continue
        seen.add(title)
        icon = {"warn": ":material/schedule:", "info": ":material/event:", "error": ":material/error:"}[level]
        (st.warning if level == "warn" else st.error if level == "error" else st.info)(f"**{title}**  \n{detail}", icon=icon)
    if not items:
        st.success("Tidak ada temuan.")


# ---------------------------------------------------------------- history
def tab_history():
    s = st.session_state
    for e in s.mg_log:
        with st.container(border=True):
            st.markdown(f"**{e['what']}** · {d.tgl(e['when'])} · sesi ini" + (f"  \n_{e['note']}_" if e["note"] else ""))
            st.button("Batalkan", key=f"undo_{e['what']}", icon=":material/undo:")
    for i, u in enumerate(reversed(d.kb().updates)):
        if i >= 15:
            st.caption(f"... dan {len(d.kb().updates) - 15} versi lebih lama.")
            break
        n = len(d.kb().updates) - i
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"**v{n}** · {d.tgl(u.recorded_on)} · {d.doc_title(u.document)}")
        c2.button("Kembalikan ke sini", key=f"rb_{u.update_id}", icon=":material/history:", width="stretch",
                  help="Membuat versi baru yang sama dengan versi ini. Riwayat tidak dihapus.")
    ui.mock("Kembalikan dan Batalkan disimulasikan.")


def show():
    _seed()
    s = st.session_state
    st.title("Manajemen knowledge base")
    g.md(f"Tambah, ubah, cabut, dan {g.term('review')} pengetahuan sistem. Dokumen baru dibaca AI menjadi "
         f"{g.term('usulan')}; tidak ada yang berubah sebelum Anda setujui. Butuh bantuan? "
         f"{g.term('asisten', 'Asisten KB')} ada di panel kiri.")
    n_review = sum(i["status"] == "review" for i in s.mg_inbox) + len(s.mg_drafts)
    tabs = st.tabs(["Kotak masuk", f"Review ({n_review})", "Tambah", "Ubah atau cabut", "Kebijakan perusahaan",
                    "Cek KB", "Riwayat"])
    with tabs[0]:
        tab_inbox()
    with tabs[1]:
        tab_review()
    with tabs[2]:
        tab_add()
    with tabs[3]:
        tab_change()
    with tabs[4]:
        tab_policy()
    with tabs[5]:
        tab_health()
    with tabs[6]:
        tab_history()
    with st.sidebar:
        assistant_panel()
