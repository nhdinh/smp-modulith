#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from uuid import UUID

from typing import NewType

StoreWarehouseId = NewType('StoreWarehouseId', tp=UUID)


@dataclass
class StoreWarehouse:
    warehouse_id: StoreWarehouseId
    warehouse_owner: str
    warehouse_name: str
