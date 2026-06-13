"""Webhook signature verification utilities."""

from __future__ import annotations

import base64
import hashlib
import hmac


def verify_webhook_signature(body: str, signature: str, secret: str) -> bool:
    """Verify an image-delivery webhook signature.

    The ``X-Apertur-Signature`` header carries ``sha256=<hex>``.
    Calculation: ``HMAC-SHA256(body, secret)``.
    """
    expected = hmac.new(
        secret.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    sig = signature.removeprefix("sha256=") if signature.startswith("sha256=") else signature

    if len(expected) != len(sig):
        return False

    return hmac.compare_digest(expected, sig)


def verify_event_signature(
    body: str,
    timestamp: str,
    signature: str,
    secret: str,
) -> bool:
    """Verify an event webhook signature (HMAC SHA-256 method).

    Headers: ``X-Apertur-Signature: sha256=<hex>``,
    ``X-Apertur-Timestamp: <unix seconds>``.
    Calculation: ``HMAC-SHA256("{timestamp}.{body}", secret)``.
    """
    signature_base = f"{timestamp}.{body}"
    expected = hmac.new(
        secret.encode("utf-8"),
        signature_base.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    sig = signature.removeprefix("sha256=") if signature.startswith("sha256=") else signature

    if len(expected) != len(sig):
        return False

    return hmac.compare_digest(expected, sig)


def verify_svix_signature(
    body: str,
    svix_id: str,
    timestamp: str,
    signature: str,
    secret: str,
) -> bool:
    """Verify an event webhook signature (Svix method).

    Headers: ``svix-id``, ``svix-timestamp``, ``svix-signature: v1,<base64>``.
    Calculation: ``HMAC-SHA256("{svix_id}.{timestamp}.{body}",
    bytes.fromhex(secret))``.
    """
    signature_base = f"{svix_id}.{timestamp}.{body}"
    expected_bytes = hmac.new(
        bytes.fromhex(secret),
        signature_base.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    expected_b64 = base64.b64encode(expected_bytes)

    sig = signature.removeprefix("v1,") if signature.startswith("v1,") else signature
    sig_bytes = base64.b64decode(sig)

    if len(expected_bytes) != len(sig_bytes):
        return False

    return hmac.compare_digest(expected_bytes, sig_bytes)
