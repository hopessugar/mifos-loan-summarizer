from fastapi import APIRouter, HTTPException
from backend.schemas.request import ContractRequest
from backend.schemas.response import AnalysisResponse
from backend.services.ai_service import analyse_contract
from backend.services.fineract_service import get_product_as_text

router = APIRouter(tags=['analysis'])


@router.post('/analyze', response_model=AnalysisResponse)
async def analyze_contract(request: ContractRequest):
    try:
        if request.text:
            result = await analyse_contract(
                text=request.text,
                language=request.language,
                provider_override=request.provider,
            )
            return result

        elif request.loan_product_id:
            try:
                text = await get_product_as_text(request.loan_product_id)
            except Exception:
                raise HTTPException(
                    status_code=503,
                    detail='Cannot connect to Mifos X. Use manual paste instead.',
                )
            result = await analyse_contract(
                text=text,
                language=request.language,
                provider_override=request.provider,
            )
            return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))