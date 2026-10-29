"""Calculator v4 (mini_demo/RANCANGAN_KALKULATOR.md): one employee, one grid as the only source of numbers.

Rows are the months up to the month asked for; columns are the company's pay components and the other monthly data the
rules read. Everything the screen asks for comes from the knowledge base (inputs.py): the profile and company fields,
the kinds a pay component can be, the HR data columns, their labels and types, which components a company policy
computes, and the choices. Scenarios fill the form in company words; the employee can be saved and reopened, and is
told when the knowledge base changed its results.
"""
import json
import re
from datetime import date, datetime

import pandas as pd
import streamlit as st

import data as d
import demo
import employee as emp
import explain as ex
import glossary as g
import inputs
import ui


# ---------------------------------------------------------------- engine case
def case_of(rec, omega):
    """The case for the engine. When PPh 21 actually withheld is recorded and the employer pays the tax (method, or a
    company policy that sets it, read from the engine), the tax allowance of that month is recorded with it."""
    installed = rec.get("policy") in demo.installed_policies()
    case = emp.to_case(rec, policy_installed=installed)
    if not rec["withheld"]:
        return case
    r0, _ = d.compute(case, omega)
    method = (d.value(r0, "withholding_method") if r0 else None) or case["method"]
    pays = method != "gross" or bool(r0 and any(r0.periods[m].get("tax_allowance") for m in r0.periods))
    return emp.to_case(rec, policy_installed=installed, employer_pays_tax=pays)


# ---------------------------------------------------------------- record state
def _norm(rec):
    """The record as text, with empty cells left out (an empty cell and 0 mean the same)."""
    r = dict(rec)
    r["grid"] = {m: {c: v for c, v in row.items() if v not in (None, "", 0, False)} for m, row in rec["grid"].items()}
    r["grid"] = {m: row for m, row in r["grid"].items() if row}
    return json.dumps(r, sort_keys=True, default=str)


def _load(rec, origin):
    s = st.session_state
    s.rec = emp.copy_record(rec)
    s.rec_origin = origin                      # ("scenario", title) or ("saved", name)
    s.rec_clean = _norm(s.rec)
    s.rec_ver = s.get("rec_ver", 0) + 1


def _dirty():
    s = st.session_state
    return _norm(s.rec) != s.get("rec_clean")


def _apply_scenario(title):
    sc = emp.scenarios()[title]
    emp.ensure_components(sc)
    _load(emp.from_scenario(sc), ("scenario", title))


def _on_scenario():
    s = st.session_state
    title = s.get("k_scn_pick")
    if not title:
        return
    if _dirty():
        s.k_scn_pending = title
    else:
        _apply_scenario(title)
    s.k_scn_pick = None


def _on_open():
    s = st.session_state
    name = s.get("k_open_pick")
    saved = demo.load()["employees"].get(name)
    if saved:
        _load(saved["record"], ("saved", name))
    s.k_open_pick = None


def _save(name):
    s = st.session_state
    s.rec["name"] = name
    r, _ = d.compute(case_of(s.rec, s.k_omega_v), s.k_omega_v)
    found = inputs.discover(s.rec["year"], s.rec.get("policy"), s.k_omega_v)
    demo.save_employee(name, {"record": s.rec, "saved": datetime.now().strftime("%d/%m/%Y %H:%M"),
                              "approved": len(demo.load()["approved"]),
                              "last": {str(m): r.periods[m].get("pph21_due") for m in r.periods} if r else {},
                              "keys": sorted(found)})
    s.rec_origin = ("saved", name)
    s.rec_clean = _norm(s.rec)


# ---------------------------------------------------------------- top bar
def top_bar():
    s = st.session_state
    rec = s.rec
    saved = demo.load()["employees"]
    c = st.columns([1.3, 1.3, 1, 1])
    who = rec["name"] or "Pegawai baru"
    origin = s.rec_origin
    c[0].markdown(f"**{who}**{' ●' if _dirty() else ''}  \n<span class='muted'>"
                  + ("dari skenario: " + origin[1] if origin[0] == "scenario" else "pegawai tersimpan") + "</span>",
                  unsafe_allow_html=True, help="● = ada perubahan yang belum disimpan.")
    c[1].selectbox("Isi dengan skenario umum", list(emp.scenarios()), index=None, key="k_scn_pick",
                   placeholder="Pilih skenario…", on_change=_on_scenario,
                   help="Mengisi form ini dengan contoh lengkap; setelah itu semua bisa diubah.")
    c[2].selectbox("Buka pegawai tersimpan", list(saved), index=None, key="k_open_pick", placeholder="Pilih…",
                   on_change=_on_open, disabled=not saved)
    with c[3]:
        st.write("")
        with st.popover("Simpan", icon=":material/save:", width="stretch"):
            name = st.text_input("Nama pegawai", rec["name"], key=f"k_save_name_{s.rec_ver}")
            if st.button("Simpan", type="primary", key="k_save_btn") and name.strip():
                _save(name.strip())
                st.rerun()
    if s.get("k_scn_pending"):
        with st.container(border=True):
            st.warning(f"Ada perubahan yang belum disimpan. Isi form dengan skenario **{s.k_scn_pending}**?",
                       icon=":material/warning:")
            b1, b2, _ = st.columns([1, 1, 3])
            if b1.button("Ya, ganti", type="primary"):
                _apply_scenario(s.k_scn_pending)
                s.k_scn_pending = None
                st.rerun()
            if b2.button("Batal"):
                s.k_scn_pending = None
                st.rerun()
    sc = emp.scenarios().get(origin[1]) if origin[0] == "scenario" else None
    if sc:
        st.caption(f"**{sc['title']}**: {sc['note']}")


def period_bar():
    s = st.session_state
    rec = s.rec
    v = s.rec_ver
    c = st.columns(5)
    ys = inputs.years()
    rec["year"] = c[0].selectbox("Tahun pajak", ys, index=ys.index(rec["year"]) if rec["year"] in ys else len(ys) - 2,
                                 key=f"k_year_{v}")
    rec["start"] = c[1].selectbox("Mulai bekerja", range(1, 13), index=rec["start"] - 1, key=f"k_start_{v}",
                                  format_func=lambda m: d.MONTHS[m - 1], help="Bulan pertama digaji tahun ini.")
    ends = list(range(rec["start"], 13))
    rec["end"] = c[2].selectbox("Bekerja sampai", ends, index=ends.index(rec["end"]) if rec["end"] in ends else len(ends) - 1,
                                key=f"k_end_{v}", format_func=lambda m: "Desember (masih bekerja)" if m == 12
                                else d.MONTHS[m - 1] + " (keluar)",
                                help="Bulan keluar menjadi bulan penutup: pajak setahun dihitung ulang di bulan itu.")
    months = list(range(rec["start"], rec["end"] + 1))
    rec["month"] = c[3].selectbox("Hitung sampai bulan", months,
                                  index=months.index(rec["month"]) if rec["month"] in months else len(months) - 1,
                                  key=f"k_month_{v}",
                                  format_func=lambda m: d.MONTHS[m - 1] + (" · penutup" if m == rec["end"] else ""),
                                  help="Hasil ditampilkan dari bulan pertama sampai bulan ini. Hitung setahun hanya "
                                       "muncul di bulan penutup (Desember atau bulan keluar).")
    s.k_omega_v = c[4].date_input("Aturan per tanggal", demo.TODAY, key="k_omega",
                                  help="Hitung memakai aturan yang sudah dikenal sistem pada tanggal ini. Berguna "
                                       "untuk melihat hitungan lama sebelum ada aturan yang berlaku surut. "
                                       f"Knowledge base demo dikenal sampai {d.tgl(demo.known_until())}.")


# ---------------------------------------------------------------- profile and company (from the knowledge base)
def _field(key, rec, year, v):
    tp = inputs.kind(key)
    lab = inputs.label(key)
    df = inputs.definition(key) or {}
    if df.get("show_if"):
        for k2, val in df["show_if"].items():
            if rec["fields"].get(k2) != val:
                return
    if df.get("origin", "keadaan awal") != "keadaan awal":
        lab += f" · baru ({df['origin']})"
    if not inputs.has_def(key):
        lab += " ⚠"
    cur = rec["fields"].get(key, inputs.default(key))
    wkey = f"k_f_{key}_{v}"
    hp = inputs.help_text(key)
    if tp == "choice":
        opts = inputs.options(key, year)
        values = [o[0] for o in opts]
        names = dict(opts)
        val = st.selectbox(lab, values, index=values.index(cur) if cur in values else 0, key=wkey,
                           format_func=lambda x: names.get(x, x), help=hp) if values else None
    elif tp in ("bool", "flag"):
        val = st.toggle(lab, bool(cur), key=wkey, help=hp)
    elif tp == "text":
        val = st.text_input(lab, cur or "", key=wkey, help=hp)
    else:
        val = st.number_input(lab, 0, 10**11, int(cur) if cur not in (None, "") else None, key=wkey, help=hp,
                              placeholder="kosong", step=1 if tp == "int" else 100_000)
    rec["fields"][key] = val


def profile():
    s = st.session_state
    rec, v = s.rec, s.rec_ver
    year, omega = rec["year"], s.k_omega_v
    with st.expander("Pegawai dan perusahaan", expanded=True):
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("**Pegawai**")
            rec["name"] = st.text_input("Nama", rec["name"], key=f"k_name_{v}")
            keys = inputs.profile_fields("pegawai", year, rec.get("policy"), omega)
            core = [k for k in keys if (inputs.definition(k) or {}).get("core")]
            more = [k for k in keys if k not in core]
            for k in core:
                _field(k, rec, year, v)
            with st.expander(f"Data pegawai lain yang dibaca aturan tahun ini ({len(more)})"):
                st.caption("Daftar ini dibentuk dari knowledge base: setiap data dibaca paling tidak oleh satu aturan "
                           f"yang berlaku tahun {year}.")
                for k in more:
                    _field(k, rec, year, v)
        with right:
            st.markdown("**Perusahaan**")
            pols = demo.installed_policies()
            opts = [""] + list(pols)
            cur = rec.get("policy") if rec.get("policy") in pols else ""
            pick = st.selectbox("Kebijakan perusahaan", opts, index=opts.index(cur), key=f"k_pol_{v}",
                                format_func=lambda p: "Tidak ada" if not p else f"{p} · {pols[p]}",
                                help=g.tip("kebijakan perusahaan") + " Hanya kebijakan yang sudah disetujui di Manajemen KB.")
            if rec.get("policy") and rec["policy"] not in pols:
                st.info(f"Form ini memakai kebijakan **{rec['policy']}**, yang belum ada di knowledge base. Setujui dulu "
                        "di Manajemen KB; kolom datanya akan muncul sendiri.", icon=":material/info:")
            else:
                rec["policy"] = pick or None
            keys = inputs.profile_fields("perusahaan", year, rec.get("policy"), omega)
            core = [k for k in keys if (inputs.definition(k) or {}).get("core")]
            more = [k for k in keys if k not in core]
            for k in core:
                _field(k, rec, year, v)
            klu = rec["fields"].get("employer.klu")
            if klu:
                lists = _lookup_tables("employer('klu')", year, omega)
                hit = [(n, rid) for n, rid in lists if klu in inputs.table_keys(n, year)]
                if not lists:
                    st.caption(f"Tidak ada aturan tahun {year} yang memakai KLU.")
                else:
                    def names(xs):
                        tabs = {n: d.table_at(n, date(year, 12, 31)) or d.table_at(n, date(year, 1, 1)) for n, _ in xs}
                        return ", ".join(f"'{(tabs[n].label_id if tabs[n] and tabs[n].label_id else n)}' ({rid})"
                                         for n, rid in xs)
                    st.caption(f"KLU {klu} " + (f"ada di daftar {names(hit)} tahun {year}." if hit else
                                                f"tidak ada di daftar yang dipakai aturan tahun {year}: {names(lists)}."))
            with st.expander(f"Data perusahaan lain yang dibaca aturan ({len(more)})"):
                for k in more:
                    _field(k, rec, year, v)


def _lookup_tables(read, year, omega):
    """(table, rule) for every table that a rule in force in the year looks this input up in, e.g. the KLU lists of
    the DTP rules. Read from the rules, so a new list in the knowledge base is found without changing the program."""
    lo, hi = date(year, 1, 1), date(year, 12, 31)
    out = []
    for r in d.kb().view(omega).rules.values():
        if (r.valid_from and r.valid_from > hi) or (r.valid_until and r.valid_until < lo):
            continue
        text = " ".join(e.text for e in (r.expression, r.condition) if e is not None)
        for name in re.findall(r"in_table\('([a-z0-9_]+)',\s*" + re.escape(read), text):
            out.append((name, r.id))
    return out


# ---------------------------------------------------------------- the grid
def _auto(key, r, shown):
    """When the rules compute this data in the months shown (the winning rule is not the one that reads the admin's
    input), its values and the rules that computed it; read from the engine's trace, so it follows the knowledge base."""
    rule = inputs.input_rules().get(key)
    if r is None or not rule:
        return None
    rid, fact = rule
    vals, by = {}, {}
    for m in shown:
        t = (r.trace or {}).get((fact, m))
        if t:
            vals[m] = int(t["value"] or 0)
            if t["rule"] != rid:
                by[t["rule"]] = t["layer"]
    return {"fact": fact, "vals": vals, "by": by} if by else None


def _columns(rec, omega, r):
    """[(col id, label, key, state)] state: edit | computed | unused | retired | nodef; and the computed values."""
    year, policy = rec["year"], rec.get("policy")
    cat = {**rec.get("component_keys", {}), **emp.catalog()}
    found = inputs.discover(year, policy, omega)
    shown = list(range(rec["start"], rec["month"] + 1))
    cols, autos = [], {}
    for name in rec["components"]:
        key = cat.get(name)
        state = "edit"
        a = _auto(key, r, shown) if key else None
        if a:
            state, autos[name] = "computed", a
        elif key and inputs.retired(key, date(year, rec["month"], 1)):
            state = "retired"
        elif key not in found or not any(m in found[key]["months"] for m in shown):
            state = "unused"
        cols.append((name, name, key, state))
    mapped = {cat.get(n) for n in rec["components"]}
    for key in inputs.component_kinds(year, policy, omega):      # computed by the rules, not entered: shown, locked
        if key in mapped:
            continue
        a = _auto(key, r, shown)
        if a and any(a["vals"].values()):
            col = f"auto:{key}"
            autos[col] = a
            cols.append((col, d.fact_label(a["fact"]), key, "computed"))
    for key in inputs.monthly_data(year, policy, omega):
        cols.append((f"data:{key}", inputs.label(key), key, "edit" if inputs.has_def(key) else "nodef"))
    return cols, found, autos


def _range_note(found, key, shown):
    ms = [m for m in shown if key in found and m in found[key]["months"]]
    if not ms or len(ms) == len(shown):
        return ""
    return f" ({d.MON[ms[0] - 1]}–{d.MON[ms[-1] - 1]})"


def grid(prev_result):
    s = st.session_state
    rec, v = s.rec, s.rec_ver
    omega = s.k_omega_v
    shown = list(range(rec["start"], rec["month"] + 1))
    cols, found, autos = _columns(rec, omega, prev_result)
    with st.container(border=True):
        h1, h2, h3 = st.columns([3, 1, 1])
        h1.markdown(f"**Rincian per bulan** · {d.MONTHS[shown[0] - 1]}–{d.MONTHS[shown[-1] - 1]} {rec['year']}")
        h1.caption("Klik dua kali sel untuk mengubah angka, lalu Enter. Angka dicatat di bulan dibayarnya. Kolom berasal "
                   "dari komponen gaji perusahaan dan data yang dibaca aturan tahun ini.")
        with h2.popover("Komponen", icon=":material/add:", width="stretch"):
            add_component(rec, shown)
        with h3.popover("Isi cepat", icon=":material/auto_fix_high:", width="stretch"):
            quick_fill(rec, cols, shown)
        table, cfg = [], {"Bulan": st.column_config.TextColumn("Bulan", disabled=True)}
        for m in shown:
            row = {"Bulan": d.MONTHS[m - 1]}
            for col, lab, key, state in cols:
                tp = inputs.kind(key) if key else "money"
                if state == "computed":
                    row[col] = autos[col]["vals"].get(m, 0)
                else:
                    val = emp.cell(rec, m, col)
                    row[col] = bool(val) if tp == "flag" else (val if tp == "choice" else (val or 0))
            row["PPh sudah dipotong"] = rec["withheld"].get(str(m)) if m < rec["month"] else None
            table.append(row)
        for col, lab, key, state in cols:
            tp = inputs.kind(key) if key else "money"
            hp = inputs.help_text(key) if key else "Komponen ini belum dipetakan ke data knowledge base."
            if state == "computed":
                by = autos[col]["by"]
                who = ("kebijakan perusahaan " + str(rec.get("policy"))) if "company" in by.values() else "aturan"
                title = f"{lab} ⚙"
                hp = (f"Dihitung otomatis oleh {who} ({', '.join(list(by)[:3])}), tidak bisa diketik. Untuk mengubahnya, "
                      "ubah data yang dibaca aturan itu (mis. gaji, risiko pekerjaan, atau data HR).")
            elif state == "unused":
                title = f"{lab} (tidak dibaca aturan)"
            elif state == "retired":
                title = f"{lab} (tidak dipakai lagi)"
            elif state == "nodef":
                title = f"{lab} ⚠"
            else:
                title = f"{lab} ✎" + _range_note(found, key, shown)
            dis = state == "computed"
            if tp == "flag":
                cfg[col] = st.column_config.CheckboxColumn(title, help=hp, disabled=dis)
            elif tp == "choice":
                cfg[col] = st.column_config.SelectboxColumn(title, help=hp, disabled=dis,
                                                            options=[o[0] for o in inputs.options(key, rec["year"])])
            else:
                cfg[col] = st.column_config.NumberColumn(title, help=hp, disabled=dis, min_value=0, format="localized",
                                                         step=1)
        cfg["PPh sudah dipotong"] = st.column_config.NumberColumn(
            "PPh sudah dipotong ✎", format="localized", min_value=0,
            help="Isi hanya bila PPh yang benar-benar dipotong bulan itu berbeda dari hitungan sistem (mis. dulu "
                 "dihitung sistem lama). Dipakai di bulan penutup.")
        sig = "|".join(c[0] for c in cols)
        auto_sig = hash(tuple(sorted((c, tuple(sorted(a["vals"].items()))) for c, a in autos.items())))
        gkey = f"k_grid_{v}_{rec['year']}_{rec['start']}_{rec['month']}_{hash(sig)}_{auto_sig}"
        # the editor keeps the user's edits relative to the data it was first given: give it the same data while its
        # key is the same; a new key (other columns, or new values computed by the rules) starts from the record
        if s.get("k_grid_base", (None,))[0] != gkey:
            s.k_grid_base = (gkey, table)
        frame = pd.DataFrame(s.k_grid_base[1])
        locked = [c[0] for c in cols if c[3] == "computed"]
        idle = [c[0] for c in cols if c[3] in ("unused", "retired")]
        styled = (frame.style
                  .set_properties(subset=["Bulan"], **{"background-color": "#f7f7f5", "font-weight": "600"})
                  .set_properties(subset=locked, **{"background-color": "#ecebe7", "color": "#6b6a66"})
                  .set_properties(subset=idle, **{"background-color": "#fff4d6", "color": "#8a6100"}))
        edited = st.data_editor(styled, key=gkey, hide_index=True, width="stretch", column_config=cfg)
        for m, (_, r) in zip(shown, edited.iterrows()):
            rowrec = rec["grid"].setdefault(str(m), {})
            for col, lab, key, state in cols:
                if state == "computed":
                    continue
                val = r[col]
                tp = inputs.kind(key) if key else "money"
                if tp == "flag":
                    rowrec[col] = 1 if val else 0
                elif tp == "choice":
                    rowrec[col] = val if isinstance(val, str) and val else None
                else:
                    rowrec[col] = int(val) if pd.notna(val) and val != "" else 0
            w = r["PPh sudah dipotong"]
            if m < rec["month"] and pd.notna(w) and w != "":
                rec["withheld"][str(m)] = int(w)
            else:
                rec["withheld"].pop(str(m), None)
        if any(c[3] == "computed" for c in cols):
            st.caption("⚙ = dihitung otomatis oleh aturan dari data lain; tampil untuk dilihat, tidak bisa diketik.")
    return cols, found, autos


def add_component(rec, shown):
    s = st.session_state
    year = rec["year"]
    cat = emp.catalog()
    existing = [n for n in cat if n not in rec["components"]]
    mode = st.radio("Komponen", ["Baru", "Dari daftar perusahaan"] if existing else ["Baru"], horizontal=True,
                    key="k_add_mode")
    if mode == "Baru":
        name = st.text_input("Nama komponen", key="k_add_name", placeholder="mis. Tunjangan komunikasi")
        kinds = inputs.component_kinds(year, rec.get("policy"), s.k_omega_v)
        key = st.selectbox("Apa ini?", kinds, key="k_add_kind", format_func=inputs.label,
                           help="Pilih yang paling sesuai dengan sifat komponen ini. Daftarnya diambil dari data yang "
                                "dibaca aturan tahun ini; cara pajaknya diputuskan aturan, bukan oleh pilihan ini.")
        if key:
            st.caption(inputs.help_text(key))
    else:
        name = st.selectbox("Komponen", existing, key="k_add_existing")
        key = cat.get(name)
        st.caption(f"Dipetakan ke: {inputs.label(key)}")
    c1, c2 = st.columns(2)
    value = c1.number_input("Nilai", 0, 10**11, 0, 50_000, key="k_add_value")
    start = c2.selectbox("Mulai bulan", shown, key="k_add_start", format_func=lambda m: d.MONTHS[m - 1])
    repeat = st.checkbox("Dibayar setiap bulan sejak itu",
                         bool((inputs.definition(key) or {}).get("repeat")) if key else True, key=f"k_add_repeat_{key}")
    if st.button("Tambahkan", type="primary", key="k_add_btn", disabled=not (name and key)):
        if mode == "Baru":
            demo.add_component(name, key)
        if name not in rec["components"]:
            rec["components"].append(name)
        for m in range(start, rec["end"] + 1):
            if m == start or repeat:
                rec["grid"].setdefault(str(m), {})[name] = int(value)
        s.rec_ver += 1
        st.rerun()
    if rec["components"]:
        st.divider()
        keep = st.multiselect("Komponen yang ditampilkan", rec["components"], rec["components"],
                              key=f"k_keep_{s.rec_ver}")
        if st.button("Terapkan", key="k_keep_btn") and keep != rec["components"]:
            rec["components"] = keep
            s.rec_ver += 1
            st.rerun()


def quick_fill(rec, cols, shown):
    s = st.session_state
    editable = [c for c in cols if c[3] in ("edit", "nodef", "unused")]
    if not editable:
        st.caption("Tidak ada kolom yang bisa diisi.")
        return
    labels = {c[0]: c[1] for c in editable}
    col = st.selectbox("Kolom", list(labels), format_func=labels.get, key="k_qf_col")
    key = next(c[2] for c in editable if c[0] == col)
    tp = inputs.kind(key) if key else "money"
    start = st.selectbox("Mulai bulan", shown, key="k_qf_start", format_func=lambda m: d.MONTHS[m - 1])
    modes = ["Isi sama sampai bulan terakhir", "Hanya bulan ini"] + (["Naik 1 tiap bulan"] if tp == "int" else [])
    mode = st.radio("Cara", modes, key="k_qf_mode")
    value = 1 if tp == "flag" else st.number_input("Nilai", 0, 10**11, 0, 1 if tp == "int" else 50_000, key="k_qf_value")
    if st.button("Isi", type="primary", key="k_qf_btn"):
        for i, m in enumerate(range(start, rec["end"] + 1)):
            if mode == "Hanya bulan ini" and m != start:
                break
            rec["grid"].setdefault(str(m), {})[col] = int(value) + (i if mode == "Naik 1 tiap bulan" else 0)
        s.rec_ver += 1
        st.rerun()


# ---------------------------------------------------------------- results
def _label(f):
    """The fact's label from the KB, with a hover explanation when the glossary has one."""
    key = g.FOR_FACT.get(f)
    return g.term(key, d.fact_label(f)) if key else d.fact_label(f)


def _components(rec, cols, m):
    """Input fact -> names of the company components (and their values) that feed it in month m."""
    fact_of = {k: fact for k, (_, fact) in inputs.input_rules().items()}
    out = {}
    for col, lab, key, state in cols:
        val = emp.cell(rec, m, col) if state != "computed" else None
        if key in fact_of and val:
            out.setdefault(fact_of[key], []).append((lab, val))
    return out


def _parts(r, key, omega, depth=0):
    """A subtotal split into the non-zero values it adds up, as deep as the formulas are plain sums."""
    kids = [k for k in ex.children(r, key, omega) if k[1] == key[1] and ex._number(ex.value(r, k))]
    if depth < 4 and kids and sum(ex.value(r, k) for k in kids) == ex.value(r, key):
        return [p for k in kids for p in _parts(r, k, omega, depth + 1)]
    return [key]


def _line(r, k, comps, op=""):
    f = k[0]
    names = comps.get(f) or []
    note = ""
    if names and not (len(names) == 1 and names[0][0].lower() == d.fact_label(f).lower()):
        note = " <span class='muted'>(" + ", ".join(n for n, _ in names) + ")</span>"
    return (f"<tr class='sub'><td>{op}</td><td>{_label(f)}{note}</td>"
            f"<td class='r'>{d.fmt(f, ex.value(r, k))}</td></tr>")


def month_card(r, rec, cols, m, omega):
    """The PPh 21 of month m, explained by the rules that computed it (read from the trace)."""
    root = (ex.ROOT, m)
    due = ex.value(r, root)
    work = ex.working(r, root, omega)
    rule = ex.rule(r, work, omega)
    comps = _components(rec, cols, m)
    rows = []
    kids = ex.children(r, work, omega)
    split = {k: (_parts(r, k, omega) if k[1] == m else [k]) for k in kids}
    for k in sorted(kids, key=lambda k: len(split[k]) == 1):      # subtotals with their parts first, in formula order
        v = ex.value(r, k)
        if v in (None, ""):
            continue
        parts = split[k]
        if len(parts) > 1:
            rows += [_line(r, p, comps, "+") for p in parts]
            rows.append(f"<tr><td class='op'>=</td><td>{_label(k[0])}</td><td class='r'>{d.fmt(k[0], v)}</td></tr>")
        else:
            rows.append(f"<tr><td class='op'></td><td>{_label(k[0])}" + ("" if k[1] == m else
                        " <span class='muted'>(setahun)</span>") + f"</td><td class='r'>{d.fmt(k[0], v)}</td></tr>")
    rows.append(f"<tr class='sub'><td></td><td colspan=2><span class='muted'>Rumus: {d.readable(rule.expression)}"
                f"</span></td></tr>" if rule is not None else "")
    rows.append(f"<tr class='total'><td class='op'>=</td><td>{g.term('PPh 21')} {d.MONTHS[m - 1]}</td>"
                f"<td class='r'>{d.money(due)}</td></tr>")
    for f in ex.downstream(r, m, omega):
        v = ex.value(r, (f, m))
        if ex._number(v):
            rows.append(f"<tr class='sub'><td>·</td><td>{_label(f)}</td><td class='r'>{d.fmt(f, v)}</td></tr>")
    final = not r.partial and r.final_month == m
    src = ex.source_of(r, work)
    where = f"{d.short_doc(src['document'])} {src['provision']}" if src else ""
    badge = (ui.badge("Bulan penutup", "orange") + g.term("masa terakhir", "apa ini?") if final
             else ui.badge(f"Bulan biasa · {d.short_doc(src['document'])}" if src else "Bulan biasa", "blue"))
    expl = (f"Dihitung dengan aturan <code>{rule.id if rule else '-'}</code> ({where})."
            + (" Pajak setahun dihitung ulang di kartu di bawah." if final else ""))
    neg = due is not None and due < 0
    ui.html(f"<div class='card'><h4>{'Lebih bayar' if neg else 'PPh 21'} · {d.MONTHS[m - 1]} {rec['year']}</h4>{badge}"
            f"<div class='big{' neg' if neg else ''}'>{d.money(abs(due) if neg else due)}</div>"
            f"<table class='lines'>{''.join(rows)}</table><div class='explain'>{expl}</div></div>")
    return [work] + ex.children(r, work, omega)


def year_card(r, rec, omega):
    """The year calculation of the final month: every year value under the PPh of the final month, from the first
    step to the result, each with the formula of its rule. Read from the trace, not from a fixed list."""
    end = r.final_month
    top = ex.working(r, (ex.ROOT, end), omega)
    steps = ex.ladder(r, top, omega)
    rows = []
    for k, level in steps:
        rl = ex.rule(r, k, omega)
        has = any(c[1] == 0 for c in ex.children(r, k, omega))
        formula = (f"<br><span class='muted'>{d.readable(rl.expression)}</span>" if rl is not None and has else "")
        cls = " class='total'" if k == top else ""
        rows.append(f"<tr{cls}><td class='op'>{'=' if has else ''}</td><td>{_label(k[0])}{formula}</td>"
                    f"<td class='r'>{d.fmt(k[0], ex.value(r, k))}</td></tr>")
    v = ex.value(r, top)
    note = ""
    if rec["withheld"]:
        note = ("PPh yang sudah dipotong memakai isian 'PPh sudah dipotong' untuk bulan "
                + ", ".join(d.MON[int(x) - 1] for x in sorted(rec["withheld"], key=int)) + "; bulan lain dari hitungan sistem.")
    if end < 12:
        note += f" Pegawai keluar di {d.MONTHS[end - 1]}: bulan itu bulan penutup."
    if isinstance(v, (int,)) or hasattr(v, "denominator"):
        note = (f"{g.term('kurang bayar') if v >= 0 else g.term('lebih bayar')} {d.MONTHS[end - 1]}: "
                f"<b>{d.money(abs(v))}</b>. " + note)
    ui.html(f"<div class='card'><h4>Hitung ulang setahun {rec['year']}</h4><table class='lines'>{''.join(rows)}</table>"
            + (f"<div class='explain'>{note}</div>" if note else "") + "</div>")
    return [k for k, _ in steps]


def warnings(r, rec, cols, found):
    """Shows the warnings; returns True when results must not be shown."""
    shown = list(range(rec["start"], rec["month"] + 1))
    blocking = [f"Komponen **{lab}** dipetakan ke data yang tidak dipakai lagi ({inputs.label(key)}). Pilih jenis baru "
                "lewat '+ Komponen' supaya penghasilannya tidak hilang dari bruto."
                for col, lab, key, state in cols if state == "retired" and any(emp.cell(rec, m, col) for m in shown)]
    for b in blocking:
        st.error(b, icon=":material/block:")
    out = []
    for col, lab, key, state in cols:
        if not key:
            out.append(f"Komponen **{lab}** belum dipetakan ke data knowledge base; tidak dihitung.")
            continue
        if state == "unused" and any(emp.cell(rec, m, col) for m in shown):
            out.append(f"**{lab}** diisi, tetapi tidak dibaca aturan yang berlaku di bulan-bulan ini; tidak dihitung.")
        if col.startswith("data:") and key in found and found[key]["layer"] == "company"                 and inputs.kind(key) in ("int", "choice", "money"):
            need = [] if (inputs.definition(key) or {}).get("optional") else [m for m in shown if m in found[key]["months"]]
            if need and all(emp.cell(rec, m, col) in (None, "", 0) for m in need):
                out.append(f"**{lab}** dibaca aturan ({', '.join(found[key]['rules'][:2])}) tetapi kosong; dihitung 0.")
        if state == "nodef":
            out.append(f"**{lab}**: definisi data ini belum ada di knowledge base; nama dan tipenya diambil dari aturan.")
    if r is not None:
        eff = d.value(r, "ptkp_status_effective")
        if eff and eff != rec["fields"].get("employee.ptkp_status"):
            out.append(f"Status PTKP yang dipakai **{eff}**: karyawati kawin memakai PTKP tidak kawin kecuali ada keterangan "
                       "suami tidak berpenghasilan.")
        cat = {**rec.get("component_keys", {}), **emp.catalog()}
        names = {}
        for n, k in cat.items():
            names.setdefault(k.split(".", 1)[1], []).append(n)
        for w in r.warnings:
            if str(w).startswith("UnreadInput"):
                k = str(w).split("(")[1].rstrip(")").split(".", 1)[1]
                who = ", ".join(n for n in names.get(k, [k]) if n in rec["components"]) or k
                out.append(f"**{who}** diisi, tetapi tidak dipakai dalam hitungan ini (syarat aturannya tidak terpenuhi).")
    for n in out:
        st.info(n, icon=":material/lightbulb:")
    return bool(blocking)


def changed_banner(r, rec):
    s = st.session_state
    if s.rec_origin[0] != "saved" or r is None:
        return
    saved = demo.load()["employees"].get(s.rec_origin[1])
    if not saved:
        return
    approved = demo.load()["approved"][saved["approved"]:]
    found = inputs.discover(rec["year"], rec.get("policy"), s.k_omega_v)
    new_keys = [k for k in found if k not in saved["keys"]]
    if new_keys:
        st.warning("Data baru dibutuhkan sejak pegawai ini disimpan: " + ", ".join(
            f"**{inputs.label(k)}** ({(inputs.definition(k) or {}).get('origin', 'aturan baru')})" for k in new_keys)
            + ". Nilai bawaan dipakai sampai diisi.", icon=":material/new_releases:")
    changed = [(int(m), old, r.periods[int(m)].get("pph21_due")) for m, old in saved["last"].items()
               if int(m) in r.periods and int(m) <= rec["month"] and old != r.periods[int(m)].get("pph21_due")]
    if changed and approved:
        st.warning(f"Hasil berubah sejak disimpan ({saved['saved']}) karena pembaruan: "
                   + ", ".join(a["title"] for a in approved) + ". "
                   + "; ".join(f"{d.MON[m - 1]}: {d.money(o)} → {d.money(n)}" for m, o, n in changed[:6]),
                   icon=":material/update:")


def basis(r, nodes):
    """The rules behind the values shown in the cards, with what they read and their article and quote."""
    seen = set()
    for key in nodes:
        t = (r.trace or {}).get(key)
        if not t or key in seen or ex.is_input(r, key) or t["value"] in (None, 0):
            continue
        seen.add(key)
        f, mm = key
        src = t["source"][0] if t["source"] else None
        reads = ", ".join(d.fact_label(k[0]) for k in ex.children(r, key, st.session_state.k_omega_v)[:6])
        layer = ui.badge("kebijakan perusahaan", "orange") if t["layer"] == "company" else ""
        ui.html(f"<div class='rule{' company' if t['layer'] == 'company' else ''}'>{layer}<b>{d.fact_label(f)}</b> = "
                f"{d.fmt(f, t['value'])} <span class='muted'>({'bulan ' + d.MONTHS[mm - 1] if mm else 'setahun'})</span><br>"
                f"<span class='muted'>Membaca: {reads or '-'} · {g.term('sumber', 'Sumber')}: "
                f"{d.short_doc(src['document']) + ' · ' + src['provision'] if src else '-'} · aturan <code>{t['rule']}</code>"
                f"</span>" + (f"<div class='quote'>“{src['quote']}”</div>" if src else "") + "</div>")


def results(rec, cols, found, autos):
    s = st.session_state
    case = case_of(rec, s.k_omega_v)
    r, err = d.compute(case, s.k_omega_v)
    changed_banner(r, rec)
    blocked = warnings(r, rec, cols, found)
    if err:
        st.error(f"Perhitungan gagal: {err}")
        return
    if blocked:
        return
    m = rec["month"]
    omega = s.k_omega_v
    shown = list(range(rec["start"], m + 1))
    final = not r.partial and r.final_month == m
    work = {x: ex.working(r, (ex.ROOT, x), omega) for x in shown}
    s.k_last = {"case": case, "month": m, "final": final, "due": {x: r.periods[x].get(ex.ROOT) for x in shown},
                "work": {x: (getattr(ex.rule(r, work[x], omega), "id", "-"), getattr(ex.rule(r, work[x], omega), "expression", None),
                             [(k, ex.value(r, k)) for k in ex.children(r, work[x], omega)]) for x in shown}}
    total = sum(rec["withheld"].get(str(x), r.periods[x].get(ex.ROOT) or 0) for x in shown)
    after = [f for f in ex.downstream(r, m, omega)
             if any(ex._number(r.periods[x].get(f)) for x in shown)][:2]      # e.g. PPh borne by the government
    c = st.columns(2 + len(after))
    c[0].metric(f"PPh 21 {d.MONTHS[m - 1]}", d.money(r.periods[m].get(ex.ROOT)), help=g.tip("PPh 21"))
    c[1].metric(f"Total {d.MON[shown[0] - 1]}–{d.MON[m - 1]}", d.money(total), help="Jumlah PPh 21 sampai bulan ini.")
    for col, f in zip(c[2:], after):
        col.metric(f"{d.fact_label(f)} {d.MON[shown[0] - 1]}–{d.MON[m - 1]}",
                   d.money(sum(r.periods[x].get(f) or 0 for x in shown)))
    left, right = st.columns([1, 1], gap="large")
    with left:
        nodes = month_card(r, rec, cols, m, omega)
        if final:
            nodes += year_card(r, rec, omega)
        else:
            st.caption(f"Hitung ulang setahun muncul di bulan penutup ({d.MONTHS[max(rec['end'], rec['start']) - 1]}).")
    with right:
        names = ex.outputs(r, shown, omega)        # the results the knowledge base marks as output
        names = [f for f in names if f == ex.ROOT] + [f for f in names if f != ex.ROOT]
        rows = []
        for x in shown:
            p = r.periods[x]
            src = ex.source_of(r, work[x])
            rows.append({"Bulan": d.MONTHS[x - 1], **{d.fact_label(f): d.fmt(f, p.get(f)) for f in names},
                         "Dihitung dengan": (d.short_doc(src["document"]) + " " + src["provision"]) if src else "",
                         "Sudah dipotong (isian)": d.money(rec["withheld"][str(x)]) if str(x) in rec["withheld"] else ""})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption("Kolom tabel: nilai yang ditandai knowledge base sebagai hasil, yang tidak nol di bulan-bulan ini.")
        st.download_button("Unduh rincian (CSV)", pd.DataFrame(rows).to_csv(index=False).encode(),
                           f"pph21_{rec['name'] or 'pegawai'}_{rec['year']}.csv", icon=":material/download:")
        with st.expander("Kenapa angkanya segini? (aturan dan pasal)"):
            basis(r, nodes)
        with st.expander("Data yang dikirim ke engine"):
            st.caption("Hanya bulan sampai bulan perhitungan yang dikirim; engine mengenali bulan penutup dari bulan selesai "
                       "bekerja dan baru memberi nilai setahun di bulan itu. PPh yang diisi di 'PPh sudah dipotong' dikirim "
                       "sebagai nilai tercatat.")
            st.json(case, expanded=False)


def show():
    s = st.session_state
    s.page_ctx = "kalkulator"
    if "rec" not in s:
        _apply_scenario("Pegawai biasa")
    st.title("Kalkulator PPh 21")
    g.md(f"Hitung {g.term('PPh 21')} satu pegawai sampai bulan tertentu. Isi atau pilih skenario, lalu ubah angka apa "
         "saja di tabel. Data yang ditanyakan mengikuti aturan yang berlaku; arahkan kursor ke kata bergaris titik atau "
         "ikon ⓘ untuk penjelasannya.")
    top_bar()
    period_bar()
    s.g_date = date(s.rec["year"], s.rec["month"], 1)     # glossary numbers of that tax month
    profile()
    rec = s.rec
    before = _norm(rec)
    pre, _ = d.compute(case_of(rec, s.k_omega_v), s.k_omega_v)
    cols, found, autos = grid(pre)
    if _norm(rec) != before and any(c[3] == "computed" for c in cols):
        st.rerun()        # an edit changed what the rules compute: show the locked columns up to date
    with st.expander("Kasus yang tidak dihitung di sini"):
        st.markdown("Hanya **pegawai tetap** di **satu perusahaan** dalam **satu tahun pajak**. Tidak dihitung: pegawai "
                    "tidak tetap atau harian, pindahan dari perusahaan lain di tahun yang sama, kembali bekerja di tahun "
                    "yang sama, pembayaran sesudah keluar, pesangon, pensiunan, pegawai asing (PPh 26), valuta asing.")
    results(rec, cols, found, autos)
