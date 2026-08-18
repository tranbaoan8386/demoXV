from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class ParserContext:
    part: Optional[str] = None
    chapter: Optional[str] = None
    chapter_index: Optional[int] = None
    section: Optional[str] = None
    subsection: Optional[str] = None
    article_number: Optional[int] = None
    article_title_lines: list = field(default_factory=list)
    clause_number: Optional[int] = None
    point_label: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'part': self.part,
            'chapter': self.chapter,
            'chapter_index': self.chapter_index,
            'section': self.section,
            'subsection': self.subsection,
            'article_number': self.article_number,
            'article_title': '\n'.join(self.article_title_lines) if self.article_title_lines else None,
            'clause_number': self.clause_number,
            'point_label': self.point_label,
        }

    def reset_article(self):
        self.article_number = None
        self.article_title_lines = []
        self.clause_number = None
        self.point_label = None

    def new_article(self, number: int, title_candidate: Optional[str]):
        self.article_number = number
        self.article_title_lines = [title_candidate] if title_candidate else []
        self.clause_number = None
        self.point_label = None

    def new_clause(self, number: int, text: Optional[str]):
        self.clause_number = number
        self.point_label = None

    def new_point(self, label: str):
        self.point_label = label
