#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Set, TYPE_CHECKING

from foundation.business_rule import BusinessRuleBase

if TYPE_CHECKING:
    from product_catalog.domain.entities.product_unit import ProductUnit


class ProductMustHaveBaseUnitRule(BusinessRuleBase):
    def __init__(self, product, base_unit):
        message = 'ProductMustHaveBaseUnit'
        super(ProductMustHaveBaseUnitRule, self).__init__(message=message)

        self.product = product
        self.units = product.units  # type: Set[ProductUnit]
        self.base_unit = base_unit

    def is_broken(self) -> bool:
        if type(self.base_unit) is ProductUnit:
            return self.base_unit not in self.units
        elif type(self.base_unit) is str:
            return not self.product.get_unit_by_name(self.base_unit)
        else:
            return True  # broken
