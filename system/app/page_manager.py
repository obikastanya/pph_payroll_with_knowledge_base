"""Knowledge base management: inbox and the acquisition pipeline step by step (replay of a stored run, or a live run
with the LLM), review and approval, a manual Delta, the company policy editor, and the version history."""
import csv
import json
import re
from datetime import date

import pandas as pd
import streamlit as st

import state
import widgets as ui
from kb_context import base_for
from pph21kbs import corpus, static
from pph21kbs.corpus import Event
from pph21kbs.engine import evaluate_case
from pph21kbs.kb import apply_delta
from pph21kbs.kb.delta import validate_delta_json
from pph21kbs.kb.model import Rule
from pph21kbs.text import TEXT_DIR, registry

PARTS = {"uji": "Peristiwa uji (regulasi nyata 2023–2026)", "pengecoh": "Pengecoh", "pengembangan": "Pengembangan",
         "fiktif": "Regulasi fiktif", "kontrafaktual": "Kontrafaktual", "uji_kebijakan": "PKB nyata",
         "sintetis": "Kebijakan buatan"}
GATES = ("G1", "G2", "G3", "G4", "G5")
GATE_NAMES = {"G1": "skema + SHACL", "G2": "kutipan, angka, tanggal", "G3": "pemeriksa statis",
              "G4": "regresi masa lalu", "G5": "setiap unsur berefek"}


def _part(e):
    if e.layer == "company":
        return "uji_kebijakan" if e.part == "uji" else ("sintetis" if e.part == "sintetis" else e.part)
    return e.part


def _scores(run, event_id):
    path = state.EXPERIMENTS / run / "scores.csv"
    if not path.exists():
        return None
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if r["event"] == event_id and r["condition"] == "proposed":
            return r
    return None


def _elements_frame(delta):
    rows = []
    for op in ("add", "change", "remove"):
        for e in delta.get(op, []):
            content = e.get("expression") or e.get("value") or e.get("assertion") or ""
            if e.get("kind") == "table":
                content = f"{len(e.get('rows') or [])} baris" if e.get("rows") else json.dumps(e.get("rows_ref"))
            rows.append({"operasi": op, "jenis": e.get("kind", "hapus"), "id": e["id"], "menghasilkan": e.get("produces", ""),
                         "isi": str(content)[:160], "syarat": e.get("condition") or "", "berlaku dari": e.get("valid_from", ""),
                         "sampai": e.get("valid_until") or "", "sumber": "; ".join(f"{s.get('document')} {s.get('provision')}"
                                                                                  for s in e.get("source") or [])})
    return pd.DataFrame(rows)


def _gate_cell(log, g):
    v = (log or {}).get(g)
    if v is None:
        return ui.pill("–", "na")
    return ui.pill("lolos", "ok") if str(v).startswith("pass") else ui.pill("gagal", "no")


def render_run(res, ev, run=None):
    """The eight pipeline steps of one result record."""
    st.markdown("<div class='step'>1 · Dokumen dan segmen terpilih</div>", unsafe_allow_html=True)
    for doc, s in (res.get("selection") or {}).items():
        st.markdown(f"`{doc}` · {s.get('tokens')} token terpilih · {len(s.get('dropped') or [])} segmen dibuang karena anggaran")
    rel = (res.get("relevance") or {}).get("output") or {}
    st.markdown("<div class='step'>2 · Relevansi dan kutipan</div>", unsafe_allow_html=True)
    if rel:
        c1, c2 = st.columns([1, 2])
        c1.markdown(("✅ relevan" if rel.get("relevant") else "⛔ tidak relevan") + f"  \nlapis: {rel.get('layer', '')}  \n"
                    f"berlaku: {rel.get('effective_from') or '-'} s.d. {rel.get('effective_until') or '-'}  \n"
                    f"kutipan ditemukan: {'ya' if (res.get('relevance') or {}).get('quotes_ok') else 'tidak'}")
        c2.markdown(f"*{rel.get('reason', '')}*")
        for q in rel.get("quotes") or []:
            c2.caption(f"{q.get('provision')}: “{q.get('quote')}”")
    else:
        st.info("Tidak ada keluaran relevansi.")
    cands = res.get("candidates") or []
    if not cands:
        st.markdown(f"**Status: {res.get('status')}** (tidak ada kandidat; dokumen dinilai tidak relevan atau anggaran habis)")
        return
    st.markdown("<div class='step'>3 · Kandidat pembaruan dari LLM</div>", unsafe_allow_html=True)
    tabs = st.tabs([f"Kandidat {c['n']}" + (" (diperbaiki)" if c.get("repaired") else "") for c in cands])
    for tab, c in zip(tabs, cands):
        with tab:
            if c.get("delta"):
                st.dataframe(_elements_frame(c["delta"]), hide_index=True, width="stretch")
                with st.expander("JSON Δ"):
                    st.json(c["delta"], expanded=False)
            else:
                st.warning(f"Tidak dapat dibaca sebagai Δ: {c.get('error', '')[:300]}")
    st.markdown("<div class='step'>4 · Gerbang verifikasi (percobaan pertama → sesudah perbaikan)</div>",
                unsafe_allow_html=True)
    head = "<tr><th>Gerbang</th>" + "".join(f"<th>Kandidat {c['n']}</th>" for c in cands) + "</tr>"
    body = ""
    for g in GATES:
        body += f"<tr><td><b>{g}</b> <span class='muted'>{GATE_NAMES[g]}</span></td>"
        for c in cands:
            first, final = _gate_cell(c.get("first_gate_log"), g), _gate_cell(c.get("gate_log"), g)
            body += f"<td>{first}{' → ' + final if c.get('repaired') else ''}</td>"
        body += "</tr>"
    st.markdown(f"<div class='card'><table style='width:100%'>{head}{body}</table></div>", unsafe_allow_html=True)
    with st.expander("Pesan gerbang"):
        for c in cands:
            msgs = {g: v for g, v in (c.get("gate_log") or {}).items() if str(v).startswith("fail")}
            st.markdown(f"**Kandidat {c['n']}**: " + ("semua lolos" if c.get("passed") else ""))
            for g, v in msgs.items():
                st.caption(f"{g}: {v[:600]}")
    st.markdown("<div class='step'>5 · Ruang uji gerbang S<sup>G</sup></div>", unsafe_allow_html=True)
    st.markdown(" · ".join(f"kandidat {c['n']}: {c.get('sg_size', 0)} kasus" for c in cands))
    st.markdown("<div class='step'>6 · Konsensus perilaku</div>", unsafe_allow_html=True)
    groups = res.get("groups") or []
    st.markdown(f"Kelompok perilaku: `{groups}` → **{res.get('status')}**"
                + (f", kandidat terpilih {res.get('selected')}" if res.get("selected") else ""))
    ui.note("Kandidat yang lolos semua gerbang dikelompokkan menurut hasil hitungnya; kelompok terbesar menang, seri = "
            "abstain (sistem menahan diri).")
    if run:
        sc = _scores(run, ev.id)
        if sc:
            word = {"benar": "✅ benar", "salah": "❌ salah", "abstain": "⏸ abstain"}[sc["outcome"]]
            st.markdown(f"**Penilaian penelitian (ruang uji S<sup>E</sup>)**: {word}"
                        + (f" · {sc['wrong_tuples']} dari {sc['tuples']} tupel salah" if sc["outcome"] == "salah" else ""),
                        unsafe_allow_html=True)
    st.markdown("<div class='step'>7 · Pembaruan terpilih dan dampak lintas lapis</div>", unsafe_allow_html=True)
    if res.get("delta"):
        d = res["delta"]
        st.dataframe(_elements_frame(d), hide_index=True, width="stretch")
        if st.button("Hitung dampak terhadap kebijakan perusahaan", key=f"impact_{ev.id}_{run}",
                     icon=":material/account_tree:"):
            _impact(ev, d)
        if st.button("Kirim ke review", type="primary", key=f"send_{ev.id}_{run}", icon=":material/send:"):
            st.session_state.review = {"delta": d, "event": ev.id, "from": run or "jalan langsung"}
            st.success("Dikirim ke tab Review.")
    else:
        st.info("Tidak ada pembaruan yang diterapkan (abstain atau Δ kosong).")


def _impact(ev, delta):
    from pph21kbs import impact
    from pph21kbs.kb import graphdb
    base, _ = base_for(ev, state.kb())
    try:
        kb2 = apply_delta(base, dict(delta, delta_id="APP-IMPACT"))
    except Exception as e:  # noqa: BLE001
        st.error(f"Δ tidak dapat diterapkan pada basisnya: {e}")
        return
    remote = graphdb.available()
    if not remote:
        st.warning("GraphDB tidak aktif; kueri dijalankan di memori dan bisa lambat.")
    pols = state.policy_deltas()
    rows = []
    with st.spinner("Menjalankan detektor dampak (SPARQL) ..."):
        for pid, pd_ in pols.items():
            try:
                kp = apply_delta(kb2, pd_)
                det = impact.detect(kp, "APP-IMPACT", [pid], ev.issued, remote=remote)[pid]
            except Exception:  # noqa: BLE001 - policy outside the base's period
                continue
            if det["kinds"]:
                rows.append({"kebijakan": pid, "jenis dampak": "".join(sorted(det["kinds"])),
                             "aturan perusahaan": ", ".join(sorted({h[1] for h in det["hits"]}))[:120]})
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption("(a) aturan kebijakan membaca fakta yang berubah; (b) menghasilkan fakta yang juga diatur Δ; "
                   "(c) bertentangan dengan aturan wajib baru.")
    else:
        st.success("Tidak ada kebijakan perusahaan yang terdampak.")


def _upload_event(file, title, issued, layer):
    import build_texts
    raw = file.read().decode("utf-8", errors="replace")
    doc_id = "UPLOAD-" + re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-").upper()[:40]
    folder = TEXT_DIR / doc_id
    folder.mkdir(parents=True, exist_ok=True)
    if "=== PDF hlm." not in raw:
        raw = "=== PDF hlm. 1 ===\n" + raw
    (folder / "teks.txt").write_text(raw, encoding="utf-8")
    (folder / "segmen.json").write_text(json.dumps(build_texts.segment(raw, layer == "company"), ensure_ascii=False),
                                        encoding="utf-8")
    registry()[doc_id] = {"id": doc_id, "event": doc_id, "role": "upload", "issued": issued.isoformat(), "title": title,
                          "files": ""}
    return Event(doc_id, "unggahan", True, (doc_id,), issued, None, None, "", layer, title)


def _live_run(ev):
    from pph21kbs.pipeline import llm
    from pph21kbs.pipeline.run import Config, run_document
    base, _ = base_for(ev, state.kb()) if not ev.part == "unggahan" else (state.kb(), ev.issued)
    ledger = llm.Ledger("app-demo", run_limit_usd=3.0)
    client = llm.AnthropicClient(ledger)
    policies = (ev.document,) if ev.layer == "company" else ()
    with st.spinner("LLM membaca dokumen dan menyusun kandidat (beberapa menit) ..."):
        res = run_document(ev, base, client, ledger, Config(m=3), run_id="app-demo",
                           out_dir=state.WORKSPACE / "runs", policies=policies)
    st.session_state.live = {ev.id: res}
    return res


def tab_inbox():
    source = st.radio("Sumber dokumen", ("Korpus penelitian", "Unggah dokumen (.txt)"), horizontal=True, key="ib_src")
    ev = None
    if source.startswith("Korpus"):
        events = state.events()
        parts = [p for p in PARTS if any(_part(e) == p for e in events)]
        c1, c2 = st.columns([1, 2.5])
        part = c1.selectbox("Kelompok", parts, format_func=PARTS.get, key="ib_part")
        group = [e for e in events if _part(e) == part]
        reg = registry()
        ev = c2.selectbox("Dokumen", group, key="ib_event",
                          format_func=lambda e: f"{e.id} · {reg.get(e.document, {}).get('title', e.title)[:90]}")
    else:
        with st.form("upload"):
            f = st.file_uploader("Teks dokumen (.txt)", type="txt")
            c1, c2, c3 = st.columns([2, 1, 1])
            title = c1.text_input("Judul", "Peraturan baru")
            issued = c2.date_input("Tanggal terbit", state.TODAY)
            layer = c3.selectbox("Lapis", ("regulation", "company"))
            if st.form_submit_button("Masukkan ke kotak masuk") and f:
                st.session_state.upload_event = _upload_event(f, title, issued, layer)
        ev = st.session_state.get("upload_event")
        if ev is None:
            st.info("Unggah teks dokumen untuk diproses. Dokumen unggahan hanya bisa dijalankan langsung dengan LLM.")
            return
    st.markdown(f"**{ev.id}** · terbit {ev.issued} · lapis {ev.layer} · dokumen {', '.join(ev.documents)}")
    runs = state.stored_runs(ev.id)
    modes = (["Putar ulang jalan tersimpan"] if runs else []) + ["Jalankan LLM sekarang"]
    mode = st.radio("Mode", modes, horizontal=True, key="ib_mode")
    if mode.startswith("Putar"):
        run = st.selectbox("Jalan eksperimen", list(runs), key="ib_run",
                           help="Hasil yang tersimpan dari eksperimen penelitian; tidak memanggil API.")
        res = state.load_json(runs[run])
        st.caption(f"Biaya jalan ini saat dijalankan: USD {res.get('cost_usd', 0):.3f}")
        render_run(res, ev, run)
    else:
        st.warning("Mode ini memanggil API Claude dan memakai kredit (±USD 0,1–0,9 per dokumen, m = 3).",
                   icon=":material/payments:")
        ok = st.checkbox("Saya paham dan ingin menjalankannya", key="ib_ok")
        if st.button("Jalankan alur akuisisi", type="primary", disabled=not ok, icon=":material/smart_toy:"):
            _live_run(ev)
        res = (st.session_state.get("live") or {}).get(ev.id)
        if res:
            st.caption(f"Biaya jalan ini: USD {res.get('cost_usd', 0):.3f}")
            render_run(res, ev)


def _check(delta, kb):
    """Schema, strict application, static check. Returns (K' or None, messages)."""
    msgs = []
    try:
        validate_delta_json(delta)
    except Exception as e:  # noqa: BLE001
        return None, [("error", f"Skema Δ: {str(e)[:300]}")]
    try:
        kb2 = apply_delta(kb, delta)
    except Exception as e:  # noqa: BLE001
        return None, [("error", f"Tidak dapat diterapkan: {str(e)[:300]}")]
    omega = date.fromisoformat(delta["document"]["issued"]) if delta.get("document", {}).get("issued") else state.TODAY
    pols = tuple({e.get("policy") for e in delta.get("add", []) if e.get("policy")})
    rep = static.check(kb2, max(omega, date(2013, 1, 1)), policies=pols)
    for f in rep.findings:
        msgs.append((f.severity, f"{f.kind}: {', '.join(f.ids)} {f.detail}"))
    return kb2, msgs


def _simulate(kb_before, kb_after, policy=None, year=None, salary=9_500_000, omega=None):
    year = year or 2025
    omega = omega or state.TODAY
    case = {"case_id": "sim", "tax_year": year, "method": "gross",
            "employee": {"ptkp_status": "K/1", "sex": "M", "tax_id_valid": True},
            "employer": {"klu": "13921", "jkk_risk_group": "very_low", "policy": policy},
            "employment": {"start_month": 1, "end_month": 12},
            "periods": [{"month": m, "income": {"base_salary": salary, **({"thr": salary} if m == 4 else {})},
                         "benefits": {}, "zakat": 0} for m in range(1, 13)]}
    rows, conflicts = [], []
    for name, k in (("sebelum", kb_before), ("sesudah", kb_after)):
        try:
            r = evaluate_case(k, case, omega)
            rows.append({"versi": name, **{ui.MONTHS[m - 1]: r.periods[m].get("pph21_due") for m in sorted(r.periods)},
                         "setahun": r.year.get("annual_pph21")})
            if name == "sesudah":
                conflicts = r.conflicts
        except Exception as e:  # noqa: BLE001
            rows.append({"versi": name, "galat": str(e)[:200]})
    return pd.DataFrame(rows), conflicts


def _review_box(delta, key, policy=None):
    kb = state.kb()
    kb2, msgs = _check(delta, kb)
    errors = [m for s, m in msgs if s == "error"]
    if kb2 is None or errors:
        for m in errors or [m for _, m in msgs]:
            st.error(m)
        return
    st.success(f"Δ valid dan dapat diterapkan · {sum(len(delta.get(o, [])) for o in ('add', 'change', 'remove'))} unsur"
               + (f" · {len(msgs)} peringatan statis" if msgs else ""))
    for _, m in msgs[:8]:
        st.caption(f"⚠ {m}")
    # the year the update starts to apply, known as of its recording date (or today, whichever is later)
    starts = [date.fromisoformat(e["valid_from"]) for e in delta.get("add", []) + delta.get("change", [])
              if e.get("valid_from")]
    issued = date.fromisoformat(delta["document"]["issued"]) if delta.get("document", {}).get("issued") else state.TODAY
    year = max([d.year for d in starts if d >= date(2013, 1, 1)] or [issued.year])
    year = min(max(year, 2023), 2027)
    omega = max(state.TODAY, issued)
    c1, c2 = st.columns(2)
    salary = c1.number_input("Gaji pegawai contoh", 0, 10**10, 15_000_000, 500_000, key=f"{key}_sal")
    year = c2.number_input("Tahun simulasi", 2013, 2027, year, key=f"{key}_year")
    df, conflicts = _simulate(kb, kb2, policy, int(year), int(salary), omega)
    st.markdown(f"**Simulasi** pegawai contoh (K/1, THR April, KLU 13921) tahun {year}, pengetahuan per {omega:%d/%m/%Y}: "
                "PPh 21 per bulan sebelum dan sesudah")
    st.dataframe(df, hide_index=True, width="stretch")
    for c in conflicts:
        st.warning(f"Konflik dilaporkan: {c.get('code', '')} · {c.get('source') or c.get('company_rules')} · {c.get('fact', '')}")
    c1, c2 = st.columns([2, 1])
    reviewer = c1.text_input("Nama peninjau", "", key=f"{key}_who")
    if c2.button("Setujui dan terapkan", type="primary", key=f"{key}_ok", disabled=not reviewer.strip(),
                 icon=":material/check:"):
        path = state.save_update(delta, note=f"disetujui {reviewer} {date.today()}")
        st.session_state.pop("review", None)
        st.success(f"Diterapkan ke ruang kerja: {path.name}")
        st.rerun()


def tab_review():
    rv = st.session_state.get("review")
    if not rv:
        st.info("Belum ada pembaruan yang dikirim ke review. Kirim dari tab Kotak masuk, atau tulis Δ di tab Δ manual.")
        return
    st.markdown(f"Pembaruan dari **{rv['from']}** untuk peristiwa **{rv['event']}**. Ubah JSON bila perlu "
                "(koreksi peninjau), lalu periksa dan setujui.")
    text = st.text_area("Δ (JSON)", json.dumps(rv["delta"], ensure_ascii=False, indent=1), height=320, key="rv_text")
    try:
        delta = json.loads(text)
    except json.JSONDecodeError as e:
        st.error(f"JSON tidak valid: {e}")
        return
    edited = delta != rv["delta"]
    if edited:
        st.caption("Δ diubah peninjau (upaya koreksi dicatat di catatan pembaruan).")
    _review_box(delta, "rv")
    if st.button("Tolak", key="rv_reject", icon=":material/close:"):
        st.session_state.pop("review", None)
        st.rerun()


EXAMPLE_DELTA = {
    "delta_id": "CONTOH-BIAYA-JABATAN-2027", "event_id": None,
    "document": {"id": "CONTOH", "title": "Contoh: kenaikan batas biaya jabatan mulai 2027", "issued": "2026-12-15"},
    "relevant": True,
    "add": [{"kind": "parameter", "id": "PAR.JOB_EXPENSE_MAX_YEAR.2027", "name": "job_expense_max_year",
             "value": 7200000, "value_type": "money", "valid_from": "2027-01-01", "recorded_on": "2026-12-15",
             "source": [{"document": "CONTOH", "provision": "Pasal 1 ayat (1)",
                         "quote": "biaya jabatan paling banyak Rp7.200.000,00 setahun"}]},
            {"kind": "parameter", "id": "PAR.JOB_EXPENSE_MAX_MONTH.2027", "name": "job_expense_max_month",
             "value": 600000, "value_type": "money", "valid_from": "2027-01-01", "recorded_on": "2026-12-15",
             "source": [{"document": "CONTOH", "provision": "Pasal 1 ayat (2)",
                         "quote": "atau Rp600.000,00 sebulan"}]}],
    "change": [{"kind": "parameter", "id": "PAR.JOB_EXPENSE_MAX_YEAR.2009", "name": "job_expense_max_year",
                "value": 6000000, "value_type": "money", "valid_from": "2009-01-01", "valid_until": "2026-12-31",
                "recorded_on": "2026-12-15",
                "source": [{"document": "CONTOH", "provision": "Pasal 2", "quote": "ketentuan lama dinyatakan tidak berlaku"}]},
               {"kind": "parameter", "id": "PAR.JOB_EXPENSE_MAX_MONTH.2009", "name": "job_expense_max_month",
                "value": 500000, "value_type": "money", "valid_from": "2009-01-01", "valid_until": "2026-12-31",
                "recorded_on": "2026-12-15",
                "source": [{"document": "CONTOH", "provision": "Pasal 2", "quote": "ketentuan lama dinyatakan tidak berlaku"}]}],
    "remove": [], "note": "contoh perubahan parameter (jenis T1)"}


def tab_manual():
    st.markdown("Tulis atau unggah Δ dalam bahasa representasi (format `docs/spesifikasi/format_data.md`). Δ diperiksa "
                "skema, diterapkan ketat, dicek statis, dan disimulasikan sebelum disetujui. Dipakai pada E1 untuk "
                "perubahan tak terlihat.")
    up = st.file_uploader("Unggah Δ (.json)", type="json", key="man_up")
    start = json.loads(up.read()) if up else EXAMPLE_DELTA
    text = st.text_area("Δ (JSON)", json.dumps(start, ensure_ascii=False, indent=1), height=320, key="man_text")
    try:
        delta = json.loads(text)
    except json.JSONDecodeError as e:
        st.error(f"JSON tidak valid: {e}")
        return
    if st.button("Periksa", key="man_check", icon=":material/fact_check:"):
        st.session_state.man_delta = delta
    if st.session_state.get("man_delta") == delta:
        _review_box(delta, "man")


def tab_policy():
    pols = state.policy_deltas()
    reg = registry()
    st.markdown("**Kebijakan perusahaan di korpus**")
    pid = st.selectbox("Kebijakan", sorted(pols), key="pol_pick",
                       format_func=lambda p: f"{p} · {reg.get(p, {}).get('title', '')[:80]}")
    st.dataframe(_elements_frame(pols[pid]), hide_index=True, width="stretch", height=240)
    st.divider()
    st.markdown("**Buat kebijakan baru** — aturan perusahaan dalam representasi yang sama. Aturan yang menyimpangi "
                "ketentuan wajib tetap disimpan, tetapi engine menerapkan regulasi dan melaporkan konfliknya.")
    c1, c2, c3 = st.columns([1, 2, 1])
    new_id = c1.text_input("Id kebijakan", "PT-CONTOH", key="pol_id").strip().upper().replace(" ", "-")
    title = c2.text_input("Judul", "Peraturan Perusahaan PT Contoh", key="pol_title")
    start = c3.date_input("Berlaku mulai", date(2025, 1, 1), key="pol_start")
    facts = sorted({r.produces for r in state.kb().view(state.TODAY).rules.values()})
    default = pd.DataFrame([
        {"nama": "MEAL_ALLOWANCE", "fakta": "other_regular_income", "ekspresi": "income('other_regular') + 750000",
         "syarat": "", "kode konflik": "", "pasal": "Pasal 10", "kutipan": "tunjangan makan sebesar Rp750.000 per bulan"},
        {"nama": "METHOD", "fakta": "withholding_method", "ekspresi": "'gross_up'", "syarat": "", "kode konflik": "",
         "pasal": "Pasal 12", "kutipan": "pajak penghasilan pekerja ditanggung perusahaan melalui tunjangan pajak"},
    ])
    rules = st.data_editor(default, num_rows="dynamic", width="stretch", key="pol_rules",
                           column_config={"fakta": st.column_config.SelectboxColumn(options=facts)})
    adds = []
    for _, r in rules.iterrows():
        if not (r["nama"] and r["fakta"] and r["ekspresi"]):
            continue
        e = {"kind": "rule", "id": f"PRS.{new_id}.{str(r['nama']).upper()}", "layer": "company", "modality": "default",
             "scope": "year" if r["fakta"] == "withholding_method" else "period", "produces": r["fakta"],
             "expression": str(r["ekspresi"]), "valid_from": start.isoformat(), "policy": new_id,
             "recorded_on": start.isoformat(),
             "source": [{"document": new_id, "provision": str(r["pasal"] or "Pasal 1"),
                         "quote": str(r["kutipan"] or "ketentuan kebijakan perusahaan")}]}
        if r["syarat"]:
            e["condition"] = str(r["syarat"])
        if r["kode konflik"]:
            e["conflict_code"] = str(r["kode konflik"])
        adds.append(e)
    delta = {"delta_id": f"POL-{new_id}", "event_id": None,
             "document": {"id": new_id, "title": title, "issued": start.isoformat()}, "relevant": True,
             "add": adds, "change": [], "remove": [], "note": "dibuat di editor kebijakan"}
    registry()[new_id] = {"id": new_id, "event": "", "role": "policy", "issued": start.isoformat(), "title": title,
                          "files": ""}
    with st.expander("JSON Δ kebijakan"):
        st.json(delta, expanded=False)
    if st.button("Periksa dan simulasikan", key="pol_check", icon=":material/fact_check:"):
        st.session_state.pol_delta = delta
    if st.session_state.get("pol_delta") == delta:
        _review_box(delta, "pol", policy=new_id)


def tab_history():
    kb = state.kb()
    rows = []
    for i, u in enumerate(kb.updates, start=1):
        rows.append({"versi": f"v{i:02d}", "pembaruan": u.update_id, "peristiwa": u.event_id or "", "dokumen": u.document,
                     "dicatat": u.recorded_on, "rekaman": u.last_seq - u.first_seq + 1,
                     "asal": "ruang kerja" if u.update_id.startswith("WS-") else "emas", "catatan": (u.note or "")[:80]})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=300)
    st.caption(f"Sidik jari KB kini: `{kb.fingerprint()[:16]}` · riwayat hanya bertambah (append-only), sehingga hasil "
               "per tanggal pengetahuan selalu dapat direproduksi (A3ω).")
    st.markdown("**Perbedaan dua versi**")
    opts = state.versions()
    labels = [o[0] for o in opts]
    c1, c2 = st.columns(2)
    a = c1.selectbox("Dari", labels, index=max(0, len(labels) - 2), key="h_a")
    b = c2.selectbox("Ke", labels, index=len(labels) - 1, key="h_b")
    ka, kb_ = state.kb_at(dict(opts)[a]), state.kb_at(dict(opts)[b])
    va = {r.id: r for r in ka.view(state.TODAY).records}
    vb = {r.id: r for r in kb_.view(state.TODAY).records}

    def content(r):
        return (getattr(r, "expression", None) and r.expression.text) or str(getattr(r, "value", "")) or \
               str(len(getattr(r, "rows", ()) or ())) + " baris"

    diff = [{"perubahan": "ditambah", "id": i, "isi": content(vb[i])[:140]} for i in sorted(set(vb) - set(va))]
    diff += [{"perubahan": "dihapus", "id": i, "isi": content(va[i])[:140]} for i in sorted(set(va) - set(vb))]
    diff += [{"perubahan": "diubah", "id": i, "isi": f"{content(va[i])[:60]} → {content(vb[i])[:60]}"
              + (f" · berlaku sampai {va[i].valid_until} → {vb[i].valid_until}" if va[i].valid_until != vb[i].valid_until else "")}
             for i in sorted(set(va) & set(vb)) if va[i].seq != vb[i].seq]
    st.dataframe(pd.DataFrame(diff), hide_index=True, width="stretch")
    st.markdown("**Unduh Δ**")
    uid = st.selectbox("Pembaruan", [r["pembaruan"] for r in rows], index=len(rows) - 1, key="h_dl")
    gold = state.ROOT / "dataset" / "12_emas" / "delta" / f"{uid}.json"
    ws = [f for f in state.workspace_files() if uid in f.name]
    path = gold if gold.exists() else (ws[0] if ws else None)
    if path:
        st.download_button(f"Unduh {path.name}", path.read_bytes(), path.name, "application/json",
                           icon=":material/download:")
    if state.workspace_files():
        st.divider()
        if st.button("Kosongkan ruang kerja (kembali ke KB emas)", icon=":material/restart_alt:"):
            state.reset_workspace()
            st.rerun()


def show():
    st.title("Manajemen knowledge base")
    st.caption("Dokumen masuk → LLM menyusun kandidat → gerbang G1–G5 → konsensus → review manusia → KB versi baru. "
               "Perubahan disimpan di ruang kerja; KB emas penelitian tidak pernah diubah.")
    tabs = st.tabs(["Kotak masuk dan akuisisi", f"Review{' (1)' if st.session_state.get('review') else ''}",
                    "Δ manual", "Editor kebijakan", "Riwayat versi"])
    with tabs[0]:
        tab_inbox()
    with tabs[1]:
        tab_review()
    with tabs[2]:
        tab_manual()
    with tabs[3]:
        tab_policy()
    with tabs[4]:
        tab_history()
