from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from config import settings

API_KEY_HEADER = APIKeyHeader(name=settings.API_KEY_HEADER_NAME, auto_error=False)


async def verify_api_key(api_key: str | None = Security(API_KEY_HEADER)) -> str:
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Missing API key. Provide valid API key in {settings.API_KEY_HEADER_NAME} header.',
            headers={'WWW-Authenticate': 'ApiKey'},
        )
    
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid API key. Check your credentials.',
            headers={'WWW-Authenticate': 'ApiKey'},
        )
    
    return api_key


def get_public_endpoints() -> list[str]:
    return ['/', '/health', '/docs', '/openapi.json', '/redoc']
