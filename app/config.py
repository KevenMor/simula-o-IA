"""Configuration management using environment variables."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ValidationError


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: str
    anthropic_api_key: Optional[str] = None
    
    # Supabase (opcional - pode usar PostgreSQL direto)
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # PostgreSQL direto (alternativa ao Supabase)
    postgres_host: Optional[str] = None
    postgres_port: int = 5432
    postgres_db: Optional[str] = None
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    
    # App Config
    api_key_n8n: str
    environment: str = "development"
    log_level: str = "INFO"
    
    # Model Settings
    default_llm_model: str = "gpt-4-turbo"
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    
    # Cache Settings
    cache_ttl_seconds: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


def _load_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        err = str(e)
        if "api_key_n8n" in err.lower() or "API_KEY_N8N" in err:
            raise RuntimeError(
                "Configure API_KEY_N8N nas variáveis de ambiente (EasyPanel). "
                "Ex.: API_KEY_N8N=sua_chave_secreta"
            ) from e
        raise


# Global settings instance
settings = _load_settings()
