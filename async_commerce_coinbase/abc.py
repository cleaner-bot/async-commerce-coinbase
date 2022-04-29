from abc import ABC

import httpx


class AbstractRequestBase(ABC):
    async def request(self, request: httpx.Request) -> httpx.Response:
        raise NotImplementedError
