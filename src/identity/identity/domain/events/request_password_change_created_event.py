#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation import Event

from identity.domain.value_objects import UserEmail


@dataclass(frozen=True)
class RequestPasswordChangeCreatedEvent(Event):
    username: str
    email: UserEmail
    token: str
