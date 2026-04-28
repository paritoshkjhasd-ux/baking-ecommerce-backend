"""
app/core/config.py
------------------
Centralised configuration loaded from the .env file.
Uses pydantic-settings so every value is type-checked at startup.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────
    APP_NAME: str = "Baking E-Commerce API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── MongoDB ───────────────────────────────────────────────
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "baking_ecommerce"

    # ── JWT ───────────────────────────────────────────────────
    SECRET_KEY: str = "dev-secret-key-change-this-before-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── CORS ──────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Return ALLOWED_ORIGINS as a Python list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    The @lru_cache decorator ensures the .env file is only
    read once for the lifetime of the application process.
    """
    return Settings()


# Convenience shortcut used throughout the app
settings = get_settings()
