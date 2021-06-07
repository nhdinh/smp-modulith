#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from identity.domain.value_objects import UserEmail

from foundation import Event


@dataclass(frozen=True)
class RequestPasswordChangeCreatedEvent(Event):
    username: str
    email: UserEmail
    token: str
