# Kosakata KB emas

Dihasilkan oleh `system/tools/build_gold.py`. Fakta bertanda keluaran membentuk $F_\mathit{nilai}$ (dibekukan, representasi.md bagian 4).

| Fakta | Tipe | Lingkup | Keluaran | Label | Label Indonesia |
|---|---|---|---|---|---|
| `base_salary` | money | period | ya | base salary | gaji pokok |
| `bonus` | money | period | ya | bonus | bonus |
| `gross_income` | money | period | ya | gross income of the period | penghasilan bruto |
| `health_premium_employer` | money | period | ya | health premium paid by employer | iuran jaminan kesehatan pemberi kerja |
| `jht_employee` | money | period | ya | old-age savings contribution paid by employee | iuran jaminan hari tua pegawai |
| `jkk_premium` | money | period | ya | work accident premium paid by employer | iuran jaminan kecelakaan kerja |
| `jkm_premium` | money | period | ya | death benefit premium paid by employer | iuran jaminan kematian |
| `jp_employee` | money | period | ya | pension contribution paid by employee | iuran jaminan pensiun pegawai |
| `overtime_pay` | money | period | ya | overtime pay | upah lembur |
| `pph21_dtp` | money | period | ya | PPh 21 borne by the government | PPh Pasal 21 ditanggung pemerintah |
| `pph21_due` | money | period | ya | PPh 21 due for the period | PPh Pasal 21 terutang |
| `take_home_pay` | money | period | ya | take-home pay | gaji bersih |
| `tax_allowance` | money | period | ya | tax allowance or tax borne by the employer | tunjangan pajak |
| `thr` | money | period | ya | religious holiday allowance (THR) | tunjangan hari raya |
| `annual_deductions` | money | year | ya | deductions of the tax year | pengurang setahun |
| `annual_gross` | money | year | ya | gross income of the tax year | penghasilan bruto setahun |
| `annual_net` | money | year | ya | net income of the tax year | penghasilan neto setahun |
| `annual_pph21` | money | year | ya | PPh 21 of the tax year | PPh Pasal 21 setahun |
| `job_expense` | money | year | ya | job expense of the tax year | biaya jabatan |
| `ptkp_amount` | money | year | ya | non-taxable income (PTKP) | penghasilan tidak kena pajak |
| `refund_to_employee` | money | year | ya | over-withholding refunded to the employee | kelebihan potong dikembalikan |
| `taxable_income` | money | year | ya | taxable income (PKP) | penghasilan kena pajak |
| `benefit_gift_other` | money | period |  | non-holiday gifts received this period | bingkisan selain hari raya |
| `benefit_housing_taxable` | money | period |  | taxable part of individual housing | natura rumah yang menjadi objek pajak |
| `benefit_sports` | money | period |  | sports facility received this period | fasilitas olahraga |
| `benefits_taxable_irregular` | money | period |  | taxable benefits in kind, irregular | natura tidak teratur |
| `benefits_taxable_regular` | money | period |  | taxable benefits in kind, regular | natura teratur |
| `bpjs_wage` | money | period |  | monthly wage for social security contributions | upah sebulan iuran |
| `cash_income` | money | period |  | cash income of the period | penghasilan tunai |
| `company_deductions` | money | period |  | deductions by the employer | potongan perusahaan |
| `covid_dtp_eligible` | bool | period |  | employee eligible for COVID DTP | pegawai penerima PPh 21 DTP |
| `covid_dtp_fixed_income` | money | period |  | fixed regular income for the COVID DTP criterion | penghasilan bruto tetap dan teratur |
| `dtp_facility` | bool | period |  | DTP facility applies in this period | masa pajak insentif |
| `dtp_fixed_income` | money | period |  | fixed regular income for the DTP criterion | penghasilan bruto tetap dan teratur |
| `employee_pension_contributions` | money | period |  | employee pension and old-age contributions | iuran pensiun pegawai |
| `employee_tax_burden` | money | period |  | PPh 21 borne by the employee | PPh Pasal 21 yang ditanggung pegawai |
| `employer_premiums_taxable` | money | period |  | employer premiums that are income | premi yang dibayar pemberi kerja |
| `fixed_allowance` | money | period |  | fixed allowances | tunjangan tetap |
| `health_employee` | money | period |  | health contribution paid by employee | iuran jaminan kesehatan pegawai |
| `health_wage` | money | period |  | wage base for health insurance | dasar upah iuran jaminan kesehatan |
| `irregular_gross` | money | period |  | irregular gross income | penghasilan bruto tidak teratur |
| `jkk_rate` | rate | period |  | work accident premium rate | tarif iuran JKK |
| `job_expense_month` | money | period |  | job expense of the month (annualised method) | biaya jabatan sebulan |
| `jp_wage` | money | period |  | wage base for pension contribution | batas upah jaminan pensiun |
| `net_regular_month` | money | period |  | net regular income of the month | penghasilan neto sebulan |
| `other_irregular_income` | money | period |  | other irregular income | penghasilan tidak teratur lain |
| `other_regular_income` | money | period |  | other regular income | penghasilan teratur lain |
| `pph21_running` | money | period |  | PPh 21 of a period other than the final one | PPh Pasal 21 masa |
| `pph_irregular_month` | money | period |  | tax on irregular income of the month | PPh atas penghasilan tidak teratur |
| `pph_regular_annual` | money | period |  | annual tax on annualised regular income | PPh setahun atas penghasilan teratur |
| `pph_regular_month` | money | period |  | monthly tax on regular income | PPh sebulan atas penghasilan teratur |
| `regular_gross` | money | period |  | regular gross income | penghasilan bruto teratur |
| `taxable_regular_annualized` | money | period |  | annualised taxable regular income | penghasilan kena pajak disetahunkan |
| `taxable_with_irregular` | money | period |  | annualised taxable income including irregular income | penghasilan kena pajak termasuk tidak teratur |
| `taxable_without_irregular` | money | period |  | annualised taxable income without irregular income | penghasilan kena pajak tanpa tidak teratur |
| `ter_rate` | rate | period |  | monthly effective rate | tarif efektif bulanan |
| `thr_minimum` | money | period |  | minimum religious holiday allowance | THR keagamaan minimum |
| `zakat_deductible` | money | period |  | zakat deductible in withholding | zakat pengurang |
| `zakat_withheld` | money | period |  | zakat paid through the employer | zakat melalui pemberi kerja |
| `annual_pension_contributions` | money | year |  | employee pension contributions of the year | iuran pensiun setahun |
| `annual_zakat_deduction` | money | year |  | zakat deducted in the year | zakat setahun |
| `annualization_factor` | int | year |  | months used to annualise | faktor pengali disetahunkan |
| `dtp_eligible` | bool | year |  | employee eligible for DTP | pegawai tetap tertentu penerima insentif |
| `dtp_eligible_tourism` | bool | year |  | employee eligible for tourism DTP | pegawai tertentu sektor pariwisata |
| `dtp_income_test` | money | year |  | fixed regular income in January or the first month | penghasilan tetap bulan pertama |
| `final_period_tax` | money | year |  | PPh 21 of the final period | PPh Pasal 21 masa pajak terakhir |
| `ptkp_status_effective` | category | year |  | PTKP status used | status PTKP yang dipakai |
| `ptkp_status_input` | category | year |  | PTKP status at the start of the year | status PTKP |
| `subjective_months` | int | year |  | months of subjective tax obligation | bulan kewajiban subjektif |
| `ter_category` | category | year |  | TER category | kategori tarif efektif bulanan |
| `withheld_before_final` | money | year |  | PPh 21 withheld before the final period | PPh Pasal 21 yang telah dipotong |
| `withholding_method` | category | year |  | withholding method | metode pemotongan |
