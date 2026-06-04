import langchain_compat  # noqa: F401

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
    start_time = time.time()
    security_warnings = []

    provider = ProviderRegistry.get(provider_override)

    segments = await asyncio.to_thread(segment_contract, text)
    segments_dict = segments_to_dict(segments)

    extraction_chain = build_extraction_chain(provider)
    extraction_result = await extraction_chain.ainvoke(segments_dict)
    
    if isinstance(extraction_result, tuple):
        schema, extraction_warnings = extraction_result
        security_warnings.extend(extraction_warnings)
    else:
        schema = extraction_result

    validated = await asyncio.to_thread(validate_extraction, schema, text)

    summary_chain = build_summary_chain(provider, language)
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