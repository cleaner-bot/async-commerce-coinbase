from __future__ import annotations

import typing

import httpx

from ..abc import AbstractRequestBase
from ..paginator import CoinbasePaginator
from .types import Money, PricingType

__all__ = ["Checkout", "CoinbaseCheckoutResource"]


class Checkout(typing.TypedDict):
    id: str
    resource: typing.Literal["checkout"]
    name: str
    description: str
    logo_url: str
    requested_info: list[RequestedInfo]
    pricing_type: PricingType


RequestedInfo = typing.Literal["name", "email"]


class CoinbaseCheckoutResource(AbstractRequestBase):
    def list_checkouts(self) -> CoinbasePaginator[Checkout]:
        return CoinbasePaginator(self, "/checkouts")

    async def create_checkout(
        self,
        name: str,
        description: str,
        requested_info: list[RequestedInfo],
        pricing_type: PricingType,
        local_price: Money,
    ) -> Checkout:
        body = {
            "name": name,
            "description": description,
            "requested_info": requested_info,
            "pricing_type": pricing_type,
            "local_price": local_price,
        }
        request = httpx.Request("POST", "/checkouts", json=body)
        response = await self.request(request)
        return typing.cast(Checkout, response["data"])

    async def get_checkout(self, code_or_id: str) -> Checkout:
        self.assert_code(code_or_id)
        request = httpx.Request("GET", f"/checkouts/{code_or_id}")
        response = await self.request(request)
        return typing.cast(Checkout, response["data"])

    async def update_checkout(
        self,
        id: str,
        *,
        name: str | None = None,
        requested_info: list[RequestedInfo] | None = None,
        local_price: Money | None = None,
    ) -> Checkout:
        self.assert_code(id)
        body: dict[str, typing.Any] = {}
        if name is not None:
            body["name"] = name
        if requested_info is not None:
            body["requested_info"] = requested_info
        if local_price is not None:
            body["local_price"] = local_price
        if not body:
            raise ValueError(
                "must specify name, requested_info or local_price to overwrite"
            )
        request = httpx.Request("PUT", f"/checkouts/{id}", json=body)
        response = await self.request(request)
        return typing.cast(Checkout, response["data"])

    async def delete_checkout(self, id: str) -> None:
        self.assert_code(id)
        request = httpx.Request("DELETE", f"/checkouts/{id}")
        await self.request(request)
