import json
import typing
from unittest import mock

import httpx
import pytest

from async_commerce_coinbase import Coinbase
from async_commerce_coinbase.resources.types import Price


@pytest.fixture
def coinbase() -> Coinbase:
    coinbase = Coinbase("test")
    coinbase.request = mock.AsyncMock()  # type: ignore
    coinbase.request.return_value = {"data": {"resource": "charge"}}
    return coinbase


def test_list_charges(coinbase: Coinbase) -> None:
    paginator = coinbase.list_charges()
    assert paginator.url == "/charges"


@pytest.mark.asyncio
async def test_create_charge(coinbase: Coinbase) -> None:
    data = typing.cast(
        CreateChargeArguments,
        {
            "name": "name",
            "description": "description",
            "pricing_type": "fixed_price",
            "local_price": {"amount": 10, "currency": "TST"},
            "redirect_url": "redirect_url",
            "cancel_url": "cancel_url",
            "metadata": {"meta": "data"},
        },
    )
    assert (await coinbase.create_charge(**data))["resource"] == "charge"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "POST"
    assert request.url == "/charges"
    assert json.loads(request.content) == data


class CreateChargeArguments(typing.TypedDict):
    name: str
    description: str
    pricing_type: typing.Literal["no_price", "fixed_price"]
    local_price: Price
    redirect_url: str
    cancel_url: str
    metadata: dict[str, str]


@pytest.mark.asyncio
async def test_get_charge(coinbase: Coinbase) -> None:
    assert (await coinbase.get_charge("test"))["resource"] == "charge"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "GET"
    assert request.url == "/charges/test"


@pytest.mark.asyncio
async def test_cancel_charge(coinbase: Coinbase) -> None:
    assert (await coinbase.cancel_charge("test"))["resource"] == "charge"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "POST"
    assert request.url == "/charges/test/cancel"


@pytest.mark.asyncio
async def test_resolve_charge(coinbase: Coinbase) -> None:
    assert (await coinbase.resolve_charge("test"))["resource"] == "charge"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "POST"
    assert request.url == "/charges/test/resolve"
