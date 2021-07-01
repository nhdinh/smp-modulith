#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from typing import Optional

from store.domain.entities.store_supplier import StoreSupplierId
from store.domain.entities.value_objects import StoreProductId

@dataclass(unsafe_hash=True)
class ProductPurchasePrice:
    supplier: StoreSupplierId
    unit: str
    price: float
    tax: Optional[float]
    applied_from: datetime = datetime.now()
