import json
from langchain_core.runnables import RunnableLambda
from backend.schemas.loan_schema import LoanAgreementSchema
from backend.pipeline.prompts import EXTRACTION_SYSTEM_PROMPT


def format_segments(segments: list[dict]) -> str:
    parts = []
    for seg in segments:
        parts.append(f"[{seg['label']}]\n{seg['text']}")
    return '\n\n'.join(parts)


def parse_llm_response(text: str) -> dict:
    text = text.strip()
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0].strip()
    elif '```' in text:
        text = text.split('```')[1].split('```')[0].strip()
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f'JSON parse error: {e}')
        print(f'Raw text was: {text[:500]}')
        return {}


def build_extraction_chain(provider):

    def _extract(segments: list[dict]) -> LoanAgreementSchema:
        formatted = format_segments(segments)

        messages = [
            {
                'role': 'system',
                'content': EXTRACTION_SYSTEM_PROMPT,
            },
            {
                'role': 'user',
                'content': f'Extract all financial entities from these contract segments:\n\n{formatted}\n\nJSON:',
            }
        ]

        try:
            import instructor
            client = instructor.from_openai(
                provider.raw_client,
                mode=instructor.Mode.JSON,
            )
            result = client.chat.completions.create(
                model=provider.get_model_name(),
                response_model=LoanAgreementSchema,
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
                max_retries=3,
            )
            print(f'Instructor extraction succeeded')
            return result

        except Exception as e1:
            print(f'Instructor failed: {e1}')

            try:
                response = provider.raw_client.chat.completions.create(
                    model=provider.get_model_name(),
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2000,
                    timeout=280,
                )
                raw_text = response.choices[0].message.content
                print(f'Raw LLM response: {raw_text[:500]}')

                parsed = parse_llm_response(raw_text)
                print(f'Parsed dict keys: {list(parsed.keys())}')

                if parsed:
                    return LoanAgreementSchema(**parsed)
                return LoanAgreementSchema()

            except Exception as e2:
                print(f'Fallback also failed: {e2}')
                return LoanAgreementSchema()

    return RunnableLambda(_extract)