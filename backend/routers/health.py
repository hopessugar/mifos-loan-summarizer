from fastapi import APIRouter
from config import settings
from services.fineract_service import check_fineract_health

router = APIRouter(tags=['health'])


@router.get('/health')
async def health_check():
    fineract_healthy = await check_fineract_health()
    return {
        'status': 'ok',
        'llm_provider': settings.LLM_PRIMARY,
        'llm_model': settings.LLM_MODEL,
        'provider_configured': bool(settings.GEMINI_API_KEY or settings.GROQ_API_KEY),
        'fineract_reachable': fineract_healthy,
        'fineract_url': settings.FINERACT_URL or 'not configured',
    }