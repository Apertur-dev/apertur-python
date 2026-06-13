"""Type definitions for the Apertur SDK.

All types use TypedDict so callers get IDE auto-completion without forcing
a specific class hierarchy.  Every field that is not always present is
marked ``NotRequired`` (Python 3.11+) or wrapped with ``Optional`` to stay
compatible with Python 3.9+.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict


# ── Client config ──────────────────────────────────────────────────────


class AperturConfig(TypedDict, total=False):
    api_key: str
    oauth_token: str
    base_url: str


# ── Sessions ───────────────────────────────────────────────────────────


class CreateSessionOptions(TypedDict, total=False):
    destination_ids: List[str]
    long_polling: bool
    tags: List[str]
    expires_in_hours: int
    expires_at: str
    max_images: int
    allowed_mime_types: List[str]
    max_image_dimension: int
    password: str


class QrOptions(TypedDict, total=False):
    format: str
    size: int
    style: str
    fg: str
    bg: str
    borderSize: int
    borderColor: str


class UpdateSessionOptions(TypedDict, total=False):
    expires_at: str
    max_images: int
    allowed_mime_types: List[str]
    max_image_dimension: int
    max_image_size_mb: int
    password: Optional[str]


class QrSpecs(TypedDict):
    endpoint: str
    formats: List[str]
    params: Dict[str, str]


class SessionDestination(TypedDict):
    id: str
    type: str
    name: str


class CreateSessionResult(TypedDict):
    id: str
    uuid: str  # Deprecated: alias of `id`; kept for backwards compatibility.
    upload_url: str
    qr_url: str
    qr_specs: QrSpecs
    destinations: List[SessionDestination]
    long_polling: bool
    expires_at: str
    password_protected: bool
    env: str


class Session(TypedDict, total=False):
    id: str
    status: str
    expiresAt: str
    tags: Optional[List[str]]
    imagesPerSession: int
    effectiveMaxImages: int
    effectiveAllowedMimeTypes: List[str]
    effectiveMaxImageDimension: Optional[int]
    password_protected: bool
    serverPublicKey: str
    e2eEnabled: bool
    e2ePublicKey: Optional[str]
    e2eDowngraded: bool


class SessionRow(TypedDict, total=False):
    id: str
    createdAt: str
    expiresAt: str
    status: str
    projectId: str
    projectName: str
    imagesCount: int
    imagesDelivered: int
    imagesFailed: int
    destinationsCount: int
    tags: Optional[List[str]]
    longPollingEnabled: bool
    label: Optional[str]
    env: str


class SessionsListPage(TypedDict):
    data: List[SessionRow]
    total: int
    page: int
    pageSize: int
    totalPages: int


# ── Upload ─────────────────────────────────────────────────────────────


class UploadOptions(TypedDict, total=False):
    filename: str
    mime_type: str
    source: str
    password: str


class UploadResult(TypedDict):
    id: str
    filename: str
    size_bytes: int
    destinations: int
    long_polling: bool


# ── Polling ────────────────────────────────────────────────────────────


class PollImage(TypedDict):
    id: str
    filename: str
    size_bytes: int
    mime_type: str
    source: str
    created_at: str


class PollResult(TypedDict):
    images: List[PollImage]


# ── Delivery status ───────────────────────────────────────────────────


class DeliveryDestinationStatus(TypedDict):
    destination_id: str
    type: str
    name: str
    status: str
    attempts: int
    last_error: Optional[str]


class DeliveryRecordStatus(TypedDict):
    record_id: str
    filename: str
    size_bytes: int
    destinations: List[DeliveryDestinationStatus]


class DeliveryStatusResponse(TypedDict):
    status: str  # "pending" | "active" | "completed" | "expired"
    files: List[DeliveryRecordStatus]
    lastChanged: str  # ISO 8601 timestamp


# ── Destinations ───────────────────────────────────────────────────────


class Destination(TypedDict, total=False):
    id: str
    type: str
    name: str
    config: Dict[str, Any]
    isActive: bool
    createdAt: str
    updatedAt: str


class CreateDestinationConfig(TypedDict, total=False):
    type: str
    name: str
    config: Dict[str, Any]


class UpdateDestinationConfig(TypedDict, total=False):
    name: str
    config: Dict[str, Any]
    isActive: bool


class TestDestinationResult(TypedDict, total=False):
    success: bool
    status: int
    error: str
    message: str


# ── API Keys ──────────────────────────────────────────────────────────


class ApiKey(TypedDict, total=False):
    id: str
    prefix: str
    label: str
    env: str
    isActive: bool
    lastUsedAt: Optional[str]
    maxImages: Optional[int]
    allowedMimeTypes: List[str]
    maxImageDimension: Optional[int]
    longPollingEnabled: bool
    defaultDestinations: List[str]
    allowedIps: List[str]
    allowedDomains: List[str]
    totpEnabled: bool
    clientCertEnabled: bool
    clientCertFingerprint: Optional[str]
    createdAt: str


class CreateApiKeyOptions(TypedDict, total=False):
    label: str
    maxImages: Optional[int]
    allowedMimeTypes: List[str]
    maxImageDimension: Optional[int]


class CreateApiKeyResult(TypedDict):
    key: ApiKey
    plainTextKey: str


class UpdateApiKeyOptions(TypedDict, total=False):
    label: str
    isActive: bool
    maxImages: int
    allowedMimeTypes: List[str]
    maxImageDimension: int
    allowedIps: List[str]
    allowedDomains: List[str]


class KeyDestinationEntry(TypedDict):
    id: str
    type: str
    name: str
    isActive: bool


class KeyDestinations(TypedDict):
    destinations: List[KeyDestinationEntry]
    longPollingEnabled: bool


# ── Event Webhooks ────────────────────────────────────────────────────


class EventWebhook(TypedDict, total=False):
    id: str
    projectId: str
    url: str
    secret: str
    signatureMethod: str
    topics: List[str]
    isActive: bool
    maxRetries: int
    retryIntervals: List[int]
    disableAfterFailures: int
    consecutiveFailures: int
    customHeaders: Dict[str, str]
    disabledAt: Optional[str]
    createdAt: str
    updatedAt: str


class CreateEventWebhookConfig(TypedDict, total=False):
    url: str
    topics: List[str]
    signatureMethod: str
    maxRetries: int
    retryIntervals: List[int]
    disableAfterFailures: int
    customHeaders: Dict[str, str]


class UpdateEventWebhookConfig(TypedDict, total=False):
    url: str
    topics: List[str]
    isActive: bool
    maxRetries: int
    retryIntervals: List[int]
    disableAfterFailures: int
    customHeaders: Dict[str, str]


class WebhookDelivery(TypedDict, total=False):
    id: str
    eventLogId: str
    topic: str
    status: str
    attempts: int
    responseCode: Optional[int]
    responseBody: Optional[str]
    durationMs: int
    lastError: Optional[str]
    nextRetryAt: Optional[str]
    createdAt: str
    updatedAt: str


class WebhookDeliveriesResult(TypedDict):
    deliveries: List[WebhookDelivery]
    total: int
    page: int
    limit: int


# ── Encryption ────────────────────────────────────────────────────────


class ServerKey(TypedDict):
    publicKey: str


class EncryptedPayload(TypedDict):
    encrypted_key: str
    iv: str
    encrypted_data: str
    algorithm: str


# ── Uploads ───────────────────────────────────────────────────────────


class UploadRow(TypedDict, total=False):
    id: str
    filename: str
    sizeBytes: int
    mimeType: str
    source: str
    isEncrypted: bool
    env: str
    createdAt: str
    sessionId: str
    projectId: str
    projectName: str
    destinationsTotal: int
    destinationsDelivered: int
    destinationsFailed: int
    status: str


class UploadsListPage(TypedDict):
    data: List[UploadRow]
    total: int
    page: int
    pageSize: int
    totalPages: int


# ── Stats ─────────────────────────────────────────────────────────────


class StatsTopProject(TypedDict):
    id: str
    name: str
    sessions: int


class Stats(TypedDict, total=False):
    sessionsThisMonth: int
    sessionsTotal: int
    imagesUploaded: int
    imagesDelivered: int
    deliverySuccessRate: float
    totalProjects: int
    activeKeys: int
    topProjects: List[StatsTopProject]
