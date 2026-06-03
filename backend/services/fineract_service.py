import httpx
import base64
from config import settings


# Shared HTTP client for Fineract API calls
# Reuses connection pool for better performance
_fineract_client: httpx.AsyncClient | None = None


def _get_ssl_config():
    """
    Determine SSL verification configuration.
    
    Returns:
        - True: Verify using system CA bundle (production default)
        - False: Skip verification (ONLY for development, blocked in production)
        - str: Path to custom CA bundle (for self-signed certs in development)
    """
    if not settings.FINERACT_SSL_VERIFY:
        # This should never happen in production due to Settings validation
        return False
    
    # If custom CA bundle provided, use it
    if settings.FINERACT_CA_BUNDLE:
        import os
        if not os.path.exists(settings.FINERACT_CA_BUNDLE):
            raise FileNotFoundError(
                f'Fineract CA bundle not found: {settings.FINERACT_CA_BUNDLE}'
            )
        return settings.FINERACT_CA_BUNDLE
    
    # Default: use system CA bundle
    return True


def _get_fineract_client() -> httpx.AsyncClient:
    """
    Get or create shared Fineract HTTP client.
    
    Benefits of shared client:
    - Connection pooling (reuses TCP connections)
    - Better performance (~20-50ms faster per request)
    - Centralized SSL configuration
    """
    global _fineract_client
    
    if _fineract_client is None:
        ssl_config = _get_ssl_config()
        _fineract_client = httpx.AsyncClient(
            verify=ssl_config,
            timeout=httpx.Timeout(10.0, connect=5.0),
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


async def list_loan_products() -> list[dict]:
    """
    Fetch list of loan products from Fineract.
    
    Returns:
        List of dicts with 'id' and 'name' keys.
    
    Raises:
        httpx.HTTPError: If Fineract API call fails.
    """
    try:
        client = _get_fineract_client()
        r = await client.get(
            f'{settings.FINERACT_URL}/api/v1/loanproducts',
            headers=_auth_headers(),
        )
        r.raise_for_status()
        return [{'id': p['id'], 'name': p['name']} for p in r.json()]
    except Exception as e:
        print(f'Fineract list_loan_products failed: {e}')
        raise


async def get_product_as_text(product_id: int) -> str:
    """
    Fetch single loan product from Fineract and convert to human-readable text.
    
    Args:
        product_id: Fineract loan product ID.
    
    Returns:
        Human-readable contract text suitable for LLM analysis.
    
    Raises:
        httpx.HTTPError: If Fineract API call fails.
    """
    try:
        client = _get_fineract_client()
        r = await client.get(
            f'{settings.FINERACT_URL}/api/v1/loanproducts/{product_id}',
            headers=_auth_headers(),
        )
        r.raise_for_status()
        d = r.json()
        return _product_to_text(d)
    except Exception as e:
        print(f'Fineract get_product failed: {e}')
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
    """
    Check if Fineract API is reachable and responding.
    
    Returns:
        True if Fineract is healthy, False otherwise.
    
    Note:
        This function does not raise exceptions - returns False on any error.
        Used by health check endpoint which should not fail.
    """
    try:
        client = _get_fineract_client()
        r = await client.get(
            f'{settings.FINERACT_URL}/api/v1/loanproducts',
            headers=_auth_headers(),
        )
        return r.status_code == 200
    except Exception:
        return False