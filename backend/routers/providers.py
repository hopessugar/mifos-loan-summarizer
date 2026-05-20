from fastapi import APIRouter
from backend.providers.registry import ProviderRegistry

router = APIRouter(tags=['providers'])


@router.get('/providers')
async def list_providers():
    return ProviderRegistry.list_all()