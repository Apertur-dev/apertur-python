"""Destination management resource."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..http_client import HttpClient
from ..types import Destination, TestDestinationResult


class Destinations:
    """``client.destinations`` -- CRUD for project destinations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, project_id: str) -> List[Destination]:
        """List all destinations for a project."""
        return self._http.request("GET", f"/api/v1/projects/{project_id}/destinations")

    def create(
        self,
        project_id: str,
        *,
        type: str,
        name: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Destination:
        """Create a new destination."""
        body: Dict[str, Any] = {"type": type, "name": name}
        if config is not None:
            body["config"] = config
        return self._http.request(
            "POST",
            f"/api/v1/projects/{project_id}/destinations",
            json=body,
        )

    def update(
        self,
        project_id: str,
        dest_id: str,
        *,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None,
    ) -> Destination:
        """Update an existing destination."""
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if config is not None:
            body["config"] = config
        if is_active is not None:
            body["isActive"] = is_active
        return self._http.request(
            "PATCH",
            f"/api/v1/projects/{project_id}/destinations/{dest_id}",
            json=body,
        )

    def delete(self, project_id: str, dest_id: str) -> None:
        """Delete a destination."""
        self._http.request(
            "DELETE",
            f"/api/v1/projects/{project_id}/destinations/{dest_id}",
        )

    def test(self, project_id: str, dest_id: str) -> TestDestinationResult:
        """Trigger a test delivery to a destination."""
        return self._http.request(
            "POST",
            f"/api/v1/projects/{project_id}/destinations/{dest_id}/test",
        )
