from __future__ import annotations

import base64
import json

import jwt
from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.schemas import AuditContractRequest, AuditHistoryResponse
from app.domain.models import ContractAudit
from app.infrastructure.config import get_settings
from app.infrastructure.database import SessionLocal, init_db
from app.infrastructure.doc_processor_client import DocProcessorClient
from app.infrastructure.gemini_audit_engine import GeminiAuditEngine
from app.infrastructure.repositories.audit_repository import AuditRepository
from app.usecases.audit_contract import AuditContractUseCase

router = APIRouter(prefix="/api/v1", tags=["audit"])
security = HTTPBearer(auto_error=False)


def _extract_user_id_from_token(token: str | None) -> str | None:
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token[7:]

    parts = token.split(".")
    if len(parts) < 2:
        return None

    payload_segment = parts[1]
    payload_segment += "=" * (-len(payload_segment) % 4)
    try:
        payload = json.loads(base64.urlsafe_b64decode(payload_segment.encode("utf-8")).decode("utf-8"))
    except Exception:
        return None

    for key in ("sub", "user_id", "userId", "id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def get_audit_use_case() -> AuditContractUseCase:
    settings = get_settings()
    fetcher = DocProcessorClient(settings=settings)
    engine = GeminiAuditEngine(settings=settings)
    session = SessionLocal()
    repository = AuditRepository(session=session)
    return AuditContractUseCase(fetcher=fetcher, engine=engine, repository=repository)


def get_db_session() -> Session:
    init_db()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.post("/audit/contract", response_model=ContractAudit)
async def audit_contract(
    payload: AuditContractRequest,
    request: Request,
    auth: HTTPAuthorizationCredentials | None = Depends(security),
    use_case: AuditContractUseCase = Depends(get_audit_use_case),
) -> ContractAudit:
    access_token = request.headers.get("authorization")
    if auth and auth.credentials:
        access_token = f"Bearer {auth.credentials}"

    user_id = None
    if auth and auth.credentials:
        user_id = _extract_user_id_from_token(auth.credentials)

    return await use_case.execute(payload.document_id, access_token=access_token, user_id=user_id)


@router.get("/audit/history", response_model=AuditHistoryResponse)
async def audit_history(
    request: Request,
    auth: HTTPAuthorizationCredentials | None = Depends(security),
    use_case: AuditContractUseCase = Depends(get_audit_use_case),
) -> AuditHistoryResponse:
    if not auth or not auth.credentials:
        return AuditHistoryResponse(success=True, data=[])

    user_id = _extract_user_id_from_token(auth.credentials)
    history = use_case.list_history(user_id or "")
    return AuditHistoryResponse(success=True, data=history)
