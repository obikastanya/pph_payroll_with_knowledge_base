"""Background update of the supporting labour regulations that company policies are checked against (conflict C10).

Permenaker 6/2016 sets the minimum religious holiday allowance (THR): one month of wages after 12 months of
continuous service, proportional from one month (Pasal 2 ayat (1), Pasal 3 ayat (1)-(2)), and keeps the right for a
permanent employee whose employment ends within 30 days before the holiday (Pasal 7 ayat (1)). It is a constraint on
the THR a company pays, not a PPh 21 rule, so it does not change any PPh 21 value: without HR data in the case the
constraint is not evaluated.

HR data read from the case (hr bucket of a period):
  thr_holiday                     1 in the period in which THR for a religious holiday is payable to the employee
  months_of_service               completed months of continuous service at the holiday
  days_terminated_before_holiday  days between the end of employment and the holiday (0 if still employed)
Wages for THR are base salary and fixed allowances (Pasal 3 ayat (2) huruf b). The regulation does not state rounding;
fractions of a rupiah are dropped.
"""
from . import Doc, Update, constraint, fact, rule

PMN6 = Doc("PERMENAKER-6-2016")
VF = "2016-04-01"   # promulgated 8 March 2016 and in force on that date; first full month


def _thr():
    q = PMN6.q
    entitled = q("Pasal 2 ayat (1)", "Pekerja/Buruh yang telah mempunyai masa kerja 1 (satu) bulan secara terus menerus atau lebih.")
    full = q("Pasal 3 ayat (1) huruf a", "12 (dua belas) bulan secara terus menerus atau lebih, diberikan sebesar 1 (satu) bulan upah;")
    prop = [q("Pasal 3 ayat (1) huruf b", "dari 12 (dua belas) bulan, diberikan secara proporsional sesuai masa kerja dengan"),
            q("Pasal 3 ayat (1) huruf b", "masa kerja x 1 (satu)bulan upah.")]
    wage = q("Pasal 3 ayat (2) huruf b", "b. upah pokoktermasuk tunjangan tetap.")
    leaver = q("Pasal 7 ayat (1)", "pemutusan hubungan kerja terhitung sejak 30 (tiga puluh) hari sebelum Hari Raya Keagamaan, berhak")
    return [
        fact("thr_minimum", "money", "period", [entitled, full] + prop, label="minimum religious holiday allowance",
             label_id="THR keagamaan minimum"),
        rule("REG.THR.MINIMUM", "thr_minimum",
             "(round((base_salary + fixed_allowance) * min(hr('months_of_service'), 12) / 12, 1, 'down')"
             " if hr('months_of_service') >= 1 and hr('days_terminated_before_holiday') <= 30 else 0)"
             " if hr('thr_holiday') == 1 else 0",
             [entitled, full] + prop + [wage, leaver], VF,
             label="THR minimum; employees whose employment ended within 30 days before the holiday keep the right"),
        constraint("CON.THR.MINIMUM", "thr >= thr_minimum", "C10", [entitled, full, leaver], VF,
                   cond="hr('thr_holiday') == 1", label="THR paid is not below the minimum"),
    ]


UPDATES = [Update("BG-010", PMN6, "background", add=_thr(),
                  note="Supporting labour regulation for company policies (C10). No PPh 21 rule changes.")]
