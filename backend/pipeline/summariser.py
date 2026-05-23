from langchain_core.runnables import RunnableLambda
from backend.pipeline.prompts import SUMMARY_SYSTEM_PROMPT
from backend.schemas.loan_schema import LoanAgreementSchema


def build_summary_input(schema: LoanAgreementSchema, validated: dict) -> str:
    la = schema.loan_amount.value
    ir = schema.interest_rate.value
    ir_type = schema.interest_rate.type
    rd = schema.repayment_duration.value
    mp = schema.monthly_payment.value
    tc = schema.total_cost.value
    lf = schema.late_fee.value
    pi = schema.penalty_interest.value
    pf = schema.processing_fee.value
    currency = schema.currency or 'INR'
    total_repayment = validated['financial_summary'].get('total_repayment')
    risk_score = validated['risk_analysis'].get('score', 0)
    risk_factors = validated['risk_analysis'].get('factors', [])
    default_events = validated['default_events']

    lines = [
        f"Loan Amount: {la} {currency}" if la else "Loan Amount: Not specified",
        f"Interest Rate: {ir}% per annum ({ir_type or 'type not specified'})" if ir else "Interest Rate: Not specified",
        f"Repayment Duration: {rd} months" if rd else "Repayment Duration: Not specified",
        f"Monthly Payment: {mp} {currency}" if mp else "Monthly Payment: Not specified",
        f"Total Repayment: {total_repayment} {currency}" if total_repayment else "Total Repayment: Not calculated",
        f"Late Fee: {lf} {currency} per month" if lf else "Late Fee: None",
        f"Penalty Interest: {pi}% per month" if pi else "Penalty Interest: None",
        f"Processing Fee: {pf} {currency}" if pf else "Processing Fee: None",
        f"Risk Score: {risk_score}/10",
        f"Risk Factors: {', '.join(risk_factors)}" if risk_factors else "Risk Factors: None",
        f"Default Triggers: {len(default_events)} found" if default_events else "Default Triggers: None specified",
    ]

    return '\n'.join(lines)


def build_summary_chain(provider, language: str = 'en'):

    def _summarise(inputs: dict) -> str:
        schema = inputs['schema']
        validated = inputs['validated']

        summary_input = build_summary_input(schema, validated)

        messages = [
            {
                'role': 'system',
                'content': SUMMARY_SYSTEM_PROMPT,
            },
            {
                'role': 'user',
                'content': (
                    f"Language: {language}\n\n"
                    f"Loan details:\n{summary_input}\n\n"
                    f"Write a plain-language summary for the borrower:"
                ),
            }
        ]

        try:
            response = provider.raw_client.chat.completions.create(
                model=provider.get_model_name(),
                messages=messages,
                temperature=0.3,
                max_tokens=500,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f'Summary generation failed: {e}')
            la = schema.loan_amount.value
            ir = schema.interest_rate.value
            rd = schema.repayment_duration.value
            mp = schema.monthly_payment.value
            tr = validated['financial_summary'].get('total_repayment')
            return (
                f"This loan is for Rs. {la:,.0f} at {ir}% interest "
                f"over {rd} months with monthly payments of Rs. {mp:,.0f}. "
                f"Total repayment will be Rs. {tr:,.0f}."
            ) if all([la, ir, rd, mp, tr]) else "Summary could not be generated."

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