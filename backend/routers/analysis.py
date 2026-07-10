from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from schemas.request import ContractRequest
from schemas.response import AnalysisResponse
from services.ai_service import analyse_contract
from services.fineract_service import get_product_as_text
from auth import verify_api_key
from exceptions import RateLimitError, ExtractionError
from slowapi import Limiter
from slowapi.util import get_remote_address
import httpx
import logging
import time

router = APIRouter(tags=['analysis'])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post('/analyze', response_model=AnalysisResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
async def analyze_contract(request: Request, contract_request: ContractRequest):
    start_time = time.time()
    
    try:
        if not contract_request.text and not contract_request.loan_product_id:
            raise HTTPException(
                status_code=400,
                detail="Please provide either 'text' (contract text) or 'loan_product_id' (Mifos X product ID)"
            )
        
        if contract_request.text:
            if len(contract_request.text.strip()) < 50:
                raise HTTPException(
                    status_code=400,
                    detail="Contract text is too short. Please provide at least 50 characters for meaningful analysis."
                )
            
            if len(contract_request.text) > 50000:
                raise HTTPException(
                    status_code=400,
                    detail="Contract text is too long. Maximum length is 50,000 characters."
                )
            
            logger.info(f"Analyzing contract: {len(contract_request.text)} chars, language={contract_request.language}")
            result = await analyse_contract(
                text=contract_request.text,
                language=contract_request.language,
                provider_override=contract_request.provider,
            )
            elapsed = time.time() - start_time
            logger.info(f"Analysis complete in {elapsed:.2f}s, provider={result.provider_used}")
            return result

        elif contract_request.loan_product_id:
            if contract_request.loan_product_id <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid product ID. Product ID must be a positive integer."
                )
            
            logger.info(f"Fetching Fineract product: {contract_request.loan_product_id}")
            try:
                text = await get_product_as_text(contract_request.loan_product_id)
                logger.info(f"Analyzing Fineract product {contract_request.loan_product_id}: {len(text)} chars")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Loan product with ID {contract_request.loan_product_id} not found in Mifos X."
                    )
                elif e.response.status_code == 401:
                    raise HTTPException(
                        status_code=503,
                        detail="Authentication failed with Mifos X. Please check Fineract credentials."
                    )
                else:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Mifos X API error: {e.response.status_code}. Please try again later."
                    )
            except (httpx.TimeoutException, httpx.ConnectError):
                raise HTTPException(
                    status_code=503,
                    detail="Cannot connect to Mifos X. The server may be down or unreachable. Please use manual paste instead."
                )
            except Exception as e:
                logger.error(f"Failed to fetch Fineract product {contract_request.loan_product_id}: {e}")
                raise HTTPException(
                    status_code=503,
                    detail='Failed to fetch loan product from Mifos X. Please check your Fineract configuration or use manual paste.'
                )
            
            result = await analyse_contract(
                text=text,
                language=contract_request.language,
                provider_override=contract_request.provider,
            )
            elapsed = time.time() - start_time
            logger.info(f"Fineract analysis complete in {elapsed:.2f}s")
            return result

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input: {str(e)}. Please check your request data."
        )
    except RateLimitError as e:
        logger.warning(f"Rate limit hit: {e}")
        raise HTTPException(
            status_code=429,
            detail=f"LLM API rate limit reached. Please wait {e.retry_after} seconds and try again.",
            headers={"Retry-After": str(e.retry_after)},
        )
    except ExtractionError as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(
            status_code=502,
            detail="All LLM providers failed to extract data. Please try again later.",
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during analysis. Please try again later or contact support if the problem persists."
        )


@router.post('/analyze/pdf', response_model=AnalysisResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
async def analyze_document(
    request: Request,
    file: UploadFile = File(..., description="Document file to analyze (PDF, DOCX, or TXT)"),
    language: str = Form(default='en', description="Output language: 'en' or 'hi'"),
    provider: str | None = Form(default=None, description="LLM provider override"),
):
    """Analyze a loan agreement from an uploaded document.
    
    Supports PDF, DOCX, and TXT files. Extracts text from the uploaded file
    and runs it through the same analysis pipeline as the /analyze endpoint.
    """
    from services.pdf_service import extract_text_from_file, validate_uploaded_file
    
    start_time = time.time()
    
    try:
        # Read file content
        file_bytes = await file.read()
        file_size = len(file_bytes)
        filename = file.filename or 'unknown'
        
        # Validate file metadata
        validation_errors = validate_uploaded_file(
            filename=filename,
            content_type=file.content_type,
            file_size=file_size,
        )
        
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail=" ".join(validation_errors)
            )
        
        # Validate language
        if language not in ('en', 'hi'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language '{language}'. Supported: 'en', 'hi'"
            )
        
        # Extract text from document
        logger.info(f"Extracting text from document: {filename} ({file_size / 1024:.1f}KB)")
        try:
            extracted_text = extract_text_from_file(file_bytes, filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Validate extracted text length
        if len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Extracted text is too short ({len(extracted_text.strip())} chars). "
                    f"The document may contain mostly images or very little text. "
                    f"Please paste the loan agreement text manually instead."
                )
            )
        
        if len(extracted_text) > 50000:
            logger.warning(f"Document text is large ({len(extracted_text)} chars), truncating to 50,000")
            extracted_text = extracted_text[:50000]
        
        logger.info(
            f"Document text extracted: {len(extracted_text)} chars from '{filename}', "
            f"language={language}"
        )
        
        # Run through the same analysis pipeline
        result = await analyse_contract(
            text=extracted_text,
            language=language,
            provider_override=provider,
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Document analysis complete in {elapsed:.2f}s, provider={result.provider_used}")
        return result
    
    except HTTPException:
        raise
    except RateLimitError as e:
        logger.warning(f"Rate limit hit during document analysis: {e}")
        raise HTTPException(
            status_code=429,
            detail=f"LLM API rate limit reached. Please wait {e.retry_after} seconds and try again.",
            headers={"Retry-After": str(e.retry_after)},
        )
    except ExtractionError as e:
        logger.error(f"Document extraction pipeline failed: {e}")
        raise HTTPException(
            status_code=502,
            detail="All LLM providers failed to extract data from the document. Please try again later.",
        )
    except Exception as e:
        logger.error(f"Document analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during document analysis. Please try again."
        )