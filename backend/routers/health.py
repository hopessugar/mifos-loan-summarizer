from fastapi import APIRouter
from config import settings
from services.fineract_service import check_fineract_health

router = APIRouter(tags=['health'])


@router.get('/health')
async def health_check():
    fineract_status = await check_fineract_health()
    
    # Determine if the LLM provider is properly configured
    # Ollama is a local provider that doesn't need an API key — just connectivity
    is_ollama = settings.LLM_PRIMARY == 'ollama'
    provider_configured = bool(
        settings.GEMINI_API_KEY
        or settings.GROQ_API_KEY
        or settings.CEREBRAS_API_KEY
        or settings.HF_TOKEN
        or is_ollama  # Ollama doesn't need an API key
    )
    
    response = {
        'status': 'ok',
        'llm_provider': settings.LLM_PRIMARY,
        'llm_model': settings.OLLAMA_MODEL if is_ollama else settings.LLM_MODEL,
        'provider_configured': provider_configured,
        'fineract_reachable': fineract_status['reachable'],
        'fineract_url': settings.FINERACT_URL or 'not configured',
        'fineract_status': fineract_status,
    }
    
    # Add detailed Ollama status when it's the active provider
    if is_ollama:
        try:
            from providers.registry import ProviderRegistry
            provider = ProviderRegistry.get('ollama')
            if hasattr(provider, 'health_check_detailed'):
                response['ollama_status'] = provider.health_check_detailed()
        except Exception as e:
            response['ollama_status'] = {
                'running': False,
                'error': str(e),
            }
    
    return response