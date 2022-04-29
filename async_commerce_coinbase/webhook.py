import hmac
import json
import typing

from .exceptions import SignatureVerificationError
from .resources.charge import Charge, PartialCharge


class Event(typing.TypedDict):
    id: str
    resource: typing.Literal["event"]
    type: str
    api_version: str
    created_at: str
    data: Charge | PartialCharge


def verify_webhook(body: str | bytes, secret: str, signature: str) -> Event:
    if hasattr(body, "encode"):
        body = body.encode()

    mac = hmac.digest(secret.encode(), body, "sha256")
    signature_mac = bytes.fromhex(signature)
    if not hmac.compare_digest(mac, signature_mac):
        raise SignatureVerificationError("signature mismatch")
    data = json.loads(body)
    return data["event"]
