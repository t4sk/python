import math

def floor(x, d):
    base = 10 ** d
    return math.floor(x / base) * base

# 青色申告控除
BLUE_FORM_DEDUCTION = 650000

# 国民健康保険 基礎控除
NATIONAL_HEALTH_INSURANCE_BASE_DEDUCTION = 330000
NURSING_CARE_FEE_MIN_AGE = 40

# 基礎控除
INCOME_TAX_BASE_DEDUCTION = 480000

# 住民税
RESIDENT_TAX_BASE_DEDUCTION = 430000
RESIDENT_TAX_RATE = 0.1
# 均等割額
RESIDENT_TAX_PER_PERSON_FEE = 5000

class HealthInsuranceTax:
    def __init__(self, **kwargs):
        # 医療 | 後期高齢者支援 | 介護
        self.rate = kwargs["rate"]
        # 均等割額
        self.per_person_fee = kwargs["per_person_fee"]
        # 平等割額
        self.flat_fee = kwargs["flat_fee"]

    def __str__(self):
        return f'医療 | 後期高齢者支援 | 介護: {self.rate:,f} 均等割額: {self.per_person_fee:,d} 平等割額: {self.flat_fee:,d}'

class IncomeBracket:
    def __init__(self, **kwargs):
        self.max = kwargs["max"]
        self.rate = kwargs["rate"]
        self.deduction = kwargs["deduction"]

    def __str__(self):
        return f'max {self.max:,f} rate {self.rate:,f} deduction {self.deduction:,f}'

INCOME_BRACKETS = [
    IncomeBracket(
        max=1950000,
        rate=0.05,
        deduction=0,
    ),
    IncomeBracket(
        max=3300000,
        rate=0.1,
        deduction=97500,
    ),
    IncomeBracket(
        max=6950000,
        rate=0.2,
        deduction=427500,
    ),
    IncomeBracket(
        max=9000000,
        rate=0.23,
        deduction=636000,
    ),
    IncomeBracket(
        max=18000000,
        rate=0.33,
        deduction=1536000,
    ),
    IncomeBracket(
        max=40000000,
        rate=0.40,
        deduction=2796000,
    ),
    IncomeBracket(
        max=math.inf,
        rate=0.45,
        deduction=4796000,
    ),
]

# 国民健康保険
def get_national_health_insurance_fee(
    pre_tax_income, age, medical, elderly_aid, nursing_care, subscribers
):
    taxable_income = (
        pre_tax_income
        - BLUE_FORM_DEDUCTION
        - NATIONAL_HEALTH_INSURANCE_BASE_DEDUCTION
    )

    num_subscribers = len(subscribers)
    num_nursing_care_subcribers = 0

    for age in subscribers:
        if age >= NURSING_CARE_FEE_MIN_AGE:
            num_nursing_care_subcribers += 1

    # 医療
    medical_fee = (
        taxable_income * medical.rate
        + medical.per_person_fee * num_subscribers
        + medical.flat_fee
    )
    # 後期高齢者支援
    elderly_aid_fee = (
        taxable_income * elderly_aid.rate
        + elderly_aid.per_person_fee * num_subscribers
        + elderly_aid.flat_fee
    )
    # 介護
    nursing_care_fee = 0
    if age >= NURSING_CARE_FEE_MIN_AGE:
        nursing_care_fee += taxable_income * nursing_care.rate
    nursing_care_fee += (
        nursing_care.per_person_fee * num_nursing_care_subcribers
        + nursing_care.flat_fee
    )

    return medical_fee + elderly_aid_fee + nursing_care_fee

# 所得税
def get_income_bracket(taxable_income):
    for income_bracket in INCOME_BRACKETS:
        if taxable_income < income_bracket.max:
            return income_bracket

    return INCOME_BRACKETS[6]

def get_income_tax(
    pre_tax_income,
    # 配偶者控除
    spouse_deduction,
    # 扶養控除
    dependents_deduction,
    # 生命保険料控除
    life_insurance_deduction,
    pension_fee,
    national_health_insurance_fee
):
    deductions = (
        INCOME_TAX_BASE_DEDUCTION
        + spouse_deduction
        + dependents_deduction
        + life_insurance_deduction
        + pension_fee
        + national_health_insurance_fee
    )

    # floor 1000
    taxable_income = floor(pre_tax_income - BLUE_FORM_DEDUCTION - deductions, 3)

    income_bracket = get_income_bracket(taxable_income)
    # floor 100
    return floor(
        taxable_income * income_bracket.rate - income_bracket.deduction,
        2,
    )

# 住民税
def get_resident_tax(
    pre_tax_income,
    # 配偶者控除
    spouse_deduction,
    # 扶養控除
    dependents_deduction,
    # 生命保険料控除
    life_insurance_deduction,
    pension_fee,
    national_health_insurance_fee,
):
    deductions = (
        RESIDENT_TAX_BASE_DEDUCTION
        + spouse_deduction
        + dependents_deduction
        + life_insurance_deduction
        + pension_fee
        + national_health_insurance_fee
    )

    taxable_income = floor(pre_tax_income - BLUE_FORM_DEDUCTION - deductions, 3)

    return taxable_income * RESIDENT_TAX_RATE + RESIDENT_TAX_PER_PERSON_FEE

### main ###
def main(**kwargs):
    pre_tax_income = kwargs["income"]
    age = kwargs["age"]
    medical = kwargs["medical"]
    elderly_aid = kwargs["elderly_aid"]
    nursing_care = kwargs["nursing_care"]
    self_employed = kwargs["self_employed"]

    ### 国民年金 ###
    pension_fee = 0
    if self_employed:
        pension_fee = 16540 * 12

    ### 国民健康保険 ###
    # 医療
    _medical = HealthInsuranceTax(
        rate = medical["rate"],
        per_person_fee = medical["per_person_fee"],
        flat_fee = medical["flat_fee"]
    )
    # 後期高齢者支援分
    _elderly_aid = HealthInsuranceTax(
        rate = elderly_aid["rate"],
        per_person_fee = elderly_aid["per_person_fee"],
        flat_fee = elderly_aid["flat_fee"]
    )
    # 介護分
    _nursing_care = HealthInsuranceTax(
        rate = nursing_care["rate"],
        per_person_fee = nursing_care["per_person_fee"],
        flat_fee = nursing_care["flat_fee"]
    )

    # 国民健康保険の加入者
    subscribers = [age]

    national_health_insurance_fee = 0
    if self_employed:
        national_health_insurance_fee = get_national_health_insurance_fee(
            pre_tax_income,
            age,
            _medical,
            _elderly_aid,
            _nursing_care,
            subscribers
        )

    ### 所得税 ###
    # 配偶者控除
    spouse_deduction = 0
    # 扶養控除
    dependents_deduction = 0
    # 生命保険料控除
    life_insurance_deduction = 0

    # NOTE should pass previous year's expenses (pension, national health)
    income_tax = get_income_tax(
        pre_tax_income,
        spouse_deduction,
        dependents_deduction,
        life_insurance_deduction,
        pension_fee,
        national_health_insurance_fee,
    )

    ### 住民税 ###
    # NOTE should pass previous year's expenses (pension, national health)
    resident_tax = get_resident_tax(
        pre_tax_income,
        spouse_deduction,
        dependents_deduction,
        life_insurance_deduction,
        pension_fee,
        national_health_insurance_fee,
    )

    ### 個人事業税 ###
    # 0 for programmers
    # business_tax = (pre_tax_income - 2900000) * 0.05
    business_tax = 0

    after_tax_income = (
        pre_tax_income
        - resident_tax
        - national_health_insurance_fee
        - pension_fee
        - income_tax
        - business_tax
    )
    total_tax = pre_tax_income - after_tax_income

    print(f'収入: {pre_tax_income:,d}')
    print(f'国民健康保険: {national_health_insurance_fee:,.0f}')
    print(f'国民年金: {pension_fee:,d}')
    print(f'住民税: {resident_tax:,.0f}')
    print(f'所得税: {income_tax:,.0f}')
    print(f'個人事業税: {business_tax:,.0f}')
    print(f'税: {total_tax:,.0f}')
    print(f'手取り収入: {after_tax_income:,.0f}')
    print(f'税 / 収入: {(total_tax / pre_tax_income) * 100:,.3f} %')

