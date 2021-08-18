#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from foundation.business_rule import BusinessRuleBase


class PasswordMustMeetRequirementRule(BusinessRuleBase):
  def __init__(self, password: str):
    message = 'Password doesn\'t meet requirement'
    super(PasswordMustMeetRequirementRule, self).__init__(message=message)

    self.passwd = password

  def is_broken(self) -> bool:
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat = re.compile(reg)

    # searching regex
    mat = re.search(pat, self.passwd)

    return not self.passwd or len(self.passwd) <= 6 or not mat
