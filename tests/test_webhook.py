import hmac
import json
import typing

import pytest

from async_commerce_coinbase import SignatureVerificationError, webhook
from async_commerce_coinbase.resources.invoice import Invoice


def test_verify() -> None:
    expected = {
        "id": "test",
        "resource": "event",
        "type": "charge:confirmed",
        "api_version": "test",
        "created_at": "test",
        "data": typing.cast(Invoice, {}),
    }
    body = json.dumps({"id": 10, "scheduled_for": 0, "event": expected})
    secret = "amazing testing"
    signature = hmac.digest(secret.encode(), body.encode(), "sha256")
    assert webhook.verify_signature(body, signature.hex(), secret) == expected


def test_verify_invalid_signature() -> None:
    with pytest.raises(SignatureVerificationError, match="signature mismatch"):
        assert webhook.verify_signature(b"", b"", b"")
