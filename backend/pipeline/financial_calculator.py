from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Optional, Tuple


def calculate_emi_reducing_balance(
    principal: Decimal,
    annual_interest_rate: Decimal,
    tenure_months: int
) -> Optional[Decimal]:
    """Calculate EMI using reducing balance method with Decimal precision"""
    if not all([principal, annual_interest_rate is not None, tenure_months]):
        return None
    
    try:
        principal = Decimal(str(principal)) if not isinstance(principal, Decimal) else principal
        annual_interest_rate = Decimal(str(annual_interest_rate)) if not isinstance(annual_interest_rate, Decimal) else annual_interest_rate
        
        if principal <= 0 or annual_interest_rate < 0 or tenure_months <= 0:
            return None
        
        monthly_rate = annual_interest_rate / Decimal('1200')  # Divide by 100 * 12
        
        if monthly_rate == 0:
            return (principal / Decimal(str(tenure_months))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
        one_plus_r = Decimal('1') + monthly_rate
        power_term = one_plus_r ** tenure_months
        
        numerator = principal * monthly_rate * power_term
        denominator = power_term - Decimal('1')
        
        emi = numerator / denominator
        
        return emi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    except (ValueError, ZeroDivisionError, OverflowError, InvalidOperation):
        return None


def calculate_emi_flat_rate(
    principal: Decimal,
    annual_interest_rate: Decimal,
    tenure_months: int
) -> Optional[Decimal]:
    """Calculate EMI using flat rate method with Decimal precision"""
    if not all([principal, annual_interest_rate is not None, tenure_months]):
        return None
    
    try:
        principal = Decimal(str(principal)) if not isinstance(principal, Decimal) else principal
        annual_interest_rate = Decimal(str(annual_interest_rate)) if not isinstance(annual_interest_rate, Decimal) else annual_interest_rate
        
        if principal <= 0 or annual_interest_rate < 0 or tenure_months <= 0:
            return None
        
        # Total Interest = Principal × Rate × Time (in years)
        total_interest = principal * (annual_interest_rate / Decimal('100')) * (Decimal(str(tenure_months)) / Decimal('12'))
        total_amount = principal + total_interest
        emi = total_amount / Decimal(str(tenure_months))
        
        return emi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    except (ValueError, ZeroDivisionError, InvalidOperation):
        return None


def calculate_total_repayment(
    emi: Decimal,
    tenure_months: int
) -> Optional[Decimal]:
    """Calculate total repayment amount with Decimal precision"""
    if not all([emi, tenure_months]):
        return None
    
    try:
        emi = Decimal(str(emi)) if not isinstance(emi, Decimal) else emi
        
        if emi <= 0 or tenure_months <= 0:
            return None
        
        return (emi * Decimal(str(tenure_months))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    except (ValueError, InvalidOperation):
        return None


def calculate_total_interest(
    total_repayment: Decimal,
    principal: Decimal
) -> Optional[Decimal]:
    """Calculate total interest paid with Decimal precision"""
    if not all([total_repayment, principal]):
        return None
    
    try:
        total_repayment = Decimal(str(total_repayment)) if not isinstance(total_repayment, Decimal) else total_repayment
        principal = Decimal(str(principal)) if not isinstance(principal, Decimal) else principal
        
        if total_repayment < principal:
            return None
        
        return (total_repayment - principal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    except (ValueError, InvalidOperation):
        return None


def calculate_effective_interest_rate(
    total_interest: Decimal,
    principal: Decimal
) -> Optional[Decimal]:
    """Calculate effective interest rate with Decimal precision"""
    if not all([total_interest, principal]):
        return None
    
    try:
        total_interest = Decimal(str(total_interest)) if not isinstance(total_interest, Decimal) else total_interest
        principal = Decimal(str(principal)) if not isinstance(principal, Decimal) else principal
        
        if principal <= 0:
            return None
        
        return ((total_interest / principal) * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    except (ValueError, ZeroDivisionError, InvalidOperation):
        return None


def verify_emi_consistency(
    stated_emi: Decimal,
    principal: Decimal,
    annual_interest_rate: Decimal,
    tenure_months: int,
    interest_type: Optional[str] = None
) -> Tuple[bool, Decimal, Decimal, str]:
    """Verify EMI calculation consistency with Decimal precision"""
    if not all([stated_emi, principal, annual_interest_rate is not None, tenure_months]):
        return False, Decimal('0'), Decimal('0'), "insufficient_data"
    
    try:
        stated_emi = Decimal(str(stated_emi)) if not isinstance(stated_emi, Decimal) else stated_emi
        principal = Decimal(str(principal)) if not isinstance(principal, Decimal) else principal
        annual_interest_rate = Decimal(str(annual_interest_rate)) if not isinstance(annual_interest_rate, Decimal) else annual_interest_rate
    except (ValueError, InvalidOperation):
        return False, Decimal('0'), Decimal('0'), "invalid_input"
    
    if interest_type and 'flat' in interest_type.lower():
        calculated_emi = calculate_emi_flat_rate(principal, annual_interest_rate, tenure_months)
        method = "flat_rate"
    elif interest_type and 'reducing' in interest_type.lower():
        calculated_emi = calculate_emi_reducing_balance(principal, annual_interest_rate, tenure_months)
        method = "reducing_balance"
    else:
        # Try both methods and pick the closest
        calculated_emi_rb = calculate_emi_reducing_balance(principal, annual_interest_rate, tenure_months)
        calculated_emi_flat = calculate_emi_flat_rate(principal, annual_interest_rate, tenure_months)
        
        if calculated_emi_rb is None and calculated_emi_flat is None:
            return False, Decimal('0'), Decimal('0'), "calculation_failed"
        
        if calculated_emi_rb and calculated_emi_flat:
            diff_rb = abs(calculated_emi_rb - stated_emi) / stated_emi
            diff_flat = abs(calculated_emi_flat - stated_emi) / stated_emi
            
            if diff_rb <= diff_flat:
                calculated_emi = calculated_emi_rb
                method = "reducing_balance"
            else:
                calculated_emi = calculated_emi_flat
                method = "flat_rate"
        else:
            calculated_emi = calculated_emi_rb or calculated_emi_flat
            method = "reducing_balance" if calculated_emi_rb else "flat_rate"
    
    if calculated_emi is None:
        return False, Decimal('0'), Decimal('0'), "calculation_failed"
    
    discrepancy_pct = (abs(calculated_emi - stated_emi) / stated_emi * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    is_consistent = discrepancy_pct <= Decimal('5.0')
    
    return is_consistent, discrepancy_pct, calculated_emi, method


def estimate_missing_emi(
    principal: Optional[Decimal],
    annual_interest_rate: Optional[Decimal],
    tenure_months: Optional[int],
    interest_type: Optional[str] = None
) -> Tuple[Optional[Decimal], str]:
    """Estimate EMI when not provided in contract"""
    if not all([principal, annual_interest_rate is not None, tenure_months]):
        return None, "insufficient_data"
    
    try:
        principal = Decimal(str(principal)) if not isinstance(principal, Decimal) else principal
        annual_interest_rate = Decimal(str(annual_interest_rate)) if not isinstance(annual_interest_rate, Decimal) else annual_interest_rate
    except (ValueError, InvalidOperation):
        return None, "invalid_input"
    
    if interest_type and 'flat' in interest_type.lower():
        emi = calculate_emi_flat_rate(principal, annual_interest_rate, tenure_months)
        return emi, "flat_rate_estimate"
    else:
        emi = calculate_emi_reducing_balance(principal, annual_interest_rate, tenure_months)
        return emi, "reducing_balance_estimate"


def convert_flat_to_reducing_rate(flat_rate: Decimal, tenure_months: int) -> Optional[Decimal]:
    """
    Convert flat interest rate to approximate reducing balance rate.
    Formula: Effective Rate ≈ (2 * n * flat_rate) / (n + 1)
    where n is tenure in months
    """
    try:
        flat_rate = Decimal(str(flat_rate)) if not isinstance(flat_rate, Decimal) else flat_rate
        
        if flat_rate <= 0 or tenure_months <= 0:
            return None
        
        n = Decimal(str(tenure_months))
        effective_rate = (Decimal('2') * n * flat_rate) / (n + Decimal('1'))
        
        return effective_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    except (ValueError, ZeroDivisionError, InvalidOperation):
        return None
