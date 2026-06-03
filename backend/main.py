from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # NLTK data is pre-downloaded in Docker image
    # Skip download to avoid startup delays
    yield


app = FastAPI(
    title='Mifos Loan Summarizer',
    description='LLM-powered loan agreement summarization for Mifos X',
    version='0.1.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://localhost:3000', 'http://localhost', 'http://localhost:80'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

from routers import analysis, loanproducts, health, providers

app.include_router(analysis.router)
app.include_router(loanproducts.router)
app.include_router(health.router)
app.include_router(providers.router)


@app.get('/')
async def root():
    return {'message': 'Mifos Loan Summarizer API', 'docs': '/docs'}