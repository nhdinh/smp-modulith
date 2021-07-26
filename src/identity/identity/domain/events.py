#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from foundation import Event
from identity.domain.value_objects import UserId, UserEmail


@dataclass(frozen=True)
class PendingUserCreatedEvent(Event):
    shop_registration_id: str
    user_id: UserId


@dataclass(frozen=True)
class RequestPasswordChangeCreatedEvent(Event):
    username: str
    email: UserEmail
    token: str


@dataclass(frozen=True)
class PasswordResettedEvent(Event):
    email: UserEmail
    username: str


@dataclass(frozen=True)
class UserCreatedEvent(Event):
    user_id: UserId
    email: str
    mobile: str
    created_at: datetime


@dataclass(frozen=True)
class ShopAdminCreatedEvent(Event):
    user_id: UserId
    email: str
    mobile: str
    created_at: datetime


@dataclass(frozen=True)
class UnexistentUserRequestEvent(Event):
    user_id: UserId


@dataclass(frozen=True)
class UserDataEmitEvent(Event):
    user_id: UserId
    email: str
    mobile: str
