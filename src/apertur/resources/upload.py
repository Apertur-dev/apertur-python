"""Image upload resource."""

from __future__ import annotations

import json as _json
import os
from typing import BinaryIO, Dict, Optional, Union

from ..crypto import encrypt_image
from ..http_client import HttpClient
from ..types import UploadResult


class Upload:
    """``client.upload`` -- upload images to a session."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def image(
        self,
        uuid: str,
        file: Union[str, bytes, BinaryIO],
        *,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        source: Optional[str] = None,
        password: Optional[str] = None,
    ) -> UploadResult:
        """Upload an image via multipart form data.

        *file* can be a file path (``str``), raw ``bytes``, or a binary
        file-like object.
        """
        file_bytes, resolved_filename = self._resolve_file(file, filename)
        resolved_mime = mime_type or "image/jpeg"

        files = {
            "file": (resolved_filename, file_bytes, resolved_mime),
        }
        data: Dict[str, str] = {}
        if source is not None:
            data["source"] = source

        headers: Dict[str, str] = {}
        if password is not None:
            headers["x-session-password"] = password

        return self._http.request(
            "POST",
            f"/api/v1/upload/{uuid}/images",
            files=files,
            data=data or None,
            headers=headers or None,
        )

    def image_encrypted(
        self,
        uuid: str,
        file: Union[str, bytes, BinaryIO],
        public_key: str,
        *,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        source: Optional[str] = None,
        password: Optional[str] = None,
    ) -> UploadResult:
        """Upload an encrypted image (RSA-OAEP + AES-256-GCM).

        The image is encrypted client-side, then sent as ``multipart/form-data``
        with the ``X-Aptr-Encrypted: default`` header. The server reads the file
        bytes (the JSON-serialised envelope), parses them, and RSA-OAEP decrypts
        server-side. This mirrors the verified Ruby/PHP SDKs.
        """
        file_bytes, resolved_filename = self._resolve_file(file, filename)

        encrypted = encrypt_image(file_bytes, public_key)

        # The file PART CONTENT is the JSON-serialised envelope (camelCase keys).
        envelope_bytes = _json.dumps(
            {
                "encryptedKey": encrypted["encryptedKey"],
                "iv": encrypted["iv"],
                "encryptedData": encrypted["encryptedData"],
                "algorithm": encrypted["algorithm"],
            }
        ).encode("utf-8")

        enc_filename = f"{resolved_filename}.enc"

        files = {
            "file": (enc_filename, envelope_bytes, "application/octet-stream"),
        }
        data: Dict[str, str] = {}
        if source is not None:
            data["source"] = source

        headers: Dict[str, str] = {
            "X-Aptr-Encrypted": "default",
        }
        if password is not None:
            headers["x-session-password"] = password

        return self._http.request(
            "POST",
            f"/api/v1/upload/{uuid}/images",
            files=files,
            data=data or None,
            headers=headers,
        )

    # ── helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _resolve_file(
        file: Union[str, bytes, BinaryIO],
        filename: Optional[str],
    ) -> tuple[bytes, str]:
        """Normalise *file* to ``(bytes, filename)``."""
        if isinstance(file, str):
            data = open(file, "rb").read()
            name = filename or os.path.basename(file)
            return data, name
        if isinstance(file, bytes):
            return file, filename or "image.jpg"
        # file-like object
        data = file.read()
        name = filename or getattr(file, "name", None) or "image.jpg"
        if isinstance(name, bytes):
            name = name.decode("utf-8", errors="replace")
        # Extract just the basename if it is a full path
        name = os.path.basename(name)
        return data, name
