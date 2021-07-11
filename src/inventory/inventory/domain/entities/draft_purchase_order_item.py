#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from store.domain.entities.store_product import StoreProduct
from store.domain.entities.store_unit import StoreProductUnit


@dataclass(unsafe_hash=True)
class DraftPurchaseOrderItem:
    product: StoreProduct
    unit: StoreProductUnit
    quantity: float
    description: str
