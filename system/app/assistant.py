"""AI assistant as a pop-up: a floating button on every page opens a separate chat window. The conversation is kept
when the window is closed (workspace/chat.json, also after a reload) and can be cleared.

The model (gpt-5.4-mini by default, through ai.chat) answers from the knowledge base context and picks at most one
action; the app carries it out with its own code: explain or check the proposal under review, prepare a fix note for
the reviewer, explain why the system was unsure, draft a new number, a revocation or a company policy (drafts go to
Review), explain the calculator result, look up a number. It never approves. Without a key or budget, or when chosen,
the keyword matching below answers instead (no API).
"""
import re
from datetime import date

import streamlit as st

import ai
import data as d
import drafts
import store

OFFLINE = "tanpa-ai"
MODELS = {"gpt-5.4-mini": "OpenAI · murah, bawaan (USD 0,75 / 4,50 per juta token)",
          "gpt-6.1-sol": "OpenAI · model kedua penelitian (USD 2 / 10)",
          OFFLINE: "Tanpa AI · pencocokan kata kunci, gratis"}
SUGGEST = {
    "kelola": ["Jelaskan usulan yang sedang direview", "Periksa usulan ini terhadap kutipan pasalnya",
               "Kenapa sistem ragu pada PKB WIKA?", "Buat aturan uang makan Rp50 ribu per hari hadir",
               "Cabut aturan bingkisan", "Batas upah JP 2027 menjadi Rp11.600.000"],
    "kalkulator": ["Kenapa PPh bulan ini segini?", "Berapa batas upah JP sekarang?", "Apa itu TER?"],
    "kb": ["Berapa batas upah JP sekarang?", "Berapa biaya jabatan?", "Apa yang berubah terakhir?"],
}


# ---------------------------------------------------------------- answers
def _current_item():
    pid = st.session_state.get("mg_open")
    if not pid:
        return None, None
    return pid, store.proposal(pid)


def _explain(pid, delta):
    els = [e for e in delta.get("add", []) + delta.get("change", []) if e.get("kind") in ("rule", "parameter", "table")]
    touched = sorted({d.fact_label(e.get("produces") or e.get("name") or e["id"]) for e in els})
    starts = sorted({e.get("valid_from") for e in els if e.get("valid_from")})
    title = (delta.get("document") or {}).get("title", pid)
    return (f"**{title}** mengusulkan {len(delta.get('add', []))} tambahan dan {len(delta.get('change', []))} perubahan, "
            f"berlaku mulai {', '.join(starts[:3]) or '-'}. Nilai yang tersentuh: {', '.join(touched[:8])}.\n\n"
            "Buka tab *Review* untuk melihat contoh sebelum dan sesudahnya pada skenario umum.")


def quote_status(delta):
    """Per element: (what, provision, quote found in the document text or None when the text is not available,
    every number of a money parameter appears in its quote). The quote gate (G2), run here and now."""
    from pph21kbs.text import normalize, normalized
    out = []
    for e in delta.get("add", []) + delta.get("change", []):
        for s in (e.get("source") or [])[:1]:
            try:
                found = normalize(s.get("quote", "")) in normalized(s.get("document"))
            except Exception:  # noqa: BLE001 - document text not available
                found = None
            num_ok = True
            if e.get("kind") == "parameter" and e.get("value_type") == "money":
                num_ok = str(int(float(e["value"]))) in re.sub(r"\D", "", s.get("quote", ""))
            out.append((d.fact_label(e.get("produces") or e.get("name") or e["id"]), s.get("provision", ""), found, num_ok))
    return out


def _check(pid, delta):
    """Real check: is every quote in the document text, and does every number of a parameter appear in its quote?"""
    lines, problems = [], 0
    for what, provision, found, num_ok in quote_status(delta):
        mark = "✓" if found and num_ok else ("?" if found is None else "⚠")
        problems += mark == "⚠"
        note = "" if found else " · kutipan tidak ditemukan di dokumen" if found is False else " · teks dokumen tidak ada"
        note += "" if num_ok else " · angka tidak ada di kutipan"
        lines.append(f"{mark} {what} ({provision}){note}")
    head = ("Semua kutipan ada di dokumen dan angkanya cocok." if not problems else
            f"{problems} bagian perlu dicek manusia.")
    return (f"{head}\n\n" + "\n".join(f"- {x}" for x in lines[:14]) +
            "\n\nIni pendapat kedua, bukan keputusan. Kecocokan kutipan belum menjamin aturannya benar: periksa juga "
            "syarat dan rumusnya.")


def _why_unsure(pid):
    r = store.run(pid)
    if not r:
        return "Tidak ada hasil AI tersimpan untuk dokumen itu."
    groups = r.get("groups") or []
    passed = sum(1 for c in r.get("candidates", []) if c.get("passed"))
    return (f"AI menyusun {len(r.get('candidates', []))} versi usulan; {passed} lolos pemeriksaan otomatis. Versi yang "
            f"lolos dihitung pada contoh kasus dan dikelompokkan menurut hasilnya: {len(groups)} kelompok "
            f"({', '.join(str(len(g)) + ' versi' for g in groups)}). Tidak ada kelompok yang lebih besar, jadi sistem ragu "
            "dan tidak menebak. Anda bisa menulis kebijakannya di tab *Kebijakan perusahaan*, atau meminta saya "
            "menyusun ulang dengan catatan Anda.")


def _param(q):
    ql = q.lower()
    best = None
    for name in d.params():
        words = [w for w in re.findall(r"[a-z]+", d.fact_label(name).lower()) if len(w) > 2]
        score = sum(w in ql for w in words)
        if score and (best is None or score > best[0]):
            best = (score, name)
    return best[1] if best else None


def _lookup(name):
    vs = sorted((r for r in d.kb().records if r.kind == "parameter" and r.name == name), key=lambda r: r.valid_from)
    cur = [r for r in vs if r.valid_from <= store.TODAY and (r.valid_until is None or store.TODAY <= r.valid_until)]
    r = cur[-1] if cur else vs[-1]
    fmt = lambda v: d.money(v.value) if v.value_type == "money" else d.pct(v.value) if v.value_type == "rate" else v.value  # noqa: E731
    src = r.source[0]
    return (f"**{d.fact_label(name)}** menurut knowledge base sekarang: **{fmt(r)}**, berlaku sejak {d.tgl(r.valid_from)}."
            f"\n\nSumber: {d.short_doc(src.document)} {src.provision}, “{src.quote}”.\n\nRiwayat: "
            + ", ".join(f"{v.valid_from.year}: {fmt(v)}" for v in vs[-4:]) +
            f"\n\nKnowledge base diketahui sampai {d.tgl(store.known_until())}.")


def _calc_why():
    last = st.session_state.get("k_last")
    if not last:
        return "Buka Kalkulator dan hitung dulu; saya menjelaskan dari hasil terakhir di sana."
    m = last["month"]
    due, work = last["due"], last["work"]

    def said(x):
        rid, expr, reads = work[x]
        parts = ", ".join(f"{d.fact_label(k[0]).lower()} {d.fmt(k[0], v)}" for k, v in reads if v not in (None, 0))
        return rid, expr, parts
    rid, expr, parts = said(m)
    text = (f"PPh {d.MONTHS[m - 1]}: **{d.money(due[m])}**, dihitung aturan `{rid}`: {d.readable(expr) if expr else '-'}"
            f" (dengan {parts or '-'}).")
    prev = max((x for x in due if x < m), default=None)
    if prev:
        prid, _, _ = said(prev)
        before = {k[0]: v for k, v in work[prev][2]}
        moved = [f"{d.fact_label(k[0]).lower()} {d.fmt(k[0], before.get(k[0]))} → {d.fmt(k[0], v)}"
                 for k, v in work[m][2] if k[0] in before and before[k[0]] != v]
        text += f" Bulan sebelumnya {d.money(due[prev])}."
        if prid != rid:
            text += f" Bulan ini memakai aturan lain (`{prid}` → `{rid}`)."
        elif moved:
            text += " Yang berubah: " + "; ".join(moved) + "."
    if last.get("final"):
        text += " Bulan ini bulan penutup: pajak setahun dihitung ulang dan dikurangi yang sudah dipotong."
    return text + "\n\nRincian dan pasalnya ada di bagian *Kenapa angkanya segini?* di bawah hasil."


def reply(q):
    """(answer, action label or None). Actions are already carried out (drafts saved) when they are returned."""
    ql = q.lower()
    pid, delta = _current_item()
    if "jelaskan usulan" in ql or ("usulan" in ql and "jelaskan" in ql):
        return (_explain(pid, delta) if delta else "Pilih dulu usulan di tab *Review*."), None
    if "periksa" in ql and "usulan" in ql:
        return (_check(pid, delta) if delta else "Pilih dulu usulan di tab *Review*."), None
    if "perbaiki" in ql:
        if not pid:
            return "Pilih dulu usulan di tab *Review*, lalu tulis catatan Anda.", None
        return act("fix_proposal", {"note": q}, q), "perbaikan"
    if "ragu" in ql or "pkb" in ql:
        return _why_unsure("PKB-WIKA-2025" if "wika" in ql or not pid else pid), None
    if ("buat" in ql or "tambah" in ql) and ("per hari" in ql or "uang makan" in ql):
        amt = re.search(r"(\d+)\s*(ribu|rb|k)?", ql)
        n = int(amt.group(1)) * (1000 if amt and amt.group(2) else 1) if amt else 50_000
        delta = drafts.meal_policy(n)
        store.add_draft(delta["delta_id"], delta["document"]["title"], delta, "asisten", inputs=[
            {"key": "hr.days_present", "label": "Hari hadir", "help": "Jumlah hari hadir bulan itu.", "type": "int",
             "group": "bulanan", "order": 65, "source": delta["document"]["title"]}])
        amount = f"{n:,}".replace(",", ".")
        return (f"Draf kebijakan perusahaan sudah saya buat: **uang makan Rp{amount} × hari hadir**, penghasilan teratur, "
                "berlaku mulai 1 Januari tahun depan. Aturan ini membaca data baru *hari hadir*, jadi setelah disetujui "
                "kolomnya muncul sendiri di kalkulator. Periksa di tab *Review*."), "draf"
    if "cabut" in ql or "hentikan" in ql:
        rule = drafts.find_rule(q)
        if not rule:
            return "Aturan mana yang ingin dicabut? Sebutkan namanya, mis. \"cabut aturan bingkisan\".", None
        delta = drafts.revoke(rule, date(store.TODAY.year, 12, 31), "permintaan lewat asisten", "-")
        store.add_draft(delta["delta_id"], delta["document"]["title"], delta, "asisten")
        return (f"Draf pencabutan **{d.fact_label(rule.produces)}** ({d.short_doc(rule.source[0].document)} "
                f"{rule.source[0].provision}) sudah ada di tab *Review*, berlaku sampai 31 Desember {store.TODAY.year}. "
                "Aturannya tidak dihapus, hanya diberi tanggal akhir, jadi hitungan lama tetap sama. Lengkapi dasar "
                "hukumnya sebelum disetujui."), "draf"
    if "menjadi" in ql:
        name = _param(q)
        num = re.search(r"rp\s*([\d.]+)", ql) or re.search(r"([\d.]{6,})", ql)
        year = re.search(r"\b(20\d\d)\b", ql)
        if name and num:
            value = int(num.group(1).replace(".", ""))
            start = date(int(year.group(1)) if year else store.TODAY.year + 1, 1, 1)
            delta = drafts.new_value(name, value, start, "permintaan lewat asisten", "-", "")
            store.add_draft(delta["delta_id"], delta["document"]["title"], delta, "asisten")
            return (f"Draf angka baru: **{d.fact_label(name)} = {d.money(value)}** mulai {d.tgl(start)}; nilai lama "
                    "berakhir sehari sebelumnya. Ada di tab *Review*. Tambahkan dokumen dan pasal dasarnya sebelum "
                    "disetujui."), "draf"
    if "pph" in ql and ("kenapa" in ql or "segini" in ql or "naik" in ql):
        return _calc_why(), None
    if "berubah terakhir" in ql or "terakhir" in ql:
        u = d.kb().updates[-1]
        return f"Pembaruan terakhir: **{d.doc_title(u.document)}**, dicatat {d.tgl(u.recorded_on)}.", None
    if "apa itu" in ql:
        import glossary
        word = ql.split("apa itu", 1)[1].strip(" ?")
        for k, (lab, _) in glossary.TERMS.items():
            if word and (word in k.lower() or word in lab.lower()):
                return glossary.tip(k), None
    name = _param(q)
    if name and ("berapa" in ql or "nilai" in ql):
        return _lookup(name), None
    return ("Saya bisa membantu:\n- menjelaskan atau memeriksa usulan yang sedang direview;\n- memperbaiki usulan sesuai "
            "catatan Anda;\n- menjelaskan kenapa sistem ragu;\n- membuat draf angka baru, aturan baru, pencabutan, atau "
            "kebijakan perusahaan;\n- menjelaskan hasil kalkulator dan angka di knowledge base.\n\nSemua perubahan "
            "masuk ke *Review*; saya tidak menyetujui apa pun."), None


# ---------------------------------------------------------------- the model (OpenAI) and its actions
def _context(q):
    """What the model may use: the page, the numbers of the knowledge base with their source, the latest updates, the
    proposal under review, and the last calculator result. No employee name is sent."""
    s = st.session_state
    lines = [f"Page: {s.get('page_ctx', 'kelola')}. Today: {store.TODAY}. Knowledge base known until "
             f"{store.known_until()}."]
    lines.append("NUMBERS OF THE KNOWLEDGE BASE IN FORCE TODAY (parameter name | label | value | source):")
    for name in sorted(d.params()):
        r = d.param_at(name, store.TODAY)
        if r is not None:
            src = r.source[0] if r.source else None
            value = (d.money(r.value) if r.value_type == "money" else d.pct(r.value) if r.value_type == "rate"
                     else str(r.value))
            lines.append(f"- {name} | {d.fact_label(name)} | {value}"
                         f" | {d.short_doc(src.document) + ' ' + src.provision if src else '-'}")
    lines.append("LATEST UPDATES: " + "; ".join(f"{d.doc_title(u.document)} ({u.recorded_on})" for u in d.kb().updates[-5:]))
    pid, delta = _current_item()
    if delta:
        lines.append(f"PROPOSAL UNDER REVIEW ({pid}): " + _explain(pid, delta))
        for e in (delta.get("change", []) + delta.get("add", []))[:12]:
            src = (e.get("source") or [{}])[0]
            lines.append(f"- {e.get('kind')} {e.get('id')} {e.get('produces') or e.get('name') or ''}: "
                         f"{e.get('expression') or e.get('value') or ''} from {e.get('valid_from')} until "
                         f"{e.get('valid_until') or '-'}; source {src.get('provision', '')}: \"{src.get('quote', '')[:160]}\"")
    if s.get("k_last"):
        lines.append("LAST CALCULATOR RESULT: " + _calc_why().split("\n\n")[0])
    return "\n".join(lines)


def act(action, args, q):
    """Carry out the action the model picked, with the app's own code. Returns the text to add, or None."""
    pid, delta = _current_item()
    args = args or {}
    if action in ("explain_proposal", "check_proposal", "fix_proposal") and not delta:
        return "Pilih dulu usulan di tab *Review*."
    if action == "explain_proposal":
        return _explain(pid, delta)
    if action == "check_proposal":
        return _check(pid, delta)
    if action == "fix_proposal":
        st.session_state.mg_open, st.session_state.mg_fix = pid, pid
        st.session_state.setdefault("mg_prefill", {})[pid] = args.get("note") or q
        return ("Catatan Anda sudah saya isikan di *Review* → **Minta AI perbaiki**. Periksa catatannya, lalu tekan "
                "*Kirim ke AI*: perbaikan memakai kredit Claude dan hasilnya diperiksa G1–G5 lagi.")
    if action == "why_unsure":
        return _why_unsure(pid or "PKB-WIKA-2025")
    if action == "calc_why":
        return _calc_why()
    if action == "lookup":
        name = args.get("param") if args.get("param") in d.params() else _param(q)
        return _lookup(name) if name else None
    if action == "new_value":
        name = args.get("param") if args.get("param") in d.params() else _param(q)
        if not name or args.get("value") is None:
            return None
        try:
            start = date.fromisoformat(args.get("start")) if args.get("start") else date(store.TODAY.year + 1, 1, 1)
        except ValueError:
            start = date(store.TODAY.year + 1, 1, 1)
        value = args["value"]
        value = int(value) if float(value).is_integer() else value
        delta = drafts.new_value(name, value, start, "permintaan lewat asisten", "-", "")
        store.add_draft(delta["delta_id"], delta["document"]["title"], delta, "asisten")
        return (f"Draf angka baru: **{d.fact_label(name)} = {d.fmt(name, value)}** mulai {d.tgl(start)}; nilai lama "
                "berakhir sehari sebelumnya. Ada di tab *Review*. Tambahkan dokumen dan pasal dasarnya sebelum disetujui.")
    if action == "revoke":
        rule = drafts.find_rule(args.get("rule") or q)
        if not rule:
            return "Aturan itu tidak saya temukan. Sebutkan namanya, mis. \"cabut aturan bingkisan\"."
        delta = drafts.revoke(rule, date(store.TODAY.year, 12, 31), "permintaan lewat asisten", "-")
        store.add_draft(delta["delta_id"], delta["document"]["title"], delta, "asisten")
        return (f"Draf pencabutan **{d.fact_label(rule.produces)}** ({d.short_doc(rule.source[0].document)} "
                f"{rule.source[0].provision}) ada di tab *Review*, berlaku sampai 31 Desember {store.TODAY.year}.")
    if action == "meal_policy":
        n = int(args.get("amount") or 50_000)
        delta = drafts.meal_policy(n)
        store.add_draft(delta["delta_id"], delta["document"]["title"], delta, "asisten", inputs=[
            {"key": "hr.days_present", "label": "Hari hadir", "help": "Jumlah hari hadir bulan itu.", "type": "int",
             "group": "bulanan", "order": 65, "source": delta["document"]["title"]}])
        return (f"Draf kebijakan perusahaan **uang makan {d.money(n)} × hari hadir** ada di tab *Review*. Setelah "
                "disetujui, kolom *hari hadir* muncul sendiri di kalkulator.")
    return None


def answer(q, msgs):
    """The reply to a question: the model when one is chosen and usable, else the keyword matching."""
    model = st.session_state.get("as_model") or default_model()
    if model == OFFLINE:
        return reply(q)[0]
    ok, why = ai.ready("asisten")
    if not ok:
        return reply(q)[0] + f"\n\n*Tanpa AI: {why}.*"
    try:
        text, action, args, cost = ai.chat(q, msgs, _context(q), model=model)
    except Exception as e:  # noqa: BLE001 - the keyword matching still answers
        return reply(q)[0] + f"\n\n*Model tidak bisa dipakai ({type(e).__name__}); dijawab tanpa AI.*"
    extra = act(action, args, q) if action != "none" else None
    if extra and action not in ("new_value", "revoke", "meal_policy", "fix_proposal"):
        text = ""             # facts come from the knowledge base through the app's own text, not the model's wording
    return (text + (f"\n\n{extra}" if extra else "")).strip() + f"\n\n<sub>{model} · USD {cost:.4f}</sub>"


def default_model():
    return ai.ASSISTANT_MODEL if ai.ready("asisten")[0] else OFFLINE


# ---------------------------------------------------------------- pop-up
def _close():
    st.session_state.as_open = False


@st.dialog("Asisten AI", width="large", on_dismiss=_close)
def window():
    s = st.session_state
    msgs = store.chat_load()
    c1, c2 = st.columns([3, 1])
    if "as_model" not in s:
        s.as_model = default_model()
    c1.selectbox("Model", list(MODELS), key="as_model", format_func=lambda m: f"{m} · {MODELS[m]}",
                 label_visibility="collapsed")
    if c2.button("Hapus percakapan", icon=":material/delete:", width="stretch"):
        store.chat_clear()
        st.rerun(scope="fragment")
    st.caption(("Tanpa AI: jawaban dari pencocokan kata kunci." if s.as_model == OFFLINE else
                f"Model menerima angka KB, usulan yang direview, dan hasil kalkulator terakhir, tanpa nama pegawai. "
                f"{ai.budget_text('asisten')}") + " Asisten tidak menyetujui apa pun.")
    box = st.container(height=300)
    with box:
        if not msgs:
            st.caption("Belum ada percakapan.")
        for m in msgs:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
    page = s.get("page_ctx", "kelola")
    pick = st.pills("Contoh", SUGGEST.get(page, SUGGEST["kelola"]), key=f"as_pick_{len(msgs)}",
                    label_visibility="collapsed")
    q = st.chat_input("Tanya atau minta dikerjakan ...", key="as_in") or pick
    if q:
        with st.spinner("Asisten menjawab ..."):
            text = answer(q, msgs)
        msgs += [{"role": "user", "content": q}, {"role": "assistant", "content": text}]
        store.chat_save(msgs)
        st.rerun(scope="fragment")


def button():
    """Floating button, bottom right, on every page."""
    with st.container(key="fab"):
        if st.button("Asisten AI", icon=":material/forum:", type="primary"):
            st.session_state.as_open = True
    if st.session_state.get("as_open"):
        window()


def open_with(question):
    """Open the pop-up and ask a question (used by buttons on the pages)."""
    msgs = store.chat_load()
    text = answer(question, msgs)
    msgs = msgs + [{"role": "user", "content": question}, {"role": "assistant", "content": text}]
    store.chat_save(msgs)
    st.session_state.as_open = True
