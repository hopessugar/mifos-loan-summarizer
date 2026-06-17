import yaml
import os
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

backend_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
root_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

if os.path.exists(backend_env):
    load_dotenv(backend_env)
    print(f'Loaded environment from: {backend_env}')
elif os.path.exists(root_env):
    load_dotenv(root_env)
    print(f'Loaded environment from: {root_env}')
else:
    print('No .env file found, using system environment variables only')


def _load_yaml() -> dict:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, 'config.yaml')
    print(f'Loading config from: {path}')
    if os.path.exists(path):
        with open(path, encoding='utf-8-sig') as f:
            data = yaml.safe_load(f) or {}
            print(f'Config loaded: primary={data.get("llm", {}).get("primary")}')
            
            # WARNING: Detect secrets in YAML configuration
            secret_warnings = _detect_secrets_in_yaml(data)
            if secret_warnings:
                print('\n' + '='*80)
                print('SECURITY WARNING: Secrets detected in config.yaml!')
                print('='*80)
                for warning in secret_warnings:
                    print(f'  ⚠️  {warning}')
                print('\nRECOMMENDATION: Use environment variables instead:')
                print('  - Set secrets via: export SECRET_NAME=value')
                print('  - Or use .env file (see backend/.env.example)')
                print('  - Remove secrets from config.yaml')
                print('='*80 + '\n')
            
            return data
    print('WARNING: config.yaml not found!')
    return {}


def _detect_secrets_in_yaml(yaml_data: dict) -> list[str]:
    warnings = []
    
    secret_fields = {
        'hf_token': ['', 'YOUR_HF_TOKEN_HERE', 'YOUR_TOKEN_HERE'],
        'fineract_password': ['', 'password'],
        'groq_api_key': [''],
        'cerebras_api_key': [''],
        'api_key': ['', 'your-secret-api-key-here', 'your-api-key-here'],
    }
    
    for field, placeholders in secret_fields.items():
        value = yaml_data.get(field, '')
        if value and value not in placeholders:
            env_var = field.upper()
            warnings.append(f'{field} found in YAML (use {env_var} environment variable instead)')
    
    return warnings


_yaml = _load_yaml()


class Settings(BaseSettings):
    LLM_PRIMARY: str = Field(default_factory=lambda: os.getenv('LLM_PRIMARY') or _yaml.get('llm', {}).get('primary', 'groq'))
    LLM_MODEL: str = Field(default_factory=lambda: os.getenv('LLM_MODEL') or _yaml.get('llm', {}).get('model', 'llama-3.1-8b-instant'))
    LLM_FALLBACK: str = Field(default_factory=lambda: os.getenv('LLM_FALLBACK') or _yaml.get('llm', {}).get('fallback', ''))
    LLM_FALLBACK_MODEL: str = Field(default_factory=lambda: os.getenv('LLM_FALLBACK_MODEL') or _yaml.get('llm', {}).get('fallback_model', 'llama3.1-8b'))

    # API Keys - prioritize environment variables
    HF_TOKEN: str = Field(default_factory=lambda: os.getenv('HF_TOKEN') or os.getenv('HF_API_KEY') or _yaml.get('hf_token', ''))
    GROQ_API_KEY: str = Field(default_factory=lambda: os.getenv('GROQ_API_KEY') or _yaml.get('groq_api_key', ''))
    CEREBRAS_API_KEY: str = Field(default_factory=lambda: os.getenv('CEREBRAS_API_KEY') or _yaml.get('cerebras_api_key', ''))
    GEMINI_API_KEY: str = Field(default_factory=lambda: os.getenv('GEMINI_API_KEY') or _yaml.get('gemini_api_key', ''))

    # Ollama Configuration
    OLLAMA_BASE_URL: str = Field(default_factory=lambda: os.getenv('OLLAMA_BASE_URL') or _yaml.get('ollama_base_url', 'http://localhost:11434'))
    OLLAMA_MODEL: str = Field(default_factory=lambda: os.getenv('OLLAMA_MODEL') or _yaml.get('ollama_model', 'qwen2.5:7b'))

    # Fineract Configuration
    FINERACT_URL: str = Field(default_factory=lambda: os.getenv('FINERACT_URL') or _yaml.get('fineract_url', ''))
    FINERACT_USER: str = Field(default_factory=lambda: os.getenv('FINERACT_USER') or _yaml.get('fineract_user', 'mifos'))
    FINERACT_PASSWORD: str = Field(default_factory=lambda: os.getenv('FINERACT_PASSWORD') or _yaml.get('fineract_password', 'password'))
    FINERACT_TENANT: str = Field(default_factory=lambda: os.getenv('FINERACT_TENANT') or _yaml.get('fineract_tenant', 'default'))
    FINERACT_SSL_VERIFY: bool = Field(default_factory=lambda: os.getenv('FINERACT_SSL_VERIFY', '').lower() not in ('false', '0', 'no') if os.getenv('FINERACT_SSL_VERIFY') else _yaml.get('fineract_ssl_verify', True))
    FINERACT_CA_BUNDLE: str = Field(default_factory=lambda: os.getenv('FINERACT_CA_BUNDLE') or _yaml.get('fineract_ca_bundle', ''))

    # Validation Thresholds
    LEVENSHTEIN_THRESHOLD: float = Field(default_factory=lambda: float(os.getenv('LEVENSHTEIN_THRESHOLD') or 0) or _yaml.get('levenshtein_threshold', 0.80))
    COSINE_THRESHOLD: float = Field(default_factory=lambda: float(os.getenv('COSINE_THRESHOLD') or 0) or _yaml.get('cosine_threshold', 0.80))
    MATH_TOLERANCE: float = Field(default_factory=lambda: float(os.getenv('MATH_TOLERANCE') or 0) or _yaml.get('math_tolerance', 0.10))
    CONFIDENCE_THRESHOLD: float = Field(default_factory=lambda: float(os.getenv('CONFIDENCE_THRESHOLD') or 0) or _yaml.get('confidence_threshold', 0.50))

    # Pipeline Configuration
    USE_SEMANTIC_CHUNKING: bool = Field(default_factory=lambda: os.getenv('USE_SEMANTIC_CHUNKING', '').lower() in ('true', '1', 'yes') if os.getenv('USE_SEMANTIC_CHUNKING') else _yaml.get('use_semantic_chunking', False))
    MAX_SEGMENT_TOKENS: int = Field(default_factory=lambda: int(os.getenv('MAX_SEGMENT_TOKENS') or 0) or _yaml.get('max_segment_tokens', 200))
    MAX_INPUT_CHARS: int = Field(default_factory=lambda: int(os.getenv('MAX_INPUT_CHARS') or 0) or _yaml.get('max_input_chars', 8000))
    EXTRACTION_MAX_TOKENS: int = Field(default_factory=lambda: int(os.getenv('EXTRACTION_MAX_TOKENS') or 0) or _yaml.get('extraction_max_tokens', 1500))
    SUMMARY_MAX_TOKENS: int = Field(default_factory=lambda: int(os.getenv('SUMMARY_MAX_TOKENS') or 0) or _yaml.get('summary_max_tokens', 600))
    EXTRACTION_TEMPERATURE: float = Field(default_factory=lambda: float(os.getenv('EXTRACTION_TEMPERATURE') or 0) or _yaml.get('extraction_temperature', 0.1))

    API_KEY: str = os.getenv('API_KEY', _yaml.get('api_key', ''))
    API_KEY_HEADER_NAME: str = os.getenv('API_KEY_HEADER_NAME', _yaml.get('api_key_header_name', 'X-API-Key'))

    class Config:
        extra = 'ignore'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # WARNING: Prevent SSL verification bypass in production
        import os
        environment = os.getenv('ENVIRONMENT', 'development').lower()
        if environment == 'production' and not self.FINERACT_SSL_VERIFY:
            raise ValueError(
                'CRITICAL SECURITY ERROR: SSL verification cannot be disabled in production. '
                'Set FINERACT_SSL_VERIFY=true or remove the setting to use secure default.'
            )
        
        # WARNING: Require API key in production
        if environment == 'production' and not self.API_KEY:
            raise ValueError(
                'CRITICAL SECURITY ERROR: API_KEY must be set in production. '
                'Set API_KEY environment variable or add api_key to config.yaml.'
            )


settings = Settings()
print(f'Settings initialized: LLM_PRIMARY={settings.LLM_PRIMARY}, LLM_MODEL={settings.LLM_MODEL}')
print(f'Fineract SSL verification: {"ENABLED" if settings.FINERACT_SSL_VERIFY else "DISABLED (development only)"}')
print(f'API authentication: {"ENABLED" if settings.API_KEY else "DISABLED (development only)"}')