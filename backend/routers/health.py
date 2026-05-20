from fastapi import APIRouter
from backend.config import settings

router = APIRouter(tags=['health'])


@router.get('/health')
async def health_check():
    return {
        'status': 'ok',
        'llm_provider': settings.LLM_PRIMARY,
        'llm_model': settings.LLM_MODEL,
        'fineract_url': settings.FINERACT_URL or 'not configured',
    }
