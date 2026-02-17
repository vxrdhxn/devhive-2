"""
Configuration management for KTP Enterprise MVP
Loads settings from environment variables with validation
"""

from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database configuration
    database_url: PostgresDsn = Field(
        default="postgresql+pg8000://ktp_user:ktp_password@localhost:5432/ktp_db",
        description="PostgreSQL connection URL"
    )
    db_pool_size: int = Field(
        default=20,
        description="Database connection pool size"
    )
    db_max_overflow: int = Field(
        default=10,
        description="Maximum overflow connections beyond pool size"
    )
    db_pool_timeout: int = Field(
        default=30,
        description="Timeout for getting connection from pool (seconds)"
    )
    db_pool_recycle: int = Field(
        default=3600,
        description="Recycle connections after this many seconds"
    )
    
    # Authentication
    jwt_secret: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    jwt_expiration_hours: int = Field(
        default=24,
        description="JWT token expiration time in hours"
    )
    
    # Groq API
    groq_api_key: Optional[str] = Field(
        default=None,
        description="Groq API key for LLM inference"
    )
    groq_model: str = Field(
        default="llama3-70b-8192",
        description="Groq model to use"
    )
    groq_timeout_seconds: int = Field(
        default=30,
        description="Timeout for Groq API calls"
    )
    
    # File Upload
    max_file_size_mb: int = Field(
        default=50,
        description="Maximum file size for uploads in MB"
    )
    upload_dir: str = Field(
        default="/tmp/uploads",
        description="Directory for temporary file uploads"
    )
    
    # Embedding Model
    embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description="SentenceTransformer model name"
    )
    embedding_batch_size: int = Field(
        default=32,
        description="Batch size for embedding generation"
    )
    
    # Search
    search_top_k: int = Field(
        default=5,
        description="Number of top results to return"
    )
    search_min_similarity: float = Field(
        default=0.3,
        description="Minimum similarity threshold for search results"
    )
    
    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: str = Field(
        default="json",
        description="Log format (json or text)"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
