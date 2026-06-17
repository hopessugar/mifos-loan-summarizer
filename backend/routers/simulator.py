from fastapi import APIRouter
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/simulator", tags=["simulator"])

class SimulatorRequest(BaseModel):
    loan_amount: Decimal
    interest_rate: Decimal
    tenure_months: int
    interest_type: str = "REDUCING"
    missed_payments: int = 0
    late_fee_per_month: Decimal = Decimal('0')

class AmortizationRow(BaseModel):
    month: int
    emi: Decimal
    principal: Decimal
    interest: Decimal
    balance: Decimal

class SimulatorResponse(BaseModel):
    effective_interest_rate: Decimal
    total_late_fees: Decimal
    amortization_schedule: list[AmortizationRow]

def convert_flat_to_reducing(flat_rate: Decimal, n: int) -> Decimal:
    if n <= 0: return flat_rate
    return (Decimal('2') * Decimal(str(n)) * flat_rate) / (Decimal(str(n)) + Decimal('1'))

@router.post("/", response_model=SimulatorResponse)
def simulate_loan(req: SimulatorRequest):
    if req.interest_type.upper() == "FLAT":
        eff_rate = convert_flat_to_reducing(req.interest_rate, req.tenure_months)
    else:
        eff_rate = req.interest_rate

    total_late_fees = Decimal(str(req.missed_payments)) * req.late_fee_per_month

    schedule = []
    balance = req.loan_amount
    monthly_rate = eff_rate / Decimal('100') / Decimal('12')
    
    if monthly_rate > 0:
        emi = (balance * monthly_rate * ((Decimal('1') + monthly_rate) ** req.tenure_months)) / (((Decimal('1') + monthly_rate) ** req.tenure_months) - Decimal('1'))
    else:
        emi = balance / Decimal(str(max(req.tenure_months, 1)))

    for month in range(1, req.tenure_months + 1):
        interest = balance * monthly_rate
        principal = emi - interest
        if balance - principal < Decimal('0.01'):
            principal = balance
            emi = principal + interest
            
        balance -= principal
        schedule.append(AmortizationRow(
            month=month,
            emi=round(emi, 2),
            principal=round(principal, 2),
            interest=round(interest, 2),
            balance=round(max(Decimal('0'), balance), 2)
        ))

    return SimulatorResponse(
        effective_interest_rate=round(eff_rate, 2),
        total_late_fees=round(total_late_fees, 2),
        amortization_schedule=schedule
    )
