import hmac
import json
import typing

from .exceptions import SignatureVerificationError
from .resources.charge import Charge, PartialCharge
from .resources.invoice import Invoice

EventType = typing.Literal[
    "charge:confirmed",
    "charge:created",
    "charge:delayed",
    "charge:failed",
    "charge:pending",
    "charge:resolved",
    "invoice:created",
    "invoice:paid",
    "invoice:payment_pending",
    "invoice:unresolved",
    "invoice:viewed",
    "invoice:voided",
]


class Event(typing.TypedDict):
    id: str
    resource: typing.Literal["event"]
    type: EventType
    api_version: str
    created_at: str
    data: Charge | PartialCharge | Invoice


def verify_signature(body: str | bytes, signature: str, secret: str) -> Event:
    if isinstance(body, str):
        body = body.encode()

    mac = hmac.digest(secret.encode(), body, "sha256")
    signature_mac = bytes.fromhex(signature)
    if not hmac.compare_digest(mac, signature_mac):
        raise SignatureVerificationError("signature mismatch")
    data = json.loads(body)
    return data["event"]  # type: ignore
