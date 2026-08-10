from __future__ import annotations

import httpx
from urllib.parse import quote

from app.domain.exceptions import DocumentNotFoundError
from app.domain.interfaces import IDocumentFetcher

from .config import Settings, get_settings


class DocProcessorClient(IDocumentFetcher):
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._base_url = self._settings.doc_processor_url.rstrip("/")

    async def fetch_document_content(self, document_id: str, access_token: str | None = None) -> tuple[str, str]:
        # URL-encode document_id to avoid issues with special characters
        encoded_id = quote(document_id, safe="")
        url = f"{self._base_url}/api/v1/docs/{encoded_id}"
        headers = {}
        if access_token:
            auth_header = access_token if access_token.startswith("Bearer ") else f"Bearer {access_token}"
            headers["Authorization"] = auth_header

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)

                if response.status_code == 404:
                    raise DocumentNotFoundError(document_id)

                response.raise_for_status()
                payload = response.json()
        except DocumentNotFoundError:
            raise
        except httpx.HTTPStatusError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                raise DocumentNotFoundError(document_id) from exc
            raise RuntimeError(f"Unable to fetch document {document_id}") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Doc processor request failed for document {document_id}") from exc
        except ValueError as exc:
            raise RuntimeError(f"Invalid response payload for document {document_id}") from exc

        if isinstance(payload, dict):
            # Doc-processor returns: {"success": true, "data": {"document_id": ..., "filename": ..., "content": ...}}
            # Normalize to a `data` dict for parsing.
            data = payload.get("data") if isinstance(payload.get("data"), dict) else payload

            # Determine filename from common keys
            file_name = None
            for fn_key in ("filename", "file_name", "name"):
                val = data.get(fn_key) if isinstance(data, dict) else None
                if isinstance(val, str) and val.strip():
                    file_name = val
                    break
            if not isinstance(file_name, str) or not file_name.strip():
                file_name = f"{document_id}.txt"

            # Determine content/extracted text from common keys
            content = None
            for content_key in ("content", "extracted_text", "text", "body"):
                val = data.get(content_key) if isinstance(data, dict) else None
                if isinstance(val, str) and val.strip():
                    content = val
                    break

            if content:
                return file_name, content

        raise DocumentNotFoundError(document_id)
