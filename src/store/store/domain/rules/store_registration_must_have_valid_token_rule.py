#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

from store.domain.entities.registration_status import RegistrationWaitingForConfirmation

if TYPE_CHECKING:
    from store.domain.entities.store_registration import StoreRegistration

from foundation.business_rule import BusinessRuleBase


class StoreRegistrationMustHaveValidTokenRule(BusinessRuleBase):
    def __init__(self, registration):
        message = self.__class__.__name__
        super(StoreRegistrationMustHaveValidTokenRule, self).__init__(message=message)

        self.reg = registration  # type:StoreRegistration

    def is_broken(self) -> bool:
        return self.reg.status != RegistrationWaitingForConfirmation
