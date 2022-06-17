import typing

__all__ = ["PricingType", "Money"]

T = typing.TypeVar("T")
PricingType = typing.Union[typing.Literal["no_price"], typing.Literal["fixed_price"]]


class Money(typing.TypedDict):
    amount: float
    currency: str
