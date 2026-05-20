from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import nltk

from backend.routers import analysis, loanproducts, health, providers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Download NLTK data once on startup
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    yield


app = FastAPI(
    title='Mifos Loan Summarizer',
    description='LLM-powered loan agreement summarization for Mifos X',
    version='0.1.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(analysis.router)
app.include_router(loanproducts.router)
app.include_router(health.router)
app.include_router(providers.router)


@app.get('/')
async def root():
    return {'message': 'Mifos Loan Summarizer API', 'docs': '/docs'}
