from pydantic import BaseModel
from typing import Any


class EntityResult(BaseModel):
    value: Any
    source_clause: str | None = None
    confidence: float = 0.0
    is_verified: bool = False
    similarity: float = 0.0
    verify_method: str = 'none'
    flag: str | None = None


class MathCheckResult(BaseModel):
    is_consistent: bool | None = None
    difference_pct: float | None = None
    warning: str | None = None


class FinancialSummary(BaseModel):
    total_repayment: float | None = None
    total_interest: float | None = None
    effective_interest_pct: float | None = None


class RiskAnalysis(BaseModel):
    score: float = 0.0
    factors: list[str] = []


class DefaultEvent(BaseModel):
    trigger: str
    source_clause: str | None = None


class AnalysisResponse(BaseModel):
    entities: dict[str, EntityResult] = {}
    math_check: MathCheckResult = MathCheckResult()
    financial_summary: FinancialSummary = FinancialSummary()
    risk_analysis: RiskAnalysis = RiskAnalysis()
    default_events: list[DefaultEvent] = []
    summary: str = ''
    whatsapp_text: str = ''
    segment_count: int = 0
    provider_used: str = ''
    processing_time_ms: int = 0
    security_warnings: list[str] = []  # Prompt injection and other security warnings
