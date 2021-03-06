import typing
from unittest import mock

import httpx
import pytest

from async_commerce_coinbase.paginator import CoinbasePaginator


@pytest.fixture
def paginator() -> CoinbasePaginator[str]:
    coinbase = mock.AsyncMock()
    pager = CoinbasePaginator(coinbase, "/test")  # type: ignore
    return pager


def test_paginator(paginator: CoinbasePaginator[str]) -> None:
    assert paginator.url == "/test"
    assert paginator.order == "desc"
    assert paginator.limit == 100


@pytest.mark.asyncio
async def test_iter(paginator: CoinbasePaginator[str]) -> None:
    paginator.coinbase.request.return_value = {  # type: ignore
        "pagination": {"next_uri": None},
        "data": ["foo", "bar"],
    }

    i = 0
    async for item in paginator:
        if i == 0:
            assert item == "foo"
        else:
            assert item == "bar"
        i += 1

    assert i == 2

    paginator.coinbase.request.assert_awaited_once()  # type: ignore
    request = typing.cast(
        httpx.Request, paginator.coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "GET"
    assert request.url == "/test?order=desc&limit=100&starting_after=&ending_before="


@pytest.mark.asyncio
async def test_all_single(paginator: CoinbasePaginator[str]) -> None:
    paginator.coinbase.request.return_value = {  # type: ignore
        "pagination": {"next_uri": None},
        "data": ["foo", "bar"],
    }

    assert await paginator.all() == ["foo", "bar"]

    paginator.coinbase.request.assert_awaited_once()  # type: ignore
    request = typing.cast(
        httpx.Request, paginator.coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "GET"
    assert request.url == "/test?order=desc&limit=100&starting_after=&ending_before="


@pytest.mark.asyncio
async def test_all_multiple(paginator: CoinbasePaginator[str]) -> None:
    paginator.coinbase.request.side_effect = [  # type: ignore
        {
            "pagination": {"next_uri": "x", "cursor": ["x", "abcdef"]},
            "data": ["foo", "bar"],
        },
        {"pagination": {"next_uri": None}, "data": ["foo", "bar"]},
    ]

    assert await paginator.all() == ["foo", "bar", "foo", "bar"]

    assert paginator.coinbase.request.await_count == 2  # type: ignore
    request = typing.cast(
        httpx.Request, paginator.coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "GET"
    assert (
        request.url == "/test?order=desc&limit=100&starting_after=abcdef&ending_before="
    )


@pytest.mark.asyncio
async def test_chunk(paginator: CoinbasePaginator[str]) -> None:
    paginator.coinbase.request.return_value = {  # type: ignore
        "pagination": {"next_uri": None},
        "data": ["foo", "bar"] * 10 + ["foo"],
    }

    i = 0
    async for chunk in paginator.chunk(2):
        if i < 10:
            assert chunk == ["foo", "bar"]
        else:
            assert chunk == ["foo"]
        i += 1

    assert i == 11

    paginator.coinbase.request.assert_awaited_once()  # type: ignore
    request = typing.cast(
        httpx.Request, paginator.coinbase.request.await_args.args[0]  # type: ignore
    )
    assert request.method == "GET"
    assert request.url == "/test?order=desc&limit=100&starting_after=&ending_before="
