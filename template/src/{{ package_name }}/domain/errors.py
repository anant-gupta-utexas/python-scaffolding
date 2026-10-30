"""Domain error hierarchy: raise these from the domain and application layers.

Messages on these errors are meant for API clients, so keep them free of internals. The API layer
maps each type to an HTTP status in one place (``infrastructure/api/errors.py``).
"""


class DomainError(Exception):
    """Base class for every expected, business-level failure."""


class NotFoundError(DomainError):
    """A requested entity does not exist."""


class DomainValidationError(DomainError):
    """Input is well-formed but violates a business rule."""
