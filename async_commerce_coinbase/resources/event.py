from __future__ import annotations

import typing

import httpx

from ..abc import AbstractRequestBase
from ..exceptions import CoinbaseHTTPError
from ..paginator import CoinbasePaginator
from .charge import PartialCharge

__all__ = ["Event", "CoinbaseEventResource"]


class Event(typing.TypedDict):
    id: str
    resource: typing.Literal["event"]
    type: str
    api_version: str
    created_at: str
    data: PartialCharge


class CoinbaseEventResource(AbstractRequestBase):
    def list_events(self) -> CoinbasePaginator[Event]:
        return CoinbasePaginator(self, "/events")

    async def show_events(self, code_or_id: str) -> Event:
        if "/" in code_or_id:
            # small protection against arbitrary requests
            raise CoinbaseHTTPError(f"'/' found in code_or_id: {code_or_id!r}")
        request = httpx.Request("GET", f"/events/{code_or_id}")
        response = await self.request(request)
        body = response.json()
        return body["data"]  # type: ignore
