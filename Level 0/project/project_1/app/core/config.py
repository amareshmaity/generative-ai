import os
from dataclasses import dataclass


@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "Level 1 Project 1 API")
    api_key: str = os.getenv("API_KEY", "level1-secret-key")
    default_model: str = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
