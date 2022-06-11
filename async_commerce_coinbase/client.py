import logging
import typing

import httpx

from .exceptions import CoinbaseHTTPError, CoinbaseHTTPStatusError
from .resources.charge import CoinbaseChargeResource
from .resources.checkout import CoinbaseCheckoutResource
from .resources.event import CoinbaseEventResource
from .resources.invoice import CoinbaseInvoiceResource

logger = logging.getLogger(__name__)
COINBASE_VERSION = "2018-03-22"
COINBASE_BASE_URL = "https://api.commerce.coinbase.com"


class Coinbase(
    CoinbaseChargeResource,
    CoinbaseCheckoutResource,
    CoinbaseInvoiceResource,
    CoinbaseEventResource,
):
    client: httpx.AsyncClient

    def __init__(
        self, api_key: str, *, client: httpx.AsyncClient | None = None
    ) -> None:
        if client is None:
            client = httpx.AsyncClient(base_url=COINBASE_BASE_URL)

        client.headers["X-CC-Version"] = COINBASE_VERSION
        client.headers["X-CC-Api-Key"] = api_key
        self.client = client

    async def request(self, request: httpx.Request) -> typing.Any:
        request = self.client.build_request(
            request.method,
            request.url,
            content=request.content,
            headers=request.headers,
            extensions=request.extensions,
        )
        response = await self.client.send(request)

        content_type = response.headers["content-type"]
        if not content_type.startswith("application/json"):
            raise CoinbaseHTTPError(
                f"content-type is {content_type!r}, expected application/json"
            )

        body = response.json()

        if warnings := body.get("warnings"):
            for warning in warnings:
                logger.debug(f"coinbase warning: {warning}")

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            (reason,) = e.args
            if error := body.get("error", None):
                if (error_type := error.get("type")) and (
                    error_message := error.get("message")
                ):
                    reason = f"{error_type}: {error_message}\n{reason}"

            raise CoinbaseHTTPStatusError(
                reason, request=e.request, response=e.response
            )

        return body

    def assert_code(self, code_or_id: str) -> None:
        if "/" in code_or_id:
            raise CoinbaseHTTPError(f"'/' found in code_or_id: {code_or_id!r}")
