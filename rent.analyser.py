
import numpy_financial as npf

# change static variables as needed (all per annum)
INSURANCE_RATE = 0.05 # dependent on rebuild cost
MAINTENANCE_RATE = 0.01
MANAGEMENT_RATE =  0.08
VACANCY_RATE = 0.07
EXPECTED_APPRECIATION = 0.03
INFLATION_RATE = 0.037
SALES_COMMISSION = 0.06

# inputs: price, downpayment, interest_rate, loan_term, rent
def rent_analyser():
    '''Using purchase price, loans, rent income and interest fees, calculates the 
    discounted cash flow per month adjusted for inflation, internal rate of return 
    and net sale proceeds over x years of investment'''

    price  = float(input("Enter property price: $"))
    downpayment = float(input("Enter upfront payment: $"))
    interest_rate = float(input("Enter annual interest rate in decimal: "))
    loan_term = int(input("Enter years to repay: "))
    years_to_hold = int(input("Enter years to hold property: "))
    tenants = int(input("Enter number of tenants (planned or existing): "))
    rent = float(input("Enter rent per tenant per month: $"))

    # base calculations
    loan = price - downpayment
    monthly_interest = interest_rate/12
    n_payments = loan_term * 12
    # calculate monthly mortgage repayments
    monthly_mortgage = -npf.pmt(monthly_interest, n_payments, loan)

    # rental income
    rental_income = tenants * rent * (1 - VACANCY_RATE)

    # operation costs
    monthly_property_tax = calculate_property_tax(price)/12
    monthly_insurance = (INSURANCE_RATE*price)/12
    monthly_maintenance = (MAINTENANCE_RATE*price)/12
    monthly_management = MANAGEMENT_RATE*rental_income
   
    # expected operating profit per month BEFORE mortgage
    operating_profit = rental_income - monthly_insurance - monthly_property_tax - monthly_maintenance - monthly_management

    # DCF for rental income
    cash_flows = [-downpayment,]
    for month in range(1, years_to_hold*12 + 1):
        # Future value of rent at this month (rent grows with appreciation)
        future_value_rent = npf.fv(
            rate=EXPECTED_APPRECIATION/12,
            nper=month,
            pmt=0,
            pv=-operating_profit
        )
        # Discount that future rent back to today's dollars (adjust for inflation)
        discounted_cash_flow = npf.pv(
            rate=INFLATION_RATE/12,
            nper=month,
            pmt=0,
            fv=-future_value_rent
        )
        cash_flows.append(discounted_cash_flow - monthly_mortgage)

    # selling price
    sale_price = price * ((1+EXPECTED_APPRECIATION)/(1+INFLATION_RATE))**years_to_hold
    sale_commission = SALES_COMMISSION * sale_price
    to_pay = -npf.fv(monthly_interest, years_to_hold*12, monthly_mortgage, -loan)
    net_sale_proceeds = sale_price - sale_commission - to_pay 
    cash_flows.append(net_sale_proceeds)

    # NPV and IRR
    npv = npf.npv(INFLATION_RATE/12, cash_flows)
    irr = npf.irr(cash_flows)
   
    return {
        'NPV': npv,
        'IRR': irr,
        'Annual Cash Flow': cash_flows[1:-1],
        'Net Sale Proceeds': cash_flows[-1]
        }

def calculate_property_tax(price):
    # information sourced from sro.vic.gov.au
    if price < 50000:
        property_tax = 0
    elif price < 100000:
        property_tax = 500
    elif price < 300000:
        property_tax = 975
    elif price < 600000:
        property_tax = 1350 + 0.003 * (price - 300000)
    elif price < 1000000:
        property_tax = 2250 + 0.006 * (price - 600000)
    elif price < 1800000:
        property_tax = 4650 + 0.009 * (price - 1000000)
    elif price < 3000000:
        property_tax = 11850 + 0.0165 * (price - 1800000)
    else:
        property_tax = 31650 + 0.0265 * (price - 3000000)
   
    return property_tax

result = rent_analyser()

print(f"\n{'='*45}")
print(f"  PROPERTY INVESTMENT ANALYSIS")
print(f"{'='*45}")
print(f"  NPV:               ${result['NPV']:>12,.2f}")
print(f"  IRR (annual):      {((1 + result['IRR'])**12 - 1)*100:>11.2f}%")
print(f"  Net Sale Proceeds: ${result['Net Sale Proceeds']:>12,.2f}")
print(f"{'='*45}")

print(f"\n  MONTHLY CASH FLOWS")
print(f"  {'Month':<8} {'Cash Flow':>12}")
print(f"  {'-'*22}")
for i, cf in enumerate(result['Annual Cash Flow'], start=1):
    print(f"  {i:<8} ${cf:>12,.2f}")

print(f"\n  Net Sale Proceeds: ${result['Net Sale Proceeds']:>12,.2f}")
print(f"{'='*45}\n")
