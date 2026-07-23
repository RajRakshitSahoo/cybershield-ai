"""
Centralized application configuration.
Reads from environment variables / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CyberShield AI"
    environment: str = "development"

    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "cybershield"
    use_mock_db: bool = True

    frontend_origin: str = "http://localhost:5173"

    virustotal_api_key: str = ""
    google_safe_browsing_api_key: str = ""
    abuseipdb_api_key: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_from_email: str = "alerts@cybershield.ai"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
