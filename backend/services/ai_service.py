import time
from backend.pipeline.segmenter import segment_contract, segments_to_dict
from backend.pipeline.extractor import build_extraction_chain
from backend.providers.registry import ProviderRegistry
from backend.schemas.response import AnalysisResponse, EntityResult


def schema_to_entities(schema) -> dict:
    entities = {}

    simple_fields = [
        'loan_amount', 'repayment_duration',
        'monthly_payment', 'total_cost',
    ]
    for field in simple_fields:
        obj = getattr(schema, field, None)
        if obj and obj.value is not None:
            entities[field] = EntityResult(
                value=obj.value,
                source_clause=obj.source_clause,
                confidence=0.8,
                is_verified=False,
            )

    ir = schema.interest_rate
    if ir and ir.value is not None:
        entities['interest_rate'] = EntityResult(
            value=f"{ir.value}% {ir.type or ''}".strip(),
            source_clause=ir.source_clause,
            confidence=0.8,
            is_verified=False,
        )

    fee_fields = [
        'late_fee', 'penalty_interest', 'prepayment_penalty',
        'processing_fee', 'insurance_fee', 'administrative_fee',
    ]
    for field in fee_fields:
        obj = getattr(schema, field, None)
        if obj and obj.value is not None:
            entities[field] = EntityResult(
                value=obj.value,
                source_clause=obj.source_clause,
                confidence=0.7,
                is_verified=False,
            )

    if schema.collateral and schema.collateral.present:
        entities['collateral'] = EntityResult(
            value=schema.collateral.description or 'Present',
            source_clause=schema.collateral.source_clause,
            confidence=0.8,
            is_verified=False,
        )

    for key, val in [
        ('payment_frequency', schema.payment_frequency),
        ('payment_due_day', schema.payment_due_day),
        ('repayment_start_date', schema.repayment_start_date),
        ('currency', schema.currency),
    ]:
        if val:
            entities[key] = EntityResult(
                value=val,
                confidence=0.75,
                is_verified=False,
            )

    return entities


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

    # Convert schema to entities
    entities = schema_to_entities(schema)

    # Basic summary (full summary chain in LMS-8)
    summary = (
        f"This loan agreement involves a principal amount of "
        f"{schema.loan_amount.value or 'unknown'} {schema.currency or 'INR'} "
        f"at an interest rate of {schema.interest_rate.value or 'unknown'}% "
        f"over {schema.repayment_duration.value or 'unknown'} months. "
        f"Monthly payment is {schema.monthly_payment.value or 'unknown'}."
    )

    processing_time = int((time.time() - start_time) * 1000)

    return AnalysisResponse(
        entities=entities,
        summary=summary,
        whatsapp_text=summary[:280],
        segment_count=len(segments),
        provider_used=provider.get_model_name(),
        processing_time_ms=processing_time,
    )