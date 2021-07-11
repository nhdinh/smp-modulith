#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.domain.entities.store_manager_type import StoreManagerType
from store.domain.entities.store_owner import StoreUser


@dataclass(unsafe_hash=True)
class StoreManager:
    store_user: StoreUser
    store_role: StoreManagerType = StoreManagerType.MANAGER

    @property
    def email(self):
        return self.store_user.email
