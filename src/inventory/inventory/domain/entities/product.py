#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import NewType
from uuid import UUID

from foundation.events import EventMixin

InventoryProductId = NewType('InventoryProductId', tp=UUID)


class Product(EventMixin):
    def __init__(
            self,
            product_id: InventoryProductId,
            sku: str,
    ):
        super(Product, self).__init__()

        self.product_id = product_id
        self.sku = sku
