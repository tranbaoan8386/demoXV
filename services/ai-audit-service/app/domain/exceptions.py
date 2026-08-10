class DomainException(Exception):
    """Base exception for domain-level errors."""


class DocumentNotFoundError(DomainException):
    """Raised when a requested document cannot be found."""


class AuditEngineError(DomainException):
    """Raised when the audit engine fails to process a contract."""
