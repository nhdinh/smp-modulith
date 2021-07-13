#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from typing import NewType

from store.domain.entities.shop_user_type import ShopUserType

ShopUserId = NewType("ShopUserId", tp=str)


class SystemUserStatus(Enum):
    NORMAL = 'NORMAL'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


@dataclass
class SystemUser:
    user_id: ShopUserId
    email: str
    mobile: str
    hashed_password: str
    confirmed_at: datetime
    status: SystemUserStatus

    def __hash__(self):
        return hash(self.email)


@dataclass
class ShopUserBase:
    _shop_user: SystemUser

    @property
    def user_id(self) -> ShopUserId:
        return self._shop_user.user_id

    @property
    def email(self) -> str:
        return self._shop_user.email

    @property
    def mobile(self) -> str:
        return self._shop_user.mobile

    @property
    def confirmed_at(self) -> datetime:
        return self._shop_user.confirmed_at

    @property
    def status(self) -> SystemUserStatus:
        return self._shop_user.status


@dataclass(unsafe_hash=True)
class ShopUser(ShopUserBase):
    shop_role: ShopUserType = ShopUserType.MANAGER


@dataclass(unsafe_hash=True)
class ShopAdmin(ShopUserBase):
    shop_role: ShopUserType = ShopUserType.ADMIN
