#!/usr/bin/env python
# -*- coding: utf-8 -*-

from foundation.business_rule import BusinessRuleBase

from store.domain.entities.registration_status import RegistrationStatus


class StoreRegistrationMustHaveValidTokenRule(BusinessRuleBase):
    def __init__(self, registration):
        message = self.__class__.__name__
        super(StoreRegistrationMustHaveValidTokenRule, self).__init__(message=message)

        self.reg = registration

    def is_broken(self) -> bool:
        return self.reg.status != RegistrationStatus.REGISTRATION_WAITING_FOR_CONFIRMATION
