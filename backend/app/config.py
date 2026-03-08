# backend/config.py
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

class Settings:
    """Application settings loaded from .env"""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "claude_analytics")
    DB_USER: str = os.getenv("DB_USER", "anjamisan")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "claude_password")
    
    # FastAPI Configuration
    FASTAPI_ENV: str = os.getenv("FASTAPI_ENV", "development")
    FASTAPI_DEBUG: bool = os.getenv("FASTAPI_DEBUG", "False").lower() == "true"
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Streamlit Configuration
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    STREAMLIT_SERVER_HEADLESS: bool = os.getenv("STREAMLIT_SERVER_HEADLESS", "true").lower() == "true"
    
    # Application Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-in-production")

# Create settings instance
settings = Settings()