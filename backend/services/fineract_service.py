import httpx
import base64
from backend.config import settings


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
    try:
        async with httpx.AsyncClient(verify=False) as client:
            r = await client.get(
                f'{settings.FINERACT_URL}/api/v1/loanproducts',
                headers=_auth_headers(),
                timeout=8.0,
            )
            r.raise_for_status()
            return [{'id': p['id'], 'name': p['name']} for p in r.json()]
    except Exception as e:
        print(f'Fineract list_loan_products failed: {e}')
        raise


async def get_product_as_text(product_id: int) -> str:
    try:
        async with httpx.AsyncClient(verify=False) as client:
            r = await client.get(
                f'{settings.FINERACT_URL}/api/v1/loanproducts/{product_id}',
                headers=_auth_headers(),
                timeout=8.0,
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
    try:
        async with httpx.AsyncClient(verify=False) as client:
            r = await client.get(
                f'{settings.FINERACT_URL}/api/v1/loanproducts',
                headers=_auth_headers(),
                timeout=5.0,
            )
            return r.status_code == 200
    except Exception:
        return False