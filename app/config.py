from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "UniCrypt"
    environment: str = "development"
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite:///./unicrypt.db"
    cookie_secure: bool = True
    cookie_samesite: str = "none"
    upload_dir: str = "uploads"
    max_upload_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
