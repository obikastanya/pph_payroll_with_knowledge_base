"""Calculator: try a calculation for one employee (this month and the end of the year), or run the payroll of a month
for many employees.

Scope of the engine (and of the research): permanent employees, one employer, one tax year. The calculation always
covers every month of employment, so the end of the year is known; months not paid yet are treated as planned.
"""
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import data as d
import glossary as g
import ui

VAR_COLS = {"Gaji pokok": "base_salary", "Tunjangan tetap": "fixed_allowance", "Lembur": "overtime_pay",
            "THR": "thr", "Bonus": "bonus", "Natura lain": "other_benefit", "Bingkisan": "gift_other",
            "Zakat": "zakat"}
VAR_HELP = {"Gaji pokok": "lembur", "Tunjangan tetap": "tunjangan tetap", "Lembur": "lembur", "THR": "THR",
            "Bonus": "bonus", "Natura lain": "natura", "Bingkisan": "natura", "Zakat": "zakat"}

BASE = dict(c_name="Rina (contoh)", c_year=2026, c_ptkp="K/1", c_sex="F", c_husband=True, c_method="gross",
            c_start=1, c_end=12, c_npwp=True, c_klu="", c_jkk="low", c_equity=False, c_salary=10_000_000,
            c_allow=1_500_000, c_vehicle=0, c_housing=0, c_raise=False, c_raise_m=4, c_raise_to=12_000_000,
            c_seed={3: {"THR": 11_500_000}})
SCENARIOS = {
    "Pegawai biasa": dict(),
    "THR + bonus": dict(c_name="Budi (contoh)", c_ptkp="TK/0", c_sex="M", c_salary=12_000_000, c_allow=0,
                        c_seed={3: {"THR": 12_000_000}, 12: {"Bonus": 24_000_000}}),
    "Masuk Juli": dict(c_name="Sari (contoh)", c_start=7, c_seed={}),
    "Keluar Agustus": dict(c_name="Andi (contoh)", c_sex="M", c_end=8, c_seed={3: {"THR": 11_500_000}}),
    "Gaji naik April": dict(c_raise=True),
    "Gross-up": dict(c_method="gross_up"),
    "Insentif DTP 2025": dict(c_name="Dewi (contoh)", c_year=2025, c_ptkp="TK/0", c_salary=6_500_000, c_allow=500_000,
                              c_klu="13921", c_seed={3: {"THR": 7_000_000}}),
    "Lembur tiap bulan": dict(c_seed={m: {"Lembur": 800_000 + 150_000 * (m % 4)} for m in range(1, 13)}),
}


def _apply(name):
    st.session_state.update(BASE)
    st.session_state.update(SCENARIOS[name])
    st.session_state.pop("c_month", None)


def _defaults():
    for k, v in BASE.items():
        st.session_state.setdefault(k, v)


# ---------------------------------------------------------------- inputs
def inputs():
    s = st.session_state
    with st.container(border=True):
        ui.step(1, "Pegawai")
        st.text_input("Nama", key="c_name")
        c1, c2 = st.columns(2)
        c1.selectbox("Tahun pajak", (2023, 2024, 2025, 2026), key="c_year",
                     help="Tahun 2023 masih memakai cara lama (tanpa TER). TER berlaku sejak Januari 2024.")
        c2.selectbox("Status PTKP", d.STATUSES, key="c_ptkp", help=g.tip("status PTKP"))
        c1, c2 = st.columns(2)
        c1.selectbox("Jenis kelamin", ("M", "F"), key="c_sex", format_func=lambda x: "Laki-laki" if x == "M" else "Perempuan")
        c2.selectbox("Cara pajak dibayar", list(d.METHODS), key="c_method", format_func=d.METHODS.get,
                     help=g.tip("gross") + "\n\n" + g.tip("gross-up") + "\n\n" + g.tip("ditanggung"))
        if s.c_sex == "F" and s.c_ptkp.startswith("K"):
            st.checkbox("Ada keterangan suami tidak berpenghasilan", key="c_husband", help=g.tip("karyawati"))
        c1, c2 = st.columns(2)
        c1.selectbox("Mulai bekerja", range(1, 13), key="c_start", format_func=lambda m: d.MONTHS[m - 1],
                     help="Bulan pertama digaji di tahun ini.")
        c2.selectbox("Bekerja sampai", range(1, 13), key="c_end", format_func=lambda m: d.MONTHS[m - 1],
                     help="Desember bila masih bekerja. Bulan keluar menjadi " + g.TERMS["masa terakhir"][0].lower() + ".")
        with st.expander("Kondisi khusus (opsional)"):
            st.toggle("Punya NPWP / NIK terdaftar", key="c_npwp", help=g.tip("NPWP"))
            st.selectbox("Bidang usaha perusahaan (KLU)", list(d.KLU), key="c_klu", format_func=d.KLU.get, help=g.tip("KLU"))
            st.selectbox("Risiko pekerjaan (JKK)", list(d.JKK), key="c_jkk", format_func=d.JKK.get, help=g.tip("risiko JKK"))
            st.toggle("Pegawai juga pemegang saham", key="c_equity",
                      help="Mobil dinas untuk pemegang saham selalu menjadi natura yang kena pajak.")

    with st.container(border=True):
        ui.step(2, "Penghasilan tetap per bulan")
        c1, c2 = st.columns(2)
        c1.number_input("Gaji pokok", 0, 10**10, step=100_000, key="c_salary", help="Gaji pokok sebulan sebelum potongan.")
        c2.number_input("Tunjangan tetap", 0, 10**10, step=100_000, key="c_allow", help=g.tip("tunjangan tetap"))
        c1, c2 = st.columns(2)
        c1.number_input("Mobil dinas (nilai/bulan)", 0, 10**9, step=100_000, key="c_vehicle", help=g.tip("natura"))
        c2.number_input("Rumah dinas (nilai/bulan)", 0, 10**9, step=100_000, key="c_housing", help=g.tip("natura"))
        st.caption(f"Total tetap per bulan: **{d.money(s.c_salary + s.c_allow)}**"
                   + (f" + natura {d.money(s.c_vehicle + s.c_housing)}" if s.c_vehicle + s.c_housing else ""))
        st.toggle("Gaji pokok berubah di tengah tahun", key="c_raise")
        if s.c_raise:
            c1, c2 = st.columns(2)
            c1.selectbox("Mulai bulan", range(1, 13), key="c_raise_m", format_func=lambda m: d.MONTHS[m - 1])
            c2.number_input("Gaji pokok baru", 0, 10**10, step=100_000, key="c_raise_to")

    with st.container(border=True):
        ui.step(3, "Rincian per bulan")
        st.caption("Sudah terisi dari langkah 2. Ubah sel untuk bulan yang berbeda: lembur, THR, bonus, cuti tanpa upah "
                   "(gaji pokok lebih kecil), dan sebagainya. Mengubah langkah 2 mengisi ulang tabel ini.")
        months = list(range(s.c_start, s.c_end + 1))
        rows = []
        for m in months:
            sal = s.c_raise_to if s.c_raise and m >= s.c_raise_m else s.c_salary
            row = {"Bulan": d.MONTHS[m - 1], "Gaji pokok": sal, "Tunjangan tetap": s.c_allow}
            for col in list(VAR_COLS)[2:]:
                row[col] = s.c_seed.get(m, {}).get(col, 0)
            rows.append(row)
        sig = hash((tuple(months), s.c_salary, s.c_allow, s.c_raise, s.c_raise_m, s.c_raise_to, str(s.c_seed)))
        table = st.data_editor(
            pd.DataFrame(rows), key=f"c_tab_{sig}", hide_index=True, width="stretch", disabled=["Bulan"],
            column_config={c: st.column_config.NumberColumn(c, min_value=0, step=50_000, format="%d",
                                                            help=g.TERMS[VAR_HELP[c]][1] if c != "Gaji pokok" else None)
                           for c in VAR_COLS})
    with st.expander("Pengaturan lanjutan"):
        omega = st.date_input("Hitung dengan aturan yang diketahui pada tanggal", d.TODAY, key="c_omega",
                              help=g.tip("tanggal pengetahuan"))
    return months, table, omega


def build_case(months, table, method=None):
    s = st.session_state
    periods = []
    for m, (_, row) in zip(months, table.iterrows()):
        inc = {VAR_COLS[c]: int(row[c] or 0) for c in ("Gaji pokok", "Tunjangan tetap", "Lembur", "THR", "Bonus")
               if int(row[c] or 0)}
        ben = {"company_vehicle": s.c_vehicle, "housing_individual": s.c_housing,
               "other_benefit": int(row["Natura lain"] or 0), "gift_other": int(row["Bingkisan"] or 0)}
        periods.append({"month": m, "income": inc, "benefits": {k: int(v) for k, v in ben.items() if v},
                        "zakat": int(row["Zakat"] or 0)})
    employee = {"ptkp_status": s.c_ptkp, "sex": s.c_sex, "tax_id_valid": s.c_npwp, "has_equity_in_employer": s.c_equity}
    if s.c_sex == "F":
        employee["husband_no_income_certified"] = bool(s.c_husband)
    return {"case_id": "kalkulator", "tax_year": s.c_year, "method": method or s.c_method, "employee": employee,
            "employer": {"klu": s.c_klu or None, "jkk_risk_group": s.c_jkk, "policy": None},
            "employment": {"start_month": s.c_start, "end_month": s.c_end}, "periods": periods}


# ---------------------------------------------------------------- results
def _month_card(r, case, m, final):
    p = r.periods[m]
    gross, due, dtp = p.get("gross_income"), p.get("pph21_due"), p.get("pph21_dtp") or 0
    rate, cat = d.value(r, "ter_rate", m), d.value(r, "ter_category")
    method = case["method"]
    contrib = sum(d.value(r, f, m) or 0 for f in ("jht_employee", "jp_employee", "health_employee"))
    kind = (ui.badge("Masa pajak terakhir", "orange") + g.term("masa terakhir", "apa ini?")) if final else \
        (ui.badge("Masa biasa · TER", "blue") + g.term("TER", "apa ini?"))
    neg = " neg" if due is not None and due < 0 else ""
    head = "Lebih bayar dikembalikan" if due is not None and due < 0 else "PPh 21 bulan ini"
    lines = [f"<tr><td class='op'></td><td>{g.term('bruto', 'Penghasilan bruto')}</td><td class='r'>{d.money(gross)}</td></tr>"]
    if final:
        lines += [f"<tr><td class='op'></td><td>{g.term('PPh setahun')} (lihat kartu akhir tahun)</td>"
                  f"<td class='r'>{d.money(d.value(r, 'annual_pph21'))}</td></tr>",
                  f"<tr><td class='op'>−</td><td>{g.term('sudah dipotong', 'Sudah dipotong')} bulan-bulan sebelumnya</td>"
                  f"<td class='r'>{d.money(d.value(r, 'withheld_before_final'))}</td></tr>"]
    elif rate is not None:
        lines.append(f"<tr><td class='op'>×</td><td>Tarif {g.term('TER')} {g.term('kategori TER', 'kategori ' + str(cat))}"
                     f"</td><td class='r'>{d.pct(rate)}</td></tr>")
    lines.append(f"<tr class='total'><td class='op'>=</td><td>{g.term('PPh 21')} terutang</td><td class='r'>{d.money(due)}</td></tr>")
    if dtp:
        lines.append(f"<tr class='sub'><td></td><td>· ditanggung pemerintah ({g.term('DTP')}), dibayarkan ke pegawai</td>"
                     f"<td class='r'>{d.money(dtp)}</td></tr>")
    if method == "gross_up" and p.get("tax_allowance"):
        lines.append(f"<tr class='sub'><td></td><td>· termasuk {g.term('gross-up', 'tunjangan pajak')} di bruto</td>"
                     f"<td class='r'>{d.money(p['tax_allowance'])}</td></tr>")
    lines.append(f"<tr class='sub'><td></td><td>Iuran {g.term('JHT')}, {g.term('JP')}, {g.term('BPJS Kesehatan')} pegawai"
                 f"</td><td class='r'>{d.money(contrib)}</td></tr>")
    lines.append(f"<tr><td></td><td><b>{g.term('gaji bersih', 'Gaji bersih diterima')}</b></td>"
                 f"<td class='r'><b>{d.money(p.get('take_home_pay'))}</b></td></tr>")
    who = {"gross": "dipotong dari gaji", "gross_up": "dibayar lewat tunjangan pajak",
           "employer_borne": "dibayar perusahaan"}[method]
    if final:
        diff = d.value(r, "final_period_tax") or 0
        expl = (f"Di masa terakhir pajak setahun dihitung ulang. {d.money(d.value(r, 'annual_pph21'))} − "
                f"{d.money(d.value(r, 'withheld_before_final'))} = <b>{d.money(diff)}</b>: "
                + ("kurang bayar, " + who + "." if diff >= 0 else "lebih bayar, dikembalikan ke pegawai bersama gaji."))
    else:
        expl = f"{d.money(gross)} × {d.pct(rate)} = <b>{d.money(due)}</b>, {who}."
        if dtp:
            expl += " Karena insentif DTP, pegawai menerima kembali jumlah itu bersama gaji."
    ui.html(f"<div class='card'><h4>{head} · {d.MONTHS[m - 1]} {case['tax_year']}</h4>{kind}"
            f"<div class='big{neg}'>{d.money(abs(due) if due is not None and due < 0 else due)}</div>"
            f"<table class='lines'>{''.join(lines)}</table><div class='explain'>{expl}</div></div>")


def _year_card(r, case):
    y = r.year
    final_m = case["employment"]["end_month"]
    pension = (y.get("annual_deductions") or 0) - (y.get("job_expense") or 0)
    diff = d.value(r, "final_period_tax") or 0
    status = d.value(r, "ptkp_status_effective")
    rows = [("", g.term("bruto", "Penghasilan bruto setahun"), y.get("annual_gross")),
            ("−", g.term("biaya jabatan", "Biaya jabatan"), y.get("job_expense")),
            ("−", g.term("iuran pensiun", "Iuran pensiun pegawai") + " dan zakat", pension),
            ("=", g.term("neto", "Penghasilan neto"), y.get("annual_net")),
            ("−", g.term("PTKP") + f" ({status})", y.get("ptkp_amount")),
            ("=", g.term("PKP", "Penghasilan kena pajak"), y.get("taxable_income")),
            ("×", g.term("Pasal 17", "Tarif Pasal 17"), None)]
    lines = "".join(f"<tr><td class='op'>{o}</td><td>{t}</td><td class='r'>{d.money(v) if v is not None else 'bertingkat'}"
                    f"</td></tr>" for o, t, v in rows)
    lines += (f"<tr class='total'><td class='op'>=</td><td>{g.term('PPh setahun')}</td>"
              f"<td class='r'>{d.money(y.get('annual_pph21'))}</td></tr>"
              f"<tr><td class='op'>−</td><td>{g.term('sudah dipotong', 'Sudah dipotong')} "
              f"{d.MON[case['employment']['start_month'] - 1]}–{d.MON[max(final_m - 2, 0)]}</td>"
              f"<td class='r'>{d.money(d.value(r, 'withheld_before_final'))}</td></tr>"
              f"<tr class='total'><td class='op'>=</td><td>Masa terakhir ({d.MONTHS[final_m - 1]}): "
              f"{g.term('kurang bayar') if diff >= 0 else g.term('lebih bayar')}</td><td class='r'>{d.money(diff)}</td></tr>")
    note = ("Sama dengan yang sudah dipotong: tidak ada selisih." if diff == 0 else
            f"Di {d.MONTHS[final_m - 1]} dipotong {d.money(diff)}." if diff > 0 else
            f"Di {d.MONTHS[final_m - 1]} pegawai menerima kembali {d.money(-diff)}.")
    if final_m < 12:
        note += f" Pegawai keluar di {d.MONTHS[final_m - 1]}, jadi bulan itu menjadi masa terakhir."
    ui.html(f"<div class='card'><h4>Akhir tahun {case['tax_year']}</h4>"
            f"<span class='muted'>Hitung ulang setahun di {g.term('masa terakhir')}</span>"
            f"<table class='lines'>{lines}</table><div class='explain'>{note}</div></div>")


def _chart(r, case, chosen):
    months = sorted(r.periods)
    final = case["employment"]["end_month"]
    vals = [float(r.periods[m].get("pph21_due") or 0) for m in months]
    colours = ["#1b7a43" if v < 0 else "#eb6834" if m == final else "#2a78d6" for m, v in zip(months, vals)]
    fig = go.Figure(go.Bar(x=[d.MON[m - 1] for m in months], y=vals, marker_color=colours,
                           marker_line_width=[2.5 if m == chosen else 0 for m in months], marker_line_color="#24231f",
                           hovertemplate="%{x}: Rp%{y:,.0f}<extra></extra>"))
    fig.update_layout(height=230, margin=dict(l=0, r=0, t=10, b=0), yaxis_tickformat=",.0f", showlegend=False,
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.caption("Biru: masa biasa (TER). Oranye: masa terakhir. Hijau: lebih bayar dikembalikan.")


def _notes(r, case, months):
    out = []
    s = st.session_state
    eff = d.value(r, "ptkp_status_effective")
    if eff and eff != s.c_ptkp:
        out.append(f"PTKP yang dipakai **{eff}**, bukan {s.c_ptkp}: karyawati kawin memakai PTKP tidak kawin kecuali ada "
                   "keterangan suami tidak berpenghasilan.")
    spikes = [m for m in months if (r.periods[m].get("thr") or 0) + (r.periods[m].get("bonus") or 0)]
    if spikes and case["tax_year"] >= 2024:
        out.append("Bulan " + ", ".join(d.MONTHS[m - 1] for m in spikes) + " ada THR atau bonus: bruto bulan itu naik, "
                   "jadi tarif TER-nya juga naik. Selisihnya diratakan lagi di masa terakhir.")
    dtp = [m for m in months if r.periods[m].get("pph21_dtp")]
    if dtp:
        out.append(f"Insentif DTP berlaku di {len(dtp)} bulan; PPh-nya ditanggung pemerintah dan dibayarkan ke pegawai.")
    elif s.c_klu:
        out.append("Bidang usaha sudah diisi, tetapi pegawai ini tidak memenuhi syarat DTP (mis. tahun, sektor, atau batas "
                   "penghasilan). Lihat 'Dasar hukum'.")
    if case["tax_year"] < 2024:
        out.append("Tahun sebelum 2024 memakai cara lama: PPh sebulan dihitung dengan menyetahunkan penghasilan.")
    for w in r.warnings:
        out.append(str(w))
    for n in out:
        st.info(n, icon=":material/lightbulb:")


def _basis(r, m):
    facts = [("gross_income", m), ("ter_rate", m), ("pph21_due", m), ("pph21_dtp", m), ("ptkp_amount", 0),
             ("job_expense", 0), ("taxable_income", 0), ("annual_pph21", 0)]
    for f, mm in facts:
        t = (r.trace or {}).get((f, mm))
        if not t:
            continue
        src = t["source"][0] if t["source"] else None
        where = f"{d.short_doc(src['document'])} · {src['provision']}" if src else "-"
        val = d.pct(t["value"]) if f == "ter_rate" else d.money(t["value"])
        cls = "rule company" if t["layer"] == "company" else "rule"
        quote = f"<div class='quote'>“{src['quote']}”</div>" if src else ""
        ui.html(f"<div class='{cls}'><b>{d.fact_label(f)}</b> = {val} "
                f"<span class='muted'>({'bulan ' + d.MONTHS[mm - 1] if mm else 'setahun'})</span><br>"
                f"<span class='muted'>{g.term('sumber', 'Sumber')}: {where} · aturan <code>{t['rule']}</code></span>"
                f"{quote}</div>")


def _compare(months, table, omega):
    rows = []
    for method, label in d.METHODS.items():
        r, err = d.compute(build_case(months, table, method), omega)
        if err:
            continue
        thp = sum(r.periods[m].get("take_home_pay") or 0 for m in r.periods)
        allowance = sum(r.periods[m].get("tax_allowance") or 0 for m in r.periods)
        tax = r.year.get("annual_pph21") or 0
        rows.append({"Cara": label, "PPh setahun": d.money(tax), "Gaji bersih setahun": d.money(thp),
                     "Pajak yang dibayar perusahaan": d.money(allowance if method == "gross_up" else
                                                              tax if method == "employer_borne" else 0)})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    ui.html(f"<span class='muted'>{g.term('gross-up')} menaikkan bruto (tunjangan pajak ikut kena pajak), jadi PPh-nya "
            f"lebih besar daripada {g.term('gross')}; {g.term('ditanggung')} tidak menambah bruto.</span>")


def single():
    left, right = st.columns([1, 1.3], gap="large")
    with left:
        months, table, omega = inputs()
    case = build_case(months, table)
    r, err = d.compute(case, omega)
    with right:
        if err:
            st.error(f"Perhitungan gagal: {err}")
            return
        final = case["employment"]["end_month"]
        default = d.TODAY.month if case["tax_year"] == d.TODAY.year and d.TODAY.month in months else months[0]
        m = st.segmented_control("Pilih bulan", months, format_func=lambda x: d.MON[x - 1], key="c_month",
                                 default=default) or default
        _month_card(r, case, m, m == final)
        _year_card(r, case)
        _chart(r, case, m)
        _notes(r, case, months)
        t1, t2, t3, t4 = st.tabs(["Rincian per bulan", "Dasar hukum", "Bandingkan cara bayar pajak", "Data perhitungan"])
        with t1:
            rows = []
            for mm in months:
                p = r.periods[mm]
                rows.append({"Bulan": d.MONTHS[mm - 1], "Bruto": d.money(p.get("gross_income")),
                             "Tarif TER": d.pct(d.value(r, "ter_rate", mm)) if mm != final else "Pasal 17",
                             "PPh 21": d.money(p.get("pph21_due")), "DTP": d.money(p.get("pph21_dtp") or 0),
                             "Gaji bersih": d.money(p.get("take_home_pay"))})
            st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
            st.download_button("Unduh rincian (CSV)", pd.DataFrame(rows).to_csv(index=False).encode(),
                               "rincian_pph21.csv", icon=":material/download:")
        with t2:
            st.caption(f"Aturan yang menghasilkan angka-angka di bulan {d.MONTHS[m - 1]} dan akhir tahun, dengan pasal dan "
                       "kutipan peraturannya.")
            _basis(r, m)
        with t3:
            _compare(months, table, omega)
        with t4:
            st.caption("Data yang dikirim ke engine (format kasus penelitian).")
            st.json(case, expanded=False)


# ---------------------------------------------------------------- payroll of a month
ROSTER = pd.DataFrame([
    {"Nama": "Rina", "PTKP": "K/1", "Cara": "gross", "Gaji pokok": 10_000_000, "Tunjangan tetap": 1_500_000,
     "Masuk": 1, "Keluar": 12, "Lembur": 0, "THR": 0, "Bonus": 0},
    {"Nama": "Budi", "PTKP": "TK/0", "Cara": "gross", "Gaji pokok": 12_000_000, "Tunjangan tetap": 0,
     "Masuk": 1, "Keluar": 12, "Lembur": 750_000, "THR": 0, "Bonus": 0},
    {"Nama": "Sari", "PTKP": "K/3", "Cara": "gross_up", "Gaji pokok": 25_000_000, "Tunjangan tetap": 3_000_000,
     "Masuk": 1, "Keluar": 12, "Lembur": 0, "THR": 0, "Bonus": 0},
    {"Nama": "Andi", "PTKP": "TK/1", "Cara": "gross", "Gaji pokok": 7_000_000, "Tunjangan tetap": 500_000,
     "Masuk": 3, "Keluar": 10, "Lembur": 300_000, "THR": 0, "Bonus": 0},
    {"Nama": "Dewi", "PTKP": "K/0", "Cara": "employer_borne", "Gaji pokok": 15_000_000, "Tunjangan tetap": 1_000_000,
     "Masuk": 1, "Keluar": 12, "Lembur": 0, "THR": 0, "Bonus": 0},
])


def payroll():
    st.caption("Untuk admin: satu tabel untuk semua pegawai, pilih masa pajak, isi komponen tidak tetap bulan itu, "
               "lalu dapatkan PPh 21 setiap pegawai dan rekapnya.")
    c1, c2, c3 = st.columns([1, 1, 2])
    year = c1.selectbox("Tahun", (2024, 2025, 2026), index=2, key="p_year")
    month = c2.selectbox("Masa pajak", range(1, 13), index=d.TODAY.month - 1, key="p_month",
                         format_func=lambda m: d.MONTHS[m - 1], help=g.tip("masa pajak"))
    c3.file_uploader("Impor data pegawai (Excel/CSV)", type=["csv", "xlsx"], key="p_up",
                     help="Kolom sama dengan tabel di bawah.")
    tab = st.data_editor(ROSTER, key="p_roster", num_rows="dynamic", hide_index=True, width="stretch",
                         column_config={
                             "PTKP": st.column_config.SelectboxColumn("PTKP", options=d.STATUSES, help=g.tip("status PTKP")),
                             "Cara": st.column_config.SelectboxColumn("Cara", options=list(d.METHODS),
                                                                      help="gross, gross_up, employer_borne"),
                             "Masuk": st.column_config.NumberColumn("Masuk", min_value=1, max_value=12,
                                                                    help="Bulan mulai bekerja tahun ini"),
                             "Keluar": st.column_config.NumberColumn("Keluar", min_value=1, max_value=12,
                                                                     help="12 bila masih bekerja"),
                             "Lembur": st.column_config.NumberColumn(f"Lembur {d.MON[month - 1]}", format="%d"),
                             "THR": st.column_config.NumberColumn(f"THR {d.MON[month - 1]}", format="%d"),
                             "Bonus": st.column_config.NumberColumn(f"Bonus {d.MON[month - 1]}", format="%d")})
    rows, total = [], {"bruto": 0, "pph": 0, "dtp": 0, "thp": 0}
    for _, e in tab.iterrows():
        if not e["Nama"] or pd.isna(e["Gaji pokok"]):
            continue
        start, end = int(e["Masuk"]), int(e["Keluar"])
        if not start <= month <= end:
            rows.append({"Nama": e["Nama"], "Masa": "tidak bekerja", "Bruto": "-", "PPh 21": "-", "DTP": "-",
                         "Gaji bersih": "-"})
            continue
        periods = []
        for m in range(start, end + 1):
            inc = {"base_salary": int(e["Gaji pokok"]), "fixed_allowance": int(e["Tunjangan tetap"] or 0)}
            if m == month:
                for col, key in (("Lembur", "overtime_pay"), ("THR", "thr"), ("Bonus", "bonus")):
                    if e[col]:
                        inc[key] = int(e[col])
            periods.append({"month": m, "income": {k: v for k, v in inc.items() if v}})
        case = {"case_id": str(e["Nama"]), "tax_year": year, "method": e["Cara"],
                "employee": {"ptkp_status": e["PTKP"], "tax_id_valid": True},
                "employer": {"klu": None, "jkk_risk_group": "low"},
                "employment": {"start_month": start, "end_month": end}, "periods": periods}
        r, err = d.compute(case)
        if err:
            rows.append({"Nama": e["Nama"], "Masa": "gagal: " + err[:60]})
            continue
        p = r.periods[month]
        total["bruto"] += p.get("gross_income") or 0
        total["pph"] += p.get("pph21_due") or 0
        total["dtp"] += p.get("pph21_dtp") or 0
        total["thp"] += p.get("take_home_pay") or 0
        rows.append({"Nama": e["Nama"], "Masa": "terakhir" if month == end else "biasa (TER)",
                     "Bruto": d.money(p.get("gross_income")), "PPh 21": d.money(p.get("pph21_due")),
                     "DTP": d.money(p.get("pph21_dtp") or 0), "Gaji bersih": d.money(p.get("take_home_pay"))})
    c = st.columns(4)
    c[0].metric("Bruto semua pegawai", d.money(total["bruto"]), help=g.tip("bruto"))
    c[1].metric("PPh 21 masa ini", d.money(total["pph"]), help=g.tip("PPh 21"))
    c[2].metric("Ditanggung pemerintah", d.money(total["dtp"]), help=g.tip("DTP"))
    c[3].metric("Gaji bersih dibayar", d.money(total["thp"]), help=g.tip("gaji bersih"))
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    c1, c2, c3 = st.columns(3)
    c1.download_button("Rekap masa (CSV)", pd.DataFrame(rows).to_csv(index=False).encode(),
                       f"rekap_pph21_{year}_{month:02d}.csv", icon=":material/download:", width="stretch")
    c2.button("Ekspor untuk e-Bupot (Coretax)", icon=":material/upload:", width="stretch", disabled=True)
    c3.button(f"Tutup masa {d.MON[month - 1]} {year}", icon=":material/lock:", width="stretch", disabled=True)
    ui.mock("Bulan lain diisi dengan gaji dan tunjangan yang sama (perkiraan) supaya akhir tahun diketahui. Di sistem "
            "penuh: data pegawai tersimpan, masa yang ditutup terkunci, PPh yang benar-benar dipotong dipakai saat "
            "menghitung masa terakhir, dan ada ekspor e-Bupot serta bukti potong A1.")


def show():
    _defaults()
    st.title("Kalkulator PPh 21")
    g.md(f"Masukkan data pegawai, lalu lihat {g.term('PPh 21')} di setiap bulan dan hitungan "
         f"{g.term('masa terakhir', 'akhir tahun')}. Arahkan kursor ke kata bergaris titik untuk penjelasannya.")
    mode = st.segmented_control("Mode", ["Coba hitung satu pegawai", "Payroll bulanan"], default="Coba hitung satu pegawai",
                                key="c_mode", label_visibility="collapsed")
    if mode == "Payroll bulanan":
        payroll()
        return
    st.pills("Coba skenario", list(SCENARIOS), key="c_scn", on_change=lambda: _apply(st.session_state.c_scn)
             if st.session_state.c_scn else None)
    with st.expander("Kasus yang belum bisa dihitung di sini"):
        st.markdown("Kalkulator ini untuk **pegawai tetap** di **satu perusahaan** dalam **satu tahun pajak**. Belum "
                    "tercakup: pegawai tidak tetap atau harian, pesangon dan uang pensiun (pajak final), pensiunan, "
                    "pegawai asing (PPh 26), pindahan dari perusahaan lain di tahun yang sama, dan gaji dalam valuta "
                    "asing. Hitung kasus ini secara manual.")
    single()
