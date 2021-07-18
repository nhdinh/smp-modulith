#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.domain.entities.shop_unit import ShopProductUnit
from store.domain.entities.store_product import ShopProduct


@dataclass(unsafe_hash=True)
class DraftPurchaseOrderItem:
    product: ShopProduct
    unit: ShopProductUnit
    quantity: float
    description: str
