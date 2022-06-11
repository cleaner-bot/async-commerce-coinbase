from __future__ import annotations

import typing

import httpx

from .abc import AbstractRequestBase

T = typing.TypeVar("T")
MAX_LIMIT_PER_PAGE = 100


class CoinbasePaginator(typing.Generic[T]):
    if typing.TYPE_CHECKING:  # pragma: no cover
        Self = typing.TypeVar("Self", bound="CoinbasePaginator[T]")

    _starting_after: str | None | bool
    _ending_before: str | None
    _pending: list[T]

    def __init__(
        self,
        coinbase: AbstractRequestBase,
        url: str,
        *,
        order: str = "desc",
        limit: int = MAX_LIMIT_PER_PAGE
    ) -> None:
        self.coinbase = coinbase
        self.url = url

        self.order = order
        self.limit = limit

        self._starting_after = None
        self._ending_before = None
        self._pending = []

    def __aiter__(self: Self) -> Self:
        self._starting_after = None
        self._ending_before = None
        self._pending.clear()
        return self

    async def __anext__(self) -> T:
        if self._pending:
            return self._pending.pop(0)
        elif self._starting_after is False:
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

        pagination = response["pagination"]
        if pagination["next_uri"] is None:
            # raise StopIteration on next anext call
            self._starting_after = False
        else:
            _, end = pagination["cursor"]
            self._starting_after = end

        self._pending.extend(typing.cast(typing.Sequence[T], response["data"]))
        return self._pending.pop(0)

    async def all(self) -> typing.Sequence[T]:
        all: list[T] = []
        async for item in self:
            all.append(item)
            all.extend(self._pending)
            self._pending.clear()
        return all

    async def chunk(
        self, chunk_size: int
    ) -> typing.AsyncGenerator[typing.Sequence[T], None]:
        chunk: list[T] = []
        async for item in self:
            chunk.append(item)
            if len(chunk) >= chunk_size:
                yield chunk[:chunk_size]
                chunk = chunk[chunk_size:]
        if chunk:
            yield chunk
