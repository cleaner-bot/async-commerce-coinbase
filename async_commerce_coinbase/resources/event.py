from __future__ import annotations

import typing

import httpx

from ..abc import AbstractRequestBase
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

    async def get_event(self, code_or_id: str) -> Event:
        self.assert_code(code_or_id)
        request = httpx.Request("GET", f"/events/{code_or_id}")
        response = await self.request(request)
        return typing.cast(Event, response["data"])
