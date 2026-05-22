from fastapi import APIRouter, HTTPException
from backend.schemas.request import ContractRequest
from backend.schemas.response import AnalysisResponse
from backend.services.ai_service import analyse_contract

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
        else:
            raise HTTPException(
                status_code=503,
                detail='Mifos X integration not yet configured. Use text input.',
            )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))