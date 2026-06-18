import langchain_compat  # noqa: F401
from config import settings

import time
import asyncio
import logging
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


async def analyse_contract(
    text: str,
    language: str = 'en',
    provider_override: str | None = None,
) -> AnalysisResponse:
    start_time = time.time()
    security_warnings = []

    primary_provider = ProviderRegistry.get(provider_override or settings.LLM_PRIMARY)
    
    # Optional fallback for consensus - DISABLED if same model or no fallback configured
    providers_to_try = [primary_provider]
    try:
        fallback_name = settings.LLM_FALLBACK
        if fallback_name and fallback_name != settings.LLM_PRIMARY:
            fallback_provider = ProviderRegistry.get(fallback_name)
            if fallback_provider.health_check() and fallback_provider.get_model_name() != primary_provider.get_model_name():
                providers_to_try.append(fallback_provider)
                logger.info(f"Using fallback provider: {fallback_provider.get_model_name()}")
            else:
                logger.info("Fallback provider not healthy or same model - skipping consensus")
    except Exception as e:
        logger.warning(f"Could not initialize fallback provider: {e}")
        # Continue with just primary

    segments = await asyncio.to_thread(segment_contract, text)
    segments_dict = segments_to_dict(segments)

    async def execute_extraction(provider):
        chain = build_extraction_chain(provider)
        return await chain.ainvoke(segments_dict)

    # Gather extractions concurrently
    results = await asyncio.gather(*[execute_extraction(p) for p in providers_to_try], return_exceptions=True)
    
    schema = None
    extraction_warnings = []
    
    # 1.4 LLM Fallback Chain
    valid_results = []
    extraction_errors = []
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            error_msg = f'Provider {i+1} extraction failed: {str(res)[:200]}'
            logger.error(error_msg)
            extraction_errors.append(error_msg)
            continue
        valid_results.append(res)
    
    if not valid_results:
        error_details = " | ".join(extraction_errors)
        raise ExtractionError(extraction_errors)
    
    # 1.2 Multi-Model Consensus Extraction
    primary_res = valid_results[0]
    schema = primary_res[0] if isinstance(primary_res, tuple) else primary_res
    if isinstance(primary_res, tuple):
        extraction_warnings.extend(primary_res[1])

    if len(valid_results) > 1:
        secondary_res = valid_results[1]
        schema2 = secondary_res[0] if isinstance(secondary_res, tuple) else secondary_res
        
        # Simple consensus check on key fields
        if schema.interest_rate.value == schema2.interest_rate.value:
            schema.interest_rate.confidence = 0.99  # HIGH confidence
        else:
            extraction_warnings.append(f"Consensus mismatch: Primary provider found interest rate {schema.interest_rate.value}, but fallback found {schema2.interest_rate.value}. Needs review.")
            schema.interest_rate.confidence = 0.40  # Low confidence / needs review
            
        if schema.loan_amount.value == schema2.loan_amount.value:
            schema.loan_amount.confidence = 0.99
        else:
            extraction_warnings.append(f"Consensus mismatch on loan amount. Primary: {schema.loan_amount.value}, Fallback: {schema2.loan_amount.value}.")
            schema.loan_amount.confidence = 0.40

    security_warnings.extend(extraction_warnings)

    # 1.3 Numerical Source Verification
    from pipeline.verification import verify_numerical_values
    schema = await asyncio.to_thread(verify_numerical_values, schema, text)

    validated = await asyncio.to_thread(validate_extraction, schema, text)

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
            provider=primary_provider.get_model_name(),
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
        provider_used=primary_provider.get_model_name(),
        processing_time_ms=processing_time,
        security_warnings=security_warnings,
        missing_terms=validated.get('missing_terms', []),
    )