#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from foundation import Event


@dataclass(frozen=True)
class WarehouseCreatedEvent(Event):
    warehouse_id: 'WarehouseId'
    admin_id: 'UserId'
    warehouse_name: str
    warehouse_created_at: datetime
