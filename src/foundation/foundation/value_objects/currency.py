from typing import Type, Dict


class Currency:
    decimal_precision = 2
    iso_code = "OVERRIDE"
    symbol = "OVERRIDE"


class USD(Currency):
    iso_code = "USD"
    symbol = "$"


class VND(Currency):
    iso_code = "VND"
    symbol = "VND"


REGISTERED_CURRENCIES = [
    USD, VND
]


def _get_registered_currency_or_default(currency: str) -> Type[Currency]:
    _REG_CURRENCIES = {c.iso_code: c for c in REGISTERED_CURRENCIES}  # type:Dict
    if not currency or currency.strip().upper() not in _REG_CURRENCIES.keys():
        raise TypeError(f"The Currency {currency} is not supported.")
    else:
        return _REG_CURRENCIES[currency.strip().upper()]
