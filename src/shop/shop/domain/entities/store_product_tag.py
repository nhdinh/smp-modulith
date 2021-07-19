#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class ShopProductTag:
    tag: str

    _product = None

    @property
    def product(self):
        return self._product

    @product.setter
    def product(self, value):
        self._product = value
