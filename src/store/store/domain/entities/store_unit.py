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
    deleted: bool = False

    if from_unit:
        base_unit = from_unit.unit

    def __eq__(self, other):
        if not other or not isinstance(other, StoreProductUnit):
            raise TypeError

        return self.unit == other.unit and self.conversion_factor == other.conversion_factor and self.from_unit == other.from_unit
