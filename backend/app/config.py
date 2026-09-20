"""
Application configuration for ReelTranscribe.
"""
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "ReelTranscribe"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # Security & Auth
    API_SECRET: str = ""
    ALLOWED_HOSTS: List[str] = Field(default_factory=lambda: ["*"])
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    # File & Processing Limits
    MAX_FILE_SIZE_MB: int = 100
    MAX_DURATION_SECONDS: int = 300
    RATE_LIMIT_PER_MINUTE: int = 30
    TEMP_DIR: Path = Path("temp")

    # ASR Providers
    SARVAM_API_KEY: str = ""
    SARVAM_ENABLED: bool = True
    SARVAM_MODEL: str = "saaras:v4"
    SARVAM_MODE: str = "codemix"  # codemix | transcribe | verbatim

    HF_TOKEN: str = ""
    HF_ENABLED: bool = True
    WHISPER_MODEL: str = "openai/whisper-large-v3"
    HINGLISH_MODEL: str = "Oriserve/Whisper-Hindi2Hinglish-Prime"

    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_ENABLED: bool = False

    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GOOGLE_ENABLED: bool = False

    OPENAI_API_KEY: str = ""
    OPENAI_ENABLED: bool = False

    # Quality Gate Thresholds
    MIN_CONFIDENCE_THRESHOLD: float = 0.65
    MAX_REPETITION_RATIO: float = 0.35

    # Caption Detection
    CAPTION_OCR_SAMPLE_FPS: float = 1.0
    CAPTION_CONFIDENCE_THRESHOLD: float = 0.50


settings = Settings()
