"""Account statistics resource."""

from __future__ import annotations

from ..http_client import HttpClient
from ..types import Stats


class Stats_:
    """``client.stats`` -- retrieve account statistics."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self) -> Stats:
        """Get account-level statistics."""
        return self._http.request("GET", "/api/v1/stats")
