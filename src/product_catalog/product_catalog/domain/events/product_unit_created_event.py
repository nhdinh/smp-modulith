#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from foundation.events import Event
from product_catalog.domain.value_objects import ProductId


@dataclass(frozen=True)
class ProductUnitCreatedEvent(Event):
  product_id: ProductId
  unit: str
  occured_on: datetime = datetime.now()
