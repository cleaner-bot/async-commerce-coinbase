from __future__ import annotations

import typing

import httpx

from ..abc import AbstractRequestBase
from ..paginator import CoinbasePaginator
from .charge import PartialCharge
from .types import Money

__all__ = ["Invoice", "ChargeData", "CoinbaseInvoiceResource"]


class Invoice(typing.TypedDict):
    id: str
    resource: typing.Literal["invoice"]
    code: str
    status: str  # TODO
    business_name: str
    customer_name: str | None
    customer_email: str
    memo: str | None
    local_price: Money
    hosted_url: str
    created_at: str
    updated_at: str
    charge: ChargeData


class ChargeData(typing.TypedDict):
    data: PartialCharge


class CoinbaseInvoiceResource(AbstractRequestBase):
    def list_invoices(self) -> CoinbasePaginator[Invoice]:
        return CoinbasePaginator(self, "/invoices")

    async def create_invoice(
        self,
        business_name: str,
        customer_email: str,
        local_price: Money,
        memo: str | None = None,
        customer_name: str | None = None,
    ) -> Invoice:
        body = {
            "business_name": business_name,
            "customer_email": customer_email,
            "memo": memo,
            "local_price": local_price,
        }
        if customer_name is not None:
            body["customer_name"] = customer_name
        if memo is not None:
            body["memo"] = memo
        request = httpx.Request("POST", "/invoices", json=body)
        response = await self.request(request)
        return typing.cast(Invoice, response["data"])

    async def get_invoice(self, code_or_id: str) -> Invoice:
        self.assert_code(code_or_id)
        request = httpx.Request("GET", f"/invoices/{code_or_id}")
        response = await self.request(request)
        return typing.cast(Invoice, response["data"])

    async def void_invoice(self, code_or_id: str) -> Invoice:
        self.assert_code(code_or_id)
        request = httpx.Request("PUT", f"/invoices/{code_or_id}/void")
        response = await self.request(request)
        return typing.cast(Invoice, response["data"])

    async def resolve_invoice(self, code_or_id: str) -> Invoice:
        self.assert_code(code_or_id)
        request = httpx.Request("PUT", f"/invoices/{code_or_id}/resolve")
        response = await self.request(request)
        return typing.cast(Invoice, response["data"])
