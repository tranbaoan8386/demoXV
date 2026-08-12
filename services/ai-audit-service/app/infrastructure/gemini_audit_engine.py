from __future__ import annotations

import asyncio
import datetime as dt
import json

from google import genai
from google.genai import types

from app.domain.enums import RiskLevel
from app.domain.exceptions import AuditEngineError
from app.domain.interfaces import IAuditEngine
from app.domain.models import Clause, ContractAudit

from .config import Settings, get_settings


class GeminiAuditEngine(IAuditEngine):
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client = genai.Client(api_key=self._settings.gemini_api_key)

    def _get_models(self) -> list[str]:
        models = [self._settings.gemini_model]
        if self._settings.gemini_fallback_model and self._settings.gemini_fallback_model not in models:
            models.append(self._settings.gemini_fallback_model)
        return models

    async def analyze_contract(self, document_id: str, file_name: str, document_text: str) -> ContractAudit:
        try:
            system_prompt = (
                "You are an expert contract auditor. Analyze the provided contract text and "
                "return a strict JSON object with the following structure: "
                "{\"id\": string, \"document_id\": string, \"file_name\": string, "
                "\"overall_risk_score\": number, \"summary\": string, \"clauses\": [{\"title\": string, "
                "\"content\": string, \"risk_level\": \"LOW\"|\"MEDIUM\"|\"HIGH\"|\"CRITICAL\", "
                "\"risk_description\": string, \"recommendation\": string}]}. "
                "Do not include extra commentary."
            )

            raw_text = await asyncio.to_thread(
                self._call_gemini,
                document_id=document_id,
                document_text=document_text,
                system_prompt=system_prompt,
            )

            if not raw_text:
                raise AuditEngineError("Gemini returned an empty response")

            parsed = json.loads(raw_text)
            clauses = [
                Clause(
                    title=str(clause.get("title", "Untitled clause")),
                    content=str(clause.get("content", "")),
                    risk_level=self._parse_risk_level(clause.get("risk_level")),
                    risk_description=str(clause.get("risk_description", "")),
                    recommendation=str(clause.get("recommendation", "")),
                )
                for clause in parsed.get("clauses", [])
            ]

            return ContractAudit(
                id=str(parsed.get("id", document_id)),
                document_id=str(parsed.get("document_id", document_id)),
                file_name=str(parsed.get("file_name", file_name)),
                overall_risk_score=float(parsed.get("overall_risk_score", 0.0)),
                summary=str(parsed.get("summary", "")),
                clauses=clauses,
                created_at=dt.datetime.now(dt.timezone.utc),
            )
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
            raise AuditEngineError("Failed to parse Gemini audit response") from exc
        except Exception as exc:
            raise AuditEngineError(f"Gemini audit failed: {exc}") from exc

    def _call_gemini(self, *, document_id: str, document_text: str, system_prompt: str) -> str:
        last_error: Exception | None = None
        for model_name in self._get_models():
            try:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=f"Document ID: {document_id}\n\nContract text:\n{document_text}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.2,
                        response_mime_type="application/json",
                    ),
                )
                return response.text or ""
            except Exception as exc:  # pragma: no cover - defensive fallback
                last_error = exc
                message = str(exc).lower()
                if "429" not in message and "resource exhausted" not in message and "quota" not in message:
                    raise

        if last_error is not None:
            raise last_error
        raise AuditEngineError("Gemini request failed")

    def _parse_risk_level(self, value: object) -> RiskLevel:
        if isinstance(value, str):
            normalized = value.upper()
            if normalized in RiskLevel.__members__:
                return RiskLevel[normalized]
        return RiskLevel.LOW
