import typing

import httpx

from .abc import AbstractRequestBase

T = typing.TypeVar("T")


class CoinbasePaginator(typing.Generic[T]):
    Self = typing.TypeVar("Self", bound="CoinbasePaginator[T]")

    _starting_after: str | None | bool
    _ending_before: str | None

    def __init__(
        self,
        coinbase: AbstractRequestBase,
        url: str,
        *,
        order: str = "desc",
        limit: int = 100
    ) -> None:
        self.coinbase = coinbase
        self.url = url

        self.order = order
        self.limit = limit

        self._starting_after = None
        self._ending_before = None

    def __aiter__(self: Self) -> Self:
        self._starting_after = None
        self._ending_before = None
        return self

    async def __anext__(self) -> typing.Sequence[T]:
        if self._starting_after is False:
            raise StopAsyncIteration

        request = httpx.Request(
            "GET",
            self.url,
            params={
                "order": self.order,
                "limit": self.limit,
                "starting_after": self._starting_after,
                "ending_before": self._ending_before,
            },
        )
        response = await self.coinbase.request(request)
        body = response.json()

        pagination = body["pagination"]
        if pagination["next_uri"] is None:
            # raise StopIteration on next anext call
            self._starting_after = False
        else:
            _, end = pagination["cursor"]
            self._starting_after = end

        return body["data"]  # type: ignore

    async def all(self) -> typing.Sequence[T]:
        all: list[T] = []
        async for chunk in self:
            all.extend(chunk)
        return all

    async def chunk(self: Self, limit: int) -> Self:
        self.limit = limit
        return self
