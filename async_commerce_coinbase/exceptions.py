import httpx


class CoinbaseException(Exception):
    pass


class CoinbaseHTTPError(CoinbaseException, httpx.HTTPError):
    pass


class CoinbaseHTTPStatusError(CoinbaseHTTPError, httpx.HTTPStatusError):
    pass


class SignatureVerificationError(CoinbaseException):
    pass
