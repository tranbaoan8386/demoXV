from __future__ import annotations

import datetime as dt
from typing import Any

from sqlalchemy import JSON, String, Text, Double, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class AuditRecord(Base):
    __tablename__ = "audit_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(dt.datetime.now(dt.timezone.utc).timestamp()))
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    overall_risk_score: Mapped[float] = mapped_column(Double, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    clauses: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: dt.datetime.now(dt.timezone.utc))
