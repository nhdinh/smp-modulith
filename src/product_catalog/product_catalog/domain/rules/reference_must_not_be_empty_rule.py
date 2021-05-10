#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase


class ReferenceMustNotBeEmptyRule(BusinessRuleBase):
    def __init__(self, reference: str, message=''):
        """
        Check reference string and assure such string is not empty

        :param reference: the `reference` string to check
        :param message: custom error message
        """
        if not message:
            message = 'Reference must not be empty'
        super(ReferenceMustNotBeEmptyRule, self).__init__(message=message)

        self.reference = reference

    def is_broken(self) -> bool:
        return not self.reference
