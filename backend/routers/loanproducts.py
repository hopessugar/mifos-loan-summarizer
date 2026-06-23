from fastapi import APIRouter, HTTPException, Depends
from services.fineract_service import list_loan_products, get_product_as_text, invalidate_products_cache
from auth import verify_api_key
import httpx
import logging

router = APIRouter(tags=['loanproducts'])
logger = logging.getLogger(__name__)


@router.get('/loanproducts', dependencies=[Depends(verify_api_key)])
async def list_products():
    try:
        return await list_loan_products()
    except httpx.HTTPStatusError as e:
        logger.error(f'Fineract API error: {e.response.status_code}')
        if e.response.status_code == 401:
            raise HTTPException(
                status_code=503,
                detail='Authentication failed with Mifos X. Check FINERACT_USER and FINERACT_PASSWORD.',
            )
        raise HTTPException(
            status_code=503,
            detail=f'Mifos X returned HTTP {e.response.status_code}. Check Fineract configuration.',
        )
    except (httpx.TimeoutException, httpx.ConnectError):
        raise HTTPException(
            status_code=503,
            detail='Cannot connect to Mifos X. The server may be down or unreachable.',
        )
    except Exception as e:
        logger.error(f'Unexpected error listing products: {e}')
        raise HTTPException(
            status_code=503,
            detail='Cannot connect to Mifos X. Use manual paste instead.',
        )


@router.get('/loanproducts/{product_id}', dependencies=[Depends(verify_api_key)])
async def get_product(product_id: int):
    try:
        text = await get_product_as_text(product_id)
        return {'text': text}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f'Loan product {product_id} not found in Mifos X.',
            )
        raise HTTPException(
            status_code=503,
            detail=f'Mifos X returned HTTP {e.response.status_code}.',
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail='Cannot connect to Mifos X. Use manual paste instead.',
        )


@router.post('/loanproducts/refresh', dependencies=[Depends(verify_api_key)])
async def refresh_products():
    """Invalidate the loan products cache and fetch fresh data."""
    invalidate_products_cache()
    try:
        products = await list_loan_products()
        return {
            'message': f'Cache refreshed. {len(products)} products loaded.',
            'products': products,
        }
    except Exception as e:
        logger.error(f'Failed to refresh products: {e}')
        raise HTTPException(
            status_code=503,
            detail='Cache cleared but failed to fetch fresh products from Mifos X.',
        )