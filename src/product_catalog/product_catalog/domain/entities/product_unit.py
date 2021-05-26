#!/usr/bin/env python
# -*- coding: utf-8 -*-
import decimal
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(unsafe_hash=True)
class ProductUnit:
    unit: str
    base_unit: str
    multiplier: decimal
    default: bool

    def __init__(
            self,
            unit: str,
            base_unit: Optional[str] = None,
            multiplier: decimal = 0,
            default=False
    ):
        self.unit = unit
        self._base_unit = base_unit
        self.multiplier = multiplier
        self.default = default
        self.created_at = datetime.now()
