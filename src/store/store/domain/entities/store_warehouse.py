#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from store.domain.entities.value_objects import StoreId

StoreWarehouseId = NewType('StoreWarehouseId', tp=UUID)


@dataclass(unsafe_hash=True)
class StoreWarehouse:
    warehouse_id: StoreWarehouseId
    store_id: StoreId
    warehouse_owner: str
    warehouse_name: str
    default: bool = False
    disabled: bool = False
