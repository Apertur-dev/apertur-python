"""Upload history resource."""

from __future__ import annotations

from typing import Dict, List, Optional

from ..http_client import HttpClient
from ..types import UploadRow, UploadsListPage


class Uploads:
    """``client.uploads`` -- list and query past uploads."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> UploadsListPage:
        """List uploads (paginated)."""
        params: Dict[str, str] = {}
        if page is not None:
            params["page"] = str(page)
        if page_size is not None:
            params["pageSize"] = str(page_size)
        return self._http.request("GET", "/api/v1/uploads", params=params or None)

    def recent(self, *, limit: Optional[int] = None) -> List[UploadRow]:
        """List recent uploads."""
        params: Dict[str, str] = {}
        if limit is not None:
            params["limit"] = str(limit)
        return self._http.request("GET", "/api/v1/uploads/recent", params=params or None)
