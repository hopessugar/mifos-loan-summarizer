from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from decimal import Decimal


class EntityField(BaseModel):
    value: Optional[Decimal] = None
    source_clause: Optional[str] = None
    confidence: Optional[float] = None
    extraction_method: Optional[str] = None
    is_verified: bool = False
    similarity: float = 0.0


class InterestField(BaseModel):
    value: Optional[Decimal] = None
    type: Optional[str] = None
    source_clause: Optional[str] = None
    confidence: Optional[float] = None
    extraction_method: Optional[str] = None
    is_verified: bool = False
    similarity: float = 0.0


class FeeField(BaseModel):
    value: Optional[Decimal] = None
    logic: Optional[str] = None
    base: Optional[str] = None
    source_clause: Optional[str] = None
    confidence: Optional[float] = None
    extraction_method: Optional[str] = None
    is_verified: bool = False
    similarity: float = 0.0


class CollateralField(BaseModel):
    present: bool = False
    description: Optional[str] = None
    seizure_clause: Optional[str] = None
    source_clause: Optional[str] = None


class RepaymentScheduleField(BaseModel):
    frequency: Optional[str] = None
    installment_amount: Optional[Decimal] = None
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

    late_fee: FeeField = FeeField()
    late_payment_interest: FeeField = FeeField()
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

    @model_validator(mode='before')
    @classmethod
    def replace_none_with_defaults(cls, values):
        """Convert null/None values from LLM JSON into empty dicts for nested models."""
        if isinstance(values, dict):
            nested_fields = [
                'loan_amount', 'interest_rate', 'repayment_duration',
                'monthly_payment', 'total_cost', 'late_fee',
                'late_payment_interest', 'penalty_interest', 'prepayment_penalty',
                'processing_fee', 'insurance_fee', 'administrative_fee',
                'other_fee', 'collateral', 'repayment_schedule',
            ]
            for field in nested_fields:
                if values.get(field) is None:
                    values[field] = {}
            if values.get('default_events') is None:
                values['default_events'] = []
        return values

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
            expected = mp * Decimal(str(rd))
            diff_pct = abs(expected - tc) / tc
            if diff_pct > Decimal('0.10'):
                pass
        return self