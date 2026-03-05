import os


def _normalize_database_url(raw_url: str | None) -> str | None:
    if not raw_url:
        return None
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return raw_url


class Config:
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.getenv("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    DEBUG = False
