from __future__ import annotations

from typing import Sequence

from sqlalchemy.orm import Session

from app.domain.models import ContractAudit
from app.infrastructure.models import AuditRecord


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_user_and_document(self, *, user_id: str, document_id: str) -> AuditRecord | None:
        return (
            self._session.query(AuditRecord)
            .filter(AuditRecord.user_id == user_id, AuditRecord.document_id == document_id)
            .order_by(AuditRecord.created_at.desc())
            .first()
        )

    def list_by_user(self, *, user_id: str) -> Sequence[AuditRecord]:
        return (
            self._session.query(AuditRecord)
            .filter(AuditRecord.user_id == user_id)
            .order_by(AuditRecord.created_at.desc())
            .all()
        )

    def save(self, *, user_id: str, audit: ContractAudit) -> AuditRecord:
        record = AuditRecord(
            id=audit.id,
            user_id=user_id,
            document_id=audit.document_id,
            file_name=audit.file_name,
            overall_risk_score=audit.overall_risk_score,
            summary=audit.summary,
            clauses=[clause.model_dump() for clause in audit.clauses],
            created_at=audit.created_at,
        )
        self._session.add(record)
        self._session.commit()
        self._session.refresh(record)
        return record

    def get_audit_by_document_id(self, *, document_id: str, user_id: str | None = None) -> AuditRecord | None:
        query = self._session.query(AuditRecord).filter(AuditRecord.document_id == document_id)
        if user_id:
            query = query.filter(AuditRecord.user_id == user_id)
        return query.order_by(AuditRecord.created_at.desc()).first()
