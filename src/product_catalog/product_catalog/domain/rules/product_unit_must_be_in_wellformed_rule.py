#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase
from product_catalog.domain.entities.product_unit import ProductUnit


class ProductUnitMustBeInWellformedRule(BusinessRuleBase):
    def __init__(self, product_unit: ProductUnit):
        message = 'ProductUnitMustBeInWellformedRule'
        super(ProductUnitMustBeInWellformedRule, self).__init__(message=message)

        self.product_unit = product_unit

    def is_broken(self) -> bool:
        raise NotImplementedError
