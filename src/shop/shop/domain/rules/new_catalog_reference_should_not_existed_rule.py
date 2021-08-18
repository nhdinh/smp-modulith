#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import Set

from foundation.business_rule import BusinessRuleBase


class NewCatalogReferenceShouldNotExistedRule(BusinessRuleBase):
    def __init__(self, reference: str, store_catalog_list: Set[str]):
        super(NewCatalogReferenceShouldNotExistedRule, self).__init__(message=self.__class__.__name__)
        self.reference = reference
        self.store_catalog_list = store_catalog_list

    def is_broken(self) -> bool:
        return self.reference in self.store_catalog_list
