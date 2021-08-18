#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from foundation import Event
from inventory.domain.entities.value_objects import WarehouseId


@dataclass(frozen=True)
class WarehouseCreatedEvent(Event):
  warehouse_id: WarehouseId
  admin_id: str
  warehouse_name: str
  warehouse_created_at: datetime


@dataclass(frozen=True)
class PendingWarehouseCreatedEvent(Event):
  warehouse_id: WarehouseId
