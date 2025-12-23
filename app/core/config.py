from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Database
    DATABASE_URL: str
    
    # JWT Settings
    SECRET_KEY: str = '67f79f54a85671dce02e3d8c3fc5e0b2'
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000","http://127.0.0.1:3000","https://eygar.com"
    
    # Service
    SERVICE_NAME: str = "eygar-payment-service"

    AUTH_SERVICE_URL: str = os.getenv('AUTH_SERVICE_URL', "http://127.0.0.1:8000/api/v1/auth")
    JWT_SECRET_KEY: str = "abcdefgh"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
