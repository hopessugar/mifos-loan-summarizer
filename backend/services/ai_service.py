# Import compatibility shim first to fix langchain.debug issue
try:
    from backend import langchain_compat
except ImportError:
    pass  # Compatibility shim not needed or not available

import time
import asyncio
from pipeline.segmenter import segment_contract, segments_to_dict
from pipeline.extractor import build_extraction_chain
from pipeline.validator import validate_extraction
from pipeline.summariser import build_summary_chain, build_whatsapp_text
from providers.registry import ProviderRegistry
from schemas.response import (
    AnalysisResponse, EntityResult,
    MathCheckResult, FinancialSummary,
    RiskAnalysis, DefaultEvent,
)


async def analyse_contract(
    text: str,
    language: str = 'en',
    provider_override: str | None = None,
) -> AnalysisResponse:
    """
    Analyze loan contract with proper async/await patterns.
    
    Performance improvements:
    - CPU-bound operations run in thread pool (segment, validate)
    - I/O-bound operations use async (LLM API calls)
    - Enables concurrent request handling
    """
    start_time = time.time()
    security_warnings = []

    provider = ProviderRegistry.get(provider_override)

    # Stage 1: segment (CPU-bound → run in thread pool)
    segments = await asyncio.to_thread(segment_contract, text)
    segments_dict = segments_to_dict(segments)

    # Stage 2: extract (I/O-bound → use ainvoke for async LLM call)
    extraction_chain = build_extraction_chain(provider)
    extraction_result = await extraction_chain.ainvoke(segments_dict)
    
    # Handle tuple return (schema, warnings) from updated extractor
    if isinstance(extraction_result, tuple):
        schema, extraction_warnings = extraction_result
        security_warnings.extend(extraction_warnings)
    else:
        schema = extraction_result

    # Stage 3: validate (CPU-bound → run in thread pool)
    validated = await asyncio.to_thread(validate_extraction, schema, text)

    # Stage 4: summarise (I/O-bound → use ainvoke for async LLM call)
    summary_chain = build_summary_chain(provider, language)
    summary_result = await summary_chain.ainvoke({
        'schema': schema,
        'validated': validated,
    })
    
    # Handle tuple return (summary, warnings) from updated summarizer
    if isinstance(summary_result, tuple):
        summary, summary_warnings = summary_result
        security_warnings.extend(summary_warnings)
    else:
        summary = summary_result

    whatsapp_text = build_whatsapp_text(summary, schema, validated)

    # Convert entities
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
    )

    default_events = [
        DefaultEvent(**e)
        for e in validated['default_events']
    ]

    processing_time = int((time.time() - start_time) * 1000)

    return AnalysisResponse(
        entities=entities,
        math_check=math_check,
        financial_summary=financial_summary,
        risk_analysis=risk_analysis,
        default_events=default_events,
        summary=summary,
        whatsapp_text=whatsapp_text,
        segment_count=len(segments),
        provider_used=provider.get_model_name(),
        processing_time_ms=processing_time,
        security_warnings=security_warnings,
    )