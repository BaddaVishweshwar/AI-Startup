from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Business Analytics AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./analytics.db"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-r1:latest"  # Best reasoning model (strong instruction following)
    OLLAMA_TIMEOUT: int = 120
    
    # Gemini
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash-001"
    GOOGLE_CLIENT_ID: Optional[str] = "951242114092-v8s1mbdf81sjr9oian032ag0jckmfsgk.apps.googleusercontent.com"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_API_BASE: Optional[str] = "https://models.inference.ai.azure.com" # Default to GitHub Models for hex keys, or can be overridden
    
    
    # Email Configuration
    GMAIL_USER: Optional[str] = None
    GMAIL_APP_PASSWORD: Optional[str] = None
    EMAIL_FROM_NAME: str = "AI Data Analyst"
    RESET_PASSWORD_URL: str = "http://localhost:5174/reset-password"
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    VECTOR_DB_DIR: str = "./vector_db"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: set = {".csv", ".xlsx", ".xls", ".sas7bdat", ".parquet"}
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
