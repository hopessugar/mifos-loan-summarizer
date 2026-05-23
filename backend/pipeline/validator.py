import re
from Levenshtein import ratio as levenshtein_ratio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.config import settings
from backend.schemas.loan_schema import LoanAgreementSchema


FINANCIAL_KEYWORDS = [
    'interest', 'rate', 'emi', 'instalment', 'installment', 'penalty',
    'principal', 'prepayment', 'schedule', 'repayment', 'loan', 'amount',
    'fee', 'charge', 'default', 'payment', 'monthly', 'annual', 'per annum',
    'processing', 'insurance', 'collateral', 'tenure', 'duration',
]


def check_hallucination(value: str, contract_text: str) -> dict:
    if not value or not contract_text:
        return {
            'is_verified': False,
            'similarity': 0.0,
            'verify_method': 'none',
        }

    value_str = str(value).strip()

    # Short values — use Levenshtein sliding window
    if len(value_str) <= 50:
    best_score = 0.0
    window_size = max(len(value_str), 5)
    for i in range(0, len(contract_text) - window_size + 1, 3):
        window = contract_text[i:i + window_size]
        score = levenshtein_ratio(value_str.lower(), window.lower())
        if score > best_score:
            best_score = score
    if best_score < settings.LEVENSHTEIN_THRESHOLD:
        for i in range(0, len(contract_text) - window_size + 1, 3):
            window = contract_text[i:i + window_size + 10]
            score = levenshtein_ratio(value_str.lower(), window.lower())
            if score > best_score:
                best_score = score
    return {
        'is_verified': best_score >= settings.LEVENSHTEIN_THRESHOLD,
        'similarity': round(best_score, 3),
        'verify_method': 'levenshtein',
    }

    # Long clauses — use TF-IDF cosine similarity
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
        return {
            'is_verified': False,
            'similarity': 0.0,
            'verify_method': 'cosine_failed',
        }


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


def calculate_confidence(
    field_name: str,
    value,
    source_clause: str,
    similarity: float,
) -> float:
    regex_score = get_regex_score(field_name, value)
    keyword_score = get_keyword_proximity_score(source_clause)
    confidence = (
        0.40 * regex_score +
        0.35 * keyword_score +
        0.25 * similarity
    )
    return round(min(confidence, 1.0), 3)


def check_math_consistency(schema: LoanAgreementSchema) -> dict:
    mp = schema.monthly_payment.value
    rd = schema.repayment_duration.value
    tc = schema.total_cost.value

    if not all([mp, rd]):
        return {
            'is_consistent': None,
            'difference_pct': None,
            'warning': 'Cannot check — one or more values missing',
        }

    expected = mp * rd

    if tc:
        diff_pct = abs(expected - tc) / tc
        is_consistent = diff_pct <= settings.MATH_TOLERANCE
        warning = None
        if not is_consistent:
            warning = f"Numbers do not add up — {round(diff_pct * 100, 1)}% difference. Ask lender to explain."
        return {
            'is_consistent': is_consistent,
            'difference_pct': round(diff_pct * 100, 2),
            'warning': warning,
        }

    return {
        'is_consistent': None,
        'difference_pct': None,
        'warning': f'Total cost not found — estimated total repayment: Rs. {expected:,.0f}',
    }


def compute_risk_analysis(schema: LoanAgreementSchema) -> dict:
    score = 0.0
    factors = []

    ir = schema.interest_rate.value
    if ir:
        if ir >= 36:
            score += 4.0
            factors.append('Very high interest rate (36%+)')
        elif ir >= 24:
            score += 3.0
            factors.append('High interest rate (24%+)')
        elif ir >= 18:
            score += 2.0
            factors.append('Moderately high interest rate (18%+)')

    pi = schema.penalty_interest.value
    if pi and pi >= 36:
        score += 2.0
        factors.append('Severe penalty interest rate (36%+)')

    if schema.prepayment_penalty.value:
        score += 1.0
        factors.append('Early repayment is penalised')

    if schema.collateral.present:
        score += 2.0
        factors.append('Asset seizure risk on default')

    if len(schema.default_events) >= 3:
        score += 1.5
        factors.append('High number of default triggers')

    score = max(0.0, min(10.0, score))

    return {
        'score': round(score, 1),
        'factors': factors,
    }


def validate_extraction(
    schema: LoanAgreementSchema,
    contract_text: str,
) -> dict:
    entity_results = {}

    fields_to_validate = {
        'loan_amount': schema.loan_amount.value,
        'interest_rate': schema.interest_rate.value,
        'repayment_duration': schema.repayment_duration.value,
        'monthly_payment': schema.monthly_payment.value,
        'total_cost': schema.total_cost.value,
        'late_fee': schema.late_fee.value,
        'processing_fee': schema.processing_fee.value,
        'penalty_interest': schema.penalty_interest.value,
    }

    source_clauses = {
        'loan_amount': schema.loan_amount.source_clause or '',
        'interest_rate': schema.interest_rate.source_clause or '',
        'repayment_duration': schema.repayment_duration.source_clause or '',
        'monthly_payment': schema.monthly_payment.source_clause or '',
        'total_cost': schema.total_cost.source_clause or '',
        'late_fee': schema.late_fee.source_clause or '',
        'processing_fee': schema.processing_fee.source_clause or '',
        'penalty_interest': schema.penalty_interest.source_clause or '',
    }

    for field_name, value in fields_to_validate.items():
        if value is None:
            continue

        hallucination = check_hallucination(str(value), contract_text)
        confidence = calculate_confidence(
            field_name,
            value,
            source_clauses[field_name],
            hallucination['similarity'],
        )

        flag = None
        if not hallucination['is_verified']:
            flag = 'Could not verify this value in the source contract'
        elif confidence < settings.CONFIDENCE_THRESHOLD:
            flag = 'Low confidence — please verify manually'

        entity_results[field_name] = {
            'value': value,
            'source_clause': source_clauses[field_name] or None,
            'confidence': confidence,
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

    mp = schema.monthly_payment.value
    rd = schema.repayment_duration.value
    la = schema.loan_amount.value
    ir = schema.interest_rate.value

    total_repayment = (mp * rd) if mp and rd else None
    total_interest = (total_repayment - la) if total_repayment and la else None
    eff_rate = (total_interest / la * 100) if total_interest and la else None

    financial_summary = {
        'total_repayment': total_repayment,
        'total_interest': total_interest,
        'effective_interest_pct': round(eff_rate, 2) if eff_rate else None,
    }

    default_events = [
        {'trigger': e.trigger, 'source_clause': e.source_clause}
        for e in schema.default_events
    ]

    return {
        'entities': entity_results,
        'math_check': math_check,
        'financial_summary': financial_summary,
        'risk_analysis': risk,
        'default_events': default_events,
    }