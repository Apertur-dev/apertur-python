"""Long-polling resource."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List

from ..http_client import HttpClient
from ..types import PollImage, PollResult


class Polling:
    """``client.polling`` -- poll a session for new images and acknowledge them."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, uuid: str) -> PollResult:
        """Return the list of unacknowledged images for a session."""
        return self._http.request("GET", f"/api/v1/upload-sessions/{uuid}/poll")

    def download(self, uuid: str, image_id: str) -> bytes:
        """Download an image's binary data."""
        return self._http.request_raw(
            "GET",
            f"/api/v1/upload-sessions/{uuid}/images/{image_id}",
        )

    def ack(self, uuid: str, image_id: str) -> Dict[str, str]:
        """Acknowledge receipt of an image so it is removed from the poll queue."""
        return self._http.request(
            "POST",
            f"/api/v1/upload-sessions/{uuid}/images/{image_id}/ack",
        )

    def poll_and_process(
        self,
        uuid: str,
        handler: Callable[[Dict[str, Any], bytes], None],
        *,
        interval: float = 3.0,
        timeout: float = 0,
    ) -> None:
        """Block and continuously poll for new images.

        For every new image the *handler* is called with ``(image_dict,
        image_bytes)`` and the image is automatically acknowledged.

        Args:
            uuid: The upload-session UUID.
            handler: Called for each new image with ``(image_metadata, raw_bytes)``.
            interval: Seconds between poll cycles (default ``3.0``).
            timeout: Maximum seconds to run (``0`` = unlimited).
                     The loop always respects ``KeyboardInterrupt``.
        """
        deadline = (time.monotonic() + timeout) if timeout > 0 else None

        try:
            while True:
                if deadline is not None and time.monotonic() >= deadline:
                    break

                result: PollResult = self.list(uuid)

                for image in result.get("images", []):
                    if deadline is not None and time.monotonic() >= deadline:
                        return
                    data = self.download(uuid, image["id"])
                    handler(image, data)
                    self.ack(uuid, image["id"])

                if deadline is not None and time.monotonic() >= deadline:
                    break

                time.sleep(interval)

        except KeyboardInterrupt:
            pass
