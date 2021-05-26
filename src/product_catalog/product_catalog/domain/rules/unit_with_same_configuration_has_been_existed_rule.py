#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase
from product_catalog.domain.entities.product_unit import ProductUnit


class UnitWithSameConfigurationHasBeenExistedRule(BusinessRuleBase):
    def __init__(self, product, product_unit):
        message = 'UnitWithSameConfigurationHasBeenExistedRule'
        super(UnitWithSameConfigurationHasBeenExistedRule, self).__init__(message=message)

        self.product = product
        self.product_unit = product_unit  # type:ProductUnit

    def is_broken(self) -> bool:
        base = self.product_unit.base_unit
        multiplier = self.product_unit.multiplier

        try:
            check = next(u for u in self.product.units if u.base_unit == base and u.multiplier == multiplier)

            if check:
                return True  # broken
        except StopIteration:
            pass

        return False  # good to go
