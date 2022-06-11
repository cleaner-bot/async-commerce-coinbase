import typing
from abc import ABC

import httpx


class AbstractRequestBase(ABC):
    async def request(self, request: httpx.Request) -> typing.Any:
        raise NotImplementedError  # pragma: no cover

    def assert_code(self, code: str) -> None:
        raise NotImplementedError  # pragma: no cover
