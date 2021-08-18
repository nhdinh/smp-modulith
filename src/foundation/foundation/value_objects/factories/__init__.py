#!/usr/bin/env python
# -*- coding: utf-8 -*-

from decimal import Decimal
from typing import Union

from foundation.value_objects import Currency, Money
from foundation.value_objects.currency import _get_registered_currency_or_default


def get_money(amount: Union[Decimal, float, int], currency_str: str = None) -> Money:
    currency = _get_registered_currency_or_default(currency_str)  # type: Currency

    return Money(currency, amount)


__all__ = ["get_money"]
