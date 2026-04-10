from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "geocoding-service"
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8080, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    mapbox_access_token: str = Field(default="", alias="MAPBOX_ACCESS_TOKEN")
    mapbox_geocoding_base_url: str = Field(
        default="https://api.mapbox.com/geocoding/v5/mapbox.places", alias="MAPBOX_GEOCODING_BASE_URL"
    )
    http_timeout_seconds: float = Field(default=5.0, alias="HTTP_TIMEOUT_SECONDS")

    default_country_code: str = Field(default="IL", alias="DEFAULT_COUNTRY_CODE")

    geocoding_cache_enabled: bool = Field(default=True, alias="GEOCODING_CACHE_ENABLED")
    geocoding_cache_ttl_seconds: int = Field(default=86400, alias="GEOCODING_CACHE_TTL_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
