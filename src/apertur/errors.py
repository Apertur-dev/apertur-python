"""Exception classes for the Apertur SDK."""

from __future__ import annotations

from typing import Optional


class AperturError(Exception):
    """Base exception for all Apertur API errors."""

    def __init__(
        self,
        message: str,
        status_code: int,
        code: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(status_code={self.status_code}, code={self.code!r}, message={self.message!r})"


class AuthenticationError(AperturError):
    """Raised on HTTP 401 responses."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status_code=401, code="AUTHENTICATION_FAILED")


class NotFoundError(AperturError):
    """Raised on HTTP 404 responses."""

    def __init__(self, message: str = "Not found") -> None:
        super().__init__(message, status_code=404, code="NOT_FOUND")


class RateLimitError(AperturError):
    """Raised on HTTP 429 responses."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message, status_code=429, code="RATE_LIMIT")
        self.retry_after = retry_after


class ValidationError(AperturError):
    """Raised on HTTP 400 responses."""

    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message, status_code=400, code="VALIDATION_ERROR")
