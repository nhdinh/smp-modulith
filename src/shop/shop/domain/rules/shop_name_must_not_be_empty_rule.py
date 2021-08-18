#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase


class ShopNameMustNotBeEmptyRule(BusinessRuleBase):
  def __init__(self, shop_name: str):
    message = self.__class__.__name__
    super(ShopNameMustNotBeEmptyRule, self).__init__(message=message)

    self.shop_name = shop_name

  def is_broken(self) -> bool:
    return self.shop_name == ''
