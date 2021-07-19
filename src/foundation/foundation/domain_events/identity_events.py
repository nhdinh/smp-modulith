#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from foundation.events import Event


@dataclass(frozen=True)
class UserCreatedEvent(Event):
    user_id: 'UserId'
    email: str
    mobile: str
    created_at: datetime
