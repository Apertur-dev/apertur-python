"""Low-level HTTP wrapper around ``httpx`` for the Apertur API."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from .errors import (
    AperturError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class HttpClient:
    """Thin HTTP layer that every resource delegates to."""

    def __init__(
        self,
        base_url: str,
        *,
        api_key: Optional[str] = None,
        oauth_token: Optional[str] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")

        token = api_key or oauth_token or ""
        headers: Dict[str, str] = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self._client = httpx.Client(
            base_url=self._base_url,
            headers=headers,
            timeout=30.0,
        )

    # ── public helpers ─────────────────────────────────────────────────

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Send a request and return parsed JSON (or ``None`` for 204)."""
        response = self._send(
            method,
            path,
            json=json,
            data=data,
            files=files,
            headers=headers,
            params=params,
            timeout=timeout,
        )

        if response.status_code == 204:
            return None

        return response.json()

    def request_raw(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> bytes:
        """Send a request and return the raw response body as bytes."""
        response = self._send(method, path, headers=headers, params=params)
        return response.content

    # ── internals ──────────────────────────────────────────────────────

    def _send(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> httpx.Response:
        request_kwargs: Dict[str, Any] = {
            "json": json,
            "data": data,
            "files": files,
            "headers": headers,
            "params": params,
        }
        if timeout is not None:
            request_kwargs["timeout"] = timeout
        response = self._client.request(method, path, **request_kwargs)

        if response.is_success:
            return response

        self._handle_error(response)
        # unreachable – _handle_error always raises
        raise AperturError("Unexpected error", response.status_code)  # pragma: no cover

    def _handle_error(self, response: httpx.Response) -> None:
        """Parse the error body and raise the appropriate exception."""
        try:
            body = response.json()
        except Exception:
            body = {}

        message: str = body.get("message", f"HTTP {response.status_code}")
        code: Optional[str] = body.get("code")

        status = response.status_code
        if status == 401:
            raise AuthenticationError(message)
        if status == 404:
            raise NotFoundError(message)
        if status == 429:
            retry_after_raw = response.headers.get("Retry-After")
            retry_after: Optional[int] = None
            if retry_after_raw is not None:
                try:
                    retry_after = int(retry_after_raw)
                except ValueError:
                    pass
            raise RateLimitError(message, retry_after=retry_after)
        if status == 400:
            raise ValidationError(message)

        raise AperturError(message, status_code=status, code=code)

    def close(self) -> None:
        """Close the underlying ``httpx.Client``."""
        self._client.close()
