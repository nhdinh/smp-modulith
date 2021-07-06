#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation.events import Event


@dataclass(frozen=True)
class StoreRegisteredEvent(Event):
    registration_id: 'StoreRegistrationId'
    store_name: str
    owner_email: str
    confirmation_token: str


@dataclass(frozen=True)
class StoreRegistrationResendEvent(Event):
    registration_id: 'StoreRegistrationId'
    store_name: str
    owner_email: str
    confirmation_token: str


@dataclass(frozen=True)
class StoreRegistrationConfirmedEvent(Event):
    store_id: 'StoreId'
    store_name: str
    owner_id: 'StoreOwnerId'
    email: str
    mobile: str
    hashed_password: str
