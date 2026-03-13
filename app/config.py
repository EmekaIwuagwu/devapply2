import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "DevApply"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database & Caching
    # Falls back to SQLite so the app starts even without a PostgreSQL URL.
    # Set DATABASE_URL in Render → Environment to use a real database.
    DATABASE_URL: str = "sqlite+aiosqlite:///./devapply.db"
    REDIS_URL: str = "sqla+sqlite:///./celery_broker.db"
    DATABASE_ECHO: bool = False

    # Celery
    CELERY_BROKER_URL: str = "sqla+sqlite:///./celery_broker.db"
    CELERY_RESULT_BACKEND: str = "db+sqlite:///./celery_results.db"

    # JWT & Security
    # Set JWT_SECRET_KEY in Render → Environment with a strong random value.
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 7

    # Ollama
    OLLAMA_API_URL: str = "http://localhost:11434"
    OLLAMA_MODEL_NAME: str = "llama2"
    OLLAMA_FAST_MODEL: str = "mistral"
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_NUM_PREDICT: int = 256

    # Hugging Face
    HF_TRANSFORMERS_CACHE: str = "./.cache/huggingface"
    HF_OCR_MODEL: str = "distilbert-base-uncased"
    HF_EMBEDDINGS_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Storage
    STORAGE_PATH: str = "./storage/resumes"
    MAX_RESUME_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = "pdf,docx,doc"

    # Playwright
    PLAYWRIGHT_TIMEOUT_MS: int = 30000
    USE_HEADLESS_BROWSER: bool = True
    BROWSER_VIEWPORT_WIDTH: int = 1920
    BROWSER_VIEWPORT_HEIGHT: int = 1080
    ENABLE_STEALTH_MODE: bool = True
    BROWSER_LAUNCH_ARGS: str = "--no-sandbox,--disable-gpu"

    # Bot Detection
    MIN_DELAY_BETWEEN_ACTIONS_SEC: int = 1
    MAX_DELAY_BETWEEN_ACTIONS_SEC: int = 5
    RANDOMIZE_USER_AGENT: bool = True
    ROTATE_PROXIES: bool = False
    PROXY_LIST: Optional[str] = None

    # Agent
    MAX_APPLICATIONS_PER_RUN: int = 10
    MAX_DAILY_APPLICATIONS: int = 50
    AGENT_EXECUTION_TIMEOUT_MINUTES: int = 60
    ENABLE_AGENT_LOGGING: bool = True
    AGENT_LOG_PATH: str = "./logs/agents.log"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
