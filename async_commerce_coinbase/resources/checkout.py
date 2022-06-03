from __future__ import annotations

import typing

import httpx

from ..abc import AbstractRequestBase
from ..exceptions import CoinbaseHTTPError
from ..paginator import CoinbasePaginator
from .types import Price, PricingType

__all__ = ["Checkout", "CoinbaseCheckoutResource"]


class Checkout(typing.TypedDict):
    id: str
    resource: typing.Literal["checkout"]
    name: str
    description: str
    logo_url: str
    request_info: list[str]
    pricing_type: PricingType


class CoinbaseCheckoutResource(AbstractRequestBase):
    def list_checkouts(self) -> CoinbasePaginator[Checkout]:
        return CoinbasePaginator(self, "/checkouts")

    async def create_checkout(
        self,
        name: str,
        description: str,
        requested_info: list[str],
        pricing_type: PricingType,
        local_price: Price,
    ) -> Checkout:
        body = {
            "name": name,
            "description": description,
            "requested_info": requested_info,
            "pricing_type": pricing_type,
            "local_price": local_price,
        }
        request = httpx.Request("POST", "/charges", json=body)
        response = await self.request(request)
        body = response.json()
        return body["data"]  # type: ignore

    async def get_checkout(self, code_or_id: str) -> Checkout:
        if "/" in code_or_id:
            # small protection against arbitrary requests
            raise CoinbaseHTTPError(f"'/' found in code_or_id: {code_or_id!r}")
        request = httpx.Request("GET", f"/checkouts/{code_or_id}")
        response = await self.request(request)
        body = response.json()
        return body["data"]  # type: ignore

    async def put_checkout(
        self,
        code_or_id: str,
        *,
        name: str | None = None,
        requested_info: list[str] | None = None,
        local_price: Price | None = None,
    ) -> Price:
        if "/" in code_or_id:
            # small protection against arbitrary requests
            raise CoinbaseHTTPError(f"'/' found in code_or_id: {code_or_id!r}")
        body: dict[str, typing.Any] = {}
        if name is not None:
            body["name"] = name
        if requested_info is not None:
            body["requested_info"] = requested_info
        if local_price is not None:
            body["local_price"] = local_price
        request = httpx.Request("PUT", f"/checkouts/{code_or_id}", json=body)
        response = await self.request(request)
        body = response.json()
        return body["data"]  # type: ignore

    async def delete_checkout(self, code_or_id: str) -> None:
        if "/" in code_or_id:
            # small protection against arbitrary requests
            raise CoinbaseHTTPError(f"'/' found in code_or_id: {code_or_id!r}")
        request = httpx.Request("DELETE", f"/checkouts/{code_or_id}")
        await self.request(request)
