from __future__ import annotations

from typing import List

from pydantic import BaseModel

from app.domain.models import ContractAudit


class AuditContractRequest(BaseModel):
    document_id: str


class AuditHistoryResponse(BaseModel):
    success: bool
    data: List[ContractAudit]
