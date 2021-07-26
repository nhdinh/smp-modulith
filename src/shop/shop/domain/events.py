#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from foundation import Event
from shop.domain.entities.value_objects import ShopRegistrationId, ShopId, SystemUserId, ShopProductId


@dataclass(frozen=True)
class ShopRegistrationCreatedEvent(Event):
    registration_id: ShopRegistrationId
    shop_name: str
    owner_email: str
    owner_mobile: str
    password: str
    confirmation_token: str


@dataclass(frozen=True)
class PendingShopCreatedEvent(Event):
    # shop_registration_id: ShopRegistrationId
    shop_id: ShopId


@dataclass(frozen=True)
class ShopRegistrationConfirmedEvent(Event):
    registration_id: ShopRegistrationId
    user_email: SystemUserId
    user_hashed_password: str
    mobile: str


@dataclass(frozen=True)
class ShopCreatedEvent(Event):
    shop_id: ShopId
    admin_id: SystemUserId
    shop_name: str
    admin_email: str
    shop_created_at: datetime


@dataclass(frozen=True)
class ShopRegistrationResendEvent(Event):
    registration_id: ShopRegistrationId
    shop_name: str
    owner_email: str
    confirmation_token: str


@dataclass(frozen=True)
class ShopProductCreatedEvent(Event):
    shop_id: ShopId
    product_id: ShopProductId
    restock_threshold = -1
    maxstock_threshold = -1

    default_unit: Optional[str] = None
    units: List[str] = list
    first_stocks: List[int] = list


@dataclass(frozen=True)
class ShopProductUpdatedEvent(Event):
    product_id: ShopProductId
    shop_id: ShopId
    updated_keys: List[str] = list


@dataclass(frozen=True)
class ShopUserCreatedEvent(Event):
    user_id: 'SystemUserId'
    shop_id: ShopId
