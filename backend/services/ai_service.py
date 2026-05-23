import time
from backend.pipeline.segmenter import segment_contract, segments_to_dict
from backend.pipeline.extractor import build_extraction_chain
from backend.pipeline.validator import validate_extraction
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

    # Convert entities
    entities = {
        k: EntityResult(**v)
        for k, v in validated['entities'].items()
    }

    # Math check
    mc = validated['math_check']
    math_check = MathCheckResult(
        is_consistent=mc.get('is_consistent'),
        difference_pct=mc.get('difference_pct'),
        warning=mc.get('warning'),
    )

    # Financial summary
    fs = validated['financial_summary']
    financial_summary = FinancialSummary(
        total_repayment=fs.get('total_repayment'),
        total_interest=fs.get('total_interest'),
        effective_interest_pct=fs.get('effective_interest_pct'),
    )

    # Risk analysis
    ra = validated['risk_analysis']
    risk_analysis = RiskAnalysis(
        score=ra.get('score', 0),
        factors=ra.get('factors', []),
    )

    # Default events
    default_events = [
        DefaultEvent(**e)
        for e in validated['default_events']
    ]

    # Basic summary
    la = schema.loan_amount.value
    ir = schema.interest_rate.value
    rd = schema.repayment_duration.value
    mp = schema.monthly_payment.value

    summary = (
        f"This loan is for Rs. {la:,.0f} at {ir}% interest "
        f"over {rd} months. Monthly payment is Rs. {mp:,.0f}. "
        f"Total repayment will be Rs. {fs.get('total_repayment', 0):,.0f}. "
        f"Risk score: {ra.get('score', 0)}/10."
    ) if all([la, ir, rd, mp]) else 'Could not generate summary — extraction incomplete.'

    processing_time = int((time.time() - start_time) * 1000)

    return AnalysisResponse(
        entities=entities,
        math_check=math_check,
        financial_summary=financial_summary,
        risk_analysis=risk_analysis,
        default_events=default_events,
        summary=summary,
        whatsapp_text=summary[:280],
        segment_count=len(segments),
        provider_used=provider.get_model_name(),
        processing_time_ms=processing_time,
    )