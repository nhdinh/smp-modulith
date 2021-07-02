#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from typing import Optional

from foundation.value_objects import Money, Currency
from foundation.value_objects.factories import get_money
from store.domain.entities.store_supplier import StoreSupplierId, StoreSupplier
from store.domain.entities.store_unit import StoreProductUnit
from store.domain.entities.value_objects import StoreProductId


@dataclass(unsafe_hash=True)
class ProductPurchasePrice:
    def __init__(self, supplier: StoreSupplier, product_unit: StoreProductUnit, price: Money, tax: Optional[float],
                 effective_from: datetime):
        self.supplier = supplier
        self.product_unit = product_unit
        self._price = price.amount
        self.currency = price.currency.iso_code
        self.tax = tax
        self.effective_from = effective_from

    @property
    def price(self) -> Money:
        return get_money(amount=self._price, currency_str=self.currency)

    @price.setter
    def price(self, value: Money):
        self._price = value.amount
        self.currency = value.currency
