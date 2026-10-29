"""Payroll calculator on the research knowledge base: payslip with derivation graph and trace to the article,
comparison across versions and knowledge dates, one employee across periods, and a batch payroll run."""
import calendar
import io
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import state
import widgets as ui
from pph21kbs.engine import evaluate_case

SLIP_INCOME = ("base_salary", "fixed_allowance", "overtime_pay", "thr", "bonus", "other_regular_income",
               "jkk_premium", "jkm_premium", "health_premium_employer", "tax_allowance")
SLIP_DEDUCT = ("jht_employee", "jp_employee")
KLU_EXAMPLES = {"": "(tidak diisi)", "13921": "13921 industri tekstil rumah tangga (padat karya, DTP)",
                "14111": "14111 pakaian jadi (padat karya)", "55110": "55110 hotel bintang (pariwisata, DTP 2025-Q4)",
                "62019": "62019 aktivitas pemrograman lainnya", "47111": "47111 perdagangan eceran"}


def employee_form(prefix="c"):
    with st.container(border=True):
        st.markdown("**Pegawai**")
        name = st.text_input("Nama", "Pegawai A", key=f"{prefix}_name")
        c1, c2 = st.columns(2)
        ptkp = c1.selectbox("Status PTKP", ui.STATUSES, index=4, key=f"{prefix}_ptkp")
        sex = c2.selectbox("Jenis kelamin", ("M", "F"), format_func=lambda s: "Laki-laki" if s == "M" else "Perempuan",
                           key=f"{prefix}_sex")
        method = st.selectbox("Metode", list(ui.METHODS), format_func=ui.METHODS.get, key=f"{prefix}_method")
        salary = st.number_input("Gaji pokok / bulan", 0, 10**10, 9_500_000, 100_000, key=f"{prefix}_salary")
        allowance = st.number_input("Tunjangan tetap / bulan", 0, 10**10, 0, 100_000, key=f"{prefix}_allow")
        overtime = st.number_input("Lembur / bulan", 0, 10**10, 0, 100_000, key=f"{prefix}_ot")
        c1, c2 = st.columns([2, 1])
        thr = c1.number_input("THR", 0, 10**10, 0, 500_000, key=f"{prefix}_thr")
        thr_m = c2.selectbox("Bulan", range(1, 13), index=3, format_func=lambda i: ui.MONTHS[i - 1], key=f"{prefix}_thrm")
        c1, c2 = st.columns([2, 1])
        bonus = c1.number_input("Bonus", 0, 10**10, 0, 500_000, key=f"{prefix}_bonus")
        bonus_m = c2.selectbox("Bulan ", range(1, 13), index=11, format_func=lambda i: ui.MONTHS[i - 1],
                               key=f"{prefix}_bonusm")
        vehicle = st.number_input("Natura kendaraan / bulan", 0, 10**9, 0, 100_000, key=f"{prefix}_veh")
        start, end = st.slider("Bulan bekerja", 1, 12, (1, 12), key=f"{prefix}_months")
        with st.expander("Pemberi kerja dan lainnya"):
            klu = st.selectbox("KLU pemberi kerja", list(KLU_EXAMPLES), format_func=KLU_EXAMPLES.get, key=f"{prefix}_klu")
            klu_other = st.text_input("atau KLU lain (5 digit)", "", key=f"{prefix}_klu2")
            jkk = st.selectbox("Kelompok risiko JKK", list(ui.JKK), format_func=ui.JKK.get, key=f"{prefix}_jkk")
            npwp = st.toggle("Punya NPWP/NIK valid", True, key=f"{prefix}_npwp")
        policy = ui.policy_picker(f"{prefix}_policy")
    return {"name": name, "ptkp": ptkp, "sex": sex, "method": method, "salary": int(salary), "allowance": int(allowance),
            "overtime": int(overtime), "thr": int(thr), "thr_month": thr_m, "bonus": int(bonus), "bonus_month": bonus_m,
            "vehicle": int(vehicle), "start": start, "end": end, "klu": (klu_other.strip() or klu or None),
            "jkk": jkk, "npwp": npwp, "policy": policy}


def build_case(emp, year, case_id="kalkulator"):
    periods = []
    for m in range(emp["start"], emp["end"] + 1):
        inc = {"base_salary": emp["salary"]}
        if emp["allowance"]:
            inc["fixed_allowance"] = emp["allowance"]
        if emp["overtime"]:
            inc["overtime_pay"] = emp["overtime"]
        if emp["thr"] and m == emp["thr_month"]:
            inc["thr"] = emp["thr"]
        if emp["bonus"] and m == emp["bonus_month"]:
            inc["bonus"] = emp["bonus"]
        ben = {"company_vehicle": emp["vehicle"]} if emp["vehicle"] else {}
        periods.append({"month": m, "income": inc, "benefits": ben, "zakat": 0})
    return {"case_id": case_id, "tax_year": year, "method": emp["method"],
            "employee": {"ptkp_status": emp["ptkp"], "sex": emp["sex"], "tax_id_valid": emp["npwp"]},
            "employer": {"klu": emp["klu"], "jkk_risk_group": emp["jkk"], "policy": emp["policy"]},
            "employment": {"start_month": emp["start"], "end_month": emp["end"]}, "periods": periods}


def compute(case, omega, update_id=None, policy=None, trace=False):
    kb = state.kb_for(update_id, policy)
    try:
        return evaluate_case(kb, case, omega, trace=trace), None
    except Exception as e:  # noqa: BLE001 - shown to the user
        return None, f"{type(e).__name__}: {e}"


def _payslip(emp, case, r, month, omega):
    row = r.periods.get(month, {})
    known = "semua yang diketahui hari ini" if omega == state.TODAY else f"pengetahuan per {omega:%d/%m/%Y}"
    html = [f"<div class='card slip'><h4>Slip gaji · {ui.MONTHS[month - 1]} {case['tax_year']}</h4>",
            f"<div class='muted'>{emp['name']} · {emp['ptkp']} · {ui.METHODS[emp['method']]} · {known}</div><table>"]
    for f in SLIP_INCOME:
        if row.get(f):
            html.append(f"<tr><td>{ui.label(f)}</td><td class='r'>{ui.rp(row[f])}</td></tr>")
    html.append(f"<tr class='total'><td>Penghasilan bruto</td><td class='r'>{ui.rp(row.get('gross_income'))}</td></tr>")
    html.append(f"<tr><td>PPh 21 terutang</td><td class='r'>{ui.rp(row.get('pph21_due'))}</td></tr>")
    if row.get("pph21_dtp"):
        html.append(f"<tr class='sub'><td>· ditanggung pemerintah (DTP)</td><td class='r'>{ui.rp(row['pph21_dtp'])}</td></tr>")
    for f in SLIP_DEDUCT:
        if row.get(f):
            html.append(f"<tr class='sub'><td>{ui.label(f)}</td><td class='r'>{ui.rp(row[f])}</td></tr>")
    html.append(f"<tr class='total'><td>Take-home pay</td><td class='r'>{ui.rp(row.get('take_home_pay'))}</td></tr>")
    html.append("</table></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _year_table(r):
    rows = []
    for m in sorted(r.periods):
        p = r.periods[m]
        rows.append({"Bulan": ui.MONTHS[m - 1], "Bruto": p.get("gross_income"), "PPh 21": p.get("pph21_due"),
                     "DTP": p.get("pph21_dtp") or 0, "Take-home pay": p.get("take_home_pay")})
    return pd.DataFrame(rows)


def _trace_table(r, kb):
    view_rules = {}
    rows = []
    for (fact, m), t in sorted((r.trace or {}).items(), key=lambda kv: (kv[0][1], kv[0][0])):
        rid = t["rule"]
        if rid not in view_rules:
            hist = kb.history(rid)
            view_rules[rid] = hist[-1] if hist else None
        rec = view_rules[rid]
        rows.append({"bulan": "setahun" if m == 0 else ui.MONTHS[m - 1], "fakta": fact, "nilai": ui.number(t["value"]),
                     "aturan": rid, "lapis": t["layer"], "modalitas": t["modality"],
                     "sumber": "; ".join(dict.fromkeys(f"{s['document']} {s['provision']}" for s in t.get("source") or [])),
                     "kutipan": " | ".join(s.get("quote", "") for s in t.get("source") or []),
                     "ekspresi": ui.text_of(getattr(rec, "expression", None)) if rec else ""})
    return pd.DataFrame(rows)


def tab_payslip(emp):
    c1, c2, c3 = st.columns([1, 1.3, 1.4])
    with c1:
        year, month = ui.period_picker("p", 2025, 3)
    with c2:
        omega = ui.knowledge_picker("p")
    with c3:
        update_id = ui.version_picker("p_version")
    case = build_case(emp, year)
    month = min(max(month, emp["start"]), emp["end"])
    r, err = compute(case, omega, update_id, emp["policy"], trace=True)
    if err:
        st.error(f"Engine tidak dapat menghitung kasus ini: {err}")
        return
    left, right = st.columns([1, 1.35])
    with left:
        _payslip(emp, case, r, month, omega)
        y = r.year
        items = [("Bruto setahun", y.get("annual_gross")), ("Biaya jabatan", y.get("job_expense")),
                 ("PTKP", y.get("ptkp_amount")), ("PKP", y.get("taxable_income")),
                 ("PPh 21 setahun", y.get("annual_pph21"))]
        cells = "".join(f"<tr><td>{k}</td><td class='r'>{ui.rp(v)}</td></tr>" for k, v in items if v is not None)
        st.markdown(f"<div class='card slip' style='margin-top:.8rem'><h4>Setahun {case['tax_year']}</h4>"
                    f"<table>{cells}</table></div>", unsafe_allow_html=True)
        for c in r.conflicts:
            st.warning(f"Konflik lintas lapis **{c.get('code', '')}**: aturan perusahaan `{c.get('source') or c.get('company_rules')}` "
                       f"untuk `{c.get('fact', '')}` dikalahkan aturan wajib. Engine menerapkan regulasi dan "
                       "melaporkan konflik (syarat A4).", icon=":material/gavel:")
        for e in r.errors:
            st.error(e)
    with right:
        st.markdown("**Mengapa angka ini**")
        c1, c2 = st.columns([1.4, 1])
        facts = sorted({f for (f, m) in (r.trace or {}) if m in (month, 0)})
        default = facts.index("pph21_due") if "pph21_due" in facts else 0
        fact = c1.selectbox("Fakta", facts, index=default, key="p_fact")
        depth = c2.slider("Kedalaman", 1, 5, 2, key="p_depth")
        st.graphviz_chart(ui.derivation_dot(r, month if (fact, month) in (r.trace or {}) else 0, fact, depth),
                          width="stretch")
        ui.note("Setiap fakta keluaran punya jejak sampai aturan dan pasal yang menghasilkannya (biru = regulasi, "
                "oranye = kebijakan perusahaan).")
    t1, t2 = st.tabs(["Setahun", "Jejak perhitungan"])
    with t1:
        st.dataframe(_year_table(r), hide_index=True, width="stretch",
                     column_config={k: st.column_config.NumberColumn(format="localized")
                                    for k in ("Bruto", "PPh 21", "DTP", "Take-home pay")})
    with t2:
        st.dataframe(_trace_table(r, state.kb_for(update_id, emp["policy"])), hide_index=True, width="stretch",
                     height=420)


def tab_compare(emp):
    st.markdown("Pegawai dan tahun yang sama dihitung dengan beberapa versi knowledge base atau tanggal pengetahuan. "
                "Sel yang berbeda dari kolom pertama ditandai.")
    c1, c2 = st.columns([1, 2])
    year = c1.selectbox("Tahun pajak", list(range(2013, 2027)), index=list(range(2013, 2027)).index(2024), key="cmp_y")
    options = state.versions()
    labels = [o[0] for o in options]
    by_id = {o[1]: o[0] for o in options}
    defaults = [by_id[u] for u in ("GOLD-E02", "GOLD-E04", "GOLD-E06") if u in by_id] + [labels[-1]]
    chosen = c2.multiselect("Versi", labels, default=defaults[-3:], key="cmp_versions")
    dates = st.text_input("Tanggal pengetahuan tambahan (pisahkan koma, format YYYY-MM-DD)", "2023-12-01, 2024-06-30",
                          key="cmp_dates")
    case = build_case(emp, year)
    cols = {}
    for lab in chosen:
        r, err = compute(case, state.TODAY, dict(options)[lab], emp["policy"])
        if r:
            cols[lab.split(" · ")[0] + " " + lab.split(" · ")[1]] = {m: r.periods[m].get("pph21_due") for m in r.periods}
    for d in filter(None, (x.strip() for x in dates.split(","))):
        try:
            w = date.fromisoformat(d)
        except ValueError:
            st.warning(f"Tanggal tidak dikenal: {d}")
            continue
        r, err = compute(case, w, None, emp["policy"])
        if r:
            cols[f"KB kini, ω = {w:%d/%m/%Y}"] = {m: r.periods[m].get("pph21_due") for m in r.periods}
    if not cols:
        return
    df = pd.DataFrame(cols)
    df.index = [ui.MONTHS[m - 1] for m in df.index]
    first = df.columns[0]

    def mark(col):
        return ["background-color: #fff3cd" if col.name != first and v != df[first].iloc[i] else ""
                for i, v in enumerate(col)]
    st.markdown(f"**PPh 21 terutang per bulan, {year}**")
    st.dataframe(df.style.apply(mark).format(lambda v: ui.number(v)), width="stretch")
    ui.note("Syarat A2 (hasil berubah sesuai perubahan) dan A3 (hasil lama tidak berubah) terlihat langsung; eksperimen "
            "memeriksa hal yang sama pada seluruh ruang uji.")


def tab_periods(emp):
    st.markdown("Satu pegawai dari 2023 sampai 2026: dihitung dengan semua yang diketahui hari ini, dan dengan "
                "pengetahuan pada akhir setiap bulan (seperti dihitung saat itu). Selisih menunjukkan perubahan yang "
                "terbit belakangan atau berlaku surut.")
    years = st.multiselect("Tahun", [2023, 2024, 2025, 2026], default=[2023, 2024, 2025, 2026], key="per_years")
    rows = []
    with st.spinner("Menghitung ..."):
        for y in years:
            case = build_case(emp, y)
            today, _ = compute(case, state.TODAY, None, emp["policy"])
            for m in range(emp["start"], emp["end"] + 1):
                w = date(y, m, calendar.monthrange(y, m)[1])
                then, _ = compute(case, min(w, state.TODAY), None, emp["policy"])
                rows.append({"periode": f"{y}-{m:02d}", "hari ini": (today.periods.get(m) or {}).get("pph21_due") if today else None,
                             "saat itu": (then.periods.get(m) or {}).get("pph21_due") if then else None})
    if not rows:
        return
    df = pd.DataFrame(rows)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["periode"], y=df["hari ini"], name="semua yang diketahui hari ini", line=dict(color=ui.REG)))
    fig.add_trace(go.Scatter(x=df["periode"], y=df["saat itu"], name="seperti diketahui saat itu",
                             line=dict(color=ui.COMPANY, dash="dot")))
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10), yaxis_title="PPh 21 terutang (Rp)",
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, width="stretch")
    diff = df[df["hari ini"] != df["saat itu"]]
    if len(diff):
        st.markdown(f"**{len(diff)} masa** berbeda antara pengetahuan hari ini dan pengetahuan saat itu:")
        st.dataframe(diff, hide_index=True, width="stretch")
    else:
        st.success("Tidak ada masa yang berubah karena pengetahuan yang terbit belakangan.")


SAMPLE = pd.DataFrame([
    {"nama": "Andi", "ptkp": "TK/0", "gaji": 6_000_000, "tunjangan": 500_000, "metode": "gross", "klu": ""},
    {"nama": "Budi", "ptkp": "K/1", "gaji": 9_500_000, "tunjangan": 0, "metode": "gross", "klu": "13921"},
    {"nama": "Citra", "ptkp": "K/2", "gaji": 15_000_000, "tunjangan": 2_000_000, "metode": "gross_up", "klu": ""},
    {"nama": "Dewi", "ptkp": "TK/1", "gaji": 22_000_000, "tunjangan": 3_000_000, "metode": "gross", "klu": ""},
    {"nama": "Eko", "ptkp": "K/3", "gaji": 7_500_000, "tunjangan": 750_000, "metode": "employer_borne", "klu": "14111"},
    {"nama": "Fajar", "ptkp": "K/0", "gaji": 35_000_000, "tunjangan": 5_000_000, "metode": "gross", "klu": ""},
])


def tab_batch():
    st.markdown("Semua pegawai satu perusahaan untuk satu bulan. Ubah tabel, atau unggah CSV dengan kolom "
                "`nama, ptkp, gaji, tunjangan, metode, klu`.")
    up = st.file_uploader("Unggah CSV", type="csv", key="batch_csv")
    data = pd.read_csv(up, dtype={"klu": str}).fillna("") if up else SAMPLE
    data = st.data_editor(data, num_rows="dynamic", width="stretch", key="batch_table")
    c1, c2, c3 = st.columns([1, 1, 1.4])
    with c1:
        year, month = ui.period_picker("b", 2025, 3)
    with c2:
        omega = ui.knowledge_picker("b")
    with c3:
        policy = ui.policy_picker("b_policy")
    out = []
    for _, row in data.iterrows():
        emp = {"name": row["nama"], "ptkp": row["ptkp"], "sex": "M", "method": row["metode"] or "gross",
               "salary": int(row["gaji"] or 0), "allowance": int(row["tunjangan"] or 0), "overtime": 0, "thr": 0,
               "thr_month": 4, "bonus": 0, "bonus_month": 12, "vehicle": 0, "start": 1, "end": 12,
               "klu": str(row.get("klu") or "") or None, "jkk": "very_low", "npwp": True, "policy": policy}
        r, err = compute(build_case(emp, year, row["nama"]), omega, None, policy)
        p = (r.periods.get(month) or {}) if r else {}
        out.append({"nama": row["nama"], "bruto": p.get("gross_income"), "PPh 21": p.get("pph21_due"),
                    "DTP": p.get("pph21_dtp") or 0, "take-home pay": p.get("take_home_pay"), "galat": err or ""})
    res = pd.DataFrame(out)
    st.dataframe(res, hide_index=True, width="stretch",
                 column_config={k: st.column_config.NumberColumn(format="localized")
                                for k in ("bruto", "PPh 21", "DTP", "take-home pay")})
    m1, m2, m3 = st.columns(3)
    m1.metric("Total bruto", ui.rp(int(res["bruto"].fillna(0).sum())))
    m2.metric("Total PPh 21", ui.rp(int(res["PPh 21"].fillna(0).sum())))
    m3.metric("Total DTP", ui.rp(int(res["DTP"].fillna(0).sum())))
    buf = io.StringIO()
    res.to_csv(buf, index=False)
    st.download_button("Unduh hasil (CSV)", buf.getvalue(), f"payroll_{year}_{month:02d}.csv", "text/csv",
                       icon=":material/download:")


def show():
    st.title("Kalkulator PPh 21")
    st.caption("Engine inferensi dengan wajah: semua pengetahuan pajak ada di knowledge base; kalkulator hanya memilih "
               "versi, periode, dan tanggal pengetahuan.")
    left, right = st.columns([1, 3.2])
    with left:
        emp = employee_form()
    with right:
        t1, t2, t3, t4 = st.tabs(["Slip gaji", "Bandingkan versi", "Lintas periode", "Payroll massal"])
        with t1:
            tab_payslip(emp)
        with t2:
            tab_compare(emp)
        with t3:
            tab_periods(emp)
        with t4:
            tab_batch()
