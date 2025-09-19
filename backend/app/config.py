from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str = "http://localhost:8000/auth/callback"
    
    # JWT Configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "sqlite:///./app.db"
    
    # Application
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Google OAuth URLs
    google_auth_url: str = "https://accounts.google.com/o/oauth2/auth"
    google_token_url: str = "https://oauth2.googleapis.com/token"
    google_user_info_url: str = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()