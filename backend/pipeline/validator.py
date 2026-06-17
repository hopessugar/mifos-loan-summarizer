import re
from Levenshtein import ratio as levenshtein_ratio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import settings
from schemas.loan_schema import LoanAgreementSchema
from pipeline.financial_calculator import (
    estimate_missing_emi,
    verify_emi_consistency,
    calculate_total_repayment,
    calculate_total_interest,
    calculate_effective_interest_rate
)


# TODO: Expand this list based on domain knowledge
FINANCIAL_KEYWORDS = [
    'interest', 'rate', 'emi', 'instalment', 'installment', 'penalty',
    'principal', 'prepayment', 'schedule', 'repayment', 'loan', 'amount',
    'fee', 'charge', 'default', 'payment', 'monthly', 'annual', 'per annum',
    'processing', 'insurance', 'collateral', 'tenure', 'duration',
]


def verify_numerical_value(value, source_clause: str) -> bool:
    if not source_clause or value is None:
        return False
    import re
    from decimal import Decimal
    clean_clause = source_clause.replace(',', '')
    numbers = re.findall(r'\d+(?:\.\d+)?', clean_clause)
    
    try:
        val_dec = Decimal(str(value))
    except Exception:
        return False
        
    for num in numbers:
        try:
            if Decimal(num) == val_dec:
                return True
        except Exception:
            pass
    return False


def check_hallucination(value: str, source_clause: str, contract_text: str) -> dict:
    if not value or not contract_text:
        return {'is_verified': False, 'similarity': 0.0, 'verify_method': 'none'}

    if source_clause and len(source_clause) > 10:
        source_lower = source_clause.lower().strip()
        contract_lower = contract_text.lower()
        
        if source_lower in contract_lower:
            return {
                'is_verified': True,
                'similarity': 1.0,
                'verify_method': 'exact_match',
            }
        
        best_score = 0.0
        window_size = len(source_clause)
        step = max(1, window_size // 4)
        
        for i in range(0, max(1, len(contract_text) - window_size + 1), step):
            window = contract_text[i:i + window_size + 20]
            score = levenshtein_ratio(source_lower, window.lower())
            if score > best_score:
                best_score = score
                
        return {
            'is_verified': best_score >= 0.75,
            'similarity': round(best_score, 3),
            'verify_method': 'levenshtein_clause',
        }
    
    value_str = str(value).strip()

    if len(value_str) <= 50:
        best_score = 0.0
        window_size = max(len(value_str), 5)
        step = 3
        for i in range(0, max(1, len(contract_text) - window_size + 1), step):
            window = contract_text[i:i + window_size + 5]
            score = levenshtein_ratio(value_str.lower(), window.lower())
            if score > best_score:
                best_score = score
        return {
            'is_verified': best_score >= settings.LEVENSHTEIN_THRESHOLD,
            'similarity': round(best_score, 3),
            'verify_method': 'levenshtein',
        }

    try:
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform([value_str, contract_text])
        score = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
        return {
            'is_verified': score >= settings.COSINE_THRESHOLD,
            'similarity': round(score, 3),
            'verify_method': 'cosine',
        }
    except Exception:
        return {'is_verified': False, 'similarity': 0.0, 'verify_method': 'cosine_failed'}


def get_regex_score(field_name: str, value) -> float:
    if value is None:
        return 0.3
    value_str = str(value)
    patterns = {
        'loan_amount': r'^\d+(\.\d+)?$',
        'interest_rate': r'^\d+(\.\d+)?(%?\s*(reducing|flat|diminishing))?$',
        'repayment_duration': r'^\d+(\.\d+)?$',
        'monthly_payment': r'^\d+(\.\d+)?$',
        'total_cost': r'^\d+(\.\d+)?$',
        'late_fee': r'^\d+(\.\d+)?$',
        'processing_fee': r'^\d+(\.\d+)?$',
        'penalty_interest': r'^\d+(\.\d+)?$',
    }
    pattern = patterns.get(field_name)
    if not pattern:
        return 0.7
    if re.fullmatch(pattern, value_str.strip(), re.IGNORECASE):
        return 1.0
    if re.search(r'\d', value_str):
        return 0.9
    return 0.3


def get_keyword_proximity_score(source_clause: str) -> float:
    if not source_clause:
        return 0.0
    clause_lower = source_clause.lower()
    matches = sum(1 for kw in FINANCIAL_KEYWORDS if kw in clause_lower)
    return min(matches / 3.0, 1.0)


def calculate_confidence(field_name: str, value, source_clause: str, similarity: float) -> tuple[float, str]:
    if similarity >= 0.95 and source_clause:
        return 0.98, 'exact_match'
    
    if similarity >= 0.80 and source_clause and len(source_clause) > 10:
        regex_score = get_regex_score(field_name, value)
        keyword_score = get_keyword_proximity_score(source_clause)
        
        if regex_score >= 0.9 and keyword_score >= 0.3:
            return 0.90, 'pattern_match'
        elif regex_score >= 0.9:
            return 0.85, 'pattern_match'
    
    if similarity >= 0.60 or (source_clause and len(source_clause) > 10):
        regex_score = get_regex_score(field_name, value)
        if regex_score >= 0.9:
            return 0.75, 'inference'
        else:
            return 0.65, 'inference'
    
    if similarity > 0:
        return 0.45, 'model_guess'
    
    return 0.30, 'model_guess'


def check_math_consistency(schema: LoanAgreementSchema) -> dict:
    mp = schema.monthly_payment.value
    rd = schema.repayment_duration.value
    la = schema.loan_amount.value
    ir = schema.interest_rate.value
    ir_type = schema.interest_rate.type

    result = {
        'is_consistent': None,
        'difference_pct': None,
        'warning': None,
        'emi_status': 'not_checked',
        'estimated_emi': None,
        'calculation_method': None,
        'discrepancy_details': None
    }

    if not all([la, ir, rd]):
        result['warning'] = 'Insufficient data to verify calculations (missing principal, rate, or tenure)'
        result['emi_status'] = 'insufficient_data'
        return result

    if not mp:
        estimated_emi, method = estimate_missing_emi(la, ir, rd, ir_type)
        
        if estimated_emi:
            result['estimated_emi'] = estimated_emi
            result['calculation_method'] = method
            result['emi_status'] = 'estimated'
            result['warning'] = f'Contract does not specify monthly payment. Estimated EMI: Rs. {estimated_emi:,.2f} (using {method.replace("_", " ")}). Please confirm with lender.'
            result['is_consistent'] = None
            
            total_repayment = calculate_total_repayment(estimated_emi, rd)
            result['estimated_total_repayment'] = total_repayment
            result['estimated_total_interest'] = calculate_total_interest(total_repayment, la) if total_repayment else None
        else:
            result['warning'] = 'Cannot estimate EMI - calculation failed'
            result['emi_status'] = 'calculation_failed'
        
        return result

    is_consistent, discrepancy_pct, calculated_emi, method = verify_emi_consistency(
        mp, la, ir, rd, ir_type
    )
    
    result['estimated_emi'] = calculated_emi
    result['calculation_method'] = method
    result['difference_pct'] = discrepancy_pct
    result['emi_status'] = 'verified'
    
    if method == 'insufficient_data':
        result['is_consistent'] = None
        result['warning'] = 'Cannot verify EMI - insufficient data'
        result['emi_status'] = 'verification_failed'
    elif method == 'calculation_failed':
        result['is_consistent'] = None
        result['warning'] = 'Cannot verify EMI - calculation failed'
        result['emi_status'] = 'verification_failed'
    elif is_consistent:
        result['is_consistent'] = True
        result['warning'] = None
    else:
        result['is_consistent'] = False
        
        if discrepancy_pct > 20:
            result['warning'] = f'⚠️ CRITICAL: Stated EMI (Rs. {mp:,.2f}) differs significantly from calculated EMI (Rs. {calculated_emi:,.2f}) - {discrepancy_pct:.1f}% discrepancy. This may indicate hidden fees or incorrect calculations. Request detailed amortization schedule from lender.'
        elif discrepancy_pct > 10:
            result['warning'] = f'⚠️ WARNING: Stated EMI (Rs. {mp:,.2f}) differs from calculated EMI (Rs. {calculated_emi:,.2f}) - {discrepancy_pct:.1f}% discrepancy. Ask lender to explain this difference.'
        else:
            result['warning'] = f'Minor discrepancy: Stated EMI (Rs. {mp:,.2f}) vs calculated EMI (Rs. {calculated_emi:,.2f}) - {discrepancy_pct:.1f}% difference. Likely due to rounding.'
        
        result['discrepancy_details'] = {
            'stated_emi': mp,
            'calculated_emi': calculated_emi,
            'difference_amount': abs(mp - calculated_emi),
            'method_used': method
        }

    return result


# WARNING: Standard default triggers should NOT significantly increase risk
STANDARD_DEFAULT_TRIGGERS = {
    'missed payment', 'non-payment', 'failure to pay', 'payment default',
    'insolvency', 'bankruptcy', 'liquidation',
    'fraud', 'misrepresentation', 'false information',
    'death of borrower', 'criminal activity'
}


def is_standard_default_clause(trigger: str) -> bool:
    trigger_lower = trigger.lower()
    return any(std in trigger_lower for std in STANDARD_DEFAULT_TRIGGERS)


def is_predatory_clause(trigger: str) -> bool:
    trigger_lower = trigger.lower()
    predatory_indicators = [
        'change of employment', 'loss of job', 'relocation',
        'any reason', 'sole discretion', 'without cause',
        'demand', 'lender may declare', 'acceleration',
        'cross-default', 'associated', 'related party'
    ]
    return any(ind in trigger_lower for ind in predatory_indicators)


def compute_risk_analysis(schema: LoanAgreementSchema) -> dict:
    score = 0.0
    factors = []
    warnings = []

    ir = schema.interest_rate.value
    if ir:
        if ir >= 48:
            score += 4.0
            factors.append(f'Extremely high interest rate ({ir}% per annum)')
            warnings.append('CRITICAL: This interest rate is likely predatory and may be illegal in some jurisdictions')
        elif ir >= 36:
            score += 3.5
            factors.append(f'Very high interest rate ({ir}% per annum - well above market rates)')
            warnings.append('WARNING: This rate is significantly higher than typical personal loans')
        elif ir >= 24:
            score += 2.5
            factors.append(f'High interest rate ({ir}% per annum)')
        elif ir >= 18:
            score += 1.5
            factors.append(f'Above-average interest rate ({ir}% per annum)')
        elif ir >= 12:
            score += 0.5
            factors.append(f'Moderate interest rate ({ir}% per annum)')

    late_payment_interest = schema.late_payment_interest.value
    late_fee = schema.late_fee.value
    
    if late_payment_interest and late_payment_interest >= 48:
        score += 2.5
        factors.append(f'Extreme late payment interest rate ({late_payment_interest}% per annum)')
        warnings.append('CRITICAL: Late payment interest rate is predatory')
    elif late_payment_interest and late_payment_interest >= 36:
        score += 2.0
        factors.append(f'Very high late payment interest rate ({late_payment_interest}% per annum)')
    elif late_payment_interest and late_payment_interest >= 24:
        score += 1.0
        factors.append(f'High late payment interest rate ({late_payment_interest}% per annum)')
    
    if late_fee and late_fee > 1000:
        score += 1.0
        factors.append(f'Large late payment fee (Rs. {late_fee:,.0f})')

    prepayment_penalty = schema.prepayment_penalty.value
    if prepayment_penalty:
        pp_pct = prepayment_penalty * 100 if prepayment_penalty < 1 else prepayment_penalty
        
        if pp_pct >= 5:
            score += 2.0
            factors.append(f'Severe prepayment penalty ({pp_pct}% - discourages early repayment)')
            warnings.append('WARNING: High prepayment penalty restricts your ability to repay early')
        elif pp_pct >= 3:
            score += 1.5
            factors.append(f'Significant prepayment penalty ({pp_pct}%)')
        elif pp_pct >= 1:
            score += 0.5
            factors.append(f'Prepayment penalty applies ({pp_pct}%)')

    penalty_interest = schema.penalty_interest.value
    if penalty_interest and penalty_interest >= 36:
        score += 1.5
        factors.append(f'High general penalty interest rate ({penalty_interest}% per annum)')
    elif penalty_interest and penalty_interest >= 24:
        score += 1.0
        factors.append(f'Elevated general penalty interest rate ({penalty_interest}% per annum)')

    if schema.collateral.present:
        if schema.collateral.seizure_clause:
            score += 2.5
            factors.append('Asset seizure risk: Lender can seize collateral on default')
            warnings.append('WARNING: Your assets are at risk if you cannot repay')
        else:
            score += 1.5
            factors.append('Collateral required (asset may be at risk)')

    default_events = schema.default_events
    standard_count = sum(1 for e in default_events if is_standard_default_clause(e.trigger))
    predatory_count = sum(1 for e in default_events if is_predatory_clause(e.trigger))
    
    if predatory_count >= 3:
        score += 3.0
        factors.append(f'Multiple predatory default triggers ({predatory_count} unusual clauses)')
        warnings.append('CRITICAL: Contract contains multiple unusual default triggers that give lender excessive power')
    elif predatory_count >= 1:
        score += 2.0
        factors.append(f'Contains {predatory_count} unusual/predatory default trigger(s)')
        warnings.append('WARNING: Some default triggers are not standard protective clauses')
    elif len(default_events) >= 8:
        score += 1.0
        factors.append(f'Large number of default triggers ({len(default_events)} clauses)')

    processing_fee = schema.processing_fee.value
    loan_amount = schema.loan_amount.value
    if processing_fee and loan_amount and (processing_fee / loan_amount) > 0.05:
        score += 1.0
        pct = (processing_fee / loan_amount) * 100
        factors.append(f'High processing fee ({pct:.1f}% of loan amount)')

    score = round(max(0.0, min(10.0, score)), 1)
    
    if score <= 3.0:
        risk_band = 'Low Risk'
        band_explanation = 'Standard loan terms with reasonable conditions'
    elif score <= 6.0:
        risk_band = 'Moderate Risk'
        band_explanation = 'Some concerning terms - review carefully before signing'
    elif score <= 8.0:
        risk_band = 'High Risk'
        band_explanation = 'Multiple red flags - seek independent legal advice'
    else:
        risk_band = 'Very High Risk'
        band_explanation = 'Severe predatory lending indicators - strongly consider alternatives'

    return {
        'score': score,
        'risk_band': risk_band,
        'band_explanation': band_explanation,
        'factors': factors,
        'warnings': warnings,
        'default_events_breakdown': {
            'total': len(default_events),
            'standard_clauses': standard_count,
            'predatory_clauses': predatory_count
        }
    }


def detect_missing_terms(schema: LoanAgreementSchema) -> list[str]:
    missing_warnings = []
    if not schema.prepayment_penalty.value and not schema.prepayment_penalty.source_clause:
        missing_warnings.append("No mention of prepayment policy — ask: 'Can I repay early without penalty?'")
    if not schema.late_fee.value and not schema.late_fee.source_clause:
        missing_warnings.append("No mention of late payment fee — ask: 'What happens if I miss a payment?'")
    if not schema.interest_rate.type:
        missing_warnings.append("No mention of interest rate type — ask: 'Is this a flat rate or reducing balance?'")
    if not schema.repayment_schedule.due_day:
        missing_warnings.append("No due day specified — ask: 'What day of the month is my EMI due?'")
    return missing_warnings


def validate_extraction(schema: LoanAgreementSchema, contract_text: str) -> dict:
    entity_results = {}

    fields_to_validate = {
        'loan_amount': (schema.loan_amount.value, schema.loan_amount.source_clause),
        'interest_rate': (schema.interest_rate.value, schema.interest_rate.source_clause),
        'repayment_duration': (schema.repayment_duration.value, schema.repayment_duration.source_clause),
        'monthly_payment': (schema.monthly_payment.value, schema.monthly_payment.source_clause),
        'total_cost': (schema.total_cost.value, schema.total_cost.source_clause),
        'late_fee': (schema.late_fee.value, schema.late_fee.source_clause),
        'late_payment_interest': (schema.late_payment_interest.value, schema.late_payment_interest.source_clause),
        'penalty_interest': (schema.penalty_interest.value, schema.penalty_interest.source_clause),
        'prepayment_penalty': (schema.prepayment_penalty.value, schema.prepayment_penalty.source_clause),
        'processing_fee': (schema.processing_fee.value, schema.processing_fee.source_clause),
    }

    for field_name, (value, source_clause) in fields_to_validate.items():
        if value is None:
            continue

        display_value = value
        if field_name == 'prepayment_penalty' and value is not None and value < 1:
            display_value = value * 100  # 0.02 -> 2%

        hallucination = check_hallucination(str(value), source_clause or '', contract_text)
        confidence, extraction_method = calculate_confidence(field_name, value, source_clause or '', hallucination['similarity'])

        from decimal import Decimal
        is_numeric = isinstance(value, (int, float, Decimal))
        
        if is_numeric and hallucination['is_verified']:
            num_verified = verify_numerical_value(value, source_clause)
            if not num_verified:
                hallucination['is_verified'] = False
                hallucination['verify_method'] = 'failed_numerical_check'
                
        flag = None
        if not hallucination['is_verified']:
            flag = 'Could not verify this value in the source contract'
        elif confidence < settings.CONFIDENCE_THRESHOLD:
            flag = 'Low confidence — please verify manually'

        entity_results[field_name] = {
            'value': display_value,
            'source_clause': source_clause or None,
            'confidence': round(confidence, 3),
            'extraction_method': extraction_method,
            'is_verified': hallucination['is_verified'],
            'similarity': hallucination['similarity'],
            'verify_method': hallucination['verify_method'],
            'flag': flag,
        }

    for key, val in [
        ('payment_frequency', schema.payment_frequency),
        ('payment_due_day', schema.payment_due_day),
        ('repayment_start_date', schema.repayment_start_date),
        ('currency', schema.currency),
    ]:
        if val:
            entity_results[key] = {
                'value': val,
                'source_clause': None,
                'confidence': 0.75,
                'is_verified': True,
                'similarity': 0.75,
                'verify_method': 'metadata',
                'flag': None,
            }

    math_check = check_math_consistency(schema)
    risk = compute_risk_analysis(schema)
    missing_terms = detect_missing_terms(schema)
    
    # Calculate Borrower Protection Score (BPS)
    # Risk score is 0-10, where 0 is safest. Base BPS is 100 - (risk * 10).
    base_bps = 100 - (risk['score'] * 10)
    # Deduct 5 points for every missing term
    bps_score = max(0, min(100, base_bps - (len(missing_terms) * 5)))
    
    # Generate negotiation tips
    negotiation_tips = []
    for factor in risk['factors']:
        if 'seizure' in factor.lower():
            negotiation_tips.append("Negotiation Tip: Lender may seize collateral. Ask to add: 'Lender shall provide 30 days written notice before initiating collateral seizure proceedings'")
        if 'prepayment penalty' in factor.lower():
            negotiation_tips.append("Negotiation Tip: High prepayment penalty. Ask to cap it at 1-2% or remove it after the first year.")
        if 'interest rate' in factor.lower() and ('Very high' in factor or 'Extremely high' in factor):
            negotiation_tips.append("Negotiation Tip: Interest rate is well above market average. Strongly recommend negotiating a lower rate or finding another lender.")
            
    risk['bps_score'] = bps_score
    risk['negotiation_tips'] = negotiation_tips

    mp = schema.monthly_payment.value
    rd = schema.repayment_duration.value
    la = schema.loan_amount.value

    # FIXME: Add estimated EMI to entities when EMI was not extracted but was calculated
    if not mp and math_check.get('estimated_emi'):
        estimated_emi = math_check.get('estimated_emi')
        calculation_method = math_check.get('calculation_method', 'reducing_balance_estimate')
        
        entity_results['monthly_payment'] = {
            'value': estimated_emi,
            'source_clause': None,
            'confidence': 0.80,  # High confidence in calculation
            'extraction_method': 'calculated',
            'is_verified': True,
            'similarity': 0.80,
            'verify_method': 'calculated_from_loan_terms',
            'flag': f'Estimated using {calculation_method.replace("_", " ")} - not explicitly stated in contract',
        }

    emi_for_calculation = mp if mp else math_check.get('estimated_emi')
    
    total_repayment = None
    total_interest = None
    eff_rate = None
    emi_note = None

    if emi_for_calculation and rd:
        total_repayment = calculate_total_repayment(emi_for_calculation, rd)
        
        if total_repayment and la:
            total_interest = calculate_total_interest(total_repayment, la)
            eff_rate = calculate_effective_interest_rate(total_interest, la)
        
        if not mp and math_check.get('estimated_emi'):
            emi_note = 'calculated_from_loan_terms'

    return {
        'entities': entity_results,
        'math_check': math_check,
        'financial_summary': {
            'total_repayment': total_repayment,
            'total_interest': total_interest,
            'effective_interest_pct': eff_rate,
            'emi_used': emi_for_calculation,
            'emi_note': emi_note,
        },
        'risk_analysis': risk,
        'default_events': [
            {'trigger': e.trigger, 'source_clause': e.source_clause}
            for e in schema.default_events
        ],
        'missing_terms': missing_terms,
    }