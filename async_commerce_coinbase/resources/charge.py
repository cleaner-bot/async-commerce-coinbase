from __future__ import annotations

import typing

import httpx

from .types import PricingType, Price
from ..abc import AbstractRequestBase
from ..exceptions import CoinbaseHTTPError
from ..paginator import CoinbasePaginator


__all__ = [
    "Charge",
    "PartialCharge",
    "PartialCheckout",
    "TimelinePoint",
    "PaymentThreshold",
    "Payment",
    "BlockInfo",
    "CoinbaseChargeResource",
]


class Charge(typing.TypedDict):
    id: str
    resource: typing.Literal["charge"]
    code: str
    name: str
    description: str
    logo_url: str
    hosted_url: str
    created_at: str
    confirmed_at: str
    expires_at: str
    checkout: PartialCheckout
    timeline: list[TimelinePoint]
    metadata: dict[str, str]
    pricing_type: PricingType
    pricing: dict[str, Price]
    payment_threshold: PaymentThreshold
    applied_threshold: Price
    applied_threshold_type: str
    payments: list[Payment]
    addresses: dict[str, str]


class PartialCharge(typing.TypedDict):
    id: str
    resource: typing.Literal["charge"]
    code: str
    name: str
    description: str
    logo_url: str
    hosted_url: str
    created_at: str
    expires_at: str
    timeline: list[TimelinePoint]
    metadata: dict[str, str]
    pricing_type: PricingType
    pricing: dict[str, Price]
    payments: list[Payment]
    payment_threshold: PaymentThreshold
    addresses: dict[str, str]
    redirect_url: str
    cancel_url: str


class PartialCheckout(typing.TypedDict):
    id: str


class TimelinePoint(typing.TypedDict):
    time: str
    status: str


class PaymentThreshold(typing.TypedDict):
    overpayment_absolute_threshold: Price
    overpayment_relative_threshold: float
    underpayment_absolute_threshold: Price
    underpayment_relative_threshold: float


class Payment(typing.TypedDict):
    network: str
    tranction_id: str
    status: str  # TODO: be more specific
    value: dict[str, Price]
    block: BlockInfo


class BlockInfo(typing.TypedDict):
    height: int
    hash: str
    confirmations_accumulated: int
    confirmations_required: int


class CoinbaseChargeResource(AbstractRequestBase):
    def list_charges(self) -> CoinbasePaginator[Charge]:
        return CoinbasePaginator(self, "/charges")

    async def create_charge(
        self,
        name: str,
        description: str,
        pricing_type: PricingType,
        local_price: Price,
        redirect_url: str,
        cancel_url: str,
        metadata: dict[str, str] = None,
    ) -> PartialCharge:
        body = {
            "name": name,
            "description": description,
            "pricing_type": pricing_type,
            "local_price": local_price,
            "redirect_url": redirect_url,
            "cancel_url": cancel_url,
            "metadata": metadata,
        }
        request = httpx.Request("POST", "/charges", json=body)
        response = await self.request(request)
        response_body = response.json()
        return response_body["data"]

    async def get_charge(self, code_or_id: str) -> Charge:
        if "/" in code_or_id:
            # small protection against arbitrary requests
            raise CoinbaseHTTPError(f"'/' found in code_or_id: {code_or_id!r}")
        request = httpx.Request("GET", f"/charges/{code_or_id}")
        response = await self.request(request)
        body = response.json()
        return body["data"]

    async def cancel_charge(self, code_or_id: str) -> PartialCharge:
        if "/" in code_or_id:
            # small protection against arbitrary requests
            raise CoinbaseHTTPError(f"'/' found in code_or_id: {code_or_id!r}")
        request = httpx.Request("POST", f"/charges/{code_or_id}/cancel")
        response = await self.request(request)
        body = response.json()
        return body["data"]

    async def resolve_charge(self, code_or_id: str) -> PartialCharge:
        if "/" in code_or_id:
            # small protection against arbitrary requests
            raise CoinbaseHTTPError(f"'/' found in code_or_id: {code_or_id!r}")
        request = httpx.Request("POST", f"/charges/{code_or_id}/resolve")
        response = await self.request(request)
        body = response.json()
        return body["data"]
