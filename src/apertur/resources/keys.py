"""API key management resource."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..http_client import HttpClient
from ..types import ApiKey, CreateApiKeyResult, KeyDestinations


class Keys:
    """``client.keys`` -- CRUD for project API keys."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, project_id: str) -> List[ApiKey]:
        """List all API keys for a project."""
        return self._http.request("GET", f"/api/v1/projects/{project_id}/keys")

    def create(
        self,
        project_id: str,
        *,
        label: str,
        max_images: Optional[int] = None,
        allowed_mime_types: Optional[List[str]] = None,
        max_image_dimension: Optional[int] = None,
    ) -> CreateApiKeyResult:
        """Create a new API key."""
        body: Dict[str, Any] = {"label": label}
        if max_images is not None:
            body["maxImages"] = max_images
        if allowed_mime_types is not None:
            body["allowedMimeTypes"] = allowed_mime_types
        if max_image_dimension is not None:
            body["maxImageDimension"] = max_image_dimension
        return self._http.request(
            "POST",
            f"/api/v1/projects/{project_id}/keys",
            json=body,
        )

    def update(
        self,
        project_id: str,
        key_id: str,
        *,
        label: Optional[str] = None,
        is_active: Optional[bool] = None,
        max_images: Optional[int] = None,
        allowed_mime_types: Optional[List[str]] = None,
        max_image_dimension: Optional[int] = None,
        allowed_ips: Optional[List[str]] = None,
        allowed_domains: Optional[List[str]] = None,
    ) -> ApiKey:
        """Update an existing API key."""
        body: Dict[str, Any] = {}
        if label is not None:
            body["label"] = label
        if is_active is not None:
            body["isActive"] = is_active
        if max_images is not None:
            body["maxImages"] = max_images
        if allowed_mime_types is not None:
            body["allowedMimeTypes"] = allowed_mime_types
        if max_image_dimension is not None:
            body["maxImageDimension"] = max_image_dimension
        if allowed_ips is not None:
            body["allowedIps"] = allowed_ips
        if allowed_domains is not None:
            body["allowedDomains"] = allowed_domains
        return self._http.request(
            "PATCH",
            f"/api/v1/projects/{project_id}/keys/{key_id}",
            json=body,
        )

    def delete(self, project_id: str, key_id: str) -> None:
        """Delete an API key."""
        self._http.request(
            "DELETE",
            f"/api/v1/projects/{project_id}/keys/{key_id}",
        )

    def set_destinations(
        self,
        key_id: str,
        destination_ids: List[str],
        long_polling_enabled: bool = False,
    ) -> KeyDestinations:
        """Assign destinations (and optionally enable long polling) for a key."""
        body: Dict[str, Any] = {
            "destination_ids": destination_ids,
            "long_polling_enabled": long_polling_enabled,
        }
        return self._http.request(
            "PUT",
            f"/api/v1/keys/{key_id}/destinations",
            json=body,
        )
