import json
import typing
from unittest import mock

import httpx
import pytest

from async_commerce_coinbase import Coinbase
from async_commerce_coinbase.resources.types import Money


@pytest.fixture
def coinbase() -> Coinbase:
    coinbase = Coinbase("test")
    coinbase.request = mock.AsyncMock()  # type: ignore
    coinbase.request.return_value = {"data": {"resource": "invoice"}}
    return coinbase


def test_list_invoices(coinbase: Coinbase) -> None:
    paginator = coinbase.list_invoices()
    assert paginator.url == "/invoices"


@pytest.mark.asyncio
async def test_create_invoice(coinbase: Coinbase) -> None:
    data = typing.cast(
        CreateInvoiceArguments,
        {
            "business_name": "business_name",
            "customer_email": "customer_email",
            "customer_name": "customer_name",
            "memo": "memo",
            "local_price": {"amount": 10, "currency": "TST"},
        },
    )
    assert (await coinbase.create_invoice(**data))["resource"] == "invoice"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "POST"
    assert request.url == "/invoices"
    assert json.loads(request.content) == data


class CreateInvoiceArguments(typing.TypedDict):
    business_name: str
    customer_email: str
    customer_name: str
    memo: str
    local_price: Money


@pytest.mark.asyncio
async def test_get_invoice(coinbase: Coinbase) -> None:
    assert (await coinbase.get_invoice("test"))["resource"] == "invoice"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "GET"
    assert request.url == "/invoices/test"


@pytest.mark.asyncio
async def test_void_invoice(coinbase: Coinbase) -> None:
    assert (await coinbase.void_invoice("test"))["resource"] == "invoice"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "PUT"
    assert request.url == "/invoices/test/void"


@pytest.mark.asyncio
async def test_resolve_invoice(coinbase: Coinbase) -> None:
    assert (await coinbase.resolve_invoice("test"))["resource"] == "invoice"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "PUT"
    assert request.url == "/invoices/test/resolve"
