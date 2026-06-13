"""Server-side encryption key resource."""

from __future__ import annotations

from ..http_client import HttpClient
from ..types import ServerKey


class Encryption:
    """``client.encryption`` -- retrieve the server's RSA public key."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get_server_key(self) -> ServerKey:
        """Fetch the server's RSA public key used for encrypted uploads."""
        return self._http.request("GET", "/api/v1/encryption/server-key")
