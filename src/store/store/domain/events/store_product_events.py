#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List, Optional

from foundation import Event
from store.domain.entities.value_objects import StoreProductId


@dataclass
class StoreProductCreatedEvent(Event):
    product_id: StoreProductId
    restock_threshold = -1
    maxstock_threshold = -1

    default_unit: Optional[str] = None
    units: List[str] = list
    first_stocks: List[int] = list


@dataclass
class StoreProductUpdatedEvent(Event):
    product_id: StoreProductId
    updated_keys: List[str] = list
