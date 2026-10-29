"""AI assistant as a pop-up: a floating button on every page opens a separate chat window. The conversation is kept
when the window is closed (workspace/chat.json, also after a reload) and can be cleared. The model can be chosen;
the cheap one is the default.

What it does, by page:
- Knowledge base management: explain or check a proposal, ask the AI to fix it with your notes, explain why the
  system was unsure, draft a new rule, a new number, a revocation or a company policy. Drafts go to Review; the
  assistant never approves.
- Calculator: why a month's tax is what it is (from the engine's trace).
- Anywhere: look up a number of the knowledge base with its source.

Mockup: answers come from intent matching over the real knowledge base and the stored AI runs; checks, drafts and
lookups are real, the wording is prepared, and no API is called. "Fix with my notes" is simulated with the
research's reference answer and says so.
"""
import re
from datetime import date

import streamlit as st

import data as d
import demo
import drafts

MODELS = {"gpt-5.4-mini": "OpenAI · murah, bawaan (USD 0,75 / 4,50 per juta token)",
          "gpt-6.1-sol": "OpenAI · model kedua penelitian (USD 2 / 10)",
          "claude-opus-5-5": "Anthropic · model utama penelitian, paling mahal"}
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
    return pid, demo.proposal(pid)


def _explain(pid, delta):
    els = [e for e in delta.get("add", []) + delta.get("change", []) if e.get("kind") in ("rule", "parameter", "table")]
    touched = sorted({d.fact_label(e.get("produces") or e.get("name") or e["id"]) for e in els})
    starts = sorted({e.get("valid_from") for e in els if e.get("valid_from")})
    title = (delta.get("document") or {}).get("title", pid)
    return (f"**{title}** mengusulkan {len(delta.get('add', []))} tambahan dan {len(delta.get('change', []))} perubahan, "
            f"berlaku mulai {', '.join(starts[:3]) or '-'}. Nilai yang tersentuh: {', '.join(touched[:8])}.\n\n"
            "Buka tab *Review* untuk melihat contoh sebelum dan sesudahnya pada skenario umum.")


def _check(pid, delta):
    """Real check: is every quote in the document text, and does every number of a parameter appear in its quote?"""
    from pph21kbs.text import normalize, normalized
    lines, problems = [], 0
    for e in delta.get("add", []) + delta.get("change", []):
        for s in (e.get("source") or [])[:1]:
            doc = s.get("document")
            try:
                found = normalize(s.get("quote", "")) in normalized(doc)
            except Exception:  # noqa: BLE001 - document text not available
                found = None
            num_ok = True
            if e.get("kind") == "parameter" and e.get("value_type") == "money":
                digits = re.sub(r"\D", "", s.get("quote", ""))
                num_ok = str(int(float(e["value"]))) in digits
            mark = "✓" if found and num_ok else ("?" if found is None else "⚠")
            problems += mark == "⚠"
            what = d.fact_label(e.get("produces") or e.get("name") or e["id"])
            note = "" if found else " · kutipan tidak ditemukan di dokumen" if found is False else " · teks dokumen tidak ada"
            note += "" if num_ok else " · angka tidak ada di kutipan"
            lines.append(f"{mark} {what} ({s.get('provision', '')}){note}")
    head = ("Semua kutipan ada di dokumen dan angkanya cocok." if not problems else
            f"{problems} bagian perlu dicek manusia.")
    return (f"{head}\n\n" + "\n".join(f"- {x}" for x in lines[:14]) +
            "\n\nIni pendapat kedua, bukan keputusan. Kecocokan kutipan belum menjamin aturannya benar: periksa juga "
            "syarat dan rumusnya.")


def _why_unsure(pid):
    r = demo.run(pid)
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
    cur = [r for r in vs if r.valid_from <= demo.TODAY and (r.valid_until is None or demo.TODAY <= r.valid_until)]
    r = cur[-1] if cur else vs[-1]
    fmt = lambda v: d.money(v.value) if v.value_type == "money" else d.pct(v.value) if v.value_type == "rate" else v.value  # noqa: E731
    src = r.source[0]
    return (f"**{d.fact_label(name)}** menurut knowledge base sekarang: **{fmt(r)}**, berlaku sejak {d.tgl(r.valid_from)}."
            f"\n\nSumber: {d.short_doc(src.document)} {src.provision}, “{src.quote}”.\n\nRiwayat: "
            + ", ".join(f"{v.valid_from.year}: {fmt(v)}" for v in vs[-4:]) +
            f"\n\nKnowledge base demo diketahui sampai {d.tgl(demo.known_until())}.")


def _calc_why():
    last = st.session_state.get("k_last")
    if not last:
        return "Buka Kalkulator dan hitung dulu; saya menjelaskan dari hasil terakhir di sana."
    m = last["month"]
    due, gross = last["due"], last["gross"]
    prev = max((x for x in due if x < m), default=None)
    text = f"PPh {d.MONTHS[m - 1]}: **{d.money(due[m])}** dari bruto {d.money(gross[m])}."
    if prev:
        text += f" Bulan sebelumnya {d.money(due[prev])} dari bruto {d.money(gross[prev])}."
        if gross[m] != gross[prev]:
            text += (" Bedanya karena bruto berubah; tarif TER mengikuti besar bruto bulan itu, jadi THR, bonus, atau "
                     "lembur bisa menaikkan tarifnya.")
    if m == last["case"]["employment"]["end_month"]:
        text += " Bulan ini masa terakhir: pajak setahun dihitung ulang dengan Pasal 17 dan dikurangi yang sudah dipotong."
    return text + "\n\nRincian dan pasalnya ada di tab *Dasar hukum* di bawah hasil."


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
        ref = demo.gold_delta(pid)
        if not ref:
            return "Untuk usulan ini belum ada contoh perbaikan di demo.", None
        demo.set_fixed(pid, ref, q, "AI (simulasi)")
        return ("Catatan Anda saya kirim bersama usulan lama dan teks dokumen, lalu usulan disusun ulang dan diperiksa "
                "lagi. Versi baru sudah ada di tab *Review*.\n\n*Mockup: hasil perbaikan di demo ini memakai jawaban "
                "acuan penelitian; di sistem penuh ini satu putaran AI (± USD 0,1–0,8).*"), "perbaikan"
    if "ragu" in ql or "pkb" in ql:
        return _why_unsure("PKB-WIKA-2025" if "wika" in ql or not pid else pid), None
    if ("buat" in ql or "tambah" in ql) and ("per hari" in ql or "uang makan" in ql):
        amt = re.search(r"(\d+)\s*(ribu|rb|k)?", ql)
        n = int(amt.group(1)) * (1000 if amt and amt.group(2) else 1) if amt else 50_000
        delta = drafts.meal_policy(n)
        demo.add_draft(delta["delta_id"], delta["document"]["title"], delta, "asisten", inputs=[
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
        delta = drafts.revoke(rule, date(demo.TODAY.year, 12, 31), "permintaan lewat asisten", "-")
        demo.add_draft(delta["delta_id"], delta["document"]["title"], delta, "asisten")
        return (f"Draf pencabutan **{d.fact_label(rule.produces)}** ({d.short_doc(rule.source[0].document)} "
                f"{rule.source[0].provision}) sudah ada di tab *Review*, berlaku sampai 31 Desember {demo.TODAY.year}. "
                "Aturannya tidak dihapus, hanya diberi tanggal akhir, jadi hitungan lama tetap sama. Lengkapi dasar "
                "hukumnya sebelum disetujui."), "draf"
    if "menjadi" in ql:
        name = _param(q)
        num = re.search(r"rp\s*([\d.]+)", ql) or re.search(r"([\d.]{6,})", ql)
        year = re.search(r"\b(20\d\d)\b", ql)
        if name and num:
            value = int(num.group(1).replace(".", ""))
            start = date(int(year.group(1)) if year else demo.TODAY.year + 1, 1, 1)
            delta = drafts.new_value(name, value, start, "permintaan lewat asisten", "-", "")
            demo.add_draft(delta["delta_id"], delta["document"]["title"], delta, "asisten")
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
        for k, (lab, expl) in glossary.TERMS.items():
            if word and (word in k.lower() or word in lab.lower()):
                return f"**{lab}**: {expl}", None
    name = _param(q)
    if name and ("berapa" in ql or "nilai" in ql):
        return _lookup(name), None
    return ("Saya bisa membantu:\n- menjelaskan atau memeriksa usulan yang sedang direview;\n- memperbaiki usulan sesuai "
            "catatan Anda;\n- menjelaskan kenapa sistem ragu;\n- membuat draf angka baru, aturan baru, pencabutan, atau "
            "kebijakan perusahaan;\n- menjelaskan hasil kalkulator dan angka di knowledge base.\n\nSemua perubahan "
            "masuk ke *Review*; saya tidak menyetujui apa pun."), None


# ---------------------------------------------------------------- pop-up
def _close():
    st.session_state.as_open = False


@st.dialog("Asisten AI", width="large", on_dismiss=_close)
def window():
    s = st.session_state
    msgs = demo.chat_load()
    c1, c2 = st.columns([3, 1])
    c1.selectbox("Model", list(MODELS), key="as_model", format_func=lambda m: f"{m} · {MODELS[m]}",
                 label_visibility="collapsed")
    if c2.button("Hapus percakapan", icon=":material/delete:", width="stretch"):
        demo.chat_clear()
        st.rerun(scope="fragment")
    st.caption("Mockup: jawaban disusun tanpa memanggil API. Data pribadi pegawai tidak dikirim ke model.")
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
        text, action = reply(q)
        msgs += [{"role": "user", "content": q}, {"role": "assistant", "content": text}]
        demo.chat_save(msgs)
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
    text, _ = reply(question)
    msgs = demo.chat_load() + [{"role": "user", "content": question}, {"role": "assistant", "content": text}]
    demo.chat_save(msgs)
    st.session_state.as_open = True
