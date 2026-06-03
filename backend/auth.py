"""
Authentication module for API key verification.

Provides FastAPI security dependencies for protecting endpoints with API key authentication.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from config import settings

# Define the header name for API key
API_KEY_HEADER = APIKeyHeader(name=settings.API_KEY_HEADER_NAME, auto_error=False)


async def verify_api_key(api_key: str | None = Security(API_KEY_HEADER)) -> str:
    """
    Verify API key from request header.
    
    Args:
        api_key: API key from X-API-Key header (or configured header name)
    
    Returns:
        str: The validated API key
    
    Raises:
        HTTPException: 401 if API key is missing or invalid
    
    Usage:
        @router.post('/protected', dependencies=[Depends(verify_api_key)])
        async def protected_endpoint():
            return {'message': 'Access granted'}
    """
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
    """
    Return list of endpoints that should remain public (no authentication required).
    
    Public endpoints:
    - / (root) - API discovery
    - /health - Health checks for monitoring tools
    - /docs - API documentation (can be restricted in production if needed)
    - /openapi.json - OpenAPI schema
    """
    return ['/', '/health', '/docs', '/openapi.json', '/redoc']
