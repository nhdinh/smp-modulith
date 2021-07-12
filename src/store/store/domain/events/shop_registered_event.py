#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation.events import Event


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
class ShopRegistrationConfirmedEvent(Event):
    shop_id: 'ShopId'
    shop_name: str
    owner_id: 'ShopUserId'
    email: str
    mobile: str
    hashed_password: str
