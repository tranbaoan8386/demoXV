from __future__ import annotations

import datetime
from typing import List

from pydantic import BaseModel

from .enums import RiskLevel


class Clause(BaseModel):
    title: str
    content: str
    risk_level: RiskLevel
    risk_description: str
    recommendation: str


class ContractAudit(BaseModel):
    id: str
    document_id: str
    file_name: str
    overall_risk_score: float
    summary: str
    clauses: List[Clause]
    created_at: datetime.datetime
