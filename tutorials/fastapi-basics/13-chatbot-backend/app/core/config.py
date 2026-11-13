from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "AI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost/aidb"
    
    # SQLite for caching and sessions
    CACHE_DB_PATH: str = "./data/cache.db"
    SESSION_DB_PATH: str = "./data/sessions.db"
    RATE_LIMIT_DB_PATH: str = "./data/rate_limit.db"
    
    # Vector DB
    VECTOR_DB_PATH: str = "./vector_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Groq API
    GROQ_API_KEY: str
    GROQ_MODEL: str = "mixtral-8x7b-32768"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()