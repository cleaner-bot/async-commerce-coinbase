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
    coinbase.request.return_value = {"data": {"resource": "checkout"}}
    return coinbase


def test_list_checkouts(coinbase: Coinbase) -> None:
    paginator = coinbase.list_checkouts()
    assert paginator.url == "/checkouts"


@pytest.mark.asyncio
async def test_create_checkout(coinbase: Coinbase) -> None:
    data = typing.cast(
        CreateCheckoutArguments,
        {
            "name": "name",
            "description": "description",
            "requested_info": ["test123", "test456"],
            "pricing_type": "fixed_price",
            "local_price": {"amount": 10, "currency": "TST"},
        },
    )
    assert (await coinbase.create_checkout(**data))["resource"] == "checkout"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "POST"
    assert request.url == "/checkouts"
    assert json.loads(request.content) == data


class CreateCheckoutArguments(typing.TypedDict):
    name: str
    description: str
    requested_info: list[str]
    pricing_type: typing.Literal["no_price", "fixed_price"]
    local_price: Price


@pytest.mark.asyncio
async def test_get_checkout(coinbase: Coinbase) -> None:
    assert (await coinbase.get_checkout("test"))["resource"] == "checkout"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "GET"
    assert request.url == "/checkouts/test"


@pytest.mark.asyncio
async def test_update_checkout(coinbase: Coinbase) -> None:
    assert (
        await coinbase.update_checkout(
            "test",
            name="name",
            requested_info=["abc", "def"],
            local_price={"amount": 1337, "currency": "TST2"},
        )
    )["resource"] == "checkout"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "PUT"
    assert request.url == "/checkouts/test"


@pytest.mark.asyncio
async def test_update_checkout_without_arguments(coinbase: Coinbase) -> None:
    with pytest.raises(ValueError):
        await coinbase.update_checkout("test")


@pytest.mark.asyncio
async def test_delete_checkout(coinbase: Coinbase) -> None:
    assert await coinbase.delete_checkout("test") is None
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "DELETE"
    assert request.url == "/checkouts/test"
