import langchain_compat  # noqa: F401
from config import settings

import re
import time
import asyncio
import logging
import unicodedata
from pipeline.segmenter import segment_contract, segments_to_dict
from pipeline.extractor import build_extraction_chain
from pipeline.validator import validate_extraction
from pipeline.summariser import build_summary_chain, build_whatsapp_text
from providers.registry import ProviderRegistry
from services.audit_service import log_analysis
from exceptions import ExtractionError
from schemas.response import (
    AnalysisResponse, EntityResult,
    MathCheckResult, FinancialSummary,
    RiskAnalysis, DefaultEvent,
)

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """Normalize contract text for deterministic LLM processing.
    
    Ensures that the same contract content produces identical LLM input
    regardless of source format (PDF, DOCX, TXT, pasted text).
    This is critical for consistent extraction, risk scores, and summaries.
    """
    # 1. Unicode normalization (NFKC: compatibility decomposition + canonical composition)
    text = unicodedata.normalize('NFKC', text)
    
    # 2. Remove PDF artifacts: page markers, form feeds, vertical tabs
    text = re.sub(r'\f', '\n', text)  # form feed → newline
    text = re.sub(r'\v', '\n', text)  # vertical tab → newline
    text = re.sub(r'---+\s*Page\s*\d+\s*---+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
    
    # 3. Normalize whitespace: tabs → space, multiple spaces → single space
    text = text.replace('\t', ' ')
    text = re.sub(r'[^\S\n]+', ' ', text)  # collapse horizontal whitespace (preserve newlines)
    
    # 4. Normalize line breaks: collapse 3+ consecutive newlines → 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 5. Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # 6. Remove empty lines at start/end
    text = text.strip()
    
    return text


async def analyse_contract(
    text: str,
    language: str = 'en',
    provider_override: str | None = None,
) -> AnalysisResponse:
    start_time = time.time()
    security_warnings = []

    # Normalize text for deterministic processing across all input formats
    text = normalize_text(text)

    primary_provider = ProviderRegistry.get(provider_override or settings.LLM_PRIMARY)
    
    # Timeout-based fallback configuration
    providers_to_try = [primary_provider]
    fallback_provider = None
    
    try:
        fallback_name = settings.LLM_FALLBACK
        if fallback_name and fallback_name != settings.LLM_PRIMARY and settings.FALLBACK_ON_TIMEOUT:
            fallback_provider = ProviderRegistry.get(fallback_name)
            if fallback_provider.health_check():
                logger.info(f"Fallback provider configured: {fallback_provider.get_model_name()} (timeout: {settings.PRIMARY_PROVIDER_TIMEOUT}s)")
            else:
                logger.warning(f"Fallback provider {fallback_name} not healthy - proceeding with primary only")
                fallback_provider = None
    except Exception as e:
        logger.warning(f"Could not initialize fallback provider: {e}")
        fallback_provider = None

    segments = await asyncio.to_thread(segment_contract, text)
    segments_dict = segments_to_dict(segments)

    async def execute_extraction_with_timeout(provider, timeout_seconds=None):
        """Execute extraction with timeout. Returns (result, provider_name, execution_time)"""
        provider_start = time.time()
        try:
            chain = build_extraction_chain(provider)
            if timeout_seconds:
                result = await asyncio.wait_for(
                    chain.ainvoke(segments_dict),
                    timeout=timeout_seconds
                )
            else:
                result = await chain.ainvoke(segments_dict)
            
            execution_time = time.time() - provider_start
            return (result, provider.get_model_name(), execution_time)
        except asyncio.TimeoutError:
            execution_time = time.time() - provider_start
            logger.warning(f"Provider {provider.get_model_name()} timed out after {execution_time:.1f}s")
            raise
        except Exception as e:
            execution_time = time.time() - provider_start
            logger.error(f"Provider {provider.get_model_name()} failed after {execution_time:.1f}s: {str(e)[:200]}")
            raise

    # Try primary provider with timeout
    schema = None
    extraction_warnings = []
    provider_used = primary_provider.get_model_name()
    
    try:
        logger.info(f"Attempting extraction with primary provider: {primary_provider.get_model_name()} (timeout: {settings.PRIMARY_PROVIDER_TIMEOUT}s)")
        result, provider_name, exec_time = await execute_extraction_with_timeout(
            primary_provider, 
            timeout_seconds=settings.PRIMARY_PROVIDER_TIMEOUT
        )
        
        schema = result[0] if isinstance(result, tuple) else result
        if isinstance(result, tuple):
            extraction_warnings.extend(result[1])
        
        provider_used = provider_name
        logger.info(f"✅ Primary provider succeeded in {exec_time:.2f}s")
        
    except asyncio.TimeoutError:
        if fallback_provider:
            logger.warning(f"⏱️ Primary provider timed out after {settings.PRIMARY_PROVIDER_TIMEOUT}s, trying fallback: {fallback_provider.get_model_name()}")
            extraction_warnings.append(f"Primary provider ({primary_provider.get_model_name()}) timed out after {settings.PRIMARY_PROVIDER_TIMEOUT}s. Switched to fallback provider ({fallback_provider.get_model_name()}).")
            
            try:
                # No timeout on fallback - let it take as long as it needs
                result, provider_name, exec_time = await execute_extraction_with_timeout(
                    fallback_provider, 
                    timeout_seconds=None
                )
                
                schema = result[0] if isinstance(result, tuple) else result
                if isinstance(result, tuple):
                    extraction_warnings.extend(result[1])
                
                provider_used = provider_name
                logger.info(f"✅ Fallback provider succeeded in {exec_time:.2f}s")
                
            except Exception as fallback_error:
                error_msg = f"Both primary and fallback providers failed. Primary: timeout after {settings.PRIMARY_PROVIDER_TIMEOUT}s. Fallback: {str(fallback_error)[:200]}"
                logger.error(error_msg)
                raise ExtractionError([error_msg])
        else:
            error_msg = f"Primary provider timed out after {settings.PRIMARY_PROVIDER_TIMEOUT}s and no fallback configured"
            logger.error(error_msg)
            raise ExtractionError([error_msg])
            
    except Exception as primary_error:
        if fallback_provider:
            logger.warning(f"❌ Primary provider failed: {str(primary_error)[:100]}, trying fallback: {fallback_provider.get_model_name()}")
            extraction_warnings.append(f"Primary provider ({primary_provider.get_model_name()}) failed. Switched to fallback provider ({fallback_provider.get_model_name()}).")
            
            try:
                result, provider_name, exec_time = await execute_extraction_with_timeout(
                    fallback_provider, 
                    timeout_seconds=None
                )
                
                schema = result[0] if isinstance(result, tuple) else result
                if isinstance(result, tuple):
                    extraction_warnings.extend(result[1])
                
                provider_used = provider_name
                logger.info(f"✅ Fallback provider succeeded in {exec_time:.2f}s")
                
            except Exception as fallback_error:
                error_msg = f"Both primary and fallback providers failed. Primary: {str(primary_error)[:100]}. Fallback: {str(fallback_error)[:100]}"
                logger.error(error_msg)
                raise ExtractionError([error_msg])
        else:
            error_msg = f"Primary provider failed: {str(primary_error)[:200]}"
            logger.error(error_msg)
            raise ExtractionError([error_msg])
    
    if not schema:
        raise ExtractionError(["No schema could be extracted from any provider"])

    security_warnings.extend(extraction_warnings)

    # 1.3 Numerical Source Verification
    from pipeline.verification import verify_numerical_values
    schema = await asyncio.to_thread(verify_numerical_values, schema, text)

    validated = await asyncio.to_thread(validate_extraction, schema, text)

    # Use the same provider that succeeded for summarization
    summary_provider = ProviderRegistry.get(provider_used.split('/')[0] if '/' in provider_used else ('ollama' if 'llama' in provider_used.lower() else 'gemini'))
    summary_chain = build_summary_chain(summary_provider, language)
    summary_result = await summary_chain.ainvoke({
        'schema': schema,
        'validated': validated,
    })
    
    if isinstance(summary_result, tuple):
        summary, summary_warnings = summary_result
        security_warnings.extend(summary_warnings)
    else:
        summary = summary_result

    whatsapp_text = build_whatsapp_text(summary, schema, validated)

    entities = {
        k: EntityResult(**v)
        for k, v in validated['entities'].items()
    }

    math_check = MathCheckResult(
        is_consistent=validated['math_check'].get('is_consistent'),
        difference_pct=validated['math_check'].get('difference_pct'),
        warning=validated['math_check'].get('warning'),
    )

    financial_summary = FinancialSummary(
        total_repayment=validated['financial_summary'].get('total_repayment'),
        total_interest=validated['financial_summary'].get('total_interest'),
        effective_interest_pct=validated['financial_summary'].get('effective_interest_pct'),
    )

    risk_analysis = RiskAnalysis(
        score=validated['risk_analysis'].get('score', 0),
        factors=validated['risk_analysis'].get('factors', []),
        bps_score=validated['risk_analysis'].get('bps_score', 100.0),
        negotiation_tips=validated['risk_analysis'].get('negotiation_tips', []),
    )

    default_events = [
        DefaultEvent(**e)
        for e in validated['default_events']
    ]

    processing_time = int((time.time() - start_time) * 1000)

    # Audit trail — log every analysis for regulatory compliance
    try:
        log_analysis(
            contract_text=text,
            provider=provider_used,
            risk_score=validated['risk_analysis'].get('score'),
            processing_time_ms=processing_time,
            warnings=security_warnings,
            entities_found=len(validated.get('entities', {})),
            language=language,
            source='text',
        )
    except Exception as e:
        logger.error(f"Audit logging failed: {e}")

    return AnalysisResponse(
        entities=entities,
        math_check=math_check,
        financial_summary=financial_summary,
        risk_analysis=risk_analysis,
        default_events=default_events,
        summary=summary,
        whatsapp_text=whatsapp_text,
        segment_count=len(segments),
        provider_used=provider_used,
        processing_time_ms=processing_time,
        security_warnings=security_warnings,
        missing_terms=validated.get('missing_terms', []),
    )


async def analyse_fineract_product(
    schema,
    product_text: str,
    language: str = 'en',
    provider_override: str | None = None,
) -> AnalysisResponse:
    """Analyse a Fineract loan product using a pre-built schema.

    Unlike analyse_contract(), this does NOT run LLM extraction — the schema
    is built directly from Fineract's structured API response, so every
    financial value is 100% accurate from the authoritative source.

    The LLM is ONLY used for generating the borrower-friendly summary.
    """
    start_time = time.time()
    security_warnings = []

    primary_provider = ProviderRegistry.get(provider_override or settings.LLM_PRIMARY)

    # --- Validation (risk scoring, math checks, financial calcs) ---
    # These are purely deterministic — no LLM involvement
    validated = await asyncio.to_thread(validate_extraction, schema, product_text)

    # --- LLM Summary Generation ---
    # This is the ONLY LLM call — generating a human-readable summary
    summary_chain = build_summary_chain(primary_provider, language)
    summary_result = await summary_chain.ainvoke({
        'schema': schema,
        'validated': validated,
    })

    if isinstance(summary_result, tuple):
        summary, summary_warnings = summary_result
        security_warnings.extend(summary_warnings)
    else:
        summary = summary_result

    whatsapp_text = build_whatsapp_text(summary, schema, validated)

    # --- Build response ---
    entities = {
        k: EntityResult(**v)
        for k, v in validated['entities'].items()
    }

    math_check = MathCheckResult(
        is_consistent=validated['math_check'].get('is_consistent'),
        difference_pct=validated['math_check'].get('difference_pct'),
        warning=validated['math_check'].get('warning'),
    )

    financial_summary = FinancialSummary(
        total_repayment=validated['financial_summary'].get('total_repayment'),
        total_interest=validated['financial_summary'].get('total_interest'),
        effective_interest_pct=validated['financial_summary'].get('effective_interest_pct'),
    )

    risk_analysis = RiskAnalysis(
        score=validated['risk_analysis'].get('score', 0),
        factors=validated['risk_analysis'].get('factors', []),
        bps_score=validated['risk_analysis'].get('bps_score', 100.0),
        negotiation_tips=validated['risk_analysis'].get('negotiation_tips', []),
    )

    default_events = [
        DefaultEvent(**e)
        for e in validated['default_events']
    ]

    processing_time = int((time.time() - start_time) * 1000)

    # Audit trail
    try:
        log_analysis(
            contract_text=product_text,
            provider=primary_provider.get_model_name(),
            risk_score=validated['risk_analysis'].get('score'),
            processing_time_ms=processing_time,
            warnings=security_warnings,
            entities_found=len(validated.get('entities', {})),
            language=language,
            source='fineract',
        )
    except Exception as e:
        logger.error(f"Audit logging failed: {e}")

    return AnalysisResponse(
        entities=entities,
        math_check=math_check,
        financial_summary=financial_summary,
        risk_analysis=risk_analysis,
        default_events=default_events,
        summary=summary,
        whatsapp_text=whatsapp_text,
        segment_count=0,
        provider_used=primary_provider.get_model_name(),
        processing_time_ms=processing_time,
        security_warnings=security_warnings,
        missing_terms=validated.get('missing_terms', []),
    )