"""Main Apertur client."""

from __future__ import annotations

from typing import Optional

from .http_client import HttpClient
from .resources.destinations import Destinations
from .resources.encryption import Encryption
from .resources.keys import Keys
from .resources.polling import Polling
from .resources.sessions import Sessions
from .resources.stats import Stats_
from .resources.upload import Upload
from .resources.uploads import Uploads
from .resources.webhooks import Webhooks

_DEFAULT_BASE_URL = "https://api.aptr.ca"
_SANDBOX_BASE_URL = "https://sandbox.api.aptr.ca"


class Apertur:
    """Official Python client for the Apertur API.

    Usage::

        from apertur import Apertur

        client = Apertur(api_key="aptr_live_...")
        session = client.sessions.create()
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        oauth_token: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        if not api_key and not oauth_token:
            raise ValueError("Either api_key or oauth_token must be provided")

        # Detect environment from key prefix
        token = api_key or oauth_token or ""
        self.env: str = "test" if token.startswith("aptr_test_") else "live"

        # Auto-select sandbox URL for test keys unless base_url is explicitly set
        resolved_url = base_url or (_SANDBOX_BASE_URL if self.env == "test" else _DEFAULT_BASE_URL)

        self._http = HttpClient(resolved_url, api_key=api_key, oauth_token=oauth_token)

        # Resource namespaces
        self.sessions = Sessions(self._http)
        self.upload = Upload(self._http)
        self.uploads = Uploads(self._http)
        self.polling = Polling(self._http)
        self.destinations = Destinations(self._http)
        self.keys = Keys(self._http)
        self.webhooks = Webhooks(self._http)
        self.encryption = Encryption(self._http)
        self.stats = Stats_(self._http)

    def close(self) -> None:
        """Close the underlying HTTP connection."""
        self._http.close()

    def __enter__(self) -> "Apertur":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
