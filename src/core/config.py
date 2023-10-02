import os
from functools import lru_cache
from typing import Optional

from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Todo: complete documentation
# ---------------------------------------------------------------------------
class Setting(BaseSettings):
    # App config
    APP_NAME: str
    OPENAPI_URL: str

    # Database config
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    DATABASE_URL: PostgresDsn | None = None

    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_HOURS: int
    TERMINAL_EXPIRE_MINUTES: int
    DYNAMIC_PASSWORD_EXPIRE_MINUTES: int

    # Admin info
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ADMIN_NATIONAL_CODE: str

    # Minio settings
    MINIO_URL: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_DEFAULT_BUCKET: str
    MINIO_SITE_MEDIA_BUCKET: str
    MINIO_PROFILE_IMAGE_BUCKET: str

    # SMS settings
    KAVENEGAR_TOKEN: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: Optional[str], values: ValidationInfo):
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data["POSTGRES_USER"],
            password=values.data["POSTGRES_PASSWORD"],
            host=values.data["POSTGRES_HOST"],
            path=f"{values.data['POSTGRES_DB'] or ''}",
        )


# ---------------------------------------------------------------------------
class DevSetting(Setting):
    model_config = SettingsConfigDict(
        env_file=".env.sample",
        case_sensitive=True,
        env_file_encoding="utf-8",
    )


# ---------------------------------------------------------------------------
class ProdSetting(Setting):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding="utf-8",
    )


# ---------------------------------------------------------------------------
@lru_cache
def get_settings() -> Setting:
    setting_dict = {"Development": DevSetting, "Production": ProdSetting}
    environment = os.environ.get("APP_ENV", "Development")
    setting_class = setting_dict.get(environment)
    return setting_class()


# ---------------------------------------------------------------------------
settings: Setting = get_settings()
