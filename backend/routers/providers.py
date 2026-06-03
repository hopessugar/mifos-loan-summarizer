from fastapi import APIRouter, Depends
from providers.registry import ProviderRegistry
from auth import verify_api_key

router = APIRouter(tags=['providers'])


@router.get('/providers', dependencies=[Depends(verify_api_key)])
async def list_providers():
    return ProviderRegistry.list_all()