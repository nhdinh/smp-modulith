#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.domain.entities.shop_manager_type import ShopManagerType
from store.domain.entities.shop_user import ShopUser


@dataclass(unsafe_hash=True)
class ShopManager:
    shop_user: ShopUser
    shop_role: ShopManagerType = ShopManagerType.MANAGER

    @property
    def email(self):
        return self.shop_user.email


@dataclass(unsafe_hash=True)
class ShopAdmin(ShopManager):
    shop_user: ShopUser
    shop_role: ShopManagerType = ShopManagerType.ADMIN
