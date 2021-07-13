#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(unsafe_hash=True)
class ShopProductUnit:
    unit_name: str
    conversion_factor: float = 0
    default: bool = False
    disabled: bool = False
    referenced_unit: Optional[ShopProductUnit] = None
    deleted: bool = False

    def __eq__(self, other):
        if not other or not isinstance(other, ShopProductUnit):
            raise TypeError('Cannot compare StoreProductUnit with another data type')

        return self.unit_name == other.unit_name and self.conversion_factor == other.conversion_factor and self.referenced_unit == other.referenced_unit
