"""Image encryption using RSA-OAEP + AES-256-GCM."""

from __future__ import annotations

import base64
import os
from typing import Dict

from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import load_pem_public_key


def encrypt_image(image_data: bytes, public_key_pem: str) -> Dict[str, str]:
    """Encrypt *image_data* with AES-256-GCM, wrapping the key with RSA-OAEP.

    Returns a dict with ``encryptedKey``, ``iv``, ``encryptedData``, and
    ``algorithm`` -- all strings (base64-encoded where applicable).

    The keys are camelCase to match the API contract and the other Apertur
    SDKs: ``image_encrypted`` spreads this dict directly into the JSON body
    that the server decrypts, so the field names must be exactly
    ``encryptedKey`` / ``iv`` / ``encryptedData`` / ``algorithm``.
    """
    # Generate random AES-256 key (32 bytes) and 12-byte nonce/IV
    aes_key = os.urandom(32)
    iv = os.urandom(12)

    # Encrypt image with AES-256-GCM
    aesgcm = AESGCM(aes_key)
    # AESGCM.encrypt appends the 16-byte auth tag to the ciphertext
    encrypted_data = aesgcm.encrypt(iv, image_data, None)

    # Wrap AES key with RSA-OAEP (SHA-256)
    public_key = load_pem_public_key(public_key_pem.encode("utf-8"))
    wrapped_key = public_key.encrypt(  # type: ignore[union-attr]
        aes_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=SHA256()),
            algorithm=SHA256(),
            label=None,
        ),
    )

    return {
        "encryptedKey": base64.b64encode(wrapped_key).decode("ascii"),
        "iv": base64.b64encode(iv).decode("ascii"),
        "encryptedData": base64.b64encode(encrypted_data).decode("ascii"),
        "algorithm": "RSA-OAEP+AES-256-GCM",
    }
