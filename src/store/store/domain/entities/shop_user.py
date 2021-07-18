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
    user_id: SystemUserId
    email: str
    mobile: str
    shop_role: ShopUserType
