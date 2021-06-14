#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase


class NewCatalogReferenceShouldNotExistedRule(BusinessRuleBase):
    def __init__(self, reference: str):
        super(NewCatalogReferenceShouldNotExistedRule, self).__init__(message=self.__class__.__name__)
        self.reference = reference

    def is_broken(self) -> bool:
        # check against the system catalog list
        raise NotImplementedError
