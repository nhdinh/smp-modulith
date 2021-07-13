#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import date
from typing import Optional

from foundation.value_objects import Money
from foundation.value_objects.factories import get_money
from store.domain.entities.shop_supplier import ShopSupplier
from store.domain.entities.shop_unit import ShopProductUnit


@dataclass(unsafe_hash=True)
class ProductPurchasePrice:
    def __init__(self, supplier: ShopSupplier, product_unit: ShopProductUnit, price: Money, tax: Optional[float],
                 effective_from: date):
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

    def __eq__(self, other):
        if not isinstance(other, ProductPurchasePrice):
            raise TypeError

        return self.supplier == other.supplier and self.product_unit == other.product_unit and self.price == other.price and self.tax == other.tax and self.effective_from == other.effective_from

    def __str__(self):
        return f"<PurchasePrice {self.price} supplier={self.supplier.supplier_name}> unit={self.product_unit.unit_name}>"
