#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import NewType

StoreUserId = NewType("StoreOwnerId", tp=str)


@dataclass(unsafe_hash=True)
class StoreUser:
    user_id: StoreUserId
    email: str
    mobile: str
    hashed_password: str
    confirmed_at: datetime
    active: bool = True

    def __eq__(self, other):
        if not other or not isinstance(other, StoreUser):
            raise TypeError

        return self.email == other.email and self.hashed_password == other.hashed_password
