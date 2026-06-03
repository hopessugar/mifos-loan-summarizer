from fastapi import APIRouter, HTTPException, Depends
from services.fineract_service import list_loan_products, get_product_as_text
from auth import verify_api_key

router = APIRouter(tags=['loanproducts'])


@router.get('/loanproducts', dependencies=[Depends(verify_api_key)])
async def list_products():
    try:
        return await list_loan_products()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail='Cannot connect to Mifos X. Use manual paste instead.',
        )


@router.get('/loanproducts/{product_id}', dependencies=[Depends(verify_api_key)])
async def get_product(product_id: int):
    try:
        text = await get_product_as_text(product_id)
        return {'text': text}
    except Exception:
        raise HTTPException(
            status_code=503,
            detail='Cannot connect to Mifos X. Use manual paste instead.',
        )