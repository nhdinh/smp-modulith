#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase


class StoreNameMustNotBeEmptyRule(BusinessRuleBase):
    def __init__(self, store_name: str):
        message = self.__class__.__name__
        super(StoreNameMustNotBeEmptyRule, self).__init__(message=message)

        self.store_name = store_name

    def is_broken(self) -> bool:
        return self.store_name == ''
