from decimal import Decimal
from typing import Union

from foundation.value_objects import Money, currency
from foundation.value_objects.currency import _get_registered_currency_or_default


def get_money(amount: Union[Decimal, float, int], currency_str: str = None) -> Money:
    currency = _get_registered_currency_or_default(currency_str)

    return Money(currency, amount)
