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


def verify_signature(
    body: str | bytes, signature: str | bytes, secret: str | bytes
) -> Event:
    if isinstance(body, str):
        body = body.encode()
    if isinstance(signature, str):
        signature = bytes.fromhex(signature)
    if isinstance(secret, str):
        secret = secret.encode()

    mac = hmac.digest(secret, body, "sha256")
    if not hmac.compare_digest(mac, signature):
        raise SignatureVerificationError("signature mismatch")
    data = json.loads(body)
    return typing.cast(Event, data["event"])
