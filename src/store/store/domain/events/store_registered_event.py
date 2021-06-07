#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from uuid import UUID

from foundation.events import Event
from store.domain.entities.value_objects import StoreId


@dataclass(frozen=True)
class StoreRegisteredEvent(Event):
    registration_id: UUID
    store_name: str
    owner_email: str
    confirmation_token: str


@dataclass(frozen=True)
class StoreRegistrationConfirmedEvent(Event):
    store_id: StoreId
    store_name: str