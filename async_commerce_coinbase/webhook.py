import hmac
import json
import typing

from .exceptions import SignatureVerificationError
from .resources.charge import Charge, PartialCharge
from .resources.invoice import Invoice

EventType = (
    typing.Literal["charge:confirmed"]
    | typing.Literal["charge:created"]
    | typing.Literal["charge:delayed"]
    | typing.Literal["charge:failed"]
    | typing.Literal["charge:pending"]
    | typing.Literal["charge:resolved"]
    | typing.Literal["invoice:created"]
    | typing.Literal["invoice:paid"]
    | typing.Literal["invoice:payment_pending"]
    | typing.Literal["invoice:unresolved"]
    | typing.Literal["invoice:viewed"]
    | typing.Literal["invoice:voided"]
)


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
    return data["event"]
