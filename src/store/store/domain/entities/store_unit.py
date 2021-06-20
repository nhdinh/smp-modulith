#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(unsafe_hash=True)
class StoreProductUnit:
    unit: str
    conversion_factor: float = 0
    default: bool = False
    disabled: bool = False
    from_unit: Optional[StoreProductUnit] = None

    if from_unit:
        base_unit = from_unit.unit

    # _from_unit: Optional[StoreProductUnit] = None
    #
    # def __init__(self, unit: str, base_unit: str = None, conversion_factor: float = 0, default: bool = False,
    #              disabled: bool = False):
    #     self.unit = unit
    #     self.conversion_factor = conversion_factor
    #     self.default = default
    #     self.disabled = disabled

    @property
    def product(self):
        return getattr(self, '_product')

    @product.setter
    def product(self, value):
        setattr(self, '_product', value)

    # @property
    # def from_unit(self):
    #     return self._from_unit
    #
    # @from_unit.setter
    # def from_unit(self, value):
    #     self._from_unit = value

    def __repr__(self):
        return f"<StoreProductUnit unit={self.unit} product={self.product.reference}>"
