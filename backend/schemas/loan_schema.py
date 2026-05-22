from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class EntityField(BaseModel):
    value: Optional[float] = None
    source_clause: Optional[str] = None


class InterestField(BaseModel):
    value: Optional[float] = None
    type: Optional[str] = None
    source_clause: Optional[str] = None


class FeeField(BaseModel):
    value: Optional[float] = None
    logic: Optional[str] = None
    base: Optional[str] = None
    source_clause: Optional[str] = None


class CollateralField(BaseModel):
    present: bool = False
    description: Optional[str] = None
    seizure_clause: Optional[str] = None
    source_clause: Optional[str] = None


class RepaymentScheduleField(BaseModel):
    frequency: Optional[str] = None
    installment_amount: Optional[float] = None
    start_condition: Optional[str] = None
    due_day: Optional[str] = None
    source_clause: Optional[str] = None


class DefaultEventField(BaseModel):
    trigger: str
    source_clause: Optional[str] = None


class LoanAgreementSchema(BaseModel):
    # Core financial fields
    loan_amount: EntityField = EntityField()
    interest_rate: InterestField = InterestField()
    repayment_duration: EntityField = EntityField()
    monthly_payment: EntityField = EntityField()
    total_cost: EntityField = EntityField()
    payment_frequency: Optional[str] = None
    payment_due_day: Optional[str] = None
    repayment_start_date: Optional[str] = None
    currency: Optional[str] = 'INR'

    # Fee fields
    late_fee: FeeField = FeeField()
    penalty_interest: FeeField = FeeField()
    prepayment_penalty: FeeField = FeeField()
    processing_fee: FeeField = FeeField()
    insurance_fee: FeeField = FeeField()
    administrative_fee: FeeField = FeeField()
    other_fee: FeeField = FeeField()

    # Risk fields
    collateral: CollateralField = CollateralField()
    repayment_schedule: RepaymentScheduleField = RepaymentScheduleField()
    default_events: list[DefaultEventField] = []

    @field_validator('loan_amount', mode='before')
    @classmethod
    def validate_loan_amount(cls, v):
        if isinstance(v, dict) and v.get('value') is not None:
            if v['value'] <= 0:
                raise ValueError('loan_amount must be positive')
        return v

    @field_validator('interest_rate', mode='before')
    @classmethod
    def validate_interest_rate(cls, v):
        if isinstance(v, dict) and v.get('value') is not None:
            if v['value'] < 0 or v['value'] > 200:
                raise ValueError('interest_rate must be between 0 and 200')
        return v

    @model_validator(mode='after')
    def check_math_consistency(self):
        mp = self.monthly_payment.value
        rd = self.repayment_duration.value
        tc = self.total_cost.value
        if mp and rd and tc:
            expected = mp * rd
            diff_pct = abs(expected - tc) / tc
            if diff_pct > 0.10:
                pass
        return self