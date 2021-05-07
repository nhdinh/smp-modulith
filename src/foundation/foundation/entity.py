#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase, BusinessRuleValidationError


class Entity:
    def check_rule(self, rule: BusinessRuleBase):
        if rule.is_broken():
            raise BusinessRuleValidationError(rule)
