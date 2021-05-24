#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Set

from foundation.business_rule import BusinessRuleBase
from product_catalog.domain.entities.product import Product
from product_catalog.domain.entities.product_unit import ProductUnit


class ProductMustHaveBaseUnitRule(BusinessRuleBase):
    def __init__(self, product: Product, base_unit: str):
        message = 'ProductMustHaveBaseUnit'
        super(ProductMustHaveBaseUnitRule, self).__init__(message=message)

        self.units = product.units  # type: Set[ProductUnit]
        self.base_unit = base_unit

    def is_broken(self) -> bool:
        try:
            d = next(u for u in self.units if u.unit == self.base_unit)
            return False
        except StopIteration:
            return True
