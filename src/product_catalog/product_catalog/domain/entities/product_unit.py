#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import decimal
from dataclasses import dataclass
# set the default multiplier factor for the default product_unit
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  pass

DEFAULT_UNIT_CONVERSION_MULTIPLIER_FACTOR = -1


@dataclass(unsafe_hash=True)
class ProductUnit:
  unit: str
  base_unit: str
  multiplier: decimal
  default: bool
