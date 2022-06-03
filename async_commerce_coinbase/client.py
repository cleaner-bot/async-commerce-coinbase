import httpx

from .exceptions import CoinbaseHTTPError, CoinbaseHTTPStatusError
from .resources.charge import CoinbaseChargeResource
from .resources.checkout import CoinbaseCheckoutResource
from .resources.event import CoinbaseEventResource
from .resources.invoice import CoinbaseInvoiceResource

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

    async def request(self, request: httpx.Request) -> httpx.Response:
        request = self.client.build_request(
            request.method,
            request.url,
            content=request.content,
            headers=request.headers,
            extensions=request.extensions,
        )
        response = await self.client.send(request)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            (reason,) = e.args
            if response.headers["content-type"].startswith("application/json"):
                error = response.json().get("error", None)
                if error is not None:
                    error_type = error.get("type")
                    error_message = error.get("message")
                    if error_type is not None and error_message is not None:
                        reason = f"{error_type}: {error_message}\n{reason}"

            raise CoinbaseHTTPStatusError(
                reason, request=e.request, response=e.response
            )

        content_type = response.headers["content-type"]
        if not content_type.startswith("application/json"):
            raise CoinbaseHTTPError(
                f"content-type is {content_type!r}, expected application/json"
            )

        return response
