import json

import langchain_compat  # noqa: F401

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
        formatted = format_segments(segments)
        
        # WARNING: Sanitize input to prevent prompt injection
        sanitized, warnings = sanitize_contract_text(formatted)
        
        if warnings:
            print(f'SECURITY: Input sanitization warnings: {warnings}')
        
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

        is_ollama = 'ollama' in provider.get_model_name().lower() or hasattr(provider, '__class__') and 'ollama' in provider.__class__.__name__.lower()
        
        try:
            import instructor
            
            if is_ollama:
                print('Using fallback mode for Ollama (instructor compatibility)')
                raise Exception("Skipping instructor for Ollama compatibility")
            
            client = instructor.from_openai(
                provider.raw_client,
                mode=instructor.Mode.JSON,
            )
            result = client.chat.completions.create(
                model=provider.get_model_name(),
                response_model=LoanAgreementSchema,
                messages=messages,
                temperature=0.1,
                max_tokens=1200,
                max_retries=3,
            )
            print(f'Instructor extraction succeeded')
            
            # WARNING: Validate output for injection signs
            is_valid, issues = validate_extraction_output(
                result.dict(),
                formatted,
                warnings
            )
            
            if not is_valid:
                print(f'SECURITY: Output validation issues: {issues}')
                warnings.extend(issues)
            
            return result, warnings

        except Exception as e1:
            print(f'Instructor failed (fallback to manual JSON parsing): {e1}')

            try:
                is_ollama = 'ollama' in provider.__class__.__name__.lower()
                
                if is_ollama and hasattr(provider, 'generate_native'):
                    print('Using Ollama native API for extraction...')
                    system_prompt = EXTRACTION_SYSTEM_PROMPT
                    user_prompt = user_message
                    
                    raw_text = provider.generate_native(
                        prompt=user_prompt,
                        system=system_prompt,
                        max_tokens=1200,
                        temperature=0.1
                    )
                else:
                    timeout = 120 if is_ollama else 60
                    
                    response = provider.raw_client.chat.completions.create(
                        model=provider.get_model_name(),
                        messages=messages,
                        temperature=0.1,
                        max_tokens=1200,
                        timeout=timeout,
                    )
                    raw_text = response.choices[0].message.content
                
                print(f'Raw LLM response (first 500 chars): {raw_text[:500]}')

                parsed = parse_llm_response(raw_text)
                print(f'Parsed dict keys: {list(parsed.keys())}')

                if parsed:
                    schema = LoanAgreementSchema(**parsed)
                    
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
                import traceback
                traceback.print_exc()
                return LoanAgreementSchema(), warnings

    return RunnableLambda(_extract)

    return RunnableLambda(_extract)