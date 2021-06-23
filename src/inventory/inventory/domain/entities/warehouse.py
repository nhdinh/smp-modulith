#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime


class WareHouse:
    def __init__(
            self,
            version: int = 0
    ):
        self.version = version

    #region ## Inner quantity check ##

    #endregion

    def add_product_stock(self, product: ProductIdentifier, stocking_unit: ProductUnit, stocking_quantity: int,
                          stocking_date: datetime):
        ...

    def deduct_product(self, product: ProductIdentifier, unit: ProductUnit, quantity: int, on_date: datetime):
        ...


