import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    key_encryption_secret: str = os.getenv("KEY_ENCRYPTION_SECRET", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
