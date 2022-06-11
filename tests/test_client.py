import typing
from unittest import mock

import httpx
import pytest

from async_commerce_coinbase import Coinbase, CoinbaseHTTPError, CoinbaseHTTPStatusError


def forged_coinbase(
    return_value: typing.Any,
    raise_for_status: bool = False,
    content_type: str = "application/json",
) -> Coinbase:
    mocked_return = mock.Mock()
    mocked_return.headers = {"content-type": content_type}
    mocked_return.json.return_value = return_value
    if raise_for_status:
        mocked_return.raise_for_status.side_effect = httpx.HTTPStatusError(
            "test error", request=None, response=None  # type: ignore
        )

    coinbase = Coinbase("test")
    coinbase.client.send = mock.AsyncMock()  # type: ignore
    coinbase.client.send.return_value = mocked_return
    return coinbase


def test_client() -> None:
    coinbase = Coinbase("test")
    assert coinbase.client.headers["X-CC-Version"]
    assert coinbase.client.headers["X-CC-Api-Key"] == "test"

    coinbase = Coinbase(
        "test", client=httpx.AsyncClient(headers={"X-CC-Version": "something wrong"})
    )
    assert coinbase.client.headers["X-CC-Version"] != "something wrong"
    assert coinbase.client.headers["X-CC-Api-Key"] == "test"


@pytest.mark.asyncio
async def test_request() -> None:
    coinbase = forged_coinbase({"value": "test"})
    request = httpx.Request("GET", "/test")
    response = await coinbase.request(request)
    assert response == {"value": "test"}


@pytest.mark.asyncio
async def test_request_with_application_json_utf8() -> None:
    coinbase = forged_coinbase(
        {"value": "test"}, content_type="application/json; charset=utf-8"
    )
    request = httpx.Request("GET", "/test")
    response = await coinbase.request(request)
    assert response == {"value": "test"}


@pytest.mark.asyncio
async def test_request_with_invalid_content_type() -> None:
    coinbase = forged_coinbase({"value": "test"}, content_type="application/error")
    request = httpx.Request("GET", "/test")
    with pytest.raises(CoinbaseHTTPError):
        await coinbase.request(request)


@pytest.mark.asyncio
async def test_request_with_error() -> None:
    coinbase = forged_coinbase({"value": "test"}, True)
    request = httpx.Request("GET", "/test")
    with pytest.raises(CoinbaseHTTPStatusError, match="test error"):
        await coinbase.request(request)


@pytest.mark.asyncio
async def test_request_with_error_message() -> None:
    coinbase = forged_coinbase(
        {"value": "test", "error": {"type": "ETYPE", "message": "EMESSAGE"}}, True
    )
    request = httpx.Request("GET", "/test")
    with pytest.raises(CoinbaseHTTPStatusError, match="ETYPE: EMESSAGE\ntest error"):
        await coinbase.request(request)


@pytest.mark.asyncio
async def test_request_with_warnings() -> None:
    coinbase = forged_coinbase({"value": "test", "warnings": ["test123", "test456"]})
    request = httpx.Request("GET", "/test")
    with mock.patch("async_commerce_coinbase.client.logger") as logger_mock:
        response = await coinbase.request(request)
        assert logger_mock.debug.mock_calls == [
            mock.call("coinbase warning: test123"),
            mock.call("coinbase warning: test456"),
        ]
    assert response["value"] == "test"


@pytest.mark.parametrize(
    "value,failure",
    [
        ("test", False),
        ("..", True),
        ("test/cancel", True),
        ("../charges/test", True),
    ],
)
def test_assert_code(value: str, failure: str) -> None:
    coinbase = Coinbase("test")

    if failure:
        with pytest.raises(ValueError):
            coinbase.assert_code(value)

    else:
        coinbase.assert_code(value)
