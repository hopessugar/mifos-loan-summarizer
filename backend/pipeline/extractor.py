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
from config import settings


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
        
        # Truncate if too large to fit in API limits
        if len(formatted) > settings.MAX_INPUT_CHARS:
            print(f'⚠️  Contract too large ({len(formatted)} chars), truncating to {settings.MAX_INPUT_CHARS}')
            formatted = formatted[:settings.MAX_INPUT_CHARS] + "\n\n[CONTRACT TRUNCATED DUE TO SIZE LIMITS]"
        
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
        is_gemini = 'gemini' in provider.get_model_name().lower() or hasattr(provider, '_is_gemini')
        
        try:
            import instructor
            
            if is_ollama or is_gemini:
                print(f'Using fallback mode for {"Ollama" if is_ollama else "Gemini"} (instructor compatibility)')
                raise Exception(f"Skipping instructor for {'Ollama' if is_ollama else 'Gemini'} compatibility")
            
            client = instructor.from_openai(
                provider.raw_client,
                mode=instructor.Mode.JSON,
            )
            result = client.chat.completions.create(
                model=provider.get_model_name(),
                response_model=LoanAgreementSchema,
                messages=messages,
                temperature=settings.EXTRACTION_TEMPERATURE,
                max_tokens=settings.EXTRACTION_MAX_TOKENS,
                max_retries=3,
            )
            print(f'✅ Instructor extraction succeeded')
            
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
                is_gemini = 'gemini' in provider.__class__.__name__.lower() or hasattr(provider, '_is_gemini')
                
                if (is_ollama or is_gemini) and hasattr(provider, 'generate_native'):
                    provider_name = 'Ollama' if is_ollama else 'Gemini'
                    print(f'Using {provider_name} native API for extraction...')
                    system_prompt = EXTRACTION_SYSTEM_PROMPT
                    user_prompt = user_message
                    
                    raw_text = provider.generate_native(
                        prompt=user_prompt,
                        system=system_prompt,
                        max_tokens=settings.EXTRACTION_MAX_TOKENS,
                        temperature=settings.EXTRACTION_TEMPERATURE
                    )
                else:
                    timeout = 120 if is_ollama else 60
                    
                    response = provider.raw_client.chat.completions.create(
                        model=provider.get_model_name(),
                        messages=messages,
                        temperature=settings.EXTRACTION_TEMPERATURE,
                        max_tokens=settings.EXTRACTION_MAX_TOKENS,
                        timeout=timeout,
                    )
                    raw_text = response.choices[0].message.content
                
                print(f'Raw LLM response (first 500 chars): {raw_text[:500]}')

                parsed = parse_llm_response(raw_text)
                print(f'Parsed dict keys: {list(parsed.keys())}')

                if parsed:
                    schema = LoanAgreementSchema(**parsed)
                    print(f'✅ Successfully parsed extraction response')
                    
                    is_valid, issues = validate_extraction_output(
                        parsed,
                        formatted,
                        warnings
                    )
                    
                    if not is_valid:
                        print(f'SECURITY: Output validation issues: {issues}')
                        warnings.extend(issues)
                    
                    return schema, warnings
                else:
                    print(f'⚠️  Parsed response is empty - LLM may have returned invalid JSON')
                    raise Exception("Empty JSON response from LLM")

            except Exception as e2:
                print(f'❌ Fallback also failed: {e2}')
                print(f'   Provider: {provider.__class__.__name__}')
                print(f'   Model: {provider.get_model_name()}')
                
                # Check for specific error types
                error_msg = str(e2)
                if '413' in error_msg or 'Payload Too Large' in error_msg or 'Request too large' in error_msg:
                    raise Exception(f"Contract size exceeds API limits for {provider.get_model_name()}. Please use a shorter document or upgrade your API tier.")
                elif '429' in error_msg or 'rate_limit' in error_msg.lower():
                    raise Exception(f"Rate limit exceeded for {provider.get_model_name()}. Please wait a few minutes and try again.")
                elif 'Connection error' in error_msg or 'Name or service not known' in error_msg:
                    raise Exception(f"Cannot connect to {provider.get_model_name()} API. Check your internet connection and API configuration.")
                else:
                    raise Exception(f"Extraction failed: {error_msg[:200]}")

    return RunnableLambda(_extract)