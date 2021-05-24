#!/usr/bin/env python
# -*- coding: utf-8 -*-
import decimal
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from product_catalog.domain.value_objects import ProductId


@dataclass
class Unit:
    title: str