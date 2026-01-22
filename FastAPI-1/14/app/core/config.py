from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """
    Application settings - সব configuration এক জায়গায়
    Environment variables থেকে automatically load হবে
    """
    # App Config
    APP_NAME: str = "AI Backend System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Security - JWT এর জন্য
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database - PostgreSQL connection
    DATABASE_URL: str
    
    # Cache - SQLite based (Redis replacement)
    CACHE_DB_PATH: str = "./data/cache.db"
    
    # Groq API - LLM এর জন্য
    GROQ_API_KEY: str
    GROQ_MODEL: str = "mixtral-8x7b-32768"
    
    # Vector DB - RAG এর জন্য
    VECTOR_DB_PATH: str = "./data/vector_store"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.CACHE_DB_PATH), exist_ok=True)
        os.makedirs(self.VECTOR_DB_PATH, exist_ok=True)
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

@lru_cache()
def get_settings() -> Settings:
    """
    Settings singleton - একবার load করে cache করে রাখবে
    Dependency injection এ use করবো
    """
    return Settings()