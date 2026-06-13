"""Upload-session management."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..http_client import HttpClient
from ..types import (
    CreateSessionResult,
    DeliveryStatusResponse,
    Session,
    SessionRow,
    SessionsListPage,
)


class Sessions:
    """``client.sessions`` -- create, retrieve, update, and list upload sessions."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        destination_ids: Optional[List[str]] = None,
        long_polling: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        expires_in_hours: Optional[int] = None,
        expires_at: Optional[str] = None,
        max_images: Optional[int] = None,
        allowed_mime_types: Optional[List[str]] = None,
        max_image_dimension: Optional[int] = None,
        password: Optional[str] = None,
    ) -> CreateSessionResult:
        """Create a new upload session."""
        body: Dict[str, Any] = {}
        if destination_ids is not None:
            body["destination_ids"] = destination_ids
        if long_polling is not None:
            body["long_polling"] = long_polling
        if tags is not None:
            body["tags"] = tags
        if expires_in_hours is not None:
            body["expires_in_hours"] = expires_in_hours
        if expires_at is not None:
            body["expires_at"] = expires_at
        if max_images is not None:
            body["max_images"] = max_images
        if allowed_mime_types is not None:
            body["allowed_mime_types"] = allowed_mime_types
        if max_image_dimension is not None:
            body["max_image_dimension"] = max_image_dimension
        if password is not None:
            body["password"] = password
        return self._http.request("POST", "/api/v1/upload-sessions", json=body)

    def get(self, uuid: str) -> Session:
        """Retrieve session details."""
        return self._http.request("GET", f"/api/v1/upload/{uuid}/session")

    def update(
        self,
        uuid: str,
        *,
        expires_at: Optional[str] = None,
        max_images: Optional[int] = None,
        allowed_mime_types: Optional[List[str]] = None,
        max_image_dimension: Optional[int] = None,
        max_image_size_mb: Optional[int] = None,
        password: Optional[str] = ...,  # type: ignore[assignment]
    ) -> Session:
        """Update session settings.

        Pass ``password=None`` to explicitly remove a password.
        """
        body: Dict[str, Any] = {}
        if expires_at is not None:
            body["expires_at"] = expires_at
        if max_images is not None:
            body["max_images"] = max_images
        if allowed_mime_types is not None:
            body["allowed_mime_types"] = allowed_mime_types
        if max_image_dimension is not None:
            body["max_image_dimension"] = max_image_dimension
        if max_image_size_mb is not None:
            body["max_image_size_mb"] = max_image_size_mb
        if password is not ...:
            body["password"] = password
        return self._http.request("PATCH", f"/api/v1/upload-sessions/{uuid}", json=body)

    def list(
        self,
        *,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> SessionsListPage:
        """List sessions (paginated)."""
        params: Dict[str, str] = {}
        if page is not None:
            params["page"] = str(page)
        if page_size is not None:
            params["pageSize"] = str(page_size)
        return self._http.request("GET", "/api/v1/sessions", params=params or None)

    def recent(self, *, limit: Optional[int] = None) -> List[SessionRow]:
        """List recent sessions."""
        params: Dict[str, str] = {}
        if limit is not None:
            params["limit"] = str(limit)
        return self._http.request("GET", "/api/v1/sessions/recent", params=params or None)

    def qr(
        self,
        uuid: str,
        *,
        format: Optional[str] = None,
        size: Optional[int] = None,
        style: Optional[str] = None,
        fg: Optional[str] = None,
        bg: Optional[str] = None,
        border_size: Optional[int] = None,
        border_color: Optional[str] = None,
    ) -> bytes:
        """Download the QR code image for a session."""
        params: Dict[str, str] = {}
        if format is not None:
            params["format"] = format
        if size is not None:
            params["size"] = str(size)
        if style is not None:
            params["style"] = style
        if fg is not None:
            params["fg"] = fg
        if bg is not None:
            params["bg"] = bg
        if border_size is not None:
            params["borderSize"] = str(border_size)
        if border_color is not None:
            params["borderColor"] = border_color
        return self._http.request_raw(
            "GET",
            f"/api/v1/upload-sessions/{uuid}/qr",
            params=params or None,
        )

    def verify_password(self, uuid: str, password: str) -> Dict[str, bool]:
        """Verify a session password."""
        return self._http.request(
            "POST",
            f"/api/v1/upload/{uuid}/verify-password",
            json={"password": password},
        )

    def delivery_status(
        self,
        uuid: str,
        *,
        poll_from: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> DeliveryStatusResponse:
        """Get per-destination delivery status for a session.

        Returns a dict with ``status`` (``"pending"``, ``"active"``,
        ``"completed"`` or ``"expired"``), ``files`` (a list of per-file
        delivery records) and ``lastChanged`` (ISO 8601 timestamp).

        When ``poll_from`` (ISO 8601 timestamp) is provided, the server
        long-polls for up to 5 minutes waiting for something to change
        before responding. Pass ``timeout=360.0`` (6 minutes) so the
        server releases first under the happy path.
        """
        params: Optional[Dict[str, str]] = None
        if poll_from is not None:
            params = {"pollFrom": poll_from}
        return self._http.request(
            "GET",
            f"/api/v1/upload-sessions/{uuid}/delivery-status",
            params=params,
            timeout=timeout,
        )
