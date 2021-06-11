#!/usr/bin/env python
# -*- coding: utf-8 -*-
from email_validator import validate_email, EmailNotValidError

from foundation.business_rule import BusinessRuleBase


class UserEmailMustBeValidRule(BusinessRuleBase):
    def __init__(self, email: str):
        message = self.__class__.__name__
        super(UserEmailMustBeValidRule, self).__init__(message=message)

        self.email = email

    def is_broken(self) -> bool:
        broken = True

        try:
            # Validate.
            validate_email(self.email)

            # Update with the normalized form.
            return not broken
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            return broken
