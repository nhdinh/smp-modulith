#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.domain.entities.store_product import StoreProduct
from store.domain.entities.store_unit import StoreProductUnit


@dataclass(unsafe_hash=True)
class PurchaseOrderItem:
    product: StoreProduct
    unit: StoreProductUnit
    stock_quantity: int
    purchase_price: float
    description: str
