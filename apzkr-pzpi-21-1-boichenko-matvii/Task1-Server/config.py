from __future__ import annotations

import os
import secrets
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib.parse import quote

from pydantic import PostgresDsn, AnyHttpUrl, field_validator, model_validator
from pydantic_core.core_schema import ValidatorFunctionWrapHandler, ValidationInfo
from pydantic_settings import BaseSettings
from sqlalchemy import URL


class ModeEnum(StrEnum):
    development = "development"
    production = "production"
    testing = "testing"


class Settings(BaseSettings):
    MODE: ModeEnum = ModeEnum.development
    DEBUG: bool = MODE == ModeEnum.development
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    PROJECT_NAME: str = 'DrinkPointAPI'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 1  # 1 hour
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 100  # 100 days
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int | str
    DATABASE_NAME: str
    DATABASE_SCHEMA: str
    DB_POOL_SIZE: int = 8
    WEB_CONCURRENCY: int = 5
    POOL_SIZE: int = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)
    ASYNC_DATABASE_URI: str | None
    SYNC_DATABASE_URI: URL | None
    PASSWORD_TOKEN_SECRET: str = 'Qwerty1234'
    VERIFICATION_TOKEN_SECRET: str = 'Qwerty1234'
    JWT_SECRET: str = 'Qwerty1234567890'
    API_HASH_SECRET_KEY: str = 'BEdQVei3kmWJGhu4qn5uncL8VXjER8'

    MQTT_USER: str | None = None
    MQTT_PASS: str | None = None
    MQTT_BROKER_HOST: str | None = None
    MQTT_BROKER_PORT: int = 1883

    @field_validator("DATABASE_PASSWORD", mode="before")
    @classmethod
    def validate_password(cls, v: str):
        encoded_string = quote(v)
        return encoded_string

    @model_validator(mode="wrap")
    @classmethod
    def assemble_async_db_connection(cls, data: dict[str, Any] | "Settings", handler: ValidatorFunctionWrapHandler,
                                     info: ValidationInfo) -> Any:
        values = data if isinstance(data, dict) else data.model_dump()

        async_dsn = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            host=values.get("DATABASE_HOST"),
            port=int(values.get("DATABASE_PORT")),
            path=values.get('DATABASE_NAME'),
            # query={"server_settings.search_path": f"{values['DATABASE_SCHEMA']}"}
            # query={"search_path": values.get("DATABASE_SCHEMA")}
            #{"server_settings": {"search_path": values.get("DATABASE_SCHEMA")}}#f"search_path%3D%3D{values['DATABASE_SCHEMA']}"}
        )
        # {"search_path": values.get("DATABASE_SCHEMA")}}
        # print("async_dsn", async_dsn)
        sync_dsn = URL.create(
            drivername="postgresql+psycopg2",
            username=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            host=values.get("DATABASE_HOST"),
            port=int(values.get("DATABASE_PORT")),
            database=values.get('DATABASE_NAME'),
            query={"options": f"-c search_path={values['DATABASE_SCHEMA']}"}
        )
        # print("sync_dsn", sync_dsn)

        if isinstance(data, dict):
            data["ASYNC_DATABASE_URI"] = str(async_dsn)
            data["SYNC_DATABASE_URI"] = sync_dsn
        else:
            data.ASYNC_DATABASE_URI = str(async_dsn)
            data.SYNC_DATABASE_URI = sync_dsn

        return handler(data)

    # SECRET_KEY: str = secrets.token_urlsafe(32)
    # ENCRYPT_KEY: str = secrets.token_urlsafe(32)
    # BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl] = []

    # @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    # @classmethod
    # def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
    #     if isinstance(v, str) and not v.startswith("["):
    #         return [i.strip() for i in v.split(",")]
    #     elif isinstance(v, (list, str)):
    #         return v
    #     raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = os.path.join(f"{os.path.abspath(Path(__file__).parent)}", ".env")


settings = Settings()
