"""Knowledge base management: new documents with the AI's real work from the research runs, review (approve, edit,
ask the AI to fix with your notes, reject), add / change / revoke by hand or by asking the AI, company policies,
knowledge base check, and version history. Everything is kept in the demo workspace and undone by Reset.
"""
import json
from datetime import date, timedelta

import pandas as pd
import streamlit as st

import assistant
import data as d
import demo
import drafts
import glossary as g
import inputs
import ui
from pph21kbs import static
from pph21kbs.kb import apply_delta
from pph21kbs.kb.delta import validate_delta_json
import employee as emp

STATUS = {"review": ("Siap direview", "blue"), "ragu": ("Sistem ragu", "yellow"), "tidak relevan": ("Tidak relevan", "grey"),
          "disetujui": ("Disetujui", "green"), "ditolak": ("Ditolak", "red"), "menunggu AI": ("Menunggu AI", "grey")}
GATES = {"G1": "Format dan struktur benar", "G2": "Kutipan, angka, dan tanggal ada di dokumen",
         "G3": "Tidak bertabrakan dengan aturan lain", "G4": "Hitungan masa lalu tidak berubah",
         "G5": "Setiap bagian usulan berpengaruh"}


def _title(pid):
    p = demo.PENDING_BY_ID.get(pid)
    return d.doc_title(p["doc"]) if p else pid


# ---------------------------------------------------------------- new documents
def _ai_steps(pid, stat):
    r = demo.run(pid)
    n = len(r.get("candidates", [])) if r else 0
    passed = sum(1 for c in (r or {}).get("candidates", []) if c.get("passed"))
    groups = (r or {}).get("groups") or []
    steps = [("Baca teks", "done")]
    if stat == "tidak relevan":
        return steps + [("Cek relevan: tidak relevan", "skip")]
    steps += [("Cek relevan", "done"), (f"Susun {n} versi usulan", "done"), (f"Pemeriksaan: {passed}/{n} lolos", "done")]
    if stat == "ragu":
        return steps + [(f"Cek kesepakatan: {len(groups)} kelompok berbeda", "skip")]
    steps.append((f"Cek kesepakatan: {max(map(len, groups)) if groups else 0}/{passed} sama", "done"))
    label = {"disetujui": ("Disetujui", "done"), "ditolak": ("Ditolak", "fail")}.get(stat, ("Review Anda", "now"))
    return steps + [label]


def _ai_detail(pid):
    r = demo.run(pid)
    rel = (r.get("relevance") or {}).get("output") or {}
    st.markdown(f"**Alasan AI soal relevansi** (ditulis AI dalam bahasa Inggris): _{rel.get('reason', '-')}_")
    sel = r.get("selection") or {}
    st.caption("Bagian dokumen yang dibaca: " + ", ".join(f"{k} ({v.get('tokens', 0):,} token)".replace(",", ".")
                                                          for k, v in sel.items()))
    rows = []
    for c in r.get("candidates", []):
        log = c.get("gate_log") or {}
        rows.append({"Versi": c.get("n"), "Lolos": "ya" if c.get("passed") else "tidak",
                     "Diperbaiki otomatis": "ya" if c.get("repaired") else "-",
                     **{GATES[k]: ("✓" if log.get(k) == "pass" else "✗" if log.get(k) else "-") for k in GATES},
                     "Catatan": (c.get("error") or "")[:80]})
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    groups = r.get("groups") or []
    if groups:
        st.caption("Versi yang hasil hitungnya sama: " + " · ".join("versi " + ", ".join(map(str, g_)) for g_ in groups)
                   + f". Dipilih: versi {r.get('selected') or '-'}. Biaya AI: USD {r.get('cost_usd', 0):.2f}.")


def tab_documents():
    s = demo.load()
    with st.container(border=True):
        c1, c2 = st.columns([2, 1])
        up = c1.file_uploader("Unggah dokumen: PDF, TXT, atau JSON", type=["pdf", "txt", "json"], key="mg_up",
                              help="PDF/TXT dibaca AI lalu diusulkan menjadi pembaruan. JSON adalah pembaruan yang "
                                   "sudah jadi: langsung diperiksa lalu masuk Review.")
        kind = c2.radio("Isi dokumen", ("Peraturan negara", "Kebijakan perusahaan"), key="mg_kind",
                        help=g.tip("regulasi") + "\n\n" + g.tip("kebijakan perusahaan"))
        if up and st.button("Proses dokumen", type="primary", icon=":material/play_arrow:"):
            if up.name.lower().endswith(".json"):
                try:
                    delta = json.loads(up.getvalue())
                    validate_delta_json(delta)
                    demo.add_draft(delta["delta_id"], (delta.get("document") or {}).get("title", up.name), delta,
                                   "unggah JSON")
                    st.success("Pembaruan JSON valid dan masuk ke Review.")
                except Exception as e:  # noqa: BLE001
                    st.error(f"JSON tidak bisa dipakai: {str(e)[:250]}")
            else:
                s["uploads"].append({"name": up.name, "kind": kind, "when": str(demo.TODAY)})
                demo.save(s)
                st.success("Dokumen tersimpan dan menunggu AI.")
    for u in s["uploads"]:
        with st.container(border=True):
            ui.html(f"{ui.badge('Menunggu AI', 'grey')}<b>{u['name']}</b> <span class='muted'>· {u['kind']}</span>")
            c1, c2 = st.columns([2, 1])
            model = c1.selectbox("Model AI", list(assistant.MODELS), key=f"mg_model_{u['name']}",
                                 format_func=lambda m: f"{m} · {assistant.MODELS[m]}")
            c2.button("Jalankan AI", key=f"mg_run_{u['name']}", icon=":material/smart_toy:", disabled=True,
                      help="Mockup: AI tidak dijalankan di demo ini. Delapan dokumen di bawah memakai hasil AI asli "
                           "dari penelitian.")
            st.caption(f"Perkiraan biaya {model}: USD 0,1–1,9 per dokumen (data penelitian). Model selain "
                       "claude-opus-5-5 tidak diuji di penelitian.")
    presenter = st.toggle("Tampilkan catatan untuk presenter", key="mg_presenter",
                          help="Menampilkan hasil penelitian untuk setiap dokumen. Matikan saat demo agar penonton "
                               "menilai sendiri.")
    for p in demo.PENDING:
        stat = demo.status(p["id"], s)
        label, colour = STATUS.get(stat, (stat, "grey"))
        with st.container(border=True):
            ui.html(f"{ui.badge(label, colour)}{ui.badge('peraturan negara' if p['kind'] == 'regulasi' else 'kebijakan perusahaan', 'blue' if p['kind'] == 'regulasi' else 'orange')}"
                    f"<b>{_title(p['id'])}</b>")
            ui.flow(_ai_steps(p["id"], stat))
            if presenter:
                st.caption(f"Catatan presenter · hasil di penelitian: **{p['research']}**. {p['why']}")
            c1, c2, c3 = st.columns(3)
            if stat == "review" and c1.button("Review", key=f"rv_{p['id']}", icon=":material/rate_review:", width="stretch"):
                st.session_state.mg_open = p["id"]
                st.toast("Buka tab Review.")
            if stat == "ragu":
                g.md(f"Versi-versi usulan AI tidak sepakat, jadi sistem {g.term('ragu')} dan tidak menebak.")
                if c1.button("Minta AI mengerjakan ulang", key=f"redo_{p['id']}", icon=":material/smart_toy:", width="stretch"):
                    ref = demo.gold_delta(p["id"])
                    demo.add_draft(p["id"], _title(p["id"]), ref, "AI mengerjakan ulang (simulasi)")
                    st.session_state.mg_open = p["id"]
                    st.rerun()
                if c2.button("Kerjakan manual", key=f"man_{p['id']}", icon=":material/edit:", width="stretch"):
                    st.toast("Tulis aturannya di tab Kebijakan perusahaan atau Tambah, ubah, cabut.")
            if stat == "tidak relevan":
                g.md(f"AI menilai dokumen ini tidak {g.term('relevan')} untuk PPh 21 pegawai tetap. Tidak ada yang berubah.")
            if stat in ("review", "ragu", "tidak relevan", "disetujui", "ditolak"):
                with st.expander("Lihat pekerjaan AI"):
                    _ai_detail(p["id"])


# ---------------------------------------------------------------- review
def _prev(rec_id, kb):
    found = [r for r in kb.records if r.id == rec_id]
    return max(found, key=lambda r: r.seq) if found else None


def _iso(x):
    return d.tgl(date.fromisoformat(str(x))) if x else "-"


def card(el, kb):
    kind = el.get("kind")
    src = (el.get("source") or [{}])[0]
    quote = f"<div class='quote'>“{src.get('quote', '')}” · {src.get('provision', '')}</div>"
    period = f"berlaku {_iso(el.get('valid_from'))}" + (f" s.d. {_iso(el['valid_until'])}" if el.get("valid_until") else "")
    old = _prev(el["id"], kb)
    if kind == "parameter":
        title = (el.get("label_id") or d.fact_label(el.get("name", ""))).capitalize()
        same = [r for r in kb.records if r.kind == "parameter" and r.name == el.get("name") and r.id != el["id"]]
        ref = old or (max(same, key=lambda r: r.valid_from) if same else None)
        fmt = lambda v, t: d.money(int(float(v))) if t == "money" else (d.pct(float(v)) if t == "rate" else str(v))  # noqa: E731
        new = fmt(el.get("value"), el.get("value_type"))
        oldv = fmt(ref.value, ref.value_type) if ref else None
        body = (f"<span class='diff-old'>{oldv}</span> → " if oldv and oldv != new else "") + f"<span class='diff-new'>{new}</span>"
        what = "Angka diubah" if old else ("Angka baru" if not oldv else "Angka baru (nilai lama berakhir)")
    elif kind == "rule":
        title = d.fact_label(el["produces"])
        body = f"<b>Rumus:</b> {d.readable(el['expression'])}"
        if el.get("condition"):
            body = f"<b>Jika:</b> {d.readable(el['condition'])}<br>" + body
        if old and d.expr_text(old.expression) == el["expression"]:
            what = "Masa berlaku diubah"
            body += (f"<br><span class='diff-old'>s.d. {d.tgl(old.valid_until) if old.valid_until else 'tanpa batas'}</span>"
                     f" → <span class='diff-new'>s.d. {_iso(el.get('valid_until')) if el.get('valid_until') else 'tanpa batas'}</span>")
        elif old:
            what = "Aturan diubah"
            body = f"<span class='diff-old'>{d.readable(old.expression)}</span><br>" + body
        else:
            what = "Aturan baru" + (" (perusahaan)" if el.get("layer") == "company" else "")
            # the rule already in the knowledge base for the same value, so the reviewer can compare
            same = [r for r in kb.view(demo.TODAY).rules.values() if r.produces == el["produces"]
                    and r.layer == el.get("layer", "regulation") and not d.is_input_convention(r)]
            if same:
                prev = max(same, key=lambda r: r.valid_from or date.min)
                body += (f"<br><span class='muted'>Aturan yang sudah ada untuk nilai ini "
                         f"({d.tgl(prev.valid_from)}{' s.d. ' + d.tgl(prev.valid_until) if prev.valid_until else ''}): "
                         f"</span><span class='diff-old' style='text-decoration:none'>{d.readable(prev.expression)}</span>")
                if prev.condition:
                    body += f" <span class='muted'>jika {d.readable(prev.condition)}</span>"
    elif kind == "table":
        title, what = (el.get("label_id") or el.get("name", "")).capitalize(), "Tabel " + ("diubah" if old else "baru")
        body = (f"Diambil dari tabel lampiran dokumen ({el['rows_ref'].split('/')[-1]})" if el.get("rows_ref")
                else f"{len(el.get('rows') or [])} baris")
    elif kind == "fact":
        title, what, body = (el.get("label_id") or el["id"]).capitalize(), "Istilah baru", el.get("label", "")
        period = ""
    else:
        title, what, body = el.get("id", ""), kind, ""
    cls = "rule company" if el.get("layer") == "company" else "rule"
    ui.html(f"<div class='{cls}'>{ui.badge(what, 'green' if 'baru' in what else 'blue')}<b>{title}</b> "
            f"<span class='muted'>· {period}</span><br>{body}{quote}</div>")


def check(delta, kb):
    """Schema, application, static check: the gates that run without the AI, here and now."""
    try:
        validate_delta_json(delta)
    except Exception as e:  # noqa: BLE001
        return None, [("error", f"Format: {str(e)[:250]}")]
    try:
        kb2 = apply_delta(kb, delta)
    except Exception as e:  # noqa: BLE001
        return None, [("error", f"Tidak bisa diterapkan pada knowledge base sekarang: {str(e)[:250]}")]
    pols = tuple({e.get("policy") for e in delta.get("add", []) + delta.get("change", []) if e.get("policy")})
    issued = (delta.get("document") or {}).get("issued")
    at = max(date.fromisoformat(issued) if issued else demo.TODAY, date(2013, 1, 1))
    rep = static.check(kb2, at, policies=pols)
    return kb2, [(f.severity, f"{f.kind}: {f.detail}") for f in rep.findings]


def regression(kb, kb2, policies):
    """Every scenario before and after: PPh of the scenario's month and of the year."""
    rows = []
    for sc in emp.scenarios().values():
        case = emp.scenario_case(sc)
        m = sc["month"]
        out = []
        for k in (kb, kb2):
            r, err = d.compute(case, demo.TODAY, k)
            out.append((r.periods[m].get("pph21_due"), r.year.get("annual_pph21")) if r else (None, None))
        (a, ya), (b, yb) = out
        changed = a != b or ya != yb
        rows.append({"Skenario": sc["title"], "Bulan": f"{d.MON[m - 1]} {case['tax_year']}",
                     "PPh sebelum": d.money(a), "PPh sesudah": d.money(b),
                     "Setahun sebelum → sesudah": f"{d.money(ya)} → {d.money(yb)}" if ya != yb else d.money(ya),
                     "Hasil": "berubah" if changed else "sama"})
    return pd.DataFrame(rows)


def affected_policies(delta, kb):
    """Installed company policies whose rules read or produce a value this update touches (static, like RQ4)."""
    touched = set()
    for e in delta.get("add", []) + delta.get("change", []):
        if e.get("kind") == "rule":
            touched.add(e["produces"])
        elif e.get("kind") in ("parameter", "table"):
            for r in kb.view(demo.TODAY).rules.values():
                if f"'{e.get('name')}'" in d.expr_text(r.expression) + d.expr_text(r.condition or ""):
                    touched.add(r.produces)
    out = []
    for r in kb.view(demo.TODAY).rules.values():
        if r.layer != "company":
            continue
        text = d.expr_text(r.expression) + " " + d.expr_text(r.condition or "")
        hit = [f for f in touched if f == r.produces or f in text]
        if hit:
            out.append((r.policy, r.id, hit))
    return out


def tab_review():
    s = demo.load()
    items = [p["id"] for p in demo.PENDING if demo.status(p["id"], s) == "review"]
    items += [x["id"] for x in s["drafts"] if x["id"] not in items]
    if not items:
        st.success("Tidak ada yang menunggu review.")
        return
    names = {i: _title(i) for i in items}
    names.update({x["id"]: f"{x['title']} ({x['origin']})" for x in s["drafts"]})
    cur = st.session_state.get("mg_open")
    pid = st.selectbox("Yang direview", items, index=items.index(cur) if cur in items else 0, format_func=names.get)
    st.session_state.mg_open = pid
    delta = demo.proposal(pid, s)
    kb = demo.kb()
    if pid in s["fixed"]:
        st.info(f"Ini versi yang diperbaiki ({s['fixed'][pid]['by']}). Catatan: “{s['fixed'][pid]['note']}”",
                icon=":material/auto_fix_high:")
    elif pid in demo.PENDING_BY_ID:
        st.caption("Usulan asli AI dari penelitian (claude-opus-5-5).")
    kb2, msgs = check(delta, kb)
    left, right = st.columns([1.6, 1], gap="large")
    with left:
        st.markdown(f"**Perubahan yang diusulkan** · {len(delta.get('add', []))} tambahan, "
                    f"{len(delta.get('change', []))} perubahan")
        for el in delta.get("change", []) + delta.get("add", []):
            card(el, kb)
    with right:
        st.markdown("**Pemeriksaan**")
        run = demo.run(pid) if pid in demo.PENDING_BY_ID and pid not in s["fixed"] else None
        if run:
            sel = next((c for c in run["candidates"] if c.get("n") == run.get("selected")), run["candidates"][0])
            for k, v in GATES.items():
                ok = (sel.get("gate_log") or {}).get(k) == "pass"
                st.markdown(f"{':material/check_circle:' if ok else ':material/cancel:'} {v}",
                            help="Hasil pemeriksaan saat AI menyusun usulan.")
        errors = [m for sev, m in msgs if sev == "error"]
        if kb2 is None:
            st.error(errors[0] if errors else msgs[0][1])
        else:
            st.markdown(":material/check_circle: Bisa diterapkan pada knowledge base sekarang",
                        help="Diperiksa ulang sekarang: format, penerapan, dan pemeriksa statis.")
            for sev, m in msgs[:4]:
                st.caption(f"⚠ {m}")
        if st.button("Tanya asisten tentang usulan ini", icon=":material/forum:", width="stretch"):
            assistant.open_with("Periksa usulan ini terhadap kutipan pasalnya")
            st.rerun()
    if kb2 is not None:
        st.markdown("**Contoh sebelum dan sesudah** · semua skenario umum dihitung dengan knowledge base sekarang dan "
                    "sesudah usulan ini. Hasil tahun-tahun sebelum tanggal berlaku harus sama.")
        with st.spinner("Menghitung skenario ..."):
            df = regression(kb, kb2, tuple(demo.installed_policies()))
        st.dataframe(df.style.apply(lambda r: ["background-color: #fff4d6" if r["Hasil"] == "berubah" else ""] * len(r),
                                    axis=1), hide_index=True, width="stretch")
        affected = affected_policies(delta, kb2)
        st.markdown("**Kebijakan perusahaan yang terdampak**", help=g.tip("dampak"))
        if affected:
            for pol, rid, facts in affected:
                ui.html(f"<div class='rule company'><b>{pol}</b> · aturan <code>{rid}</code> membaca atau menghasilkan "
                        f"nilai yang berubah: {', '.join(d.fact_label(f) for f in facts)}. Periksa apakah kebijakan ini "
                        "masih sesuai.</div>")
        else:
            st.caption("Tidak ada kebijakan perusahaan terpasang yang membaca nilai yang berubah.")
    st.divider()
    c1, c2 = st.columns([1, 2])
    reviewer = c1.text_input("Nama reviewer", "Admin", key="mg_reviewer")
    note = c2.text_input("Catatan", key=f"mg_note_{pid}", placeholder="opsional")
    b = st.columns(4)
    if b[0].button("Setujui", type="primary", icon=":material/check:", width="stretch", disabled=kb2 is None):
        demo.approve(pid, names[pid].split(" (")[0], delta, reviewer, note)
        st.session_state.mg_open = None
        st.toast("Disetujui. Knowledge base diperbarui.")
        st.rerun()
    if b[1].button("Sunting", icon=":material/edit:", width="stretch"):
        st.session_state.mg_edit = pid
    if b[2].button("Minta AI perbaiki", icon=":material/auto_fix_high:", width="stretch"):
        st.session_state.mg_fix = pid
    if b[3].button("Tolak", icon=":material/close:", width="stretch"):
        demo.reject(pid, names[pid], note or "-")
        st.session_state.mg_open = None
        st.rerun()
    if st.session_state.get("mg_fix") == pid:
        with st.container(border=True):
            notes_ = st.text_area("Catatan untuk AI", key=f"mg_fixnote_{pid}",
                                  placeholder="mis. Batas penghasilan DTP Rp10 juta dihitung dari gaji dan tunjangan tetap "
                                              "saja; natura mobil dinas jangan ikut.")
            if st.button("Kirim ke AI", icon=":material/send:"):
                ref = demo.gold_delta(pid)
                if ref:
                    demo.set_fixed(pid, ref, notes_ or "-", "AI (simulasi)")
                    st.session_state.mg_fix = None
                    st.rerun()
                st.warning("Untuk usulan ini belum ada contoh perbaikan di demo.")
            ui.mock("Di sistem penuh catatan Anda dikirim ke AI bersama usulan lama dan teks dokumen (satu putaran "
                    "perbaikan, ± USD 0,1–0,8), lalu hasilnya diperiksa lagi. Di demo ini hasil perbaikan diambil dari "
                    "jawaban acuan penelitian.")
    if st.session_state.get("mg_edit") == pid:
        with st.container(border=True):
            text = st.text_area("Usulan (JSON)", json.dumps(delta, ensure_ascii=False, indent=1), height=300,
                                key=f"mg_json_{pid}")
            if st.button("Simpan suntingan", icon=":material/save:"):
                try:
                    new = json.loads(text)
                    demo.set_fixed(pid, new, "disunting manual", "Admin")
                    st.session_state.mg_edit = None
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"JSON tidak valid: {e}")


# ---------------------------------------------------------------- add, change, revoke
def _source(key):
    c1, c2 = st.columns(2)
    doc = c1.text_input("Dokumen dasar", key=f"{key}_doc", placeholder="mis. PMK 168/2023")
    prov = c2.text_input("Pasal", key=f"{key}_prov", placeholder="mis. Pasal 2 ayat (1)")
    quote = st.text_input("Kutipan kalimat", key=f"{key}_quote", help=g.tip("kutipan"))
    return doc, prov, quote


def tab_edit():
    with st.container(border=True):
        g.md(f"**Minta AI mengerjakan**: tulis perubahannya dengan kalimat biasa; {g.term('asisten')} membuat draf dan "
             "memasukkannya ke Review.")
        c1, c2 = st.columns([4, 1])
        ask = c1.text_input("Permintaan", key="mg_ask", label_visibility="collapsed",
                            placeholder="mis. Batas upah JP 2027 menjadi Rp11.600.000 · Cabut aturan bingkisan")
        if c2.button("Minta AI", icon=":material/smart_toy:", width="stretch") and ask:
            assistant.open_with(ask)
            st.rerun()
    st.markdown("**Atau kerjakan manual**")
    what = st.segmented_control("Jenis", ["Angka baru", "Aturan baru", "Ubah aturan", "Cabut aturan"],
                                default="Angka baru", key="mg_what", label_visibility="collapsed")
    if what == "Angka baru":
        names = sorted({r.name for r in d.kb().records if r.kind == "parameter" and r.value_type in ("money", "rate")},
                       key=d.fact_label)
        name = st.selectbox("Angka", names, format_func=d.fact_label, key="mg_p")
        cur = drafts.current_param(name)
        cv = d.money(cur.value) if cur.value_type == "money" else d.pct(cur.value)
        st.caption(f"Sekarang **{cv}**, berlaku sejak {d.tgl(cur.valid_from)} ({d.short_doc(cur.source[0].document)}).")
        c1, c2 = st.columns(2)
        value = c1.number_input("Nilai baru" + (" (Rp)" if cur.value_type == "money" else " (desimal, mis. 0.01)"),
                                0.0, 1e11, None, key="mg_pv")
        start = c2.date_input("Berlaku mulai", date(demo.TODAY.year + 1, 1, 1), key="mg_ps")
        doc, prov, quote = _source("mg_pp")
        if value is not None and st.button("Kirim ke Review", type="primary", icon=":material/send:"):
            v = int(value) if cur.value_type == "money" else value
            delta = drafts.new_value(name, v, start, doc, prov, quote)
            demo.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
            st.success("Masuk ke Review.")
    elif what == "Aturan baru":
        facts = sorted(d.facts(), key=d.fact_label)
        c1, c2 = st.columns(2)
        produces = c1.selectbox("Nilai yang dihitung", facts, format_func=d.fact_label, key="mg_rf")
        company = c2.radio("Berlaku untuk", ("Peraturan negara", "Kebijakan perusahaan"), key="mg_rl") != "Peraturan negara"
        policy = st.text_input("Kode kebijakan", "PRS-DEMO", key="mg_rpol") if company else None
        cond = st.text_input("Berlaku jika (opsional)", key="mg_rc", placeholder="mis. gross_income > 10000000")
        expr = st.text_input("Rumus", key="mg_re", placeholder="mis. 50000 * hr('days_present') + income('other_regular')")
        with st.expander("Nama nilai dan data yang bisa dipakai"):
            st.dataframe(pd.DataFrame([{"Nama": f, "Arti": d.fact_label(f)} for f in facts]), hide_index=True,
                         height=200, width="stretch")
            st.caption("Data kasus dibaca dengan income('…'), benefit('…'), hr('…'), employee('…'), employer('…'). "
                       "Data baru lewat hr('…') otomatis menjadi kolom di kalkulator.")
        c1, c2 = st.columns(2)
        start = c1.date_input("Berlaku mulai", date(demo.TODAY.year + 1, 1, 1), key="mg_rs")
        end = c2.date_input("Berlaku sampai (kosongkan bila tanpa batas)", None, key="mg_ru")
        doc, prov, quote = _source("mg_rp")
        if expr:
            ui.html(f"<div class='rule{' company' if company else ''}'><b>{d.fact_label(produces)}</b> = {d.readable(expr)}"
                    + (f" <i>jika {d.readable(cond)}</i>" if cond else "") + "</div>")
            if st.button("Kirim ke Review", type="primary", icon=":material/send:", key="mg_rsend"):
                delta = drafts.new_rule(produces, expr, cond, start, end, company, policy, doc, prov, quote)
                demo.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
                st.success("Masuk ke Review.")
    else:
        rules = {r.id: r for r in d.kb().view(demo.TODAY).rules.values()
                 if not d.is_input_convention(r) and (r.valid_until is None or r.valid_until >= demo.TODAY)}
        ids = sorted(rules, key=lambda i: d.fact_label(rules[i].produces))
        rid = st.selectbox("Aturan", ids, key="mg_cr", format_func=lambda i: f"{d.fact_label(rules[i].produces)} · "
                           f"{d.short_doc(rules[i].source[0].document) if rules[i].source else ''}")
        r = rules[rid]
        ui.html(f"<div class='rule'><b>{d.fact_label(r.produces)}</b><br><b>Rumus:</b> {d.readable(r.expression)}<br>"
                f"<span class='muted'>Berlaku {d.tgl(r.valid_from)}{' s.d. ' + d.tgl(r.valid_until) if r.valid_until else ''}"
                f"</span></div>")
        if what == "Cabut aturan":
            g.md(f"{g.term('pencabutan', 'Mencabut')} = memberi tanggal akhir. Aturan tidak dihapus, jadi hitungan "
                 "lama tetap sama.")
            end = st.date_input("Tidak berlaku lagi sesudah", date(demo.TODAY.year, 12, 31), key="mg_ce")
            others = [x for x in d.kb().view(demo.TODAY).rules.values() if x.produces == r.produces and x.id != r.id
                      and (x.valid_until is None or x.valid_until > end)]
            readers = [x.id for x in d.kb().view(demo.TODAY).rules.values()
                       if r.produces in d.expr_text(x.expression) + d.expr_text(x.condition or "")]
            if not others:
                st.warning(f"Sesudah {d.tgl(end)} tidak ada aturan lain yang menghitung *{d.fact_label(r.produces)}*, "
                           f"padahal {len(readers)} aturan memakainya. Tambahkan pengganti, atau pastikan peraturannya "
                           "memang menghapus.", icon=":material/warning:")
            doc, prov, quote = _source("mg_cp")
            if st.button("Kirim ke Review", type="primary", icon=":material/send:", key="mg_csend"):
                delta = drafts.revoke(r, end, doc, prov, quote)
                demo.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
                st.success("Masuk ke Review.")
        else:
            expr = st.text_input("Rumus baru", d.expr_text(r.expression), key="mg_ue")
            start = st.date_input("Berlaku mulai", date(demo.TODAY.year + 1, 1, 1), key="mg_us",
                                  help="Versi lama tetap dipakai untuk bulan-bulan sebelumnya.")
            doc, prov, quote = _source("mg_up_")
            if expr != d.expr_text(r.expression) and st.button("Kirim ke Review", type="primary", icon=":material/send:",
                                                               key="mg_usend"):
                delta = drafts.change_rule(r, expr, start, doc, prov, quote)
                demo.add_draft(delta["delta_id"], delta["document"]["title"], delta, "manual")
                st.success("Masuk ke Review.")


# ---------------------------------------------------------------- company policies
def tab_policy():
    pols = demo.installed_policies()
    g.md(f"{g.term('kebijakan perusahaan', 'Kebijakan perusahaan')} yang terpasang dipakai kalkulator bila dipilih. "
         "Aturan perusahaan tidak boleh bertentangan dengan peraturan; sistem memeriksanya.")
    if pols:
        for pid, title in pols.items():
            with st.expander(f"{pid} · {title}"):
                for r in d.kb().view(demo.TODAY).rules.values():
                    if r.layer == "company" and r.policy == pid:
                        ui.html(f"<div class='rule company'><b>{d.fact_label(r.produces)}</b>: {d.readable(r.expression)}"
                                f"<br><span class='muted'>berlaku {d.tgl(r.valid_from)}"
                                f"{' s.d. ' + d.tgl(r.valid_until) if r.valid_until else ''}</span></div>")
                found = inputs.discover(demo.TODAY.year, pid)
                new_cols = [inputs.label(k) for k, e in found.items() if e["layer"] == "company"]
                if new_cols:
                    st.caption("Data yang ditanyakan kalkulator karena kebijakan ini: " + ", ".join(new_cols))
    else:
        st.caption("Belum ada kebijakan perusahaan terpasang. Setujui SP14 di Dokumen baru, atau buat dari contoh di "
                   "bawah.")
    st.markdown("**Buat dari contoh**")
    c1, c2 = st.columns(2)
    pid = c1.text_input("Kode kebijakan", "PRS-DEMO", key="mg_pol_id")
    tpl = c2.selectbox("Contoh", ["Uang makan per hari hadir", "THR kelipatan upah", "Bonus tahunan"], key="mg_pol_tpl")
    start = st.date_input("Berlaku mulai", date(demo.TODAY.year + 1, 1, 1), key="mg_pol_start")
    if tpl == "Uang makan per hari hadir":
        n = st.number_input("Rupiah per hari hadir", 0, 1_000_000, 50_000, 5_000, key="mg_pol_n")
        delta = drafts.meal_policy(int(n), pid, start)
    elif tpl == "THR kelipatan upah":
        n = st.number_input("Kelipatan upah", 0.5, 5.0, 1.5, 0.5, key="mg_pol_t")
        delta = drafts.thr_policy(n, pid, start)
    else:
        c1, c2 = st.columns(2)
        n = c1.number_input("Persen gaji pokok", 1, 500, 100, key="mg_pol_b")
        m = c2.selectbox("Bulan dibayar", range(1, 13), 11, format_func=lambda x: d.MONTHS[x - 1], key="mg_pol_m")
        delta = drafts.bonus_policy(n, m, pid, start)
    for el in delta["add"]:
        card(el, d.kb())
    if st.button("Kirim ke Review", type="primary", icon=":material/send:", key="mg_pol_send"):
        demo.add_draft(delta["delta_id"], delta["document"]["title"], delta, "contoh")
        st.success("Masuk ke Review.")


# ---------------------------------------------------------------- check and history
@st.cache_data
def _health(signature, today):
    kb = demo.kb()
    out = []
    by_name = {}
    for r in kb.records:
        if r.kind == "parameter":
            by_name.setdefault(r.name, []).append(r)
    for name, vs in by_name.items():
        years = sorted({v.valid_from.year for v in vs})
        if len(years) >= 3 and years[-1] - years[-2] == 1 and years[-1] < today.year + 1:
            out.append(("warn", f"{d.fact_label(name)} berganti tiap tahun; nilai {years[-1] + 1} belum ada.",
                        f"Terakhir: {d.short_doc(vs[-1].source[0].document)} ({years[-1]})."))
    ending = {}
    for r in kb.view(today).rules.values():
        if r.valid_until and r.valid_until >= today - timedelta(days=400) and r.valid_until.year <= today.year:
            ending.setdefault((r.valid_until, d.topic_of(r)), []).append(r)
    for (until, topic), rs in sorted(ending.items())[-4:]:
        out.append(("info", f"{topic}: {len(rs)} aturan berakhir {d.tgl(until)}.",
                    "Bila diperpanjang, unggah peraturan barunya di Dokumen baru."))
    found = inputs.discover(today.year, None)
    undefined = [k for k in found if not inputs.has_def(k)]
    if undefined:
        out.append(("warn", f"{len(undefined)} data yang dibaca aturan belum punya definisi (label dan penjelasan).",
                    ", ".join(undefined[:6])))
    for f in static.check(kb, today).findings[:8]:
        out.append(("error" if f.severity == "error" else "warn", f"{f.kind}: {f.detail}", ", ".join(f.ids)))
    return out


def tab_health():
    g.md("Pemeriksaan rutin atas isi knowledge base, supaya masalah ketahuan sebelum perhitungan salah.")
    items = _health(demo.signature(), demo.TODAY)
    for level, title, detail in items:
        icon = {"warn": ":material/schedule:", "info": ":material/event:", "error": ":material/error:"}[level]
        (st.warning if level == "warn" else st.error if level == "error" else st.info)(f"**{title}**  \n{detail}", icon=icon)
    if not items:
        st.success("Tidak ada temuan.")


def tab_history():
    s = demo.load()
    base = demo.base()
    ui.html(f"<div class='rule'><b>Keadaan awal demo</b> · {len(base.updates)} pembaruan dari penelitian, diketahui "
            f"sampai {demo.BASE_LABEL}.</div>")
    for i, a in enumerate(s["approved"]):
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"**v{i + 1}** · {a['title']} · disetujui {a['when']} oleh {a['reviewer']}"
                    + (f"  \n_{a['note']}_" if a.get("note") else ""))
        if c2.button("Kembalikan ke sebelum ini", key=f"rb_{i}", icon=":material/history:", width="stretch",
                     help="Pembaruan ini dan sesudahnya dibatalkan; dokumennya kembali menunggu review."):
            demo.rollback(i)
            st.rerun()
    if s["log"]:
        st.markdown("**Catatan aktivitas**")
        for e in s["log"][:20]:
            st.caption(f"{e['when']} · {e['what']}")


def show():
    st.session_state.page_ctx = "kelola"
    st.title("Manajemen knowledge base")
    g.md(f"Tambah, ubah, cabut, dan {g.term('review')} pengetahuan sistem. Bisa dikerjakan manual, atau minta "
         f"{g.term('asisten', 'Asisten AI')} (tombol di kanan bawah) membantu memeriksa dan mengerjakan. Tidak ada yang "
         "berubah sebelum Anda setujui.")
    s = demo.load()
    n_review = len({p["id"] for p in demo.PENDING if demo.status(p["id"], s) == "review"} | {x["id"] for x in s["drafts"]})
    tabs = st.tabs(["Dokumen baru", f"Review ({n_review})", "Tambah, ubah, cabut", "Kebijakan perusahaan", "Cek KB",
                    "Riwayat versi"])
    with tabs[0]:
        tab_documents()
    with tabs[1]:
        tab_review()
    with tabs[2]:
        tab_edit()
    with tabs[3]:
        tab_policy()
    with tabs[4]:
        tab_health()
    with tabs[5]:
        tab_history()
