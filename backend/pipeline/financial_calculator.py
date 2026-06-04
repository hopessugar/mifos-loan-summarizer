import math
from typing import Optional, Tuple


def calculate_emi_reducing_balance(
    principal: float,
    annual_interest_rate: float,
    tenure_months: int
) -> Optional[float]:
    if not all([principal, annual_interest_rate, tenure_months]):
        return None
    
    if principal <= 0 or annual_interest_rate < 0 or tenure_months <= 0:
        return None
    
    try:
        monthly_rate = annual_interest_rate / 12 / 100
        
        if monthly_rate == 0:
            return principal / tenure_months
        
        numerator = principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)
        denominator = math.pow(1 + monthly_rate, tenure_months) - 1
        
        emi = numerator / denominator
        
        return round(emi, 2)
    
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def calculate_emi_flat_rate(
    principal: float,
    annual_interest_rate: float,
    tenure_months: int
) -> Optional[float]:
    if not all([principal, annual_interest_rate, tenure_months]):
        return None
    
    if principal <= 0 or annual_interest_rate < 0 or tenure_months <= 0:
        return None
    
    try:
        total_interest = principal * (annual_interest_rate / 100) * (tenure_months / 12)
        total_amount = principal + total_interest
        emi = total_amount / tenure_months
        
        return round(emi, 2)
    
    except (ValueError, ZeroDivisionError):
        return None


def calculate_total_repayment(
    emi: float,
    tenure_months: int
) -> Optional[float]:
    if not all([emi, tenure_months]):
        return None
    
    if emi <= 0 or tenure_months <= 0:
        return None
    
    return round(emi * tenure_months, 2)


def calculate_total_interest(
    total_repayment: float,
    principal: float
) -> Optional[float]:
    if not all([total_repayment, principal]):
        return None
    
    if total_repayment < principal:
        return None
    
    return round(total_repayment - principal, 2)


def calculate_effective_interest_rate(
    total_interest: float,
    principal: float
) -> Optional[float]:
    if not all([total_interest, principal]):
        return None
    
    if principal <= 0:
        return None
    
    return round((total_interest / principal) * 100, 2)


def verify_emi_consistency(
    stated_emi: float,
    principal: float,
    annual_interest_rate: float,
    tenure_months: int,
    interest_type: Optional[str] = None
) -> Tuple[bool, float, float, str]:
    if not all([stated_emi, principal, annual_interest_rate, tenure_months]):
        return False, 0.0, 0.0, "insufficient_data"
    
    if interest_type and 'flat' in interest_type.lower():
        calculated_emi = calculate_emi_flat_rate(principal, annual_interest_rate, tenure_months)
        method = "flat_rate"
    elif interest_type and 'reducing' in interest_type.lower():
        calculated_emi = calculate_emi_reducing_balance(principal, annual_interest_rate, tenure_months)
        method = "reducing_balance"
    else:
        calculated_emi_rb = calculate_emi_reducing_balance(principal, annual_interest_rate, tenure_months)
        calculated_emi_flat = calculate_emi_flat_rate(principal, annual_interest_rate, tenure_months)
        
        if calculated_emi_rb is None and calculated_emi_flat is None:
            return False, 0.0, 0.0, "calculation_failed"
        
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
        return False, 0.0, 0.0, "calculation_failed"
    
    discrepancy_pct = abs(calculated_emi - stated_emi) / stated_emi * 100
    is_consistent = discrepancy_pct <= 5.0
    
    return is_consistent, round(discrepancy_pct, 2), calculated_emi, method


def estimate_missing_emi(
    principal: Optional[float],
    annual_interest_rate: Optional[float],
    tenure_months: Optional[float],
    interest_type: Optional[str] = None
) -> Tuple[Optional[float], str]:
    if not all([principal, annual_interest_rate, tenure_months]):
        return None, "insufficient_data"
    
    if interest_type and 'flat' in interest_type.lower():
        emi = calculate_emi_flat_rate(principal, annual_interest_rate, tenure_months)
        return emi, "flat_rate_estimate"
    else:
        emi = calculate_emi_reducing_balance(principal, annual_interest_rate, tenure_months)
        return emi, "reducing_balance_estimate"
