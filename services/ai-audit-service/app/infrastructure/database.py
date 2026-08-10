from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    from .models import AuditRecord

    Base.metadata.create_all(bind=engine)

    # Ensure the table exists even if the app imported models before the settings were ready.
    if settings.auto_migrate:
        Base.metadata.create_all(bind=engine)
