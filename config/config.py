from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    app_name: str = "AI Rent Analysis"
    debug_mode: bool = True
    environment: str = "development"
    anthropic_api_key: SecretStr
    db_name: SecretStr
    db_password: SecretStr

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")


settings = Settings()
