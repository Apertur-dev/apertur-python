# apertur-sdk

Official Python SDK for the [Apertur](https://apertur.ca) API. Supports API key and OAuth token authentication, session management, image uploads (plain and encrypted), long polling, webhook verification, and full resource CRUD.

## Installation

Requires Python 3.9+ and is installed via pip.

```bash
pip install apertur-sdk
```

## Quick Start

Create a client, open an upload session, and upload an image in a few lines. See the [API documentation](https://docs.apertur.ca) for a full overview.

```python
from apertur import Apertur

client = Apertur(api_key="aptr_live_...")

session = client.sessions.create()
image = client.upload.image(session["uuid"], "/path/to/photo.jpg")

print(image["id"])
```

## Authentication

The client accepts either a long-lived API key or a short-lived OAuth bearer token. Only one is required. The environment (`live` / `test`) is auto-detected from the key prefix. See [Authentication documentation](https://docs.apertur.ca/authentication).

```python
from apertur import Apertur

# API key
client = Apertur(api_key="aptr_live_...")

# OAuth token
client = Apertur(oauth_token=access_token)

# Custom base URL
client = Apertur(api_key="aptr_live_...", base_url="https://sandbox.api.aptr.ca")

# Context manager (auto-closes the HTTP connection)
with Apertur(api_key="aptr_live_...") as client:
    session = client.sessions.create()
```

## Sessions

Upload sessions scope every image upload. You can create a session with optional settings, retrieve it, protect it with a password, and check delivery status. See [Sessions documentation](https://docs.apertur.ca/upload-sessions).

```python
from apertur import Apertur

client = Apertur(api_key="aptr_live_...")

# Create a session
session = client.sessions.create(password="s3cr3t", max_images=200)

# Retrieve session details
details = client.sessions.get(session["uuid"])

# Verify a password-protected session before uploading
result = client.sessions.verify_password(session["uuid"], "s3cr3t")

# Check per-destination delivery status. Returns
# { "status": "pending|active|completed|expired", "files": [...], "lastChanged": "<ISO 8601>" }
status = client.sessions.delivery_status(session["uuid"])

# Long-poll: server holds the response up to 5 min waiting for a change.
# Pass timeout=360.0 (6 min) so the server releases first under the happy path.
status = client.sessions.delivery_status(
    session["uuid"],
    poll_from=status["lastChanged"],
    timeout=360.0,
)
```

## Uploading Images

Upload a plain image using a file path, raw bytes, or a file-like object. For end-to-end encrypted uploads, use `image_encrypted` with the server's RSA public key. See [Upload documentation](https://docs.apertur.ca/upload-sessions).

```python
from apertur import Apertur

client = Apertur(api_key="aptr_live_...")
uuid = "session-uuid-here"

# Upload from a file path
image = client.upload.image(uuid, "/tmp/photo.jpg", filename="photo.jpg", source="my-app")

# Upload from bytes
with open("/tmp/photo.jpg", "rb") as f:
    image = client.upload.image(uuid, f.read())

# Upload from a file-like object
with open("/tmp/photo.jpg", "rb") as f:
    image = client.upload.image(uuid, f)

# Upload to a password-protected session
image = client.upload.image(uuid, "/tmp/photo.jpg", password="s3cr3t")

# Encrypted upload (fetch the server key first)
server_key = client.encryption.get_server_key()
image = client.upload.image_encrypted(
    uuid, "/tmp/photo.jpg", server_key["publicKey"],
    filename="photo.jpg", mime_type="image/jpeg",
)
```

## Long Polling

Poll a session for new images, download each one, and acknowledge receipt to advance the queue. The `poll_and_process` helper loops automatically and calls your handler for every image. See [Long Polling documentation](https://docs.apertur.ca/long-polling).

```python
from apertur import Apertur

client = Apertur(api_key="aptr_live_...")
uuid = "session-uuid-here"

# Manual poll / download / ack cycle
result = client.polling.list(uuid)
for image in result["images"]:
    data = client.polling.download(uuid, image["id"])
    with open(f"/tmp/{image['id']}.jpg", "wb") as f:
        f.write(data)
    client.polling.ack(uuid, image["id"])

# Automatic loop with 60-second timeout and 3-second interval
def handle_image(image, data):
    with open(f"/tmp/{image['id']}.jpg", "wb") as f:
        f.write(data)
    print(f"Saved {image['id']}")

client.polling.poll_and_process(uuid, handle_image, interval=3.0, timeout=60)
```

## Receiving Webhooks

Apertur signs every webhook payload so you can verify it was not tampered with. Three verification functions are available. See [Webhooks documentation](https://docs.apertur.ca/webhooks).

```python
from apertur import verify_webhook_signature, verify_event_signature, verify_svix_signature

# Image delivery webhook
valid = verify_webhook_signature(body, signature, secret)

# Event webhook -- HMAC method
valid = verify_event_signature(body, timestamp, signature, secret)

# Event webhook -- Svix method
valid = verify_svix_signature(body, svix_id, timestamp, signature, secret)
```

## Destinations

Destinations define where uploaded images are delivered (S3, webhook, long-poll queue, etc.). See [Destinations documentation](https://docs.apertur.ca/destinations).

```python
from apertur import Apertur

client = Apertur(api_key="aptr_live_...")
project_id = "proj_..."

# List all destinations
destinations = client.destinations.list(project_id)

# Create a new destination
dest = client.destinations.create(
    project_id, type="s3", name="Primary S3 bucket",
    config={"bucket": "my-bucket", "region": "us-east-1"},
)

# Update a destination
client.destinations.update(project_id, dest["id"], name="Updated name")

# Trigger a test delivery
client.destinations.test(project_id, dest["id"])

# Delete a destination
client.destinations.delete(project_id, dest["id"])
```

## API Keys

API keys are scoped to a project and optionally restricted to specific destinations. See [API Keys documentation](https://docs.apertur.ca/api-keys).

```python
from apertur import Apertur

client = Apertur(api_key="aptr_live_...")
project_id = "proj_..."

# List keys
keys = client.keys.list(project_id)

# Create a key
key = client.keys.create(project_id, label="Mobile app key")

# Update a key
client.keys.update(project_id, key["key"]["id"], label="Mobile app key v2")

# Assign destinations (and optionally enable long polling)
client.keys.set_destinations(key["key"]["id"], ["dest_abc", "dest_def"], long_polling_enabled=True)

# Delete a key
client.keys.delete(project_id, key["key"]["id"])
```

## Event Webhooks

Event webhooks push real-time notifications to your endpoint. See [Event Webhooks documentation](https://docs.apertur.ca/event-webhooks).

```python
from apertur import Apertur

client = Apertur(api_key="aptr_live_...")
project_id = "proj_..."

# List webhooks
webhooks = client.webhooks.list(project_id)

# Create a webhook
webhook = client.webhooks.create(
    project_id,
    url="https://example.com/webhooks/apertur",
    topics=["image.uploaded", "session.completed"],
)

# Test, update, list deliveries, retry, delete
client.webhooks.test(project_id, webhook["id"])
client.webhooks.update(project_id, webhook["id"], topics=["image.uploaded"])
deliveries = client.webhooks.deliveries(project_id, webhook["id"], page=1, limit=25)
client.webhooks.retry_delivery(project_id, webhook["id"], deliveries["deliveries"][0]["id"])
client.webhooks.delete(project_id, webhook["id"])
```

## Encryption

Apertur supports end-to-end encrypted uploads using RSA-OAEP + AES-256-GCM. See [Encryption documentation](https://docs.apertur.ca/encryption).

```python
from apertur import Apertur

client = Apertur(api_key="aptr_live_...")

# Fetch the server's RSA public key
server_key = client.encryption.get_server_key()

# Upload an encrypted image
image = client.upload.image_encrypted(
    "session-uuid-here",
    "/tmp/photo.jpg",
    server_key["publicKey"],
    filename="photo.jpg",
    mime_type="image/jpeg",
)
```

## Error Handling

All API errors raise typed exceptions that extend `AperturError`. See [Error Handling documentation](https://docs.apertur.ca/errors).

```python
from apertur import (
    Apertur,
    AperturError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

client = Apertur(api_key="aptr_live_...")

try:
    session = client.sessions.create()
    image = client.upload.image(session["uuid"], "/tmp/photo.jpg")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
except NotFoundError as e:
    print(f"Not found: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except ValidationError as e:
    print(f"Validation error: {e.message}")
except AperturError as e:
    print(f"API error {e.status_code}: {e.message} [{e.code}]")
```

## API Reference

Full API reference, guides, and changelog are available at [docs.apertur.ca](https://docs.apertur.ca).

## License

This package is open-source software licensed under the [MIT license](https://opensource.org/licenses/MIT).
