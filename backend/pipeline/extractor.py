import json

# Import compatibility shim first to fix langchain.debug issue
try:
    from backend import langchain_compat
except ImportError:
    pass  # Compatibility shim not needed or not available

from langchain_core.runnables import RunnableLambda
from schemas.loan_schema import LoanAgreementSchema
from pipeline.prompts import EXTRACTION_SYSTEM_PROMPT
from pipeline.input_sanitizer import (
    sanitize_contract_text,
    validate_extraction_output,
    create_secure_prompt,
)


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

    def _extract(segments: list[dict]) -> tuple[LoanAgreementSchema, list[str]]:
        """
        Extract financial entities from contract segments with prompt injection protection.
        
        Returns:
            Tuple of (schema, security_warnings)
        """
        formatted = format_segments(segments)
        
        # Layer 1: Sanitize input to prevent prompt injection
        sanitized, warnings = sanitize_contract_text(formatted)
        
        if warnings:
            print(f'SECURITY: Input sanitization warnings: {warnings}')
        
        # Layer 2: Use secure prompt with delimiters
        user_message = create_secure_prompt(
            "Extract all financial entities from the contract below.",
            sanitized,
            delimiter_start='<CONTRACT>',
            delimiter_end='</CONTRACT>'
        )

        messages = [
            {
                'role': 'system',
                'content': EXTRACTION_SYSTEM_PROMPT,
            },
            {
                'role': 'user',
                'content': user_message,
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
            
            # Layer 3: Validate output for injection signs
            is_valid, issues = validate_extraction_output(
                result.dict(),
                formatted,  # Use original unsanitized text for validation
                warnings
            )
            
            if not is_valid:
                print(f'SECURITY: Output validation issues: {issues}')
                warnings.extend(issues)
            
            return result, warnings

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
                    schema = LoanAgreementSchema(**parsed)
                    
                    # Layer 3: Validate output
                    is_valid, issues = validate_extraction_output(
                        parsed,
                        formatted,
                        warnings
                    )
                    
                    if not is_valid:
                        print(f'SECURITY: Output validation issues: {issues}')
                        warnings.extend(issues)
                    
                    return schema, warnings
                
                return LoanAgreementSchema(), warnings

            except Exception as e2:
                print(f'Fallback also failed: {e2}')
                return LoanAgreementSchema(), warnings

    return RunnableLambda(_extract)

    return RunnableLambda(_extract)