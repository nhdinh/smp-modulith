#!/usr/bin/env python
# -*- coding: utf-8 -*-
from email_validator import EmailNotValidError, validate_email

from auth.domain.value_objects import UserEmail
from foundation.business_rule import BusinessRuleBase


class EmailMustBeValidAddressRule(BusinessRuleBase):
    def __init__(self, email: UserEmail):
        message = 'Email address is not valid'
        super(EmailMustBeValidAddressRule, self).__init__(message=message)

        self.eml = email

    def is_broken(self) -> bool:
        try:
            validate_email(self.eml)
            return False
        except EmailNotValidError:
            return True
