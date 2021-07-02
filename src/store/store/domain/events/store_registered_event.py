#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from uuid import UUID

from foundation.events import Event
from store.domain.entities.store import StoreId
from store.domain.entities.store_owner import StoreOwnerId


@dataclass(frozen=True)
class StoreRegisteredEvent(Event):
    registration_id: UUID
    store_name: str
    owner_email: str
    confirmation_token: str


@dataclass(frozen=True)
class StoreRegistrationResendEvent(Event):
    registration_id: UUID
    store_name: str
    owner_email: str
    confirmation_token: str


@dataclass(frozen=True)
class StoreRegistrationConfirmedEvent(Event):
    store_id: StoreId
    store_name: str
    owner_id: StoreOwnerId
    email: str
    mobile: str
    hashed_password: str
