#!/usr/bin/env python
# -*- coding: utf-8 -*-
from foundation.business_rule import BusinessRuleBase
from store import CountStoreOwnerByEmailQuery


class UserEmailMustBeUniqueRule(BusinessRuleBase):
    def __init__(self, email, count_store_owner_by_email_query: CountStoreOwnerByEmailQuery):
        message = self.__class__.__name__
        super(UserEmailMustBeUniqueRule, self).__init__(message=message)

        self.email = email
        self.q = count_store_owner_by_email_query

    def is_broken(self) -> bool:
        return self.q.query(email=self.email) > 0
