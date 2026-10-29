"""Assistant chat beside knowledge base management.

Design: gpt-5.4-mini (OpenAI; USD 0.75 / 4.50 per million input / output tokens, 400k context) with tools that read
the knowledge base (search rules, read a parameter, list versions, explain a review item) and tools that only write
drafts (add, change, revoke). Every change still goes through review.

In this mockup the answers come from simple intent matching over the real knowledge base: values and sources are
real, the wording is prepared. No API is called.
"""
import re

import streamlit as st

import data as d
import glossary as g

MODEL = "gpt-5.4-mini"
SUGGESTIONS = ["Berapa batas upah JP sekarang?", "Apa yang berubah di PMK 105/2025?", "Cabut aturan bingkisan",
               "Kenapa PKB WIKA ditahan?", "Buat aturan uang makan Rp50 ribu per hari"]


def _param_answer(q):
    ql = q.lower()
    best = None
    for name, p in d.params().items():
        label = d.fact_label(name).lower()
        words = [w for w in re.findall(r"[a-z]+", label) if len(w) > 2]
        score = sum(w in ql for w in words) + (3 if name.replace("_", " ") in ql else 0)
        if score and (best is None or score > best[0]):
            best = (score, name)
    if not best:
        return None
    name = best[1]
    vs = sorted((r for r in d.kb().records if r.kind == "parameter" and r.name == name), key=lambda r: r.valid_from)
    cur = [r for r in vs if r.valid_from <= d.TODAY and (r.valid_until is None or d.TODAY <= r.valid_until)]
    r = cur[-1] if cur else vs[-1]
    val = d.money(r.value) if r.value_type == "money" else d.pct(r.value) if r.value_type == "rate" else r.value
    src = r.source[0]
    fmt = lambda v: d.money(v.value) if v.value_type == "money" else d.pct(v.value) if v.value_type == "rate" else v.value  # noqa: E731
    hist = ", ".join(f"{v.valid_from.year}: {fmt(v)}" for v in vs[-4:])
    return (f"**{d.fact_label(name)}** saat ini **{val}**, berlaku sejak {d.tgl(r.valid_from)}.\n\n"
            f"Sumber: {d.short_doc(src.document)} {src.provision}, “{src.quote}”.\n\nRiwayat terakhir: {hist}.")


@st.cache_data
def _summary(event):
    """Plain summary of a gold update: counts and the values it touches."""
    import build_gold
    u = next(x for x in build_gold.collect() if x.event_id == event)
    j = u.to_json()
    touched = sorted({d.fact_label(el.get("produces") or el.get("name") or el["id"])
                      for el in j["add"] + j["change"] if el.get("kind") in ("rule", "parameter", "table")})
    extended = sum(1 for el in j["change"] if el.get("kind") == "rule" and el.get("valid_until"))
    return (f"**{d.doc_title(u.doc.id)}**: {len(j['add'])} tambahan dan {len(j['change'])} perubahan"
            + (f" ({extended} di antaranya mengubah masa berlaku)" if extended else "") + ". Nilai yang tersentuh: "
            + ", ".join(touched[:8]) + ". Usulannya ada di tab *Review*, lengkap dengan contoh dampak.")


def _rule_target(q):
    ql = q.lower()
    for r in d.kb().view(d.TODAY).rules.values():
        label = d.fact_label(r.produces).lower()
        if any(w in ql for w in re.findall(r"[a-z]{6,}", label)) and not d.is_input_convention(r):
            return r
    return None


def reply(q):
    """(text, action) for a question. action: None or (label, session updates)."""
    ql = q.lower()
    if any(w in ql for w in ("cabut", "hapus", "hentikan")):
        r = _rule_target(q)
        if r:
            return (f"Draf pencabutan untuk **{d.fact_label(r.produces)}** "
                    f"({d.short_doc(r.source[0].document)} {r.source[0].provision}) sudah saya siapkan di tab *Ubah atau "
                    "cabut*. Periksa tanggal akhir dan dasar hukumnya; aturan lama tidak dihapus, hanya diberi tanggal "
                    "akhir.", ("Buka draf pencabutan", {"mg_revoke_target": r.id, "mg_ch_act": "Cabut aturan"}))
        return "Aturan mana yang ingin dicabut? Sebutkan namanya, mis. \"cabut aturan natura kendaraan\".", None
    if any(w in ql for w in ("buat aturan", "tambah aturan", "uang makan", "tunjangan baru")):
        amt = re.search(r"(\d+)\s*(ribu|rb|k)?", ql)
        n = int(amt.group(1)) * (1000 if amt and amt.group(2) else 1) if amt else 50000
        return (f"Ini rancangan aturan perusahaan:\n\n> **Penghasilan teratur lain** = Rp{n:,} × hari hadir\n\n"
                .replace(",", ".") + "Jenis: kebijakan perusahaan, berlaku mulai 1 Januari tahun depan. Uang makan tunai "
                "termasuk penghasilan teratur, jadi menambah bruto. Saya masukkan sebagai draf ke Review?",
                ("Kirim draf ke Review", {"_draft": f"Uang makan dan transport Rp{n:,} per hari hadir".replace(",", ".")}))
    if "pkb" in ql or "ragu" in ql or "ditahan" in ql:
        return ("PKB WIKA ditahan karena dua versi usulan dari AI sama-sama lolos pemeriksaan otomatis, tetapi "
                "hasil hitungnya berbeda. Tidak ada yang lebih banyak, jadi sistem **ragu** dan tidak "
                "menebak. Di penelitian, AI belum pernah benar pada PKB, jadi aturan PKB sebaiknya ditulis lewat tab "
                "*Kebijakan perusahaan*. Saya bisa membantu menyusun dari pasal yang Anda tempel.", None)
    if "berubah" in ql or "ringkas" in ql or "pmk" in ql:
        if "105" in ql:
            return _summary("E11"), ("Buka review", {"mg_open": "E11"})
        u = d.kb().updates[-1]
        return (f"Pembaruan terakhir: **{d.doc_title(u.document)}**, dicatat {d.tgl(u.recorded_on)}. "
                "Lihat tab *Riwayat* untuk semua versi.", None)
    ans = _param_answer(q)
    if ans:
        return ans, None
    return ("Saya bisa membantu:\n- menjelaskan aturan, angka, dan sumbernya;\n- meringkas isi dokumen di kotak masuk;\n"
            "- menyiapkan draf tambah, ubah, atau cabut aturan (selalu lewat review Anda);\n- menjelaskan kenapa usulan "
            "ditahan atau ditolak.", None)


def panel():
    s = st.session_state
    s.setdefault("as_msgs", [{"role": "assistant", "content": "Halo, saya asisten knowledge base. Tanyakan aturan atau "
                                                              "minta saya menyiapkan draf perubahan."}])
    with st.container(border=True):
        g.md(f"**{g.term('asisten', 'Asisten KB')}** <span class='mock'>· {MODEL} · mockup, belum memanggil API</span>")
        box = st.container(height=420)
        with box:
            for i, m in enumerate(s.as_msgs):
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])
                    act = m.get("action")
                    if act and st.button(act[0], key=f"as_act_{i}", icon=":material/arrow_forward:"):
                        for k, v in act[1].items():
                            if k == "_draft":
                                s.mg_drafts.append({"title": v, "html": f"<div class='rule company'>{v}</div>"})
                            else:
                                s[k] = v
                        st.toast("Selesai. Lihat tab terkait.")
        pick = st.pills("Contoh pertanyaan", SUGGESTIONS, key="as_sugg", label_visibility="collapsed")
        q = st.chat_input("Tanya atau minta draf ...", key="as_in")
        q = q or (pick if pick and s.get("as_last_pick") != pick else None)
        if pick:
            s.as_last_pick = pick
        if q:
            text, action = reply(q)
            s.as_msgs.append({"role": "user", "content": q})
            s.as_msgs.append({"role": "assistant", "content": text, "action": action})
            st.rerun()
        st.caption("Asisten hanya membaca KB dan menyiapkan draf. Perubahan tetap lewat review.")
