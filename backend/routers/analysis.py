from fastapi import APIRouter, HTTPException
from backend.schemas.request import ContractRequest
from backend.schemas.response import AnalysisResponse

router = APIRouter(tags=['analysis'])


@router.post('/analyze', response_model=AnalysisResponse)
async def analyze_contract(request: ContractRequest):
    # Stub — full pipeline wired in LMS-6
    return AnalysisResponse(
        summary='Pipeline not yet implemented.',
        provider_used='stub',
        segment_count=0,
    )
