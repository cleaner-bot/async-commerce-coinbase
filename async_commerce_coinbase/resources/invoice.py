from __future__ import annotations

import typing

import httpx

from ..abc import AbstractRequestBase
from ..paginator import CoinbasePaginator
from .charge import PartialCharge
from .types import Price

__all__ = ["Invoice", "ChargeData", "CoinbaseInvoiceResource"]


class Invoice(typing.TypedDict):
    id: str
    resource: typing.Literal["invoice"]
    code: str
    status: str  # TODO
    business_name: str
    customer_name: str
    customer_email: str
    memo: str
    local_price: Price
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
        customer_name: str,
        memo: str,
        local_price: Price,
    ) -> Invoice:
        body = {
            "business_name": business_name,
            "customer_email": customer_email,
            "customer_name": customer_name,
            "memo": memo,
            "local_price": local_price,
        }
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
