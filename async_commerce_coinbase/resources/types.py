import typing


__all__ = ["PricingType", "Price"]

T = typing.TypeVar("T")
PricingType = typing.Union[typing.Literal["no_price"], typing.Literal["fixed_price"]]


class Price(typing.TypedDict):
    amount: float
    currency: str
