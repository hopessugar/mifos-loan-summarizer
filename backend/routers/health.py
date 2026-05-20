from fastapi import APIRouter
from backend.config import settings
from backend.providers.registry import ProviderRegistry

router = APIRouter(tags=['health'])


@router.get('/health')
async def health_check():
    provider = ProviderRegistry.get()
    return {
        'status': 'ok',
        'llm_provider': settings.LLM_PRIMARY,
        'llm_model': settings.LLM_MODEL,
        'provider_healthy': provider.health_check(),
        'fineract_url': settings.FINERACT_URL or 'not configured',
    }