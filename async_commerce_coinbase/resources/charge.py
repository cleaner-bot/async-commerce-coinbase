from __future__ import annotations

import typing

import httpx

from ..abc import AbstractRequestBase
from ..paginator import CoinbasePaginator
from .types import Money, PricingType

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
    pricing: dict[str, Money]
    payment_threshold: PaymentThreshold
    applied_threshold: Money
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
    pricing: dict[str, Money]
    payments: list[Payment]
    payment_threshold: PaymentThreshold
    addresses: dict[str, str]
    redirect_url: str
    cancel_url: str
    # undocumented
    exchange_rates: dict[str, str]
    local_exchange_rates: dict[str, str]
    fees_settled: bool
    offchain_eligible: bool
    organization_name: str
    pwcb_only: bool
    support_email: str
    utxo: bool


class PartialCheckout(typing.TypedDict):
    id: str


class TimelinePoint(typing.TypedDict, total=False):
    time: str
    status: typing.Literal["NEW", "PENDING", "COMPLETED", "EXPIRED", "UNRESOLVED", "RESOLVED", "CANCELED", "REFUND PENDING", "REFUNDED"]
    context: str


class PaymentThreshold(typing.TypedDict):
    overpayment_absolute_threshold: Money
    overpayment_relative_threshold: float
    underpayment_absolute_threshold: Money
    underpayment_relative_threshold: float


class Payment(typing.TypedDict):
    network: str
    tranction_id: str
    status: str  # TODO: be more specific
    value: dict[str, Money]
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
        local_price: Money,
        redirect_url: str,
        cancel_url: str,
        metadata: dict[str, str] | None = None,
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
        return typing.cast(PartialCharge, response["data"])

    async def get_charge(self, code_or_id: str) -> Charge:
        self.assert_code(code_or_id)
        request = httpx.Request("GET", f"/charges/{code_or_id}")
        response = await self.request(request)
        return typing.cast(Charge, response["data"])

    async def cancel_charge(self, code_or_id: str) -> PartialCharge:
        self.assert_code(code_or_id)
        request = httpx.Request("POST", f"/charges/{code_or_id}/cancel")
        response = await self.request(request)
        return typing.cast(PartialCharge, response["data"])

    async def resolve_charge(self, code_or_id: str) -> PartialCharge:
        self.assert_code(code_or_id)
        request = httpx.Request("POST", f"/charges/{code_or_id}/resolve")
        response = await self.request(request)
        return typing.cast(PartialCharge, response["data"])
