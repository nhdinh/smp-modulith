#!/usr/bin/env python
# -*- coding: utf-8 -*-
import injector
from injector import inject

from foundation.business_rule import BusinessRuleBase
from store import CountStoreOwnerByEmailQuery, SqlCountStoreOwnerByEmailQuery


class UserEmailMustBeUniqueRule(BusinessRuleBase):
    @inject
    def __init__(self, email, count_store_owner_by_email_query: CountStoreOwnerByEmailQuery = None):
        message = self.__class__.__name__
        super(UserEmailMustBeUniqueRule, self).__init__(message=message)

        self.email = email
        self.q = count_store_owner_by_email_query
        if not self.q:
            inj = injector.Injector()
            self.q = inj.get(SqlCountStoreOwnerByEmailQuery)

    def is_broken(self) -> bool:
        return self.q.query(email=self.email) > 0
