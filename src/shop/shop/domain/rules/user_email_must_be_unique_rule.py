#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector

from foundation.business_rule import BusinessRuleBase
from shop.application.services.shop_user_counters import ShopUserCounter
from shop.domain.entities.value_objects import ExceptionMessages


class UserEmailMustBeUniqueRule(BusinessRuleBase):
  @injector.inject
  def __init__(self, email, user_counter_services: ShopUserCounter):
    message = self.__class__.__name__
    super(UserEmailMustBeUniqueRule, self).__init__(message=ExceptionMessages.EMAIL_HAS_BEEN_REGISTERED)

    self.email = email
    self.counter = user_counter_services

  def is_broken(self) -> bool:
    return self.counter.is_shop_user_email_existed(self.email)
