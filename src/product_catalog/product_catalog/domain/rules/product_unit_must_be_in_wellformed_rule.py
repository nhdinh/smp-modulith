#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase
from product_catalog.domain.entities.product_unit import ProductUnit, DEFAULT_UNIT_CONVERSION_MULTIPLIER_FACTOR


class ProductUnitMustBeInWellformedRule(BusinessRuleBase):
    def __init__(self, product_unit: ProductUnit):
        message = 'ProductUnit is not in a wellformed data'
        super(ProductUnitMustBeInWellformedRule, self).__init__(message=message)
        self.pu = product_unit

    def is_broken(self):
        _d = self.pu.default
        _b_none = self.pu.base_unit is None
        _m_neg = self.pu.multiplier == DEFAULT_UNIT_CONVERSION_MULTIPLIER_FACTOR

        if self.pu.unit is None:
            # logger.debug('PU.unit is None')
            return True

        # default but base_unit is not None; or multiplier is not Negative
        if _d and ((not _b_none or not _m_neg) or (not _b_none and not _m_neg)):
            # logger.debug(f'is_default but base is not None or multiplier !== {ProductUnit.DEFAULT_MULTIPLIER_FACTOR}')
            return True

        # not default but base_unit is None or multiplier is negative
        if not _d and (_b_none or _m_neg):
            # logger.debug('not is_default but base is None or multiplier is neg')
            return True

        # not default but unit and base_unit are the same
        if not _d and self.pu.unit == self.pu.base_unit:
            # logger.debug('not default but 2 unit and base_unit is the same')
            return True

        # multiplier less than or equal 0, and != -1 (default value if the ProductUnit is default)
        if self.pu.multiplier != DEFAULT_UNIT_CONVERSION_MULTIPLIER_FACTOR and self.pu.multiplier <= 0:
            # logger.debug(f'multiplier !== {ProductUnit.DEFAULT_MULTIPLIER_FACTOR} and < 0')
            return True

        return False
