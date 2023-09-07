"""
Config load from environment.
"""

import os
from dataclasses import dataclass
from typing import Optional

import dotenv
from pydantic_settings import BaseSettings

dotenv.load_dotenv()


class DbConfig(BaseSettings):
    DB_USER: str | None = os.environ.get("DB_USER")
    DB_PASS: str | None = os.environ.get("DB_PASS")
    DB_HOST: str | None = os.environ.get("DB_HOST")
    DB_PORT: str | None = os.environ.get("DB_PORT")
    DB_NAME: str | None = os.environ.get("DB_NAME")

    DATABASE_URL: str = (
        f"postgresql+asyncpg://"
        f"{DB_USER}:"
        f"{DB_PASS}@"
        f"{DB_HOST}:"
        f"{DB_PORT}/"
        f"{DB_NAME}"
    )


@dataclass
class Config:
    db: DbConfig


def load_config():
    return Config(db=DbConfig())
