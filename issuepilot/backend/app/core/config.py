from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./issuepilot.db"
    github_token: str | None = None
    github_webhook_secret: str = "change-me"
    openai_api_key: str | None = None
    openai_model: str | None = None
    cors_origins: str = "http://localhost:5173"
    duplicate_threshold: float = 0.55
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
