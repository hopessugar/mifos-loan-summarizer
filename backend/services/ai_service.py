import time
from backend.pipeline.segmenter import segment_contract, segments_to_dict
from backend.pipeline.extractor import build_extraction_chain
from backend.pipeline.validator import validate_extraction
from backend.pipeline.summariser import build_summary_chain, build_whatsapp_text
from backend.providers.registry import ProviderRegistry
from backend.schemas.response import (
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

    provider = ProviderRegistry.get(provider_override)

    # Stage 1: segment
    segments = segment_contract(text)
    segments_dict = segments_to_dict(segments)

    # Stage 2: extract
    extraction_chain = build_extraction_chain(provider)
    schema = extraction_chain.invoke(segments_dict)

    # Stage 3: validate
    validated = validate_extraction(schema, text)

    # Stage 4: summarise
    summary_chain = build_summary_chain(provider, language)
    summary = summary_chain.invoke({
        'schema': schema,
        'validated': validated,
    })

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
    )