import langchain_compat  # noqa: F401

from langchain_core.runnables import RunnableLambda
from pipeline.prompts import SUMMARY_SYSTEM_PROMPT
from schemas.loan_schema import LoanAgreementSchema
from pipeline.input_sanitizer import sanitize_contract_text, create_secure_prompt
import re


def validate_summary_against_data(summary: str, structured_input: str) -> list[str]:
    warnings = []
    summary_lower = summary.lower()
    input_lower = structured_input.lower()
    
    # Check for common hallucination patterns
    hallucination_patterns = [
        (r'\d+%\s*(per month|monthly|pm)', 'monthly percentage rate'),
        (r'penalty.*if.*don\'t pay', 'penalty conditions'),
        (r'will be charged|will incur', 'future charges'),
        (r'must pay|required to pay', 'payment obligations'),
    ]
    
    for pattern, description in hallucination_patterns:
        if re.search(pattern, summary_lower):
            # Check if this information is in the input data
            if 'not specified' in input_lower and description in summary_lower:
                warnings.append(f'Summary may contain hallucinated {description} not in source data')
    
    # Check if summary mentions penalties not in input
    penalty_terms = ['late fee', 'late payment', 'prepayment penalty', 'penalty interest']
    for term in penalty_terms:
        if term in summary_lower:
            # Make sure it's actually specified in input
            if f'{term}: not specified' in input_lower:
                warnings.append(f'Summary mentions {term} but it is not specified in agreement')
    
    return warnings


def build_summary_input(schema: LoanAgreementSchema, validated: dict) -> str:
    la = schema.loan_amount.value
    ir = schema.interest_rate.value
    ir_type = schema.interest_rate.type
    rd = schema.repayment_duration.value
    mp = schema.monthly_payment.value
    tc = schema.total_cost.value
    
    # Distinguish between different penalty types
    lf = schema.late_fee.value
    lpi = schema.late_payment_interest.value
    pi = schema.penalty_interest.value
    pp = schema.prepayment_penalty.value
    pf = schema.processing_fee.value
    
    currency = schema.currency or 'INR'
    
    financial_summary = validated['financial_summary']
    total_repayment = financial_summary.get('total_repayment')
    total_interest = financial_summary.get('total_interest')
    emi_note = financial_summary.get('emi_note')
    
    risk_analysis = validated['risk_analysis']
    risk_score = risk_analysis.get('score', 0)
    risk_band = risk_analysis.get('risk_band', 'Unknown')
    risk_factors = risk_analysis.get('factors', [])
    warnings = risk_analysis.get('warnings', [])
    
    math_check = validated['math_check']
    default_events = validated['default_events']

    lines = [
        "=== CORE LOAN TERMS ===",
        f"Loan Amount: {la} {currency}" if la else "Loan Amount: NOT SPECIFIED IN AGREEMENT",
        f"Interest Rate: {ir}% per annum ({ir_type or 'type not specified'})" if ir else "Interest Rate: NOT SPECIFIED IN AGREEMENT",
        f"Repayment Duration: {rd} months" if rd else "Repayment Duration: NOT SPECIFIED IN AGREEMENT",
        f"Monthly Payment (EMI): {mp} {currency}" if mp else f"Monthly Payment: NOT SPECIFIED (Estimated: {math_check.get('estimated_emi', 'N/A')} {currency} - please confirm with lender)" if math_check.get('estimated_emi') else "Monthly Payment: NOT SPECIFIED IN AGREEMENT",
    ]
    
    if emi_note:
        lines.append(f"NOTE: Monthly payment is estimated from loan terms, not explicitly stated in agreement")
    
    lines.extend([
        "",
        "=== TOTAL COSTS ===",
        f"Total Repayment: {total_repayment} {currency}" if total_repayment else "Total Repayment: NOT CALCULATED",
        f"Total Interest: {total_interest} {currency}" if total_interest else "Total Interest: NOT CALCULATED",
    ])
    
    lines.extend([
        "",
        "=== FEES AND PENALTIES ===",
    ])
    
    if lf:
        lines.append(f"Late Payment Fee: {lf} {currency} (one-time or recurring fee for late payment)")
    else:
        lines.append("Late Payment Fee: NOT SPECIFIED IN AGREEMENT")
    
    if lpi:
        lines.append(f"Late Payment Interest: {lpi}% per annum (additional interest on overdue amount)")
    else:
        lines.append("Late Payment Interest: NOT SPECIFIED IN AGREEMENT")
    
    if pp:
        pp_pct = pp * 100 if pp < 1 else pp
        lines.append(f"Prepayment Penalty: {pp_pct}% (fee for early repayment)")
    else:
        lines.append("Prepayment Penalty: NOT SPECIFIED IN AGREEMENT")
    
    if pi:
        lines.append(f"General Penalty Interest: {pi}% (for other breaches)")
    else:
        lines.append("General Penalty Interest: NOT SPECIFIED IN AGREEMENT")
    
    if pf:
        lines.append(f"Processing Fee: {pf} {currency}")
    else:
        lines.append("Processing Fee: NOT SPECIFIED IN AGREEMENT")
    
    lines.extend([
        "",
        "=== RISK ASSESSMENT ===",
        f"Risk Score: {risk_score}/10 ({risk_band})",
        f"Risk Level Explanation: {risk_analysis.get('band_explanation', 'N/A')}",
    ])
    
    if risk_factors:
        lines.append(f"Risk Factors ({len(risk_factors)}):")
        for factor in risk_factors:
            lines.append(f"  - {factor}")
    else:
        lines.append("Risk Factors: None identified")
    
    if warnings:
        lines.append("CRITICAL WARNINGS:")
        for warning in warnings:
            lines.append(f"  ⚠️ {warning}")
    
    lines.extend([
        "",
        "=== DEFAULT TRIGGERS ===",
    ])
    
    if default_events:
        lines.append(f"Total Default Triggers: {len(default_events)}")
        breakdown = risk_analysis.get('default_events_breakdown', {})
        lines.append(f"  - Standard protective clauses: {breakdown.get('standard_clauses', 0)}")
        lines.append(f"  - Unusual/predatory clauses: {breakdown.get('predatory_clauses', 0)}")
    else:
        lines.append("Default Triggers: NOT SPECIFIED IN AGREEMENT")
    
    lines.extend([
        "",
        "=== MATH VERIFICATION ===",
    ])
    
    if math_check.get('warning'):
        lines.append(f"Math Check: {math_check['warning']}")
    else:
        lines.append("Math Check: All calculations verified as consistent")

    return '\n'.join(lines)


def build_summary_chain(provider, language: str = 'en'):

    def _summarise(inputs: dict) -> tuple[str, list[str]]:
        schema = inputs['schema']
        validated = inputs['validated']

        summary_input = build_summary_input(schema, validated)
        
        sanitized_input, warnings = sanitize_contract_text(summary_input, max_length=10_000)
        
        if warnings:
            print(f'SECURITY: Summary input sanitization warnings: {warnings}')
        
        user_message = create_secure_prompt(
            f"Language: {language}\n\nWrite a plain-language summary for the borrower based on the loan details below.",
            sanitized_input,
            delimiter_start='<DATA>',
            delimiter_end='</DATA>'
        )

        messages = [
            {
                'role': 'system',
                'content': SUMMARY_SYSTEM_PROMPT,
            },
            {
                'role': 'user',
                'content': user_message,
            }
        ]

        try:
            is_ollama = 'ollama' in provider.__class__.__name__.lower()
            is_gemini = 'gemini' in provider.__class__.__name__.lower() or hasattr(provider, '_is_gemini')
            
            if (is_ollama or is_gemini) and hasattr(provider, 'generate_native'):
                provider_name = 'Ollama' if is_ollama else 'Gemini'
                print(f'Using {provider_name} native API for summarization...')
                summary = provider.generate_native(
                    prompt=user_message,
                    system=SUMMARY_SYSTEM_PROMPT,
                    max_tokens=500,
                    temperature=0.1
                )
                if summary is None:
                    raise Exception(f"{provider_name} returned empty response")
                summary = summary.strip()
            else:
                timeout_kwarg = {}
                if is_ollama:
                    timeout_kwarg = {'timeout': 90}
                
                response = provider.raw_client.chat.completions.create(
                    model=provider.get_model_name(),
                    messages=messages,
                    temperature=0.1,
                    max_tokens=500,
                    **timeout_kwarg
                )
                summary = response.choices[0].message.content
                if summary is None:
                    raise Exception("LLM returned empty response")
                summary = summary.strip()
            
            hallucination_warnings = validate_summary_against_data(summary, summary_input)
            if hallucination_warnings:
                print(f'SUMMARY VALIDATION WARNINGS: {hallucination_warnings}')
                warnings.extend(hallucination_warnings)
            
            return summary, warnings
        except Exception as e:
            print(f'Summary generation failed: {e}')
            la = schema.loan_amount.value
            ir = schema.interest_rate.value
            rd = schema.repayment_duration.value
            mp = schema.monthly_payment.value
            tr = validated['financial_summary'].get('total_repayment')
            fallback = (
                f"This loan is for Rs. {la:,.0f} at {ir}% interest "
                f"over {rd} months with monthly payments of Rs. {mp:,.0f}. "
                f"Total repayment will be Rs. {tr:,.0f}."
            ) if all([la, ir, rd, mp, tr]) else "Summary could not be generated."
            return fallback, warnings

    return RunnableLambda(_summarise)


def build_whatsapp_text(summary: str, schema: LoanAgreementSchema, validated: dict) -> str:
    la = schema.loan_amount.value
    ir = schema.interest_rate.value
    mp = schema.monthly_payment.value
    tr = validated['financial_summary'].get('total_repayment')
    risk = validated['risk_analysis'].get('score', 0)

    text = (
        f"Loan: Rs.{la:,.0f} | Rate: {ir}% | EMI: Rs.{mp:,.0f} | "
        f"Total: Rs.{tr:,.0f} | Risk: {risk}/10"
    ) if all([la, ir, mp, tr]) else summary[:280]

    return text[:300]