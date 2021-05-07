#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase


class DisplayNameMustNotBeEmptyRule(BusinessRuleBase):
    def __init__(self, dn: str):
        message = 'Reference must not be empty'
        super(DisplayNameMustNotBeEmptyRule, self).__init__(message=message)

        self.display_name = dn

    def is_broken(self) -> bool:
        return not self.display_name
