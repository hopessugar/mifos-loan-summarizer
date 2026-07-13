import httpx
import base64
from config import settings
from pipeline.currency import format_currency
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from functools import lru_cache
import time
import logging

logger = logging.getLogger(__name__)

# Cache timestamp for invalidation
_products_cache_time = 0
_products_cache = None
CACHE_TTL = 300  # 5 minutes


# Shared HTTP client for Fineract API calls
# Reuses connection pool for better performance
_fineract_client: httpx.AsyncClient | None = None


def _get_ssl_config():
    if not settings.FINERACT_SSL_VERIFY:
        return False
    
    if settings.FINERACT_CA_BUNDLE:
        import os
        if not os.path.exists(settings.FINERACT_CA_BUNDLE):
            raise FileNotFoundError(
                f'Fineract CA bundle not found: {settings.FINERACT_CA_BUNDLE}'
            )
        return settings.FINERACT_CA_BUNDLE
    
    return True


def _get_fineract_client() -> httpx.AsyncClient:
    global _fineract_client
    
    if _fineract_client is None:
        ssl_config = _get_ssl_config()
        _fineract_client = httpx.AsyncClient(
            verify=ssl_config,
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
    
    return _fineract_client


def _auth_headers() -> dict:
    token = base64.b64encode(
        f'{settings.FINERACT_USER}:{settings.FINERACT_PASSWORD}'.encode()
    ).decode()
    return {
        'Authorization': f'Basic {token}',
        'Fineract-Platform-TenantId': settings.FINERACT_TENANT,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


def invalidate_products_cache():
    """Clear the cached loan products so the next call fetches fresh data."""
    global _products_cache, _products_cache_time
    _products_cache = None
    _products_cache_time = 0
    logger.info('Fineract products cache invalidated')


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def list_loan_products() -> list[dict]:
    global _products_cache, _products_cache_time
    
    current_time = time.time()
    if _products_cache and (current_time - _products_cache_time) < CACHE_TTL:
        logger.info(f"Returning cached loan products ({len(_products_cache)} items)")
        return _products_cache
    
    url = f'{settings.FINERACT_URL}/api/v1/loanproducts'
    try:
        client = _get_fineract_client()
        logger.info(f'Fetching loan products from: {url}')
        r = await client.get(url, headers=_auth_headers())
        r.raise_for_status()
        products = [{'id': p['id'], 'name': p['name']} for p in r.json()]
        
        _products_cache = products
        _products_cache_time = current_time
        
        logger.info(f'Successfully fetched {len(products)} loan products from Fineract (cached)')
        return products
    except httpx.HTTPStatusError as e:
        logger.error(f'Fineract API returned {e.response.status_code} for {url}: {e.response.text[:200]}')
        raise
    except Exception as e:
        logger.error(f'Fineract list_loan_products failed for {url}: {e}')
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def get_product_as_text(product_id: int) -> str:
    url = f'{settings.FINERACT_URL}/api/v1/loanproducts/{product_id}'
    try:
        client = _get_fineract_client()
        logger.info(f'Fetching loan product {product_id} from: {url}')
        r = await client.get(url, headers=_auth_headers())
        r.raise_for_status()
        d = r.json()
        logger.info(f'Successfully fetched loan product {product_id} from Fineract')
        return _product_to_text(d)
    except httpx.HTTPStatusError as e:
        logger.error(f'Fineract API returned {e.response.status_code} for {url}: {e.response.text[:200]}')
        raise
    except Exception as e:
        logger.error(f'Fineract get_product failed for product_id={product_id} at {url}: {e}')
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def get_product_raw(product_id: int) -> dict:
    """Fetch the full structured JSON for a Fineract loan product.
    
    Returns the raw API response dict — the authoritative source of truth
    for all product fields. No text conversion, no lossy formatting.
    """
    url = f'{settings.FINERACT_URL}/api/v1/loanproducts/{product_id}'
    try:
        client = _get_fineract_client()
        logger.info(f'Fetching raw loan product {product_id} from: {url}')
        r = await client.get(url, headers=_auth_headers())
        r.raise_for_status()
        data = r.json()
        logger.info(f'Successfully fetched raw loan product {product_id} ({data.get("name", "?")})')
        return data
    except httpx.HTTPStatusError as e:
        logger.error(f'Fineract API returned {e.response.status_code} for {url}: {e.response.text[:200]}')
        raise
    except Exception as e:
        logger.error(f'Fineract get_product_raw failed for product_id={product_id} at {url}: {e}')
        raise


def build_schema_from_fineract(data: dict):
    """Build a LoanAgreementSchema directly from Fineract structured JSON.
    
    This bypasses LLM extraction entirely — every value comes directly from
    the Fineract API response, which is the authoritative source. No guessing,
    no inference, no hallucination.
    
    Returns (LoanAgreementSchema, str) — the schema and a text representation
    for summary generation.
    """
    from decimal import Decimal
    from schemas.loan_schema import (
        LoanAgreementSchema, EntityField, InterestField,
        FeeField, CollateralField, RepaymentScheduleField, DefaultEventField,
    )

    product_name = data.get('name', 'Unknown Product')

    # ---- Currency ----
    currency_data = data.get('currency', {})
    currency_code = currency_data.get('code', 'USD') if isinstance(currency_data, dict) else 'USD'
    currency_symbol = currency_data.get('displaySymbol', '$') if isinstance(currency_data, dict) else '$'

    # ---- Principal (loan amount) ----
    # Fineract returns principal as a plain number (the default value)
    principal_val = data.get('principal')
    min_principal = data.get('minPrincipal')
    max_principal = data.get('maxPrincipal')

    principal_source = f'Fineract product "{product_name}": default principal = {principal_val} {currency_code}'
    if min_principal is not None and max_principal is not None:
        principal_source += f' (range: {min_principal} to {max_principal} {currency_code})'

    loan_amount = EntityField(
        value=Decimal(str(principal_val)) if principal_val is not None else None,
        source_clause=principal_source if principal_val is not None else None,
        confidence=0.99,
        extraction_method='fineract_api',
        is_verified=True,
        similarity=1.0,
    )

    # ---- Interest Rate ----
    # Fineract provides both interestRatePerPeriod and annualInterestRate
    # ALWAYS use annualInterestRate for consistency (our schema expects annual %)
    annual_rate = data.get('annualInterestRate')
    rate_per_period = data.get('interestRatePerPeriod')
    min_rate = data.get('minInterestRatePerPeriod')
    max_rate = data.get('maxInterestRatePerPeriod')

    # Interest rate frequency tells us whether rate_per_period is monthly/yearly
    rate_freq_data = data.get('interestRateFrequencyType', {})
    rate_freq_code = rate_freq_data.get('code', '') if isinstance(rate_freq_data, dict) else ''
    rate_freq_label = rate_freq_data.get('value', '') if isinstance(rate_freq_data, dict) else ''

    # Interest type: declining balance vs flat
    interest_type_data = data.get('interestType', {})
    interest_type_code = interest_type_data.get('code', '') if isinstance(interest_type_data, dict) else ''
    interest_type_label = interest_type_data.get('value', '') if isinstance(interest_type_data, dict) else ''

    # Map Fineract interestType codes to our schema types
    if 'flat' in interest_type_code.lower():
        schema_interest_type = 'flat'
    elif 'declining' in interest_type_code.lower():
        schema_interest_type = 'reducing'
    else:
        schema_interest_type = interest_type_label or None

    interest_source = f'Fineract product "{product_name}": annual interest rate = {annual_rate}% per annum'
    if rate_per_period is not None and annual_rate != rate_per_period:
        interest_source += f' (rate per period = {rate_per_period}% {rate_freq_label})'
    interest_source += f', interest type = {interest_type_label}'
    if min_rate is not None and max_rate is not None:
        interest_source += f' (rate range: {min_rate}% to {max_rate}%)'

    interest_rate = InterestField(
        value=Decimal(str(annual_rate)) if annual_rate is not None else None,
        type=schema_interest_type,
        source_clause=interest_source if annual_rate is not None else None,
        confidence=0.99,
        extraction_method='fineract_api',
        is_verified=True,
        similarity=1.0,
    )

    # ---- Repayment Duration ----
    num_repayments = data.get('numberOfRepayments')
    min_repayments = data.get('minNumberOfRepayments')
    max_repayments = data.get('maxNumberOfRepayments')
    repay_every = data.get('repaymentEvery', 1)

    repay_freq_data = data.get('repaymentFrequencyType', {})
    repay_freq_label = repay_freq_data.get('value', 'Months') if isinstance(repay_freq_data, dict) else 'Months'
    repay_freq_code = repay_freq_data.get('code', '') if isinstance(repay_freq_data, dict) else ''

    # Calculate total duration in months
    # If frequency is months, total = num_repayments * repay_every
    # If frequency is weeks, convert: total_months = (num_repayments * repay_every * 7) / 30
    if 'weeks' in repay_freq_code.lower():
        duration_months = int((num_repayments * repay_every * 7) / 30) if num_repayments else None
    else:
        duration_months = num_repayments * repay_every if num_repayments else None

    duration_source = f'Fineract product "{product_name}": {num_repayments} repayments every {repay_every} {repay_freq_label.lower()}'
    if min_repayments is not None and max_repayments is not None:
        duration_source += f' (range: {min_repayments} to {max_repayments})'

    repayment_duration = EntityField(
        value=Decimal(str(duration_months)) if duration_months is not None else None,
        source_clause=duration_source if num_repayments is not None else None,
        confidence=0.99,
        extraction_method='fineract_api',
        is_verified=True,
        similarity=1.0,
    )

    # ---- Payment Frequency ----
    if 'weeks' in repay_freq_code.lower():
        if repay_every == 2:
            payment_frequency = 'fortnightly'
        else:
            payment_frequency = 'weekly'
    else:
        payment_frequency = 'monthly'

    # ---- Charges → Fee Fields ----
    # Fineract charges have chargeTimeType and chargeCalculationType
    # We map them to the correct fee fields based on their type
    processing_fee = FeeField()
    late_fee = FeeField()
    late_payment_interest = FeeField()
    penalty_interest = FeeField()
    prepayment_penalty = FeeField()
    insurance_fee = FeeField()
    administrative_fee = FeeField()
    other_fee = FeeField()

    for charge in data.get('charges', []):
        charge_name = charge.get('name', '')
        charge_amount = charge.get('amount')
        if charge_amount is None:
            continue

        charge_time_type = charge.get('chargeTimeType', {})
        charge_time_code = charge_time_type.get('code', '') if isinstance(charge_time_type, dict) else ''
        charge_time_label = charge_time_type.get('value', '') if isinstance(charge_time_type, dict) else ''

        charge_calc_type = charge.get('chargeCalculationType', {})
        charge_calc_code = charge_calc_type.get('code', '') if isinstance(charge_calc_type, dict) else ''
        charge_calc_label = charge_calc_type.get('value', '') if isinstance(charge_calc_type, dict) else ''

        charge_source = (
            f'Fineract charge "{charge_name}": {charge_amount} {currency_code}, '
            f'timing = {charge_time_label}, calculation = {charge_calc_label}'
        )

        is_percentage = 'percent' in charge_calc_code.lower()
        fee_base = f'{charge_calc_label}' if charge_calc_label else ('percentage' if is_percentage else 'flat fee')

        fee_field = FeeField(
            value=Decimal(str(charge_amount)),
            logic=f'{charge_name} ({charge_calc_label})',
            base=fee_base,
            source_clause=charge_source,
            confidence=0.99,
            extraction_method='fineract_api',
            is_verified=True,
            similarity=1.0,
        )

        # Classify by Fineract charge time type
        charge_name_lower = charge_name.lower()
        if 'disbursement' in charge_time_code.lower() or 'processing' in charge_name_lower:
            processing_fee = fee_field
        elif 'overdue' in charge_time_code.lower() or 'late' in charge_name_lower:
            if is_percentage:
                late_payment_interest = fee_field
            else:
                late_fee = fee_field
        elif 'prepayment' in charge_name_lower or 'foreclosure' in charge_name_lower:
            prepayment_penalty = fee_field
        elif 'penalty' in charge_name_lower:
            penalty_interest = fee_field
        elif 'insurance' in charge_name_lower:
            insurance_fee = fee_field
        elif 'admin' in charge_name_lower or 'administrative' in charge_name_lower:
            administrative_fee = fee_field
        else:
            # For unclassified charges, check charge time type
            if 'disbursement' in charge_time_code.lower():
                processing_fee = fee_field
            elif 'overdue' in charge_time_code.lower():
                if is_percentage:
                    penalty_interest = fee_field
                else:
                    late_fee = fee_field
            else:
                other_fee = fee_field

    # ---- Repayment Schedule ----
    repayment_schedule = RepaymentScheduleField(
        frequency=f'Every {repay_every} {repay_freq_label.lower()}',
        installment_amount=None,  # Not known at product level (depends on actual loan)
        start_condition=None,
        due_day=None,
        source_clause=f'Fineract product "{product_name}": repayment every {repay_every} {repay_freq_label.lower()}',
    )

    # ---- Grace Periods (as default events / notes) ----
    default_events = []
    grace_principal = data.get('graceOnPrincipalPayment')
    grace_interest = data.get('graceOnInterestPayment')
    if grace_principal:
        default_events.append(DefaultEventField(
            trigger=f'Grace period on principal: {grace_principal} periods',
            source_clause=f'Fineract product config: graceOnPrincipalPayment = {grace_principal}',
        ))
    if grace_interest:
        default_events.append(DefaultEventField(
            trigger=f'Grace period on interest: {grace_interest} periods',
            source_clause=f'Fineract product config: graceOnInterestPayment = {grace_interest}',
        ))

    # ---- Down Payment (adjusts principal for EMI calculation) ----
    enable_down_payment = data.get('enableDownPayment', False)
    down_payment_pct = data.get('disbursedAmountPercentageForDownPayment')
    net_principal = principal_val  # Default: full principal

    if enable_down_payment and down_payment_pct and principal_val:
        down_payment_amount = principal_val * (down_payment_pct / 100)
        net_principal = principal_val - down_payment_amount

        # Update loan_amount to net principal (after down payment deduction)
        # EMI, total repayment, total interest all depend on this
        loan_amount = EntityField(
            value=Decimal(str(net_principal)),
            source_clause=(
                f'Fineract product "{product_name}": principal {principal_val} {currency_code} '
                f'minus {down_payment_pct}% down payment '
                f'({format_currency(down_payment_amount, currency_code)}) = '
                f'net {format_currency(net_principal, currency_code)}'
            ),
            confidence=0.99,
            extraction_method='fineract_api',
            is_verified=True,
            similarity=1.0,
        )

        default_events.append(DefaultEventField(
            trigger=(
                f'Down payment required: {down_payment_pct}% of disbursed amount '
                f'({format_currency(down_payment_amount, currency_code)})'
            ),
            source_clause=(
                f'Fineract product config: enableDownPayment = true, '
                f'disbursedAmountPercentageForDownPayment = {down_payment_pct}%'
            ),
        ))

    # ---- Interest Calculation Details ----
    interest_calc_data = data.get('interestCalculationPeriodType', {})
    interest_calc_label = interest_calc_data.get('value', '') if isinstance(interest_calc_data, dict) else ''

    # ---- Transaction Processing Strategy ----
    txn_strategy_name = data.get('transactionProcessingStrategyName', '')

    # ---- Arrears Tolerance ----
    arrears_tolerance = data.get('inArrearsTolerance')
    if arrears_tolerance and arrears_tolerance > 0:
        default_events.append(DefaultEventField(
            trigger=f'Arrears tolerance: {arrears_tolerance} days before loan is flagged as overdue',
            source_clause=f'Fineract product config: inArrearsTolerance = {arrears_tolerance}',
        ))

    # ---- Grace on Arrears Ageing ----
    grace_arrears = data.get('graceOnArrearsAgeing')
    if grace_arrears and grace_arrears > 0:
        default_events.append(DefaultEventField(
            trigger=f'Grace on arrears ageing: {grace_arrears} days',
            source_clause=f'Fineract product config: graceOnArrearsAgeing = {grace_arrears}',
        ))

    # ---- Interest Recalculation ----
    is_recalc = data.get('isInterestRecalculationEnabled', False)

    # ---- Multi-disbursement / Tranche Loans ----
    multi_disburse = data.get('multiDisburseLoan', False)
    max_tranches = data.get('maxTrancheCount')
    if multi_disburse:
        tranche_text = (
            f'Multi-disbursement loan (max {max_tranches} tranches)'
            if max_tranches
            else 'Multi-disbursement loan enabled'
        )
        default_events.append(DefaultEventField(
            trigger=tranche_text,
            source_clause='Fineract product config: multiDisburseLoan = true',
        ))

    # ---- Overdue Day Configuration ----
    due_days = data.get('dueDaysForRepaymentEvent')
    overdue_days = data.get('overDueDaysForRepaymentEvent')
    if due_days and due_days > 0:
        default_events.append(DefaultEventField(
            trigger=f'Repayment considered due after {due_days} days',
            source_clause=f'Fineract product config: dueDaysForRepaymentEvent = {due_days}',
        ))
    if overdue_days and overdue_days > 0:
        default_events.append(DefaultEventField(
            trigger=f'Repayment considered overdue after {overdue_days} days',
            source_clause=f'Fineract product config: overDueDaysForRepaymentEvent = {overdue_days}',
        ))

    # ---- Build Schema ----
    schema = LoanAgreementSchema(
        loan_amount=loan_amount,
        interest_rate=interest_rate,
        repayment_duration=repayment_duration,
        monthly_payment=EntityField(),  # Not available at product level
        total_cost=EntityField(),       # Will be calculated by financial_calculator
        payment_frequency=payment_frequency,
        payment_due_day=None,
        repayment_start_date=None,
        currency=currency_code,
        late_fee=late_fee,
        late_payment_interest=late_payment_interest,
        penalty_interest=penalty_interest,
        prepayment_penalty=prepayment_penalty,
        processing_fee=processing_fee,
        insurance_fee=insurance_fee,
        administrative_fee=administrative_fee,
        other_fee=other_fee,
        collateral=CollateralField(),
        repayment_schedule=repayment_schedule,
        default_events=default_events,
    )

    # ---- Build text representation for summary generation ----
    # This is ONLY used by the LLM to generate the human-readable summary
    text_lines = [
        f'FINERACT LOAN PRODUCT: {product_name}',
        f'Product ID: {data.get("id")}',
        '',
    ]

    # Principal — show both gross and net if down payment applies
    if net_principal != principal_val:
        text_lines.append(
            f'Loan Principal: {principal_val} {currency_code} '
            f'(net after {down_payment_pct}% down payment: {net_principal} {currency_code})'
        )
    else:
        text_lines.append(f'Loan Principal: {principal_val} {currency_code}')

    if min_principal is not None and max_principal is not None:
        text_lines.append(f'Principal Range: {min_principal} to {max_principal} {currency_code}')

    text_lines.extend([
        f'Annual Interest Rate: {annual_rate}% per annum',
        f'Interest Type: {interest_type_label}',
        f'Interest Calculation: {rate_freq_label}',
    ])
    if interest_calc_label:
        text_lines.append(f'Interest Calculation Period: {interest_calc_label}')
    if min_rate is not None and max_rate is not None:
        text_lines.append(f'Interest Rate Range: {min_rate}% to {max_rate}%')

    text_lines.extend([
        f'Number of Repayments: {num_repayments}',
        f'Repayment Frequency: Every {repay_every} {repay_freq_label.lower()}',
        f'Total Duration: {duration_months} months',
    ])
    if min_repayments is not None and max_repayments is not None:
        text_lines.append(f'Repayment Range: {min_repayments} to {max_repayments} instalments')

    amort_data = data.get('amortizationType', {})
    amort_label = amort_data.get('value', '') if isinstance(amort_data, dict) else ''
    if amort_label:
        text_lines.append(f'Amortization: {amort_label}')

    if txn_strategy_name:
        text_lines.append(f'Payment Application Order: {txn_strategy_name}')

    if is_recalc:
        text_lines.append('Interest recalculation is enabled (interest adjusts on early/partial payments)')

    if grace_principal:
        text_lines.append(f'Grace Period on Principal: {grace_principal} periods')
    if grace_interest:
        text_lines.append(f'Grace Period on Interest: {grace_interest} periods')
    if arrears_tolerance and arrears_tolerance > 0:
        text_lines.append(f'Arrears Tolerance: {arrears_tolerance} days before flagging as overdue')

    for charge in data.get('charges', []):
        cname = charge.get('name', 'Charge')
        camount = charge.get('amount', '')
        calc_type_data = charge.get('chargeCalculationType', {})
        calc_label = calc_type_data.get('value', '') if isinstance(calc_type_data, dict) else ''
        text_lines.append(f'CHARGE: {cname} — {camount} ({calc_label})')

    if enable_down_payment and down_payment_pct:
        text_lines.append(
            f'Down Payment: {down_payment_pct}% of disbursed amount '
            f'({format_currency(principal_val * (down_payment_pct / 100), currency_code)})'
        )

    product_text = '\n'.join(text_lines)

    logger.info(
        f'Built schema from Fineract product "{product_name}": '
        f'principal={net_principal} (gross={principal_val}), rate={annual_rate}%, '
        f'duration={duration_months}mo, charges={len(data.get("charges", []))}'
    )

    return schema, product_text


def _safe_get(d: dict, key: str, fallback=None):
    """Get a value that might be a nested dict with 'defaultValue'/'value' or a plain value."""
    val = d.get(key, fallback)
    if isinstance(val, dict):
        return val.get('defaultValue') or val.get('value') or fallback
    return val


def _product_to_text(d: dict) -> str:
    lines = [f'LOAN PRODUCT: {d.get("name", "Unknown")}', '']

    # Principal — handle both {defaultValue: X} and plain number formats
    principal_raw = d.get('principal', {})
    if isinstance(principal_raw, dict):
        principal_val = principal_raw.get('defaultValue') or principal_raw.get('value')
    else:
        principal_val = principal_raw
    
    if principal_val:
        currency_raw = d.get('currency', {})
        if isinstance(currency_raw, dict):
            currency = currency_raw.get('code') or currency_raw.get('displaySymbol', 'INR')
        else:
            currency = currency_raw or 'INR'
        lines.append(
            f'The loan principal amount is {principal_val} {currency}.'
        )

    # Interest rate
    interest_raw = d.get('interestRatePerPeriod', {})
    if isinstance(interest_raw, dict):
        interest_val = interest_raw.get('value') or interest_raw.get('defaultValue')
    else:
        interest_val = interest_raw
    
    interest_type_raw = d.get('interestType', {})
    interest_type = interest_type_raw.get('value', '') if isinstance(interest_type_raw, dict) else str(interest_type_raw or '')
    
    freq_raw = d.get('interestRatePeriodFrequencyType', {})
    freq = freq_raw.get('value', 'per annum') if isinstance(freq_raw, dict) else str(freq_raw or 'per annum')
    
    if interest_val is not None:
        lines.append(
            f'The interest rate is {interest_val}% {freq}. '
            f'Interest calculation method: {interest_type}.'
        )

    # Repayment schedule
    repay_every = d.get('repaymentEvery')
    repay_freq_raw = d.get('repaymentFrequencyType', {})
    repay_freq = repay_freq_raw.get('value', '') if isinstance(repay_freq_raw, dict) else str(repay_freq_raw or '')
    
    num_repayments = d.get('numberOfRepayments')
    if isinstance(num_repayments, dict):
        num_repayments = num_repayments.get('defaultValue') or num_repayments.get('value')
    
    if repay_every and num_repayments:
        lines.append(
            f'Repayment is due every {repay_every} {repay_freq} '
            f'for {num_repayments} instalments.'
        )

    # Charges
    for charge in d.get('charges', []):
        name = charge.get('name', 'Charge')
        amount = charge.get('amount', '')
        calc_type_raw = charge.get('chargeCalculationType', {})
        calc_type = calc_type_raw.get('value', '') if isinstance(calc_type_raw, dict) else str(calc_type_raw or '')
        lines.append(f'CHARGE: {name} — {amount} ({calc_type}).')

    # Amortization
    amort_raw = d.get('amortizationType', {})
    amort = amort_raw.get('value', '') if isinstance(amort_raw, dict) else str(amort_raw or '')
    if amort:
        lines.append(f'Amortization type: {amort}.')

    # Grace periods (additional detail from Fineract)
    grace_principal = d.get('graceOnPrincipalPayment')
    grace_interest = d.get('graceOnInterestPayment')
    if grace_principal:
        lines.append(f'Grace period on principal: {grace_principal} periods.')
    if grace_interest:
        lines.append(f'Grace period on interest: {grace_interest} periods.')

    return '\n'.join(lines)


async def check_fineract_health() -> dict:
    """Check Fineract connectivity. Returns dict with status details."""
    url = f'{settings.FINERACT_URL}/api/v1/loanproducts'
    try:
        client = _get_fineract_client()
        r = await client.get(url, headers=_auth_headers())
        if r.status_code == 200:
            product_count = len(r.json()) if r.headers.get('content-type', '').startswith('application/json') else 0
            return {
                'reachable': True,
                'status_code': r.status_code,
                'product_count': product_count,
                'error': None,
            }
        else:
            return {
                'reachable': True,
                'status_code': r.status_code,
                'product_count': 0,
                'error': f'HTTP {r.status_code}: {r.text[:100]}',
            }
    except httpx.ConnectError as e:
        return {
            'reachable': False,
            'status_code': None,
            'product_count': 0,
            'error': f'Connection failed: {e}',
        }
    except httpx.TimeoutException:
        return {
            'reachable': False,
            'status_code': None,
            'product_count': 0,
            'error': 'Connection timed out',
        }
    except Exception as e:
        return {
            'reachable': False,
            'status_code': None,
            'product_count': 0,
            'error': str(e),
        }