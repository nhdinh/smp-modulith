#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from typing import NewType

from store.domain.entities.shop_user_type import ShopUserType

SystemUserId = NewType("SystemUserId", tp=str)


class SystemUserStatus(Enum):
    NORMAL = 'NORMAL'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


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


@dataclass(unsafe_hash=True)
class ShopUser:
    _system_user: SystemUser
    shop_role: ShopUserType

    @property
    def system_user_id(self) -> SystemUserId:
        return self._system_user.user_id

    @property
    def email(self) -> str:
        return self._system_user.email

    @property
    def mobile(self) -> str:
        return self._system_user.mobile

    @property
    def confirmed_at(self) -> datetime:
        return self._system_user.confirmed_at

    @property
    def status(self) -> SystemUserStatus:
        return self._system_user.status
