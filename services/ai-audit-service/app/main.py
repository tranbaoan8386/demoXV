from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import router
from app.domain.exceptions import AuditEngineError, DocumentNotFoundError
from app.infrastructure.database import init_db

app = FastAPI(title="DemoXV AI Audit Service")


@app.on_event("startup")
def startup() -> None:
    init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(DocumentNotFoundError)
async def document_not_found_handler(_: Request, exc: DocumentNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(AuditEngineError)
async def audit_engine_error_handler(_: Request, exc: AuditEngineError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(exc)})


app.include_router(router)
