"""Event webhook management resource."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..http_client import HttpClient
from ..types import EventWebhook, WebhookDeliveriesResult


class Webhooks:
    """``client.webhooks`` -- CRUD for project event webhooks."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, project_id: str) -> List[EventWebhook]:
        """List all webhooks for a project."""
        return self._http.request("GET", f"/api/v1/projects/{project_id}/webhooks")

    def create(
        self,
        project_id: str,
        *,
        url: str,
        topics: List[str],
        signature_method: Optional[str] = None,
        max_retries: Optional[int] = None,
        retry_intervals: Optional[List[int]] = None,
        disable_after_failures: Optional[int] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> EventWebhook:
        """Create a new event webhook."""
        body: Dict[str, Any] = {"url": url, "topics": topics}
        if signature_method is not None:
            body["signatureMethod"] = signature_method
        if max_retries is not None:
            body["maxRetries"] = max_retries
        if retry_intervals is not None:
            body["retryIntervals"] = retry_intervals
        if disable_after_failures is not None:
            body["disableAfterFailures"] = disable_after_failures
        if custom_headers is not None:
            body["customHeaders"] = custom_headers
        return self._http.request(
            "POST",
            f"/api/v1/projects/{project_id}/webhooks",
            json=body,
        )

    def update(
        self,
        project_id: str,
        webhook_id: str,
        *,
        url: Optional[str] = None,
        topics: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
        max_retries: Optional[int] = None,
        retry_intervals: Optional[List[int]] = None,
        disable_after_failures: Optional[int] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> EventWebhook:
        """Update an existing event webhook."""
        body: Dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if topics is not None:
            body["topics"] = topics
        if is_active is not None:
            body["isActive"] = is_active
        if max_retries is not None:
            body["maxRetries"] = max_retries
        if retry_intervals is not None:
            body["retryIntervals"] = retry_intervals
        if disable_after_failures is not None:
            body["disableAfterFailures"] = disable_after_failures
        if custom_headers is not None:
            body["customHeaders"] = custom_headers
        return self._http.request(
            "PATCH",
            f"/api/v1/projects/{project_id}/webhooks/{webhook_id}",
            json=body,
        )

    def delete(self, project_id: str, webhook_id: str) -> None:
        """Delete a webhook."""
        self._http.request(
            "DELETE",
            f"/api/v1/projects/{project_id}/webhooks/{webhook_id}",
        )

    def test(self, project_id: str, webhook_id: str) -> Dict[str, str]:
        """Trigger a test delivery for a webhook."""
        return self._http.request(
            "POST",
            f"/api/v1/projects/{project_id}/webhooks/{webhook_id}/test",
        )

    def deliveries(
        self,
        project_id: str,
        webhook_id: str,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> WebhookDeliveriesResult:
        """List delivery attempts for a webhook (paginated)."""
        params: Dict[str, str] = {}
        if page is not None:
            params["page"] = str(page)
        if limit is not None:
            params["limit"] = str(limit)
        return self._http.request(
            "GET",
            f"/api/v1/projects/{project_id}/webhooks/{webhook_id}/deliveries",
            params=params or None,
        )

    def retry_delivery(
        self,
        project_id: str,
        webhook_id: str,
        delivery_id: str,
    ) -> Dict[str, str]:
        """Retry a failed webhook delivery."""
        return self._http.request(
            "POST",
            f"/api/v1/projects/{project_id}/webhooks/{webhook_id}/deliveries/{delivery_id}/retry",
        )
