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
    }


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
    
    try:
        client = _get_fineract_client()
        r = await client.get(
            f'{settings.FINERACT_URL}/api/v1/loanproducts',
            headers=_auth_headers(),
        )
        r.raise_for_status()
        products = [{'id': p['id'], 'name': p['name']} for p in r.json()]
        
        _products_cache = products
        _products_cache_time = current_time
        
        logger.info(f'Successfully fetched {len(products)} loan products from Fineract (cached)')
        return products
    except Exception as e:
        logger.error(f'Fineract list_loan_products failed: {e}')
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def get_product_as_text(product_id: int) -> str:
    try:
        client = _get_fineract_client()
        r = await client.get(
            f'{settings.FINERACT_URL}/api/v1/loanproducts/{product_id}',
            headers=_auth_headers(),
        )
        r.raise_for_status()
        d = r.json()
        logger.info(f'Successfully fetched loan product {product_id} from Fineract')
        return _product_to_text(d)
    except Exception as e:
        logger.error(f'Fineract get_product failed for product_id={product_id}: {e}')
        raise


def _product_to_text(d: dict) -> str:
    lines = [f'LOAN PRODUCT: {d.get("name", "Unknown")}', '']

    principal = d.get('principal', {})
    if principal.get('defaultValue'):
        currency = d.get('currency', {}).get('code', 'INR')
        lines.append(
            f'The loan principal amount is {principal["defaultValue"]} {currency}.'
        )

    interest = d.get('interestRatePerPeriod', {})
    interest_type = d.get('interestType', {}).get('value', '')
    freq = d.get('interestRatePeriodFrequencyType', {}).get('value', 'per annum')
    if interest.get('value') is not None:
        lines.append(
            f'The interest rate is {interest["value"]}% {freq}. '
            f'Interest calculation method: {interest_type}.'
        )

    repay_every = d.get('repaymentEvery')
    repay_freq = d.get('repaymentFrequencyType', {}).get('value', '')
    num_repayments = d.get('numberOfRepayments')
    if repay_every and num_repayments:
        lines.append(
            f'Repayment is due every {repay_every} {repay_freq} '
            f'for {num_repayments} instalments.'
        )

    for charge in d.get('charges', []):
        name = charge.get('name', 'Charge')
        amount = charge.get('amount', '')
        calc_type = charge.get('chargeCalculationType', {}).get('value', '')
        lines.append(f'CHARGE: {name} — {amount} ({calc_type}).')

    amort = d.get('amortizationType', {}).get('value', '')
    if amort:
        lines.append(f'Amortization type: {amort}.')

    return '\n'.join(lines)


async def check_fineract_health() -> bool:
    try:
        client = _get_fineract_client()
        r = await client.get(
            f'{settings.FINERACT_URL}/api/v1/loanproducts',
            headers=_auth_headers(),
        )
        return r.status_code == 200
    except Exception:
        return False