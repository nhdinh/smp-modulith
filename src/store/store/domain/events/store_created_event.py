#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from foundation import Event


@dataclass(frozen=True)
class StoreCreatedEvent(Event):
    store_id: 'StoreId'
    store_name: str
    owner_name: str
    owner_email: str
