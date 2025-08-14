from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from common.config import AppConfig


config = AppConfig()

dsn = (
    f"postgresql+psycopg://{config.postgres_user}:{config.postgres_password}"
    f"@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}"
)

engine = create_engine(dsn, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

__all__ = ["engine", "SessionLocal", "Base"]


