#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(unsafe_hash=True)
class StoreProductUnit:
    unit: str
    conversion_factor: float
    default: bool
    disabled: bool = False
    from_unit: Optional[StoreProductUnit] = None

    @property
    def product(self):
        return getattr(self, '_product')

    @product.setter
    def product(self, value):
        setattr(self, '_product', value)
