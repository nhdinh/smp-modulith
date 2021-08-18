#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from shop.domain.entities.value_objects import ShopUserType, SystemUserId, SystemUserStatus, GenericShopItemStatus


@dataclass
class SystemUser:
    user_id: SystemUserId
    email: str
    mobile: str
    hashed_password: str
    confirmed_at: datetime
    status: SystemUserStatus

    def __hash__(self):
        return hash(self.email)


@dataclass
class ShopUser:
    user_id: SystemUserId
    email: Optional[str] = ''
    mobile: Optional[str] = ''
    shop_role: Optional[ShopUserType] = ShopUserType.MANAGER
    status: GenericShopItemStatus = GenericShopItemStatus.NORMAL

    def __hash__(self):
        # return hash from _shop_id (backref of Shop), user_id and shop_role
        shop = getattr(self, '_shop', None)
        return hash((shop.shop_id if shop else None, self.user_id, self.shop_role))

    def __eq__(self, other):
        if not other or not isinstance(other, ShopUser):
            return False

        shop_comparison = True
        if getattr(self, '_shop', None) and getattr(other, '_shop', None):
            shop_comparison = self._shop == other._shop

        return self.user_id == other.user_id and shop_comparison
