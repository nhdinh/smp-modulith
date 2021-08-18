#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase


class DefaultPassedRule(BusinessRuleBase):
  def __init__(self):
    super(DefaultPassedRule, self).__init__(message=self.__class__.__name__)

  def is_broken(self) -> bool:
    return False
