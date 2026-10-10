import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "Level 1 Project 2 Upload API")
    api_key: str = os.getenv("API_KEY", "level1-upload-key")
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", str(2 * 1024 * 1024)))


settings = Settings()
