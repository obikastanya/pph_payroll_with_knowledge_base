"""Gold Deltas of the real company policies (collective agreements, PKB): WIKA 2025-2026, Century Textile 2024-2026,
AVCO 2024-2026, TKG Taekwang 2024-2026, Sansan 2021-2024 (test) and TPK Koja 2012-2014 (development).

Each policy is one side update (kind "policy") installed on any K*_n (build_gold.apply_side). Company rules are rank 3:
they beat the input convention and regulation defaults, and lose to mandatory regulation rules, in which case the
engine reports an override conflict (conflict_code where the clause table names one). Sources are the clause tables
dataset/10_kebijakan_perusahaan/klausul/*.csv: every element cites the clause id in its label and quotes of the clause
that contain its numbers, verified against the locked text dataset/13_teks/PKB-*/teks.txt; every dated element also
quotes the validity clause of the agreement (gate G2 grounds numbers and dates in the element's own quotes).

Validity: the calendar months the agreement covers (first day of the month it starts, last day of the month it ends).

Case data read by these rules (case["periods"][i]["hr"], 0 when absent; employee()/employer() attributes):
  months_of_service   full months of continuous service at the reference date of a payment made this period
                      (THR: up to the religious holiday; bonus: the policy's reference date)
  service_years       full years of service at the reference date of an award or leave payment made this period
  thr_holiday         1 in the period the religious holiday allowance (THR) is paid (names shared with
                      bg_support: months_of_service, days_terminated_before_holiday)
  leave_pay_paid      1 in the period annual leave money is paid; leave_days_paid: leave days compensated
  award_paid, bonus_paid, separation_paid   1 in the period that payment is made; separation_reason "resign", ...
  sick_month, furlough_month, detained_month   n-th month of continuous illness, lay-off at home, detention
  dependents          number of dependants (detention aid)
  family_events       number of weddings or bereavements this period that the policy supports
  unpaid_leave_months months of continuous unpaid leave in the THR year; days_terminated_before_holiday with
                      separation_reason 'resign': resigned before the holiday
  ot_work_h1, ot_work_h2plus       overtime minutes on working days in the first hour and in later hours
  ot_rest_h1_7, ot_rest_h8, ot_rest_h9, ot_rest_h10plus   overtime minutes on rest days and public holidays by
                      hour of the day (the language has no iteration over days, so the time sheet gives the split)
  days_present, days_absent_unpaid, workdays_in_month, ...   attendance (see each policy)
Monetary inputs keep the input convention: base_salary, fixed_allowance, other_regular, other_irregular, bonus, thr.
"""
import csv

from pph21kbs.config import REPO

from . import Doc, Update, fact, param, rule, table

KLAUSUL = REPO / "dataset" / "10_kebijakan_perusahaan" / "klausul"


class Clauses:
    """Clause table of one agreement: q(clause_id[, quote]) is a verified source entry of the clause."""

    def __init__(self, doc, csv_name):
        self.doc = doc
        with open(KLAUSUL / csv_name, encoding="utf-8") as f:
            self.rows = {r["id"]: r for r in csv.DictReader(f)}

    def provision(self, cid):
        r = self.rows[cid]
        head = r["pasal"] if r["pasal"].startswith("Lampiran") else f"Pasal {r['pasal']}"
        ayat = r["ayat"]
        if ayat in ("", "-"):
            return head
        return f"{head} ayat ({ayat})" if ayat[0].isdigit() else f"{head} {ayat}"

    def q(self, cid, quote=None):
        return self.doc.q(self.provision(cid), quote or self.rows[cid]["kutipan"])


def _company(short, policy, vf, vu, validity):
    def prs(rid, produces, expression, src, *, scope="period", cond=None, code=None, label="", fixed_point=None,
            overrides=()):
        src = src if isinstance(src, list) else [src]
        return rule(f"PRS.{short}.{rid}", produces, expression, src + [validity], vf, vu=vu, scope=scope, cond=cond,
                    layer="company", modality="default", policy=policy, code=code, label=label,
                    fixed_point=fixed_point, overrides=overrides)
    return prs


def _fact(name, ftype, src, label, label_id, scope="period"):
    return fact(name, ftype, scope, src if isinstance(src, list) else [src], label=label, label_id=label_id)


def _band(bands, default="0"):
    """Nested conditional: bands = [(condition, value), ...] tested in order."""
    expr = default
    for cond, value in reversed(bands):
        expr = f"({value} if {cond} else {expr})"
    return expr


def _factor(sick, furlough=None, detained=None):
    """Share of the wage paid in a month of long illness, lay-off at home, or detention (bands of the agreement)."""
    bands = [(f"hr('sick_month') > {m}", v) for m, v in sick]
    if furlough:
        bands += [(f"hr('furlough_month') > {m}", v) for m, v in furlough]
    if detained:
        months, shares = detained
        bands.append((f"hr('detained_month') > {months}", "0"))
        bands += [(f"hr('detained_month') > 0 and hr('dependents') >= {n}", v) for n, v in shares]
        bands.append(("hr('detained_month') > 0", "0"))
    return _band(bands, default="1")


def _overtime(hourly, work, rest):
    """Overtime pay: hourly wage x (multiplier x minutes / 60) per hour bucket, rounded once to the rupiah.
    work = (first hour, later hours); rest = multipliers for hours 1-7, 8, 9, 10+."""
    terms = [f"{work[0]} * hr('ot_work_h1')", f"{work[1]} * hr('ot_work_h2plus')",
             f"{rest[0]} * hr('ot_rest_h1_7')", f"{rest[1]} * hr('ot_rest_h8')", f"{rest[2]} * hr('ot_rest_h9')",
             f"{rest[3]} * hr('ot_rest_h10plus')"]
    return f"round({hourly} * ({' + '.join(terms)}) / 60, 1, 'half_up')"


ROUND = "param('pph_round_mode')"
ATTENDANCE = "(employee('attendance_permille') if employee('attendance_permille') != None else 0)"
SERVICE_YEARS = "(employee('service_years') if employee('service_years') != None else 0)"
GRADE = "(employee('avco_grade') if employee('avco_grade') != None else 'C')"


# ============================================================================================== WIKA
WIKA = Doc("PKB-WIKA-2025")


def _wika():
    c = Clauses(WIKA, "PKB_WIKA_2025_2026.csv")
    validity = WIKA.q("Diktum KEDUA", "berlaku terhitung tanggal 01 Maret 2025 s.d. 31 Desember 2026")
    prs = _company("WIKA", WIKA.id, "2025-03-01", "2026-12-31", validity)
    fp, tg = "income('base_salary')", "income('other_regular')"
    sick = c.q("WIKA-49-2", "lama sakit fixed pay perbulan 4 bulan pertama 100% 4 bulan kedua 85% 4 bulan ketiga 75%"
                            " > 12 bulan 50%")
    furlough = c.q("WIKA-36-2", "ke-1 s/d bulan ke-3 75% 0% ke-4 s/d bulan ke-6 70% 0% ke-7 s/d bulan ke-9 65% 0%"
                                " ke-10 s/d bulan ke-12 60% 0%")
    detained = c.q("WIKA-35-1", "untuk 1 (satu) orang tanggungan, 25% (dua puluh lima persen) dari upah (fixed pay);"
                                " b. untuk 2 (dua) orang tanggungan, 35% (tiga puluh lima persen) dari upah (fixed pay);"
                                " c. untuk 3 (tiga) orang tanggungan, 45% (empat puluh lima persen) dari upah (fixed pay);"
                                " d. untuk 4 (empat) orang tanggungan atau lebih, 50% (lima puluh persen)")
    detained6 = c.q("WIKA-35-1", "diberikan untuk paling lama 6 (enam) bulan terhitung sejak hari pertama pegawai ditahan")
    thr = [c.q("WIKA-31-3"), c.q("WIKA-31-4"), c.q("WIKA-31-5"), c.q("WIKA-31-6"), c.q("WIKA-31-7"), c.q("WIKA-31-8")]
    award = c.q("WIKA-44-1", "15 (lima belas) tahun satya karya 15 tahun 1,0 x fixed pay 20 (dua puluh) tahun satya"
                             " karya 20 tahun 1,5 x fixed pay 25 (dua puluh lima) tahun satya karya 25 tahun 2,0 x fixed"
                             " pay 30 (tiga puluh) tahun satya karya 30 tahun 2,5 x fixed pay 35 (tiga puluh lima) tahun"
                             " satya karya 35 tahun 3,0 x fixed pay")
    family = [c.q("WIKA-37-6", "1 sumbangan pernikahan 1 x fixed pay 2 sumbangan duka 1 x fixed pay"),
              c.q("WIKA-37-6", "1 sumbangan pernikahan 1,5 x fixed pay 2 sumbangan duka 1,5 x fixed pay")]
    separation = c.q("WIKA-90-1", ">=1 sd 3 tahun 1 (satu) kali fixed pay >3 sd 6 tahun 2 (dua) kali fixed pay > 6 sd 9"
                                  " tahun 3 (tiga) kali fixed pay >9 sd 12 tahun 4 (empat) kali fixed pay diatas 12 tahun"
                                  " 5 (lima) kali fixed pay")
    leave_comp = c.q("WIKA-52-7", "penggantian kompensasi berupa uang sesuai perhitungan sebagai berikut")
    leave = [c.q("WIKA-52-4"), c.q("WIKA-L1"),
             WIKA.q("Pasal 52 ayat (9)", "besarnya ekstra uang cuti dan ekstra hari cuti sebagaimana tercantum dalam"
                                         " lampiran-1 pkb ini")]
    bpjs = c.q("WIKA-32-4", "dasar pengali iuran bpjstk sebagaimana ayat (3) adalah fixed pay terakhir pegawai, dan"
                            " apabila fixed pay di bawah ump provinsi daerah khusus jakarta")
    return [
        _fact("wika_fixed_pay", "money", c.q("WIKA-4-13"), "Fixed Pay", "Fixed Pay"),
        _fact("wika_grade_allowance", "money", [c.q("WIKA-19-3"), c.q("WIKA-4-36")],
              "grade allowance (not a fixed allowance; outside the contribution base)", "Tunjangan Grade"),
        _fact("wika_take_home", "money", c.q("WIKA-4-35"), "take home pay = Fixed Pay + grade allowance",
              "Take Home Pay"),
        _fact("wika_pay_factor", "exact", [sick, furlough, detained], "share of Fixed Pay paid during illness, "
              "lay-off at home, or detention", "persentase Fixed Pay dibayar"),
        _fact("wika_leave_pay", "money", leave, "annual leave money with extra", "uang cuti dan ekstra uang cuti"),
        _fact("wika_service_award", "money", award, "long-service award (Satya Karya)", "penghargaan Satya Karya"),
        _fact("wika_family_aid", "money", family, "wedding and bereavement aid", "sumbangan pernikahan dan duka"),
        _fact("wika_retirement_prep_pay", "money", c.q("WIKA-76-5"), "retirement preparation pay (MPP)",
              "kompensasi Masa Persiapan Pensiun"),
        _fact("wika_separation_pay", "money", [separation, leave_comp],
              "separation pay and leave compensation on termination (final tax, PP 68/2009; not gross income)",
              "uang pisah dan kompensasi sisa cuti"),
        table("TAB.WIKA.EXTRA_LEAVE_PAY.2025", "wika_extra_leave_pay", "lookup", leave + [validity], "2025-03-01",
              vu="2026-12-31", label_id="ekstra uang cuti menurut masa kerja (Lampiran 1, tabel gambar PDF hlm. 78)",
              rows_ref={"extracted_table": "PKB-WIKA-2025/LAMPIRAN-1",
                        "columns": {"key": "masa_kerja_tahun", "value": "ekstra_uang_cuti_persen"},
                        "value_scale": "percent"}),
        prs("FIXED_PAY", "wika_fixed_pay", fp, c.q("WIKA-4-13"), label="WIKA-4-13: Fixed Pay set by decree (input)"),
        prs("GRADE", "wika_grade_allowance", tg, c.q("WIKA-19-3"),
            label="WIKA-19-3, 4-36: grade allowance entered as other regular income"),
        prs("THP", "wika_take_home", "wika_fixed_pay + wika_grade_allowance", c.q("WIKA-4-35"),
            label="WIKA-4-35, 19-3"),
        prs("PAY_FACTOR", "wika_pay_factor",
            _factor([(12, "dec('0.50')"), (8, "dec('0.75')"), (4, "dec('0.85')"), (0, "1")],
                    [(9, "dec('0.60')"), (6, "dec('0.65')"), (3, "dec('0.70')"), (0, "dec('0.75')")],
                    (6, [(4, "dec('0.50')"), (3, "dec('0.45')"), (2, "dec('0.35')"), (1, "dec('0.25')")])),
            [sick, furlough, detained, detained6],
            label="WIKA-49-2 illness 100/85/75/50%, 36-2 lay-off 75/70/65/60%, 35-1 detention aid 25-50% of Fixed Pay "
                  "for at most 6 months"),
        prs("BASE_SALARY", "base_salary", f"round({fp} * wika_pay_factor, 1, 'half_up')", [sick, furlough, detained],
            label="Fixed Pay actually paid this period"),
        prs("GRADE_PAID", "other_regular_income",
            f"0 if (hr('sick_month') > 0 or hr('furlough_month') > 0 or hr('detained_month') > 0) else {tg}",
            [furlough, sick, c.q("WIKA-50-4")],
            label="WIKA-36-2 grade allowance 0% when laid off; 49-2 and 35-1 name Fixed Pay only; 50-4 full THP on "
                  "maternity leave"),
        prs("METHOD", "withholding_method", "'employer_borne'", c.q("WIKA-22-2"), scope="year",
            label="WIKA-22-2: PPh 21 borne by the company (except production bonus and IHL: not formalised, the "
                  "regulation rule fixes the borne tax as the whole tax of the period)"),
        prs("DTP_WITHHELD", "pph21_dtp", "0", [c.q("WIKA-22-3"), c.q("WIKA-P22-3")], code="C4",
            label="WIKA-22-3: government tax incentives are not passed to employees (C4, latent: construction KLU "
                  "is not eligible)"),
        prs("THR", "thr",
            "0 if (hr('unpaid_leave_months') >= 10 or (hr('days_terminated_before_holiday') > 0 and hr('separation_reason') == 'resign') or hr('months_of_service') <= 1)"
            " else round(min(max(0, hr('months_of_service') - hr('unpaid_leave_months')), 12) * wika_take_home / 12,"
            " 1, 'half_up')", thr, cond="hr('thr_holiday') > 0",
            label="WIKA-31-3..8: THR 1 x THP after 12 months, proportional above 1 month (exactly 1 month: none, C10 "
                  "latent), none after >= 10 months unpaid leave or on resignation within 30 days (C10 latent); "
                  "31-6 numerator read as service months minus unpaid leave months"),
        prs("LEAVE_PAY", "wika_leave_pay",
            "wika_fixed_pay + (round(wika_fixed_pay * lookup('wika_extra_leave_pay', hr('service_years')), 1,"
            " 'half_up') if hr('service_years') in (5, 10, 15, 20, 25, 30, 35) else 0)",
            leave, cond="hr('leave_pay_paid') > 0",
            label="WIKA-52-4, L1: leave money 1 x FP once a year in the hiring month, extra 50-200% FP at 5..35 "
                  "years of service (paid at the minimum)"),
        prs("NO_LEAVE_PAY", "wika_leave_pay", "0", c.q("WIKA-52-4"), cond="hr('leave_pay_paid') <= 0"),
        prs("SERVICE_AWARD", "wika_service_award",
            "round(wika_fixed_pay * " + _band([
                ("hr('service_years') == 15", "1"), ("hr('service_years') == 20", "dec('1.5')"),
                ("hr('service_years') == 25", "2"), ("hr('service_years') == 30", "dec('2.5')"),
                ("hr('service_years') == 35", "3")]) + ", 1, 'half_up')",
            [award, c.q("WIKA-44-2"), c.q("WIKA-44-4")], cond="hr('award_paid') > 0",
            label="WIKA-44-1, 44-2, 44-4: Satya Karya at 15..35 years (service to 11 March), paid in the "
                  "anniversary payroll; the gold medal (44-3) is not formalised"),
        prs("NO_SERVICE_AWARD", "wika_service_award", "0", c.q("WIKA-44-4"), cond="hr('award_paid') <= 0"),
        prs("FAMILY_AID", "wika_family_aid",
            "(round(wika_fixed_pay * (dec('1.5') if employee('wika_class') == 'terampil' else 1), 1, 'half_up')"
            " * hr('family_events') if hr('service_years') >= 1 else 0)", family,
            label="WIKA-37-6/7: 1 x FP (Organik) or 1.5 x FP (Terampil) per event, service >= 1 year"),
        prs("RETIREMENT_PREP", "wika_retirement_prep_pay", "wika_fixed_pay * hr('retirement_prep_months')",
            c.q("WIKA-76-5"), label="WIKA-76-5: MPP months (3/6/9/12 by service and category, case data) x FP, "
                                    "paid at once"),
        prs("OTHER_IRREGULAR", "other_irregular_income",
            "income('other_irregular') + wika_leave_pay + wika_service_award + wika_family_aid"
            " + wika_retirement_prep_pay", [c.q("WIKA-52-4"), c.q("WIKA-44-4"), c.q("WIKA-37-6"), c.q("WIKA-76-5")],
            label="irregular income added by the agreement"),
        prs("SEPARATION_PAY", "wika_separation_pay",
            "(wika_fixed_pay * " + _band([
                ("hr('months_of_service') > 12 * 12", "5"), ("hr('months_of_service') > 9 * 12", "4"),
                ("hr('months_of_service') > 6 * 12", "3"), ("hr('months_of_service') > 3 * 12", "2"),
                ("hr('months_of_service') >= 12", "1")]) + " if hr('separation_reason') == 'resign' else 0)"
            " + round(wika_take_home * hr('leave_days_paid') / 21, 1, 'half_up')",
            [separation, leave_comp], cond="hr('separation_paid') > 0",
            label="WIKA-90-1 separation pay 1-5 x FP by service; 52-7 THP x remaining leave days / 21"),
        prs("NO_SEPARATION_PAY", "wika_separation_pay", "0", c.q("WIKA-90-1"), cond="hr('separation_paid') <= 0"),
        prs("BPJS_WAGE", "bpjs_wage",
            "max(wika_fixed_pay, employer('regional_minimum_wage') if employer('regional_minimum_wage') != None else 0)",
            [bpjs, c.q("WIKA-4-36")], code="C8",
            cond="max(wika_fixed_pay, employer('regional_minimum_wage') if employer('regional_minimum_wage') != None"
                 " else 0) < base_salary + fixed_allowance",
            label="WIKA-32-4, 4-36: contribution base = last Fixed Pay, at least the DKI minimum wage; the grade "
                  "allowance is excluded. Active only when that base is narrower than the statutory base (C8); a "
                  "wider base is allowed and is not a conflict (second reader, pkb.cek.csv item 2)"),
    ]


WIKA_NOTE = ("PKB PT Wijaya Karya 2025-2026. Not formalised: 23-1, 24, 32-6, 33-1, 37-10, 70-1a7 (no amounts or formula "
             "in the agreement), 22-2 for production bonus and IHL (partial tax bearing: the regulation rule fixes the "
             "borne tax as the whole tax of the period), 26-3 (cash or in kind decided by the unit), 28 and 30-1 "
             "(amounts set by the board; entered as bonus input), 44-3 (gold medal value), 89-2 and L2 (severance "
             "under PP 35/2021, final tax), 91-1 (debt set-off). 4-13, 19-3, 4-35, 21, 22-1, 50-4 need no element "
             "beyond the definitions (inputs, payment timing, data condition).")

# ============================================================================================== Century Textile
CENTEX = Doc("PKB-CENTEX-2024")


def _centex():
    c = Clauses(CENTEX, "PKB_Century_Textile_2024_2026.csv")
    validity = CENTEX.q("Pasal 59 ayat (3)", "27 maret 2024 sampai dengan tanggal 26 maret 2026")
    prs = _company("CENTEX", CENTEX.id, "2024-03-01", "2026-03-31", validity)
    ot = c.q("CENTEX-L1", "hari biasa : jam 1 = 1,5 x u.p. jam 2 dan seterusnya = 2 x u.p b. hari libur group/hari"
                          " besar nasional : jam 1-7 = 2 x u.p. jam ke 8 = 3 x u.p. jam ke 9 dan seterusnya = 4 x u.p."
                          " c. hari libur resmi/hari besar nasional pada hari terpendek untuk non 4 group 3 shift jam"
                          " 1-5 = 2 x u.p. jam ke 6 = 3 x u.p. jam ke 7 dan seterusnya = 4 x u.p.")
    up = c.q("CENTEX-L1C", "gaji bulanan ii dan bulanan tetap : u.p = b + c + d + e + f + g 173")
    sched = [c.q("CENTEX-13-1d", "tiap kelompok pekerja yang bekerja dalam giliran malam bekerja satu seperempat jam"
                                 " sebagai kerja lembur. 2.1. tiap kelompok pekerja bekerja lima jam sebagai kerja"
                                 " lembur pada tiap hari yang ke-28"),
             CENTEX.q("Pasal 13 ayat 1 huruf e", "tiap kelompok pekerja yang bekerja dalam giliran malam, bekerja satu"
                                                 " jam sebagai kerja lembur. 1.2 tiap kelompok pekerja yang bekerja"
                                                 " hari sabtu, bekerja dua jam sebagai kerja lembur"),
             CENTEX.q("Pasal 13 ayat 1 huruf c", "pekerja yang bekerja pada hari sabtu, bekerja 3 jam sebagai kerja"
                                                 " lembur")]
    thr = c.q("CENTEX-24", "tunjangan hari raya (tahun baru) sebesar 120% x satu bulan upah")
    thr2 = CENTEX.q("Pasal 24", "telah bekerja pada perusahaan sekurang-kurangnya satu bulan terus menerus atau lebih."
                                " pekerja yang phk dengan waktu sudah memasuki bulan puasa berhak")
    bonus = [c.q("CENTEX-25"),
             c.q("CENTEX-25-1", "pekerja dengan masa kerja sembilan bulan atau lebih, tetapi kurang dari satu tahun"
                                " mendapat 75%. b. pekerja dengan masa kerja enam bulan atau lebih, tetapi kurang dari"
                                " sembilan bulan mendapat 50%. c. pekerja dengan masa kerja tiga bulan atau lebih, tetapi"
                                " kurang dari enam bulan mendapat 25%. d. pekerja dalam masa percobaan mendapat 10%."),
             c.q("CENTEX-25-2")]
    retire = c.q("CENTEX-L6", "21 desember - 20 januari 1/12 x 1 bulan upah 2.21 januari - 20 februari 2/12 x 1 bulan"
                              " upah")
    leave = [c.q("CENTEX-15-1", "penggantian sisa cuti dengan uang hanya berlaku bagi pekerja yang prosentase"
                                " kehadirannya dalam satu tahun 98,50% ke atas"),
             c.q("CENTEX-L2", "penggantian sisa cuti 1,5 x [ b + c + d + e + f + g 30 ] x a")]
    absence = [c.q("CENTEX-L3"), c.q("CENTEX-L3", "4 group 3 shift jumlah hari 30 x gaji pokok x 1.125 b. non 4 group"
                                                  " 3 shift jumlah hari 30 x gaji pokok"),
               c.q("CENTEX-44-1", "statusnya dirubah dari bulanan ii menjadi bulanan tetap dengan syarat prosentase"
                                  " absen kehadirannya paling sedikit 98.00%")]
    sick = c.q("CENTEX-27-2", "untuk 4 bulan pertama dibayar 100% b. untuk 4 bulan kedua dibayar 75% c. untuk 4 bulan"
                              " ketiga dibayar 50% d. untuk selanjutnya dibayar 25%")
    sanction = c.q("CENTEX-46-1", "pengurangan gaji ( pemotongan upah ) sebesar 10% kali gaji per bulan , paling lama 3"
                                  " bulan")
    aid = [c.q("CENTEX-31", "yaitu sebesar rp250.000,- ( dua ratus lima puluh ribu rupiah )"),
           c.q("CENTEX-35-1", "pekerja berkeluarga : rp685.000,- b. pekerja bujangan (lajang) : rp585.000,- c."
                              " isteri/suami pekerja : rp255.000,- d. anak kandung : rp255.000,- e. ayah/ibu kandung :"
                              " rp205.000,- f. ayah/ibu mertua : rp205.000,-"),
           c.q("CENTEX-35-1", "sumbangan pernikahan pertama kepada pekerja sebesar rp225.000,-"),
           c.q("CENTEX-35-1", "sampai dengan anak ketiga sebesar rp.180.000,-")]
    repair = c.q("CENTEX-14-5b")
    lag = c.q("CENTEX-33-4", "penyesuaian iuran asuransi atas gaji baru , dilaksanakan dua bulan sesudah gaji baru"
                             " selesai dinegosiasikan")
    jkk = c.q("CENTEX-33-3a", "jaminan kecelakaan kerja 0,89% dari upah, dibayar pengusaha")
    wage = "centex_wage"
    hourly = "centex_hourly_wage"
    sick_factor = _factor([(12, "dec('0.25')"), (8, "dec('0.50')"), (4, "dec('0.75')"), (0, "1")])
    return [
        _fact("centex_wage", "money", [c.q("CENTEX-2-14"), up], "one month wage B+C+D+E+F+G", "satu bulan upah"),
        _fact("centex_hourly_wage", "exact", up, "overtime hourly wage (B+...+G)/173", "upah per jam lembur"),
        _fact("centex_pay_factor", "exact", sick, "share of wage paid in long illness", "persentase upah sakit"),
        _fact("centex_ot_workday", "money", ot, "overtime on working days", "lembur hari biasa"),
        _fact("centex_ot_restday", "money", ot, "overtime on group rest days and holidays", "lembur hari libur"),
        _fact("centex_ot_scheduled", "money", sched, "scheduled overtime of shift work", "lembur terjadwal"),
        _fact("centex_bonus", "money", bonus, "annual bonus by service band", "bonus tahunan"),
        _fact("centex_retirement_bonus", "money", retire, "extra bonus on retirement at 55", "tambahan bonus pensiun"),
        _fact("centex_leave_compensation", "money", leave, "cash for unused leave", "penggantian sisa cuti"),
        _fact("centex_absence_deduction", "money", absence, "deduction for unpaid absence (Bulanan II)",
              "potongan absen"),
        _fact("centex_sanction_deduction", "money", sanction, "disciplinary wage cut", "pengurangan gaji sanksi"),
        _fact("centex_aid", "money", aid, "glasses, bereavement, wedding and birth aid", "bantuan dan sumbangan"),
        prs("WAGE", wage, "income('base_salary') + income('fixed_allowance')", [c.q("CENTEX-2-14"), up],
            label="CENTEX-2-14, L1C: wage includes the allowances B..G (entered as base salary and fixed allowance)"),
        prs("HOURLY", hourly, f"{wage} / 173", up, label="CENTEX-L1C, 22-2"),
        prs("PAY_FACTOR", "centex_pay_factor", sick_factor, sick, label="CENTEX-27-2: 100/75/50/25% per 4 months"),
        prs("BASE_SALARY", "base_salary", "round(income('base_salary') * centex_pay_factor, 1, 'half_up')", sick,
            label="CENTEX-27-2 applied to the base wage"),
        prs("FIXED_ALLOWANCE", "fixed_allowance", "round(income('fixed_allowance') * centex_pay_factor, 1, 'half_up')",
            sick, label="CENTEX-27-2 applied to the fixed allowances"),
        prs("METHOD", "withholding_method", "'employer_borne'", c.q("CENTEX-28"), scope="year",
            label="CENTEX-28: PPh 21 on all income borne by the company"),
        prs("JKK_RATE", "jkk_rate", "dec('0.0089')", jkk, code="C6",
            label="CENTEX-33-3a: JKK 0.89% fixed in the agreement (C6 when the relief of PP 7/2025 and PP 36/2025 "
                  "applies)"),
        prs("BPJS_WAGE", "bpjs_wage",
            "value_in('base_salary', max(first_month, month - 2)) + value_in('fixed_allowance', max(first_month,"
            " month - 2))", lag, code="C6",
            label="CENTEX-33-4: contributions follow a new wage two months later (C6 latent: base of a superseded "
                  "wage during the lag)"),
        prs("THR", "thr", f"round(dec('1.2') * {wage}, 1, 'half_up') if hr('months_of_service') >= 1 else 0",
            [thr, thr2], cond="hr('thr_holiday') > 0",
            label="CENTEX-24: 120% of one month wage after at least one month, not prorated"),
        prs("OT_WORKDAY", "centex_ot_workday",
            f"round({hourly} * (dec('1.5') * hr('ot_work_h1') + 2 * hr('ot_work_h2plus')) / 60, 1, 'half_up')",
            [ot, up], label="CENTEX-L1 a: hour 1 1.5x, hour 2+ 2x; fractional hours pro rata"),
        prs("OT_RESTDAY", "centex_ot_restday",
            f"round({hourly} * (2 * hr('ot_rest_h1_7') + 3 * hr('ot_rest_h8') + 4 * (hr('ot_rest_h9')"
            " + hr('ot_rest_h10plus')) + 2 * hr('ot_short_h1_5') + 3 * hr('ot_short_h6') + 4 * hr('ot_short_h7plus'))"
            " / 60, 1, 'half_up')", [ot, up],
            label="CENTEX-L1 b-c: group rest day or holiday 2x/3x/4x; official holiday on the shortest day 2x (1-5), "
                  "3x (6), 4x (7+)"),
        prs("OT_SCHEDULED", "centex_ot_scheduled",
            f"round({hourly} * (2 * hr('night_shifts_4g3s') + (dec('1.5') + 2 * 4) * hr('day28_shifts')"
            " + dec('1.5') * hr('night_shifts_3g') + (dec('1.5') + 2) * hr('saturdays_3g')"
            " + (dec('1.5') + 2 + 2) * hr('saturdays_warehouse')), 1, 'half_up')", sched + [ot, up],
            label="CENTEX-13-1d: scheduled overtime 1 1/4 h per night shift (1.5x + 1/4 h at 2x = 2 hour-units), "
                  "5 h on day 28, 1 h night and 2 h Saturday (3 groups), 3 h Saturday (warehouse)"),
        prs("OVERTIME", "overtime_pay", "centex_ot_workday + centex_ot_restday + centex_ot_scheduled", [ot, up],
            label="CENTEX-22-2: overtime pay of the agreement"),
        prs("BONUS_AMOUNT", "centex_bonus",
            "round((hr('bonus_wage_base') if hr('bonus_wage_base') > 0 else " + wage + ") * " + _band([
                ("employee('centex_probation') == True", "dec('0.10')"), ("hr('months_of_service') >= 12", "1"),
                ("hr('months_of_service') >= 9", "dec('0.75')"), ("hr('months_of_service') >= 6", "dec('0.50')"),
                ("hr('months_of_service') >= 3", "dec('0.25')")]) + ", 1, 'half_up')",
            bonus, cond="hr('bonus_paid') > 0",
            label="CENTEX-25, 25-1, 25-2: one month wage (December wage, alpha = 0) by service band at 20 December"),
        prs("NO_BONUS", "centex_bonus", "0", bonus[:1], cond="hr('bonus_paid') <= 0"),
        prs("RETIREMENT_BONUS", "centex_retirement_bonus",
            f"round({wage} * hr('retirement_bonus_twelfths') / 12, 1, 'half_up')", retire,
            label="CENTEX-L6: n/12 x one month wage on retirement at 55, n by exit period (case data)"),
        prs("BONUS", "bonus", "income('bonus') + centex_bonus + centex_retirement_bonus", bonus + [retire],
            label="bonus paid under the agreement"),
        prs("LEAVE_COMPENSATION", "centex_leave_compensation",
            f"0 if hr('leave_days_paid') <= 0 else (round(dec('1.5') * {wage} * hr('leave_days_paid') / 30, 1,"
            f" 'half_up') if {ATTENDANCE} >= 10 * dec('98.5') else 0)", leave,
            label="CENTEX-15-1, L2: 1.5 x wage/30 x days, attendance at least 98.50% (employee attendance_permille)"),
        prs("ABSENCE", "centex_absence_deduction",
            "0 if hr('days_absent_unpaid') <= 0 else (round(income('base_salary') * hr('days_absent_unpaid') * (1125"
            " if employee('centex_four_group_three_shift') == True else 1000) / (30 * 1000), 1, 'half_up') if not"
            f" ({SERVICE_YEARS} > 5 and {ATTENDANCE} >= 10 * 98) else 0)", absence,
            label="CENTEX-L3, 44-1: Bulanan II workers lose days/30 x base x 1.125 (4 groups 3 shifts) or x 1; "
                  "Bulanan Tetap status after 5 years with attendance >= 98%"),
        prs("SANCTION", "centex_sanction_deduction",
            "round(dec('0.10') * income('base_salary'), 1, 'half_up') if hr('sanction_month') > 0 and"
            " hr('sanction_month') <= 3 else 0", sanction, label="CENTEX-46-1: wage cut 10% for at most 3 months"),
        prs("AID", "centex_aid",
            "250000 * hr('glasses_aid') + 685000 * hr('death_worker_married') + 585000 * hr('death_worker_single')"
            " + 255000 * (hr('death_spouse') + hr('death_child')) + 205000 * (hr('death_parent') + hr('death_parent_in_law'))"
            " + 225000 * hr('first_wedding') + 180000 * hr('births')", aid,
            label="CENTEX-31 glasses 250,000; 35-1 bereavement 685/585/255/255/205/205 thousand, wedding 225,000, "
                  "birth 180,000"),
        prs("OTHER_REGULAR", "other_regular_income",
            "income('other_regular') + 23000 * hr('repair_calls') - centex_absence_deduction - centex_sanction_deduction",
            [repair] + absence + [sanction],
            label="CENTEX-14-5b repair call incentive 23,000 (written in words); deductions reduce gross income "
                  "(GT5 putusan 14)"),
        prs("OTHER_IRREGULAR", "other_irregular_income", "income('other_irregular') + centex_leave_compensation"
            " + centex_aid", leave + aid, label="irregular income added by the agreement"),
    ]


CENTEX_NOTE = ("PKB PT Century Textile Industry 2024-2026. Not formalised: 20-1, 21, 39 (nominal amounts outside the "
               "agreement; inputs), 20-2e (timing of raises: wage input), 26 (deduction list; inputs), 47-2 (full wage, "
               "no change), 53-4 and 55 (severance under PP 35/2021, final tax), 56 (gold souvenir value), L4 (unit "
               "unclear). 25 alpha undefined: alpha = 0 (GT5 putusan 12). 33-3b and 34 restate the regulation.")

# ============================================================================================== AVCO
AVCO = Doc("PKB-AVCO-2024")


def _avco():
    c = Clauses(AVCO, "PKB_AVCO_2024_2026.csv")
    validity = AVCO.q("Pasal 65 ayat 1", "pkb ini berlaku selama 2 tahun sejak 1 april 2024 dan berakhir pada 31 maret"
                                         " 2026")
    prs = _company("AVCO", AVCO.id, "2024-04-01", "2026-03-31", validity)
    base = "income('base_salary')"
    hourly_q = c.q("AVCO-22-3a")
    ot_q = [hourly_q,
            c.q("AVCO-22-3b1", "kerja lembur pertama setelah 8 jam dalam 1 hari, pekerja/buruh pratama 22 berhak menerima"
                               " upah kerja lembur sebesar 1,5 kali upah kerja lembur per jam. b.1.2. jam kerja lembur"
                               " ke-2 dan seterusnya, pekerja/buruh pratama berhak menerima upah kerja lembur sebesar 2"
                               " kali"),
            c.q("AVCO-22-3b2"),
            c.q("AVCO-22-3b3", "untuk 7 jam pertama pekerja/buruh pratama berhak menerima upah kerja lembur sebesar 2"
                               " kali upah kerja lembur per jam. b.3.2. untuk jam ke-8 pekerja/buruh pratama berhak"
                               " menerima upah kerja lembur sebesar 3 kali upah kerja lembur per jam. b.3.3. untuk jam"
                               " ke-9 dan seterusnya, pekerja/buruh pratama berhak menerima upah kerja lembur sebesar 4"
                               " kali"),
            c.q("AVCO-22-2")]
    ug = c.q("AVCO-22-3c", "premi kerja lembur tambahan (ug overtime premium) sebesar 35% dari jumlah nominal upah kerja"
                           " lembur pada bulan berjalan")
    thr = [c.q("AVCO-23-1"), c.q("AVCO-23-1a"),
           AVCO.q("Pasal 23 ayat 1 huruf d", "yang hubungan kerjanya berakhir 30 hari kalender atau kurang sebelum tanggal"
                                             " hari raya keagamaannya berhak atas tunjangan hari raya")]
    shift = c.q("AVCO-23-3", "menerima tunjangan kerja gilir sebesar rp.55.000,-, dan yang bekerja gilir tidak di tambang"
                             " terbuka atau bawah tanah menerima tunjangan sebesar rp30.000.- b. pekerja/buruh pratama"
                             " yang bekerja malam diberikan bonus perangsang sebesar rp.25.000,-/malam")
    shift2 = AVCO.q("Pasal 23 ayat 3 huruf c", "pabrik pengeringan (dewatering plant) menerima tunjangan kerja gilir"
                                               " sebesar rp25.000,-")
    transport = [c.q("AVCO-23-5", "adapun besar bantuan uang transportasi adalah rp28.000,- per hari per kehadiran. c)"
                                  " bantuan transportasi ini tidak diberikan terhadap pekerja/buruh yang tinggal di"
                                  " akomodasi perusahaan d) bantuan transportasi darat bagi pekerja/buruh pratama jakarta"
                                  " diberikan sebesar rp500.000,- per bulan")]
    acting = c.q("AVCO-23-2", "akan menerima bonus sebesar 20% dari upah pokok tertinggi dari golongan tertinggi (a5)"
                              " selama memegang jabatan itu")
    scale = [c.q("AVCO-L2", "upah pokok bulanan pekerja/buruh pratama terdapat pada tabel skala upah pokok yang tercantum"
                            " dalam pkb lampiran i dan lampiran ii")]
    radiation = c.q("AVCO-23-8", "pengusaha memberikan tunjangan radiasi sebesar maksimal rp950.000,- per bulan (net)")
    absence = [c.q("AVCO-24-3"),
               AVCO.q("Pasal 1 angka 26", "jam kerja reguler: jam kerja yang mengacu kepada peraturan perundangan yang"
                                          " berlaku, yaitu 7 atau 8 jam per hari")]
    sick = c.q("AVCO-30-5", "4 bulan pertama 100% 4 bulan kedua 75% 4 bulan ketiga 50% b. untuk bulan selanjutnya dibayar"
                            " sebesar 25% dari upah sebelum")
    leave = c.q("AVCO-23-4", "berhak atas tunjangan cuti sebesar 1 bulan upah pokok. b untuk memperoleh tunjangan ini,"
                             " pekerja/buruh pratama wajib mempunyai masa kerja sekurang-kurangnya 90 hari")
    travel = c.q("AVCO-26-1e")
    perdiem = c.q("AVCO-28-4", "a. pekerja/buruh : rp500.000,- per hari. b. isteri/suami : rp500.000,- per hari. c. anak :"
                               " rp250.000,- per hari/orang")
    pilgrimage = c.q("AVCO-30-6c")
    glasses = c.q("AVCO-32-2", "termasuk bingkai dan lensa, maksimal senilai rp.1.400.000,-/tahun")
    lens = c.q("AVCO-32-2", "penggantian biaya pembelian lensa kacamata berdasarkan resep dokter, maksimal senilai"
                            " rp.600.000,- pertahun")
    medivac = c.q("AVCO-33-1d", "tunjangan perdiem medivac adalah sebagai berikut: dewasa rp500.000,- per hari, anak"
                                " rp250.000,- per hari")
    dental = [c.q("AVCO-34-8"), c.q("AVCO-34-8", "memerlukan pendidikan khusus (contoh: autisme) maksimal sebesar"
                                                 " rp.2.000.000,-/bulan")]
    edu = c.q("AVCO-36-1", "paud (1 tahun) rp2.960.000,- tk (2 tahun) rp5.330.000,- sd (6 tahun) rp10.650.000,- sltp (3"
                           " tahun) rp12.420.000,- slta (3 tahun) rp14.190.000,- slb (selama 12 tahun) rp17.750.000,- pt"
                           " (5 tahun) rp17.750.000,-")
    savings = c.q("AVCO-42-2", "tingkat kompetensi master (golongan a) maksimal sebesar rp.1.500.000,- per bulan b."
                               " tingkat kompetensi spesialis (golongan b) maksimal sebesar rp.1.250.000,- per bulan c."
                               " tingkat kompetensi dasar (golongan f - golongan c) maksimal sebesar rp.1.000.000,-")
    savings_once = c.q("AVCO-42-4", "pembayaran (one time payment) sebesar rp2.000.000.-")
    housing = c.q("AVCO-44-1a")
    living = c.q("AVCO-44-4", "lajang yang tinggal di luar akomodasi perusahaan sebesar rp.7.000.000,- per tahun. b.2."
                              " menikah yang tinggal di dalam akomodasi perusahaan sebesar rp.8.700.000,- per tahun. b.3."
                              " menikah yang tinggal di luar akomodasi perusahaan sebesar rp.10.400.000,-")
    ta = c.q("AVCO-LX-3d")
    jkk = c.q("AVCO-41-2", "program jaminan kecelakaan kerja: 1,74% dibayar oleh pengusaha")
    jht = c.q("AVCO-41-2", "program jaminan hari tua: 3,70% dibayar oleh pengusaha + iuran 2,00% dibayar oleh"
                           " pekerja/buruh")
    death = [c.q("AVCO-38-1", "pengusaha akan membayarkan santunan kematian sebesar 1 tahun upah"),
             c.q("AVCO-38-1", "pengusaha akan membayarkan santunan kematian sebesar 3 bulan upah"),
             c.q("AVCO-39-3"), c.q("AVCO-55")]
    sick_factor = _factor([(12, "dec('0.25')"), (8, "dec('0.50')"), (4, "dec('0.75')"), (0, "1")])
    radiation_expr = ("min(hr('radiation_net'), 950000) + round(bracket('ter_monthly', ter_category, gross_income)"
                      f" * gross_income, 1, {ROUND}) - round(bracket('ter_monthly', ter_category, gross_income"
                      f" - avco_radiation_allowance) * (gross_income - avco_radiation_allowance), 1, {ROUND})")
    return [
        _fact("avco_hourly_wage", "exact", hourly_q, "overtime hourly wage = monthly wage / 173",
              "upah kerja lembur per jam"),
        _fact("avco_pay_factor", "exact", sick, "share of wage paid in long illness", "persentase upah sakit"),
        _fact("avco_shift_allowance", "money", [shift, shift2], "shift and night allowances", "tunjangan kerja gilir"),
        _fact("avco_transport", "money", transport, "transport allowance", "bantuan transportasi"),
        _fact("avco_acting_supervisor", "money", acting, "acting supervisor bonus", "bonus pejabat penyelia sementara"),
        _fact("avco_radiation_allowance", "money", radiation,
              "radiation allowance grossed up: net amount plus the extra PPh 21 it causes", "tunjangan radiasi"),
        _fact("avco_absence_deduction", "money", absence, "deduction for absconding", "potongan mangkir"),
        _fact("avco_savings_employer", "money", savings, "employer savings-plan contribution", "kontribusi tabungan"),
        _fact("avco_irregular", "money", [leave, travel, perdiem, pilgrimage, glasses, medivac, edu, housing, living],
              "irregular allowances and reimbursements of the agreement", "tunjangan dan penggantian tidak teratur"),
        _fact("avco_termination_pay", "money", death,
              "separation pay, death benefit and funeral aid (final tax, PP 68/2009; not gross income)",
              "uang pisah dan santunan kematian"),
        table("TAB.AVCO.WAGE_SCALE.2024", "avco_wage_scale", "lookup", scale + [validity], "2024-04-01",
              label_id="skala upah pokok April 2024 (Lampiran I, tabel gambar; golongan yang terbaca)",
              rows_ref={"extracted_table": "PKB-AVCO-2024/LAMPIRAN-I",
                        "columns": {"key": "golongan", "value": "upah_pokok"}}),
        table("TAB.AVCO.WAGE_SCALE.2025", "avco_wage_scale", "lookup",
              scale + [c.q("AVCO-21-6"), validity], "2025-04-01", vu="2026-03-31",
              label_id="skala upah pokok April 2025 (Lampiran II, tabel gambar; golongan yang terbaca)",
              rows_ref={"extracted_table": "PKB-AVCO-2024/LAMPIRAN-II",
                        "columns": {"key": "golongan", "value": "upah_pokok"}}),
        prs("METHOD", "withholding_method", "'gross'", c.q("AVCO-20-10"), scope="year",
            label="AVCO-20-10: PPh 21 withheld from the employee"),
        prs("HOURLY", "avco_hourly_wage", f"{base} / 173", hourly_q,
            label="AVCO-22-3a: monthly wage / 173; for Pratama the wage is the base wage (GT5 putusan 12)"),
        prs("PAY_FACTOR", "avco_pay_factor", sick_factor, sick, label="AVCO-30-5: 100/75/50% per 4 months, then 25%"),
        prs("BASE_SALARY", "base_salary", f"round({base} * avco_pay_factor, 1, 'half_up')", sick,
            label="base wage paid this period"),
        prs("OVERTIME", "overtime_pay",
            f"(round(round(avco_hourly_wage * (dec('1.5') * hr('ot_work_h1') + 2 * hr('ot_work_h2plus')"
            " + 2 * hr('ot_rest_h1_7') + 3 * hr('ot_rest_h8') + 4 * (hr('ot_rest_h9') + hr('ot_rest_h10plus'))"
            " + 2 * hr('ot_short_h1_5') + 3 * hr('ot_short_h6') + 4 * hr('ot_short_h7plus')) / 60, 1, 'half_up')"
            " * (1 + (dec('0.35') if employee('avco_underground') == True else 0)), 1, 'half_up')"
            " if employee('avco_pratama') != False else 0)", ot_q + [ug],
            label="AVCO-22-2..3: Pratama only; working days 1.5x first hour then 2x; rest days and holidays 2x "
                  "(1-7), 3x (8), 4x (9+); holiday on the shortest day of a 6-day pattern 2x/3x/4x; underground "
                  "+35%"),
        prs("THR", "thr",
            f"round(2 * {base} * min(hr('months_of_service'), 12) / 12, 1, 'half_up') if hr('months_of_service') >= 1 else 0",
            thr, cond="hr('thr_holiday') > 0",
            label="AVCO-23-1, 23-1a: 2 x base wage, proportional months/12 below 12 months"),
        prs("SHIFT", "avco_shift_allowance",
            "hr('shift_days') * " + _band([("employee('avco_shift_location') == 'mine'", "55000"),
                                          ("employee('avco_shift_location') == 'non_shift_mine'", "25000")],
                                         default="30000") + " + 25000 * hr('night_shifts')", [shift, shift2],
            label="AVCO-23-3: per shift day 55,000 (mine), 30,000 (elsewhere), 25,000 (non-shift at mine or mill); "
                  "night +25,000"),
        prs("TRANSPORT", "avco_transport",
            "(500000 if employee('avco_location') == 'jakarta' else (0 if employee('avco_in_accommodation') == True"
            " else 28000 * hr('days_present')))", transport,
            label="AVCO-23-5: 28,000 per day present (not for residents of company housing); Jakarta 500,000 a month"),
        prs("ACTING", "avco_acting_supervisor",
            "round(dec('0.20') * lookup('avco_wage_scale', 'A5'), 1, 'half_up') if hr('acting_supervisor') > 0 else 0",
            [acting] + scale, label="AVCO-23-2: 20% of the A5 base wage while acting (day proration not formalised)"),
        prs("RADIATION", "avco_radiation_allowance", radiation_expr, radiation,
            cond="hr('radiation_net') > 0 and not is_final_period", fixed_point=("0", "1000000000000"),
            label="AVCO-23-8: net allowance; the extra PPh it causes is borne by the company and grossed up (least "
                  "fixed point, GT5 putusan 3); in the final period the net amount only"),
        prs("RADIATION.FINAL", "avco_radiation_allowance", "min(hr('radiation_net'), 950000)", radiation,
            cond="hr('radiation_net') > 0 and is_final_period"),
        prs("NO_RADIATION", "avco_radiation_allowance", "0", radiation, cond="hr('radiation_net') <= 0"),
        prs("ABSENCE", "avco_absence_deduction",
            f"round({base} * (hr('days_absent_unpaid') * (7 if employee('avco_work_pattern') == '6-1' else 8)"
            " + hr('days_absent_unpaid_sixth_day') * 5) / 173, 1, 'half_up')", absence,
            label="AVCO-24-3: base wage / 173 x regular hours of the day (7 or 8; 5 on the sixth day of the 6-1 "
                  "pattern, counted in hr('days_absent_unpaid_sixth_day'))"),
        prs("SAVINGS", "avco_savings_employer",
            "0 if (employer('avco_savings_plan_pension_fund') == True or hr('savings_employee_contribution') <= 0) else"
            " min(hr('savings_employee_contribution'), "
            + _band([(f"startswith({GRADE}, 'A')", "1500000"),
                     (f"startswith({GRADE}, 'B')", "1250000")], default="1000000") + ")", savings,
            label="AVCO-42-2: employer matches the employee contribution up to 1.5/1.25/1.0 million; income unless "
                  "the provider is a pension fund (case data)"),
        prs("OTHER_REGULAR", "other_regular_income",
            "income('other_regular') + avco_shift_allowance + avco_transport + avco_acting_supervisor"
            " + avco_radiation_allowance + avco_savings_employer - avco_absence_deduction",
            [shift, transport[0], acting, radiation, savings] + absence,
            label="regular income added by the agreement; the absconding deduction reduces gross income"),
        prs("IRREGULAR", "avco_irregular",
            f"({base} if hr('leave_allowance_paid') > 0 and hr('service_days') >= 90 else 0)"
            f" + ({base} if hr('travel_allowance_paid') > 0 else 0)"
            " + 2 * (500000 * hr('bereavement_adults') + 250000 * hr('bereavement_children'))"
            " + (4 * 500000 if hr('pilgrimage') > 0 else 0)"
            " + (min(hr('glasses_claim'), 1400000) if hr('glasses_claim') > 0 else min(hr('lens_claim'), 600000))"
            " + 500000 * hr('medivac_adult_days') + 250000 * hr('medivac_child_days')"
            " + min(hr('dental_claim'), 1000000 * hr('dental_visits')) + min(hr('special_needs_claim'), 2000000)"
            " + 2960000 * hr('edu_paud') + 5330000 * hr('edu_tk') + 10650000 * hr('edu_sd') + 12420000 * hr('edu_sltp')"
            " + 14190000 * hr('edu_slta') + 17750000 * (hr('edu_slb') + hr('edu_pt'))"
            " + (25000000 if hr('housing_grant_paid') > 0 else 0)"
            " + (" + _band([("employee('avco_living_status') == 'single_outside'", "7000000"),
                           ("employee('avco_living_status') == 'married_inside'", "8700000"),
                           ("employee('avco_living_status') == 'married_outside'", "10400000")])
            + " if hr('living_aid_paid') > 0 else 0)"
            " + (2000000 if hr('savings_one_time') > 0 and employer('avco_savings_plan_pension_fund') != True else 0)"
            " + round(hr('travel_allowance_unused') / 2, 1, 'half_up')",
            [leave, travel, perdiem, pilgrimage, glasses, lens, medivac] + dental
            + [edu, housing, living, savings_once, ta],
            label="AVCO-23-4 leave allowance (service >= 90 days), 26-1e travel allowance, 28-4 bereavement per diem, "
                  "30-6c pilgrimage, 32-2 glasses, 33-1d medivac, 34-8 dental and special needs, 36-1 education "
                  "(per child by level), 44-1a housing grant, 44-4 living aid, 42-4 one-time savings payment, LX-3d "
                  "unused travel allowance at most 50%"),
        prs("OTHER_IRREGULAR", "other_irregular_income", "income('other_irregular') + avco_irregular",
            [leave, travel], label="irregular income added by the agreement"),
        prs("TERMINATION_PAY", "avco_termination_pay",
            f"({base} if hr('separation_reason') in ('resign', 'absconding') else 0)"
            f" + (12 * ({base} + income('fixed_allowance')) if hr('separation_reason') == 'death' and"
            f" hr('service_days') >= 90 else (3 * ({base} + income('fixed_allowance')) if hr('separation_reason') =="
            f" 'death' else 0)) + (2 * {base} if hr('separation_reason') == 'death' else 0)", death,
            cond="hr('separation_paid') > 0",
            label="AVCO-55 separation pay 1 x base; 38-1 death benefit 1 year wage (3 months in probation); 39-3 "
                  "funeral aid 200% base"),
        prs("NO_TERMINATION_PAY", "avco_termination_pay", "0", death[3], cond="hr('separation_paid') <= 0"),
        prs("JKK_RATE", "jkk_rate", "dec('0.0174')", jkk, code="C6",
            label="AVCO-41-2: JKK 1.74% (highest risk group) fixed in the agreement"),
    ]


AVCO_NOTE = ("PKB PT Airfast Aviation Facilities 2024-2026. Not formalised: 23-7 (bonus formula outside the agreement; "
             "bonus input), 27-3 (ticket value depends on the route), 40-3 (USD benefit; currency outside the case "
             "model), 43-1 (DPLK contribution not stated), 52-2 (debt set-off), 41-4 (JKN restates the regulation), 41-2 employee JHT 2% (restates the regulation; an equal company rule has no effect and gate G5 rejects it), "
             "1-80, 1-84, 20-11 (definitions and payment dates). L2/21-6: only the legible grades of the wage scale "
             "images are tabulated; base wage stays a case input. 23-6 lunch in kind is excluded from income and needs "
             "no element.")

# ============================================================================================== TKG Taekwang
TKG = Doc("PKB-TAEKWANG-2024")


def _tkg():
    c = Clauses(TKG, "PKB_Taekwang_2024_2026.csv")
    validity = TKG.q("Keputusan pencatatan, Diktum KEDUA", "berlaku pada tanggal maret 2024 s.d 28 maret 2026")
    prs = _company("TKG", TKG.id, "2024-03-01", "2026-03-31", validity)
    wage = "tkg_wage"
    comp = [c.q("TKG-38-1"), c.q("TKG-2-27")]
    ot = [c.q("TKG-44-2", "standar upah lembur per jam adalah 1/173 kali upah"),
          c.q("TKG-44-3a", "jam kerja lembur pertama wajib dibayar upah sebesar 1,5 (satu koma lima) kali standar upah"
                           " lembur; 2) jam kerja lembur kedua dan ketiga wajib dibayar 2 (dua) kali standar upah"
                           " lembur"),
          c.q("TKG-44-3b", "untuk 6 (enam) hari kerja adalah sebagai berikut: 1) jam kesatu sampai dengan jam"
                           " ketujuh, yaitu 2 (dua) kali standar upah lembur; 2) jam kedelapan, yaitu 3 (tiga) kali"
                           " standar upah lembur; 3) jam kesembilan dan seterusnya, yaitu 4 (empat) kali"),
          c.q("TKG-44-3b", "untuk 5 (lima) hari kerja adalah sebagai berikut: 1) jam kesatu sampai dengan jam"
                           " kedelapan, yaitu 2 (dua) kali standar upah lembur; 2) jam kesembilan, yaitu 3 (tiga) kali"
                           " standar upah lembur; 3) jam kesepuluh dan seterusnya, yaitu 4 (empat) kali"),
          TKG.q("Pasal 44 ayat 3 huruf d", "komponen upah untuk perhitungan lembur adalah: 1) gaji pokok; 2) tunjangan"
                                           " tetap"),
          c.q("TKG-2-55")]
    thr = [c.q("TKG-53-1"),
           c.q("TKG-53-2", "masa kerja 3 (tiga) tahun sampai dengan kurang dari 4 (empat) tahun + 10% dari upah. b. masa"
                           " kerja 4 (empat) tahun sampai dengan kurang dari 5 (lima) tahun + 20% dari upah. c. masa"
                           " kerja 5 (lima) tahun ke atas + 30% dari upah"),
           c.q("TKG-53-3"), c.q("TKG-53-4")]
    prorata = [c.q("TKG-37-3"), c.q("TKG-37-9"), TKG.q("Pasal 37 ayat 4", "perhitungan mulai tanggal 1 sampai dengan"
                                                                          " tanggal terakhir bulan berjalan")]
    attendance = [c.q("TKG-41-4", "pekerja tidak hadir bekerja karena mangkir/alpa, maka tunjangan kehadiran tidak"
                                  " diberikan sebanyak 100% pada bulan tersebut. b. pekerja yang tidak hadir bekerja"
                                  " selain karena mengambil cuti tahunan, maka tunjangan kehadiran tidak diberikan pada"
                                  " hari yang ditinggalkan tersebut. c. pekerja datang terlambat sebanyak 3 (tiga) kali"
                                  " dalam waktu satu bulan di atas 5 (lima) menit"),
                  TKG.q("Pasal 41 ayat 4 huruf d-e", "pekerja yang datang terlambat tanpa izin 1 (satu) atau 2 (dua)"
                                                     " kali dalam sebulan maka tunjangan kehadiran tidak diberikan pada"
                                                     " hari tersebut. e. pekerja izin datang terlambat lebih dari 2"
                                                     " (dua) jam")]
    transport = c.q("TKG-42-4", "pekerja tidak hadir bekerja karena mangkir/alpa, maka tunjangan transportasi akan"
                                " hangus sebanyak 100% untuk bulan tersebut. b. pekerja yang tidak hadir bekerja selain"
                                " karena mengambil cuti tahunan, maka tunjangan transportasi tidak diberikan")
    shift = c.q("TKG-43")
    sick = c.q("TKG-28-1", "untuk 4 bulan pertama, dibayar 100% dari upah satu bulan. b. untuk 4 bulan kedua, dibayar"
                           " 75% dari upah satu bulan. c. untuk 4 bulan ketiga, dibayar 50% dari upah satu bulan. 2."
                           " untuk bulan selanjutnya dibayar 25%")
    detained = c.q("TKG-73-1", "untuk 1 orang tanggungan = 25% x upah satu bulan; b. untuk 2 orang tanggungan = 35% x"
                               " upah satu bulan; c. untuk 3 orang tanggungan = 45% upah satu bulan; d. untuk 4 orang"
                               " atau lebih tanggungan = 50% x upah satu bulan")
    grief = c.q("TKG-61", "kepada pekerja yang anggota keluarganya (suami/istri dan anak) meninggal dunia yang"
                          " besarannya adalah sebesar rp2.000.000,-")
    grief_heirs = c.q("TKG-61")
    factor = _factor([(12, "dec('0.25')"), (8, "dec('0.50')"), (4, "dec('0.75')"), (0, "1")], None,
                     (6, [(4, "dec('0.50')"), (3, "dec('0.45')"), (2, "dec('0.35')"), (1, "dec('0.25')")]))
    partial = "hr('calendar_days_worked') > 0 and hr('calendar_days_worked') < hr('calendar_days_in_month')"
    return [
        _fact("tkg_wage", "money", comp, "wage = base wage + fixed allowances", "upah tetap"),
        _fact("tkg_pay_factor", "exact", [sick, detained], "share of wage paid in long illness or detention",
              "persentase upah sakit atau ditahan"),
        _fact("tkg_prorated_wage", "money", prorata, "wage of a partial first or last month (calendar days)",
              "upah prorata"),
        _fact("tkg_attendance_allowance", "money", attendance, "attendance allowance after forfeits",
              "tunjangan kehadiran"),
        _fact("tkg_transport", "money", transport, "transport allowance", "tunjangan transportasi"),
        _fact("tkg_ot_workday", "money", ot, "overtime on working days", "lembur hari kerja"),
        _fact("tkg_ot_restday", "money", ot, "overtime on rest days and public holidays", "lembur hari libur"),
        _fact("tkg_death_aid_heirs", "money", grief_heirs, "condolence money to the heirs of a deceased employee "
              "(final tax with the termination; not gross income)", "sumbangan duka cita ahli waris"),
        prs("WAGE", wage, "income('base_salary') + income('fixed_allowance')", comp,
            label="TKG-38-1, 2-25, 2-27: fixed wage = base wage + fixed allowances"),
        prs("METHOD", "withholding_method", "'gross'", c.q("TKG-46"), scope="year",
            label="TKG-46: PPh 21 deducted from the wage"),
        prs("PAY_FACTOR", "tkg_pay_factor", factor, [sick, detained],
            label="TKG-28-1 illness 100/75/50/25%; 73-1 detention aid 25-50% for at most 6 months"),
        prs("BASE_SALARY", "base_salary", "round(income('base_salary') * tkg_pay_factor, 1, 'half_up')",
            [sick, detained], label="base wage paid this period"),
        prs("FIXED_ALLOWANCE", "fixed_allowance", "round(income('fixed_allowance') * tkg_pay_factor, 1, 'half_up')",
            [sick, detained], label="fixed allowances paid this period"),
        prs("PRORATED", "tkg_prorated_wage",
            f"round({wage} * hr('calendar_days_worked') / hr('calendar_days_in_month'), 1, 'half_up') if {partial}"
            f" else {wage}", prorata,
            label="TKG-37-3, 37-9: calendar days of the first or last month / days of the month (GT5 putusan 13)"),
        prs("THR", "thr",
            f"round({wage} * (1 + " + _band([("hr('service_years') >= 5", "dec('0.30')"),
                                           ("hr('service_years') >= 4", "dec('0.20')"),
                                           ("hr('service_years') >= 3", "dec('0.10')")]) + "), 1, 'half_up')"
            f" if hr('months_of_service') >= 12 else (round({wage} * hr('months_of_service') / 12, 1, 'half_up')"
            " if hr('months_of_service') > 1 else 0)", thr, cond="hr('thr_holiday') > 0",
            label="TKG-53-1..4: one month wage plus 10/20/30% at 3/4/5+ years; proportional above 1 month (exactly "
                  "1 month: none, C10 latent)"),
        prs("ATTENDANCE", "tkg_attendance_allowance",
            "0 if (hr('days_absconded') > 0 or hr('late_count') >= 3 or " + partial + ") else"
            " round(income('attendance_allowance') * max(0, hr('workdays_in_month') - hr('days_absent_other')"
            " - hr('late_count') - hr('late_over_2h_days')) / hr('workdays_in_month'), 1, 'half_up')"
            " if hr('workdays_in_month') > 0 else income('attendance_allowance')", attendance + prorata,
            label="TKG-41-4: forfeited for the month on absconding or 3 late arrivals, per day otherwise (daily value "
                  "= monthly amount / working days, GT5 putusan 13); not paid in a partial month"),
        prs("TRANSPORT", "tkg_transport",
            "0 if hr('days_absconded') > 0 else employer('transport_per_day') * hr('days_present')"
            " if employer('transport_per_day') != None else 0", transport,
            label="TKG-42-4: per day present (rate outside the agreement: employer data); forfeited for the month "
                  "on absconding"),
        prs("OT_WORKDAY", "tkg_ot_workday",
            f"round({wage} * (dec('1.5') * hr('ot_work_h1') + 2 * hr('ot_work_h2plus')) / (173 * 60), 1, 'half_up')"
            " if employee('tkg_all_in') != True else 0", ot,
            label="TKG-44-2, 44-3a: hour 1 1.5x, hours 2-3 2x, hour 4 2x by the regulation referred to (GT5 putusan "
                  "15); none for all-in positions (2-55)"),
        prs("OT_RESTDAY", "tkg_ot_restday",
            f"(round({wage} * (2 * (hr('ot_rest_h1_7') + hr('ot_rest_h8')) + 3 * hr('ot_rest_h9')"
            " + 4 * hr('ot_rest_h10plus')) / (173 * 60), 1, 'half_up') if employee('tkg_work_pattern') == '5' else"
            f" round({wage} * (2 * hr('ot_rest_h1_7') + 3 * hr('ot_rest_h8') + 4 * (hr('ot_rest_h9')"
            " + hr('ot_rest_h10plus'))) / (173 * 60), 1, 'half_up')) if employee('tkg_all_in') != True else 0", ot,
            label="TKG-44-3b: 6-day pattern 2x (1-7), 3x (8), 4x (9+); 5-day pattern 2x (1-8), 3x (9), 4x (10+)"),
        prs("OVERTIME", "overtime_pay", "tkg_ot_workday + tkg_ot_restday", ot, label="TKG-44: overtime pay"),
        prs("OTHER_REGULAR", "other_regular_income",
            f"income('other_regular') + tkg_attendance_allowance + tkg_transport - ({wage} - tkg_prorated_wage)"
            " + (employer('shift_allowance_per_day') * hr('shift_2_3_days') if employer('shift_allowance_per_day')"
            " != None else 0)", attendance + [transport, shift] + prorata,
            label="TKG-41, 42, 43 allowances; 37-3/37-9 proration as a deduction from the wage (contributions stay on "
                  "the full monthly wage as in GT5 TKG-03)"),
        prs("OTHER_IRREGULAR", "other_irregular_income", "income('other_irregular') + 2000000 * hr('family_deaths')",
            grief, label="TKG-61 ayat 2: condolence money 2,000,000 for a deceased spouse or child"),
        prs("DEATH_AID", "tkg_death_aid_heirs", "2500000 if hr('separation_reason') == 'death' else 0", grief_heirs,
            label="TKG-61 ayat 1: 2,500,000 to the heirs"),
    ]


TKG_NOTE = ("PKB PT TKG Taekwang Indonesia 2024-2026. Not formalised: 27-5 and 27-9 (hour limit and meal in kind, no "
            "value effect), 31-6 and 31-8 (no formula or daily wage), 40-5 (canteen in kind; Ramadan cash amount set by "
            "the company), 45-4 (scale outside the agreement), 76 and 81-3 (severance under PP 35/2021, final tax), "
            "13-3 (union dues per by-laws), 50-2 and 52-1 (follow the regulation), 37-4 and 44-3e (payment timing), "
            "74-2 (full wage). Allowance amounts of 41, 42, 43 are outside the agreement and come from case data.")

# ============================================================================================== Sansan
SANSAN = Doc("PKB-SANSAN-2021")


def _sansan():
    c = Clauses(SANSAN, "PKB_Sansan_2021_2024.csv")
    validity = SANSAN.q("Pasal masa berlaku ayat 1", "selama 3 (tiga) tahun sejak ditetapkan tanggal 23 september 2021 dan"
                                                     " berakhir tanggal 23 september 2024")
    prs = _company("SANSAN", SANSAN.id, "2021-09-01", "2024-09-30", validity)
    wage = "sansan_wage"
    thr = [c.q("SANSAN-41-1"),
           c.q("SANSAN-41-2", "bagi pekerja/buruh yang mempunyai masa kerja kurang dari 12 bulan (1 tahun) tetapi lebih"
                              " dari 1 bulan, maka thr diberikan secara proporsional yaitu : (masa kerja/12) x 1 bulan"
                              " upah"),
           c.q("SANSAN-41-4", "bagi pekerja/buruh yang mengundurkan diri atau terkena pemutusan hubungan kerja (phk) 30"
                              " (tiga puluh) hari sebelum tanggal pembayaran, maka perusahaan tetap memberikan tunjangan"
                              " hari raya")]
    premium = c.q("SANSAN-37-2", "besarnya premi hadir ditentukan maksimum 20% (dua puluh persen) dari upah pokok dan"
                                 " premi hadir. b. apabila pekerja/buruh tidak hadir selama 1 (satu) hari pada hari kerja"
                                 " perusahaan, maka premi hadir hilang sebesar 50% dan apabila tidak hadir selama 2 (dua)"
                                 " hari maka premi hadir hilang seluruhnya")
    premium2 = SANSAN.q("Pasal 37 ayat 2", "premi hadir diberikan kepada pekerja/buruh yang berhak atas perhitungan upah"
                                           " lembur")
    meal = [c.q("SANSAN-36-1"),
            SANSAN.q("Pasal 36 ayat 2", "kompensasi tunjangan makan kepada pekerja/buruh yang bekerja lembur lebih dari"
                                        " 4 jam dengan nilai tunjangan makan sama seperti tunjangan makan siang")]
    sick = c.q("SANSAN-34-2", "empat bulan pertama 100% x upah pokok sebulan b. empat bulan kedua 75% x upah pokok"
                              " sebulan c. empat bulan ketiga 50% x upah pokok sebulan d. bulan selanjutnya 25% x upah"
                              " pokok sebulan")
    detained = [c.q("SANSAN-82-2", "untuk 1 orang tanggungan : 25% x upah. b. untuk 2 orang tanggungan : 35% x upah. c."
                                   " untuk 3 orang tanggungan : 45% x upah. d. untuk 4 orang tanggungan atau lebih : 50%"
                                   " x upah"),
                SANSAN.q("Pasal 82 ayat 4", "wajib membayar upah pekerja/buruh sekurang-kurangnya 75% (tujuh puluh lima"
                                            " persen) dan berlaku paling lama 6 (enam) bulan takwim")]
    jkk = c.q("SANSAN-52-2a", "ketentuan iuran divisi garmen= 0,24% x upah sebulan ditanggung oleh perusahaan. -"
                              " ketentuan iuran divisi tekstil= 0,89% x upah sebulan")
    death = c.q("SANSAN-47-1")
    separation = c.q("SANSAN-L2", "masa kerja 3 (tiga) tahun atau lebih tetapi kurang dari 6 (enam) tahun 0.6 1,945,157"
                                  " masa kerja 6 (enam) tahun atau lebih tetapi kurang dari 9 (sembilan) tahun 0.8"
                                  " 2,593,543 masa kerja 9 (sembilan) tahun atau lebih tetapi kurang dari 12 (dua belas)"
                                  " tahun 1.1 3,566,122 masa kerja 12 (dua belas) tahun atau lebih tetapi kurang dari 15"
                                  " (lima belas) tahun 1.3 4,214,508 masa kerja 15 (lima belas) tahun atau lebih tetapi"
                                  " kurang dari 18 (delapan belas) tahun 1.6 5,192,086 masa kerja 18 (delapan belas) tahun"
                                  " atau lebih tetapi kurang dari 21 (dua puluh satu) tahun 1.8 5,835,472 masa kerja 21"
                                  " (dua puluh satu) tahun atau lebih tetapi kurang dari 24 (dua puluh empat) tahun 2.1"
                                  " 6,808,051 masa kerja 24 (dua puluh empat) tahun atau lebih 2.3")
    factor = _band([(f"hr('sick_month') > {m}", v) for m, v in
                    [(12, "dec('0.25')"), (8, "dec('0.50')"), (4, "dec('0.75')"), (0, "1")]]
                   + [("hr('detained_month') > 6", "0"),
                      ("hr('detained_month') > 0 and hr('detained_by_company_complaint') > 0", "dec('0.75')"),
                      ("hr('detained_month') > 0 and hr('dependents') >= 4", "dec('0.50')"),
                      ("hr('detained_month') > 0 and hr('dependents') >= 3", "dec('0.45')"),
                      ("hr('detained_month') > 0 and hr('dependents') >= 2", "dec('0.35')"),
                      ("hr('detained_month') > 0 and hr('dependents') >= 1", "dec('0.25')"),
                      ("hr('detained_month') > 0", "0")], default="1")
    return [
        _fact("sansan_wage", "money", c.q("SANSAN-31-3"), "wage = base wage + position allowance", "upah"),
        _fact("sansan_pay_factor", "exact", [sick] + detained, "share of wage paid in long illness or detention",
              "persentase upah sakit atau ditahan"),
        _fact("sansan_attendance_premium", "money", [premium], "attendance premium", "premi hadir"),
        _fact("sansan_separation_pay", "money", [separation, c.q("SANSAN-47-1")],
              "separation pay of operators and condolence money on death (final tax, PP 68/2009; not gross income)",
              "uang pisah operator dan sumbangan kedukaan"),
        prs("WAGE", wage, "income('base_salary') + income('fixed_allowance')", c.q("SANSAN-31-3"),
            label="SANSAN-31-3: wage = base wage + position allowance"),
        prs("METHOD", "withholding_method", "'gross'", [c.q("SANSAN-31-8"), c.q("SANSAN-1-14")], scope="year",
            label="SANSAN-31-8, 1-14: gross method"),
        prs("PAY_FACTOR", "sansan_pay_factor", factor, [sick] + detained,
            label="SANSAN-34-2 illness 100/75/50/25% of base wage; 82-2 detention aid 25-50%, at least 75% when "
                  "detained on the company's complaint, at most 6 months"),
        prs("BASE_SALARY", "base_salary", "round(income('base_salary') * sansan_pay_factor, 1, 'half_up')",
            [sick] + detained, label="base wage paid this period"),
        prs("THR", "thr",
            f"{wage} if hr('months_of_service') >= 12 else (round({wage} * hr('months_of_service') / 12, 1, 'half_up')"
            " if hr('months_of_service') > 1 else 0)", thr, cond="hr('thr_holiday') > 0",
            label="SANSAN-41-1, 41-2, 41-4: one month wage after 12 months, proportional above 1 month (exactly 1 "
                  "month: none, C10 latent); leaving within 30 days before payment keeps the right"),
        prs("ATTENDANCE_PREMIUM", "sansan_attendance_premium",
            "0 if (employee('sansan_overtime_eligible') == False or hr('days_absent') >= 2) else"
            " round(min(income('attendance_premium'), income('base_salary') * dec('0.20') / (1 - dec('0.20')))"
            " * (dec('0.50') if hr('days_absent') == 1 else 1), 1, 'half_up')", [premium, premium2],
            label="SANSAN-37-2: premium <= 20% of (base wage + premium), i.e. 25% of base wage (GT5 putusan 10); "
                  "-50% after one day absent, nothing after two; amount set by the company (input)"),
        prs("OTHER_REGULAR", "other_regular_income",
            "income('other_regular') + sansan_attendance_premium + (employer('meal_allowance_per_day')"
            " * (hr('days_present') + hr('ot_long_days')) if employer('meal_allowance_per_day') != None else 0)",
            [premium] + meal,
            label="SANSAN-36-1: meal allowance per day present and per overtime day over 4 hours (rate outside the "
                  "agreement: employer data)"),
        prs("JKK_RATE", "jkk_rate", "dec('0.0089') if employee('sansan_division') == 'textile' else dec('0.0024')",
            jkk, code="C6", label="SANSAN-52-2a: JKK 0.24% garment division, 0.89% textile division"),
        prs("SEPARATION_PAY", "sansan_separation_pay",
            "(round(employer('regional_minimum_wage') * " + _band([
                ("hr('service_years') >= 24", "dec('2.3')"), ("hr('service_years') >= 21", "dec('2.1')"),
                ("hr('service_years') >= 18", "dec('1.8')"), ("hr('service_years') >= 15", "dec('1.6')"),
                ("hr('service_years') >= 12", "dec('1.3')"), ("hr('service_years') >= 9", "dec('1.1')"),
                ("hr('service_years') >= 6", "dec('0.8')"), ("hr('service_years') >= 3", "dec('0.6')")])
            + ", 1, 'half_up') if hr('separation_reason') == 'resign' and employee('sansan_operator') != False"
            " else 0) + (income('base_salary') if hr('separation_reason') == 'death' else 0)",
            [separation, death], cond="hr('separation_paid') > 0",
            label="SANSAN-L2: separation pay of operators = city minimum wage x factor by service; 47-1 condolence "
                  "1 x base wage on death"),
        prs("NO_SEPARATION_PAY", "sansan_separation_pay", "0", death, cond="hr('separation_paid') <= 0"),
    ]


SANSAN_NOTE = ("PKB PT Sansan Saudaratex Jaya 2021-2024. Not formalised: 29-6 (daily wage not defined), 33-1 (overtime "
               "follows PP 35/2021 Ps 31; the multipliers are the regulation's, overtime stays a case input; ayat 2 "
               "unclear), 36-1 meal rate (outside the agreement), 51-2b (cooperative instalments), 52-2d (restates PP "
               "45/2015; not a conflict, GT5 putusan 11), 53-2 and 74-2 (full wage), 54-4 (no formula), 92-2 "
               "(severance under PP 35/2021, final tax), L1 (piece rates without cost per minute), 1-10 (same as the "
               "PTKP regulation), 31-5 (payment dates).")

# ============================================================================================== TPK Koja (development)
KOJA = Doc("PKB-KOJA-2012")


def _koja():
    c = Clauses(KOJA, "PKB_TPK_Koja_2012_2014.csv")
    validity = KOJA.q("Pasal 134 ayat (1)", "berlaku sejak tanggal 28 desember 2012 sampai dengan 28 desember 2014")
    prs = _company("KOJA", KOJA.id, "2012-12-01", "2014-12-31", validity)
    wage = "koja_basic_wage"
    leave = c.q("KOJA-50-2", "tunjangan cuti diberikan pekerja1,7 (satu koma tujuh) kali upah pokok")
    thr = c.q("KOJA-51-2", "tunjangan hari raya keagamaan (thr) diberikan sebesar 1,7 (satu koma tujuh) kali upah pokok")
    wage13 = c.q("KOJA-52-1", "upah bulan ke-13 adalah sebesar 1,7 (satu koma tujuh) kali upah, yang diberikan kepada"
                              " pekerja oleh perusahaan engan persyaratan masa kerja 1 tahun lebih")
    long_leave = c.q("KOJA-53", "maka diberikan kompensasi sebesar 1,7 (satu koma tujuh) kali upah pokok")
    bonus = [c.q("KOJA-55-2", "bagi pekerja dengan masa kerja 3 (tiga) bulan dan kurang dari 1 (satu) tahun besarnya"
                              " bonus dihitung secara proporsional"), c.q("KOJA-55-5", "pajak atas bonus ditanggung oleh"
                                                                                       " perusahaan")]
    detained = c.q("KOJA-58-1", "a.1 (satu) tanggungan : 25% dari upah pokok b.2 (satu) tanggungan : 35% dari upah"
                                " pokok c.3 (satu) tanggungan : 45% dari upah pokok d.4 (satu) tanggungan : 50% dari upah"
                                " pokok")
    jamsostek = c.q("KOJA-63-2", "jaminan kecelakaan kerja (jkk) : 1,27% dari upah pokok b.jaminan hari tua (jht) :"
                                 " 5,70% dari upah pokok c.jaminan kematian (jkm) : 0,30% dari upah pokok")
    dplk = c.q("KOJA-64-1", "a.iuran pensiun : 9% dari upah pokok b.iuran pekerja: 1,25% dari upah pokok")
    award = [c.q("KOJA-122-2f", "penghargaan masa kerja, dengan formula : masa kerja (dalam bulan) x 50 x upah pokok /"
                                " 360"),
             c.q("KOJA-122-2f", "santunan kematian dari perusahaan sebesar 10x (sepuluh) kali upah pokok"),
             c.q("KOJA-122-2f", "santunan kematian dari perusahaan sebesar 15x (limabelas) kali upah pokok")]
    factor = _band([("hr('detained_month') > 0 and hr('dependents') >= 4", "dec('0.50')"),
                    ("hr('detained_month') > 0 and hr('dependents') >= 3", "dec('0.45')"),
                    ("hr('detained_month') > 0 and hr('dependents') >= 2", "dec('0.35')"),
                    ("hr('detained_month') > 0 and hr('dependents') >= 1", "dec('0.25')"),
                    ("hr('detained_month') > 0", "0")], default="1")
    return [
        _fact("koja_basic_wage", "money", c.q("KOJA-38-1"), "basic wage = base salary + housing allowance",
              "upah pokok"),
        _fact("koja_pay_factor", "exact", detained, "share of wage paid as detention aid", "persentase bantuan ditahan"),
        _fact("koja_annual_payments", "money", [leave, wage13, long_leave],
              "leave allowance, 13th wage and long-leave compensation", "tunjangan cuti, upah ke-13, cuti besar"),
        _fact("koja_termination_pay", "money", award,
              "service award and death benefit on termination (final tax; not gross income)",
              "penghargaan masa kerja dan santunan kematian"),
        prs("WAGE", wage, "income('base_salary') + income('fixed_allowance')", c.q("KOJA-38-1"),
            label="KOJA-38-1: basic wage = base salary + housing allowance"),
        prs("METHOD", "withholding_method", "'gross_up'", [c.q("KOJA-61"), c.q("KOJA-38-2q", "p.bonus produksi q.tunjangan pajak"),
                                                         c.q("KOJA-39-2")],
            scope="year", label="KOJA-61, 38-2q, 39-2: tax allowance equal to the tax due (gross-up); base salary is "
                                "stated net"),
        prs("PAY_FACTOR", "koja_pay_factor", factor, detained,
            label="KOJA-58-1: detention aid 25-50% of basic wage (56 illness: 100% for 12 months, no change)"),
        prs("BASE_SALARY", "base_salary", "round(income('base_salary') * koja_pay_factor, 1, 'half_up')", detained,
            label="base salary paid this period"),
        prs("THR", "thr", f"round(dec('1.7') * {wage}, 1, 'half_up')", thr, cond="hr('thr_holiday') > 0",
            label="KOJA-51-2: THR 1.7 x basic wage"),
        prs("ANNUAL_PAYMENTS", "koja_annual_payments",
            f"(round(dec('1.7') * {wage}, 1, 'half_up') if hr('leave_pay_paid') > 0 else 0)"
            f" + (round(dec('1.7') * {wage}, 1, 'half_up') if hr('bonus_paid') > 0 and hr('months_of_service') > 12 else 0)"
            f" + (round(dec('1.7') * {wage}, 1, 'half_up') if hr('long_leave_paid') > 0 else 0)",
            [leave, wage13, long_leave],
            label="KOJA-50-2 leave allowance, 52-1 13th wage after more than 1 year, 53 long-leave compensation: "
                  "each 1.7 x basic wage"),
        prs("BONUS", "bonus",
            "round(income('bonus') * hr('months_of_service') / 12, 1, 'half_up') if hr('months_of_service') >= 3 and"
            " hr('months_of_service') < 12 else (income('bonus') if hr('months_of_service') >= 12 else 0)", bonus,
            label="KOJA-55-2: share of the bonus pool (input) proportional months/12 for 3 to 11 months of service; "
                  "55-5 tax borne by the company (gross-up method)"),
        prs("OTHER_IRREGULAR", "other_irregular_income", "income('other_irregular') + koja_annual_payments",
            [leave, wage13], label="irregular income added by the agreement"),
        prs("JKK_PREMIUM", "jkk_premium", f"round(dec('0.0127') * {wage}, 1, param('bpjs_round_mode'))", jamsostek,
            label="KOJA-63-2: Jamsostek JKK 1.27% of basic wage paid by the employer (income)"),
        prs("JKM_PREMIUM", "jkm_premium", f"round(dec('0.0030') * {wage}, 1, param('bpjs_round_mode'))", jamsostek,
            label="KOJA-63-2: Jamsostek JKM 0.30% of basic wage paid by the employer (income)"),
        prs("DPLK_EMPLOYEE", "jp_employee", f"round(dec('0.0125') * {wage}, 1, param('bpjs_round_mode'))", dplk,
            label="KOJA-64-1: employee DPLK contribution 1.25% (a pension contribution, deductible); the employer's "
                  "9% is not income"),
        prs("TERMINATION_PAY", "koja_termination_pay",
            f"round(hr('months_of_service') * 50 * {wage} / 360, 1, 'half_up') + (10 * {wage} if hr('separation_reason')"
            f" == 'death' else (15 * {wage} if hr('separation_reason') == 'death_work_accident' else 0))", award,
            cond="hr('separation_paid') > 0",
            label="KOJA-122-2f: service award months x 50 x basic wage / 360; death benefit 10x (illness) or 15x "
                  "(work accident)"),
        prs("NO_TERMINATION_PAY", "koja_termination_pay", "0", award[0], cond="hr('separation_paid') <= 0"),
    ]


KOJA_NOTE = ("PKB KSO TPK Koja 2012-2014 (development). Not formalised: 43-3 (incentive formula in a management decree), "
             "46-2 (meals in kind; not income of the employee before 2023), 47-7 (overtime base = basic wage, "
             "multipliers from the regulation; overtime stays a case input), 54-2 (rate in a decree), 55-4 (pool "
             "formula; the individual share is an input), 56 and 59-1 (full wage), 63-2 JHT split (not stated), 68-3 "
             "(premium not stated).")

UPDATES = []
SIDE_UPDATES = [
    Update("GOLD-PKB-WIKA", WIKA, "policy", add=_wika(), note=WIKA_NOTE),
    Update("GOLD-PKB-CENTEX", CENTEX, "policy", add=_centex(), note=CENTEX_NOTE),
    Update("GOLD-PKB-AVCO", AVCO, "policy", add=_avco(), note=AVCO_NOTE),
    Update("GOLD-PKB-TKG", TKG, "policy", add=_tkg(), note=TKG_NOTE),
    Update("GOLD-PKB-SANSAN", SANSAN, "policy", add=_sansan(), note=SANSAN_NOTE),
    Update("GOLD-PKB-KOJA", KOJA, "policy", add=_koja(), note=KOJA_NOTE),
]
