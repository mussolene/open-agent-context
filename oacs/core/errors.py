from __future__ import annotations


class OacsError(Exception):
    """Base domain error."""


class AccessDenied(OacsError):
    """Raised when a capability check denies an operation."""


class NotFound(OacsError):
    """Raised when a record cannot be found."""


class LockedKeyError(OacsError):
    """Raised when encrypted storage is accessed without an unlocked key."""


class ValidationFailure(OacsError):
    """Raised when a typed contract is invalid."""


class MemoryDecryptError(OacsError):
    """Raised when an encrypted memory row cannot be decrypted or decoded."""

    def __init__(self, message: str, record: dict[str, object]):
        super().__init__(message)
        self.record = record
