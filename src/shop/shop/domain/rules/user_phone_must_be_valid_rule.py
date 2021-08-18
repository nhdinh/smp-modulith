#!/usr/bin/env python
# -*- coding: utf-8 -*-
import phonenumbers as phonenumbers

from foundation.business_rule import BusinessRuleBase
from shop.domain.entities.value_objects import ExceptionMessages


class UserMobileMustBeValidRule(BusinessRuleBase):
    def __init__(self, mobile_number: str):
        message = self.__class__.__name__
        super(UserMobileMustBeValidRule, self).__init__(message=ExceptionMessages.PHONE_NUMBER_IS_NOT_VALID)

        default_country_code = 'VN'
        if 'DEFAULT_COUNTRY_CODE' in globals():
            default_country_code = globals().get('DEFAULT_COUNTRY_CODE', 'VN')
        self.mn = phonenumbers.parse(mobile_number, default_country_code)

    def is_broken(self) -> bool:
        return not phonenumbers.is_valid_number(self.mn)
