from __future__ import annotations

from abc import ABC, abstractmethod

from .models import ContractAudit


class IDocumentFetcher(ABC):
    @abstractmethod
    async def fetch_document_content(self, document_id: str, access_token: str | None = None) -> tuple[str, str]:
        """Fetch document metadata and extracted text by document ID."""
        raise NotImplementedError


class IAuditEngine(ABC):
    @abstractmethod
    async def analyze_contract(self, document_id: str, file_name: str, document_text: str) -> ContractAudit:
        """Analyze contract text and return a domain audit result."""
        raise NotImplementedError
