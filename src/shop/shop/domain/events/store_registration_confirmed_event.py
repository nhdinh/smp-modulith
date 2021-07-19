#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.domain.entities.value_objects import ShopId


@dataclass(frozen=True)
class StoreRegistrationConfirmedEvent:
    store_id: ShopId
    store_name: str
