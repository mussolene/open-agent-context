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
