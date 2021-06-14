#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation.events import Event
from identity.domain.value_objects import UserId


@dataclass(frozen=True)
class UserRegistrationConfirmedEvent(Event):
    user_id: UserId
    email: str
    mobile: str
    hashed_password: str
