"""
Configuration management for KTP Enterprise MVP
Loads settings from environment variables with validation
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Supabase Configuration
    supabase_url: Optional[str] = Field(
        default=None,
        description="URL for the Supabase project"
    )
    supabase_service_role_key: Optional[str] = Field(
        default=None,
        description="Service role key for Supabase admin operations"
    )

    # Embedding Configuration
    embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description="SentenceTransformer or HuggingFace model name"
    )
    huggingface_api_key: Optional[str] = Field(
        default=None,
        description="API key for HuggingFace Inference API (Optional but recommended to avoid rate limits)"
    )
    embedding_batch_size: int = Field(
        default=32,
        description="Batch size for generating embeddings"
    )

    # Database configuration
    database_url: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection URL"
    )
    
    # Groq API
    groq_api_key: Optional[str] = Field(
        default=None,
        description="Groq API key for LLM inference"
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model to use"
    )
    
    # CORS
    cors_origins: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # Logging
    log_level: str = Field(
        default="DEBUG",
        description="Logging level"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
try:
    settings = Settings()
    # Check for missing critical settings
    missing = []
    if not settings.supabase_url: missing.append("SUPABASE_URL")
    if not settings.supabase_service_role_key: missing.append("SUPABASE_SERVICE_ROLE_KEY")
    if not settings.database_url: missing.append("DATABASE_URL")
    
    if missing:
        print(f"\n[!] WARNING: The following required environment variables are MISSING: {', '.join(missing)}")
        print("[!] The application may fail to function correctly until these are set in Render/Vercel.\n")
except Exception as e:
    print(f"\n[!] ERROR: Failed to load settings: {e}")
    # Still create a partial settings object to avoid crashing the whole import
    settings = Settings.model_construct()

def get_settings() -> Settings:
    """Get application settings"""
    return settings
