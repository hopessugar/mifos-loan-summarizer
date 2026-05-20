from fastapi import APIRouter
from backend.config import settings

router = APIRouter(tags=['providers'])

ALL_PROVIDERS = ['hf_inference', 'ollama', 'groq', 'cerebras']


@router.get('/providers')
async def list_providers():
    return [
        {
            'name': p,
            'active': p == settings.LLM_PRIMARY,
        }
        for p in ALL_PROVIDERS
    ]
