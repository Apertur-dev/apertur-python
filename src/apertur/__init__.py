"""Apertur SDK -- Official Python client for the Apertur API."""

from .client import Apertur
from .crypto import encrypt_image
from .errors import (
    AperturError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .signature import (
    verify_event_signature,
    verify_svix_signature,
    verify_webhook_signature,
)

__all__ = [
    "Apertur",
    "AperturError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "encrypt_image",
    "verify_event_signature",
    "verify_svix_signature",
    "verify_webhook_signature",
]
