import httpx
import base64
from config import settings
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