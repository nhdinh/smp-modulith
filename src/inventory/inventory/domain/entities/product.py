#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import NewType
from uuid import UUID

from foundation.events import EventMixin

ProductId = NewType('ProductId', tp=UUID)


class Product(EventMixin):
    def __init__(
            self,
            product_id: ProductId,
            sku: str,
    ):
        super(Product, self).__init__()

        self.product_id = product_id
        self.sku = sku
