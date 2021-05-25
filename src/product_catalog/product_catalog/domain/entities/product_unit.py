#!/usr/bin/env python
# -*- coding: utf-8 -*-
import decimal
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class ProductUnit:
    unit: str
    base_unit: str
    multiplier: decimal
    default: bool
