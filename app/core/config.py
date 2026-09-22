"""
Sana application configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Sana AI"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Gemini
    gemini_api_key: str

    # Supabase
    supabase_url: str
    supabase_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
