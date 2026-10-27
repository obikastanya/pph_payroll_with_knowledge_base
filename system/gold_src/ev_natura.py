"""Gold Delta of E02, PMK 66/2023: benefits in kind become subject to PPh 21 withholding from Masa Juli 2023
(classification change T3; tafsir K12, K4; tafsir_korpus B4).

Benefits of January-June 2023 are not withheld (Pasal 23 ayat (4)) and stay out of the December recalculation: the
default rule (zero) keeps applying to those periods because the new rules are valid from 2023-07-01. Monthly
housing and meal coupons are regular income; gifts are irregular (K12). Excluded kinds are simply not added to the
taxable benefits (an earlier version recorded them in a fact no output reads; gate G5 rejects such a vacuous rule).
"""
from . import Doc, Update, fact, param, rule

D = Doc("PMK-66-2023")
VF = "2023-07-01"
UPPER = "1000000000000"


def _dated(elements, *quotes):
    """Every element with a validity also cites the provision that sets its period (gate G2 grounds dates per
    element)."""
    for e in elements:
        if e.get("valid_from") or e.get("valid_until"):
            e["source"] = list(e["source"]) + [q for q in quotes if q not in e["source"]]
    return elements


def _delta():
    q = D.q
    obj = q("Pasal 23 ayat (1)", "dalam bentuk natura dan/atau kenikmatan wajib")
    start = q("Pasal 27", "Peraturan Menteri ini mulai berlaku pada tanggal 1 Juli 2023.")
    excl_h1 = q("Pasal 23 ayat (4)", "Januari 2023 sampai dengan Masa Pajak Juni 2023")
    housing = [q("Lampiran A angka 7", "perseorangan (individual) antara"), q("Lampiran A angka 7", "Rp2.000.000,00 (dua juta")]
    coupon = [q("Pasal 5 ayat (4) huruf a", "a. Rp2.000.000,00 (dua juta rupiah) untuk tiap Pegawai"),
              q("Pasal 5 ayat (1) huruf b", "kupon makanan dan/atau minuman bagi Pegawai")]
    gift = [q("Lampiran A angka 2", "yang diberikan selain dalam"), q("Lampiran A angka 2", "Rp3.000.000,00 (tiga juta")]
    sports = [q("Lampiran A angka 5", "Fasilitas olahraga dari pemberi"), q("Lampiran A angka 5", "Rpl.500.000,00 (satu juta")]
    vehicle = [q("Lampiran A angka 8", "Fasilitas kendaraan dari pemberi"),
               q("Lampiran A angka 8", "modal pada pemberi kerja;"), q("Lampiran A angka 8", "Rpl00.000.000,00 (seratus")]
    excluded = [q("Lampiran A angka 1", "Bingkisan dart pemberi kerja diterima atau diperoleh seluruh"),
                q("Lampiran A angka 3", "Peralatan dan fasilitas kerja dart a. diterima atau diperoleh"),
                q("Lampiran A angka 6", "Fasilitas tempat tinggal dari diterima atau diperoleh Pegawai."),
                q("Pasal 5 ayat (1) huruf a", "a. makanan dan/atau minuman yang disediakan oleh")]
    vehicle_taxable = ("(benefit('company_vehicle') if (employee('has_equity_in_employer') == True or "
                       "(employee('avg_monthly_gross_12m') if employee('avg_monthly_gross_12m') != None else "
                       "base_salary + fixed_allowance) > param('natura_vehicle_gross_cap')) else 0)")
    return _dated([
        fact("benefit_gift_other", "money", "period", obj, label="non-holiday gifts received this period",
             label_id="bingkisan selain hari raya"),
        fact("benefit_sports", "money", "period", obj, label="sports facility received this period",
             label_id="fasilitas olahraga"),
        param("PAR.NATURA_HOUSING_CAP.2023", "natura_housing_individual_cap", 2000000, "money", housing, VF,
              label_id="batas fasilitas tempat tinggal individual"),
        param("PAR.NATURA_COUPON_CAP.2023", "natura_meal_coupon_cap", 2000000, "money", coupon, VF,
              label_id="batas kupon makanan"),
        param("PAR.NATURA_GIFT_CAP.2023", "natura_gift_other_cap", 3000000, "money", gift, VF,
              label_id="batas bingkisan selain hari raya"),
        param("PAR.NATURA_SPORTS_CAP.2023", "natura_sports_cap", 1500000, "money", sports, VF,
              label_id="batas fasilitas olahraga"),
        param("PAR.NATURA_VEHICLE_GROSS_CAP.2023", "natura_vehicle_gross_cap", 100000000, "money", vehicle, VF,
              label_id="batas penghasilan bruto fasilitas kendaraan"),
        rule("REG.NATURA.GIFT_VALUE", "benefit_gift_other", "benefit('gift_other')", gift, VF),
        rule("REG.NATURA.SPORTS_VALUE", "benefit_sports", "benefit('sports_facility')", sports, VF),
        rule("REG.NATURA.REGULAR", "benefits_taxable_regular",
             "max(0, benefit('housing_individual') - param('natura_housing_individual_cap'))"
             " + max(0, benefit('meal_coupon_field_duty') - param('natura_meal_coupon_cap'))"
             f" + {vehicle_taxable} + benefit('other_benefit')",
             [obj, start] + housing + coupon + vehicle, VF, label="tafsir K12: monthly benefits are regular income"),
        rule("REG.NATURA.IRREGULAR", "benefits_taxable_irregular",
             "max(0, cumulative('benefit_gift_other') - param('natura_gift_other_cap'))"
             " - max(0, cumulative_before('benefit_gift_other') - param('natura_gift_other_cap'))"
             " + max(0, cumulative('benefit_sports') - param('natura_sports_cap'))"
             " - max(0, cumulative_before('benefit_sports') - param('natura_sports_cap'))",
             [obj, start, excl_h1] + gift + sports, VF,
             label="tafsir K12: annual caps applied cumulatively; gifts are irregular income"),
        rule("REG.BORNE.GROSSUP.RUNNING", "tax_allowance", "pph21_running", obj, VF,
             cond="withholding_method == 'employer_borne' and not is_final_period", fixed_point=("0", UPPER),
             label="tafsir K4: tax borne by the employer is a benefit withheld from July 2023, full gross-up"),
        rule("REG.BORNE.GROSSUP.FINAL", "tax_allowance", "max(0, final_period_tax)", obj, VF,
             cond="withholding_method == 'employer_borne' and is_final_period", fixed_point=("0", UPPER),
             label="tafsir K4 and K3 item 2"),
    ], start)


UPDATES = [Update("GOLD-E02", D, "event", event_id="E02", add=_delta())]
