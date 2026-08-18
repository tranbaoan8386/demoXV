from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class LegalDocument:
    id: str
    title: Optional[str]
    reference_number: Optional[str]
    issued_date: Optional[str]
    original_filename: str
    storage_path: str
    uploader_id: Optional[str]
    status: str = 'PENDING'
    error_message: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class LegalClause:
    document_id: str
    section: Optional[str]
    chapter: Optional[str]
    chapter_index: Optional[int]
    article_number: Optional[int]
    clause_number: Optional[int]
    point_label: Optional[str]
    content: str
    order_index: int
    raw_context: Optional[dict] = None
    # Phase2 additions
    part: Optional[str] = None
    subsection: Optional[str] = None
    article_title: Optional[str] = None
    article_id: Optional[str] = None
    start_paragraph_index: Optional[int] = None
    end_paragraph_index: Optional[int] = None
    parent_clause_id: Optional[str] = None
    is_needs_review: bool = False
    review_reason: Optional[str] = None
