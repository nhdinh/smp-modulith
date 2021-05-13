#!/usr/bin/env python
# -*- coding: utf-8 -*-
from identity.domain.value_objects import UserEmail
from foundation.business_rule import BusinessRuleBase


class EmailMustNotBeEmptyRule(BusinessRuleBase):
    def __init__(self, email: UserEmail):
        message = 'Email must not be empty'
        super(EmailMustNotBeEmptyRule, self).__init__(message=message)

        self.eml = email

    def is_broken(self) -> bool:
        return not self.eml
