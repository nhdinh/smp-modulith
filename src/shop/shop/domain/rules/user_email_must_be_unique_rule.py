#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation.business_rule import BusinessRuleBase

from store.application.services.user_counter_services import UserCounters


class UserEmailMustBeUniqueRule(BusinessRuleBase):
    @injector.inject
    def __init__(self, email, user_counter_services: UserCounters):
        message = self.__class__.__name__
        super(UserEmailMustBeUniqueRule, self).__init__(message=message)

        self.email = email
        self.counter = user_counter_services

    def is_broken(self) -> bool:
        return self.counter.count(self.email) > 0
