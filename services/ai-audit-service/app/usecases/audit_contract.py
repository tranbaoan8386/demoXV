from __future__ import annotations

from app.domain.interfaces import IAuditEngine, IDocumentFetcher
from app.domain.models import Clause, ContractAudit
from app.infrastructure.repositories.audit_repository import AuditRepository


class AuditContractUseCase:
    def __init__(self, fetcher: IDocumentFetcher, engine: IAuditEngine, repository: AuditRepository) -> None:
        self._fetcher = fetcher
        self._engine = engine
        self._repository = repository

    async def execute(self, document_id: str, access_token: str | None = None, user_id: str | None = None) -> ContractAudit:
        if user_id:
            cached = self._repository.get_by_user_and_document(user_id=user_id, document_id=document_id)
            if cached is not None:
                return ContractAudit(
                    id=cached.id,
                    document_id=cached.document_id,
                    file_name=cached.file_name,
                    overall_risk_score=float(cached.overall_risk_score),
                    summary=cached.summary,
                    clauses=[
                    Clause.model_validate(item)
                    for item in (cached.clauses or [])
                ],
                    created_at=cached.created_at,
                )

        file_name, document_text = await self._fetcher.fetch_document_content(document_id, access_token=access_token)
        audit = await self._engine.analyze_contract(document_id, file_name, document_text)

        if user_id:
            self._repository.save(user_id=user_id, audit=audit)

        return audit

    def list_history(self, user_id: str) -> list[ContractAudit]:
        records = self._repository.list_by_user(user_id=user_id)
        return [
            ContractAudit(
                id=record.id,
                document_id=record.document_id,
                file_name=record.file_name,
                overall_risk_score=float(record.overall_risk_score),
                summary=record.summary,
                clauses=[
                    Clause.model_validate(item)
                    for item in (record.clauses or [])
                ],
                created_at=record.created_at,
            )
            for record in records
        ]
