#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation.business_rule import BusinessRuleBase
from shop.application.services.shop_user_counters import ShopUserCounter
from shop.domain.entities.value_objects import ExceptionMessages


class UserPhoneMustBeUniqueRule(BusinessRuleBase):
    @injector.inject
    def __init__(self, phone, user_counter_services: ShopUserCounter):
        super(UserPhoneMustBeUniqueRule, self).__init__(message=ExceptionMessages.PHONE_NUMBER_HAS_BEEN_REGISTERED)

        self.phone = phone
        self.counter = user_counter_services

    def is_broken(self) -> bool:
        return self.counter.is_shop_user_phone_existed(self.phone)
