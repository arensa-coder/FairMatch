from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/fairmatch"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # App
    app_name: str = "FairMatch API"
    debug: bool = False
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["http://localhost:3000"]

    # Encryption (AES-256 for sensitive fields)
    field_encryption_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Email
    sendgrid_api_key: str = ""
    from_email: str = "noreply@fairmatch.com"

    # SMS
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # Google Maps (Distance Matrix API for commute scoring)
    google_maps_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
