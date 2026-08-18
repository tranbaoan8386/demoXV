from abc import ABC, abstractmethod


class DocConverter(ABC):
    @abstractmethod
    def convert_to_docx(self, path: str) -> str:
        """Convert given .doc file to .docx and return new path"""
        raise NotImplementedError()
