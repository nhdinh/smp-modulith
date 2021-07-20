#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from foundation import Event


@dataclass(frozen=True)
class ShopCreatedEvent(Event):
    shop_id: 'StoreId'
    admin_id: 'SystemUserId'
    shop_name: str
    admin_email: str
    shop_created_at: datetime


@dataclass(frozen=True)
class ShopRegistrationConfirmedEvent(Event):
    registration_id: 'ShopRegistrationId'
    user_email: 'SystemUserId'
    user_hashed_password: str
    mobile: str


@dataclass(frozen=True)
class ShopRegisteredEvent(Event):
    registration_id: 'ShopRegistrationId'
    shop_name: str
    owner_email: str
    confirmation_token: str


@dataclass(frozen=True)
class ShopRegistrationResendEvent(Event):
    registration_id: 'ShopRegistrationId'
    shop_name: str
    owner_email: str
    confirmation_token: str


@dataclass(frozen=True)
class ShopProductCreatedEvent(Event):
    product_id: 'ShopProductId'
    restock_threshold = -1
    maxstock_threshold = -1

    default_unit: Optional[str] = None
    units: List[str] = list
    first_stocks: List[int] = list


@dataclass(frozen=True)
class ShopProductUpdatedEvent(Event):
    product_id: 'ShopProductId'
    updated_keys: List[str] = list