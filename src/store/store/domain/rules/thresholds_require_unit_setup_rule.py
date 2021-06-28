#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase


class ThresholdsRequireUnitSetupRule(BusinessRuleBase):
    def __init__(self, restock_threshold: int, maxstock_threshold: int, default_unit: str):
        super(ThresholdsRequireUnitSetupRule, self).__init__(message=self.__class__.__name__)
        self.restock_t = restock_threshold
        self.maxstock_t = maxstock_threshold
        self.du = default_unit

    def is_broken(self) -> bool:
        return (self.restock_t >= 0 or self.maxstock_t >= 0) and (not self.du or self.du == '')
