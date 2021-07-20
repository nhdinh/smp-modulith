#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase

from product_catalog.domain.entities.product_unit import ProductUnit


class UnitMustBeCalculatedToDefaultUnitRule(BusinessRuleBase):
    def __init__(self, product, product_unit):
        message = 'UnitMustBeCalculatedToDefaultUnitRule'
        super(UnitMustBeCalculatedToDefaultUnitRule, self).__init__(message=message)

        self.product = product

        if type(product_unit.base_unit) is ProductUnit:
            self.product_unit = product_unit.base_unit  # type:ProductUnit
        elif type(product_unit.base_unit) is str:
            self.product_unit = self.product.get_unit_by_name(product_unit.base_unit)  # type:ProductUnit

    def is_broken(self) -> bool:
        default_unit_found = self.product_unit.default
        product_unit = self.product_unit

        if not default_unit_found:
            while product_unit.base_unit:
                if product_unit.base_unit.default:
                    default_unit_found = True
                    break
                else:
                    product_unit = product_unit.base_unit

        return not default_unit_found
