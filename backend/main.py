from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from config import settings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import sys


MAX_REQUEST_BODY_BYTES = 1_048_576  # 1MB


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject request bodies larger than MAX_REQUEST_BODY_BYTES."""

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_BODY_BYTES:
            return JSONResponse(
                status_code=413,
                content={"detail": f"Request body too large. Maximum {MAX_REQUEST_BODY_BYTES // 1024}KB."},
            )
        return await call_next(request)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    environment = os.getenv('ENVIRONMENT', 'development')
    logger.info("🚀 Starting Mifos Loan Summarizer API")
    logger.info(f"Environment: {environment}")
    logger.info(f"LLM Primary Provider: {settings.LLM_PRIMARY}")
    logger.info(f"LLM Model: {settings.LLM_MODEL}")
    logger.info(f"API Authentication: {'ENABLED' if settings.API_KEY else 'DISABLED'}")
    yield
    logger.info("🛑 Shutting down Mifos Loan Summarizer API")


app = FastAPI(
    title='Mifos Loan Summarizer',
    description='LLM-powered loan agreement summarization for Mifos X',
    version='0.1.0',
    lifespan=lifespan,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://localhost:3000', 'http://localhost', 'http://localhost:80'],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=['Content-Type', 'X-API-Key', 'Accept'],
)
app.add_middleware(RequestSizeLimitMiddleware)

from routers import analysis, loanproducts, health, providers, simulator

app.include_router(analysis.router)
app.include_router(loanproducts.router)
app.include_router(health.router)
app.include_router(providers.router)
app.include_router(simulator.router)


@app.get('/')
async def root():
    return {'message': 'Mifos Loan Summarizer API', 'docs': '/docs'}