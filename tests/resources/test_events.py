import typing
from unittest import mock

import httpx
import pytest

from async_commerce_coinbase import Coinbase


@pytest.fixture
def coinbase() -> Coinbase:
    coinbase = Coinbase("test")
    coinbase.request = mock.AsyncMock()  # type: ignore
    coinbase.request.return_value = {"data": {"resource": "event"}}
    return coinbase


def test_list_events(coinbase: Coinbase) -> None:
    paginator = coinbase.list_events()
    assert paginator.url == "/events"


@pytest.mark.asyncio
async def test_get_event(coinbase: Coinbase) -> None:
    assert (await coinbase.get_event("test"))["resource"] == "event"
    request = typing.cast(
        httpx.Request, coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "GET"
    assert request.url == "/events/test"
