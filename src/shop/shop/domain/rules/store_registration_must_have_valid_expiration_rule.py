#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from foundation import BusinessRuleBase

if TYPE_CHECKING:
  from shop.domain.entities.shop_registration import ShopRegistration


class StoreRegistrationMustHaveValidExpirationRule(BusinessRuleBase):
  def __init__(self, registration):
    message = self.__class__.__name__
    super(StoreRegistrationMustHaveValidExpirationRule, self).__init__(message=message)

    self.reg = registration  # type:ShopRegistration

  def is_broken(self) -> bool:
    created_at = getattr(self.reg, 'created_at', None)
    if not created_at:
      return False
    elif datetime.now() - created_at > timedelta(days=2):
      return True  # broken

    return False
