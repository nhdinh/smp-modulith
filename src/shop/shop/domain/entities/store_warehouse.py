#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from shop.domain.entities.value_objects import StoreWarehouseId, ShopId


@dataclass(unsafe_hash=True)
class ShopWarehouse:
    warehouse_id: StoreWarehouseId
    shop_id: 'ShopId'
    warehouse_name: str
    # default: bool = False
    # disabled: bool = False
