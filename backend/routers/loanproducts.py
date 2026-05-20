from fastapi import APIRouter, HTTPException

router = APIRouter(tags=['loanproducts'])


@router.get('/loanproducts')
async def list_loan_products():
    # Stub — Fineract connector wired in LMS-11
    return []


@router.get('/loanproducts/{product_id}')
async def get_loan_product(product_id: int):
    # Stub — Fineract connector wired in LMS-11
    raise HTTPException(status_code=503, detail='Fineract not configured yet')
