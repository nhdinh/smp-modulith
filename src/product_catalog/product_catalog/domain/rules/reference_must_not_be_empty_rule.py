#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase


class ReferenceMustNotBeEmptyRule(BusinessRuleBase):
    def __init__(self, reference: str):
        message = 'Reference must not be empty'
        super(ReferenceMustNotBeEmptyRule, self).__init__(message=message)

        self.reference = reference

    def is_broken(self) -> bool:
        return not self.reference
