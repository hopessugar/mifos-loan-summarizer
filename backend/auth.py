import hmac
import logging

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from config import settings

logger = logging.getLogger(__name__)

API_KEY_HEADER = APIKeyHeader(name=settings.API_KEY_HEADER_NAME, auto_error=False)


async def verify_api_key(api_key: str | None = Security(API_KEY_HEADER)) -> str:
    """Verify API key from request header.
    
    Security rules:
    - If API_KEY is not configured (empty): auth is DISABLED (dev mode only).
    - If API_KEY is configured: all requests must provide a valid key.
    - Uses hmac.compare_digest() to prevent timing attacks.
    """
    # Dev mode: no API key configured → skip auth
    if not settings.API_KEY:
        return "dev-mode"

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Missing API key. Provide valid API key in {settings.API_KEY_HEADER_NAME} header.',
            headers={'WWW-Authenticate': 'ApiKey'},
        )

    # Timing-safe comparison to prevent side-channel attacks
    if not hmac.compare_digest(api_key, settings.API_KEY):
        logger.warning("Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid API key. Check your credentials.',
            headers={'WWW-Authenticate': 'ApiKey'},
        )

    return api_key
