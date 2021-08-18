#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase


class DisplayNameMustNotBeEmptyRule(BusinessRuleBase):
  def __init__(self, dn: str, message=''):
    """
    Check the display name string is not none or empty

    :param dn: the display_name to check
    :param message: custom message
    """
    if not message:
      message = 'Display name must not be empty'
    super(DisplayNameMustNotBeEmptyRule, self).__init__(message=message)

    self.display_name = dn

  def is_broken(self) -> bool:
    return not self.display_name
