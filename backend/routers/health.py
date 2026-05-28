from fastapi import APIRouter
from backend.config import settings
from backend.providers.registry import ProviderRegistry
from backend.services.fineract_service import check_fineract_health

router = APIRouter(tags=['health'])


@router.get('/health')
async def health_check():
    provider = ProviderRegistry.get()
    fineract_healthy = await check_fineract_health()
    return {
        'status': 'ok',
        'llm_provider': settings.LLM_PRIMARY,
        'llm_model': settings.LLM_MODEL,
        'provider_healthy': provider.health_check(),
        'fineract_reachable': fineract_healthy,
        'fineract_url': settings.FINERACT_URL or 'not configured',
    }