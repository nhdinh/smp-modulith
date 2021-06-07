#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.domain.entities.value_objects import StoreOwnerId


@dataclass(unsafe_hash=True)
class StoreOwner:
    id: StoreOwnerId
    email: str
    mobile: str
    hashed_password: str
